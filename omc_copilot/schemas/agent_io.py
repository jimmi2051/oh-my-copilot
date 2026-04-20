from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .task import TaskStep


@dataclass(slots=True)
class PlannerOutput:
    steps: List[TaskStep] = field(default_factory=list)


@dataclass(slots=True)
class ArchitectOutput:
    design_notes: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)


@dataclass(slots=True)
class ExecutorOutput:
    step_id: str
    result_text: str
    files_touched: List[str] = field(default_factory=list)


@dataclass(slots=True)
class ReviewerIssue:
    severity: str
    message: str


@dataclass(slots=True)
class ReviewerOutput:
    issues: List[ReviewerIssue] = field(default_factory=list)


@dataclass(slots=True)
class TesterOutput:
    passed: bool
    summary: str
    details: str = ""


@dataclass(slots=True)
class FixerOutput:
    patched_code: str
    rationale: str
