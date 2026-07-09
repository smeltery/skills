---
name: feature-gap
description: Compare an upstream/source GitHub repository against a destination repository, identify real missing feature gaps, implement them cleanly in the destination repo, then commit and push to the destination main branch. Use when the user types `/feature-gap <source-github-url> <destination-repo>` or asks to port missing features from one repo into another.
argument-hint: "<SOURCE-GITHUB-URL> <DESTINATION-REPO>"
---

# Feature-gap: source-to-destination feature parity driver

Stateful skill for finding real feature gaps between a source repository and a
destination repository, then landing clean, tested changes directly on the
destination repo's default branch when the user asked for that workflow.

This is not a bulk copy workflow. Prefer small, idiomatic destination-native
changes that preserve the destination repo's identity, architecture, tests,
docs, and release conventions.

**Arguments:** "$ARGUMENTS"

## 0. Parse arguments

Inputs:

- `<SOURCE-GITHUB-URL>`: GitHub URL like `https://github.com/<owner>/<repo>`.
- `<DESTINATION-REPO>`: destination slug like `<owner>/<repo>`, or omitted if
  the current directory is already the destination repository.

If source is missing or malformed, abort. If destination is omitted and the
current directory is not a GitHub repo discoverable by `gh repo view`, abort and
ask for the destination repo.

## 1. Load state

State file: `~/.claude/feature-gap/<source-owner>-<source-repo>__<dest-owner>-<dest-repo>.json`.

```json
{
  "sourceUrl": "https://github.com/source/repo",
  "sourceSlug": "source/repo",
  "destinationSlug": "owner/repo",
  "destinationPath": "/absolute/path/to/destination",
  "sourcePath": "/absolute/path/to/source-scratch",
  "baseBranch": "main",
  "phase": "intake|audit|compare|plan|implement|validate|commit|handoff",
  "approvedPlan": false,
  "lastCommitSha": null
}
```

Create `~/.claude/feature-gap/` if needed. If state exists, re-check GitHub and
the filesystem before resuming. State is a cache; GitHub and local files are the
source of truth.

## 2. Route

```text
if no state file OR phase == "intake": run Intake (§3)
elif phase == "audit": run Audit (§4)
elif phase == "compare": run Compare (§5)
elif phase == "plan": run Plan (§6)
elif phase == "implement": run Implement (§7)
elif phase == "validate": run Validate (§8)
elif phase == "commit": run Commit and Push (§9)
elif phase == "handoff": run Handoff (§10)
```

---

## 3. Intake

Use `gh`, not unauthenticated scraping:

```bash
gh repo view "$SOURCE_SLUG" --json nameWithOwner,description,isPrivate,defaultBranchRef,licenseInfo
gh repo view "$DESTINATION_SLUG" --json nameWithOwner,description,isPrivate,defaultBranchRef
```

Confirm:

- Source and destination access are available.
- Destination default branch is known.
- User explicitly asked to commit and push to destination main/default branch.
- Destination worktree is clean before editing.
- Source license allows inspection and implementation. If attribution,
  licensing, or copying obligations are unclear, stop and ask.

Do not copy source code verbatim unless licensing and user intent clearly allow
it. Prefer reimplementation guided by behavior, tests, APIs, and docs.

Set `phase: "audit"`.

---

## 4. Audit

Clone the source into a scratch path if it is not already available:

```bash
git clone "$SOURCE_URL" "$SOURCE_PATH"
```

Inspect both repositories:

- Product surface: CLIs, commands, APIs, UI routes, configuration, file formats,
  protocols, integrations, and documented workflows.
- Tests: unit, integration, e2e, fixtures, snapshots, golden files.
- Docs: README, subproject READMEs, guides, changelogs, release notes.
- Architecture: packages/apps/crates/modules and responsibility boundaries.
- Tooling: build, test, lint, typecheck, docs, pre-commit, CI, Flox/dev env.

