"""OpenAI Responses API loop for the Polymath agent."""

from __future__ import annotations

import json
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional

from polymath_agent.config import AgentConfig
from polymath_agent.heartbeat import Heartbeat
from polymath_agent.memory import MemoryStore
from polymath_agent.skills import SkillsRepository
from polymath_agent.tools import build_tool_registry


@dataclass(frozen=True)
class AgentTurn:
    """The result of one user turn."""

    response: Any
    last_response_id: Optional[str]
    output_text: str
    tool_rounds: int


class PolymathAgent:
    """A compact, typed agent loop built on the OpenAI Responses API."""

    def __init__(self, config: AgentConfig, client: Optional[Any] = None) -> None:
        self.config = config
        self.workspace = config.resolved_workspace()
        self.skills = SkillsRepository(config.resolved_skills_dir())
        self.memory = MemoryStore(config.resolved_memory_path())
        self.tools = build_tool_registry(
            workspace=self.workspace,
            skills=self.skills,
            memory=self.memory,
            max_output_chars=config.max_output_chars,
        )
        self.heartbeat = Heartbeat(
            config.resolved_heartbeat_path(),
            metadata={"model": config.model, "workspace": str(self.workspace)},
        )
        if client is not None:
            self.client = client
        else:
            self.client = _build_default_client()

    @property
    def system_prompt(self) -> str:
        """Build the current system prompt, including installed skill metadata."""

        return build_system_prompt(self.skills.available_skills_xml())

    def turn(self, user_text: str, previous_response_id: Optional[str] = None) -> AgentTurn:
        """Run one user turn, including all requested function calls."""

        if not user_text.strip():
            raise ValueError("user_text must be non-empty")

        self._beat("turn_started")
        response = self._create_response(
            input_items=[{"role": "user", "content": user_text}],
            previous_response_id=previous_response_id,
        )
        last_response_id = _as_optional_string(_get(response, "id"))

        tool_rounds = 0
        while True:
            calls = _function_calls(response)
            if not calls:
                break
            if tool_rounds >= self.config.max_tool_rounds:
                raise RuntimeError("model exceeded the configured tool-round limit")

            tool_outputs: List[Mapping[str, Any]] = []
            for call in calls:
                name = _as_string(_get(call, "name"))
                call_id = _as_string(_get(call, "call_id"))
                args = _parse_arguments(_as_string(_get(call, "arguments")))
                result = self.tools.run(name, args)
                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": result,
                    }
                )

            response = self._create_response(
                input_items=tool_outputs,
                previous_response_id=last_response_id,
            )
            last_response_id = _as_optional_string(_get(response, "id")) or last_response_id
            tool_rounds += 1

        self.heartbeat.increment_turns()
        text = extract_output_text(response)
        self._beat("turn_completed", last_response_id=last_response_id, tool_rounds=tool_rounds)
        return AgentTurn(
            response=response,
            last_response_id=last_response_id,
            output_text=text,
            tool_rounds=tool_rounds,
        )

    def _create_response(
        self,
        input_items: List[Mapping[str, Any]],
        previous_response_id: Optional[str],
    ) -> Any:
        params: Dict[str, Any] = {
            "model": self.config.model,
            "instructions": self.system_prompt,
            "input": input_items,
            "tools": self.tools.definitions,
            "store": self.config.store_responses,
        }
        if previous_response_id:
            params["previous_response_id"] = previous_response_id
        return self.client.responses.create(**params)

    def _beat(self, status: str, **extra: Any) -> None:
        with suppress(OSError):
            self.heartbeat.beat(status, **extra)


def build_system_prompt(skills_xml: str) -> str:
    """Build the instruction block shared across all turns."""

    base = (
        "You are Polymath, a careful AI agent that can inspect a local workspace, use shell "
        "commands, fetch public web pages, search files, use Agent Skills, and maintain small "
        "explicit memories. Prefer the narrowest safe tool for the job: use read_file, list_dir, "
        "and search_files before bash when they are sufficient. Treat bash as powerful and risky; "
        "avoid destructive commands unless the user clearly asked for them. When a task matches an "
        "installed Agent Skill, load that skill first, follow its instructions, and read any "
        "referenced skill files with read_skill_file. Use remember only for durable facts the user "
        "asked you to keep or facts that are clearly useful for this project. Keep answers "
        "concise, grounded in tool results, and explicit about errors or uncertainty."
    )
    if skills_xml:
        return f"{base}\n\n{skills_xml}"
    return base


def extract_output_text(response: Any) -> str:
    """Extract text from an OpenAI response object or compatible test double."""

    direct = _get(response, "output_text")
    if isinstance(direct, str) and direct:
        return direct

    output = _get(response, "output", [])
    if not isinstance(output, list):
        return ""
    fragments: List[str] = []
    for item in output:
        content = _get(item, "content", [])
        if not isinstance(content, list):
            continue
        for part in content:
            text = _get(part, "text")
            if isinstance(text, str):
                fragments.append(text)
    return "\n".join(fragments)


def _function_calls(response: Any) -> List[Any]:
    output = _get(response, "output", [])
    if not isinstance(output, list):
        return []
    return [item for item in output if _get(item, "type") == "function_call"]


def _parse_arguments(raw: str) -> Mapping[str, Any]:
    try:
        decoded = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _as_string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _as_optional_string(value: Any) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def _build_default_client() -> Any:
    try:
        from openai import OpenAI as OpenAIClient
    except ImportError as exc:  # pragma: no cover - only occurs without project deps installed.
        raise RuntimeError("The openai package is not installed. Run `pip install -e .`.") from exc
    return OpenAIClient()
