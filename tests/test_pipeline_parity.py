from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from omc_copilot.adapters.runtime_base import RuntimeReply
from omc_copilot.agents.base import AgentContext
from omc_copilot.compatibility.pipeline_registry import (
    PIPELINES,
    get_pipeline,
    get_pipeline_spec,
    normalize_pipeline_name,
)
from omc_copilot.orchestrator.autopilot_loop import run_autopilot_loop
from omc_copilot.orchestrator.ralph_loop import run_ralph_loop
from omc_copilot.orchestrator.team_pipeline import run_team_pipeline
from omc_copilot.orchestrator.ultrawork_loop import run_ultrawork_loop
from omc_copilot.schemas.agent_io import (
    ArchitectOutput,
    ExecutorOutput,
    FixerOutput,
    PlannerOutput,
    ReviewerIssue,
    ReviewerOutput,
    TesterOutput,
)
from omc_copilot.schemas.task import TaskStep


class _NoopRuntime:
    def generate(self, prompt: str) -> RuntimeReply:
        return RuntimeReply(prompt=prompt, text="ok")


class _Planner:
    def run(self, _context: AgentContext) -> PlannerOutput:
        return PlannerOutput(
            steps=[
                TaskStep(id="step-1", title="first", description="first"),
                TaskStep(id="step-2", title="second", description="second"),
            ]
        )


class _Architect:
    def run(self, _context: AgentContext) -> ArchitectOutput:
        return ArchitectOutput(design_notes=[], constraints=["safe"])


class _Executor:
    def __init__(self, fail_on_steps: set[str] | None = None) -> None:
        self.fail_on_steps = fail_on_steps or set()

    def run(
        self, _context: AgentContext, step: TaskStep, _constraints: list[str]
    ) -> ExecutorOutput:
        if step.id in self.fail_on_steps:
            raise RuntimeError(f"{step.id} exploded")
        return ExecutorOutput(
            step_id=step.id, result_text=f"done {step.id}", files_touched=[]
        )


class _Reviewer:
    def __init__(self, issues_per_call: list[list[ReviewerIssue]]) -> None:
        self.issues_per_call = issues_per_call
        self.calls = 0

    def run(self, _context: AgentContext, _execution_text: str) -> ReviewerOutput:
        idx = min(self.calls, len(self.issues_per_call) - 1)
        self.calls += 1
        return ReviewerOutput(issues=list(self.issues_per_call[idx]))


class _Tester:
    def __init__(self, passed_per_call: list[bool]) -> None:
        self.passed_per_call = passed_per_call
        self.calls = 0

    def run(self, _context: AgentContext) -> TesterOutput:
        idx = min(self.calls, len(self.passed_per_call) - 1)
        self.calls += 1
        passed = self.passed_per_call[idx]
        return TesterOutput(
            passed=passed, summary="passed" if passed else "failed", details="trace"
        )


class _Fixer:
    def __init__(self) -> None:
        self.calls = 0

    def run(
        self, _context: AgentContext, execution_text: str, _issues: list[ReviewerIssue]
    ) -> FixerOutput:
        self.calls += 1
        return FixerOutput(
            patched_code=f"[patched-{self.calls}] {execution_text}",
            rationale=f"fix-{self.calls}",
        )


class _Registry:
    def __init__(
        self,
        reviewer_issues: list[list[ReviewerIssue]],
        tester_results: list[bool],
        executor_failures: set[str] | None = None,
    ) -> None:
        self.planner = _Planner()
        self.architect = _Architect()
        self.executor = _Executor(executor_failures)
        self.reviewer = _Reviewer(reviewer_issues)
        self.tester = _Tester(tester_results)
        self.fixer = _Fixer()


def _context() -> AgentContext:
    root = Path(tempfile.gettempdir())
    return AgentContext(
        task_prompt="implement robust pipeline behavior",
        project_root=root,
        runtime=_NoopRuntime(),
        metadata={"task_id": "pipeline-test"},
    )


class PipelineParityTest(unittest.TestCase):
    def test_team_review_must_be_clean_before_tests(self) -> None:
        issue = ReviewerIssue(severity="high", message="placeholder")
        registry = _Registry(reviewer_issues=[[issue]], tester_results=[True])
        state = run_team_pipeline(_context(), registry, max_iterations=1)

        self.assertEqual(state.status.value, "failed")
        self.assertEqual(registry.tester.calls, 0)
        self.assertEqual(
            [h.phase for h in state.history], ["team-verify-review", "team-fix"]
        )

    def test_ralph_retries_verification_within_single_iteration(self) -> None:
        registry = _Registry(reviewer_issues=[[], []], tester_results=[False, True])
        state = run_ralph_loop(
            _context(), registry, max_iterations=1, max_verify_retries=2
        )

        self.assertEqual(state.status.value, "complete")
        self.assertEqual(state.iteration, 1)
        self.assertEqual(registry.tester.calls, 2)
        self.assertIn("ralph-retry-fix", [h.phase for h in state.history])

    def test_ultrawork_captures_parallel_execution_failures(self) -> None:
        registry = _Registry(
            reviewer_issues=[[]], tester_results=[True], executor_failures={"step-2"}
        )
        state = run_ultrawork_loop(_context(), registry, max_iterations=1)

        self.assertEqual(state.status.value, "failed")
        self.assertEqual(registry.fixer.calls, 1)
        self.assertTrue(
            any(
                "step-2 failed" in issue.message.lower()
                for issue in state.history[0].issues
            )
        )

    def test_pipeline_registry_normalizes_aliases(self) -> None:
        self.assertEqual(normalize_pipeline_name("ralplan"), "ralph")
        self.assertEqual(get_pipeline("deep-interview"), PIPELINES["autopilot"])
        self.assertTrue(get_pipeline_spec("team").requires_clean_review_before_tests)

    def test_autopilot_rejects_invalid_iteration_budget(self) -> None:
        registry = _Registry(reviewer_issues=[[]], tester_results=[True])
        with self.assertRaises(ValueError):
            run_autopilot_loop(_context(), registry, max_iterations=0)


if __name__ == "__main__":
    unittest.main()
