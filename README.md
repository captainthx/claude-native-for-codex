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

## Install

Install from GitHub:

```bash
codex plugin marketplace add captainthx/claude-native-for-codex
codex plugin add claude@claude-native-for-codex
```

Start a new Codex task after installation.

For local development, run `codex plugin marketplace add .` from this repository root instead.

To update an existing installation:

```bash
codex plugin marketplace upgrade claude-native-for-codex
```

## Usage

```text
@claude:delegate --model opus แล้วใช้ security-review หน่อย

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

## Releases and discovery

Installing from this public GitHub repository works now. A GitHub release is optional: it gives users a changelog and a stable version marker, but the marketplace installs the repository's selected Git ref.

For each release, update the version in `plugins/claude-native-for-codex/.codex-plugin/plugin.json`, validate it, then tag and publish it:

```bash
python3 tests/validate.py
git tag v0.2.0
git push origin main --tags
gh release create v0.2.0 --generate-notes
```

To be searchable in the public Plugins Directory shared by ChatGPT and Codex, submit this skills-only plugin through the [OpenAI plugin submission portal](https://platform.openai.com/plugins). Before submitting, prepare a verified developer identity, Apps Management write access, a logo, public website/support/privacy-policy/terms URLs, five positive and three negative test cases, and release notes. OpenAI review and publication are required; making the GitHub repository public alone does not add it to that directory. See the [official submission guide](https://developers.openai.com/plugins/deploy/submission).

## License

MIT
