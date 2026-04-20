from __future__ import annotations


def handle_subagent_stop(
    agent_name: str,
    outcome: str,
) -> dict[str, str]:
    return {
        "event": "SubagentStop",
        "agent_name": agent_name,
        "outcome": outcome,
        "status": "handled",
    }
