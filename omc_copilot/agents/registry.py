from __future__ import annotations

from dataclasses import dataclass

from .architect import ArchitectAgent
from .executor import ExecutorAgent
from .fixer import FixerAgent
from .planner import PlannerAgent
from .reviewer import ReviewerAgent
from .tester import TesterAgent


@dataclass(slots=True)
class AgentRegistry:
    planner: PlannerAgent
    architect: ArchitectAgent
    executor: ExecutorAgent
    reviewer: ReviewerAgent
    tester: TesterAgent
    fixer: FixerAgent


def build_default_registry() -> AgentRegistry:
    return AgentRegistry(
        planner=PlannerAgent(),
        architect=ArchitectAgent(),
        executor=ExecutorAgent(),
        reviewer=ReviewerAgent(),
        tester=TesterAgent(),
        fixer=FixerAgent(),
    )
