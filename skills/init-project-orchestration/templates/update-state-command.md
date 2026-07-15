---
schema: ai-project-command/v1
name: update-state
description: "Update the project's planning state from verified work completed in this session"
argument_hint: "[phase or component to update]"
capabilities:
  - filesystem-read
  - filesystem-write
adapters:
  claude:
    allowed_tools: [Read, Edit, Write]
---

# Update project state

## Process

1. Read `.planning/state.md` and `.planning/roadmap.md`.
2. Compare their claims with the work actually completed in this session.
3. Update the progress and component-status tables.
4. Record any new methodological or implementation decision with its rationale.
5. Set `Last updated` to today's date.
6. Mark a phase complete only when every required roadmap item is complete.

## Quality checks

- [ ] The date is current.
- [ ] Progress reflects verified work rather than intended work.
- [ ] No phase is complete while required roadmap items remain open.
- [ ] New decisions include a rationale.
