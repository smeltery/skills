# Evaluation, Interoperability, and Reuse Quality

Use this guide when evaluating UI Studio itself, approving visual baselines,
shipping portable tokens/assets, or composing more than one named kit.

## Quality benchmark

The bundled benchmark corpus covers dashboards, marketing, commerce, forms,
mobile flows, localization/RTL, component catalogs, and adverse service states.
It uses evidence-backed pass/fail contracts rather than aesthetic scores.

```bash
python3 scripts/benchmark.py plan fixtures/benchmark/benchmark.json
python3 scripts/benchmark.py evaluate <suite.json> <results.json>
```

Each result names a scenario, required contract, `pass|fail|not-run` status, and
specific evidence. Missing evidence cannot pass. Run affected archetypes after
changing generation, verification, accessibility, or reference-synthesis rules.
Do not claim the whole suite passed when only tooling fixtures ran.

## Structured browser observations

`make-capture.py` emits both `evidence.json` and `observations.json`. The latter
contains bounded structure counts and computed layout/style samples without
retaining page copy or source CSS. Use it to infer repeated typography, spacing,
color, geometry, motion, and breakpoint traits; it is evidence, not a token
extraction license. Validate it with schema `observation` and disclose sampling
limits.

## Production verification receipt

Generate a verifier beside the Playwright capture harness:

```bash
python3 scripts/make-verifier.py <ui-kit.json> \
  --base-url <production-preview-url> --route / --out <ignored-test-directory>
```

Use `--missing-route-policy status` when the host must return an HTTP error, or
`rendered` when an SPA deliberately preserves the missing path and renders its
own not-found surface. Choose from the approved hosting contract rather than
making the verifier infer policy from an arbitrary response body.

The generated spec records route/deep-link/refresh behavior, asset and console
failures, horizontal overflow, keyboard focus movement, base paths, and missing
routes into `verification.json`. It supplements rather than replaces the manual
accessibility matrix, hosting-header review, critique, or product-specific flow
tests.

## Public compatibility and composition

`compare-kits.py` compares manifest entry points, package exports, exported type
declarations, design-token paths/values, CSS custom properties, themes, peers,
and public scope. Its version recommendation is a lower bound; changed token or
CSS values require human review even when names remain compatible.

Before consuming multiple kits, run:

```bash
python3 scripts/compose-kits.py <kit-a/ui-kit.json> <kit-b/ui-kit.json>
```

Resolve duplicate identities, incompatible peer majors, conflicting CSS custom
properties, and unscoped global selectors. Shared names with equal values still
need an explicit ownership decision.

## DTCG-compatible tokens

Prefer Design Tokens Community Group-shaped token JSON using `$value`, `$type`,
inherited group types, and optional `$description`. Preserve aliases and rich
values as JSON; never stringify them into CSS prematurely.

```bash
python3 scripts/tokens.py validate tokens.json
python3 scripts/tokens.py flatten tokens.json flat-tokens.json
python3 scripts/tokens.py expand flat-tokens.json tokens.json
```

Flattening is for interchange and diffing. Expansion recreates hierarchy from
dotted paths but cannot recover group descriptions that were not retained.

## Visual approval

Use Playwright `toHaveScreenshot` for repository-native perceptual comparison.
The bundled baseline tool adds an explicit approval record and exact artifact
inventory:

```bash
python3 scripts/visual-baselines.py approve <screenshots> visual-baseline.json \
  --kit <name> --version <version> --rationale <decision> --approve
python3 scripts/visual-baselines.py compare visual-baseline.json <screenshots>
```

Never approve reference-site screenshots as generated-kit baselines. Review
every added, removed, or changed image; exact hashes detect drift but do not
explain whether a visual change is acceptable.

## Asset provenance

Copy `templates/provenance.json`, record every shipped font, icon, image,
illustration, reused code asset, and relevant dependency, then run:

```bash
python3 scripts/provenance.py provenance.json --root <kit-root>
```

The checker finds uninventoried common asset files, duplicate records, missing
assets, and missing license files. It cannot determine legal compatibility;
retain verified license identifiers, attribution, source, and rights decisions.

## Framework portability

The portability fixture consumes one public kit package from React, Vue, Svelte,
and native web components. It tests public JavaScript/styles, SSR-safe browser
boundaries, dependency pinning, and production builds without making any one
framework the default for generated kits.

```bash
python3 scripts/check-portability.py
./scripts/dogfood-portability.sh
```

Use the repository's supported framework versions for a real kit. The fixture's
pinned versions validate UI Studio itself and are not recommendations for user
projects.
