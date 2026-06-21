# Source-Pathology Catalogue (Phase 4)

> Grep-based detectors for LaTeX source patterns that compile cleanly but produce visually fragile or weird output. Each pathology lists a detection signature, severity tier, remediation, and false-positive caveats.
>
> Provenance: GPT-5.5 Pro recommendation 2026-06-19 after a titlepage line-spacing failure on the v5 PhD proposal. Pattern #9 (label-before-caption) promoted to Small-effort by the user after Pro initially graded it Medium.

## How Phase 4 runs

After Phase 3 (final report), before Phase 5 (citation audit), if the build was clean:

1. Run each grep-based detector against the project's `.tex` files (main + any `\input`/`\include`'d files).
2. Run `chktex -q -n8 -n44 <main>.tex` if installed; collect output.
3. Run `latexindent -k <main>.tex` if installed; collect diff and exit code.
4. Report findings in a "Source pathologies" subsection.
5. Forward deductions to Phase 6 per `quality-rubric.md`.

Phase 4 produces **findings**, not auto-fixes. The single exception is Pattern 1 ("Spacing hacks fighting global spacing"), where the standard remediation (`\begin{singlespace}…\end{singlespace}` scope + delete negative kerns) is offered as an opt-in auto-fix the user can accept.

## Detection patterns

### 1. Spacing hacks fighting global spacing — **Major**

**Pathology.** Global `\onehalfspacing` / `\doublespacing` / `\setstretch{>1}` is active, and local blocks (typically `titlepage`, `center`, or headings) use negative `\\[-Xcm]` skips or `\vspace{-…}` to fight it. Negative kerns scale differently across font sizes, so the visible result is uneven inter-line gaps.

**Detection.**
```bash
PREAMBLE_HAS_GLOBAL_SPACING=$(grep -nE '^[^%]*\\(onehalfspacing|doublespacing|setstretch)\b' "$tex" | head -1)
LOCAL_NEGATIVE_KERNS=$(grep -nE '\\\\\[\s*-[0-9.]+\s*(cm|em|pt|in|mm)\s*\]|\\vspace\*?\{\s*-[0-9.]+[^}]*\}' "$tex")
```
Flag when both match.

**Remediation.** Wrap the affected block in `\begin{singlespace}…\end{singlespace}` (from `setspace`, usually already loaded) and delete the negative kerns. The body's global spacing is unaffected.

**False-positive caveats.** Legitimate negative kerns may appear in fine-tuning under TikZ pictures or math display environments. Limit Phase 4's reporting to `titlepage`, `center`, `flushleft|flushright`, and `\maketitle`-adjacent blocks; ignore matches inside `\begin{tikzpicture}` or `\begin{equation*}`.

### 2. Manual vertical-rhythm surgery — **Moderate–Major**

**Pathology.** Body text peppered with `\vspace`, `\vskip`, `\enlargethispage`, `\pagebreak`, `\nopagebreak` — usually accreted in late drafting to "make things fit". Each is a single-page fix that breaks the next time the surrounding text changes.

**Detection.**
```bash
# Count occurrences outside front matter (after first \section or 50 lines past \begin{document})
grep -nE '\\(vspace|vskip|enlargethispage|pagebreak|nopagebreak)\b' "$tex"
```

Tier: Moderate if 1–5 instances; Major if >5.

**Remediation.** Replace per-instance vertical fixes with structural solutions: `\titlespacing` from `titlesec`, paragraph spacing from `parskip`, or fixing the underlying float placement.

**False-positive caveats.** Title pages legitimately use `\vspace*{...}` and `\vfill`; ignore matches inside `\begin{titlepage}…\end{titlepage}`.

### 3. Line breaks as layout engine — **Moderate–Major**

**Pathology.** `\\`, `\newline`, or `\linebreak` used inside `\section{…}`, `\subsection{…}`, `\caption{…}`, or other semantic units. The break suppresses automatic typography (hyphenation, justification, TOC entry formatting) and brittle-renders under template changes.

**Detection.**
```bash
grep -nE '\\(section|subsection|subsubsection|paragraph|chapter|caption)\{[^}]*\\\\|\\newline|\\linebreak' "$tex"
```

Tier: Major inside `\section`/`\caption`; Moderate inside titlepage.

**Remediation.** For section titles, define a custom heading format via `titlesec`. For captions, write a shorter caption + use `\caption[short]{long}`.

**False-positive caveats.** None inside captions or section commands — these are essentially always wrong.

### 4. Forced-float carpet bombing — **Moderate**

**Pathology.** Repeated `[H]`, `[!h]`, `\FloatBarrier` in figure/table environments overrides LaTeX's float algorithm globally, often producing worse placement than the algorithm would.

**Detection.**
```bash
grep -cE '\\begin\{(figure|table)\}\[[!Hh]+\]' "$tex"
grep -cE '\\FloatBarrier' "$tex"
```

Tier: Moderate if >3 of either; Minor if 1–3.

**Remediation.** Replace with `[tbp]` and trust the float algorithm. Use `\FloatBarrier` sparingly at section boundaries only.

**False-positive caveats.** Occasional `[H]` is fine and sometimes necessary (e.g., immediately before a `\subsection` boundary). Don't flag isolated uses.

### 5. Shrink-to-fit tables/figures — **Major**

**Pathology.** Tables or figures wrapped in `\resizebox{\textwidth}{!}{…}` or `\adjustbox{width=\textwidth}{…}` to force fit. Produces visually unreadable text when the source is much wider than `\textwidth`.

