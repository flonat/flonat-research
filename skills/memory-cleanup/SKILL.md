---
name: memory-cleanup
description: "Use when you need to prune duplicates and merge overlapping entries in MEMORY.md files."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
argument-hint: "[project-path or 'all' for global consolidation]"
---

# Consolidate Memory

Periodic refinement of `MEMORY.md` files across projects. Prunes redundant entries, merges overlapping knowledge, generates higher-order abstractions from accumulated patterns, and removes stale or superseded entries.

Inspired by npcsh's knowledge graph sleep/dream cycles — memory consolidation applied to research project knowledge.

## When to Use

- Monthly maintenance (pair with `system-audit`)
- When a `MEMORY.md` exceeds 100 entries
- After completing a major project milestone (e.g., paper submission)
- When starting a new session and `MEMORY.md` feels cluttered
- When the same correction keeps appearing across multiple projects

## When NOT to Use

- During active work sessions — consolidation is a maintenance task
- When `MEMORY.md` has fewer than 10 entries — not enough to consolidate
- Immediately after recording `[LEARN]` tags — let knowledge accumulate first

## Modes

Ask the user which mode to run:

| Mode | Scope | What it does |
|------|-------|-------------|
| **Project** (default) | Project `MEMORY.md` + its portable `.context/auto-memory/<project-id>/` copy | Consolidate project knowledge and its shared continuity copy |
| **Global** | Portable memory for all manifest-discovered projects + Task Management | Consolidate all and cross-pollinate shared patterns |

## Workflow

### Phase 1: Sleep (Consolidation)

Resolve Task Management with `head -1 ~/.config/task-mgmt/path`, then read the
target `MEMORY.md` file(s) and their manifest-owned portable copies under
`$TM/.context/auto-memory/<project-id>/`. Use `config/ai-context.toml` and the
memory-status command as the source of project coverage; never reconstruct a
client's private cache path by hand.

#### 1.1 Duplicate Detection

Find entries that say the same thing in different words.

**Signals:**
- Same correction direction (wrong → right) with different phrasing
- Same file/variable referenced in multiple entries
- Entries from different dates that record the same learning

**Action:** Merge into a single entry, keeping the most precise wording. Note the merge in a comment: `<!-- merged from 2 entries -->`.

#### 1.2 Contradiction Resolution

Find entries that contradict each other (e.g., "use X" in one entry, "don't use X" in another).

**Signals:**
- Opposite correction directions for the same variable/convention
- Entries where a later one supersedes an earlier one

**Action:** Keep the most recent/correct entry. Flag contradictions for user review if the resolution isn't obvious.

#### 1.3 Staleness Detection

Find entries that are no longer relevant.

**Signals:**
- References to files, variables, or conventions that no longer exist in the project
- Entries about bugs that have been fixed
- Entries about tools or APIs that have changed
- Entries marked with dates older than 6 months with no recent reinforcement

**Action:** Mark as `[STALE?]` and present to user for confirmation before removing. Never auto-delete.

#### 1.4 Tier Routing Check

Check whether entries are in the correct tier (see `learn-tags` rule for the two-tier system).

**Promotion candidates** (portable project memory → project/global MEMORY.md):
- Entries that would help a collaborator or a different client
- Local workarounds that turned out to be general conventions
- Tool quirks that apply to all machines

**Local-only candidates** (remove from portable memory only with approval):
- Entries in `MEMORY.md` that reference local paths, machine-specific tool versions, or environment quirks
- Workarounds that only apply to this specific setup

**Action:** Present promotion/local-only suggestions to the user. Move or remove
entries only after explicit approval. Never copy machine-specific material into
the Git-synchronised portable tree.

#### 1.5 Strengthening

Entries that have been independently confirmed multiple times are high-confidence knowledge.

**Signals:**
- Same pattern recorded from different sessions
- Corrections reinforced by compilation errors or test failures
- Conventions confirmed by supervisor feedback

**Action:** Move to the top of their section. Add `[CONFIRMED]` marker if supported by 3+ independent occurrences.

### Phase 2: Dream (Abstraction)

Generate higher-order patterns from the accumulated entries.

#### 2.1 Cross-Entry Patterns

Look for patterns that span multiple entries:

- "Every time we work with X, we hit Y" → Record as a general rule
- "We always use convention A for project type B" → Record as a convention
- "Corrections in category C cluster around the same mistake" → Record the root cause

#### 2.2 Cross-Project Patterns (Global mode only)

When consolidating across all projects, look for knowledge that applies everywhere:

