from __future__ import annotations

from datetime import datetime, timezone


def handle_session_end(summary: str) -> dict:
    return {
        "event": "SessionEnd",
        "summary": summary,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "handled",
    }
