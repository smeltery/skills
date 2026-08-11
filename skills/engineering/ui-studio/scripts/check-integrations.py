#!/usr/bin/env python3
"""Check semantic safety invariants for optional UI Studio providers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def check(plan: dict[str, Any], release: bool) -> list[str]:
    issues: list[str] = []
    paper = plan.get("paper", {})
    if paper.get("enabled") != (paper.get("mode") != "disabled"):
        issues.append("Paper enabled and mode are inconsistent")
    if paper.get("enabled") and not paper.get("fileIdentity"):
        issues.append("enabled Paper integration requires a resolved file identity")
    if paper.get("mode") == "read-only-reference":
        if paper.get("writeApproved") or paper.get("writeScope"):
            issues.append("read-only Paper mode cannot approve or scope writes")
    if paper.get("mode") == "collaborative-canvas" and paper.get("writeApproved"):
        if not paper.get("fileIdentity") or not paper.get("writeScope"):
            issues.append("approved Paper writes require file identity and write scope")
    if release and paper.get("enabled") and not paper.get("connectionVerified"):
        issues.append("enabled Paper integration was not connection-verified")
    if release and paper.get("mode") == "collaborative-canvas":
        if not paper.get("writeApproved"):
            issues.append("collaborative Paper mode lacks recorded write approval")

    refero = plan.get("refero", {})
    if refero.get("enabled") != (refero.get("mode") != "disabled"):
        issues.append("Refero enabled and mode are inconsistent")
    if refero.get("enabled"):
        if not refero.get("query"):
            issues.append("enabled Refero research requires a product question")
        limit = refero.get("resultLimit")
        if not isinstance(limit, int) or not 1 <= limit <= 12:
            issues.append("Refero resultLimit must be between 1 and 12")
        if len(refero.get("diversityDimensions", [])) < 2:
            issues.append("Refero research requires at least two diversity dimensions")
        if refero.get("rightsMode") != "inspiration-only":
            issues.append("Refero evidence must remain inspiration-only")
        if release and refero.get("mode") == "mcp" and not refero.get("connectionVerified"):
            issues.append("Refero MCP use was not connection-verified")

    ui_sh = plan.get("uiSh", {})
    if ui_sh.get("enabled") != (ui_sh.get("mode") != "disabled"):
        issues.append("ui.sh enabled and mode are inconsistent")
    if ui_sh.get("enabled") and not ui_sh.get("skills"):
        issues.append("enabled ui.sh integration requires at least one selected skill")
    if release and ui_sh.get("enabled") and not ui_sh.get("availabilityVerified"):
        issues.append("selected ui.sh skills were not verified in the active registry")
    if ui_sh.get("mode") == "existing-project-install" and not ui_sh.get("installApproved"):
        issues.append("project installation of ui.sh skills requires approval")
    if ui_sh.get("tokenHandling") != "user-only":
        issues.append("ui.sh installer token handling must remain user-only")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--release", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            raise ValueError("integration plan root must be an object")
        issues = check(plan, args.release)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    report = {"valid": not issues, "releaseMode": args.release, "issues": issues}
    if args.json:
        print(json.dumps(report, indent=2))
    elif issues:
        for issue in issues:
            print(f"ERROR {issue}")
    else:
        print("OK    optional provider integration invariants")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
