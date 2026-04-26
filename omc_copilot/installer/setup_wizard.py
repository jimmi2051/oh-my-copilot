from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from omc_copilot.adapters.runtime_factory import includes_codex

from .codex_skill_installer import CodexSkillInstaller
from .hook_installer import HookInstaller
from .instruction_installer import InstructionInstaller


@dataclass(slots=True)
class SetupResult:
    target_root: Path
    instruction_files: list[Path]
    hook_manifest: Path
    codex_skill_dirs: list[Path] = field(default_factory=list)


class SetupWizard:
    def __init__(self, package_root: Path) -> None:
        self.instructions = InstructionInstaller(package_root=package_root)
        self.hooks = HookInstaller()
        self.codex_skills = CodexSkillInstaller(package_root=package_root)

    def run(
        self,
        target_root: Path,
        runtime_name: str = "copilot",
        codex_skills_dir: Path | None = None,
    ) -> SetupResult:
        target_root.mkdir(parents=True, exist_ok=True)
        instruction_files = self.instructions.install(target_root, runtime_name)
        hook_manifest = self.hooks.install_manifest(target_root)
        codex_skill_dirs: list[Path] = []
        if includes_codex(runtime_name):
            codex_skill_dirs = self.codex_skills.install(
                skills_root=codex_skills_dir
            ).skill_dirs
        return SetupResult(
            target_root=target_root,
            instruction_files=instruction_files,
            hook_manifest=hook_manifest,
            codex_skill_dirs=codex_skill_dirs,
        )
