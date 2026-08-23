# /wrap-resume

Picker for unfinished sessions. Reads plan files written by [`/wrap`](../wrap/README.md), surfaces each one's `# 🔴 RESUME HERE` block, and lets you pick which thread to continue.

## Invocation

```sh
/wrap-resume
```

No arguments. Lists every plan in `$WRAP_PLANS_DIR` that still has a live `# 🔴 RESUME HERE` block, sorted most-recent first.

## What it does

1. Resolves `PLANS_DIR` (`$WRAP_PLANS_DIR` → `$WRAP_STATE_DIR/plans` → `$HOME/.wrap/plans`).
2. Filters to plans containing a `# 🔴 RESUME HERE` marker.
3. Extracts `Status:`, `Mode:`, `Current task:`, and `Immediate next action:` from each block.
4. Renders a numbered picker showing last-wrap timestamp, current task, and next action — with an `⚠` flag on rows where `Mode: EMERGENCY` (context was limited when the wrap was written).
5. On selection, opens the chosen plan and proposes the next concrete step as an actionable question.

## Pairs with

- [`/wrap`](../wrap/README.md) — writes the RESUME HERE blocks that `/wrap-resume` reads.

The two skills share a single output contract: the `# 🔴 RESUME HERE` block format and the plan-directory convention. Any reader that honors the same format (a personal `/work` skill, a team dashboard, etc.) can stand in for `/wrap-resume`.

## When it asks before acting

- If the chosen plan's `Context source: unknown due compaction`, the picker warns that origin context was lost — offer to start fresh or proceed with partial context.
- If multiple plans share the same timestamp window and describe the same task, the picker asks which one you meant instead of guessing.

## Error handling

- **Missing plans dir** — tells you `/wrap` hasn't been run yet in this setup.
- **Unreadable plan** — skips that file, continues with the rest; one corrupt plan does not kill the picker.

## Install

```bash
npx skills@latest add smeltery/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/wrap-resume
curl -fsSL https://raw.githubusercontent.com/smeltery/skills/main/skills/productivity/wrap-resume/SKILL.md \
  -o ~/.claude/skills/wrap-resume/SKILL.md
```

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
