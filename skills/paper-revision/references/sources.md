# Sources

What the workflow borrows from, so the rules can be checked and the user can read further.
Links were checked on 2026-11-05.

## Guidance on responding to reviewers (rules used in `response-letter.md`)

- Noble, W. S. (2017). Ten simple rules for writing a response to reviewers. *PLOS
  Computational Biology* 13(10): e1005730. https://doi.org/10.1371/journal.pcbi.1005730
  — overview first; full quotes; split multi-part comments; self-contained letter quoting the
  new text with locations; distinct typography for comment, reply and new text; answer
  directly; a misreading means the text was unclear; run requested analyses even if they stay
  out of the paper; write the reply twice.
- Taylor & Francis Author Services. How to respond to reviewer comments.
  https://authorservices.taylorandfrancis.com/blog/peer-review/how-to-respond-to-reviewer-comments/
  — quote comments in full; structural changes before wording; log changes as you make them;
  old and new figures; decline politely with reasons.
- PLOS Biology. Revising your manuscript.
  https://journals.plos.org/plosbiology/s/revising-your-manuscript
  — response letter, clean manuscript, and a version with changes marked.

## Project organization

- Wilson, G., Bryan, J., Cranston, K., Kitzes, J., Nederbragt, L., Teal, T. K. (2017). Good
  enough practices in scientific computing. *PLOS Computational Biology* 13(6): e1005510.
  https://doi.org/10.1371/journal.pcbi.1005510 — plain-text manuscripts under version
  control; separate raw data, code, results and documents.

## Tools

| Tool | Use in this workflow | Link |
|---|---|---|
| latexdiff | marked-changes PDF (`latexdiff.py` wraps it) | https://ctan.org/pkg/latexdiff · https://github.com/ftilmann/latexdiff |
| git-latexdiff | the same, directly from git revisions (Linux/macOS) | https://gitlab.com/git-latexdiff/git-latexdiff |
| chktex | LaTeX lint (ships with TeX Live) | https://ctan.org/pkg/chktex |
| TeXtidote | spelling and grammar of LaTeX via LanguageTool | https://github.com/sylvainhalle/textidote |
| Vale | configurable prose linter, if you want house rules beyond `style_audit.py` | https://github.com/vale-cli/vale |
| jourrr | a LaTeX class for response letters, an alternative to the template here | https://ctan.org/pkg/jourrr |
| rejoinderoo | builds a response letter from a spreadsheet of comments | https://github.com/andreas-bauer/rejoinderoo |
| showyourwork | reproducible paper-and-code builds | https://github.com/showyourwork/showyourwork |
| cookiecutter-data-science | a standard layout for the code repository | https://github.com/drivendataorg/cookiecutter-data-science |

## Further reading (not checked page by page; no rule here is attributed to them)

- Higham, N. J. (2020). *Handbook of Writing for the Mathematical Sciences*, 3rd ed. SIAM.
  Chapters on revising a draft and on refereeing.
- Belcher, W. L. (2019). *Writing Your Journal Article in Twelve Weeks*, 2nd ed. University of
  Chicago Press. Includes drafting the revision cover letter.
- Williams, J. M., Bizup, J. *Style: Lessons in Clarity and Grace*. Pearson. Sentence-level
  clarity (old information before new; characters as subjects, actions as verbs).
- Annesley, T. M. (2011). Top 10 tips for responding to reviewer and editor comments.
  *Clinical Chemistry* 57(4): 551–554.

## Origin of the house rules

The rules in `writing-rules.md`, the proposal loop, and the file layout come from a complete
revise-and-resubmit of a statistics methods paper (LaTeX, Overleaf, a separate code repository,
double-anonymous review, a page limit), where each rule was written down after a concrete
correction by the authors.
