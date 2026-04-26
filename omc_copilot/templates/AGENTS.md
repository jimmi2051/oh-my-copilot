# oh-my-copilot Agent Profile

You are operating in oh-my-copilot compatibility mode.

Core rules:
1. Execute every implementation task through staged orchestration: plan -> execute -> review -> test -> fix.
2. Keep task state, notes, and generated artifacts under `.omc/`.
3. Produce deterministic outputs with explicit commands, paths, and failure reasons.
4. Preserve the intent of OMC compatibility commands and workflows.

Stage contract:
- Plan: identify the requested outcome, affected files, validation strategy, and expected artifact paths.
- Execute: make the smallest coherent changes that satisfy the requested outcome.
- Review: inspect the diff for regressions, drift from OMC compatibility, and accidental unrelated edits.
- Test: run the narrowest reliable validation first, then broader tests when the change affects shared behavior.
- Fix: address any review or test failures and record unresolved blockers explicitly.

State and artifact conventions:
- Runtime state belongs in `.omc/state/`.
- Final task artifacts belong in `.omc/artifacts/`.
- Hook and integration metadata belongs in `.omc/hooks/`.
- Do not write OMC state outside `.omc/` unless a command explicitly requires a project file update.

Compatibility expectations:
- Keep setup/init behavior idempotent.
- Keep managed instruction blocks bounded by the `omc-copilot` start/end markers.
- Prefer additive updates that preserve user-authored content outside managed blocks.
- When a compatibility command cannot be completed, report the exact failed stage and reason.

Codex runtime usage:
- In Codex CLI sessions, invoke OMC workflows with `omc-copilot` commands from the project root.
- Use `omc-copilot setup --runtime codex --target .` to install or refresh this `AGENTS.md` block without requiring Copilot-specific `.github` instructions.
- The same setup command installs Codex-native OMC skills under `$CODEX_HOME/skills` or `~/.codex/skills`; start a new Codex session after setup to refresh skill discovery.
- Use `omc-copilot run "<task>" --runtime codex`, `omc-copilot team "<task>" --runtime codex`, or `omc-copilot ask "<prompt>" --runtime codex` to route model calls through `codex exec`.
- `OMC_RUNTIME=codex` may be used instead of repeating `--runtime codex`.
- Codex backend calls run non-interactively with read-only sandbox defaults; project changes should be made by the active outer Codex session.
