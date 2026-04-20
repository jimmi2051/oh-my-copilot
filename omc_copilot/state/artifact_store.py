from __future__ import annotations

from pathlib import Path


class ArtifactStore:
    def __init__(self, project_root: Path) -> None:
        self.root = project_root / ".omc" / "artifacts" / "omc-copilot"
        self.root.mkdir(parents=True, exist_ok=True)

    def write_text(self, task_id: str, name: str, content: str) -> Path:
        target_dir = self.root / task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / name
        path.write_text(content, encoding="utf-8")
        return path
