# Phase 2.1: Pre-Template Detection & Remediation

> Detailed check for the `audit-project-research` Phase 2.1 neutral scaffold.

## Pre-template project detection

If the project has **no `.context/`** and neither `CLAUDE.md` nor `AGENTS.md`, flag it as a **pre-template project** and add a consolidated note. A `.claude/` or `.codex/` adapter directory on its own is not shared project context.

```
Pre-template project detected
===============================
This project predates the current client-neutral research-project template.
To bring it into the framework, consider adding:

  1. mkdir -p .context && touch .context/current-focus.md .context/project-recap.md
  2. Create the root guidance used by the installed clients (CLAUDE.md, AGENTS.md, or both)
  3. mkdir to-sort && touch to-sort/.gitkeep
  4. Add client-specific adapter files only for clients that use them

Or use the `init-project-research` skill in "retrofit" mode where available.
```

## Remediation suggestions

For each missing common core item, include a one-line remediation suggestion:

| Missing item | Suggestion |
|-------------|------------|
| `.context/` | `mkdir -p .context && touch .context/current-focus.md .context/project-recap.md` |
| `.gitignore` | Copy the current `init-project-research` Phase 4 template |
| client adapter settings | Optional; use the applicable client configuration skill only when that adapter is installed |
| `to-sort/` | `mkdir to-sort && touch to-sort/.gitkeep` |
| root guidance | See the current `init-project-research` Phase 4 templates for `CLAUDE.md` and `AGENTS.md` |
| `README.md` | See the current `init-project-research` Phase 4 template |
| `correspondence/` | `mkdir -p correspondence/referee-reviews && touch correspondence/referee-reviews/.gitkeep` |
| `docs/` | `mkdir -p docs/{literature-review,readings}` |
| `docs/literature-review/` | `mkdir -p docs/literature-review && touch docs/literature-review/.gitkeep` -- `literature` outputs go here |
| `docs/venues/` | `mkdir -p docs/venues && touch docs/venues/.gitkeep` |
| `log/` | `mkdir log && touch log/.gitkeep` |
| `MEMORY.md` | Seed from the current `init-project-research` Phase 4 template (research or teaching variant) |
