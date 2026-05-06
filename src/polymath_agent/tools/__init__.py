"""Public helpers for constructing the model tool registry."""

from __future__ import annotations

from pathlib import Path

from polymath_agent.memory import MemoryStore
from polymath_agent.skills import SkillsRepository
from polymath_agent.tools.memory_tools import MemoryTools
from polymath_agent.tools.registry import ToolRegistry
from polymath_agent.tools.skill_tools import SkillTools
from polymath_agent.tools.workspace import WorkspaceTools


def build_tool_registry(
    workspace: Path,
    skills: SkillsRepository,
    memory: MemoryStore,
    max_output_chars: int,
) -> ToolRegistry:
    """Create the complete registry used by the agent."""

    specs = []
    specs.extend(WorkspaceTools(workspace, max_output_chars=max_output_chars).specs())
    specs.extend(SkillTools(skills).specs())
    specs.extend(MemoryTools(memory).specs())
    return ToolRegistry(specs)


__all__ = ["ToolRegistry", "build_tool_registry"]
