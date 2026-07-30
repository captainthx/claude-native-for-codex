# Claude Short Invocation and Auto Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose the seven workflows as `@claude:<skill>` in the app and `$claude:<skill>` in Codex, while launching delegated background sessions in Claude Code Auto mode.

**Architecture:** Keep the plugin skills-only and declarative. Rename the installed plugin identity and skill folders/frontmatter in place, add one native Claude CLI flag to delegate, and extend the existing standard-library validator before changing implementation or documentation.

**Tech Stack:** Codex plugin JSON, Markdown skills, Python 3 standard library, native Claude Code CLI

## Global Constraints

- Manifest plugin name and marketplace plugin entry name: `claude`.
- Plugin display name: `Claude`.
- Plugin version: `0.2.0`.
- Top-level marketplace source name and repository directory remain `claude-native-for-codex`.
- App invocation uses `@claude:<skill>`; Codex invocation uses `$claude:<skill>`.
- Keep exactly seven skills: `review`, `adversarial-review`, `delegate`, `status`, `result`, `cancel`, and `resume`.
- Delegate uses `--permission-mode auto` as fixed behavior.
- Do not add permission configuration, a manual retry, a bypass mode, old-name aliases, a wrapper runtime, or model-consuming automated tests.

---

## File Structure

- `.agents/plugins/marketplace.json`: Keep marketplace source identity and path; rename its single plugin entry to `claude`.
- `plugins/claude-native-for-codex/.codex-plugin/plugin.json`: Set installed identity, version, and display name.
- `plugins/claude-native-for-codex/skills/*/SKILL.md`: Rename all seven folders/frontmatter entries and update active cross-skill invocations.
- `plugins/claude-native-for-codex/skills/delegate/SKILL.md`: Add fixed Claude Code Auto mode to the native background launch.
- `tests/validate.py`: Define and enforce the renamed package, skill set, and Auto-mode contract.
- `README.md`: Document installation plus app and Codex invocation forms.

### Task 1: Rename the Runtime Contract and Enable Auto Mode

**Files:**
- Modify: `tests/validate.py:8-128`
- Modify: `.agents/plugins/marketplace.json`
- Modify: `plugins/claude-native-for-codex/.codex-plugin/plugin.json`
- Move: `plugins/claude-native-for-codex/skills/claude-review/` to `plugins/claude-native-for-codex/skills/review/`
- Move: `plugins/claude-native-for-codex/skills/claude-adversarial-review/` to `plugins/claude-native-for-codex/skills/adversarial-review/`
- Move: `plugins/claude-native-for-codex/skills/claude-delegate/` to `plugins/claude-native-for-codex/skills/delegate/`
- Move: `plugins/claude-native-for-codex/skills/claude-status/` to `plugins/claude-native-for-codex/skills/status/`
- Move: `plugins/claude-native-for-codex/skills/claude-result/` to `plugins/claude-native-for-codex/skills/result/`
- Move: `plugins/claude-native-for-codex/skills/claude-cancel/` to `plugins/claude-native-for-codex/skills/cancel/`
- Move: `plugins/claude-native-for-codex/skills/claude-resume/` to `plugins/claude-native-for-codex/skills/resume/`

**Interfaces:**
- Consumes: Existing plugin directory `plugins/claude-native-for-codex` and Claude CLI version floor `2.1.206`.
- Produces: Installed namespace `claude`; seven exact skill names; delegate command `claude --bg --permission-mode auto --model "<model>" --effort "<effort>" "<task>"`.

- [ ] **Step 1: Change the validator to the new package and skill contract**

Replace the identity and skill constants with:

```python
EXPECTED_MARKETPLACE_NAME = "claude-native-for-codex"
EXPECTED_NAME = "claude"
EXPECTED_VERSION = "0.2.0"
EXPECTED_SKILLS = {
    "review": (
        "claude -p",
        "--output-format json",
        "--permission-mode plan",
        "--tools",
    ),
    "adversarial-review": (
        "claude -p",
        "--output-format json",
        "--permission-mode plan",
        "--tools",
    ),
    "delegate": (
        "claude --bg --permission-mode auto",
        "--model <alias-or-name>",
        "--effort <low|medium|high|xhigh|max>",
        "claude --bg --permission-mode auto --model sonnet --effort high",
        "Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task",
    ),
    "status": ("claude agents --json --all --cwd",),
    "result": ("claude logs",),
    "cancel": ("claude stop",),
    "resume": (
        "claude agents --json --all --cwd",
        "claude -p",
        "--resume",
    ),
}
```

