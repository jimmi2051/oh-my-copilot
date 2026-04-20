from __future__ import annotations

from pathlib import Path
from typing import Any

from omc_copilot.compatibility.hook_registry import supported_hook_events

from .handlers.permission_request import handle_permission_request
from .handlers.post_tool_use_failure import handle_post_tool_use_failure
from .handlers.post_tool_use import handle_post_tool_use
from .handlers.pre_compact import handle_pre_compact
from .handlers.pre_tool_use import handle_pre_tool_use
from .handlers.session_end import handle_session_end
from .handlers.session_start import handle_session_start
from .handlers.stop import handle_stop
from .handlers.subagent_start import handle_subagent_start
from .handlers.subagent_stop import handle_subagent_stop
from .handlers.user_prompt_submit import handle_user_prompt_submit


def _as_str(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _as_optional_str(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return default


class HookDispatcher:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def dispatch(self, event: str, **kwargs: Any) -> dict[str, Any]:
        if event == "SessionStart":
            return handle_session_start(self.project_root)
        if event == "UserPromptSubmit":
            return handle_user_prompt_submit(_as_str(kwargs.get("prompt")))
        if event == "PreToolUse":
            return handle_pre_tool_use(_as_str(kwargs.get("tool_name")))
        if event == "PermissionRequest":
            return handle_permission_request(
                tool_name=_as_str(kwargs.get("tool_name")),
                reason=_as_optional_str(kwargs.get("reason")),
                requires_approval=_as_bool(kwargs.get("requires_approval"), default=True),
            )
        if event == "PostToolUse":
            return handle_post_tool_use(
                tool_name=_as_str(kwargs.get("tool_name")),
                ok=_as_bool(kwargs.get("ok"), default=False),
            )
        if event == "PostToolUseFailure":
            return handle_post_tool_use_failure(
                tool_name=_as_str(kwargs.get("tool_name")),
                error=_as_str(kwargs.get("error"), default="unknown error"),
                exit_code=_as_int(kwargs.get("exit_code"), default=1),
            )
        if event == "SubagentStart":
            return handle_subagent_start(
                agent_name=_as_str(kwargs.get("agent_name")),
                task_id=_as_optional_str(kwargs.get("task_id")),
            )
        if event == "SubagentStop":
            return handle_subagent_stop(
                agent_name=_as_str(kwargs.get("agent_name")),
                outcome=_as_str(kwargs.get("outcome"), default="completed"),
            )
        if event == "PreCompact":
            return handle_pre_compact(
                reason=_as_optional_str(kwargs.get("reason")),
                messages_before=_as_int(kwargs.get("messages_before"), default=0),
            )
        if event == "Stop":
            return handle_stop(_as_optional_str(kwargs.get("active_mode")))
        if event == "SessionEnd":
            return handle_session_end(_as_str(kwargs.get("summary")))
        if event in supported_hook_events():
            return {"event": event, "status": "handled-noop", "payload": kwargs}
        return {"event": event, "status": "unsupported", "supported_events": supported_hook_events()}
