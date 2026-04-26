---
name: omc.doctor
description: Use when the user wants to validate OMC installation health for Codex, Copilot, or both runtimes.
---

# OMC Doctor

For Codex health checks, run:

```bash
omc-copilot doctor --runtime codex --project-root <path>
```

Use `--runtime both` to check Codex skills and Copilot plugin assets together. Report any `MISSING` or `INVALID` lines with exact paths.
