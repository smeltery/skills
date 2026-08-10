---
name: ui-studio
description: Use Playwright CLI to study live websites, runnable repository UIs, or curated design-library references such as Mobbin, then turn the evidence into a named, reusable UI kit and a runnable, hostable showcase through a resumable gated workflow. Use when the user wants to investigate reference sites, shared UI flows, or UI codebases, synthesize a visual direction, build sophisticated pages or components, create a design system, or iterate on an existing named UI kit.
argument-hint: "<URL|REPO|MOBBIN-LINK|IMAGE|PATH>... [--kit <NAME>] [--target <PATH>]"
---

# UI Studio

Build a durable UI system from references, not a pixel copy. The output is a
named kit with tokens, reusable components, representative compositions, and a
viewable showcase that can later be imported into a product.

**Arguments:** "$ARGUMENTS"

## Operating contract

- Treat references as evidence about hierarchy, rhythm, typography, color,
  interaction, and density. Do not copy source code, protected assets, logos,
  brand names, distinctive illustrations, or a site's complete trade dress.
- Preserve the user's product goals and content model. Visual fidelity never
  outranks usability, accessibility, or an explicit requirement.
- Prefer the target repository's framework, package manager, component model,
  and styling conventions. Discover them; do not replace them casually.
- Build production-shaped components, not a screenshot made from absolute
  positioning. Reuse must be visible in the API and file structure.
- Use Playwright CLI for reference-site exploration and built-UI review. Never
  claim to have inspected an inaccessible viewport, interaction, or
  authenticated page, and never silently substitute a static page fetch.
- Keep user-facing updates concise: current phase, evidence, decision needed,
  and the next gate.

## 1. Parse intent and locate state

Collect website URLs, repository paths or clone URLs, curated design-library
links such as Mobbin shares, attached images, local paths, a requested kit name,
target path, desired surfaces, and constraints from the request. A reference may
be an entire site or repository UI, a saved collection or flow, or a specific
page, screen, region, state, or interaction. Keep reference repositories
distinct from the destination repository; never assume the UI being studied is
where the new kit should be written.

Discover the repository root and any existing app before choosing an output
location. Resolution order:

1. explicit `--target` or user-stated path;
2. an existing app/package that owns the requested UI;
3. a new sibling package or app proposed at the Name gate.

Store resumable state at `<target>/.ui-studio/<kit-slug>/state.json`. Before a
target exists, use `<repo-root>/.ui-studio/intake-<stable-reference-hash>.json`.
If no repository exists, ask where the durable kit should live; do not invent a
global agent-specific directory.

State shape:

```json
{
  "schemaVersion": 1,
  "kitName": null,
  "kitSlug": null,
  "targetPath": null,
  "phase": "intake|capture|synthesize|direction-gate|name-gate|plan|scaffold|foundations|components|compositions|showcase|verify|release-gate|handoff|iterate",
  "references": [],
  "referenceRepos": [],
  "curatedReferences": [],
  "playwrightEvidence": [],
  "approvedDirection": null,
  "approvedScope": [],
  "stack": null,
  "generatedFiles": {},
  "lastVerifiedAt": null
}
```

Write state atomically after each completed phase. State is a cache: references,
the manifest, and the filesystem are authoritative. On resume, re-check them
before routing. Never advance a phase merely because a state file says it ran.
After the Name gate approves a slug and target, atomically move the intake state
to `<target>/.ui-studio/<kit-slug>/state.json`; do not leave two active states.

## 2. State machine

```text
intake -> capture -> synthesize -> direction-gate -> name-gate -> plan
       -> scaffold -> foundations -> components -> compositions -> showcase
       -> verify -> release-gate -> handoff -> iterate
```

Route explicitly from the persisted phase:

```text
intake:         run Intake
capture:        bring up references and run Playwright Capture
synthesize:     synthesize the reference evidence
direction-gate: present direction and wait for approval
name-gate:      present name, target, stack, and public API; wait for approval
plan:           write the dependency-ordered implementation plan
scaffold:       create or integrate the package and manifest
foundations:    implement design tokens and themes
components:     implement public components and states
compositions:   assemble representative pages and flows
showcase:       create and exercise the viewable catalog
verify:         run the complete verification matrix
release-gate:   present the built showcase and wait for approval
handoff:        document versioned reuse and limitations
iterate:        route an iteration to its earliest affected phase
```

