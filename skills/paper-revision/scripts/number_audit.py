"""Check every decimal number in the manuscript against the values in result CSV files.

A number in the text counts as matched when some CSV value rounds to it at the same number
of decimals (optionally also 1 - value, for "power" vs "type II error" style pairs).
Unmatched numbers are listed with their section and context for checking by hand.

Examples:
    python number_audit.py --config revision/revision.toml
    python number_audit.py --tex main.tex --results ../code/results --exclude quick --all
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from _common import (get, load_config, mask_refs, read_text, resolve, slice_between,
                     strip_comments, use_utf8_stdout, warn_if_inputs)

# A decimal not glued to a word or another number; a sentence-ending period is allowed.
NUMBER = re.compile(r"(?<![\w.^_{])(\d+\.\d+)(?!\w|\.\d)")
SECTION = re.compile(r"\\(?:sub)*section\*?\{([^}]*)\}")
NUMERIC_CELL = re.compile(r"-?\d+(\.\d+)?([eE]-?\d+)?")
MAX_HITS_SHOWN = 4


@dataclass(frozen=True)
class Cell:
    value: float
    file: str
    key: str
    column: str


@dataclass(frozen=True)
class Finding:
    section: str
    number: str
    context: str
    hits: tuple[Cell, ...] = field(default_factory=tuple)


def prepare_body(text: str, start: str | None, end: str | None) -> str:
    """The part of the manuscript to audit, without comments, labels and citation keys."""
    body, _ = slice_between(text, start, end)
    return mask_refs(strip_comments(body))


def _csv_files(paths: list[Path], pattern: str, exclude: list[str]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob(pattern)))
        else:
            raise SystemExit(f"results path not found: {path}")
    return [f for f in files if not any(word in f.name for word in exclude)]


def load_cells(paths: list[Path], pattern: str = "*.csv",
               exclude: list[str] | None = None) -> list[Cell]:
    """Every numeric token in the CSV files, with file stem, row key and column name."""
    cells: list[Cell] = []
    for csv_file in _csv_files(paths, pattern, exclude or []):
        try:
            with open(csv_file, encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.reader(handle))
        except UnicodeDecodeError as error:
            raise SystemExit(f"{csv_file}: not UTF-8 ({error.reason}); re-save it as UTF-8") from error
        if not rows:
            continue
        header = rows[0]
        for row in rows[1:]:
            key = " ".join(c for c in row if not NUMERIC_CELL.fullmatch(c.strip()))[:45]
            for column, cell in zip(header, row):
                for token in cell.split():
                    try:
                        cells.append(Cell(float(token), csv_file.stem, key, column))
                    except ValueError:
                        continue
    return cells


def _matches(number: str, cell: Cell, complement: bool, percent: bool) -> bool:
    decimals = len(number.split(".")[1])
    target = float(number)
    # abs(): the text may print a negative value with a separate minus sign ("$-$0.5").
    candidates = [abs(cell.value)] + ([1 - cell.value] if complement else [])
    if percent:  # "4.5\%" in the text may be 0.045 in the CSV
        candidates += [100 * v for v in candidates]
    return any(round(v, decimals) == target for v in candidates)


def audit(body: str, cells: list[Cell], complement: bool = True) -> list[Finding]:
    sections = [(m.start(), m.group(1)) for m in SECTION.finditer(body)]
    findings = []
    for match in NUMBER.finditer(body):
        number = match.group(1)
        section = max((s for s in sections if s[0] <= match.start()), default=(0, "?"))[1]
        context = re.sub(r"\s+", " ", body[max(0, match.start() - 70):match.end() + 40])
        percent = body[match.end():match.end() + 2] == "\\%"
        hits = tuple(c for c in cells if _matches(number, c, complement, percent))
        findings.append(Finding(section[:40], number, context, hits))
    return findings


def format_report(findings: list[Finding], show_all: bool) -> str:
    lines = []
    for f in findings:
        if f.hits and not show_all:
            continue
        lines.append(f"[{f.section}] {f.number} | {f.context}")
        if show_all:
            shown = "; ".join(f"{h.file}[{h.key}|{h.column}]" for h in f.hits[:MAX_HITS_SHOWN])
            extra = f" (+{len(f.hits) - MAX_HITS_SHOWN})" if len(f.hits) > MAX_HITS_SHOWN else ""
            lines.append(f"        -> {shown + extra if f.hits else 'NO MATCH'}")
    return "\n".join(lines) + ("\n" if lines else "")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", help="revision.toml (default: search upward from the current folder)")
    parser.add_argument("--tex", help="manuscript .tex (default: [paper] main_tex)")
    parser.add_argument("--results", nargs="*", help="CSV files or folders (default: [results] paths)")
    parser.add_argument("--glob", help="file pattern inside result folders (default *.csv)")
    parser.add_argument("--exclude", nargs="*", help="skip CSV files whose name contains any of these")
    parser.add_argument("--start", help="start marker (default: [paper] body_start)")
    parser.add_argument("--end", help="end marker (default: [paper] body_end)")
    parser.add_argument("--no-complement", action="store_true", help="do not accept 1 - value")
    parser.add_argument("--all", action="store_true", help="list every number with its matching cells")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any number is unmatched")
    parser.add_argument("--out", help="write the report here (default: print it)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args = parse_args(argv)
    config = load_config(args.config)
    tex = Path(args.tex) if args.tex else resolve(config, get(config, "paper.main_tex"))
    if tex is None:
        raise SystemExit("no manuscript: pass --tex or set [paper] main_tex in revision.toml")
    result_paths = ([Path(p) for p in args.results] if args.results
                    else [resolve(config, p) for p in get(config, "results.paths", [])])
    if not result_paths:
        raise SystemExit("no results: pass --results or set [results] paths in revision.toml")
    text = read_text(tex)
    warn_if_inputs(text, tex)
    body = prepare_body(text, args.start or get(config, "paper.body_start"),
                        args.end or get(config, "paper.body_end"))
    exclude = args.exclude if args.exclude is not None else get(config, "results.exclude", [])
    cells = load_cells(result_paths, args.glob or get(config, "results.glob", "*.csv"), exclude)
    complement = not args.no_complement and get(config, "results.complement", True)
    findings = audit(body, cells, complement)
    report = format_report(findings, args.all)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    unmatched = sum(1 for f in findings if not f.hits)
    print(f"numbers: {len(findings)}, matched: {len(findings) - unmatched}, unmatched: {unmatched}")
    return 1 if args.strict and unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
