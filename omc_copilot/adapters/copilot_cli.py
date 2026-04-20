from __future__ import annotations

from pathlib import Path
from typing import Optional

from omc_copilot.execution.copilot_wrapper import CopilotWrapper

from .runtime_base import RuntimeAdapter, RuntimeReply


class CopilotRuntimeAdapter(RuntimeAdapter):
    def __init__(self, working_dir: Optional[Path] = None) -> None:
        self.wrapper = CopilotWrapper(working_dir=working_dir)

    def generate(self, prompt: str) -> RuntimeReply:
        out = self.wrapper.run_copilot(prompt)
        return RuntimeReply(prompt=prompt, text=out.output)
