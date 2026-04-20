---
name: omc.autopilot
description: Run default autopilot orchestration mode.
aliases: omc-autopilot, autopilot
---

Run:
`omc-copilot run "<task>" --mode autopilot --cwd <path>`

Behavior:
- Executes plan -> execute -> review -> test -> fix loop.
- Stores artifacts under `.omc/artifacts/`.
