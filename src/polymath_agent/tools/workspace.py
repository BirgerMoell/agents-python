"""Workspace and network tools exposed to the model."""

from __future__ import annotations

import fnmatch
import json
import platform
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from polymath_agent.tools.registry import ToolSpec

SKIPPED_SEARCH_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


class WorkspaceTools:
    """Tools that read, search, fetch, and execute inside a workspace."""

    def __init__(self, workspace: Path, max_output_chars: int = 300_000) -> None:
        self.workspace = workspace.expanduser().resolve()
        self.max_output_chars = max_output_chars

    def specs(self) -> List[ToolSpec]:
        """Return all workspace tool specs."""

        return [
            ToolSpec(_ping_definition(), self._run_ping),
            ToolSpec(_bash_definition(), self._run_bash),
            ToolSpec(_read_file_definition(), self._run_read_file),
            ToolSpec(_list_dir_definition(), self._run_list_dir),
            ToolSpec(_fetch_url_definition(), self._run_fetch_url),
            ToolSpec(_search_files_definition(), self._run_search_files),
        ]

    def resolve_inside_workspace(self, raw_path: str) -> Path:
        """Resolve a model-provided path and ensure it remains inside the workspace."""

        candidate = Path(raw_path).expanduser()
        if not candidate.is_absolute():
            candidate = self.workspace / candidate
        resolved = candidate.resolve()
        try:
            resolved.relative_to(self.workspace)
        except ValueError as exc:
            raise ValueError("path must be inside workspace") from exc
        return resolved

    def _run_ping(self, args: Mapping[str, Any]) -> str:
        host = _required_string(args, "host")
        if host.startswith("-") or any(char.isspace() for char in host):
            return "error: host must be a hostname or IP address, not command flags"
        count_flag = "-n" if platform.system().lower().startswith("win") else "-c"
        command = ["ping", count_flag, "5", host]
        return self._run_process(command, timeout_seconds=15)

    def _run_bash(self, args: Mapping[str, Any]) -> str:
        command = _required_string(args, "command")
        completed = subprocess.run(
            command,
            capture_output=True,
            executable="/bin/bash",
            shell=True,
            text=True,
            timeout=60,
            check=False,
        )
        output = _combine_output(completed.stdout, completed.stderr)
        if completed.returncode != 0:
            output = f"exit_code={completed.returncode}\n{output}"
        return _truncate(output, self.max_output_chars)

    def _run_read_file(self, args: Mapping[str, Any]) -> str:
        raw_path = _required_string(args, "path")
        try:
            path = self.resolve_inside_workspace(raw_path)
        except ValueError as exc:
            return f"error: {exc}"
        if not path.exists():
            return "error: file not found"
        if not path.is_file():
            return "error: not a file"
        try:
            return _truncate(path.read_text(encoding="utf-8"), self.max_output_chars)
        except UnicodeDecodeError:
            return "error: file is not valid UTF-8 text"
        except OSError as exc:
            return f"error: {exc}"

    def _run_list_dir(self, args: Mapping[str, Any]) -> str:
        raw_path = _required_string(args, "path")
        recursive = bool(args.get("recursive", False))
        try:
            path = self.resolve_inside_workspace(raw_path or ".")
        except ValueError as exc:
            return f"error: {exc}"
        if not path.exists():
            return "error: directory not found"
        if not path.is_dir():
            return "error: not a directory"
        lines = list(_walk_directory(path, self.workspace, recursive=recursive, max_depth=2))
        return "\n".join(lines) if lines else "(empty)"

    def _run_fetch_url(self, args: Mapping[str, Any]) -> str:
        url = _required_string(args, "url")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            return "error: url scheme must be http or https"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "PolymathAgentPython/1.0"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                body = response.read(self.max_output_chars + 1)
        except urllib.error.URLError as exc:
            return f"error: {exc}"
        text = body.decode("utf-8", errors="replace")
        return _truncate(text, self.max_output_chars)

    def _run_search_files(self, args: Mapping[str, Any]) -> str:
        pattern = _required_string(args, "pattern")
        raw_dir = str(args.get("dir") or ".")
        glob = args.get("glob")
        glob_text = glob.strip() if isinstance(glob, str) and glob.strip() else None
        try:
            directory = self.resolve_inside_workspace(raw_dir)
        except ValueError as exc:
            return f"error: {exc}"
        if not directory.exists():
            return "error: directory not found"
        if not directory.is_dir():
            return "error: not a directory"

        regex = _compile_regex_or_literal(pattern)
        results: List[str] = []
        for path in _iter_searchable_files(directory):
            if len(results) >= 200:
                break
            rel = path.relative_to(self.workspace).as_posix()
            if glob_text and not fnmatch.fnmatch(rel, glob_text):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if len(content) > 500_000:
                continue
            for match in regex.finditer(content):
                line_number = content.count("\n", 0, match.start()) + 1
                line = content.splitlines()[line_number - 1].strip()
                results.append(f"{rel}:{line_number}: {line}")
                if len(results) >= 200:
                    break
        return "\n".join(results) if results else "no matches"

    def _run_process(self, command: List[str], timeout_seconds: int) -> str:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        output = _combine_output(completed.stdout, completed.stderr)
        if completed.returncode != 0:
            output = f"exit_code={completed.returncode}\n{output}"
        return _truncate(output, self.max_output_chars)


