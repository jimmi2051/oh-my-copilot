from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor

from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import AgentRegistry
from omc_copilot.schemas.agent_io import ReviewerIssue
from omc_copilot.schemas.state import IterationRecord, TaskState, TaskStatus
from omc_copilot.schemas.task import TaskStep


def run_ultrawork_loop(context: AgentContext, registry: AgentRegistry, max_iterations: int) -> TaskState:
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    task_id = context.metadata["task_id"]
    plan = registry.planner.run(context)
    architecture = registry.architect.run(context)

    state = TaskState(
        task_id=task_id,
        prompt=context.task_prompt,
        status=TaskStatus.ACTIVE,
        mode="ultrawork",
        iteration=0,
        max_iterations=max_iterations,
        steps=plan.steps
        or [
            TaskStep(
                id="step-1",
                title=context.task_prompt[:80] or "implement-task",
                description=context.task_prompt,
            )
        ],
    )

    latest_output = ""
    for iteration in range(1, max_iterations + 1):
        state.iteration = iteration
        execution_issues: list[ReviewerIssue] = []
        with ThreadPoolExecutor(max_workers=max(1, len(state.steps))) as pool:
            future_map: dict[Future, str] = {
                pool.submit(registry.executor.run, context, step, architecture.constraints): step.id
                for step in state.steps
            }
            outputs = []
            for future, step_id in future_map.items():
                try:
                    outputs.append(future.result())
                except Exception as exc:
                    execution_issues.append(
                        ReviewerIssue(severity="high", message=f"Step {step_id} failed during execution: {exc}")
                    )
        latest_output = "\n\n".join(f"[{out.step_id}] {out.result_text}" for out in outputs)

        review = registry.reviewer.run(context, latest_output)
        combined_issues = [*execution_issues, *review.issues]
        test = registry.tester.run(context)
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
                phase="parallel-review-test",
                summary=f"issues={len(combined_issues)} tests={'pass' if test.passed else 'fail'}",
                issues=combined_issues,
            )
        )

        if not combined_issues and test.passed:
            state.status = TaskStatus.COMPLETE
            state.final_result = latest_output
            return state

        fixed = registry.fixer.run(context, latest_output, combined_issues)
        latest_output = fixed.patched_code
        state.history.append(
            IterationRecord(
                index=iteration,
                phase="parallel-fix",
                summary=fixed.rationale,
                issues=combined_issues,
            )
        )

    state.status = TaskStatus.FAILED
    state.final_result = latest_output
    return state
