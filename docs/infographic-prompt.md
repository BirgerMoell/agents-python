# README Hero Infographic Prompt

Use this prompt to generate a polished README hero infographic for the top of the repository.
Recommended output path after generation:

```text
docs/assets/polymath-agent-infographic.png
```

Suggested Markdown placement directly below the main README heading:

```markdown
![Polymath Agent Python architecture infographic](docs/assets/polymath-agent-infographic.png)
```

## Copy-Paste Prompt

```text
Create a world-class 16:9 README hero infographic for a GitHub repository named "Polymath Agent Python".

Purpose:
Explain, at a glance, that this is a transparent Python implementation of a tool-using OpenAI Responses API agent, designed for a course project and built to be readable, tested, and well documented.

Art direction:
Premium technical editorial infographic, crisp vector-like rendering, suitable for the top of a serious engineering README. Use a clean off-white or very light neutral background with deep ink text, electric blue accents, mint green for local tools, amber for skills, and coral for validation. The style should feel like a top-tier developer documentation diagram: precise, calm, modern, and trustworthy. Avoid stock-photo aesthetics, decorative gradients, fake screenshots, clutter, tiny text, cartoon characters, and official company logos.

Canvas:
2400 x 1350 px, 16:9 aspect ratio, high resolution, sharp edges, generous margins, balanced negative space. It must remain readable when displayed at GitHub README width.

Main layout:
Place a clear title at the top:
"Polymath Agent Python"

Subtitle beneath it:
"A transparent Responses API agent with local tools, skills, memory, tests, and documentation"

Central visual:
A clean circular or left-to-right flow diagram showing the actual agent loop:
1. User prompt
2. OpenAI Responses API
3. Function call request
4. Python ToolRegistry
5. Local tool execution
6. function_call_output
7. Final answer

Make the loop visually obvious with numbered nodes and arrows. The "Python ToolRegistry" node should be the central hub.

Left side module stack:
Show a tidy vertical stack labeled "Python package" with these module cards:
- agent.py: response loop
- tools/: schemas + runners
- skills.py: Agent Skills
- memory.py: JSON memory
- heartbeat.py: run status
- cli.py: one-shot + chat

Right side quality stack:
Show a tidy vertical stack labeled "Course-ready engineering" with these cards:
- strict JSON schemas
- path-safe workspace tools
- pytest fake-client tests
- Ruff linting
- mypy type checks
- live smoke test

Bottom band:
Add a horizontal band labeled "Agent Skills loaded on demand" showing:
.skills/<skill>/SKILL.md -> load_skill -> read_skill_file -> focused instructions

Small footer note:
"No hidden framework: the model-tool loop is visible, inspectable, and testable."

Text rules:
Use only the labels above or very close variants. Keep text large, sparse, and legible. No paragraphs inside the image. No code blocks. No invented metrics. No fake terminal output. Do not misspell "Responses API", "ToolRegistry", "function_call_output", "pytest", "Ruff", or "mypy".

Composition rules:
The image should communicate architecture first, polish second. Use consistent line weights, aligned cards, clear arrows, and a restrained palette with multiple accent colors. Make the central loop the strongest visual element, with the module and quality stacks supporting it. Leave enough top and bottom padding so the image feels elegant when embedded directly under the README title.

Negative constraints:
No official logos. No mascots. No 3D robots. No busy dashboards. No dark mode background. No tiny unreadable labels. No random code snippets. No generic AI brain imagery. No extra claims that are not represented in the repository.
```
