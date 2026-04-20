---
name: omc.session.search
description: Search persisted session history stored in `.omc/state/omc-copilot-history.jsonl`.
aliases: omc-session-search, session-search
---

Run:
`omc-copilot session search "<query>" --project-root <path>`

Behavior:
- Performs textual search over persisted JSONL history entries.
- Returns matching lines for quick runtime trace lookup.
