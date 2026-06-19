# Contributing

Each skill lives in its own directory under
`skills/<category>/<name>/SKILL.md`, where `<category>` is one of
`engineering`, `productivity`, or `misc`. Every `SKILL.md` must start with YAML
frontmatter containing at minimum `name` and `description`. CI validates
frontmatter, checks that the directory name matches the `name` field, and
lints markdown across the repo.

## Repository layout

Skills follow a consistent `skills/<category>/<name>/` pattern. Each skill
directory holds the canonical `SKILL.md`, a `README.md`, and any bundled
reference files the skill loads on demand:

```text
skills/
  engineering/
    diagnose/
      SKILL.md
      README.md
      scripts/hitl-loop.template.sh
    improve-codebase-architecture/
      SKILL.md  README.md
      DEEPENING.md  HTML-REPORT.md  INTERFACE-DESIGN.md  LANGUAGE.md
    ...
  productivity/
    teach/
      SKILL.md  README.md
      GLOSSARY-FORMAT.md  LEARNING-RECORD-FORMAT.md
      MISSION-FORMAT.md   RESOURCES-FORMAT.md
    ...
scripts/
  link-skills.sh   # symlink every SKILL.md into ~/.claude/skills/
  list-skills.sh   # print discovered SKILL.md paths
```

See [docs/skills.md](./skills.md) for the full list of skills.

The `npx skills add` CLI scans `skills/<category>/<name>/SKILL.md`, so any
skill added under that layout is auto-discovered.
