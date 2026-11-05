# Intake and triage: from the decision letter to the comment register

Load this when the user has just received a decision, or pastes reviewer comments.

## 1. Intake (verbatim, no interpretation yet)

1. Save the decision email as `revision/original/decision-letter.md`, and each report as its own
   file (`AE.md`, `R1.md`, …). Reports that came as PDF: keep the PDF next to a markdown
   transcription. Header lines: `Source:` and `Received: YYYY-MM-DD`.
2. Assign IDs in the transcription by adding `**R1-3**` before each comment. Keep the
   reviewer's own numbering; add, never remove. Editor's procedural requests (data, code,
   formatting, deadline) become `ED-1`, `ED-2`, ….
3. Record in `revision.toml`: `deadline` and `page_limit`. Save the journal's author
   instructions into `papers/requirements/` and quote the binding sentences in `rules.md` (word
   or page limit, what counts, anonymity, required statements, supplement and code rules, any
   AI-use declaration, whether an extension must be requested before the deadline). A value the
   user only stated in chat goes into `rules.md` as "source: user, YYYY-MM-DD; to verify
   against the journal page", and becomes an open question until checked.
4. Check that phase 0 is done: tag `submitted-v1` exists and the submitted PDF is in `papers/`.

If something is missing — no decision letter (only reports were forwarded), a report that
arrived only as a PDF, no submitted PDF — record what you have, add an open question (`Q-n`)
asking the user for the rest, and continue with what does not depend on it.

## 2. Triage: one entry per comment

Fill `comments.md`: one table row per ID, then one detailed entry per comment from
`templates/comment-entry.md`. For each comment write:

- **Quote** — the full comment, verbatim (the letter will quote it in full too).
- **Plain reading** — what the reviewer literally asks, in one or two sentences, in the user's
  language if that helps them.
- **Real worry** — what the reviewer is afraid of (novelty, correctness, fairness of
  comparisons, practical use, clarity). Replies are written to this, not to the surface request.
- **Verdict** — agree / partly agree / misunderstanding (then the text is unclear and still
  changes) / out of scope (decline politely, with a reason).
- **Action** — concrete: analysis to run, text to change, nothing (and why).
- **Placement** — `main` (only if essential to the paper's claims), `supp`, or `letter`.
- **Effort and risk** — small / medium / large; what could go wrong (a result that may not
  favour the method, a page cost).
- **Overlaps** — other IDs that ask the same thing. Merge them into one plan step but keep
  both IDs; each still gets its own reply, which may point to the other.
- **Letter label** — how the letter will head it ("Major comment 2"). Fill the table column.

Leave the Steps and Proposals columns empty at triage; planning fills Steps, the proposal loop
fills Proposals.

Split a comment with several questions into parts (`R1-3a`, `R1-3b`) when the parts need
different actions; the letter answers each part separately.

## 3. Read the whole set, then talk to the user

Before planning, give the user a short overview (in chat, a few lines):

- the decision and the deadline;
- the 3–5 comments that decide the outcome (usually the AE's and anything about novelty,
  correctness, or a missing comparison);
- comments that conflict with each other, and comments you think are mistaken;
- the decisions the user must make first (what to decline, positioning, which experiments).

Put each question in the open-questions table of `decisions.md` (`Q-1`, `Q-2`, …) and record
each answer as a dated entry when it comes. Do not start planning before the user has seen this
overview. Once they have, plan everything; steps whose shape depends on an unanswered question
are `deferred` with the `Q-` in their "Depends on" column, and work that does not depend on
any answer (for example a wording fix) can go ahead.

## Tone of the internal notes

The register is private. It can say plainly that a comment is mistaken or that a reviewer
missed a section. That frankness stays here; the letter is written later and politely
(write the reply twice: blunt internal note first, final letter after a pause).
