---
name: workon
description: Pick up a Linear ticket end-to-end — worktree, implement, PR, then watch the PR on a 5-min loop addressing reviewer comments (Codex, CodeRabbit), CI failures, and merge conflicts until merged. Use when the user types `/workon <TICKET-ID>` (e.g. `/workon ENG-66`).
argument-hint: "<TICKET-ID>"
---

# Workon: end-to-end ticket driver

Idempotent, state-branched skill. Same invocation drives three phases:

- **Setup** — no worktree yet → create worktree, read ticket, implement, PR, start loop.
- **Watch** — worktree + open PR → address reviewer comments (Codex, CodeRabbit), fix CI, resolve conflicts, check convergence, check merge.
- **Teardown** — PR merged → remove worktree, stop loop.

**Arguments:** "$ARGUMENTS"

## 0. Parse argument

Extract `<TICKET-ID>` (e.g. `ENG-66`). Must match `[A-Z]+-\d+`. If missing or malformed, abort with a short error telling the user the expected form.

## 1. Load state

State file: `~/.claude/workon/<TICKET-ID>.json`. Shape:

```json
{
  "ticketId": "ENG-66",
  "worktreePath": "/absolute/path/to/worktree",
  "branchName": "feat/...",
  "baseBranch": "main",
  "repoSlug": "owner/repo",
  "prNumber": 123,
  "phase": "setup|watch|teardown",
  "convergenceCommentPosted": false,
  "lastAddressedCommentISO": null,
  "lastAddressedCommentIds": [],
  "lastRetriedCheckRunId": null,
  "lastFixedCheckRunId": null,
  "loopStarted": false
}
```

- `lastAddressedCommentIds`: namespaced ids (`issue:<id>` / `review:<id>`) of comments AT `lastAddressedCommentISO`, for boundary-second dedup (§4.3).
- `lastRetriedCheckRunId` / `lastFixedCheckRunId`: per-check-run-id watermarks that stop the loop from rerunning or re-fixing the same failing check forever (§4.4).

Create the `~/.claude/workon/` dir if it doesn't exist. If no state file, this is a fresh Setup run. If state exists, jump to the phase it declares and re-verify against GitHub — phase transitions are owned by the skill, not the state file (state is a cache, GitHub is source of truth).

## 2. Route

```text
if no state file OR phase == "setup":
    run Setup (§3)
elif phase == "watch":
    # Re-verify PR is still open; if merged, route to Teardown
    if pr.state == "MERGED": run Teardown (§5)
    else: run Watch (§4)
elif phase == "teardown":
    # Already done — no-op and hint at /loop-stop
    print "workon <ticket>: already torn down. Run /loop-stop to end the loop."
    exit
```

---

## 3. Setup phase

### 3.1 Load the ticket

Pull full ticket context through the configured **Linear MCP server** before doing anything else. The exact tool prefix depends on the user's MCP server name (e.g. `mcp__claude_ai_Linear__*`); match what's surfaced in the available tool list.

1. **Issue body** — `mcp__*Linear__get_issue`.
2. **Full comment thread** — `mcp__*Linear__list_comments`. Read every comment, not just the most recent — earlier comments usually hold the product reasoning that the title/summary glosses over.
3. **Attachments** — enumerate the attachments returned with the issue and pull each one that's relevant to scope:
   - Linked design docs / specs (Notion, Google Docs, Figma) — open via the appropriate authenticated MCP (e.g. `notion-fetch` for Notion) or `WebFetch` for fully public URLs.
   - Screenshots and inline images — load via `mcp__*Linear__extract_images` so visual content is actually in context, not just referenced.
   - Linked GitHub issues / PRs — `gh issue view` / `gh pr view` to surface upstream / sibling work.
   - Cross-referenced tickets (blockers, parents, duplicates) — recurse with `mcp__*Linear__get_issue` for any that are clearly load-bearing on scope.
   - Skip obvious irrelevances (user avatars, bot footers, generic CI links) — note them but don't fetch.

