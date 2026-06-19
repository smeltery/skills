# Installation

## Quickstart

```bash
npx skills@latest add dotbrains/skills
```

Pick the skills you want, choose the agents to install them on, and you're done.

## Manual install

If you don't want to use `npx skills`, copy the `SKILL.md` you want into your
agent's skills directory. For Claude Code:

```bash
mkdir -p ~/.claude/skills/diagnose
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/engineering/diagnose/SKILL.md \
  -o ~/.claude/skills/diagnose/SKILL.md
```

Or, from a clone of this repo, symlink every skill into `~/.claude/skills/`:

```bash
./scripts/link-skills.sh
```
