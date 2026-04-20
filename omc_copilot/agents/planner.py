from __future__ import annotations

import re

from omc_copilot.schemas.agent_io import PlannerOutput
from omc_copilot.schemas.task import TaskStep

from .base import AgentContext


class PlannerAgent:
    def run(self, context: AgentContext) -> PlannerOutput:
        task = context.task_prompt.strip()
        parts: list[str] = []
        numbered = re.findall(r"\d+[.)]\s+([^\n]+)", task)
        if numbered:
            parts = [p.strip() for p in numbered if p.strip()]
        elif " and " in task.lower():
            parts = [
                p.strip()
                for p in re.split(r"\s+and\s+", task, flags=re.IGNORECASE)
                if p.strip()
            ]
        else:
            parts = [task]

        steps = [
            TaskStep(id=f"step-{idx+1}", title=part[:80], description=part)
            for idx, part in enumerate(parts)
        ]
        return PlannerOutput(steps=steps)
