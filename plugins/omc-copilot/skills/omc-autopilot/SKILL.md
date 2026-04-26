---
name: omc.autopilot
description: Run default autopilot orchestration mode.
aliases: omc-autopilot, autopilot
---

Run:
`omc-copilot run "<task>" --mode autopilot --cwd <path> [--runtime copilot|codex]`

Behavior:
- Executes plan -> execute -> review -> test -> fix loop.
- Defaults to Copilot unless `--runtime` or `OMC_RUNTIME` selects Codex.
- Stores artifacts under `.omc/artifacts/`.
