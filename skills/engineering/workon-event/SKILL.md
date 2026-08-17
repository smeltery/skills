---
name: workon-event
description: "Event-driven ticket driver — receives a single event (ticket-ready, PR comment, CI failure, base advanced, merge, close, convergence check) and dispatches to the matching handler. Same surface as /workon but reactive instead of polling. Triggers when the harness delivers an event payload referencing a Linear ticket."
version: 1.1.0
argument-hint: "<TICKET-ID> <EVENT-JSON>"
user-invocable: false
category: development
---

# Workon-event: event-driven ticket driver

Reactive sibling of the `workon` skill. The original `workon` runs a Setup pass and then schedules itself on a 5-minute timer; this skill is invoked **once per event** by an external dispatcher (a webhook router, a queue consumer, or a hook on Linear/GitHub state changes) and exits cleanly after handling that single event. There is no polling, no `sleep`, and no scheduled re-entry inside this skill.

This file is the **scaffold**:

- Event-input contract (§2)
- State-file shape (§3)
- Dispatch table that routes each event to a handler (§4)
- §4.1-equivalent merge-state routing — every PR-keyed event re-verifies PR state from GitHub before its handler runs, and re-routes to teardown if the PR is already merged or closed (§5)

Six handlers are fully implemented: `handle_ticket_ready` (§3.1), `handle_pr_comment` (§4.3), `handle_pr_ci_failure` (§4.4), `handle_pr_base_advanced` (§4.2), `handle_pr_merged` (§5), and `handle_pr_closed` (§5). Only `handle_pr_push` and `handle_convergence_check` remain stubs that emit one structured log line and return.

## 0. Parse argument

Inputs:

- `$1` (`<TICKET-ID>`): must match `[A-Z]+-\d+`. If missing or malformed, abort with a short error.
- `$2` (`<EVENT-JSON>`): a single JSON object matching the event-input contract in §2. Exactly one of three forms — the dispatcher picks one and supplies `$2` accordingly:
  1. **Literal JSON string.** `$2` is the raw JSON (e.g. `{"type":"pr-comment",...}`).
  2. **Path to a JSON file.** `$2` is a filesystem path that exists and contains the JSON object.
  3. **Stdin.** `$2` is the literal single-character `-`, in which case the JSON is read from stdin until EOF.

  `$2` is always required; missing or empty `$2` must fail. The empty string is **not** a valid signal for "use stdin" — only `-` is. If `$2 == "-"` and stdin is empty or not valid JSON, fail. If `$2` is non-empty and is neither valid JSON nor an existing file path, fail.

Both inputs are required. The skill never infers the event type from the ticket; the dispatcher tells us what happened.

**Ticket-ID consistency check.** After the JSON is parsed but **before** state is loaded or any handler dispatch, the skill must verify `event.ticketId == $1`. A mismatch indicates a dispatcher bug or an unsafe manual invocation: continuing would load/save state under one ticket while processing event data for another, corrupting the idempotency record on both sides. On mismatch, emit a single `result: "validation-error"` log line (see §6) naming both IDs and exit non-zero. Do not load state, do not dispatch.

## 1. Scope of this scaffold

Six handler bodies are fully implemented: `handle_ticket_ready` (§3.1), `handle_pr_comment` (§4.3), `handle_pr_ci_failure` (§4.4), `handle_pr_base_advanced` (§4.2), `handle_pr_merged` (§5), and `handle_pr_closed` (§5). Only `handle_pr_push` and `handle_convergence_check` remain stubs. The scaffold is invocable end-to-end for all event types.

The §9 reference table at the bottom of this file maps each `workon` section to the event(s) and handler(s) that subsume it.

## 2. Event-input contract

The dispatcher passes a single event per invocation. Every event is a JSON object with this top-level shape:

```json
{
  "type": "<event-type>",
  "ticketId": "PROJ-123",
  "ts": "2026-05-05T22:30:00Z",
  "payload": { "...": "event-specific fields" }
}
```

Required fields on every event:

| Field | Type | Notes |
| --- | --- | --- |
| `type` | string | Non-empty. Recognized values are listed in the taxonomy table below; any other non-empty string passes top-level validation and routes to the `unknown` handler (see Validation rule below). |
| `ticketId` | string | Linear identifier, e.g. `PROJ-123`. Must match `[A-Z]+-\d+`. |
| `ts` | string | RFC 3339 / ISO 8601 timestamp of when the event was emitted. Used for ordering and idempotency. |
| `payload` | object | Event-specific fields (see per-event sections). May be an empty object for events with no extra context. |

### Event taxonomy

The taxonomy covers every phase the original `workon` skill drives — Setup (§3), Watch (§4.1–§4.5), and Teardown (§5).

| Event `type` | Source trigger | Phase served | Handler (this file) |
| --- | --- | --- | --- |
| `ticket-ready` | Linear ticket marked groomed / ready-for-work | Setup | `handle_ticket_ready` |
| `pr-comment` | GitHub PR issue-comment or review-comment created | Watch §4.3 | `handle_pr_comment` |
| `pr-push` | A new commit landed on the PR branch | Watch (commit-time bookkeeping) | `handle_pr_push` |
| `pr-ci-failure` | Required GitHub Actions check turned red | Watch §4.4 | `handle_pr_ci_failure` |
| `pr-base-advanced` | The PR's base branch advanced past its merge-base (whether or not a conflict materialized) | Watch §4.2 | `handle_pr_base_advanced` |
| `pr-merged` | PR `state == "MERGED"` | Teardown §5 | `handle_pr_merged` |
| `pr-closed` | PR `state == "CLOSED"` and not merged | Teardown §5 | `handle_pr_closed` |
| `convergence-check` | Periodic tick from the dispatcher (e.g. every 5 min while a PR is open) | Watch §4.5 | `handle_convergence_check` |

### Per-event payload shapes

`ticket-ready` — no extra fields required. The handler will pull the ticket body itself via the Linear MCP.

```json
{ "type": "ticket-ready", "ticketId": "PROJ-123", "ts": "...", "payload": {} }
```

All `pr-*` and `convergence-check` events carry enough PR identity to look the PR up without re-deriving it from state:

```json
{
  "type": "pr-comment",
  "ticketId": "PROJ-123",
  "ts": "2026-05-05T22:30:00Z",
  "payload": {
    "prNumber": 123,
    "repoSlug": "owner/repo",
    "commentId": 9876543210,
    "commentKind": "issue|review",
    "author": "chatgpt-codex-connector",
    "createdAt": "2026-05-05T22:29:58Z"
  }
}
```

| Event | Required `payload` fields | Optional |
| --- | --- | --- |
| `pr-comment` | `prNumber`, `repoSlug`, `commentId`, `commentKind` (`"issue"` or `"review"`), `author`, `createdAt` | thread/body fields the dispatcher already has on hand |
| `pr-push` | `prNumber`, `repoSlug`, `sha`, `committedAt` | `pusher` |
| `pr-ci-failure` | `prNumber`, `repoSlug`, `checkRunId`, `checkName`, `conclusion` | `runUrl` |
| `pr-base-advanced` | `prNumber`, `repoSlug` | `mergeStateStatus` |
| `pr-merged` | `prNumber`, `repoSlug`, `mergedAt` | `mergedBy`, `mergeCommitSha` |
| `pr-closed` | `prNumber`, `repoSlug`, `closedAt` | `closedBy` (not exposed by `gh pr view --json`; the §5 pre-check leaves it absent on rerouted payloads — fetch via `gh api repos/.../issues/<n>/events` if needed) |
| `convergence-check` | `prNumber`, `repoSlug` | — |

**Validation rule.** Validation is split into two layers, in this order:

1. **Top-level shape (always enforced).** The event must be a JSON object carrying all four top-level fields — `type`, `ticketId`, `ts`, `payload` — with `type` and `ticketId` non-empty strings, `ts` a non-empty string, and `payload` an object. `type` is **not** checked against the known taxonomy at this stage: any non-empty string passes.
2. **Per-type payload shape (only when `type` is a known taxonomy value).** When `event.type` matches one of the rows below, the listed `payload` fields must also be present. Unknown `type` values skip this layer entirely so the dispatcher can route them to `handle_unknown` and emit the `result: "unknown"` line promised in §6.

| Event `type` | Required `payload` fields enforced at validation time |
| --- | --- |
| `ticket-ready` | (none beyond top-level) |
| `pr-comment` | `prNumber`, `repoSlug`, `commentId`, `commentKind`, `author`, `createdAt` |
| `pr-push` | `prNumber`, `repoSlug`, `sha`, `committedAt` |
| `pr-ci-failure` | `prNumber`, `repoSlug`, `checkRunId`, `checkName`, `conclusion` |
| `pr-base-advanced` | `prNumber`, `repoSlug` |
| `pr-merged` | `prNumber`, `repoSlug`, `mergedAt` |
| `pr-closed` | `prNumber`, `repoSlug`, `closedAt` |
| `convergence-check` | `prNumber`, `repoSlug` |

A missing field at either layer emits a single `result: "validation-error"` log line (see §6) naming the missing field, exits non-zero, and writes no state. An unknown `type` value is **not** a validation error — it passes validation, reaches the dispatch table, falls through to `handle_unknown`, and emits the `result: "unknown"` line. This split guarantees that malformed events surface as `validation-error` while unrecognized event types surface as `unknown`, matching the line-count contract in §6.

Validation runs **before** the merge-state pre-check in §5, so a malformed event never causes a `gh pr view` call. An unknown `type` likewise skips the §5 pre-check — there is no PR-keyed routing decision to make for an event whose type the dispatcher doesn't recognize, and the per-type payload contract that would supply `prNumber` / `repoSlug` was not enforced.

## 3. State-file shape

Location: `~/.claude/workon-event/<TICKET-ID>.json`. The directory mirrors the original `workon` skill's `~/.claude/workon/` layout but is deliberately separate so the two skills can run side-by-side without trampling each other during the migration.

```json
{
  "ticketId": "PROJ-123",
  "worktreePath": "/absolute/path/to/worktree",
  "branchName": "feat/...",
  "baseBranch": "main",
  "repoSlug": "owner/repo",
  "prNumber": 123,
  "phase": "setup|watch|teardown",
  "convergenceCommentPosted": false,
  "lastHandledEventTs": null,
  "lastHandledEventType": null
}
```

Field notes:

- `phase` is informational only — this skill does not branch on it. The dispatcher decides which event to send; the handler executes. `phase` is maintained so the original `workon` view of the world still reads cleanly.
- `lastHandledEventTs` / `lastHandledEventType` are for idempotency: if the dispatcher delivers the same event twice (`ts` and `type` match what was last handled for this ticket), handlers may no-op. The scaffold records these on every successful dispatch but does not yet enforce de-duplication — that decision is left to the per-handler implementations.
- The state file is a **cache**. GitHub and Linear are the sources of truth. Every handler that needs PR or ticket state re-reads it from the API rather than trusting the cache.

