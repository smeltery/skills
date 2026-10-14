# AGENTS.md

Guidance for agents working in `smeltery/skills`.

## Scope

This repository is the canonical home for portable smeltery skills. Each skill
lives at `skills/<category>/<name>/`, with a canonical `SKILL.md` and a
user-facing `README.md` that also supplies its website overview.

Keep changes focused on:

- Skill behavior and wording in `skills/<name>/SKILL.md`
- Documentation clarity in the top-level `README.md`
- Skill discovery, website pages, and checks that keep these in sync
- Portability across environments (no company-internal assumptions)

## Rules

- Keep branding generic and open-source friendly.
- Each `SKILL.md` must start with YAML frontmatter containing `name`,
  `description`, and `argument-hint`.
- Skill directory name must match the `name` field in its frontmatter.
- Prefer explicit idempotency and recovery behavior in skill flows.
- Do not hardcode environment-specific defaults when they can be discovered.
- Keep human-facing output concise and free of internal jargon.

## Adding a new skill

Follow [Adding a skill](docs/adding-a-skill.md). Do not stop after writing
`SKILL.md`:

1. Create `skills/<category>/<name>/SKILL.md` with the required frontmatter and
   a sibling `README.md` with useful overview, examples, and resource links.
2. Link that README from root `README.md`, `docs/skills.md`, and the category
   README. Keep names and descriptions consistent.
3. Check the website task group in `apps/site/src/lib/catalog.ts`. Skill pages,
   search entries, counts, sitemap, and agent documents are generated from the
   canonical files; do not create a separate Astro page for each skill.
4. Run `npm run skill:check -- <name>` and the skill's own tests. This command
   checks registration, runs site checks/tests, builds the site, and verifies
   every generated skill page and discovery entry.
5. Inspect `/skills/<name>/` in the production preview on desktop and mobile,
   including overview, install command, full instructions, links, and diagrams.
   Report the route and actual checks performed. Do not imply local changes
   are already on the public website.

## Validation

Before finishing, verify:

1. Every `SKILL.md` frontmatter is valid and complete.
2. References are generic (no company-internal docs).
3. `./scripts/list-skills.sh` lists every skill you intended to add.
4. CI passes (markdown lint + skill frontmatter validation).
5. The website build passes its generated-page coverage check. For new skills,
   the targeted registration check and rendered page inspection are complete.
