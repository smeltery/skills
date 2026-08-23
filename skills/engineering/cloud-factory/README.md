# /cloud-factory

Convert a GitHub repository into a cloud software factory with agent skills,
workflow triggers, labels, and domain-doc placeholders.

## Install

```bash
npx skills@latest add smeltery/skills --skill cloud-factory --agent codex --yes
```

## Usage

```text
/cloud-factory
```

The skill installs the reusable assets from
[smeltery/cloud-factory](https://github.com/smeltery/cloud-factory) into the
current repository and verifies the factory scaffold.

## Factory flow

```mermaid
flowchart LR
  Issue["New GitHub issue"] --> Triage["Triage agent"]
  Triage --> Decision{"Readiness"}
  Decision -->|ready-to-implement| Implement["Implementation agent"]
  Decision -->|ready-to-spec| Spec["Spec agent"]
  Decision -->|needs-info| Human["Human follow-up"]
  Decision -->|wait-to-implement| Park["Parked"]
  Spec --> SpecPR["PRODUCT.md + TECH.md PR"]
  SpecPR --> Implement
  Implement --> PR["Implementation PR"]
  PR --> Review["Review agent"]
  Review --> HumanReview["Human review"]
  HumanReview --> Improve["Review-skill improvement loop"]
  Improve --> Review
```

## Files

- [`SKILL.md`](./SKILL.md) — canonical skill definition.