If the file does not exist, the skill creates the directory and writes a default skeleton with `phase: "setup"` and null PR fields before dispatching. This first-time write is **deferred until after** the §5 pre-check guards have passed (see §4 "Pre-handler steps") so that rejection paths — `validation-error`, `unknown`, `pre-check-error`, and `stale` — never leave a state file behind for a first-time ticket. The unknown-type path short-circuits to `log_unknown` and exits before `load_or_create_state` runs at all; the other rejection paths exit between validation and state load. State load happens immediately before handler invocation, never before.

## 4. Dispatch table

Pseudocode for the top-level body of the skill. Most handler bodies are stubs in the scaffold — they log and return. `handle_pr_comment`, `handle_pr_ci_failure`, and `handle_pr_base_advanced` are the exceptions: their full implementations live in §4.3, §4.4, and §4.2 respectively. The merge-state pre-check in §5 runs before any handler that isn't `ticket-ready`.

The post-handler state-write block (`lastHandledEvent*` + `save_state`) is **mandatory on every dispatched code path**, including re-routed ones. Returning early from a re-route without writing state breaks the idempotency contract in §3 and §7 — the next invocation would treat the event as never handled and could re-run teardown on every retry.

When a re-route flips the effective event type (e.g. `pr-comment` → `pr-merged`), the downstream handler still expects the **payload invariants** for the *new* type to hold (see §2: `pr-merged` requires `payload.mergedAt`, `pr-closed` requires `payload.closedAt`). The original event payload doesn't carry those fields. Before invoking the rerouted handler, the dispatch loop synthesizes a payload that satisfies the destination contract, using fields it already fetched from `gh pr view` for the §5 pre-check. The original event is preserved (for the `rerouted` log line and for `state.lastHandledEvent*`), but the value passed into the rerouted handler is the synthesized event.

**Pre-handler steps.** Validate the event (§2), enforce ticket-ID consistency between `$1` and `event.ticketId` (§0), short-circuit unknown event types (emit `result: "unknown"` and exit), then run the §5 pre-check guards (`pre-check-error`, `stale`, re-route routing). State load/create is deferred until **after** all of those guards pass — it is the last step before invoking a handler. This ordering matters because the `validation-error`, `unknown`, `pre-check-error`, and `stale` outcomes must all leave the state file untouched, and `load_or_create_state` is a disk write for first-time tickets: an early call would write the default skeleton (§3) before the guards rejected the event, mutating disk state on paths the contract says write none. The §0 mismatch case and the unknown-type short-circuit are bounded the same way for the same reason.

**Merge-state pre-check.** For every PR-keyed event (everything except `ticket-ready`), `gh pr view` is called against `payload.repoSlug` / `payload.prNumber` with the `--json` field set defined in §5 — `state`, `mergeable`, `mergeStateStatus`, `mergedAt`, `mergedBy`, `mergeCommit`, `closedAt`. (`gh pr view --json` does not expose `closedBy`; see §5 for how callers obtain closer identity.) If the call itself fails (non-zero exit, network outage, PR-not-found, JSON parse failure), the pre-check emits a single `result: "pre-check-error"` line, exits non-zero, and writes no state — see "`gh pr view` failure handling" below. If the call succeeds: when the PR is `MERGED` and the event is not `pr-merged`, dispatch is re-routed to `handle_pr_merged`; when the PR is `CLOSED` (not merged) and the event is not `pr-closed`, dispatch is re-routed to `handle_pr_closed` — including the case where the original event type was `pr-merged`, since GitHub is the source of truth and a closed-not-merged PR must run the closed-without-merge teardown. When the PR is `OPEN` and the event is `pr-merged` or `pr-closed`, the pre-check rejects the event as stale: no handler runs, no state is written, and a single `result: "stale"` line is emitted. A re-route emits the `rerouted` log line first, before invoking the downstream handler (see §6).

**Synthesized payload on re-route.** The `pr-merged` and `pr-closed` payload contracts in §2 require `mergedAt` and `closedAt` respectively, and the originating event (e.g. a `pr-comment`) does not carry those fields. The dispatch loop builds a payload that satisfies the destination contract from the `gh pr view` result already in hand: `mergedAt` (required), `mergedBy` (optional), and `mergeCommitSha` (optional, sourced from `mergeCommit.oid` **only when `mergeCommit` is non-null**) for `pr-merged`; `closedAt` (required) for `pr-closed`. `mergeCommitSha` is conditional because `gh pr view --json mergeCommit` returns `null` for PRs whose merge mode does not produce a stable merge commit object (and for not-yet-merged PRs); a blind `mergeCommit.oid` dereference would crash before the handler runs and before state is saved, causing the dispatcher to retry the same event indefinitely. When `pr_view.mergeCommit` is null the synthesizer simply omits `mergeCommitSha` from the payload, consistent with its optional status in §2. `closedBy` is intentionally **not** synthesized — `gh pr view --json` does not expose a `closedBy` field, so it stays optional on `pr-closed` (§2) and absent from the synthesized payload. Handlers that need closer identity fetch it separately (see §5). The handler receives the synthesized event; the *original* event is what gets recorded on `state.lastHandledEvent*`, so duplicate-delivery detection keys off what the dispatcher actually sent.

**`gh pr view` failure handling.** The §5 pre-check is a network call and can fail for reasons unrelated to the event — auth outage, transient network error, the PR no longer exists (manually deleted / repo renamed), or GitHub returning a non-zero exit. None of these failure modes correspond to a routing decision, but they must still produce a structured outcome so the dispatcher can classify the result instead of seeing an unstructured crash. On any non-zero exit from the `gh pr view` call (or any failure to parse its JSON output), the dispatch loop emits a single `result: "pre-check-error"` log line (§6) carrying the original event's `eventType` and `eventTs` and a `note` identifying the failure (exit code, stderr summary, or PR-not-found marker), exits non-zero, and writes no state. State is intentionally not written so the dispatcher can re-deliver the same event after the underlying problem clears, on the same idempotency footing as the §5 stale-teardown guard.

**Post-handler bookkeeping is mandatory on every dispatched code path**, including re-routes. The state-write step records the original event's `(type, ts)` and runs before exit. Returning early from a re-route without writing state breaks the idempotency contract in §3 and §7 — the next invocation would treat the event as never handled and could re-run teardown on every retry. The stale-teardown guard and the `pre-check-error` guard are not dispatched paths: both exit before any handler runs and intentionally do **not** write state, so the dispatcher can re-deliver the same event after live PR state catches up (or after the API outage clears).

```
ticket_id = $1
event = parse_json($2)
validate_event(event)
require_equal(event.ticketId, ticket_id)
# State load is deferred until after the §5 pre-check guards. For a
# first-time ticket, load_or_create_state writes a default skeleton
# to ~/.claude/workon-event/<TICKET-ID>.json — running it before the
# pre-check would mutate disk on the stale and pre-check-error paths,
# which the contract says write no state. See "Pre-handler steps" above.

# Unknown event types reach this point because §2 validation only enforces
# the per-type payload contract for known types — an unrecognized type
# passes top-level shape validation and falls through to handle_unknown,
# which emits the result: "unknown" line required by §6. A bare
# DISPATCH_TABLE[type] would raise before logging, breaking the contract.
handler = DISPATCH_TABLE.get(event.type, handle_unknown)
dispatched_event = event

# Short-circuit unknown event types BEFORE load_or_create_state. Per §3
# and §7, the "unknown" outcome is a no-state-mutation rejection path —
# but load_or_create_state writes a default skeleton for first-time
# tickets, so falling through to the post-pre-check load below would
# create ~/.claude/workon-event/<TICKET-ID>.json on disk for a typo'd
# event type that was never actually handled. Emit the unknown line and
# exit before any state I/O happens.
if event.type not in DISPATCH_TABLE:
    log_unknown(ticket_id, event.ts, event.type, f"unhandled event type: {event.type}")
    exit 1

if event.type in PR_KEYED_EVENTS:
    # Single gh pr view call returns every field needed for both
    # the routing decision and the rerouted payload synthesis below.
    # See §5 for the full --json list. Any non-zero exit or JSON
    # parse failure from this call is reported as result:
    # "pre-check-error" without writing state, so the dispatcher
    # can safely re-deliver after the underlying problem clears.
    try:
        pr_view = gh_pr_view(event.payload.repoSlug, event.payload.prNumber)
    except GhPrViewError as err:
        log_pre_check_error(event, err)
        exit 1
    if pr_view.state == "MERGED" and event.type != "pr-merged":
        log_rerouted(event, "pr-merged")
        handler = handle_pr_merged
        # mergeCommitSha is optional in §2 and is only sourced from
        # pr_view.mergeCommit.oid when GitHub actually returned a
        # mergeCommit object. PRs whose merge mode does not produce
        # a stable merge commit (and not-yet-merged PRs) get null
        # back; a blind dereference would crash before the handler
        # runs and trip the dispatcher into infinite retries.
        merged_payload = {
            "prNumber": event.payload.prNumber,
            "repoSlug": event.payload.repoSlug,
            "mergedAt": pr_view.mergedAt,
            "mergedBy": pr_view.mergedBy,
        }
        if pr_view.mergeCommit is not None:
            merged_payload["mergeCommitSha"] = pr_view.mergeCommit.oid
        dispatched_event = synthesize_event(
            type      = "pr-merged",
            ticketId  = event.ticketId,
            ts        = event.ts,
            payload   = merged_payload,
        )
    elif pr_view.state == "CLOSED" and event.type != "pr-closed":
        # GitHub is the source of truth: a CLOSED-not-merged PR routes to
        # handle_pr_closed even when the originating event was mislabeled
        # as pr-merged. The merged branch above only fires when GitHub
        # itself reports MERGED, so this elif cannot run for a truly
        # merged PR.
        log_rerouted(event, "pr-closed")
        handler = handle_pr_closed
        dispatched_event = synthesize_event(
            type      = "pr-closed",
            ticketId  = event.ticketId,
            ts        = event.ts,
            payload   = {
                "prNumber": event.payload.prNumber,
                "repoSlug": event.payload.repoSlug,
                "closedAt": pr_view.closedAt,
                # closedBy is intentionally omitted — gh pr view --json does
                # not expose it. See §5 for how downstream handlers fetch
                # closer identity when needed.
            },
        )
    elif pr_view.state == "OPEN" and event.type in ("pr-merged", "pr-closed"):
        # Stale teardown guard. The event claims the PR is merged or closed,
        # but GitHub reports it is still open — this is a delayed,
        # out-of-order, or post-reopen delivery. "GitHub is source of truth"
        # means we must not run destructive teardown (worktree cleanup,
        # state archival) against a live PR. Emit a structured `stale`
        # outcome and exit without dispatching to a handler. State is not
        # written for stale events: lastHandledEvent* must reflect handlers
        # that actually ran.
        log_stale(event, pr_view.state)
        exit 1

# All pre-check guards have passed (validation, ticket-ID consistency,
# pre-check-error, stale). Only now is it safe to touch the state file:
# load_or_create_state may write the default skeleton for a first-time
# ticket, and that disk write must not happen on any rejection path.
state = load_or_create_state(ticket_id)

handler(ticket_id, dispatched_event, state)

state.lastHandledEventTs   = event.ts
state.lastHandledEventType = event.type
save_state(state)
exit 0
```

