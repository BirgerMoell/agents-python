"""Agent Skills discovery and loading.

This module implements the lightweight Agent Skills pattern used by the original TypeScript
project: each skill is a folder containing a ``SKILL.md`` file with YAML-like frontmatter.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_SKILL_FILE_DIRS = {"assets", "references", "scripts"}


@dataclass(frozen=True)
class SkillMetadata:
    """Metadata extracted from a skill's ``SKILL.md`` file."""

    name: str
    description: str
    path: Path
    directory: Path


class SkillsRepository:
    """Discover and read skills from a local directory."""

    def __init__(self, skills_dir: Path) -> None:
        self.skills_dir = skills_dir.expanduser().resolve()

    def discover(self) -> List[SkillMetadata]:
        """Return all valid skills sorted by name."""

        if not self.skills_dir.is_dir():
            return []

        skills: List[SkillMetadata] = []
        for entry in sorted(self.skills_dir.iterdir(), key=lambda item: item.name):
            if not entry.is_dir() or entry.name.startswith("."):
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.is_file():
                continue
            try:
                raw = skill_md.read_text(encoding="utf-8")
            except OSError:
                continue
            metadata = parse_skill_markdown(entry.resolve(), skill_md.resolve(), raw)
            if metadata is not None:
                skills.append(metadata)
        return skills

    def get_metadata(self, name: str) -> Optional[SkillMetadata]:
        """Return metadata for one skill, or ``None`` when it is missing or invalid."""

        normalized = name.strip()
        skill_dir = (self.skills_dir / normalized).resolve()
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            return None
        try:
            raw = skill_md.read_text(encoding="utf-8")
        except OSError:
            return None
        return parse_skill_markdown(skill_dir, skill_md.resolve(), raw)

    def load_skill(self, name: str) -> Optional[str]:
        """Return the full ``SKILL.md`` content for activation."""

        metadata = self.get_metadata(name)
        if metadata is None:
            return None
        try:
            return metadata.path.read_text(encoding="utf-8")
        except OSError:
            return None

    def read_skill_file(self, skill_name: str, relative_path: str) -> str:
        """Read a file from ``scripts/``, ``references/``, or ``assets/`` inside one skill."""

        metadata = self.get_metadata(skill_name)
        if metadata is None:
            return "error: skill not found"
        try:
            path = self.resolve_skill_file(metadata, relative_path)
        except ValueError as exc:
            return f"error: {exc}"
        try:
            if not path.is_file():
                return "error: not a file"
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return "error: file not found"
        except UnicodeDecodeError:
            return "error: file is not valid UTF-8 text"
        except OSError as exc:
            return f"error: {exc}"

    def list_skill_files(self, skill_name: str) -> str:
        """List optional bundled files for a skill."""

        metadata = self.get_metadata(skill_name)
        if metadata is None:
            return "error: skill not found"
        lines: List[str] = []
        for directory_name in sorted(ALLOWED_SKILL_FILE_DIRS):
            directory = metadata.directory / directory_name
            if not directory.is_dir():
                continue
            for path in sorted(directory.rglob("*")):
                if path.is_file():
                    lines.append(path.relative_to(metadata.directory).as_posix())
        return "\n".join(lines) if lines else "no optional files"

    def resolve_skill_file(self, metadata: SkillMetadata, relative_path: str) -> Path:
        """Resolve a bundled skill file and ensure it stays inside the skill directory."""

        requested = Path(relative_path)
        if requested.is_absolute():
            raise ValueError("path must be relative to the skill directory")
        parts = requested.parts
        if not parts or parts[0] not in ALLOWED_SKILL_FILE_DIRS:
            allowed = ", ".join(sorted(ALLOWED_SKILL_FILE_DIRS))
            raise ValueError(f"path must start with one of: {allowed}")
        resolved = (metadata.directory / requested).resolve()
        try:
            resolved.relative_to(metadata.directory)
        except ValueError as exc:
            raise ValueError("path must stay inside the skill directory") from exc
        return resolved

    def available_skills_xml(self) -> str:
        """Return an XML block suitable for injecting into the system prompt."""

        return build_available_skills_xml(self.discover())


def parse_skill_markdown(
    skill_dir: Path, skill_md_path: Path, raw_content: str
) -> Optional[SkillMetadata]:
    """Parse and validate skill metadata.

    The project only needs ``name`` and ``description`` from frontmatter, so this parser is small
    by design. It accepts simple ``key: value`` frontmatter and ignores all other keys.
    """

    frontmatter = _extract_frontmatter(raw_content)
    if frontmatter is None:
        return None
    data = _parse_simple_frontmatter(frontmatter)
    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    if not name or not description:
        return None
    if len(name) > 64 or len(description) > 1024:
        return None
    if not SKILL_NAME_RE.fullmatch(name):
        return None
    if name != skill_dir.name:
        return None
    return SkillMetadata(
        name=name,
        description=description,
        path=skill_md_path,
        directory=skill_dir,
    )


def build_available_skills_xml(skills: Iterable[SkillMetadata]) -> str:
    """Build the ``<available_skills>`` prompt block."""

    parts = []
    for skill in skills:
        parts.append(
            "  <skill>\n"
            f"    <name>{html.escape(skill.name)}</name>\n"
            f"    <description>{html.escape(skill.description)}</description>\n"
            f"    <location>{html.escape(str(skill.path))}</location>\n"
            "  </skill>"
        )
    if not parts:
        return ""
    return "<available_skills>\n" + "\n".join(parts) + "\n</available_skills>"


def _extract_frontmatter(raw_content: str) -> Optional[List[str]]:
    lines = raw_content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:index]
    return None


def _parse_simple_frontmatter(lines: Iterable[str]) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition(":")
        if not separator:
            continue
        key = key.strip()
        if key not in {"name", "description"}:
            continue
        data[key] = _unquote(value.strip())
    return data


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
