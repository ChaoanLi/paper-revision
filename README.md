# paper-revision

A Claude Code skill for answering reviewers on a LaTeX paper: from the decision letter to the
resubmitted package, with the author approving every change.

It turns a revise-and-resubmit into a fixed sequence of files and steps:

```
decision letter + reports ──► original/ (verbatim, IDs added)
                          ──► comments.md (register: reading, real worry, action, placement, status)
                          ──► plan.md (ordered steps: method → code → experiments → writing)
                          ──► proposals/current.md (one change at a time; approve → apply → archive)
                          ──► response_letter.tex (reply drafted with each change)
                          ──► checks/ (numbers, math kept, style, latexdiff) ──► mock re-review ──► submit
```

## Why

A revision touches the manuscript, the code, the bibliography and a long letter at once, over
weeks, often with coauthors. The usual failure modes are quiet: a comment never answered, a
number in the text that no longer matches the results, a formula lost while cutting pages, a
reply that promises a change the paper does not contain, an ID scheme that collides halfway
through. This skill keeps one register of comments, one open proposal at a time, one
append-only decision log, and scripts that check the mechanical parts.

## What is in it

| Part | Content |
|---|---|
| [`SKILL.md`](skills/paper-revision/SKILL.md) | golden rules, phases, file contract, scripts |
| [`references/`](skills/paper-revision/references/) | setup (layout, naming, git, Overleaf), intake and triage, planning and page budget, the proposal loop, the response letter, checks and mock review, submission, writing rules, sources |
| [`templates/`](skills/paper-revision/templates/) | project scaffold, comment entry, proposal, response letter (LaTeX), mock-reviewer prompt |
| [`scripts/`](skills/paper-revision/scripts/) | `init_project`, `status`, `number_audit`, `math_audit`, `style_audit`, `latexdiff`, `anonymize_code` |
| [`examples/toy-revision/`](examples/toy-revision/) | a fictional revision a few days in |

### Scripts

Python 3.11+, standard library only; each has `--help` and reads `revision/revision.toml`.

| Script | Does |
|---|---|
| `init_project.py` | creates the local `revision/` workspace and the `.gitignore` block; never overwrites |
| `status.py` | open comments, replies not final, current proposal, decisions, `\PH` placeholders left, pages vs limit, days to deadline |
| `number_audit.py` | every decimal in the text matched against the result CSVs (rounding, 1 − p, percentages) |
| `math_audit.py` | formulas and citations dropped between two versions (`git:submitted-v1:main.tex` works) |
| `style_audit.py` | mechanical style checks plus project rules; hits in protected (coauthor) text tagged separately |
| `latexdiff.py` | marked-changes PDF of the submitted tag against the working tree, built in a temp folder |
| `anonymize_code.py` | anonymous code zip for double-anonymous review; refuses to write while names or e-mails remain |

## Install

As a plugin (Claude Code):

```
/plugin marketplace add ChaoanLi/paper-revision
/plugin install paper-revision@paper-revision
```

Or copy the skill folder:

```sh
git clone https://github.com/ChaoanLi/paper-revision.git
cp -r paper-revision/skills/paper-revision ~/.claude/skills/
```

Requirements: Python 3.11+, git. Optional: TeX Live or MiKTeX (`latexdiff`, `latexmk`,
`pdfinfo`, `chktex`).

## Use

Tell Claude you received reviews ("we got a major revision, here are the reports"), or invoke
`/paper-revision`. It will set up `revision/` next to your manuscript, store the reports, build
the comment register, and give you an overview with the decisions you need to make first.
From then on, every session starts with `status.py`, and every change to the paper arrives as
a proposal in `revision/proposals/current.md` for you to approve.

What stays out of git: `revision/` (reviews are confidential), `papers/` (reference PDFs), and
the code repository (its own repo). Keep `revision/` in a synced or backed-up folder. Details in
[`references/setup.md`](skills/paper-revision/references/setup.md).

## Related skills

- [paper-audit](https://github.com/ChaoanLi/paper-audit): figure–text, code–paper and
  redundancy passes, used in the checks phase.
- [academic-code-release](https://github.com/ChaoanLi/academic-code-release): tidy the code
  repository before the anonymous package.

## Sources

The response-letter rules follow Noble (2017), "Ten simple rules for writing a response to
reviewers", and publisher guidance (Taylor & Francis, PLOS); the layout follows Wilson et al.
(2017), "Good enough practices in scientific computing". The house rules come from a complete
revision of a statistics methods paper. Full list with links:
[`references/sources.md`](skills/paper-revision/references/sources.md).

## Development

```sh
cd skills/paper-revision
python -m pytest tests --cov=scripts
```

Tests use synthetic files only. The latexdiff test runs when `latexdiff` is installed.

## 中文说明

这是一个用于期刊返修（revise and resubmit）的 Claude Code skill，适合用 LaTeX + git（可选
Overleaf）写论文、代码单独一个仓库的情况。

- **流程**：审稿意见原文存档并编号 → 逐条解读（字面意思、真实担心、处理方式、放正文/附录/只在回信）
  → 按顺序排计划（先定方法、再改代码和跑实验、最后写文字）→ 每处修改先写成提案
  `proposals/current.md`，作者确认后才改 tex → 回信与修改同步起草 → 机械检查（数字对 CSV、
  公式与引用没丢、文风、latexdiff）→ 模拟二审 → 投稿。
- **哪些进 git**：tex、bib、图、编译好的 PDF 和 .bbl、回信。**不进 git**：`revision/`（审稿意见保密）、
  `papers/`（参考文献 PDF）、代码（单独的仓库）。
- **编号**：意见 `AE-1`、`R1-2`、`R2-M1`；步骤 `S-01`；提案 `P-001`，一个计数器，永不复用。
  状态只用 `todo · proposed · approved · applied · rejected · deferred`。
- **安装**：见上面的 Install；对 Claude 说"收到审稿意见了"即可开始。

## License

MIT. See [LICENSE](LICENSE).
