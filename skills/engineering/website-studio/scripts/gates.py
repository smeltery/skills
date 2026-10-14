#!/usr/bin/env python3
"""Ordered website evidence receipts. Does not judge visual or test quality."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timezone

CHECKS = {
    "context": ["brief", "baseline", "scope"],
    "references": ["observations", "source-review", "translation"],
    "direction": ["thesis", "tokens", "composition"],
    "structure": ["routes", "content", "journeys"],
    "build": ["runnable", "complete", "maintainable"],
    "journeys": ["navigation", "primary-flow", "adverse-states"],
    "responsive": ["viewports", "reflow", "input-modes"],
    "accessibility": ["semantics", "keyboard", "audit"],
    "discovery": ["metadata", "assets", "crawl"],
    "performance": ["budgets", "measurements", "regressions"],
    "critique": ["visual-review", "consistency", "repairs"],
    "delivery": ["reproducible", "scope-complete", "handoff"],
}
GATES = list(CHECKS)
RUNTIME_GATES = GATES[GATES.index("build"):]
SKIP_DIRS = {
    ".git", ".website-studio", "node_modules", "dist", "build", ".next",
    ".astro", ".cache", ".venv", "venv", "__pycache__", "coverage",
    "test-results", "playwright-report",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    """Hash inputs, including untracked assets, without generated output or secrets."""
    files = {}
    for directory, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(names):
            path = Path(directory) / name
            if name.startswith(".env") or path.suffix in {".pem", ".key"}:
                continue
            if name == ".DS_Store" or path.suffix in {".pyc", ".log"}:
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                files[relative] = "link:" + os.readlink(path)
            else:
                files[relative] = digest(path)
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def evidence_path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Evidence paths must be nonempty strings")
    path = (root / value).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Evidence must be an existing file inside the project: {value}")
    if path.name == "state.json" or not path.stat().st_size:
        raise ValueError(f"Evidence cannot be empty or the state file: {value}")
    return path


def validate_report(root, report):
    if not isinstance(report, dict) or report.get("gate") not in CHECKS:
        raise ValueError("Report needs a known gate")
    gate = report["gate"]
    checks = report.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(CHECKS[gate]):
        raise ValueError(f"{gate} needs exactly these checks: {', '.join(CHECKS[gate])}")
    if report.get("issues") != []:
        raise ValueError("Report must contain issues: [] after required issues are resolved")
    evidence = {}
    for name, check in checks.items():
        if not isinstance(check, dict) or check.get("result") != "pass":
            raise ValueError(f"{gate}/{name} has not passed")
        if not isinstance(check.get("note"), str) or not check["note"].strip():
            raise ValueError(f"{gate}/{name} needs a factual note")
        paths = check.get("evidence")
        if not isinstance(paths, list) or not paths:
            raise ValueError(f"{gate}/{name} needs evidence files")
        for value in paths:
            path = evidence_path(root, value)
            evidence[path.relative_to(root).as_posix()] = digest(path)
    return evidence


def save(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            json.dump(state, file, indent=2)
            file.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load(path, root):
    state = json.loads(path.read_text())
    if not isinstance(state, dict) or state.get("version") != 1 or state.get("root") != str(root):
        raise ValueError("State version or project root does not match; inspect before recovery")
    receipts = state.get("receipts")
    if not isinstance(receipts, dict) or list(receipts) != GATES[:len(receipts)]:
        raise ValueError("State receipts must be an ordered gate prefix")
    if any(not isinstance(receipt, dict) for receipt in receipts.values()):
        raise ValueError("State receipts must be objects")
    return state


def next_gate(root, state):
    current_snapshot = None
    for gate in GATES:
        receipt = state["receipts"].get(gate)
        if receipt is None:
            return gate, "pending"
        try:
            report_path = evidence_path(root, receipt["report"])
            if digest(report_path) != receipt["reportHash"]:
                return gate, "report changed"
            report = json.loads(report_path.read_text())
            evidence = validate_report(root, report)
            if report["gate"] != gate:
                return gate, "receipt refers to a different gate"
            if evidence != receipt["evidence"]:
                return gate, "evidence changed"
            if gate in RUNTIME_GATES:
                if current_snapshot is None:
                    current_snapshot = snapshot(root)
                if receipt["sourceHash"] != current_snapshot:
                    return gate, "project inputs changed; rebuild and verify"
        except (OSError, ValueError, KeyError, TypeError) as error:
            return gate, f"invalid evidence: {error}"
    return None, "complete"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "status", "pass", "invalidate"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--gate", choices=GATES)
    parser.add_argument("--reason")
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Project root must be a directory")
    path = root / ".website-studio" / "state.json"
    if args.command == "init" and not path.exists():
        save(path, {"version": 1, "root": str(root), "receipts": {}})
    state = load(path, root)
    gate, reason = next_gate(root, state)
    if args.command == "invalidate":
        if not args.gate or not args.reason or not args.reason.strip():
            raise ValueError("invalidate requires --gate and --reason")
        keep = GATES[:GATES.index(args.gate)]
        state["receipts"] = {k: v for k, v in state["receipts"].items() if k in keep}
        state["lastInvalidation"] = {"gate": args.gate, "reason": args.reason}
        save(path, state)
    elif args.command == "pass":
        if not args.report:
            raise ValueError("pass requires --report (relative to project root or absolute)")
        report_path = evidence_path(root, str(args.report))
        report = json.loads(report_path.read_text())
        evidence = validate_report(root, report)
        requested = report["gate"]
        # Repeated identical receipts are a no-op only while all prior gates hold.
        prior = state["receipts"].get(requested)
        if prior and (gate is None or GATES.index(requested) < GATES.index(gate)):
            if digest(report_path) == prior["reportHash"]:
                print(f"{requested}: already passed")
                return 0
        if requested != gate:
            raise ValueError(f"Next gate is {gate or 'complete'}, not {requested}")
        keep = GATES[:GATES.index(gate)]
        state["receipts"] = {k: v for k, v in state["receipts"].items() if k in keep}
        state["receipts"][gate] = {
            "report": report_path.relative_to(root).as_posix(),
            "reportHash": digest(report_path), "evidence": evidence,
            "sourceHash": snapshot(root) if gate in RUNTIME_GATES else None,
            "verifiedAt": datetime.now(timezone.utc).isoformat(),
        }
        save(path, state)
    gate, reason = next_gate(root, state)
    print(json.dumps({"next": gate, "reason": reason, "state": str(path)}))
    return 1 if args.command == "status" and reason not in {"pending", "complete"} else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Gate error: {error}", file=sys.stderr)
        sys.exit(1)
