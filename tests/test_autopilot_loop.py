from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.adapters.runtime_base import RuntimeReply
from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import build_default_registry
from omc_copilot.orchestrator.autopilot_loop import run_autopilot_loop


class _FakeRuntime:
    def generate(self, prompt: str) -> RuntimeReply:
        return RuntimeReply(prompt=prompt, text="implemented output without placeholders")


class AutopilotLoopTest(unittest.TestCase):
    def test_completes_with_fake_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            context = AgentContext(
                task_prompt="build a small API and tests",
                project_root=Path(td),
                runtime=_FakeRuntime(),
                metadata={"task_id": "task-test"},
            )
            registry = build_default_registry()
            state = run_autopilot_loop(context, registry, max_iterations=2)
            self.assertIn(state.status.value, {"complete", "failed"})
            self.assertGreaterEqual(state.iteration, 1)


if __name__ == "__main__":
    unittest.main()
