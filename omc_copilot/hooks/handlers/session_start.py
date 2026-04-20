from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def handle_session_start(project_root: Path) -> dict:
    return {
        "event": "SessionStart",
        "project_root": str(project_root),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "handled",
    }
