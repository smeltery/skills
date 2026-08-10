# Reference Intake and Synthesis

Use this guide for `intake`, `capture`, `synthesize`, and `direction-gate`.

## Input types

Accept any combination of:

- public, preview, or authenticated website URLs;
- local repository paths, repository clone URLs, or runnable worktrees;
- component-explorer or documentation URLs;
- curated screen, flow, pattern, or collection links such as Mobbin;
- design-file links when an authenticated connector is available;
- screenshots, image sets, screen recordings, and local HTML files;
- an existing named UI Studio kit.

Record whether each input is navigable, static, ordered, authenticated, and
versioned. Static evidence can supplement a navigable source but cannot prove
interaction behavior.

## Rights mode

Assign one mode to every source during Intake:

- `inspiration-only` — infer abstract traits; do not copy code, branded assets,
  proprietary copy, or distinctive trade dress.
- `behavior-reimplementation` — reproduce observable behavior using original
  implementation and presentation.
- `licensed-reuse` — reuse only the code/assets covered by a verified compatible
  license, preserving notices and attribution.
- `same-product-reuse` — reuse from a user-owned product or repository within
  the explicitly approved boundary.

If ownership, license, or allowed reuse is unclear, default to
`inspiration-only`. A request for “close adaptation” does not override rights.
Record provenance for every reused asset, font, icon set, and implementation.

## Artifact policy

Agree on an artifact policy before Capture:

```json
{
  "visibility": "public|internal|restricted",
  "commitEvidence": "never|redacted-only|approved",
  "retention": "session|until-release|manual",
  "redactions": ["credentials", "tokens", "personal-data", "private-copy"]
}
```

- Browser storage state, cookies, authorization headers, credentials, and raw
  request/response bodies are always local ephemeral artifacts and never
  committable.
- Treat screenshots, traces, videos, DOM/ARIA snapshots, console output, and
  network URLs as potentially sensitive.
- Redact personal data, account names, private copy, internal endpoints, and
  identifiers before approved evidence is persisted.
- Store evidence under ignored `.ui-studio/` runtime state unless the policy
  explicitly allows a redacted durable artifact.
- Delete session-scoped evidence and authentication state when Capture ends.

## Bring up a repository reference

Make the UI observable without altering tracked reference code:

1. Resolve the repository root, remote, current commit, worktree status, and
   applicable agent/contributor instructions.
2. Read the root and app READMEs, workspace manifests, lockfiles, version files,
   task-runner configuration, environment examples, and UI documentation.
3. Identify plausible entry points: web apps, component explorers, docs sites,
   examples, and desktop shells with web previews. Prefer the user's named app;
   otherwise disclose the best-evidence choice.
4. Inspect install, lifecycle, dev, seed, and fixture scripts before executing
   them. Treat unfamiliar repositories as untrusted code. Prefer an available
   sandbox/container for scripts with broad filesystem, credential, or network
   access. Stop for approval on suspicious postinstall steps, external writes,
   destructive seeds, or commands that require real secrets.
5. Use the repository's pinned runtime, package manager, lockfile, and frozen or
   immutable install mode when supported. Do not replace tooling or invent
   environment values.
6. Start the documented UI command as a managed process. Discover its host,
   port, base path, and readiness signal from configuration or output; do not
   assume framework defaults.
7. Record remote/path, commit, chosen app, reviewed scripts, bootstrap/start
   commands, served URL, fixture/auth mode, and limitations.
8. Compare worktree status before and after. Report generated tracked changes and
   revert none without the user's permission. Stop the managed process after
   Capture unless the next phase explicitly reuses it.

If required secrets or services are unavailable, block Capture with the exact
prerequisite. Do not patch a reference app merely to make it run unless the user
separately requests that change.

## Open a curated reference

For Mobbin and comparable providers:

1. Open the exact deep link with Playwright and record provider, title, platform
   or device, source application when displayed, and whether it is a screen,
   ordered flow, pattern, or collection.
2. Preserve screen order and grouping. Explore zoom, annotations, variants, and
   neighboring states only when they explain the requested product surface. Do
   not bulk-crawl a provider catalog.
3. When authentication is required, the user completes it in the isolated
   browser session. Follow the auth-state handling in `PLAYWRIGHT.md`.
4. If a link cannot be reopened, accept exported screens as static evidence and
   record that interaction, order, or metadata could not be verified.

Curated screens omit application context. Infer only visible traits; validate
hierarchy later with the user's real navigation, content, and adverse states.

## Capture ledger

Start each exploration with a question, for example: “How does navigation
collapse, and how do filters reveal state?” For each source record:

- source/revision, region or flow, timestamp, viewport/device, access limits;
- Playwright action path plus snapshot, screenshot, trace, or video identifiers;
- layout grid, density, spacing rhythm, type roles, semantic colors, borders,
  depth, imagery/icons, motion, and responsive transformation;
- navigation, disclosure, selection, feedback, error recovery, and keyboard
  behavior;
- content assumptions and scale limits;
- traits to adapt, transform, or reject with reasons;
- rights mode, provenance, licensing concerns, and artifact policy.

With multiple references, build a trait matrix. Weight sources by user priority,
product relevance, content similarity, and evidence quality. Resolve conflicts
into one coherent rule; do not average unrelated styles.

Capture completes only when every approved surface has behavioral evidence or a
disclosed gap. Never fabricate inaccessible or unobserved states.

## Synthesize an original direction

Produce:

- a one-sentence design thesis;
- three to five product-linked principles;
- information hierarchy and interaction model;
- type, spacing, sizing, color, shape, depth, imagery, icon, motion, breakpoint,
  density, and layering rules;
- explicit non-goals and rejected reference traits;
- a content scenario matrix covering sparse, typical, dense, long-copy, empty,
  loading, error, narrow, wide, zoomed, reduced-motion, and localization/RTL
  cases when relevant;
- two or three genuinely different visual direction boards when the direction
  is not already explicit.

Direction boards may be temporary HTML or images under ignored runtime state.
They must show hierarchy, typography, palette, density, shape, and representative
components—not only mood imagery. Preserve the approved thesis and rationale in
durable kit documentation after the Name gate.

Avoid generic “AI dashboard” defaults: arbitrary gradients, excess rounded
cards, decorative glass, repeated hero copy, and uniform whitespace without a
content reason. Sophistication comes from hierarchy, proportion, states,
content realism, and restraint.
