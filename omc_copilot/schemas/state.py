from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from .agent_io import ReviewerIssue
from .task import TaskStep


class TaskStatus(str, Enum):
    ACTIVE = "active"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass(slots=True)
class IterationRecord:
    index: int
    phase: str
    summary: str
    issues: List[ReviewerIssue] = field(default_factory=list)


@dataclass(slots=True)
class TaskState:
    task_id: str
    prompt: str
    status: TaskStatus
    mode: str
    iteration: int
    max_iterations: int
    steps: List[TaskStep] = field(default_factory=list)
    history: List[IterationRecord] = field(default_factory=list)
    final_result: Optional[str] = None
