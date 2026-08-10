#!/usr/bin/env python3
"""Compare reusable UI kit manifests and classify compatibility impact."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent


def load_validator() -> Any:
    path = SKILL_DIR / "scripts" / "validate-kit.py"
    spec = importlib.util.spec_from_file_location("ui_studio_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    schema = json.loads(
        (SKILL_DIR / "schemas" / "ui-kit.schema.json").read_text(encoding="utf-8")
    )
    errors = load_validator().validate(data, schema)
    if errors:
        raise ValueError(f"{path}: invalid manifest:\n  " + "\n  ".join(errors))
    return data


def key_changes(
    before: dict[str, Any], after: dict[str, Any], field: str
) -> tuple[list[str], list[str], list[str]]:
    old = before.get(field, {})
    new = after.get(field, {})
    if isinstance(old, list):
        old = {item: item for item in old}
    if isinstance(new, list):
        new = {item: item for item in new}
    if not isinstance(old, dict) or not isinstance(new, dict):
        return [], [], [field] if old != new else []
    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    changed = sorted(key for key in set(old) & set(new) if old[key] != new[key])
    return removed, added, changed


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    breaking: list[str] = []
    additive: list[str] = []
    changed: list[str] = []
    for field in ("entryPoints", "publicScope", "themes", "peerDependencies"):
        removed, added, modified = key_changes(before, after, field)
        breaking.extend(f"{field}: removed {item}" for item in removed)
        if field == "peerDependencies":
            breaking.extend(f"{field}: added required {item}" for item in added)
        else:
            additive.extend(f"{field}: added {item}" for item in added)
        if field in {"entryPoints", "peerDependencies"}:
            breaking.extend(f"{field}: changed {item}" for item in modified)
        else:
            changed.extend(f"{field}: changed {item}" for item in modified)
    for field in ("slug", "stack"):
        if before.get(field) != after.get(field):
            breaking.append(f"{field}: {before.get(field)!r} -> {after.get(field)!r}")
    if before.get("hosting", {}).get("basePath") != after.get("hosting", {}).get("basePath"):
        breaking.append("hosting.basePath changed")
    recommendation = "major" if breaking else "minor" if additive else "patch"
    return {
        "compatible": not breaking,
        "recommendedBump": recommendation,
        "breaking": breaking,
        "additive": additive,
        "changed": changed,
    }


def package_exports(path: Path) -> Any:
    package_path = path.parent / "package.json"
    if not package_path.is_file():
        return {}
    package = json.loads(package_path.read_text(encoding="utf-8"))
    return package.get("exports", {}) if isinstance(package, dict) else {}


def add_package_export_changes(
    report: dict[str, Any], before_path: Path, after_path: Path
) -> None:
    before = {"packageExports": package_exports(before_path)}
    after = {"packageExports": package_exports(after_path)}
    removed, added, changed = key_changes(before, after, "packageExports")
    report["breaking"].extend(f"packageExports: removed {item}" for item in removed)
    report["breaking"].extend(f"packageExports: changed {item}" for item in changed)
    report["additive"].extend(f"packageExports: added {item}" for item in added)
    if report["breaking"]:
        report["compatible"] = False
        report["recommendedBump"] = "major"
    elif report["additive"]:
        report["recommendedBump"] = "minor"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-breaking", action="store_true")
    args = parser.parse_args()
    try:
        report = compare(load(args.before), load(args.after))
        add_package_export_changes(report, args.before, args.after)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Compatibility: {'compatible' if report['compatible'] else 'breaking'}")
        print(f"Recommended version bump: {report['recommendedBump']}")
        for category in ("breaking", "additive", "changed"):
            for item in report[category]:
                print(f"{category.upper():8} {item}")
    return 2 if args.fail_on_breaking and report["breaking"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