Do not fall back to the Linear REST API, the `linear` CLI, or scraped HTML for any of the above. If no Linear MCP server is connected, stop and tell the user to connect one — do not guess ticket contents.

Synthesize scope using current status fields, the full comment history, and the pulled attachments — not only title/summary.

If the ticket is ambiguous, under-specified, or blocked on a decision after this full sweep, stop and tell the user. Do not guess, do not create the worktree yet.

### 3.2 Determine repo metadata

- `repoSlug`: `gh repo view --json nameWithOwner --jq .nameWithOwner`
- `baseBranch`: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` (do **not** hardcode `main` or `master`)
- Repo root: `git rev-parse --show-toplevel`

### 3.3 Create the worktree

- Branch name: use conventional prefixes (`feat` / `fix` / `chore`) and append the ticket id for auto-linking: `<type>/<slug>-<ticket-id-lower>`.
- Worktree path: `<repo-parent>/<repo-basename>-wt-<TICKET-ID>`.

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
PARENT=$(dirname "$REPO_ROOT")
REPO_NAME=$(basename "$REPO_ROOT")
WT="$PARENT/${REPO_NAME}-wt-${TICKET_ID}"
git -C "$REPO_ROOT" fetch origin "$BASE_BRANCH"
git -C "$REPO_ROOT" worktree add -b "$BRANCH" "$WT" "origin/$BASE_BRANCH"
```

Write the state file with `phase: "setup"` so crashes can resume cleanly.

### 3.4 Gather repo context

Before writing any code, build a working picture of the repo's conventions, standards, and the tooling already available to you. This is a read-only sweep — do not edit anything yet.

**Repository documentation** — read what's present, skip what isn't:

- Root-level: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `README.md`, `STYLEGUIDE.md`, `ARCHITECTURE.md`.
- `docs/` and `documentation/` trees — focus on entries about contributing, conventions, testing, architecture.
- AI-assistant rules: `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules` — treat as authoritative when present.
- The nearest `CLAUDE.md` / `AGENTS.md` to the files you expect to edit (subdirectory rules can override repo-root rules).
- Lint/format/test config (`.eslintrc*`, `prettier*`, `pyproject.toml`, `tsconfig.json`, `Makefile`, `package.json` scripts) — surfaces required quality gates, naming conventions, and the commands used for §3.5 local checks.

**Available skills** — identify ones that fit the ticket's domain:

- Re-read the available-skills list already provided in this conversation; flag any whose description matches the ticket scope (e.g. `claude-api` for Anthropic SDK work, `tdd` for test-first changes, `simplify` for cleanup passes, `review` before pushing).
- Also scan `~/.claude/skills/`, `~/.agents/skills/`, and `<repo>/.claude/skills/` for project-local skills that may not appear in the conversation list.
- When a skill clearly applies, plan to invoke it via the `Skill` tool during §3.5 rather than reinventing its workflow.

If repo docs and ticket scope conflict, prefer repo docs and raise the conflict on the Linear ticket before coding.

### 3.4b Scope-budget gate

Enforce the ticket's groomed scope budget before handing the PR off for review. Read the `## Scope budget` line from the brief on `<TICKET-ID>` (set by `/groom`). Briefs without the heading skip the check; a malformed line — missing fields, non-numeric, **zero, or negative** — emits one warning and skips rather than guessing (both `loc` and `files` must be strictly positive integers).

Measure the cumulative diff against the base **after the §3.5 implementation pass, before the §3.6 push** — the diff only exists once code is written:

```bash
git fetch origin "$BASE_BRANCH"   # refresh origin/$BASE_BRANCH first
LOC=$(git diff --shortstat "origin/$BASE_BRANCH"...HEAD)        # insertions + deletions
FILES=$(git diff --name-only "origin/$BASE_BRANCH"...HEAD | wc -l)
```

Both the fetch and the triple-dot range are required: a stale `origin/$BASE_BRANCH` mis-measures against an old merge-base, and a bare `git diff --shortstat` (no range) compares the worktree to the index and returns zero after commits — either silently skips the halt.

