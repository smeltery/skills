---
name: port
description: Port an upstream GitHub repository into a fresh private destination repository with a new identity, clean single-commit history, detailed docs, CI/pre-commit/Flox setup, structure cleanup, and upstream-reference sanitization. Use when the user types `/port <source-github-url>` or asks to port one repo into a private org repo.
argument-hint: "<SOURCE-GITHUB-URL>"
---

# Port: private repo productization driver

Idempotent, state-branched skill for turning an upstream repository into a
fresh private repository under a user-approved new name.

Same invocation drives: Intake → Name gate → Audit → Plan → Initialize →
Sanitize → Restructure → Document → Harden → Tool → Validate → Commit →
Handoff.

**Arguments:** "$ARGUMENTS"

## 0. Parse argument

Extract `<SOURCE-GITHUB-URL>`. It must be a GitHub repository URL such as
`https://github.com/<owner>/<repo>`. If the argument is missing or malformed,
abort with a short error telling the user the expected form.

Destination owner/org is discovered from the user request or asked for during
Intake. Do not assume the destination owner unless the user stated it.

## 1. Load state

State file: `~/.local/share/port/<source-owner>-<source-repo>.json`.

```json
{
  "sourceUrl": "https://github.com/source/repo",
  "sourceSlug": "source/repo",
  "destinationOwner": "example-org",
  "destinationName": null,
  "destinationSlug": null,
  "workspacePath": "/absolute/path/to/scratch/repo",
  "baseBranch": "main",
  "phase": "intake|name|audit|plan|initialize|sanitize|restructure|document|harden|tool|validate|commit|handoff",
  "legalHold": false,
  "nameApproved": false,
  "repoCreated": false,
  "finalCommitSha": null
}
```

Create `~/.local/share/port/` if needed. If no state exists, start at Intake. If
state exists, jump to its phase, then re-check local files and GitHub before
continuing. State is a cache; GitHub and the filesystem are source of truth.

## 2. Route

```text
if no state file OR phase == "intake": run Intake (§3)
elif phase == "name": run Name Gate (§4)
elif phase == "audit": run Source Audit (§5)
elif phase == "plan": run Migration Plan (§6)
elif phase == "initialize": run Repository Initialization (§7)
elif phase == "sanitize": run Identity Sanitization (§8)
elif phase == "restructure": run Structure Cleanup (§9)
elif phase == "document": run Documentation (§10)
elif phase == "harden": run Documentation and Budget Hardening (§11)
elif phase == "tool": run Tooling (§12)
elif phase == "validate": run Validation (§13)
elif phase == "commit": run Final Commit (§14)
elif phase == "handoff": run Handoff (§15)
```

---

## 3. Intake phase

### 3.1 Verify GitHub access

Use `gh`, not unauthenticated scraping, for repository metadata:

```bash
gh repo view "$SOURCE_SLUG" \
  --json nameWithOwner,description,isPrivate,isArchived,defaultBranchRef,licenseInfo
```

Also confirm the destination owner/org can create private repositories:

```bash
gh repo view "$DESTINATION_OWNER/placeholder" >/dev/null 2>&1 || true
gh auth status
```

If source access, destination access, or `gh` auth is missing, stop and tell the
user exactly what access is needed.

### 3.2 Identify source facts

Determine the default branch, license/notice obligations, language stack,
package/build/test systems, monorepo shape, submodules/LFS/generated/vendored
assets, release artifacts, CI, pre-commit, docs, and dev environment tooling.

### 3.3 Legal gate

Read license files and notice files before sanitizing identity. If the license
requires attribution or preserving notices, set `legalHold: true`, summarize the
obligation, and stop for user approval. Do not silently remove legally required
notices.

Set `phase: "name"` when Intake is complete.

---

## 4. Name Gate

The destination repo name must be different, unique, and explicitly approved by
the user before cloning for migration, creating the destination repo, or making
commits.

### 4.1 Ask for a name

Ask the user for the new repository name. If useful, suggest several names
based on the domain, but do not choose for them.

Name requirements:

- Different from the source repository name.
- Available under the destination owner/org.
- Does not mention or strongly resemble the source owner or source repo.
- Suitable for package, docs, badge, and release identity.

### 4.2 Check availability

Use `gh`:

```bash
gh repo view "$DESTINATION_OWNER/$DESTINATION_NAME"
```

If the repo exists, ask whether to use that existing private repo only if it is
empty and the user explicitly approves. Otherwise ask for a new name.

Set `nameApproved: true` and `phase: "audit"` only after explicit user
approval.

---

## 5. Source Audit

Clone the source into a scratch location only after the name gate passes. Keep
the upstream remote local to the scratch repo and never reuse upstream history
for the final destination.

```bash
git clone "$SOURCE_URL" "$WORKSPACE_PATH"
cd "$WORKSPACE_PATH"
git fetch --all --tags
```

