from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from omc_copilot.cli.commands.doctor import run_doctor
from omc_copilot.installer.codex_skill_installer import \
    expected_codex_skill_dirs
from omc_copilot.installer.merge_strategy import END_MARKER, START_MARKER


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_codex_skills(skills_root: Path) -> None:
    for skill_dir in expected_codex_skill_dirs(skills_root):
        _write(skill_dir / "SKILL.md", "---\nname: test\n---\n")


class DoctorCommandTest(unittest.TestCase):
    def _create_base_project(self, root: Path) -> None:
        _write(root / "AGENTS.md", "# agents\n")
        _write(root / ".github" / "copilot-instructions.md", "# instructions\n")
        _write(root / ".github" / "instructions" / "omc.instructions.md", "# omc\n")
        _write(
            root / ".github" / "plugin" / "marketplace.json", '{"name":"omc-copilot"}'
        )

    def test_doctor_reports_plugin_and_marketplace_assets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._create_base_project(root)
            _write(
                root / "plugins" / "omc-copilot" / "plugin.json",
                '{"agents":"agents","skills":"skills","hooks":"hooks.json"}',
            )
            (root / "plugins" / "omc-copilot" / "agents").mkdir(
                parents=True, exist_ok=True
            )
            (root / "plugins" / "omc-copilot" / "skills").mkdir(
                parents=True, exist_ok=True
            )
            _write(root / "plugins" / "omc-copilot" / "hooks.json", '{"name":"hooks"}')

            output = io.StringIO()
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/copilot",
            ):
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
            (root / "plugins" / "omc-copilot" / "agents").mkdir(
                parents=True, exist_ok=True
            )
            (root / "plugins" / "omc-copilot" / "skills").mkdir(
                parents=True, exist_ok=True
            )
            _write(root / "plugins" / "omc-copilot" / "hooks.json", '{"name":"hooks"}')

            output = io.StringIO()
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/copilot",
            ):
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
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/copilot",
            ):
                with patch(
                    "omc_copilot.cli.commands.doctor.subprocess.run",
                    return_value=CompletedProcess(
                        args=["copilot", "plugin", "list"],
                        returncode=0,
                        stdout="omc-copilot",
                        stderr="",
                    ),
                ):
                    with contextlib.redirect_stdout(output):
                        code = run_doctor(root)

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn("plugin-package-scope", text)
            self.assertIn("copilot-plugin-install", text)
            self.assertNotIn("plugins/omc-copilot/plugin.json", text)

    def test_doctor_codex_checks_codex_cli_and_agents_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(
                root / "AGENTS.md",
                f"{START_MARKER}\n# oh-my-copilot\n{END_MARKER}\n",
            )
            skills_root = root / "codex-skills"
            _write_codex_skills(skills_root)

            output = io.StringIO()
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/codex",
            ):
                with contextlib.redirect_stdout(output):
                    code = run_doctor(
                        root, runtime_name="codex", codex_skills_dir=skills_root
                    )

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn("selected runtime: codex", text)
            self.assertIn("codex-cli", text)
            self.assertIn("OMC managed instruction block", text)
            self.assertIn("omc-copilot-ask", text)
            self.assertNotIn("copilot-cli", text)

    def test_doctor_both_reports_copilot_and_codex_checks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / ".github" / "copilot-instructions.md", "# instructions\n")
            _write(root / ".github" / "instructions" / "omc.instructions.md", "# omc\n")
            _write(
                root / "AGENTS.md",
                f"{START_MARKER}\n# oh-my-copilot\n{END_MARKER}\n",
            )
            skills_root = root / "codex-skills"
            _write_codex_skills(skills_root)

            output = io.StringIO()
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/tool",
            ):
                with patch(
                    "omc_copilot.cli.commands.doctor.subprocess.run",
                    return_value=CompletedProcess(
                        args=["copilot", "plugin", "list"],
                        returncode=0,
                        stdout="omc-copilot",
                        stderr="",
                    ),
                ):
                    with contextlib.redirect_stdout(output):
                        code = run_doctor(
                            root, runtime_name="both", codex_skills_dir=skills_root
                        )

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn("selected runtime: both", text)
            self.assertIn("copilot-cli", text)
            self.assertIn("codex-cli", text)

    def test_doctor_codex_flags_missing_skills(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(
                root / "AGENTS.md",
                f"{START_MARKER}\n# oh-my-copilot\n{END_MARKER}\n",
            )

            output = io.StringIO()
            with patch(
                "omc_copilot.cli.commands.doctor.shutil.which",
                return_value="/usr/local/bin/codex",
            ):
                with contextlib.redirect_stdout(output):
                    code = run_doctor(
                        root,
                        runtime_name="codex",
                        codex_skills_dir=root / "missing-skills",
                    )

            self.assertEqual(code, 1)
            text = output.getvalue()
            self.assertIn("MISSING", text)
            self.assertIn("Codex OMC skill", text)


if __name__ == "__main__":
    unittest.main()
