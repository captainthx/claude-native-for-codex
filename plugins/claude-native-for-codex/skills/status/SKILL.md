---
name: status
description: Show native Claude Code background sessions for the current Git workspace.
---

# Status

List Claude-managed sessions without reading plugin-owned state.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`. If it fails, stop and report that status is scoped by Git workspace.
2. Run:

```bash
claude agents --json --all --cwd "<workspace-root>"
```

3. Parse the JSON array and render one row per background session with short `id`, `name`, `state`, `startedAt`, and `waitingFor` when present.
4. Preserve the native states `working`, `blocked`, `done`, `failed`, and `stopped`.
5. When no rows match, return `No Claude background sessions for this workspace.`
6. For a blocked session, recommend `claude attach <short-id>`.

Return malformed JSON as raw stdout and stderr with a `Claude agents JSON parse error` label.
