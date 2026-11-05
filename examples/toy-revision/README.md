# Example: a revision in progress (fictional)

Everything here is invented: the paper (a permutation scan test for a change in variance),
the reports, the reference "Smith and Lee (2019)", and every number. It shows what the
`revision/` folder looks like a few days into a revision.

| File | Shows |
|---|---|
| [revision/original/AE.md](revision/original/AE.md), [R1.md](revision/original/R1.md) | reports stored verbatim with IDs added |
| [revision/comments.md](revision/comments.md) | the register table and two detailed entries |
| [revision/plan.md](revision/plan.md) | ordered steps; writing waits for experiments; page budget |
| [revision/decisions.md](revision/decisions.md) | dated, append-only decisions and an open question |
| [revision/proposals/P-001-new-vs-borrowed.md](revision/proposals/P-001-new-vs-borrowed.md) | an applied proposal with its letter reply |
| [revision/proposals/current.md](revision/proposals/current.md) | the open proposal waiting for approval |
| `revision/revision.toml`, `rules.md`, `README.md` | as created by `init_project.py` |

Try the status script on it:

```sh
cd examples/toy-revision
python ../../skills/paper-revision/scripts/status.py --config revision/revision.toml
```

```
comments: 5 (applied 1, proposed 1, todo 3)
  open: AE-2, R1-1, R1-2, R1-3
  reply not final: AE-1, AE-2, R1-1, R1-2, R1-3
proposals closed: 1 (applied 1)
  open (current.md): P-002 — "significantly larger" on page 4
decisions logged: 2
  open questions: 1 (Q-1)
...
```

In a real project `revision/` sits next to the manuscript and is listed in `.gitignore`; it is
committed here only because it is an example.