Halt when **either** `LOC > multiplier × budget.loc` (default `multiplier = 1.5`) **or** `LOC > budget.loc + overage_loc` (default `overage_loc = 500`). File count is reported but does not gate. Thresholds are tunable via `WORKON_SCOPE_OVERAGE_MULTIPLIER` / `WORKON_SCOPE_OVERAGE_LOC`; `WORKON_SCOPE_OVERAGE_OVERRIDE` (truthy: `1`, `true`, `yes`) bypasses the whole halt — raising one threshold env var alone does **not** disable the OR-joined other branch.

On halt: post a split-proposal as a Linear comment via `mcp__*Linear__save_comment` carrying (a) the actual diff summary, (b) the over-budget delta, (c) candidate seams derived from the changed-file groupings, and (d) three options — split the ticket / update the budget on the ticket / user override. Leave the worktree with WIP commits intact, do **not** push, do **not** open the PR, and stop. Resume (re-run `/workon <TICKET-ID>`) once the user splits the ticket or sets the override.

### 3.5 Implement the ticket

Work inside the worktree (`cd "$WT"`). Run autonomously in this phase — no user check-in before opening the PR.

- Apply the conventions and constraints surfaced in §3.4.
- Reuse existing patterns before introducing new libraries/APIs.
- Work in small commits using conventional commit types.
- Run project quality gates locally before pushing.

If implementation requires a product decision outside ticket scope, stop, leave a WIP commit, notify the user, and exit.

### 3.6 Push and open PR

First enforce the §3.4b scope-budget gate against the finished diff. If it halts, stop here — do not push or open the PR.

**Local review rounds next, when a local adversarial reviewer CLI (e.g. `codex`) is available.** AI review on a PR is slow and public — every round costs a push, a wait, and a thread someone has to read — so converge locally first: run the reviewer against the working-tree diff, aiming for 5 rounds with a hard cap of 8. Converged means a full round produced no finding you'd act on; a round of only invalid findings counts as converged. Pull latest `$BASE_BRANCH` before each round that changes code. Bucket every finding: **fix** it only if directly related to the change or genuinely catastrophic; **defer** valid-but-unrelated findings to a follow-up ticket that carries the real obstacle, not just the finding restated (a finding your own diff caused still lands here, with that fact stated); **note** invalid findings with a one-line reason so the next round doesn't relitigate them. No local reviewer CLI → skip; the watch loop (§4) does the same job at the PR, just slower.

**Verify commit signatures before pushing** when the repo requires verified signatures (or signing is configured): `git log --format='%H %G?' origin/$BASE_BRANCH..HEAD` must show `G` on every line. Re-sign any unsigned commit; never bypass signing to get a commit through. With squash-merge the platform signs the squash, so an unsigned branch commit won't block the merge and won't be noticed until it matters — check now.

Use your normal PR workflow. Required behavior:

- Base branch = repo default branch from §3.2.
- PR title: `<type>: <short description> [<TICKET-ID>]`.
- Respect `.github/pull_request_template.md` when present.
- Keep description concise. When local review rounds ran, state the deferrals (with ticket ids) and the invalid findings (with their one-line reasons) upfront — that's what stops the PR-side reviewer re-raising them.
- Assign to the current user.
- **Always open as a draft.** Pass `--draft` to `gh pr create` (or the equivalent flag for whatever PR tool is in use). The skill never opens a PR ready-for-review and never marks an existing draft ready — that decision belongs to the human owner. The watch loop continues to drive Codex comments, CI fixes, and conflict resolution on the draft PR; conversion happens out-of-band.

Record `prNumber` in the state file.

### 3.7 Kick off the watch loop

Set `phase: "watch"`, `loopStarted: true`, then invoke:

```text
/loop 5m /workon <TICKET-ID>
```

Exit setup. The loop drives §4.

---

## 4. Watch phase

Runs once per 5-minute tick. Fast no-op when nothing is actionable. Do §4.1–§4.5 in order each tick.

Context: `cd "$worktreePath"`. Refresh with `git fetch origin`.

