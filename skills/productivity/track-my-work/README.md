# track-my-work

A personal standup logger for AI coding agents. Run `/track-my-work` at the end of the day and it will:

1. Pull your recent Linear tickets and GitHub PRs (back to your last logged entry, max 14 days).
2. Classify each item by impact and type.
3. Write or update entries in *your own* Notion Standup Log database, cross-linking Linear ↔ GitHub where a PR references a ticket.
4. Ask you about anything not auto-captured — Notion docs you authored, chat decisions, meetings, off-ticket work.
5. Report a summary including a PRs-reviewed count.

**Why Notion docs are manual-only:** the Notion search API doesn't reliably filter to pages you actually authored (its `created_by_user_ids` filter returns false positives for pages you only viewed or were mentioned in). Rather than log other people's docs as yours, the skill asks you in Step 7's manual prompt instead.

It's idempotent: running it multiple times the same day updates existing entries instead of duplicating.

## Prerequisites

- **Linear MCP** connected in your agent config (e.g. `mcp__claude_ai_Linear__*` tools available). The exact prefix depends on your MCP server name.
- **Notion MCP** connected (e.g. `mcp__claude_ai_Notion__*` tools available) — used for writing entries to your Standup Log.
- **`gh` CLI authenticated** (`gh auth status` should succeed) and scoped to the org(s) you want tracked.
- **`python3` on PATH** for the timezone fallback.

### Optional: Linear API key for full coverage

`/track-my-work` runs in two modes:

| Mode | Setup | What you get |
| --- | --- | --- |
| **Reduced** (default) | None — just install | Linear: assigned tickets only. GitHub: full. |
| **Full** | Generate a Linear API key (~30 sec) + a local `linear-cli` | Linear: assigned + tickets you created + comments you authored. GitHub: full. |

To enable full mode (useful for cross-team work, RCA writeups, triage):

1. In Linear, open **Settings → Security & access → Personal API keys** (`.../settings/account/security`).
2. Click **New API key**, name it `track-my-work-key`, scope **Full access**, click **Create**.
3. Save the key:
   ```
   mkdir -p ~/.config/linear-cli
   echo '{"apiKey":"lin_api_..."}' > ~/.config/linear-cli/config.json
   chmod 600 ~/.config/linear-cli/config.json
   ```

Full mode also needs a local `linear-cli` that reads `~/.config/linear-cli/config.json` and exposes `issues-mine-assigned`, `issues-mine-created`, and `comments-mine`. Without it, the skill stays in reduced mode and degrades gracefully. The first-run setup offers the API-key step interactively, and you can enable it later anytime with `/track-my-work --setup-linear-cli`.

## First-run setup

The skill bootstraps itself on first invocation. Just run `/track-my-work` — it will walk you through:

