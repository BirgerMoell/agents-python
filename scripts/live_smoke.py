"""Run a live end-to-end smoke test against the OpenAI API.

This script is intentionally separate from the normal pytest suite because it requires a real
``OPENAI_API_KEY`` and will make a billable API call. It verifies the part unit tests cannot:
whether the packaged agent can reach OpenAI, receive a tool call, execute that tool locally, and
return a final answer.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from polymath_agent.agent import PolymathAgent
from polymath_agent.config import DEFAULT_MODEL, AgentConfig

PROMPT = (
    "Use the list_dir tool on the project root, then answer with exactly one sentence naming "
    "two top-level files you saw."
)


def main() -> int:
    """Run one live agent turn and fail if no tool call happened."""

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Missing OPENAI_API_KEY. Set it in the environment or create .env from .env.example.",
            file=sys.stderr,
        )
        return 2

    agent = PolymathAgent(
        AgentConfig(
            model=os.getenv("POLYMATH_MODEL", DEFAULT_MODEL),
            workspace=Path.cwd(),
            max_tool_rounds=4,
        )
    )
    turn = agent.turn(PROMPT)
    print(turn.output_text)
    print(f"\ntool_rounds={turn.tool_rounds}")

    if not turn.output_text.strip():
        print("Smoke test failed: the model returned no final text.", file=sys.stderr)
        return 1
    if turn.tool_rounds < 1:
        print("Smoke test failed: the model did not call any tool.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
