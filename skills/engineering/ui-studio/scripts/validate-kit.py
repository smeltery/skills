#!/usr/bin/env python3
"""Validate UI Studio state and kit manifests without third-party packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATHS = {
    "state": SKILL_DIR / "schemas" / "state.schema.json",
    "manifest": SKILL_DIR / "schemas" / "ui-kit.schema.json",
}
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", ".cache"}


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: str) -> bool:
    actual = json_type(value)
    if expected == "number":
        return actual in {"integer", "number"}
    return actual == expected


def validate(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']!r}")

    expected = schema.get("type")
    if expected is not None:
        expected_types = [expected] if isinstance(expected, str) else expected
        if not any(type_matches(value, item) for item in expected_types):
            errors.append(
                f"{path}: expected {' or '.join(expected_types)}, got {json_type(value)}"
            )
            return errors

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: must not be empty")
        pattern = schema.get("pattern")
        if pattern and not re.search(pattern, value):
            errors.append(f"{path}: {value!r} does not match {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: must be >= {schema['minimum']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: requires at least {schema['minItems']} item(s)")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(validate(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        if len(value) < schema.get("minProperties", 0):
            errors.append(
                f"{path}: requires at least {schema['minProperties']} properties"
            )
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property {key!r}")

        properties = schema.get("properties", {})
        extra_schema = schema.get("additionalProperties", True)
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(validate(item, properties[key], child_path))
            elif extra_schema is False:
                errors.append(f"{child_path}: additional property is not allowed")
            elif isinstance(extra_schema, dict):
                errors.extend(validate(item, extra_schema, child_path))

    return errors


def walk_named(root: Path, names: set[str]) -> list[Path]:
    matches: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(item for item in dirs if item not in SKIP_DIRS)
        for name in sorted(names.intersection(files)):
            matches.append(Path(current) / name)
    return matches


def infer_kind(path: Path, data: dict[str, Any]) -> str | None:
    if path.name == "ui-kit.json":
        return "manifest"
    if path.name == "state.json" or {"phase", "generatedFiles"}.issubset(data):
        return "state"
    if {"entryPoints", "commands", "hosting"}.issubset(data):
        return "manifest"
    return None


def load_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"{path}: {error}"]
    if not isinstance(value, dict):
        return None, [f"{path}: root must be a JSON object"]
    return value, []


def check_paths(path: Path, data: dict[str, Any], kind: str) -> list[str]:
    errors: list[str] = []
    if kind == "manifest":
        candidates: list[tuple[str, str]] = []
        for key, value in data.get("entryPoints", {}).items():
            if isinstance(value, str):
                candidates.append((f"entryPoints.{key}", value))
        for key in ("sourceLedger", "designDecision", "critiqueReport"):
            value = data.get(key)
            if isinstance(value, str):
                candidates.append((key, value))
        for label, raw in candidates:
            if "://" in raw or raw.startswith("#"):
                continue
            candidate = (path.parent / raw).resolve()
            if not candidate.exists():
                errors.append(f"{path}: {label} does not exist: {raw}")

    if kind == "state":
        target_raw = data.get("targetPath")
        if not isinstance(target_raw, str) or not target_raw:
            return errors
        target = Path(target_raw).expanduser().resolve()
        for raw, expected in data.get("generatedFiles", {}).items():
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = target / candidate
            if not candidate.is_file():
                errors.append(f"{path}: generated file is missing: {raw}")
                continue
            actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual != expected:
                errors.append(f"{path}: generated file changed outside state: {raw}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="JSON file or search root")
    parser.add_argument("--schema", choices=sorted(SCHEMA_PATHS))
    parser.add_argument(
        "--check-files",
        action="store_true",
        help="verify manifest paths and generated-file hashes",
    )
    args = parser.parse_args()

    schema_cache = {
        key: json.loads(value.read_text(encoding="utf-8"))
        for key, value in SCHEMA_PATHS.items()
    }
    inputs: list[Path] = []
    for raw in args.paths:
        path = raw.expanduser().resolve()
        if path.is_dir():
            inputs.extend(walk_named(path, {"ui-kit.json", "state.json"}))
        else:
            inputs.append(path)

    inputs = sorted(set(inputs))
    if not inputs:
        print("No ui-kit.json or state.json files found.", file=sys.stderr)
        return 1

    failed = False
    for path in inputs:
        data, errors = load_json(path)
        kind = args.schema or (infer_kind(path, data) if data else None)
        if data is not None and kind is None:
            errors.append(f"{path}: cannot infer schema; pass --schema")
        if data is not None and kind is not None:
            errors.extend(validate(data, schema_cache[kind]))
            if args.check_files:
                errors.extend(check_paths(path, data, kind))
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR {error}")
        else:
            print(f"OK    {path} ({kind})")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