Update `check_package()` to require:

```python
assert marketplace["name"] == EXPECTED_MARKETPLACE_NAME
assert marketplace["interface"]["displayName"] == "Claude Native for Codex"
assert entry["name"] == EXPECTED_NAME
assert manifest["name"] == EXPECTED_NAME
assert manifest["version"] == EXPECTED_VERSION
assert manifest["interface"]["displayName"] == "Claude"
```

Update the specialized skill lookups:

```python
for review_name in ("review", "adversarial-review"):
    text = read_text(skills_root / review_name / "SKILL.md")
    assert "Do not expose `Edit`, `Write`" in text

resume = read_text(skills_root / "resume" / "SKILL.md")
```

- [ ] **Step 2: Run the validator and verify the new contract fails**

Run:

```bash
python3 tests/validate.py
```

Expected: non-zero with failures for package identity and skill set mismatch because the manifest and folders still use the old names.

- [ ] **Step 3: Update the manifest and marketplace plugin entry**

In `.agents/plugins/marketplace.json`, change only `plugins[0].name`:

```json
{
  "name": "claude-native-for-codex",
  "interface": {
    "displayName": "Claude Native for Codex"
  },
  "plugins": [
    {
      "name": "claude",
      "source": {
        "source": "local",
        "path": "./plugins/claude-native-for-codex"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

In the plugin manifest, set:

```json
{
  "name": "claude",
  "version": "0.2.0",
  "interface": {
    "displayName": "Claude"
  }
}
```

Preserve every other manifest field and value.

- [ ] **Step 4: Rename all seven skill directories**

Run:

```bash
git mv plugins/claude-native-for-codex/skills/claude-review plugins/claude-native-for-codex/skills/review
git mv plugins/claude-native-for-codex/skills/claude-adversarial-review plugins/claude-native-for-codex/skills/adversarial-review
git mv plugins/claude-native-for-codex/skills/claude-delegate plugins/claude-native-for-codex/skills/delegate
git mv plugins/claude-native-for-codex/skills/claude-status plugins/claude-native-for-codex/skills/status
git mv plugins/claude-native-for-codex/skills/claude-result plugins/claude-native-for-codex/skills/result
git mv plugins/claude-native-for-codex/skills/claude-cancel plugins/claude-native-for-codex/skills/cancel
git mv plugins/claude-native-for-codex/skills/claude-resume plugins/claude-native-for-codex/skills/resume
```

- [ ] **Step 5: Update skill frontmatter, headings, and cross-skill names**

Apply these exact name and heading pairs:

```text
review              -> name: review              / # Review
adversarial-review  -> name: adversarial-review  / # Adversarial Review
delegate            -> name: delegate            / # Delegate
status              -> name: status              / # Status
result              -> name: result              / # Result
cancel              -> name: cancel              / # Cancel
resume              -> name: resume              / # Resume
```

Replace active invocations inside skill instructions:

```text
$claude-adversarial-review -> $claude:adversarial-review
$claude-delegate           -> $claude:delegate
$claude-status             -> $claude:status
$claude-resume             -> $claude:resume
```

Do not rewrite historical design or plan documents.

- [ ] **Step 6: Add fixed Auto mode to delegate**

In `skills/delegate/SKILL.md`, make the command block:

```bash
claude --bg --permission-mode auto --model "<model>" --effort "<effort>" "<task>"
```

Make the no-flag example:

```text
With no flags, this is `claude --bg --permission-mode auto --model sonnet --effort high "<task>"`.
```

Replace the obsolete instruction not to override the effective permission mode with:

```text
Use Auto mode only. Do not weaken or replace Claude's permission checks. Do not launch a wrapper process, store a PID, create plugin-owned logs, or create a second worktree.
```

- [ ] **Step 7: Run the focused validator and active-skill scan**

Run:

```bash
python3 tests/validate.py
rg -n '\$claude-|name: claude-|skills/claude-' plugins/claude-native-for-codex tests/validate.py
```

Expected: the validator still passes its existing README assertions; the scan prints no matches.

- [ ] **Step 8: Commit the runtime contract**

```bash
git add .agents/plugins/marketplace.json plugins/claude-native-for-codex tests/validate.py
git commit -m "feat: shorten Claude skills and enable auto mode"
```

### Task 2: Document and Validate Both Invocation Surfaces

**Files:**
- Modify: `tests/validate.py:140-152`
- Modify: `README.md`

**Interfaces:**
- Consumes: Installed namespace `claude` and the seven skill names produced by Task 1.
- Produces: Install command `codex plugin add claude@claude-native-for-codex` and complete app/Codex invocation documentation.

- [ ] **Step 1: Replace README assertions with the new public interface**

Update `check_docs_and_ci()` to contain:

```python
assert "Claude Code 2.1.206" in readme
assert "codex plugin marketplace add ." in readme
assert "codex plugin add claude@claude-native-for-codex" in readme
assert "python3 tests/validate.py" in readme
for name in EXPECTED_SKILLS:
    assert f"@claude:{name}" in readme
    assert f"$claude:{name}" in readme
