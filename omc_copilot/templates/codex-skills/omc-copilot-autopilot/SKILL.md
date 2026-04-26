---
name: omc.autopilot
description: Use when the user wants the default OMC plan-execute-review-test-fix orchestration loop in Codex.
---

# OMC Autopilot

Run autopilot through Codex:

```bash
omc-copilot run "<task>" --mode autopilot --runtime codex --cwd <path>
```

Keep outputs deterministic, preserve `.omc/` state/artifact locations, and relay validation results.
