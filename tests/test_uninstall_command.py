from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.cli.main import main
from omc_copilot.cli.commands.uninstall import run_uninstall
from omc_copilot.installer.merge_strategy import END_MARKER, START_MARKER


class UninstallCommandTest(unittest.TestCase):
    def test_uninstall_codex_removes_managed_assets_and_preserves_user_content(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target"
            skills_root = Path(td) / "skills"
            target.mkdir()
            (target / "AGENTS.md").write_text(
                "# user notes\n\n"
                f"{START_MARKER}\nmanaged OMC content\n{END_MARKER}\n\n"
                "after notes\n",
                encoding="utf-8",
            )
            hook_manifest = target / ".omc" / "hooks" / "omc-copilot-hooks.json"
            hook_manifest.parent.mkdir(parents=True)
            hook_manifest.write_text("{}", encoding="utf-8")
            state_file = target / ".omc" / "state" / "omc-copilot-history.jsonl"
            state_file.parent.mkdir(parents=True)
            state_file.write_text("keep\n", encoding="utf-8")
            skill_dir = skills_root / "omc-copilot-ask"
            skill_dir.mkdir(parents=True)
            (skills_root / "other-skill").mkdir()

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = run_uninstall(
                    target=target,
                    runtime_name="codex",
                    codex_skills_dir=skills_root,
                )

            agents = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(code, 0)
            self.assertIn("# user notes", agents)
            self.assertIn("after notes", agents)
            self.assertNotIn(START_MARKER, agents)
            self.assertFalse(hook_manifest.exists())
            self.assertFalse(skill_dir.exists())
            self.assertTrue((skills_root / "other-skill").exists())
            self.assertTrue(state_file.exists())
            self.assertIn("- runtime: codex", output.getvalue())

    def test_main_routes_uninstall_codex_options(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target"
            skills_root = Path(td) / "skills"

            with patch("omc_copilot.cli.main.run_uninstall") as run:
                run.return_value = 0
                code = main(
                    [
                        "uninstall",
                        "--target",
                        str(target),
                        "--runtime",
                        "codex",
                        "--codex-skills-dir",
                        str(skills_root),
                    ]
                )

            self.assertEqual(code, 0)
            run.assert_called_once_with(
                target.resolve(),
                runtime_name="codex",
                codex_skills_dir=skills_root.resolve(),
            )


if __name__ == "__main__":
    unittest.main()
