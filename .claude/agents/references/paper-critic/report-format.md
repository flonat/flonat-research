# Paper Critic — CRITIC-REPORT.md format

> Full markdown template for the `CRITIC-REPORT.md` artefact. Referenced by `paper-critic.md`.
>
> Write the report to `reviews/paper-critic/YYYY-MM-DD_CRITIC-REPORT.md` in the **project root** (the directory containing the `.tex` files, NOT the Task Management directory). Create `reviews/paper-critic/` if it does not exist. Do NOT overwrite previous reports — each review is dated. **Write this AFTER `findings.json` is finalised** (see `json-schema.md`).

## Template

```markdown
# Paper Critic Report

**Document:** [main .tex filename]
**Date:** YYYY-MM-DD
**Round:** [N — 1 for first review, increment for subsequent rounds]
**contract_id:** paper-critic/fixer/v1
**schema_version:** v1.0.0

## Verdict: APPROVED / NEEDS REVISION / BLOCKED

## Hard Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| Compilation | PASS / FAIL | [PDF found at out/X.pdf / No PDF in out/] |
| References | PASS / FAIL | [0 undefined / N undefined: list them] |
| Citations | PASS / FAIL | [0 undefined / N undefined: list them] |
| Page limit | PASS / FAIL / N/A | [X pages, limit is Y / no limit stated] |

## Quality Score

| Metric | Value |
|--------|-------|
| **Score** | XX / 100 |
| **Verdict** | [from framework: Ship / Ship with notes / Revise / Revise (major) / Blocked] |

### Deductions

| # | Issue | Tier | Deduction | Category | Location |
|---|-------|------|-----------|----------|----------|
| C1 | [description] | Critical | -15 | Notation | file.tex:42 |
| M1 | [description] | Major | -5 | LaTeX | file.tex:108 |
| m1 | [description] | Minor | -2 | Grammar | file.tex:15 |
| ... | | | | | |
| | **Total deductions** | | **-XX** | | |

## Critical Issues (MUST FIX)

### C1: [Short title]
- **Category:** [Grammar / Notation / Citation / Tone / LaTeX / TikZ / Internal Consistency / Tables & Figures]
- **Location:** `file.tex:line`
- **Problem:** [What is wrong]
- **Fix:** [Precise instruction for the fixer — what to change, not why]

### C2: ...

## Major Issues (SHOULD FIX)

### M1: [Short title]
- **Category:** [...]
- **Location:** `file.tex:line`
- **Problem:** [What is wrong]
- **Fix:** [Precise instruction]

### M2: ...

## Minor Issues (NICE TO FIX)

### m1: [Short title]
- **Category:** [...]
- **Location:** `file.tex:line`
- **Problem:** [What is wrong]
- **Fix:** [Precise instruction]

### m2: ...
```

## Notes

- The markdown CRITIC-REPORT.md uses human-readable tier names ("Critical"/"Major"/"Minor") in headings. The JSON `findings.json` (see `json-schema.md`) is rigid and uses single-letter codes (`C`/`M`/`m`).
- Both files must agree: same issue count, same IDs, same deductions, same quotes. If they diverge during authoring, `findings.json` is the source of truth.
- The `## Verdict:` line at the top must be parseable verbatim — no prose preamble, no ambiguity. Downstream contract-compliance check (D1) reads it directly.
