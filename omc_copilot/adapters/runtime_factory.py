from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from .codex_cli import CodexRuntimeAdapter
from .copilot_cli import CopilotRuntimeAdapter
from .runtime_base import RuntimeAdapter

RuntimeName = Literal["copilot", "codex"]
SetupRuntimeName = Literal["copilot", "codex", "both"]

DEFAULT_RUNTIME: RuntimeName = "copilot"
RUNTIME_ENV_VAR = "OMC_RUNTIME"


def resolve_runtime_name(
    runtime: str | None = None, *, allow_both: bool = False
) -> RuntimeName | SetupRuntimeName:
    raw = runtime or os.environ.get(RUNTIME_ENV_VAR) or DEFAULT_RUNTIME
    normalized = raw.strip().lower()
    allowed = {"copilot", "codex"}
    if allow_both:
        allowed.add("both")
    if normalized not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(
            f"Unsupported runtime `{raw}`. Expected one of: {choices}."
        )
    return normalized  # type: ignore[return-value]


def build_runtime_adapter(
    runtime: str | None = None, *, working_dir: Path | None = None
) -> RuntimeAdapter:
    runtime_name = resolve_runtime_name(runtime)
    if runtime_name == "codex":
        return CodexRuntimeAdapter(working_dir=working_dir)
    return CopilotRuntimeAdapter(working_dir=working_dir)


def includes_copilot(runtime: str) -> bool:
    return runtime in {"copilot", "both"}


def includes_codex(runtime: str) -> bool:
    return runtime in {"codex", "both"}
