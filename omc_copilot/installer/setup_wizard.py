from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .hook_installer import HookInstaller
from .instruction_installer import InstructionInstaller


@dataclass(slots=True)
class SetupResult:
    target_root: Path
    instruction_files: list[Path]
    hook_manifest: Path


class SetupWizard:
    def __init__(self, package_root: Path) -> None:
        self.instructions = InstructionInstaller(package_root=package_root)
        self.hooks = HookInstaller()

    def run(self, target_root: Path) -> SetupResult:
        target_root.mkdir(parents=True, exist_ok=True)
        instruction_files = self.instructions.install(target_root)
        hook_manifest = self.hooks.install_manifest(target_root)
        return SetupResult(target_root=target_root, instruction_files=instruction_files, hook_manifest=hook_manifest)
