from __future__ import annotations


def handle_pre_tool_use(tool_name: str) -> dict[str, str]:
    return {"event": "PreToolUse", "tool_name": tool_name, "status": "handled"}
