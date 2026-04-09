#!/usr/bin/env python3
"""Install Sennen Codex skills into a target repo."""

from __future__ import annotations

import argparse
from pathlib import Path

from install_support import (
    codex_skill_source_root,
    ensure_target_repo,
    install_codex_skills,
    remove_legacy_codex_install_paths,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Sennen Codex skills into a target repo."
    )
    parser.add_argument(
        "target_repo",
        help="Path to the repo where Codex should see the local plugin.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Accepted for compatibility; Codex skills are always copied.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing installed Codex skills.",
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
        help="Exclude a skill directory such as sen-join from the installed Codex skills.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    target_repo = Path(args.target_repo).expanduser().resolve()
    ensure_target_repo(target_repo)

    remove_legacy_codex_install_paths(target_repo)
    installed_codex_skills = install_codex_skills(
        codex_skill_source_root(),
        target_repo / ".agents" / "skills",
        exclude_skill_names=args.exclude_skill,
    )

    if not args.quiet:
        print(f"Installed {len(installed_codex_skills)} Codex skills into {target_repo / '.agents' / 'skills'}")


if __name__ == "__main__":
    main()
