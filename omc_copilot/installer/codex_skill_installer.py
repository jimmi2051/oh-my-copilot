from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

CODEX_HOME_ENV_VAR = "CODEX_HOME"
CODEX_SKILLS_TEMPLATE_DIR = Path("templates") / "codex-skills"


@dataclass(slots=True)
class CodexSkillInstallResult:
    skills_root: Path
    skill_dirs: list[Path]


def default_codex_skills_dir() -> Path:
    codex_home = os.environ.get(CODEX_HOME_ENV_VAR)
    if codex_home:
        return Path(codex_home).expanduser() / "skills"
    return Path.home() / ".codex" / "skills"


class CodexSkillInstaller:
    def __init__(self, package_root: Path) -> None:
        self.templates_root = package_root / CODEX_SKILLS_TEMPLATE_DIR

    def install(self, skills_root: Path | None = None) -> CodexSkillInstallResult:
        resolved_root = (skills_root or default_codex_skills_dir()).expanduser()
        if not self.templates_root.exists():
            raise RuntimeError(
                f"Codex skill templates not found: {self.templates_root}"
            )

        installed: list[Path] = []
        resolved_root.mkdir(parents=True, exist_ok=True)
        for template_dir in sorted(self.templates_root.iterdir()):
            if not template_dir.is_dir():
                continue
            target_dir = resolved_root / template_dir.name
            if target_dir.exists():
                if target_dir.is_dir() and not target_dir.is_symlink():
                    shutil.rmtree(target_dir)
                else:
                    target_dir.unlink()
            shutil.copytree(template_dir, target_dir)
            installed.append(target_dir)

        return CodexSkillInstallResult(
            skills_root=resolved_root,
            skill_dirs=installed,
        )


def expected_codex_skill_dirs(skills_root: Path | None = None) -> list[Path]:
    resolved_root = (skills_root or default_codex_skills_dir()).expanduser()
    templates_root = Path(__file__).resolve().parents[1] / CODEX_SKILLS_TEMPLATE_DIR
    if not templates_root.exists():
        return []
    return [
        resolved_root / template_dir.name
        for template_dir in sorted(templates_root.iterdir())
        if template_dir.is_dir()
    ]
