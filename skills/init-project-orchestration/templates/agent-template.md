# Neutral project-agent template

Copy this structure to `.ai/orchestration/agents/<role>.md`. Replace every
placeholder and keep the source free of client-home paths and client tool
syntax.

```markdown
---
schema: ai-project-agent/v1
name: <role-name>
description: "<When this role should be dispatched and what it owns>"
artifact_contract:
  mode: project-write
write_policy:
  project: scoped-write
  git: forbidden
capabilities:
  - filesystem-read
  - filesystem-write
model_preferences:
  claude: sonnet
  codex: default
adapters:
  claude:
    tools: [Read, Write, Edit, Glob, Grep]
---

# <Role title>

You are the <role description> for **<project title>**.

## Responsibilities

- <project-specific responsibility>
- <project-specific responsibility>

## Working surfaces

- Read: `<specific project paths>`
- Write: `<specific project paths>`

## Standards

- <project-specific standard>
- <project-specific verification requirement>

## Boundaries

- Do not <adjacent responsibility>; the `<other-role>` agent owns it.
- Never modify `data/raw/`.
```

Use `artifact_contract.mode: response-only` with
`write_policy.project: read-only` for a project agent that only reports to its
caller. Keep `write_policy.git: forbidden` unless Git mutation is an explicit,
caller-authorized part of the role.
