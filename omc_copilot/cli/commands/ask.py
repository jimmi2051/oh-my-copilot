from __future__ import annotations

from pathlib import Path

from omc_copilot.adapters.runtime_factory import build_runtime_adapter


def run_ask(prompt: str, cwd: Path, runtime_name: str | None = None) -> int:
    runtime = build_runtime_adapter(runtime_name, working_dir=cwd)
    reply = runtime.generate(prompt)
    print(reply.text)
    return 0
