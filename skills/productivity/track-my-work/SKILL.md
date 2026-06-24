---
name: track-my-work
description: "Pulls your recent Linear and GitHub activity into a personal Notion Standup Log database. Deduplicates against prior entries, updates them when state has progressed, and prompts for anything not captured automatically (Notion docs, meetings, chat decisions). Activates on /track-my-work or when you ask to update your standup log."
version: 1.1.0
user-invocable: true
category: productivity
argument-hint: "[--setup | --dry-run]"
requires: [python3]
---

A daily standup logger that reads activity from Linear and GitHub, classifies it (Impact + Type), and writes it to your personal Standup Log database in Notion. Prompts for anything not auto-captured (Notion docs, chat decisions, meetings) as a manual step. Idempotent — re-running the same day updates existing entries instead of duplicating.

**Why no Notion auto-pull:** the Notion search API can't reliably filter to pages you actually authored (the `created_by_user_ids` filter returns false positives for pages where you are associated but not the creator). To avoid logging other people's docs as if they were yours, Notion contributions are captured only through Step 7's manual prompt.

> **MCP tool prefixes vary.** This skill references Linear and Notion through MCP. The exact tool prefix depends on your MCP server name (e.g. `mcp__claude_ai_Linear__*`, `mcp__claude_ai_Notion__*`). Match what's surfaced in the available tool list — this doc writes `mcp__*Linear__*` / `mcp__*Notion__*` where the prefix is environment-specific.

## What's available

- **First-run bootstrap** — locates or initializes your config + Standup Log on the first invocation.
- **Daily run** — pulls activity since the last logged entry (or 7 days, whichever is shorter, capped at 14), classifies, and writes to your Standup Log.
- **Manual capture** — always prompts for items not in any of the three sources (chat decisions, meetings, off-ticket work).

### Per-user config

Stored at `~/.config/track-my-work/config.json`:

```json
{
  "standupLogDbId": "fb63e1d3-4f60-44d1-8ed0-8d6f87959113",
  "githubOrg": "your-org",
  "timezone": "America/Los_Angeles"
}
```

- `standupLogDbId` — the Notion database this skill writes to (set during first-run setup).
- `githubOrg` — the GitHub org to scope PR searches to. Optional: if omitted/`null`, GitHub searches run by author across **all** orgs you can see (slower, broader).
- `timezone` — IANA timezone, detected on first run.

Everything else (Linear "me", GitHub username) is resolved at runtime — no identity stored. Linear activity is not filtered by team; whatever you're assigned to anywhere shows up.

### Linear coverage

Linear reads go entirely through the **Linear MCP** — no CLI, no API key, no extra setup. The MCP covers two of the three activity types directly:

| Activity | How | Coverage |
| --- | --- | --- |
| **Assigned** | `list_issues { assignee: "me" }` | Full |
| **Created** | `list_issues { createdAt: <lookback> }` then client-filter on `creator == me` (the MCP has no `creator` filter, so the date-windowed scan bounds the result set) | Full within the lookback window |
| **Commented** | No global "comments I authored" query exists in the MCP | Not pulled directly — recovered via the GitHub→Linear cross-link (Step 3) and Step 7's manual prompt |

The GitHub cross-link means a ticket you created *or* commented on that also has a PR you authored/reviewed still surfaces. The only gap is a Linear ticket you touched with no associated PR activity in the window — Step 7 is the catch-all for those.

## Common workflows

### First run — bootstrap config

If `~/.config/track-my-work/config.json` does not exist, run setup before anything else:

