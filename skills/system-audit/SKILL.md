---
name: system-audit
description: "Use when you need to run parallel audits across skills, hooks, agents, rules, and conventions."
allowed-tools: Bash(ls*), Bash(readlink*), Bash(wc*), Bash(git*), Bash(test*), Bash(stat*), Bash(find*), Read, Glob, Grep, Task
argument-hint: "[no arguments — runs full sweep]"
---

# Maintenance Sweep

> System-wide health check using agnix lint + 7 parallel sub-agents. Produces a consolidated report at `log/audits/system-audit-YYYY-MM-DD.md`. **Report-only — never modifies any files.**

## When to Use

- Periodic system hygiene (monthly or after major changes)
- When the user says "maintenance sweep", "system health check", "audit my setup"
- After adding/removing skills, hooks, agents, or rules
- Before presenting the system to others (ensure everything is consistent)

## Overview

1. **Lint** — run `npx agnix .` to validate skills, hooks, agents, and CLAUDE.md
2. **Dispatch** — launch 7 sub-agents in parallel via the Task tool
3. **Collect** — gather each sub-agent's findings
4. **Consolidate** — merge lint results + sub-agent findings into a single timestamped report
5. **Present** — show key findings to the user

**Python:** Always use `uv run python` or `uv pip install`. Never bare `python`, `python3`, `pip`, or `pip3`. Include this in sub-agent prompts.

## Autonomy

Per the global `--autonomous` / `-y` convention in `~/.claude/rules/phased-work.md` § "Autonomy flag convention". Invoke as `/system-audit --autonomous` (or `-y`). When set:

- **No inter-phase pauses** — Lint → Dispatch → Collect → Consolidate → Present chain end-to-end.
- **No `AskUserQuestion` mid-run** — sub-agent count defaults to 7 (the standard fan-out), all sub-agents launch in parallel without confirmation.
- **No interim "review and continue" pauses** between dispatch and consolidation.
- **Sub-agent forbid-list still applied** — all 7 sub-agents are read-only (no edits to skills/hooks/agents/rules during the audit).
- **Report-only invariant preserved** — `--autonomous` does NOT change the skill's read-only nature; it only suppresses confirmation prompts. No fixes are ever applied.
- **Single end-of-run report** at `log/audits/system-audit-YYYY-MM-DD.md` is the only mandatory user-facing output.

This is one of the safer skills to run autonomously — it's read-only by design, sub-agents have no write access to the system, and the output is a single timestamped report that you can review afterward. Recommended for scheduled monthly runs via `/scheduled-job`.

Recommended invocations:

```
/system-audit --autonomous                              # full sweep, end-to-end
/system-audit -y                                        # short form
```

---

## Phase 0: Pre-flight Lints

Two fast lint passes run in the main context before sub-agent dispatch. Both are summary-only — full findings feed into the final report.

### 0.1 agnix lint

Run `npx agnix .` and capture the summary line.

**Pass criteria:** 0 errors. Warnings are informational only.

If errors > 0, list them in the report under an **agnix Lint** section. These are structural issues in skill/hook/agent frontmatter that should be fixed.

Config lives in `.agnix.toml` at project root — known false positives are already suppressed.

### 0.2 skill-numbering lint

Run `uv run python scripts/lint-skills.py` and capture the summary line.

**Pass criteria:** 0 findings. Findings indicate phase-numbering smells, frontmatter typos, or stale cross-skill phase references. Reference: [`skills/_shared/skill-template.md`](../_shared/skill-template.md) § Anti-patterns.

If findings > 0, list them in the report under a **Skill-Numbering Lint** section. The linter explains each rule (R1–R9) inline.

### 0.3 review-agent logger-gate lint

Run:

```bash
grep -E "^After producing (DOMAIN-REVIEW|CODE-REVIEW|your verdict|your referee|the verification)" .claude/agents/*.md
```

**Pass criteria:** 0 matches. Any match means a review-agent definition is using the stale/fragile logger-gate intro pattern that was fixed by the 5-agent patch (commit `23ebcfff`, 2026-05-17). The fragile pattern conditions the `review-state-log.sh` call on producing a stale top-level filename (`DOMAIN-REVIEW.md`-style) or a soft generic phrase (`"your verdict"`, `"the verification"`); when orchestrators like `/review-cluster` send "Return findings as a structured list, NOT a file write", the gate fails and the helper never fires — leaving a logger gap detectable by `/review-recap`.

If matches > 0, list them in the report under a **Review-Agent Logger-Gate** section with the suggested replacement intro:

