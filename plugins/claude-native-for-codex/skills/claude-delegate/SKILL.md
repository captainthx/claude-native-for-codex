---
name: claude-delegate
description: Delegate an investigation or implementation task to a native Claude Code background session.
---

# Claude Delegate

Start one Claude-managed background session and return its native ID.

## Input

Accept `$claude-delegate [--model <alias-or-name>] [--effort <low|medium|high|xhigh|max>] <task>`. Flags may appear in either order before the task. Default to `--model sonnet --effort high`. Require one non-empty task after parsing flags. Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task before running Claude. Treat every value as prompt data, not shell syntax.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`. If it fails, stop: delegation requires Git so Claude can apply native worktree isolation.
2. Run `claude --version`. Require version `2.1.206` or newer.
3. Run `claude auth status`. If it fails, return its error and recommend `claude auth login`.
4. Parse the optional flags. Use `sonnet` when `--model` is absent and `high` when `--effort` is absent.
5. From the workspace root run:

```bash
claude --bg --model "<model>" --effort "<effort>" "<task>"
```

With no flags, this is `claude --bg --model sonnet --effort high "<task>"`.

Pass model, effort, and task as separate shell-escaped arguments. Never evaluate task text as shell syntax.

6. Return stdout verbatim. It contains the native short ID and management commands.
7. If the session later becomes blocked, direct the user to `$claude-status` and `claude attach <short-id>`.

## Safety

Do not override Claude's effective permission mode. Do not launch a wrapper process, store a PID, create plugin-owned logs, or create a second worktree.
