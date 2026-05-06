"""Small JSON heartbeat file for observing a running agent."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class Heartbeat:
    """Write process status snapshots to disk.

    A heartbeat is intentionally simple: every call overwrites one JSON file atomically enough for
    local development. It is useful in a course project because it makes long-running behavior
    inspectable without introducing a database or background service.
    """

    def __init__(self, path: Path, metadata: Dict[str, Any]) -> None:
        self.path = path
        self.metadata = dict(metadata)
        self.turn_count = 0

    def beat(self, status: str, **extra: Any) -> None:
        """Write a status snapshot.

        Heartbeat failures should not crash the agent, so callers may safely ignore exceptions if
        they are running in a restricted filesystem.
        """

        payload = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
            "turn_count": self.turn_count,
            **self.metadata,
            **extra,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(self.path)

    def increment_turns(self) -> None:
        """Record that a user turn completed."""

        self.turn_count += 1
