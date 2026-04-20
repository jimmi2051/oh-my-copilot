from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class ParityInventory:
    commands: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    pipelines: List[str] = field(default_factory=list)