assert "$claude-" not in readme
assert "claude-native-for-codex@claude-native-for-codex" not in readme
assert "--permission-mode auto" in readme
assert "Sonnet at high effort" in readme
assert "python3 tests/validate.py" in workflow
```

- [ ] **Step 2: Run the validator and verify README coverage fails**

Run:

```bash
python3 tests/validate.py
```

Expected: non-zero in `docs and CI` because README still documents the old installation and skill names.

- [ ] **Step 3: Replace the workflow list with an invocation table**

Under `## What you get`, document all seven rows:

```markdown
| Workflow | App | Codex |
| --- | --- | --- |
| Review | `@claude:review` | `$claude:review` |
| Adversarial review | `@claude:adversarial-review` | `$claude:adversarial-review` |
| Delegate | `@claude:delegate` | `$claude:delegate` |
| Status | `@claude:status` | `$claude:status` |
| Result | `@claude:result` | `$claude:result` |
| Cancel | `@claude:cancel` | `$claude:cancel` |
| Resume | `@claude:resume` | `$claude:resume` |
```

- [ ] **Step 4: Update install, examples, permission behavior, and smoke-test references**

Use this install command:

```bash
codex plugin add claude@claude-native-for-codex
```

Change every active Codex example to the `$claude:<skill>` form. Add this app example before the Codex examples:

```text
@claude:delegate แล้วใช้ security-review หน่อย opus นะ
```

Describe delegate behavior with:

```markdown
`$claude:delegate` defaults to Sonnet at high effort and starts Claude Code with `--permission-mode auto`. Use `--model` and/or `--effort` before the task to override one delegated session.
```

Replace the delegate safety bullet with:

```markdown
- Delegate uses Claude Code Auto mode; its classifier can still deny risky actions.
```

Keep `claude attach <short-id>` only as exceptional recovery when Auto mode blocks repeatedly. Update the manual smoke-test status reference to `$claude:status`.

- [ ] **Step 5: Run complete deterministic verification**

Run:

```bash
python3 tests/validate.py
git diff --check
rg -n '\$claude-|claude-native-for-codex@claude-native-for-codex' README.md plugins/claude-native-for-codex
```

Expected:

```text
PASS: package
PASS: skills
PASS: runtime policy
PASS: docs and CI
```

The final scan prints no matches.

- [ ] **Step 6: Commit documentation and verification**

```bash
git add README.md tests/validate.py
git commit -m "docs: explain short Claude invocations"
```

- [ ] **Step 7: Verify final repository state**

Run:

```bash
python3 tests/validate.py
git status --short
git log -3 --oneline
```

Expected: all four checks pass, the worktree is clean, and the latest two implementation commits are the runtime change followed by the documentation change.
