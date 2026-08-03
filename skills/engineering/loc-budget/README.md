# /loc-budget

Portable `/loc-budget` skill for finding large line-count hitters, modularizing
them into cohesive files, and installing file-size and flat-directory budget
gates so the repo stays healthy.

The budget checker can be implemented in whatever language fits the target repo:
Python, JavaScript/TypeScript, Ruby, Go, Rust, shell, or another existing
toolchain. Popcorn's Python implementation is a reference pattern, not a
requirement.

The analysis output is standardized across languages. Tools such as Fast
TypeScript Analyzer can feed complexity signals for TypeScript/JavaScript repos,
but every run reports the same normalized file, directory, complexity,
classification, action, and reason fields.

1. Audit tracked files by LOC and direct files per directory.
2. Classify large files as refactorable, test/docs split candidates, generated,
   vendored, fixtures, lockfiles, migrations, or justified framework files.
3. Plan a focused modularization batch.
4. Extract responsibilities into destination-native modules.
5. Add or tighten file-size and flat-directory budget checks.
6. Validate with repo-local quality gates.
7. Hand off before/after LOC and remaining hitters.

## Lifecycle

```mermaid
flowchart LR
  A[Intake] --> B[Audit]
  B --> C[Plan]
  C --> D[Modularize]
  D --> E[Budget Gate]
  E --> F[Validate]
  F --> G[Commit]
  G --> H[Handoff]
```

## Install

Via the dotbrains skills CLI flow:

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/loc-budget
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/engineering/loc-budget/SKILL.md \
  -o ~/.claude/skills/loc-budget/SKILL.md
```

## Usage

```text
/loc-budget
/loc-budget ./packages/player
/loc-budget dotbrains/popcorn
```

## Requirements

- `git`
- Local build/test tools for the target repository
- `gh` when discovering the default branch from GitHub
- Permission to edit CI/pre-commit files when installing budget gates

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition consumed by the agent.
