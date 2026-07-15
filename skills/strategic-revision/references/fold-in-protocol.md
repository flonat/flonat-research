# Fold-in protocol — second-review extension of an existing DAG

> Companion to the main 11-phase protocol in `phases.md`. Use when a paper that already has a `strategic-revision` package receives a **second independent review** and you want to extend the existing DAG rather than start over.

## When to invoke

Trigger the fold-in path when **all** of the following hold:

- The paper has an existing `strategic-revision` output directory (`correspondence/referee-reviews/{venue}-round{n}/` or `docs/{venue}/internal-reviews/<source>-<date>/`) containing at least one `plan/revision_tasks*.json` (versioned `v1`, `v2`, …).
- A new review report exists — journal referee report, AI self-review, co-author critique, conference discussant notes, blindspot agent output, peer-reviewer agent output, anything substantive.
- The new review covers the same paper at roughly the same draft state. (If the draft has changed materially since v1, fold-in is the wrong path — re-run from Phase 1 instead.)

Skip when the new review is purely editorial polish on a paper whose existence-of-equilibrium / identification / scope foundations are already settled. Fold-in pays off when the second pass attacks load-bearing structure.

## Why fold-in instead of re-running Phase 1

Re-running the full skill loses the v1 verification trail (which findings you already checked against the `.tex` source, which converted to DISAGREE, which got Coaching positions). Fold-in **preserves** that trail and adds the second review as a versioned extension. The DAG itself is the durable artifact; reviews are the inputs that grow it.

## Versioning convention

| File | v1 (initial) | vN (after fold-in N−1) |
|---|---|---|
| Task definitions | `plan/revision_tasks.json` | `plan/revision_tasks-v2.json`, `-v3.json`, … |
| Validator output | `plan/revision_dag_analysis.json` | `plan/revision_dag_analysis-v2.json`, … |
| Master plan | `plan/REVISION_MASTER_PLAN.md` (one file, **addendum-appended**) | same file, new "v{N} Addendum" section at the end |
| Comment tracker | `analysis/comment-tracker.md` (one file, **addendum-appended**) | same file, new "v{N} Addendum" section at the end |
| Review analysis | `analysis/review-analysis.md` (one file, **section-appended**) | same file, new "v{N} cross-review picture" section |
| Per-review markdown | `reviews/<source-N>.md` (one per review) | same convention; one new file per fold-in |
| Source PDFs/MDs | `reviews-original.*` or `review-original-<source>.*` | preserved alongside |

**Never overwrite v1 files.** The provenance of which finding came from which review at which time is the entire point. The authoritative working task set is the highest-numbered `revision_tasks-v*.json`; older versions are reference.

## Step-by-step

### Step 1 — Detect the existing package

Find the latest version of the DAG:

```bash
ls plan/revision_tasks-v*.json plan/revision_tasks.json 2>/dev/null
# Pick the highest N. Read it.
# Also read plan/REVISION_MASTER_PLAN.md and analysis/comment-tracker.md for the
# established SourceID conventions (e.g., 'R1.a1' vs 'OF1' vs 'C12').
```

### Step 2 — Ingest the new review

Apply Phases 2–3 of the main protocol to the new review only:

- Write `reviews/<source-N>.md` — faithful structured transcription preserving the review's own numbering, with math in `\(...\)` form per `markdown-math-delimiters.md`.
- Skip Phase 4 (LaTeX verbatim transcription) **unless** there is a co-author who reads on paper and the source has OCR / formatting that would garble in markdown. For single-author papers with a clean digital source, the structured Phase 3 file is sufficient. (Adapted from real-session experience: standalone `.tex` verbatim adds friction with no reader.)

### Step 3 — Atomic parse + classification (Phases 5–6 on the new review)

Apply Phases 5–6 only to the new findings. **SourceIDs for new findings must not collide with v1.** Prefix with a reviewer label that identifies the new source — e.g. v1 used `R1.a1, OF1, C12`; v2 fold-in uses `R2.M1, R2.M5, R2.m1` for referee2 Majors/Minors. Convention: pick a stable short prefix per review (`R2`, `EiC2`, `BS` for blindspot, `PC` for paper-critic, etc.).

### Step 4 — Triage every new finding against the existing DAG

This is the heart of the fold-in. For each new atomic finding, classify on a **second axis** (independent of the 5-cat × R&R routing):

| Disposition | When | Action |
|---|---|---|
| **OVERLAP** | The existing v1 task already covers the substantive concern (possibly under a different name) | Note in the cross-review picture as confirming evidence; **do not** create a new task; **do not** edit the existing task |
| **MERGE** | The existing task is in the right area but the new finding refines, extends, or sharpens it | Edit the existing task's `description` to absorb the new requirement; record the merge in the v{N} addendum |
| **NEW** | The new finding identifies a load-bearing concern no v1 task addresses | Create a new task with a fresh ID, proper block assignment, `depends_on`, and `collateral_risks` |

A finding can also be **DISAGREE** (the reviewer is wrong) — verify against the `.tex` per Phase 10 before deciding. Do not auto-fold disputed findings.

### Step 5 — Build `revision_tasks-v{N}.json`

Start from a copy of v{N−1}. Apply:

- For each **MERGE**: rewrite the affected task's `description` (preserve `category`, `block`, `depends_on` unless the merge genuinely re-blocks it).
- For each **NEW**: add a task block following `task-schema.md`. Assign:
  - `category` per the 5-cat axis (Phase 6, axis 1)
  - `block` per the standard A/B/C/D/E sequence (Phase 9)
  - `depends_on` — read the existing tasks carefully; new root-level concerns may add edges into the lowest-block tasks (which is *fine* — they become new Block A roots), and new mid-stream concerns may insert into Block C or D
  - `collateral_risks` for cross-cutting effects on existing tasks

