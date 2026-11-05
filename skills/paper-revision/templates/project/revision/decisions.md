# Decisions

Append-only. Never edit an old entry; if a decision changes, add a new entry that says which
one it replaces. Newest at the bottom. `status.py` counts the dated `## YYYY-MM-DD` headings.

Entry format:

    ## YYYY-MM-DD — short title
    - **Decided by:** user / advisor / coauthor
    - **Decision:** one sentence.
    - **Why:** one or two sentences; link comment IDs (R1-2) and steps (S-03).
    - **Replaces:** (optional) the date and title of the entry it overrides.

## Open questions

IDs `Q-1`, `Q-2`, … (never reused). Steps that wait for an answer are `deferred` and name the
question in their "Depends on" column. Move a question into a dated entry once it is answered,
then delete its row here. `status.py` lists the rows still open.

| ID | Question | Recommendation | Needed by |
|---|---|---|---|

## Log