### 4.1 Check merge state

```bash
gh pr view "$PR" --json state,mergedAt,mergeable,mergeStateStatus
```

- `state == "MERGED"` → route to Teardown (§5).
- `state == "CLOSED"` (not merged) → post a note on the Linear ticket, set `phase: "teardown"`, remove worktree, exit.
- Otherwise continue.

### 4.2 Fix merge conflicts

Re-read live merge state first (`gh pr view`); if it now reports `MERGEABLE`, the conflict already cleared — no-op this tick. If `mergeable == "CONFLICTING"`:

```bash
git fetch origin
git merge "origin/$BASE_BRANCH"
# resolve mechanical conflicts in-place, then:
git add -A
git commit
git push origin HEAD
```

Resolve each conflict region by reading both sides and merging their intent — never by taking one side wholesale. Note also that a conflicting PR has no merge ref, so its CI cannot run at all; until the conflict is resolved and CI runs on the merged head, treat all check state in §4.4 as unknown, not green.

If the merge driver auto-resolved everything (no conflict markers left), just commit and push the merge.

If any conflict region needs product-level judgment (a semantic conflict), **`git merge --abort`** to restore a clean worktree, then notify the ticket owner on Linear with the conflicting files and exit this tick. Never leave the worktree mid-merge — a half-resolved state breaks the next tick's fetch/merge.

### 4.3 Address reviewer comments (Codex, CodeRabbit)

Fetch comments newer than `lastAddressedCommentISO`. The author regex
`codex|chatgpt|coderabbit` covers Codex (`chatgpt-codex-connector`) and
CodeRabbit (`coderabbitai[bot]`). CodeRabbit's summary/walkthrough/status are
auto-generated *issue* comments (marked with an HTML comment naming
`coderabbit.ai`, or a `walkthrough_start` marker) — skip those; its actionable
findings arrive as review (line-level) comments.

```bash
# Issue comments (general PR comments) — drop CodeRabbit's auto-generated summaries
gh api "repos/$REPO/issues/$PR/comments" --paginate \
  --jq '[.[] | select((.user.login | test("codex|chatgpt|coderabbit"; "i"))
                       and ((.body | test("<!--[^>]*coderabbit\\.ai|walkthrough_start"; "i")) | not))]'

# Review comments (line-level)
gh api "repos/$REPO/pulls/$PR/comments" --paginate \
  --jq '[.[] | select(.user.login | test("codex|chatgpt|coderabbit"; "i"))]'
```

Dedup against the watermark: skip comments older than `lastAddressedCommentISO`, and at the boundary second (`created_at == lastAddressedCommentISO`) skip those whose namespaced id (`issue:<id>` / `review:<id>`) is already in `lastAddressedCommentIds`. Process the survivors oldest-first so the watermark never advances past an unhandled comment.

For each new reviewer comment, bucket it — the bar is deliberately strict because review bots get nit-picky as a diff gets clean:

1. **Fix it** only if it's directly related to this PR's change, or genuinely catastrophic. Those two conditions are the whole test.
2. **Defer it** if it's valid but unrelated: reply acknowledging it and file a follow-up ticket that carries the real obstacle, not just the finding restated — otherwise whoever picks it up re-derives the analysis. A valid-but-unrelated finding your own diff caused still lands here, with that fact stated, not hidden. **Note it** if it's invalid: reply with the one-line reason why, so the next tick doesn't relitigate it — no code change, no ticket.
3. Commit fixes.
4. Resolve review threads explicitly after pushing.
5. Advance the watermark: set `lastAddressedCommentISO` to the newest processed `created_at` and `lastAddressedCommentIds` to the namespaced ids at that timestamp. If the newest timestamp **equals** the existing watermark, union the id sets instead of replacing — so two comments sharing a second aren't dropped or re-processed.

Push once at the end of §4.3.

### 4.4 Fix CI failures

```bash
gh pr checks "$PR"
```

