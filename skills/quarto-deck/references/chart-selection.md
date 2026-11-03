# Chart selection for slides

> Pick the chart from the comparison you want the audience to make, then strip it
> to that comparison. Framework after Zelazny (*Say It with Charts*) and Abela's
> chart chooser; adapted for research talks, where distributions and
> uncertainty matter more than in business decks.

## Decide the comparison first

| The slide's claim compares… | Default chart | Notes |
|---|---|---|
| **Items** (groups, models, countries) | Horizontal bar, sorted by value | Long labels read without tilting; sort descending unless the order means something |
| **Over time**, few periods | Columns | Time runs left to right, never vertical |
| **Over time**, many periods | Line | Label lines directly at their ends; no legend box |
| **Parts of a whole** at one time | 100% stacked bar, or waterfall for additions and subtractions | Pie only for 2–4 shares that differ clearly |
| **Parts of a whole** over time | Stacked columns (few periods) or stacked area (many) | 100% versions when only the shares matter |
| **Distribution** of one variable | Histogram, density, or box/violin plot | Show the spread, not just the mean; jitter points when n is small |
| **Distributions across groups** | Small multiples, ridgeline, or box plots side by side | Same axis for every panel |
| **Relationship** between two variables | Scatter | Add a fit line only if the claim is about the trend |
| **Relationship** with a third variable | Colour or facet, before bubble size | Bubble area is hard to compare |
| **Estimates with uncertainty** (coefficients, effects) | Dot-and-interval (coefficient) plot | Usually beats a regression table on a slide |

## Make the chart carry one claim

1. **Title states the finding**, not the variable ("Effects fade after six months", not "Effect by month").
2. **Highlight the comparison** in the accent colour; everything else in grey.
3. **Label directly** on the bars or lines; drop the legend where possible.
4. **Bars start at zero.** If the interesting change is small, use a line or a dot plot instead of truncating a bar axis.
5. **Show uncertainty** where the claim depends on it (intervals, bands), and say in the notes what they are (95% CI, SE).
6. **Remove chart junk**: heavy gridlines, 3D, shadows, duplicate axis labels, decimal places nobody reads.
7. **Readable from the back**: axis text at least as large as the slide's body text; export at the slide's size, not a paper figure's.
8. **Alt text** says what the chart shows, including the finding (`fig-alt`).
9. **Colour-safe**: do not rely on red versus green; check the palette in grey.

## Academic exceptions

- A paper figure rarely works unchanged on a slide. Redraw it with fewer series,
  bigger text and the one comparison the talk needs.
- A full regression table belongs in the paper or a backup slide. On the main
  slide show the coefficient plot, or the one row that carries the claim.
- Maps only when location is the point; otherwise a sorted bar chart of the same
  regions is easier to read.
