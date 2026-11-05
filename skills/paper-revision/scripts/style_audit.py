"""Mechanical style checks of a LaTeX manuscript (prose only; math, comments and refs masked).

Each hit is printed as  TAG L<line> [rule] 'match': ...context...
TAG is PROT inside a protected range (text you may change only for real errors, e.g. a
coauthor's section; see [[style.protected]] in revision.toml) and OWN elsewhere.

Default rules: weak word, British spelling, colour name, contraction, digit below 10, plus
structure checks (section with one subsection, one-sentence paragraph, long sentence, list or
footnote in the main text). Optional rules ([style] enable): present perfect.
Project rules ([style.rules] name = 'regex', case-insensitive) add terminology or hyphenation.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from _common import get, load_config, read_text, resolve, use_utf8_stdout, warn_if_inputs

DEFAULT_RULES: dict[str, tuple[str, int]] = {
    "weak word": (r"\b(novel|superior|remarkable|significantly|clearly|obviously|worth noting"
                  r"|in order to|utiliz\w*|a number of|very)\b", re.I),
    "British spelling": (r"\b(centred|centre|normalis\w+|modelling|modelled|behaviour\w*"
                         r"|analys(e|ed|ing)\b|colour\w*|favour\w*|optimis\w+|generalis\w+"
                         r"|summaris\w+|characteris\w+|parametris\w+|randomis\w+|regularis\w+"
                         r"|recognis\w+|organis\w+|minimis\w+|maximis\w+)", re.I),
    "colour name": (r"\b(blue|red|green|orange|purple|black|grey|gray|yellow)\b", re.I),
    "contraction": (r"\b\w+n't\b|\b(it's|that's|let's)\b", re.I),
    "digit below 10": (r"(?<![\w.\-/{(\[$\\])([1-9])(?![\w.\-/}%:)\]$])", 0),
}
OPTIONAL_RULES: dict[str, tuple[str, int]] = {
    "present perfect": (r"\b(has|have) been\b", re.I),
}
# A digit right after one of these words is a reference ("Section 2"), not a count.
REFERENCE_WORDS = re.compile(
    r"(Section|Sections|Table|Tables|Figure|Figures|Fig\.|Appendix|Theorem|Lemma|Remark|Condition"
    r"|Assumption|Step|Eq\.|Equation|equation|Chapter|Corollary|Proposition|Definition|Example"
    r"|Algorithm|Case|Model|Scenario|Setting|level|order|line|page|p\.|pp\.)[~\s-]*$")
MATH_ENVS = r"equation|align|gather|multline|eqnarray|displaymath|math"
MATH_BEGIN = re.compile(r"\\begin\{(" + MATH_ENVS + r")\*?\}|^\s*\\\[")
MATH_END = re.compile(r"\\end\{(" + MATH_ENVS + r")\*?\}|\\\]")
# Display math (\[ ... \] and environments) is skipped line by line in _rule_hits; masking it
# here would turn a display line into a word and merge the paragraphs around it.
INLINE_MATH = re.compile(r"\$\$.*?\$\$|\$[^$]*\$|\\\(.*?\\\)")
REFS = re.compile(r"\\(label|ref|cref|Cref|eqref|autoref|cite[tp]?|citealp|citeauthor|includegraphics"
                  r"|url|href|input|include)\*?(\[[^\]]*\])*\{[^}]*\}")
STRUCTURAL = re.compile(r"\s*\\(begin|end|toprule|midrule|bottomrule|cmidrule|hline)\b")
LONG_SENTENCE_WORDS = 40
SHORT_PARAGRAPH_WORDS = 8


@dataclass(frozen=True)
class Hit:
    line: int
    tag: str
    rule: str
    match: str
    context: str


def build_rules(config: dict) -> dict[str, re.Pattern]:
    enabled = set(get(config, "style.enable", []))
    disabled = set(get(config, "style.disable", []))
    rules = {**DEFAULT_RULES, **{k: v for k, v in OPTIONAL_RULES.items() if k in enabled}}
    rules.update({name: (pattern, re.I) for name, pattern in get(config, "style.rules", {}).items()})
    compiled = {}
    for name, (pattern, flags) in rules.items():
        if name in disabled:
            continue
        try:
            compiled[name] = re.compile(pattern, flags)
        except re.error as error:
            raise SystemExit(f"[style.rules] {name!r}: invalid regex: {error}") from error
    return compiled


def prose(line: str) -> str:
    s = re.sub(r"(?<!\\)%.*$", "", line)
    s = INLINE_MATH.sub(" MATH ", s)
    return REFS.sub(" REF ", s)


def first_line(lines: list[str], marker: str | None, default: int, after: int = 0) -> int:
    if not marker:
        return default
    return next((i for i, l in enumerate(lines) if i >= after and marker in l), default)


def protected_ranges(lines: list[str], config: dict) -> list[tuple[int, int]]:
    ranges = []
    for item in get(config, "style.protected", []):
        start = first_line(lines, item.get("start"), -1)
        if start < 0:
            raise SystemExit(f"protected start marker not found: {item.get('start')!r}")
        end = first_line(lines, item.get("end"), -1, after=start + 1) if item.get("end") else len(lines) - 1
        if end < 0:
            raise SystemExit(f"protected end marker not found after its start: {item.get('end')!r}")
        ranges.append((start, end))
    return ranges


def _rule_hits(lines, rules, start, tag) -> list[Hit]:
    hits, in_math = [], False
    for i in range(start, len(lines)):
        raw = lines[i]
        if not in_math:
            begin = MATH_BEGIN.search(raw)
            if begin:
                in_math = not MATH_END.search(raw[begin.end():])
                continue
        else:
            in_math = not MATH_END.search(raw)
            continue
        s = prose(raw)
        if STRUCTURAL.match(s) or "&" in s:
            continue
        for name, pattern in rules.items():
            for m in pattern.finditer(s):
                if name == "digit below 10" and REFERENCE_WORDS.search(s[:m.start()]):
                    continue
                context = s[max(0, m.start() - 50):m.end() + 40].strip()
                hits.append(Hit(i + 1, tag(i), name, m.group(0), context))
    return hits


def _section_hits(lines, tag) -> list[Hit]:
    hits: list[Hit] = []
    section, subsections = None, 0
    for i, l in enumerate(lines + ["\\section{END}"]):
        if l.lstrip().startswith("\\section"):
            if section is not None and subsections == 1:
                hits.append(Hit(section + 1, tag(section), "section with one subsection", "",
                                lines[section].strip()[:80]))
            section, subsections = i, 0
        elif l.lstrip().startswith("\\subsection"):
            subsections += 1
    return hits


def _paragraph_hits(lines, start, max_words, tag) -> list[Hit]:
    hits: list[Hit] = []
    paragraph: list[str] = []
    para_start = start
    for i, raw in enumerate(lines[start:] + [""], start):
        s = prose(raw).strip()
        if s and not s.startswith("\\") and "&" not in s:
            if not paragraph:
                para_start = i
            paragraph.append(s)
            continue
        if not paragraph:
            continue
        text = " ".join(paragraph)
        sentences = [x for x in re.split(r"(?<=[.?!])\s+(?=[A-Z\\])", text) if x.strip()]
        if len(sentences) == 1 and len(text.split()) > SHORT_PARAGRAPH_WORDS:
            hits.append(Hit(para_start + 1, tag(para_start), "one-sentence paragraph", "", text[:110]))
        for sentence in sentences:
            n = len(sentence.split())
            if n > max_words:
                hits.append(Hit(para_start + 1, tag(para_start), f"long sentence ({n} words)",
                                "", sentence[:110]))
        paragraph = []
    return hits


def _list_hits(lines, start, main_end, tag) -> list[Hit]:
    return [Hit(i + 1, tag(i), "list or footnote in main text", "", lines[i].strip()[:80])
            for i in range(start, main_end)
            if re.search(r"\\begin\{(itemize|enumerate|description)\}|\\footnote", lines[i])]


def audit_file(tex: Path, config: dict) -> list[Hit]:
    text = read_text(tex)
    warn_if_inputs(text, tex)
    lines = text.split("\n")
    start = first_line(lines, get(config, "style.start", "\\begin{document}"), 0)
    main_end = first_line(lines, get(config, "style.main_end", "\\appendix"), len(lines))
    ranges = protected_ranges(lines, config)
    max_words = int(get(config, "style.max_sentence_words", LONG_SENTENCE_WORDS))

    def tag(i: int) -> str:
        return "PROT" if any(a <= i <= b for a, b in ranges) else "OWN"

    hits = (_rule_hits(lines, build_rules(config), start, tag) + _section_hits(lines, tag)
            + _paragraph_hits(lines, start, max_words, tag) + _list_hits(lines, start, main_end, tag))
    return sorted(hits, key=lambda h: (h.line, h.rule))


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tex", nargs="?", help="manuscript .tex (default: [paper] main_tex)")
    parser.add_argument("--config", help="revision.toml (default: search upward)")
    parser.add_argument("--own-only", action="store_true", help="hide hits in protected ranges")
    parser.add_argument("--strict", action="store_true", help="exit 1 when there are OWN hits")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    tex = Path(args.tex) if args.tex else resolve(config, get(config, "paper.main_tex"))
    if tex is None:
        raise SystemExit("no manuscript: pass a .tex file or set [paper] main_tex in revision.toml")
    hits = audit_file(tex, config)
    shown = [h for h in hits if not (args.own_only and h.tag == "PROT")]
    for h in shown:
        match = f" {h.match!r}:" if h.match else ""
        print(f"{h.tag} L{h.line} [{h.rule}]{match} ...{h.context}...")
    own = sum(1 for h in hits if h.tag == "OWN")
    print(f"hits: {len(hits)} (OWN {own}, PROT {len(hits) - own})")
    return 1 if args.strict and own else 0


if __name__ == "__main__":
    sys.exit(main())
