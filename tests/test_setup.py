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


def run_setup(
    repo: Path,
    *args: str,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(SETUP), *args, str(repo)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
        input=input_text,
    )


def test_claude_standalone_installs_commands_and_gitignore_entries(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(
        repo,
        "--claude-standalone",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        input_text="y\ny\nsk-test-join\n",
    )

    assert result.returncode == 0, result.stderr
    assert "Ready." in result.stdout
    assert "claude: standalone commands in .claude/commands" in result.stdout
    assert "top-level directory: .claude (claude standalone install)" in result.stdout
    assert (repo / ".claude" / "commands" / "sen-metrics.md").exists()
    assert (repo / ".env").read_text().strip() == "TWENTYMINDS_API_KEY=sk-test-join"
    assert (repo / ".claude" / "skills" / "sen-join" / "SKILL.md").exists()
    assert (repo / ".claude" / "skills" / "sen-join" / "assets" / "join_guest_meet.py").exists()
    gitignore = (repo / ".gitignore").read_text()
    assert "__pycache__/" in gitignore
    assert "mlruns/" in gitignore
    assert "mlflow.db" in gitignore
    assert ".env" in gitignore


def test_setup_supports_combined_claude_and_codex_flags(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(
        repo,
        "--claude",
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
    )

    assert result.returncode == 0, result.stderr
    assert "Ready." in result.stdout
    assert "top-level directory: plugins (claude plugin install)" in result.stdout
    assert "top-level directory: .agents (codex skills)" in result.stdout
    assert "codex: enabled" in result.stdout
    assert f"codex skills: {repo}/.agents/skills" in result.stdout
    assert f"claude: {repo}/plugins/sennen" in result.stdout
    assert (repo / "plugins" / "sennen").exists()
    assert (repo / ".agents" / "skills" / "sen-plan" / "SKILL.md").exists()


def test_setup_installs_join_command_for_codex_when_enabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(
        repo,
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        input_text="y\ny\nsk-test-join\n",
    )

    assert result.returncode == 0, result.stderr
    assert (repo / ".agents" / "skills" / "sen-join" / "SKILL.md").exists()
    assert (repo / ".agents" / "skills" / "sen-join" / "assets" / "join_guest_meet.py").exists()
    assert not (repo / "plugins").exists()


def test_setup_reuses_existing_twentyminds_api_key_from_env(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")
    env["TWENTYMINDS_API_KEY"] = "sk-from-env"

    result = run_setup(
        repo,
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        env=env,
        input_text="y\ny\n",
    )

    assert result.returncode == 0, result.stderr
    assert "Using existing TWENTYMINDS_API_KEY" in result.stdout
    assert (repo / ".env").read_text().strip() == "TWENTYMINDS_API_KEY=sk-from-env"


def test_setup_reuses_existing_twentyminds_api_key_from_repo_env(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".env").write_text("TWENTYMINDS_API_KEY=sk-from-dotenv\n")
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")

    result = run_setup(
        repo,
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        env=env,
        input_text="y\ny\n",
    )

    assert result.returncode == 0, result.stderr
    assert "Using existing TWENTYMINDS_API_KEY" in result.stdout
    assert (repo / ".env").read_text().strip() == "TWENTYMINDS_API_KEY=sk-from-dotenv"


def test_setup_skips_join_skill_when_not_enabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(tmp_path / "home")

    result = run_setup(
        repo,
        "--claude",
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        env=env,
        input_text="y\nn\n",
    )

    assert result.returncode == 0, result.stderr
    assert not (repo / ".env").exists()
    assert (repo / ".agents" / "skills" / "sen-plan" / "SKILL.md").exists()
    assert not (repo / ".codex" / "prompts").exists()
    assert not (repo / ".codex" / "commands").exists()
    assert not (repo / ".codex" / "skills").exists()
    assert not (repo / ".agents" / "skills" / "sen-join").exists()
    assert not (repo / "plugins" / "sennen" / "skills" / "sen-join").exists()
    assert not (repo / "plugins" / "sennen" / "commands" / "join.md").exists()


def test_setup_skips_db_skills_when_not_enabled(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(
        repo,
        "--codex",
        "--no-git",
        "--no-uv",
        "--no-dvc",
        "--no-tracking",
        input_text="n\nn\n",
    )

    assert result.returncode == 0, result.stderr
    assert not (repo / ".agents" / "skills" / "db-chembl").exists()
    assert (repo / ".agents" / "skills" / "sen-plan" / "SKILL.md").exists()


def test_setup_rejects_combined_standalone_and_plugin_modes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = run_setup(repo, "--claude-standalone", "--codex", "--no-git", "--no-uv", "--no-dvc", "--no-tracking")

    assert result.returncode != 0
    assert "--claude-standalone cannot be combined with --claude or --codex" in result.stderr


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


def test_setup_global_default_installs_codex_and_claude(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    env["TWENTYMINDS_API_KEY"] = "sk-from-env"

    result = subprocess.run(
        [str(SETUP)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
        input="y\ny\n",
    )

    assert result.returncode == 0, result.stderr
    assert "Install the optional database research skills?" in result.stdout
    assert "Install the optional conference-call assistant skill?" in result.stdout
    assert "sennen ready (codex + claude)" in result.stdout
    assert (home / ".codex" / "skills" / "sen-plan" / "SKILL.md").exists()
    assert (home / ".codex" / "skills" / "db-chembl" / "SKILL.md").exists()
    assert not (home / ".codex" / "plugins" / "sennen").exists()
    assert not (home / ".agents" / "plugins" / "marketplace.json").exists()
    assert (home / ".claude" / "skills" / "sen-join" / "SKILL.md").exists()
    assert not (home / ".claude" / "commands" / "sen-join.md").exists()
    assert not (home / ".claude" / "plugins" / "sennen").exists()


def test_setup_global_claude_standalone_requires_repo_path(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)

    result = subprocess.run(
        [str(SETUP), "--claude-standalone"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "setup --claude-standalone requires a repo path" in result.stderr
