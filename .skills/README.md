# Example Agent Skills

This folder contains example skills copied from the original project.

Each skill lives in its own folder and contains a required `SKILL.md` file:

```text
.skills/
├── ascii-art-image/
├── create-skill/
└── weather-finder/
```

The agent only injects skill metadata at startup. Full instructions are loaded on demand with the
`load_skill` tool.

To add a skill:

1. Create `.skills/my-skill/SKILL.md`.
2. Add frontmatter with `name: my-skill` and a useful `description`.
3. Put long references in `.skills/my-skill/references/`.
4. Restart the agent or run it again so discovery sees the new skill.
