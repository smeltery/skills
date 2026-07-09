# Available skills

Each skill directory contains its own `README.md` (with usage and any diagrams)
and the canonical `SKILL.md` consumed by the agent.

## Engineering

Skills for code work — bug-hunting, design, planning, review, and execution.

- **[branch-conventions](../skills/engineering/branch-conventions/README.md)** — Standard branch naming and creation flow using conventional prefixes and an up-to-date default branch.
- **[ci-monitoring](../skills/engineering/ci-monitoring/README.md)** — Monitor GitHub PR checks, rerun failed jobs when appropriate, and confirm merge-readiness.
- **[commit-conventions](../skills/engineering/commit-conventions/README.md)** — Keep commit messages aligned with branch intent using conventional commit types.
- **[diagnose](../skills/engineering/diagnose/README.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **[feature-gap](../skills/engineering/feature-gap/README.md)** — Compare a source GitHub repository against a destination repository, identify real missing functionality, implement it destination-natively, then commit and push to the destination default branch.
- **[git-commit](../skills/engineering/git-commit/README.md)** — Safe commit-message workflow using temp files and `git commit -F` to avoid shell-substitution pitfalls.
- **[git-safety](../skills/engineering/git-safety/README.md)** — Guardrails for safe git operations: stash/cherry-pick preference, force-push constraints, and destructive-command avoidance.
- **[grill-with-docs](../skills/engineering/grill-with-docs/README.md)** — Code-aware grilling session that challenges your plan against the existing domain model and updates `CONTEXT.md` / ADRs inline.
- **[improve-codebase-architecture](../skills/engineering/improve-codebase-architecture/README.md)** — Surface architectural friction and propose deepening opportunities — refactors that turn shallow modules into deep ones.
- **[pr-monitor](../skills/engineering/pr-monitor/README.md)** — One-pass PR monitor that processes bot review feedback, CI failures, and merge-readiness signals.
- **[pr-workflow](../skills/engineering/pr-workflow/README.md)** — Create and update PRs with clear reviewer-focused descriptions and mergeability checks.
- **[port](../skills/engineering/port/README.md)** — Port an upstream GitHub repository into a fresh private destination repository with a new identity, clean single-commit history, detailed docs, CI/pre-commit/Flox setup, structure cleanup, and upstream-reference sanitization.
- **[prototype](../skills/engineering/prototype/README.md)** — Build a throwaway prototype to flush out a design before committing to it. Routes between an interactive terminal app for state/logic questions, or several radically different UI variations on one route.
- **[review](../skills/engineering/review/README.md)** — Read-only, high-signal pull request review using PR description, ticket scope, full diff context, and PR-suggested tests. Returns Critical / Suggestions / Nits.
- **[tdd](../skills/engineering/tdd/README.md)** — Test-driven development with a red-green-refactor loop. Vertical slices via tracer bullets — one test, one implementation, repeat.
- **[to-issues](../skills/engineering/to-issues/README.md)** — Break a plan, spec, or PRD into independently-grabbable issues using tracer-bullet vertical slices.
- **[to-prd](../skills/engineering/to-prd/README.md)** — Turn the current conversation context into a PRD and publish it to the project issue tracker.
- **[triage](../skills/engineering/triage/README.md)** — Move issues through a small state machine of triage roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`).
- **[workon](../skills/engineering/workon/README.md)** — Pick up a Linear ticket end-to-end: worktree, implement, PR, then watch the PR on a 5-minute loop addressing review comments, CI failures, and merge conflicts until merged.
- **[workon-event](../skills/engineering/workon-event/README.md)** — Event-driven `/workon` companion that handles one ticket event per invocation via a dispatcher.
- **[zoom-out](../skills/engineering/zoom-out/README.md)** — Tell the agent to zoom out and give a higher-level perspective on an unfamiliar section of code.

## Productivity

General workflow skills, not code-specific.

- **[caveman](../skills/productivity/caveman/README.md)** — Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler while keeping full technical accuracy.
- **[grill-me](../skills/productivity/grill-me/README.md)** — Get interviewed relentlessly about a plan or design until every branch of the decision tree resolves.
- **[handoff](../skills/productivity/handoff/README.md)** — Compact the current conversation into a handoff document so another agent can pick up the work.
- **[teach](../skills/productivity/teach/README.md)** — Teach the user a new skill or concept across multiple sessions, building durable lessons and reference docs in a teaching workspace.
- **[track-my-work](../skills/productivity/track-my-work/README.md)** — Personal standup logger: pulls your recent Linear and GitHub activity into a Notion Standup Log, classifies it by impact/type, cross-links PRs to tickets, and prompts for anything not auto-captured.
- **[wrap](../skills/productivity/wrap/README.md)** — End-of-session wrap-up: classify completion, persist a `RESUME HERE` handoff before prompting, write durable memory (episodes, reflections, insights), and surface anti-sycophantic highlights.
- **[wrap-resume](../skills/productivity/wrap-resume/README.md)** — Picker that reads the `RESUME HERE` blocks `/wrap` writes and lets you continue an unfinished session.
- **[write-a-skill](../skills/productivity/write-a-skill/README.md)** — Create new agent skills with proper structure, progressive disclosure, and bundled resources.
