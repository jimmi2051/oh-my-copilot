from __future__ import annotations

from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import AgentRegistry
from omc_copilot.schemas.agent_io import ReviewerIssue
from omc_copilot.schemas.state import IterationRecord, TaskState, TaskStatus
from omc_copilot.schemas.task import TaskStep


def run_team_pipeline(context: AgentContext, registry: AgentRegistry, max_iterations: int) -> TaskState:
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    task_id = context.metadata["task_id"]
    state = TaskState(
        task_id=task_id,
        prompt=context.task_prompt,
        status=TaskStatus.ACTIVE,
        mode="team",
        iteration=0,
        max_iterations=max_iterations,
    )
    plan = registry.planner.run(context)
    architecture = registry.architect.run(context)
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
        execution = []
        for step in state.steps:
            out = registry.executor.run(context, step, architecture.constraints)
            execution.append(f"[{step.id}] {out.result_text}")
        latest_output = "\n\n".join(execution)

        review = registry.reviewer.run(context, latest_output)
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="team-verify-review",
                summary=f"issues={len(review.issues)}",
                issues=review.issues,
            )
        )
        if review.issues:
            patched = registry.fixer.run(context, latest_output, review.issues)
            latest_output = patched.patched_code
            state.history.append(
                IterationRecord(
                    index=iteration,
                    phase="team-fix",
                    summary=patched.rationale,
                    issues=review.issues,
                )
            )
            continue

        test = registry.tester.run(context)
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="team-verify-test",
                summary=test.summary,
                issues=[],
            )
        )
        if test.passed:
            state.status = TaskStatus.COMPLETE
            state.final_result = latest_output
            return state

        test_issue = ReviewerIssue(severity="high", message=f"Tests failed: {test.summary}. {test.details[:250]}".strip())
        patched = registry.fixer.run(context, latest_output, [test_issue])
        latest_output = patched.patched_code
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="team-fix",
                summary=patched.rationale,
                issues=[test_issue],
            )
        )

    state.status = TaskStatus.FAILED
    state.final_result = latest_output
    return state
