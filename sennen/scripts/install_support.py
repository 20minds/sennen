#!/usr/bin/env python3
"""Shared installation helpers for Sennen."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


PLUGIN_NAME = "sennen"
MARKETPLACE_DEFAULT = {
    "name": "local-plugins",
    "interface": {
        "displayName": "Local Plugins",
    },
    "plugins": [],
}


def plugin_source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def codex_skill_source_root() -> Path:
    return plugin_source_root() / "skills"


def ensure_target_repo(target_repo: Path) -> None:
    if not target_repo.exists():
        raise FileNotFoundError(f"Target repo does not exist: {target_repo}")
    if not target_repo.is_dir():
        raise NotADirectoryError(f"Target repo is not a directory: {target_repo}")


def install_plugin_dir(source: Path, destination: Path, copy_mode: bool, force: bool) -> None:
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
    if copy_mode:
        shutil.copytree(source, destination)
    else:
        destination.symlink_to(source, target_is_directory=True)


def install_codex_skills(source_root: Path, plugin_root: Path, target_repo: Path) -> list[Path]:
    skills_dir = target_repo / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    installed = []

    root_skill_source = plugin_root / "SKILL.md"
    root_skill_dir = skills_dir / "sennen"
    root_skill_dir.mkdir(parents=True, exist_ok=True)
    root_skill_target = root_skill_dir / "SKILL.md"
    shutil.copy2(root_skill_source, root_skill_target)
    installed.append(root_skill_target)

    for source in sorted(source_root.glob("*/SKILL.md")):
        skill_name = source.parent.name
        destination_dir = skills_dir / f"sennen-{skill_name}"
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / "SKILL.md"
        shutil.copy2(source, destination)
        installed.append(destination)

    return installed


def load_marketplace(path: Path) -> dict:
    if not path.exists():
        return json.loads(json.dumps(MARKETPLACE_DEFAULT))
    with path.open() as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Marketplace file must contain a JSON object: {path}")
    return payload


def update_marketplace(path: Path) -> None:
    payload = load_marketplace(path)
    plugins = payload.setdefault("plugins", [])
    interface = payload.setdefault("interface", {})

    if not isinstance(plugins, list):
        raise ValueError(f"Marketplace field 'plugins' must be a list: {path}")
    if not isinstance(interface, dict):
        raise ValueError(f"Marketplace field 'interface' must be an object: {path}")

    payload.setdefault("name", MARKETPLACE_DEFAULT["name"])
    interface.setdefault("displayName", MARKETPLACE_DEFAULT["interface"]["displayName"])

    entry = {
        "name": PLUGIN_NAME,
        "source": {
            "source": "local",
            "path": f"./plugins/{PLUGIN_NAME}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": "Developer Tools",
    }

    for index, plugin in enumerate(plugins):
        if isinstance(plugin, dict) and plugin.get("name") == PLUGIN_NAME:
            plugins[index] = entry
            break
    else:
        plugins.append(entry)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
