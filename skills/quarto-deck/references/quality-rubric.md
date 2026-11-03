# Quality Rubric: Quarto Deck

> Scoring rubric for `quarto-deck`. Uses the shared framework in [`../../shared/quality-scoring.md`](../../shared/quality-scoring.md).
> Mechanical items come from `scripts/lint_deck.py` (Phase 4); judgement items
> from the rhetoric review (Phase 5) and the visual check (Phase 4).

## Deduction Table

### Blocker (-100)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| `quarto render` fails, no HTML output | -100 | Deck is broken |
| Statistic or quote with no real source, or a template placeholder left in (`[XX%]`, `[Claim ...]`) | -100 | Never ship invented or placeholder numbers |

### Critical (-15 to -25)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| No narrative arc (no Problem → Investigation → Resolution structure) | -20 | Fundamental rhetoric failure |
| Label title instead of assertion (e.g., "Results" not a claim) | -15 | Per slide; lint flags common labels |
| Multiple ideas on a single slide | -15 | Per slide |
| Lint ERROR (image not found) | -15 | Per broken image |
| MathJax rendering failure (broken equation) | -15 | Per broken equation |
| PDF export blank or missing pages (when a PDF was asked for) | -15 | Once |

### Major (-5 to -14)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Content overflow seen in the visual check (text or figure runs off the slide) | -8 | Per slide |
| Missing transitions between sections | -8 | Per missing transition |
| Build-up uses `.semi-fade-out` (audience can read ahead) | -5 | Per slide; use `.fade-in-then-semi-out` |
| Text-heavy slide (lint: words over limit) not justified by a table, equation or code | -5 | Per slide |
| Inline `style=` in the deck instead of a theme class | -5 | Per instance |
| Figure without alt text | -5 | Per figure |
| Figure sizing wrong (too small/large for slide) | -5 | Per figure |
| Colour palette not accessible (contrast, red/green reliance) | -5 | Once for the deck |
| Aristotelian balance off for audience type | -5 | Once for the deck |
| Code chunk errors or broken highlighting | -5 | Per chunk |

### Minor (-1 to -4)

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Conclusion-last instead of conclusion-first (Pyramid Principle) | -3 | Per slide |
| Slide visually cramped | -3 | Per slide |
| Cognitive load spike | -3 | Per instance |
| Speaker notes missing on key slides | -2 | Per key slide |
| List longer than the lint limit without grouping | -2 | Per list |
| Inconsistent formatting between slides | -2 | Once for the deck |

## Category Mapping

| Rubric category | Phase |
|----------------|-------|
| Rendering & structure | Phase 3–4 (render, lint) |
| Visual quality (overflow, figures, layout) | Phase 4 (page images) |
| Rhetoric (arc, titles, one idea) | Phase 5 |
| Final polish | Phase 6 |
