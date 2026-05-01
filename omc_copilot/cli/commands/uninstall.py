from __future__ import annotations

from pathlib import Path

from omc_copilot.adapters.runtime_factory import includes_codex, resolve_runtime_name
from omc_copilot.installer.uninstall_wizard import UninstallWizard


def run_uninstall(
    target: Path,
    runtime_name: str | None = None,
    codex_skills_dir: Path | None = None,
) -> int:
    resolved_runtime = resolve_runtime_name(runtime_name, allow_both=True)
    result = UninstallWizard().run(
        target_root=target,
        runtime_name=resolved_runtime,
        codex_skills_dir=codex_skills_dir,
    )

    print(f"Uninstall completed for {result.target_root}")
    print(f"- runtime: {resolved_runtime}")
    for path in result.updated_files:
        print(f"- updated: {path}")
    for path in result.removed_files:
        print(f"- removed: {path}")
    if includes_codex(resolved_runtime):
        for path in result.removed_codex_skill_dirs:
            print(f"- removed codex skill: {path}")
    return 0
