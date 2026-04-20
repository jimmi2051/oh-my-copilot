from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Optional

from omc_copilot.schemas.state import TaskState
from omc_copilot.utils.serialization import read_json, write_json


class StateManager:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.state_dir = project_root / ".omc" / "state" / "omc-copilot"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def task_state_path(self, task_id: str) -> Path:
        return self.state_dir / f"{task_id}.json"

    def save(self, state: TaskState) -> Path:
        path = self.task_state_path(state.task_id)
        write_json(path, asdict(state))
        return path

    def load(self, task_id: str) -> Optional[dict]:
        path = self.task_state_path(task_id)
        if not path.exists():
            return None
        return read_json(path)