### Dispatch table

```
DISPATCH_TABLE = {
  "ticket-ready":       handle_ticket_ready,
  "pr-comment":         handle_pr_comment,
  "pr-push":            handle_pr_push,
  "pr-ci-failure":      handle_pr_ci_failure,
  "pr-base-advanced":   handle_pr_base_advanced,
  "pr-merged":          handle_pr_merged,
  "pr-closed":          handle_pr_closed,
  "convergence-check":  handle_convergence_check,
}

PR_KEYED_EVENTS = {
  "pr-comment", "pr-push", "pr-ci-failure",
  "pr-base-advanced", "pr-merged", "pr-closed",
  "convergence-check",
}
```

### Logging helpers

The pseudocode below uses one helper per `result` value, and the mapping is part of the contract — a handler that picks the wrong helper silently misclassifies the outcome and breaks the §6 line-count table:

| Helper | `result` field value | Used by |
| --- | --- | --- |
| `log_event(...)` | `"stub"` | The two remaining in-taxonomy handler stubs: `handle_pr_push` and `handle_convergence_check` |
| `log_unknown(...)` | `"unknown"` | `handle_unknown` only — never `log_event` |
| `log_rerouted(event, dest_type)` | `"rerouted"` | The §4 dispatch loop, before invoking a re-routed downstream handler |
| `log_stale(event, live_state)` | `"stale"` | The §4/§5 stale-teardown guard |
| `log_pre_check_error(event, err)` | `"pre-check-error"` | The §4/§5 pre-check failure guard |
| `log_validation_error(event, missing_field)` | `"validation-error"` | The §2 validation step (and §0 ticket-ID consistency check) |

`log_event` and `log_unknown` are intentionally distinct helpers, not the same function with a different first argument. Implementations must not collapse them: an unknown event running through `log_event` would emit `result: "stub"`, which the §6 line-count table reserves for handler stubs and which dispatcher retry/metrics logic would interpret as "successfully handled."

### Handler stubs

`handle_pr_push` and `handle_convergence_check` are the two remaining stubs. All other in-taxonomy handlers are fully implemented.

```
handle_ticket_ready(ticket_id, event, state):
    # Real implementation — see "§3.1 ticket-ready handler" section below.
    ticket_ready_handler(ticket_id, event, state)

handle_pr_comment(ticket_id, event, state):
    # Real implementation — see "§4.3 pr-comment handler" section below.
    pr_comment_handler(ticket_id, event, state)

handle_pr_push(ticket_id, event, state):
    log_event("pr-push", ticket_id, event.ts,
              f"stub: pr-push handler not yet implemented (sha={event.payload.sha})")

handle_pr_ci_failure(ticket_id, event, state):
    # Real implementation — see "§4.4 pr-ci-failure handler" section below.
    pr_ci_failure_handler(ticket_id, event, state)

handle_pr_base_advanced(ticket_id, event, state):
    # Real implementation — see "§4.2 pr-base-advanced handler" section below.
    pr_base_advanced_handler(ticket_id, event, state)

handle_pr_merged(ticket_id, event, state):
    # Real implementation — see "§5 Teardown handlers" section below.
    teardown_merged_handler(ticket_id, event, state)

handle_pr_closed(ticket_id, event, state):
    # Real implementation — see "§5 Teardown handlers" section below.
    teardown_closed_handler(ticket_id, event, state)

handle_convergence_check(ticket_id, event, state):
    log_event("convergence-check", ticket_id, event.ts, "stub: convergence handler not yet implemented")

handle_unknown(ticket_id, event, state):
    # log_unknown — NOT log_event — so result is "unknown" per §6,
    # not "stub". Misclassifying as "stub" would tell the dispatcher
    # the unsupported event was successfully handled.
    #
    # In practice the §4 dispatch loop short-circuits unknown event
    # types before load_or_create_state runs, so this body is invoked
    # via the short-circuit's log_unknown call, not through the
    # handler signature above. The signature is preserved for
    # symmetry with the other stubs and for direct test invocation.
    log_unknown(ticket_id, event.ts, event.type, f"unhandled event type: {event.type}")
    exit 1
```

## 3.1 ticket-ready handler

Ports `workon` §3 ("Setup") to the event-driven model. Invoked by the dispatch table when `event.type == "ticket-ready"`. There is no PR yet when this handler runs — it creates the branch and PR.

### Inputs

- `ticket_id`: Linear ticket identifier
- `event.payload`: empty (the handler fetches the ticket body itself via the Linear MCP)
- `state`: setup state loaded from `~/.claude/workon-event/<TICKET-ID>.json`; may be a fresh default skeleton on first run

### Idempotency

A true no-op requires all four responsibilities complete AND the PR is OPEN or MERGED with the `agentic` label. An OPEN PR without the `agentic` label is not a no-op — it must resume at the labeling step. The helper returns `nextStep` which identifies which responsibility to resume at; loop until `nextStep="complete"`.

```
result:"noop:already-set-up"
```

Emit that result line and return zero when the helper returns `nextStep="complete"` and `noop=true`.

### Scope-budget check

Before pushing or opening the PR, run the scope-budget gate described in §8.1. If the diff is over budget and no override is set, post the split-proposal as a Linear comment via `mcp__claude_ai_Linear__save_comment`, leave the worktree with WIP commits intact, do not push, do not open the PR, and exit non-zero. The proposal must carry (a) the actual diff summary, (b) the over-budget delta, (c) candidate seams derived from changed-file groupings, and (d) the three options (split / update the ticket budget / override). Measure the diff with `git fetch origin "$BASE_BRANCH" && git diff --shortstat "origin/$BASE_BRANCH"...HEAD` and `git diff --name-only "origin/$BASE_BRANCH"...HEAD | wc -l` (triple-dot range required; see §8.1 for why a bare shortstat returns zero).

### Implementation

```
ticket_ready_handler(ticket_id, event, state):
    REPO        = event.payload.repoSlug  # passed via event or derived from runner env
    STATE_FILE  = "~/.claude/workon-event/{ticket_id}.json"

    # ── 1. Call helper to determine next step ──
    #
    # bun run src/workflows/workon-event/main.ts setup <ticket-id> <repo> [state-file]
    # Returns JSON: { nextStep, livePrState, liveHasAgenticLabel, noop }
    # nextStep values: transition-in-progress | create-pr | apply-label |
    #                  invite-codex | transition-in-review | complete
    setup_result = shell("""
      bun run src/workflows/workon-event/main.ts setup \
        "$ticket_id" "$REPO" "$STATE_FILE"
    """)

    # ── 2. Idempotency guard ──
    if setup_result.noop == true:
        echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"ticket-ready","eventTs":"'"$event.ts"'","result":"noop:already-set-up","note":"all four responsibilities complete, PR open with agentic label"}'
        return

    # ── 3. Loop through each mandatory responsibility ──
    #
    # After each step, persist the updated flag, then call the helper again
    # to get the next step. Repeat until nextStep="complete". Never stop after
    # only one step — all four are mandatory.
    while setup_result.nextStep != "complete":
        match setup_result.nextStep:

            case "transition-in-progress":
                # Responsibility 1: move ticket to In Progress before any code exists.
                mcp__claude_ai_Linear__save_issue(
                    id=<linear-issue-id-for-ticket_id>,
                    stateId=<in-progress-state-id>
                )
                state.ticketTransitionedToInProgress = true
                persist(state, STATE_FILE)

            case "create-pr":
                # Responsibility 2: implement the ticket and open a draft PR.
                #
                # Read the ticket body via mcp__claude_ai_Linear__get_issue to understand scope.
                # Create branch off main (naming: feat/<slug> or fix/<slug>).
                # Work in GITHUB_WORKSPACE (the runner's checkout root — no sub-worktree
                # for ticket-ready since there is no existing PR).
                # Run quality gates before opening the PR (typecheck, lint, tests).
                #
                # Scope-budget check fires here, before gh pr create:
                #   git fetch origin "$BASE_BRANCH"
                #   read loc_ins loc_del < <(git diff --shortstat "origin/$BASE_BRANCH"...HEAD | grep -oP '\d+(?= insertion)' ; git diff --shortstat ... | grep -oP '\d+(?= deletion)')
                #   LOC=$(( loc_ins + loc_del ))
                #   files=$(git diff --name-only "origin/$BASE_BRANCH"...HEAD | wc -l)
                #   if over_budget(LOC, files, budget): halt (post Linear comment, exit 1)
                #
                # If a previous PR was already in state (closed PR being replaced):
                #   clear post-PR flags before persisting the new number:
                #   state.agenticLabelApplied = false
                #   state.codexReviewInvited = false
                #   state.ticketTransitionedToInReview = false
                gh pr create --draft --title "<title>" --body "<body>" --repo "$REPO"
                state.prNumber = <new-pr-number>
                persist(state, STATE_FILE)

            case "apply-label":
                # Responsibility 2b: label the PR so it's visible to watch loops.
                gh pr edit "$state.prNumber" --add-label agentic --repo "$REPO"
                state.agenticLabelApplied = true
                persist(state, STATE_FILE)

            case "invite-codex":
                # Responsibility 3: invite Codex after label is confirmed.
                gh pr comment "$state.prNumber" --body "@codex review" --repo "$REPO"
                state.codexReviewInvited = true
                persist(state, STATE_FILE)

            case "transition-in-review":
                # Responsibility 4: move ticket to In Review after label+comment confirmed.
                mcp__claude_ai_Linear__save_issue(
                    id=<linear-issue-id-for-ticket_id>,
                    stateId=<in-review-state-id>
                )
                state.ticketTransitionedToInReview = true
                persist(state, STATE_FILE)

        # Re-query helper to get the next step.
        setup_result = shell("""
          bun run src/workflows/workon-event/main.ts setup \
            "$ticket_id" "$REPO" "$STATE_FILE"
        """)

    # ── 4. Finalize ──
    state.phase = "watch"
    persist(state, STATE_FILE)

    echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"ticket-ready","eventTs":"'"$event.ts"'","result":"acted","note":"setup complete, PR #'"$state.prNumber"' opened and handed to Codex"}'
```

