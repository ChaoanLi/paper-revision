# revision/

Local working notes for this revision. Not committed (see the repository `.gitignore`); keep it
in a cloud-synced folder or another private backup, because reviewer reports are confidential.

| Path | What it is | Who writes it |
|---|---|---|
| `revision.toml` | Paths, markers, limits and audit settings for the scripts | set up once |
| `rules.md` | Journal requirements (quoted), protected text, positioning, user rules | grows |
| `original/` | Decision letter and reports, verbatim, one file each | intake only |
| `comments.md` | Comment register: ID, letter label, steps, proposals, status, reply | triage, then updated |
| `plan.md` | Phases, ordered steps, page budget, next actions | planning, then updated |
| `decisions.md` | Append-only dated decisions and open questions | every decision |
| `proposals/current.md` | The one open proposal | proposal loop |
| `proposals/P-###-slug.md` | Every proposal ever made, with its final status | proposal loop |
| `checks/` | Output of audits, latexdiff PDF, final checklist | checks phase |
| `mock-review/` | Simulated re-review reports and their summary | before submission |
| `archive/` | Anything superseded; nothing is deleted | any time |

Status at a glance: `python <skill>/scripts/status.py`.