**Detection.**
```bash
grep -nE '\\(resizebox|scalebox)\s*\{[^}]*\\textwidth' "$tex"
grep -nE '\\begin\{adjustbox\}.*width\s*=.*\\textwidth' "$tex"
```

**Remediation.** Redesign the table (drop columns, abbreviate headers, split across two), use `\small`/`\footnotesize` typography, or rotate to landscape via `lscape`.

**False-positive caveats.** Mild shrinkage (e.g. `0.95\textwidth` on a 100% table) is usually acceptable; flag only when the scale factor is `\textwidth` exactly (=auto-fit to whatever width the source happens to be).

### 6. Tiny-table typography hacks — **Moderate–Major**

**Pathology.** `\scriptsize`/`\tiny` inside tabular environments, negative `\tabcolsep`, or `\arraystretch < 0.9` to compress a table that should be redesigned.

**Detection.**
```bash
grep -nE '\\(scriptsize|tiny)\b' "$tex" | while read m; do
    # Check if within 5 lines of a tabular begin
    ...
done
grep -nE '\\setlength\{\\tabcolsep\}\{\s*-' "$tex"
grep -nE '\\renewcommand\{\\arraystretch\}\{0\.[0-8]' "$tex"
```

**Remediation.** Same as Pattern 5.

**False-positive caveats.** `\scriptsize` in footnote-tables is legitimate; tier as Moderate, not Major, unless multiple symptoms cluster.

### 7. Absolute / overlap positioning — **Major**

**Pathology.** `\raisebox`, `\makebox[0pt]`, `\llap`, `\rlap`, `\smash`, `\hspace*` used outside of TikZ pictures or math contexts to manually place text. Silent overlaps are easy to introduce and hard to spot.

**Detection.**
```bash
grep -nE '\\(raisebox|makebox\s*\[0pt\]|llap|rlap|smash|hspace\*)\b' "$tex"
```

**Remediation.** Use a structured environment (minipage, tabularx, TikZ overlay) and document intent.

**False-positive caveats.** `\smash` in math environments is common and benign — skip matches inside `\begin{equation}…\end{equation}`, `\[…\]`, etc. `\hspace*` at line starts is also usually intentional spacing.

### 8. Fixed-width layout assumptions — **Moderate**

**Pathology.** Hard-coded `cm` widths for `minipage`, `parbox`, or table `p{Xcm}` columns. Breaks when the document's margins, class, or page size change.

**Detection.**
```bash
grep -nE '\\begin\{minipage\}\{[0-9.]+cm\}|\\parbox\{[0-9.]+cm\}|\bp\{[0-9.]+cm\}' "$tex"
```

**Remediation.** Use `\textwidth` fractions: `\begin{minipage}{0.45\textwidth}` etc.

**False-positive caveats.** Document classes whose width is fixed (business cards, posters) legitimately use absolute units — don't apply to `\documentclass{a0poster}` or similar.

### 9. Label-before-caption inside floats — **Major**

**Pathology.** `\label{…}` placed before `\caption{…}` inside a `figure` or `table` environment. The `\ref` target ends up pointing at the surrounding section counter, not the figure/table counter — and the document still compiles cleanly.

**Detection.** AWK-walk each `\begin{figure}`…`\end{figure}` and `\begin{table}`…`\end{table}` block. Flag if `\label{…}` line precedes `\caption{…}` line within the same block.

```awk
/^[^%]*\\begin\{(figure|table)\}/ { in_float = 1; label_line = 0; caption_line = 0 }
in_float && /\\label\{[^}]+\}/ && !label_line { label_line = NR }
in_float && /\\caption\{/ && !caption_line { caption_line = NR }
/^[^%]*\\end\{(figure|table)\}/ {
    if (label_line && caption_line && label_line < caption_line)
        print FILENAME ":" label_line ": label before caption (caption at " caption_line ")"
    in_float = 0
}
```

**Remediation.** Move the `\label{…}` line to immediately after `\caption{…}`.

**False-positive caveats.** None — this is essentially always wrong.

## External-tool integration

### `chktex` (if installed)

```bash
chktex -q -n8 -n44 "$tex" 2>&1 | grep -v "^$"
```

Flags: `-q` quiet, `-n8` suppresses "wrong dash" (false-positive heavy), `-n44` suppresses "use \frac" (style preference). Report findings; deduct -1 per unique warning, capped at -10.

`chktex` covers: typographic nits (spacing around punctuation, ellipses, dashes), unmatched braces in math, common command-vs-environment confusions, suspicious `\ldots` placements.

`chktex` does **not** cover: any of Patterns 1, 4, 5, 6, 7, 9 above.

### `latexindent -k` (if installed)

```bash
latexindent -k "$tex" 2>&1
echo "Exit: $?"
```

Exit code non-zero → source structure is inconsistent with the `latexindent` default style; flag as a "source-cleanliness smoke test failure". Deduct -3 once, not per line.

`latexindent` covers: chaotic indentation, fragile hand-rolled blocks, table alignment that's structurally wrong (will misrender under tracked changes / collaborators).

`latexindent` does **not** judge visual output.

## What Phase 4 does NOT do

- Inspect the rendered PDF (that's `/latex-polish` — proposed but not yet implemented).
- Auto-rewrite Pattern 2–9 issues (report only).
- Rewrite anything that changes the meaning of the prose (that's `/proofread`).
- Run on builds that failed compilation (skip; the source-pattern lint is meaningless if the doc doesn't build).
