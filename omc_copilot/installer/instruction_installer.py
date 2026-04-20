from __future__ import annotations

from pathlib import Path

from .merge_strategy import merge_file


class InstructionInstaller:
    def __init__(self, package_root: Path) -> None:
        self.templates_root = package_root / "templates"

    def install(self, target_root: Path) -> list[Path]:
        installed: list[Path] = []

        agents_template = (self.templates_root / "AGENTS.md").read_text(encoding="utf-8")
        agents_target = target_root / "AGENTS.md"
        merge_file(agents_target, agents_template)
        installed.append(agents_target)

        ci_template = (self.templates_root / "copilot-instructions.md").read_text(encoding="utf-8")
        ci_target = target_root / ".github" / "copilot-instructions.md"
        merge_file(ci_target, ci_template)
        installed.append(ci_target)

        path_template = (self.templates_root / "instructions" / "omc.instructions.md").read_text(encoding="utf-8")
        path_target = target_root / ".github" / "instructions" / "omc.instructions.md"
        path_target.parent.mkdir(parents=True, exist_ok=True)
        path_target.write_text(path_template, encoding="utf-8")
        installed.append(path_target)
        return installed