### Logging and result classification

Emit `result: "acted"` on successful completion. Emit `result: "noop:already-set-up"` when the helper returns noop. On scope-budget halt, emit `result: "halted:over-budget"` before exiting non-zero. Do NOT use `log_event` (which emits `result: "stub"`).

### Cross-cutting constraints (from §8)

- **One push per invocation.** Commit incrementally, push once before `gh pr create`.
- **Never force-push** unless explicitly requested.
- **Worktree is the source of truth for edits.** Work in GITHUB_WORKSPACE for ticket-ready (no sub-worktree before the PR exists).
- **No speculative tickets.** Leave out-of-scope concerns as Open Questions on Linear.
- **No internal jargon in external artifacts.** Commit messages, PR body, and Linear comments describe the change.
- **Use project-preferred terminology** in any text that reaches a human.

---

## 4.3 pr-comment handler

Ports `workon` §4.3 ("Address reviewer comments") to the event-driven model. Invoked by the dispatch table when `event.type == "pr-comment"` and the PR is OPEN. Handles automated-reviewer bots — Codex/ChatGPT and CodeRabbit.

### Inputs

- `ticket_id`: Linear ticket identifier
- `event.payload.prNumber`, `event.payload.repoSlug`: PR identity
- `event.payload.commentId`, `event.payload.commentKind` (`"issue"` or `"review"`), `event.payload.createdAt`: the triggering comment
- `state.lastAddressedCommentISO`: ISO-8601 high-water mark — comments older than this timestamp have already been handled
- `state.lastAddressedCommentIds`: set of `"issue:<id>"` / `"review:<id>"` namespaced keys for comments AT the high-water timestamp, to handle boundary-second deduplication

### Implementation

```
pr_comment_handler(ticket_id, event, state):
    PR   = event.payload.prNumber
    REPO = event.payload.repoSlug
    watermark_iso = state.lastAddressedCommentISO   # null on first run
    watermark_ids = state.lastAddressedCommentIds   # [] on first run

    # ── 1. Fetch all reviewer issue comments on the PR ──
    #
    # --paginate is required; --slurp cannot be combined with --jq
    # (unsupported by gh); use external jq -s 'add // []' to merge pages.
    # Filter to automated-reviewer authors with an anchored, case-insensitive
    # regex covering both supported bots:
    #   codex|chatgpt → Codex      (chatgpt-codex-connector, codex* logins)
    #   coderabbit    → CodeRabbit (coderabbitai, coderabbitai[bot])
    # (CodeRabbit added alongside the original codex|chatgpt filter.)
    #
    # CodeRabbit posts its summary, walkthrough, and status as PR *issue*
    # comments carrying an auto-generated marker — an HTML comment naming
    # `coderabbit.ai` (e.g. `<!-- This is an auto-generated comment: summarize
    # by coderabbit.ai -->`) or a `walkthrough_start` marker. Those are
    # informational, not actionable findings, so they are excluded here:
    # replying to them only adds noise, and CodeRabbit's actionable findings
    # arrive as review (inline) comments fetched in step 2. Codex issue
    # comments carry no such marker and are kept.
    issue_comments = shell("""
      gh api "repos/$REPO/issues/$PR/comments" --paginate \
        | jq -s 'add // [] | [.[] | select(
            (.user.login | test("codex|chatgpt|coderabbit"; "i")) and
            ((.body | test("<!--[^>]*coderabbit\\.ai|walkthrough_start"; "i")) | not)
          )]'
    """)

    # ── 2. Fetch all reviewer review (inline/line-level) comments ──
    #
    # /pulls/$PR/comments returns review comments. Same reviewer-author regex
    # (codex|chatgpt|coderabbit) — this is where CodeRabbit's actionable
    # line-level findings live. Filter replies (in_reply_to_id != null) — only
    # top-level comments are actionable findings; a reply to a prior reply is
    # not an open question for this handler. Note: this endpoint uses
    # snake_case, not camelCase.
    review_comments = shell("""
      gh api "repos/$REPO/pulls/$PR/comments" --paginate \
        | jq -s 'add // [] | [.[] | select(
            (.user.login | test("codex|chatgpt|coderabbit"; "i")) and
            (.in_reply_to_id == null)
          )]'
    """)

    # ── 3. Deduplicate against the watermark ──
    #
    # A comment is already-addressed when:
    #   (a) its createdAt is strictly before watermark_iso, OR
    #   (b) its createdAt equals watermark_iso AND its namespaced key is in
    #       watermark_ids.
    # Namespace: issue comments use "issue:<id>", review comments use "review:<id>".
    # This prevents cross-endpoint ID collisions (GitHub issue IDs and review
    # comment IDs share a numeric space).
    new_issue_comments   = [c for c in issue_comments
                            if not already_addressed(c.id, "issue", c.created_at,
                                                     watermark_iso, watermark_ids)
                            and not c.body.startswith("<!-- workon-event-reply -->")]

    new_review_comments  = [c for c in review_comments
                            if not already_addressed(c.id, "review", c.created_at,
                                                     watermark_iso, watermark_ids)]

    # Merge and sort oldest-first so comments are processed in the order
    # they were written. Both endpoints use independent ordering; a global
    # sort prevents a newer comment from the other stream from being
    # processed before an older one, which would advance the watermark
    # past the older one and drop it permanently.
    all_new = sort_by_created_at(
        [(c, "issue")  for c in new_issue_comments] +
        [(c, "review") for c in new_review_comments]
    )

    if len(all_new) == 0:
        log_event("pr-comment", ticket_id, event.ts,
                  f"no new reviewer comments newer than watermark={watermark_iso}")
        return  # state.lastHandledEvent* written by dispatch loop

    # ── 4. Address each new reviewer comment ──
    #
    # Work in the PR's worktree. The worktree path is in state.worktreePath
    # (set by the setup handler). Verify it exists before starting; if it
    # doesn't, post a Linear escalation comment and exit non-zero so the
    # dispatcher retries.
    if not path_exists(state.worktreePath):
        post_linear_comment(ticket_id,
            f"pr-comment handler: worktree {state.worktreePath} not found. "
            f"PR #{PR} in {REPO}. Manual intervention may be needed.")
        exit 1

    addressed_comments = []  # list of (id, namespace, createdAt) for watermark update

    for (comment, ns) in all_new:
        comment_id  = comment.id          # numeric GitHub ID
        comment_iso = comment.created_at  # ISO-8601

        if ns == "review":
            # For review comments: fetch the thread node ID needed for
            # resolveReviewThread mutation. Use the REST comment ID to
            # look up the GraphQL node ID via the reviews endpoint:
            #   gh api graphql -f query='
            #     query($id: Int!, $repo: String!, $owner: String!) {
            #       repository(owner: $owner, name: $repo) {
            #         pullRequest(number: $id) {
            #           reviewThreads(first: 100) {
            #             nodes {
            #               id
            #               isResolved
            #               comments(first: 1) { nodes { databaseId } }
            #             }
            #           }
            #         }
            #       }
            #     }' -F id=$PR -f repo=<repo-name> -f owner=<owner>
            # Match threads whose first comment's databaseId == comment.id.
            # Store the thread node ID for later resolution.
            thread_id = resolve_thread_id(REPO, PR, comment_id)

        # Read the comment body and decide: fix or explain-and-resolve.
        body = comment.body

        # Bucket the finding — the bar is deliberately strict because review
        # bots get nit-picky as a diff gets clean (mirrors workon §4.3):
        #   fix     — directly related to this PR's change, or genuinely
        #             catastrophic; those two conditions are the whole test.
        #   explain — everything else. Valid but unrelated: acknowledge, cite
        #             the follow-up ticket that carries the real obstacle
        #             (a finding this diff caused still defers, with that fact
        #             stated). Invalid: give the one-line reason so the next
        #             event doesn't relitigate it.

        decision = judge_comment(body)  # "fix" | "explain"

        if decision == "fix":
            apply_fix_in_worktree(state.worktreePath, body)
            # Commit message follows workon §4.3: descriptive when possible,
            # generic fallback.
            commit_message = derive_commit_message(body) or "fix: address reviewer feedback"
            git_commit(state.worktreePath, commit_message)
        else:
            # Post a reply explaining the decision. The reply sentinel
            # "<!-- workon-event-reply -->" must be the FIRST thing in the
            # body so future fetches can exclude it from the reviewer-comment
            # list and prevent self-reply loops.
            reply_body = "<!-- workon-event-reply -->\n" + explanation(body)
            if ns == "review":
                # Reply to a review comment thread:
                gh api "repos/$REPO/pulls/$PR/comments" \
                    --method POST \
                    -f body="$reply_body" \
                    -F in_reply_to=$comment_id
            else:
                # Reply to an issue comment (general PR comment):
                gh api "repos/$REPO/issues/$PR/comments" \
                    --method POST \
                    -f body="$reply_body"

        addressed_comments.append((comment_id, ns, comment_iso))

        # ── 5. Resolve the review thread ──
        #
        # REQUIRED after addressing a review comment, regardless of whether
        # the fix was applied or the comment was replied to. Pushing a commit
        # does NOT auto-resolve GitHub review threads — only calling
        # resolveReviewThread does. Leaving threads open makes addressed
        # findings look like open work to human reviewers.
        if ns == "review" and thread_id is not None:
            gh api graphql -f query='
              mutation($id: ID!) {
                resolveReviewThread(input: {threadId: $id}) {
                  thread { id isResolved }
                }
              }' -F id="$thread_id"

    # ── 6. Single push ──
    #
    # Push all commits accumulated in this handler invocation in one shot.
    # Never push per-comment — each push resets the 30-minute convergence
    # clock and burns a CI run. If there are no new commits (all comments
    # were explain-and-resolve), skip the push.
    if git_has_unpushed_commits(state.worktreePath, state.branchName):
        git push origin HEAD  # from within state.worktreePath

    # ── 7. Advance the watermark ──
    #
    # Boundary-second semantics (see watermark.ts for the full contract):
    #   - Find the max createdAt among addressed_comments.
    #   - If it is newer than watermark_iso → replace lastAddressedCommentIds.
    #   - If it equals watermark_iso → merge (union) the ID sets.
    #   - If it is older → no change (should not happen under normal operation).
    new_iso = max(c.createdAt for c in addressed_comments)
    if watermark_iso is None or new_iso > watermark_iso:
        state.lastAddressedCommentISO = new_iso
        state.lastAddressedCommentIds = [
            f"{ns}:{cid}" for (cid, ns, created) in addressed_comments
            if created == new_iso
        ]
    elif new_iso == watermark_iso:
        new_keys = {f"{ns}:{cid}" for (cid, ns, created) in addressed_comments
                    if created == new_iso}
        state.lastAddressedCommentIds = list(
            set(watermark_ids) | new_keys
        )
    # else: new_iso < watermark_iso → no change

    log_event("pr-comment", ticket_id, event.ts,
              f"addressed {len(addressed_comments)} reviewer comment(s) "
              f"on PR #{PR}; pushed={git_has_unpushed_commits_was_true}")
