---
name: proofread
description: "Proofread a LaTeX academic paper across eleven language, notation, citation, and consistency categories. Use when the requested task is bounded proofreading rather than substantive rewriting, clarity stress-testing, or venue compliance."
allowed-tools: Read, Glob, Grep
argument-hint: "[project-path or tex-file]"
skill-dependencies: [devils-advocate]
---

# Academic Proofreading

**Report-only skill.** Never edit source files — produce `reviews/<scope>/proofread/<YYYY-MM-DD-HHMM>.md` only (where `<scope>` is the paper slug, e.g. `paper-jtp`).

## Output Path

Per `rules/review-artefact-routing.md` (auto-loads in research projects (path-scoped to `paper-*/` and `paper/`)):

- **Source slug:** `proofread`
- **Write reports to:** `reviews/<scope>/proofread/YYYY-MM-DD.md` inside the project, where `<scope>` is the paper slug (e.g., `paper-jtp`). Path is relative to the research project root, not the Task-Management repo.
- **Never** at project root (`./CRITIC-REPORT.md`-style filenames are forbidden — pre-rule layout).
- **Idempotency:** if today's file exists, append a same-day descriptor (`{date}-revision.md`, `{date}-r2.md`, `{date}-pre-submission.md`) — never overwrite.
- **Index update:** if `reviews/INDEX.md` exists, write a one-line entry under "Latest per source" pointing at the new file. Otherwise `review-recap` will rebuild the index next time it runs.
- **Infrastructure repos** (Task-Management, atlas-workspace, etc.): this section does not apply — the path-scoped rule won't load there.


## When to Use

- Before sending a draft to supervisors
- Before submission to a journal/conference
- After major revisions to check consistency
- When you want a fresh-eyes check on writing quality

## When NOT to Use

- **Formal audits** — use the Referee 2 agent for systematic verification
- **Argument quality** — use `devils-advocate` for logical scrutiny
- **Citation completeness** — use an installed bibliography validator or direct cite-key cross-referencing (this skill flags only obvious citation-format issues)

## Workflow

1. **Locate files**: Find all `.tex` files in the project (and `.log` files for LaTeX diagnostics)
2. **Read the document**: Read all `.tex` source files in order
3. **Run 11 check categories** (below)
4. **Produce report**: Write `reviews/<scope>/proofread/<YYYY-MM-DD-HHMM>.md` under the project directory (where `<scope>` is the paper slug, e.g., `paper-jtp`; create the directory if it does not exist: `mkdir -p reviews/<scope>/proofread/`). Do NOT overwrite previous reports — each review is timestamped to the minute. Canonical convention: the installed shared resource `shared/review-state-schema.md`.

## Check Categories

Eleven categories, run in order. Full catalogue — every bullet, threshold, and worked example — in [`references/check-categories.md`](references/check-categories.md):

| # | Category | # | Category |
|---|----------|---|----------|
| 1 | Grammar & Spelling | 7 | TikZ Diagram Review |
| 2 | Notation Consistency | 8 | Numeric Text↔Table Cross-Check |
| 3 | Citation Format | 9 | Causal Language Audit |
| 4 | Academic Tone | 10 | Equation Completeness |
| 5 | LaTeX-Specific Issues | 11a | Anonymity (double-blind venues only) |
| 6 | Citation Voice Balance | 11 | Preprint Staleness |

## Severity Levels

| Level | Definition | Example |
|-------|-----------|---------|
| **Critical** | Will be noticed by reviewers, may cause rejection | Broken references, major grammar errors, inconsistent core notation, text↔table number mismatch, causal overclaiming with weak design |
| **Major** | Noticeable quality issue | Inconsistent citation style, tone issues, overfull hbox > 10pt, undefined variable in equation, stale preprint, ambiguous "significant" |
| **Minor** | Polish issue | Occasional British/American mix, minor spacing, missing equation number for referenced equation |

## Quality Scoring

Apply numeric quality scoring using the shared framework and skill-specific rubric:

- **Framework:** [`../shared/quality-scoring.md`](../shared/quality-scoring.md) — severity tiers, thresholds, verdict rules
- **Rubric:** [`references/quality-rubric.md`](references/quality-rubric.md) — issue-to-deduction mappings for this skill

