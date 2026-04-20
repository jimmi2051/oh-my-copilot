from __future__ import annotations


def handle_permission_request(
    tool_name: str,
    reason: str | None,
    requires_approval: bool,
) -> dict[str, str | bool | None]:
    return {
        "event": "PermissionRequest",
        "tool_name": tool_name,
        "reason": reason,
        "requires_approval": requires_approval,
        "decision": "prompt-user" if requires_approval else "auto-allow",
        "status": "handled",
    }
