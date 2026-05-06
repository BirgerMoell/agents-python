from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

from polymath_agent.agent import PolymathAgent
from polymath_agent.config import AgentConfig


class FakeResponses:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return SimpleNamespace(
                id="response-1",
                output=[
                    SimpleNamespace(
                        type="function_call",
                        name="read_file",
                        call_id="call-1",
                        arguments='{"path": "README.md"}',
                    )
                ],
                output_text="",
            )
        return SimpleNamespace(
            id="response-2",
            output=[SimpleNamespace(content=[SimpleNamespace(text="I read the file.")])],
            output_text="I read the file.",
        )


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_agent_runs_tool_call_loop(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("Course project.\n", encoding="utf-8")
    client = FakeClient()
    agent = PolymathAgent(
        AgentConfig(
            model="test-model",
            workspace=tmp_path,
            skills_dir=tmp_path / ".skills",
            memory_path=tmp_path / ".polymath" / "memory.json",
            heartbeat_path=tmp_path / ".polymath" / "heartbeat.json",
        ),
        client=client,
    )

    turn = agent.turn("Read the README")

    assert turn.output_text == "I read the file."
    assert turn.tool_rounds == 1
    second_call = client.responses.calls[1]
    assert second_call["previous_response_id"] == "response-1"
    assert second_call["input"][0]["type"] == "function_call_output"
    assert "Course project." in second_call["input"][0]["output"]
