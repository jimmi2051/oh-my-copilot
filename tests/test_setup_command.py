from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.cli.commands.setup import run_setup
from omc_copilot.installer.merge_strategy import END_MARKER, START_MARKER
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
                    code = run_setup(
                        target=target, plugin_guidance=True, package_root=package_root
                    )

            self.assertEqual(code, 0)
            wizard_cls.assert_called_once_with(package_root=package_root)
            text = output.getvalue()
            self.assertIn("copilot plugin install", text)
            self.assertIn(str(plugin_manifest.parent), text)

    def test_setup_codex_skips_plugin_manifest_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            package_root = Path(td) / "package"
            package_root.mkdir(parents=True, exist_ok=True)
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
                    code = run_setup(
                        target=target,
                        package_root=package_root,
                        runtime_name="codex",
                    )

            self.assertEqual(code, 0)
            wizard_cls.return_value.run.assert_called_once_with(
                target_root=target, runtime_name="codex", codex_skills_dir=None
            )
            text = output.getvalue()
            self.assertIn("SKIPPED", text)
            self.assertIn("- runtime: codex", text)

    def test_setup_both_requires_plugin_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            package_root = Path(td) / "package"
            package_root.mkdir(parents=True, exist_ok=True)
            target = Path(td) / "target"

            output = io.StringIO()
            with patch("omc_copilot.cli.commands.setup.SetupWizard") as wizard_cls:
                with contextlib.redirect_stdout(output):
                    code = run_setup(
                        target=target,
                        package_root=package_root,
                        runtime_name="both",
                    )

            self.assertEqual(code, 1)
            wizard_cls.assert_not_called()
            self.assertIn("MISSING", output.getvalue())

    def test_setup_copilot_passes_runtime_to_wizard(self) -> None:
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
                    code = run_setup(
                        target=target,
                        package_root=package_root,
                        runtime_name="copilot",
                    )

            self.assertEqual(code, 0)
            wizard_cls.return_value.run.assert_called_once_with(
                target_root=target, runtime_name="copilot", codex_skills_dir=None
            )
            self.assertIn("- runtime: copilot", output.getvalue())

    def test_setup_codex_is_idempotent_and_installs_codex_skills(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "omc_copilot"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target"
            skills_root = Path(td) / "codex-skills"
            target.mkdir(parents=True, exist_ok=True)
            (target / "AGENTS.md").write_text(
                "# user notes\n\n" f"{START_MARKER}\nold managed block\n{END_MARKER}\n",
                encoding="utf-8",
            )

            with contextlib.redirect_stdout(io.StringIO()):
                first_code = run_setup(
                    target=target,
                    package_root=package_root,
                    runtime_name="codex",
                    codex_skills_dir=skills_root,
                )
                second_code = run_setup(
                    target=target,
                    package_root=package_root,
                    runtime_name="codex",
                    codex_skills_dir=skills_root,
                )

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(first_code, 0)
            self.assertEqual(second_code, 0)
            self.assertEqual(agents.count(START_MARKER), 1)
            self.assertEqual(agents.count(END_MARKER), 1)
            self.assertIn("# user notes", agents)
            self.assertIn("Codex runtime usage:", agents)
            self.assertFalse((target / ".github" / "copilot-instructions.md").exists())
            self.assertTrue((skills_root / "omc-copilot-ask" / "SKILL.md").exists())
            self.assertTrue((skills_root / "omc-copilot-team" / "SKILL.md").exists())

    def test_setup_both_installs_copilot_assets(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "omc_copilot"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target"
            skills_root = Path(td) / "codex-skills"

            with contextlib.redirect_stdout(io.StringIO()):
                code = run_setup(
                    target=target,
                    package_root=package_root,
                    runtime_name="both",
                    codex_skills_dir=skills_root,
                )

            self.assertEqual(code, 0)
            self.assertTrue((target / "AGENTS.md").exists())
            self.assertTrue((target / ".github" / "copilot-instructions.md").exists())
            self.assertTrue(
                (target / ".github" / "instructions" / "omc.instructions.md").exists()
            )
            self.assertTrue(
                (skills_root / "omc-copilot-autopilot" / "SKILL.md").exists()
            )

    def test_setup_codex_prints_installed_skill_paths(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "omc_copilot"
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target"
            skills_root = Path(td) / "codex-skills"

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_setup(
                    target=target,
                    package_root=package_root,
                    runtime_name="codex",
                    codex_skills_dir=skills_root,
                )

            self.assertEqual(code, 0)
            text = output.getvalue()
            self.assertIn("- codex skill:", text)
            self.assertIn("omc-copilot-ask", text)


if __name__ == "__main__":
    unittest.main()
