from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PipelineSpec:
    name: str
    stages: tuple[str, ...]
    default_max_iterations: int
    verify_retries: int = 1
    requires_clean_review_before_tests: bool = False
    parallel_execution: bool = False


PIPELINES: dict[str, list[str]] = {
    "autopilot": ["plan", "execute", "review", "test", "fix"],
    "team": ["team-plan", "team-prd", "team-exec", "team-verify", "team-fix"],
    "ralph": ["execute", "verify", "repeat"],
    "ultrawork": ["plan", "parallel-execute", "review", "fix"],
    "ultraqa": ["test", "analyze-failures", "fix", "retest"],
}

PIPELINE_ALIASES: dict[str, str] = {
    "deep-interview": "autopilot",
    "ralplan": "ralph",
}

PIPELINE_SPECS: dict[str, PipelineSpec] = {
    "autopilot": PipelineSpec(
        name="autopilot",
        stages=tuple(PIPELINES["autopilot"]),
        default_max_iterations=8,
    ),
    "team": PipelineSpec(
        name="team",
        stages=tuple(PIPELINES["team"]),
        default_max_iterations=10,
        verify_retries=2,
        requires_clean_review_before_tests=True,
    ),
    "ralph": PipelineSpec(
        name="ralph",
        stages=tuple(PIPELINES["ralph"]),
        default_max_iterations=12,
        verify_retries=2,
    ),
    "ultrawork": PipelineSpec(
        name="ultrawork",
        stages=tuple(PIPELINES["ultrawork"]),
        default_max_iterations=8,
        parallel_execution=True,
    ),
    "ultraqa": PipelineSpec(
        name="ultraqa",
        stages=tuple(PIPELINES["ultraqa"]),
        default_max_iterations=8,
        verify_retries=2,
    ),
}


def get_pipeline(name: str) -> list[str]:
    normalized = normalize_pipeline_name(name)
    return PIPELINES[normalized]


def normalize_pipeline_name(name: str | None) -> str:
    if not name:
        return "autopilot"
    if name in PIPELINES:
        return name
    if name in PIPELINE_ALIASES:
        return PIPELINE_ALIASES[name]
    return "autopilot"


def get_pipeline_spec(name: str | None) -> PipelineSpec:
    normalized = normalize_pipeline_name(name)
    return PIPELINE_SPECS[normalized]
