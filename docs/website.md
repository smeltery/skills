# Skills website

The Astro site lives in `apps/site/`. React powers the searchable catalog;
Astro generates the guides and every skill page as static HTML.

## Develop

Use Node.js 24 or newer and npm. From the repository root:

```bash
npm ci
npm run dev
```

Open the URL printed by Astro. The preferred port is 4321; Astro selects another
available port if it is occupied.

```bash
npm run check
npm test
npm run build
npm run preview
```

The production output is `apps/site/dist/`. No application server or database is
required. Set `SITE_URL` to the production origin before building to emit canonical
and Open Graph URLs. No production domain is assumed.

## Content

The catalog reads `skills/<category>/<name>/SKILL.md` and its sibling `README.md`
at build time. Names, descriptions, category, and invocation modes come from those
files. Adding a canonical skill automatically adds a catalog entry and detail page.
Run commands through the root npm scripts so the source paths resolve consistently.

Task group assignments and recommended ordering live in `src/lib/catalog.ts` and
`src/components/SkillFinder.tsx`, relative to `apps/site/`. Unassigned engineering
skills appear in Build & debug; productivity skills appear in Work & communicate.
Counts are derived from the catalog. They are never manually maintained.

Search uses all query words across skill names, descriptions, categories, and task
groups. Search, category, and sort state are reflected in the URL. The initial HTML
contains every skill, so the library is usable without JavaScript. Hydration adds
filtering and incremental display. Installation and prompt copy buttons report
clipboard errors and leave the text available for manual copying.

Repository Markdown is sanitized before rendering. Shiki highlights fenced code
and shell commands at build time with a light syntax theme; language labels make
blocks easier to scan. Unknown languages fall back to escaped plain text. No
syntax-highlighting runtime is shipped to the browser. Relative source links point
back to their correct GitHub location. Mermaid blocks render lazily in the browser with a matching sage theme. Each diagram
includes an expanded view with zoom controls and an accessible source disclosure.
The source remains readable without JavaScript or when rendering fails. Mermaid
uses strict security mode and its default protected configuration keys.

The shared navigation includes a site-wide search dialog (Command+K or Control+K),
scoped search for skills and guides, exact-name ranking, and keyboard result
navigation. The full-height mobile dialog provides search, page cards, task
categories, and a suggested first skill. Native dialogs contain keyboard focus;
closing restores the original trigger and page scroll. Both panels share one
scroll-lock implementation with the expanded diagram viewer.

Development, check, and production builds use separate Vite caches so building
does not invalidate lazy diagram modules in an open preview.

## Design references

The implementation was informed by the local `smeltery/adamou-financial-consulting`
repository and its [live tool library](https://adamou-financial-consulting.vercel.app/tools/),
with branding from a fresh checkout of [smeltery/website](https://github.com/smeltery/website)
at commit `2813b8f44dbcc0dd188f728561c28825c0842135`.

Patterns carried forward include warm paper backgrounds, restrained serif headings,
a shared navigation and footer, searchable categorized tools, individual detail
pages, related recommendations, clear next actions, and keyboard-accessible mobile
navigation. The skills site uses the Smeltery mark, warm paper/charcoal/sage tokens,
self-hosted DM Sans and IBM Plex Mono, and rounded navigation from that design
system. The catalog retains its task-based layout. Decorative diagonal arrows are deliberately omitted. Active navigation uses
a filled pill; ordinary text links use a single underline.

The GitHub brand icon comes from Font Awesome Free (CC BY 4.0), with its attribution
in the icon component. See [Font Awesome licensing](https://fontawesome.com/license/free).
The icon identifies the repository link; it does not imply an endorsement.

## Deployment

Deploy `apps/site/dist/` to a static host. For Vercel, the root `vercel.json` sets
installation, build, and output paths. Connect the repository and configure
`SITE_URL` to match the assigned domain. Deployment is not part of local development.

## Validation

`npm run check` checks Astro and TypeScript. `npm test` covers source discovery,
search intersections, invocation modes, installation commands, and safe Markdown
rendering. `npm run build` generates all routes. The website CI job runs these checks.

For browser changes, use Maestri portals to check desktop and mobile navigation,
search, no-results recovery, filters, sort, pagination, detail pages, clipboard
feedback, and horizontal overflow. Check the rendered production build as well as
local development when changing the catalog pipeline.