```

### Logging and result classification

This handler MUST emit `result: "acted"` (not `result: "stub"`) in its `log_event` call. The dispatcher runner reads the skill's stdout to distinguish real work from a no-op — a `stub` result is classified as `noop:stub` and flagged in the job summary. Use the logging contract in §6 but with `result: "acted"` (or an appropriate production value such as `"noop:nothing-actionable"` when the watermark already covers all comments).

The `log_event` helper defined in §4 always emits `result: "stub"` — do NOT use it here. Emit the JSON line directly:

```bash
echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-comment","eventTs":"'"$event_ts"'","result":"acted","note":"'"$summary"'"}'
```

Or when no actionable comments were found (watermark covers everything):

```bash
echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-comment","eventTs":"'"$event_ts"'","result":"noop:nothing-actionable","note":"no new reviewer comments newer than watermark"}'
```

Both `"acted"` and `"noop:nothing-actionable"` are non-stub results that the dispatcher runner classifies correctly. Only `"stub"` triggers the `noop:stub` no-op classification.

### Cross-cutting constraints (from §8)

- **One push per invocation.** Commit incrementally, push once at the end.
- **Never force-push** unless explicitly requested.
- **Worktree is the source of truth for edits.** All fixes happen in `state.worktreePath`. Do not edit files in the repo root (this skill's own checkout).
- **No speculative tickets.** Surface out-of-scope concerns as PR comments or Open Questions on Linear — do not create new tickets.
- **No internal jargon in external artifacts.** Commit messages, PR replies, and Linear comments describe the change, not team-local labels.

---

## 4.4 pr-ci-failure handler

Ports `workon` §4.4 ("Fix CI failures") to the event-driven model. Invoked by the dispatch table when `event.type == "pr-ci-failure"` and the PR is OPEN.

### Inputs

- `ticket_id`: Linear ticket identifier
- `event.payload.prNumber`, `event.payload.repoSlug`: PR identity
- `event.payload.checkRunId`: the GitHub Actions check-run ID for the failing check
- `event.payload.checkName`: human-readable name of the failing check (e.g. `typecheck`, `lint`)
- `event.payload.conclusion`: the check's terminal conclusion (`failure`, `timed_out`, `cancelled`, etc.)
- `event.payload.runUrl` (optional): direct URL to the failing workflow run
- `state.worktreePath`: filesystem path to the PR's worktree

### Implementation

```
pr_ci_failure_handler(ticket_id, event, state):
    PR         = event.payload.prNumber
    REPO       = event.payload.repoSlug
    check_id   = event.payload.checkRunId
    check_name = event.payload.checkName
    conclusion = event.payload.conclusion

    # ── 1. Re-read current check state — the event may be stale ──
    #
    # The dispatcher fires this handler when a check turns red, but CI can
    # self-recover (e.g. a transient outage clears, a re-run was manually
    # triggered). Re-fetch the specific run's conclusion before doing any
    # work; if it has since passed, no action is needed.
    #
    # GET /repos/{owner}/{repo}/check-runs/{check_run_id}
    live_run = gh api "repos/$REPO/check-runs/$check_id"
    if live_run.conclusion == "success":
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-ci-failure","eventTs":"' + event.ts + '","result":"noop:check-already-passed","note":"check ' + check_name + ' now passing — no fix needed"}')
        return

    # ── 2. Classify the failure: flaky vs. deterministic ──
    #
    # Flaky signals: `conclusion == "timed_out"`, or the check name matches
    # known infra-noise patterns (e.g. "upload-artifact", "cache", network
    # errors in logs). Also treat a fresh failure on a check that passed on
    # the immediately prior run as a candidate flake.
    #
    # Strategy: rerun once if the failure looks flaky; if it fails again, or
    # if the failure looks deterministic from the start, diagnose and fix.
    #
    # Avoid re-running the same run_id twice in a row — GitHub deduplicates
    # re-run requests on the same check-run within a short window, so a
    # double-rerun emits a 422 and wastes an API call. Guard with
    # state.lastRetriedCheckRunId: if check_id == state.lastRetriedCheckRunId,
    # skip straight to the diagnose-and-fix path. The state field is nil until
    # first set here.

    is_likely_flaky = (conclusion == "timed_out") or looks_infra_noise(live_run.output.text)

    if is_likely_flaky and state.lastRetriedCheckRunId != check_id:
        # Rerun once before diagnosing.
        #
        # `gh run rerun --failed` re-queues only the failed jobs, not the
        # full workflow. Requires `actions:write`. The check-run belongs to a
        # workflow run; extract the workflow run ID from the check-run object.
        #
        # GET /repos/{owner}/{repo}/check-runs/{id} returns
        # check_suite.id — that is the check-suite, not the workflow run.
        # Resolve the workflow run id via:
        #   gh api "repos/$REPO/actions/runs?check_suite_id=<suite_id>"
        #   and pick runs[0].id.
        # Then rerun:
        #   gh run rerun <workflow_run_id> --failed --repo "$REPO"
        suite_id     = live_run.check_suite.id
        runs_page    = gh api "repos/$REPO/actions/runs?check_suite_id=$suite_id"
        workflow_run_id = runs_page.workflow_runs[0].id
        gh run rerun "$workflow_run_id" --failed --repo "$REPO"

        state.lastRetriedCheckRunId = check_id
        # Emit a structured result so the dispatcher knows a rerun was issued
        # and should re-evaluate when the rerun completes.
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-ci-failure","eventTs":"' + event.ts + '","result":"acted","note":"rerun issued for likely-flaky check ' + check_name + ' (run ' + str(workflow_run_id) + '); awaiting outcome"}')
        return  # state.lastHandledEvent* + lastRetriedCheckRunId written by dispatch loop

    # ── 3. Diagnose from failing logs ──
    #
    # Fetch the annotated log for the failed jobs only. This avoids pulling
    # multi-megabyte success logs and focuses the diagnostic context.
    #
    #   gh run view <workflow_run_id> --log-failed --repo "$REPO"
    #
    # The log is streamed to stdout; capture it and scan for the first
    # clearly actionable error region (compile error, lint failure, test
    # assertion, type error). Trim to ≤200 lines of context around the first
    # error — models and readers lose signal past that threshold.
    if state.lastRetriedCheckRunId == check_id:
        # Already retried once; we need the new workflow run id from the
        # re-queued run, but since the re-run produces a new check_run_id,
        # a re-delivery of pr-ci-failure from the dispatcher will carry the
        # new check_id. If we're here with the same check_id post-rerun, the
        # rerun itself failed — use the same run for diagnosis.
        suite_id     = live_run.check_suite.id
        runs_page    = gh api "repos/$REPO/actions/runs?check_suite_id=$suite_id"
        workflow_run_id = runs_page.workflow_runs[0].id
    # else: workflow_run_id was resolved in step 2 for the fresh-fail path

    log_text = gh run view "$workflow_run_id" --log-failed --repo "$REPO"
    failure_summary = extract_first_error_region(log_text, max_lines=200)

    # ── 4. Decide: fixable vs. needs-human ──
    #
    # Fixable in this handler:
    #   - TypeScript type errors in files we own (tsc output, jest type errors)
    #   - Lint rule violations with a clear auto-fix path (eslint, prettier)
    #   - Test failures caused by a deterministic assertion that matches the
    #     current diff (i.e. the test was checking old behavior we changed)
    #   - Missing generated file (e.g. a catalog regeneration step failed
    #     because a source file changed but the generated output wasn't updated)
    #
    # Escalate if:
    #   - The failure is in infrastructure we don't own (third-party service
    #     calls, Docker build environment, external network timeouts on
    #     non-flaky-patterned runs)
    #   - The error message suggests a secret/permission problem
    #   - The failure is in a different PR's check that was grouped into the
    #     same workflow (rare but possible on mono-repo matrix builds)
    #   - We've already attempted and pushed a fix for this exact check_id
    #     in a prior invocation (state.lastFixedCheckRunId == check_id) —
    #     to avoid infinite fix loops, escalate instead of retrying

    unfixable = is_infra_failure(failure_summary) \
                or is_permission_failure(failure_summary) \
                or (state.lastFixedCheckRunId == check_id)

    if unfixable:
        reason = "already-attempted" if state.lastFixedCheckRunId == check_id else failure_summary[:120]
        post_linear_comment(ticket_id,
            f"pr-ci-failure handler: check '{check_name}' failed and cannot be fixed automatically. "
            f"PR #{PR} in {REPO}. Reason: {reason}. Manual intervention needed.")
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-ci-failure","eventTs":"' + event.ts + '","result":"escalated:needs-human","note":"' + reason[:120] + '"}')
        return

    # ── 5. Apply the fix in the worktree ──
    #
    # Verify the worktree is present before touching anything.
    if not path_exists(state.worktreePath):
        post_linear_comment(ticket_id,
            f"pr-ci-failure handler: worktree {state.worktreePath} not found. "
            f"Cannot apply fix for check '{check_name}' on PR #{PR} in {REPO}. "
            f"Manual intervention may be needed.")
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-ci-failure","eventTs":"' + event.ts + '","result":"error","note":"worktree missing: ' + state.worktreePath + '"}')
        exit 1

    # Work inside the worktree. Read the relevant source files identified by
    # the failure_summary, then apply the minimal fix. Commit with a message
    # that names the check so CI and reviewers can trace the commit to the
    # failure.
    apply_fix_in_worktree(state.worktreePath, failure_summary)
    commit_message = f"fix(ci): resolve {check_name} failure"
    git_commit(state.worktreePath, commit_message)

    # ── 6. Single push ──
    #
    # One push per invocation — matches §8's "one push per handler" rule.
    git push origin HEAD  # from within state.worktreePath

    # Record that we pushed a fix for this check_run_id so a subsequent
    # re-delivery of the same event (same check_id, same ts) is treated as
    # already-attempted rather than triggering a second fix attempt.
    state.lastFixedCheckRunId = check_id

    summary = f"applied fix for check '{check_name}' on PR #{PR}; pushed commit"
    print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-ci-failure","eventTs":"' + event.ts + '","result":"acted","note":"' + summary + '"}')
