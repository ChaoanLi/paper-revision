# Revision plan (fictional example)

Order of work: **freeze the method → code → experiments → writing → letter → checks → submit.**

## Steps

| Step | Comments | What | Where | Placement | Pages ± | Depends on | Status |
|---|---|---|---|---|---|---|---|
| S-01 | AE-1 | Decide what is claimed as new; list borrowed results | decisions.md | — | 0 | — | applied |
| S-02 | R1-1 | Data-driven rule for $m$; freeze the method | code repo | — | 0 | S-01 | todo |
| S-03 | AE-2, R1-2 | Rerun size/power: $t_3$, $t_5$ errors; tune both tests the same way | code repo | — | 0 | S-02 | todo |
| S-04 | — | Page budget: measure, pair additions with cuts | plan.md | — | 0 | S-03 | todo |
| S-05 | AE-1 | Introduction: new vs borrowed paragraph | main.tex §1 | main | +0.2 | S-01 | applied |
| S-06 | AE-2, R1-2 | Table 2 and its paragraph; supplement Section S2 | main.tex §5, supp | main + supp | +0.3 | S-03 | todo |
| S-07 | R1-1 | Rule for $m$ in §3.3; sensitivity in supplement | main.tex §3.3, supp | main + supp | +0.1 | S-02 | todo |
| S-08 | R1-3 | Wording | main.tex p. 4 | main | 0 | — | proposed |
| S-09 | all | Letter: cover note, fill `\PH`, final read | response_letter.tex | letter | — | S-05–S-08 | todo |
| S-10 | all | Checks, latexdiff, mock re-review | revision/checks | — | — | S-09 | todo |

S-06 and S-07 are writing steps; they wait for S-02 and S-03 because their numbers are not final.

## Page budget

Limit 25 pages including references (journal page, saved 2027-03-03). Measured 2027-03-04:
24.6 pages. Planned additions +0.6; paired cut: move the second robustness figure to the
supplement (−0.5) and shorten §2 (−0.2).

## Next

- P-002 (R1-3 wording) is waiting for the user's OK in `proposals/current.md`.
- S-02: compare the rule $m = \lceil n^{1/2} \rceil$ with the fixed $m = 20$; ask the user to freeze.
