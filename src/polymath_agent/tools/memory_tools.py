"""Tool wrappers around the JSON memory store."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from polymath_agent.memory import MemoryRecord, MemoryStore
from polymath_agent.tools.registry import ToolSpec
from polymath_agent.tools.workspace import format_json


class MemoryTools:
    """Expose small persistent memories to the model."""

    def __init__(self, memory: MemoryStore) -> None:
        self.memory = memory

    def specs(self) -> List[ToolSpec]:
        return [
            ToolSpec(_remember_definition(), self._remember),
            ToolSpec(_recall_definition(), self._recall),
            ToolSpec(_forget_definition(), self._forget),
        ]

    def _remember(self, args: Mapping[str, Any]) -> str:
        key = _required_string(args, "key")
        value = _required_string(args, "value")
        record = self.memory.remember(key, value)
        return format_json(_record_to_dict(record))

    def _recall(self, args: Mapping[str, Any]) -> str:
        key = args.get("key")
        query = args.get("query")
        records = self.memory.recall(
            key=key.strip() if isinstance(key, str) and key.strip() else None,
            query=query.strip() if isinstance(query, str) and query.strip() else None,
        )
        return format_json([_record_to_dict(record) for record in records])

    def _forget(self, args: Mapping[str, Any]) -> str:
        key = _required_string(args, "key")
        existed = self.memory.forget(key)
        return format_json({"deleted": existed, "key": key})


def _record_to_dict(record: MemoryRecord) -> Dict[str, str]:
    return {"key": record.key, "value": record.value, "updated_at": record.updated_at}


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


def _remember_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "remember",
        "description": "Persist a small user-approved memory by key.",
        "parameters": _schema(
            {
                "key": {
                    "type": "string",
                    "description": "Stable memory key, such as user.project_goal.",
                },
                "value": {"type": "string", "description": "The memory content to store."},
            },
            ["key", "value"],
        ),
        "strict": True,
    }


def _recall_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "recall_memory",
        "description": "Recall memories by exact key, by search query, or all memories.",
        "parameters": _schema(
            {
                "key": {
                    "type": "string",
                    "description": "Optional exact key. Leave empty to omit.",
                },
                "query": {
                    "type": "string",
                    "description": "Optional case-insensitive search query. Leave empty to omit.",
                },
            },
            ["key", "query"],
        ),
        "strict": True,
    }


def _forget_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "forget_memory",
        "description": "Delete a memory by exact key.",
        "parameters": _schema(
            {"key": {"type": "string", "description": "Exact memory key to delete."}},
            ["key"],
        ),
        "strict": True,
    }
