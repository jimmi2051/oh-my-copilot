from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

CODEX_HOME_ENV_VAR = "CODEX_HOME"
CODEX_SKILLS_TEMPLATE_DIR = Path("templates") / "codex-skills"
CODEX_ADAPTATION_MARKER = "<!-- omc-copilot:codex-adaptation -->"
CODEX_ADAPTATION_BLOCK = f"""{CODEX_ADAPTATION_MARKER}

## Codex Runtime Adaptation

This installed skill runs inside Codex. Treat Claude Code-specific examples in the
body as upstream OMC compatibility notes and translate them before acting:

- Use Codex tools, Codex skills, and `omc-copilot ... --runtime codex --cwd <path>`;
  do not invoke Claude-only `Skill(...)`, `Task(...)`, `WebSearch`, `WebFetch`, or
  `/oh-my-claudecode:...` syntax literally.
- When a body references `oh-my-claudecode:<skill>`, route to the corresponding
  installed Codex skill or to the equivalent `omc-copilot` command.
- Store project runtime state, specs, plans, and artifacts under `.omc/`.
- Use `${{CODEX_HOME:-~/.codex}}/skills` for Codex user-level skills. Mention
  `~/.claude` paths only when diagnosing or migrating a Claude Code installation.
- If a requested behavior has no Codex implementation yet, state the unsupported
  part explicitly and use the closest supported Codex compatibility path.
"""


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
            _adapt_skill_file_for_codex(target_dir / "SKILL.md")
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


def uninstall_codex_skills(skills_root: Path | None = None) -> list[Path]:
    removed: list[Path] = []
    for skill_dir in expected_codex_skill_dirs(skills_root):
        if not skill_dir.exists():
            continue
        if skill_dir.is_dir() and not skill_dir.is_symlink():
            shutil.rmtree(skill_dir)
        else:
            skill_dir.unlink()
        removed.append(skill_dir)
    return removed


def _adapt_skill_file_for_codex(skill_file: Path) -> None:
    if not skill_file.exists():
        return

    content = skill_file.read_text(encoding="utf-8")
    if CODEX_ADAPTATION_MARKER in content:
        return

    if not content.startswith("---\n"):
        skill_file.write_text(f"{CODEX_ADAPTATION_BLOCK}\n{content}", encoding="utf-8")
        return

    frontmatter_end = content.find("\n---\n", 4)
    if frontmatter_end == -1:
        skill_file.write_text(f"{CODEX_ADAPTATION_BLOCK}\n{content}", encoding="utf-8")
        return

    insert_at = frontmatter_end + len("\n---\n")
    adapted = (
        content[:insert_at] + "\n" + CODEX_ADAPTATION_BLOCK + "\n" + content[insert_at:]
    )
    skill_file.write_text(adapted, encoding="utf-8")
