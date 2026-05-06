# Security Notes

This project is designed for local learning, not for running untrusted users' prompts on a server.
It gives a model access to local tools, including Bash, so the security model matters.

## What Is Protected

- Workspace file tools cannot read outside the configured workspace.
- Skill file reads are restricted to `scripts/`, `references/`, and `assets/`.
- `fetch_url` only uses HTTP and HTTPS.
- `ping` avoids shell interpolation.
- Tool outputs are truncated to reduce runaway memory usage.
- Tool calls are limited by `max_tool_rounds`.
- Tests verify path traversal rejection.

## What Is Not Protected

- `bash` can run arbitrary shell commands.
- Network fetches can contact public URLs.
- The memory file is plain JSON and should not store secrets.
- The agent is not sandboxed by this Python package.
- Prompt injection in fetched or local content is not fully solved.

## Recommended Course Demo Settings

For classroom demos, run in a disposable directory:

```bash
mkdir demo-workspace
cd demo-workspace
polymath-agent --workspace .
```

Avoid putting real secrets, SSH keys, personal notes, or unrelated projects in the workspace.

## Production Hardening Ideas

- Replace `bash` with a narrower allowlisted command runner.
- Run the process in a container or VM with a read-only filesystem.
- Add user approval before mutating commands.
- Add domain allowlists for `fetch_url`.
- Store memory in a scoped database with audit logs.
- Add structured tool-output schemas for easier policy checks.
