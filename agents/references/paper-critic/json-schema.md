# Paper Critic — findings.json schema

> Machine-readable companion to `CRITIC-REPORT.md`. Write to `reviews/<paper_slug>/paper-critic/YYYY-MM-DD-HHMM.findings.json` alongside the markdown report. Referenced by `paper-critic.md`.
>
> **Canonical types live in `packages/pdf-clean/src/pdf_clean/models.py`.** Do not invent a parallel schema — extend the `Comment` dataclass with the project-specific fields below.

The schema aligns with `pdf_clean.Comment` / `pdf_clean.ReviewResult` so downstream consumers (anchor tooling, Phase 12 viz, `synthesise-reviews`) can merge findings across agents without re-parsing prose.

## Schema enforcement — DO NOT rename fields

The anchor pipeline (`pdf_clean.assign_paragraph_indices`), Phase 12 viz, and `synthesise-reviews` read the JSON with **exact** key names. Renaming even one field silently breaks every downstream consumer. Past incident (2026-04-21): an agent emitted `issues`/`problem`/`severity` instead of `comments`/`explanation`/`tier` — validator returned 0% coverage despite 4 legitimate findings being recorded.

**Required top-level keys** (exact names): `method`, `paper_slug`, `anchor_version`, `round`, `verdict`, `score`, `overall_feedback`, `comments`, `num_comments`.

**Required per-item keys inside `comments[]`** (exact names): `id`, `tier`, `category`, `title`, `quote`, `explanation`, `fix`, `comment_type`, `location`, `deduction`, `paragraph_index`.

**Forbidden aliases** (do NOT use these, even if they feel more natural):

| Wrong | Correct |
|-------|---------|
| `issues` | `comments` |
| `issue_count` | `num_comments` |
| `problem` | `explanation` |
| `severity` | `tier` |
| `"Blocker"` / `"Critical"` / `"Major"` / `"Minor"` (as `tier` value) | `"C"` / `"M"` / `"m"` (single-letter; Blocker is a verdict, not a tier) |
| `hard_gates` as top-level object | Report hard gate failures as regular `comments[]` entries with `tier: "C"` and `category: "LaTeX-Specific"` or `"Citation"` |

**Verdict vs tier:** `verdict` is document-level (`APPROVED`, `NEEDS REVISION`, `BLOCKED`). `tier` is per-comment (`C`, `M`, `m`). A BLOCKED verdict still requires the `comments[]` array populated — do not short-circuit the schema because one hard gate failed. List the gate failure as a Critical comment AND set `verdict: "BLOCKED"`.

## Final pre-write checklist

Run mentally before writing `findings.json`:

1. Top-level has `comments` (not `issues`)? ✓
2. Every item has `explanation` (not `problem`) and `tier` (not `severity`)? ✓
3. Every `tier` value is `"C"`, `"M"`, or `"m"` (not `"Critical"`/`"Major"`/`"Minor"`)? ✓
4. Every item has `paragraph_index: null`? ✓
5. Every item has `comment_type` set to `"technical"` or `"logical"`? ✓
6. `anchor_version: 1`? ✓

If any check fails, rewrite before finalising. The markdown CRITIC-REPORT.md is free to use human-readable tier names ("Critical"/"Major"/"Minor") in its headings — but the JSON is rigid.

## Schema example

```json
{
  "method": "paper-critic",
  "paper_slug": "<project-dir basename>",
  "model": "<opus|sonnet|...>",
  "anchor_version": 1,
  "round": 1,
  "verdict": "APPROVED | NEEDS REVISION | BLOCKED",
  "score": 87,
  "overall_feedback": "<one-paragraph summary; same prose as the markdown report's top section>",
  "comments": [
    {
      "id": "C1",
      "tier": "C",
      "category": "Notation",
      "title": "Inconsistent treatment indicator",
      "quote": "<exact verbatim text from the source .tex — load-bearing for anchor recovery>",
      "explanation": "<what is wrong, stated factually>",
      "fix": "<precise instruction for the fixer>",
      "comment_type": "logical",
      "location": "main.tex:42",
      "deduction": -15,
      "paragraph_index": null
    }
  ],
  "num_comments": 1
}
```

## Field rules

| Field | Type | Notes |
|-------|------|-------|
| `method` | string | Always `"paper-critic"` for this agent |
| `paper_slug` | string | Basename of the project directory containing the `.tex` files |
| `anchor_version` | int | `1` for Phase 11+ output. Never emit `0` (reserved for legacy unpatched artefacts) |
| `comments[].id` | string | Matches the markdown ID (`C1`, `M3`, `m7`) |
| `comments[].tier` | string | `"C"` / `"M"` / `"m"` — the single-letter prefix from the ID |
| `comments[].category` | string | One of the 9 check dimensions (Grammar, Notation, Citation, Tone, LaTeX, TikZ, Internal Consistency, Tables & Figures, Causal Overclaiming) |
| `comments[].quote` | string | **Exact verbatim text from the source.** Never paraphrase. Post-hoc anchor recovery (`pdf_clean.assign_paragraph_indices`) relies on this matching cleaned PDF prose — paraphrased quotes break the anchor pipeline |
| `comments[].comment_type` | string | `"technical"` or `"logical"` — maps to `pdf_clean.Comment.comment_type`. Use `"technical"` for math/formula/equation/proof/parameter issues; `"logical"` otherwise |
| `comments[].location` | string | `file.tex:line` — matches the markdown Location field |
| `comments[].deduction` | int | Negative integer matching the deductions table in the markdown report |
| `comments[].paragraph_index` | int \| null | **Leave as `null`**. Derived post-hoc by `pdf_clean.assign_paragraph_indices(comments, cleaned_pdf_text)` at consumption time — agents have no access to the cleaned PDF's paragraph index space, only to LaTeX source. The exact `quote` is what enables the downstream recovery |

## Why both markdown and JSON?

- Markdown (`CRITIC-REPORT.md`) is the human-facing artefact — the fixer agent and the user read this.
- JSON (`findings.json`) is the machine-facing artefact — `synthesise-reviews`, Phase 12 viz, anchor tooling, and any future consumer read this.

Both files must agree: same issue count, same IDs, same deductions, same quotes. **Emit `findings.json` FIRST** (machine-readable, small, cheap to write, anchor-critical) so stall/watchdog events still preserve the anchor artefacts. Write the markdown CRITIC-REPORT.md SECOND as the human-facing companion. If the two diverge during authoring, `findings.json` is the source of truth — the markdown should be rewritten to match, not the other way around.

**Backward compatibility:** Pre-Phase-11 reports have no `findings.json`. Consumers detect this (missing file → `anchor_version=0` semantics) and skip anchor-dependent processing. Do not retroactively generate JSON for historical reports.
