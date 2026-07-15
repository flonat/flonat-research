# Atlas Sync — Phase 7 Details

> Referenced from: `init-project-research/SKILL.md` Phase 7

Creates the research topic in the canonical Research Vault, then registers the corresponding project and Task Management context. Define `VAULT_ROOT` from `RESEARCH_VAULT_ROOT` when set or the home-relative `vault` directory otherwise.

## 7a. Create Atlas Topic File

1. Read theme files from `<vault-root>/themes/` — current themes and their metadata
2. Glob `<vault-root>/atlas/**/*.md` — existing slugs (avoid duplicates)
3. Determine the **slug** (kebab-case, 2-5 words). Pattern: `{contribution}-{domain-object}`. Names the idea, not venue/output/method. Within clusters (e.g., carbon, elicitation), each slug needs a unique distinguishing word. Anti-patterns: acronyms (`efficient-pe`), bare fields (`smart-meters`), venue names (`facct-paper`). Good: `carbon-collusion`, `elicitation-cost-tradeoffs`.
4. Write `<vault-root>/atlas/{theme-dir}/{slug}.md` using the YAML frontmatter template from [`atlas-schema.md`](atlas-schema.md). Include `## Description`, `## Key References`, `## Open Questions`.
5. **Validate the topic file** before proceeding: from `$TM_ROOT/packages/atlas-vault/`, run `uv run python schema.py <vault-root>/atlas/{theme-dir}/{slug}.md`. If validation fails, fix the file before continuing.
6. If a new theme is needed, create the theme directory under `<vault-root>/atlas/` and add a theme file at `<vault-root>/themes/{slug}.md`. The topic file created in step 4 is sufficient — no separate slug list to maintain.

## 7b. Confirm vault transport

The Markdown file written in 7a is already the canonical Atlas entry. Syncthing transports the Research Vault between managed machines; no client-specific Atlas push command is involved. Verify the file exists at the resolved vault path and use only valid Methods values from `atlas-schema.md`. If the vault is unavailable, stop this phase and report incomplete state rather than writing a second copy elsewhere.

## 7b2. Create Vault Submission Entry (MANDATORY)

**Always create a submission entry — regardless of topic status (even Idea stage).** This makes the topic visible to taskflow MCP queries, deadline tracking, and portfolio views.

Write `<vault-root>/submissions/{slug}.md`:

```yaml
---
title: <full paper title from interview>
type: submission
paper: '[[{slug}]]'
venue: '[[{target venue}]]'
status: <matches atlas topic status, e.g. Idea>
year: null
deadline: <if known from interview, else null>
notification_date: null
conference_date: null
location: ''
---

<one-line summary of the project and co-authors>
```

The body is a free-form prose paragraph — **no `## Notes` heading**. This matches the convention used for venue files in the vault: short content sits inline below the frontmatter; `## Sub-section` headings are reserved for genuinely structured content (multi-paragraph entries, distinct topics).

**Never skip this step.** A topic without a submission entry is invisible to the pipeline.

## 7c. Create Project Folder

Create the project directory under the research projects root:

```bash
RESEARCH_ROOT="$(cat ~/.config/task-mgmt/research-root)"
mkdir -p "$RESEARCH_ROOT/{ThemeAbbrev}/{slug}"
```

Theme abbreviations: T1, T2, T3, T4, T5, T6, T7, T8, T9, T10 (define your own theme codes). Folder name must be the kebab-case slug (same as the atlas topic filename).

## 7d. Regenerate RECAP.md

```bash
cd "$TM/packages/atlas-vault" && uv run python generate_recap.py
```

## 7e. Update Atlas Counts

If topic or theme count changed, update `$TM/packages/atlas-vault/CLAUDE.md` topic/theme counts and theme directory listing.

## Atlas Defaults

| Setting | Default | Override |
|---------|---------|---------|
| Status | `Idea` | User specifies |
| Priority | `Medium` | User specifies |
| Data Availability | `None` | User specifies |
| Feasibility | `Medium` | User specifies |
| Institution | Infer from theme/co-author | User specifies |

---

## Never Do These (Atlas Anti-Patterns)

These five anti-patterns silently break atlas tooling. Each has caused at least one prior incident.

- **Never create a topic file without YAML frontmatter** — it breaks `RECAP.md` generation.
- **Never hard-code vault theme paths** — always look them up. They change if recreated and the hard-coded path goes stale.
- **Never use Methods values outside the valid multi-select options** — the API will reject the entry. Valid values live in [`atlas-schema.md`](atlas-schema.md).
- **Never use venue or output names as slugs** — the slug names the **research idea**, not where it's submitted. `facct-paper` is wrong; `dark-patterns-ai-safety` is right.
- **Never create a separate topic file for a companion paper of an existing idea** — add it as an output on the existing topic. One idea, one topic file, multiple outputs.
