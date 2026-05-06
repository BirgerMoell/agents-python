"""Tool wrappers around Agent Skills."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from polymath_agent.skills import SkillsRepository
from polymath_agent.tools.registry import ToolSpec
from polymath_agent.tools.workspace import format_json


class SkillTools:
    """Expose skill discovery and loading as model-callable functions."""

    def __init__(self, skills: SkillsRepository) -> None:
        self.skills = skills

    def specs(self) -> List[ToolSpec]:
        return [
            ToolSpec(_list_skills_definition(), self._list_skills),
            ToolSpec(_load_skill_definition(), self._load_skill),
            ToolSpec(_read_skill_file_definition(), self._read_skill_file),
            ToolSpec(_list_skill_files_definition(), self._list_skill_files),
        ]

    def _list_skills(self, args: Mapping[str, Any]) -> str:
        del args
        skills = self.skills.discover()
        if not skills:
            return "No skills installed. Add skill folders with SKILL.md to .skills."
        return "\n\n".join(f"{skill.name}: {skill.description}" for skill in skills)

    def _load_skill(self, args: Mapping[str, Any]) -> str:
        name = _required_string(args, "name")
        content = self.skills.load_skill(name)
        return content if content is not None else f'error: skill "{name}" not found'

    def _read_skill_file(self, args: Mapping[str, Any]) -> str:
        name = _required_string(args, "skill_name")
        path = _required_string(args, "path")
        return self.skills.read_skill_file(name, path)

    def _list_skill_files(self, args: Mapping[str, Any]) -> str:
        name = _required_string(args, "skill_name")
        return self.skills.list_skill_files(name)


def _required_string(args: Mapping[str, Any], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _schema(properties: Mapping[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": required,
        "additionalProperties": False,
    }


def _list_skills_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "list_skills",
        "description": "List installed Agent Skills with names and descriptions.",
        "parameters": _schema({}, []),
        "strict": True,
    }


def _load_skill_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "load_skill",
        "description": "Load a skill's full SKILL.md instructions before using that skill.",
        "parameters": _schema(
            {"name": {"type": "string", "description": "Skill name, such as weather-finder."}},
            ["name"],
        ),
        "strict": True,
    }


def _read_skill_file_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "read_skill_file",
        "description": "Read a file from a skill's scripts/, references/, or assets/ directory.",
        "parameters": _schema(
            {
                "skill_name": {"type": "string", "description": "Skill name."},
                "path": {
                    "type": "string",
                    "description": "Path relative to the skill root, such as references/NOTES.md.",
                },
            },
            ["skill_name", "path"],
        ),
        "strict": True,
    }


def _list_skill_files_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "list_skill_files",
        "description": "List bundled scripts, references, and assets for one skill.",
        "parameters": _schema(
            {"skill_name": {"type": "string", "description": "Skill name."}},
            ["skill_name"],
        ),
        "strict": True,
    }


def skills_as_json(skills: SkillsRepository) -> str:
    """Return skill metadata as JSON for diagnostics."""

    return format_json(
        [
            {
                "name": skill.name,
                "description": skill.description,
                "path": str(skill.path),
            }
            for skill in skills.discover()
        ]
    )
