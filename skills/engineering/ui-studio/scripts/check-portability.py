#!/usr/bin/env python3
"""Validate the framework-neutral UI kit portability fixture contracts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
ROOT = SKILL_DIR / "fixtures" / "portability"
CONSUMERS = {
    "react": "src.js",
    "vue": "src.js",
    "svelte": "src.js",
    "web-components": "src.js",
}


def main() -> int:
    issues: list[str] = []
    kit_package = json.loads((ROOT / "kit" / "package.json").read_text(encoding="utf-8"))
    exports = kit_package.get("exports", {})
    for public_entry in (".", "./styles.css", "./tokens.json"):
        if public_entry not in exports:
            issues.append(f"kit is missing export {public_entry}")
    kit_source = (ROOT / "kit" / "src" / "index.js").read_text(encoding="utf-8")
    if "typeof window" not in kit_source:
        issues.append("kit runtime lacks an SSR-safe browser boundary")
    for framework, source_name in CONSUMERS.items():
        directory = ROOT / framework
        package = json.loads((directory / "package.json").read_text(encoding="utf-8"))
        dependencies = package.get("dependencies", {})
        if dependencies.get("@ui-studio/portability-kit") != "*":
            issues.append(f"{framework}: does not consume the workspace kit")
        if package.get("scripts", {}).get("build") != "vite build":
            issues.append(f"{framework}: lacks the production build contract")
        source = (directory / source_name).read_text(encoding="utf-8")
        if "@ui-studio/portability-kit" not in source:
            issues.append(f"{framework}: bypasses the public kit entry point")
        if "@ui-studio/portability-kit/styles.css" not in source:
            issues.append(f"{framework}: bypasses the public style entry point")
        for dependency, version in {
            **package.get("dependencies", {}),
            **package.get("devDependencies", {}),
        }.items():
            if dependency == "@ui-studio/portability-kit":
                continue
            if not isinstance(version, str) or version.startswith(("^", "~", ">", "<")):
                issues.append(f"{framework}: dependency {dependency} is not pinned")
    if issues:
        for issue in issues:
            print(f"ERROR {issue}")
        return 1
    print("UI Studio portability contracts passed for React, Vue, Svelte, and web components.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
