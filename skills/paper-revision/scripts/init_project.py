"""Set up the revision workspace inside a paper folder. Safe to run again: it never overwrites.

Creates, inside VENUE (the folder that holds the manuscript .tex):
    revision/   README, revision.toml, rules, comments register, plan, decisions, proposals/,
                original/, checks/, mock-review/, archive/      (local only, not committed)
    papers/requirements/                                         (local only, not committed)
and appends a marked block to the repository's .gitignore so that revision/, papers/, code/
and LaTeX intermediates stay out of git.

Example:
    python init_project.py journal --main-tex main.tex
    python init_project.py . --dry-run
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from _common import git_root, use_utf8_stdout

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "project"
EXTRA_DIRS = ("revision/proposals", "revision/checks", "revision/mock-review", "revision/archive",
              "papers/requirements")
BLOCK_START = "# >>> paper-revision"
BLOCK_END = "# <<< paper-revision"
LOCAL_ONLY = ("revision/", "papers/", "code/")
LATEX_INTERMEDIATES = ("*.aux", "*.log", "*.blg", "*.out", "*.toc", "*.fls", "*.fdb_latexmk",
                       "*.synctex.gz", "*.bcf", "*.run.xml", "*-diff.tex", "*-diff.pdf")


@dataclass(frozen=True)
class Action:
    kind: str  # "mkdir", "write" or "append"
    path: Path
    content: str = ""


def gitignore_block(prefix: str) -> str:
    """The .gitignore lines for a venue folder at prefix ("" = repository root)."""
    base = f"{prefix.rstrip('/')}/" if prefix else ""
    lines = [BLOCK_START,
             "# Local-only: revision notes (confidential reviews), reference PDFs, code repo",
             *(base + item for item in LOCAL_ONLY),
             "# LaTeX intermediates (the compiled PDF and .bbl stay tracked for Overleaf)",
             *LATEX_INTERMEDIATES,
             BLOCK_END]
    return "\n" + "\n".join(lines) + "\n"


def body_start_marker(manuscript: Path) -> str:
    """\\section{Introduction} when the manuscript has it, else \\begin{document}."""
    introduction = "\\section{Introduction}"
    if manuscript.is_file() and introduction in manuscript.read_text(encoding="utf-8-sig",
                                                                     errors="replace"):
        return introduction
    return "\\begin{document}"


def _fill(text: str, main_tex: str, body_start: str) -> str:
    # Forward slashes: a Windows "sub\main.tex" would be an invalid escape in a TOML string.
    tex = PurePosixPath(main_tex.replace("\\", "/"))
    return (text.replace("{{MAIN_TEX}}", f"../{tex.as_posix()}")
                .replace("{{MAIN_PDF}}", f"../{tex.with_suffix('.pdf').as_posix()}")
                .replace("{{BODY_START}}", body_start))


def _venue_prefix(venue: Path, root: Path) -> str:
    try:
        rel = venue.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return ""
    return "" if rel == "." else rel


def plan_actions(venue: Path, main_tex: str) -> list[Action]:
    actions: list[Action] = []
    body_start = body_start_marker(venue / main_tex.replace("\\", "/"))
    for template in sorted(TEMPLATE_DIR.rglob("*")):
        if not template.is_file():
            continue
        target = venue / template.relative_to(TEMPLATE_DIR)
        if not target.exists():
            content = _fill(template.read_text(encoding="utf-8"), main_tex, body_start)
            actions.append(Action("write", target, content))
    actions += [Action("mkdir", venue / d) for d in EXTRA_DIRS if not (venue / d).exists()]
    root = git_root(venue) or venue
    gitignore = root / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    if BLOCK_START not in existing:
        actions.append(Action("append", gitignore, gitignore_block(_venue_prefix(venue, root))))
    return actions


def apply(actions: list[Action]) -> None:
    for action in actions:
        if action.kind == "mkdir":
            action.path.mkdir(parents=True, exist_ok=True)
        elif action.kind == "write":
            action.path.parent.mkdir(parents=True, exist_ok=True)
            action.path.write_text(action.content, encoding="utf-8")
        elif action.kind == "append":
            with open(action.path, "a", encoding="utf-8") as handle:
                handle.write(action.content)


def main(argv: list[str] | None = None) -> int:
    """Returns the number of actions taken (or that would be taken with --dry-run)."""
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("venue", nargs="?", default=".", help="folder holding the manuscript .tex")
    parser.add_argument("--main-tex", default="main.tex", help="manuscript file name inside VENUE")
    parser.add_argument("--dry-run", action="store_true", help="only list what would be done")
    args = parser.parse_args(argv)
    venue = Path(args.venue)
    if not venue.is_dir():
        raise SystemExit(f"not a folder: {venue}")
    if not (venue / args.main_tex).exists():
        print(f"note: {venue / args.main_tex} does not exist yet; edit revision/revision.toml later")
    actions = plan_actions(venue, args.main_tex)
    verb = "would " if args.dry_run else ""
    for action in actions:
        print(f"{verb}{action.kind}: {action.path}")
    if not args.dry_run:
        apply(actions)
    print(f"{len(actions)} action(s); nothing existing was overwritten" if actions
          else "already set up; nothing to do")
    return len(actions)


if __name__ == "__main__":
    main()
    sys.exit(0)