### Step 6 — Re-validate

```bash
uv run --with networkx python plan/dag_validator.py plan/revision_tasks-v{N}.json \
    --output plan/revision_dag_analysis-v{N}.json
```

Read the new output. Compare to v{N−1}:

- Did the **critical path** change? (Often yes — a new Block A root with high out-degree can reshape the longest chain.)
- Did the **bottleneck ordering** change? (Track shifts; new tasks can push existing bottlenecks down.)
- Did any **block boundaries** invert? (A Block C task now depending on a Block D task is a structural problem — fix the dependency or re-block.)
- Did total task count and dep count both go up sensibly? (A fold-in that adds 5 tasks and 0 deps is suspicious — new tasks usually slot into the dependency graph.)

### Step 7 — Append addendums (never rewrite v1)

**`plan/REVISION_MASTER_PLAN.md`** — append a single `# v{N} Addendum — <source-N> fold-in (<date>)` section at the end. Cover:

- Source + provenance of the new review (one line + link to the report file)
- **Cross-review picture** — overlap vs new angles between v{N−1} and v{N}; explicitly state whether either review is a *superset* of the other (often neither is — the union is the real picture)
- Mapping table: which new findings map to OVERLAP / MERGE / NEW
- v{N} computational results (machine-validated): task count, dep count, batch count, critical path, bottleneck shifts
- If the critical path changed, state both the old and the new and why
- If a new GO/NO-GO surfaces (e.g., two root decisions must be made jointly), name it explicitly

**`analysis/comment-tracker.md`** — append a `## v{N} Addendum — <source-N> fold-in (<date>)` section. Cover:

- New task rows in the same format as the v1 table (SourceID, Quote, Atomic Task, Category, Routing, Priority, Verify?)
- Merged-task note: list v1 task IDs whose descriptions changed, with one-line rationale
- Updated summary counts (Category / Routing / Priority — v{N} totals, not deltas; clearer to read)
- Phase 10 verification: which Verify? Y tasks were checked against the `.tex` for this fold-in; verdict per task

**`analysis/review-analysis.md`** — append a v{N} cross-review picture section if the submission decision changes. The original Strategy A / Strategy B / Recommendation should be revised in light of the new review, not silently replaced.

**`revision-log.md`** (if it exists) — add rows for any new Block A roots (they're the most likely to be acted on first).

### Step 8 — Stamp the new review independently

Run the review-state-log helper for the new review's report file (per `rules/stamp-after-review-dispatch.md` if dispatched to a sub-agent, or directly otherwise). The fold-in *does not* re-stamp v1 — that row stays in `reviews/INDEX.md` exactly as written. The new review gets its own row.

## Cross-review picture — what to write

The cross-review picture is the most valuable output of a fold-in. It is *not* a synthesis (don't merge prose) — it is a **disposition table** plus a short narrative answering:

1. Where do the two reviews **agree**? (Overlap is genuine confirmation — the issue is real, two independent readers found it.)
2. Where does each review hit angles the other **missed**? (List explicitly. This is where the union beats either review alone.)
3. Is either review a **superset** of the other? (Usually no. Stating "neither is a superset" is meaningful — it means the union is the real pre-submission picture.)
4. What changed in the **action sequence**? (Critical path, GO/NO-GO gates, block boundaries.)

Keep this to one screen of text. The detail lives in the comment tracker; the picture lives here.

## When the new review changes the submission decision

If v1 said "hold submission" and v{N} confirms it from a new angle, the decision is unchanged but the *rationale* is now broader (two independent surfaces). State this.

If v1 said "submit" and v{N} reveals a new defect, the decision shifts to "hold". This is the most important fold-in outcome to surface clearly — in the master plan addendum *and* in any project-level status (project `CLAUDE.md`, atlas topic, focus file).

If v1 said "hold" and v{N} only finds polish issues, the recommendation may upgrade to "minor revision and submit". Rare for substantive fold-ins; common for an editorial pass.

## What fold-in does NOT do

- **Does not re-verify v1 findings.** The Phase 10 verification trail from v1 is preserved as-is. Only new findings get verified.
- **Does not edit v1 task IDs, categories, or block assignments** (only descriptions, via MERGE). Renaming tasks across versions destroys traceability.
- **Does not write the response letter** — same as the base skill.
- **Does not re-stamp v1 in INDEX.md.** The new review gets its own stamp; v1's row stays.
- **Does not delete v{N−1} files.** The lineage is the point.

## Common patterns

- **Adversarial second-pass on an AI self-review.** v1 = `refine.ink` AI self-review processed → v2 = `referee2-reviewer` grounded mode folded in. Catches what an AI tool may miss (e.g., structural assumptions a tool doesn't model). Real example: 2026-06-08/10 on the JTP responsive-media paper.
- **Co-author critique on a paper-critic-driven v1.** v1 = `paper-critic` agent → v2 = co-author's marked-up PDF folded in. Co-author often catches positioning/narrative issues an agent misses.
- **Conference discussant on a journal-referee-driven v1.** v1 = journal R&R round 1 → v2 = conference discussant notes after a presentation. Discussant often raises framing issues that won't surface in writing-only review.

In all three patterns, the value of fold-in is preserving the v1 work while making the *union* of findings the operational object.
