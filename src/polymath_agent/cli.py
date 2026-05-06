"""Command-line interface for the Polymath agent."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from polymath_agent.agent import PolymathAgent
from polymath_agent.config import DEFAULT_MODEL, AgentConfig


def main(argv: Optional[List[str]] = None) -> int:
    """Run the agent CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.no_dotenv:
        _load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Missing OPENAI_API_KEY. Create .env from .env.example or export the variable.",
            file=sys.stderr,
        )
        return 2

    config = AgentConfig(
        model=args.model,
        workspace=Path(args.workspace),
        skills_dir=Path(args.skills_dir) if args.skills_dir else None,
        memory_path=Path(args.memory_file) if args.memory_file else None,
        heartbeat_path=Path(args.heartbeat_file) if args.heartbeat_file else None,
        max_tool_rounds=args.max_tool_rounds,
    )
    agent = PolymathAgent(config)

    prompt = " ".join(args.prompt).strip()
    if prompt:
        turn = agent.turn(prompt)
        if turn.output_text:
            print(turn.output_text)
        return 0

    print("Polymath Agent - type a message and press Enter (Ctrl+C to exit).\n")
    previous_response_id: Optional[str] = None
    while True:
        try:
            line = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        try:
            turn = agent.turn(line, previous_response_id=previous_response_id)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            continue
        previous_response_id = turn.last_response_id
        if turn.output_text:
            print(f"\nPolymath: {turn.output_text}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="polymath-agent",
        description="Run a small OpenAI Responses API agent with local tools and Agent Skills.",
    )
    parser.add_argument("prompt", nargs="*", help="Optional one-shot prompt. Omit for chat mode.")
    parser.add_argument(
        "--model",
        default=os.getenv("POLYMATH_MODEL", DEFAULT_MODEL),
        help=f"OpenAI model to use. Defaults to env POLYMATH_MODEL or {DEFAULT_MODEL}.",
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Workspace root exposed to file tools. Defaults to the current directory.",
    )
    parser.add_argument(
        "--skills-dir",
        default=None,
        help="Skills directory. Defaults to env SKILLS_DIR or .skills inside the workspace.",
    )
    parser.add_argument(
        "--memory-file",
        default=None,
        help="JSON memory file. Defaults to .polymath/memory.json inside the workspace.",
    )
    parser.add_argument(
        "--heartbeat-file",
        default=None,
        help="Heartbeat JSON file. Defaults to .polymath/heartbeat.json inside the workspace.",
    )
    parser.add_argument(
        "--max-tool-rounds",
        type=int,
        default=8,
        help="Maximum model/tool continuation rounds per user turn.",
    )
    parser.add_argument(
        "--no-dotenv",
        action="store_true",
        help="Do not load a local .env file before starting.",
    )
    return parser


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()
