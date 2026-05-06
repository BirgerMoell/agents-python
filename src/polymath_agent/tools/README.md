# Tool Modules

The `tools` package exposes local functionality to the model through strict JSON-schema function
tools.

## Modules

- `registry.py`: Stores tool definitions and dispatches calls by name.
- `workspace.py`: File, directory, search, URL, ping, and Bash tools.
- `skill_tools.py`: Tools for listing and loading Agent Skills.
- `memory_tools.py`: Tools for writing, reading, and deleting JSON memories.

## Output Convention

Every tool returns a string. Errors start with `error:` so the model can recover and try another
approach.

## Adding A New Tool

Add the runner, add the schema, register the spec in `build_tool_registry`, then document and test
the behavior.
