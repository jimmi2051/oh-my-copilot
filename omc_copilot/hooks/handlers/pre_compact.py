from __future__ import annotations


def handle_pre_compact(reason: str | None, messages_before: int) -> dict[str, str | int | None]:
    return {
        "event": "PreCompact",
        "reason": reason,
        "messages_before": messages_before,
        "status": "handled",
    }
