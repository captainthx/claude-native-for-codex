# Claude delegate model defaults

## Goal

Let Codex hand its written plan to Claude Code for implementation with a predictable default: Sonnet at high effort. Permit a per-delegation override without adding plugin-owned session state.

## Interface

`$claude-delegate` accepts:

```text
$claude-delegate [--model <alias-or-name>] [--effort <low|medium|high|xhigh|max>] <task>
```

- With no flags, it runs `claude --bg --model sonnet --effort high "<task>"`.
- With either flag, that value overrides only the new Claude session.
- The task remains one shell-escaped prompt argument.
- Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task before running Claude.

## Resume

`$claude-resume` keeps its existing interface and continues the selected session with its saved model and effort. It does not accept model or effort flags.

Claude Code preserves a resumed session's model even when startup model configuration changes. A user who must change it attaches to the native session and uses `/model <alias-or-name>`, then may use `$claude-resume` normally afterward.

## Boundaries

- Do not add a model configuration file, wrapper process, job database, or handoff session.
- Do not change default models outside this plugin invocation.
- Preserve all current Git-root, Claude version, authentication, exact-ID, and permission-policy checks.

## Verification

Extend the standard-library validator to assert the delegate defaults and accepted override command tokens, and that resume does not advertise a model override. Run `python3 tests/validate.py`.