def _iter_searchable_files(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.rglob("*")):
        if any(part in SKIPPED_SEARCH_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def _walk_directory(path: Path, workspace: Path, recursive: bool, max_depth: int) -> Iterable[str]:
    def walk(current: Path, depth: int) -> Iterable[str]:
        entries = sorted(current.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))
        for entry in entries:
            rel = entry.relative_to(workspace).as_posix()
            if entry.is_dir():
                yield rel + "/"
                if recursive and depth < max_depth:
                    yield from walk(entry, depth + 1)
            else:
                yield rel

    return walk(path, 0)


def _required_string(args: Mapping[str, Any], key: str) -> str:
    value = args.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value.strip()


def _compile_regex_or_literal(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern)
    except re.error:
        return re.compile(re.escape(pattern))


def _combine_output(stdout: str, stderr: str) -> str:
    if stdout and stderr:
        return stdout + "\n[stderr]\n" + stderr
    return stdout or stderr or "(no output)"


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    omitted = len(text) - max_chars
    return text[:max_chars] + f"\n... truncated {omitted} characters ..."


def _schema(properties: Mapping[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": required,
        "additionalProperties": False,
    }


def _ping_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "ping",
        "description": "Ping a host to check reachability or latency.",
        "parameters": _schema(
            {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP address, such as 8.8.8.8 or example.com.",
                }
            },
            ["host"],
        ),
        "strict": True,
    }


def _bash_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "bash",
        "description": (
            "Run a Bash command in the local environment. This is powerful and can be dangerous; "
            "prefer narrower tools for reading, listing, fetching, and searching."
        ),
        "parameters": _schema(
            {"command": {"type": "string", "description": "The Bash command to execute."}},
            ["command"],
        ),
        "strict": True,
    }


def _read_file_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "read_file",
        "description": "Read a UTF-8 text file inside the workspace.",
        "parameters": _schema(
            {
                "path": {
                    "type": "string",
                    "description": "Path relative to the workspace, such as README.md.",
                }
            },
            ["path"],
        ),
        "strict": True,
    }


def _list_dir_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "list_dir",
        "description": "List files and folders inside a workspace directory.",
        "parameters": _schema(
            {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to the workspace. Use . for root.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "When true, recurse up to two directory levels.",
                },
            },
            ["path", "recursive"],
        ),
        "strict": True,
    }


def _fetch_url_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "fetch_url",
        "description": "Fetch a public HTTP or HTTPS URL with GET and return text.",
        "parameters": _schema(
            {"url": {"type": "string", "description": "The full http:// or https:// URL."}},
            ["url"],
        ),
        "strict": True,
    }


def _search_files_definition() -> Dict[str, Any]:
    return {
        "type": "function",
        "name": "search_files",
        "description": (
            "Search UTF-8 text files under a workspace directory with a regex or literal."
        ),
        "parameters": _schema(
            {
                "pattern": {"type": "string", "description": "Regex pattern or literal text."},
                "dir": {
                    "type": "string",
                    "description": "Directory to search, relative to the workspace.",
                },
                "glob": {
                    "type": "string",
                    "description": "Optional file glob, such as *.py or docs/*.md.",
                },
            },
            ["pattern", "dir", "glob"],
        ),
        "strict": True,
    }


def format_json(data: Any) -> str:
    """Return stable JSON for tool outputs."""

    return json.dumps(data, indent=2, sort_keys=True)