```

### Result classification

This handler emits one of four `result` values via direct JSON — never `"stub"`:

| Result | Condition |
| --- | --- |
| `"noop:check-already-passed"` | Live check state is `success` when re-read; nothing to do |
| `"acted"` with note `"rerun issued…"` | Likely-flaky failure; a rerun was dispatched |
| `"acted"` with note `"applied fix…"` | Deterministic fix pushed to the PR branch |
| `"escalated:needs-human"` | Infra/permission failure, or same check_id already attempted once |
| `"error"` | Worktree is missing; exit non-zero so dispatcher retries |

The `"escalated:needs-human"` path also posts a Linear comment so the ticket owner sees it even if they're not watching the PR.

### Retry budget and idempotency

- `state.lastRetriedCheckRunId` guards the flake-rerun: at most one rerun per unique `checkRunId`. If the dispatcher re-delivers the same event after the rerun completes (same `checkRunId`, possibly different `ts`), the handler skips straight to diagnosis.
- `state.lastFixedCheckRunId` guards the fix-push: at most one fix attempt per unique `checkRunId`. A second delivery with the same `checkRunId` (e.g. a duplicate from the dispatcher or a stale requeue) escalates rather than re-applying a fix, preventing fix-loop spirals.
- Both state fields start as `nil` and are written to `state` before the dispatch loop records `lastHandledEvent*` on exit. Neither field is in the base state-file schema (§3) — implementations must treat a missing key as `nil`.

### Cross-cutting constraints (from §8)

- **One push per invocation.** Steps 5–6 commit all changes and push once.
- **Never force-push.**
- **Worktree is the source of truth for edits.** All fixes apply in `state.worktreePath`.
- **No speculative tickets.** Surface unfixable failures as PR comments and Linear comments; do not create new tickets.

---

## 4.2 pr-base-advanced handler

Ports `workon` §4.2 ("Fix merge conflicts") to the event-driven model. Invoked by the dispatch table when `event.type == "pr-base-advanced"` and the PR is OPEN. The event signals that the PR's base branch has advanced past its current merge-base, which may or may not have produced a conflict.

### Inputs

- `ticket_id`: Linear ticket identifier
- `event.payload.prNumber`, `event.payload.repoSlug`: PR identity
- `event.payload.mergeStateStatus` (optional): GitHub's cached `mergeStateStatus` at dispatch time (e.g. `CONFLICTING`, `CLEAN`, `UNKNOWN`)
- `state.worktreePath`: filesystem path to the PR's worktree
- `state.baseBranch`: the PR's base branch name (e.g. `main`)

### Implementation

```
pr_base_advanced_handler(ticket_id, event, state):
    PR          = event.payload.prNumber
    REPO        = event.payload.repoSlug
    BASE_BRANCH = state.baseBranch  # e.g. "main"

    # ── 1. Re-read live merge state — the event may be stale ──
    #
    # `mergeStateStatus` in the event payload is an optional hint from the
    # dispatcher, captured at dispatch time. GitHub's state can change by the
    # time this handler runs (e.g. the conflict was resolved by another push,
    # or the base advanced again). Re-fetch from the API to avoid acting on
    # stale state.
    #
    # The §5 pre-check already called `gh pr view --json ... mergeable,mergeStateStatus`
    # before dispatch; the handler receives a fresh event but not the live view
    # result. Re-issue a targeted call here.
    pr_view = gh pr view "$PR" --repo "$REPO" --json mergeable,mergeStateStatus,headRefOid
    live_mergeable         = pr_view.mergeable           # "MERGEABLE" | "CONFLICTING" | "UNKNOWN"
    live_merge_state       = pr_view.mergeStateStatus    # "CLEAN" | "CONFLICTING" | "UNKNOWN" | ...
    current_head_sha       = pr_view.headRefOid

    # ── 2. Verify the worktree is present ──
    if not path_exists(state.worktreePath):
        post_linear_comment(ticket_id,
            f"pr-base-advanced handler: worktree {state.worktreePath} not found. "
            f"Cannot merge base into PR #{PR} in {REPO}. Manual intervention may be needed.")
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"error","note":"worktree missing: ' + state.worktreePath + '"}')
        exit 1

    # ── 3. Fetch and check if merge is needed ──
    #
    # Always fetch to make sure the local clone sees the latest base tip.
    git fetch origin "$BASE_BRANCH"  # from within state.worktreePath

    # If GitHub reports the PR is already MERGEABLE (no conflict), the base
    # advanced but did not produce a conflict — nothing to resolve. Still
    # confirm the local branch tip matches the remote HEAD to rule out a
    # local-only divergence.
    if live_mergeable == "MERGEABLE" and live_merge_state not in ("CONFLICTING", "UNKNOWN"):
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"noop:no-conflict","note":"base advanced but PR is MERGEABLE; no merge required"}')
        return

    # ── 4. Attempt the merge ──
    #
    # Run `git merge origin/<base>` in the worktree. Capture exit code and
    # stdout/stderr to distinguish clean merge from conflict.
    merge_result = git merge "origin/$BASE_BRANCH"  # from within state.worktreePath

    if merge_result.exit_code == 0:
        # Clean merge — no conflicts. Commit was created by git merge.
        # Push immediately.
        git push origin HEAD  # from within state.worktreePath
        summary = f"merged origin/{BASE_BRANCH} into PR #{PR} cleanly; pushed"
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"acted","note":"' + summary + '"}')
        return

    # ── 5. Conflict detected — attempt mechanical resolution ──
    #
    # Inspect `git status --porcelain` to identify conflicting files.
    # "Mechanical" conflicts are those where:
    #   (a) both sides modified the same file but in non-overlapping regions
    #       and a standard merge driver can produce a deterministic result, OR
    #   (b) one side deleted a file and the other modified it, and the deletion
    #       aligns with the intent of this PR (no heuristic guessing here —
    #       require that the deleted file is NOT in the PR's changed-file set;
    #       if it is, treat it as semantic).
    #
    # For all other conflicts — overlapping edits to the same region, logic
    # contradictions between the PR change and the incoming base change —
    # the handler cannot reliably resolve without semantic understanding of
    # both changes. Escalate rather than produce a broken merge.
    conflicting_files = list_conflicting_files(state.worktreePath)  # git status --porcelain | grep "^UU\|^AA\|^DD"

    # Check if git's standard 3-way merge left clean markers (no remaining
    # conflict markers in files). Some merge drivers resolve automatically
    # without producing conflict markers even on overlapping hunks.
    if has_no_conflict_markers(state.worktreePath, conflicting_files):
        # All conflicts were resolved by the merge driver automatically.
        git add -A  # from within state.worktreePath
        commit_message = f"chore: merge origin/{BASE_BRANCH} into branch (no conflicts)"
        git_commit(state.worktreePath, commit_message)
        git push origin HEAD
        summary = f"merged origin/{BASE_BRANCH} into PR #{PR} (auto-resolved); pushed"
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"acted","note":"' + summary + '"}')
        return

    # Attempt to resolve mechanical (non-semantic) conflicts:
    #   - files where both sides changed non-overlapping sections
    #     (conflict markers only exist in distinct regions — resolve by
    #     accepting both sides' changes in order: ours then theirs)
    #   - files where this PR did not touch the conflicting region at all
    #     (safe to accept "theirs" for that region)
    resolved, unresolvable = attempt_mechanical_resolution(state.worktreePath, conflicting_files)

    if len(unresolvable) > 0:
        # ── 6. Semantic conflict — escalate ──
        #
        # Abort the merge so the worktree is left clean (no partial merge
        # state). `git merge --abort` restores the pre-merge state. Then
        # verify compilation/tests still pass on the unmerged branch — the
        # worktree must remain in a shippable state so human intervention
        # can pick up where we left off.
        git merge --abort  # from within state.worktreePath

        conflict_list = ", ".join(unresolvable[:5])  # cap at 5 for readability
        if len(unresolvable) > 5:
            conflict_list += f" … and {len(unresolvable) - 5} more"

        post_linear_comment(ticket_id,
            f"pr-base-advanced handler: base branch '{BASE_BRANCH}' advanced into a semantic conflict "
            f"on PR #{PR} in {REPO}. Conflicting files require manual resolution: {conflict_list}. "
            f"The merge was aborted; the PR branch is untouched. Please resolve and push.")
        print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"escalated:needs-human","note":"semantic conflict in ' + str(len(unresolvable)) + ' file(s): ' + conflict_list + '"}')
        return

    # ── 7. Push resolved merge ──
    #
    # All conflicts were resolved mechanically. Stage, commit, push.
    git add -A  # from within state.worktreePath
    commit_message = f"chore: merge origin/{BASE_BRANCH} (resolve conflicts)"
    git_commit(state.worktreePath, commit_message)
    git push origin HEAD

    summary = f"merged origin/{BASE_BRANCH} into PR #{PR}; resolved {len(resolved)} conflict(s); pushed"
    print('{"skill":"workon-event","ticketId":"' + ticket_id + '","eventType":"pr-base-advanced","eventTs":"' + event.ts + '","result":"acted","note":"' + summary + '"}')
