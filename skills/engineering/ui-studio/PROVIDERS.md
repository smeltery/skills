# Optional Design Providers

Use this guide only when Paper, Refero, or ui.sh is supplied by the user,
available in the active tool/skill registry, or useful enough to propose at a
gate. The core UI Studio workflow must remain usable without any provider.

Copy `templates/integrations.json` to the kit's durable documentation after the
Name gate when a provider affects design decisions or generated files. Validate
it with schema `integrations`, then run `check-integrations.py`; use `--release`
before the Release gate. Do not commit credentials, authentication state,
subscription data, or provider-returned private artifacts.

```bash
python3 scripts/validate-kit.py --schema integrations integrations.json
python3 scripts/check-integrations.py integrations.json --release
```

## Paper MCP: shared design canvas

Paper MCP can read and write the design file currently open in Paper Desktop.
Treat the active MCP tool schema as authoritative; never invent tool names or
parameters. Current capabilities include file/selection summaries, node trees,
screenshots, JSX and computed styles, image fills, fonts, exports, and scoped
node creation or mutation.

Choose one mode during Intake:

- `read-only-reference` — inspect the named file, selected artboards, hierarchy,
  screenshots, and computed design evidence. This is the default.
- `collaborative-canvas` — create or revise explicitly named artboards for
  direction boards, responsive variants, sticker sheets, or review feedback.

Before either mode, ask the provider for basic file/page/artboard information
and the current selection, then show the resolved identity. A selected frame is
context, not permission to inspect unrelated pages.

For collaborative mode:

1. Obtain explicit approval for the file, artboards/nodes, allowed operation
   classes, and whether exports may be written to disk. Record this scope without
   copying private content into state.
2. Capture a before screenshot and compact tree summary for affected nodes.
3. Make the smallest reversible write. Prefer creating a new labeled artboard or
   duplicating an approved node over destructively replacing existing work.
4. Never delete nodes, overwrite an existing artboard, or export to a durable
   path unless that exact action is approved.
5. Re-read the changed hierarchy/styles, capture an after screenshot, clear any
   provider working indicator, and report node IDs plus limitations.

Paper is based on web layout, but a Paper frame is not a navigable product.
Structural, screenshot, JSX, and style inspection cannot prove focus, keyboard,
network, responsive, or state behavior. Exercise an exported/runnable result
with Playwright when those claims matter.

Treat Paper JSX and computed styles as design evidence. Rebuild the approved
direction through the destination repository's public components and tokens;
do not paste provider output wholesale or let it override rights restrictions.
When syncing tokens, normalize them through the DTCG workflow in `QUALITY.md`
and review aliases, fonts, images, and unsupported translation details.

Connection and authentication belong to the user. Paper's official Codex path
uses its Desktop plugin or a user-configured local MCP server. UI Studio may
diagnose a missing connection, but it must not install plugins, alter global MCP
configuration, or impersonate the user. See [Paper MCP documentation](https://paper.design/docs/mcp).

## Refero: real-product design research

Use Refero to answer a product question, not to select a fashionable skin. Its
MCP returns curated real-product screens/flows with structured metadata; a deep
link or authorized export may be used through the ordinary curated-reference
path when MCP is unavailable.

Before searching, define:

- the task, user, content pressure, platform, and state/flow to investigate;
- a bounded result count, normally three to eight;
- diversity dimensions such as product category, density, platform, interaction
  model, visual voice, or accessibility constraint;
- traits the current direction must avoid, not merely traits to copy.

Prefer a small evidence set from distinct products over many visually similar
screens. For every result, retain the provider result ID/deep link, source
product when supplied, screen/flow/pattern type, structured rationale, and the
specific product question it informs. Preserve ordered flows. Do not bulk-query
or crawl the catalog.

Refero evidence is `inspiration-only` unless the user independently establishes
reuse rights. A provider-generated style guide, DESIGN.md, token table, image,
or screenshot does not license brand assets, proprietary copy, trade dress, or
source implementation. Convert evidence into original product rules and record
which conspicuous traits were transformed or rejected.

At Synthesis, run an anti-generic check:

- no direction is justified only by popularity, polish, or one source;
- each adopted trait solves the product's hierarchy, content, or interaction
  problem;
- each direction names at least one generic generated-UI cliché it excludes;
- combined traits form one coherent system rather than a collage;
- realistic, adverse, dense, and narrow states still govern the result.

Refero authentication opens in the user's browser and may require a paid plan.
Never request, paste, store, or commit its credentials/session. The active MCP
schema is authoritative. If unavailable, disclose the gap and continue with
other sources. See [Refero MCP documentation](https://doc.refero.design/mcp/getting-started).

## ui.sh: optional specialist polishing skills

ui.sh skills are project-installed external skills. Use only skills visible in
the active skill registry or installed in the destination repository. Read the
selected skill's instructions completely and let its own contract govern its
work. Never copy or vendor ui.sh's proprietary skill text into the kit.

Route the smallest relevant set:

| ui.sh skill | UI Studio phase and boundary |
| --- | --- |
| `ideas` | Generate genuinely different direction candidates before the Direction gate; remove option-picker scaffolding from production. |
| `design` | Refine an approved product-linked direction during Foundations through Compositions; repository conventions and public contracts still win. |
| `brand-kit` | Propose brand foundations only when brand creation is in approved scope; preserve provenance and token review. |
| `markup-from-image` | Bootstrap semantic structure from authorized static evidence; it cannot prove behavior or grant copying rights. |
| `make-responsive` | Stress approved compositions across content-led breakpoints, then rerun Playwright and accessibility checks. |
| `add-dark-mode` | Add an explicitly approved theme; verify contrast, imagery, system preferences, and semantic token parity. |
| `dark-mode-image` | Create approved raster variants with provenance; never transform third-party assets without rights. |
| `componentize` | Refactor only after behavior stabilizes; rerun public API, consumer, and compatibility checks. |
| `canonicalize-tailwind` | Use only when Tailwind is already present; treat as a behavior-preserving cleanup and rerun visual/build checks. |

Do not invoke every installed skill by default or use polishing to conceal weak
hierarchy. UI Studio's Direction, Name, and Release gates remain authoritative,
as do generated-file hash protection, critique, production verification, and
accepted limitations.

The official installer requires a private token and changes the project. Propose
installation at the Name gate as a tool/dependency addition. The user runs or
authorizes the installer through their own credential flow; UI Studio never asks
them to paste the token into chat or state. If no relevant ui.sh skill is
installed, continue with UI Studio's native build and critique workflow. See
[ui.sh skills](https://ui.sh/).
