# Submission package and wrap-up

Load this when all proposals are applied and the checks are clean.

## The package

Usually (confirm against `rules.md`, the journal decides):

1. **Clean revised manuscript** (PDF, and source if the journal wants it), anonymized if the
   review is double-anonymous.
2. **Marked version**: `latexdiff.py` output, or the manuscript with new material in colour if
   the journal or the user prefers that (a `\newmaterial` environment in the tex, switched off
   for the clean version).
3. **Response letter** PDF.
4. **Supplement** (if separate) and **code/data**: for anonymous review build the zip with
   `anonymize_code.py <code repo> revision/checks/code_anonymous.zip`; it refuses to write the
   zip while any forbidden string (names, institution, URLs, e-mail) is left. If the
   `academic-code-release` skill is installed, use it to tidy the code repository first.
5. **Statements** the journal requires (funding, disclosure, data availability, generative-AI
   use). The AI-use declaration must be truthful; its wording is the user's decision.

## Final checklist

Copy into `revision/checks/final-checklist-YYYY-MM-DD.md` and tick with evidence.

- [ ] `status.py`: no open comments, every reply `final`, no `\PH`, pages within the limit
- [ ] Number, math and style audits rerun on the final tex; every remaining item explained
- [ ] latexdiff PDF built from `submitted-v1` against the final commit
- [ ] Letter: every comment quoted in full and answered; quoted new text matches the paper
- [ ] Locations in the letter checked against the final PDF
- [ ] Citations added in the revision checked against the original PDFs
- [ ] Figures regenerated from the final code; captions match
- [ ] Anonymity: PDF metadata (`pdfinfo`), acknowledgements, self-citations, code package
- [ ] Required statements present, in the template's order
- [ ] Bibliography compiles without warnings; no undefined references (`grep -c undefined *.log`)
- [ ] Final commit pushed; Overleaf (if used) shows it (`git log -1 origin/main`)
- [ ] Tag `resubmitted-v2` on the commit that was submitted

## Wrap-up

After submitting:

- Tag the commit (`git tag resubmitted-v2`), push tags.
- Move working notes that are finished into `revision/archive/`; keep `original/`,
  `comments.md`, `decisions.md` and `proposals/` as they are — the next round starts from them.
- Write a short `revision/README.md` "state" section: what was submitted, when, and what is
  pending (e.g. the code repository to make public on acceptance).
- If the skill's rules missed something this time, note it for the next revision (a user rule
  in `rules.md`, or an issue on the skill's repository).
