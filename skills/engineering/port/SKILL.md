---
name: port
description: Port an upstream GitHub repository into a fresh private destination repository with a new identity, clean initial history, detailed docs, CI/pre-commit/Flox setup, structure cleanup, and upstream-reference sanitization. Use when the user types `/port <source-github-url>` or asks to port one repo into a private org repo.
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
  "runnerProvider": null,
  "ciRunIds": [],
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

### 3.4 Runner choice

Ask whether to use Blacksmith or GitHub-hosted Actions runners unless the user
already chose. Record `runnerProvider` in state and confirm available labels,
platforms, and organization access before writing workflows. Both choices use
GitHub Actions; do not silently substitute providers.

### 3.5 Destination license

Copy [assets/LICENSE](assets/LICENSE) byte-for-byte to the destination `LICENSE`.
Do not substitute a similarly named standard license, change the copyright, or
mention the template's originating project in generated files or the handoff.
Preserve required upstream and third-party notices separately. If the source
license conflicts with applying this license, stop and explain the conflict;
user approval alone does not remove license obligations.

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

Do not fork. Do not preserve upstream commits. The initial push must contain
exactly one fresh commit. Subsequent CI repairs may add focused commits; never
rewrite published history merely to restore a one-commit count.

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

Keep the root README slim: project purpose, high-level capabilities, a working
quick start, technology/runtime badges, CI/release/license badges, and a link to
`docs/`. Include a subproject table only for a monorepo. Link badges to real
destination workflows, releases, and tools; omit unsupported claims.

Put detailed installation, configuration, usage, troubleshooting, architecture,
and contributor guidance in focused pages under `docs/`, with `docs/README.md`
as their index. Organize around user tasks, split large topics into linked
subdirectories, and verify examples against actual behavior. Include Mermaid
diagrams for meaningful architecture or workflow explanations.

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
  destination badges, quick start, `docs/` index, and license.
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

- Use the `loc-budget` skill when available, or implement its equivalent: file-size checker,
  flat-directory checker, budget data files, justified exceptions, and
  pre-commit/CI wiring.
- Use the destination repo's idiomatic tooling: Python, Node/Bun/Deno, Ruby, Go,
  Rust, shell, or an existing repo-native command.
- Record a LOC baseline and explicit budgets for handwritten code; prefer deleting
  duplication and unnecessary abstractions before splitting files. Track net LOC
  change and avoid satisfying budgets by minifying code or moving it to exclusions.
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

- Use the runner provider selected at Intake; validate labels for every OS and
  architecture, including release jobs. Ask about platform-specific exceptions.
- Include applicable formatting, lint, typecheck, test, build, dependency/security,
  shell, Actions syntax, docs-link, LOC/flat-directory, and lockfile checks.
- Validate Markdown and every Mermaid block in Markdown using a pinned Mermaid
  parser or renderer; Markdown lint alone does not validate diagram syntax.
- Share check commands with local hooks and run them in Flox. Use frozen/locked
  dependency installs, cache keys tied to lockfiles, job timeouts, concurrency,
  pinned actions, and least-privilege permissions. Avoid duplicate checks/jobs.

### 12.2 Pre-commit

Configure hooks that invoke the same scripts, versions, configs, and Flox
environment as CI, including Markdown, Mermaid, and budget checks. Fast checks
run at commit time; expensive full suites can run at pre-push with a documented
full local command. Publishing and credentials-dependent checks remain CI-only;
document those exceptions. A missing tool must fail clearly, not skip a gate.

Document and verify `pre-commit install`, any pre-push installation, and
`pre-commit run --all-files` from a clean checkout.

### 12.3 Flox and Bun

Make Flox the shared development and CI toolchain: commit the environment
manifest and lockfile, declare runtimes and validation/release tools, and expose
consistent build, test, lint, docs, and budget commands. Document activation,
hook setup, and running the same checks locally and in CI. Validate a clean
activation and document platform limitations rather than silently bypassing it.

Prefer Bun for compatible JavaScript/TypeScript dependency installation,
scripts, tests, and docs tooling. Check framework and lifecycle-script
compatibility before migrating; retain required Node runtimes. Pin Bun through
Flox, commit its lockfile, use frozen installs in CI, and remove obsolete
lockfiles only after validating the migration. Do not introduce a JS toolchain
solely to replace adequate native tooling.

### 12.4 Automatic releases

Implement `.github/workflows/auto-release.yml` and `release.yml` adapted to the
destination stack and artifacts:

- Trigger auto-release on successful completion of the named CI workflow for a
  push to the destination default branch, never a pull request or fork run.
- Check out and tag the successful run's exact `head_sha`, not a newer untested
  branch head. Serialize tagging; fetch tags and reuse an existing semantic
  version tag on that SHA. Start at `v0.1.0`, then increment the latest stable
  patch version unless the project has an established versioning policy.
