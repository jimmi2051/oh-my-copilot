# omc-copilot

`omc-copilot` is an OMC-style multi-agent orchestration system built on top of GitHub Copilot CLI.

It ships as both:
- a Python CLI (`omc-copilot ...`) for orchestration and setup
- a Copilot plugin package (`plugins/omc-copilot/`) with agents, skills, and hooks

---

## Plugin-first workflow (recommended)

1. Add a marketplace (or use a local checkout)
2. Install the `omc-copilot` plugin
3. Install the Python CLI binary
4. Run repository setup
5. Use `omc-copilot` commands for orchestration

```bash
# from this repository
copilot plugin marketplace add .
copilot plugin marketplace browse omc-copilot-marketplace
copilot plugin install omc-copilot@omc-copilot-marketplace

# plugin install does NOT install the `omc-copilot` shell binary
python -m pip install -e .

omc-copilot setup --target /path/to/repo --plugin-guidance
omc-copilot doctor --project-root .
```

`setup` validates `plugins/omc-copilot/plugin.json` before installing instruction assets.

If you only installed the plugin and see `zsh: command not found: omc-copilot`, install the Python package first (`python -m pip install -e .`) or invoke directly with `python -m omc_copilot.cli.main ...`.

---

## What gets installed in a target repo

`omc-copilot setup --target <path>` installs:
- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/omc.instructions.md`
- `.omc/hooks/omc-copilot-hooks.json`

The hook manifest declares supported lifecycle events for OMC-compatible plugin behavior.

---

## Architecture overview

### 1) Agents

- Runtime orchestration uses internal agent roles: planner, architect, executor, reviewer, tester, fixer.
- Plugin package also ships orchestrator agent specs under:
  - `plugins/omc-copilot/agents/autopilot-orchestrator.agent.md`
  - `plugins/omc-copilot/agents/team-orchestrator.agent.md`
  - `plugins/omc-copilot/agents/ralph-orchestrator.agent.md`
  - `plugins/omc-copilot/agents/ultrawork-orchestrator.agent.md`
  - `plugins/omc-copilot/agents/ultraqa-orchestrator.agent.md`

### 2) Skills

Plugin skills live under `plugins/omc-copilot/skills/*/SKILL.md` and define OMC-style entry points like:
- `omc.setup`, `omc.ask`, `omc.team`, `omc.session.search`, `omc.doctor`, `omc.hud`
- mode skills such as `omc.autopilot`, `omc.ralph`, `omc.ultrawork`, `omc.ultraqa`
- compatibility wrappers such as `omc.deep-interview`, `omc.ralplan`, `omc.skills.invoke`

### 3) Hooks

Plugin hooks are declared in `plugins/omc-copilot/hooks.json` and support:
- `UserPromptSubmit`, `SessionStart`, `PreToolUse`, `PermissionRequest`
- `PostToolUse`, `PostToolUseFailure`
- `SubagentStart`, `SubagentStop`
- `PreCompact`, `Stop`, `SessionEnd`

### 4) Pipelines / modes

Supported modes in `omc-copilot run --mode <name>`:
- `autopilot` (default)
- `team`
- `ralph`
- `ultrawork`
- `ultraqa`

Aliases:
- `deep-interview` → `autopilot`
- `ralplan` → `ralph`

### 5) State and artifacts

Runtime writes to:
- `.omc/state/omc-copilot/<task-id>.json` (task state snapshots)
- `.omc/state/omc-copilot-history.jsonl` (session history events)
- `.omc/artifacts/omc-copilot/<task-id>/result-<mode>.md` (final artifacts)

---

## CLI command reference

```bash
omc-copilot run "<task>" [--mode MODE] [--max-iterations N] [--cwd PATH]
omc-copilot setup [--target PATH] [--plugin-guidance]
omc-copilot ask "<prompt>" [--cwd PATH]
omc-copilot team "<task>" [--max-iterations N] [--cwd PATH]
omc-copilot session search "<query>" [--project-root PATH]
omc-copilot doctor [--project-root PATH]
omc-copilot hud [--project-root PATH]
omc-copilot parity-inventory --omc-root PATH
```

Quick examples:

```bash
omc-copilot run "build a REST API in FastAPI"
omc-copilot run "stabilize flaky tests" --mode ultraqa --cwd .
omc-copilot team "implement auth and tests"
omc-copilot ask "review this patch for security issues"
omc-copilot session search "auth" --project-root .
omc-copilot hud --project-root .
omc-copilot doctor --project-root .
```

`doctor` checks runtime and required assets, including:
- `plugins/omc-copilot/plugin.json`
- `.github/plugin/marketplace.json`
- plugin component paths declared in `plugin.json` (`agents`, `skills`, `hooks`)

Scope note:
- In the `omc-copilot` source repository, `doctor` validates local plugin package and marketplace files.
- In a consumer repository (for example, your app repo), `doctor` skips local plugin-package checks and verifies installed plugin presence via `copilot plugin list`.

---

## In-session methods and skill mapping

`omc_copilot/compatibility/session_method_map.json` is the source of truth for method routing.

Current status model:
- `implemented`: command/function path is wired end-to-end
- `partial`: route exists but dedicated compatibility surface is incomplete
- `planned`: metadata/spec exists but command surface is not wired yet

Examples:
- `omc.setup` → `omc-copilot setup`
- `omc.ask` → `omc-copilot ask`
- `omc.team` → `omc-copilot team`
- `omc.autopilot` / `omc.ralph` / `omc.ultrawork` / `omc.ultraqa` → `omc-copilot run --mode ...`
- `omc.skills.invoke` is documented for compatibility; dedicated session-level invocation command is not exposed yet

---

## Marketplace and plugin operations

### Add / list / browse marketplaces

```bash
copilot plugin marketplace add <owner/repo-or-local-path>
copilot plugin marketplace list
copilot plugin marketplace browse <marketplace-name>
copilot plugin marketplace update [marketplace-name]
copilot plugin marketplace remove <marketplace-name>
```

Examples:

```bash
copilot plugin marketplace add jimmi2051/oh-my-copilot
copilot plugin marketplace add .
copilot plugin marketplace list
copilot plugin marketplace browse omc-copilot-marketplace
```

### Install / list / update / uninstall plugins

```bash
copilot plugin install ./plugins/omc-copilot
copilot plugin install omc-copilot@omc-copilot-marketplace
copilot plugin list
copilot plugin update omc-copilot
copilot plugin uninstall omc-copilot
```

---

## Local development setup flow

```bash
cd omc-copilot
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -p "test_*.py"
```

Then validate the plugin-first path:

```bash
copilot plugin install ./plugins/omc-copilot
omc-copilot setup --target .
omc-copilot doctor --project-root .
```

---

## License

This project is licensed under the MIT License. See `LICENSE` for the full text.

## Copyright

Copyright (c) 2025 OMC-Copilot contributors.

## Attribution / Inspiration

Inspired by: oh-my-claudecode by Yeachan Heo. The power of multi-agent orchestration, now for GitHub Copilot.