Audit and record: top-level map, subprojects, build/test/lint/typecheck/docs
commands, CI runners, pre-commit, Flox/Nix/devcontainer/asdf/mise files,
README coverage, contributor docs, files over 1000 LOC, flat directories, and
source identity references. Categorize large files as implementation, generated,
vendored, fixture, data, lockfile, or docs.

Use explicit searches:

```bash
rg -n "$SOURCE_OWNER|$SOURCE_REPO|github.com/$SOURCE_OWNER/$SOURCE_REPO" .
find . -type f | while read -r file; do wc -l "$file"; done | sort -nr | head
```

Set `phase: "plan"` when the audit is complete.

---

## 6. Migration Plan

Write a concise but concrete migration plan before making destructive or
large-scale changes.

The plan must cover new repo/package/binary/module/docs/release identity,
directories to reorganize, >1000 LOC files to split or justify, docs to add or
rewrite, CI/pre-commit/Flox changes, validation commands, final search terms,
and legal notices that must remain.

If the plan includes public API breaks, package renames that affect consumers,
or a large risky refactor, stop for user approval. Otherwise continue.

Set `phase: "initialize"`.

---

## 7. Repository Initialization

### 7.1 Create destination repo

Create a private destination repository with `gh`:

```bash
gh repo create "$DESTINATION_OWNER/$DESTINATION_NAME" --private
```

If the repo already exists, verify it is private, empty, and explicitly approved
by the user before using it.

### 7.2 Reset history

Remove upstream Git history and initialize fresh:

```bash
rm -rf .git
git init
git branch -M "$DESTINATION_DEFAULT_BRANCH"
git remote add origin "git@github.com:$DESTINATION_OWNER/$DESTINATION_NAME.git"
```

Do not fork. Do not preserve upstream commits. The final repository must have
exactly one fresh commit after completion.

Set `phase: "sanitize"`.

---

## 8. Identity Sanitization

Remove or replace source identity everywhere legally allowed.

Search and update README/docs, comments, package metadata, import/module paths,
CLI names/help, env vars/config namespaces, CI names/badges, Docker images,
release artifacts, snapshots/examples, generated docs, Git remotes, and package
registry metadata.

No final commit message, docs page, code file, badge, package manifest, or
config file may mention the upstream repo unless legally required and approved.

Validation search:

```bash
rg -n "$SOURCE_OWNER|$SOURCE_REPO|github.com/$SOURCE_OWNER/$SOURCE_REPO" .
git remote -v
```

Set `phase: "restructure"`.

---

## 9. Structure Cleanup

### 9.1 Flat directories

For each flat directory found in the audit:

1. Decide whether flatness is idiomatic for the language/framework.
2. If it mixes responsibilities, group files into cohesive subdirectories.
3. Update imports, package configs, tests, docs, and scripts.
4. Preserve public APIs unless the user approved a breaking change.

Avoid cosmetic churn. Reorganize only when navigation or maintainability
improves.

### 9.2 Files over 1000 LOC

For each file over 1000 LOC:

1. Skip generated, vendored, fixture, data, lock, or checked-in build artifact
   files unless there is a specific reason to change them.
2. Split implementation files by responsibility, not arbitrary line count.
3. Keep exported behavior stable.
4. Add or update tests for risky seams.
5. Document any intentionally remaining >1000 LOC files.

Set `phase: "document"`.

---

## 10. Documentation

Create detailed user-facing and contributor-facing docs.

### 10.1 Root README

Use the destination identity and include the project name, description, badges,
status, quick start, installation, usage examples, subproject table, common
tasks, docs links, and license.

The shape should be comparable to a mature monorepo README: badge block, clear
quick start, subproject table, and concrete commands.

### 10.2 Subproject READMEs

Every app/package/crate/subproject in a monorepo gets a README with name,
purpose, useful badges, install/build, usage, development/testing, relationship
to the broader repo, and a root docs link.

### 10.3 Contributor docs

Add or improve `CONTRIBUTING.md` or `docs/development.md`,
`docs/architecture.md`, `docs/testing.md`, `docs/ci.md`, `docs/releasing.md`
when releases exist, and `AGENTS.md` when agent guidance is useful.

Use Mermaid diagrams where they clarify architecture, development workflow, CI,
state machines, or release flow. Do not add diagrams where prose is clearer.

Set `phase: "harden"`.

---

## 11. Documentation and Budget Hardening

Make the migrated repo crisp and enforceable before generic tooling work.

### 11.1 README and docs

- Slim the root README into a scannable entry point: concise description,
  destination badges, status, quick start, install/usage, monorepo table, common
  commands, docs links, and license.
- Move long architecture, API, operations, release, configuration, and
  contribution detail into focused docs or subproject READMEs.
