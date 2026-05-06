"""Tool registration and execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping

ToolRunner = Callable[[Mapping[str, Any]], str]


@dataclass(frozen=True)
class ToolSpec:
    """One executable tool and its OpenAI tool definition."""

    definition: Dict[str, Any]
    runner: ToolRunner

    @property
    def name(self) -> str:
        """Return the tool name from its JSON schema definition."""

        return str(self.definition["name"])


class ToolRegistry:
    """A small name-to-tool registry used by the agent loop."""

    def __init__(self, specs: List[ToolSpec]) -> None:
        self._specs = {spec.name: spec for spec in specs}

    @property
    def definitions(self) -> List[Dict[str, Any]]:
        """Return OpenAI-compatible tool definitions."""

        return [spec.definition for spec in self._specs.values()]

    def run(self, name: str, args: Mapping[str, Any]) -> str:
        """Execute a tool and normalize unexpected failures into text output."""

        spec = self._specs.get(name)
        if spec is None:
            return f'error: unknown tool "{name}"'
        try:
            return spec.runner(args)
        except Exception as exc:  # pragma: no cover - defensive boundary for model-facing tools.
            return f"error: {exc}"
