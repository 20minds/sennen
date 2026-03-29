from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from sennen.scripts import install_support


@pytest.fixture
def tmpdir_path(tmp_path: Path) -> Path:
    return tmp_path


def test_update_marketplace_creates_expected_entry(tmpdir_path: Path) -> None:
    marketplace = tmpdir_path / ".agents" / "plugins" / "marketplace.json"

    install_support.update_marketplace(marketplace)

    payload = json.loads(marketplace.read_text())
    assert payload["name"] == "local-plugins"
    assert payload["interface"]["displayName"] == "Local Plugins"
    assert len(payload["plugins"]) == 1
    assert payload["plugins"][0]["name"] == "sennen"
    assert payload["plugins"][0]["source"]["path"] == "./plugins/sennen"


def test_update_marketplace_preserves_other_plugins_and_replaces_sennen(tmpdir_path: Path) -> None:
    marketplace = tmpdir_path / "marketplace.json"
    marketplace.write_text(
        json.dumps(
            {
                "name": "custom",
                "interface": {"displayName": "Custom"},
                "plugins": [
                    {"name": "other", "source": {"source": "local", "path": "./plugins/other"}},
                    {"name": "sennen", "source": {"source": "local", "path": "./bad/path"}},
                ],
            }
        )
    )

    install_support.update_marketplace(marketplace)

    payload = json.loads(marketplace.read_text())
    assert len(payload["plugins"]) == 2
    assert payload["plugins"][0]["name"] == "other"
    assert payload["plugins"][1]["name"] == "sennen"
    assert payload["plugins"][1]["source"]["path"] == "./plugins/sennen"


def test_install_plugin_dir_symlinks_by_default(tmpdir_path: Path) -> None:
    source = tmpdir_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("hello")
    destination = tmpdir_path / "dest" / "plugin"

    install_support.install_plugin_dir(source, destination, copy_mode=False, force=False)

    assert destination.is_symlink()
    assert os.readlink(destination) == str(source)


def test_install_plugin_dir_copies_when_requested(tmpdir_path: Path) -> None:
    source = tmpdir_path / "source"
    source.mkdir()
    (source / "file.txt").write_text("hello")
    destination = tmpdir_path / "dest" / "plugin"

    install_support.install_plugin_dir(source, destination, copy_mode=True, force=False)

    assert destination.is_dir()
    assert not destination.is_symlink()
    assert (destination / "file.txt").read_text() == "hello"


def test_install_codex_skills_copies_root_and_child_skills(tmpdir_path: Path) -> None:
    plugin_root = tmpdir_path / "plugin"
    source_root = plugin_root / "skills"
    target_repo = tmpdir_path / "repo"
    (plugin_root / "SKILL.md").parent.mkdir(parents=True)
    (plugin_root / "SKILL.md").write_text("# root\n")
    (source_root / "data").mkdir(parents=True)
    (source_root / "data" / "SKILL.md").write_text("# data\n")
    (source_root / "metrics").mkdir(parents=True)
    (source_root / "metrics" / "SKILL.md").write_text("# metrics\n")

    installed = install_support.install_codex_skills(source_root, plugin_root, target_repo)

    assert len(installed) == 3
    assert (target_repo / ".agents" / "skills" / "sennen" / "SKILL.md").read_text() == "# root\n"
    assert (target_repo / ".agents" / "skills" / "sennen-data" / "SKILL.md").read_text() == "# data\n"
    assert (target_repo / ".agents" / "skills" / "sennen-metrics" / "SKILL.md").read_text() == "# metrics\n"
