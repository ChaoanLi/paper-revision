# Decisions (fictional example)

Append-only. Newest at the bottom.

## Open questions

| ID | Question | Recommendation | Needed by |
|---|---|---|---|
| Q-1 | Choose $m$ by the rule $\lceil n^{1/2}\rceil$ or keep $m = 20$? | the rule, if the size stays within 0.04–0.06 | S-02 |

## Log

## 2027-03-04 — What the paper claims as new
- **Decided by:** user, with the advisor
- **Decision:** new = the permutation null for short series and the finite-sample bound in
  Theorem 1; the scan statistic is borrowed and cited; Lemma 2 is labelled "adapted from".
- **Why:** AE-1 asks for exactly this split; S-01.

## 2027-03-05 — Heavy tails in the main table, details in the supplement
- **Decided by:** user
- **Decision:** add $t_3$ and $t_5$ columns for the size only; power curves go to Supplement S2.
- **Why:** AE-2 and R1-2; keeps the main text within the page limit (plan.md, page budget).
