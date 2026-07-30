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

    assert marketplace["name"] == EXPECTED_MARKETPLACE_NAME
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
    assert manifest["version"] == EXPECTED_VERSION
    assert manifest["skills"] == "./skills/"
    assert manifest["license"] == "MIT"
    assert manifest["interface"]["displayName"] == "Claude"
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

    delegate = read_text(skills_root / "delegate" / "SKILL.md")
    permission_modes = re.findall(r"--permission-mode\s+(\S+)", delegate)
    assert permission_modes and all(mode == "auto" for mode in permission_modes), (
        f"delegate permission modes must all be auto: {permission_modes}"
    )

    for review_name in ("review", "adversarial-review"):
        text = read_text(skills_root / review_name / "SKILL.md")
        assert "Do not expose `Edit`, `Write`" in text

    resume = read_text(skills_root / "resume" / "SKILL.md")
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
