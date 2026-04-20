from __future__ import annotations

from omc_copilot.schemas.agent_io import ArchitectOutput

from .base import AgentContext


class ArchitectAgent:
    def run(self, context: AgentContext) -> ArchitectOutput:
        notes = [
            "Preserve modular boundaries between orchestrator, agents, execution, state, and CLI.",
            "Prefer deterministic state transitions and explicit error surfaces.",
            "Keep generated artifacts under .omc/ for compatibility.",
        ]
        constraints = [
            "Use Copilot CLI only for generation/explanation calls.",
            "Persist iteration history for replay and debugging.",
            "Bound retries to avoid unending loops.",
        ]
        if "api" in context.task_prompt.lower():
            notes.append("Prioritize API contract clarity and testability.")
        return ArchitectOutput(design_notes=notes, constraints=constraints)
