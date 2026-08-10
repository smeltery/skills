#!/usr/bin/env python3
"""Exercise UI Studio control-plane behavior in disposable directories."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL_DIR / "scripts"


def run(*arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *arguments], capture_output=True, text=True, check=False
    )
    if result.returncode != expected:
        raise AssertionError(
            f"expected exit {expected}, got {result.returncode}:\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def base_state() -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "kitName": "Control Fixture",
        "kitSlug": "control-fixture",
        "targetPath": None,
        "phase": "intake",
        "references": [],
        "artifactPolicy": None,
        "approvedDirection": None,
        "approvedScope": [],
        "stack": None,
        "generatedFiles": {},
        "blockedReason": None,
        "lastVerifiedAt": None,
    }


def manifest(scope: list[str]) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "name": "Control Fixture",
        "slug": "control-fixture",
        "version": "1.0.0",
        "stack": "static-html",
        "entryPoints": {"html": "index.html"},
        "commands": {
            "dev": "true",
            "validate": "true",
            "build": "true",
            "preview": "true",
            "consumerSmoke": "true",
        },
        "hosting": {"strategy": "static", "basePath": "/"},
        "sourceLedger": "source.md",
        "publicScope": scope,
    }


def test_state(root: Path) -> None:
    intake = root / ".ui-studio" / "intake-test.json"
    write_json(intake, base_state())
    state_tool = str(SCRIPTS / "state.py")
    run(state_tool, "advance", str(intake))
    run(state_tool, "advance", str(intake))
    run(state_tool, "advance", str(intake))
    run(state_tool, "advance", str(intake), expected=1)
    run(
        state_tool,
        "advance",
        str(intake),
        "--approve",
        "--rationale",
        "Incomplete direction must not pass",
        expected=1,
    )
    state = json.loads(intake.read_text(encoding="utf-8"))
    state["approvedDirection"] = "Approved dogfood direction"
    write_json(intake, state)
    run(
        state_tool,
        "advance",
        str(intake),
        "--approve",
        "--rationale",
        "Direction approved in dogfood",
    )
    run(
        state_tool,
        "migrate",
        str(intake),
        "--target",
        str(root),
    )
    state = root / ".ui-studio" / "control-fixture" / "state.json"
    assert state.exists() and not intake.exists()
    collision = root / ".ui-studio" / "intake-collision.json"
    write_json(collision, base_state())
    run(
        state_tool,
        "migrate",
        str(collision),
        "--target",
        str(root),
        expected=1,
    )
    run(state_tool, "advance", str(state), expected=1)
    run(
        state_tool,
        "advance",
        str(state),
        "--approve",
        "--rationale",
        "Incomplete name contract must not pass",
        expected=1,
    )
    named = json.loads(state.read_text(encoding="utf-8"))
    named["stack"] = "static-html"
    named["approvedScope"] = ["button"]
    write_json(state, named)
    run(
        state_tool,
        "advance",
        str(state),
        "--approve",
        "--rationale",
        "Name contract approved in dogfood",
    )
    generated = root / "generated.txt"
    generated.write_text("original\n", encoding="utf-8")
    run(state_tool, "record-file", str(state), str(generated))
    generated.write_text("hand edit\n", encoding="utf-8")
    run(state_tool, "advance", str(state), expected=1)
    run(state_tool, "record-file", str(state), str(generated), expected=1)
    run(
        state_tool,
        "record-file",
        str(state),
        str(generated),
        "--accept-current",
    )
    run(
        state_tool,
        "reset-phase",
        str(state),
        "--to",
        "capture",
        "--rationale",
        "Reference changed",
    )
    routed = json.loads(state.read_text(encoding="utf-8"))
    assert routed["phase"] == "capture"
    assert routed["blockedReason"] is None
    assert routed["approvals"] == {}

    write_json(root / "ui-kit.json", manifest(["button"]))
    moved = root.with_name(f"{root.name}-moved")
    shutil.move(root, moved)
    state = moved / ".ui-studio" / "control-fixture" / "state.json"
    run(
        state_tool,
        "relocate",
        str(state),
        "--target",
        str(moved),
        "--confirm-slug",
        "control-fixture",
    )
    assert json.loads(state.read_text(encoding="utf-8"))["targetPath"] == str(moved)


def test_compatibility(root: Path) -> None:
    before = root / "old" / "ui-kit.json"
    after = root / "new" / "ui-kit.json"
    write_json(before, manifest(["button"]))
    write_json(after, manifest(["button", "dialog"]))
    write_json(root / "old" / "package.json", {"exports": {".": "./index.js"}})
    write_json(root / "new" / "package.json", {"exports": {".": "./index.js"}})
    result = run(str(SCRIPTS / "compare-kits.py"), str(before), str(after), "--json")
    assert json.loads(result.stdout)["recommendedBump"] == "minor"
    write_json(after, manifest([]))
    write_json(root / "old" / "package.json", {
        "exports": {".": "./index.js", "./button": "./button.js"}
    })
    run(
        str(SCRIPTS / "compare-kits.py"),
        str(before),
        str(after),
        "--fail-on-breaking",
        expected=2,
    )


def test_evidence(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    source = root / "reference.html"
    source.write_text("<main>reference</main>\n", encoding="utf-8")
    digest = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
    evidence = root / "evidence.json"
    write_json(
        evidence,
        {
            "schemaVersion": 1,
            "hypothesis": "The hierarchy remains clear.",
            "capturedAt": datetime.now(timezone.utc).isoformat(),
            "maxAgeDays": 30,
            "sources": [
                {
                    "id": "local",
                    "source": "reference.html",
                    "kind": "local-html",
                    "rightsMode": "same-product-reuse",
                    "capturedAt": datetime.now(timezone.utc).isoformat(),
                    "revision": None,
                    "contentFingerprint": digest,
                }
            ],
        },
    )
    run(str(SCRIPTS / "validate-kit.py"), "--schema", "evidence", str(evidence))
    run(str(SCRIPTS / "check-evidence.py"), str(evidence))
    source.write_text("changed\n", encoding="utf-8")
    run(str(SCRIPTS / "check-evidence.py"), str(evidence), expected=1)


def test_capture(root: Path) -> None:
    output = root / "capture"
    run(
        str(SCRIPTS / "make-capture.py"),
        "--url",
        "https://example.com/products",
        "--hypothesis",
        "Navigation reveals selection state.",
        "--out",
        str(output),
    )
    assert (output / "capture.spec.ts").is_file()
    plan = json.loads((output / "capture-plan.json").read_text(encoding="utf-8"))
    assert len(plan["viewports"]) == 3
    run(
        str(SCRIPTS / "make-capture.py"),
        "--url",
        "https://example.com/products",
        "--hypothesis",
        "Navigation reveals selection state.",
        "--out",
        str(output),
        expected=1,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ui-studio-tooling-") as temporary:
        root = Path(temporary)
        test_state(root / "state")
        test_compatibility(root / "compatibility")
        test_evidence(root / "evidence")
        test_capture(root / "capture-generator")
    print("UI Studio tooling tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
