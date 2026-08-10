---
name: ui-studio
description: Use Playwright CLI to study live websites, runnable repository UIs, curated design-library links, and visual references, then turn the evidence into a named reusable UI kit and hostable showcase through a resumable gated workflow. Use when the user wants to investigate reference UIs, synthesize a visual direction, build sophisticated pages or components, create a design system, or iterate on an existing named UI kit.
argument-hint: "<URL|REPO|DESIGN-LINK|IMAGE|VIDEO|PATH>... [--kit <NAME>] [--target <PATH>]"
---

# UI Studio

Build an original, durable UI system from reference evidence. The output is a
named kit with tokens, reusable components, representative compositions, and a
viewable showcase that can later be imported into a product.

**Arguments:** "$ARGUMENTS"

## Operating contract

- Treat references as evidence, not templates to clone. Respect the approved
  rights mode for every source.
- Preserve the user's product goals and content model. Fidelity never outranks
  usability, accessibility, privacy, or an explicit requirement.
- Use Playwright CLI for every navigable reference and for the built UI. Never
  imply that static inspection exercised an interaction.
- Prefer the destination repository's framework, package manager, component
  model, and styling conventions. Discover them instead of replacing them.
- Build reusable components, not screenshot-shaped absolute positioning.
- Persist only evidence allowed by the artifact policy. Never commit browser
  authentication state, credentials, private traces, or unredacted user data.
- Keep user updates concise: current phase, evidence, decision needed, next gate.

## Load only the guide needed for the current phase

- Intake, source rights, privacy, repository startup, curated links, capture,
  and synthesis: [REFERENCES.md](REFERENCES.md)
- Playwright command discovery, exploration, capture harnesses, authentication,
  traces, and production traversal: [PLAYWRIGHT.md](PLAYWRIGHT.md)
- Foundations, components, packaging, showcase, production hosting, verification,
  and iteration: [BUILD.md](BUILD.md)
- Manual acceptance runs for the skill itself: [DOGFOOD.md](DOGFOOD.md)

Read a linked guide completely before executing a phase that depends on it. Do
not load unrelated guides merely because they exist.

## 1. Parse intent and locate state

Collect the reference inputs, intended product surface, kit name if supplied,
destination path, hosting target, and constraints. Keep reference repositories
distinct from the destination repository unless the user explicitly makes them
the same.

Resolve the destination in this order:

1. explicit `--target` or user-stated path;
2. an existing app/package that owns the requested UI;
3. a new sibling package or app proposed at the Name gate.

Store resumable state at `<target>/.ui-studio/<kit-slug>/state.json`. Before a
target exists, use `<repo-root>/.ui-studio/intake-<stable-reference-hash>.json`.
If no repository exists, ask where the durable kit should live. Do not invent a
global agent-specific directory.

Initial state:

```json
{
  "schemaVersion": 1,
  "kitName": null,
  "kitSlug": null,
  "targetPath": null,
  "phase": "intake",
  "references": [],
  "artifactPolicy": null,
  "approvedDirection": null,
  "approvedScope": [],
  "stack": null,
  "generatedFiles": {},
  "lastVerifiedAt": null
}
```

Allowed phases are `intake`, `capture`, `synthesize`, `direction-gate`,
`name-gate`, `plan`, `scaffold`, `foundations`, `components`, `compositions`,
`showcase`, `verify`, `release-gate`, `handoff`, and `iterate`.

Write state atomically after each completed phase. State is a cache: references,
the kit manifest, and the filesystem are authoritative. On resume, re-check them
before routing. After the Name gate approves a target and slug, atomically move
the intake state to its named location and leave no second active state.

State and transient evidence under `.ui-studio/` are local runtime artifacts by
default. Do not commit them unless the approved artifact policy names specific
redacted files. Durable decisions belong in the kit manifest and documentation.

## 2. Route by phase

```text
intake -> capture -> synthesize -> direction-gate -> name-gate -> plan
       -> scaffold -> foundations -> components -> compositions -> showcase
       -> verify -> release-gate -> handoff -> iterate
```

Before running the persisted phase, verify all earlier completion contracts.
Route back to the earliest incomplete phase when an artifact is absent or stale.
Set `phase` to the next phase only after the current artifact is persisted and
its completion test passes. `blocked` is a recorded condition, not a phase.