1. **Set up the Standup Log database.** Two paths:
   - **Let the skill create it** — paste a Notion parent page URL and it builds the database with the [exact schema](#standup-log-schema) for you (portable default; no shared template needed).
   - **Use an existing database** — paste the URL of a Standup Log you already have.
2. **Detect your timezone** (or ask if it can't be determined).
3. **Resolve your GitHub org** to scope PR searches to (or `all`).
4. **Save config** to `~/.config/track-my-work/config.json`.
5. **Offer to schedule daily auto-runs.** The setup asks whether you want this to fire automatically every weekday evening (default 7pm local). If yes, it computes the UTC cron and hands it to your scheduling skill. If you'd rather run `/track-my-work` manually, choose that — you can always schedule it later.
6. **Run the first daily pass immediately** so your standup is logged for today.

The first run both sets you up *and* logs that day's work — no separate setup command.

### Reconfigure later

Run `/track-my-work --setup` to redo any of the above. Or delete `~/.config/track-my-work/config.json` and it'll re-bootstrap on the next run.

## Standup Log schema

First-run setup recreates the canonical template (title `track-my-work — Standup Log`) exactly — same columns, same option colors, same two views — so every install gets an identical source of truth without sharing a template page. If you build it manually (or verify the one the skill created), it must match:

| Column | Type | Notes |
| --- | --- | --- |
| `Entry` | Title | The primary action — "Fixed X", "Reviewed Y", "Wrote RCA for Z" |
| `Date` | Date | Day the work happened, in your local timezone |
| `Impact` | Select | `High` (red), `Medium` (yellow), `Low` (green) |
| `Type` | Multi-select | `Bug Fix` (blue), `RCA` (purple), `AAR` (brown), `Incident` (red), `Spike` (pink), `Code Review` (blue), `Release Support` (orange), `Backlog` (gray), `Testing` (green), `Process` (orange), `AI/Automation` (yellow) |
| `Linear Ticket` | URL | |
| `GitHub PR` | URL | Auto-cross-linked if a PR body or branch references a Linear ticket |
| `Notes` | Text (rich) | 1–3 sentences. Mentions/link-previews supported (incl. Notion page mentions for manual entries). |

**Views:**

- **Default view** (table) — sorted by `Date` descending; shows `Entry`, `Date`, `Notes`, `Type`, `Impact`, `Linear Ticket`, `GitHub PR`.
- **Calendar** (calendar) — laid out by `Date`; shows `Entry`.

The exact create-database DDL and view configuration live in [`SKILL.md`](./SKILL.md#standup-log-schema). The `Type`/`Impact` options must exist on the database; if you create the DB by duplicating an existing one, option values only carry over if they exist on the source.

## Common usage

```
# Daily standup capture
/track-my-work

# Reconfigure database location, org, or timezone
/track-my-work --setup

# See what would be logged without writing anything
/track-my-work --dry-run
```

## Scheduling

The first-run setup offers to create a daily schedule for you (default: 7pm local weekdays). If you said no then but change your mind, or want a different time, the cron expressions for 7pm local weekdays are:

| Zone | Cron (UTC) |
| --- | --- |
| Pacific (PDT, summer) | `0 2 * * 2-6` |
| Pacific (PST, winter) | `0 3 * * 2-6` |
| Mountain (MDT) | `0 1 * * 2-6` |
| Central (CDT) | `0 0 * * 2-6` |
| Eastern (EDT, summer) | `0 23 * * 1-5` |
| Eastern (EST, winter) | `0 0 * * 2-6` |
| UK (BST) | `0 18 * * 1-5` |
| UK (GMT) | `0 19 * * 1-5` |

How you wire the cron up depends on your scheduling tooling. If your agent has a cloud scheduling skill (e.g. `/schedule`), point it at the cron above with prompt `/track-my-work`:

```
/schedule create --name track-my-work-daily --cron "0 2 * * 2-6" --prompt "/track-my-work"
/schedule list
/schedule delete track-my-work-daily
```

> **Heads up:** cloud scheduling runs on your provider's infrastructure and may count against your plan. Each daily fire is a normal agent session.

You can also invoke `/track-my-work` ad-hoc anytime — it picks up everything since the last logged entry, so missing a scheduled day doesn't lose work.

### Running as a cloud routine

Cloud routines run in a fresh sandbox each fire — `gh` may **not** be preinstalled and your local auth does **not** carry over. Without setup, the GitHub half of your standup is silently skipped (Linear and Notion still work via MCP). Configure the routine's environment once:

1. **Setup script** — install the GitHub CLI. `gh` is not in stock Ubuntu's default repos, so add GitHub's official apt source first:

   ```bash
   #!/bin/bash
   set -e
   apt-get update || true
   # Bootstrap the downloader first — a minimal image may not ship curl.
   type -p curl >/dev/null || apt-get install -y curl
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   apt-get update || true
   apt-get install -y gh
   ```

2. **Environment variables / secrets** — add `GH_TOKEN`. The `gh` CLI reads it automatically at runtime (no `gh auth login` needed). Use a GitHub **fine-grained or classic PAT** scoped to just `repo` + `read:org` — **not** your local `gh` OAuth token — and store it in the **secret** field, not a plain env var, to limit blast radius if a routine log leaks.

The setup script only *installs* gh, so the "env vars aren't available during setup" limitation doesn't matter here — `GH_TOKEN` is only needed later when the session runs `gh search prs`.

## How identity resolves

To keep this skill portable across teammates, **nothing about you is hardcoded** and only the bare minimum is stored in config:

| Identity | How it resolves |
| --- | --- |
| Linear user | `assignee: "me"` — Linear MCP resolves to whichever account is authenticated |
| Linear team filter | None — tracks your activity across **all** teams you're assigned on |
| GitHub username | `gh api user --jq .login` at runtime |
| GitHub org | `config.githubOrg` (set on first run; `null` = search across all orgs by author) |
| Notion docs | Manual capture in Step 7 — Notion search filter is unreliable for "pages I authored" |
| Timezone | Stored in config, detected on first run |
| Standup Log DB | Stored in config, set during first-run setup |

## Known issues

- **GitHub MCP fallback.** The GitHub MCP token may lack visibility into private repos. When this happens, Step 3 returns zero results even when you clearly had PR activity. The skill auto-falls-back to `gh search prs` via Bash, so practically you'll still get your PRs — just slightly slower.
- **Linear assignee filter.** `assignee: "me"` sometimes misses tickets you only briefly touched (e.g., triage closures). Surfaces as occasional missing standup entries for cleanup work. Workaround: add anything missed via the manual capture prompt.
