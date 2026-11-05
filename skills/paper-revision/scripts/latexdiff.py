"""Marked-changes PDF: the submitted version (a git tag) against the current working tree.

Exports the tagged version and a copy of the current files to a temporary folder, runs
latexdiff --flatten (so \\input files are included), and compiles the result with latexmk.
Nothing is written inside the repository except the output file.

Examples:
    python latexdiff.py --config revision/revision.toml
    python latexdiff.py --tex main.tex --base submitted-v1 --out marked.pdf -- --math-markup=0
    python latexdiff.py --tex main.tex --base submitted-v1 --no-pdf --out marked.tex

Arguments after "--" are passed to latexdiff (e.g. --type=CFONT, --math-markup=whole).
"""
from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

from _common import get, git, git_root, load_config, resolve, use_utf8_stdout


def build_latexdiff_command(old: Path, new: Path, extra: list[str]) -> list[str]:
    return ["latexdiff", "--flatten", *extra, str(old), str(new)]


def default_output(revision_dir: Path, base: str, today: str, pdf: bool) -> Path:
    suffix = "pdf" if pdf else "tex"
    return revision_dir / "checks" / f"latexdiff-{base}-vs-current-{today}.{suffix}"


def export_revision(root: Path, rev: str, dest: Path) -> None:
    """Write the files of revision REV into dest (git archive, no checkout)."""
    data = subprocess.run(["git", "archive", "--format=zip", rev], cwd=root,
                          capture_output=True, check=False)
    if data.returncode != 0:
        message = data.stderr.decode(errors="ignore").strip()
        raise SystemExit(f"git archive {rev} failed: {message}")
    with zipfile.ZipFile(io.BytesIO(data.stdout)) as archive:
        archive.extractall(dest)


def copy_worktree(root: Path, dest: Path) -> None:
    """Copy tracked and untracked-but-not-ignored files of the working tree."""
    names = git(["ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root)
    for name in filter(None, names.split("\0")):
        source = root / name
        if source.is_file():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def run_latexdiff(old_tex: Path, new_tex: Path, diff_tex: Path, extra: list[str]) -> None:
    result = subprocess.run(build_latexdiff_command(old_tex, new_tex, extra), cwd=new_tex.parent,
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise SystemExit(f"latexdiff failed:\n{result.stderr.strip()[-2000:]}")
    diff_tex.write_text(result.stdout, encoding="utf-8")


def compile_pdf(diff_tex: Path) -> Path:
    if shutil.which("latexmk") is None:
        raise SystemExit("latexmk is not installed; use --no-pdf and compile the .tex yourself")
    result = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-f", diff_tex.name],
                            cwd=diff_tex.parent, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", check=False)
    pdf = diff_tex.with_suffix(".pdf")
    if not pdf.is_file():
        raise SystemExit(f"compilation failed; rerun with --keep and read {diff_tex.stem}.log")
    if result.returncode != 0:
        print("warning: LaTeX reported errors; the PDF was produced anyway (latexmk -f). "
              "Check it, or rerun with --keep and read the .log.", file=sys.stderr)
    return pdf


def parse_args(argv: list[str] | None) -> tuple[argparse.Namespace, list[str]]:
    argv = list(sys.argv[1:] if argv is None else argv)
    split = argv.index("--") if "--" in argv else len(argv)
    own, extra = argv[:split], argv[split + 1:]
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", help="revision.toml (default: search upward)")
    parser.add_argument("--tex", help="manuscript .tex (default: [paper] main_tex)")
    parser.add_argument("--base", help="git tag or commit of the old version ([paper] submitted_tag)")
    parser.add_argument("--out", help="output file (default: revision/checks/latexdiff-...)")
    parser.add_argument("--no-pdf", action="store_true", help="write the diff .tex, do not compile")
    parser.add_argument("--keep", action="store_true", help="keep the temporary build folder")
    return parser.parse_args(own), extra


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args, extra = parse_args(argv)
    config = load_config(args.config)
    base = args.base or get(config, "paper.submitted_tag")
    if not base:
        raise SystemExit("no base version: pass --base TAG or set [paper] submitted_tag")
    if base.startswith("-"):
        raise SystemExit(f"invalid base version: {base!r}")
    if shutil.which("latexdiff") is None:
        raise SystemExit("latexdiff is not installed (it ships with TeX Live and MiKTeX)")
    tex = Path(args.tex) if args.tex else resolve(config, get(config, "paper.main_tex"))
    if tex is None or not tex.is_file():
        raise SystemExit(f"manuscript not found: {tex}")
    tex = tex.resolve()
    root = git_root(tex)
    if root is None:
        raise SystemExit(f"{tex} is not inside a git repository")
    rel = tex.relative_to(root)
    out = Path(args.out) if args.out else default_output(
        config["_dir"], base, date.today().isoformat(), pdf=not args.no_pdf)
    build = Path(tempfile.mkdtemp(prefix="latexdiff-"))
    try:
        export_revision(root, base, build / "old")
        copy_worktree(root, build / "new")
        old_tex, new_tex = build / "old" / rel, build / "new" / rel
        if not old_tex.is_file():
            raise SystemExit(f"{rel.as_posix()} does not exist at {base}")
        diff_tex = new_tex.with_name(f"{new_tex.stem}-diff.tex")
        run_latexdiff(old_tex, new_tex, diff_tex, extra)
        result = diff_tex if args.no_pdf else compile_pdf(diff_tex)
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(result, out)
    finally:
        if args.keep:
            print(f"build folder kept: {build}")
        else:
            shutil.rmtree(build, ignore_errors=True)
    print(f"written: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
