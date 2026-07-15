# Neutral project-command template

Copy this structure to `.ai/orchestration/commands/<workflow>.md`. The renderer
creates the Claude Code command and Codex repository skill; do not put either
client's invocation syntax in this canonical source.

```markdown
---
schema: ai-project-command/v1
name: <workflow-name>
description: "<What this project workflow accomplishes>"
argument_hint: "[<expected input>]"
capabilities:
  - filesystem-read
  - filesystem-write
adapters:
  claude:
    allowed_tools: [Read, Write, Edit, Glob, Grep]
---

# <Workflow title>

## Process

1. Read the active client's project guidance and relevant `.context/` files.
2. Read `.planning/state.md` and the project inputs for this workflow.
3. <project-specific execution step>
4. <project-specific verification step>
5. Update `.planning/state.md` with progress.

## Quality checks

- [ ] <project-specific check>
- [ ] Only declared output paths changed.
- [ ] `.planning/state.md` reflects the result.
```

Capabilities describe behavior. Claude's `allowed_tools` field is adapter-only
metadata; Codex receives a repository-scoped skill and follows its active
permission mode.
