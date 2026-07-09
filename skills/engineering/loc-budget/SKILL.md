---
name: loc-budget
description: Find large line-count hitters in a repository, modularize them into smaller cohesive files, and add or tighten file-size and flat-directory budget CI gates. Use when the user asks to reduce LOC, split large files, modularize oversized modules, or install LOC/file-count budgets.
argument-hint: "[path-or-repo]"
---

# LOC Budget: large-file modularization driver

Stateful skill for reducing oversized files and preventing regression with
line-count and flat-directory budgets.

The goal is not arbitrary splitting. Reduce files by extracting real
responsibilities into cohesive modules, preserving behavior, and installing a
budget gate so the repo does not drift back.

**Arguments:** "$ARGUMENTS"

## 0. Parse argument

Input is optional:

- A repo path: work there.
- A GitHub repo URL or slug: clone or open that repo if needed.
- Empty: use the current repository.

If the target repo cannot be discovered, abort with a short error.

## 1. Load state

State file: `~/.claude/loc-budget/<repo-owner-or-dir>-<repo-name>.json`.

```json
{
  "repoPath": "/absolute/path/to/repo",
  "baseBranch": "main",
  "phase": "intake|audit|plan|modularize|budget|validate|commit|handoff",
  "budgetInstalled": false,
  "largeFiles": [],
  "completedFiles": [],
  "deferredFiles": [],
  "lastCommitSha": null
}
```

Create `~/.claude/loc-budget/` if needed. If state exists, re-check the repo
before resuming. State is a cache; the filesystem and Git are source of truth.

## 2. Route

```text
if no state file OR phase == "intake": run Intake (§3)
elif phase == "audit": run Audit (§4)
elif phase == "plan": run Plan (§5)
elif phase == "modularize": run Modularize (§6)
elif phase == "budget": run Budget Gate (§7)
elif phase == "validate": run Validate (§8)
elif phase == "commit": run Commit (§9)
elif phase == "handoff": run Handoff (§10)
```

---

## 3. Intake

Work in a clean repository:

```bash
git status --short
git rev-parse --show-toplevel
git branch --show-current
```

If the worktree is dirty, inspect the changes. Do not overwrite unrelated user
work. Stop if the dirty state makes modularization unsafe.

Read repo guidance before editing: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
docs, architecture notes, lint/test configs, package manifests, and nearest
subdirectory instructions.

Discover the default branch when GitHub metadata is available:

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

Set `phase: "audit"`.

---

## 4. Audit

Measure line-count hitters and flat directories using tracked files, excluding
generated, vendored, dependency, build, fixture, and asset directories.

Preferred file audit:

```bash
git ls-files |
  rg -v '(^|/)(node_modules|target|dist|build|deps|_build|site|fixtures|vendor|\\.git)(/|$)' |
  while read -r file; do
    test -f "$file" && printf "%s\t%s\n" "$(wc -l < "$file")" "$file"
  done |
  sort -nr |
  head -50
```

Preferred flat-directory audit:

```bash
git ls-files |
  rg -v '(^|/)(node_modules|target|dist|build|deps|_build|site|fixtures|vendor|\\.git)(/|$)' |
  xargs -n1 dirname |
  sort |
  uniq -c |
  sort -nr |
  head -50
```

Classify each large file:

- Refactorable implementation file.
- Test file that should be split by scenario.
- Documentation file that should be split by topic.
- Generated, vendored, fixture, lock, migration, asset, or snapshot file.
- Framework convention file that may need an exception.

Record baseline totals: largest files, budget failures, flat directories, test
commands, and current CI/pre-commit budget gates if any.

Set `phase: "plan"`.

---

## 5. Plan

Pick a focused batch. Prefer one file or one tightly related cluster at a time.

For each selected hitter, write:

- Current LOC and target budget.
- Why the file is large.
- Proposed module boundaries by responsibility.
- Public API or import path compatibility plan.
- Tests that prove behavior did not change.
- Docs or examples that need path updates.
- Whether the budget gate should enforce the target immediately or allow a
  temporary exception while deeper work remains.

Stop for user approval when the batch changes public APIs, file formats,
storage, security-sensitive code, release behavior, or more than one unrelated
area.

Set `phase: "modularize"`.

---

## 6. Modularize

Refactor by responsibility, not by line count alone.

Rules:

- Preserve behavior first; reduce LOC second.
- Keep public exports stable unless the plan approved a breaking change.
- Extract cohesive modules with names that match domain language.
- Move tests with the code when local test placement is conventional.
- Split giant test files by scenario or surface area.
- Split docs by topic and preserve navigation.
- Avoid splitting generated, vendored, fixture, lock, migration, and asset files.
- Do not create a shallow pile of tiny files just to satisfy a number.

