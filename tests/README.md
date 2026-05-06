# Tests

The tests deliberately avoid live OpenAI API calls. They verify the deterministic parts of the
project: path safety, skill discovery, JSON memory behavior, and the Responses API tool-call loop
with a fake client.

Run them from the repository root:

```bash
python -m pytest
```

For the full quality gate used during development:

```bash
python -m pytest
python -m ruff check .
python -m mypy src tests
```