Before running the routed phase, verify that earlier phase outputs still exist
and satisfy their completion conditions. If not, route back to the earliest
incomplete phase and explain why. Set `phase` to the next phase only after the
current phase completes and its output is persisted. `blocked` is a condition
with a reason, not a terminal phase. Once it clears, resume the same phase.

Hard gates require explicit user approval:

1. **Direction gate** — approve the synthesized visual direction and what is
   intentionally excluded. Remain in `direction-gate` until approval, then set
   `phase: "name-gate"`.
2. **Name gate** — approve the kit name, slug, target, public component scope,
   and framework before durable code is created. Remain in `name-gate` until
   approval, migrate state to its named location, then set `phase: "plan"`.
3. **Release gate** — approve the reviewed showcase before declaring the kit
   reusable or integrating it into another product. Remain in `release-gate`
   until approval, then set `phase: "handoff"`.

Approval of one gate does not imply approval of later gates. If the user gave a
decision explicitly in the original request, record it and do not ask twice.

## 3. Intake

Establish enough context to study the right problem:

- intended product, audience, primary tasks, and representative content;
- requested pages, flows, component families, states, and responsive targets;
- target repository or greenfield output;
- reference priority: inspiration, close adaptation, or one source for a
  specific trait;
- required themes, accessibility level, browser support, and hosting limits.

Ask only for missing decisions that would materially change the result. Use
clearly labeled assumptions for reversible details. Do not start Capture until
at least one website, runnable repository UI, curated design-library reference,
or static visual reference and one intended product surface are known.

## 4. Capture references with Playwright CLI

Playwright CLI is required for navigable website references. Discover the
installed command from the target repository, package scripts, and `PATH`, then
read its `--help` before use because CLI distributions and versions expose
different command names. Prefer the repository-pinned CLI. If none is present,
use the active package manager's ephemeral runner without changing the project
manifest. If that is unavailable, block Capture with the missing prerequisite;
do not fall back to HTTP scraping without telling the user.

Use an isolated browser session for this skill, never the user's everyday
browser profile. Reuse that session within a reference domain so menus, consent
choices, and navigation can be investigated consistently. Do not bypass access
controls, defeat bot protection, enter secrets into untrusted pages, submit
orders, send messages, or trigger any destructive action.

### Bring up a repository reference

When a reference is a repository instead of a URL, first make its UI observable:

1. Resolve the repository root and current commit. Read its `README`, agent and
   contributor instructions, workspace manifests, lockfiles, task-runner config,
   environment examples, and app/package documentation before running anything.
2. Identify every plausible UI entry point: web apps, component explorers,
   documentation sites, example apps, and desktop shells with a web preview.
   Prefer the entry point named by the user; otherwise choose the one that best
   covers the requested surfaces and disclose the choice.
3. Discover the repository's package manager, dependency bootstrap, fixture or
   seed flow, and development command. Use its pinned versions and lockfile.
   Do not replace tooling, invent environment values, or write real credentials.
4. Bring up the UI using the documented command in a managed process whose logs
   and process identity are retained for cleanup. Read the served host, port,
   base path, and readiness signal from configuration or runtime output; do not
   assume a framework, command, or default port.
5. If setup requires missing secrets, external services, destructive seed data,
   or a choice among materially different apps, block Capture with the exact
   prerequisite. Do not edit reference application code merely to make it run
   unless the user separately asks for that change.
6. Record repository path or remote, commit SHA, chosen app/package, bootstrap
   and start commands, served URL, fixture/auth mode, and known limitations.
   Stop the managed process after Capture unless it is explicitly retained for
   the next phase.

Dependency installation and generated caches may be necessary to run the UI,
but the reference repository's tracked files must remain unchanged. Check its
working tree before and after bring-up and call out any tool-generated changes.
If the repository already exposes a running preview URL, record the commit or
revision it represents when discoverable and investigate that preview directly.

### Open a curated design-library reference

Treat Mobbin links and comparable screen, flow, pattern, or collection libraries
as curated references rather than ordinary marketing sites:

1. Open the exact deep link with Playwright CLI and record the provider, shared
   item title, platform or device, source application when shown, and whether it
   represents one screen, an ordered flow, a pattern, or a collection.
2. Preserve the curator's screen order and grouping. Explore zoom, annotations,
   variants, transitions, and neighboring states only when they help explain the
   requested product surface; do not bulk-crawl the provider's catalog.
