# R&R Comment Tracker — {{PAPER_TITLE}}

## Triage Summary

| Field | Value |
|-------|-------|
| Venue | {{VENUE}} |
| Manuscript | {{PAPER_TITLE}} |
| Round | Revision {{ROUND}} |
| Date received | {{DATE_RECEIVED}} |
| Response deadline | {{DEADLINE}} |
| Coordinating author | {{LEAD_AUTHOR}} |

## Comment Matrix

| ID | Reviewer | Comment (verbatim) | Type | Priority | Action | Owner | Status | Section |
|----|----------|--------------------|------|----------|--------|-------|--------|---------|
| R1-C1 | R1 | "..." | Major | High | | | Pending | |

**Type:** Major / Minor / Editorial / Question / Praise
**Priority:** Critical / High / Medium / Low
**Status:** Pending / In progress / Ready for QA / Done / Won't fix

## Evidence & Provenance Log

> Link each response claim to the script/output/data that supports it.
> Optional for non-empirical papers.

| Comment ID | Script / notebook | Data input | Model / spec | Output artifact(s) | Key finding | Reproducible |
|------------|-------------------|------------|--------------|---------------------|-------------|--------------|
| | | | | | | |

## Manuscript Patch Plan

> Track text changes to be applied in Overleaf. One row per location changed.

| Comment ID | Section / location | Current claim | Proposed revision | Linked evidence | Applied (Y/N) | Date |
|------------|-------------------|---------------|-------------------|-----------------|---------------|------|
| | | | | | | |

## Fulfillment Ledger (close-out)

> Filled at close-out, before the response letter is finalised. Verify each
> commitment **against the manuscript** (read/grep the actual `.tex`), never on
> the response letter's or this tracker's say-so. Exception:
> `acknowledgment_only` commitments (no manuscript change promised) — their
> evidence IS the letter text. (Ported from academic-research-skills v3.19
> commitment ledger, 2026-07-24.)

| Comment ID | Commitment (what the response promises) | Fulfillment | Manuscript evidence (section / lines) | Unfulfilled rationale | Residual action |
|------------|------------------------------------------|-------------|----------------------------------------|-----------------------|-----------------|
| | | | | | |

**Fulfillment:** fulfilled / partial / not_fulfilled / acknowledgment_only
— `partial` and `not_fulfilled` REQUIRE both a rationale and a residual action; a blank rationale is not an option.

## Response Letter Draft Blocks

> One block per substantive comment. Use this template:

<!--
### R{n}-C{m}: [short label]

We thank the reviewer for [summary]. We addressed this by [action]. Specifically, [details]. This is reflected in [section/table/figure].

Evidence:
- [artifact 1]
- [artifact 2]

Residual limitations (if any):
- [limitation]
-->

## QA Checklist

- [ ] Every reviewer comment has an ID in the matrix
- [ ] Every Critical/High comment has a response block drafted
- [ ] Every response block links to at least one concrete artifact
- [ ] No response overstates evidence or omits uncertainty
- [ ] Manuscript text, tables, and response letter are numerically consistent
- [ ] All changed analyses are reproducible from scripts in code/
- [ ] All Overleaf-applied changes are marked Y in the patch plan
- [ ] Every commitment has a Fulfillment Ledger row verified against the manuscript (not the letter)
- [ ] No partial / not_fulfilled row is missing its rationale and residual action
- [ ] Response letter proofread by co-author

## Status Dashboard

| Metric | Value |
|--------|-------|
| Total comments | |
| Done | |
| In progress | |
| Ready for QA | |
| Pending | |
| Won't fix | |
| Critical/High open | |
| Blocked | |

## Blockers & Decisions

| Date | Blocker / decision needed | Impacted comment IDs | Proposed options | Owner | Resolution |
|------|--------------------------|---------------------|------------------|-------|------------|
| | | | | | |
