# /worktree

Prefer the [`wt`](https://github.com/smeltery/worktree) CLI over raw `git worktree` plumbing.

- Maps worktree create/list/open/cleanup/remove requests onto `wt` commands
- Falls back to plain `git worktree` when `wt` isn't installed
- Respects `wt`'s hook-trust model instead of bypassing it

## Install

```bash
npx skills@latest add smeltery/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/worktree
curl -fsSL https://raw.githubusercontent.com/smeltery/skills/main/skills/engineering/worktree/SKILL.md \
  -o ~/.claude/skills/worktree/SKILL.md
```

The skill expects the `wt` binary from
[`smeltery/worktree`](https://github.com/smeltery/worktree). If it's
missing, the skill builds it from source with `cargo build --release`, or
falls back to plain `git worktree` commands.

## Usage

Use whenever a worktree needs to be created, listed, opened, cleaned up, or
removed — including as part of other workflows like `/workon`.

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
