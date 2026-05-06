# Tool Contracts

Tools are defined as strict JSON-schema function tools. Each tool returns a string because the
Responses API expects function-call outputs to be text. Structured results are encoded as formatted
JSON strings when that is clearer.

## Workspace Tools

### `read_file`

Reads a UTF-8 file inside the configured workspace.

Inputs:

- `path`: workspace-relative path.

Safety behavior:

- rejects paths outside the workspace
- rejects directories
- returns an error for non-UTF-8 files

### `list_dir`

Lists a directory inside the workspace.

Inputs:

- `path`: workspace-relative directory path
- `recursive`: recurse up to two levels when true

### `search_files`

Searches text files under a workspace directory.

Inputs:

- `pattern`: regex pattern, with literal fallback if the regex is invalid
- `dir`: workspace-relative search root
- `glob`: optional glob such as `*.py` or `docs/*.md`

Search skips common generated directories such as `.git`, `.venv`, `node_modules`, and caches.

### `fetch_url`

Fetches a public HTTP or HTTPS URL with a GET request.

Inputs:

- `url`: full URL

Safety behavior:

- allows only `http` and `https`
- sets a user agent
- truncates large responses
- times out after 15 seconds

### `ping`

Runs the platform ping command with a fixed count of five packets.

Inputs:

- `host`: hostname or IP address

Safety behavior:

- passes arguments as a list, not shell text
- rejects whitespace and leading command flags in the host

### `bash`

Runs a Bash command.

Inputs:

- `command`: shell command string

This is the broadest and riskiest tool. It exists because the original project exposed a general
shell tool. The Python implementation adds a timeout, captures output, and documents that narrower
tools should be preferred.

## Skill Tools

### `list_skills`

Returns available skill names and descriptions.

### `load_skill`

Loads the full `SKILL.md` for one skill. The system prompt instructs the model to call this before
following a matching skill.

### `read_skill_file`

Reads files from a skill's `scripts/`, `references/`, or `assets/` directory.

### `list_skill_files`

Lists optional bundled files for a skill.

## Memory Tools

### `remember`

Stores a key-value memory in `.polymath/memory.json`.

Inputs:

- `key`: stable key using letters, digits, `_`, `.`, `:`, or `-`
- `value`: non-empty text

### `recall_memory`

Returns memories by exact key, query, or all memories.

Inputs:

- `key`: optional exact key; pass an empty string to omit
- `query`: optional case-insensitive query; pass an empty string to omit

### `forget_memory`

Deletes one memory by exact key.

## Adding A Tool

1. Add a runner method or class in `src/polymath_agent/tools/`.
2. Add a strict JSON schema with `additionalProperties: false`.
3. Register it in `build_tool_registry(...)`.
4. Add tests for valid inputs, invalid inputs, and boundary behavior.
5. Document it here.
