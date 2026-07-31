---
name: wayfinder
description: Plan work too large or unclear for one agent session by creating a shared issue-tracker map, breaking uncertainty into decision tickets, and working one frontier ticket at a time until the path is clear. Use when the user has a large vague goal, migration, redesign, or decision tree that needs discovery before implementation.
argument-hint: "<idea-or-map-reference>"
---

# Wayfinder

A loose idea has arrived, too large for one agent session and wrapped in fog.
Wayfinding is about finding the path to the destination, not charging at the
destination. The skill charts a shared map on the repo's issue tracker, then
works decision tickets one at a time until the route is clear.

Default posture: **plan, do not implement**. Each ticket resolves a decision or
unblocks a decision. If the next step is straightforward execution, hand off to
the appropriate implementation skill.

## Core concepts

- **Destination** — the end state this map is trying to make clear: a spec, a
  decision, a migration route, or an implementation plan. Naming it is the first
  act of charting because it fixes the scope.
- **Map** — one parent issue labelled `wayfinder:map`.
- **Tickets** — child issues under the map, each sized for one fresh agent
  session. A ticket is a question, not a build slice.
- **Frontier** — open, unblocked, unclaimed child issues.
- **Fog** — in-scope uncertainty that cannot yet be phrased as a precise ticket.
- **Out of scope** — work ruled outside this destination.

Refer to maps and tickets by linked title in user-facing text, not bare issue
numbers.

## Map issue body

```markdown
## Destination

<One or two lines describing what will be clear or decided when the map is done.>

## Notes

<Domain context, skills to consult, standing preferences, tracker conventions.>

## Decisions so far

<!-- One line per closed ticket: linked title plus gist. Details live on the ticket. -->

## Not yet specified

<!-- In-scope fog that is not sharp enough to ticket yet. -->

## Out of scope

<!-- Ruled-out work, with links to closed tickets when relevant. -->
```

The map is an index, not a duplicate knowledge store. Put detailed answers on
the ticket that resolved them; keep the map as a low-resolution route summary.

## Ticket body

```markdown
## Question

<The decision or investigation this ticket resolves.>
```

Apply one type label:

- `wayfinder:research` — AFK reading of docs, APIs, repo history, or local
  resources. Resolve with a concise linked summary. Use when knowledge outside
  the current working context is required.
- `wayfinder:prototype` — HITL reaction to a cheap artifact, mock, outline,
  state machine, stub, or UI/logic prototype. Link the prototype asset from the
  ticket.
- `wayfinder:grilling` — HITL decision sharpening through direct questioning.
- `wayfinder:task` — manual or agent work required before a decision can be
  made. Use only when doing the task unblocks later decisions.

Claim a ticket by assigning it to yourself before working it. Use the tracker's
native blocking/dependency relationship when available; otherwise record
`Blocked by` links in the body.

The answer is recorded on resolution, not in the ticket body. Assets created
while resolving a ticket are linked from the issue, not pasted in.

## Invocation modes

### Chart a new map

Use this when the user provides a large vague goal.

1. Name the destination. Interview just enough to make the end state explicit.
2. Explore breadth-first. Surface the decision areas, first takeable questions,
   blockers, and fog.
3. If there is no fog and the path fits one session, stop and recommend a
   smaller planning or implementation skill instead.
4. Create the map issue with `wayfinder:map`.
5. Create only the tickets that can be phrased precisely now.
6. Wire blocking edges after ticket creation, because real issue IDs are needed.
7. Leave still-unclear areas in `Not yet specified`.
8. Stop. Do not also resolve a ticket in the charting session.

### Work through a map

Use this when the user provides a map reference. A ticket reference is optional.

1. Load the map issue, not every child ticket.
2. Pick a ticket: use the named ticket, or choose the first frontier ticket.
3. Claim it by assigning yourself before doing any work.
4. Resolve only that ticket. Load related ticket details on demand.
5. Post a resolution comment, close the ticket, and append one linked gist to
   `Decisions so far`.
6. Graduate newly sharp fog into tickets, then remove that text from
   `Not yet specified`.
7. Add or update blocking edges.
8. Move revealed non-goals into `Out of scope` and close any tickets now beyond
   the destination.
9. Stop. Never resolve more than one ticket per session.

The user may run unblocked tickets in parallel, so expect other sessions to be
editing the tracker concurrently.

## Fog handling

Create a ticket only when the question can be stated precisely, not merely when
it can be answered now. Blocked but precise questions are tickets. Vague but
in-scope areas stay in `Not yet specified`; resolving frontier tickets should
make some fog sharp enough to graduate. Do not pre-slice fog into speculative
tickets.

Out-of-scope work is not fog. It belongs in `Out of scope` and should not
graduate unless the destination changes. If a live ticket turns out to sit past
the destination, close it and leave one linked line in `Out of scope`.

## Tracker fallback

Use the repo's configured tracker when known. If no tracker is configured, use a
local markdown tracker:

- `wayfinder-map.md` for the map.
- A `wayfinder-tickets/` directory with one markdown file per ticket.
- `Blocked by` title links for dependencies.
- A `Status` field with `open`, `claimed`, or `closed`.

Prefer native issue relationships whenever the tracker supports them.
