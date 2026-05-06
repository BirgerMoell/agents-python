"""A tiny persistent key-value memory store for the agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

MEMORY_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}$")
MAX_MEMORY_VALUE_CHARS = 20_000


@dataclass(frozen=True)
class MemoryRecord:
    """A stored memory value plus metadata."""

    key: str
    value: str
    updated_at: str


class MemoryStore:
    """JSON-backed memory for small facts the model should remember.

    The store is deliberately modest. It is good for course demonstrations and reproducible local
    state, not for high-volume retrieval or secrets management.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def remember(self, key: str, value: str) -> MemoryRecord:
        """Create or replace one memory entry."""

        clean_key = key.strip()
        clean_value = value.strip()
        if not MEMORY_KEY_RE.fullmatch(clean_key):
            raise ValueError(
                "memory key must be 1-80 chars and contain only letters, digits, _, ., :, or -"
            )
        if not clean_value:
            raise ValueError("memory value must be non-empty")
        if len(clean_value) > MAX_MEMORY_VALUE_CHARS:
            raise ValueError("memory value is too large")

        data = self._load()
        record = MemoryRecord(
            key=clean_key,
            value=clean_value,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        data[clean_key] = {"value": record.value, "updated_at": record.updated_at}
        self._write(data)
        return record

    def recall(self, key: Optional[str] = None, query: Optional[str] = None) -> List[MemoryRecord]:
        """Return memories by exact key, by search query, or all memories."""

        data = self._load()
        records = [
            MemoryRecord(
                key=item_key,
                value=str(raw.get("value", "")),
                updated_at=str(raw.get("updated_at", "")),
            )
            for item_key, raw in sorted(data.items())
            if isinstance(raw, dict)
        ]
        if key:
            wanted = key.strip()
            return [record for record in records if record.key == wanted]
        if query:
            needle = query.strip().lower()
            return [
                record
                for record in records
                if needle in record.key.lower() or needle in record.value.lower()
            ]
        return records

    def forget(self, key: str) -> bool:
        """Delete one memory entry. Returns ``True`` if an entry existed."""

        clean_key = key.strip()
        data = self._load()
        existed = clean_key in data
        if existed:
            del data[clean_key]
            self._write(data)
        return existed

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(raw, dict):
            return {}
        result: Dict[str, Dict[str, Any]] = {}
        for key, value in raw.items():
            if isinstance(key, str) and isinstance(value, dict):
                result[key] = value
        return result

    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(self.path)
