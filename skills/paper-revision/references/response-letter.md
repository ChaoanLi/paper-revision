# The response letter

Load this when drafting or revising replies. The letter source is
`<venue>/response/response_letter.tex`, started from `templates/response_letter.tex`.

## Structure

1. **Cover note to the editor**: thanks in one sentence, then a numbered list of the main
   changes (one line each, with where they are), then how the letter is organized and what
   the typography means. Signed as the journal's anonymity rules require ("The Authors" for
   double-anonymous review).
2. **One section per person**, in the order Editor → AE → Reviewer 1 → Reviewer 2 ….
3. For every comment: the full comment, quoted verbatim in italics (cut only with `[…]` for
   pure courtesies); then **Response.**; then, where the manuscript changed, the new text
   quoted in a box or indented block with its location in the revised version
   (Section, page, line).

Three things must look different, and the cover note says how: the reviewer's words, your
reply, and quoted new manuscript text (Noble 2017, rule 6). The template does this with
`revcomment`, `\response`, and `revised`.

## Writing each reply

These rules come from the literature (see `sources.md`) and from what worked in practice.

- **The first sentence answers the real worry.** Find what the reviewer is afraid of (see the
  register entry) and answer it head-on: "Yes — the test keeps its level when …", "We agree
  that heavy tails matter for these data, so we added …". Background comes after.
- **Several questions → numbered items**, one per question, without a meta opener such as
  "We answer the three questions in turn". Each item: the direct answer in its first sentence,
  then short bullets with details. Nothing dangling after a list; every sentence belongs to an
  item.
- **Conclusion before numbers**: "close to the nominal level (0.046–0.054 over all settings)".
- **When the reviewer found a gap**, say it is important and what the revision added; do not
  dwell on what the first version lacked.
- **When the reviewer misread**, treat it as a sign the text was unclear: apologise briefly,
  clarify the text anyway, and quote the change (Noble, rules 2–3).
- **When you decline**, say so plainly, give the reason (out of scope, would need a separate
  study, conflicts with another reviewer's request), and offer what you did instead. Never
  argue that "only one reviewer raised this".
- **Never open with a rebuttal.** A first sentence that pushes back reads as defensive even
  when it is right; put the agreement or the fact first.
- **Every requested analysis is reported**, even if it stays out of the paper; say where the
  full result is (supplement section) or give it in the letter.
- **Changed figures and tables**: say what changed and whether conclusions changed; show old
  and new side by side if the change is substantial.
- **Locations**: every change is located (Section, page, line of the revised version). Use the
  placeholder macro `\PH` while the manuscript is moving; fill all of them at the end
  (`status.py` counts them).
- **Plain human wording**: no slogans, no "Relative to …", no mechanical parallel phrasing, no
  repeated content. A reply should sound like the author talking to a colleague.
- **Consistency**: a reply and the manuscript change it describes are proposed together. If
  the change is later edited, the reply is checked again.

## Order of drafting

Draft each reply when its change is applied (it is part of the proposal), mark the register
`Reply` column `draft`. When all changes are in: write the cover note, fill locations, read the
whole letter once as the editor would, cut repetition, and mark replies `final`.

## Before sending

- Every ID in the register has a reply (status.py: "reply not final" is empty).
- No `\PH` left; every location checked against the final PDF.
- Quoted manuscript text matches the final manuscript word for word.
- Names, institutions and self-identifying links are absent if review is anonymous.
- The letter compiles and its PDF is attached in the format the journal asks for.
