# Quarto Reveal.js reference

> Format reference for `quarto-deck`. Checked against Quarto 1.10 (2026-10). One
> `.qmd` file is one deck; `#` starts a section slide, `##` a content slide.

## Front matter

```yaml
---
title: "Distance to a clinic raises abortion costs"   # an assertion, not a topic
subtitle: "Department seminar · 12 October 2026"
author: "the user"
format:
  revealjs:
    theme: [default, theme.scss]
    width: 1280            # 16:9 canvas; Reveal scales it to the screen
    height: 720
    slide-number: true
    hash-type: number      # stable URLs (#/7) for sharing a slide
    transition: fade
    footer: "Short deck name"
    # embed-resources: true   # single self-contained HTML (no webR, no live cells)
---
```

Keep shared settings in the project `_quarto.yml` when several decks share a
look (as the PB130 and PB230 workshop decks do); a deck then sets only its title
and footer.

## Slide structure

```markdown
# Section title           <- section slide (Act boundaries)

## Claim as a sentence    <- content slide

Content.

::: notes
What you say. Press `s` in the browser for the speaker view.
:::
```

A `---` rule also starts a slide; directly before a heading it is redundant.
Both `::: notes` and `::: {.notes}` work.

## Layout

Columns (widths should sum to at most 100%):

```markdown
:::: {.columns}
::: {.column width="62%"}
![](figures/effect.png){fig-alt="Effect size by distance band, rising from 0 to 0.4"}
:::
::: {.column width="38%"}
- Reads the figure
:::
::::
```

Theme classes from `templates/theme.scss`:

| Class | Use |
|---|---|
| `.step-card` + `[01]{.step-number}` | numbered 3-step process (inside three 32% columns) |
| `.card` | grouped point without a number |
| `.stat` with `[..]{.number}` and `[..]{.caption}` | one big number; always followed by a `.source` line |
| `.source` | small source line under any figure, table or number |
| `.takeaway` | the closing sentence |
| `.accent`, `.muted` | emphasis by colour (never underline) |

Other built-ins: `{.r-fit-text}` (fit one line to the slide), `{.r-stretch}`
(image fills remaining height), `{.smaller}` on a slide heading (smaller text
for a dense table slide), `::: {.callout-note}` (boxed aside).

## Building up a slide

| Want | Markup |
|---|---|
| Items appear one at a time | `::: {.incremental}` around a list |
| Appear, then dim when the next arrives | `::: {.fragment .fade-in-then-semi-out}` on each block |
| Highlight a word on a click | `[word]{.fragment .highlight-blue}` |

Do **not** use `.semi-fade-out` to build up content: it starts fully visible and
only dims on its click, so the audience can read ahead (checked in Quarto 1.10's
`reveal.css`). PDF export prints every fragment in its final state.

## Figures, tables, maths and code

- Every figure gets alt text: `![](f.png){fig-alt="..."}` or, in a chunk,
  `#| fig-alt: "..."`. Generate figures from scripts in `figures/` before
  writing the slide; never paste screenshots of plots.
- Tables: keep to what is read aloud; a regression table slide gets `{.smaller}`
  and the key row in `.accent`. Exceptions to the word limit are fine for tables,
  equations and code; split the slide rather than shrinking text further.
- Maths: `$...$` and `$$...$$` render with MathJax by default.
- Code: fenced chunks with `#| echo: true`; `code-line-numbers: "2-3"` on a chunk
  highlights lines.

## Live code (quarto-live, webR / Pyodide)

For teaching decks where students run code in the browser:

```bash
quarto add r-wasm/quarto-live        # once per project, adds _extensions/r-wasm/live
```

```yaml
format:
  live-revealjs:
    theme: [default, theme.scss]
webr:
  packages: [dplyr]
```

````markdown
{{< include ./_extensions/r-wasm/live/_knitr.qmd >}}

```{webr}
mean(c(1, 2, 3))
```
````

Live decks need internet in the room (webR downloads packages). For a printable
handout, keep a second format or profile without webR and switch cells with
`::: {.content-visible unless-profile="handout"}` (live cell) and
`::: {.content-visible when-profile="handout"}` (an executed `{r}` chunk with
`#| echo: true`), as in the PB130 decks. Render the handout with
`--profile handout` and export it with `scripts/export-pdf.sh ... --profile handout`.

## Commands

| Command | What it does |
|---|---|
| `quarto preview deck.qmd` | live preview with reload |
| `quarto render deck.qmd` | build the HTML |
| `bash <this-skill>/scripts/export-pdf.sh deck.qmd --png pages/` | PDF plus page images for the visual check |
| `uv run python <this-skill>/scripts/lint_deck.py deck.qmd` | mechanical lint (exit 1 on errors) |

Keys in the browser: `s` speaker view, `f` fullscreen, `o` overview, `?` help.

## Legacy reveal-md decks

Before 2026-10 this skill produced `reveal-md` Markdown (`.md`, `Note:` speaker
notes). Those decks still run with `npx reveal-md deck.md`. To move one to
Quarto: rename to `.qmd`, move `revealOptions` into `format: revealjs:`, turn
`Note:` blocks into `::: notes ... :::`, and replace `--css custom.css` with a
`theme.scss` in the format's `theme:` list.