- Ignore non-blocking informational checks.
- **Count which checks actually ran before trusting green.** Passing peripheral checks while the main CI workflow never started is not green; a missing expected workflow is not-yet-known, not a pass.
- Re-read the failing check's live conclusion before acting — it may have cleared on a newer run.
- **Likely-flaky** (`conclusion == "timed_out"`, or an infra-noise check: upload-artifact, cache, network/registry) → rerun the failed jobs once (`gh run rerun <run-id> --failed`) and record the check-run id in `lastRetriedCheckRunId`. Never rerun the same check-run id twice — if it's already in `lastRetriedCheckRunId`, treat the failure as deterministic.
- **Deterministic failure** → fetch failed logs (`gh run view <run-id> --log-failed`), diagnose, fix at the cause, commit, push, and record the check-run id in `lastFixedCheckRunId`. Never fix a red check by deleting, skipping, or weakening the test.
- **Escalate to the ticket owner** (Linear comment, stop fixing this check) when the failure is unfixable — infra / permission / secret errors — or when the same check-run id is already in `lastFixedCheckRunId` (a prior fix didn't take; retrying would just loop).

### 4.5 Convergence check

Read last commit timestamp and last reviewer comment timestamp:

```bash
LAST_COMMIT=$(gh api "repos/$REPO/pulls/$PR/commits" --jq '[.[]][-1].commit.committer.date')
LAST_REVIEWER=$(gh api "repos/$REPO/issues/$PR/comments" --paginate \
  --jq '[.[] | select(.user.login | test("codex|chatgpt|coderabbit"; "i")) | .created_at] | last')
```

Guard every parsed value against being unreadable: an API error string sitting in a timestamp field reads as a definite answer. `LAST_COMMIT` empty or non-ISO → treat convergence as not-yet-known and skip the check this tick; never declare convergence from unreadable inputs. Only an empty `LAST_REVIEWER` has a defined meaning (no reviewer comments yet).

Converged when both:

1. `now - LAST_COMMIT >= 30 minutes`, and
2. `LAST_REVIEWER` is null or `LAST_REVIEWER < LAST_COMMIT`.

If converged and `convergenceCommentPosted == false`, post a concise Linear update with PR URL and set `convergenceCommentPosted: true`.

Continue watching after convergence — humans may still comment and CI/conflict state may change.

---

## 5. Teardown phase

### 5.1 Final Linear comment (optional)

If PR merged and no convergence comment was posted, leave a short merge confirmation with PR URL. Otherwise skip.

### 5.2 Remove the worktree

```bash
REPO_ROOT_MAIN=$(git -C "$worktreePath" rev-parse --git-common-dir | xargs dirname)
cd "$REPO_ROOT_MAIN"
git worktree remove --force "$worktreePath"
git branch -D "$branchName" 2>/dev/null || true
```

### 5.3 Stop the loop

Set `phase: "teardown"` in state so subsequent ticks no-op.

Then try, in order:

1. `/loop-stop` (or equivalent).
2. Scheduler API delete for the matching `/workon <TICKET-ID>` entry.
3. If neither is available, print: **"PR merged, worktree removed. Run /loop-stop to end the watch loop."**

### 5.4 Exit

Print a two-line summary: PR URL + "merged and cleaned up."

---

## Cross-cutting rules

- **One push per tick.** Batch fixes and push once; each push resets the 30-minute convergence clock.
- **Never force-push** unless the user explicitly asks for history rewrite.
- **No speculative ticket creation.** Fix in-scope issues or leave concise open questions for the user.
- **Avoid internal jargon** in ticket comments; write clear external-facing language.
- **State file is a cache.** GitHub and filesystem are sources of truth.
- **Idempotency first.** Setup/watch/teardown must be safe to re-enter.
- **Linear via MCP, always.** Every Linear read (`get_issue`, `list_comments`) and write (`save_comment`, `save_issue`) goes through the configured Linear MCP server — never the Linear REST API, the `linear` CLI, or HTML scraping. The exact tool prefix varies by MCP server name; match what's surfaced in the available tool list. If the Linear MCP is not connected, surface the gap to the user and stop instead of falling back.
