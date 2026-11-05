# Planning: ordered steps, placement, page budget

Load this after triage, when turning the comment register into work.

## Order of work

**Freeze the method → fix the code → run experiments → write → letter → checks → submit.**

- Method changes come first because they change every number. Once the user says the method
  is final, record it in `decisions.md` ("method frozen") and do not reopen it for a better
  result; sensitivity goes to a robustness section instead.
- No manuscript text for a part whose experiments are not finished. Drafting first and
  re-drafting after the numbers move is the most common waste in a revision.
- Run every analysis a reviewer requested, even if it ends up only in the letter: the letter
  can then report the result and say why it is or is not in the paper.
- Structural changes (moving sections, cutting a subsection) before wording.

## Steps

Write `plan.md` as one table, one row per step `S-01`, `S-02`, … in execution order. Each row:
the comment IDs it serves, what is done, where (file and section), placement, page impact,
dependencies, status. Rules:

- A step is small enough to finish and review in one sitting. Writing steps are usually one
  section or one reply.
- Every comment ID appears in at least one step, or its register entry says why not (reply only).
- Group by phase (decide, method and code, experiments, writing, letter, checks, submit), not
  by reviewer.
- Keep a "Next" list at the bottom with the next two or three actions; update it at the end of
  every session.

## Placement

For each addition decide where it goes before writing it:

| Kind of content | Goes to |
|---|---|
| What is mathematically true and under which conditions | theory section (theorem, remark) |
| What to do in practice, defaults, why in one sentence | method / implementation section |
| Numbers (sizes, power, sensitivity, timing) | results sections, tables |
| Checks done only because a reviewer asked | supplement; one pointer sentence in the main text at most |
| Why something changed since the first version | the letter only, never the paper |

One reviewer question is often answered in two or three of these places at once.

## Page budget

Do this once, early, not three times late.

1. Measure the current length against the limit, counted the way the journal counts
   (check `rules.md`: references, captions, appendices included or not). Compile the manuscript
   (`latexmk -pdf main.tex` in the venue folder, or download the PDF from Overleaf) and point
   `[paper] pdf` in `revision.toml` at it; `status.py` then reports pages against the limit.
   If the journal counts only part of the PDF (e.g. main text plus references), note the page
   where counting stops.
2. List planned additions with estimated size.
3. Pair every main-text addition with a cut that pays for it; write both in `plan.md`.
4. Cut in tiers: (1) no change to numbers, math or citations (wording, duplicate sentences,
   moving checks to the supplement); (2) needs a decision (drop a figure, a remark, a
   comparison). Tier 2 goes to the user as a list.
5. After a large cut, one restore pass: diff against the version before the cut
   (`math_audit.py` lists dropped formulas and citations) and restore anything that a reader or
   reviewer will miss.

Never cut protected text, protected references (`rules.md`), or a formula; moving a display
inline is fine.