- Notation conventions used consistently across 3+ projects → Promote to global MEMORY.md
- The same code pitfall appearing in multiple projects → Record once with cross-references
- Citation corrections that apply to shared bibliography entries → Consolidate

#### 2.3 Abstraction Generation

For each pattern found, generate an abstraction:

```markdown
## Abstraction: [Name]

**Pattern:** [What keeps happening]
**Root cause:** [Why it happens]
**Prevention:** [How to avoid it in future]
**Evidence:** [Which entries support this]
```

Present abstractions to the user. Only write the ones they approve.

### Phase 3: Write

#### 3.1 Restructure

Rewrite `MEMORY.md` with:
1. **Abstractions** at the top (new section: `## Patterns`)
2. **Confirmed entries** next (high-confidence knowledge)
3. **Regular entries** in their standard sections (Notation Registry, Citations, Key Decisions, Anti-Patterns, Code Pitfalls)
4. **Stale entries removed** (only those confirmed by user)

Also rewrite the matching portable memory file when the user approved the same
consolidation there. Do not edit undocumented client-local cache files.

#### 3.2 Diff Report

Before writing, show a summary:

```markdown
## Consolidation Summary

| Action | Count |
|--------|-------|
| Duplicates merged | X |
| Contradictions resolved | X |
| Stale entries flagged | X |
| Stale entries removed | X (user-confirmed) |
| Entries strengthened | X |
| Abstractions generated | X |
| Promotions (portable project → project/global) | X |
| Local-only removals from portable memory | X |
| Cross-project promotions | X (global mode) |

### Entries Before: XX
### Entries After: YY
### Net reduction: ZZ
```

#### 3.3 Confirmation

**Always show the full proposed MEMORY.md before writing.** Wait for explicit approval. The user may want to keep entries flagged as stale, adjust abstractions, or revert merges.

### Phase 4: Converge Portable Memory

The client-neutral memory engine owns local/shared selection, newest-wins
convergence, conflict copies, privacy preflight, and tombstones. This skill may
edit approved canonical memory content and append explicit tombstones, but it
must never copy whole client directories or implement its own merge loop.

1. Resolve the engine:

   ```bash
   TM="$(head -1 "$HOME/.config/task-mgmt/path")"
   ENGINE="$TM/scripts/ai-context.py"
   ```

2. Before writing, require a clean read-only status:

   ```bash
   uv run --no-sync --project "$TM" python "$ENGINE" memory-status --json
   ```

   If it reports divergence, conflicts, missing metadata, or pending
   tombstones, stop and run the normal memory-sync workflow before editing.

3. Apply only the approved consolidation to the project `MEMORY.md` and/or the
   matching `$TM/.context/auto-memory/<project-id>/` files. A shared-only file
   is valid data from another machine, never evidence of deletion.

4. For an explicitly approved whole-file deletion, append that filename to the
   matching portable directory's `.tombstones` file with a dated comment. Do
   not infer tombstones from set differences, and do not delete conflict files.

5. Run the engine, then verify idempotence:

   ```bash
   uv run --no-sync --project "$TM" python "$ENGINE" sync-memory --json
   uv run --no-sync --project "$TM" python "$ENGINE" memory-status --json
   ```

   The second command must report `ok: true` and `pending: 0`. Review every
   generated `.conflict-<host>-<timestamp>` artifact; never delete one as part
   of the same run.

6. Commit approved changes under `.context/auto-memory/` through the normal Git
   workflow. Do not auto-commit from this skill.

## MEMORY.md Sections (Reference)

Standard sections from the `learn-tags` rule:

| Section | Columns |
|---------|---------|
| **Patterns** | Pattern / Root cause / Prevention / Evidence (NEW — added by this skill) |
| **Notation Registry** | Variable / Convention / Anti-pattern |
| **Estimand Registry** | What we estimate / Identification / Key assumptions |
| **Citations** | One-liner corrections |
| **Key Decisions** | Decision / Rationale / Date |
| **Anti-Patterns** | What went wrong / Correction |
| **Code Pitfalls** | Bug / Impact / Fix |

## Global MEMORY.md Location

The Task Management MEMORY.md at the project root:
```
$TM/MEMORY.md
```

Portable auto-memory is rooted at:
```
$TM/.context/auto-memory/
```

## Cross-References

- **`system-audit`** — Run consolidation as part of periodic maintenance
- **`skill-extract`** — Creates the entries that this skill consolidates
- **`[LEARN]` tags** (rule) — The tagging system that feeds MEMORY.md
- **`session-close`** — May surface entries worth recording before consolidation