3. If authentication is required, keep the isolated Playwright session open and
   ask the user to complete authentication themselves. Never request, type,
   store, or expose their credentials. Resume from the same session afterward.
4. If the deep link cannot be shared or reopened, accept exported screens or
   user-provided screenshots as static evidence and record that interactive
   states, ordering, or metadata could not be independently verified.
5. Record the deep link, observed screen identifiers, order, annotations,
   viewport/device metadata, access limitations, and the Playwright snapshots
   and screenshots used in the source ledger.

Curated examples often omit application context. Infer only the visible pattern;
do not treat a polished isolated screen as proof that the same hierarchy works
with the user's real content, navigation, or edge cases.

For each accessible URL, run this investigation loop:

1. Open the exact supplied URL and capture a DOM/accessibility snapshot before
   acting. Record redirects, title, viewport, and any blocked or missing state.
2. Use snapshot-backed, user-visible locators to navigate. Exercise primary
   navigation, menus, tabs, accordions, drawers, dialogs, carousels, search,
   filters, and other interactions relevant to the requested surface.
3. Scroll through the complete surface and follow only links needed to
   understand the system. Capture the state before and after important actions
   so behavior is evidence, not memory.
4. Repeat at representative narrow, middle, and wide viewports. Also exercise
   hover, focus, keyboard navigation, reduced motion, and light/dark modes when
   the reference exposes them.
5. Save named screenshots for important states and use Playwright output to
   inspect accessible names, semantics, console errors, failed requests, and
   observable timing or animation behavior.
6. Close the isolated session when Capture completes or record the session
   needed for a resumable authenticated flow.

Do not interact randomly. Start with a short exploration hypothesis such as
"learn how navigation collapses and how product filtering reveals state," then
revise it as evidence appears. For attached images or local non-HTML files,
inspect the originals at sufficient resolution and label them as static evidence
that Playwright could not exercise.

Record a source ledger in the state or kit documentation:

- source, page/region, viewport, access date, Playwright action path, screenshot
  or snapshot identifier, and access limitations;
- observed layout grid, spacing rhythm, type roles, palette roles, border and
  elevation language, icon/imagery treatment, motion, and interaction patterns;
- what to adapt, transform, or reject, with a short reason;
- asset and font licensing concerns.

With multiple references, build a trait matrix. Attribute each adopted trait to
evidence, identify conflicts, and choose one coherent rule rather than averaging
unrelated styles. Never fabricate details hidden behind inaccessible pages.

Capture is complete only when the evidence covers every approved surface, the
relevant UI has actually been exercised with Playwright CLI, and gaps are
disclosed for the Direction gate. If Playwright cannot access a required
reference, block Capture rather than implying that a static approximation was
interactive evidence.

## 5. Synthesize and pass the Direction gate

Turn observations into an original system:

- a one-sentence design thesis;
- three to five design principles tied to product goals;
- type scale, spacing and sizing rhythm, semantic color roles, shape, depth,
  imagery, motion, and responsive behavior;
- information hierarchy and interaction model;
- explicit non-goals and reference traits that will not be used.

Avoid the default "AI dashboard" look: arbitrary gradients, excessive rounded
cards, decorative glass effects, repeated hero copy, and uniform whitespace
without a content reason. Sophistication comes from coherent hierarchy,
proportion, states, and restraint.

Present the synthesis and, when useful, two or three genuinely different
direction boards. Stop at the Direction gate until the user chooses or revises
one. Persist the approval and rationale.

## 6. Pass the Name gate and plan

Propose a few pronounceable, product-neutral kit names unless the user supplied
one. Check for collisions in the repository and package/workspace configuration.
At the gate, show:

- display name and filesystem/package-safe slug;
- target path and detected stack;
- public tokens, components, patterns, and showcase surfaces;
- build, preview, and static-host strategy;
- dependencies to add, if any.

Do not create durable implementation files until the user explicitly approves
this contract. After approval, write a dependency-ordered plan and set `phase`
to `plan`.

## 7. Build the kit

### Scaffold

Integrate with the existing workspace when present. For greenfield work, choose
a widely supported stack suited to the requested host, explain the choice at the
Name gate, pin dependencies through its lockfile, and provide one command each
for development, validation, and production build.

Create a `ui-kit.json` (or idiomatic equivalent) manifest containing the kit
name, schema version, stack, entry points, themes, source-ledger path, commands,
and current kit version. Include a concise README with install, run, import,
theme, extension, and hosting instructions.

