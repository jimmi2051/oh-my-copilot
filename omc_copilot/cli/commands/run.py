from __future__ import annotations

import json
from pathlib import Path

from omc_copilot.orchestrator.engine import OrchestratorEngine


def run_task(
    prompt: str,
    mode: str | None,
    max_iterations: int,
    cwd: Path,
    runtime_name: str | None = None,
) -> int:
    engine = OrchestratorEngine(project_root=cwd, runtime=runtime_name)
    state = engine.run(prompt=prompt, mode=mode, max_iterations=max_iterations)
    print(json.dumps(engine.state_to_dict(state), indent=2))
    return 0 if state.status.value == "complete" else 1
