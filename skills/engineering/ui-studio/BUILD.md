# Kit Build and Verification

Use this guide for `plan` through `handoff`, and for implementation iterations.

## Plan and Name gate contract

Before durable implementation, present and receive approval for:

- display name, filesystem/package-safe slug, destination, and detected stack;
- public tokens, components, patterns, compositions, and showcase surfaces;
- dependency additions and peer-dependency policy;
- development, validation, production-build, preview, and hosting strategy;
- discovered performance baselines or the plan for establishing them, with
  repository-appropriate budgets and repeatable commands;
- rights and artifact policies plus evidence that can enter the repository;
- a scenario matrix derived from real content pressure and adverse states.

Write a dependency-ordered plan: scaffold -> foundations -> components ->
compositions -> showcase -> consumer and production verification.

## Scaffold and manifest

Integrate with the existing workspace when present. For greenfield work, choose a
widely supported stack suited to the host, explain it at the Name gate, pin
dependencies with a lockfile, and provide one command each for development,
validation, production build, and production preview.

Create `ui-kit.json` or an idiomatic manifest containing:

- schema version, kit name/slug/version, stack, and destination;
- public JavaScript/type, style, token, and asset entry points;
- themes, supported environments, browser targets, and host/base-path rules;
- peer and runtime dependencies;
- source-ledger and durable design-decision paths;
- machine-readable evidence index and production verification receipt paths
  when retained by policy;
- asset-provenance report and approved generated-kit visual-baseline path when
  those artifacts exist;
- development, validation, build, preview, and consumer-smoke commands.
- performance budgets with units, baseline, limit, expected variance, command,
  and rationale.

Write concise install, run, import, theme, extension, versioning, migration, and
hosting instructions.

## Foundations

Implement semantic tokens before components. Separate primitives from semantic
roles and component aliases. Cover the properties the design actually uses:
typography, color, spacing, sizing, radii, borders, elevation, motion,
breakpoints, density, and layering.

Prefer CSS custom properties or the target stack's native theme contract so
consumers can override semantics without forking. Document fonts, icons, and
assets with provenance, license, loading/fallback behavior, and failure modes.
Do not hide one-off component values in a token system.

When tokens must cross tools or repositories, use the DTCG-compatible workflow
in `QUALITY.md`. Preserve semantic hierarchy and typed rich values; flattened
tokens are an interchange artifact, not the authoring source by default.

## Components and compositions

Build the smallest public component set that expresses the approved surfaces.
Every public component needs:

- a typed or clearly documented API and composition slots where appropriate;
- default, interactive, disabled, loading, empty, error, overflow, long-copy,
  and high-volume behavior when applicable;
- keyboard, focus-visible, accessible-name, screen-reader, reduced-motion, and
  touch behavior;
- responsive behavior driven by content pressure, not only device labels;
- realistic showcase fixtures from the scenario matrix.

Prefer composition over a large prop matrix. Do not bake reference-site names,
page copy, or application business logic into primitives.

Build representative pages and flows only from public components. Cover sparse,
typical, dense, adverse, narrow, wide, zoomed, localized/RTL, and touch scenarios
when relevant. Model meaningful behavior with an explicit reducer or state
machine rather than scattered booleans.

## Distribution contract

Make reuse real rather than aspirational:

- expose intentional package exports for runtime code, types, tokens, styles,
  themes, and assets;
- classify peer versus bundled dependencies and avoid duplicate framework copies;
- declare style side effects deliberately and preserve tree-shaking elsewhere;
- separate server-safe and client-only entry points when the stack requires it;
- avoid browser globals during server rendering unless isolated behind a client
  boundary;
- keep asset URLs, fonts, and CSS functional under the supported base path;
- document theming order and required global style imports.

Create a minimal consumer fixture outside the package source. Install or link the
built artifact through the documented public entry point, import its types and
styles, render representative components, and run its build. An internal relative
import from the showcase does not satisfy the consumer test.

## Showcase

Create a navigable story catalog or showcase exposing:

- kit name and version;
- foundations and themes;
- every public component state;
- representative compositions and flows;
- scenario, theme, and viewport controls or clearly linked routes;
- safe fixture data and stubbed actions only.

It must run with one documented command, build for production, and be hostable on
the user's target or as static files when supported. Make review routes easy to
share. Use Playwright after each meaningful slice.

