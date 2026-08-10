# /ui-studio

Use Playwright CLI to investigate live websites, runnable repository UIs, or
curated design-library references such as Mobbin, then turn the evidence into an
original, named UI kit with reusable tokens and components, representative
compositions, and a runnable, hostable showcase.

The skill studies references as evidence rather than cloning them. It navigates
and exercises reference interactions with Playwright CLI, applies explicit
rights and evidence-retention policies, synthesizes a coherent design language,
waits at three meaningful gates, verifies real package consumption and
production hosting, and preserves state for safe later iteration.

## Lifecycle

```mermaid
stateDiagram-v2
  [*] --> Intake
  Intake --> Capture
  Capture --> Synthesize
  Synthesize --> DirectionGate
  DirectionGate --> NameGate: direction approved
  NameGate --> Plan: name, target, API approved
  Plan --> Scaffold
  Scaffold --> Foundations
  Foundations --> Components
  Components --> Compositions
  Compositions --> Showcase
  Showcase --> Verify
  Verify --> ReleaseGate
  ReleaseGate --> Handoff: showcase approved
  Handoff --> Iterate
  Iterate --> Capture: new references
  Iterate --> Components: compatible extension
  Iterate --> DirectionGate: system-level change

  DirectionGate --> Blocked: awaiting decision
  NameGate --> Blocked: awaiting contract
  Verify --> Blocked: required check fails
  ReleaseGate --> Blocked: awaiting review
```

State is stored with the target at `.ui-studio/<kit-slug>/state.json`. The
filesystem and kit manifest remain authoritative, and generated-file hashes
prevent a resumed run from silently overwriting hand edits.

## Usage

```text
/ui-studio https://example.com https://example.org/products --kit Northstar
/ui-studio <mobbin-share-link> --kit Northstar
```

References may be URLs, Mobbin or comparable design-library deep links,
repositories, attached screenshots, or local paths. The user can also point a
later invocation at an existing kit and request another component, theme, page
composition, or visual direction.

For curated design libraries, the skill preserves screen order and flow context
instead of treating every frame as an unrelated image. If the provider requires
authentication, the user completes it in the isolated Playwright session; the
skill never handles their credentials.

A repository can be the reference even when no public site exists. The skill
discovers the relevant app, package manager, setup and start commands from that
repository, starts the UI as a managed local process, and feeds its actual served
URL into the Playwright investigation loop. It records the commit and runtime
recipe while leaving tracked reference files unchanged.

The skill requires Playwright CLI and a compatible browser for navigable web or
repository references, plus the build tools used by the reference and selected
target projects. It also uses Playwright CLI to exercise the finished showcase
at multiple viewports and inspect interaction, accessibility, console, and
network behavior.

Bundled dependency-free Python tools discover repository UI entry points and
named kits, validate runtime state and `ui-kit.json` manifests against portable
schemas, and report generated-file drift. A disposable dogfood runner exercises
the local Playwright path without retaining browser evidence.

The official Playwright path uses `codegen` for headed or user-authenticated
exploration and short scratch Playwright Test specs for repeatable autonomous
capture. Agent-oriented Playwright CLIs are supported when their own help exposes
interactive session commands; the skill never invents unavailable commands.

## Tooling

```bash
python3 scripts/doctor.py --root /path/to/repository
python3 scripts/validate-kit.py --check-files /path/to/kit
./scripts/dogfood.sh
```

The doctor does not execute discovered repository scripts. The dogfood runner
uses a disposable copy and may download Playwright Test or Chromium when they are
not already available; see `DOGFOOD.md` for overrides and host prerequisites.

## Install

```bash
npx skills@latest add dotbrains/skills
```

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition consumed by the agent.
- [`REFERENCES.md`](./REFERENCES.md) — intake, rights, privacy, repository and
  curated-reference capture, evidence ledger, and design synthesis.
- [`PLAYWRIGHT.md`](./PLAYWRIGHT.md) — executable browser exploration and
  production-verification protocol.
- [`BUILD.md`](./BUILD.md) — foundations, components, distribution, showcase,
  consumer testing, performance budgets, hosting, release, and handoff.
- [`CRITIQUE.md`](./CRITIQUE.md) — evidence-based structural and finish review
  before the Release gate.
- [`DOGFOOD.md`](./DOGFOOD.md) — automated local and manual acceptance matrix
  for the skill itself.
- [`schemas/`](./schemas/) — portable state and kit-manifest contracts.
- [`templates/`](./templates/) — source-ledger and critique-report starting
  points.
- [`scripts/doctor.py`](./scripts/doctor.py) — read-only UI/tooling/kit discovery.
- [`scripts/validate-kit.py`](./scripts/validate-kit.py) — dependency-free schema,
  path, and generated-hash validation.
- [`scripts/dogfood.sh`](./scripts/dogfood.sh) — disposable local Playwright
  acceptance run using the bundled fixture.
- [`fixtures/`](./fixtures/) — static reference app and Playwright dogfood
  harness used only in disposable copies.
