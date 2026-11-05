# P-001 — Introduction: what is new and what is borrowed

**Status:** applied (2027-03-06, commit "docs: introduction separates new and borrowed results")
**Serves:** AE-1 · step S-05
**File:** `main.tex`, Section 1, line 48 ("Scan statistics have a long history …")
**Page impact:** +4 lines (measured after compiling: +0.15 pages)

## Original

> Scan statistics have a long history in change detection. We propose a permutation scan test
> for a change in variance and study its properties.

## New

> Scan statistics have a long history in change detection. We propose a permutation scan test
> for a change in variance and study its properties. The statistic $S_m = \max_t |V_{t,m}|$ is
> the CUSUM-of-squares scan of Smith and Lee (2019); our contribution is its permutation null,
> which is exact for series of any length, and the finite-sample bound on the power in
> Theorem 1. Lemma 2 is adapted from their Lemma 3 to windows that overlap.

## What changed

- adds two sentences that separate the borrowed statistic from the new null and theory;
- labels Lemma 2 as adapted (AE-1 asked "what is taken from earlier work");
- the first two sentences are unchanged.

## Basis

- "exact for series of any length" → Proposition 1 (permutation invariance under $H_0$).
- Smith and Lee (2019) → `papers/SmithLee_2019_ScanCUSUM.pdf`, Section 2, eq. (4); Lemma 3, p. 9.

## Reply in the letter

> **Response.** The statistic itself is the scan of Smith and Lee (2019); what is new is its
> permutation null, exact for short series, and the finite-sample power bound of Theorem 1.
> The introduction now says this (Section 1, \PH), and Lemma 2 is labelled as adapted from
> their Lemma 3.

<details>
<summary>LaTeX to apply</summary>

```latex
Scan statistics have a long history in change detection. We propose a permutation scan test
for a change in variance and study its properties. The statistic $S_m=\max_t|V_{t,m}|$ is the
CUSUM-of-squares scan of \citet{smith2019scan}; our contribution is its permutation null,
which is exact for series of any length, and the finite-sample bound on the power in
\Cref{thm:power}. \Cref{lem:overlap} is adapted from Lemma~3 of \citet{smith2019scan} to
windows that overlap.
```

</details>
