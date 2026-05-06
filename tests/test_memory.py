from pathlib import Path

from polymath_agent.memory import MemoryStore


def test_memory_store_round_trip_and_search(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")

    stored = store.remember("course.goal", "Build a documented Python agent.")

    assert stored.key == "course.goal"
    assert store.recall(key="course.goal")[0].value == "Build a documented Python agent."
    assert store.recall(query="documented")[0].key == "course.goal"
    assert store.forget("course.goal") is True
    assert store.recall() == []


def test_memory_rejects_bad_keys(tmp_path: Path) -> None:
    store = MemoryStore(tmp_path / "memory.json")

    try:
        store.remember("../secret", "nope")
    except ValueError as exc:
        assert "memory key" in str(exc)
    else:
        raise AssertionError("bad memory key should fail")
