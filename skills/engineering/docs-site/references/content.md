# Content guide

## Build the outline from sources

Inventory the application before proposing pages:

- README, existing `docs/`, CHANGELOG, and examples.
- CLI commands and flags from `--help` output or the argument parser.
- HTTP routes, request and response shapes, auth, limits, and error codes.
- Configuration: environment variables, config files, defaults.
- Install and deploy paths that the repository actually supports.

Group pages using the template's defaults unless the app needs others:

| Group      | Holds                                               |
| ---------- | --------------------------------------------------- |
| Start here | Overview (with `hero`), Quick start                 |
| Guides     | Task-oriented pages: one goal per page              |
| Reference  | Exhaustive tables: CLI, config, API, errors, limits |
| Examples   | Complete, copyable programs or recipes              |

## Write pages

- One JSON file per page under `content/`. Match the schema in the template's
  `content/reference/page-schema.json`; the content test rejects unknown keys.
- The first paragraph answers "what is this and when do I use it".
- Paragraphs are plain text. Put commands and payloads in `code` with a
  `language` label such as `Terminal`, `cURL`, `JSON`, or a filename.
- Every command and example must have been run or read from source. Mark
  anything else as an open question for the Content gate.
- Use `diagram` for request flows and lifecycles; keep labels under 40
  characters. Use `endpoint` sections for each API route.
- Use `table` for flags, options, and errors. The first row is the header.
- Link related pages with `links` cards rather than inline URLs.
- Set `popular` in `brand.json` to the four to six pages readers need first.

## Before the Content gate

- `bun run ci` passes.
- Every page has at least one section with real content.
- No sample page from the template remains.
- Search finds each page by its main term.
