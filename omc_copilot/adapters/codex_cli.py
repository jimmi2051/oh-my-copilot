from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from omc_copilot.execution.command_runner import run_command

from .runtime_base import RuntimeAdapter, RuntimeReply


class CodexRuntimeAdapter(RuntimeAdapter):
    def __init__(self, working_dir: Optional[Path] = None) -> None:
        self.working_dir = working_dir
        self._require_codex()

    @staticmethod
    def _require_codex() -> None:
        if not shutil.which("codex"):
            raise RuntimeError(
                "Codex CLI executable `codex` is not installed or not in PATH."
            )

    def generate(self, prompt: str) -> RuntimeReply:
        command = [
            "codex",
            "exec",
            "--sandbox",
            "read-only",
            "-c",
            'approval_policy="never"',
        ]
        if self.working_dir:
            command.extend(["--cd", str(self.working_dir)])
        command.append(prompt)

        result = run_command(command, cwd=self.working_dir)
        if not result.ok:
            details = result.stderr or result.stdout
            raise RuntimeError(
                f"codex command failed (code={result.returncode}): {details}"
            )
        return RuntimeReply(prompt=prompt, text=result.stdout)
