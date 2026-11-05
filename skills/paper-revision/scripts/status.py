"""One-screen status of the revision: comments, proposals, decisions, letter, pages, deadline.

Reads revision.toml (searched upward from the current folder, or --config), the comment
register (comments.md), proposals/, decisions.md, the response letter and the compiled PDF.

Example:
    python status.py --config journal/revision/revision.toml
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from _common import get, load_config, read_text, resolve, strip_comments, use_utf8_stdout

STATUSES = ("todo", "proposed", "approved", "applied", "rejected", "deferred")
OPEN_STATUSES = ("todo", "proposed", "approved", "deferred")
PROPOSAL_FILE = re.compile(r"^(P-\d+)")
STATUS_LINE = re.compile(r"\*\*Status:\*\*\s*([\w-]+)", re.I)
DECISION_HEADING = re.compile(r"^## \d{4}-\d{2}-\d{2}", re.M)


@dataclass(frozen=True)
class RegisterSummary:
    counts: Counter
    open_ids: list[str]
    reply_missing: list[str]
    unknown: list[str]


def _cells(line: str) -> list[str]:
    """Split a markdown table row on | outside $...$, `...` and escaped \\|."""
    cells, current, in_math, in_code, i = [], [], False, False, 0
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    while i < len(text):
        char = text[i]
        if char == "\\" and i + 1 < len(text):
            current.append(text[i:i + 2])
            i += 2
            continue
        if char == "$" and not in_code:
            in_math = not in_math
        elif char == "`":
            in_code = not in_code
        elif char == "|" and not (in_math or in_code):
            cells.append("".join(current).strip())
            current = []
            i += 1
            continue
        current.append(char)
        i += 1
    cells.append("".join(current).strip())
    return cells


def parse_register(text: str) -> list[dict[str, str]]:
    """Rows of the first markdown table whose header has both ID and Status columns."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        header = _cells(line)
        if "ID" not in header or "Status" not in header:
            continue
        rows = []
        for row_line in lines[i + 2:]:
            if not row_line.lstrip().startswith("|"):
                break
            cells = _cells(row_line)
            if cells and cells[0]:
                rows.append(dict(zip(header, cells)))
        return rows
    return []


def summarize_register(rows: list[dict[str, str]]) -> RegisterSummary:
    counts = Counter(r.get("Status", "").lower() for r in rows)
    open_ids = [r["ID"] for r in rows if r.get("Status", "").lower() in OPEN_STATUSES]
    reply_missing = [r["ID"] for r in rows if r.get("Reply", "").lower() != "final"]
    unknown = [f"{r['ID']} ({r.get('Status', '')})" for r in rows
               if r.get("Status", "").lower() not in STATUSES]
    return RegisterSummary(counts, open_ids, reply_missing, unknown)


def proposal_statuses(folder: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not folder.is_dir():
        return result
    for path in sorted(folder.glob("P-*.md")):
        match = PROPOSAL_FILE.match(path.name)
        if match is None:
            continue  # e.g. P-notes.md: not a numbered proposal
        status = STATUS_LINE.search(read_text(path))
        value = status.group(1).lower() if status else "?"
        key = match.group(1)
        result[key if key not in result else f"{key} (duplicate: {path.name})"] = value
    return result


def current_title(folder: Path) -> str | None:
    current = folder / "current.md"
    if not current.is_file():
        return None
    heading = re.search(r"^# (.+)$", read_text(current), re.M)
    return heading.group(1).strip() if heading else None


def count_placeholders(text: str, placeholder: str) -> int:
    return len(re.findall(re.escape(placeholder) + r"(?![A-Za-z])", text))


def page_count(pdf: Path) -> int | None:
    if not pdf.is_file() or shutil.which("pdfinfo") is None:
        return None
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout or ""
    match = re.search(r"^Pages:\s+(\d+)", info, re.M)
    return int(match.group(1)) if match else None


def days_left(deadline, today: date) -> int | None:
    """Days until the deadline; accepts "YYYY-MM-DD" or an unquoted TOML date."""
    if isinstance(deadline, date):
        return (deadline - today).days
    try:
        return (date.fromisoformat(str(deadline)) - today).days
    except ValueError:
        return None


def _counts_text(counts: Counter) -> str:
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items()) if k)


