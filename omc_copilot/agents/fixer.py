from __future__ import annotations

from omc_copilot.schemas.agent_io import FixerOutput, ReviewerIssue

from .base import AgentContext


class FixerAgent:
    def run(self, context: AgentContext, execution_text: str, issues: list[ReviewerIssue]) -> FixerOutput:
        issue_lines = "\n".join(f"- ({issue.severity}) {issue.message}" for issue in issues) or "- No issues"
        prompt = (
            "Revise the implementation output to resolve the issues below.\n"
            f"Issues:\n{issue_lines}\n\n"
            f"Current output:\n{execution_text}\n\n"
            "Return an improved patched output."
        )
        patched = context.runtime.generate(prompt).text
        return FixerOutput(
            patched_code=patched,
            rationale="Patched output generated to address reviewer issues.",
        )
