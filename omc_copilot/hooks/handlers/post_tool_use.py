from __future__ import annotations


def handle_post_tool_use(tool_name: str, ok: bool) -> dict[str, str | bool]:
    return {
        "event": "PostToolUse",
        "tool_name": tool_name,
        "ok": ok,
        "status": "handled",
    }
