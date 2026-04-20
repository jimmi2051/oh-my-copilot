from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from omc_copilot.compatibility.hook_registry import supported_hook_events
from omc_copilot.installer.hook_installer import HookInstaller


class HookInstallerTest(unittest.TestCase):
    def test_manifest_contains_supported_events(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            manifest_path = HookInstaller().install_manifest(Path(td))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["name"], "omc-copilot")
            self.assertEqual(manifest["events"], supported_hook_events())


if __name__ == "__main__":
    unittest.main()
