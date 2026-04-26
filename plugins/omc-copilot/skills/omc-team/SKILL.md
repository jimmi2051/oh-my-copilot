---
name: omc.team
description: Execute team orchestration with review-first verification behavior.
aliases: omc-team, team
---

Run:
`omc-copilot team "<task>" --cwd <path> --max-iterations <n> [--runtime copilot|codex]`

Behavior:
- Uses dedicated team pipeline semantics.
- Defaults to Copilot unless `--runtime` or `OMC_RUNTIME` selects Codex.
- Requires clean review outcomes before test execution.
