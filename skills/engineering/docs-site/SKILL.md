---

name: docs-site
description: Create a branded documentation site for an application from the smeltery/quire template, matching the application's name, logo, colors, and voice. Runs a resumable workflow with user approval gates for scope, brand, outline, content, and release. Use when the user wants a docs site, developer docs, or API reference for an app, or wants to rebrand or extend an existing quire site. Use website-studio for a marketing site instead.
argument-hint: "<app repo|URL|path> [--docs-repo <owner/name>] [--target <path>]"
---

# Docs Site

Turn an application into a branded, searchable documentation site built on
[smeltery/quire](https://github.com/smeltery/quire). The template supplies the
layout, search, diagrams, page actions, CI, and releases. This workflow supplies
the brand, the page outline, and accurate content.

**Arguments:** "$ARGUMENTS"

## Operating contract

- The application is the source of truth. Every claim on a page must trace to
  its code, README, CLI help, API routes, or a fact the user stated. Never invent
  features, flags, limits, endpoints, pricing, or customers.
- Change data, not template code: `brand.json`, `public/` assets, and
  `content/**/*.json`. Edit `src/` only when a gate approves a template change.
- Stop at every gate below and wait for an explicit answer. Approval that is
  already in the user's request counts; never ask twice for the same decision.
- Gates authorize only what they name. Creating repositories, pushing, opening
  pull requests, and deploying need the Release gate.
- Keep updates short: current phase, evidence, the decision needed, next gate.

## 1. Start or resume

1. Locate the application. For a URL or `owner/name`, use a fresh read-only clone
   in a scratch directory; never modify the application repository.
2. Locate or plan the docs repository. An existing quire site has `brand.json`
   and `content/`; resume inside it. Otherwise, the docs repository is created
   at the Release gate. Until then, work in a local clone of the template:

   ```bash
   gh repo clone smeltery/quire <target> -- --depth 1
   cd <target> && rm -rf .git && git init -b main
   ```

3. Read state at `<target>/.docs-site/state.json`. Create it if missing:

   ```json
   {
     "schemaVersion": 1,
     "app": null,
     "target": null,
     "docsRepo": null,
     "phase": "scope-gate",
     "approvals": {},
     "outline": [],
     "verifiedAt": null
   }
   ```

4. State is a cache. Re-check the files a phase produced before trusting it, and
   route back to the earliest phase whose artifact is missing or stale. Keep
   `.docs-site/` out of version control (it is in the template's `.gitignore`).

## 2. Route by phase

```text
scope-gate -> brand -> brand-gate -> outline -> outline-gate
          -> write -> verify -> content-gate -> release-gate -> handoff
```

Write state after each phase. Record each gate as
`approvals.<gate> = { "at": <ISO time>, "summary": <one line> }` and only then
advance. A rejected gate stays put with the requested revisions noted.

| Phase          | Artifact                                                      | Completion test                                               |
| -------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| `scope-gate`   | App source, audience, docs repo name and visibility, host     | User approves the scope summary                               |
| `brand`        | `brand.json`, `public/logo.svg`, `public/og.svg`, brand notes | Values trace to the app; text contrast is at least 4.5:1      |
| `brand-gate`   | Screenshots of the branded site beside the app                | User approves or names changes                                |
| `outline`      | Page table: path, title, group, purpose, sources              | Every feature in scope maps to a page; no page lacks a source |
| `outline-gate` | The outline                                                   | User approves the page list and groups                        |
| `write`        | `content/**/*.json`; sample pages removed                     | One file per approved page, schema test passes                |
| `verify`       | Command log and rendered-page review                          | `bun run ci` passes; each page is inspected in a browser      |
| `content-gate` | Page links, screenshots, open questions                       | User approves the content                                     |
| `release-gate` | Exact repo, push, and deploy actions                          | User approves each external action                            |
| `handoff`      | URLs, CI status, how to edit                                  | CI is green on the pushed commit                              |

## 3. Gates

1. **Scope gate.** Summarize the application, the readers (end users, API
   clients, operators, contributors), what is in and out of scope, the docs
   repository `owner/name` and visibility, and the intended host. Ask once for
   anything you cannot discover.
2. **Brand gate.** Follow [brand extraction](references/brand-extraction.md).
   Show the proposed name, wordmark, logo, palette with contrast ratios, and
   desktop and mobile screenshots next to the app's own UI. Note every value you
   guessed.
3. **Outline gate.** Follow [content guide](references/content.md). Present the
   outline as a table with the source for each page. Flag thin areas rather
   than padding them.
4. **Content gate.** Link every page on the local preview, attach screenshots
   of the overview and one dense page, and list open questions and claims you
   could not verify. Unverifiable claims are removed, not softened.
5. **Release gate.** List the exact actions: `gh repo create <owner/name>
   --template smeltery/quire`, the push, the hosting change. Execute only what the
   user approves.

## 4. Execute phases

### brand

Read [brand extraction](references/brand-extraction.md). Fill every key in
`brand.json`, keep all `theme` token names, and replace both SVGs. Set `nav`,
`groups`, and `popular` after the outline is approved.

### outline and write

Read [the content guide](references/content.md). Remove the template's sample
pages, keep the JSON schema, and prefer more short pages over long ones. Use
diagrams for flows with more than two actors, and endpoint sections for API
reference. Run `bun test` after each batch of pages.

### verify

```bash
flox activate -- bun run ci   # or: bun install && bun run ci
bun run preview
```

Open every page at desktop and mobile widths. Check the sidebar, search for
three real terms, copy a code block, use Copy as Markdown, and open the 404
page. Fix broken layout, overflow, or empty sections before the Content gate.

### release-gate and handoff

After approval, create the repository from the template, copy the branded
files over the fresh clone, commit as a single change, and push. Watch the
`ci` workflow until it passes; fix failures rather than skipping hooks. The
`auto-release` workflow tags the green commit, and `release` attaches the
built site archive. Report the repository, CI run, release, and preview or
deployed URL. Distinguish a local preview from a deployment.

## Completion

Done means every gate is approved, CI is green on the pushed commit, and every
page states only verified facts. If a dependency blocks progress, record it in
state, finish independent work, and report the blocker with the resume command:
`/docs-site <target>`.
