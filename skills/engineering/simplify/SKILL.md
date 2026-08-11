---
name: simplify
description: Simplify a finished code change for human review without changing behavior. Use automatically after the scoped implementation works and relevant checks pass, or whenever writing and reviewing code comments.
argument-hint: "[path-or-diff-range]"
---

# Simplify: final code and comment cleanup

Review the current change, or the scope supplied by the user. Make the code
easier to read while preserving behavior, public contracts, and repository
conventions.

**Arguments:** "$ARGUMENTS"

## 1. Establish scope and baseline

Read the repository guidance that applies to the selected files. Resolve the
scope from, in order:

1. the user's paths or diff range;
2. the current branch diff;
3. the smallest set of files changed for the stated task.

Inspect `git status` and the full scoped diff before editing. Identify unrelated
user changes and leave them untouched. Record the relevant checks and their
current result. If the implementation does not work yet, return to the build or
diagnosis loop instead of polishing broken code.

## 2. Use plain words

Treat names and comments as prose:

- Prefer short, concrete words over long or abstract ones.
- Cut words the surrounding module or type already supplies.
- Use active language and familiar project vocabulary.
- Keep one word for each concept and one concept for each word.
- Rename a compound phrase when one precise term carries the same meaning.

Do not rename stable public APIs merely to satisfy a wording preference. Follow
the repository's compatibility policy and update all in-scope callers when an
internal rename is worthwhile.

## 3. Improve names

Build a small vocabulary from nearby code before renaming anything. Check that:

- the same concept has the same name across the scope;
- different concepts do not share one vague name;
- booleans read as clear conditions;
- functions state the useful action without repeating their module or type;
- temporary and callback names remain clear at their actual reading distance.

Prefer no rename over a lateral rename that merely reflects personal style.

## 4. Improve comments

Comments should explain a constraint, reason, invariant, side effect, or other
fact the code cannot show clearly.

- Add a comment for non-obvious logic or a surprising constraint.
- Add API documentation when callers need behavior, side effects, failure, or
  lifecycle details that the signature cannot express.
- Delete comments that restate self-evident code.
- Delete change-history narration that belongs in version control.
- Rewrite jargon and stale comments in plain language.

When asked only to review comments, keep the edit scope to comments unless a
small nearby rename is required to make the comment truthful.

## 5. Simplify structure

Apply these checks without forcing every file into one shape:

1. **Lead with the important code.** Put exports or significant entry points
   before details when the language and local conventions allow it.
2. **Group by concept.** Split a large unit only when the new boundary owns a
   coherent responsibility.
3. **Merge overlap.** Combine types, functions, or constants that model the same
   concept and do not need separate lifecycles.
4. **Reuse local code.** Search for an existing helper before adding another.
5. **Derive instead of store.** Remove parameters or state that can be computed
   cheaply and reliably from values already in scope.
6. **Flatten needless flow.** Prefer early exits and direct data flow when they
   make success and failure paths easier to see.

Do not create abstractions solely to shorten a file or remove a few repeated
lines. A useful simplification lowers the number of concepts a reader must hold.

## 6. Remove branch-history artifacts

Code must make sense to a reader who did not watch the task happen:

- Rewrite names and comments that rely on conversation or PR history.
- Remove compatibility paths for an earlier shape that existed only in the
  current unshipped branch, then update its in-scope callers.
- Keep compatibility for released or externally consumed behavior unless the
  user explicitly approves a breaking change.
- Remove dead experiments, unused aliases, and defensive branches only when
  searches and tests show they are not needed.

## 7. Edit in small batches

Work from low-risk wording and dead-comment cleanup toward structural changes.
After each meaningful batch, inspect the diff and run the narrowest relevant
formatter, type check, lint, or test.

If a batch breaks a check, fix it or undo only that batch. Never reset the
worktree or discard unrelated changes. On restart, treat the filesystem and
current diff as source of truth; do not assume the earlier batch completed.

## 8. Verify and stop

Run the repository's relevant existing checks after the final edit and compare
with the baseline. Review the resulting diff for behavior changes, API drift,
and churn.

Stop when another pass would only trade one valid style for another. A second
run over unchanged code should find no worthwhile edits.

Report:

```text
Scope: <paths or diff>
Simplified: <names, comments, structure, or none>
Behavior: <why it remains unchanged>
Verified: <checks run and results>
Open: <remaining risk or none>
```
