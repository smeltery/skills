#!/usr/bin/env bash
# lean-diff PostToolUse hook — surface the running git diff size after every
# code-touching edit, so scope creep is visible before the agent calls a
# change done rather than only at final review.
#
# Best-effort only: silently no-ops outside a git repo or when there's
# nothing uncommitted yet. Never blocks (always exits 0).
set -u

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

unstaged=$(git diff --shortstat 2>/dev/null)
staged=$(git diff --cached --shortstat 2>/dev/null)

[[ -z "$unstaged" && -z "$staged" ]] && exit 0

echo "[lean-diff] unstaged: ${unstaged:-none} | staged: ${staged:-none}"
echo "[lean-diff] Before finishing: re-check every changed line is required by the task — revert drive-by formatting, unrelated renames, and unrequested additions."

exit 0
