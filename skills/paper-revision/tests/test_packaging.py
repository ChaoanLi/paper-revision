"""Tests for anonymize_code and latexdiff (synthetic repositories only)."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import pytest

from conftest import run_git, write_config

import anonymize_code
import latexdiff


# ---------------------------------------------------------------- anonymize_code

@pytest.fixture
def code_repo(git_repo: Path) -> Path:
    (git_repo / "LICENSE").write_text("Copyright (c) 2027 Jane Roe\n", encoding="utf-8")
    (git_repo / "README.md").write_text("# Toy\nContact jane.roe@uni.example\n", encoding="utf-8")
    (git_repo / "pkg").mkdir()
    (git_repo / "pkg" / "core.py").write_text("x = 1\n", encoding="utf-8")
    (git_repo / ".gitignore").write_text("results/\n", encoding="utf-8")
    (git_repo / "results").mkdir()
    (git_repo / "results" / "big.csv").write_text("a\n", encoding="utf-8")
    run_git(git_repo, "add", ".")
    run_git(git_repo, "commit", "-q", "-m", "init")
    (git_repo / "notes.txt").write_text("untracked but not ignored\n", encoding="utf-8")
    return git_repo


ANON_CONFIG = """[anonymize]
top = "supp"
forbidden = ["roe"]
[[anonymize.replace]]
file = "LICENSE"
old = "Jane Roe"
new = "The authors"
[[anonymize.replace]]
file = "README.md"
old = "Contact jane.roe@uni.example"
new = "Contact withheld for review"
"""


def test_anonymize_builds_clean_zip(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", ANON_CONFIG)
    out = tmp_path / "out" / "code.zip"
    assert anonymize_code.main([str(code_repo), str(out), "--config", str(cfg)]) == 0
    with zipfile.ZipFile(out) as archive:
        names = set(archive.namelist())
        assert "supp/LICENSE" in names and "supp/pkg/core.py" in names
        assert "supp/notes.txt" in names
        assert not any(n.startswith("supp/results/") for n in names)
        assert "The authors" in archive.read("supp/LICENSE").decode()


def test_anonymize_fails_on_leftover_identity(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", '[anonymize]\nforbidden = ["roe"]\n')
    with pytest.raises(SystemExit, match="Identifying strings left"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg)])
    assert not (tmp_path / "x.zip").exists()


def test_anonymize_email_always_checked(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", (
        '[anonymize]\nforbidden = []\n[[anonymize.replace]]\nfile = "LICENSE"\n'
        'old = "Jane Roe"\nnew = "The authors"\n'))
    with pytest.raises(SystemExit, match="README.md:2"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg)])


def test_anonymize_missing_replacement_text(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", (
        '[anonymize]\n[[anonymize.replace]]\nfile = "LICENSE"\nold = "Nobody"\nnew = "x"\n'))
    with pytest.raises(SystemExit, match="expected text not found"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg)])


def test_anonymize_extra_forbid_flag(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", ANON_CONFIG)
    with pytest.raises(SystemExit, match="core.py"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg),
                             "--forbid", r"x = 1"])


def test_anonymize_scans_any_text_file_and_utf16(code_repo: Path, tmp_path: Path):
    (code_repo / "analysis.Rmd").write_text("author: Jane Roe\n", encoding="utf-8")
    (code_repo / "log.txt").write_bytes("run by Roe\n".encode("utf-16"))
    cfg = write_config(tmp_path / "revision.toml", ANON_CONFIG)
    with pytest.raises(SystemExit) as error:
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg)])
    assert "analysis.Rmd:1" in str(error.value) and "log.txt:1" in str(error.value)


def test_anonymize_binary_warning_and_line_endings(code_repo: Path, tmp_path: Path, capsys):
    (code_repo / "run.sh").write_bytes(b"#!/bin/sh\n# Jane Roe\necho ok\n")
    (code_repo / "img.bin").write_bytes(b"\x00\x01\x02")
    cfg = write_config(tmp_path / "revision.toml", ANON_CONFIG + (
        '[[anonymize.replace]]\nfile = "run.sh"\nold = "Jane Roe"\nnew = "anon"\n'))
    out = tmp_path / "x.zip"
    assert anonymize_code.main([str(code_repo), str(out), "--config", str(cfg)]) == 0
    assert "img.bin: binary file not scanned" in capsys.readouterr().out
    with zipfile.ZipFile(out) as archive:
        assert archive.read("supp/run.sh") == b"#!/bin/sh\n# anon\necho ok\n"


def test_anonymize_rejects_bad_replace_entries(code_repo: Path, tmp_path: Path):
    outside = write_config(tmp_path / "a.toml", (
        '[anonymize]\n[[anonymize.replace]]\nfile = "../escape.txt"\nold = "a"\nnew = "b"\n'))
    with pytest.raises(SystemExit, match="inside the repository"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(outside)])
    incomplete = write_config(tmp_path / "b.toml", '[anonymize]\n[[anonymize.replace]]\nfile = "LICENSE"\n')
    with pytest.raises(SystemExit, match="lacks"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(incomplete)])


def test_anonymize_top_name_and_output_inside_repo(code_repo: Path, tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", ANON_CONFIG)
    with pytest.raises(SystemExit, match="top folder"):
        anonymize_code.main([str(code_repo), str(tmp_path / "x.zip"), "--config", str(cfg),
                             "--top", "roe_code"])
    inside = code_repo / "supp.zip"
    assert anonymize_code.main([str(code_repo), str(inside), "--config", str(cfg)]) == 0
    assert anonymize_code.main([str(code_repo), str(inside), "--config", str(cfg)]) == 0
    with zipfile.ZipFile(inside) as archive:
        assert "supp/supp.zip" not in archive.namelist()


def test_anonymize_missing_repo(tmp_path: Path):
    with pytest.raises(SystemExit, match="not a folder"):
        anonymize_code.main([str(tmp_path / "nope"), str(tmp_path / "x.zip")])


def test_forbidden_pattern_matches_email_and_custom():
    pattern = anonymize_code.forbidden_pattern(["acme"])
    assert pattern.search("mail a.b@c.org") and pattern.search("ACME lab")
    assert not pattern.search("nothing here")


# ---------------------------------------------------------------- latexdiff

def test_build_command_and_default_output(tmp_path: Path):
    cmd = latexdiff.build_latexdiff_command(Path("old.tex"), Path("new.tex"), ["--math-markup=0"])
    assert cmd[:2] == ["latexdiff", "--flatten"] and cmd[-2:] == ["old.tex", "new.tex"]
    assert "--math-markup=0" in cmd
    out = latexdiff.default_output(tmp_path, "submitted-v1", "2027-01-05", pdf=True)
    assert out == tmp_path / "checks" / "latexdiff-submitted-v1-vs-current-2027-01-05.pdf"


def test_latexdiff_requires_tool(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(latexdiff.shutil, "which", lambda _: None)
    with pytest.raises(SystemExit, match="latexdiff is not installed"):
        latexdiff.main(["--tex", str(tmp_path / "main.tex"), "--base", "v1"])


def test_latexdiff_rejects_option_like_base(tmp_path: Path):
    with pytest.raises(SystemExit, match="invalid base"):
        latexdiff.main(["--tex", str(tmp_path / "main.tex"), "--base=--output=x"])


@pytest.mark.skipif(shutil.which("latexdiff") is None, reason="latexdiff not installed")
def test_latexdiff_follows_input_files(git_repo: Path, tmp_path: Path):
    paper = git_repo / "journal"
    paper.mkdir()
    (paper / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\n\\input{sec}\n\\end{document}\n",
        encoding="utf-8")
    (paper / "sec.tex").write_text("The old section text.\n", encoding="utf-8")
    run_git(git_repo, "add", ".")
    run_git(git_repo, "commit", "-q", "-m", "submitted")
    run_git(git_repo, "tag", "submitted-v1")
    (paper / "sec.tex").write_text("The rewritten section text.\n", encoding="utf-8")
    out = tmp_path / "diff.tex"
    assert latexdiff.main(["--tex", str(paper / "main.tex"), "--base", "submitted-v1",
                           "--no-pdf", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "\\DIFadd" in text and "rewritten" in text and "\\DIFdel" in text


def test_latexdiff_requires_base(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit, match="base"):
        latexdiff.main(["--tex", str(tex)])


@pytest.mark.skipif(shutil.which("latexdiff") is None, reason="latexdiff not installed")
def test_latexdiff_marks_changes_against_tag(git_repo: Path, tmp_path: Path):
    paper = git_repo / "journal"
    paper.mkdir()
    body = "\\documentclass{article}\n\\begin{document}\n%s\n\\end{document}\n"
    (paper / "main.tex").write_text(body % "The old sentence.", encoding="utf-8")
    run_git(git_repo, "add", ".")
    run_git(git_repo, "commit", "-q", "-m", "submitted")
    run_git(git_repo, "tag", "submitted-v1")
    (paper / "main.tex").write_text(body % "The new sentence.", encoding="utf-8")
    out = tmp_path / "diff.tex"
    assert latexdiff.main(["--tex", str(paper / "main.tex"), "--base", "submitted-v1",
                           "--no-pdf", "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "\\DIFadd" in text and "new" in text
