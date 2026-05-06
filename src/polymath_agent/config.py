"""Configuration objects for the Polymath agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

DEFAULT_MODEL = "gpt-5.5"
DEFAULT_MAX_TOOL_ROUNDS = 8


@dataclass(frozen=True)
class AgentConfig:
    """Runtime configuration for an agent process.

    The defaults are deliberately useful for local development: the workspace is the current
    directory, skills live in ``.skills``, and persistent state lives in ``.polymath``.
    """

    model: str = field(default_factory=lambda: os.getenv("POLYMATH_MODEL", DEFAULT_MODEL))
    workspace: Path = field(default_factory=Path.cwd)
    skills_dir: Optional[Path] = None
    memory_path: Optional[Path] = None
    heartbeat_path: Optional[Path] = None
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS
    store_responses: bool = True
    max_output_chars: int = 300_000

    def resolved_workspace(self) -> Path:
        """Return the normalized workspace directory."""

        return self.workspace.expanduser().resolve()

    def resolved_skills_dir(self) -> Path:
        """Return the directory that contains Agent Skills."""

        env_dir = os.getenv("SKILLS_DIR")
        raw = self.skills_dir or (Path(env_dir) if env_dir else Path(".skills"))
        return _resolve_from_workspace(raw, self.resolved_workspace())

    def resolved_memory_path(self) -> Path:
        """Return the JSON file used by memory tools."""

        raw = self.memory_path or Path(".polymath/memory.json")
        return _resolve_from_workspace(raw, self.resolved_workspace())

    def resolved_heartbeat_path(self) -> Path:
        """Return the JSON file updated by the heartbeat subsystem."""

        raw = self.heartbeat_path or Path(".polymath/heartbeat.json")
        return _resolve_from_workspace(raw, self.resolved_workspace())


def _resolve_from_workspace(path: Path, workspace: Path) -> Path:
    """Resolve relative paths from the workspace and absolute paths directly."""

    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded.resolve()
    return (workspace / expanded).resolve()
