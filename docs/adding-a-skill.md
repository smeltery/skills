# Adding a skill

A skill is complete when agents can discover it and people can find, read, and
install it from the website. Use this checklist for every new skill.

## Create the canonical files

Choose `skills/engineering/<name>/` or `skills/productivity/<name>/`. Add:

- `SKILL.md` with YAML `name`, `description`, and `argument-hint`. The name must
  match its directory and be unique across categories.
- `README.md` with a concise overview, working usage examples, requirements,
  links to supporting resources, and attribution when applicable. This is also
  the website's overview content.
- References, scripts, and meaningful tests only when the workflow needs them.

## Register it once, verify every surface

Link the skill README from root `README.md`, `docs/skills.md`, and its category
README. Choose an appropriate task group in `apps/site/src/lib/catalog.ts`;
unassigned engineering skills default to Build & debug, and productivity skills
default to Work & communicate. Recommended ordering is optional.

The site automatically generates `/skills/<name>/` through
`apps/site/src/pages/skills/[slug].astro`. The homepage catalog, search, counts,
sitemap, and agent-readable documents derive from the same canonical skill
files. Do not maintain a duplicate page or a hardcoded skill count.

## Run the completion check

With Node.js 24+ and dependencies installed using `npm ci`, run from the root:

```bash
npm run skill:check -- website-studio
```

Replace `website-studio` with the new name. The command checks its required
metadata, README, and three catalog links, then runs site type checks, tests,
and the production build. Every build also verifies **all** canonical skills
have generated detail pages, overview/instructions sections, install commands,
homepage links, sitemap entries, agent-index entries, and Markdown documents.
The existing website CI job runs this same build guard.

Run the skill's own tests and Markdown lint as appropriate. The targeted check
requires all current metadata fields for new skills; it does not silently
rewrite older skills or unrelated files.

## Inspect the actual page

```bash
npm run preview
```

Open the URL printed by Astro followed by `/skills/<name>/`. Check desktop and
mobile layouts, the overview, install/copy commands, full-instructions disclosure,
resource links, and any Mermaid diagrams. Find the skill through the homepage
catalog and search. Automated coverage checks prove generated files and links
exist; browser inspection checks whether the page is actually usable.

In the handoff, include the route, validation results, and any blocker. A local
build is not a public deployment. When commit/push is authorized, include only
task changes and monitor the resulting CI/deployment checks.
