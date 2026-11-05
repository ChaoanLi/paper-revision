---
name: paper-revision
description: Run a journal revise-and-resubmit for a LaTeX paper end to end. Sets up a local-only revision workspace, turns the decision letter and reviewer reports into a comment register with stable IDs, orders the work (method, code, experiments, writing), proposes every manuscript change one at a time for the author's approval, drafts the point-by-point response letter, runs mechanical checks (numbers against result CSVs, formulas and citations kept, style, page budget, latexdiff), simulates a second-round review, and assembles the resubmission. Use when the user has received reviews, a major or minor revision, or an R&R decision, or asks for a revision plan, a response to reviewers, or a rebuttal letter.
license: MIT
---

# Paper revision (revise and resubmit)

A working method for answering reviewers on a LaTeX paper kept in git, with the author in
control of every sentence. It assumes a manuscript repository (often synced with Overleaf), a
separate code repository that produced the numbers, and a local folder of notes.

## Golden rules

1. **No change to the manuscript, bibliography or letter without an approved proposal.**
   Investigate freely; edit only after the user's explicit OK. See `references/proposals.md`.
2. **One proposal at a time**, in `revision/proposals/current.md`, with math rendered and the
   LaTeX in a collapsed block. The chat gets one line saying it is there.
3. **Every number, claim and citation in a proposal has a source**: result file and row,
   equation or theorem, original PDF and page.
4. **Stable IDs, one status vocabulary.** Comments `ED-1`, `AE-1`, `R1-1`, `R2-M1`; steps
   `S-01`; proposals `P-001`; open questions `Q-1`. Never reuse an ID. Status: `todo · proposed
   · approved · applied · rejected · deferred` — a comment or step is `proposed` once its
   proposal is in `current.md`, `approved` on the user's OK, `applied` when the edit is made,
   `deferred` while it waits for an answer to a `Q-`.
5. **Order: freeze the method → code → experiments → writing → letter → checks → submit.**
   No text is drafted for results that are not final.
6. **Reviews stay private.** `revision/` and `papers/` are never committed or shared.
7. **The author decides** what is cited, what is declined, and any change to protected text
   (an advisor's or coauthor's). Record each decision in `revision/decisions.md` when made, and
   each rule the user states in `revision/rules.md` with its date.
8. **Omission is allowed, fabrication never.** Flag any omission that would make a stated
   claim false.
9. **Say only what was verified.** Do not report "pushed", "Overleaf updated", "compiles" or
   "all comments answered" without checking.

`<skill>` in these files means the folder that holds this SKILL.md. Claude Code sets
`${CLAUDE_SKILL_DIR}` to it; if that variable is empty, use the folder path itself.

## Start of every session

1. `python "<skill>/scripts/status.py"` from the paper repository or the venue folder (or
   `--config <venue>/revision/revision.toml`). If there is no config, go to phase 0.
2. Read `revision/rules.md`, the last entries of `revision/decisions.md`, and
   `revision/proposals/current.md`.
3. Check `git status`; pull if coauthors or Overleaf may have changed the paper.
4. Tell the user in two or three lines where things stand and what is next (from `plan.md`).

## Phases

| # | Phase | Main output | Load |
|---|---|---|---|
| 0 | Set up the workspace, work branch, tag the submitted version | `revision/`, `.gitignore`, tag `submitted-v1` | `references/setup.md` |
| 1 | Intake: decision letter and reports, verbatim, with IDs | `revision/original/*.md` | `references/intake-and-triage.md` |
| 2 | Triage: reading, real worry, verdict, action, placement | `revision/comments.md`, overview to the user | `references/intake-and-triage.md` |
| 3 | Plan: ordered steps, placement, page budget, decisions | `revision/plan.md`, `revision/decisions.md` | `references/planning.md` |
| 4 | Method, code, experiments (in the code repository) | results files, frozen method | `references/planning.md` |
| 5 | Write: one proposal per change, with its letter reply | `proposals/P-###-*.md`, edited tex | `references/proposals.md`, `references/writing-rules.md`, `references/response-letter.md` |
| 6 | Letter: reply drafted with each change, then finalized | `response/response_letter.tex` | `references/response-letter.md` |
| 7 | Checks: numbers, math, style, citations, pages, latexdiff | `revision/checks/` | `references/checks.md` |
| 8 | Mock re-review by simulated original reviewers | `revision/mock-review/` | `references/checks.md` |
| 9 | Submit and wrap up | package, tag `resubmitted-v2` | `references/submission.md` |

Load a reference file when its phase starts, not all at once. When the user arrives mid-way
(notes already exist), map their files onto this structure in conversation and continue; move
or rename their files only if they ask.

## Files

All under `<venue>/revision/` (created by `init_project.py`; never committed):

| File | Role |
|---|---|
| `revision.toml` | paths, section markers, limits, audit settings (read by every script) |
| `rules.md` | journal requirements quoted with sources, protected text, positioning, user rules |
| `original/` | decision letter and reports, verbatim, one file each |
| `comments.md` | comment register: the table `status.py` reads, then one entry per comment |
| `plan.md` | phases, steps `S-xx`, page budget, next actions |
| `decisions.md` | append-only, dated decisions; open questions `Q-n` |
| `proposals/current.md`, `proposals/P-###-slug.md` | the open proposal; every proposal with its final status |
| `checks/`, `mock-review/`, `archive/` | tool outputs; simulated reviews; anything superseded |

Templates for new entries are in `templates/` (`comment-entry.md`, `proposal.md`,
`response_letter.tex`, `mock-review-persona.md`).

## Scripts

Python 3.11+, standard library only. Run with `python "<skill>/scripts/<name>.py"`; each has
`--help` and reads `revision.toml` (searched upward from the current folder, and in
`<venue>/revision/` below it).

| Script | Does |
|---|---|
| `init_project.py <venue> [--main-tex F] [--dry-run]` | creates `revision/`, `papers/requirements/`, the `.gitignore` block; never overwrites |
| `status.py` | comments by status, open IDs, replies not final, proposals, decisions, `\PH` left, pages, days to deadline |
| `number_audit.py [--all] [--strict]` | decimals in the text without a matching value in the result CSVs |
| `math_audit.py OLD NEW` | formulas and citations dropped between versions (`git:submitted-v1:main.tex` works) |
| `style_audit.py [--own-only]` | mechanical style checks; hits in protected text tagged PROT |
| `latexdiff.py [-- latexdiff options]` | marked-changes PDF of the submitted tag against the working tree |
| `anonymize_code.py REPO OUT.zip` | anonymous code supplement; refuses to write while names or e-mails remain |

Script output is evidence for the user, not a verdict: report what it found, explain or fix
each item through a proposal.

## Working with the user

- Answer in the user's language. Notes in `revision/` follow the user's preference; the
  manuscript and the letter are in the paper's language.
- When a decision is needed, give the options with a recommendation and its reason, then
  record the answer in `decisions.md`.
- Keep chat short; details go into the files. Point to the file and section.
- When the user corrects you, add the rule to `rules.md` (dated, in their words) and apply it
  from then on. If it would help any paper, mention that it could become a rule of this skill.

## Related skills

- **paper-audit** (if installed): figure–text, code–paper and redundancy passes in phase 7.
- **academic-code-release** (if installed): tidy and document the code repository before the
  anonymous package in phase 9.

## Out of scope

Writing a new paper from scratch, choosing what to cite on the author's behalf, and anything
that would invent data, results or reviewer statements.
