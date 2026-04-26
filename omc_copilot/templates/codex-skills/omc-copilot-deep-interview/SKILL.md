---
name: omc.deep-interview
description: Use when the user requests OMC deep-interview compatibility behavior in Codex; this currently maps to autopilot.
---

# OMC Deep Interview

Run the compatibility route through Codex:

```bash
omc-copilot run "<task>" --mode deep-interview --runtime codex --cwd <path>
```

Mention that current compatibility maps this mode to autopilot semantics if relevant.
