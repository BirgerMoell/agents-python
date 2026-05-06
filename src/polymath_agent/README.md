# `polymath_agent` Package

This package contains the Python implementation of the agent.

## Files

- `agent.py`: The OpenAI Responses API loop, tool-call continuation, and system prompt.
- `cli.py`: The command-line interface for one-shot and interactive usage.
- `config.py`: Runtime configuration and path resolution.
- `heartbeat.py`: JSON status snapshots for a running process.
- `memory.py`: JSON-backed memory records.
- `skills.py`: Agent Skills discovery, validation, and safe file loading.
- `tools/`: Tool schemas and execution.

## Design Principle

The package favors explicit Python over framework magic. Each subsystem has one clear job, which
makes the code easier to test, explain, and modify for a course project.
