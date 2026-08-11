---
name: taste-review
description: Get an independent, taste-driven judgment on an ambiguous choice such as UI polish, prose, naming, or formatting, then weigh and apply the recommendation when authorized. Use when objective checks pass but several defensible options remain.
argument-hint: "<question> [paths...]"
---

# Taste Review: independent judgment for fuzzy choices

Use a separate reviewer to make a clear call when correctness checks cannot
settle the choice. The reviewer advises; the current agent owns the decision,
scope, and verification.

**Arguments:** "$ARGUMENTS"

## 1. Frame the decision

Turn the request into one question. Record:

- the artifact and exact paths in scope;
- the intended audience and outcome;
- constraints that cannot change;
- the options already considered, if any;
- the objective checks that have already passed.

If the choice is actually about correctness, security, accessibility, legal
requirements, or a documented project rule, resolve that evidence first. Do
not use taste to overrule a hard constraint.

## 2. Read the local context

Read the nearest repository guidance and only the files needed to understand
the choice. Inspect the current diff when the artifact is under version
control. Do not modify files yet.

Separate authored work from unrelated user changes. A taste review never
expands the edit scope on its own.

## 3. Choose an independent reviewer

Prefer an already-configured agent, subagent, model tool, or review service
that can receive a fresh brief. The reviewer should not inherit the current
agent's conclusion or hidden chain of reasoning.

Before using an external process or service:

- discover what is available instead of assuming a command, vendor, account,
  operating system, or credential location;
- use its documented non-interactive interface when one exists;
- do not install software, change global configuration, authenticate, or send
  private material without user approval;
- share only the approved question and files, and never expose credentials or
  unrelated repository content.

If no independent reviewer is available, continue with a structured self-review
and label it as such. Never claim that a second opinion occurred when it did
not.

## 4. Send a neutral brief

Give the reviewer enough evidence to judge without steering it toward a desired
answer:

```text
Decision: <one plain question>
Audience and goal: <who and why>
Files or artifact: <bounded paths or description>
Constraints: <facts that cannot change>
Options considered: <optional, neutrally phrased>

Make one recommendation. Explain the strongest reasons, name meaningful
tradeoffs, and list credible alternatives you rejected.
```

For visual work, provide the smallest useful screenshots or runnable route when
the approved reviewer can inspect them. For naming or prose, include the nearby
vocabulary and usage rather than isolated words.

## 5. Adjudicate the result

Check the recommendation against project rules, user intent, accessibility,
rights, and technical constraints. Reject confident advice that conflicts with
evidence. When reviewers disagree, identify the assumption causing the split
instead of averaging their answers.

If the user asked only for an opinion, stop after reporting the call. If edits
are authorized, apply the smallest change that expresses the chosen direction.
Do not copy a reviewer's prose or code wholesale when a narrower edit works.

## 6. Verify and finish

Run the relevant existing checks after an edit. For visual changes, inspect the
rendered result at representative sizes; for prose or naming, search callers and
references for consistency.

If a check fails, determine whether it failed before the edit. Fix or undo only
the changes made by this run; never discard unrelated work. On restart, inspect
the current files and diff before reapplying a recommendation.

A repeated run with the same artifact and no new evidence should not create
more churn. Finish with:

```text
Call: <recommendation>
Reviewer: <independent tool/agent, or structured self-review>
Why: <decisive reasons>
Alternatives: <credible rejected options>
Applied: <paths changed, or none>
Verified: <checks run>
Open: <remaining subjective uncertainty, or none>
```
