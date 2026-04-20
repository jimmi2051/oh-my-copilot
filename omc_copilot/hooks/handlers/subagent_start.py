from __future__ import annotations


def handle_subagent_start(
    agent_name: str,
    task_id: str | None,
) -> dict[str, str | None]:
    return {
        "event": "SubagentStart",
        "agent_name": agent_name,
        "task_id": task_id,
        "status": "handled",
    }
