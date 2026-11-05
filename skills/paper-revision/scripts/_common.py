"""Shared helpers for the paper-revision scripts: config loading and LaTeX text handling.

Standard library only (Python 3.11+ for tomllib).
"""
from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path

CONFIG_NAME = "revision.toml"

# Commands whose argument is a key or a file name, not prose or a number.
REF_COMMANDS = (
    r"label|ref|cref|Cref|eqref|autoref|pageref|cite[tp]?|citealp|citealt|citeauthor|citeyear"
    r"|includegraphics|input|include|url|href|bibliography|bibliographystyle"
)
REF_PATTERN = re.compile(r"\\(?:" + REF_COMMANDS + r")\*?(?:\[[^\]]*\])*\{[^}]*\}")
# A comment starts at % preceded by an even number of backslashes (\% is a percent sign,
# \\% is a line break followed by a comment).
COMMENT_PATTERN = re.compile(r"(?<!\\)((?:\\\\)*)%.*$", re.MULTILINE)


def use_utf8_stdout() -> None:
    """Avoid UnicodeEncodeError on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def find_config(start: Path) -> Path | None:
    """Look for revision/revision.toml or revision.toml in start and its parents, then in
    <venue>/revision/ one level below start (running from the repository root)."""
    start = start.resolve()
    for folder in (start, *start.parents):
        for candidate in (folder / CONFIG_NAME, folder / "revision" / CONFIG_NAME):
            if candidate.is_file():
                return candidate
    below = sorted(start.glob(f"*/revision/{CONFIG_NAME}"))
    if len(below) > 1:
        raise SystemExit("several revision.toml files found; pass --config: "
                         + ", ".join(str(p) for p in below))
    return below[0] if below else None


def load_config(path: str | Path | None) -> dict:
    """Load the TOML config. Returns {"_dir": <cwd>} when no config is given or found.

    Paths inside the config are relative to the folder that holds the config file.
    """
    config_path = Path(path) if path else find_config(Path.cwd())
    if config_path is None:
        return {"_dir": Path.cwd()}
    if not config_path.is_file():
        raise SystemExit(f"config not found: {config_path}")
    try:
        data = tomllib.loads(read_text(config_path))
    except tomllib.TOMLDecodeError as error:
        raise SystemExit(f"{config_path}: invalid TOML: {error}") from error
    return {**data, "_dir": config_path.parent.resolve()}


def get(config: dict, dotted: str, default=None):
    """config["a"]["b"] for dotted="a.b", or default when any level is missing."""
    node = config
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def resolve(config: dict, value: str | Path | None) -> Path | None:
    """Resolve a config path relative to the config folder; absolute paths pass through."""
    if value in (None, ""):
        return None
    path = Path(value)
    return path if path.is_absolute() else (config["_dir"] / path).resolve()


def read_text(path: str | Path) -> str:
    """Read a UTF-8 file (a byte-order mark is accepted); exit with a clear message otherwise."""
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except FileNotFoundError as error:
        raise SystemExit(f"file not found: {path}") from error
    except UnicodeDecodeError as error:
        raise SystemExit(f"{path}: not UTF-8 ({error.reason} at byte {error.start}); "
                         "re-save the file as UTF-8") from error


INPUT_COMMAND = re.compile(r"^[^%\n]*\\(input|include)\{", re.MULTILINE)


def warn_if_inputs(text: str, path: str | Path) -> None:
    """Scripts read one file; say so when the manuscript is split with \\input or \\include."""
    if INPUT_COMMAND.search(text):
        print(f"warning: {path} uses \\input/\\include; only this file is checked "
              "(run the script on each part, or on a flattened copy from latexdiff.py --no-pdf)",
              file=sys.stderr)


def slice_between(text: str, start: str | None, end: str | None) -> tuple[str, int]:
    """Return (text from the start marker up to the end marker, offset of the slice).

    A missing marker argument means "from the beginning" / "to the end". A marker that is
    given but absent from the text is an error, so a renamed section is noticed.
    """
    begin = 0
    if start:
        begin = text.find(start)
        if begin < 0:
            raise SystemExit(f"start marker not found: {start!r}")
    finish = len(text)
    if end:
        finish = text.find(end, begin)
        if finish < 0:
            raise SystemExit(f"end marker not found after the start marker: {end!r}")
    return text[begin:finish], begin


def strip_comments(text: str) -> str:
    """Remove LaTeX comments (an unescaped % to the end of the line)."""
    return COMMENT_PATTERN.sub(r"\1", text)


def mask_refs(text: str, replacement: str = " ") -> str:
    """Replace \\label{..}, \\cite{..}, \\includegraphics{..} and similar with a placeholder."""
    return REF_PATTERN.sub(replacement, text)


def git(args: list[str], cwd: Path) -> str:
    """Run git and return stdout; exit with git's message on failure."""
    if not Path(cwd).is_dir():
        raise SystemExit(f"not a folder: {cwd}")
    try:
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", check=True)
    except FileNotFoundError as error:
        raise SystemExit("git is not installed or not on PATH") from error
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"git {' '.join(args)} failed: {error.stderr.strip()}") from error
    return result.stdout


def git_root(path: Path) -> Path | None:
    """Top folder of the git repository containing path, or None outside a repository."""
    folder = path if path.is_dir() else path.parent
    try:
        # git prints paths in UTF-8; the Windows locale default would garble non-ASCII folders.
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=folder,
                             capture_output=True, text=True, encoding="utf-8",
                             check=True).stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return Path(out).resolve()


def read_source(spec: str) -> str:
    """Read a file, or a file at a git revision written as git:REV:path.

    The path after REV is relative to the current folder, e.g. git:submitted-v1:main.tex.
    """
    if not spec.startswith("git:"):
        return read_text(spec)
    try:
        _, rev, rel = spec.split(":", 2)
    except ValueError as error:
        raise SystemExit(f"expected git:REV:path, got {spec!r}") from error
    target = (Path.cwd() / rel).resolve()
    root = git_root(target.parent if target.parent.exists() else Path.cwd())
    if root is None:
        raise SystemExit(f"{spec}: not inside a git repository")
    inside = target.relative_to(root).as_posix()
    return git(["show", f"{rev}:{inside}"], cwd=root)
