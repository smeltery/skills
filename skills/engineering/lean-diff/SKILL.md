---
name: lean-diff
description: Keep the net diff as small as possible whenever code is written, edited, or refactored — minimal targeted changes over rewrites, no drive-by reformatting or renaming, no unrequested abstractions, and a git diff review before calling any code change done. Use on every coding task, not just explicit refactors. Also invocable directly to audit and trim the current uncommitted diff.
argument-hint: "[path-or-diff-range]"
---

# Lean Diff

Every extra line changed is a line a reviewer has to read, a line that can hide a regression, and a line that makes a revert harder. The smallest diff that fully satisfies the requirement is the correct diff — this skill is the habit of checking that before calling a change done.

This skill ships a `PostToolUse` hook (`scripts/diff-stat.sh`) that echoes the running `git diff --shortstat` after every `Edit`/`Write`/`MultiEdit`/`NotebookEdit`, so the running total stays visible without waiting for a final review. Use that number as a prompt to re-check scope, not as the goal itself — a genuinely large change should still have a large diff.

## Before editing

- Identify the minimal set of lines that must change to satisfy the requirement. Don't rewrite a whole function or file when a targeted edit does the job.
- Reuse existing functions, types, and helpers instead of duplicating logic nearby.
- If the correct fix genuinely requires a large diff (a real migration, a wide rename across call sites, a requested refactor), say so up front and confirm scope rather than let it grow silently.

## While editing

- Prefer patch-style edits over full-file rewrites — untouched lines should never enter the diff.
- Don't reformat, reflow, reorder imports/members, or rename anything outside what the task asked for, even if it looks nicer. That's a separate change.
- Don't add comments, config flags, defensive checks, tests, or abstractions the task doesn't call for.
- Delete dead code outright rather than commenting it out.
- Match the style of the surrounding code in the lines you do touch instead of imposing a new one.

## Before calling it done

1. Run `git diff --stat` for the shape, then `git diff` to read every changed hunk.
2. For each hunk, ask: is this line required by the task? If not, revert it.
3. Watch specifically for: whitespace-only changes, files touched that aren't part of the task, variables renamed without need, added blank lines, reordered members.
4. Report the net diff (files changed / insertions / deletions) in your summary so the size is visible at a glance.

## Audit mode — invoked directly with no code change in flight

Review the current uncommitted diff end to end:

1. `git status` and `git diff` (staged and unstaged) to see the full scope.
2. Walk every hunk and flag lines that aren't load-bearing for the change's stated purpose — leftover debug output, unrelated formatting, unused variables, duplicated logic that could reuse something existing.
3. Apply the trims directly, then re-run `git diff --stat` and report the before/after line counts.

## When a larger diff is actually right

Don't fight the requirement. A genuine feature, a real cross-cutting rename, or an explicitly requested refactor will have a proportionally larger diff — the goal is zero unnecessary lines, not an arbitrarily small line count. If everything non-essential has been trimmed and the diff is still big, say so and explain why.

## Related skills

- [`simplify`](../simplify/) — a different axis, not a duplicate: `simplify` runs after the diff is settled and improves the *readability* of the surviving lines (naming, comments, structure), and can add lines (a clarifying comment, a split function) if that's what readability needs. `lean-diff` runs throughout editing and cares only about *size* — whether a line needed to exist in the diff at all. Run `lean-diff` first to keep the diff honest, then `simplify` to polish what's left.
- [`loc-budget`](../loc-budget/) — a repo-wide, standing concern (are existing files too big, is the directory structure too flat) enforced via CI gates. `lean-diff` is a per-change, in-the-moment discipline (is *this* diff bigger than it needs to be). A change can pass one and fail the other.
- [`workon`](../workon/) — §3.5 implementation step and §4.3 reviewer-comment fixes
- [`workon-event`](../workon-event/) — `create-pr` handler
- [`pr-monitor`](../pr-monitor/) — review-thread fix handling

`workon` and `workon-event` also carry a numeric **scope-budget gate** (§3.4b) — a hard halt when a diff blows past a multiplier or absolute LOC floor set by `/groom`. That gate is a backstop against gross overrun, not a substitute for this skill: a diff can sail well under the gate and still carry drive-by reformatting, dead code, or an unrequested abstraction. Apply `lean-diff` throughout implementation; let the gate catch what it's there to catch.
