from __future__ import annotations

from pathlib import Path

from omc_copilot.schemas.parity import ParityInventory

from .hook_registry import supported_hook_events
from .pipeline_registry import PIPELINES
from .skill_loader import list_skill_names


def _extract_commands_from_cli_index(cli_index: Path) -> list[str]:
    commands: list[str] = []
    if not cli_index.exists():
        return commands
    for line in cli_index.read_text(encoding="utf-8").splitlines():
        if ".command(" not in line:
            continue
        quote = "'" if "'" in line else '"'
        parts = line.split(quote)
        if len(parts) >= 2:
            command = parts[1].split()[0]
            if command:
                commands.append(command)
    return sorted(set(commands))


def _extract_agents_from_reference(reference_md: Path) -> list[str]:
    if not reference_md.exists():
        return []
    agents: list[str] = []
    table_started = False
    for line in reference_md.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| Domain"):
            table_started = True
            continue
        if table_started and line.strip().startswith("---"):
            continue
        if table_started and line.startswith("---"):
            break
        if table_started and line.startswith("|"):
            for chunk in line.split("`"):
                if chunk and "-" in chunk and " " not in chunk:
                    if chunk not in {"Domain", "LOW", "MEDIUM", "HIGH"}:
                        agents.append(chunk)
    return sorted(set(agents))


def generate_parity_inventory(omc_root: Path) -> ParityInventory:
    commands = _extract_commands_from_cli_index(omc_root / "src" / "cli" / "index.ts")
    skills = list_skill_names(omc_root / "skills")
    agents = _extract_agents_from_reference(omc_root / "docs" / "REFERENCE.md")
    return ParityInventory(
        commands=commands,
        agents=agents,
        skills=skills,
        hooks=supported_hook_events(),
        pipelines=sorted(PIPELINES.keys()),
    )
