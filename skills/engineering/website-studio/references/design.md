# Design and content

## Context: infer the right project

Identify the visitor, their problem, the offer, the primary action, the facts
available, and what a successful visit looks like. For an existing project,
inspect routes, components, content sources, assets, styles, analytics already
present, package scripts, tests, hosting, and current failures. Preserve working
behavior and URLs unless the request requires a migration with redirects.

Use the existing stack and package manager. For a new content-led site, favor
static/server-rendered HTML with small interactive islands; for an application,
choose the simplest stack its state and backend require. Bun is useful when
compatible, not a reason to migrate a functioning project. Reuse an existing
Flox environment or equivalent reproducible setup. Do not add authentication,
a CMS, commerce, analytics, or a database without a real product need.

If the user supplies no business brief, infer a coherent demo from context and
label it fictional. Use a descriptive working name and continue. An empty brief
does not justify a questionnaire about aesthetic preferences.

## References: study live behavior and implementation separately

Read [the reference study](reference-study.md) as calibration for the requested
quality. These sites are examples, not mandatory network dependencies. Prioritize
user-supplied references for the current project.

For each relevant reference, inspect the homepage, an interior/detail page,
navigation, a primary journey, and a narrow viewport. Capture the rendered view
after fonts, images, and transitions settle. Scroll through the whole page and
inspect the footer. If a capture is blank or incomplete, investigate readiness
and recapture; do not treat a file on disk as proof of visual review.

Record typography roles, content width, section rhythm, palette, image crops,
CTA hierarchy, mobile transformations, and interaction feedback. Separate what
was seen in a browser from what was inferred from code. Test navigation/search
without submitting inquiries to real businesses.

Find repositories through links, hosting metadata, authenticated repository
search, or available local checkouts. Confirm the mapping; do not assume a repo
based only on its name. Inspect route composition, tokens, content models,
interactive code, asset handling, test coverage, and build/deployment scripts.
Record a commit identifier and dirty-worktree status. A local checkout may differ
from production. Inspect reference repos read-only; do not execute unfamiliar
setup scripts merely to read their architecture.

If a repo or site cannot be accessed, record the attempt, use available evidence,
and narrow the claims. Never fabricate implementation findings. A reference outage
need not block building an original site; inability to test the destination does
block its browser gates.

## Direction: make a specific design decision

Write a short design thesis connecting the audience to the visual treatment.
Consider two plausible directions internally and select one with a reason.
Preserve an established identity. If no direction is supplied, the calibration
set suggests editorial hierarchy, restrained surfaces, generous but purposeful
spacing, and strong typography with imagery or a useful product demonstration.
Adapt that language to the business instead of repeating the same split hero.

Define a compact system before scattering values through components:

- Semantic background, text, muted, border, accent, action, and status colors.
- Display, body, label, and optional code typography; actual font availability,
  fallback, weights, fluid scale, line height, and readable measure.
- Content widths, gutters, spacing rhythm, image ratios/focal points, border and
  radius rules, icon family, and responsive transformations.
- Focus, hover, active, selected, disabled, loading, success, and error treatment.
- Motion purpose, duration, reduced-motion behavior, and content-visible fallback.

Compose the hero and a contrasting interior section using real-length copy at
desktop and mobile widths. A lightweight HTML/CSS study or annotated layout is
enough; do not make a reusable component library a prerequisite. Revisit the
direction if it cannot accommodate the content without awkward wraps or density.

Avoid decorative sameness: identical card grids for unrelated content, excessive
pills, arbitrary gradients, tiny low-contrast labels, enormous empty gaps, and
animation that hides information. Use borders, grids, photography, diagrams,
lists, and type according to the content. Density should vary deliberately.

## Structure: design the complete visitor journey

Create the route matrix and write substantive copy before broad implementation.
Every page must answer a visitor question, have a distinct purpose, and offer
a logical next step. A detail page expands on a summary; it cannot be filler
repeating the homepage. Use one clear primary action per decision point.

Consider these surfaces according to the business, recording exclusions:

| Site need | Possible surfaces | Completion obligation |
| --- | --- | --- |
| Understand an offer | Home, services/product, process, about | Concrete benefits, scope, audience, and next action |
| Assess credibility | Portfolio, case study, track record, team | Real proof with provenance; omit invented metrics/testimonials |
| Take action | Contact, inquiry, booking, installation | Reachable destination, truthful outcome, error and recovery path |
| Explore a collection | Directory, filters, search, detail pages | Discoverable items, empty/reset states, deep links, history |
| Use a tool | Calculator, planner, gallery, download | Correct domain behavior, labels, edge cases, usable results |
| Understand site operation | Privacy, credits, relevant terms | Accurate to actual collection/providers; no fabricated compliance claims |
| Recover or share | 404, metadata, social image, favicon | Useful recovery, consistent identity, correct destination URLs |

Do not add tools, search, pricing, FAQs, or legal boilerplate solely because the
references have them. Include search when content scale benefits from it, and
ensure every added feature earns its implementation and testing cost.

Inventory assets with source, usage rights, role, crop, dimensions, and alt text.
Prefer owned existing assets; source permitted photos or generate original
illustration when useful and tools are available. Do not reuse reference logos,
portraits, proprietary copy, or imagery without rights. Never pass synthetic
people or generated work off as actual staff or client work. If no imagery is
available, build an intentional typography/diagram composition, not broken-image
placeholders. Use a simple original wordmark when no logo exists.

Gate evidence: brief, source observations, chosen direction/tokens, complete
route/content/action matrix, and asset ledger. Keep these compact and editable.