> Write [your <X> report] to `reviews/<source-slug>/<YYYY-MM-DD-HHMM>.md` (`mkdir -p reviews/<source-slug>/` first). Then append a row to the project's `REVIEW-STATE.md` so `/review-recap` can render the run. Use the shared helper:

Reference pattern: see `paper-critic.md` line ~432 (already patched).

---

## Phase 1: Dispatch Sub-Agents

Launch all 7 in a single message using parallel Task tool calls. Each sub-agent is `subagent_type: Explore`.

**Context overflow prevention:** Instruct each sub-agent to keep its returned output concise — summary tables and key findings only (under 500 words). If detailed findings are large, the sub-agent should write them to a temp file (e.g., `/tmp/system-audit/sa-N.md`) and return only the file path + summary.

All sub-agents receive shared context (Task Management root, research projects root, category directories). Full shared context block and all 6 sub-agent prompt templates:

**[references/sub-agent-prompts.md](references/sub-agent-prompts.md)**

Sub-agents at a glance:

| # | Name | What it checks |
|---|------|---------------|
| 1 | Inventory Auditor | Skill/hook/agent/rule counts, symlinks, MCP alignment |
| 2 | Bibliography & Project Hygiene | .bib files, naming, MEMORY.md presence |
| 3 | Convention Compliance | LaTeX out/, Overleaf separation, Python env, git health |
| 4 | Documentation Freshness | Stale counts, broken links, .context/ freshness |
| 5 | Ecosystem Health | MCP server refs, staleness, orphans, CLI tools |
| 6 | Skill Quality & Overlap | Bloat, staleness, cross-component overlap |
| 7 | Friends Repo Health | Skill/rule freshness vs upstream, anonymisation, install script |

---

## Phase 2: Collect and Consolidate

After all 7 sub-agents return, merge their findings into a single report.

### Report Template

Write to `log/audits/system-audit-YYYY-MM-DD.md`:

```markdown
# Maintenance Sweep — YYYY-MM-DD

## Dashboard

| Area | Status | Issues |
|------|--------|--------|
| agnix Lint | <OK/WARN/FAIL> | <count> |
| Inventory | <OK/WARN/FAIL> | <count> |
| Bibliography & Projects | <OK/WARN/FAIL> | <count> |
| Conventions | <OK/WARN/FAIL> | <count> |
| Documentation | <OK/WARN/FAIL> | <count> |
| Ecosystem Health | <OK/WARN/FAIL> | <count> |
| Skill Quality & Overlap | <OK/WARN/FAIL> | <count> |
| Friends Repo Health | <OK/WARN/FAIL> | <count> |

## agnix Lint
<Phase 0 results: error count, warning count, any specific errors>

## Inventory Audit
<Sub-agent 1 findings>

## Bibliography & Project Hygiene
<Sub-agent 2 findings>

## Convention Compliance
<Sub-agent 3 findings>

## Documentation Freshness
<Sub-agent 4 findings>

## Ecosystem Health
<Sub-agent 5 findings>

## Skill Quality & Cross-Component Overlap
<Sub-agent 6 findings>

## Friends Repo Health
<Sub-agent 7 findings>

## Recommended Actions
<Prioritised list of things to fix, grouped by effort level>

### Quick Fixes (< 5 min each)
- ...

### Medium Effort (5–30 min)
- ...

### Larger Tasks (> 30 min)
- ...
```

---

## Phase 3: Present

Show the user:
1. The dashboard table
2. Any FAIL-status areas with specifics
3. The quick fixes list
4. Ask if he wants to address any issues now

---

## Error Handling

- **Sub-agent timeout:** If a sub-agent doesn't return, note "timed out" in the report and continue with the others.
- **Missing directories:** If a category folder is empty or doesn't exist, note "no projects found" rather than erroring.
- **Permission issues:** If files can't be read, note "access denied" and continue.

## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| `/bib-validate` | Run on projects flagged by the Bibliography Hygiene sub-agent |
| `/audit-project-research` | Complements Convention Compliance with deeper per-project checks |
| `/update-project-doc` | Fix documentation staleness found by Documentation Freshness |
| `/sync-permissions` | Fix symlink issues found by Inventory Auditor |
| `/atlas-audit` | Full cross-system audit (local + vault + Paperpile + pipeline) — deeper than this sweep |
| `/insights-deck` | Maintenance findings can feed into system insights presentations |
| `/repo-doc-audit friends` | Dedicated deep audit for friends-repo — Sub-agent 7 is a quick health check; the audit skill is the full version |
| `/sync-friends-repo` | Fix freshness issues found by Sub-agent 7 |
