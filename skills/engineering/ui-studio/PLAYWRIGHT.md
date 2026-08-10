# Playwright Protocol

Use this guide for every navigable reference and every runnable kit/showcase.

## Discover the supported CLI

Prefer the Playwright version pinned by the reference or destination repository.
Inspect package scripts and run the active package manager's equivalent of
`playwright --help` before issuing commands.

Two modes are valid:

1. **Agent-oriented Playwright CLI** — use it only when its own help lists
   session primitives such as open, snapshot, click, fill, resize, console, or
   network inspection. Follow its exact surfaced syntax; do not invent commands.
2. **Official Playwright CLI** — use `codegen` for headed/user-assisted
   exploration and a short Playwright Test capture spec for repeatable autonomous
   navigation, snapshots, screenshots, traces, console, and network evidence.

The official CLI exposes test execution, code generation, debugging, reports,
browser installation, and trace viewing. “Snapshot-backed click” is a workflow,
not a portable official subcommand.

If no pinned Playwright exists, use the active package manager's ephemeral
package runner in an ignored scratch directory without editing either project
manifest. Install a compatible browser only when missing. Block with the exact
prerequisite when the runtime, browser, or network is unavailable.

If browser launch reports missing host libraries, surface Playwright's exact
`install-deps` command. Run it only in an authorized disposable environment or
when system-package installation is already within scope; otherwise block and
let the user provision the host. Never silently invoke `sudo` on their machine.

## Session safety

- Use a fresh isolated browser context, never the user's everyday profile.
- Do not bypass access controls or bot protection.
- Do not submit purchases, messages, destructive forms, production mutations,
  or irreversible consent changes.
- Use fixtures or safe stub actions for mutation paths.
- Keep authentication state and traces in an ignored, access-restricted scratch
  directory governed by the artifact policy.

## Headed exploration and authentication

Use the project runner's equivalent of:

```bash
npx playwright codegen --viewport-size="1440,900" <url>
```

Codegen is appropriate for learning flows, selecting resilient role/text/test-id
locators, and allowing the user to complete authentication personally. Repeat
with `--device` or another `--viewport-size`, and `--color-scheme` when relevant.

When a resumable authenticated session is unavoidable, `--save-storage` may
write cookies, local storage, and IndexedDB. Save it only beneath ignored runtime
state, restrict access, never inspect or commit its contents, use it only for the
approved source, and delete it at the retention boundary. Prefer keeping a live
isolated session over persisting storage.

## Repeatable capture spec

When starting from HTTP(S) references, the bundled generator can establish a
reviewable scratch plan and repeatable three-viewport harness:

```bash
python3 <skill-dir>/scripts/make-capture.py \
  --url <reference-url> \
  --hypothesis "<question this capture answers>" \
  --out <ignored-scratch-directory>
```

Review the generated source list, rights mode, viewports, and placeholder before
adding only approved interactions. Run with one worker and set
`UI_STUDIO_EVIDENCE_OUTPUT` to an ignored `evidence.json` path. Validate that
index and apply the artifact policy before retaining it. The generator refuses
to overwrite an existing harness unless `--force` is supplied after review.

For autonomous evidence, create a short scratch Playwright Test spec outside the
reference repository's tracked files. Adapt this shape to the pinned version:

```ts
import { test, expect } from '@playwright/test';

test('capture approved reference flow', async ({ page }, testInfo) => {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];

  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', error => consoleErrors.push(error.message));
  page.on('requestfailed', request => failedRequests.push(request.url()));

  await page.goto(process.env.REFERENCE_URL!);
  await expect(page.getByRole('main')).toBeVisible();
  const aria = await page.locator('body').ariaSnapshot();
  await testInfo.attach('aria.yml', { body: aria, contentType: 'text/yaml' });
  await page.screenshot({ path: testInfo.outputPath('wide.png'), fullPage: true });

  // Add only approved, hypothesis-driven interactions using user-visible roles.

  await testInfo.attach('console-errors.json', {
    body: JSON.stringify(consoleErrors), contentType: 'application/json'
  });
  await testInfo.attach('failed-requests.json', {
    body: JSON.stringify(failedRequests), contentType: 'application/json'
  });
});
```

Use role, label, placeholder, text, or stable test-id locators. Avoid brittle CSS
paths and coordinates. Capture before and after meaningful interactions. When
the pinned version supports AI-optimized ARIA snapshots, they may help analysis;
fall back to the default ARIA snapshot rather than upgrading the project solely
for that feature.

Run deterministically with the repository runner's equivalent of:

```bash
npx playwright test <scratch-spec> --workers=1 --trace=on
```

Do not assert that a reference site has zero console or network failures; record
them as evidence. The generated kit, by contrast, must explain or eliminate its
own failures.

## Investigation loop

For each accessible surface:

1. State the exploration hypothesis.
2. Open the exact URL and record redirects, title, revision when known, viewport,
   and access limitations.
3. Capture an ARIA/DOM snapshot and full-page screenshot before interaction.
4. Exercise relevant navigation, menus, tabs, disclosure, dialogs, carousels,
   search, filters, forms, focus order, and recovery paths.
5. Repeat important states at narrow, middle, and wide viewports. Include touch
   device emulation, hover/pointer differences, reduced motion, color scheme,
   zoom, and keyboard-only operation when relevant.
6. Record observable animation timing, console/page errors, failed requests, and
   the before/after state of each important action.
7. Redact or delete evidence according to policy, close contexts, and stop any
   managed server.

Do not interact randomly or crawl beyond the approved evidence question.

After Capture, record the source revision, capture timestamp, route, and content
fingerprint when it is locally or safely observable. A fingerprint detects
change; it is not proof that two rendered interfaces are semantically equal.

## Drive the built UI

After each meaningful build slice, reuse or start the local server and traverse
the affected flow with Playwright. Repair obvious visual, semantic, interaction,
console, and network defects before continuing.

For final verification, prefer the repository's Playwright `webServer`
configuration. Otherwise start a managed production server with a discovered
URL and readiness check. Traverse every showcase route and representative
interaction against the production build at narrow, middle, and wide viewports.

Keep traces on failure or when the artifact policy allows review evidence. Use
ARIA snapshots for structural intent and targeted assertions for behavior; do
not approve large snapshot updates without understanding the diff.

## Official references

- [Playwright command line](https://playwright.dev/docs/test-cli)
- [Test generator and authentication state](https://playwright.dev/docs/codegen)
- [ARIA snapshots](https://playwright.dev/docs/aria-snapshots)
- [Trace Viewer](https://playwright.dev/docs/trace-viewer-intro)
- [Starting a web server for tests](https://playwright.dev/docs/test-webserver)
