---
name: cloud-factory
description: Convert the current GitHub repository into a cloud software factory by installing agent skills, docs, labels, specs directories, and GitHub Actions workflow templates. Use when the user wants one-command repository setup for automated triage, spec, implementation, review, or feedback loops.
argument-hint: "[repo path] [--agent codex|claude|all]"
---

# Cloud Factory

Convert a repository into a software factory.

## Default command

From the target repository root, run:

```sh
gh api repos/dotbrains/cloud-factory/contents/scripts/install-cloud-factory.sh \
  --jq .content | base64 --decode | bash
```

For per-agent installation, set `CLOUD_FACTORY_AGENT` to a comma-separated list:

```sh
CLOUD_FACTORY_AGENT=codex,claude \
  bash scripts/install-cloud-factory.sh
```

When using the remote installer with multiple agent targets:

```sh
CLOUD_FACTORY_AGENT=codex,claude \
  bash -c "$(gh api repos/dotbrains/cloud-factory/contents/scripts/install-cloud-factory.sh --jq .content | base64 --decode)"
```

## Workflow

1. Resolve the target repository. Use the current working directory unless the
   user provided a path.
2. Confirm it is a Git repository.
3. Run the installer with the requested agent target. Default to `codex` when
   unspecified. Use authenticated `gh api` for the private canonical repo.
4. Verify these files exist:
   - `.agents/skills/triage/SKILL.md`
   - `.agents/skills/spec/SKILL.md`
   - `.agents/skills/implementation/SKILL.md`
   - `.agents/skills/review-pr/SKILL.md`
   - `.agents/skills/improve-review-pr/SKILL.md`
   - `.github/workflows/triage-issues.yml`
   - `.github/workflows/spec-ready-issues.yml`
   - `.github/workflows/implement-ready-issues.yml`
   - `.github/workflows/review-pull-requests.yml`
   - `.github/workflows/improve-review-pr.yml`
   - `docs/agents/issue-tracker.md`
   - `docs/agents/triage-labels.md`
   - `docs/agents/domain.md`
5. Report what changed and what still needs human configuration.

## Human setup checklist

- Create GitHub labels:
  - `needs-triage`
  - `ready-to-implement`
  - `ready-to-spec`
  - `needs-info`
  - `wait-to-implement`
- Set the cloud-runner API key secret required by the installed workflows.
- Edit `vision.md`, `roadmap.md`, and `CONTEXT.md` so triage has real product
  and domain context.

## Guardrails

- Do not overwrite secrets or `.env` files.
- Do not enable auto-merge.
- Do not remove existing repository instructions.
- If files already exist, keep user changes and only replace Cloud Factory files
  when the user explicitly asks for a refresh.
