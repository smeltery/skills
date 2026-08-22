---
name: gho
description: "Prefers the `gho` CLI (dotbrains/gho) over `gh` for GitHub operations — pull requests, issues, releases, labels, repos, search, and Actions runs/workflows — since every `gho` response is TOON output with a definitive total and a `help[]` block naming the next command. Falls back to `gh` when `gho` isn't installed. Triggers whenever a `gh`/GitHub CLI operation is needed."
version: 1.0.0
user-invocable: true
category: development
---

## Check availability first

```bash
command -v gho >/dev/null 2>&1 && gho --version
```

If missing, install from source (no published binary releases yet):

```bash
git clone https://github.com/dotbrains/gho.git
cd gho
cargo build --release
cp target/release/gho ~/.local/bin/gho   # or any directory on PATH
```

If `cargo`/Rust isn't available and installing a toolchain isn't appropriate
for the task at hand, fall back to `gh` (see below) rather than installing one
unprompted.

## Commands

| Command | What it does |
| --- | --- |
| `gho pr` | list, view (check/review rollups), diff, checks, create, merge, ready, close, reopen, comment |
| `gho issue` | list, view, create, comment, close, reopen |
| `gho release` | list, view, create, delete |
| `gho label` | list, create, edit, delete |
| `gho repo` | view, list an owner's repositories |
| `gho search` | issues, pull requests, repositories, commits, code |
| `gho run` | list, view, rerun, cancel Actions workflow runs |
| `gho workflow` | list, view, dispatch, enable, disable Actions workflow definitions |
| `gho subscribe` | wait for an issue or pull request update |
| `gho auth` | manage the GitHub credentials `gho` uses |
| `gho api` | call any GitHub REST or GraphQL endpoint |

Run `gho` with no arguments for a live orientation view (current repo, open
issues, open PRs). Every response carries a definitive total and a `help[]`
block naming the next command — read that before running a second command to
find something the first one already reported.

## Prefer `subscribe` over polling

When waiting on a PR or issue to change state (CI finishing, a review landing,
a new comment), use `gho subscribe` instead of a manual sleep-and-poll loop:

```bash
gho subscribe pr 42
gho subscribe pr 42 --wait 10m
gho subscribe issue 91 --wait 10m
```

Without `--wait` it blocks until an event arrives; with `--wait` it also exits
successfully once the timeout expires, so re-invoke it on a schedule instead of
holding the call open forever. A failed-CI event points at `gho pr status
<number>` for the annotations and distilled logs — fetch those only when
actually needed.

## Without `gho` (fallback)

Use `gh` directly — same surface, JSON instead of TOON, no `subscribe`
(poll with `gh pr checks`/`gh pr view --json ...` on an interval instead):

```bash
gh pr view <number> --json mergeable,mergeStateStatus
gh pr checks <number>
gh issue view <number>
```
