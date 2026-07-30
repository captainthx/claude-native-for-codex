---
name: review
description: Ask Claude Code for a read-only review of the working tree or a branch diff.
---

# Review

Run a findings-first Claude Code review without modifying files.

## Input

Accept either no arguments or exactly `--base <git-ref>`. Reject unknown flags and extra focus text; focused challenge reviews belong to `$claude:adversarial-review`.

## Procedure

1. Resolve the workspace root with `git rev-parse --show-toplevel`. If it fails, stop and report that review requires a Git repository.
2. Run `claude --version`. Require version `2.1.206` or newer.
3. Run `claude auth status`. If it fails, return its error and recommend `claude auth login`.
4. When `--base` is present, validate the ref with `git rev-parse --verify --end-of-options "<git-ref>^{commit}"`. Do not fall back to another ref.
5. Build a prompt that identifies either the current working tree, including staged, unstaged, and untracked files, or the branch diff against the validated base ref.
6. Require findings ordered by severity. Each finding must include a file and line reference, impact, and concise remediation. Omit style-only comments.
7. Run Claude from the workspace root using this command shape:

```bash
claude -p \
  --output-format json \
  --permission-mode plan \
  --tools "Read,Glob,Grep,Bash" \
  --allowedTools "Read,Glob,Grep,Bash(git status *),Bash(git diff *),Bash(git log *),Bash(git show *),Bash(git merge-base *)" \
  "<review-prompt>"
```

Pass the prompt as one shell-escaped argument. Never evaluate user input as shell syntax.

8. Parse the JSON envelope and return only its `result` text. If parsing fails, return raw stdout and stderr with a `Claude JSON parse error` label.

## Safety

Do not expose `Edit`, `Write`, or unrestricted shell commands. Do not make changes after receiving the review.
