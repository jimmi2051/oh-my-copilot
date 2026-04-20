from __future__ import annotations

from pathlib import Path

from omc_copilot.adapters.copilot_cli import CopilotRuntimeAdapter


def run_ask(prompt: str, cwd: Path) -> int:
    runtime = CopilotRuntimeAdapter(working_dir=cwd)
    reply = runtime.generate(prompt)
    print(reply.text)
    return 0
