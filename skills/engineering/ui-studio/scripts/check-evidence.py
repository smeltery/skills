#!/usr/bin/env python3
"""Check UI Studio evidence age and locally verifiable source revisions."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_time(raw: str) -> datetime:
    value = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def local_fingerprint(path: Path) -> str | None:
    if path.is_file():
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return None


def repository_revision(path: Path) -> str | None:
    if not path.is_dir():
        return None
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def inspect_source(source: dict[str, Any], root: Path, max_age: int) -> list[str]:
    issues: list[str] = []
    label = source.get("id", "unknown")
    try:
        captured = parse_time(source["capturedAt"])
        age = (datetime.now(timezone.utc) - captured).total_seconds() / 86400
        if age < -(5 / 1440):
            issues.append(f"{label}: capturedAt is in the future")
        if age > max_age:
            issues.append(f"{label}: evidence is {age:.1f} days old (limit {max_age})")
    except (KeyError, TypeError, ValueError) as error:
        issues.append(f"{label}: invalid capturedAt: {error}")

    raw = source.get("source")
    if not isinstance(raw, str) or "://" in raw:
        return issues
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    expected_fingerprint = source.get("contentFingerprint")
    actual_fingerprint = local_fingerprint(path)
    if expected_fingerprint and actual_fingerprint and expected_fingerprint != actual_fingerprint:
        issues.append(f"{label}: local content fingerprint changed")
    expected_revision = source.get("revision")
    actual_revision = repository_revision(path)
    if expected_revision and actual_revision and expected_revision != actual_revision:
        issues.append(f"{label}: repository revision changed to {actual_revision}")
    if not path.exists():
        issues.append(f"{label}: local source no longer exists: {path}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--max-age-days", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        path = args.evidence.expanduser().resolve()
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
            raise ValueError("evidence root must contain a sources array")
        max_age = args.max_age_days
        if max_age is None:
            max_age = data.get("maxAgeDays", 30)
        if not isinstance(max_age, int) or max_age < 0:
            raise ValueError("max age must be a non-negative integer")
        issues = [
            issue
            for source in data.get("sources", [])
            for issue in inspect_source(source, path.parent, max_age)
        ]
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    report = {
        "fresh": not issues,
        "issues": issues,
        "sourceCount": len(data.get("sources", [])),
    }
    if args.json:
        print(json.dumps(report, indent=2))
    elif issues:
        for issue in issues:
            print(f"STALE {issue}")
    else:
        print(f"OK    {report['sourceCount']} source(s) are within the freshness contract")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
