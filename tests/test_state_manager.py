from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.schemas.state import TaskState, TaskStatus
from omc_copilot.state.state_manager import StateManager


class StateManagerTest(unittest.TestCase):
    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manager = StateManager(root)
            state = TaskState(
                task_id="task-1",
                prompt="demo",
                status=TaskStatus.ACTIVE,
                mode="autopilot",
                iteration=1,
                max_iterations=5,
            )
            manager.save(state)
            loaded = manager.load("task-1")
            self.assertIsNotNone(loaded)
            assert loaded is not None
            self.assertEqual(loaded["task_id"], "task-1")
            self.assertEqual(loaded["mode"], "autopilot")


if __name__ == "__main__":
    unittest.main()
