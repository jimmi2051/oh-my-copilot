from __future__ import annotations

from pathlib import Path

from omc_copilot.execution.command_runner import run_command
from omc_copilot.schemas.agent_io import TesterOutput

from .base import AgentContext


class TesterAgent:
    def _detect_command(self, root: Path) -> list[str]:
        if (root / "pyproject.toml").exists():
            return ["python", "-m", "unittest", "discover", "-s", "tests"]
        if (root / "package.json").exists():
            return ["npm", "test", "--silent"]
        return []

    def run(self, context: AgentContext) -> TesterOutput:
        command = self._detect_command(context.project_root)
        if not command:
            return TesterOutput(passed=True, summary="No test command detected; skipped.", details="")

        result = run_command(command, cwd=context.project_root)
        summary = "Tests passed" if result.ok else "Tests failed"
        details = "\n".join(filter(None, [result.stdout, result.stderr]))
        return TesterOutput(passed=result.ok, summary=summary, details=details)
