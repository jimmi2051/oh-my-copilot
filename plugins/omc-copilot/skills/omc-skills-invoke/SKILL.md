---
name: omc.skills.invoke
description: Compatibility wrapper for skill invocation until a dedicated CLI command is surfaced.
aliases: omc-skills-invoke, skills-invoke
---

Compatibility wrapper behavior:
1. Resolve the requested OMC method to one of the shipped day-one skills.
2. Execute the mapped `omc-copilot` command for that skill.
3. If no direct mapping exists, use `omc-copilot ask` with explicit fallback context.

Current status:
- Metadata loading is implemented in `omc_copilot.compatibility.skill_loader`.
- A dedicated session-level skill invocation command is not exposed yet.