After each extraction, search for stale imports, paths, and symbols:

```bash
rg -n "old_module_name|old_path|old_symbol" .
```

Update imports, package manifests, docs, examples, snapshots, and build scripts.

Set `phase: "budget"` when the selected batch is complete.

---

## 7. Budget Gate

Install or tighten Popcorn-style budget gates when the repo does not already
have equivalent checks.

Popcorn implements these gates in Python. Use Python only when it fits the
target repo. In JavaScript/TypeScript repos, a Node/Bun/Deno script may be
better; in Ruby repos use Ruby; in Go or Rust repos a small checked-in tool may
fit; in simple repos shell may be enough. The contract matters more than the
language.

### File-size budget

Pattern:

- A tracked checker such as `scripts/check_file_sizes.py`,
  `scripts/check-file-sizes.mjs`, `scripts/check_file_sizes.rb`,
  `tools/check-file-sizes.go`, or an equivalent repo-native command.
- A data file such as `scripts/file-size-budgets.json`.
- Default budget such as `1000` lines.
- Per-file exceptions with explicit budgets for justified cases.

The checker should:

- Read tracked files through `git ls-files` or the repo's VCS equivalent.
- Check only source/docs/scripts/workflow suffixes relevant to the repo.
- Exclude dependency, build, generated, fixture, and asset paths.
- Fail with `path: actual lines > budget N`.
- Accept a custom budget-file argument where practical.

Budget JSON shape:

```json
{
  "default_lines": 1000,
  "files": {
    "path/to/justified-large-file.ext": 1500
  }
}
```

### Flat-directory budget

Pattern:

- A tracked checker such as `scripts/check_flat_directories.py`,
  `scripts/check-flat-directories.mjs`, `tools/check-flat-directories.go`, or
  an equivalent repo-native command.
- A data file such as `scripts/flat-directory-budgets.json`.
- Default direct-file count such as `25`.
- Per-directory exceptions with optional reasons.

Budget JSON shape:

```json
{
  "default_files": 25,
  "directories": {
    "path/to/framework-owned-dir": {
      "limit": 50,
      "reason": "Framework convention keeps these files together."
    }
  }
}
```

### CI and pre-commit wiring

Wire the checks into the repo's normal hygiene path. Examples:

```yaml
- id: file-sizes
  name: file size budgets
  entry: python3 scripts/check_file_sizes.py
  language: system
  pass_filenames: false
```

For non-Python repos, swap the entry for the repo-native command:

```yaml
entry: node scripts/check-file-sizes.mjs
```

```yaml
entry: cargo run -p check-file-sizes --quiet
```

In CI, run the hygiene target on the repo's standard runner. If the repo uses
Blacksmith, keep using Blacksmith runners.

Budget philosophy:

- Default budgets should be ambitious but not instantly impossible.
- Exceptions are allowed only when justified.
- Ratchet down budgets after modularization; do not ratchet up to hide drift.
- Generated or framework-owned files should be excluded or explicitly justified.

Set `phase: "validate"`.

---

## 8. Validate

Run:

- File-size budget check.
- Flat-directory budget check.
- Formatting.
- Linting.
- Type checking.
- Unit/integration tests touched by the refactor.
- Full test/build suite when shared modules changed.
- Docs build when docs or navigation changed.
- Pre-commit all files when configured.

Also rerun the audit commands and compare before/after LOC for each selected
file. If a selected file remains over budget, document why or return to
`modularize`.

Set `phase: "commit"` when checks pass.

---

## 9. Commit

Commit only the modularization and budget-gate changes.

Before committing:

```bash
git status --short
git diff --stat
```

Commit message examples:

```text
refactor: modularize large parser files
```

```text
ci: add file size budget gates
```

Use one commit when the budget gate and modularization are one coherent slice;
split commits if the repo convention prefers code and CI separately.

Set `phase: "handoff"`.

---

## 10. Handoff

Report:

- Largest files before and after.
- Files modularized and new module boundaries.
- Budgets installed or tightened.
- Checker language/tooling chosen and why.
- Exceptions and why they remain.
- Validation commands run.
- Commit SHA, if committed.
- Next largest hitters still worth addressing.

## Definition of Done

- Large tracked files were audited and classified.
- Refactorable hitters in the selected batch were modularized.
- Behavior was preserved with tests or documented verification.
- File-size and flat-directory budget gates exist or equivalent gates are
  already present.
- Budget checkers use the target repo's idiomatic scripting/toolchain.
- Budget exceptions are explicit and justified.
- Validation passes.
- Remaining large files are documented as next work or justified exceptions.
