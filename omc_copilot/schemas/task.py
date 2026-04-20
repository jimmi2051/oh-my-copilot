from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class TaskRequest:
    prompt: str
    mode: str = "autopilot"
    max_iterations: int = 8


@dataclass(slots=True)
class TaskStep:
    id: str
    title: str
    description: str


@dataclass(slots=True)
class TaskPlan:
    steps: List[TaskStep] = field(default_factory=list)
