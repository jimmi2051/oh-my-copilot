from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omc_copilot.installer.codex_skill_installer import (
    CODEX_ADAPTATION_MARKER,
    CodexSkillInstaller,
    default_codex_skills_dir,
    expected_codex_skill_dirs,
)


class CodexSkillInstallerTest(unittest.TestCase):
    def test_default_skills_dir_uses_codex_home(self) -> None:
        with patch.dict("os.environ", {"CODEX_HOME": "/tmp/codex-home"}):
            self.assertEqual(default_codex_skills_dir(), Path("/tmp/codex-home/skills"))

    def test_expected_skill_dirs_are_namespaced(self) -> None:
        root = Path("/tmp/skills")
        paths = expected_codex_skill_dirs(root)
        self.assertIn(root / "omc-copilot-ask", paths)
        self.assertIn(root / "omc-copilot-team", paths)
        self.assertIn(root / "omc-copilot-ultrawork", paths)
        self.assertNotIn(root / "omc-copilot-claudecode-debug", paths)
        self.assertEqual(len(paths), 13)

    def test_install_is_idempotent_and_replaces_managed_skill(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "omc_copilot"
        with tempfile.TemporaryDirectory() as td:
            skills_root = Path(td) / "skills"
            stale_skill = skills_root / "omc-copilot-ask"
            stale_skill.mkdir(parents=True)
            (stale_skill / "stale.txt").write_text("old", encoding="utf-8")

            installer = CodexSkillInstaller(package_root=package_root)
            first = installer.install(skills_root)
            second = installer.install(skills_root)

            template_count = sum(
                1 for path in installer.templates_root.iterdir() if path.is_dir()
            )
            self.assertEqual(len(first.skill_dirs), template_count)
            self.assertEqual(len(second.skill_dirs), template_count)
            self.assertFalse((stale_skill / "stale.txt").exists())
            self.assertTrue((stale_skill / "SKILL.md").exists())
            self.assertTrue((skills_root / "omc-copilot-team" / "SKILL.md").exists())

    def test_install_adds_codex_adaptation_to_every_skill(self) -> None:
        package_root = Path(__file__).resolve().parents[1] / "omc_copilot"
        with tempfile.TemporaryDirectory() as td:
            skills_root = Path(td) / "skills"

            result = CodexSkillInstaller(package_root=package_root).install(skills_root)

            for skill_dir in result.skill_dirs:
                content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(CODEX_ADAPTATION_MARKER, content)
                self.assertIn("omc-copilot ... --runtime codex", content)
                if content.startswith("---\n"):
                    frontmatter_end = content.find("\n---\n", 4)
                    self.assertGreater(frontmatter_end, 0)
                    self.assertGreater(
                        content.find(CODEX_ADAPTATION_MARKER), frontmatter_end
                    )


if __name__ == "__main__":
    unittest.main()