- Explicitly dispatch `release.yml` with the tag after pushing it: do not rely
  on a tag pushed with `GITHUB_TOKEN` triggering another workflow. Grant only
  the auto-release job the required contents/actions write permissions.
- Support tag-push and manual tag-input release triggers. Validate the tag,
  build from its immutable commit, run preflight checks, package appropriate
  platform artifacts with checksums, and publish generated release notes.
- Serialize release runs by tag across both triggers. Verify expected assets
  and checksums; retries must reuse tags and complete missing release work,
  including dispatch recovery when tag creation succeeded on an earlier run.
- Adapt package names, version injection, targets, secrets, and badge URLs to
  the destination. Do not copy unrelated integrations or project references.

Document triggers, versioning, permissions, artifacts, and retry procedures in
`docs/releasing.md`; validate packaging locally without publishing.

Set `phase: "validate"`.

---

## 13. Validation

Run every applicable local gate: format, lint, type check, unit/integration
tests, build, docs build, pre-commit all files, workflow syntax validation, and
release smoke checks.

Run repository audits:

```bash
rg -n "$SOURCE_OWNER|$SOURCE_REPO|github.com/$SOURCE_OWNER/$SOURCE_REPO" .
rg -n "runs-on:" .github/workflows
find docs -type f 2>/dev/null | rg '/[A-Z][^/]*$' || true
git log --oneline
git remote -v
```

Confirm no disallowed upstream references/history remain, the destination remote
is correct, README is slim and linked to detail docs, docs filenames are
lowercase except conventional files, Mermaid diagrams are useful and valid,
badges point to the destination repo, LOC/flat-directory budgets pass, >1000 LOC
files and flat directories are improved or justified, CI uses the selected
runner provider, the license matches the bundled asset exactly, and shared
pre-commit/Flox checks and automatic releases are documented.

If a validation failure cannot be fixed, document it in the handoff and stop for
user approval before committing.

Set `phase: "commit"`.

---

## 14. Final Commit

On the first push, create exactly one fresh commit. On resume, inspect the
remote and recorded SHA first; if already pushed, continue monitoring or add
only necessary repair commits.

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

Before the initial push, verify there is exactly one commit:

```bash
test "$(git rev-list --count HEAD)" -eq 1
```

### 14.1 Monitor CI and releases

After every push, discover runs for the pushed SHA and watch them to completion
with `gh run watch <run-id> --exit-status`. Also track the downstream auto-release
and release runs for that commit/tag; a green build alone is insufficient.
Record run IDs and the final SHA in state so monitoring can resume.

Inspect failed logs, fix actionable failures, run affected checks locally, push
focused repair commits, and repeat until all required CI and release checks are
green for the final SHA. Do not disable gates to obtain green status or force-push
over published commits/tags. If credentials, unavailable runners, or an external
outage prevents progress, report the exact blocker and run URLs; leave the phase
at `commit` and do not claim completion. Resume monitoring after resolution.

Set `phase: "handoff"` only after confirming green runs and expected release
artifacts.

---

## 15. Handoff

Report the destination URL, privacy, name, final SHA, initial-history confirmation, final CI/release run URLs,
major identity/structure/refactor changes, README/docs hardening, lowercase docs
renames, Mermaid diagrams, badges, LOC/flat-directory budget setup,
CI/pre-commit/Flox setup, validation commands, and any approved legal notices or
remaining exceptions.

Keep the response concise. Do not mention the source repository in the handoff
unless required for legal or user-approved context.

## Definition of Done

- User approved the new destination name.
- Private destination repository exists.
- Initial push has one fresh commit; any CI repair commits are identified.
- No upstream Git history remains.
- No disallowed upstream references remain.
- Required legal notices are preserved or approved.
- Root and contributor docs are complete.
- Root README is slim and links to deeper docs.
- Documentation filenames are lowercase except conventional required files.
- Mermaid diagrams are added where they clarify architecture or workflow.
- README badges point to the destination repo.
- Each monorepo subproject has a useful README.
- CI uses the selected Blacksmith or GitHub-hosted runners.
- Pre-commit hooks are configured and documented.
- Flox provides the shared local/CI toolchain; Bun is used where compatible.
- The destination license matches the bundled license byte-for-byte.
- Markdown and Mermaid validation run in CI and local hooks.
- Automatic releases are retry-safe and build the CI-validated commit.
- Required CI and release runs are green for the final SHA.
- LOC and flat-directory budget gates are installed or equivalent gates exist.
- Flat directories and >1000 LOC files are addressed or justified in budgets.
- Validation passes or exceptions are explicitly approved.
