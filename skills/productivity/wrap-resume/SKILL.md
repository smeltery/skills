---
name: wrap-resume
description: "Reads resume-state from plan files written by /wrap and presents a picker for continuing prior sessions. Shows each plan's RESUME HERE block with its immediate next action. Triggers on /wrap-resume, 'pick up where we left off', 'continue', 'what's open'. Renamed from /resume to free up that slash command for the Claude Code built-in session-switcher (which takes a UUID arg)."
version: 1.1.0
user-invocable: true
category: development
---

# /wrap-resume — Pick Up Prior Sessions

Thin companion to `/wrap` (name mirrors the wrap/wrap-resume pair). Reads plan files with `# 🔴 RESUME HERE` markers from the wrap plans directory and presents a picker so the user can continue unfinished work.

> **History:** This skill was previously `/resume`. Renamed because `/resume <uuid>` is a Claude Code built-in for switching conversation branches by session ID — the user-skill shadowed it. Renaming to `/wrap-resume` restores the built-in and makes the wrap↔wrap-resume relationship explicit.

Plans dir resolution (shell):

```sh
STATE_DIR="${WRAP_STATE_DIR:-$HOME/.wrap}"
PLANS_DIR="${WRAP_PLANS_DIR:-$STATE_DIR/plans}"
```

`$HOME` is used instead of `~` inside the parameter defaults because `~` does not reliably expand inside `${VAR:-~/...}` — it expands only at the start of an unquoted word.

This skill is ONE reader of `/wrap`'s output contract. If you have a personal or team task picker that consumes the same `# 🔴 RESUME HERE` format, you can use it in place of `/wrap-resume` — both honor the same plan files.

---

## Steps

1. **Locate plan files.** Resolve `PLANS_DIR` as above, then `ls -t "$PLANS_DIR"/*.md 2>/dev/null` — sorted most-recent first.

2. **Filter to resumable.** For each file path (call the variable `$file`):

   ```sh
   grep -l -- '# 🔴 RESUME HERE' "$file"
   ```

   Keep only files where grep found the marker.

3. **Extract the picker fields.** From each resumable plan, pull the RESUME HERE block from the `# 🔴 RESUME HERE` heading down to the **next top-level markdown heading** (regex `^#\s`) OR **EOF**, whichever comes first. Do NOT stop at blank lines — the canonical RESUME HERE block has no blank lines, but any agent-written block may contain them and stopping on blank lines will truncate the block and miss fields. Parse:
   - `Status:` line
   - `Mode:` line (NORMAL or EMERGENCY; field introduced in wrap v1.0.0)
   - `Current task:` line
   - `Immediate next action:` line
   - Last-modified timestamp of the file

4. **Show the picker.**

    ```markdown
    # What should we pick up?

    | # | Last wrap | Current task | Next action |
    | --- | --- | --- | --- |
    | 1 | 2h ago    | one-sentence task | copy from plan |
    | 2 | yesterday | ... | ... |
    ```

    If `Mode: EMERGENCY` is set on a plan, flag the row (e.g., prefix the row with a `⚠` marker) so the user knows context was limited when that wrap was written. For older plans that predate the `Mode:` field (wrap <1.0.0), fall back to checking for `EMERGENCY` in the RESUME HERE heading itself. Plan filename is available on selection — omitted from the picker to save width.

5. **On selection** (user says a number):
   - Read the full plan file
   - Lead with "Last time: [Current task]. Next step: [Immediate next action]."
   - If the plan has a `Session thread:` block, surface `Original intent` and `Pending detours`
   - Propose the specific next step as an actionable question: "Ready to [immediate next action]?"

6. **If no resumable plans:** say so — `No RESUME HERE blocks found in the plans directory. Nothing to resume.` Do not invent items.

---

## When to stop and ask

- If the chosen plan's `Context source: unknown due compaction`, warn the user that the prior session couldn't capture full origin context. Offer to start fresh or proceed with partial context.
- If multiple plans share the same timestamp window and describe the same task, ask which one the user means rather than guessing.

---

## Error handling

- **Missing plans dir:** `${WRAP_PLANS_DIR}` / default not created yet → tell the user `/wrap` hasn't been run yet in this setup.
- **Unreadable plan:** skip the file, log the error, continue with the rest. One corrupt plan doesn't kill the picker.

---

## Relationship to /wrap

`/wrap` writes the `RESUME HERE` block. `/wrap-resume` reads it. The two skills share the state-dir convention (`WRAP_STATE_DIR`) and the block format. If you fork one, fork the other, or keep the contract intact.
