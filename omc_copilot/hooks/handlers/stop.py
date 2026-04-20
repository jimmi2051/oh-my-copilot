from __future__ import annotations


def handle_stop(active_mode: str | None) -> dict[str, str | None]:
    return {"event": "Stop", "active_mode": active_mode, "status": "handled"}
