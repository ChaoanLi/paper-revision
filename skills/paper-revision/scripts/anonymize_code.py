"""Build an anonymous code supplement (for double-anonymous review) from a git repository.

Copies every file git tracks plus untracked files that are not ignored, applies the text
replacements from [anonymize] in revision.toml, then refuses to write the zip if any forbidden
pattern (names, institution, URLs, IDs; e-mail addresses always) is left in a text file, a file
name, or PDF metadata.

Example:
    python anonymize_code.py ../code/myrepo revision/checks/code_anonymous.zip
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from _common import get, git, load_config, use_utf8_stdout

EMAIL = r"[\w.+-]+@[\w-]+(\.[\w-]+)+"
PDF_FIELDS = ("Author", "Creator", "Producer", "Title", "Subject", "Keywords")
PREVIEW = 100
SNIFF_BYTES = 8192


def forbidden_pattern(patterns: list[str]) -> re.Pattern:
    return re.compile("|".join([EMAIL, *patterns]), re.IGNORECASE)


def tracked_files(repo: Path) -> list[str]:
    out = git(["ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=repo)
    return sorted({name for name in out.split("\0") if name})


def copy_files(repo: Path, stage: Path, names: list[str]) -> None:
    for name in names:
        source = repo / name
        if not source.is_file():
            continue  # deleted in the working tree but still in the index
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def apply_replacements(stage: Path, replacements: list[dict]) -> None:
    for item in replacements:
        missing = {"file", "old", "new"} - set(item)
        if missing:
            raise SystemExit(f"[[anonymize.replace]] entry {item!r} lacks {sorted(missing)}")
        path = (stage / item["file"]).resolve()
        if not path.is_relative_to(stage.resolve()):
            raise SystemExit(f"{item['file']}: must be a path inside the repository")
        if not path.is_file():
            raise SystemExit(f"{item['file']}: file not in the package; fix [[anonymize.replace]]")
        with open(path, encoding="utf-8", newline="") as handle:  # keep line endings as they are
            text = handle.read()
        if item["old"] not in text:
            raise SystemExit(f"{item['file']}: expected text not found: {item['old'][:60]!r}")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text.replace(item["old"], item["new"]))


def read_as_text(path: Path) -> str | None:
    """The file's text if it looks like text (UTF-8, or UTF-16 with a BOM), else None."""
    data = path.read_bytes()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    if b"\0" in data[:SNIFF_BYTES]:
        return None
    return data.decode("utf-8", errors="replace")


def _pdf_metadata(path: Path, rel: str, pattern: re.Pattern) -> tuple[list[str], list[str]]:
    result = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        return [], [f"{rel}: pdfinfo failed, PDF metadata not checked"]
    return [f"{rel} (PDF metadata): {line.strip()}" for line in (result.stdout or "").splitlines()
            if line.startswith(PDF_FIELDS) and pattern.search(line)], []


def scan(stage: Path, pattern: re.Pattern) -> tuple[list[str], list[str]]:
    """Return (problems, warnings) for every file in the staged package."""
    problems: list[str] = []
    warnings: list[str] = []
    has_pdfinfo = shutil.which("pdfinfo") is not None
    for path in sorted(stage.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(stage).as_posix()
        if pattern.search(rel):
            problems.append(f"{rel}: file name")
        if path.suffix.lower() == ".pdf":
            if has_pdfinfo:
                found, warned = _pdf_metadata(path, rel, pattern)
                problems += found
                warnings += warned
            else:
                warnings.append(f"{rel}: PDF metadata not checked (pdfinfo not installed)")
            continue
        text = read_as_text(path)
        if text is None:
            warnings.append(f"{rel}: binary file not scanned; check it by hand")
            continue
        problems += [f"{rel}:{n}: {line.strip()[:PREVIEW]}"
                     for n, line in enumerate(text.splitlines(), 1) if pattern.search(line)]
    return problems, warnings


def write_zip(stage: Path, output: Path, top: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(stage.rglob("*")):
            if path.is_file():
                archive.write(path, f"{top}/{path.relative_to(stage).as_posix()}")


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repo", help="code repository (a git working tree)")
    parser.add_argument("output", help="zip file to write")
    parser.add_argument("--config", help="revision.toml with an [anonymize] table")
    parser.add_argument("--top", help="top folder name inside the zip")
    parser.add_argument("--forbid", nargs="*", default=[], help="extra forbidden regexes")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    repo, output = Path(args.repo), Path(args.output)
    try:
        pattern = forbidden_pattern([*get(config, "anonymize.forbidden", []), *args.forbid])
    except re.error as error:
        raise SystemExit(f"invalid forbidden pattern: {error}") from error
    top = args.top or get(config, "anonymize.top", "code_supplement")
    if pattern.search(top):
        raise SystemExit(f"the top folder name {top!r} itself contains a forbidden string")
    names = tracked_files(repo)
    out_resolved = output.resolve()
    names = [n for n in names if (repo / n).resolve() != out_resolved]  # never pack an old zip
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp)
        copy_files(repo, stage, names)
        apply_replacements(stage, get(config, "anonymize.replace", []))
        problems, warnings = scan(stage, pattern)
        for warning in warnings:
            print(f"warning: {warning}")
        if problems:
            stale = (f"\nNote: the existing {output} is from an earlier run and was not checked now."
                     if output.exists() else "")
            raise SystemExit("Identifying strings left (zip not written):\n"
                             + "\n".join(problems) + stale)
        write_zip(stage, output, top)
        count = sum(1 for p in stage.rglob("*") if p.is_file())
    size = output.stat().st_size / 1e6
    print(f"{output}: {count} files, {size:.2f} MB, no forbidden strings found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
