#!/usr/bin/env python3
"""Generate a disposable, hypothesis-driven Playwright capture harness."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_VIEWPORTS = ["390x844", "1024x768", "1440x900"]


def parse_viewport(raw: str) -> dict[str, int]:
    match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", raw)
    if not match:
        raise ValueError(f"invalid viewport {raw!r}; expected WIDTHxHEIGHT")
    return {"width": int(match.group(1)), "height": int(match.group(2))}


def validate_url(raw: str) -> None:
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"capture URL must be absolute HTTP(S): {raw}")
    if parsed.username or parsed.password:
        raise ValueError("capture URLs must not embed credentials")


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"refusing to overwrite {path}; pass --force after review")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def render_spec(plan_name: str) -> str:
    return f"""import {{ createHash }} from 'node:crypto';
import {{ mkdirSync, readFileSync, writeFileSync }} from 'node:fs';
import {{ dirname, resolve }} from 'node:path';
import {{ test, expect }} from '@playwright/test';

const plan = JSON.parse(readFileSync(resolve(__dirname, '{plan_name}'), 'utf8'));
const observations: any[] = [];
const structuredCaptures: any[] = [];

for (const source of plan.sources) {{
  for (const viewport of plan.viewports) {{
    test(`${{source.id}} ${{viewport.width}}x${{viewport.height}}`, async ({{ page }}, testInfo) => {{
      const consoleErrors: string[] = [];
      const failedRequests: string[] = [];
      page.on('console', message => {{
        if (message.type() === 'error') consoleErrors.push(message.text());
      }});
      page.on('pageerror', error => consoleErrors.push(error.message));
      page.on('requestfailed', request => failedRequests.push(request.url()));
      await page.setViewportSize(viewport);
      const response = await page.goto(source.source, {{ waitUntil: 'domcontentloaded' }});
      await expect(page.locator('body')).toBeVisible();
      const aria = await page.locator('body').ariaSnapshot();
      const size = `${{viewport.width}}x${{viewport.height}}`;
      const structured = await page.evaluate(() => {{
        const selected = Array.from(document.querySelectorAll(
          'h1,h2,h3,p,a,button,input,select,textarea,[role]'
        )).slice(0, 80);
        const samples = selected.map((element) => {{
          const style = getComputedStyle(element);
          const rect = element.getBoundingClientRect();
          return {{
            tag: element.tagName.toLowerCase(),
            role: element.getAttribute('role'),
            textLength: (element.textContent || '').trim().length,
            rect: {{ x: rect.x, y: rect.y, width: rect.width, height: rect.height }},
            style: {{
              display: style.display,
              position: style.position,
              fontFamily: style.fontFamily,
              fontSize: style.fontSize,
              fontWeight: style.fontWeight,
              lineHeight: style.lineHeight,
              color: style.color,
              backgroundColor: style.backgroundColor,
              borderRadius: style.borderRadius,
              padding: style.padding,
              gap: style.gap,
              transitionDuration: style.transitionDuration,
              animationDuration: style.animationDuration,
            }},
          }};
        }});
        return {{
          structure: {{
            headings: document.querySelectorAll('h1,h2,h3,h4,h5,h6').length,
            landmarks: document.querySelectorAll(
              'main,nav,header,footer,aside,[role="main"],[role="navigation"]'
            ).length,
            controls: document.querySelectorAll(
              'button,input,select,textarea,a[href]'
            ).length,
            dialogs: document.querySelectorAll('dialog,[role="dialog"]').length,
            lists: document.querySelectorAll('ul,ol,[role="list"]').length,
          }},
          samples,
          media: {{
            reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
            darkScheme: matchMedia('(prefers-color-scheme: dark)').matches,
            forcedColors: matchMedia('(forced-colors: active)').matches,
            coarsePointer: matchMedia('(pointer: coarse)').matches,
          }},
        }};
      }});
      await testInfo.attach('aria.yml', {{ body: aria, contentType: 'text/yaml' }});
      await page.screenshot({{ path: testInfo.outputPath(`${{size}}.png`), fullPage: true }});
      observations.push({{
        ...source,
        capturedAt: new Date().toISOString(),
        finalUrl: page.url(),
        title: await page.title(),
        status: response?.status() ?? null,
        viewport: size,
        contentFingerprint: `sha256:${{createHash('sha256').update(aria).digest('hex')}}`,
        evidence: ['aria.yml', `${{size}}.png`],
        consoleErrors,
        failedRequests,
      }});
      structuredCaptures.push({{
        sourceId: source.id,
        url: page.url(),
        viewport: size,
        structure: structured.structure,
        samples: structured.samples,
        media: structured.media,
        limitations: [
          'Samples are bounded observations, not reusable source CSS.'
        ],
      }});
      // Add only approved, hypothesis-driven interactions below this line.
    }});
  }}
}}

test.afterAll(() => {{
  const output = resolve(process.env.UI_STUDIO_EVIDENCE_OUTPUT || 'test-results/evidence.json');
  mkdirSync(dirname(output), {{ recursive: true }});
  writeFileSync(output, JSON.stringify({{
    schemaVersion: 1,
    hypothesis: plan.hypothesis,
    capturedAt: new Date().toISOString(),
    maxAgeDays: plan.maxAgeDays,
    sources: observations,
  }}, null, 2) + '\\n');
  const observationOutput = resolve(
    process.env.UI_STUDIO_OBSERVATION_OUTPUT || 'test-results/observations.json'
  );
  mkdirSync(dirname(observationOutput), {{ recursive: true }});
  writeFileSync(observationOutput, JSON.stringify({{
    schemaVersion: 1,
    hypothesis: plan.hypothesis,
    capturedAt: new Date().toISOString(),
    captures: structuredCaptures,
  }}, null, 2) + '\\n');
}});
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", required=True)
    parser.add_argument("--hypothesis", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--viewport", action="append")
    parser.add_argument("--max-age-days", type=int, default=30)
    parser.add_argument(
        "--rights-mode",
        choices=[
            "inspiration-only",
            "behavior-reimplementation",
            "licensed-reuse",
            "same-product-reuse",
        ],
        default="inspiration-only",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        for url in args.url:
            validate_url(url)
        if not args.hypothesis.strip():
            raise ValueError("--hypothesis must not be empty")
        if args.max_age_days < 0:
            raise ValueError("--max-age-days must be non-negative")
        viewport_labels = args.viewport or DEFAULT_VIEWPORTS
        viewports = [parse_viewport(item) for item in viewport_labels]
        plan = {
            "schemaVersion": 1,
            "hypothesis": args.hypothesis,
            "maxAgeDays": args.max_age_days,
            "viewports": viewports,
            "sources": [
                {
                    "id": f"source-{index}",
                    "source": url,
                    "kind": "website",
                    "rightsMode": args.rights_mode,
                    "revision": None,
                    "routes": [urlparse(url).path or "/"],
                    "limitations": [],
                }
                for index, url in enumerate(args.url, start=1)
            ],
        }
        output = args.out.expanduser().resolve()
        plan_path = output / "capture-plan.json"
        spec_path = output / "capture.spec.ts"
        existing = [path for path in (plan_path, spec_path) if path.exists()]
        if existing and not args.force:
            names = ", ".join(str(path) for path in existing)
            raise ValueError(f"refusing to overwrite {names}; pass --force after review")
        write_new(plan_path, json.dumps(plan, indent=2) + "\n", args.force)
        write_new(spec_path, render_spec("capture-plan.json"), args.force)
    except (OSError, ValueError) as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"Created capture harness in {output}")
    print("Review interactions, then run with --workers=1 and UI_STUDIO_EVIDENCE_OUTPUT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
