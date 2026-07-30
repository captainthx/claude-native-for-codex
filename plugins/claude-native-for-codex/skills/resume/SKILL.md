---
name: resume
description: Continue a native Claude Code session in foreground print mode.
---

# Resume

Resolve a native session and return its follow-up answer directly to Codex.

## Input

Require a short session ID or full session UUID followed by non-empty follow-up text.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`.
2. Run `claude --version`; require version `2.1.206` or newer.
3. Run `claude auth status`; on failure recommend `claude auth login`.
4. Query:

```bash
claude agents --json --all --cwd "<workspace-root>"
```

5. If input is a short ID, require one exact `id` match and read its `sessionId`.
6. If input is a full UUID, use it as the session ID. Do not use fuzzy name search.
7. Run from the workspace root:

```bash
claude -p \
  --output-format json \
  --resume "<session-id>" \
  "<follow-up>"
```

Pass the session ID and follow-up as separate shell-escaped arguments. Never evaluate follow-up text as shell syntax.

8. Parse the JSON envelope and return only its `result` text. If parsing fails, return raw stdout and stderr with a `Claude JSON parse error` label.

## Model and effort

`$claude:resume` does not accept model or effort flags. Claude Code preserves the model selected by the saved session when resuming. To change it, direct the user to `claude attach <short-id>`, use `/model <alias-or-name>` there, then resume normally.

## Scope

Resume runs in foreground for version `0.2.0`. Do not add background continuation or a plugin-owned session record.
