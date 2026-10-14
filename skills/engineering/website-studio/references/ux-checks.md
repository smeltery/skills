# Implementation and UX gates

## Build: complete the agreed site

Implement shared navigation, footer, tokens, page layouts, and semantic controls.
Keep page content distinct from interaction logic where it makes edits simpler.
Prefer native links, buttons, forms, disclosure elements, and dialogs over custom
framework machinery. Preserve existing backend contracts and environment names.

Implement every route in the matrix, including detail pages, fallback routes,
favicon and social assets. Verify linked downloads and image/font files exist.
No dead buttons, `href="#"` stand-ins, TODO copy, fabricated proof, or fake success.
Avoid giant page files and fragmented one-line abstractions. Use existing LOC
budgets; otherwise record a modest file-size/complexity budget suited to the
project and justify exceptions without minifying source to satisfy it.

Document installation, build, preview, content editing, relevant environment
variable names, and verification commands before the final build snapshot.
Use frozen dependency installation where supported. Start the production build
with the correct adapter/runtime; a static file server cannot test server routes.

## Journeys: exercise each control, including failure

Create a checklist from the actual rendered controls and route matrix. Mark
features absent only when the product does not contain or require them. Test
with fixtures or intercepted requests; do not send test leads, payments, or emails
to live recipients. Record mocked versus real integration coverage explicitly.

| Surface | Required behavior when present |
| --- | --- |
| Navigation | Logo home link, current page, submenu, mobile open/close, Escape, outside click if intended, focus return, restored body scroll |
| Links and CTAs | Correct destination and context, no dead end, downloads work, external/new-tab semantics match labels |
| Forms | Persistent labels, required/optional clarity, correct input types/autocomplete, trimmed validation, field errors, focus on invalid field |
| Submission | Pending feedback, duplicate prevention, real success only after confirmation, timeout/offline/server error, retry, preserved input |
| Email fallback | Say draft/prepared, not sent; handle no mail app or long text with copy/download; actual delivery remains unverified |
| Search | Open/close, input focus, matching and zero results, clear/reset, keyboard navigation, current index, route changes and back navigation |
| Filters/sort | Combined filters, result counts, no-results recovery, reset, retained/deep-linked state where useful, invalid query parameters |
| Dialog/gallery | Accessible name, modal focus containment, Escape, close control, trigger focus restoration, scroll unlock, image failure; next/previous if present |
| Tools/calculators | Known inputs and outputs, units, zero/negative/extreme/invalid values, rounding, reset, copy/export, result announcements |
| Long/dynamic content | Long names, multiline labels, many/few/zero items, missing optional media/data, slow data, failures |
| Navigation lifecycle | Direct deep-link load, refresh, back/forward, repeated open/close, no duplicate listeners after client navigation |

If an essential backend is missing, finish the UI and local mocked tests, then
report the integration blocker. An honest fallback satisfies delivery only when
it fulfills the declared scope; it cannot replace a required working submission.
Never clear the form on failure or celebrate a request before it succeeds.

## Responsive: inspect the rendered transformation

Use at least 360–390px mobile, about 768px tablet, and 1280–1440px desktop.
Additionally check 320px reflow and widths immediately around navigation/layout
breakpoints. Record actual viewport dimensions, not just the requested preset.
Test real touch emulation when available; viewport resizing alone is not touch.

Capture and inspect top, middle, footer, and key interaction states for each page
family. Look for horizontal overflow, clipped text, orphaned heading words,
unreadable overlays, broken grid ordering, disproportionate whitespace, cut-off
faces, stretched logos, cramped controls, and sticky elements hiding content.
Fix the cause; `overflow-x: hidden` is not a general overflow repair.

Check 200% zoom, large text, landscape/short-height screens, and form behavior
with the virtual keyboard where supported. Content order must remain meaningful.
Primary actions should remain findable without forcing every CTA above the fold.
Keep touch controls comfortably spaced, aim for 44px targets, and never make
hover the only path to information or an action.

Honor reduced motion and retain visible content when JS or animation fails.
Avoid scroll hijacking. Back/forward navigation must not leave the page invisible
or the body locked. Wait for stable fonts/images before final screenshots.

## Accessibility: automated and manual evidence

Use semantic landmarks, a logical heading hierarchy, descriptive page titles,
meaningful link text, correct button roles, and a skip link when repeated
navigation warrants it. Give meaningful images informative alt text and hide
pure decoration from assistive technology. Associate labels, instructions,
errors, and status announcements with their controls.

Complete the primary journey using only a keyboard. Verify visible focus,
logical focus order, modal focus handling, no traps, and menus usable without
hover. Inspect contrast for text and controls in every state, including images
behind text. Apply WCAG AA contrast expectations; do not claim full conformance
from an automated score. Test screen-reader output when supported and record
the coverage honestly.

Run an available accessibility scanner on representative routes and interactive
states. Triage every finding; fix confirmed issues, document evidenced false
positives, and rerun. A scanner cannot approve copy, visual hierarchy, keyboard
flow, or the meaning of alt text on the agent's behalf.

## Discovery: finish the often-forgotten surfaces

- Unique, accurate page titles and descriptions; correct canonical URLs once
  the deployment origin is known. Do not leak localhost or an invented domain.
- Working social preview image, favicon, app icon where needed, and consistent
  branding on errors, forms, tool results, and shared links.
- Sitemap for indexable public routes and robots rules appropriate to the actual
  environment. Preview/private sites must not accidentally become indexable.
  Robots directives are not access control.
- Structured data only when supported by actual content; no fake reviews,
  location, pricing, organization identifiers, or claims.
- Crawl internal links and fragments, assets, downloads, redirects, and 404s.
  An unknown route must not return a successful homepage disguised as an error.
- Preserve working old URLs or provide deliberate redirects after a redesign.
  Ensure server-rendered essentials remain useful before hydration.

Add brand-download pages, feeds, machine-readable content, or a CMS only when
they serve the project. Do not turn a complete website into a checklist of
unnecessary features.
