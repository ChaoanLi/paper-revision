"""Tests for init_project and status (synthetic project only)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from conftest import write_config

import init_project
import status

REGISTER = """# Comment register

| ID | Letter label | Summary | Steps | Proposals | Status | Reply |
|---|---|---|---|---|---|---|
| AE-1 | AE comment 1 | novelty | S-01 | P-001 | applied | final |
| R1-1 | Comment 1 | toy power | S-02 | P-002 | proposed | draft |
| R1-2 | Comment 2 | typo | S-03 | | todo | — |
| R2-M1 | Major comment 1 | scope | | | rejected | final |
| R2-m1 | Minor comment 1 | odd | | | someday | — |

## AE-1 — novelty
details
"""


# ---------------------------------------------------------------- init_project

def test_init_creates_tree_config_and_gitignore(git_repo: Path):
    venue = git_repo / "journal"
    venue.mkdir()
    actions = init_project.main([str(venue), "--main-tex", "paper.tex"])
    rev = venue / "revision"
    for name in ("README.md", "revision.toml", "comments.md", "plan.md", "decisions.md",
                 "rules.md", "proposals/current.md", "original/README.md"):
        assert (rev / name).is_file(), name
    assert (venue / "papers" / "requirements").is_dir()
    config = (rev / "revision.toml").read_text(encoding="utf-8")
    assert 'main_tex = "../paper.tex"' in config and "{{" not in config
    gitignore = (git_repo / ".gitignore").read_text(encoding="utf-8")
    assert "journal/revision/" in gitignore and "journal/papers/" in gitignore
    assert actions > 0


def test_init_is_idempotent_and_keeps_user_edits(git_repo: Path):
    venue = git_repo / "journal"
    venue.mkdir()
    init_project.main([str(venue)])
    (venue / "revision" / "plan.md").write_text("my plan", encoding="utf-8")
    assert init_project.main([str(venue)]) == 0
    assert (venue / "revision" / "plan.md").read_text(encoding="utf-8") == "my plan"
    gitignore = (git_repo / ".gitignore").read_text(encoding="utf-8")
    assert gitignore.count(init_project.BLOCK_START) == 1


def test_init_dry_run_writes_nothing(git_repo: Path, capsys):
    venue = git_repo / "journal"
    venue.mkdir()
    assert init_project.main([str(venue), "--dry-run"]) > 0
    assert not (venue / "revision").exists()
    assert not (git_repo / ".gitignore").exists()
    assert "would" in capsys.readouterr().out


def test_init_outside_git_uses_venue_folder(tmp_path: Path, monkeypatch):
    venue = tmp_path / "paper"
    venue.mkdir()
    monkeypatch.setattr(init_project, "git_root", lambda _: None)
    init_project.main([str(venue)])
    assert "\nrevision/\n" in (venue / ".gitignore").read_text(encoding="utf-8")


def test_init_rejects_missing_folder(tmp_path: Path):
    with pytest.raises(SystemExit):
        init_project.main([str(tmp_path / "nope")])


def test_gitignore_block_for_repo_root():
    block = init_project.gitignore_block("")
    assert "\nrevision/\n" in block and "*.aux" in block


# ---------------------------------------------------------------- status

def test_parse_register_reads_first_table():
    rows = status.parse_register(REGISTER)
    assert [r["ID"] for r in rows] == ["AE-1", "R1-1", "R1-2", "R2-M1", "R2-m1"]
    assert rows[1]["Status"] == "proposed"


def test_parse_register_without_table():
    assert status.parse_register("# nothing yet\n") == []


def test_summarize_register_counts_and_flags():
    summary = status.summarize_register(status.parse_register(REGISTER))
    assert summary.counts["applied"] == 1 and summary.counts["todo"] == 1
    assert summary.open_ids == ["R1-1", "R1-2"]
    assert summary.reply_missing == ["R1-1", "R1-2", "R2-m1"]
    assert summary.unknown == ["R2-m1 (someday)"]


def test_proposal_statuses(tmp_path: Path):
    folder = tmp_path / "proposals"
    folder.mkdir()
    (folder / "P-001-novelty.md").write_text("# P-001\n**Status:** applied\n", encoding="utf-8")
    (folder / "P-002-power.md").write_text("# P-002\n**Status:** proposed\n", encoding="utf-8")
    (folder / "P-003-x.md").write_text("# P-003\nno status line\n", encoding="utf-8")
    (folder / "current.md").write_text("# P-002 — power\n", encoding="utf-8")
    assert status.proposal_statuses(folder) == {"P-001": "applied", "P-002": "proposed", "P-003": "?"}
    assert status.current_title(folder) == "P-002 — power"


def test_cells_keep_pipes_inside_math_code_and_escapes():
    row = "| R1-4 | Comment 4 | bound on $|x|$ and `a|b` and a\\|b | | | todo | — |"
    cells = status._cells(row)
    assert len(cells) == 7 and cells[5] == "todo"


def test_proposal_statuses_skip_unnumbered_and_flag_duplicates(tmp_path: Path):
    folder = tmp_path / "proposals"
    folder.mkdir()
    (folder / "P-notes.md").write_text("scratch", encoding="utf-8")
    (folder / "P-001-a.md").write_text("**Status:** applied", encoding="utf-8")
    (folder / "P-001-b.md").write_text("**Status:** rejected", encoding="utf-8")
    result = status.proposal_statuses(folder)
    assert result["P-001"] == "applied"
    assert any("duplicate" in key for key in result)
    assert len(result) == 2


def test_days_left_accepts_toml_date():
    assert status.days_left(date(2027, 1, 31), date(2027, 1, 1)) == 30


def test_status_rejects_bad_page_limit(tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", '[paper]\npage_limit = "25 pages"\n')
    with pytest.raises(SystemExit, match="page_limit"):
        status.main(["--config", str(cfg)])


def test_init_normalizes_windows_paths(git_repo: Path):
    venue = git_repo / "journal"
    venue.mkdir()
    init_project.main([str(venue), "--main-tex", "sub\\main.tex"])
    import _common
    config = _common.load_config(venue / "revision" / "revision.toml")
    assert config["paper"]["main_tex"] == "../sub/main.tex"


def test_days_left():
    assert status.days_left("2027-01-31", date(2027, 1, 1)) == 30
    assert status.days_left("", date(2027, 1, 1)) is None
    assert status.days_left("soon", date(2027, 1, 1)) is None


def test_count_placeholders():
    assert status.count_placeholders(r"a \PH b \PH\ c \PHX", r"\PH") == 2


def test_status_cli_end_to_end(tmp_path: Path, capsys):
    rev = tmp_path / "revision"
    (rev / "proposals").mkdir(parents=True)
    (rev / "comments.md").write_text(REGISTER, encoding="utf-8")
    (rev / "proposals" / "P-001-a.md").write_text("**Status:** applied\n", encoding="utf-8")
    (rev / "proposals" / "current.md").write_text("# P-002 — b\n", encoding="utf-8")
    (tmp_path / "letter.tex").write_text(r"see \PH and \PH", encoding="utf-8")
    (rev / "decisions.md").write_text("## 2027-01-02 — a\n## 2027-01-03 — b\n", encoding="utf-8")
    cfg = write_config(rev / "revision.toml", (
        '[paper]\nmain_tex = "../main.tex"\npdf = "../main.pdf"\npage_limit = 25\n'
        'deadline = "2999-01-01"\n[letter]\ntex = "../letter.tex"\n'))
    assert status.main(["--config", str(cfg)]) == 0
    out = capsys.readouterr().out
    assert "comments: 5" in out
    assert "open: R1-1, R1-2" in out
    assert "placeholders left in the letter: 2" in out
    assert "decisions logged: 2" in out
    assert "open (current.md): P-002 — b" in out
    assert "pages: PDF not found" in out


def test_open_questions_and_deferred_count_as_open():
    text = ("## Open questions\n\n| ID | Question | Recommendation | Needed by |\n|---|---|---|---|\n"
            "| Q-1 | rule for m? | the rule | S-02 |\n| Q-2 | cite X? | ask | S-05 |\n\n## Log\n")
    assert status.open_questions(text) == ["Q-1", "Q-2"]
    rows = status.parse_register("| ID | Status | Reply |\n|---|---|---|\n| R1-1 | deferred | — |\n")
    assert status.summarize_register(rows).open_ids == ["R1-1"]


def test_config_found_from_repository_root(git_repo: Path, monkeypatch):
    venue = git_repo / "journal"
    venue.mkdir()
    (venue / "main.tex").write_text("\\begin{document}\nx\n\\end{document}\n", encoding="utf-8")
    init_project.main([str(venue)])
    monkeypatch.chdir(git_repo)
    assert status.main([]) == 0
    config = (venue / "revision" / "revision.toml").read_text(encoding="utf-8")
    assert "body_start = '\\begin{document}'" in config  # no Introduction section in this paper
    (git_repo / "arxiv" / "revision").mkdir(parents=True)
    (git_repo / "arxiv" / "revision" / "revision.toml").write_text("", encoding="utf-8")
    with pytest.raises(SystemExit, match="several revision.toml"):
        status.main([])


def test_status_without_config_fails_cleanly(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match="revision.toml"):
        status.main([])


def test_page_count_handles_missing_tool(tmp_path: Path, monkeypatch):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(status.shutil, "which", lambda _: None)
    assert status.page_count(pdf) is None


def test_init_then_status_on_fresh_project(git_repo: Path, capsys):
    venue = git_repo / "journal"
    venue.mkdir()
    init_project.main([str(venue)])
    assert status.main(["--config", str(venue / "revision" / "revision.toml")]) == 0
    assert "comments: 0" in capsys.readouterr().out
