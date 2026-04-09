#!/usr/bin/env python3
"""Install Sennen into personal Codex skills directories."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from install_support import codex_skill_source_root, install_codex_skills


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Sennen into personal Codex skills directories."
    )
    parser.add_argument(
        "--home",
        default=str(Path.home()),
        help="Home directory where Codex personal skill folders should be installed.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress status output for wrapper scripts.",
    )
    parser.add_argument(
        "--exclude-skill",
        action="append",
        default=[],
        help="Exclude a skill directory such as sen-join from the installed skills.",
    )
    return parser.parse_args()


def remove_legacy_plugin_install(home_dir: Path) -> None:
    legacy_paths = [
        home_dir / ".codex" / "plugins" / "sennen",
        home_dir / ".agents" / "plugins",
    ]
    for path in legacy_paths:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            shutil.rmtree(path)


def main() -> None:
    args = parse_args()
    home_dir = Path(args.home).expanduser().resolve()
    remove_legacy_plugin_install(home_dir)

    skills_dir = home_dir / ".codex" / "skills"
    installed = install_codex_skills(
        codex_skill_source_root(),
        skills_dir,
        exclude_skill_names=args.exclude_skill,
    )

    if not args.quiet:
        print(f"Installed {len(installed)} Codex skills into {skills_dir}")


if __name__ == "__main__":
    main()
