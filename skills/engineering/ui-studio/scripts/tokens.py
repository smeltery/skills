#!/usr/bin/env python3
"""Validate, flatten, or expand DTCG-compatible design-token JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("token root must be an object")
    return value


def walk(group: dict[str, Any], prefix: str = "", inherited_type: str | None = None) -> tuple[dict[str, dict[str, Any]], list[str]]:
    flattened: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    group_type = group.get("$type", inherited_type)
    for key, value in group.items():
        if key.startswith("$"):
            continue
        name = f"{prefix}.{key}" if prefix else key
        if not isinstance(value, dict):
            issues.append(f"{name}: token or group must be an object")
            continue
        if "$value" in value:
            token_type = value.get("$type", group_type)
            if not token_type:
                issues.append(f"{name}: token requires $type or inherited group $type")
                continue
            flattened[name] = {"$type": token_type, "$value": value["$value"]}
            if "$description" in value:
                flattened[name]["$description"] = value["$description"]
        else:
            nested, nested_issues = walk(value, name, value.get("$type", group_type))
            flattened.update(nested)
            issues.extend(nested_issues)
    if not prefix and not flattened:
        issues.append("token document contains no tokens")
    return flattened, issues


def expand(flattened: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for name, token in flattened.items():
        if not isinstance(name, str) or not name or not isinstance(token, dict):
            raise ValueError("flat tokens must map dotted names to token objects")
        if "$value" not in token or "$type" not in token:
            raise ValueError(f"{name}: flat token requires $value and $type")
        cursor = output
        parts = name.split(".")
        for part in parts[:-1]:
            child = cursor.setdefault(part, {})
            if not isinstance(child, dict) or "$value" in child:
                raise ValueError(f"{name}: group collides with a token")
            cursor = child
        if parts[-1] in cursor:
            raise ValueError(f"duplicate token path: {name}")
        cursor[parts[-1]] = token
    return output


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("input", type=Path)
    flatten_parser = subparsers.add_parser("flatten")
    flatten_parser.add_argument("input", type=Path)
    flatten_parser.add_argument("output", type=Path)
    expand_parser = subparsers.add_parser("expand")
    expand_parser.add_argument("input", type=Path)
    expand_parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        data = load(args.input)
        if args.command == "expand":
            write(args.output, expand(data))
            print(f"Expanded tokens to {args.output}")
            return 0
        flattened, issues = walk(data)
        if issues:
            raise ValueError("invalid tokens:\n  " + "\n  ".join(issues))
        if args.command == "flatten":
            write(args.output, flattened)
            print(f"Flattened {len(flattened)} token(s) to {args.output}")
        else:
            print(f"OK    {len(flattened)} DTCG-compatible token(s)")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
