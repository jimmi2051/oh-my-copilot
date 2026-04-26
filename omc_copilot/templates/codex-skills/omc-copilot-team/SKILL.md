---
name: omc.team
description: Use when the user requests OMC team-style multi-agent orchestration in Codex with review-first verification behavior.
---

# OMC Team

Run the team pipeline through Codex:

```bash
omc-copilot team "<task>" --runtime codex --cwd <path> --max-iterations <n>
```

Use the repository root for `--cwd` unless the user specifies another target. Preserve OMC stage behavior and report generated `.omc/` artifacts.
