from __future__ import annotations

KEYWORD_TO_MODE: dict[str, str] = {
    "autopilot": "autopilot",
    "ralph": "ralph",
    "ultrawork": "ultrawork",
    "ultraqa": "ultraqa",
    "team": "team",
    "deep interview": "deep-interview",
    "ralplan": "ralplan",
}


def detect_mode(prompt: str, default: str = "autopilot") -> str:
    lowered = prompt.lower()
    for keyword, mode in KEYWORD_TO_MODE.items():
        if keyword in lowered:
            return mode
    return default
