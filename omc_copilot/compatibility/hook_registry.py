from __future__ import annotations

HOOK_EVENTS: tuple[str, ...] = (
    "UserPromptSubmit",
    "SessionStart",
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "PostToolUseFailure",
    "SubagentStart",
    "SubagentStop",
    "PreCompact",
    "Stop",
    "SessionEnd",
)


def supported_hook_events() -> list[str]:
    return list(HOOK_EVENTS)
