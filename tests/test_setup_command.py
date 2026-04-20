from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.cli.commands.setup import run_setup
from omc_copilot.installer.setup_wizard import SetupResult


class SetupCommandTest(unittest.TestCase):
    def test_setup_aborts_when_plugin_manifest_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            package_root = Path(td) / "package"
            package_root.mkdir(parents=True, exist_ok=True)
            target = Path(td) / "target"

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.setup.SetupWizard") as wizard_cls:
                with contextlib.redirect_stdout(output):
                    code = run_setup(target=target, package_root=package_root)

            self.assertEqual(code, 1)
            wizard_cls.assert_not_called()
            text = output.getvalue()
            self.assertIn("MISSING", text)
            self.assertIn("plugins/omc-copilot/plugin.json", text)

    def test_setup_prints_plugin_guidance_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            package_root = Path(td) / "package"
            plugin_manifest = package_root / "plugins" / "omc-copilot" / "plugin.json"
            plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
            plugin_manifest.write_text("{}", encoding="utf-8")
            target = Path(td) / "target"
            setup_result = SetupResult(
                target_root=target,
                instruction_files=[target / "AGENTS.md"],
                hook_manifest=target / ".omc" / "hooks" / "omc-copilot-hooks.json",
            )

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.setup.SetupWizard") as wizard_cls:
                wizard_cls.return_value.run.return_value = setup_result
                with contextlib.redirect_stdout(output):
                    code = run_setup(target=target, plugin_guidance=True, package_root=package_root)

            self.assertEqual(code, 0)
            wizard_cls.assert_called_once_with(package_root=package_root)
            text = output.getvalue()
            self.assertIn("copilot plugin install", text)
            self.assertIn(str(plugin_manifest.parent), text)


if __name__ == "__main__":
    unittest.main()
