# The proposal loop: one change at a time, approved before it touches the tex

Load this before any change to the manuscript, the bibliography or the response letter.

## Why

The user (and often an advisor) owns every sentence of the paper. Editing first and reporting
later forces them to reverse-engineer a diff; a proposal they can read in two minutes, with
the evidence beside it, gets a fast and confident yes or no.

## The loop

1. **Investigate (read-only).** Read the section, the comment entry, the results, the cited
   papers. Nothing is edited yet.
2. **Write the proposal** into `revision/proposals/current.md` using `templates/proposal.md`:
   - ID `P-###` (next number; never reused, even for rejected proposals) and a short title;
   - the comment IDs and plan step it serves;
   - **location**: file, section, line number, and the opening words of the passage;
   - **original**: the full current text; **new**: the full proposed text — both rendered
     (math as `$…$` / `$$…$$` so the user reads formulas, not LaTeX);
   - **what changed** in a short list, and what was deliberately kept;
   - **basis**: every number → source file and row (CSV, log); every mathematical claim →
     equation, lemma, or paper and section; every citation → the original PDF in `papers/`;
   - **page impact** (estimated lines or pages);
   - **to confirm**: the questions the user must answer;
   - the exact LaTeX in a collapsed `<details>` block at the end.
3. **Tell the user in one line** that the proposal is in `current.md` (and its title). Do not
   paste LaTeX into the chat. Set the comment register row and the plan step to `proposed` and
   put the `P-###` in the register's Proposals column. When the proposal answers a comment,
   draft its reply as `references/response-letter.md` describes.
4. **Wait for an explicit OK.** "Looks good", "可以", "go" count; silence and questions do not.
   If the user edits the wording, use theirs. On the OK, the status becomes `approved`.
5. **Apply exactly what was approved** to the tex (or bib, or letter). Compile. Report the
   actual page change and any warning.
6. **Close it:** save the proposal as `proposals/P-###-<slug>.md` with
   `**Status:** applied` (or `rejected` with the reason), update the comment register row
   (`applied` once all of the comment's proposals are applied; Reply `draft`), log any decision
   in `decisions.md`, and commit with a
   message that names the change. Then overwrite `current.md` with the next proposal.

One step may need several proposals; handle them one at a time. Small, mechanical batches
(typos found by the style audit, reference formatting) may go in one proposal as a table of
location / original / new, if the user agrees to batch them.

## Things that always need a proposal

- Any change to protected text (`rules.md`): only for a real error, at word level, shown
  against the original.
- Any bibliography change: adding, removing, or editing an entry, or adding a `\cite`. The
  user decides what is cited. After a batch, ask the user to save the originals of new
  references into `papers/` so each citation can be checked against the source.
- Any change to a number, a theorem statement, or a figure.
- Anything that answers a reviewer: the reply in the letter is proposed together with the
  manuscript change it describes, so the two stay consistent.

## Drafting the new text

Before showing a proposal, reread the new text against `references/writing-rules.md`:
plain declarative sentences in the style of the surrounding text, no revision narrative,
placement right (theory / implementation / results), nothing claimed that the results do not
support, every formula of the original kept.
