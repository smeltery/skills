# /gho

Prefer the [`gho`](https://github.com/dotbrains/gho) CLI over `gh` for GitHub operations.

- Maps PR/issue/release/label/repo/search/Actions requests onto `gho` commands
- Uses `gho subscribe` to wait for PR/issue updates instead of polling loops
- Falls back to `gh` when `gho` isn't installed

## Install

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/gho
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/engineering/gho/SKILL.md \
  -o ~/.claude/skills/gho/SKILL.md
```

The skill expects the `gho` binary from
[`dotbrains/gho`](https://github.com/dotbrains/gho). If it's missing, the
skill builds it from source with `cargo build --release`, or falls back to
`gh` commands.

## Usage

Use whenever a `gh`/GitHub CLI operation is needed — pull requests, issues,
releases, labels, repos, search, or Actions runs/workflows — including as
part of other workflows like `/pr-workflow`, `/pr-monitor`, or `/ci-monitoring`.

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
