#!/usr/bin/env python3
"""Check multiple UI kits for composition and runtime contract collisions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: manifest root must be an object")
    return data


def major(raw: str) -> str | None:
    if any(marker in raw for marker in (">", "<", "|", "*", "x", "X")):
        return None
    match = re.fullmatch(r"[~^]?([0-9]+)(?:\.[0-9]+)?(?:\.[0-9]+)?", raw.strip())
    return match.group(1) if match else None


def css_contract(path: Path, manifest: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    variables: dict[str, str] = {}
    globals_found: list[str] = []
    entries = manifest.get("entryPoints", {})
    if not isinstance(entries, dict):
        return variables, globals_found
    for label, raw in entries.items():
        if not isinstance(raw, str) or not (label in {"styles", "style", "css"} or raw.endswith(".css")):
            continue
        css_path = (path.parent / raw).resolve()
        if not css_path.is_file():
            continue
        css = re.sub(r"/\*.*?\*/", "", css_path.read_text(encoding="utf-8"), flags=re.S)
        variables.update(dict(re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}{]+)", css)))
        for selector_group in re.findall(r"([^{}]+)\{", css):
            for selector in selector_group.split(","):
                normalized = selector.strip()
                bare_elements = {
                    "a", "button", "dialog", "form", "h1", "h2", "h3", "img",
                    "input", "label", "li", "ol", "p", "select", "table", "textarea", "ul",
                }
                if (
                    normalized in {"*", "html", "body"}
                    or normalized in bare_elements
                    or normalized.startswith(("html ", "body "))
                ):
                    globals_found.append(normalized)
        for body in re.findall(r":root\s*\{([^}]*)\}", css, flags=re.S):
            declarations = [item.strip() for item in body.split(";") if item.strip()]
            if any(not item.startswith("--") for item in declarations):
                globals_found.append(":root(non-token declarations)")
    return variables, sorted(set(globals_found))


def analyze(paths: list[Path]) -> dict[str, Any]:
    loaded = [(path, load(path)) for path in paths]
    blockers: list[str] = []
    concerns: list[str] = []
    names: dict[str, Path] = {}
    slugs: dict[str, Path] = {}
    peers: dict[str, tuple[str, str]] = {}
    variables: dict[str, tuple[str, str]] = {}
    for path, manifest in loaded:
        label = str(manifest.get("name") or path.parent.name)
        for field, registry in (("name", names), ("slug", slugs)):
            value = manifest.get(field)
            if isinstance(value, str) and value in registry:
                blockers.append(f"duplicate {field} {value!r}: {registry[value]} and {path}")
            elif isinstance(value, str):
                registry[value] = path
        peer_dependencies = manifest.get("peerDependencies", {})
        if isinstance(peer_dependencies, dict):
            for dependency, raw in peer_dependencies.items():
                if not isinstance(raw, str):
                    continue
                if dependency in peers:
                    prior_range, prior_kit = peers[dependency]
                    if major(prior_range) and major(raw) and major(prior_range) != major(raw):
                        blockers.append(
                            f"peer {dependency!r} has incompatible majors: "
                            f"{prior_kit}={prior_range}, {label}={raw}"
                        )
                    elif prior_range != raw:
                        concerns.append(
                            f"peer {dependency!r} ranges require resolution: "
                            f"{prior_kit}={prior_range}, {label}={raw}"
                        )
                else:
                    peers[dependency] = (raw, label)
        kit_variables, global_selectors = css_contract(path, manifest)
        blockers.extend(f"{label}: unscoped global selector {item!r}" for item in global_selectors)
        for token, value in kit_variables.items():
            if token in variables:
                prior_value, prior_kit = variables[token]
                if prior_value.strip() != value.strip():
                    blockers.append(
                        f"CSS variable {token} conflicts: {prior_kit}={prior_value.strip()!r}, "
                        f"{label}={value.strip()!r}"
                    )
                else:
                    concerns.append(f"CSS variable {token} is shared by {prior_kit} and {label}")
            else:
                variables[token] = (value, label)
    return {
        "compatible": not blockers,
        "kits": [str(path) for path in paths],
        "blockers": blockers,
        "concerns": concerns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if len(args.manifests) < 2:
        parser.error("provide at least two manifests")
    try:
        report = analyze([path.expanduser().resolve() for path in args.manifests])
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Composition: {'compatible' if report['compatible'] else 'blocked'}")
        for category in ("blockers", "concerns"):
            for item in report[category]:
                print(f"{category.upper():8} {item}")
    return 0 if report["compatible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