### Foundations

Implement semantic design tokens before components. Separate primitive values
from semantic roles and component aliases. Cover typography, color, spacing,
sizing, radii, borders, elevation, motion, breakpoints, and layering where the
design uses them. Prefer CSS custom properties or the target stack's native
theme mechanism so consumers can override the system without forking it.

### Components

Build the smallest component set that expresses the approved surfaces. Each
public component must have:

- a typed or documented API with composition slots where appropriate;
- default, interactive, disabled, loading, empty, error, overflow, and long-copy
  behavior where applicable;
- keyboard, focus-visible, screen-reader, and reduced-motion behavior;
- responsive behavior based on content pressure, not only common device widths;
- at least one showcase example using realistic fixture data.

Do not bake page copy, source-site names, or application business logic into
reusable primitives. Prefer composition over a large prop matrix.

### Compositions

Assemble representative pages and flows from the public components. Include
dense and sparse content, narrow and wide viewports, and at least one adverse
state. If the requested UI has meaningful behavior, model it explicitly with a
reducer or state machine rather than scattered booleans.

### Showcase

Create a navigable showcase or story catalog that exposes foundations,
component variants, compositions, themes, and viewport checks. It must:

- run locally with one documented command;
- build for production and be hostable on the user's target or as static files
  when the stack permits;
- use fixture data and safe stub actions, never live destructive mutations;
- display the kit name and version;
- make review URLs or routes easy to share.

After each meaningful build slice, start or reuse the local development server
and drive the result with Playwright CLI. Navigate through the implemented flow,
exercise every new interaction, inspect snapshots rather than judging only from
screenshots, and repair obvious behavioral or visual defects before moving on.

## 8. Verify

Use the repository's existing quality commands, then add only missing checks
proportionate to the kit. Verify:

- install from a clean dependency state and production build;
- lint, type checking, and focused component tests;
- automated accessibility checks plus keyboard-only review;
- no horizontal overflow or clipped content at representative narrow, middle,
  and wide viewports;
- contrast, focus visibility, reduced motion, zoom, long text, and both themes
  when supported;
- browser console and network failures;
- Playwright CLI traversal of every showcase route and representative
  interaction, with named screenshots at narrow, middle, and wide viewports;
- visual review against the approved direction, not pixel equality with a
  reference site;
- consumer import from the documented public entry point.

Save screenshots or visual baselines when the target repository has a suitable
convention. Report commands and failures truthfully. A failing required check
blocks the Release gate unless the user explicitly accepts the named limitation.

## 9. Release gate and handoff

Give the user the local command, built artifact path or preview URL, showcase
routes, kit name/version, and a short checklist for review. Stop for approval.

After approval:

- mark the manifest/version reusable;
- record accepted limitations and the next candidate components;
- document how a future app imports tokens, components, and styles;
- set `phase: "iterate"` and preserve the state for later runs.

Do not publish a package, deploy externally, or modify a consuming product
unless the user requested that action and the destination is unambiguous.

## 10. Iterate an existing kit

When a request names or points to an existing kit, load its manifest, state,
showcase, and public API before editing. Treat hand-edited files as user-owned.

For each iteration:

1. restate the requested outcome and affected public surfaces;
2. capture new references only if they add evidence;
3. return to the Direction or Name gate only when visual principles, stack,
   target, or public API materially change;
4. update tokens before one-off component values;
5. keep existing consumers compatible, or document a versioned migration;
6. rerun affected checks and the production build;
7. update the showcase, changelog, manifest version, and state.

## Recovery and idempotency

- Track generated file hashes in `generatedFiles`. Before replacing a tracked
  file, compare its current hash. If it changed outside the skill, merge
  carefully or stop with the exact conflict; never silently overwrite it.
- Re-running a completed phase verifies its outputs and no-ops when they still
  satisfy the phase contract.
- If a run stops mid-write, retain the last completed phase and list partial
  files. Repair or remove only those confirmed partial outputs on resume.
- If a reference disappears, keep prior observations labeled as stale and ask
  for a replacement only when the missing evidence blocks the current phase.
- If the target moves, discover the manifest by kit name, confirm the move, and
  update state paths without rebuilding the kit.

## Completion report

Keep the final handoff compact:

```text
Kit: <name> v<version>
Phase: <iterate|blocked phase>
View: <command and URL/path>
Reuse: <public entry point>
Verified: <checks run>
Open: <accepted limitations or next gate>
```
