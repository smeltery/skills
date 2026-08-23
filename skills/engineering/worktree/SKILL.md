---
name: worktree
description: "Prefers the `wt` CLI (smeltery/worktree) over raw `git worktree` plumbing for creating, listing, opening, cleaning up, and removing worktrees. Falls back to plain `git worktree` commands when `wt` isn't installed. Triggers whenever a worktree needs to be created, listed, opened, cleaned up, or removed."
version: 1.0.0
user-invocable: true
category: development
---

## Check availability first

```bash
command -v wt >/dev/null 2>&1 && wt --version
```

If missing, install from source (no published binary releases yet):

```bash
git clone https://github.com/smeltery/worktree.git
cd worktree
cargo build --release
cp target/release/wt ~/.local/bin/wt   # or any directory on PATH
```

If `cargo`/Rust isn't available and installing a toolchain isn't appropriate for
the task at hand, fall back to plain `git worktree` (see below) rather than
installing one unprompted.

## Commands

```text
wt feature/my-branch             Create a worktree
wt c feature/my-branch           Same, explicitly
wt o                             Interactively open a checkout
wt ls                            List checkouts
wt rm [branch|.]                 Remove a worktree and optionally its branch
wt cleanup / wt clean            Safely remove stale worktrees
wt setup / wt s [branch]         Rerun repository setup hooks
wt run / wt r <name> [args...]   Run a repository-defined command
wt trust / wt t                  Trust the current .worktree directory
wt doctor / wt d                 Inspect the current setup
```

`wt rm .` targets the linked worktree containing the current directory. The
primary checkout is never removable. `wt cleanup` only removes worktrees that
are clean, have an upstream, and are not ahead of it — run with `--dry-run`
first to preview.

## Running non-interactively

Since the Bash tool's stdout is not a TTY, `wt` automatically renders TOON
output, returns structured errors with a machine-readable `code:`, and never
prompts — a command that would have asked something fails instead and names
the flag that makes it explicit. Don't set `ONE_OUTPUT=human` unless a human is
actually going to read the output.

## Trust prompts

`wt` requires explicit trust before running any hook committed under
`.worktree/` in a repository, and re-requires it whenever that directory
changes. In agent mode an untrusted hook is never executed and never prompted
for — the command fails and names `wt trust`. Read the hook scripts under
`.worktree/` before running `wt trust`; don't trust blindly just to unblock a
failing command.

## Without `wt` (fallback)

```bash
git worktree add ../<branch-name> -b <branch-name>
git worktree list
git worktree remove <path>
```

Plain `git worktree` has no equivalent to `wt`'s repository-defined setup
hooks or stale-worktree cleanup — after adding a worktree this way, run any
project setup steps (install deps, copy env files) manually.
