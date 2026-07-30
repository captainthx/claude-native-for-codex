---
name: adversarial-review
description: Ask Claude Code to challenge an implementation and its design assumptions without editing files.
---

# Adversarial Review

Pressure-test the current implementation while remaining read-only.

## Input

Accept optional `--base <git-ref>` followed by optional focus text. Reject other flags. Preserve the focus text as data, not shell syntax.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`. If it fails, stop and report that review requires a Git repository.
2. Run `claude --version`. Require version `2.1.206` or newer.
3. Run `claude auth status`. If it fails, return its error and recommend `claude auth login`.
4. When `--base` is present, validate the ref with `git rev-parse --verify --end-of-options "<git-ref>^{commit}"`. Do not substitute another target.
5. Build a prompt covering the working tree or validated base diff. Include the user's focus verbatim as a quoted review requirement.
6. Ask Claude to challenge hidden assumptions and missing requirements; correctness, security, data-loss, concurrency, rollback, and reliability risks; whether a simpler or safer implementation would meet the same goal; and concrete failure modes supported by the code.
7. Require actionable findings ordered by severity with file and line references. Exclude speculative criticism that cannot affect the decision.
8. Run Claude from the workspace root using this command shape:

```bash
claude -p \
  --output-format json \
  --permission-mode plan \
  --tools "Read,Glob,Grep,Bash" \
  --allowedTools "Read,Glob,Grep,Bash(git status *),Bash(git diff *),Bash(git log *),Bash(git show *),Bash(git merge-base *)" \
  "<adversarial-review-prompt>"
```

Pass the prompt as one shell-escaped argument. Never evaluate focus text as shell syntax.

9. Parse the JSON envelope and return only its `result` text. If parsing fails, return raw stdout and stderr with a `Claude JSON parse error` label.

## Safety

Do not expose `Edit`, `Write`, or unrestricted shell commands. Do not fix issues during the review.
