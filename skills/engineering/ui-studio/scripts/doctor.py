#!/usr/bin/env python3
"""Read-only discovery for UI apps, tooling, hosting, and named UI Studio kits."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".next",
    ".cache",
    ".turbo",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
LOCKFILES = {
    "bun.lock": "bun",
    "bun.lockb": "bun",
    "deno.lock": "deno",
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
}
RUNTIME_FILES = {
    ".node-version",
    ".nvmrc",
    ".python-version",
    ".tool-versions",
    "mise.toml",
    "rust-toolchain.toml",
}
HOST_FILES = {
    "firebase.json",
    "netlify.toml",
    "render.yaml",
    "vercel.json",
    "wrangler.json",
    "wrangler.jsonc",
    "wrangler.toml",
}
UI_SCRIPT_WORDS = ("dev", "start", "storybook", "docs", "preview", "serve", "build")
RUN_SCRIPT_WORDS = ("dev", "start", "storybook", "docs", "preview", "serve")
MCP_CONFIG_NAMES = {
    ".mcp.json",
    "config.toml",
    "mcp.json",
    "mcp_config.json",
    "opencode.json",
    "settings.json",
}
UI_SH_SKILL_NAMES = {
    "add-dark-mode",
    "brand-kit",
    "canonicalize-tailwind",
    "componentize",
    "dark-mode-image",
    "design",
    "ideas",
    "make-responsive",
    "markup-from-image",
}
SKILL_DIR = Path(__file__).resolve().parent.parent


def load_validator():
    path = SKILL_DIR / "scripts" / "validate-kit.py"
    spec = importlib.util.spec_from_file_location("ui_studio_validate_kit", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    schema = json.loads(
        (SKILL_DIR / "schemas" / "ui-kit.schema.json").read_text(encoding="utf-8")
    )
    return module.validate, schema


def walk(root: Path):
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(item for item in dirs if item not in SKIP_DIRS)
        yield Path(current), sorted(files)


def relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)) or "."
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def discover(root: Path) -> dict[str, Any]:
    validate_manifest, manifest_schema = load_validator()
    package_managers: set[str] = set()
    runtimes: list[str] = []
    packages: list[dict[str, Any]] = []
    playwright_configs: list[str] = []
    explorers: list[str] = []
    hosting: list[str] = []
    kits: list[dict[str, Any]] = []
    paper_configs: list[str] = []
    refero_configs: list[str] = []
    ui_sh_candidates: list[dict[str, str]] = []

    for current, files in walk(root):
        for filename in files:
            path = current / filename
            rel = relative(path, root)
            if filename in LOCKFILES:
                package_managers.add(LOCKFILES[filename])
            if filename in RUNTIME_FILES:
                runtimes.append(rel)
            if filename in HOST_FILES:
                hosting.append(rel)
            if filename.startswith("playwright.config."):
                playwright_configs.append(rel)
            if ".storybook" in path.parts or filename.startswith("storybook."):
                explorers.append(rel)
            if filename in MCP_CONFIG_NAMES:
                try:
                    if path.stat().st_size <= 1_000_000:
                        config_text = path.read_text(encoding="utf-8", errors="ignore")
                        if (
                            "127.0.0.1:29979/mcp" in config_text
                            or "paper-design/agent-plugins" in config_text
                        ):
                            paper_configs.append(rel)
                        if "api.refero.design/mcp" in config_text:
                            refero_configs.append(rel)
                except OSError:
                    pass
            if filename == "SKILL.md":
                try:
                    skill_head = path.read_text(encoding="utf-8", errors="ignore")[:4000]
                except OSError:
                    skill_head = ""
                match = re.search(r"^name:\s*['\"]?([^'\"\n]+)", skill_head, re.M)
                name = match.group(1).strip() if match else ""
                if name in UI_SH_SKILL_NAMES:
                    ui_sh_candidates.append({"name": name, "path": rel})

        if "package.json" in files:
            path = current / "package.json"
            data = read_json(path)
            if data is not None:
                scripts = data.get("scripts", {})
                if not isinstance(scripts, dict):
                    scripts = {}
                ui_scripts = {
                    key: value
                    for key, value in sorted(scripts.items())
                    if isinstance(value, str)
                    and any(word in key.lower() for word in UI_SCRIPT_WORDS)
                }
                dependencies: dict[str, Any] = {}
                for field in ("dependencies", "devDependencies"):
                    value = data.get(field, {})
                    if isinstance(value, dict):
                        dependencies.update(value)
                packages.append(
                    {
                        "path": relative(path, root),
                        "name": data.get("name"),
                        "uiScripts": ui_scripts,
                        "playwrightPackages": sorted(
                            key for key in dependencies if "playwright" in key.lower()
                        ),
                        "componentExplorers": sorted(
                            key
                            for key in dependencies
                            if "storybook" in key.lower() or "ladle" in key.lower()
                        ),
                        "runnableUi": any(
                            any(word in key.lower() for word in RUN_SCRIPT_WORDS)
                            for key in ui_scripts
                        ),
                    }
                )

        if "ui-kit.json" in files:
            path = current / "ui-kit.json"
            data = read_json(path)
            validation_errors = (
                validate_manifest(data, manifest_schema) if data is not None
                else ["manifest is not valid JSON"]
            )
            kits.append(
                {
                    "path": relative(path, root),
                    "name": data.get("name") if data else None,
                    "slug": data.get("slug") if data else None,
                    "version": data.get("version") if data else None,
                    "validJson": data is not None,
                    "schemaValid": not validation_errors,
                    "validationErrors": validation_errors,
                }
            )

    name_paths: dict[str, list[str]] = {}
    slug_paths: dict[str, list[str]] = {}
    for kit in kits:
        if kit["name"]:
            name_paths.setdefault(str(kit["name"]), []).append(kit["path"])
        if kit["slug"]:
            slug_paths.setdefault(str(kit["slug"]), []).append(kit["path"])
    collisions = [
        {"name": name, "paths": paths}
        for name, paths in sorted(name_paths.items())
        if len(paths) > 1
    ]
    slug_collisions = [
        {"slug": slug, "paths": paths}
        for slug, paths in sorted(slug_paths.items())
        if len(paths) > 1
    ]

    local_playwright = root / "node_modules" / ".bin" / "playwright"
    playwright_command = None
    if local_playwright.is_file():
        playwright_command = str(local_playwright)
    elif shutil.which("playwright"):
        playwright_command = shutil.which("playwright")
    elif any(item["playwrightPackages"] for item in packages):
        manager = next(iter(sorted(package_managers)), "npm")
        playwright_command = {
            "npm": "npx playwright",
            "pnpm": "pnpm exec playwright",
            "yarn": "yarn playwright",
            "bun": "bunx playwright",
            "deno": "deno run npm:playwright"
        }.get(manager, "npx playwright")

    return {
        "root": str(root),
        "packageManagers": sorted(package_managers),
        "runtimeFiles": sorted(set(runtimes)),
        "packages": sorted(packages, key=lambda item: item["path"]),
        "playwright": {
            "command": playwright_command,
            "configs": sorted(set(playwright_configs)),
            "browserProbe": "run scripts/dogfood.sh or the discovered CLI capture harness"
        },
        "componentExplorerConfigs": sorted(set(explorers)),
        "hostingConfigs": sorted(set(hosting)),
        "kits": sorted(kits, key=lambda item: item["path"]),
        "kitNameCollisions": collisions,
        "kitSlugCollisions": slug_collisions,
        "integrations": {
            "paper": {
                "repositoryConfigPaths": sorted(set(paper_configs)),
                "connectionProbed": False,
            },
            "refero": {
                "repositoryConfigPaths": sorted(set(refero_configs)),
                "connectionProbed": False,
            },
            "uiSh": {
                "skillCandidates": sorted(
                    ui_sh_candidates, key=lambda item: (item["name"], item["path"])
                ),
                "activeRegistryInspected": False,
            },
        },
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [f"Root: {report['root']}"]
    managers = ", ".join(report["packageManagers"]) or "none detected"
    lines.append(f"Package managers: {managers}")
    lines.append(
        f"Playwright: {report['playwright']['command'] or 'not detected'}"
    )
    lines.append("Candidate UI packages:")
    candidates = [item for item in report["packages"] if item["runnableUi"]]
    if candidates:
        for item in candidates:
            scripts = ", ".join(item["uiScripts"])
            lines.append(f"  - {item['path']}: {scripts}")
    else:
        lines.append("  - none detected")
    lines.append("Named kits:")
    if report["kits"]:
        for kit in report["kits"]:
            status = "valid" if kit["schemaValid"] else "invalid"
            lines.append(
                f"  - {kit['name'] or '<unnamed>'} {kit['version'] or ''} "
                f"[{status}] ({kit['path']})"
            )
    else:
        lines.append("  - none detected")
    if report["kitNameCollisions"]:
        lines.append("Kit name collisions:")
        for item in report["kitNameCollisions"]:
            lines.append(f"  - {item['name']}: {', '.join(item['paths'])}")
    if report["kitSlugCollisions"]:
        lines.append("Kit slug collisions:")
        for item in report["kitSlugCollisions"]:
            lines.append(f"  - {item['slug']}: {', '.join(item['paths'])}")
    integrations = report["integrations"]
    lines.append("Optional design providers (repository evidence only):")
    for provider in ("paper", "refero"):
        paths = integrations[provider]["repositoryConfigPaths"]
        lines.append(f"  - {provider}: {', '.join(paths) if paths else 'not detected'}")
    ui_sh = integrations["uiSh"]["skillCandidates"]
    rendered = ", ".join(f"{item['name']} ({item['path']})" for item in ui_sh)
    lines.append(f"  - ui.sh candidates: {rendered or 'none detected'}")
    if report["hostingConfigs"]:
        lines.append(f"Hosting configs: {', '.join(report['hostingConfigs'])}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"root is not a directory: {root}")
    report = discover(root)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
