---
name: ui-studio
description: Use Playwright CLI, Paper MCP, Refero research, optional ui.sh polishing skills, runnable repository UIs, curated design links, and visual references to create an original named reusable UI kit and hostable showcase through a resumable gated workflow. Use when the user wants to investigate reference UIs, synthesize a visual direction, build sophisticated pages or components, create a design system, or iterate on an existing named UI kit.
argument-hint: "<URL|REPO|PAPER|REFERO|DESIGN-LINK|IMAGE|VIDEO|PATH>... [--kit <NAME>] [--target <PATH>]"
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
- Ordered visual and interaction evidence from video or animated references:
  [RECORDINGS.md](RECORDINGS.md)
- Foundations, components, packaging, showcase, production hosting, verification,
  and iteration: [BUILD.md](BUILD.md)
- Benchmarks, structured observations, compatibility, token interchange, visual
  approval, provenance, and framework portability: [QUALITY.md](QUALITY.md)
- Paper MCP, Refero research, and optional ui.sh polishing skills:
  [PROVIDERS.md](PROVIDERS.md)
- Optional container isolation for executing unfamiliar repository references:
  [SANDBOX.md](SANDBOX.md)
- Evidence-based structural and visual review before release:
  [CRITIQUE.md](CRITIQUE.md)
- Manual acceptance runs for the skill itself: [DOGFOOD.md](DOGFOOD.md)

Read a linked guide completely before executing a phase that depends on it. Do
not load unrelated guides merely because they exist.

## 1. Parse intent and locate state

Collect the reference inputs, intended product surface, kit name if supplied,
destination path, hosting target, and constraints. Keep reference repositories
distinct from the destination repository unless the user explicitly makes them
the same.

Identify requested or available design providers. Paper files are explicit
reference/canvas inputs, Refero is a curated research source, and ui.sh supplies
optional project skills rather than reference evidence. Read `PROVIDERS.md`
before using any of them.

Resolve the loaded skill directory, then run its read-only doctor when Python is
available:

```bash
python3 <skill-dir>/scripts/doctor.py --root <repo-root>
```

Use the report to identify candidate UI apps, package managers, commands,
Playwright setup, hosting configuration, and existing `ui-kit.json` manifests.
When the user names an existing kit, match by manifest name/slug, show collisions,
and confirm the chosen path instead of making them remember it.

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
  "approvals": {},
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

Validate state after each transition when the bundled validator is available:

```bash
python3 <skill-dir>/scripts/validate-kit.py <state.json>
```

Prefer the bundled state controller so legal transitions, explicit gate
receipts, atomic writes, target migration, and hand-edit detection are enforced:

```bash
python3 <skill-dir>/scripts/state.py status <state.json>
python3 <skill-dir>/scripts/state.py advance <state.json>
```

`status` reports stale generated artifacts, and `advance` refuses to move while
any recorded file is missing or its hash has drifted. Route backward or inspect
and adopt the hand edit instead of bypassing that check.

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
| `verify` | Verification, performance, and critique reports plus production artifacts | Required checks, budgets, consumer/host smoke tests, and critique complete |
| `release-gate` | User review decision with critique recommendation and accepted limitations | User explicitly approves reuse or names revisions |
| `handoff` | Version, changelog, reuse/hosting docs and migration notes | A fresh consumer can follow the documented path |
| `iterate` | Updated request mapped to affected phases | Route to the earliest invalidated contract or no-op |

## 3. Hard gates

Hard gates require explicit approval. An approval already present in the user's
request counts; never ask twice.

Hard-gate approval does not implicitly authorize external provider mutations.
Before the Name gate, any Paper write requires exact per-action file/node scope;
the Name gate may approve a continuing collaborative-canvas scope for later
phases. ui.sh installation is always a separate project mutation approved at
the Name gate or explicitly in the request.

1. **Direction gate** — approve the synthesis and exclusions. Remain in
   `direction-gate` until approval, then set `phase: "name-gate"`.
2. **Name gate** — approve name, slug, destination, stack, public API, dependency
   additions, provider installation/tooling, collaborative-canvas write scope,
   and hosting strategy before durable implementation. Then migrate state and
   set `phase: "plan"`.
3. **Release gate** — review the production-built showcase and accepted
   limitations before calling the kit reusable. Then set `phase: "handoff"`.

When using the state controller, leave a gate with `advance --approve
--rationale <summary>`. The rationale records the user's decision without
requiring verbatim conversation or private content.

## 4. Execute the routed phase

### Intake through synthesis

Read [REFERENCES.md](REFERENCES.md). For navigable sources also read
[PLAYWRIGHT.md](PLAYWRIGHT.md). Do not advance Capture based only on screenshots
when the source was accessible and interactive behavior matters.
For video or animated references, read [RECORDINGS.md](RECORDINGS.md) and keep
observed, inferred, and unknown behavior distinct.
For Paper or Refero inputs, read [PROVIDERS.md](PROVIDERS.md); provider metadata
does not replace Playwright evidence for a runnable interface.

### Plan through handoff

Read [BUILD.md](BUILD.md). Use [PLAYWRIGHT.md](PLAYWRIGHT.md) for the feedback
loop and production traversal. Verify the built artifact, not only a dev server.
After mechanical checks pass, read [CRITIQUE.md](CRITIQUE.md) completely and
perform its fresh production review before the Release gate.
Read [QUALITY.md](QUALITY.md) when the kit ships portable tokens/assets, changes
an existing public contract, composes with another kit, or retains visual
baselines.
Read [PROVIDERS.md](PROVIDERS.md) before invoking any installed ui.sh skill.

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
- Use `state.py record-file`; adopt a hand edit with `--accept-current` only
  after inspecting it and deciding it is authoritative.
- Re-running a completed phase verifies its outputs and no-ops when they remain
  valid.
- On a partial write, retain the last completed phase and record partial files.
  Repair or remove only confirmed partial output on resume.
- If a source disappears, retain prior observations as stale and request a
  replacement only when the missing evidence blocks the current phase.
- If a target moves, find the manifest by kit name, confirm the move, and update
  state paths without rebuilding the kit. Use `state.py relocate --target
  <path> --confirm-slug <slug>` to verify the destination manifest before the
  path changes.
- Routing backward clears approvals for invalidated gates and later gates;
  retain earlier approvals only when their contracts still hold.
- Stop all managed reference/showcase processes and delete ephemeral auth state
  at completion or before a blocking handoff unless the user asks to retain them.
- For Paper writes, persist the approved file/node scope and before/after node
  identifiers. On interruption, re-read the live file before continuing; never
  assume a partially applied external mutation rolled back.
- Validate the state and `ui-kit.json` manifest with the bundled validator before
  Release and Handoff. Use `--check-files` once durable paths and hashes exist.

## Completion report

```text
Kit: <name> v<version>
Phase: <iterate|blocked phase>
View: <command and URL/path>
Reuse: <public entry point>
Evidence: <source-ledger path and policy>
Verified: <checks run>
Performance: <budgets met or accepted exceptions>
Critique: <approve|revise|approve-with-limitations and report path>
Integrations: <Paper/Refero/ui.sh modes used, or none>
Open: <accepted limitations or next gate>
```
