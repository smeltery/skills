#!/usr/bin/env python3
"""Validate asset provenance and report uninventoried local UI assets."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


ASSET_SUFFIXES = {
    ".avif", ".eot", ".gif", ".ico", ".jpeg", ".jpg", ".otf", ".png",
    ".svg", ".ttf", ".webp", ".woff", ".woff2",
}
SKIP_DIRS = {".git", ".ui-studio", "node_modules", "dist", "build", ".next"}


def discover(root: Path) -> set[str]:
    found: set[str] = set()
    for current, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in SKIP_DIRS]
        for name in files:
            path = Path(current) / name
            if path.suffix.lower() in ASSET_SUFFIXES:
                found.add(path.relative_to(root).as_posix())
    return found


def check(root: Path, inventory: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    recorded: set[str] = set()
    for asset in inventory.get("assets", []):
        if not isinstance(asset, dict):
            issues.append("inventory asset must be an object")
            continue
        raw = asset.get("path")
        if not isinstance(raw, str):
            issues.append("inventory asset requires a path")
            continue
        if raw in recorded:
            issues.append(f"duplicate inventory path: {raw}")
        recorded.add(raw)
        if asset.get("kind") != "dependency" and not (root / raw).is_file():
            issues.append(f"inventoried asset is missing: {raw}")
        license_file = asset.get("licenseFile")
        if isinstance(license_file, str) and not (root / license_file).is_file():
            issues.append(f"license file is missing for {raw}: {license_file}")
        for field in ("source", "license", "rightsMode"):
            if not asset.get(field):
                issues.append(f"{raw}: missing {field}")
    discovered = discover(root)
    missing = sorted(discovered - recorded)
    issues.extend(f"asset lacks provenance: {path}" for path in missing)
    return {
        "valid": not issues,
        "inventoried": len(recorded),
        "discovered": len(discovered),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        if not isinstance(inventory, dict):
            raise ValueError("inventory root must be an object")
        report = check(args.root.expanduser().resolve(), inventory)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    elif report["issues"]:
        for issue in report["issues"]:
            print(f"ERROR {issue}")
    else:
        print(f"OK    {report['inventoried']} asset provenance record(s)")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
