from __future__ import annotations

import json
from pathlib import Path


def run_session_search(query: str, project_root: Path) -> int:
    history_file = project_root / ".omc" / "state" / "omc-copilot-history.jsonl"
    if not history_file.exists():
        print("No session history found.")
        return 1

    query_l = query.lower()
    matched = 0
    for line in history_file.read_text(encoding="utf-8").splitlines():
        if query_l in line.lower():
            print(json.dumps(json.loads(line), indent=2))
            matched += 1
    if matched == 0:
        print("No matching events found.")
        return 1
    return 0
