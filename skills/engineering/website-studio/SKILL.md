---
name: website-studio
description: Design, implement, and verify a complete polished website from a brief, an empty directory, or an existing repository. Use for autonomous website creation or substantial redesign with evidence-backed gates for content, visual design, user journeys, responsive behavior, accessibility, and production readiness. Use ui-studio instead for a reusable UI kit or component showcase, and design for a proposal without implementation.
argument-hint: "<brief or repo> [reference URLs...] [--target <path>]"
---

# Website Studio

Deliver a complete, distinctive website whose real user journeys work. Own the
decisions, implementation, browser review, and repairs through completion.
Do not stop at a plan, a hero mockup, or a list of improvements for the user.

## Autonomy contract

The gates below are evidence gates cleared by the agent, not approval meetings.
Choose a coherent direction, write down reasonable assumptions, and proceed.
Honor existing brand, content, stack, integrations, and user decisions. Ask only
when a missing fact prevents a truthful or authorized result; finish independent
work while waiting. Do not ask the user to choose fonts, spacing, or section order.

Building locally is the default delivery scope. Follow any existing permission
to commit, push, or deploy; the skill itself grants none. If publishing is not
authorized, finish and verify a production build locally. Missing credentials
must not turn a form into fake success or a local preview into a claimed launch.

Do not invent testimonials, customers, credentials, metrics, addresses, pricing,
or legal claims. For an unspecified business, choose an explicitly fictional
concept and original copy. For a real business, use verified facts, omit optional
unknown claims, and report essential missing content. Never silently publish a
fictional identity as a real business.

## Start and resume

1. Read repository instructions, inspect the worktree, and locate the actual web
   app. Preserve unrelated work. For a supplied repo URL, use a fresh local clone
   if needed; do not overwrite an existing checkout. With no repo, create a
   descriptive directory in the user's workspace and record the assumption.
2. Discover available browser, screenshot, test, asset-generation, and deployment
   tools. Use their supported interfaces; no particular provider is required.
3. Resolve this skill's installed directory. Read
   [the gate protocol](references/gate-protocol.md), then initialize state:

   ```bash
   python3 <skill-dir>/scripts/gates.py init --root <project-root>
   python3 <skill-dir>/scripts/gates.py status --root <project-root>
   ```

4. Keep reports, screenshots, command logs, and state in
   `<project-root>/.website-studio/`. Keep this local evidence out of deployment
   and version control by default. Durable setup/content documentation belongs
   in the project's existing docs convention. Never store secrets or form PII.
5. On resume, inspect current files and run `status`; continue at the earliest
   missing or stale gate. Never reset state merely to bypass a failure.

Python 3.10+ is needed only for the controller. If unavailable, keep the same
ordered receipts manually and disclose that automated gate enforcement was
unavailable. A browser is required to pass rendered UX and visual gates; source
inspection alone cannot substitute for it.

## Gate sequence

Read each linked guide before its first relevant gate. A pass requires the
observable results below and a receipt accepted by the controller. Every gate
is required; conditional features are evaluated against the declared site scope.

| Gate | Required checks | Evidence needed to proceed |
| --- | --- | --- |
| `context` | `brief`, `baseline`, `scope` | Audience, purpose, primary action, known facts/assumptions; existing route/feature inventory and commands; local/publish scope |
| `references` | `observations`, `source-review`, `translation` | Browser observations and available repo inspection; justified design principles; inaccessible sources disclosed |
| `direction` | `thesis`, `tokens`, `composition` | Chosen visual direction, content hierarchy, tokens, asset plan, and a concrete desktop/mobile composition |
| `structure` | `routes`, `content`, `journeys` | Complete route/content matrix, genuine copy and asset provenance, CTA destinations and interaction states |
| `build` | `runnable`, `complete`, `maintainable` | Clean install/build; every planned page and asset implemented; shared components, documented commands, lean dependencies |
| `journeys` | `navigation`, `primary-flow`, `adverse-states` | Browser execution of navigation and every primary journey, including failures, empty states, and recovery |
| `responsive` | `viewports`, `reflow`, `input-modes` | Inspected screenshots across mobile/tablet/desktop; no clipping; touch, keyboard, zoom, and motion behavior |
| `accessibility` | `semantics`, `keyboard`, `audit` | Semantic and contrast review; keyboard-only completion; automated audit findings fixed and manual checks recorded |
| `discovery` | `metadata`, `assets`, `crawl` | Route-specific metadata, social/favicon assets, valid links, correct errors and production indexing rules |
| `performance` | `budgets`, `measurements`, `regressions` | Production measurements against declared budgets; optimized media/fonts/JS; applicable tests and CI checks pass |
| `critique` | `visual-review`, `consistency`, `repairs` | Fresh rendered review of every page family, resolved visual/UX defects, and verified repair evidence |
| `delivery` | `reproducible`, `scope-complete`, `handoff` | Final production smoke, instructions, and authorized deployment/CI verification or explicitly local delivery |

Use [design and content guidance](references/design.md) for `context` through
`structure`, [implementation and UX checks](references/ux-checks.md) for `build`
through `discovery`, and [verification and delivery](references/verification.md)
for `performance` through `delivery`.

## Execute without dropping requirements

- Before coding, create a route matrix: route, visitor task, content source,
  primary/secondary actions, data source, interaction states, and verification.
  Map every requested feature to a row. Include existing routes to preserve.
- Maintain an issue list with route, viewport, reproduction, severity, fix, and
  retest evidence. An unchecked item is pending, never implicitly passed.
- Build all contracted routes, then use the production preview for verification.
  Inspect desktop and mobile captures, not just whether a screenshot file exists.
- Run the gate checks, write the receipt, and use `pass` to advance. Failed or
  missing evidence blocks dependent phases. Continue independent fixes.
- When a change invalidates a passed gate, invalidate it and all later gates,
  repair the cause, and rerun affected verification. Do not blindly replay
  scaffolding, overwrite user edits, or refresh hashes without rerunning checks.
- At `critique`, inspect the product afresh as a visitor. Repair visible hierarchy,
  density, crop, wrapping, affordance, and interaction problems before delivery.
  Automated lint and accessibility scores do not prove a good design.
- Persist progress before context limits or interruptions. Keep the same target,
  scope, decisions, receipts, and issue list across sessions.

## Completion and stopping rules

Complete only when every gate passes, all promised routes and journeys work,
and no required defect remains. Do not lower budgets, remove features, mute
errors, or mark failed checks inapplicable to manufacture completion.

If a dependency is unavailable, retain the failed gate with the concrete error
and completed work. Try a compatible local alternative within scope. If repeated
attempts produce no new evidence, stop with the narrow blocker and resume command;
do not claim the website is verified. Optional polish can be deferred only when
it does not weaken the agreed design or a required journey.

Report the website path or authorized URL, chosen direction, completed journeys,
checks actually run, evidence location, and any remaining blocker. Distinguish
local production preview, deployed preview, and live production. Leave a usable
preview running when the environment supports it and identify its command/URL.

## Supporting material

- [Reference study](references/reference-study.md): the five original examples
  and inspected repository patterns. Calibration, not a template or dependency.
- [Evaluation scenarios](references/evaluation.md): validate changes to this skill
  against empty, existing, broken, interrupted, and inaccessible projects.
