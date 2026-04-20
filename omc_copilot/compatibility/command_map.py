from __future__ import annotations

OMC_TO_OMC_COPILOT_COMMANDS: dict[str, str] = {
    "omc setup": "omc-copilot setup",
    "omc ask": "omc-copilot ask",
    "omc team": "omc-copilot team",
    "omc session search": "omc-copilot session search",
    "omc doctor": "omc-copilot doctor",
    "omc hud": "omc-copilot hud",
    "omc run": "omc-copilot run",
}


def translate_command(command: str) -> str:
    for k, v in OMC_TO_OMC_COPILOT_COMMANDS.items():
        if command.startswith(k):
            return command.replace(k, v, 1)
    return command
