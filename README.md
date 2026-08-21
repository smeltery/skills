# skills

[![CI](https://github.com/dotbrains/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/dotbrains/skills/actions/workflows/ci.yml)
[![License: PolyForm Shield](https://img.shields.io/badge/License-PolyForm%20Shield-brightgreen.svg)](https://polyformproject.org/licenses/shield/1.0.0)

[![skills.sh](https://skills.sh/b/dotbrains/skills)](https://skills.sh/dotbrains/skills)

**Portable agent skills from [dotbrains](https://github.com/dotbrains).**

[Why these skills](#why-these-skills) · [Quickstart](#quickstart) · [Choose a skill](#choose-a-skill) · [All skills](#all-skills) · [Invocation](#invocation) · [Guides](#documentation)

## Why these skills

Coding agents are capable but directionless without guardrails. Left alone
they misalign on what you actually want, produce code that compiles but
doesn't behave, let a codebase rot faster than any human can track, and turn
a simple PR into an hours-long slog of review comments and flaky CI.

Each skill here targets one of those failure modes and encodes the workaround
so the agent does it without being asked. The set is deliberately broad but
each skill is narrow — install only what a given task needs.

See **[why these skills exist](./docs/motivation.md)** for the full
failure-mode breakdown and the four books behind it.

## Quickstart

```bash
npx skills@latest add dotbrains/skills
```

Pick the skills you want, choose the agents to install them on, and you're done.
Other install options (manual copy) are in
[docs/installation.md](./docs/installation.md).

## Choose a skill

Most work starts in one of these places. Ask what result you need next:

| You need... | Reach for |
| --- | --- |
| A quick orientation in unfamiliar code | [`zoom-out`](./skills/engineering/zoom-out/README.md) |
| A current `ARCHITECTURE.md` for the repo as it exists today | [`architecture`](./skills/engineering/architecture/README.md) |
| A decision about what to build next, before writing code | [`to-prd`](./skills/engineering/to-prd/README.md) (light) or [`design`](./skills/engineering/design/README.md) (rigorous, with `INV-n`/`AC-n` IDs) |
| A challenge to a proposal before implementation starts | [`architecture-review`](./skills/engineering/architecture-review/README.md) |
| Decided work split into ordered, independently-gradable tasks | [`to-issues`](./skills/engineering/to-issues/README.md) or [`wayfinder`](./skills/engineering/wayfinder/README.md) |
| A feature built test-first | [`tdd`](./skills/engineering/tdd/README.md) |
| A hard bug or perf regression run to ground | [`diagnose`](./skills/engineering/diagnose/README.md) |
| A ticket driven end-to-end — worktree, PR, and the review loop until merged | [`workon`](./skills/engineering/workon/README.md) |
| An independent, high-signal review of a diff or PR | [`review`](./skills/engineering/review/README.md) |
| Proof that a change meets its stated acceptance criteria | [`verify`](./skills/engineering/verify/README.md) |
| Cleaner code with the same behavior before merge | [`simplify`](./skills/engineering/simplify/README.md) |
| The smallest diff that still satisfies the task | [`lean-diff`](./skills/engineering/lean-diff/README.md) |
| A finished PRD or design turned into a readable HTML doc | [`html-doc`](./skills/engineering/html-doc/README.md) |
| A durable handoff before ending a session | [`wrap`](./skills/productivity/wrap/README.md) or [`handoff`](./skills/productivity/handoff/README.md) |

Small, clear changes don't need any of this — just make the change. These
skills earn their keep when the decision, the diagnosis, or the review is
worth getting right.

## All skills

<details>
<summary><strong>45 skills across two categories</strong> — expand for the full list, or see <a href="./docs/skills.md">docs/skills.md</a> for the annotated catalog.</summary>

### Engineering

Code work — bug-hunting, design, planning, review, and execution.

| Group | Skills |
| --- | --- |
| **Git & commits** | [branch-conventions](./skills/engineering/branch-conventions/README.md) · [commit-conventions](./skills/engineering/commit-conventions/README.md) · [git-commit](./skills/engineering/git-commit/README.md) · [git-safety](./skills/engineering/git-safety/README.md) |
| **Plan & shape work** | [wayfinder](./skills/engineering/wayfinder/README.md) · [grill-with-docs](./skills/engineering/grill-with-docs/README.md) · [to-prd](./skills/engineering/to-prd/README.md) · [design](./skills/engineering/design/README.md) · [to-issues](./skills/engineering/to-issues/README.md) · [triage](./skills/engineering/triage/README.md) · [html-doc](./skills/engineering/html-doc/README.md) |
| **Design & architecture** | [zoom-out](./skills/engineering/zoom-out/README.md) · [architecture](./skills/engineering/architecture/README.md) · [architecture-review](./skills/engineering/architecture-review/README.md) · [prototype](./skills/engineering/prototype/README.md) · [ui-studio](./skills/engineering/ui-studio/README.md) · [improve-codebase-architecture](./skills/engineering/improve-codebase-architecture/README.md) · [loc-budget](./skills/engineering/loc-budget/README.md) |
| **Build & debug** | [tdd](./skills/engineering/tdd/README.md) · [diagnose](./skills/engineering/diagnose/README.md) · [performance-engineer](./skills/engineering/performance-engineer/README.md) |
| **Review, CI & PRs** | [review](./skills/engineering/review/README.md) · [verify](./skills/engineering/verify/README.md) · [simplify](./skills/engineering/simplify/README.md) · [lean-diff](./skills/engineering/lean-diff/README.md) · [pr-workflow](./skills/engineering/pr-workflow/README.md) · [pr-monitor](./skills/engineering/pr-monitor/README.md) · [ci-monitoring](./skills/engineering/ci-monitoring/README.md) |
| **End-to-end delivery** | [cloud-factory](./skills/engineering/cloud-factory/README.md) · [feature-gap](./skills/engineering/feature-gap/README.md) · [port](./skills/engineering/port/README.md) · [workon](./skills/engineering/workon/README.md) · [workon-event](./skills/engineering/workon-event/README.md) |

### Productivity

General workflow, not code-specific.

| Group | Skills |
| --- | --- |
| **Communicate** | [caveman](./skills/productivity/caveman/README.md) · [grill-me](./skills/productivity/grill-me/README.md) · [taste-review](./skills/productivity/taste-review/README.md) · [unslop](./skills/productivity/unslop/README.md) |
| **Sessions & continuity** | [handoff](./skills/productivity/handoff/README.md) · [wrap](./skills/productivity/wrap/README.md) · [wrap-resume](./skills/productivity/wrap-resume/README.md) |
| **Track & report** | [track-my-work](./skills/productivity/track-my-work/README.md) |
| **Tools** | [linear](./skills/productivity/linear/README.md) |
| **Research** | [web-search](./skills/productivity/web-search/README.md) |
| **Author & learn** | [teach](./skills/productivity/teach/README.md) · [write-a-skill](./skills/productivity/write-a-skill/README.md) |

</details>

## Invocation

A skill can start two ways, and most of these support both:

- **Model-invoked** — the agent matches the skill's description against the
  work in front of it and loads the skill itself. No prompting needed.
- **User-invoked** — you type `/<skill-name>`, or ask for it by name.

Three skills are deliberately one-sided:

| Skill | Invocation | Why |
| --- | --- | --- |
| [`zoom-out`](./skills/engineering/zoom-out/README.md) | user only — `disable-model-invocation: true` | You know when you've lost the thread; the agent doesn't. |
| [`teach`](./skills/productivity/teach/README.md) | user only — `disable-model-invocation: true` | A teaching session is something you ask for, not something the agent should start mid-task. |
| [`workon-event`](./skills/engineering/workon-event/README.md) | model only — `user-invocable: false` | Dispatched by the harness with an event payload attached; there is nothing useful to type by hand. |

Of the rest, a handful are written to fire off the operation itself rather than
wait to be asked — [`git-commit`](./skills/engineering/git-commit/README.md),
[`git-safety`](./skills/engineering/git-safety/README.md),
[`branch-conventions`](./skills/engineering/branch-conventions/README.md),
[`commit-conventions`](./skills/engineering/commit-conventions/README.md), and
[`simplify`](./skills/engineering/simplify/README.md) trigger on a commit, a
force-push, a new branch, or a finished diff. Those are the guardrails; install
them and forget them. Everything else is a workflow you'll usually kick off
yourself, even though the agent may reach for it when the description fits.

## Documentation

- **[Available skills](./docs/skills.md)** — the full annotated catalog.
- **[Why these skills exist](./docs/motivation.md)** — the failure modes each skill targets, and the books behind them.
- **[Installation](./docs/installation.md)** — quickstart and manual install.
- **[Contributing](./docs/contributing.md)** — skill layout, conventions, and repository structure.

## Attributions

Several skills are ported from
[mattpocock/skills](https://github.com/mattpocock/skills),
[ogulcancelik/agent-skills](https://github.com/ogulcancelik/agent-skills),
[bholmesdev/skills](https://github.com/bholmesdev/skills), and
[owainlewis/blueprint](https://github.com/owainlewis/blueprint)
under MIT — see
[THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) for the full attribution
and license text.

## License

PolyForm Shield 1.0.0 — see [LICENSE](./LICENSE).
