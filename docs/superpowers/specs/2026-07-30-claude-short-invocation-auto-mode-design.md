# Claude Short Invocation and Auto Mode Design

**Date:** 2026-07-30

## Goal

Shorten every installed plugin skill to the `claude:<skill>` namespace and let delegated Claude Code sessions handle ordinary permissions without requiring the user to attach to the background session.

## Public Interface

Change the plugin manifest name from `claude-native-for-codex` to `claude`, its display name to `Claude`, and its version from `0.1.0` to `0.2.0`.

Rename the skills as follows:

| Current skill | New skill | App invocation | Codex invocation |
| --- | --- | --- | --- |
| `claude-review` | `review` | `@claude:review` | `$claude:review` |
| `claude-adversarial-review` | `adversarial-review` | `@claude:adversarial-review` | `$claude:adversarial-review` |
| `claude-delegate` | `delegate` | `@claude:delegate` | `$claude:delegate` |
| `claude-status` | `status` | `@claude:status` | `$claude:status` |
| `claude-result` | `result` | `@claude:result` | `$claude:result` |
| `claude-cancel` | `cancel` | `@claude:cancel` | `$claude:cancel` |
| `claude-resume` | `resume` | `@claude:resume` | `$claude:resume` |

This is an intentional breaking rename. Do not retain duplicate compatibility skills or aliases. Change the marketplace plugin entry name to `claude` so it matches the manifest. The top-level marketplace source name and repository directory remain `claude-native-for-codex`.

The install command becomes:

```bash
codex plugin add claude@claude-native-for-codex
```

## Delegate Behavior

Keep the existing delegate arguments, Sonnet/high defaults, validation, Git-root check, authentication check, and native background lifecycle.

Launch the native session with:

```bash
claude --bg --permission-mode auto --model "<model>" --effort "<effort>" "<task>"
```

`auto` is fixed behavior rather than a new user-facing flag. The plugin must not retry in manual mode and must not use `bypassPermissions`. If Claude Code rejects Auto mode because the account, model, provider, or organization policy does not support it, return the native error without starting a less-protected session.

Auto mode can still deny risky actions or eventually pause after repeated denials. Existing `status` and native `claude attach <short-id>` recovery remain available for those exceptional sessions, but ordinary delegated implementation should no longer stop for each edit or shell command.

## Documentation and Validation

Update the README, manifest validation, expected skill list, folder names, frontmatter names, headings, cross-skill references, examples, and install instructions to use the new names.

The deterministic validator must assert:

- Manifest and marketplace plugin entry name `claude`, display name `Claude`, and version `0.2.0`.
- Exactly the seven renamed skill directories and matching frontmatter names.
- Delegate includes `--permission-mode auto`.
- No skill or documentation advertises a permission bypass.
- README uses the new install and invocation syntax.

Run the existing standard-library validator. Do not invoke Claude during automated tests or consume model quota.

## Out of Scope

- Permission-mode flags or configuration.
- Compatibility aliases for the old skill names.
- A plugin-owned approval relay, daemon, job database, or session wrapper.
- Automatic fallback when Auto mode is unavailable.
