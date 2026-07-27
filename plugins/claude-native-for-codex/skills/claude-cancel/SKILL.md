---
name: claude-cancel
description: Stop one exact native Claude Code background session.
---

# Claude Cancel

Stop one session without deleting its transcript or worktree.

## Input

Require exactly one native short session ID.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`.
2. Query `claude agents --json --all --cwd "<workspace-root>"`.
3. Require one exact `id` match. Never guess or stop all sessions.
4. Run:

```bash
claude stop "<short-id>"
```

5. Return Claude's native response verbatim.

Do not run `claude rm`, stop the supervisor, delete a transcript, or remove a worktree.
