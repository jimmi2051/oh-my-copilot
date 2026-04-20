from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .command_runner import CommandResult, run_command


@dataclass(slots=True)
class CopilotSuggestResult:
    prompt: str
    output: str
    command: list[str]


@dataclass(slots=True)
class CopilotExplainResult:
    code: str
    explanation: str
    command: list[str]


class CopilotWrapper:
    def __init__(self, working_dir: Optional[Path] = None) -> None:
        self.working_dir = working_dir
        self._require_copilot()

    @staticmethod
    def _require_copilot() -> None:
        if not shutil.which("copilot"):
            raise RuntimeError(
                "GitHub Copilot CLI executable `copilot` is not installed or not in PATH."
            )

    def _run(self, prompt: str) -> CommandResult:
        command = ["copilot", "-p", prompt]
        result = run_command(command, cwd=self.working_dir)
        if not result.ok:
            raise RuntimeError(
                f"copilot command failed (code={result.returncode}): {result.stderr or result.stdout}"
            )
        return result

    def run_copilot(self, prompt: str) -> CopilotSuggestResult:
        result = self._run(prompt)
        return CopilotSuggestResult(prompt=prompt, output=result.stdout, command=result.command)

    def explain_code(self, code: str) -> CopilotExplainResult:
        explain_prompt = (
            "Explain the following code with focus on logic, edge cases, and risks.\n\n"
            "```text\n"
            f"{code}\n"
            "```"
        )
        result = self._run(explain_prompt)
        return CopilotExplainResult(code=code, explanation=result.stdout, command=result.command)
