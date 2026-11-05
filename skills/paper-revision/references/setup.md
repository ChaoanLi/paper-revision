# Setup: folder layout, naming, git, Overleaf

Load this when starting a revision, or when the user asks where something belongs or whether to
commit it.

## Folder layout

```
<paper-repo>/                      git; GitHub main ↔ Overleaf (if used)
  README.md                        what is where, what is not tracked and why
  <venue>/                         one folder per version: journal/, arxiv/, thesis-chapter/ …
    main.tex  bibliography.bib     manuscript (the journal template's own file name is fine)
    main.pdf  main.bbl             tracked: Overleaf and coauthors need them
    plots/                         figures used by the tex (copied from the code repo's output)
    journal-template/              the template exactly as downloaded; never edited
    response/response_letter.tex   the letter (tracked; it is part of the submission)
    code/      → its own git repo  NOT tracked here (gitignored); anonymous zip made from it
    papers/                        NOT tracked: reference PDFs, own submitted version, journal pages
      requirements/                saved copies of the journal's instructions (HTML/PDF)
    revision/                      NOT tracked: confidential reviews and working notes
```

`python <skill>/scripts/init_project.py <venue> --main-tex main.tex` creates `revision/`,
`papers/requirements/` and the `.gitignore` block. It never overwrites a file.

## Phase 0 checklist

1. Find the commit the reviewers read and tag it: `git tag submitted-v1 <commit>`. If unsure,
   compare the submitted PDF with `git log -- <venue>/main.pdf`, or ask the user.
2. Make sure `papers/` holds the submitted PDF (reviewers' page numbers refer to it). If there
   is none, build it from the tag in a separate folder:
   `git worktree add ../submitted-v1 submitted-v1`, compile there, copy the PDF to `papers/`
   with the `_submitted-YYYY-MM-DD` suffix, then `git worktree remove ../submitted-v1`.
3. Create the work branch from the default branch (`main` or `master`):
   `git switch -c revision`.
4. Run `init_project.py`. Show the user the `.gitignore` block it appended and, with their OK,
   commit it alone: `chore: keep revision notes and reference PDFs out of git`.
5. Run `status.py` once to confirm the config is found.

**Why reviews stay out of git:** reports are confidential, and a paper repo is often shared
with coauthors or synced to Overleaf. Keep `revision/` in a cloud-synced folder (OneDrive,
Dropbox, iCloud) or a separate private repository so it is backed up.

## Naming

| Thing | Pattern | Example |
|---|---|---|
| Reference paper | `AuthorAuthor_Year_ShortTitle.pdf` (≤3 surnames, then `EtAl`) | `SmithJones_2019_KernelTests.pdf` |
| Preprint / supplement | add `_preprint`, `_supp` | `LeeEtAl_2027_Bounds_supp.pdf` |
| Own submitted version | `<Authors>_<Year>_<Short>_submitted-YYYY-MM-DD.pdf` | reviewers' page numbers refer to it |
| Journal instructions | `papers/requirements/<page title>.html` | save the page; it may change |
| Comment IDs | `ED-n`, `AE-n`, `R1-n`, `R2-Mn`/`R2-mn` | see `comments.md` |
| Plan steps | `S-01`, `S-02`, … | one counter for the whole revision |
| Proposals | `P-001-<slug>.md` | one counter; never reused |
| Check outputs | `checks/<tool>-YYYY-MM-DD.txt` | `checks/numbers-2027-02-01.txt` |
| Git tags | `submitted-v1`, `resubmitted-v2`, … | the base for latexdiff |

Rename reference PDFs on download; check each citation against the original PDF, not memory.

## Git

- Work on a branch (e.g. `revision`), not on the default branch (`main` or `master`). Commit
  small, one change per commit.
- Commit messages: conventional prefixes and a plain subject that says what changed in the
  paper: `docs: shorten Section 2 and relate the test to earlier work`,
  `fix: sign error in equation (7)`, `chore: rebuild PDF`.
- Do not add AI co-author trailers unless the user wants them; ask once and record the answer
  in `rules.md`.
- **Tag the submitted version in phase 0** (checklist above); every diff and audit compares
  against `submitted-v1`.
- Keep the code repository separate; record which code commit produced the paper's numbers
  (a tag such as `paper-v2`) in `decisions.md`.

## Overleaf

Overleaf's GitHub sync reads **one branch, usually the default one**. When the user says
"push":

1. `git fetch`; check that `origin/main` is an ancestor of the work branch
   (`git merge-base --is-ancestor origin/main HEAD`).
2. Push the branch and fast-forward main: `git push origin <branch> <branch>:main`.
3. Verify with `git log -1 origin/main`. Never tell the user Overleaf is updated without this.

If coauthors edit on Overleaf, pull ("Updates from Overleaf" commits) before every local edit
session, and never rewrite history that Overleaf has seen.

## Session start

At the start of every session on a revision:

1. `python <skill>/scripts/status.py` (finds `revision/revision.toml` from the repository root
   or the venue folder).
2. Read `revision/rules.md`, the last entries of `decisions.md`, and `proposals/current.md`.
3. `git status` and `git log -5` in the paper repo; pull if Overleaf may have changed.
