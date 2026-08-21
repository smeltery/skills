# Available skills

Each skill directory contains its own `README.md` (with usage and any diagrams)
and the canonical `SKILL.md` consumed by the agent.

Unless noted below, every skill works both ways: the agent can load it on its
own when the description matches the work, and you can invoke it directly with
`/<skill-name>`. The exceptions are marked inline — **user-invoked only**
(`disable-model-invocation: true`) or **model-invoked only**
(`user-invocable: false`). See [Invocation](../README.md#invocation) for the
reasoning.

## Engineering

Skills for code work — bug-hunting, design, planning, review, and execution.

- **[architecture](../skills/engineering/architecture/README.md)** — Create or update root `ARCHITECTURE.md` from verified implementation: source of truth, dependency direction, trust boundaries, and critical-flow walkthroughs.
- **[architecture-review](../skills/engineering/architecture-review/README.md)** — Read-only review of a technical proposal before implementation, with Blocker/Important findings and an Approve/Request-changes/Blocked verdict.
- **[branch-conventions](../skills/engineering/branch-conventions/README.md)** — Standard branch naming and creation flow using conventional prefixes and an up-to-date default branch.
- **[ci-monitoring](../skills/engineering/ci-monitoring/README.md)** — Monitor GitHub PR checks, rerun failed jobs when appropriate, and confirm merge-readiness.
- **[cloud-factory](../skills/engineering/cloud-factory/README.md)** — Convert a GitHub repository into a cloud software factory with agent skills, workflow triggers, labels, and domain-doc placeholders.
- **[commit-conventions](../skills/engineering/commit-conventions/README.md)** — Keep commit messages aligned with branch intent using conventional commit types.
- **[design](../skills/engineering/design/README.md)** — Write a rigorous design document for a proposed change, with numbered `INV-n` invariants and `AC-n` acceptance criteria that stay stable through review and verification.
- **[diagnose](../skills/engineering/diagnose/README.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **[feature-gap](../skills/engineering/feature-gap/README.md)** — Compare a source GitHub repository against a destination repository, identify real missing functionality, implement it destination-natively, then commit and push to the destination default branch.
- **[git-commit](../skills/engineering/git-commit/README.md)** — Safe commit-message workflow using temp files and `git commit -F` to avoid shell-substitution pitfalls.
- **[git-safety](../skills/engineering/git-safety/README.md)** — Guardrails for safe git operations: stash/cherry-pick preference, force-push constraints, and destructive-command avoidance.
- **[grill-with-docs](../skills/engineering/grill-with-docs/README.md)** — Code-aware grilling session that challenges your plan against the existing domain model and updates `CONTEXT.md` / ADRs inline.
- **[html-doc](../skills/engineering/html-doc/README.md)** — Render a finished Markdown PRD or design into one verified, self-contained static HTML reading view; Markdown stays canonical.
- **[improve-codebase-architecture](../skills/engineering/improve-codebase-architecture/README.md)** — Surface architectural friction and propose deepening opportunities — refactors that turn shallow modules into deep ones.
- **[lean-diff](../skills/engineering/lean-diff/README.md)** — Keep the net diff as small as possible on every code change — targeted edits over rewrites, no drive-by reformatting, and a running diff-size nudge after every edit.
- **[loc-budget](../skills/engineering/loc-budget/README.md)** — Find large line-count hitters, modularize them into cohesive files, and add file-size and flat-directory budget gates in the repo's idiomatic tooling.
- **[performance-engineer](../skills/engineering/performance-engineer/README.md)** — Measure, diagnose, and improve software performance on a specific critical path with bounded experiments and before/after evidence.
- **[pr-monitor](../skills/engineering/pr-monitor/README.md)** — One-pass PR monitor that processes bot review feedback, CI failures, and merge-readiness signals.
- **[pr-workflow](../skills/engineering/pr-workflow/README.md)** — Create and update PRs with clear reviewer-focused descriptions and mergeability checks.
- **[port](../skills/engineering/port/README.md)** — Port an upstream GitHub repository into a fresh private destination repository with a new identity, clean single-commit history, detailed docs, CI/pre-commit/Flox setup, structure cleanup, and upstream-reference sanitization.
- **[prototype](../skills/engineering/prototype/README.md)** — Build a throwaway prototype to flush out a design before committing to it. Routes between an interactive terminal app for state/logic questions, or several radically different UI variations on one route.
- **[review](../skills/engineering/review/README.md)** — Read-only, high-signal review for pull requests or local change sets using scope, ticket context, full diff context, and relevant tests.
- **[simplify](../skills/engineering/simplify/README.md)** — Make a finished code change easier to read without changing behavior by tightening names, comments, concepts, and structure before human review.
- **[tdd](../skills/engineering/tdd/README.md)** — Test-driven development with a red-green-refactor loop. Vertical slices via tracer bullets — one test, one implementation, repeat.
- **[to-issues](../skills/engineering/to-issues/README.md)** — Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices.
- **[to-prd](../skills/engineering/to-prd/README.md)** — Turn the current conversation context into a PRD and publish it to the project issue tracker.
- **[triage](../skills/engineering/triage/README.md)** — Move issues through a small state machine of triage roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`).
- **[ui-studio](../skills/engineering/ui-studio/README.md)** — Use Playwright CLI to investigate live websites, runnable repository UIs, or curated references such as Mobbin, then create an original, named UI kit with reusable components and a runnable showcase.
- **[verify](../skills/engineering/verify/README.md)** — Prove that a code change meets its acceptance criteria, mapping every `AC-n`/`INV-n` ID to concrete automated or browser evidence.
- **[wayfinder](../skills/engineering/wayfinder/README.md)** — Plan work too large or unclear for one agent session by creating an issue-tracker map and resolving one frontier decision ticket at a time.
- **[workon](../skills/engineering/workon/README.md)** — Pick up a Linear ticket end-to-end: worktree, implement, PR, then watch the PR on a 5-minute loop addressing review comments, CI failures, and merge conflicts until merged.
- **[workon-event](../skills/engineering/workon-event/README.md)** — Event-driven `/workon` companion that handles one ticket event per invocation via a dispatcher. _Model-invoked only — the harness supplies the event payload._
- **[zoom-out](../skills/engineering/zoom-out/README.md)** — Tell the agent to zoom out and give a higher-level perspective on an unfamiliar section of code. _User-invoked only._

## Productivity

General workflow skills, not code-specific.

- **[caveman](../skills/productivity/caveman/README.md)** — Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler while keeping full technical accuracy.
- **[grill-me](../skills/productivity/grill-me/README.md)** — Get interviewed relentlessly about a plan or design until every branch of the decision tree resolves.
- **[handoff](../skills/productivity/handoff/README.md)** — Compact the current conversation into a handoff document so another agent can pick up the work.
- **[linear](../skills/productivity/linear/README.md)** — Use the `linear` CLI to search Linear, inspect issues, manage comments, list workspace metadata, and check Linear platform status.
- **[taste-review](../skills/productivity/taste-review/README.md)** — Get an independent judgment on an ambiguous design, prose, naming, or formatting choice, then weigh and apply the recommendation when authorized.
- **[teach](../skills/productivity/teach/README.md)** — Teach the user a new skill or concept across multiple sessions, building durable lessons and reference docs in a teaching workspace. _User-invoked only._
- **[track-my-work](../skills/productivity/track-my-work/README.md)** — Personal standup logger: pulls your recent Linear and GitHub activity into a Notion Standup Log, classifies it by impact/type, cross-links PRs to tickets, and prompts for anything not auto-captured.
- **[unslop](../skills/productivity/unslop/README.md)** — Strip AI writing tells out of a piece of text and put a real voice back in before it ships.
- **[web-search](../skills/productivity/web-search/README.md)** — Search the web through a local browser daemon, fetch selected results, and extract pages as readable Markdown.
- **[wrap](../skills/productivity/wrap/README.md)** — End-of-session wrap-up: classify completion, persist a `RESUME HERE` handoff before prompting, write durable memory (episodes, reflections, insights), and surface anti-sycophantic highlights.
- **[wrap-resume](../skills/productivity/wrap-resume/README.md)** — Picker that reads the `RESUME HERE` blocks `/wrap` writes and lets you continue an unfinished session.
- **[write-a-skill](../skills/productivity/write-a-skill/README.md)** — Create new agent skills with proper structure, progressive disclosure, and bundled resources.
