# /taste-review

Portable `/taste-review` skill for getting a clear second opinion when an
artifact is correct but the best design, prose, naming, or formatting choice is
still subjective.

The skill frames a neutral brief, uses an independent reviewer already
available in the environment, weighs the answer against project constraints,
and applies the smallest approved change. It does not require a particular
model vendor or CLI.

## Install

```bash
npx skills@latest add smeltery/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/taste-review
curl -fsSL https://raw.githubusercontent.com/smeltery/skills/main/skills/productivity/taste-review/SKILL.md \
  -o ~/.claude/skills/taste-review/SKILL.md
```

## Usage

```text
/taste-review Which empty state feels clearer for first-time users? src/routes/inbox
/taste-review Pick the strongest name for this public API packages/core/src/client.ts
```

## Requirements

- An artifact or decision with a bounded review scope
- Optional access to an independent agent, model tool, or review service
- Project-local validation tools when the recommendation is applied

Without an independent reviewer, the skill performs a disclosed structured
self-review instead.

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition consumed by the agent.

## Attribution

Adapted from
[`bholmesdev/skills` — `taste-review`](https://github.com/bholmesdev/skills/tree/main/skills/taste-review)
under MIT. See [THIRD_PARTY_LICENSES.md](../../../THIRD_PARTY_LICENSES.md).
