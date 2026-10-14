# Evaluation scenarios

Use an isolated temporary target for behavioral testing of this skill. These are
acceptance scenarios for a real agent run, not a claim that the gate controller
can judge visual quality. Preserve screenshots, command results, and the final
site for review. Do not deploy or contact real recipients during evaluation.

## 1. Empty directory, one prompt

Prompt: “Build a complete website for a fictional coastal architecture studio.
Choose the details yourself. Include a portfolio and a way to prepare an inquiry.
Use an editorial visual direction and deliver a local production preview.”

Pass only if the agent chooses and documents a coherent identity without asking
for routine design approvals, produces substantive home/about/work/detail/inquiry
surfaces appropriate to the brief, makes the inquiry outcome honest, and captures
and inspects mobile/desktop production views. No invented real client claims.
All twelve receipts must correspond to actual work. Merely creating JSON receipts
or screenshots is a failure.

## 2. Existing repo and preserved behavior

Supply a working site with a distinctive brand, a nondefault package manager,
an existing form endpoint, and one unrelated user edit. Ask for a full redesign.

Pass only if the agent inventories and preserves the routes, form contract,
package manager, and user edit; improves hierarchy and responsiveness; verifies
real journey behavior with intercepted/test requests; and avoids unnecessary
framework/CMS/backend replacement. Compare the final diff against the starting
worktree, not just the original commit.

## 3. Attractive homepage with hidden UX defects

Seed a site with an attractive desktop hero but an overflowing mobile menu,
invisible keyboard focus, a search with no empty/reset state, a dead detail CTA,
and a form that announces success for a failed request.

Pass only if the agent discovers and fixes every defect through rendered
interaction, preserves input on failure, reruns affected tests, and does not
approve from the homepage screenshot or a clean build alone.

## 4. Missing providers and constrained scope

Provide a reference with an inaccessible repo and a brief that requires actual
online submission, but no delivery credentials. Disallow publishing.

Pass only if the agent records the missing reference evidence, proceeds with an
original design, finishes local work, and reports the required submission as
blocked. A mock/fallback cannot be relabeled verified delivery. It must neither
invent source findings nor ask permission to publish an already local-only task.

## 5. Interrupted or changed work

Pause after `responsive`, change a source file and an earlier evidence file,
then resume with the same prompt.

Pass only if the earliest stale gate is detected, later receipts are invalidated,
changed user files are preserved, affected checks are rerun, and scaffolding is
not duplicated. Run an unchanged completed invocation again; it should verify
and no-op rather than repaint the website.

## Automated controller checks

`tests/test_gates.py` exercises the public CLI in temporary projects. It covers
ordered progression, idempotent initialization, refusal of incomplete/failed
receipts, evidence path containment, stale/missing evidence, source changes,
new untracked assets, explicit invalidation, completion, and corrupt state.

These tests deliberately use synthetic evidence. They validate state mechanics,
not an autonomous agent's design ability. Evaluate the scenarios above with
rendered outputs before making stronger claims about consistent website quality.
