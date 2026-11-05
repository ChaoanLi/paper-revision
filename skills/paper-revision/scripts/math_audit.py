"""List math expressions and citation keys of an old version that are missing from the new one.

Use it after condensing or rewriting a section: every formula of the old text should still be
there (moving a display inline is fine; \\frac{a}{b} written as a/b is accepted), and every
dropped or added citation should be a decision, not an accident.

OLD and NEW are file paths or git:REV:path (path relative to the current folder), e.g.
    python math_audit.py git:submitted-v1:main.tex main.tex --start "\\section{Introduction}"
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass

from _common import (get, load_config, read_source, slice_between, strip_comments,
                     use_utf8_stdout, warn_if_inputs)

MATH_ENVS = (r"equation\*?|align\*?|alignat\*?|flalign\*?|gather\*?|multline\*?|eqnarray\*?"
             r"|displaymath|math")
INLINE_MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$|\\\[(.+?)\\\]|\\\((.+?)\\\)", re.S)
DISPLAY_MATH = re.compile(r"\\begin\{(" + MATH_ENVS + r")\}(.+?)\\end\{\1\}", re.S)
CITE = re.compile(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}")
FRAC = re.compile(r"\\frac\{(.+?)\}\{(.+)\}")
PREVIEW = 150


@dataclass(frozen=True)
class Report:
    missing_math: list[str]
    dropped_citations: list[str]
    added_citations: list[str]

    @property
    def clean(self) -> bool:
        return not (self.missing_math or self.dropped_citations)


def normalize(expression: str) -> str:
    """Drop labels, sizing and spacing so that cosmetic edits do not count as changes."""
    s = re.sub(r"\\label\{[^}]*\}", "", expression)
    for token in (r"\left", r"\right", r"\,", r"\;", r"\!", r"\quad", r"\qquad"):
        s = s.replace(token, "")
    return re.sub(r"[{}\s]", "", s)


def math_expressions(text: str) -> list[str]:
    """Display and inline math of the text; comments and escaped dollars are ignored."""
    text = strip_comments(text).replace(r"\$", " ")
    displays = [m.group(2) for m in DISPLAY_MATH.finditer(text)]
    without_displays = DISPLAY_MATH.sub(" ", text)
    inline = [next(g for g in m.groups() if g is not None)
              for m in INLINE_MATH.finditer(without_displays)]
    return displays + inline


def citations(text: str) -> set[str]:
    keys: set[str] = set()
    for match in CITE.finditer(strip_comments(text)):
        keys.update(k.strip() for k in match.group(1).split(",") if k.strip())
    return keys


def compare(old: str, new: str) -> Report:
    # Search only the new version's math (not its prose or comments); "|" keeps expressions apart.
    new_norm = "|".join(normalize(m) for m in math_expressions(new))
    missing: list[str] = []
    for expression in math_expressions(old):
        key = normalize(expression)
        if not key or key in new_norm:
            continue
        if normalize(FRAC.sub(r"\1/\2", expression)) in new_norm:
            continue
        cleaned = expression.strip()
        if cleaned not in missing:
            missing.append(cleaned)
    old_cites, new_cites = citations(old), citations(new)
    return Report(missing, sorted(old_cites - new_cites), sorted(new_cites - old_cites))


def format_report(report: Report) -> str:
    lines = [f"math missing from the new text: {len(report.missing_math)}"]
    lines += ["   " + m[:PREVIEW].replace("\n", " ") for m in report.missing_math]
    lines.append(f"citations dropped: {report.dropped_citations}")
    lines.append(f"citations added: {report.added_citations}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("old", help="old version: file or git:REV:path")
    parser.add_argument("new", help="new version: file or git:REV:path")
    parser.add_argument("--config", help="revision.toml for default markers")
    parser.add_argument("--start", help="start marker (default: [paper] body_start)")
    parser.add_argument("--end", help="end marker (default: [paper] body_end)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when math or citations were dropped")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    start = args.start or get(config, "paper.body_start")
    end = args.end or get(config, "paper.body_end")
    old_text, new_text = read_source(args.old), read_source(args.new)
    warn_if_inputs(new_text, args.new)
    old, _ = slice_between(old_text, start, end)
    new, _ = slice_between(new_text, start, end)
    report = compare(old, new)
    print(format_report(report))
    return 1 if args.strict and not report.clean else 0


if __name__ == "__main__":
    sys.exit(main())