| Phase | Required artifact | Completion test |
| --- | --- | --- |
| `intake` | Reference inventory, intended surface, destination, rights and artifact policies | Every source is classifiable and at least one product surface is known |
| `capture` | Source ledger with Playwright evidence for navigable sources | Approved surfaces are covered or each gap is disclosed |
| `synthesize` | Design thesis, principles, trait matrix, direction options and non-goals | Every proposed rule traces to product need or evidence |
| `direction-gate` | Explicit direction approval and rationale | User approves one direction and its exclusions |
| `name-gate` | Approved name, slug, target, stack, public scope and host strategy | User approves the complete kit contract |
| `plan` | Dependency-ordered implementation plan and scenario matrix | Every public surface maps to build and verification work |
| `scaffold` | Runnable package/app, manifest and documented commands | Clean install, development command and initial build start successfully |
| `foundations` | Semantic tokens, themes and foundation showcase | Roles are consumable without component-local duplication |
| `components` | Public components, documented APIs and state examples | Approved component scenarios render and operate accessibly |
| `compositions` | Representative pages/flows using public components | Dense, sparse, adverse and responsive scenarios are covered |
| `showcase` | Navigable named/versioned catalog | One command runs it and every review route is reachable |
| `verify` | Verification report and production artifacts | Required checks and consumer/host smoke tests pass |
| `release-gate` | User review decision with accepted limitations | User explicitly approves reuse or names revisions |
| `handoff` | Version, changelog, reuse/hosting docs and migration notes | A fresh consumer can follow the documented path |
| `iterate` | Updated request mapped to affected phases | Route to the earliest invalidated contract or no-op |

## 3. Hard gates

Hard gates require explicit approval. An approval already present in the user's
request counts; never ask twice.

1. **Direction gate** — approve the synthesis and exclusions. Remain in
   `direction-gate` until approval, then set `phase: "name-gate"`.
2. **Name gate** — approve name, slug, destination, stack, public API, dependency
   additions, and hosting strategy before durable implementation. Then migrate
   state and set `phase: "plan"`.
3. **Release gate** — review the production-built showcase and accepted
   limitations before calling the kit reusable. Then set `phase: "handoff"`.

## 4. Execute the routed phase

### Intake through synthesis

Read [REFERENCES.md](REFERENCES.md). For navigable sources also read
[PLAYWRIGHT.md](PLAYWRIGHT.md). Do not advance Capture based only on screenshots
when the source was accessible and interactive behavior matters.

### Plan through handoff

Read [BUILD.md](BUILD.md). Use [PLAYWRIGHT.md](PLAYWRIGHT.md) for the feedback
loop and production traversal. Verify the built artifact, not only a dev server.

### Iterate

Load the existing manifest, state, showcase, changelog, and public entry points.
Treat hand-edited files as user-owned. Route changes as follows:

- new reference or missing evidence -> `capture`;
- changed design principles or rights -> `direction-gate`;
- changed stack, destination, name, dependency policy, or breaking public API ->
  `name-gate`;
- token/theme change -> `foundations`;
- compatible component behavior or API -> `components`;
- page, content, or flow change -> `compositions`;
- catalog or hosting change -> `showcase`;
- verification-only regression -> earliest failing build phase.

After any iteration, rerun affected checks plus the production build, update the
showcase and changelog, and version by the repository's existing policy. When no
policy exists, use patch for compatible fixes, minor for compatible public
additions, and major only for an explicitly approved breaking change.

## 5. Recovery and idempotency

- Track generated-file hashes. Before replacing a tracked file, compare its
  current hash. Merge or stop on user edits; never silently overwrite them.
- Re-running a completed phase verifies its outputs and no-ops when they remain
  valid.
- On a partial write, retain the last completed phase and record partial files.
  Repair or remove only confirmed partial output on resume.
- If a source disappears, retain prior observations as stale and request a
  replacement only when the missing evidence blocks the current phase.
- If a target moves, find the manifest by kit name, confirm the move, and update
  state paths without rebuilding the kit.
- Stop all managed reference/showcase processes and delete ephemeral auth state
  at completion or before a blocking handoff unless the user asks to retain them.

## Completion report

```text
Kit: <name> v<version>
Phase: <iterate|blocked phase>
View: <command and URL/path>
Reuse: <public entry point>
Evidence: <source-ledger path and policy>
Verified: <checks run>
Open: <accepted limitations or next gate>
```