Start at 100, deduct per issue found, apply verdict. Insert the Score Block into the report after the summary table.

## Recurring Pattern Grouping

When the same issue appears 3+ times, **group it as a single pattern finding** instead of listing each instance separately. This prevents reports bloated with 50 individual items when the real message is "you have 3 recurring problems."

**Format:**
```
### M3: Hedge phrase "interestingly" (8 instances)
- **Category:** Academic tone
- **Locations:** lines 42, 67, 103, 145, 189, 203, 267, 301
- **Problem:** Filler hedge phrase adds no content
- **Fix:** Delete all 8 instances
```

One deduction for the pattern (not 8 separate deductions). Escalation still applies: 5+ instances of the same minor issue → one Major deduction.

## Report Format

```markdown
# Proofread Report

**Document:** [filename]
**Date:** YYYY-MM-DD
**Pages:** [approximate]

## Summary

| Category | Critical | Major | Minor |
|----------|----------|-------|-------|
| Grammar & spelling | 0 | 0 | 0 |
| Notation consistency | 0 | 0 | 0 |
| Citation format | 0 | 0 | 0 |
| Academic tone | 0 | 0 | 0 |
| LaTeX-specific | 0 | 0 | 0 |
| Citation voice balance | 0 | 0 | 0 |
| TikZ diagrams | 0 | 0 | 0 |
| Numeric cross-check | 0 | 0 | 0 |
| Causal language | 0 | 0 | 0 |
| Equation completeness | 0 | 0 | 0 |
| Preprint staleness | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** |

## Critical Issues

[List each with file, line/section, and specific issue]

## Major Issues

[List each with file, line/section, and specific issue]

## Minor Issues

[List each with file, line/section, and specific issue]

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | Ship / Ship with notes / Revise / Revise (major) / Blocked |

### Deductions

| # | Issue | Tier | Deduction | Category |
|---|-------|------|-----------|----------|
| 1 | [description] | [tier] | -X | [category] |
| | **Total deductions** | | **-XX** | |

## Recommendations

[Optional: overall observations about the writing — prioritise fixes by deduction size]
```

## Council Mode (Optional)

For high-stakes pre-submission checks, run in council mode — 3 LLM providers independently run the 7 check categories, cross-review, and a chairman synthesises one `PROOFREAD-REPORT.md`. **Trigger:** "council proofread" / "thorough proofread". Full orchestration + invocation: [`../shared/council-protocol.md`](../shared/council-protocol.md).

**Value:** Diminishing returns for pure formatting — most valuable combined with citation-voice-balance and notation-consistency checks, where different models have genuinely different pattern recognition.

## Log to REVIEW-STATE.md (final step)

After writing the proofread report, append a row to the project's `REVIEW-STATE.md`:

```bash
bash <skills-root>/_shared/review-state-log.sh \
  --check proofread \
  --paper "<paper-{venue} dir>" \
  --verdict "<PASS|ISSUES FOUND>" \
  --open-issues "<total-issues-across-categories>/<total-issues-across-categories>" \
  --report "reviews/<scope>/proofread/<YYYY-MM-DD-HHMM>.md" \
  --notes "<one-line: e.g. '3 critical, 12 minor; mostly notation §3'>" \
  [--trigger "pre-submission-report|review-cluster"]
```

- Verdict: PASS if no issues found across any category; ISSUES FOUND otherwise.
- Open issues: total count across all 7 (or 11) check categories at run time.
- Trigger: pass orchestrator name only if invoked via `pre-submission-report` or `review-cluster`. Otherwise omit.

Schema: the installed shared resource `shared/review-state-schema.md`.

**Source format.** Paper prose stays one line per paragraph; normalize edited files with `.scripts/latex_paragraph_format.py --apply` and recompile. Canonical: `rules/latex-source-format.md`.

## Cross-References

- **Installed bibliography validator** — For thorough bibliography cross-referencing and metadata checks
- **`latex`** — For compilation and error resolution (run before proofreading to ensure the document compiles cleanly)
- **Referee 2 agent** — For formal code + paper auditing
- **`devils-advocate`** — For argument quality and logical scrutiny
