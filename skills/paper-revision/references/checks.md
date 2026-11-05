# Checks and the mock re-review

Load this when the writing is done (and after any large edit). Save each tool's output in
`revision/checks/<tool>-YYYY-MM-DD.txt`; report findings to the user as a short prioritized
list, and turn each accepted fix into a proposal.

Scripts are in `<skill>/scripts/` (Python 3.11+, standard library only). Each takes `--help`,
reads `revision/revision.toml`, and accepts flags that override it.

## Mechanical checks

| Check | Command | What it catches |
|---|---|---|
| Status | `status.py` | open comments, replies not final, `\PH` left, pages vs limit, days left |
| Numbers | `number_audit.py [--all]` | every decimal in the text without a matching value in the result CSVs (rounding, 1 − p, and percentages accepted); `--all` lists the matching file/row/column for each number, for a line-by-line check of the results sections |
| Math and citations kept | `math_audit.py git:submitted-v1:main.tex main.tex` | formulas of the old text missing from the new one; citations dropped or added |
| Style | `style_audit.py [--own-only]` | weak words, British spelling (switch off if the journal uses it), colour names in text, contractions, small numbers as digits, long sentences, one-sentence paragraphs, single subsections, lists or footnotes in the main text, plus project rules (terminology, hyphenation) from `[style.rules]`; hits in protected text are tagged PROT |
| Marked changes | `latexdiff.py` | builds the latexdiff PDF of `submitted-v1` against the working tree in a temporary folder |
| LaTeX lint | `chktex -q main.tex` (TeX Live) | spacing, dashes, quotes, `\ref` without `~` |
| Grammar (optional) | `textidote --check en main.tex` | spelling and grammar via LanguageTool, HTML report |

The number audit reports candidates, not verdicts: an unmatched number may be a constant, a
setting, or a derived quantity. Explain each one in the check file (e.g. "0.0365 = Monte Carlo
band 0.05 − 1.96·√(0.05·0.95/1000)") or fix it.

## Reading checks (by Claude, with evidence)

- **Every comment answered**: walk the register; for each ID, the manuscript location and the
  letter reply both exist and say the same thing.
- **Citations against originals**: for every citation added or moved during the revision, open
  the PDF in `papers/` and confirm the cited result is where and what the text says
  (theorem number, assumption, year, venue). List references whose PDFs are missing.
- **Math re-check** of new or changed derivations: each step follows; conditions stated; no
  result claimed as new that is borrowed (label borrowed / adapted / new).
- **Claims vs results**: each sentence about performance is supported by the numbers it
  points to, including any qualifier ("in all settings", "for n ≥ 100").
- **Code ↔ paper**: defaults, sample sizes, replication counts, and formulas in the text
  match the code that produced the numbers. If the `paper-audit` skill is installed, run it
  for figure–text, code–paper and redundancy passes.
- **Journal format**: required statements present and in the template's order; anonymity;
  bibliography style; figure and caption rules (`rules.md`).
- **Pages**: final count against the limit, counted as the journal counts.

## Mock re-review (before submission)

A simulated second round catches what the real reviewers will check first: whether *their*
comments were answered.

1. Start one subagent per original reviewer (AE, R1, R2, …) with
   `templates/mock-review-persona.md`. Each gets: its own original report, the final letter,
   the revised PDF (or tex), and the latexdiff. Each works independently, read-only.
2. Each report: likely recommendation; a status table of its own first-round comments
   (resolved / partly / not, with the evidence checked); new concerns from a fresh read;
   prioritized changes (must / should / optional), each with a location and a paired cut if
   it adds text.
3. Merge the reports in `revision/mock-review/summary.md` into four buckets:
   **must fix** (raised by two or more personas, or verified), **your call** (needs the
   user's judgement), **optional**, **pages**. Mark each item ✔ verified against code, CSV or
   git, or △ needs judgement.
4. Turn accepted items into proposals as usual. Mock findings that are unfavourable to the
   paper are reported to the user; whether to address them is the user's call
   (`writing-rules.md`, "omission vs fabrication").
