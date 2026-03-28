from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import os


REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "setup"


class SetupScriptTests(unittest.TestCase):
    def make_fake_uv(self, root: Path) -> Path:
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

    def run_setup(self, repo: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SETUP), *args, str(repo)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )

    def test_claude_standalone_installs_commands_and_gitignore_entries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sennen-setup-") as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()

            result = self.run_setup(repo, "--claude-standalone", "--no-git", "--no-uv", "--no-dvc", "--no-tracking")

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("sennen ready (repo claude-standalone)", result.stdout)
            self.assertTrue((repo / ".claude" / "commands" / "metrics.md").exists())
            gitignore = (repo / ".gitignore").read_text()
            self.assertIn("data/", gitignore)
            self.assertIn("mlruns/", gitignore)
            self.assertIn("mlflow.db", gitignore)

    def test_setup_dot_path_generates_valid_pyproject_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sennen-project-name-") as tmp:
            repo = Path(tmp) / "biontech"
            repo.mkdir()
            fake_bin = self.make_fake_uv(Path(tmp))
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

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            pyproject = (repo / "pyproject.toml").read_text()
            self.assertIn('name = "biontech"', pyproject)
            self.assertIn("tracking: mlflow", result.stdout)
            self.assertIn("mlflow uri: sqlite:///mlflow.db", result.stdout)

    def test_setup_repairs_invalid_dash_project_name(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sennen-project-repair-") as tmp:
            repo = Path(tmp) / "trial-repo"
            repo.mkdir()
            fake_bin = self.make_fake_uv(Path(tmp))
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

            self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
            pyproject = (repo / "pyproject.toml").read_text()
            self.assertIn('name = "trial-repo"', pyproject)


if __name__ == "__main__":
    unittest.main()
