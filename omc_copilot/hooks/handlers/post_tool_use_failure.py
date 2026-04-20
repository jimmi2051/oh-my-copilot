from __future__ import annotations


def handle_post_tool_use_failure(
    tool_name: str,
    error: str,
    exit_code: int,
) -> dict[str, str | int]:
    return {
        "event": "PostToolUseFailure",
        "tool_name": tool_name,
        "error": error,
        "exit_code": exit_code,
        "status": "handled",
    }
