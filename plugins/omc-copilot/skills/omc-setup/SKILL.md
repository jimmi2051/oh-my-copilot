---
name: omc.setup
description: Install OMC-compatible instructions and hook manifest into a target repository for Copilot, Codex, or both runtimes.
aliases: omc-setup, setup
---

Run:
`omc-copilot setup --target <path> [--runtime copilot|codex|both]`

Behavior:
- Installs `AGENTS.md` for all runtimes.
- Installs Copilot `.github` instruction assets for `copilot` and `both`.
- Installs Codex-native OMC skills for `codex` and `both`.
- Installs `.omc/hooks/omc-copilot-hooks.json` with supported event names.
