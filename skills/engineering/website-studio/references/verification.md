# Verification and delivery

## Performance gate

Declare budgets during direction/structure work, then measure the production
build under recorded device/network settings. Reuse stricter existing budgets.
For an ordinary content-led site without budgets, use these starting targets:

| Measure | Initial target | Evidence |
| --- | --- | --- |
| Largest contentful paint | At most 2.5 seconds under the chosen mobile test profile | Production lab report; distinguish it from real-user data |
| Cumulative layout shift | At most 0.1 | Load and interaction observations/report |
| Initial compressed JS per route | At most 150 KB | Build/bundle or transferred-resource report |
| Initial page transfer | At most 1.5 MB | Network capture including initial images/fonts |
| Interaction response | No visible stalls during key actions | Browser trace; INP at most 200ms if meaningful field data exists |

These are project budgets, not a claim that a single lab run proves field
performance. Explain justified product-specific adjustments before measuring;
do not raise a budget after a failed test simply to pass. Repeat unstable
measurements and report settings and variation.

Prioritize the actual hero/LCP asset; size responsive images and reserve their
space. Lazy-load below-fold media, limit font weights, use reliable fallbacks,
and avoid hydrating static sections. Remove unused dependencies and duplicated
scripts. Test font/image failure, slow loading, and content visibility with JS
disabled when the site is intended to support progressive enhancement.

Run formatting, lint, type checks, meaningful domain tests, production build,
link checks, browser journeys, and accessibility checks applicable to the stack.
Use existing CI and local hooks with shared commands. Add missing checks for
implemented behavior; avoid tests that only assert source strings. Never change
runner providers or add unrelated release infrastructure as part of a redesign.

## Critique gate: fresh visual and UX review

Open the production preview without relying on implementation memory. Review
each page family at desktop and mobile widths, including header, footer, detail
pages, and adverse states. Inspect the screenshots themselves. Compare to the
declared design thesis and relevant reference traits, not pixel identity.

Assess each category with specific route/viewport evidence:

1. **Purpose and hierarchy:** the visitor can tell what the site offers and what
   to do next; the most important content wins visually.
2. **Typography and rhythm:** deliberate scale and measure, good heading wraps,
   readable labels, balanced spacing and density through the whole page.
3. **Imagery and identity:** coherent asset direction, meaningful crops, correct
   logos, distinctive treatment suited to the business.
4. **Composition:** sections have appropriate contrast and variety; mobile order
   is intentional; the footer and interior pages receive equal attention.
5. **Interaction finish:** controls look usable; feedback, focus, empty/error
   states, and recovery feel like the same product.
6. **Content and trust:** specific and truthful copy, useful details, accurate
   outcomes, no template residue, fake proof, or unexplained claims.

Record defects as blocker (broken task/accessibility/required behavior), major
(material hierarchy, clarity, consistency, or responsive flaw), or minor
(optional refinement). Fix all blockers and majors. Fix in-scope minor defects
that undermine the chosen finish. Do not average serious failures into a
passing numeric score.

For each repair, invalidate the earliest affected gate, rebuild, recapture, and
rerun relevant journeys. Keep before/after evidence and ensure the fix did not
break another viewport. End when the contracts hold, rather than endlessly
changing acceptable colors. If no progress is possible, report the unresolved
gate honestly. Do not ask the user to perform the critique or enumerate fixes.

## Delivery gate

Ensure a fresh install and production build are reproducible using documented
commands and lockfiles. Use test credentials/fixtures, not production messages
or transactions. Verify the final artifact rather than a dev-server-only path.
Check runtime configuration, secret handling, actual form endpoints, security
headers appropriate to the framework, and hosting error/deep-link behavior.

If deployment was requested and authorized, use the existing host/project or
the approved target. Verify the deployed revision and repeat primary journey,
mobile, asset, metadata, and deep-link smoke checks against that URL. Watch CI
and deployment checks for the final pushed revision until green; diagnose and
repair failures without weakening gates. Missing access or provider outages
remain blockers, not a reason to claim success.

If publishing was not requested, an inspected local production preview is a
complete delivery. The receipt must explicitly say local, record the preview
command, and avoid implying CI or remote deployment was run. Do not add an
approval checkpoint simply to finish an already authorized local website.

Finish with a concise summary of the design, what works, how to run it, and what
was actually verified. Include any required external setup as a blocker to the
promised scope. Do not describe a mock submission as a verified integration.
