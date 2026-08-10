#!/usr/bin/env python3
"""Safely inspect and transition UI Studio workflow state."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
PHASES = [
    "intake",
    "capture",
    "synthesize",
    "direction-gate",
    "name-gate",
    "plan",
    "scaffold",
    "foundations",
    "components",
    "compositions",
    "showcase",
    "verify",
    "release-gate",
    "handoff",
    "iterate",
]
GATES = {"direction-gate", "name-gate", "release-gate"}


def load_validator() -> Any:
    path = SKILL_DIR / "scripts" / "validate-kit.py"
    spec = importlib.util.spec_from_file_location("ui_studio_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


def load_state(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read state: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("state root must be an object")
    validator = load_validator()
    schema = json.loads(
        (SKILL_DIR / "schemas" / "state.schema.json").read_text(encoding="utf-8")
    )
    errors = validator.validate(data, schema)
    if errors:
        raise ValueError("invalid state:\n  " + "\n  ".join(errors))
    return data


def artifact_issues(path: Path, state: dict[str, Any]) -> list[str]:
    validator = load_validator()
    return validator.check_paths(path, state, "state")


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=False) + "\n"
    descriptor, raw_temp = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temp = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def gate_issues(phase: str, state: dict[str, Any]) -> list[str]:
    if phase == "direction-gate":
        return [] if state.get("approvedDirection") else ["approvedDirection"]
    if phase == "name-gate":
        required = ("kitName", "kitSlug", "targetPath", "stack")
        missing = [field for field in required if not state.get(field)]
        if not state.get("approvedScope"):
            missing.append("approvedScope")
        return missing
    if phase == "release-gate":
        return [] if state.get("lastVerifiedAt") else ["lastVerifiedAt"]
    return []


def command_status(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    phase = state["phase"]
    next_phase = PHASES[PHASES.index(phase) + 1] if phase != PHASES[-1] else None
    result = {
        "state": str(args.state.resolve()),
        "phase": phase,
        "nextPhase": next_phase,
        "blockedReason": state.get("blockedReason"),
        "routeReason": state.get("routeReason"),
        "generatedFiles": len(state.get("generatedFiles", {})),
        "artifactIssues": artifact_issues(args.state, state),
        "approvals": sorted(state.get("approvals", {})),
    }
    print(json.dumps(result, indent=2) if args.json else "\n".join(
        f"{key}: {value}" for key, value in result.items()
    ))
    return 0


def command_advance(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    stale = artifact_issues(args.state, state)
    if stale:
        raise ValueError("stale generated artifacts:\n  " + "\n  ".join(stale))
    current = state["phase"]
    expected = PHASES[PHASES.index(current) + 1] if current != PHASES[-1] else None
    destination = args.to or expected
    if expected is None:
        raise ValueError("iterate is terminal; route explicitly with reset-phase")
    if destination != expected:
        raise ValueError(
            f"illegal transition {current!r} -> {destination!r}; expected {expected!r}"
        )
    if args.approve and current not in GATES:
        raise ValueError(f"{current!r} is not an approval gate")
    if current in GATES:
        incomplete = gate_issues(current, state)
        if incomplete:
            raise ValueError(
                f"{current!r} contract is incomplete: {', '.join(incomplete)}"
            )
        if not args.approve or not args.rationale:
            raise ValueError(
                f"leaving {current!r} requires --approve and a non-empty --rationale"
            )
        state.setdefault("approvals", {})[current] = {
            "approvedAt": utc_now(),
            "rationale": args.rationale,
        }
    state["phase"] = destination
    state["blockedReason"] = None
    state["routeReason"] = None
    atomic_write(args.state, state)
    load_state(args.state)
    print(f"Advanced {current} -> {destination}: {args.state}")
    return 0


def command_reset(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    current = state["phase"]
    if PHASES.index(args.to) > PHASES.index(current) and current != "iterate":
        raise ValueError("reset-phase may only route backward; use advance for forward movement")
    if not args.rationale:
        raise ValueError("reset-phase requires --rationale")
    state["phase"] = args.to
    state["blockedReason"] = None
    state["routeReason"] = f"Routed from {current}: {args.rationale}"
    approvals = state.setdefault("approvals", {})
    for gate in list(approvals):
        if gate in PHASES and PHASES.index(gate) >= PHASES.index(args.to):
            del approvals[gate]
    atomic_write(args.state, state)
    print(f"Routed {current} -> {args.to}: {args.state}")
    return 0


def target_root(state: dict[str, Any], state_path: Path) -> Path:
    raw = state.get("targetPath")
    if isinstance(raw, str) and raw:
        return Path(raw).expanduser().resolve()
    marker = state_path.resolve()
    for parent in marker.parents:
        if parent.name == ".ui-studio":
            return parent.parent
    raise ValueError("cannot resolve target root; set targetPath in state")


def command_record(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    root = target_root(state, args.state)
    candidate = args.file.expanduser().resolve()
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ValueError(f"generated file must be inside target {root}") from error
    if not candidate.is_file():
        raise ValueError(f"generated file does not exist: {candidate}")
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    key = relative.as_posix()
    previous = state.setdefault("generatedFiles", {}).get(key)
    if previous and previous != digest and not args.accept_current:
        raise ValueError(
            f"hand edit detected for {key}; inspect it, then use --accept-current to adopt"
        )
    state["generatedFiles"][key] = digest
    atomic_write(args.state, state)
    print(f"Recorded {key} sha256:{digest}")
    return 0


def command_migrate(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    if not state.get("kitSlug"):
        raise ValueError("state must have an approved kitSlug before migration")
    target = args.target.expanduser().resolve()
    destination = target / ".ui-studio" / state["kitSlug"] / "state.json"
    if destination.exists() and destination.resolve() != args.state.resolve():
        raise ValueError(f"destination state already exists: {destination}")
    state["targetPath"] = str(target)
    atomic_write(destination, state)
    if destination.resolve() != args.state.resolve():
        args.state.unlink()
        try:
            args.state.parent.rmdir()
        except OSError:
            pass
    print(f"Migrated state to {destination}")
    return 0


def command_relocate(args: argparse.Namespace) -> int:
    state = load_state(args.state)
    target = args.target.expanduser().resolve()
    manifest_path = target / "ui-kit.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot verify relocated target manifest: {error}") from error
    if not isinstance(manifest, dict):
        raise ValueError(f"relocated target manifest must be an object: {manifest_path}")
    validator = load_validator()
    schema = json.loads(
        (SKILL_DIR / "schemas" / "ui-kit.schema.json").read_text(encoding="utf-8")
    )
    errors = validator.validate(manifest, schema)
    if errors:
        raise ValueError("relocated target manifest is invalid:\n  " + "\n  ".join(errors))
    slug = state.get("kitSlug")
    if manifest.get("slug") != slug or args.confirm_slug != slug:
        raise ValueError(
            "relocated target and --confirm-slug must match the state's kitSlug"
        )
    state["targetPath"] = str(target)
    state["routeReason"] = f"Confirmed target relocation to {target}"
    atomic_write(args.state, state)
    print(f"Confirmed relocated target for {slug}: {target}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="show validated routing state")
    status.add_argument("state", type=Path)
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=command_status)

    advance = subparsers.add_parser("advance", help="advance exactly one legal phase")
    advance.add_argument("state", type=Path)
    advance.add_argument("--to", choices=PHASES)
    advance.add_argument("--approve", action="store_true")
    advance.add_argument("--rationale")
    advance.set_defaults(handler=command_advance)

    reset = subparsers.add_parser(
        "reset-phase", help="route to an invalidated phase"
    )
    reset.add_argument("state", type=Path)
    reset.add_argument("--to", choices=PHASES, required=True)
    reset.add_argument("--rationale", required=True)
    reset.set_defaults(handler=command_reset)

    record = subparsers.add_parser(
        "record-file", help="record or adopt a generated file"
    )
    record.add_argument("state", type=Path)
    record.add_argument("file", type=Path)
    record.add_argument("--accept-current", action="store_true")
    record.set_defaults(handler=command_record)

    migrate = subparsers.add_parser(
        "migrate", help="move intake state under a named target"
    )
    migrate.add_argument("state", type=Path)
    migrate.add_argument("--target", type=Path, required=True)
    migrate.set_defaults(handler=command_migrate)

    relocate = subparsers.add_parser(
        "relocate", help="confirm a moved target by matching its kit manifest"
    )
    relocate.add_argument("state", type=Path)
    relocate.add_argument("--target", type=Path, required=True)
    relocate.add_argument("--confirm-slug", required=True)
    relocate.set_defaults(handler=command_relocate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return args.handler(args)
    except ValueError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
