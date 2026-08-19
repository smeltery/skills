---
name: unslop
description: Edit writing to strip out AI-generated tells and put a real voice back in. Use before shipping any text a human will read closely — docs, PR descriptions, comments, Slack messages, emails — especially text a model drafted or touched.
argument-hint: "[file | text to edit]"
---

# Unslop

Text drafted by a model tends to carry a fingerprint: hedged claims, inflated adjectives, the same handful of transition words, and a rhythm that never varies. None of that is wrong sentence by sentence. Stacked up, it reads as generated rather than written. This skill is a pass to find that fingerprint and remove it, then put back the specificity and opinion that made the writing worth reading in the first place.

## When to run this

- Before sending a PR description, doc, or write-up that a model helped draft.
- On any text where a reader would notice it "sounds like AI" — that reaction is a real signal, not vibes.
- Skip it for throwaway internal notes where nobody will read closely, and skip it for code comments (those have their own bar: only write one when the why isn't obvious).

## Process

1. Read the text once straight through, flagging every sentence that trips one of the tells below.
2. Rewrite flagged sentences. Keep the meaning and the intended tone — this is not a rewording pass for its own sake, only fix what's actually broken.
3. Reread for voice: does a specific person seem to be saying this, or could it have been assembled by anyone about anything?
4. Last check: pick the single most generic-sounding sentence left. If you can't sharpen it, cut it.

## The tells

**Inflated framing.** Phrases that make something sound bigger than it is without adding information: "a testament to", "stands as a pivotal moment", "marks a significant milestone", "an ever-evolving landscape". Say what happened in plain terms instead.

**Weasel attribution.** "Experts agree", "many believe", "it is widely understood" — with no expert named. Either cite who said it or drop the claim.

**Hedge stacking.** Multiple qualifiers doing the job of one: "could potentially somewhat improve" collapses to "may improve" or, better, a number.

**Filler connective tissue.** "In order to" → "to". "Due to the fact that" → "because". "It is worth noting that" and "it is important to mention that" almost never need saying — delete the frame and state the fact.

**The stock word list.** A small set of words shows up constantly in model output because they're safe and vague: delve, boast, robust, seamless, leverage (as a verb), utilize, facilitate, foster, underscore, showcase, elevate, unlock, tapestry, landscape (used abstractly), realm, journey (used metaphorically for a process). Swap in the plain word: use, help, show, limit, or the specific mechanism.

**Rule-of-three padding.** Forcing every list into exactly three items whether or not three is the right count. Use however many the content actually needs.

**"Not just X, but Y."** A construction that manufactures drama out of a simple statement. Say Y directly.

**Synonym rotation.** Calling the same thing by three different names in one paragraph to avoid repetition — "the tool," "the utility," "the application" — when repeating the actual name would be clearer. Pick one term and reuse it.

**Metaphor-as-jargon.** Abstract nouns borrowed to sound technical — substrate, vector, surface (for "API surface"), north star, flywheel, primitive (as a noun), scaffolding used loosely. If there's a concrete word for the actual thing, use that instead.

**Passive voice hiding the actor.** "Requests are validated before processing" tells you nothing about who validates them. "The gateway validates requests before forwarding them" does. Use passive only when the actor genuinely doesn't matter.

**Adverb crutches.** "Runs significantly faster" wants a number or a comparison; if you have neither, the claim probably isn't ready to make.

**Punctuation tics.** Overusing em dashes as a substitute for periods or commas, colons used mid-sentence as a connector rather than to introduce a list, and bolding every proper noun or key term until nothing stands out because everything does.

**List-itis.** Turning a paragraph of connected reasoning into a bullet list of fragments, or a bold label followed by a colon and a sentence that just restates the label ("**Performance:** Performance is much better now."). Prose reads better than a list when the ideas depend on each other; save lists for genuinely parallel, independent items.

**Assistant-speak.** "I hope this helps!", "Let me know if you have questions!", "Great question!", "Of course!" — leftover politeness formulas from chat interfaces. In written docs and PR descriptions there's no one to be polite to; just state the thing.

**Generic closers.** Ending on a sentence that could close any piece of writing about anything: "the future looks bright," "this opens up exciting possibilities." Close on the actual next step or the actual result instead.

## Putting a voice back in

Removing the tells above gets you to neutral, not to good. Neutral, voiceless writing is its own tell. To finish the job:

- Take a position. If something is a bad idea, say it's a bad idea instead of listing "considerations."
- Let sentence length vary. A short sentence lands harder right after a longer one that set it up.
- Say "I" when the sentence is about a choice you made — hiding behind passive voice to sound objective usually just sounds evasive.
- Keep one telling specific over three generic ones. "The build takes eleven minutes" beats "the build takes a while."
- A little roughness — an aside, a mid-thought correction, an opinion that doesn't fully resolve — reads as human. Manicured, uniform paragraphs read as generated.
