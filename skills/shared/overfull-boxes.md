# Shared Reference: Overfull / Underfull Boxes

Detection, severity grading, and remediation for TeX's `Overfull`/`Underfull`
`\hbox`/`\vbox` messages. Consumed by `latex` (Phase 3 report + Phase 5 score),
`latex-health-check` (Phase 2c parse + 2d flag), and `pre-submission-report`.

> **Why this file exists.** Box messages are NOT `Warning`-tagged in the log, so
> `grep -c "Warning"` silently misses every one of them. Both compile skills must
> use the recipes below, not a `Warning` grep, or the box count is wrong and the
> quality-rubric box deductions (`-5`/`-2`/`-1`) never fire.

## What the log actually says

Box messages have no `Warning` token — they start with `Overfull`/`Underfull`:

```
Overfull \hbox (29.5pt too wide) in paragraph at lines 12--14
Overfull \hbox (5.0pt too wide) in alignment at lines 100--105
Overfull \hbox (1.2pt too wide) detected at line 200
Underfull \hbox (badness 10000) in paragraph at lines 45--47
Overfull \vbox (12.0pt too high) has occurred while \output is active
```

## Detection recipes (stdlib grep/awk only)

Count, separated from real warnings:

```bash
# LaTeX/package warnings (the "Warning"-tagged lines — refs, fonts, packages)
grep -c "Warning" out/<file>.log
# Overfull boxes (NOT captured by the line above)
grep -cE 'Overfull \\[hv]box \([0-9.]+pt too (wide|high)\)' out/<file>.log
# Underfull boxes
grep -cE 'Underfull \\[hv]box \(badness [0-9]+\)' out/<file>.log
```

Top offenders, sorted by overflow magnitude (the number that decides severity):

```bash
awk -F'[()]' '/Overfull \\[hv]box/ {
    split($2, a, "pt"); w = a[1] + 0;          # overflow in pt
    loc = $0; sub(/.*too (wide|high)\) */, "", loc);
    printf "%7.1f pt  %s\n", w, loc
}' out/<file>.log | sort -rn | head -20
```

## Severity gradient (aligned to `latex/references/quality-rubric.md`)

| Overflow | Grade | Score impact | Typical cause |
|----------|-------|--------------|---------------|
| `< 1 pt` | ignore | none | rounding below `\hfuzz` — not worth reporting |
| `1–10 pt` | minor | `-2` each | justification / missing hyphenation |
| `> 10 pt` | major | `-5` each | wide table, URL, verbatim, or display math exceeding `\textwidth` |
| underfull (`badness`) | low | `-1` each | over-stretched line/page — usually cosmetic |

Report the location (`lines a--b` or `line n`) and overflow width for every box
`≥ 1 pt`. A major box almost always points at one unbreakable wide object, not at
prose.

## Remediation ladder (least-invasive first — never silently reword prose)

1. **`\usepackage{microtype}`** — global, near-zero cost, eliminates most `1–10 pt`
   boxes via character protrusion + font expansion. Check it is loaded first.
2. **URLs / paths / long tokens** — `\usepackage{xurl}` (or `url` + `\sloppy` in a
   local scope), `\seqsplit`, or allow line breaks at punctuation.
3. **Long unbreakable words** — discretionary hyphens (`foo\-bar`) or a preamble
   `\hyphenation{foo-bar}` entry.
4. **Wide tables** — `tabularx`/`\resizebox{\textwidth}{!}{…}`/`\small`/`adjustbox`,
   or `landscape` (`lscape`/`pdflscape`) for genuinely wide data.
5. **Wide display math** — `split`/`multline`/`aligned`, `\resizebox`, or a manual
   `\\` break.
6. **Localised only** — wrap the offending paragraph in
   `\begin{sloppypar}…\end{sloppypar}`. **Never** put a global `\sloppy` in the
   preamble — it degrades typography document-wide.
7. **Never** silently reword the author's prose to make a line fit. That is a
   content decision — flag the box and its location, let the human decide
   (`rules/manuscript-edit-budget.md`).

## Auto-fix stance

`microtype` insertion (step 1) is the only safe automatic action, and only if the
package is genuinely missing and no `\usepackage{microtype}` is already present.
Everything else (steps 2–6) is a **suggestion** in the report; do not apply
without confirmation. Underfull boxes are reported but not fixed.
