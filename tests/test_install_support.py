from __future__ import annotations

import os
from pathlib import Path

import pytest

from sennen.scripts import install_support


@pytest.fixture
def tmpdir_path(tmp_path: Path) -> Path:
    return tmp_path


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


def test_remove_legacy_codex_install_paths_cleans_legacy_paths(tmpdir_path: Path) -> None:
    target_repo = tmpdir_path / "repo"
    (target_repo / ".agents" / "commands").mkdir(parents=True)
    (target_repo / ".agents" / "commands" / "join.md").write_text("legacy\n")
    (target_repo / ".agents" / "plugins").mkdir(parents=True)
    (target_repo / ".agents" / "plugins" / "marketplace.json").write_text("{}\n")
    (target_repo / ".codex" / "prompts").mkdir(parents=True)
    (target_repo / ".codex" / "prompts" / "sen-join.md").write_text("legacy\n")
    (target_repo / ".codex" / "commands").mkdir(parents=True)
    (target_repo / ".codex" / "commands" / "join.md").write_text("legacy\n")
    (target_repo / ".codex" / "skills").mkdir(parents=True)
    (target_repo / ".codex" / "skills" / "SKILL.md").write_text("legacy\n")

    install_support.remove_legacy_codex_install_paths(target_repo)

    assert not (target_repo / ".agents" / "commands").exists()
    assert not (target_repo / ".agents" / "plugins").exists()
    assert not (target_repo / ".codex" / "prompts").exists()
    assert not (target_repo / ".codex" / "commands").exists()
    assert not (target_repo / ".codex" / "skills").exists()


def test_install_plugin_dir_forces_copy_when_exclusions_present(tmpdir_path: Path) -> None:
    source = tmpdir_path / "source"
    (source / "skills" / "sen-join").mkdir(parents=True)
    (source / "skills" / "sen-join" / "SKILL.md").write_text("join\n")
    (source / "skills" / "sen-data").mkdir(parents=True)
    (source / "skills" / "sen-data" / "SKILL.md").write_text("data\n")
    (source / "commands").mkdir()
    (source / "commands" / "join.md").write_text("join cmd\n")
    (source / "commands" / "data.md").write_text("data cmd\n")
    destination = tmpdir_path / "dest" / "plugin"

    install_support.install_plugin_dir(
        source, destination, copy_mode=False, force=False, exclude_skill_names=["sen-join"]
    )

    assert destination.is_dir()
    assert not destination.is_symlink()
    assert not (destination / "skills" / "sen-join").exists()
    assert not (destination / "commands" / "join.md").exists()
    assert (destination / "skills" / "sen-data" / "SKILL.md").exists()
    assert (destination / "commands" / "data.md").exists()


def test_install_codex_skills_copies_skill_dirs(tmpdir_path: Path) -> None:
    source_root = tmpdir_path / "skills"
    (source_root / "sen-data").mkdir(parents=True)
    (source_root / "sen-data" / "SKILL.md").write_text("data\n")
    (source_root / "sen-join").mkdir(parents=True)
    (source_root / "sen-join" / "SKILL.md").write_text("join\n")
    destination_root = tmpdir_path / "dest"

    installed = install_support.install_codex_skills(source_root, destination_root)

    assert len(installed) == 2
    assert (destination_root / "sen-data" / "SKILL.md").read_text() == "data\n"
    assert (destination_root / "sen-join" / "SKILL.md").read_text() == "join\n"


def test_install_codex_skills_excludes_named_skills(tmpdir_path: Path) -> None:
    source_root = tmpdir_path / "skills"
    (source_root / "sen-data").mkdir(parents=True)
    (source_root / "sen-data" / "SKILL.md").write_text("data\n")
    (source_root / "sen-join").mkdir(parents=True)
    (source_root / "sen-join" / "SKILL.md").write_text("join\n")
    (source_root / "db-chembl").mkdir(parents=True)
    (source_root / "db-chembl" / "SKILL.md").write_text("chembl\n")
    destination_root = tmpdir_path / "dest"

    installed = install_support.install_codex_skills(
        source_root, destination_root, exclude_skill_names=["sen-join", "db-chembl"]
    )

    assert len(installed) == 1
    assert (destination_root / "sen-data" / "SKILL.md").exists()
    assert not (destination_root / "sen-join").exists()
    assert not (destination_root / "db-chembl").exists()


def test_install_codex_skills_removes_previously_installed_excluded_skill(tmpdir_path: Path) -> None:
    source_root = tmpdir_path / "skills"
    (source_root / "sen-join").mkdir(parents=True)
    (source_root / "sen-join" / "SKILL.md").write_text("join\n")
    destination_root = tmpdir_path / "dest"
    (destination_root / "sen-join").mkdir(parents=True)
    (destination_root / "sen-join" / "SKILL.md").write_text("old\n")

    install_support.install_codex_skills(
        source_root, destination_root, exclude_skill_names=["sen-join"]
    )

    assert not (destination_root / "sen-join").exists()
