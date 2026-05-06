from pathlib import Path

from polymath_agent.tools.registry import ToolRegistry
from polymath_agent.tools.workspace import WorkspaceTools


def build_registry(tmp_path: Path) -> ToolRegistry:
    return ToolRegistry(WorkspaceTools(tmp_path, max_output_chars=10_000).specs())


def test_read_list_and_search_workspace_files(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "example.py").write_text(
        "def hello():\n    return 'world'\n",
        encoding="utf-8",
    )
    registry = build_registry(tmp_path)

    assert "example.py" in registry.run("list_dir", {"path": ".", "recursive": True})
    assert "return 'world'" in registry.run("read_file", {"path": "src/example.py"})
    search_result = registry.run("search_files", {"pattern": "hello", "dir": ".", "glob": "*.py"})
    assert "src/example.py:1" in search_result


def test_workspace_paths_cannot_escape_root(tmp_path: Path) -> None:
    registry = build_registry(tmp_path)

    assert registry.run("read_file", {"path": "../outside.txt"}).startswith("error:")
    assert registry.run("list_dir", {"path": "../", "recursive": False}).startswith("error:")
