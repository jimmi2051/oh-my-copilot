from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class RuntimeReply:
    prompt: str
    text: str


class RuntimeAdapter(Protocol):
    def generate(self, prompt: str) -> RuntimeReply:
        ...