```

### Result classification

This handler emits one of five `result` values via direct JSON — never `"stub"`:

| Result | Condition |
| --- | --- |
| `"noop:no-conflict"` | Base advanced but PR is already MERGEABLE; no merge needed |
| `"acted"` with note `"merged … cleanly"` | `git merge` succeeded without any conflict markers |
| `"acted"` with note `"merged … (auto-resolved)"` | Merge driver resolved all conflicts automatically |
| `"acted"` with note `"resolved N conflict(s)"` | Mechanical resolution succeeded; pushed |
| `"escalated:needs-human"` | Semantic conflict detected; merge aborted; Linear comment posted |
| `"error"` | Worktree is missing; exit non-zero so dispatcher retries |

### Idempotency

Re-delivery of the same `pr-base-advanced` event is safe. Step 1 re-reads live merge state; if a prior invocation already merged and pushed, the live `mergeStateStatus` will be `CLEAN` and the handler exits as `noop:no-conflict`. If the worktree was already merged but not pushed (rare crash case), `git merge` will fast-exit because the tree is already up to date, and the push will succeed normally.

### Semantic-conflict escalation guarantee

The handler never leaves the worktree in a partial-merge (conflict-marker) state. On the escalation path, `git merge --abort` is called before emitting the `"escalated:needs-human"` result, so the branch remains in its pre-merge state and a human can pick up from a clean base.

### Cross-cutting constraints (from §8)

- **One push per invocation.** Steps 4, 5, and 7 each push at most once; at most one push reaches the remote per handler call.
- **Never force-push.** The merge commit is a regular fast-forwarded push.
- **Worktree is the source of truth for edits.** All merge operations happen in `state.worktreePath`.
- **No speculative tickets.** Semantic conflicts are surfaced as a Linear comment; no new tickets are created.

---

## §5 Teardown handlers (`pr-merged` / `pr-closed`)

Ports `workon` §5 ("Teardown") to the event-driven model. Invoked by the dispatch table when `event.type == "pr-merged"` or `event.type == "pr-closed"`. The §4 merge-state pre-check ensures these handlers only run against PRs that GitHub confirms are actually in the corresponding terminal state.

**Scope: Linear + state finalization only.** No worktree removal or branch deletion — those are operator-recoverable via `git worktree prune` and `gh pr delete-branch`, and removing them automatically on an event that may arrive out-of-order would destroy working trees incorrectly. The teardown handlers set `phase="teardown"` and post the final Linear comment; nothing else.

### Inputs

- `ticket_id`: Linear ticket identifier
- `event.payload.prNumber`, `event.payload.repoSlug`: PR identity
- `event.payload.mergedAt` (pr-merged) or `event.payload.closedAt` (pr-closed): terminal timestamp from GitHub
- `state.convergenceCommentPosted`: whether the convergence comment was already posted in Watch

### At-most-once semantics

The teardown handler sets `phase="teardown"` BEFORE posting the Linear comment. This guarantees at most one comment even if the dispatcher delivers the event twice. The sequence:

1. Check `isTeardownComplete(state)` — if already in teardown phase, exit as `result:"noop:already-torn-down"`.
2. Set `state.phase = "teardown"` and persist immediately (before the Linear write).
3. Post the final Linear comment (once).
4. Set `state.finalCommentPosted = true` and persist.

### Implementation

```
teardown_merged_handler(ticket_id, event, state):
    PR   = event.payload.prNumber
    REPO = event.payload.repoSlug

    # At-most-once guard (phase=teardown is set BEFORE the Linear write).
    teardown_state = normalizeTeardownState(state.teardown)
    if isTeardownComplete(teardown_state):
        echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-merged","eventTs":"'"$event.ts"'","result":"noop:already-torn-down","note":"teardown already complete"}'
        return

    # Persist teardown phase first — at-most-once guard for the Linear comment.
    state.teardown = createTeardownMarker()
    state.phase    = "teardown"
    persist(state, STATE_FILE)

    # Post merge confirmation to Linear if not already posted.
    if shouldPostFinalComment(state.teardown):
        # Post a one-line note. Only post if convergence comment was not already sent
        # to avoid redundant messages — but convergenceCommentPosted is advisory only;
        # always post on merge so the ticket has a clear terminal marker.
        mcp__claude_ai_Linear__save_comment(
            issueId = <linear-issue-id-for-ticket_id>,
            body    = f"PR #{PR} merged into {REPO}."
        )
        state.teardown.finalCommentPosted = true
        persist(state, STATE_FILE)

    echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-merged","eventTs":"'"$event.ts"'","result":"acted","note":"teardown complete; merge comment posted to Linear"}'

teardown_closed_handler(ticket_id, event, state):
    PR   = event.payload.prNumber
    REPO = event.payload.repoSlug

    # At-most-once guard.
    teardown_state = normalizeTeardownState(state.teardown)
    if isTeardownComplete(teardown_state):
        echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-closed","eventTs":"'"$event.ts"'","result":"noop:already-torn-down","note":"teardown already complete"}'
        return

    # Persist teardown phase first.
    state.teardown = createTeardownMarker()
    state.phase    = "teardown"
    persist(state, STATE_FILE)

    # Post closed-without-merge note to Linear.
    if shouldPostFinalComment(state.teardown):
        mcp__claude_ai_Linear__save_comment(
            issueId = <linear-issue-id-for-ticket_id>,
            body    = f"PR #{PR} closed without merging ({REPO})."
        )
        state.teardown.finalCommentPosted = true
        persist(state, STATE_FILE)

    echo '{"skill":"workon-event","ticketId":"'"$ticket_id"'","eventType":"pr-closed","eventTs":"'"$event.ts"'","result":"acted","note":"teardown complete; closed-without-merge note posted to Linear"}'
```

### Result classification

| Result | Condition |
| --- | --- |
| `"acted"` | Teardown ran for the first time; Linear comment posted |
| `"noop:already-torn-down"` | `state.teardown.phase` was already `"teardown"` before this invocation |

### Linear issue ID resolution

Use `mcp__claude_ai_Linear__get_issue` with the human-readable `ticket_id` (e.g. `PROJ-123`) to look up the Linear issue UUID. The `save_comment` call requires the UUID (`issueId`), not the identifier.

---

## 5. §4.1 merge-state routing

The original `workon` skill begins every Watch tick with §4.1 — re-verify PR state, route to teardown if merged or closed. In an event-driven world the same guarantee has to live at dispatch time, because individual events can lag PR-state transitions (a Codex comment event might arrive seconds after the PR was merged).

Rule: **every dispatch that touches a PR re-reads PR state from GitHub before the handler runs**, and re-routes when the PR is no longer open.

```bash
# Inputs: REPO and PR from event.payload
gh pr view "$PR" --repo "$REPO" \
  --json state,mergeable,mergeStateStatus,mergedAt,mergedBy,mergeCommit,closedAt
