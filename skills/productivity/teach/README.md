# /teach

Teach the user a new skill or concept inside the current workspace. This is a
**stateful, multi-session** request — the agent treats the working directory as
a teaching workspace and builds up durable learning artifacts over time.

## Teaching workspace

The state of the user's learning lives in the directory:

- `MISSION.md` — why the user wants to learn the topic; grounds all teaching
  (see [MISSION-FORMAT.md](./MISSION-FORMAT.md)).
- `RESOURCES.md` — trusted resources to ground teaching in
  (see [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md)).
- `./lessons/*.html` — the primary unit of teaching: self-contained, beautiful,
  tightly-scoped HTML lessons.
- `./reference/*.html` — compressed cheat sheets and glossaries for quick review.
- `./learning-records/*.md` — what the user has learned and key insights
  (see [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md)).
- `NOTES.md` — working notes and the user's teaching preferences.

## Approach

Learning combines **knowledge** (from high-trust resources), **skills**
(acquired through interactive lessons with tight feedback loops), and **wisdom**
(from real-world communities). Lessons target the user's zone of proximal
development and favor storage strength over fluency — retrieval practice,
spacing, and interleaving.

## Install

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/teach
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/productivity/teach/SKILL.md \
  -o ~/.claude/skills/teach/SKILL.md
```

## Usage

Trigger by saying "teach me <topic>" or invoking `/teach`. The skill is
opt-in (`disable-model-invocation: true`) — it runs only when you ask for it.

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
- [`MISSION-FORMAT.md`](./MISSION-FORMAT.md) — format for `MISSION.md`.
- [`RESOURCES-FORMAT.md`](./RESOURCES-FORMAT.md) — format for `RESOURCES.md`.
- [`LEARNING-RECORD-FORMAT.md`](./LEARNING-RECORD-FORMAT.md) — format for learning records.
- [`GLOSSARY-FORMAT.md`](./GLOSSARY-FORMAT.md) — format for glossary reference docs.

## Attribution

Ported from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach) under MIT. See [THIRD_PARTY_LICENSES.md](../../../THIRD_PARTY_LICENSES.md).