In the destination, read `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, docs, and
the nearest local instructions before editing.

Set `phase: "compare"`.

---

## 5. Compare

Build a feature-gap matrix. A real feature gap must satisfy all three:

1. It exists in the source repo as working behavior, documented behavior, tests,
   examples, or release notes.
2. It is missing, incomplete, or materially weaker in the destination repo.
3. It fits the destination repo's product identity and architecture.

Reject:

- Branding/name differences.
- Upstream-only infrastructure or release mechanics that do not apply.
- Dead code, deprecated behavior, or unsupported experiments.
- Features already implemented differently but equivalently in the destination.
- Changes that would reintroduce upstream identity into the destination.

For each candidate gap, record evidence from both repos, user value, affected
surface area, implementation risk, tests needed, and docs impact.

Set `phase: "plan"`.

---

## 6. Plan

Pick the smallest coherent set of gaps to implement now. Prefer one vertical
slice over a broad parity sweep.

Stop for user approval when:

- More than one unrelated feature gap is found.
- A gap changes public APIs, file formats, CLI behavior, persistence, security,
  licensing, or release behavior.
- The implementation is likely to exceed a focused commit.
- The destination repo has no clear architectural place for the feature.

The plan must include:

- Selected gap(s) and rejected candidates.
- Destination-native design.
- Files/modules expected to change.
- Tests to add/update.
- Docs to add/update.
- Validation commands.
- Any license or attribution constraints.

Set `approvedPlan: true` and `phase: "implement"` after approval or when the
plan is narrow and low risk.

---

## 7. Implement

Work in the destination repo only.

Rules:

- Keep destination naming, package identity, docs, and conventions.
- Reuse existing abstractions before adding new ones.
- Preserve public APIs unless the plan approved a change.
- Add focused tests that prove the gap is closed.
- Update user/contributor docs when behavior changes.
- Do not paste source code, comments, examples, snapshots, or docs verbatim
  unless licensing and user approval allow it.
- Do not mention the source repo in commit messages or destination docs unless
  legally required and approved.

If a new gap or risk appears, return to Plan instead of expanding scope silently.

Set `phase: "validate"`.

---

## 8. Validate

Run destination-local checks:

- Format.
- Lint.
- Type check.
- Unit/integration/e2e tests relevant to the feature.
- Full test/build suite when the blast radius is broad.
- Docs build or link checks when docs changed.
- Pre-commit hooks when configured.

Run a destination reference search if source identity was touched:

```bash
rg -n "$SOURCE_OWNER|$SOURCE_REPO|github.com/$SOURCE_OWNER/$SOURCE_REPO" .
```

Confirm the feature gap is closed by pointing to tests, examples, or manual
verification. If validation fails and cannot be fixed quickly, stop before
committing and report the blocker.

Set `phase: "commit"`.

---

## 9. Commit and Push

Commit directly on the destination default branch only because this skill is for
the explicit "commit and push to main/default" workflow. If repo policy forbids
direct pushes, stop and say a PR is required.

Before committing:

```bash
git status --short
git branch --show-current
git pull --ff-only origin "$BASE_BRANCH"
```

Commit requirements:

- Conventional commit format.
- Human-written message describing why the feature gap is being closed.
- No source repo mention unless legally required.
- No AI attribution.
- No `Co-Authored-By`.

Example:

```text
feat: add missing export filters
```

Push:

```bash
git push origin "$BASE_BRANCH"
```

Record the commit SHA and set `phase: "handoff"`.

---

## 10. Handoff

Report:

- Destination repo and branch.
- Commit SHA.
- Feature gap(s) closed.
- Key files changed.
- Tests and validation run.
- Any feature gaps intentionally deferred.
- Any legal or policy constraints encountered.

Keep the response concise and focused on the landed destination change.

## Definition of Done

- Source and destination were inspected through authenticated GitHub access.
- Real feature gaps were distinguished from branding, infrastructure, or
  already-equivalent behavior.
- User approval was obtained for broad or risky changes.
- Implementation is destination-native.
- Tests/docs were updated where appropriate.
- Destination checks pass or approved exceptions are documented.
- Changes were committed and pushed to the destination default branch.
