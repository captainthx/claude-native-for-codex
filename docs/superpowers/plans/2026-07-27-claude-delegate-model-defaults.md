# Claude Delegate Model Defaults Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start delegated Claude Code sessions with Sonnet at high effort by default, while allowing per-session model and effort overrides.

**Architecture:** Keep the plugin declarative: `$claude-delegate` parses its documented flags and invokes the native Claude CLI with either defaults or supplied values. `$claude-resume` deliberately preserves the native session model; users change it through `claude attach` and `/model` when needed. The existing standard-library validator protects these contract strings.

**Tech Stack:** Codex plugin Markdown skills, Python 3 standard library validation, GitHub Actions.

## Global Constraints

- Default delegate model is exactly `sonnet`; default effort is exactly `high`.
- `$claude-delegate` accepts only `--model <alias-or-name>` and `--effort <low|medium|high|xhigh|max>` before one non-empty task.
- Reject repeated flags, missing values, invalid effort values, unknown flags, and an empty task before running Claude.
- Treat model, effort, and task inputs as shell-escaped data; never evaluate them as shell syntax.
- Do not create a model config file, wrapper process, job database, or plugin-owned handoff session.
- `$claude-resume` must not advertise model or effort overrides; its native session retains the original model.
- Preserve the existing Git-root, version, authentication, exact-ID, and permission-policy safeguards.
- Use only the Python standard library and existing project dependencies.

---

## File structure

- Modify `plugins/claude-native-for-codex/skills/claude-delegate/SKILL.md`: define the input grammar, defaults, validation, and native command shape.
- Modify `plugins/claude-native-for-codex/skills/claude-resume/SKILL.md`: state why model/effort flags are intentionally unsupported and give the native `/model` recovery path.
- Modify `README.md`: document default and override examples, plus the plan-to-delegate workflow.
- Modify `tests/validate.py`: validate all new public skill contract tokens deterministically.

### Task 1: Lock the public contract in the validator

**Files:**

- Modify: `tests/validate.py:16-35`
- Modify: `tests/validate.py:70-92`

**Interfaces:**

- Consumes: the `EXPECTED_SKILLS` mapping and current `check_skills()` loop.
- Produces: validation failures when the delegate defaults, accepted flags, input rejection rules, or resume limitation are removed from skill text.

- [ ] **Step 1: Write the failing contract assertions**

Add these exact strings to the `claude-delegate` tuple in `EXPECTED_SKILLS`:

```python
"--model <alias-or-name>",
"--effort <low|medium|high|xhigh|max>",
"claude --bg --model sonnet --effort high",
"Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task",
```

After the review-specific assertion block in `check_skills()`, add:

```python
resume = read_text(skills_root / "claude-resume" / "SKILL.md")
assert "does not accept model or effort flags" in resume
assert "claude attach <short-id>" in resume
assert "/model <alias-or-name>" in resume
```

- [ ] **Step 2: Run validation to verify it fails**

Run: `python3 tests/validate.py`

Expected: `FAIL: skills` because the unmodified delegate and resume skill text does not contain the new contract strings.

- [ ] **Step 3: Keep the validator minimal**

Do not add a test framework, subprocess calls, or a Claude invocation. The existing validator reads package files only; the new string assertions belong in its existing `check_skills()` function.

- [ ] **Step 4: Commit the failing-contract test**

```bash
git add tests/validate.py
git commit -m "test: define delegate model defaults contract"
```

### Task 2: Document native delegate defaults and resume boundary

**Files:**

- Modify: `plugins/claude-native-for-codex/skills/claude-delegate/SKILL.md:8-31`
- Modify: `plugins/claude-native-for-codex/skills/claude-resume/SKILL.md:8-37`

**Interfaces:**

- Consumes: the contract asserted by Task 1 and native Claude CLI `--model`, `--effort`, and `--bg` flags.
- Produces: `$claude-delegate [--model <alias-or-name>] [--effort <low|medium|high|xhigh|max>] <task>` and an explicit no-override rule for `$claude-resume`.

- [ ] **Step 1: Replace delegate input wording with the exact grammar**

Replace the current `## Input` paragraph with:

````markdown
## Input

Accept `$claude-delegate [--model <alias-or-name>] [--effort <low|medium|high|xhigh|max>] <task>`. Flags may appear in either order before the task. Default to `--model sonnet --effort high`. Require one non-empty task after parsing flags. Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task before running Claude. Treat every value as prompt data, not shell syntax.
````

