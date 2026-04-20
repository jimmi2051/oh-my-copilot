from __future__ import annotations

from omc_copilot.schemas.agent_io import ReviewerIssue, ReviewerOutput

from .base import AgentContext


class ReviewerAgent:
    def run(self, _context: AgentContext, execution_text: str) -> ReviewerOutput:
        issues: list[ReviewerIssue] = []
        lowered = execution_text.lower()
        if "todo" in lowered or "placeholder" in lowered:
            issues.append(
                ReviewerIssue(
                    severity="high", message="Output contains placeholder/TODO content"
                )
            )
        if len(execution_text.strip()) < 40:
            issues.append(
                ReviewerIssue(
                    severity="medium",
                    message="Execution output is too short to be actionable",
                )
            )
        if "error" in lowered and "fix" not in lowered:
            issues.append(
                ReviewerIssue(
                    severity="medium",
                    message="Execution mentions error without remediation",
                )
            )
        return ReviewerOutput(issues=issues)
