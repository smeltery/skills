# /unslop

Strip AI writing tells out of a piece of text and put a real voice back in.

Model-drafted prose has a fingerprint: hedged claims, inflated framing, the
same handful of transition words, uniform sentence rhythm, and chatbot
leftovers like "I hope this helps!" `/unslop` is a targeted edit pass that
finds those tells and fixes them without changing the meaning, then adds back
the opinion and specificity that make writing worth reading.

## Install

```bash
npx skills@latest add smeltery/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/unslop
curl -fsSL https://raw.githubusercontent.com/smeltery/skills/main/skills/productivity/unslop/SKILL.md \
  -o ~/.claude/skills/unslop/SKILL.md
```

## Usage

```text
/unslop docs/onboarding.md
/unslop <paste text here>
```

Run it on anything a human will read closely before it ships — docs, PR
descriptions, comments, write-ups. Skip it for throwaway notes nobody's going
to scrutinize.

## What it looks for

- Inflated framing and weasel attribution ("a testament to", "experts agree")
- Hedge stacking and filler connective tissue ("could potentially somewhat", "in order to")
- The stock AI vocabulary (delve, leverage, utilize, showcase, tapestry, and the rest)
- Rule-of-three padding, "not just X, but Y", synonym rotation
- Metaphor-as-jargon (substrate, vector, north star) standing in for a concrete word
- Passive voice that hides who's doing the thing
- Punctuation tics — em-dash overuse, mid-sentence colons, bolding everything
- List-itis — bullet fragments and bold-label-then-colon where prose would read better
- Assistant-speak and generic closers left over from chat interfaces

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition consumed by the agent.
