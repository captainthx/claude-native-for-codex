# Claude Native for Codex

Use Claude Code from Codex through Claude's native CLI and background-agent lifecycle.

## What you get

| Workflow | App | Codex |
| --- | --- | --- |
| Review | `@claude:review` | `$claude:review` |
| Adversarial review | `@claude:adversarial-review` | `$claude:adversarial-review` |
| Delegate | `@claude:delegate` | `$claude:delegate` |
| Status | `@claude:status` | `$claude:status` |
| Result | `@claude:result` | `$claude:result` |
| Cancel | `@claude:cancel` | `$claude:cancel` |
| Resume | `@claude:resume` | `$claude:resume` |

The plugin does not run its own daemon or job database. Claude Code remains the source of truth for permissions, sessions, logs, and worktrees.

## Requirements

- Codex with plugin support
- Claude Code 2.1.206 or newer
- Git
- An authenticated Claude Code account or configured provider

Check Claude before installing:

```bash
claude --version
claude auth status
```

## Install from a checkout

From this repository root:

```bash
codex plugin marketplace add .
codex plugin add claude@claude-native-for-codex
```

Start a new Codex task after installation.

Codex also accepts a public GitHub `owner/repo` slug or HTTPS Git URL as the marketplace source.

## Usage

```text
@claude:delegate แล้วใช้ security-review หน่อย opus นะ

$claude:review
$claude:review --base main
$claude:adversarial-review --base main inspect race conditions and rollback safety
$claude:delegate investigate the flaky integration test
$claude:delegate implement the Codex plan above
$claude:delegate --model opus --effort high implement the Codex plan above
$claude:status
$claude:result 7c5dcf5d
$claude:cancel 7c5dcf5d
$claude:resume 7c5dcf5d summarize the final changes
```

`$claude:delegate` defaults to Sonnet at high effort and starts Claude Code with `--permission-mode auto`. Use `--model` and/or `--effort` before the task to override one delegated session.

Delegated work uses Claude's native background supervisor. If Auto mode blocks a session repeatedly, attach for exceptional recovery:

```bash
claude attach 7c5dcf5d
```

## Safety

- Reviews use plan mode and expose only read-only tools.
- Delegate uses Claude Code Auto mode; its classifier can still deny risky actions.
- Cancel stops one exact session and does not delete transcripts or worktrees.
- The plugin never enables a permission-bypass mode.

## Development

Run the deterministic validation:

```bash
python3 tests/validate.py
```

The validator uses only Python's standard library. CI does not invoke Claude or consume quota.

## Manual release smoke test

Use a disposable Git repository and verify:

1. Both review skills leave `git status --short` unchanged.
2. Delegate returns a native short ID visible in `$claude:status`.
3. Result returns native output.
4. Cancel stops one running session.
5. Resume continues a completed session in foreground.

## License

MIT
