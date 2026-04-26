from __future__ import annotations

from pathlib import Path

from .run import run_task


def run_team(
    task: str, cwd: Path, max_iterations: int, runtime_name: str | None = None
) -> int:
    return run_task(
        prompt=task,
        mode="team",
        max_iterations=max_iterations,
        cwd=cwd,
        runtime_name=runtime_name,
    )
