---
name: claude-result
description: Read the captured output of one native Claude Code background session.
---

# Claude Result

Return native Claude output without copying it into a plugin store.

## Input

Require exactly one native short session ID.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`.
2. Query `claude agents --json --all --cwd "<workspace-root>"`.
3. Require one exact `id` match. Never use prefix guessing. If no session matches, show the available workspace-scoped IDs.
4. Run:

```bash
claude logs "<short-id>"
```

5. If the session is `working` or `blocked`, report that state before the available output.
6. Return the captured output verbatim. For `blocked`, also recommend `claude attach <short-id>`.

Pass the ID as one shell-escaped argument.
