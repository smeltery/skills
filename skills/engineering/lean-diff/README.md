# /lean-diff

Portable `/lean-diff` skill for keeping the net diff as small as possible on
every code change: targeted edits over rewrites, no drive-by reformatting or
renaming, no unrequested abstractions, and a `git diff` read-through before
calling any change done.

It applies automatically to any task that touches code, and is also directly
invocable to audit and trim whatever is currently uncommitted.

## Install

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/lean-diff
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/engineering/lean-diff/SKILL.md \
  -o ~/.claude/skills/lean-diff/SKILL.md
```

## Usage

```text
/lean-diff
```

No arguments needed to audit the current uncommitted diff. As a standing
discipline it applies to any coding task without being invoked explicitly.

## The hook

This skill ships a `PostToolUse` hook (`scripts/diff-stat.sh`) that runs after
every `Edit`, `Write`, `MultiEdit`, or `NotebookEdit` and echoes the current
`git diff --shortstat`. It's a passive nudge, not a gate — it never blocks, it
just keeps the running diff size visible so scope creep gets caught early
instead of at final review.

## Requirements

- `git`

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition consumed by the agent.
- [`hooks.json`](./hooks.json) — `PostToolUse` hook spec wiring `scripts/diff-stat.sh` to code-touching tool calls.
- [`scripts/diff-stat.sh`](./scripts/diff-stat.sh) — echoes the running `git diff --shortstat`; best-effort, never blocks.
