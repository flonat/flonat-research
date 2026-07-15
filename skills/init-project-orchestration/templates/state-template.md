# State Template

> Copy this to `<project>/.planning/state.md` and replace `<placeholders>`.

```markdown
# State — <Working Title>

**Last updated**: <date>
**Current phase**: Phase 0 — Setup complete

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: Setup | Complete | Structure, agents, commands |
| Phase 1: TBD | Not started | — |

## Component Status

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| Data pipeline | Not started | `code/` | — |
| Estimation | Not started | `code/` | — |
| Paper draft | Not started | `paper/` | — |

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Orchestration initialised | Added neutral agents, workflows, adapters, and planning | <date> |
```

## Notes

- **"Last updated" is always today's date** — every `update-state` workflow run refreshes it.
- **Progress table** mirrors phases from `roadmap.md`.
- **Component Status** is optional — useful for projects with distinct work streams.
- **Decisions table** captures methodological choices with rationale and date.
- **Phase status values**: `Not started`, `In progress`, `Complete`.
