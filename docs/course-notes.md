# Course Notes

This repository is structured to make grading and review easy.

## What To Look At First

1. `README.md` for the project overview.
2. `src/polymath_agent/agent.py` for the core model/tool loop.
3. `src/polymath_agent/tools/workspace.py` for local tool safety.
4. `src/polymath_agent/skills.py` for Agent Skills support.
5. `tests/` for deterministic verification.

## Original Project Mapping

| Original TypeScript file | Python equivalent |
| --- | --- |
| `agent.ts` | `src/polymath_agent/agent.py` and `src/polymath_agent/cli.py` |
| `tools.ts` | `src/polymath_agent/tools/` |
| `skills.ts` | `src/polymath_agent/skills.py` |
| `.skills/` | `.skills/` |

## Improvements In The Python Copy

- The code is packaged and importable.
- Tool implementations are split by responsibility.
- File path boundaries are tested.
- The OpenAI client is injectable for tests.
- Memory and heartbeat features are implemented rather than only planned.
- The codebase includes subsystem documentation.

## Suggested Presentation Talking Points

- Explain why tool definitions use strict JSON schema.
- Show the fake client test in `tests/test_agent.py`.
- Show how `previous_response_id` is used after tool calls.
- Demonstrate path traversal protection with `tests/test_workspace_tools.py`.
- Load an included skill and show how its full instructions are not injected until needed.
