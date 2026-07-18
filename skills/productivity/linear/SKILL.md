---
name: linear
description: Use the `linear` CLI to search Linear, inspect issues, manage comments, list workspace metadata, and check Linear platform status. Use when the user asks about Linear issues, bugs, comments, labels, teams, projects, cycles, documents, notifications, roadmaps, initiatives, or Linear status.
argument-hint: "[Linear query, issue id, or action]"
---

# Linear

Use the installed `linear` command for Linear work when available. It returns
JSON, so prefer structured reads with `jq` or equivalent parsing over brittle
text scraping.

## Availability

First check that the CLI exists:

```bash
linear --help
```

If it is missing, install it from `dotbrains/linear-cli` before continuing.
Prefer the published GitHub Packages install when `npm` is available:

```bash
npm config set @dotbrains:registry https://npm.pkg.github.com
npm config set //npm.pkg.github.com/:_authToken "$(gh auth token)"
npm install -g @dotbrains/linear-cli
linear --help
```

If `gh auth token` is unavailable, ask the user for a GitHub token with
`read:packages` access and use that value for the `_authToken` config. Do not
print or persist the token anywhere except npm's package-auth config.

If GitHub Packages installation is unavailable but repository access works,
install from source:

```bash
git clone https://github.com/dotbrains/linear-cli.git
cd linear-cli
bun install
bun link
linear --help
```

After installing, continue with `linear init` if authentication is missing.
Do not fall back to scraping Linear HTML.

If authentication is missing or stale, run:

```bash
linear init
```

This prompts for a Linear API key and writes the CLI config.

## Common Reads

```bash
linear search "auth bug"
linear issue ENG-123
linear issues --labels Bug
linear comments-mine
linear teams
linear labels
linear workflow-states
linear projects
linear status
```

Use `linear issue <id>` before commenting or updating so you have the current
issue title, state, assignee, labels, and comment context.

## Writes

Before mutating Linear, make sure the requested target is unambiguous. Prefer
human-readable issue identifiers such as `ENG-123` when the user provides them,
and resolve ambiguous search results with the user rather than guessing.

```bash
linear comment-add ENG-123 -b "Comment body"
linear comment-edit <comment-id> -b "Updated comment body"
linear comment-delete <comment-id>
linear issue-create --team <team-id> --title "Issue title"
linear issue-update ENG-123 --title "Updated title"
```

For destructive operations such as deleting issues, comments, labels, projects,
documents, webhooks, roadmaps, or initiatives, ask for explicit confirmation
unless the user already gave an exact command-level instruction.

## Search Flow

When the user asks you to find Linear work:

1. Start broad with `linear search "<terms>"` or the relevant list command.
2. Narrow with structured fields such as team, label, state, assignee, or
   priority where the CLI supports them.
3. Fetch promising issues individually with `linear issue <id>`.
4. Summarize findings with issue identifiers, titles, states, assignees, and
   URLs when present.

## Error Handling

- CLI missing: tell the user the `linear` command is unavailable and provide
  the install requirement.
- Authentication failure: run or suggest `linear init`.
- Empty search result: say no matching Linear items were found and include the
  query or filters used.
- Permission failure: report the Linear error without retrying unrelated
  commands.
- Multiple matches for a write target: stop and ask which issue or resource to
  modify.
