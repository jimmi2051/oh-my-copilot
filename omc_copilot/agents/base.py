from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from omc_copilot.adapters.runtime_base import RuntimeAdapter


@dataclass(slots=True)
class AgentContext:
    task_prompt: str
    project_root: Path
    runtime: RuntimeAdapter
    metadata: dict[str, Any] = field(default_factory=dict)
