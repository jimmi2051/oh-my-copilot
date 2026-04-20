from __future__ import annotations

import json
from pathlib import Path


def run_hud(project_root: Path) -> int:
    state_dir = project_root / ".omc" / "state" / "omc-copilot"
    if not state_dir.exists():
        print("HUD: no active tasks")
        return 0
    files = sorted(
        state_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not files:
        print("HUD: no active tasks")
        return 0
    latest = json.loads(files[0].read_text(encoding="utf-8"))
    mode = latest.get("mode")
    status = latest.get("status")
    iteration = latest.get("iteration")
    max_iterations = latest.get("max_iterations")
    print(
        f"HUD | mode={mode} | status={status} | iteration={iteration}/{max_iterations}"
    )
    return 0
