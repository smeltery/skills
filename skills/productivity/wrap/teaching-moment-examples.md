# Teaching Moment — Calibration Examples

Reference file for `/wrap` Phase 3d. Do not load unless calibrating the teaching moment format. The main SKILL.md keeps the format rules inline; this file holds the extended examples so they don't bloat the hot path.

## Audience calibration

The typical /wrap user is a senior technical builder who leads engineers and reads papers, but is not necessarily a CS researcher. They don't need vocabulary flexing; they need durable mental models they can actually reuse.

Write the teaching moment so the user can:

- Read it once and absorb the core idea
- Explain it back to a colleague in their own words
- Recognize the pattern the next time it applies

## Jargon rule — TEACH the term, don't hide it

Users at this level WANT to grow their engineering vocabulary. Hiding the real term used by the field is condescending; the goal is to teach it so they can recognize and use it with their team.

**Rule:** When a concept has a real name that practitioners use, **lead with the name, then define it in the same breath**. Don't smuggle the idea in under a plain-English paraphrase — the reader misses the chance to learn the word.

**Format:** "[Real term]. It's [what it means in plain English, 1 clause]." — then continue with the session-anchored example, analogy, and takeaway.

### Examples of the right pattern

- "**Ablation isolation.** It's testing one change at a time so you can tell which one actually caused an improvement — 'ablating' the other variables..."
- "**Idempotent operations.** Operations you can run twice and get the same result as running them once..."
- "**Goodharting the eval.** When a metric becomes the target, it stops being a good measure — named after the economist Charles Goodhart..."
- "**Hysteresis.** A built-in lag so a system doesn't oscillate back and forth between states — think of a thermostat that only kicks on when the room drops 2 degrees below target, not the instant it dips..."

## Anti-examples and the fix

❌ **Bad (jargon stacked, undefined):** "Ablation isolation catches Goodharting by forcing a clean A/B — otherwise we can't attribute r@5 lift to the right phase."
— Three terms, zero definitions, reader bounces.

❌ **Bad (over-simplified, vocabulary hidden):** "If two changes both affect the same score, you can't tell which one caused the improvement — you have to turn them on one at a time."
— True but loses the teachable word. The user can't now say "ablation" to a colleague.

✅ **Good (names term, defines it, anchors, analogizes, ends with cue):**

> "**Ablation isolation.** It's testing one change at a time so you can tell which one caused the improvement. That's why we kept chunking separate from the retrieval change today. Same idea as a chef changing one ingredient at a time in a recipe. Next time two improvements ship together, ask *which one did the work?*"

## Calibration summary

- Don't ban jargon — teach it.
- Name → define → anchor in session → analogy → reusable question.
- Skip terms that are actually vocabulary flexing (Pareto frontier, asymptotic, etc.) when simpler words capture the same idea. But if "ablation" is the word the field uses, use it and teach it.
- Max 4 short sentences. If it's longer, you're showing off, not teaching.
