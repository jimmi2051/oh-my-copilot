from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from subprocess import CompletedProcess

from omc_copilot.cli.commands.doctor import run_doctor


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class DoctorCommandTest(unittest.TestCase):
    def _create_base_project(self, root: Path) -> None:
        _write(root / "AGENTS.md", "# agents\n")
        _write(root / ".github" / "copilot-instructions.md", "# instructions\n")
        _write(root / ".github" / "instructions" / "omc.instructions.md", "# omc\n")
        _write(root / ".github" / "plugin" / "marketplace.json", '{"name":"omc-copilot"}')

    def test_doctor_reports_plugin_and_marketplace_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._create_base_project(root)
            _write(
                root / "plugins" / "omc-copilot" / "plugin.json",
                '{"agents":"agents","skills":"skills","hooks":"hooks.json"}',
            )
            (root / "plugins" / "omc-copilot" / "agents").mkdir(parents=True, exist_ok=True)
            (root / "plugins" / "omc-copilot" / "skills").mkdir(parents=True, exist_ok=True)
            _write(root / "plugins" / "omc-copilot" / "hooks.json", '{"name":"hooks"}')

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.doctor.shutil.which", return_value="/usr/local/bin/copilot"):
                with contextlib.redirect_stdout(output):
                    code = run_doctor(root)

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn(".github/plugin/marketplace.json", text)
            self.assertIn("plugins/omc-copilot/agents", text)
            self.assertNotIn("MISSING", text)
            self.assertNotIn("INVALID", text)

    def test_doctor_flags_invalid_plugin_manifest_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._create_base_project(root)
            _write(root / "plugins" / "omc-copilot" / "plugin.json", "{not-json")
            (root / "plugins" / "omc-copilot" / "agents").mkdir(parents=True, exist_ok=True)
            (root / "plugins" / "omc-copilot" / "skills").mkdir(parents=True, exist_ok=True)
            _write(root / "plugins" / "omc-copilot" / "hooks.json", '{"name":"hooks"}')

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.doctor.shutil.which", return_value="/usr/local/bin/copilot"):
                with contextlib.redirect_stdout(output):
                    code = run_doctor(root)

            self.assertEqual(code, 1)
            text = output.getvalue()
            self.assertIn("INVALID", text)
            self.assertIn("plugins/omc-copilot/plugin.json", text)

    def test_doctor_skips_local_plugin_checks_in_consumer_repo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "AGENTS.md", "# agents\n")
            _write(root / ".github" / "copilot-instructions.md", "# instructions\n")
            _write(root / ".github" / "instructions" / "omc.instructions.md", "# omc\n")

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.doctor.shutil.which", return_value="/usr/local/bin/copilot"):
                with patch(
                    "omc_copilot.cli.commands.doctor.subprocess.run",
                    return_value=CompletedProcess(args=["copilot", "plugin", "list"], returncode=0, stdout="omc-copilot", stderr=""),
                ):
                    with contextlib.redirect_stdout(output):
                        code = run_doctor(root)

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn("plugin-package-scope", text)
            self.assertIn("copilot-plugin-install", text)
            self.assertNotIn("plugins/omc-copilot/plugin.json", text)


if __name__ == "__main__":
    unittest.main()
