#!/usr/bin/env python3
"""Generate a Playwright production verifier that emits verification.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse


def load_manifest(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    for field in ("name", "version", "hosting"):
        if field not in data:
            raise ValueError(f"manifest is missing {field}")
    return data


def validate_base_url(raw: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--base-url must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password:
        raise ValueError("--base-url must not contain credentials")
    return raw.rstrip("/") + "/"


def render_spec(config_name: str) -> str:
    return f"""import {{ mkdirSync, readFileSync, writeFileSync }} from 'node:fs';
import {{ dirname, resolve }} from 'node:path';
import {{ test, expect }} from '@playwright/test';

const config = JSON.parse(readFileSync(resolve(__dirname, '{config_name}'), 'utf8'));
const routes: any[] = [];
let missingRouteHandled = false;

for (const path of config.routes) {{
  test(`verify production route ${{path}}`, async ({{ page }}) => {{
    const assetFailures: string[] = [];
    const consoleErrors: string[] = [];
    page.on('requestfailed', request => {{
      if (['document', 'stylesheet', 'script', 'font', 'image'].includes(request.resourceType())) {{
        assetFailures.push(request.url());
      }}
    }});
    page.on('console', message => {{
      if (message.type() === 'error') consoleErrors.push(message.text());
    }});
    page.on('pageerror', error => consoleErrors.push(error.message));
    const url = new URL(path.replace(/^\\//, ''), config.baseUrl).toString();
    const response = await page.goto(url, {{ waitUntil: 'networkidle' }});
    await expect(page.locator('body')).toBeVisible();
    const status = response?.status() ?? 0;
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
    );
    const focusable = await page.locator(
      'a[href],button,input,select,textarea,[tabindex]:not([tabindex="-1"])'
    ).count();
    await page.keyboard.press('Tab');
    const focusMoved = await page.evaluate(() => document.activeElement !== document.body);
    await page.reload({{ waitUntil: 'networkidle' }});
    await expect(page.locator('body')).toBeVisible();
    routes.push({{
      path,
      status,
      deepLink: status >= 200 && status < 400,
      refresh: true,
      assetFailures,
      consoleErrors,
      horizontalOverflow: overflow,
      focusable,
      focusMoved,
    }});
  }});
}}

test('verify missing-route handling', async ({{ page }}) => {{
  const url = new URL(config.missingRoute.replace(/^\\//, ''), config.baseUrl).toString();
  const response = await page.goto(url, {{ waitUntil: 'domcontentloaded' }});
  const status = response?.status() ?? 0;
  if (config.missingRoutePolicy === 'status') {{
    missingRouteHandled = status >= 400;
  }} else {{
    missingRouteHandled = status >= 200 && status < 400
      && new URL(page.url()).pathname === config.missingRoute
      && await page.locator('body').isVisible();
  }}
}});

test.afterAll(() => {{
  const routeFailures = routes.filter(route =>
    !route.deepLink || !route.refresh || route.assetFailures.length ||
    route.consoleErrors.length || route.horizontalOverflow
  );
  const keyboardPass = routes.every(route => route.focusable === 0 || route.focusMoved);
  const output = resolve(
    process.env.UI_STUDIO_VERIFICATION_OUTPUT || 'test-results/verification.json'
  );
  mkdirSync(dirname(output), {{ recursive: true }});
  writeFileSync(output, JSON.stringify({{
    schemaVersion: 1,
    kit: config.kit,
    version: config.version,
    verifiedAt: new Date().toISOString(),
    target: config.baseUrl,
    routes,
    accessibility: {{
      scenarios: [{{
        name: 'keyboard-only',
        status: keyboardPass ? 'pass' : 'fail',
        evidence: keyboardPass
          ? 'Tab moved focus when focusable controls were present.'
          : 'Tab did not move focus on at least one route with focusable controls.',
      }}],
    }},
    deployment: {{
      basePath: routes.length > 0 && routes.every(route => route.deepLink),
      missingRoute: missingRouteHandled,
      assetPaths: routes.every(route => route.assetFailures.length === 0),
      cacheAssumptions: 'No cache claim; inspect intended-host headers separately.',
    }},
    result: routeFailures.length || !keyboardPass || !missingRouteHandled ? 'fail' : 'pass',
    limitations: [
      'Automated receipt covers mechanical production behavior; complete manual accessibility scenarios separately.'
    ],
  }}, null, 2) + '\\n');
}});
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--route", action="append")
    parser.add_argument("--missing-route", default="/__ui-studio-missing__")
    parser.add_argument(
        "--missing-route-policy", choices=["status", "rendered"], default="status"
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest.expanduser().resolve())
        base_url = validate_base_url(args.base_url)
        routes = args.route or [str(manifest["hosting"].get("basePath", "/"))]
        for route in [*routes, args.missing_route]:
            urljoin(base_url, route)
            if not route.startswith("/"):
                raise ValueError(f"route must start with /: {route}")
        output = args.out.expanduser().resolve()
        config_path = output / "verification-plan.json"
        spec_path = output / "verification.spec.ts"
        existing = [path for path in (config_path, spec_path) if path.exists()]
        if existing and not args.force:
            raise ValueError("refusing to overwrite verifier; pass --force after review")
        output.mkdir(parents=True, exist_ok=True)
        config = {
            "schemaVersion": 1,
            "kit": manifest["name"],
            "version": manifest["version"],
            "baseUrl": base_url,
            "routes": routes,
            "missingRoute": args.missing_route,
            "missingRoutePolicy": args.missing_route_policy,
        }
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        spec_path.write_text(render_spec(config_path.name), encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"Created production verifier in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
