from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class HistoryStore:
    def __init__(self, project_root: Path) -> None:
        self.history_dir = project_root / ".omc" / "state"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.history_dir / "omc-copilot-history.jsonl"

    def append(self, event: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=True) + "\n")
