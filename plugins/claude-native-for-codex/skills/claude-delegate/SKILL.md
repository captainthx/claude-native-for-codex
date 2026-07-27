---
name: claude-delegate
description: Delegate an investigation or implementation task to a native Claude Code background session.
---

# Claude Delegate

Start one Claude-managed background session and return its native ID.

## Input

Require a non-empty task after the skill name. Treat the entire task as prompt data.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`. If it fails, stop: delegation requires Git so Claude can apply native worktree isolation.
2. Run `claude --version`. Require version `2.1.206` or newer.
3. Run `claude auth status`. If it fails, return its error and recommend `claude auth login`.
4. From the workspace root run:

```bash
claude --bg "<task>"
```

Pass the task as one shell-escaped argument. Never evaluate task text as shell syntax.

5. Return stdout verbatim. It contains the native short ID and management commands.
6. If the session later becomes blocked, direct the user to `$claude-status` and `claude attach <short-id>`.

## Safety

Do not override Claude's effective permission mode. Do not launch a wrapper process, store a PID, create plugin-owned logs, or create a second worktree.
