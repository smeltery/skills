# /wrap

End-of-session wrap-up driver. Use `/wrap` to classify how the session ended, persist a `# 🔴 RESUME HERE` block before asking the user anything, write durable memory (episodes, reflections, insights), surface anti-sycophantic session highlights, and audit where the agent paused for the user (autonomy blocker buckets).

## Invocation

```sh
/wrap
```

No arguments — the skill inspects the session itself.

## What it does

Four phases run in strict order:

1. **Work Gate** — classifies the session as `COMPLETE`, `INCOMPLETE`, or `EMERGENCY`. A hard last-message parking gate forces `INCOMPLETE` when your final message signals you'll resume later ("tomorrow", "pick this up later", "blocked on you"), even if the in-session ask was satisfied.
2. **Resume Handoff** — writes a `# 🔴 RESUME HERE` block to a plan file *before* prompting the user, so persistence does not depend on a reply. When the session produced two unrelated unfinished items, writes a separate plan per item instead of bundling them.
3. **Durable Memory** — appends an episode (always for COMPLETE/INCOMPLETE) and, conditionally, a reflection plus up to three insights. Followed by anti-sycophantic Session Highlights (Phase 3.5) and an Autonomy Blocker Audit (Phase 3.6) that sorts every pause-for-user into discipline / tooling / physics buckets and routes durable fixes back into memory.
4. **Final Status** — emits a single status block with outcome, unresolved items, resume path(s), artifacts written, and any open autonomy action items.

State lives in `$WRAP_STATE_DIR` (default `$HOME/.wrap`):

```text
~/.wrap/
├── plans/             # active plan files with RESUME HERE blocks
├── episodes.jsonl     # factual session log
├── reflections.md     # corrective + learning notes (conditional)
└── insights.jsonl     # reusable rules (conditional, capped at 3 per session)
```

See `SKILL.md` for the full protocol — classification rules (including the hard parking gate), plan-selection logic (Case A vs Case B), the discrete-work-items split audit, RESUME HERE field format, conditional gates for each Phase 3 artifact, the Phase 3.5 session-highlights structure, and the Phase 3.6 autonomy-blocker audit.

## Pairs with

- [`/wrap-resume`](../wrap-resume/README.md) — picker that reads the RESUME HERE blocks `/wrap` writes.

Any other reader that honors the `# 🔴 RESUME HERE` plan-file format also works — a personal `/work` skill, a team dashboard, anything pointed at `$WRAP_PLANS_DIR`.

## Customization

All runtime behavior beyond the four core phases is opt-in:

| Env var | Purpose | Default |
| --- | --- | --- |
| `WRAP_STATE_DIR` | State root | `$HOME/.wrap` |
| `WRAP_PLANS_DIR` | Plans directory | `$WRAP_STATE_DIR/plans` |
| `WRAP_EPISODES_FILE` | Episode JSONL path | `$WRAP_STATE_DIR/episodes.jsonl` |
| `WRAP_REFLECTIONS_FILE` | Reflections markdown | `$WRAP_STATE_DIR/reflections.md` |
| `WRAP_INSIGHTS_FILE` | Insights JSONL | `$WRAP_STATE_DIR/insights.jsonl` |
| `WRAP_EXT_HOOK` | Markdown file with extra conditional writes loaded at end of Phase 3 | unset |
| `WRAP_INJECT_MEMORY` | Enable the `SessionStart` memory-injection hook | `false` |
| `WRAP_INJECT_N_REFLECTIONS` | Reflections injected per new session | 3 |
| `WRAP_INJECT_N_INSIGHTS` | Insights injected per new session | 5 |
| `WRAP_INJECT_N_EPISODES` | Episodes injected per new session | 10 |

## SessionStart memory loop (opt-in)

`scripts/inject-memory.sh` reads recent ledger entries and emits a compact `[WRAP MEMORY]` block on stdout. The bundled `hooks.json` is the reference `SessionStart` hook spec.

**Wiring is manual.** This repo does not ship an installer that merges `hooks.json` into your agent config — add the hook yourself. On Claude Code, copy the `SessionStart` entry from `hooks.json` into `~/.claude/settings.json`, replacing `${CLAUDE_SKILL_DIR}` with the skill's absolute install path (e.g. `~/.claude/skills/wrap`) unless your host agent already sets that variable.

**The loop is still opt-in.** Even once wired, the hook exits silently unless `WRAP_INJECT_MEMORY=true` is set in your shell environment. Set it in `~/.zshrc` / `~/.bashrc` when you want injection on, unset it to disable without removing the hook.

## Safety guarantees

- No semantic auto-edits — the skill never modifies behavior rules or project memory based on its own wrap artifacts.
- Persist before interact — Phase 2's handoff write always precedes any user-prompting tool call.
- Under context pressure, errs toward `EMERGENCY`, not `COMPLETE`.
- Never hallucinates missing history — writes `unknown due compaction` when origin messages aren't recoverable.

## Install

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/wrap
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/productivity/wrap/SKILL.md \
  -o ~/.claude/skills/wrap/SKILL.md
```

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
- [`hooks.json`](./hooks.json) — reference `SessionStart` hook spec for the opt-in memory loop.
- [`scripts/inject-memory.sh`](./scripts/inject-memory.sh) — reads the ledger and emits the `[WRAP MEMORY]` block (best-effort, opt-in).
- [`teaching-moment-examples.md`](./teaching-moment-examples.md) — calibration examples for Phase 3d (loaded only when needed).
