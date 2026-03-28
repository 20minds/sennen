#!/usr/bin/env python3
"""Install the Sennen plugin into a target repo as a repo-local Codex plugin."""

from __future__ import annotations

import argparse
from pathlib import Path

from install_support import (
    PLUGIN_NAME,
    codex_skill_source_root,
    ensure_target_repo,
    install_codex_skills,
    install_plugin_dir,
    plugin_source_root,
    update_marketplace,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the Sennen plugin into a target repo."
    )
    parser.add_argument(
        "target_repo",
        help="Path to the repo where Codex should see the local plugin.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy the plugin directory instead of creating a symlink.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing plugin directory or symlink.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress status output for wrapper scripts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_repo = Path(args.target_repo).expanduser().resolve()
    ensure_target_repo(target_repo)

    source = plugin_source_root()
    destination = target_repo / "plugins" / PLUGIN_NAME
    marketplace_path = target_repo / ".agents" / "plugins" / "marketplace.json"

    install_plugin_dir(source, destination, copy_mode=args.copy, force=args.force)
    update_marketplace(marketplace_path)
    installed_codex_skills = install_codex_skills(codex_skill_source_root(), source, target_repo)

    if not args.quiet:
        mode = "copied" if args.copy else "symlinked"
        print(f"{PLUGIN_NAME} {mode} into {destination}")
        print(f"Updated marketplace: {marketplace_path}")
        print(
            f"Installed {len(installed_codex_skills)} Codex skills into {target_repo / '.agents' / 'skills'}"
        )
        print(
            "Codex should discover the Sennen plugin skills from the plugin and .agents/skills, including the /sen:* command family described in the docs."
        )


if __name__ == "__main__":
    main()