- [ ] **Step 2: Replace the delegate launch instruction and command block**

Replace the current background launch step with:

````markdown
4. Parse the optional flags. Use `sonnet` when `--model` is absent and `high` when `--effort` is absent.
5. From the workspace root run:

```bash
claude --bg --model "<model>" --effort "<effort>" "<task>"
```

Pass model, effort, and task as separate shell-escaped arguments. Never evaluate task text as shell syntax.

6. Return stdout verbatim. It contains the native short ID and management commands.
7. If the session later becomes blocked, direct the user to `$claude-status` and `claude attach <short-id>`.

With no flags, this is `claude --bg --model sonnet --effort high "<task>"`.
````

- [ ] **Step 3: Add the resume model boundary**

Append this subsection before `## Scope` in `claude-resume/SKILL.md`:

```markdown
## Model and effort

`$claude-resume` does not accept model or effort flags. Claude Code preserves the model selected by the saved session when resuming. To change it, direct the user to `claude attach <short-id>`, use `/model <alias-or-name>` there, then resume normally.
```

- [ ] **Step 4: Run validation to verify it passes**

Run: `python3 tests/validate.py`

Expected: exactly four lines beginning `PASS:` for package, skills, runtime policy, and docs and CI.

- [ ] **Step 5: Commit the skill behavior**

```bash
git add plugins/claude-native-for-codex/skills/claude-delegate/SKILL.md \
  plugins/claude-native-for-codex/skills/claude-resume/SKILL.md
git commit -m "feat: default Claude delegation to sonnet high"
```

### Task 3: Document the Codex-plan workflow

**Files:**

- Modify: `README.md:35-47`
- Modify: `tests/validate.py:118-126`

**Interfaces:**

- Consumes: the delegate syntax from Task 2 and the existing README validation function.
- Produces: copy-pasteable default and override commands, and a validator that prevents their removal.

- [ ] **Step 1: Add failing README assertions**

In `check_docs_and_ci()`, after the existing command assertions, add:

```python
assert "$claude-delegate --model opus --effort high" in readme
assert "Sonnet at high effort" in readme
```

- [ ] **Step 2: Run validation to verify it fails**

Run: `python3 tests/validate.py`

Expected: `FAIL: docs and CI` because the README does not yet describe defaults or an override.

- [ ] **Step 3: Extend the usage example block**

Insert these lines after the existing `$claude-delegate investigate ...` example:

```text
$claude-delegate implement the Codex plan above
$claude-delegate --model opus --effort high implement the Codex plan above
```

Add this paragraph immediately below that block:

```markdown
`$claude-delegate` defaults to Sonnet at high effort. Use `--model` and/or `--effort` before the task to override one delegated session. A resumed session retains its original model; to switch it, run `claude attach <short-id>`, use `/model`, then resume it.
```

- [ ] **Step 4: Run the complete deterministic validation**

Run: `python3 tests/validate.py`

Expected:

```text
PASS: package
PASS: skills
PASS: runtime policy
PASS: docs and CI
```

- [ ] **Step 5: Commit the user-facing documentation and check**

```bash
git add README.md tests/validate.py
git commit -m "docs: explain Claude delegate model overrides"
```

### Task 4: Final verification

**Files:**

- Verify: `README.md`
- Verify: `plugins/claude-native-for-codex/skills/claude-delegate/SKILL.md`
- Verify: `plugins/claude-native-for-codex/skills/claude-resume/SKILL.md`
- Verify: `tests/validate.py`

**Interfaces:**

- Consumes: the three previous commits.
- Produces: a clean, validated repository ready for optional manual Claude CLI smoke testing.

- [ ] **Step 1: Run the project validator**

Run: `python3 tests/validate.py`

Expected: the four `PASS:` lines from Task 3.

- [ ] **Step 2: Inspect committed changes**

Run: `git diff --check HEAD~3..HEAD && git status --short`

Expected: no whitespace errors and no worktree changes.

- [ ] **Step 3: Keep native Claude smoke testing optional**

Do not call `claude` during automated verification because it requires authentication and may consume quota. If the user requests it, manually verify a disposable Git repository with:

```bash
claude --bg --model sonnet --effort high "return the current Git branch without changing files"
```

Confirm the command prints a native short ID; stop that exact ID afterward with `claude stop "<short-id>"`.
