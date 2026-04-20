from __future__ import annotations


def handle_user_prompt_submit(prompt: str) -> dict[str, str | int]:
    normalized_prompt = prompt.strip()
    return {
        "event": "UserPromptSubmit",
        "prompt": normalized_prompt,
        "prompt_length": len(normalized_prompt),
        "status": "handled",
    }
