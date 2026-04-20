from __future__ import annotations

from omc_copilot.schemas.agent_io import ExecutorOutput
from omc_copilot.schemas.task import TaskStep

from .base import AgentContext


class ExecutorAgent:
    def run(self, context: AgentContext, step: TaskStep, constraints: list[str]) -> ExecutorOutput:
        prompt = (
            "You are implementing one execution step.\n"
            f"Task: {context.task_prompt}\n"
            f"Step: {step.description}\n"
            "Constraints:\n"
            + "\n".join(f"- {item}" for item in constraints)
            + "\nReturn concrete implementation guidance and code edits."
        )
        reply = context.runtime.generate(prompt)
        return ExecutorOutput(step_id=step.id, result_text=reply.text, files_touched=[])