1. **Set up the Standup Log.** You need a Notion database matching the [canonical template below](#standup-log-schema). Offer the user two paths:
   - **Create it for them (recommended)** — ask for a Notion parent page URL, then recreate the canonical template exactly: call `mcp__*Notion__notion-create-database` with the DDL from [Standup Log schema](#standup-log-schema) (this sets every column, the `Impact`/`Type` options *and their colors*), then add the two views with `mcp__*Notion__notion-create-view` / `mcp__*Notion__notion-update-view` as specified there. This is the portable default — no shared template page required, and the result is identical to the source of truth.
   - **Use an existing database** — if the user already has a Standup Log (or a duplicated template), ask them to paste its URL.
2. **Validate the database.** Extract the database ID with the regex `[0-9a-f]{32}` or `[0-9a-f-]{36}`. Then call `mcp__*Notion__notion-query-data-sources { data_source_url: "collection://<id>" }` with `query_type: "verify_data_source_exists"` to confirm it's reachable. If the query fails, tell the user it didn't resolve and ask them to re-paste (or re-create). Then verify the schema has every required column — if any are missing, list them and stop.
3. **Detect timezone.**
   - Try `timedatectl show -p Timezone --value` (Linux), `readlink /etc/localtime | sed 's|.*/zoneinfo/||'` (mac/Linux), or read `$TZ`.
   - If none work, ask the user: "What's your IANA timezone? (e.g., `America/Los_Angeles`, `America/New_York`, `Europe/London`)"
4. **Resolve the GitHub org.** Ask the user which GitHub org to scope standup PR searches to (or `all` to search across every org by author). Store it as `githubOrg` (string or `null` for all-orgs). You can suggest a default from `gh api user/orgs --jq '.[].login'`.
5. **Write the config file.**
6. **Offer to schedule daily auto-runs.** Most people won't know they can automate this. Ask:
   > "Want this to run automatically every weekday evening, or do you prefer to invoke `/track-my-work` manually whenever?"

   If the user chooses **auto**:
   - Confirm fire time (default: **7:00pm in their local timezone, weekdays**). Let them customize.
   - Compute the UTC cron from `config.timezone` and the chosen fire time. Reference values for 7pm local weekdays:

     | Local zone | UTC cron |
     | --- | --- |
     | America/Los_Angeles (PDT) | `0 2 * * 2-6` |
     | America/Los_Angeles (PST) | `0 3 * * 2-6` |
     | America/Denver (MDT) | `0 1 * * 2-6` |
     | America/Chicago (CDT) | `0 0 * * 2-6` |
     | America/New_York (EDT) | `0 23 * * 1-5` |
     | America/New_York (EST) | `0 0 * * 2-6` |
     | Europe/London (BST) | `0 18 * * 1-5` |
     | Europe/London (GMT) | `0 19 * * 1-5` |

   - Surface the exact cron line to the user before creating, so they can sanity-check it.
   - Invoke your scheduling skill (e.g. `/schedule`) with `name: "track-my-work-daily"`, the computed cron, and prompt `/track-my-work`. **Tell the user clearly** that cloud scheduling runs on the provider's infrastructure and may count against their plan — they explicitly consent before it's created.
   - On success, print: `"Scheduled. To change or remove: /schedule list, /schedule delete track-my-work-daily."`

   If the user chooses **manual**:
   - Skip scheduling. Print: `"OK — run /track-my-work whenever you want. You can schedule it later."`
7. **Continue into the daily run** for today. The first run should both set up *and* log the user's work for the current date.

### Daily run — Steps 1–8

> Every step is mandatory. Do not skip a step because the previous one returned nothing. Do not report completion until Step 8.

**Checklist:**

- [ ] Step 0: Load config (or run first-run bootstrap above)
- [ ] Step 1: Determine lookback window
- [ ] Step 2: Pull from Linear
- [ ] Step 3: Pull from GitHub
- [ ] Step 4: Classify + consolidate (Code Review + PR Progress)
- [ ] Step 5: Match against existing entries
- [ ] Step 6: Log to Standup Log
- [ ] Step 7: Ask "Anything else to log?" (includes Notion docs, chat decisions, meetings)
- [ ] Step 8: Report summary

**Step 1 — Lookback window.** Query the Standup Log for the most recent entry:

```
mcp__*Notion__notion-query-data-sources {
  data_source_url: "collection://<config.standupLogDbId>",
  query: "SELECT \"date:Date:start\" ORDER BY \"date:Date:start\" DESC LIMIT 1"
}
```

If an entry exists, use its date as the start of the lookback window. If no entries (first run), look back 7 days. Cap at 14 days.

**Step 2 — Linear.** All Linear reads go through the Linear MCP. Resolve your user once with `mcp__*Linear__get_user { query: "me" }` (needed for the creator filter below). Then pull two sets:

**Assigned** — issues assigned to you with activity in the window:

```
mcp__*Linear__list_issues { assignee: "me", updatedAt: "<lookback-iso-or-duration>", limit: 250 }
```

**Created** — the MCP has no `creator` filter, so list issues *created* in the window workspace-wide and filter client-side to yours:

```
mcp__*Linear__list_issues { createdAt: "<lookback-iso-or-duration>", limit: 250 }
→ keep only issues whose creator is the "me" user from get_user
```

`createdAt`/`updatedAt` accept an ISO-8601 date or a relative duration (e.g. `-P14D`). Page with `cursor` if the result set hits the limit; if the created-scan still returns a full 250 after paging (very large workspace), note that created-coverage may be truncated for that window rather than silently dropping it. **Do not** filter by team — pull whatever you're assigned to / created anywhere.

Dedupe the two sets by issue ID — an issue you both created and are assigned to is one ticket. For each issue extract: title, identifier, status, URL, completion date.

**Comments you authored are not pulled here** — the MCP has no global "my comments" query. Tickets you commented on (but didn't create or get assigned) are instead recovered two ways: the GitHub→Linear cross-link in Step 3 (if you have an associated PR), and Step 7's manual prompt. If you already have a ticket in hand and want to weigh a comment's substance for Notes, `mcp__*Linear__list_comments { issueId: <id> }` reads that ticket's thread.

Do not block on Linear failures — if the MCP errors out, log the error and continue to Step 3.

**Step 3 — GitHub.** Resolve the username at runtime with `gh api user --jq .login`. Then (using `<org>` = `config.githubOrg`, or omitting the `--owner`/org filter when it's `null`):

- Use the GitHub MCP first. Search for PRs **opened**, **merged**, or **reviewed** by that user in `<org>` since the lookback date.
- **Also** run an authored-PR `updated:>=<lookback>` search (`gh search prs --author <username> --owner <org> --updated '>=<lookback>' --limit 1000`, or the MCP equivalent). The explicit high `--limit` matters: `gh search prs` defaults to 30 results, so a churny week could silently drop authored PRs before the commit-progress fetch ever sees them. This is not just an error fallback: a still-open PR opened *before* the window but pushed to *during* it won't match an opened/merged/reviewed-since query, yet it carries exactly the heads-down daily-commit progress this skill exists to capture. **But `updated:` matches any churn** — a label change, a reviewer comment, a CI status — so treat these results as **input to the commit-progress fetch only**. A PR that surfaces *solely* from this `updated:` pass (no opened/merged/reviewed event in the window) must NOT become a normal Step 3 GitHub item: drop it after the per-PR commit fetch unless it yielded ≥1 in-window user commit (or a state transition). Otherwise Step 5 sees "no prior entry" and logs a bogus open-PR row for work the user didn't do this window.
- **If GitHub MCP returns 0 results**, that's a strong signal something is wrong (MCP token may lack private-repo access). Fall back to the same `gh search prs` query via Bash before concluding there's no activity.

For each PR extract: title, URL, repo, status (open/merged/closed), role (author/reviewer), PR body, head branch name.

**Cross-link to Linear.** Parse the PR body and head branch name for a Linear identifier (regex `[A-Z]+-\d+`). When you log an entry for that Linear ticket in Step 6, attach the matching PR's URL to the same row — don't create a separate orphan entry.

**Extract context from PRs.** Scan the body for high-signal markers — security findings (static-analysis flags, XSS/SQLi/auth), RCA observations, performance catches, pre-existing bugs exposed by the change, complexity/coverage deltas. These become the substance of the `Notes` field in Step 6.

**Per-PR daily commits (authored PRs only).** `gh search prs` and the GitHub MCP search don't return commits, so a day of forward progress on a still-open PR is otherwise invisible (the state model only fires on open→merged→closed). For each PR where the user is the **author** (skip reviewer-only PRs), fetch its commits via the paginated REST endpoint — **not** `gh pr view --json commits`, which silently caps at the first 100 commits ([cli/cli#5415](https://github.com/cli/cli/issues/5415)) and would drop the most recent work on long-lived PRs:

```
gh api --paginate repos/<org>/<repo>/pulls/<number>/commits \
  --jq '.[] | {oid: .sha, date: .commit.committer.date, headline: (.commit.message | split("\n")[0]), login: .author.login}'
```

(The PR-commits endpoint tops out at 250 commits even with `--paginate`. A single PR with >250 commits is outside this daily standup tool's envelope — a lookback window is days, not the life of a long-running branch — so the 250 ceiling is an accepted limit rather than a reason to switch to the branch-range List-commits endpoint, which would pull in base-branch history.)

For each commit, **first** convert its `date` (a UTC timestamp) to its activity date in `config.timezone` (Step 6 date ladder), **then** keep it only if (a) that local activity date is inside the lookback window AND (b) `login` equals the user's GitHub login (drop teammates' commits on a shared PR). Convert-then-filter, not filter-then-convert: a commit at `2026-06-08T23:30 PDT` carries a `2026-06-09` UTC timestamp, so filtering on the raw timestamp would misplace boundary-day commits for any non-UTC user (and the inverse for positive-offset zones). The REST endpoint attributes each commit to its primary GitHub author, which is the signal we want; co-author trailers aren't surfaced here, so a commit the user only co-authored is intentionally not counted. Carry these per-PR commit lists into Step 4's PR Progress consolidation.

**Step 4 — Classify and consolidate.** For each item from Steps 2–3:

- **Impact:** `High` (incident response, CVE, cross-team, RCA writeup, major PR merged), `Medium` (user-facing bug fix, test improvement, code review, process doc, PR opened), `Low` (backlog cleanup, minor fix, small doc update).
- **Type** (pick all that apply): `Bug Fix`, `RCA`, `AAR`, `Incident`, `Spike`, `Code Review`, `Release Support`, `Backlog`, `Testing`, `Process`, `AI/Automation`.

**Code Review consolidation.** Reviews bloat the standup log fast — a heavy review week can be a dozen-plus PRs. So: any GitHub PR where the user's role is `reviewer` and the PR's Linear ticket is NOT in the user's own assigned/created set gets folded into a single per-day Code Review summary row.

- **Grouping:** group these review-only items by activity date.
- **Result:** one row per day with reviews, format:
  - `Entry`: `"Reviewed N PRs"`
  - `Date`: that day
  - `Type`: `["Code Review"]` (add `"Release Support"` if any reviewed PR has release-support flavor)
  - `Impact`: `Medium` by default
  - `Linear Ticket`, `GitHub PR`: leave blank (multiple URLs — they can't fit in URL-typed columns)
  - `Notes`: single line listing each PR with PR number, Linear ID, and a 3-5 word topic. Example: `"repo#1200 (PROJ-600 'open in original' for group members), repo#1247 (PROJ-622 TSV paste distribution), repo#1276 (PROJ-636 locationless cards at [0,0])."`

**Reviews that DON'T collapse** (kept as their own rows or cross-linked into Linear-rooted entries):
- PR where the user is the **author** — logged via Step 2/3 cross-link, not as a review.
- PR where the user reviewed AND the linked Linear ticket is one of the user's own (from `assignee:me` or `creator:me`) — the reviewed PR's URL cross-links into the user's Linear-rooted entry (e.g., self-review of own PR).

**PR Progress consolidation.** Captures days of forward progress on a still-open PR — the gap the open→merged→closed state model leaves, where a heads-down day on an unmerged PR is invisible. For each PR the user **authored**, take its per-PR commit list from Step 3 and group the user's own commits by activity date (in `config.timezone`). Each `(PR, date)` bucket is one candidate progress entry:

- **Granularity:** one entry per authored PR per active day. Do NOT emit one entry per commit.
- **Entry:** `"Progress on <repo>#<num> — <summary> (<TICKET>)"`, where `<summary>` is a one-phrase rollup of that day's commit headlines (what changed), not a verbatim dump.
- **Date:** the bucket's activity date.
- **Type:** inherit the PR's classification tags from this step; never tag a progress entry `"Code Review"`.
- **Impact:** `Medium` default; `Low` if the day is only trivial commits (lint/format/merge/typo/`wip`).
- **Linear Ticket / GitHub PR:** fill from the PR.
- **Notes:** commit count + deduped headlines, e.g. `"5 commits: added needs-action SQL query; zod schema; db layer; route handler; tests."` Collapse trivial commits into the count rather than listing each.

Dedupe against open/merge transition days is deferred to Step 5 — a progress entry is suppressed on any day that already has an open/merged/closed transition entry for the same PR.

**Step 5 — Match against existing entries.** Query the Standup Log for entries in the lookback window. For each item from Steps 2–4, determine routing:

### For Linear or GitHub items

Dedupe key is `(URL, state)` — each distinct state of a ticket/PR is its own entry.

1. **No prior entry for this URL** → create new entry in Step 6.
2. **Prior entry exists AND a new state transition happened since the last log** (PR `open` → `merged`, PR `open` → `closed`, ticket `Backlog` → `In Progress`, ticket `In Progress` → `Done`/`Canceled`, etc.) → **CREATE a new entry on the transition date.** Don't update the prior entry — both stand. Each entry represents the work done *that day*. Example:
   - 2026-05-26: `"Symbol scale slider fix, PR #1240 opened (PROJ-486)"`
   - 2026-05-27: `"Merged PROJ-486 — Symbol scale slider fix, PR #1240 merged"`

   The user explicitly wants to see daily state transitions, not collapsed history.
3. **Prior entry exists, no state transition, but new context surfaced** (substantive comment added, RCA finding, additional cross-link) → **UPDATE** the existing entry via `notion-update-page`. Refresh `Notes`, upgrade `Impact` if warranted.
4. **Prior entry exists, no change** → skip silently.

### For Code Review consolidated entries

- Match by `Date` + `Type` contains `"Code Review"`. At most one Code Review summary row per day.
- If new PRs were reviewed today and the daily summary row exists → **UPDATE** `Notes` to include the new PRs and bump the `"Reviewed N PRs"` count in Entry.
- If no Code Review summary row exists for today → **CREATE** one.

### For PR Progress candidate entries

Dedupe key: `(PR URL, date)`. At most one progress entry per PR per day.

1. **A transition entry (open / merged / closed) exists for this PR on the same date — whether already in Notion OR being created in this same run** → DROP the progress candidate. Check both: the open/merged event that surfaced this PR in Step 3 produces a transition entry in *this* run, so comparing only against existing Notion rows would let the run create the transition row and the progress row for the same day. The transition entry is the headline for that day; if its `Notes` don't already capture the commit summary, fold it in via **UPDATE**. Never stand up a separate progress entry on an open/merge/close day.
2. **A progress entry for this `(URL, date)` already exists** → **UPDATE** its `Notes` + commit count if new commits appeared since last run; otherwise skip silently.
3. **Otherwise** → **CREATE** the progress entry on the bucket's date.

### Note on first-run catchups

When the skill runs for the first time (7-day lookback against an empty Standup Log), every state of every ticket from the window may collapse to a single transition entry — there's no "open" entry from 5 days ago to anchor against, so just create the current-state entry on the current activity date. Subsequent runs follow the rules above.

URL match is a *lookup key*, not a stop signal. Old "skip if URL exists" logic created stale entries; that's why update-on-progress matters.

**Step 6 — Log to Standup Log.**

- **Create:** `mcp__*Notion__notion-create-pages` with `data_source_id: "collection://<config.standupLogDbId>"`.
- **Update:** `mcp__*Notion__notion-update-page` with the matched `page_id`, command `update_properties`, only fields that changed.

Field shapes:

| Field | Type | Notes |
| --- | --- | --- |
| `Entry` | title | Short action-oriented (e.g. "Fixed whiteboard export crash") |
| `Date` (`date:Date:start`) | date | **Today in the user's timezone — see below** |
| `Impact` | select | `High` \| `Medium` \| `Low` |
| `Type` | multi_select | JSON array of tags from Step 4 |
| `Linear Ticket` | URL | Plain URL only |
| `GitHub PR` | URL | Plain URL only — **cross-linked from Step 3 if matched** |
| `Notes` | rich_text | 1–3 sentences with mentions (see below) |

**Date computation.** All "today" computations must resolve in `config.timezone`, not UTC — otherwise entries fired at 5pm Pacific get stamped with tomorrow's UTC date. Use the first option that works:

1. `TZ=<config.timezone> date +%Y-%m-%d` — fastest, works on most hosts.
2. **Fallback for sandboxes without tzdata** (where `TZ=` is silently ignored): compute the offset from the IANA name (Pacific: `7`/PDT, `8`/PST; Eastern: `4`/EDT, `5`/EST; Central: `5`/`6`; Mountain: `6`/`7`; UK: `0`/`1`) and run `date -u -d '<N> hours ago' +%Y-%m-%d`.
3. **Final fallback:** `python3 -c "from datetime import datetime, timezone, timedelta; print((datetime.now(timezone.utc) - timedelta(hours=N)).strftime('%Y-%m-%d'))"`.

Never use bare `new Date().toISOString()` or UTC `date +%F`.

**Notes content guidance — what to highlight:**

| If the work surfaced... | Include in Notes |
| --- | --- |
| Security finding (static analysis, XSS/SQLi/auth) | Severity, mechanism, whether fix landed in the same PR |
| RCA observation or root cause | The pattern in one phrase + link to RCA doc |
| Pre-existing bug exposed by refactor | "Pre-existing on main — refactor exposed it" + fix |
| Complexity / coverage delta | Before → After numbers (e.g. "complexity 64.33 → 53.97") |
| Architectural insight or convention | One-line description + sibling PR that established it |
| Customer / cross-team impact | Name the team or customer flow |

If none apply, one sentence is fine. But for any PR with a meaningful body, try to extract one of these signals before falling back to a generic summary.

**Rich-text mentions in `Notes`.** The two URL columns (`Linear Ticket`, `GitHub PR`) are URL-typed and only accept plain strings (Notion API constraint). But `Notes` is rich_text — embed references inline as mention objects:

- **Linear/GitHub URLs:** `mention` with `type: "link_preview"` and the URL. Unfurls if the workspace has the Linear/GitHub Notion integrations installed.
- **Notion page references** (from Step 7 manual capture): `mention` with `type: "page"` and the page ID. Renders as `@Page Title`. Always works.
- **Fallback:** if the MCP rejects a `link_preview` (integration not connected), retry with a plain inline link (`text` with `link.url`). Don't fail the whole entry over a mention.

Example: `"Wrote RCA for @Login Outage 2026-04-30 covering the cascading session-store failure."`

**Step 7 — Prompt for manual additions [MANDATORY — always run].** Always ask, even if zero items were found in Steps 2–6:

> "Anything else to log? (e.g. Notion docs you authored or contributed to, chat discussions, meetings with decisions, Linear tickets you closed without being assigned, work without a ticket, onboarding tasks)"

If yes, classify and log the same way. For Notion docs the user mentions, ask for the URL so it can be embedded as a `@Page Title` mention in the Notes field. If no, move to Step 8.

**Step 8 — Summary.**

```
✅ track-my-work complete
- X standup entries added (Y high-impact)
  - Linear: X
  - GitHub authored: X
  - PR progress days: P
  - Code Review days: D
  - Manual: X
- X already logged (updated)
- X already logged (skipped, no change)
- PRs reviewed in lookback window: Z
```

`PR progress days: P` counts progress entries added or updated this run (one per authored PR per active day, excluding open/merge/close transition days). `Code Review days: D` counts daily summary rows added or updated this run. `PRs reviewed in lookback window: Z` is the total PR count across all those days (so `Z` is typically several times `D`).

The `PRs reviewed` count is cross-cutting — it counts every unique PR where the user's role was `reviewer` (from Step 3), regardless of which bucket the entry was logged in. PRs you reviewed that were cross-linked into Linear entries still count here.

If nothing new was found across all sources, say so clearly.

### Reconfigure

If the user runs `/track-my-work --setup` or asks to reconfigure, re-run the first-run bootstrap, overwriting the config file. Confirm before overwriting if the file already exists.

### Dry run

If the user runs `/track-my-work --dry-run`, do everything through Step 6 but skip the `notion-create-pages` / `notion-update-page` calls. Report what *would* be written.

## Standup Log schema

This is the canonical Standup Log template — the source of truth. First-run setup recreates it exactly: same columns, same option colors, same two views.

**Database title:** `track-my-work — Standup Log`

**Columns** (the title column is `Entry`):

| Column | Type | Options (with colors) |
| --- | --- | --- |
| `Entry` | Title | — |
| `Date` | Date | — |
| `Impact` | Select | `High`:red, `Medium`:yellow, `Low`:green |
| `Type` | Multi-select | `Bug Fix`:blue, `RCA`:purple, `AAR`:brown, `Incident`:red, `Spike`:pink, `Code Review`:blue, `Release Support`:orange, `Backlog`:gray, `Testing`:green, `Process`:orange, `AI/Automation`:yellow |
| `Linear Ticket` | URL | — |
| `GitHub PR` | URL | — |
| `Notes` | Text (rich) | — |

**Create-database DDL** — pass this as the `schema` to `notion-create-database` (option colors are part of the DDL, so they carry over exactly):

```sql
CREATE TABLE (
  "Entry" TITLE,
  "Date" DATE,
  "Impact" SELECT('High':red, 'Medium':yellow, 'Low':green),
  "Type" MULTI_SELECT('Bug Fix':blue, 'RCA':purple, 'AAR':brown, 'Incident':red, 'Spike':pink, 'Code Review':blue, 'Release Support':orange, 'Backlog':gray, 'Testing':green, 'Process':orange, 'AI/Automation':yellow),
  "Linear Ticket" URL,
  "GitHub PR" URL,
  "Notes" RICH_TEXT
)
```

**Views** — the source of truth has two. After `notion-create-database` returns the `database_id` and `data_source_id`:

1. **Default view** (table) — `notion-create-database` makes a default table view; configure it with `notion-update-view`:
   ```
   SORT BY "Date" DESC; SHOW "Entry", "Date", "Notes", "Type", "Impact", "Linear Ticket", "GitHub PR"
   ```
2. **Calendar** (calendar) — add with `notion-create-view` (`type: "calendar"`, `name: "Calendar"`):
   ```
   CALENDAR BY "Date"; SHOW "Entry"
   ```

If you're verifying an existing/duplicated database instead of creating one, the columns and `Type`/`Impact` options (and ideally the views) must match the above. Note that `Type`/`Impact` options only carry over on a Notion duplicate if they exist on the source.

## When to stop and ask the user

- **No config and the user didn't expect setup** — confirm before creating `~/.config/track-my-work/config.json` and walking them through database setup.
- **Before scheduling a cloud routine** — the user must explicitly consent. Don't silently create a recurring schedule even if setup is going well.
- **Pasted Standup Log URL doesn't resolve** — ask for the URL again; don't guess.
- **Schema mismatch on the user's Standup Log** — if a required column (`Entry`, `Date`, `Impact`, `Type`, `Linear Ticket`, `GitHub PR`, `Notes`) is missing from their DB, tell them which columns to add (or offer to recreate the DB) before continuing. Don't try to write malformed rows.
- **Before creating a duplicate entry** when Step 6 suggests an update — the heuristic for "meaningful change" is imperfect; if it's a close call (e.g., status the same but body slightly reworded), prefer updating over creating.

## Error handling

- **Linear MCP not connected** — tell the user the Linear MCP isn't available and to check their MCP config. The skill cannot run without it.
- **Notion MCP not connected** — same. The skill writes to Notion; without the MCP it's a no-op.
- **`gh` not authenticated** — Step 3 will return zero results from `gh search`. Tell the user to run `gh auth login` and re-scope. Don't silently degrade — explicitly report "GitHub source skipped: gh not authed."
- **Standup Log DB schema doesn't match** — list the missing/wrong columns and stop. Don't try to coerce data into a malformed DB.
- **Timezone detection fails** — fall through the three-fallback ladder above. If even the Python fallback fails, ask the user for their IANA timezone and write it to config so this doesn't recur.
- **`notion-create-pages` returns a validation error** — most often a malformed `Type` multi_select value or a `Date` formatted as a string instead of `{start: "YYYY-MM-DD"}`. Surface the error to the user verbatim — don't paper over it.
- **`link_preview` mention rejected** — retry once with plain inline link (`text` + `link.url`). Never block the whole entry on a mention failure.

## Known issues

- **GitHub MCP token may lack private-repo visibility.** Manifests as Step 3 returning 0 results when the user clearly had PR activity. The `gh search prs` fallback in Step 3 partially mitigates.
- **Linear `assignee: "me"` filter sometimes misses tickets the user only briefly touched.** Surfaces as standup entries missing for cleanup/triage tickets. Workaround: add anything missed via Step 7's manual capture prompt.
- **Comments you authored aren't pulled from Linear.** The MCP has no global "my comments" query, so a ticket you only commented on (didn't create or get assigned) won't appear unless it has an associated PR (Step 3 cross-link). Workaround: Step 7's manual capture prompt.
- **Created-coverage is bounded by a workspace-wide scan.** The MCP has no `creator` filter, so created issues are found by scanning issues created in the lookback window and filtering client-side. In a very large/busy workspace the window may exceed the page limit; the skill flags truncation rather than dropping silently.