```

The `--json` list is the union of the routing inputs (`state`, `mergeable`, `mergeStateStatus`) and every field consumed by the rerouted-payload synthesis in §4: `mergedAt`/`mergedBy`/`mergeCommit` (the SHA is read from `mergeCommit.oid`, and only when `mergeCommit` is non-null — see §4) for `pr-merged`, and `closedAt` for `pr-closed`. Implementations must request all of these in a single call so the same `pr_view` result satisfies both the routing decision and the destination payload contract without a second round-trip.

`gh pr view --json` does not expose a `closedBy` field, so the pre-check cannot supply closer identity to the rerouted `pr-closed` payload. `closedBy` therefore stays optional in §2's `pr-closed` row, and the synthesis step in §4 omits it. Callers that need closer identity must fetch it via a separate call — `gh api repos/<owner>/<repo>/issues/<prNumber>/events` (look for the `closed` event's `actor.login`) or the equivalent `/issues/<prNumber>/timeline` endpoint — outside of this pre-check.

### `gh pr view` failure handling

The pre-check is a network call that can fail before any routing decision is possible: GitHub auth outage, transient network error, PR not found (manually deleted or repo renamed), `gh` itself returning a non-zero exit, or JSON parse failure on the response. These failures do not correspond to any routing branch and must not be silently swallowed — silence would let the dispatcher's retry policy treat the event as handled. The dispatch loop in §4 wraps the `gh pr view` call and, on any non-zero exit or JSON parse failure, emits a single `result: "pre-check-error"` log line carrying the original event's `eventType` and `eventTs` plus a `note` identifying the failure (exit code, stderr summary, or `pr-not-found` marker), exits non-zero, and writes **no** state. State is intentionally not written — on the same idempotency footing as the stale-teardown guard — so the dispatcher can re-deliver the same event after the underlying problem clears.

Routing decisions below assume the pre-check call succeeded; a failed pre-check exits before reaching them.

Routing decisions:

- `state == "MERGED"` and `event.type != "pr-merged"` → re-dispatch as `pr-merged` (handler: `handle_pr_merged`). Skip the original handler.
- `state == "CLOSED"` (not merged) and `event.type != "pr-closed"` → re-dispatch as `pr-closed` (handler: `handle_pr_closed`). Skip the original handler. A `pr-merged` event whose PR GitHub now reports as `CLOSED` (not merged) is routed here too: GitHub is the source of truth, so a mislabeled or out-of-order `pr-merged` against a closed-not-merged PR runs the closed-without-merge teardown rather than the merged teardown.
- `state == "OPEN"` and `event.type in {"pr-merged","pr-closed"}` → **stale-teardown guard.** The event claims the PR is merged or closed but GitHub reports it is still open (delayed or reopened-after-close delivery). Skip the teardown handler entirely and emit a single `result: "stale"` line (§6); exit non-zero. State is not written, so the dispatcher can re-deliver after live state catches up. Running teardown against a live PR would clean up the worktree and archive state for an active branch, which is the opposite of what `Watch §4.1` guarantees in the polling sibling.
- Otherwise — proceed to the original handler from the dispatch table.

The pre-check is skipped for `ticket-ready`, since no PR exists yet at that point.

The pre-check uses GitHub as the source of truth, **not** the cached `prNumber` / `phase` in the state file. The state file is updated to reflect the re-routed phase only after the teardown handler returns.

**Payload invariants on re-route.** The §2 contract requires `payload.mergedAt` for `pr-merged` and `payload.closedAt` for `pr-closed`. When a `pr-comment`/`pr-push`/`pr-ci-failure`/`pr-base-advanced`/`convergence-check` event is rerouted to teardown, its original payload doesn't carry those fields. The dispatch loop (§4) synthesizes a payload that meets the destination contract using values already returned by the `gh pr view` call that triggered the re-route — `mergedAt`/`mergedBy` for `pr-merged` (always), `mergeCommitSha` (only when `pr_view.mergeCommit` is non-null; see §4), and `closedAt` for `pr-closed`. `mergeCommitSha` stays optional in §2's `pr-merged` row precisely because GitHub returns `null` for `mergeCommit` on PRs whose merge mode does not produce a stable merge-commit object — the synthesizer omits the field rather than crashing on a null dereference. `closedBy` is **not** part of the synthesized payload because `gh pr view --json` does not expose it; it remains optional on `pr-closed` (§2), and a handler that needs closer identity must fetch it via a separate API call (e.g. `gh api repos/<owner>/<repo>/issues/<prNumber>/events`). Because the §5 `--json` list explicitly requests every other field in the same call, the synthesis step never needs a second round-trip to GitHub for routing. The rerouted handler receives the synthesized event; the *original* event is what gets recorded on `state.lastHandledEvent*` for idempotency.

### Done-when criteria for §5 routing

- Invoking the skill with any PR-keyed event payload, against a PR that GitHub reports as `MERGED`, must invoke `handle_pr_merged` and not the event's nominal handler.
- Invoking the skill with any PR-keyed event payload, against a PR that GitHub reports as `MERGED` whose `mergeCommit` field is null (e.g. squash/rebase merges where `gh pr view --json mergeCommit` returns `null`), must still invoke `handle_pr_merged` with a synthesized payload that omits `mergeCommitSha`, rather than crashing on a null dereference before the handler runs.
- Invoking the skill with any PR-keyed event payload, against a PR that GitHub reports as `CLOSED` (not merged), must invoke `handle_pr_closed` and not the event's nominal handler.
- Invoking the skill with a `pr-merged` or `pr-closed` event against a PR that GitHub reports as `OPEN` must skip dispatch entirely, emit `result: "stale"`, exit non-zero, and leave the state file untouched.
- Invoking the skill with any PR-keyed event payload when `gh pr view` exits non-zero or returns unparseable output must emit `result: "pre-check-error"`, exit non-zero, and leave the state file untouched (no handler runs, no `lastHandledEvent*` write).
- Invoking the skill against a first-time ticket (no existing `~/.claude/workon-event/<TICKET-ID>.json`) and exiting via `validation-error`, `unknown`, `pre-check-error`, or `stale` must leave the directory in its original state — no skeleton state file is written. State load/create is deferred until after the §5 pre-check guards have passed (and the unknown-type short-circuit fires before state load too); see §3 and §4 "Pre-handler steps."
- Invoking the skill with `ticket-ready` never performs the PR pre-check.

## 6. Logging contract

Every handler invocation emits exactly one JSON line on stdout. A re-route in §5 is logged with one *additional* line — the `rerouted` line — emitted *before* the downstream handler line. This is the only side effect the scaffold has, and it's how tests verify dispatch.

```json
{ "skill": "workon-event", "ticketId": "PROJ-123", "eventType": "pr-comment", "eventTs": "2026-05-05T22:30:00Z", "result": "stub", "note": "..." }
```

Required fields: `skill`, `ticketId`, `eventType`, `eventTs`, `result` (`"stub"`, `"rerouted"`, `"validation-error"`, `"unknown"`, `"stale"`, or `"pre-check-error"`), `note`.

### Line-count contract per invocation

The total number of JSON lines an invocation emits is fully determined by what happened:

| Outcome | Lines emitted | In order |
| --- | --- | --- |
| Validation failure (§2) | 1 | `result: "validation-error"` |
| Unknown event type | 1 | `result: "unknown"` |
| Pre-check error (§5) | 1 | `result: "pre-check-error"` (`gh pr view` non-zero exit, network/auth outage, PR-not-found, or JSON parse failure) |
| Stale teardown (§5) | 1 | `result: "stale"` (PR `OPEN` but event is `pr-merged`/`pr-closed`) |
| Normal dispatch (no re-route) | 1 | `result: "stub"` (the handler's line) |
| Re-routed dispatch (§5) | 2 | `result: "rerouted"` first, then `result: "stub"` for the re-routed handler |

When two lines are emitted, both carry the same `ticketId` and `eventTs` so consumers can pair them. The `rerouted` line's `eventType` is the *original* event type from the dispatcher; the `stub` line's `eventType` is the type the re-route resolved to (e.g. `pr-merged` or `pr-closed`). Consumers parsing the stream must treat `result: "rerouted"` as a routing record, not a handler outcome, and must not double-count it as a handled event.

The `pre-check-error` line's `eventType` is the *original* event type — the pre-check failed before any re-route decision was possible — and its `note` carries enough detail (exit code, stderr summary, or `pr-not-found` marker) for the dispatcher to classify the failure and decide whether to retry. No state is written for `pre-check-error`, on the same footing as `stale`, so re-delivery after the underlying problem clears is safe.

## 7. Idempotency and exit semantics

- Exactly one event handled per invocation. The skill exits zero on success, non-zero on validation errors, unknown event types, pre-check errors, stale teardown rejections, **or a setup-handler scope-budget halt (§8.1)**. The first four are dispatch-layer rejections that exit before any handler runs; the scope-budget halt is the one non-zero path that exits *after* the handler ran and *after* state was written, because the event was successfully dispatched and processed — the halt is the handler's structured outcome, not a dispatch failure. Dispatcher retry/failure-class mappings should distinguish between rejections (re-deliver after the upstream condition clears) and halts (do not re-deliver until the operator splits the ticket, raises the budget, or sets an override).
- No polling, no `sleep`, no scheduled re-entry. The dispatcher owns timing. `convergence-check` is a *normal event*, not an internal timer.
- State writes are last-step-only: state is only updated after the handler returns successfully, **including for re-routed dispatches** (see §4). A crash mid-handler leaves the previous state intact, so the dispatcher can safely retry. The unknown-type short-circuit (§4), the stale-teardown guard (§5), and the pre-check-error guard (§5) do **not** write state — all three exit before `load_or_create_state` runs (state load itself is deferred until after the §5 pre-check guards have passed; see §3 and §4 "Pre-handler steps"), so a first-time-ticket invocation that exits via `unknown`, `stale`, or `pre-check-error` leaves no state file behind. `lastHandledEvent*` therefore always reflects only handlers that actually ran.
- De-duplication on `(eventType, ts)` is left to per-handler implementations. The scaffold records the latest seen pair on `state.lastHandledEvent*` but does not skip duplicates. On a re-route, the **original** event's `(type, ts)` is what's recorded — not the synthesized destination type — so duplicate-delivery detection keys off what the dispatcher actually sent.
- Ticket-ID consistency: §0 enforces `event.ticketId == $1` before state load (state load is deferred until after the §5 pre-check guards anyway; see §4). A mismatch is a `validation-error` — no state file is touched, no handler runs.
- Live-state truth: the §5 pre-check uses GitHub as the source of truth on every PR-keyed event. Teardown events whose live PR state is `OPEN` are rejected as `stale` rather than dispatched, so destructive teardown never runs against a live PR.

## 8. Cross-cutting rules (carried over from `workon`)

These rules apply uniformly to all handlers and are reproduced here so the per-handler implementations don't have to re-derive them:

- **One push per handler invocation.** When a handler does push, it batches and pushes once at the end — never per-comment or per-fix.
- **Never force-push** unless explicitly requested.
- **State file is a cache.** Re-verify PR state, worktree presence, and ticket status from the source of truth at the start of every handler.
- **No speculative tickets.** If a handler surfaces work outside the current ticket's scope, it leaves an Open Questions note on the PR or Linear comment — it does not create new tickets.
- **No internal jargon in external artifacts.** PR descriptions, Linear comments, and commit messages describe what the change contains, not the team-local label for it.
- **Use project-preferred terminology in external artifacts.** Audit drafted text for outdated or team-specific terms before posting.

### 8.1 Setup-handler scope-budget contract

`handle_ticket_ready` (the event-driven Setup path) must enforce the same scope-budget halt that the polling skill enforces between §3.4 and §3.5 (`skills/engineering/workon/SKILL.md` §3.4b). The contract is:

- Read the `## Scope budget` line from the brief on `<TICKET-ID>`. Briefs without the heading skip the check; briefs with a malformed line — missing fields, non-numeric, **zero, or negative** — emit a single warning identifying the violation and skip rather than guess. Both `loc` and `files` must be strictly positive integers per the `/groom` contract (`skills/engineering/groom/SKILL.md` §4); a zero `budget.loc` would either divide by zero in the multiplier check or turn the halt condition into a guaranteed trip on any diff, neither of which is a useful signal. The halt only fires for tickets that declared a *valid* budget.
- Measure cumulative diff against the base branch the same way `/workon` does — first `git fetch origin "$BASE_BRANCH"` so the local `origin/$BASE_BRANCH` ref reflects the current remote tip, then `git diff --shortstat "origin/$BASE_BRANCH"...HEAD` for LOC (insertions + deletions, the diff size reviewers actually scan) and `git diff --name-only "origin/$BASE_BRANCH"...HEAD | wc -l` for the file count. Both the fetch and the triple-dot range are required: a stale `origin/$BASE_BRANCH` from a long-lived clone (or after the base advanced) can mis-measure the diff against an old merge-base, and a bare `git diff --shortstat` without a range compares the working tree against the index and returns zero on a clean worktree after commits — either failure mode silently skips the halt even when the branch is far over budget.
- Halt when **either** `LOC > multiplier × budget.loc` (default `multiplier = 1.5`) **or** `LOC > budget.loc + overage_loc` (default `overage_loc = 500`). File count is reported but does not gate the halt independently.
- Thresholds are configurable via the same env vars `/workon` reads (`WORKON_SCOPE_OVERAGE_MULTIPLIER`, `WORKON_SCOPE_OVERAGE_LOC`) so a project can tune both paths uniformly. The override env var `WORKON_SCOPE_OVERAGE_OVERRIDE` (truthy: `1`, `true`, `yes`) bypasses the entire halt — both branches at once — and is the only complete way to skip the check; raising one threshold env var alone does not disable the OR-joined other branch. When the override is set, log a one-line note and continue to push + PR-open as if the budget had been met.
- Halt action is **non-interactive by construction in this skill** (the dispatcher is the caller, not a human at a terminal): post the split-proposal as a Linear comment via `mcp__claude_ai_Linear__save_comment`, leave the worktree in place with WIP commits intact, do **not** push, do **not** open the PR, and exit non-zero so the dispatcher can route the ticket to operator review. The proposal carries (a) the actual diff summary, (b) the over-budget delta, (c) candidate seams derived from the changed-file groupings (matching the named-seam contract `/groom` enforces), and (d) the same three options `/workon` surfaces (split / document the new size on the ticket / user override).
- A halt is **not** a `validation-error`, `unknown`, `stale`, or `pre-check-error` outcome — those are §6 dispatch-layer rejections. The halt happens *inside* the handler after dispatch succeeds, so the §6 line-count contract still applies (one `result: "stub"` line under the scaffold, one `result: "stub"` or production-equivalent line under a real implementation). The scope-budget halt mechanism is what the handler does internally; it does not change the dispatcher's view of the event.
- The state file is updated normally on a halt — `lastHandledEvent*` reflects that the `ticket-ready` event was processed. A subsequent re-delivery of the same event after the operator splits the ticket or applies an override is the dispatcher's call, on the same idempotency footing as any other handled event.

This rule lives here, not in a stub, because §1 forbids adding behavior to scaffold stubs. The follow-up work that ports `handle_ticket_ready` from the polling skill must implement the halt — the contract above is what reviewers check against.

## 9. Reference

Original polling implementation, useful when filling in handler bodies: `skills/engineering/workon/SKILL.md`.

Section mapping:

| `workon` section | `workon-event` event(s) | Handler |
| --- | --- | --- |
| §3 Setup | `ticket-ready` | `handle_ticket_ready` |
| §4.1 merge-state | All PR events | Pre-dispatch routing in §5 above |
| §4.2 conflicts | `pr-base-advanced` | `handle_pr_base_advanced` |
| §4.3 reviewer comments (Codex, CodeRabbit) | `pr-comment` | `handle_pr_comment` |
| §4.4 CI failures | `pr-ci-failure` | `handle_pr_ci_failure` |
| §4.5 convergence | `convergence-check` (+ `pr-push` for bookkeeping) | `handle_convergence_check` |
| §5 Teardown | `pr-merged`, `pr-closed` | `handle_pr_merged`, `handle_pr_closed` |
