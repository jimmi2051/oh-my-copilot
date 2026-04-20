from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.compatibility.skill_loader import load_skills


class SkillLoaderTest(unittest.TestCase):
    def test_load_skills(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skills" / "autopilot"
            root.mkdir(parents=True, exist_ok=True)
            (root / "SKILL.md").write_text(
                "# Autopilot\n\nRun autonomous execution.", encoding="utf-8"
            )
            skills = load_skills(Path(td) / "skills")
            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0].name, "autopilot")


if __name__ == "__main__":
    unittest.main()
