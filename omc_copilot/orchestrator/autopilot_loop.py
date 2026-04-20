from __future__ import annotations

from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import AgentRegistry
from omc_copilot.schemas.agent_io import ReviewerIssue
from omc_copilot.schemas.state import IterationRecord, TaskState, TaskStatus
from omc_copilot.schemas.task import TaskStep


def run_autopilot_loop(
    context: AgentContext, registry: AgentRegistry, max_iterations: int
) -> TaskState:
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    task_id = context.metadata["task_id"]
    state = TaskState(
        task_id=task_id,
        prompt=context.task_prompt,
        status=TaskStatus.ACTIVE,
        mode="autopilot",
        iteration=0,
        max_iterations=max_iterations,
    )

    try:
        plan = registry.planner.run(context)
        architecture = registry.architect.run(context)
    except Exception as exc:  # pragma: no cover - defensive path
        state.status = TaskStatus.FAILED
        state.history.append(
            IterationRecord(
                index=0,
                phase="bootstrap",
                summary=f"Pipeline bootstrap failed: {exc}",
                issues=[],
            )
        )
        state.final_result = ""
        return state

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
        step_outputs: list[str] = []
        execution_issues: list[ReviewerIssue] = []
        try:
            for step in state.steps:
                exec_out = registry.executor.run(
                    context, step, architecture.constraints
                )
                step_outputs.append(f"[{step.id}] {exec_out.result_text}")
        except Exception as exc:
            execution_issues.append(
                ReviewerIssue(severity="high", message=f"Execution failed: {exc}")
            )
        latest_output = "\n\n".join(step_outputs)

        try:
            review = registry.reviewer.run(context, latest_output)
            review_issues = [*execution_issues, *review.issues]
        except Exception as exc:
            review_issues = [
                *execution_issues,
                ReviewerIssue(severity="high", message=f"Review failed: {exc}"),
            ]

        test_passed = False
        test_summary = "Tests unavailable"
        test_details = ""
        try:
            test = registry.tester.run(context)
            test_passed = test.passed
            test_summary = test.summary
            test_details = test.details
        except Exception as exc:
            test_summary = f"Tester failed: {exc}"

        summary = (
            f"issues={len(review_issues)} tests={'pass' if test_passed else 'fail'}"
        )
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="review-test",
                summary=f"{summary}; {test_summary}",
                issues=review_issues,
            )
        )

        if not review_issues and test_passed:
            state.status = TaskStatus.COMPLETE
            state.final_result = latest_output
            return state

        if not test_passed:
            review_issues.append(
                ReviewerIssue(
                    severity="high",
                    message=f"Tests failed: {test_summary}. {test_details[:250]}".strip(),
                )
            )
        try:
            fixed = registry.fixer.run(context, latest_output, review_issues)
        except Exception as exc:
            state.status = TaskStatus.FAILED
            state.history.append(
                IterationRecord(
                    index=iteration,
                    phase="fix",
                    summary=f"Fix step failed: {exc}",
                    issues=review_issues,
                )
            )
            state.final_result = latest_output
            return state
        latest_output = fixed.patched_code
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="fix",
                summary=fixed.rationale,
                issues=review_issues,
            )
        )

    state.status = TaskStatus.FAILED
    state.final_result = latest_output
    return state
