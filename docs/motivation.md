# Why these skills exist

These skills are a response to specific failure modes we keep hitting with
coding agents. Each one targets a problem we got tired of repeating and
encodes the workaround so the agent does it without being asked.

## 1. The agent doesn't actually understand what you want

The default failure of any AI coding session is misalignment. You think you
described the change clearly; the agent confidently builds something else.
Catching it ten minutes in is cheap, catching it after a full implementation
is not.

The fix is a **grilling session before any code gets written** — let the
agent ask you the questions you forgot to answer.

- [`/grill-me`](../skills/productivity/grill-me/README.md) — design / non-code grilling
- [`/grill-with-docs`](../skills/engineering/grill-with-docs/README.md) — same loop, but layered on the project's domain glossary and ADRs

## 2. The agent uses ten words where one would do

Agents drop into a project with no shared vocabulary, so they describe
everything in long generic English. The longer the description, the more
tokens you burn and the easier it is to lose precision.

The fix is a **shared language** captured in a `CONTEXT.md` and grown
incrementally. Once "the materialization cascade" is a defined term, the
agent says "the materialization cascade" instead of three sentences.

`/grill-with-docs` builds that language for you as a side-effect of
grilling — whenever a fuzzy term gets sharpened during the session, it gets
written to `CONTEXT.md` immediately.

## 3. The code doesn't work

When the agent and you are aligned on what to build, the next failure mode
is the agent producing code that compiles but doesn't behave. The cure is
**fast, deterministic feedback loops**: types, tests, browser access — and
discipline about how to use them.

- [`/tdd`](../skills/engineering/tdd/README.md) — red-green-refactor with vertical-slice tracer bullets, not horizontal "write all tests first"
- [`/diagnose`](../skills/engineering/diagnose/README.md) — bug-hunt loop where Phase 1 is *building the feedback loop itself*; everything else is mechanical

## 4. The codebase becomes a ball of mud

Agents accelerate coding, which means they also accelerate entropy. Without
deliberate design effort, the codebase grows complex faster than any human
can keep in their head.

The cure is **caring about design every day** — surfacing architectural
friction early and refactoring shallow modules into deep ones before they
calcify.

- [`/zoom-out`](../skills/engineering/zoom-out/README.md) — get oriented before changing unfamiliar code
- [`/to-prd`](../skills/engineering/to-prd/README.md) — capture the modules you're about to touch in a PRD before any code gets written
- [`/improve-codebase-architecture`](../skills/engineering/improve-codebase-architecture/README.md) — find deepening opportunities in an existing codebase, run periodically

## 5. The PR cycle eats your day

Even when the agent ships good code, getting it through review, CI, and
merge is its own slog: address reviewer comments, fix flaky checks, rebase
when conflicts appear, repeat for hours.

The cure is **letting the agent own the entire ticket** — from worktree to
merge — and **reviewing each PR with the same discipline a human reviewer
would**.

- [`/workon`](../skills/engineering/workon/README.md) — drives a Linear ticket end-to-end, including a 5-minute watch loop that addresses review comments, fixes CI failures, and resolves merge conflicts until the PR merges
- [`/review`](../skills/engineering/review/README.md) — read-only, high-signal PR review with explicit Critical / Suggestions / Nits tiers, scoped against the ticket's stated intent

The first four failure modes are general — the engineering ideas behind
them are largely from
[mattpocock/skills](https://github.com/mattpocock/skills), where most of
those skills originated. `/workon` and `/review` are smeltery originals
written for our own delivery loop.

## Further reading

The skills draw on a small canon. If you want the long-form versions of the
ideas they encode, these four books are the source material:

- **[The Pragmatic Programmer](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/)** — David Thomas & Andrew Hunt. The classic on alignment ("no-one knows exactly what they want") and feedback loops ("the rate of feedback is your speed limit"). Underpins `/grill-me` and `/diagnose`.
- **[Domain-Driven Design](https://www.domainlanguage.com/ddd/)** — Eric Evans. The case for a ubiquitous language shared between developers and domain experts. Underpins `/grill-with-docs` and the `CONTEXT.md` discipline.
- **[Extreme Programming Explained](https://www.informit.com/store/extreme-programming-explained-embrace-change-9780321278654)** — Kent Beck. "Invest in the design of the system every day." Underpins `/tdd` and the design-first stance of `/improve-codebase-architecture`.
- **[A Philosophy of Software Design](https://web.stanford.edu/~ouster/cgi-bin/book.php)** — John Ousterhout. Source of the deep-modules framing — "the best modules are deep" — that drives `/improve-codebase-architecture` and informs `/to-prd`.
