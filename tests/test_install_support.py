from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from sennen.scripts import install_support


class InstallSupportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="sennen-install-support-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

    def test_update_marketplace_creates_expected_entry(self) -> None:
        marketplace = self.tmpdir / ".agents" / "plugins" / "marketplace.json"

        install_support.update_marketplace(marketplace)

        payload = json.loads(marketplace.read_text())
        self.assertEqual(payload["name"], "local-plugins")
        self.assertEqual(payload["interface"]["displayName"], "Local Plugins")
        self.assertEqual(len(payload["plugins"]), 1)
        self.assertEqual(payload["plugins"][0]["name"], "sennen")
        self.assertEqual(payload["plugins"][0]["source"]["path"], "./plugins/sennen")

    def test_update_marketplace_preserves_other_plugins_and_replaces_sennen(self) -> None:
        marketplace = self.tmpdir / "marketplace.json"
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
        self.assertEqual(len(payload["plugins"]), 2)
        self.assertEqual(payload["plugins"][0]["name"], "other")
        self.assertEqual(payload["plugins"][1]["name"], "sennen")
        self.assertEqual(payload["plugins"][1]["source"]["path"], "./plugins/sennen")

    def test_install_plugin_dir_symlinks_by_default(self) -> None:
        source = self.tmpdir / "source"
        source.mkdir()
        (source / "file.txt").write_text("hello")
        destination = self.tmpdir / "dest" / "plugin"

        install_support.install_plugin_dir(source, destination, copy_mode=False, force=False)

        self.assertTrue(destination.is_symlink())
        self.assertEqual(os.readlink(destination), str(source))

    def test_install_plugin_dir_copies_when_requested(self) -> None:
        source = self.tmpdir / "source"
        source.mkdir()
        (source / "file.txt").write_text("hello")
        destination = self.tmpdir / "dest" / "plugin"

        install_support.install_plugin_dir(source, destination, copy_mode=True, force=False)

        self.assertTrue(destination.is_dir())
        self.assertFalse(destination.is_symlink())
        self.assertEqual((destination / "file.txt").read_text(), "hello")

    def test_install_codex_skills_copies_root_and_child_skills(self) -> None:
        plugin_root = self.tmpdir / "plugin"
        source_root = plugin_root / "skills"
        target_repo = self.tmpdir / "repo"
        (plugin_root / "SKILL.md").parent.mkdir(parents=True)
        (plugin_root / "SKILL.md").write_text("# root\n")
        (source_root / "data").mkdir(parents=True)
        (source_root / "data" / "SKILL.md").write_text("# data\n")
        (source_root / "metrics").mkdir(parents=True)
        (source_root / "metrics" / "SKILL.md").write_text("# metrics\n")

        installed = install_support.install_codex_skills(source_root, plugin_root, target_repo)

        self.assertEqual(len(installed), 3)
        self.assertEqual((target_repo / ".agents" / "skills" / "sennen" / "SKILL.md").read_text(), "# root\n")
        self.assertEqual(
            (target_repo / ".agents" / "skills" / "sennen-data" / "SKILL.md").read_text(),
            "# data\n",
        )
        self.assertEqual(
            (target_repo / ".agents" / "skills" / "sennen-metrics" / "SKILL.md").read_text(),
            "# metrics\n",
        )


if __name__ == "__main__":
    unittest.main()
