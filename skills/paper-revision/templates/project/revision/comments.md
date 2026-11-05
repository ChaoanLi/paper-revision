# Comment register

The single source of truth for "has every comment been handled?". One row per comment.

- **ID** never changes once given: `ED-1` editor, `AE-1` associate editor, `R1-1` reviewer 1,
  `R2-M1` / `R2-m1` when a reviewer numbers major and minor comments separately.
  A comment with several questions keeps one ID; its parts are `R1-3a`, `R1-3b`.
- **Letter label** is how the response letter heads the reply ("Comment 1", "Major comment 1").
- **Steps** link to `plan.md` (`S-01`…), **Proposals** to `proposals/` (`P-001`…).
- **Status**: `todo` · `proposed` · `approved` · `applied` · `rejected` · `deferred`.
  `rejected` = we decline and explain why in the letter. `deferred` = waiting on a decision.
- **Reply** (response letter): `—` · `draft` · `final`.

`python <skill>/scripts/status.py` reads this table.

| ID | Letter label | Summary | Steps | Proposals | Status | Reply |
|---|---|---|---|---|---|---|

<!-- Detailed entries below, one per comment, from templates/comment-entry.md. -->
