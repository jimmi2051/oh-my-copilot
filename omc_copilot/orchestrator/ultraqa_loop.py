from __future__ import annotations

from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import AgentRegistry
from omc_copilot.schemas.agent_io import ReviewerIssue
from omc_copilot.schemas.state import IterationRecord, TaskState, TaskStatus


def run_ultraqa_loop(
    context: AgentContext, registry: AgentRegistry, max_iterations: int
) -> TaskState:
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    task_id = context.metadata["task_id"]
    state = TaskState(
        task_id=task_id,
        prompt=context.task_prompt,
        status=TaskStatus.ACTIVE,
        mode="ultraqa",
        iteration=0,
        max_iterations=max_iterations,
        steps=[],
    )
    synthetic_output = context.task_prompt

    for iteration in range(1, max_iterations + 1):
        state.iteration = iteration
        test = registry.tester.run(context)
        issues = list(registry.reviewer.run(context, synthetic_output).issues)
        if not test.passed:
            issues.append(
                ReviewerIssue(
                    severity="high",
                    message=f"Tests failed: {test.summary}. {test.details[:250]}".strip(),
                )
            )
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="qa-cycle",
                summary=f"tests={'pass' if test.passed else 'fail'} issues={len(issues)}",
                issues=issues,
            )
        )
        if test.passed and not issues:
            state.status = TaskStatus.COMPLETE
            state.final_result = synthetic_output
            return state

        fixed = registry.fixer.run(context, synthetic_output, issues)
        synthetic_output = fixed.patched_code
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="qa-fix",
                summary=fixed.rationale,
                issues=issues,
            )
        )

    state.status = TaskStatus.FAILED
    state.final_result = synthetic_output
    return state
