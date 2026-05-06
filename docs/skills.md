# Agent Skills

Agent Skills are local instruction bundles. They let the agent load detailed procedural knowledge
only when it is relevant, instead of stuffing every instruction into the system prompt.

## Directory Layout

```text
.skills/
+-- skill-name/
    +-- SKILL.md       # required
    +-- references/    # optional
    +-- scripts/       # optional
    +-- assets/        # optional
```

## Required Frontmatter

`SKILL.md` must start with simple frontmatter:

```yaml
---
name: skill-name
description: What the skill does and when the agent should use it.
---
```

Rules enforced by `SkillsRepository`:

- `name` must be lowercase letters, digits, and hyphens.
- `name` must match the folder name exactly.
- `name` must be at most 64 characters.
- `description` must be present and at most 1024 characters.

## Runtime Lifecycle

1. The agent discovers valid skills at startup.
2. The system prompt receives a lightweight `<available_skills>` XML block.
3. When a task matches a skill, the model calls `load_skill`.
4. The model follows the skill's Markdown instructions.
5. If the skill references bundled files, the model calls `read_skill_file`.

## Included Example Skills

- `ascii-art-image`: produces ASCII-only images and banners.
- `create-skill`: explains how to create new Agent Skills.
- `weather-finder`: uses Open-Meteo-style weather lookup instructions.

These examples are copied from the original TypeScript project so students can compare behavior
between the two implementations.

## Why Skill Files Are Restricted

`read_skill_file` only reads from `scripts/`, `references/`, and `assets/`. This keeps skill loading
focused on intentionally bundled material and avoids turning skill access into a second arbitrary
file reader.
