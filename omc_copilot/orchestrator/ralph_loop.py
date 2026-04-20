from __future__ import annotations

from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import AgentRegistry
from omc_copilot.schemas.agent_io import ReviewerIssue
from omc_copilot.schemas.state import IterationRecord, TaskState, TaskStatus
from omc_copilot.schemas.task import TaskStep


def run_ralph_loop(
    context: AgentContext,
    registry: AgentRegistry,
    max_iterations: int,
    max_verify_retries: int = 2,
) -> TaskState:
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")
    if max_verify_retries < 1:
        raise ValueError("max_verify_retries must be >= 1")

    task_id = context.metadata["task_id"]
    plan = registry.planner.run(context)
    architecture = registry.architect.run(context)
    state = TaskState(
        task_id=task_id,
        prompt=context.task_prompt,
        status=TaskStatus.ACTIVE,
        mode="ralph",
        iteration=0,
        max_iterations=max_iterations,
    )
    state.steps = plan.steps or [
        TaskStep(
            id="step-1",
            title=context.task_prompt[:80] or "implement-task",
            description=context.task_prompt,
        )
    ]

    latest_output = ""
    for iteration in range(1, max_iterations + 1):
        state.iteration = iteration
        executed = []
        for step in state.steps:
            out = registry.executor.run(context, step, architecture.constraints)
            executed.append(f"[{step.id}] {out.result_text}")
        latest_output = "\n\n".join(executed)

        for retry in range(1, max_verify_retries + 1):
            test = registry.tester.run(context)
            review = registry.reviewer.run(context, latest_output)
            combined_issues = list(review.issues)
            if not test.passed:
                combined_issues.append(
                    ReviewerIssue(
                        severity="high",
                        message=f"Tests failed: {test.summary}. {test.details[:250]}".strip(),
                    )
                )

            state.history.append(
                IterationRecord(
                    index=iteration,
                    phase="ralph-verify",
                    summary=f"retry={retry}/{max_verify_retries} tests={'pass' if test.passed else 'fail'} issues={len(combined_issues)}",
                    issues=combined_issues,
                )
            )

            if not combined_issues:
                state.status = TaskStatus.COMPLETE
                state.final_result = latest_output
                return state

            if retry < max_verify_retries:
                patched = registry.fixer.run(context, latest_output, combined_issues)
                latest_output = patched.patched_code
                state.history.append(
                    IterationRecord(
                        index=iteration,
                        phase="ralph-retry-fix",
                        summary=patched.rationale,
                        issues=combined_issues,
                    )
                )

    state.status = TaskStatus.FAILED
    state.final_result = latest_output
    return state
