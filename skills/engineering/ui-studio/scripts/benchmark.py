#!/usr/bin/env python3
"""Plan and evaluate evidence-backed UI Studio benchmark contracts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be an object")
    return data


def validate_suite(suite: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    seen: set[str] = set()
    scenarios = suite.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        return ["suite requires at least one scenario"]
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            issues.append("scenario must be an object")
            continue
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            issues.append("scenario requires a non-empty id")
        elif scenario_id in seen:
            issues.append(f"duplicate scenario id: {scenario_id}")
        else:
            seen.add(scenario_id)
        contracts = scenario.get("requiredContracts")
        if not isinstance(contracts, list) or not contracts:
            issues.append(f"{scenario_id}: requires at least one contract")
    return issues


def plan(suite: dict[str, Any]) -> dict[str, Any]:
    archetypes: dict[str, int] = {}
    pressures: set[str] = set()
    contract_count = 0
    for scenario in suite["scenarios"]:
        archetype = scenario["archetype"]
        archetypes[archetype] = archetypes.get(archetype, 0) + 1
        pressures.update(scenario["pressures"])
        contract_count += len(scenario["requiredContracts"])
    return {
        "suite": suite["name"],
        "scenarioCount": len(suite["scenarios"]),
        "contractCount": contract_count,
        "archetypes": archetypes,
        "pressures": sorted(pressures),
    }


def evaluate(suite: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    indexed = {
        (item.get("scenario"), item.get("contract")): item
        for item in results.get("results", [])
        if isinstance(item, dict)
    }
    failures: list[dict[str, str]] = []
    passes = 0
    for scenario in suite["scenarios"]:
        for contract in scenario["requiredContracts"]:
            item = indexed.get((scenario["id"], contract))
            if not item:
                failures.append({
                    "scenario": scenario["id"],
                    "contract": contract,
                    "reason": "missing result",
                })
                continue
            status = item.get("status")
            evidence = item.get("evidence")
            if status != "pass" or not isinstance(evidence, str) or not evidence:
                failures.append({
                    "scenario": scenario["id"],
                    "contract": contract,
                    "reason": f"status={status!r} requires evidence-backed pass",
                })
            else:
                passes += 1
    return {
        "suite": suite["name"],
        "passed": not failures,
        "contractsPassed": passes,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("suite", type=Path)
    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_parser.add_argument("suite", type=Path)
    evaluate_parser.add_argument("results", type=Path)
    args = parser.parse_args()
    try:
        suite = load_object(args.suite)
        issues = validate_suite(suite)
        if issues:
            raise ValueError("invalid suite:\n  " + "\n  ".join(issues))
        if args.command == "plan":
            report = plan(suite)
            exit_code = 0
        else:
            report = evaluate(suite, load_object(args.results))
            exit_code = 0 if report["passed"] else 1
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
