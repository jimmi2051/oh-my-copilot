---
name: omc.ask
description: Send a direct single-shot prompt through the selected Copilot or Codex runtime adapter.
aliases: omc-ask, ask
---

Run:
`omc-copilot ask "<prompt>" --cwd <path> [--runtime copilot|codex]`

Behavior:
- Uses direct prompt passthrough.
- Defaults to Copilot unless `--runtime` or `OMC_RUNTIME` selects Codex.
- Returns concise answer text without orchestration loop state.
