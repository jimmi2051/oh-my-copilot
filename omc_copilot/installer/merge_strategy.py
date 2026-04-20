from __future__ import annotations

from pathlib import Path

START_MARKER = "<!-- omc-copilot:start -->"
END_MARKER = "<!-- omc-copilot:end -->"


def merge_block(existing: str, new_block: str) -> str:
    if START_MARKER in existing and END_MARKER in existing:
        head, rest = existing.split(START_MARKER, 1)
        _, tail = rest.split(END_MARKER, 1)
        return f"{head}{START_MARKER}\n{new_block}\n{END_MARKER}{tail}"
    if existing.strip():
        return f"{existing.rstrip()}\n\n{START_MARKER}\n{new_block}\n{END_MARKER}\n"
    return f"{START_MARKER}\n{new_block}\n{END_MARKER}\n"


def merge_file(path: Path, block: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    merged = merge_block(current, block)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(merged, encoding="utf-8")
