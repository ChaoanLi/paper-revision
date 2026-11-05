# P-002 — "significantly larger" on page 4

**Status:** proposed
**Serves:** R1-3 · step S-08
**File:** `main.tex`, Section 2, line 131 ("The variance after the change …")
**Page impact:** none

## Original

> The variance after the change is significantly larger than before, so the scan window must
> cover both regimes.

## New

> The variance after the change is several times larger than before (a ratio of 4 in the
> example of Figure 1), so the scan window must cover both regimes.

## What changed

- "significantly" → "several times", with the ratio from Figure 1, so the word is not read as
  a statement about statistical significance.

## Basis

- Ratio 4 → `code/results/figure1_data.csv`, columns `sd_before` = 1.0 and `sd_after` = 2.0
  (variance ratio $2.0^2 / 1.0^2 = 4$).

## Reply in the letter

> **Response.** Thank you; we replaced "significantly larger" by "several times larger" and
> give the ratio (Section 2, \PH).

## To confirm

1. Is quoting the ratio of 4 useful here, or should the sentence stay without a number?

<details>
<summary>LaTeX to apply</summary>

```latex
The variance after the change is several times larger than before (a ratio of 4 in the example
of \Cref{fig:example}), so the scan window must cover both regimes.
```

</details>