def _register_lines(rev: Path) -> list[str]:
    register = rev / "comments.md"
    if not register.is_file():
        return [f"comments: register not found ({register})"]
    rows = parse_register(read_text(register))
    summary = summarize_register(rows)
    lines = [f"comments: {len(rows)}" + (f" ({_counts_text(summary.counts)})" if rows else "")]
    if summary.open_ids:
        lines.append("  open: " + ", ".join(summary.open_ids))
    if summary.reply_missing:
        lines.append("  reply not final: " + ", ".join(summary.reply_missing))
    if summary.unknown:
        lines.append("  unknown status: " + ", ".join(summary.unknown)
                     + f"  (use: {' · '.join(STATUSES)})")
    return lines


def _proposal_lines(rev: Path) -> list[str]:
    folder = rev / "proposals"
    statuses = proposal_statuses(folder)
    lines = [f"proposals closed: {len(statuses)}"
             + (f" ({_counts_text(Counter(statuses.values()))})" if statuses else "")]
    title = current_title(folder)
    if title and PROPOSAL_FILE.match(title):
        lines.append(f"  open (current.md): {title}")
    return lines


def open_questions(decisions_text: str) -> list[str]:
    """IDs (first column) of the rows in the "Open questions" table of decisions.md."""
    section = re.search(r"^## Open questions\s*$(.*?)(?=^## |\Z)", decisions_text, re.M | re.S)
    if not section:
        return []
    rows = [_cells(line) for line in section.group(1).splitlines() if line.lstrip().startswith("|")]
    return [r[0] for r in rows[2:] if r and r[0]]


def _decision_lines(rev: Path) -> list[str]:
    decisions = rev / "decisions.md"
    if not decisions.is_file():
        return ["decisions: decisions.md not found"]
    text = read_text(decisions)
    lines = [f"decisions logged: {len(DECISION_HEADING.findall(text))}"]
    questions = open_questions(text)
    if questions:
        lines.append(f"  open questions: {len(questions)} ({', '.join(questions)})")
    return lines


def _paper_lines(config: dict) -> list[str]:
    lines = []
    letter = resolve(config, get(config, "letter.tex"))
    if letter and letter.is_file():
        placeholder = get(config, "letter.placeholder", "\\PH")
        n = count_placeholders(strip_comments(read_text(letter)), placeholder)
        lines.append(f"placeholders left in the letter: {n}")
    elif letter:
        lines.append(f"letter: not found ({letter})")
    pdf = resolve(config, get(config, "paper.pdf"))
    try:
        limit = int(get(config, "paper.page_limit", 0) or 0)
    except (TypeError, ValueError):
        raise SystemExit("[paper] page_limit must be a whole number, e.g. page_limit = 25")
    pages = page_count(pdf) if pdf else None
    if pdf is None or not pdf.is_file():
        lines.append(f"pages: PDF not found ({pdf}); compile, or set [paper] pdf")
    elif shutil.which("pdfinfo") is None:
        lines.append("pages: pdfinfo not installed (it ships with TeX Live / poppler)")
    elif pages is None:
        lines.append(f"pages: pdfinfo could not read {pdf}")
    else:
        over = f", {pages - limit} over the limit of {limit}" if limit and pages > limit else ""
        lines.append(f"pages: {pages}" + (f" of {limit}" if limit else "") + over)
    deadline = get(config, "paper.deadline", "")
    left = days_left(deadline, date.today())
    if left is not None:
        lines.append(f"deadline: {deadline} ({left} days left)")
    return lines


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", help="revision.toml (default: search upward)")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if "paper" not in config:
        raise SystemExit("no revision.toml found here or above; run init_project.py first")
    rev = config["_dir"]
    lines = (_register_lines(rev) + _proposal_lines(rev) + _decision_lines(rev)
             + _paper_lines(config))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
