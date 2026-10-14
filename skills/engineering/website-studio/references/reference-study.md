# Reference study

These examples calibrate craft and completeness. They are not templates to copy,
required runtime dependencies, or evidence that every feature is defect-free.
The observations below combine rendered browser inspection with read-only source
review. Repository implementation does not prove a live integration works.

## Sources and provenance

Repository mappings were confirmed through GitHub repository homepage metadata.
Source review used local checkouts at the revisions below. The first four were
clean; the skills checkout included ongoing site changes. Live deployments may
represent different revisions. No production inquiries were submitted.

| Live site | Repository | Inspected revision | Useful distinction |
| --- | --- | --- | --- |
| [Adamou Financial Consulting](https://adamou-financial-consulting.vercel.app) | [Source](https://github.com/smeltery/adamou-financial-consulting) | `3e18cf7` | Calm advisory design with useful financial tools |
| [Bold Performance](https://bold-performance.vercel.app) | [Source](https://github.com/smeltery/bold-performance) | `d172881` | Strong athletic typography, photography, and guided intake |
| [JEA BizDev Consulting](https://www.jeabizdev.com) | [Source](https://github.com/smeltery/jeabizdev.com) | `e0e0a5b` | Professional credibility plus a browsable opportunity/transaction library |
| [Alder House](https://alder-house.vercel.app) | [Source](https://github.com/smeltery/alder-house) | `225bc50` | Editorial photography, portfolio detail, and inquiry context |
| [Smeltery Skills](https://smeltery-skills.vercel.app) | [Source](https://github.com/smeltery/skills) | `57fb2b3` plus local changes | A useful searchable catalog within a restrained marketing shell |

Use these paths to rediscover patterns; line numbers and implementation may
change. Refresh the evidence when fidelity to a current reference is required.

## Design observations

**Adamou:** an oversized serif headline with a restrained italic accent, warm
paper background, teal action color, mountain imagery, clear explanatory copy,
and a low-pressure next step. The narrow layout changes navigation and stacks
the hero. Source: `apps/site/src/pages/index.astro`, shared section components,
and `apps/site/src/styles/`. The lesson is approachable clarity tied to the
service, not a universal prescription for mountain photography or serif type.

**Bold:** condensed, forceful display typography, cyan accents, a contrasting
training image, and credentials near the primary action. Source:
`src/pages/index.astro`, `src/styles/hero.css`, and `src/forms/intake-client.ts`.
The intake implementation preserves answers on failure, distinguishes a prepared
email draft from a sent inquiry, and handles conditional fields. The transferable
principle is that visual confidence needs equally clear interaction outcomes.

**JEA:** blue/white identity, substantial editorial headlines, concise service
entry points, relationship imagery, and routes to evidence and opportunities.
Source: `src/styles/foundation.css`, `src/pages/index.astro`,
`src/server/inquiry.ts`, and `playwright.config.ts`. The server code validates
input and returns explicit unavailable/failure states; the browser test setup
covers desktop and mobile. Do not copy the business's claims or client evidence.

**Alder:** warm neutral surfaces, dark green typography, fine borders, framed
photography, and deliberate serif scale. The portfolio and session routes make
the visual work navigable rather than decorative. Source:
`src/pages/index.astro`, `src/client/gallery.ts`, and `tests/journeys.spec.ts`.
Gallery code includes keyboard controls, focus return, scroll restoration, and
image failure feedback. Journey tests cover session-prefilled inquiries and
back navigation with reduced motion. These are code findings, not a claim that
every interaction was independently exercised on the live site.

**Skills:** quiet sage surfaces, compact rounded navigation, a clear installation
panel, and a task-driven library. Source: `apps/site/src/pages/index.astro`,
`apps/site/src/styles/global.css`, and
`apps/site/src/components/SkillFinder.tsx`. The catalog code handles search,
categories, sorting, URL state, history restoration, counts, and reset. The
hero is useful product UI rather than a mandatory photograph.

## Shared implementation lessons

The inspected repositories use Astro for page structure, shared styles and
layouts, and focused client code or React islands for interaction. Several use
Bun and split validation into scripts, including documentation and budget checks.
This supports a lightweight content-first default, not a mandatory framework
or license to replace an existing application's architecture.

The consistent quality comes from the whole experience: distinct identities,
purposeful content, interior pages, clear routes to action, asset treatment,
error recovery, and verification. The skill therefore gates both visible design
and hidden interaction states. It does not mandate the same hero, palette,
font pairing, section count, or feature list on every project.

## Limits of this study

All five homepages were visually inspected after loading; selected narrow
layouts and navigation/search controls were inspected as additional samples.
Initial captures of some animated pages were blank before a later settled
capture, reinforcing the need to verify actual screenshot contents. This was
a design/source study, not a full accessibility, security, performance, or
production integration audit of the references. Future runs must test their
own output, including defects the reference sites might themselves contain.
