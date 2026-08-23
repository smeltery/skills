# Third-Party Licenses

This repository redistributes content from other open-source skill collections.
Each block below records the upstream source and its original license terms,
which apply to that content even though the repository as a whole is licensed
under [PolyForm Shield 1.0.0](./LICENSE).

---

## Matt Pocock — `mattpocock/skills`

**Upstream:** https://github.com/mattpocock/skills
**License:** MIT

The following skills were ported from `mattpocock/skills` and remain MIT-licensed:

- `skills/engineering/diagnose/` (including `scripts/hitl-loop.template.sh`)
- `skills/engineering/grill-with-docs/` (including `CONTEXT-FORMAT.md`, `ADR-FORMAT.md`)
- `skills/engineering/improve-codebase-architecture/` (including `DEEPENING.md`, `HTML-REPORT.md`, `INTERFACE-DESIGN.md`, `LANGUAGE.md`)
- `skills/engineering/prototype/` (including `LOGIC.md`, `UI.md`)
- `skills/engineering/tdd/` (including `tests.md`, `mocking.md`, `deep-modules.md`, `interface-design.md`, `refactoring.md`)
- `skills/engineering/to-issues/`
- `skills/engineering/to-prd/`
- `skills/engineering/triage/` (including `AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`)
- `skills/engineering/wayfinder/`
- `skills/engineering/zoom-out/`
- `skills/productivity/caveman/`
- `skills/productivity/grill-me/`
- `skills/productivity/handoff/`
- `skills/productivity/teach/` (including `GLOSSARY-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`, `MISSION-FORMAT.md`, `RESOURCES-FORMAT.md`)
- `skills/productivity/write-a-skill/`

A few upstream skills (`triage`, `to-issues`, `to-prd`) reference an
upstream `setup-matt-pocock-skills` skill that has not been ported here.
The cross-references are intentionally preserved as written; install the
upstream version from `mattpocock/skills` if you need it, or hand-configure
your issue tracker and triage label vocabulary.

### Original license

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Owain Lewis — `owainlewis/blueprint`

**Upstream:** https://github.com/owainlewis/blueprint
**License:** MIT

The following skills were ported from `owainlewis/blueprint` and remain
MIT-licensed:

- `skills/engineering/architecture/`
- `skills/engineering/architecture-review/`
- `skills/engineering/design/`
- `skills/engineering/html-doc/` (including `scripts/html_doc.py`, `assets/mermaid.json`, `assets/puppeteer.json`, `assets/styles.css`, `package.json`, `package-lock.json`, `tests/test_html_doc.py`, `tests/fixtures/`)
- `skills/engineering/verify/` (ported from upstream `test`, renamed to avoid confusion with `tdd`)

`html-doc` renames the embedded generator identity (`blueprint/html-doc@1` to
`smeltery-skills/html-doc@1`), the npm package name, and a temporary-directory
prefix away from upstream branding; the generation and verification logic is
otherwise unchanged.

### Original license

```
MIT License

Copyright (c) 2026 Owain Lewis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Can Celik — `ogulcancelik/agent-skills`

**Upstream:** https://github.com/ogulcancelik/agent-skills
**License:** MIT

The following skills were ported from `ogulcancelik/agent-skills` and remain
MIT-licensed:

- `skills/productivity/web-search/`

### Original license

```
MIT License

Copyright (c) 2025 Can Celik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Ben Holmes — `bholmesdev/skills`

**Upstream:** https://github.com/bholmesdev/skills
**Source revision:** `44da67bd1896cdafced6f60573b62ae71d18ef2a`
**License:** MIT

The following skills were adapted from `bholmesdev/skills` and remain
MIT-licensed:

- `skills/engineering/simplify/`
- `skills/productivity/taste-review/`

### Original license

```
MIT License

Copyright (c) 2026 Ben Holmes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