- Normalize docs filenames to lowercase kebab-case with `git mv`, then update
  links, docs nav, package metadata, tests, and examples. Conventional required
  files may stay uppercase: `README.md`, `LICENSE`, `CHANGELOG.md`,
  `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `AGENTS.md`, and
  framework-required files.
- Add Mermaid diagrams only where they clarify architecture boundaries,
  request/data flow, development workflow, CI/release flow, or state machines.
- Add destination-repo badges for CI, release/version, runtimes, Flox, and
  license where useful. Remove stale upstream badges.

### 11.2 LOC budgets and deflatting

- Install or adapt the `loc-budget` pattern: file-size checker,
  flat-directory checker, budget data files, justified exceptions, and
  pre-commit/CI wiring.
- Use the destination repo's idiomatic tooling: Python, Node/Bun/Deno, Ruby, Go,
  Rust, shell, or an existing repo-native command.
- Modularize the worst large-file hitters and reorganize mixed-responsibility
  flat directories before adding exceptions.
- Keep framework-conventional flat directories only when justified in the
  flat-directory budget file.
- Budget checks must pass before the final commit; temporary exceptions must be
  explicit and documented in the handoff.

Set `phase: "tool"`.

---

## 12. Tooling, Flox, CI, and Hooks

### 12.1 CI

Configure CI for the destination repo.

Requirements:

- Use Blacksmith runners instead of GitHub-hosted Ubuntu runners.
- Do not leave `ubuntu-latest` or `ubuntu-*` runners unless the user explicitly
  approves an exception.
- Include applicable jobs for formatting, linting, type checking, tests, builds,
  docs, release smoke checks, and lockfile validation.
- Use concurrency and least-privilege permissions.

Preferred runner examples:

```yaml
runs-on: blacksmith-4vcpu-ubuntu-2404
```

or for small jobs:

```yaml
runs-on: blacksmith-2vcpu-ubuntu-2404
```

### 12.2 Pre-commit

Configure stack-appropriate hooks. Prefer local hooks for repo-specific checks
and include checks for shell scripts, GitHub Actions, markdown/docs, file size
budgets, flat directory budgets, formatting, linting, and tests where useful.

Document:

```bash
pre-commit install
pre-commit run --all-files
```

### 12.3 Flox

Use Flox where practical for toolchain reproducibility:

- Add `.flox/env/manifest.toml` when the project has enough tooling to benefit.
- Pin major runtimes and CLIs where possible.
- Add activation instructions to README/docs.
- Use Flox in CI for common hygiene gates when practical.

Set `phase: "validate"`.

---

## 13. Validation

Run every applicable local gate: format, lint, type check, unit/integration
tests, build, docs build, pre-commit all files, workflow syntax validation, and
release smoke checks.

Run repository audits:

```bash
rg -n "$SOURCE_OWNER|$SOURCE_REPO|github.com/$SOURCE_OWNER/$SOURCE_REPO" .
rg -n "ubuntu-latest|runs-on: ubuntu-" .github/workflows || true
find docs -type f 2>/dev/null | rg '/[A-Z][^/]*$' || true
git log --oneline
git remote -v
```

Confirm no disallowed upstream references/history remain, the destination remote
is correct, README is slim and linked to detail docs, docs filenames are
lowercase except conventional files, Mermaid diagrams are useful and valid,
badges point to the destination repo, LOC/flat-directory budgets pass, >1000 LOC
files and flat directories are improved or justified, CI uses Blacksmith
runners, and pre-commit/Flox are documented.

If a validation failure cannot be fixed, document it in the handoff and stop for
user approval before committing.

Set `phase: "commit"`.

---

## 14. Final Commit

Create exactly one fresh commit.

Requirements: conventional commit format, human-written message, no upstream
mention, no AI attribution, no `Co-Authored-By`, and no generated-by footer.

Recommended message:

```text
feat: initialize private project
```

Then push:

```bash
git add -A
git commit -m "feat: initialize private project"
git log --oneline
git push -u origin HEAD
```

Verify there is exactly one commit:

```bash
test "$(git rev-list --count HEAD)" -eq 1
```

Set `phase: "handoff"`.

---

## 15. Handoff

Report the destination URL, privacy, name, final SHA, one-commit confirmation,
major identity/structure/refactor changes, README/docs hardening, lowercase docs
renames, Mermaid diagrams, badges, LOC/flat-directory budget setup,
CI/pre-commit/Flox setup, validation commands, and any approved legal notices or
remaining exceptions.

Keep the response concise. Do not mention the source repository in the handoff
unless required for legal or user-approved context.

## Definition of Done

- User approved the new destination name.
- Private destination repository exists.
- Repository has exactly one fresh commit.
- No upstream Git history remains.
- No disallowed upstream references remain.
- Required legal notices are preserved or approved.
- Root and contributor docs are complete.
- Root README is slim and links to deeper docs.
- Documentation filenames are lowercase except conventional required files.
- Mermaid diagrams are added where they clarify architecture or workflow.
- README badges point to the destination repo.
- Each monorepo subproject has a useful README.
- CI uses Blacksmith runners.
- Pre-commit hooks are configured and documented.
- Flox is used where practical.
- LOC and flat-directory budget gates are installed or equivalent gates exist.
- Flat directories and >1000 LOC files are addressed or justified in budgets.
- Validation passes or exceptions are explicitly approved.
