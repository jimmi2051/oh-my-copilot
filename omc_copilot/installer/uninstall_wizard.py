from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from omc_copilot.adapters.runtime_factory import includes_codex, includes_copilot

from .codex_skill_installer import uninstall_codex_skills
from .merge_strategy import remove_managed_block_file


@dataclass(slots=True)
class UninstallResult:
    target_root: Path
    removed_files: list[Path] = field(default_factory=list)
    updated_files: list[Path] = field(default_factory=list)
    removed_codex_skill_dirs: list[Path] = field(default_factory=list)


class UninstallWizard:
    def run(
        self,
        target_root: Path,
        runtime_name: str = "copilot",
        codex_skills_dir: Path | None = None,
    ) -> UninstallResult:
        removed_files: list[Path] = []
        updated_files: list[Path] = []

        agents_file = target_root / "AGENTS.md"
        if remove_managed_block_file(agents_file):
            if agents_file.exists():
                updated_files.append(agents_file)
            else:
                removed_files.append(agents_file)

        hook_manifest = target_root / ".omc" / "hooks" / "omc-copilot-hooks.json"
        if hook_manifest.exists():
            hook_manifest.unlink()
            removed_files.append(hook_manifest)

        if includes_copilot(runtime_name):
            for path in (
                target_root / ".github" / "copilot-instructions.md",
                target_root / ".github" / "instructions" / "omc.instructions.md",
            ):
                if path.exists():
                    path.unlink()
                    removed_files.append(path)

        removed_codex_skill_dirs: list[Path] = []
        if includes_codex(runtime_name):
            removed_codex_skill_dirs = uninstall_codex_skills(codex_skills_dir)

        return UninstallResult(
            target_root=target_root,
            removed_files=removed_files,
            updated_files=updated_files,
            removed_codex_skill_dirs=removed_codex_skill_dirs,
        )
