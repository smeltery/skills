# /pr-monitor

One-pass PR monitoring skill for AI review feedback, GitHub Actions failures, and merge-readiness.

- Resolves actionable bot review threads with a strict bucket bar: fix only what is directly related or genuinely catastrophic, defer valid-but-unrelated findings to a follow-up issue, push back on invalid ones with a one-line reason
- Classifies failing CI runs before touching code (rerun/fixable/stale/report-only/ask-first) and never fixes a red check by deleting or skipping a test
- Reads "green" correctly: counts which checks actually ran, treats a conflicting PR's missing CI as unknown, and treats unreadable values as not-yet-known
- Answers "has the AI reviewer reviewed this?" by requiring a review whose `commit_id` equals the current head SHA, never a wall-clock window
- Two merge bars: PR-review mode (reviewer converged on the current head, 10 minutes quiet, auto-merge never armed) and `--local-converged` (green CI + no conflicts, auto-merge armed on the first pass)

## Install

```bash
npx skills@latest add dotbrains/skills
```

Or copy just this skill:

```bash
mkdir -p ~/.claude/skills/pr-monitor
curl -fsSL https://raw.githubusercontent.com/dotbrains/skills/main/skills/engineering/pr-monitor/SKILL.md \
  -o ~/.claude/skills/pr-monitor/SKILL.md
```

## Usage

```text
/pr-monitor
/pr-monitor 123
/pr-monitor 123 --local-converged
/pr-monitor owner/repo#123
/pr-monitor https://github.com/owner/repo/pull/123
```

Pass `--local-converged` only when the diff already converged through local adversarial review rounds before the PR was opened. It is a claim about work already done, not a way to skip review.

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
