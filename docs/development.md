# Development Workflow

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quality Gate

```bash
python -m pytest
python -m ruff check .
python -m mypy src tests scripts
```

Tests use a fake OpenAI client and do not require `OPENAI_API_KEY`.

## Local Manual Check

After setting `OPENAI_API_KEY`, run:

```bash
polymath-agent "Use list_skills and tell me what skills are installed."
```

Then try an interactive session:

```bash
polymath-agent
```

For an automated live smoke test:

```bash
PYTHONPATH=src python scripts/live_smoke.py
```

This checks the real OpenAI request/tool-output/request loop and exits non-zero if the model does
not call a tool. It is not part of `pytest` because it requires credentials and makes a billable API
call.

## Packaging

Build a wheel:

```bash
python -m pip install build
python -m build
```

The package uses `hatchling` and includes only `src/polymath_agent` in the wheel. The example
`.skills` directory is repository content, not package data.

## Contribution Checklist

- Keep new tools narrow and well documented.
- Add tests for both success and failure behavior.
- Update `docs/tools.md` when tool schemas change.
- Update `docs/architecture.md` when the agent loop changes.
- Avoid adding dependencies unless they simplify real complexity.
