# skills

[![Release](https://img.shields.io/badge/release-v0.2.0-blue)](https://github.com/dotbrains/skills/releases/latest)
[![CI](https://github.com/dotbrains/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/dotbrains/skills/actions/workflows/ci.yml)
[![License: PolyForm Shield](https://img.shields.io/badge/License-PolyForm%20Shield-brightgreen.svg)](https://polyformproject.org/licenses/shield/1.0.0)

[![skills.sh](https://skills.sh/b/dotbrains/skills)](https://skills.sh/dotbrains/skills)

Portable agent skills from [dotbrains](https://github.com/dotbrains).

## Quickstart

```bash
npx skills@latest add dotbrains/skills
```

Pick the skills you want, choose the agents to install them on, and you're done.
Other install options (release script, manual copy) are in
[docs/installation.md](./docs/installation.md).

## Available skills

26 skills across two categories — see **[docs/skills.md](./docs/skills.md)** for
the full annotated catalog. Each skill directory also has its own `README.md`
alongside the canonical `SKILL.md` the agent consumes.

**Engineering** — code work: bug-hunting, design, planning, review, execution.

`branch-conventions` · `ci-monitoring` · `commit-conventions` · `diagnose` · `git-commit` · `git-safety` · `grill-with-docs` · `improve-codebase-architecture` · `pr-monitor` · `pr-workflow` · `prototype` · `review` · `tdd` · `to-issues` · `to-prd` · `triage` · `workon` · `workon-event` · `zoom-out`

**Productivity** — general workflow, not code-specific.

`caveman` · `grill-me` · `handoff` · `teach` · `wrap` · `wrap-resume` · `write-a-skill`

## Documentation

- **[Available skills](./docs/skills.md)** — the full annotated catalog.
- **[Why these skills exist](./docs/motivation.md)** — the failure modes each skill targets, and the books behind them.
- **[Installation](./docs/installation.md)** — quickstart, release script, and manual install.
- **[Contributing](./docs/contributing.md)** — skill layout, conventions, and repository structure.

## Attributions

Several skills are ported from
[mattpocock/skills](https://github.com/mattpocock/skills) under MIT — see
[THIRD_PARTY_LICENSES.md](./THIRD_PARTY_LICENSES.md) for the full attribution
and license text.

## License

PolyForm Shield 1.0.0 — see [LICENSE](./LICENSE).
