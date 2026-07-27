#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".agents/plugins/marketplace.json"
PLUGIN = ROOT / "plugins/claude-native-for-codex"
MANIFEST = PLUGIN / ".codex-plugin/plugin.json"
EXPECTED_NAME = "claude-native-for-codex"


def load_json(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


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
    assert "apps" not in manifest
    assert "mcpServers" not in manifest


def main() -> int:
    try:
        check_package()
    except (AssertionError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
