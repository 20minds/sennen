from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "setup"


def make_fake_uv(root: Path) -> Path:
    bin_dir = root / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        """#!/bin/sh
set -eu
cmd="${1:-}"
shift || true
case "$cmd" in
  venv)
    mkdir -p "${1:-.venv}"
    ;;
  add)
    exit 0
    ;;
  run)
    sub="${1:-}"
    shift || true
    if [ "$sub" = "dvc" ] && [ "${1:-}" = "version" ]; then
      exit 0
    fi
    ;;
esac
exit 0
"""
    )
    uv.chmod(0o755)
    return bin_dir


def run_setup(repo: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SETUP), *args, str(repo)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def test_claude_standalone_installs_commands_and_gitignore_entries(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(repo, "--claude-standalone", "--no-git", "--no-uv", "--no-dvc", "--no-tracking")

    assert result.returncode == 0, result.stderr
    assert "Ready." in result.stdout
    assert "claude: standalone commands in .claude/commands" in result.stdout
    assert (repo / ".claude" / "commands" / "metrics.md").exists()
    gitignore = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gitignore
    assert "mlruns/" in gitignore
    assert "mlflow.db" in gitignore


def test_setup_dot_path_generates_valid_pyproject_name(tmp_path: Path) -> None:
    repo = tmp_path / "biontech"
    repo.mkdir()
    fake_bin = make_fake_uv(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        [str(SETUP), ".", "--claude-standalone", "--no-git", "--uv", "--no-dvc", "--mlflow", "--yes"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    pyproject = (repo / "pyproject.toml").read_text()
    assert 'name = "biontech"' in pyproject
    assert "Adding mlflow..." in result.stdout
    assert "mlflow: sqlite:///mlflow.db" in result.stdout


def test_setup_repairs_invalid_dash_project_name(tmp_path: Path) -> None:
    repo = tmp_path / "trial-repo"
    repo.mkdir()
    fake_bin = make_fake_uv(tmp_path)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    (repo / "pyproject.toml").write_text(
        '[project]\nname = "-"\nversion = "0.1.0"\nrequires-python = ">=3.10"\ndependencies = []\n'
    )

    result = subprocess.run(
        [str(SETUP), ".", "--claude-standalone", "--no-git", "--uv", "--no-dvc", "--mlflow", "--yes"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    pyproject = (repo / "pyproject.toml").read_text()
    assert 'name = "trial-repo"' in pyproject
