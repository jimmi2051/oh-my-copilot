from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.installer.merge_strategy import (END_MARKER, START_MARKER,
                                                  merge_file)


class MergeStrategyTest(unittest.TestCase):
    def test_merge_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "AGENTS.md"
            merge_file(path, "first block")
            merge_file(path, "second block")
            content = path.read_text(encoding="utf-8")
            self.assertEqual(content.count(START_MARKER), 1)
            self.assertEqual(content.count(END_MARKER), 1)
            self.assertIn("second block", content)


if __name__ == "__main__":
    unittest.main()
