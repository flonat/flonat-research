# Quality Rubric: LaTeX Auto-Fix

> Scoring rubric for `/latex`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Compilation fails after 5 fix iterations | -100 | No PDF produced |
| PDF produced but with fatal rendering errors (blank pages, missing content) | -100 | Output is unusable |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Unresolved `\cite{}` — `??` or `[?]` in output | -15 | Per unique broken citation key |
| Unresolved `\ref{}` — `??` in output | -15 | Per unique broken reference |
| Auto-fix changed user intent (e.g., wrong citation key substituted) | -25 | Per instance — silent corruption |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Overfull hbox > 10pt remaining | -5 | Per instance |
| Missing `.latexmkrc` or incorrect `$out_dir` config | -10 | Build hygiene failure |
| Stale auxiliary files causing warnings | -5 | Should have been caught by cache clean |
| Package added but not strictly necessary | -5 | Per unnecessary package |
| Cited keys in `.tex` not found in `.bib` (audit) | -8 | Per missing key |
| Unused keys in `.bib` (audit, >20% unused) | -5 | Once for the pattern |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Overfull hbox 1-10pt | -2 | Per instance |
| Underfull hbox/vbox warnings | -1 | Per instance, cap at -10 |
| Font substitution warnings | -2 | Per unique substitution |
| Multiple compilation iterations needed (>2) | -1 | Per extra iteration beyond 2 |

## Source Pathologies (Phase 4)

Findings from the visual-fragility source lint. Full detector definitions in [`source-pathologies.md`](source-pathologies.md). All are report-only deductions; Pattern 1 has an opt-in auto-fix the user accepts manually.

| Pattern | Tier | Deduction |
|---------|------|-----------|
| 1. Spacing hacks fighting global spacing | Major | -5 per affected block (titlepage, center, etc.) |
| 2. Manual vertical-rhythm surgery (body) | Moderate | -1 per instance, cap at -5 |
| 2. Manual vertical-rhythm surgery (body, >5 instances) | Major | additional -5 once |
| 3. Line breaks as layout engine (inside section/caption) | Major | -5 per instance |
| 3. Line breaks as layout engine (inside titlepage) | Moderate | -2 per instance |
| 4. Forced-float carpet bombing (≤3 instances) | Minor | -1 once |
| 4. Forced-float carpet bombing (>3 instances) | Moderate | -3 once |
| 5. Shrink-to-fit table/figure (`\resizebox` to `\textwidth`) | Major | -5 per instance |
| 6. Tiny-table typography hacks | Moderate | -2 per cluster |
| 6. Tiny-table typography hacks (multiple symptoms in one table) | Major | -5 per cluster |
| 7. Absolute / overlap positioning outside math | Major | -3 per instance, cap at -10 |
| 8. Fixed-width layout assumptions (`p{Xcm}`, `minipage{Xcm}`) | Moderate | -1 per instance, cap at -5 |
| 9. Label-before-caption inside floats | Major | -5 per instance |

## External-Tool Findings (Phase 4)

| Source | Deduction | Notes |
|--------|-----------|-------|
| `chktex` warning (`-q -n8 -n44`) | -1 per unique warning | Cap at -10 |
| `latexindent -k` non-zero exit | -3 once | Source-cleanliness smoke test failure |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Pre-flight config | Phase 1 |
| Compilation errors | Phase 2 |
| Auto-fix quality | Phase 2 (fix accuracy) |
| Remaining warnings + box report | Phase 3 |
| Source pathologies + external-tool findings | Phase 4 |
| Citation audit | Phase 5 |
