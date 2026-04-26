---
name: omc.setup
description: Use when the user wants to install or refresh oh-my-copilot OMC compatibility assets for Codex, Copilot, or both runtimes in a repository.
---

# OMC Setup

Run repository setup from the target project root or pass `--target`.

Use Codex runtime setup when the user is in Codex:

```bash
omc-copilot setup --runtime codex --target <path>
```

Use `--runtime both` when the repository should support both Codex skills and Copilot plugin instructions. Setup is idempotent and updates the managed `AGENTS.md` block plus `.omc/hooks/`.
