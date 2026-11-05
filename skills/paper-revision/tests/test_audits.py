"""Tests for number_audit, math_audit and style_audit (synthetic inputs only)."""
from __future__ import annotations

from pathlib import Path

import pytest

from conftest import SAMPLE_TEX, run_git, write_config

import _common
import math_audit
import number_audit
import style_audit


# ---------------------------------------------------------------- _common

def test_slice_between_returns_body_and_offset():
    body, offset = _common.slice_between("abc START x END y", "START", "END")
    assert body == "START x "
    assert offset == 4


def test_slice_between_rejects_missing_marker():
    with pytest.raises(SystemExit, match="start marker not found"):
        _common.slice_between("abc", "\\section{Nope}", None)


def test_strip_comments_keeps_escaped_percent():
    assert _common.strip_comments("5\\% rate % note") == "5\\% rate "


def test_mask_refs_removes_keys():
    assert "doe" not in _common.mask_refs(r"see \citep[p.~3]{doe2020} and \ref{x}")


def test_load_config_resolves_relative_paths(tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", '[paper]\nmain_tex = "../main.tex"\n')
    config = _common.load_config(cfg)
    expected = (tmp_path.parent / "main.tex").resolve()
    assert _common.resolve(config, _common.get(config, "paper.main_tex")) == expected
    assert _common.get(config, "paper.missing", 7) == 7


def test_load_config_reports_bad_toml(tmp_path: Path):
    cfg = write_config(tmp_path / "revision.toml", "[paper\n")
    with pytest.raises(SystemExit, match="invalid TOML"):
        _common.load_config(cfg)


def test_find_config_walks_up(tmp_path: Path):
    (tmp_path / "revision").mkdir()
    cfg = write_config(tmp_path / "revision" / "revision.toml", "")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    assert _common.find_config(deep) == cfg.resolve()


def test_read_source_from_git_revision(git_repo: Path, monkeypatch):
    (git_repo / "main.tex").write_text("old text", encoding="utf-8")
    run_git(git_repo, "add", ".")
    run_git(git_repo, "commit", "-q", "-m", "first")
    run_git(git_repo, "tag", "submitted-v1")
    (git_repo / "main.tex").write_text("new text", encoding="utf-8")
    monkeypatch.chdir(git_repo)
    assert _common.read_source("git:submitted-v1:main.tex") == "old text"
    assert _common.read_source("main.tex") == "new text"


# ---------------------------------------------------------------- number_audit

def body_of(text: str) -> str:
    return number_audit.prepare_body(text, "\\section{Introduction}", "\\bibliography")


def test_body_excludes_appendix_and_labels():
    body = body_of(SAMPLE_TEX)
    assert "0.777" not in body
    assert "doe2020" not in body


def test_numbers_matched_by_rounding_and_quick_files_excluded(paper: Path):
    cells = number_audit.load_cells([paper / "results"], "*.csv", exclude=["quick"])
    findings = number_audit.audit(body_of(SAMPLE_TEX), cells, complement=True)
    by_number = {f.number: f for f in findings}
    assert set(by_number) == {"0.052", "0.05", "0.81", "0.047", "0.999", "0.953", "0.123"}
    assert by_number["0.052"].hits and by_number["0.81"].hits and by_number["0.05"].hits
    assert by_number["0.953"].hits  # 1 - 0.047
    assert not by_number["0.999"].hits
    assert not by_number["0.123"].hits  # only in the excluded quick file
    assert by_number["0.047"].section == "Simulation"


def test_percentages_match_proportions(paper: Path):
    cells = number_audit.load_cells([paper / "results"], "*.csv", exclude=["quick"])
    findings = number_audit.audit("rejected in 5.2\\% and 81.0\\% but 5.2 alone", cells)
    assert [bool(f.hits) for f in findings] == [True, True, False]


def test_escaped_percent_is_not_a_comment():
    body = number_audit.prepare_body("rate 4.5\\% and 9.0\\% % a comment 7.7", None, None)
    assert "9.0" in body and "7.7" not in body


def test_read_source_in_non_ascii_folder(tmp_path: Path, monkeypatch):
    repo = tmp_path / "论文 folder"
    repo.mkdir()
    for args in (("init", "-q"), ("config", "user.email", "t@example.invalid"),
                 ("config", "user.name", "T")):
        run_git(repo, *args)
    (repo / "main.tex").write_text("v1", encoding="utf-8")
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-q", "-m", "x")
    monkeypatch.chdir(repo)
    assert _common.read_source("git:HEAD:main.tex") == "v1"


def test_number_at_end_of_sentence_is_audited():
    found = [f.number for f in number_audit.audit("The power is 0.95. Next 1.5.2 is a version.", [])]
    assert found == ["0.95"]


def test_negative_values_match_printed_magnitude(paper: Path, tmp_path: Path):
    (tmp_path / "neg.csv").write_text("name,bias\na,-0.25\n", encoding="utf-8")
    cells = number_audit.load_cells([tmp_path / "neg.csv"])
    assert number_audit.audit("bias of $-$0.25", cells)[0].hits


def test_csv_with_bom_and_non_utf8_csv(tmp_path: Path):
    good = tmp_path / "bom.csv"
    good.write_bytes("\ufeffname,v\na,0.5\n".encode("utf-8"))
    assert number_audit.load_cells([good])[0].column == "v"
    bad = tmp_path / "latin.csv"
    bad.write_bytes("name,v\nr\xe9sum\xe9,0.5\n".encode("latin-1"))
    with pytest.raises(SystemExit, match="not UTF-8"):
        number_audit.load_cells([bad])


def test_strip_comments_after_escaped_backslash():
    assert _common.strip_comments("a \\\\% note") == "a \\\\"


def test_config_with_bom_and_tex_not_utf8(tmp_path: Path):
    cfg = tmp_path / "revision.toml"
    cfg.write_bytes("\ufeff[paper]\npage_limit = 25\n".encode("utf-8"))
    assert _common.get(_common.load_config(cfg), "paper.page_limit") == 25
    tex = tmp_path / "x.tex"
    tex.write_bytes("caf\xe9".encode("latin-1"))
    with pytest.raises(SystemExit, match="not UTF-8"):
        _common.read_text(tex)


def test_warn_if_inputs(capsys):
    _common.warn_if_inputs("\\input{sec1}\n", "main.tex")
    _common.warn_if_inputs("% \\input{old}\n", "main.tex")
    assert capsys.readouterr().err.count("warning") == 1


def test_git_helper_reports_missing_folder(tmp_path: Path):
    with pytest.raises(SystemExit, match="not a folder"):
        _common.git(["status"], tmp_path / "missing")


def test_complement_can_be_switched_off(paper: Path):
    cells = number_audit.load_cells([paper / "results"], "*.csv", exclude=["quick"])
    findings = number_audit.audit(body_of(SAMPLE_TEX), cells, complement=False)
    assert not {f.number: f for f in findings}["0.953"].hits


def test_hits_name_file_row_and_column(paper: Path):
    cells = number_audit.load_cells([paper / "results"], "*.csv", exclude=[])
    hit = number_audit.audit(body_of(SAMPLE_TEX), cells, complement=False)[0].hits[0]
    assert hit.file == "table1" and hit.column == "size" and "ours" in hit.key


def test_number_audit_cli_writes_report(paper: Path, capsys):
    out = paper / "numbers.txt"
    code = number_audit.main([
        "--tex", str(paper / "main.tex"), "--results", str(paper / "results"),
        "--exclude", "quick", "--out", str(out)])
    assert code == 0
    report = out.read_text(encoding="utf-8")
    assert "0.999" in report and "0.052" not in report
    # no end marker: the appendix's sentence-final "0.777." is audited too
    assert "unmatched: 3" in capsys.readouterr().out and "0.777" in report


def test_number_audit_cli_all_and_strict(paper: Path):
    out = paper / "numbers.txt"
    code = number_audit.main([
        "--tex", str(paper / "main.tex"), "--results", str(paper / "results"),
        "--all", "--strict", "--out", str(out)])
    assert code == 1  # 0.999 unmatched
    assert "0.052" in out.read_text(encoding="utf-8")


def test_number_audit_reads_config(paper: Path):
    rev = paper / "revision"
    rev.mkdir()
    cfg = write_config(rev / "revision.toml", (
        '[paper]\nmain_tex = "../main.tex"\nbody_start = \'\\section{Simulation}\'\n'
        'body_end = \'\\bibliography\'\n'
        '[results]\npaths = ["../results"]\nexclude = ["quick"]\ncomplement = false\n'))
    out = paper / "n.txt"
    assert number_audit.main(["--config", str(cfg), "--out", str(out)]) == 0
    report = out.read_text(encoding="utf-8")
    assert "0.953" in report and "0.81" not in report


def test_number_audit_requires_tex():
    with pytest.raises(SystemExit):
        number_audit.main(["--config", "does-not-exist.toml"])


# ---------------------------------------------------------------- math_audit

OLD = r"""\section{Introduction}
We use $\hat\theta_n$ and $\frac{a}{b}$ \citep{doe2020,smith2019}.
\begin{equation}
T = \max_k |Z_k|
\end{equation}
\bibliography{refs}"""

NEW = r"""\section{Introduction}
We use $\hat\theta_n$ and $a/b$ \citep{doe2020, lee2021}.
\bibliography{refs}"""


def test_math_audit_finds_dropped_math_and_citations():
    report = math_audit.compare(OLD, NEW)
    assert any("max_k" in m for m in report.missing_math)
    assert not any("theta" in m for m in report.missing_math)
    assert not any("frac" in m for m in report.missing_math)  # inline a/b accepted
    assert report.dropped_citations == ["smith2019"]
    assert report.added_citations == ["lee2021"]


def test_math_audit_ignores_commented_math_and_citations():
    new = NEW + "\n%\\begin{equation}\n% T = \\max_k |Z_k|\n%\\end{equation} \\citep{smith2019}\n"
    report = math_audit.compare(OLD, new)
    assert any("max_k" in m for m in report.missing_math)
    assert report.dropped_citations == ["smith2019"]


def test_math_audit_formula_kept_only_in_prose_counts_as_missing():
    report = math_audit.compare("$x_1 + y_2$", "we write x_1+y_2 in words")
    assert report.missing_math == ["x_1 + y_2"]


def test_math_audit_escaped_dollars_and_alignat():
    assert math_audit.math_expressions(r"costs \$5 and \$6") == []
    text = "\\begin{alignat}{2}\na &= b\n\\end{alignat}"
    assert math_audit.math_expressions(text) == ["{2}\na &= b\n"]


def test_math_audit_cli(tmp_path: Path, capsys):
    old, new = tmp_path / "old.tex", tmp_path / "new.tex"
    old.write_text(OLD, encoding="utf-8")
    new.write_text(NEW, encoding="utf-8")
    code = math_audit.main([str(old), str(new), "--start", "\\section{Introduction}",
                            "--end", "\\bibliography", "--strict"])
    out = capsys.readouterr().out
    assert code == 1
    assert "smith2019" in out and "max_k" in out


def test_math_audit_clean_when_unchanged(tmp_path: Path):
    f = tmp_path / "a.tex"
    f.write_text(OLD, encoding="utf-8")
    assert math_audit.main([str(f), str(f), "--strict"]) == 0


# ---------------------------------------------------------------- style_audit

def run_style(tmp_path: Path, config_body: str = "") -> list:
    tex = tmp_path / "main.tex"
    tex.write_text(SAMPLE_TEX, encoding="utf-8")
    config = _common.load_config(write_config(tmp_path / "revision.toml", config_body))
    return style_audit.audit_file(tex, config)


def rules_hit(hits) -> set:
    return {h.rule for h in hits}


def test_style_default_rules(tmp_path: Path):
    hits = run_style(tmp_path)
    found = rules_hit(hits)
    assert {"weak word", "contraction", "British spelling", "digit below 10",
            "colour name", "section with one subsection", "list or footnote in main text"} <= found
    assert "present perfect" not in found  # optional rule, off by default
    assert not any("max_k" in h.context for h in hits)  # math is masked
    assert not any(h.match == "2" for h in hits)  # "Section 2" is a reference, not a count


def test_style_protected_ranges_are_tagged(tmp_path: Path):
    hits = run_style(tmp_path, (
        "[[style.protected]]\nstart = '\\begin{abstract}'\nend = '\\end{abstract}'\n"))
    abstract_hits = [h for h in hits if h.match.lower() in ("very", "clearly")]
    assert abstract_hits and all(h.tag == "PROT" for h in abstract_hits)
    assert all(h.tag == "OWN" for h in hits if h.match == "modelling")


def test_style_enable_disable_and_custom_rules(tmp_path: Path):
    hits = run_style(tmp_path, (
        '[style]\nenable = ["present perfect"]\ndisable = ["colour name"]\n'
        "[style.rules]\nterminology = '\\brejection rate\\b'\n"))
    found = rules_hit(hits)
    assert "present perfect" in found
    assert "colour name" not in found
    assert "terminology" in found


def test_style_checks_captions_and_splits_at_display_math(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text(
        "\\begin{document}\n\\caption{Rates for 3 groups.}\n"
        "First short paragraph text here is long enough to count today\n"
        "\\[ x = 1 \\]\n"
        "It is a second paragraph that is also long enough to count today.\n"
        "\\end{document}\n", encoding="utf-8")
    hits = style_audit.audit_file(tex, _common.load_config(write_config(tmp_path / "r.toml", "")))
    assert any(h.rule == "digit below 10" and h.line == 2 for h in hits)
    assert sum(h.rule == "one-sentence paragraph" for h in hits) == 2


def test_style_inline_display_does_not_swallow_the_rest(tmp_path: Path):
    tex = tmp_path / "main.tex"
    tex.write_text("\\begin{document}\n\\[ x \\] then text.\nIt's here.\n\\end{document}\n",
                   encoding="utf-8")
    hits = style_audit.audit_file(tex, _common.load_config(write_config(tmp_path / "r.toml", "")))
    assert any(h.rule == "contraction" and h.line == 3 for h in hits)


def test_style_config_errors(tmp_path: Path):
    with pytest.raises(SystemExit, match="end marker"):
        run_style(tmp_path, "[[style.protected]]\nstart = '\\begin{abstract}'\nend = 'NOPE'\n")
    with pytest.raises(SystemExit, match="invalid regex"):
        run_style(tmp_path, "[style.rules]\nbroken = '(unclosed'\n")


def test_style_long_sentence_threshold(tmp_path: Path):
    hits = run_style(tmp_path, "[style]\nmax_sentence_words = 8\n")
    assert any(h.rule.startswith("long sentence") for h in hits)


def test_style_cli_prints_hits(tmp_path: Path, capsys):
    tex = tmp_path / "main.tex"
    tex.write_text(SAMPLE_TEX, encoding="utf-8")
    assert style_audit.main([str(tex)]) == 0
    out = capsys.readouterr().out
    assert "[contraction]" in out and "hits:" in out
