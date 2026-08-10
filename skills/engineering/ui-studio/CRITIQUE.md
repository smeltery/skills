# Evidence-Based UI Critique

Use this guide after the production showcase passes mechanical verification and
before the Release gate. Critique the generated kit, not the reference sources.

## Prepare an unbiased review

1. Re-read the approved design thesis, principles, non-goals, scenario matrix,
   and accepted reference rights. Do not inspect implementation code first.
2. Start the production build using the intended hosting strategy.
3. Open a fresh Playwright context without development overlays or retained
   interaction state.
4. Review representative sparse, typical, dense, adverse, narrow, middle, wide,
   touch, keyboard, reduced-motion, zoomed, and localized/RTL scenarios when
   relevant.
5. Use the approved artifact policy for every screenshot, trace, and report.

Copy [templates/critique-report.md](templates/critique-report.md) into the kit's
durable documentation when policy permits. Otherwise keep a redacted local
report and preserve only the decision and accepted limitations.

## Pass 1: Structure before decoration

Review in grayscale or mentally discount styling so polish cannot hide weak
structure:

- Is the primary task and next action obvious without reading every label?
- Does hierarchy survive sparse, dense, and long-copy content?
- Does the layout transform intentionally rather than merely shrink?
- Are navigation, selection, status, loading, empty, error, and recovery states
  distinguishable?
- Do touch order, keyboard order, DOM/ARIA order, and visual order agree?
- Does zoom, localization, or RTL reveal clipping, reordering, or ambiguity?

## Pass 2: Interaction and finish

Review the complete presentation:

- Do controls advertise their behavior and respond with timely, proportional
  feedback?
- Are focus, hover, pressed, selected, disabled, loading, success, and error
  states coherent across component families?
- Are typography, palette, spacing, shape, depth, iconography, imagery, and
  motion governed by the approved system rather than one-off taste?
- Is the result recognizably original, product-specific, and distinct from both
  its references and generic generated-UI defaults?
- Does reduced motion preserve meaning? Do touch targets and pointer behavior
  fit their input modes?
- Does the production build remain visually stable and responsive within its
  discovered performance budgets?

## Record evidence, not vibes

Classify each finding:

- `blocker` — breaks the approved task, accessibility, rights/privacy policy,
  production host, public reuse contract, or a required scenario;
- `concern` — weakens hierarchy, coherence, responsiveness, interaction, or
  performance enough to require an explicit fix-or-accept decision;
- `opportunity` — useful refinement that does not block the approved scope.

Every blocker or concern must name the route/component, state, viewport/input,
evidence, violated principle or contract, and required response. Avoid arbitrary
numeric scores: a number without evidence creates false precision.

## Release recommendation

- `revise` when any blocker remains or a required budget fails;
- `approve-with-limitations` when the user explicitly accepts every remaining
  concern with rationale and follow-up;
- `approve` when required scenarios and principles hold with no unresolved
  blocker or concern.

Attach the report path and recommendation to the Release gate. The same agent may
perform the critique, but it must use the fresh production review above rather
than approving from implementation memory.