## Verification matrix

Use repository-native checks first. Add dependencies only when approved.

- clean locked install and production build;
- lint, type checking, focused unit/component tests, and public type declarations;
- consumer-fixture install/link, import, render, and build;
- automated accessibility checks when tooling exists, plus keyboard-only and
  screen-reader-semantic review; do not imply Playwright core includes an axe
  scanner;
- focus visibility, contrast, zoom, reduced motion, long text, themes,
  localization/RTL, touch/pointer behavior, and content extremes where relevant;
- no unexplained console errors, page errors, failed requests, horizontal
  overflow, clipped content, or hydration warnings;
- Playwright traversal of all showcase routes and representative interactions;
- visual review against the approved direction, never pixel equality with a
  reference source;
- provenance, license, privacy, and artifact-policy audit.

Use `QUALITY.md` for the machine-readable provenance inventory, generated
production verifier, and explicit visual-baseline approval workflow.

Start accessibility verification from
`templates/accessibility-scenarios.json`. Decide applicability explicitly for
keyboard operation, names/roles/states and announcements, focus restoration,
200–400% zoom, forced colors, reduced motion, reduced transparency, RTL, and
touch/pointer behavior. `not-applicable` requires evidence and rationale; it is
not a shortcut around a failing scenario. Use existing automated accessibility
tooling when available, but retain manual semantic and interaction checks.

## Performance budgets

Discover existing bundle, page-weight, rendering, interaction, and hosting
budgets before inventing new ones. Reuse the repository's measurement commands
and production mode. If none exist:

1. establish a repeatable production baseline after Scaffold;
2. select only metrics relevant to the approved surface, such as compressed
   public entry-point/CSS size, font/asset weight, request count, layout shift,
   interaction latency, long tasks, or animation frame stability;
3. record environment, fixture, sample count, unit, baseline, expected variance,
   limit, command, and rationale in `ui-kit.json`;
4. receive user approval at the Name gate when a budget would materially alter
   scope or dependencies.

Do not hardcode universal thresholds or present local lab measurements as field
performance. Compare equivalent builds and fixtures, use multiple samples for
noisy timing, and block Release on a required regression unless the user accepts
the named exception. A smaller bundle does not excuse worse interaction or
accessibility.

After the ordinary build passes, serve the production output using the intended
host strategy. Verify direct deep links, browser refresh, nested routes, asset and
font URLs, configured base paths, caching assumptions, and a missing-route case.
Static-host targets must be tested from the generated static directory rather
than the development server.

Copy `templates/verification.json` to a durable or ignored location according
to policy. Record observed status, deep-link and refresh behavior, asset
failures, base-path behavior, missing-route handling, cache assumptions, and the
accessibility scenario results. Validate it with `validate-kit.py --schema
verification`; do not mark booleans true without exercising the deployed or
production-preview behavior they represent.

Visual baselines may be established for the generated kit after the direction is
approved. Store only allowed evidence. Review every baseline update; do not mask
change with broad thresholds or compare copyrighted references pixel-for-pixel.

After mechanical and performance verification, follow `CRITIQUE.md` in a fresh
production browser context. Resolve blockers and route substantive revisions to
the earliest affected phase before presenting the Release gate.

## Release and handoff

At the Release gate provide:

- production preview command and URL or built artifact path;
- showcase route inventory and review checklist;
- kit name/version and public entry points;
- checks run with results;
- performance budgets with baseline, result, variance, and accepted exceptions;
- critique recommendation and report path;
- evidence policy and retained artifacts;
- asset provenance, visual-baseline decision, and public compatibility result;
- accepted limitations and proposed next components.

After approval, update the manifest, changelog, reuse/hosting docs, and any
versioned migration notes. Do not publish, deploy externally, or modify a
consuming product unless the user requested the exact destination action.

Before versioning an iteration, compare the last released and proposed
manifests:

```bash
python3 <skill-dir>/scripts/compare-kits.py \
  <released-ui-kit.json> <proposed-ui-kit.json> --fail-on-breaking
```

Treat the result as a lower bound: removed or changed public entries are
breaking, but component API and behavioral changes still require repository
native type, test, and migration review.
When more than one named kit enters the same consumer, run `compose-kits.py` and
resolve peer, token, global-style, and identity conflicts before Release.
