# Examples

These examples are prompts and workflows you can run after setting `OPENAI_API_KEY`.

## Inspect The Project

```bash
polymath-agent "List the top-level files and explain the project structure."
```

Expected behavior: the model should use `list_dir` and summarize the repository.

## Use A Skill

```bash
polymath-agent "Make a small ASCII art banner that says POLYMATH."
```

Expected behavior: the model should notice the `ascii-art-image` skill, call `load_skill`, and
return ASCII-only art in a code block.

## Use Memory

```bash
polymath-agent "Remember that this course project is about building a Python agent from scratch."
polymath-agent "What do you remember about this course project?"
```

Expected behavior: the first command can use `remember`; the second can use `recall_memory`.

## Read A File

```bash
polymath-agent "Read docs/security.md and summarize the main risks."
```

Expected behavior: the model should use `read_file`, not `bash`.
