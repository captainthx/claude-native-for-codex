# Claude Native for Codex

Use Claude Code from Codex through Claude's native CLI and background-agent lifecycle.

## What you get

- `$claude-review`
- `$claude-adversarial-review`
- `$claude-delegate`
- `$claude-status`
- `$claude-result`
- `$claude-cancel`
- `$claude-resume`

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
codex plugin add claude-native-for-codex@claude-native-for-codex
```

Start a new Codex task after installation.

Codex also accepts a public GitHub `owner/repo` slug or HTTPS Git URL as the marketplace source.

## Usage

```text
$claude-review
$claude-review --base main
$claude-adversarial-review --base main inspect race conditions and rollback safety
$claude-delegate investigate the flaky integration test
$claude-status
$claude-result 7c5dcf5d
$claude-cancel 7c5dcf5d
$claude-resume 7c5dcf5d summarize the final changes
```

Delegated work uses Claude's native background supervisor. If a session is blocked on input or permission, run:

```bash
claude attach 7c5dcf5d
```

## Safety

- Reviews use plan mode and expose only read-only tools.
- Delegate preserves your effective Claude permission policy.
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
2. Delegate returns a native short ID visible in `$claude-status`.
3. Result returns native output.
4. Cancel stops one running session.
5. Resume continues a completed session in foreground.

## License

MIT
