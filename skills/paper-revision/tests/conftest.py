"""Shared fixtures. Everything here is synthetic."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

SAMPLE_TEX = r"""\documentclass{article}
\begin{document}
\begin{abstract}
We propose a very simple test. It's clearly fine.
\end{abstract}
\section{Introduction}\label{sec:intro}
The rejection rate is 0.052 at level 0.05 and power is 0.81 \citep{doe2020}.
We have been modelling the behaviour of 3 groups.

\section{Method}
\subsection{Only one}
A display follows.
\begin{equation}
T = \max_k |Z_k| \label{eq:t}
\end{equation}
Inline math $\hat\theta_n$ and the red curve, see Section 2.

\section{Simulation}
The size was 0.047 and the power 0.999 while 0.953 is a complement and 0.123 is unmatched.
\begin{itemize}\item x\end{itemize}
\bibliography{refs}
\appendix
\section{Proofs}
Proof text 0.777.
\end{document}
"""

SAMPLE_CSV = "method,n,size,power\nours,50,0.0521,0.8104\nother,50,0.0470,0.6000\n"
QUICK_CSV = "method,size\nquick,0.123\n"


@pytest.fixture
def paper(tmp_path: Path) -> Path:
    """A venue folder with main.tex and a results folder."""
    venue = tmp_path / "journal"
    (venue / "results").mkdir(parents=True)
    (venue / "main.tex").write_text(SAMPLE_TEX, encoding="utf-8")
    (venue / "results" / "table1.csv").write_text(SAMPLE_CSV, encoding="utf-8")
    (venue / "results" / "quick_check.csv").write_text(QUICK_CSV, encoding="utf-8")
    return venue


def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          check=True).stdout


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """An empty git repository with a local identity."""
    repo = tmp_path / "repo"
    repo.mkdir()
    run_git(repo, "init", "-q", "-b", "main")
    run_git(repo, "config", "user.name", "Test")
    run_git(repo, "config", "user.email", "test@example.invalid")
    run_git(repo, "config", "commit.gpgsign", "false")
    return repo


def write_config(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path
