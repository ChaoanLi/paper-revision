# Comment register (fictional example)

| ID | Letter label | Summary | Steps | Proposals | Status | Reply |
|---|---|---|---|---|---|---|
| AE-1 | AE comment 1 | what is new vs CUSUM-of-squares | S-01, S-05 | P-001 | applied | draft |
| AE-2 | AE comment 2 | heavy-tailed errors | S-03, S-06 | | todo | — |
| R1-1 | Comment 1 | how to choose the window $m$ | S-02, S-07 | | todo | — |
| R1-2 | Comment 2 | fair tuning in Table 2 | S-03, S-06 | | todo | — |
| R1-3 | Comment 3 | "significantly" on p. 4 | S-08 | P-002 | proposed | — |

## AE-1 — what is new relative to CUSUM-of-squares tests

**Letter label:** AE comment 1 · **Status:** applied · **Reply:** draft
**Overlaps:** none · **Steps:** S-01, S-05 · **Proposals:** P-001

**Quote**

> The contribution relative to existing CUSUM-of-squares tests is not clear. Please state
> precisely what is new in the test and in the theory, and what is taken from earlier work.

**Plain reading** — say exactly which parts are new and which are borrowed.

**Real worry** — that the paper repackages a known test with a permutation null and claims it
as new.

**Verdict** — agree: the introduction does not separate the two.

**Action** — add a short paragraph to the introduction: borrowed = the scan statistic form
(cite); new = the permutation null valid for short series and Theorem 1's finite-sample bound.
Mark Lemma 2 as adapted from the cited paper.

**Placement** — main (introduction, 4 lines) and letter. **Effort** — small.
**Risk** — Lemma 2 is closer to the cited result than the old text suggested; say so plainly.

## AE-2 — heavy-tailed errors

**Letter label:** AE comment 2 · **Status:** todo · **Reply:** —
**Overlaps:** R1-2 (same simulation table) · **Steps:** S-03, S-06 · **Proposals:** —

**Quote**

> The simulation study uses only Gaussian errors. Since the motivating data are daily
> returns, heavy-tailed errors should be considered.

**Plain reading** — rerun the simulation with $t_3$ (or similar) errors.

**Real worry** — the permutation test may lose its level or power exactly on the data the
paper is about.

**Verdict** — agree.

**Action** — add $t_3$ and $t_5$ errors to the size and power study (code repo, step S-03);
report the size in the main table, full results in the supplement.

**Placement** — main (one column of Table 2) + supp. **Effort** — medium.
**Risk** — power drops for $t_3$; acceptable if the level holds.
