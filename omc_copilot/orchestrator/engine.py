from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from omc_copilot.adapters.copilot_cli import CopilotRuntimeAdapter
from omc_copilot.agents.base import AgentContext
from omc_copilot.agents.registry import build_default_registry
from omc_copilot.compatibility.keyword_router import detect_mode
from omc_copilot.compatibility.pipeline_registry import get_pipeline_spec
from omc_copilot.orchestrator.autopilot_loop import run_autopilot_loop
from omc_copilot.orchestrator.ralph_loop import run_ralph_loop
from omc_copilot.orchestrator.team_pipeline import run_team_pipeline
from omc_copilot.orchestrator.ultraqa_loop import run_ultraqa_loop
from omc_copilot.orchestrator.ultrawork_loop import run_ultrawork_loop
from omc_copilot.schemas.state import TaskState
from omc_copilot.state.artifact_store import ArtifactStore
from omc_copilot.state.history_store import HistoryStore
from omc_copilot.state.state_manager import StateManager
from omc_copilot.utils.logging import get_logger

from .lifecycle import now_iso, task_id_from_prompt


class OrchestratorEngine:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.logger = get_logger("omc_copilot.orchestrator")
        self.runtime = CopilotRuntimeAdapter(working_dir=project_root)
        self.registry = build_default_registry()
        self.state_manager = StateManager(project_root)
        self.artifacts = ArtifactStore(project_root)
        self.history = HistoryStore(project_root)

    def run(self, prompt: str, mode: str | None = None, max_iterations: int | None = None) -> TaskState:
        requested_mode = mode or detect_mode(prompt)
        pipeline_spec = get_pipeline_spec(requested_mode)
        resolved_mode = pipeline_spec.name
        effective_iterations = max_iterations if max_iterations is not None else pipeline_spec.default_max_iterations
        task_id = task_id_from_prompt(prompt)
        context = AgentContext(
            task_prompt=prompt,
            project_root=self.project_root,
            runtime=self.runtime,
            metadata={"task_id": task_id},
        )

        self.history.append(
            {"ts": now_iso(), "event": "task_started", "task_id": task_id, "mode": resolved_mode, "prompt": prompt}
        )

        if resolved_mode == "team":
            state = run_team_pipeline(context, self.registry, max_iterations=effective_iterations)
        elif resolved_mode == "ralph":
            state = run_ralph_loop(context, self.registry, max_iterations=effective_iterations)
        elif resolved_mode == "ultrawork":
            state = run_ultrawork_loop(context, self.registry, max_iterations=effective_iterations)
        elif resolved_mode == "ultraqa":
            state = run_ultraqa_loop(context, self.registry, max_iterations=effective_iterations)
        else:
            state = run_autopilot_loop(context, self.registry, max_iterations=effective_iterations)

        self.state_manager.save(state)
        artifact_name = f"result-{resolved_mode}.md"
        self.artifacts.write_text(state.task_id, artifact_name, state.final_result or "")
        self.history.append(
            {
                "ts": now_iso(),
                "event": "task_finished",
                "task_id": state.task_id,
                "status": state.status.value,
                "iterations": state.iteration,
            }
        )
        self.logger.info("Task %s completed with status %s", state.task_id, state.status.value)
        return state

    @staticmethod
    def state_to_dict(state: TaskState) -> dict:
        return asdict(state)
