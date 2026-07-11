# Referee 2 — findings.json schema

> Machine-readable companion to the markdown referee report. Write to `reviews/<scope>/referee2-reviewer/YYYY-MM-DD_round[N]_findings.json` alongside the report, where `<scope>` is the paper slug from the agent's `paper:` directive field (e.g., `paper-jtp`, `paper-philtech`). Referenced by `referee2-reviewer.md`.
>
> Schema aligns with `pdf_clean.Comment` / `pdf_clean.ReviewResult` so downstream consumers (anchor tooling, Phase 12 viz, `/synthesise-reviews`) can merge findings across agents (`paper-critic`, `referee2-reviewer`, `domain-reviewer`) without re-parsing prose.
>
> **Canonical types live in `packages/pdf-clean/src/pdf_clean/models.py`.** Extend the `Comment` dataclass with referee2-specific fields rather than inventing a parallel schema.

## Schema example

```json
{
  "method": "referee2-reviewer",
  "paper_slug": "<project-dir basename>",
  "model": "<opus|sonnet|...>",
  "anchor_version": 1,
  "round": 1,
  "verdict": "ACCEPT | MINOR REVISION | MAJOR REVISION | REJECT",
  "overall_feedback": "<two-to-three-sentence summary of the review>",
  "dispositions": ["SKEPTIC", "MEASUREMENT"],
  "pet_peeves": {
    "critical": ["..."],
    "constructive": ["..."]
  },
  "comments": [
    {
      "id": "R1",
      "tier": "C",
      "category": "Identification | Measurement | Statistics | Replication | Presentation | Scholarship",
      "title": "Identification strategy does not address selection on unobservables",
      "quote": "<exact verbatim text from the source>",
      "explanation": "<why this is a concern and what it implies for the results>",
      "fix": "<specific, actionable recommendation — what the author should do>",
      "comment_type": "logical",
      "location": "main.tex:128",
      "paragraph_index": null
    }
  ],
  "num_comments": 1
}
```

## Field rules

| Field | Type | Notes |
|-------|------|-------|
| `method` | string | Always `"referee2-reviewer"` for this agent |
| `paper_slug` | string | Basename of the project directory |
| `anchor_version` | int | `1` for Phase 11+ output. Never emit `0` |
| `dispositions` | array of strings | The 2 randomly-assigned dispositions from `referee-config.md` |
| `pet_peeves.critical` | array of strings | The 3 critical pet peeves drawn for this invocation |
| `pet_peeves.constructive` | array of strings | The 2 constructive pet peeves drawn for this invocation |
| `comments[].id` | string | Referee-report IDs (`R1`, `R2`, ...) — match the markdown IDs |
| `comments[].tier` | string | `"C"` (Critical / blocker), `"M"` (Major / requires revision), `"m"` (Minor / nice to fix) |
| `comments[].category` | string | One of the 6 audit domains: Identification, Measurement, Statistics, Replication, Presentation, Scholarship |
| `comments[].quote` | string | **Exact verbatim text from the source.** Never paraphrase. `pdf_clean.assign_paragraph_indices` recovers anchors by fuzzy-matching this quote against cleaned PDF prose — paraphrase breaks the pipeline |
| `comments[].comment_type` | string | `"technical"` (math/stats/formula/equation/parameter/variance/proof) or `"logical"` (everything else). Maps to `pdf_clean.Comment.comment_type` |
| `comments[].location` | string | `file.tex:line` or `file.R:line` as appropriate |
| `comments[].paragraph_index` | int \| null | **Leave as `null`**. Referee 2 audits LaTeX source and code; it has no access to the cleaned PDF paragraph index space. Derived post-hoc by `pdf_clean.assign_paragraph_indices(comments, cleaned_pdf_text)` at consumption time |

## Why both markdown and JSON?

- Markdown report: human-facing, read by the user and the fixer agent.
- JSON companion: machine-facing, consumed by `/synthesise-reviews`, Phase 12 viz, and anchor tooling.

Both files must agree on issue count, IDs, categories, quotes, and verdict. Write the JSON after finalising the markdown so the markdown remains the source of truth during authoring.

**Replication artefacts** (`referee2_replicate_*.do/R/py`) are unchanged by this schema — they remain standalone scripts in `code/replication/` and are referenced from the markdown report, not embedded in the JSON.

**Backward compatibility:** Pre-Phase-11 reports have no `findings.json`. Consumers detect absence and skip anchor-dependent processing. Do not retroactively generate JSON for historical reports.
