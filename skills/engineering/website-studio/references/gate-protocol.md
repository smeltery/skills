# Gate protocol

The controller prevents skipped gates and stale receipts. It cannot decide
whether a design is attractive, a screenshot was actually inspected, or a test
log is truthful. The agent must perform the checks; file hashes are evidence
integrity, not a quality score or security boundary.

## Record a gate

Use one writer per project. Keep all receipts and temporary evidence inside
`.website-studio/`; store each gate's report separately so later notes do not
invalidate earlier evidence. Paths in reports are relative to the project root.

After actually completing a gate, write a JSON report with its exact check IDs
from the gate table in `SKILL.md`. Example shape for `context`:

```json
{
  "gate": "context",
  "checks": {
    "brief": {
      "result": "pass",
      "note": "The brief identifies the audience, offer, primary action, and assumptions.",
      "evidence": [".website-studio/brief.md"]
    },
    "baseline": {
      "result": "pass",
      "note": "The inventory records the existing routes, stack, commands, and worktree changes.",
      "evidence": [".website-studio/baseline.md"]
    },
    "scope": {
      "result": "pass",
      "note": "The requested deliverable is a locally verified production build.",
      "evidence": [".website-studio/brief.md"]
    }
  },
  "issues": []
}
```

This is a format example, not evidence to copy and pass. Evidence must describe
the actual project. Failed checks may be recorded with `result: "fail"` and
issues for recovery, but cannot advance. Every check group is required. Explain
why individual conditional features are absent within the group's evidence;
do not mark an entire core gate not applicable.

For browser evidence, record URL, actual viewport, state, actions, expected and
observed results, test data mode, and screenshot/trace paths. For commands,
record command, working directory, exit code, and useful output. Visual checks
must contain observations made after inspecting captures, not just filenames.

Advance only after resolving required issues:

```bash
python3 <skill-dir>/scripts/gates.py pass --root <project-root> \
  --report .website-studio/context.json
python3 <skill-dir>/scripts/gates.py status --root <project-root>
```

`pass` rejects wrong-order gates, missing checks, failures, unresolved issues,
empty/missing evidence, and evidence outside the project. It hashes the report
and evidence. Repeating an unchanged valid receipt is a no-op. `status` returns
the earliest missing or stale gate; stale state exits nonzero. A pending gate
is normal progress, not an error. Only `next: null` means all gates passed.

## Input changes and recovery

From `build` onward, receipts also capture a fingerprint of project files,
including untracked source and assets. New, deleted, or edited inputs invalidate
runtime evidence. The controller excludes generated/dependency directories
listed in `SKIP_DIRS`, `.website-studio/`, environment files, keys, and logs.
Inspect these exclusions against the actual project: do not keep authored source
in excluded output directories. External symlink contents and runtime secrets
are not fingerprinted; changes to them require explicit invalidation. Monorepo
users should select a root that includes shared implementation/config inputs.

Source changes generally return to `build`. Earlier changes to scope, content,
reference interpretation, or design decisions must return to their owning gate:

```bash
python3 <skill-dir>/scripts/gates.py invalidate --root <project-root> \
  --gate direction --reason "The revised brand changes tokens and page hierarchy"
```

This removes that receipt and all successors, preserving evidence files for
comparison. Rebuild and retest before recording replacement receipts. Do not
hand-edit stored hashes, delete state to hide failures, or regenerate reports
without performing their checks.

Initialization is idempotent and never overwrites existing state. State updates
use atomic replacement. Malformed state fails explicitly; inspect and restore
from actual artifacts rather than assuming completion. The target path is bound
to the state; after a deliberate project move, review and update that binding,
then revalidate evidence. Never treat a partially completed scaffold as permission
to replace existing files or rerun destructive setup.

Keep the issue list and next action persisted when interrupted. When an external
dependency blocks a gate, record the error and complete independent work without
advancing the blocked gate. Report exactly which evidence could not be obtained.
