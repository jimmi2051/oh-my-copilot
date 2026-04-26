---
name: omc.ask
description: Use when the user wants a direct single-shot OMC prompt answered through the Codex runtime without running a full orchestration loop.
---

# OMC Ask

Use the Codex runtime backend:

```bash
omc-copilot ask "<prompt>" --runtime codex --cwd <path>
```

If the user has already set `OMC_RUNTIME=codex`, the `--runtime codex` flag is optional. Return the command output directly and mention any command failure reason.
