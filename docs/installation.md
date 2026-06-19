# Installation

## Quickstart

```bash
npx skills@latest add dotbrains/skills
```

Pick the skills you want, choose the agents to install them on, and you're done.

## Release script

Use the release-delivered installer pattern by downloading and running
`install.sh` / `install.ps1` from a GitHub Release.

Prerequisites:

- Node.js 18+
- GitHub CLI (`gh`)

macOS / Linux:

```bash
tmp="$(mktemp)"; gh release download --repo dotbrains/skills --pattern 'install.sh' --output "$tmp" --clobber; bash "$tmp"; rm "$tmp"
```

Windows PowerShell:

```powershell
$p = Join-Path $env:TEMP 'install.ps1'; gh release download --repo dotbrains/skills --pattern 'install.ps1' --output $p --clobber; & $p; Remove-Item $p
```

The installer validates Node.js and then runs:

```bash
npx --yes skills@latest add dotbrains/skills
```

Any additional arguments passed to the installer are forwarded to `skills add`.

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
