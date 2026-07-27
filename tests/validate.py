#!/usr/bin/env python3

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"
PLUGIN = ROOT / "plugins/claude-native-for-codex"
MANIFEST = PLUGIN / ".codex-plugin/plugin.json"
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github/workflows/validate.yml"
EXPECTED_NAME = "claude-native-for-codex"
EXPECTED_SKILLS = {
    "claude-review": (
        "claude -p",
        "--output-format json",
        "--permission-mode plan",
        "--tools",
    ),
    "claude-adversarial-review": (
        "claude -p",
        "--output-format json",
        "--permission-mode plan",
        "--tools",
    ),
    "claude-delegate": (
        "claude --bg",
        "--model <alias-or-name>",
        "--effort <low|medium|high|xhigh|max>",
        "claude --bg --model sonnet --effort high",
        "Reject repeated flags, missing values, unknown flags, invalid effort values, and an empty task",
    ),
    "claude-status": ("claude agents --json --all --cwd",),
    "claude-result": ("claude logs",),
    "claude-cancel": ("claude stop",),
    "claude-resume": (
        "claude agents --json --all --cwd",
        "claude -p",
        "--resume",
    ),
}
BANNED_SKILL_TEXT = (
    "bypasspermissions",
    "dangerously-skip-permissions",
    "allow-dangerously-skip-permissions",
)


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def frontmatter_name(text: str) -> str:
    match = re.match(r"\A---\n(?P<header>.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise AssertionError("invalid or missing YAML frontmatter")
    name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", match.group("header"))
    if not name:
        raise AssertionError("frontmatter missing name")
    return name.group(1)


def check_package() -> None:
    marketplace = load_json(MARKETPLACE)
    manifest = load_json(MANIFEST)

    assert marketplace["name"] == EXPECTED_NAME
    assert marketplace["interface"]["displayName"] == "Claude Native for Codex"
    assert len(marketplace["plugins"]) == 1

    entry = marketplace["plugins"][0]
    assert entry["name"] == EXPECTED_NAME
    assert entry["source"] == {
        "source": "local",
        "path": "./plugins/claude-native-for-codex",
    }
    assert entry["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
    assert entry["category"] == "Productivity"

    assert manifest["name"] == EXPECTED_NAME
    assert manifest["version"] == "0.1.0"
    assert manifest["skills"] == "./skills/"
    assert manifest["license"] == "MIT"
    assert manifest["interface"]["displayName"] == "Claude Native for Codex"
    assert len(manifest["interface"]["defaultPrompt"]) <= 3
    assert (ROOT / "LICENSE").is_file()
    assert "apps" not in manifest
    assert "mcpServers" not in manifest


def check_skills() -> None:
    skills_root = PLUGIN / "skills"
    actual = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    assert actual == set(EXPECTED_SKILLS), (
        f"skill set mismatch: expected {sorted(EXPECTED_SKILLS)}, got {sorted(actual)}"
    )

    for name, required_tokens in EXPECTED_SKILLS.items():
        text = read_text(skills_root / name / "SKILL.md")
        assert frontmatter_name(text) == name
        for token in required_tokens:
            assert token in text, f"{name} missing command token: {token}"
        lowered = text.lower()
        for banned in BANNED_SKILL_TEXT:
            assert banned not in lowered, f"{name} contains banned permission text: {banned}"

    for review_name in ("claude-review", "claude-adversarial-review"):
        text = read_text(skills_root / review_name / "SKILL.md")
        assert "Do not expose `Edit`, `Write`" in text

    resume = read_text(skills_root / "claude-resume" / "SKILL.md")
    assert "does not accept model or effort flags" in resume
    assert "claude attach <short-id>" in resume
    assert "/model <alias-or-name>" in resume


def check_no_custom_runtime() -> None:
    forbidden_files = (
        ROOT / "package.json",
        PLUGIN / ".mcp.json",
        PLUGIN / ".app.json",
    )
    for path in forbidden_files:
        assert not path.exists(), f"unexpected runtime artifact: {path.relative_to(ROOT)}"

    for directory in ("scripts", "state", "logs"):
        path = PLUGIN / directory
        assert not path.exists(), f"unexpected runtime directory: {path.relative_to(ROOT)}"


def check_docs_and_ci() -> None:
    readme = read_text(README)
    workflow = read_text(WORKFLOW)
    assert "Claude Code 2.1.206" in readme
    assert "codex plugin marketplace add ." in readme
    assert "codex plugin add claude-native-for-codex@claude-native-for-codex" in readme
    assert "python3 tests/validate.py" in readme
    assert "$claude-delegate --model opus --effort high" in readme
    assert "Sonnet at high effort" in readme
    assert "python3 tests/validate.py" in workflow


def main() -> int:
    checks = (
        ("package", check_package),
        ("skills", check_skills),
        ("runtime policy", check_no_custom_runtime),
        ("docs and CI", check_docs_and_ci),
    )
    failures = []
    for label, check in checks:
        try:
            check()
            print(f"PASS: {label}")
        except (AssertionError, KeyError, json.JSONDecodeError) as error:
            failures.append((label, error))
            print(f"FAIL: {label}: {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
