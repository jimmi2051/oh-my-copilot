from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional


@dataclass(slots=True)
class SkillMetadata:
    name: str
    path: Path
    description: str = ""
    aliases: list[str] = field(default_factory=list)


def _extract_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + len(marker) :]
    result: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip().strip("'\"")
    return result, body


def _extract_first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip("# ").strip()
        if clean:
            return clean
    return ""


def load_skills(skills_root: Path) -> list[SkillMetadata]:
    found: list[SkillMetadata] = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        name = skill_file.parent.name
        text = skill_file.read_text(encoding="utf-8")
        frontmatter, body = _extract_frontmatter(text)
        description = frontmatter.get("description") or _extract_first_nonempty_line(
            body
        )
        aliases = [
            alias.strip()
            for alias in frontmatter.get("aliases", "").split(",")
            if alias.strip()
        ]
        found.append(
            SkillMetadata(
                name=name, path=skill_file, description=description, aliases=aliases
            )
        )
    return found


def list_skill_names(skills_root: Path) -> list[str]:
    return [s.name for s in load_skills(skills_root)]


def find_skill(skills_root: Path, name: str) -> Optional[SkillMetadata]:
    for skill in load_skills(skills_root):
        if skill.name == name or name in skill.aliases:
            return skill
    return None


def skill_catalog_lines(skills: Iterable[SkillMetadata]) -> list[str]:
    lines: list[str] = []
    for skill in skills:
        alias_suffix = (
            f" (aliases: {', '.join(skill.aliases)})" if skill.aliases else ""
        )
        lines.append(f"{skill.name}: {skill.description}{alias_suffix}")
    return lines
