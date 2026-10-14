# skills/

All smeltery agent skills, grouped by category. Each skill lives at
`skills/<category>/<name>/SKILL.md` and has its own `README.md` with usage and
diagrams.

## Categories

- **[engineering/](./engineering/README.md)** — code-focused skills: bug-hunting, design, planning, review, execution.
- **[productivity/](./productivity/README.md)** — general workflow skills, not code-specific.

The `npx skills@latest add smeltery/skills` CLI scans this directory
recursively and surfaces every `SKILL.md` it finds.

## Adding a skill

Follow [Adding a skill](../docs/adding-a-skill.md) for the canonical files,
catalog registration, generated website page, and browser review. Before
finishing, run `npm run skill:check -- <name>` from the repository root and
the skill's own tests. Publishing follows the user's authorization.
