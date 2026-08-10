#!/usr/bin/env python3
"""Record explicitly approved screenshot hashes and detect visual drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def dimensions(path: Path) -> tuple[int | None, int | None]:
    data = path.read_bytes()[:24]
    if path.suffix.lower() == ".png" and data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    return None, None


def inventory(root: Path) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.suffix.lower() not in SUFFIXES:
            continue
        width, height = dimensions(path)
        files[path.relative_to(root).as_posix()] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size,
            "width": width,
            "height": height,
        }
    if not files:
        raise ValueError(f"no screenshots found beneath {root}")
    return files


def compare(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    old = expected.get("files", {})
    added = sorted(set(actual) - set(old))
    removed = sorted(set(old) - set(actual))
    changed = sorted(
        key for key in set(old) & set(actual)
        if old[key].get("sha256") != actual[key].get("sha256")
    )
    return {"matches": not (added or removed or changed), "added": added, "removed": removed, "changed": changed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    record = subparsers.add_parser("approve")
    record.add_argument("screenshots", type=Path)
    record.add_argument("output", type=Path)
    record.add_argument("--kit", required=True)
    record.add_argument("--version", required=True)
    record.add_argument("--rationale", required=True)
    record.add_argument("--approve", action="store_true", required=True)
    check = subparsers.add_parser("compare")
    check.add_argument("baseline", type=Path)
    check.add_argument("screenshots", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "approve":
            files = inventory(args.screenshots.expanduser().resolve())
            value = {
                "schemaVersion": 1,
                "kit": args.kit,
                "version": args.version,
                "approvedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "rationale": args.rationale,
                "files": files,
            }
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
            print(f"Approved {len(files)} visual baseline(s): {args.output}")
            return 0
        expected = json.loads(args.baseline.read_text(encoding="utf-8"))
        report = compare(expected, inventory(args.screenshots.expanduser().resolve()))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
