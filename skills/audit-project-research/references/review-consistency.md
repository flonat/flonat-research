# Phase 4.6: Review Process Consistency

> Detailed check for `audit-project-research` Phase 4.6.
> Canonical layout: `rules/submission-file-archive.md` § "per-round folder". Retrofit tool: the `tidy-project-reviews` skill.

If `correspondence/referee-reviews/` exists and is non-empty, verify it matches the **nested per-round** convention and detect legacy/flat layouts that need retrofitting.

## Canonical structure (per review cycle)

```
correspondence/referee-reviews/{surface}-round{N}/
├── {surface}-round{N}-reviews.pdf     # REQUIRED — original; the ONLY timeline artifact
├── {surface}-round{N}-reviews.md      # REQUIRED — parsed transcription
├── {surface}-round{N}-rebuttal.md     # optional — appears when response work starts
├── analysis/                          # optional — comment-tracker, review-analysis, verbatim
└── plan/                              # optional — DAG revision-task JSONs (strategic-revision)
```

`{surface}` = short venue slug (`aies`, `emnlp`, `ejor`); `{N}` = sequential review-cycle counter (`round1`, `round2`, …), never `initial`. `referee-reviews/` contains **only** `{surface}-round{N}/` folders — no loose files.

## Step 1: `referee-reviews/` contains only round folders

List the immediate children of `correspondence/referee-reviews/`.

| Condition | Severity |
|-----------|----------|
| Only `{surface}-round{N}/` dirs (+ optional `.gitkeep`) | OK — check each round |
| **Loose file** directly under `referee-reviews/` matching `*-round*-reviews.{pdf,md}` | **Degraded (retrofit)** — "flat review file — move into `{surface}-round{N}/` with the `tidy-project-reviews` skill" |
| Loose file `reviews-original.*` (legacy name) | **Degraded (retrofit)** — "legacy `reviews-original.*` — rename to `{surface}-round{N}-reviews.*` inside a round folder" |
| Any other loose file (dissection memo, response draft at this level) | **Degraded (retrofit)** — "response-prep file loose in `referee-reviews/` — belongs inside its `{surface}-round{N}/` (rebuttal → `{surface}-round{N}-rebuttal.md`; analysis → `{round}/analysis/`)" |
| Dir not matching `*-round*` | **Info** — "unrecognized directory in `referee-reviews/`" |
| Empty (only `.gitkeep`) | **Info** — "no round directories yet" |

## Step 2: Required members per round folder

For each `{surface}-round{N}/`:

| Member | Required | Severity if absent |
|--------|----------|-------------------|
| `{surface}-round{N}-reviews.pdf` | **Yes** | **Missing** — "no reviews PDF in `{round}/`" |
| `{surface}-round{N}-reviews.md` | **Yes** | **Missing** — "no parsed reviews `.md` in `{round}/` (the pair is incomplete)" |
| `{surface}-round{N}-rebuttal.md` | No | not flagged — appears when response work begins |
| `analysis/`, `plan/` | No | not flagged — strategic-revision workspace, present only after that skill runs |

**Naming drift:** a reviews PDF/MD present but not named `{surface}-round{N}-reviews.*` (e.g. `reviews-original.pdf`, `ARR-official-reviews.pdf`) → **Degraded (retrofit)** — "review file misnamed — rename to taxonomy with the `tidy-project-reviews` skill".

## Step 3: History pointer is PDF-only

Cross-check the paper's vault submission `history:` `reviews-in` row (if resolvable):

| Condition | Severity |
|-----------|----------|
| `reviews-in` `files:` lists the `{round}/…-reviews.pdf` only | OK |
| `files:` also lists the `.md` | **Degraded** — "parsed `.md` on the timeline — history lists the PDF original only" |
| `files:` path doesn't resolve on disk | **Degraded** — "reviews-in points at a missing file (path drift after a move?)" |
| `round:` token ≠ folder number (`round2/` but `round: r1`) | **Info** — "history `round:` doesn't mirror the folder" |

## Step 4: Build artifacts in the workspace

Scan each round folder for stray LaTeX build artifacts (`*.aux *.bbl *.blg *.fdb_latexmk *.fls *.log *.synctex.gz`) outside an `out/` dir → **Degraded** — "build artifacts in `{round}/` — should be in `out/` or cleaned".

## Step 5: Misplaced review files elsewhere

Scan `docs/venues/` and project root for files that belong in a round folder (`reviewer-comment*`, `comment-tracker*`, `review-analysis*`, `*referee-report*`, `reviews-original*`) → **Degraded** — "review file outside `referee-reviews/{round}/` — relocate with the `tidy-project-reviews` skill".

## Report format

```
Review Process Consistency (nested per-round):
  referee-reviews/ contains only round folders   OK
  emnlp-round1/
    emnlp-round1-reviews.pdf     present
    emnlp-round1-reviews.md      present
    emnlp-round1-rebuttal.md     present (optional)
    analysis/                    present (optional)
  history reviews-in → PDF-only  OK
```

Retrofit needed:
```
Review Process Consistency (RETROFIT NEEDED):
  referee-reviews/aies-round1-reviews.pdf   flat file — move into aies-round1/
  referee-reviews/aies-round1-reviews.md    flat file — move into aies-round1/
  → use the tidy-project-reviews skill to migrate
```

## When to skip

- `correspondence/referee-reviews/` does not exist — Phase 2.2 flags it Missing.
- Theoretical project with no venue review history.
