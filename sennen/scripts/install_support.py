#!/usr/bin/env python3
"""Shared installation helpers for Sennen."""

from __future__ import annotations

import shutil
from collections.abc import Iterable
from pathlib import Path


def plugin_source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def codex_skill_source_root() -> Path:
    return plugin_source_root() / "skills"


def ensure_target_repo(target_repo: Path) -> None:
    if not target_repo.exists():
        raise FileNotFoundError(f"Target repo does not exist: {target_repo}")
    if not target_repo.is_dir():
        raise NotADirectoryError(f"Target repo is not a directory: {target_repo}")


def _excluded_plugin_paths(exclude_skill_names: Iterable[str]) -> list[Path]:
    paths: list[Path] = []
    for skill_name in exclude_skill_names:
        normalized = skill_name.strip()
        if not normalized:
            continue
        paths.append(Path("skills") / normalized)
        # Only sen-* skills have matching command files; db-* and others do not.
        if normalized.startswith("sen-"):
            command_name = normalized.removeprefix("sen-")
            paths.append(Path("commands") / f"{command_name}.md")
    return paths


def _prune_excluded_plugin_paths(destination: Path, exclude_skill_names: Iterable[str]) -> None:
    for relative_path in _excluded_plugin_paths(exclude_skill_names):
        target = destination / relative_path
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)


def install_plugin_dir(
    source: Path,
    destination: Path,
    copy_mode: bool,
    force: bool,
    exclude_skill_names: Iterable[str] = (),
) -> None:
    if destination.exists() or destination.is_symlink():
        if not force:
            raise FileExistsError(
                f"Plugin destination already exists: {destination}. Use --force to replace it."
            )
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        else:
            shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    excluded = [name.strip() for name in exclude_skill_names if name.strip()]
    if copy_mode or excluded:
        shutil.copytree(source, destination)
        if excluded:
            _prune_excluded_plugin_paths(destination, excluded)
    else:
        destination.symlink_to(source, target_is_directory=True)


def remove_legacy_codex_install_paths(target_repo: Path) -> None:
    legacy_paths = [
        target_repo / ".agents" / "commands",
        target_repo / ".agents" / "plugins",
        target_repo / ".codex" / "prompts",
        target_repo / ".codex" / "commands",
        target_repo / ".codex" / "skills",
    ]
    for legacy_path in legacy_paths:
        if legacy_path.is_symlink() or legacy_path.is_file():
            legacy_path.unlink()
        elif legacy_path.exists():
            shutil.rmtree(legacy_path)

    agents_dir = target_repo / ".agents"
    if agents_dir.exists() and not any(agents_dir.iterdir()):
        agents_dir.rmdir()


def install_codex_skills(
    source_root: Path,
    destination_root: Path,
    exclude_skill_names: Iterable[str] = (),
) -> list[Path]:
    destination_root.mkdir(parents=True, exist_ok=True)
    installed: list[Path] = []
    excluded = {name.strip() for name in exclude_skill_names if name.strip()}

    for source in sorted(source_root.iterdir()):
        if not source.is_dir():
            continue
        skill_name = source.name
        if skill_name in excluded:
            target = destination_root / skill_name
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.exists():
                shutil.rmtree(target)
            continue
        if not (source / "SKILL.md").exists():
            continue
        destination_dir = destination_root / skill_name
        if destination_dir.exists() or destination_dir.is_symlink():
            if destination_dir.is_symlink() or destination_dir.is_file():
                destination_dir.unlink()
            else:
                shutil.rmtree(destination_dir)
        shutil.copytree(source, destination_dir)
        installed.append(destination_dir / "SKILL.md")

    return installed

