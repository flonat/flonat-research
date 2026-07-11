---
paths:
  - "**/*.tex"
---

# Rule: LaTeX Hygiene

## Principles

1. **Never leave build artifacts in the source directory.** All compilation output goes to `out/`. Only the final PDF is copied back after a successful build.
2. **When a package is missing, install via `tlmgr` — never download `.sty` files.** Downloaded files pollute the source directory, don't update with TeX Live, and sync to Overleaf as junk.
3. **Keep source line-wrapping consistent within a file.** One line per paragraph by default — see "Source line-wrapping" below.

## Build Output

- **Always invoke `latexmk` directly.** Never substitute bare `pdflatex`/`xelatex`/`lualatex`/`bibtex`/`biber` — even with `-output-directory=out`. Bypassing `latexmk` silently ignores `.latexmkrc` (engine, build sequence, post-build hooks).
- Standard invocation: `latexmk <file>.tex`. The `.latexmkrc` controls everything else.
- If `latexmk` is unavailable, state this and ask the user to `tlmgr install latexmk`.

### `.latexmkrc` policy

- Opening an existing project: check the main `.tex` directory; if missing, create before compiling. If present, verify `$out_dir = 'out'` + END block — flag, don't modify without permission.
- New projects: always create `.latexmkrc` alongside the main `.tex`; add `out/` to `.gitignore` if git-tracked.

### Standard `.latexmkrc`

```perl
$out_dir = 'out';
$pdf_mode = 1;        # 1=pdflatex, 4=lualatex, 5=xelatex
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error %O %S';
$lualatex = 'lualatex -interaction=nonstopmode -halt-on-error %O %S';
$xelatex  = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';

# Copy PDFs from $out_dir back to source dir after a successful build
END {
    if (-d $out_dir) {
        my @pdfs = glob("$out_dir/*.pdf");
        foreach my $pdf (@pdfs) {
            my $base = $pdf;
            $base =~ s|.*/||;
            system("cp '$pdf' '$base'");
        }
    }
}
```

To switch engines: change `$pdf_mode` only (1/4/5). The relevant engine command (`$pdflatex`/`$lualatex`/`$xelatex`) is already there.

### VS Code Integration

LaTeX-Workshop config lives in **User settings** (`~/Library/Application Support/Code/User/settings.json`), not per-project. Invoke `latexmk` with `-cd` and no engine/output flags — `.latexmkrc` controls those. Don't duplicate in per-project `.vscode/settings.json` unless genuinely needed.

### Build artifacts (never in source directory)

`.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.log`, `.out`, `.toc`, `.lof`, `.lot`, `.nav`, `.snm`, `.vrb`, `.synctex.gz`, `.bcf`, `.run.xml`

### What stays in the source directory

- `.tex`, `.sty`, `.cls`, `.bst` — source files
- `.bib` — bibliography
- `.latexmkrc` — build config
- `.pdf` — final output (copied from `out/` after successful build)
- Figures: `.pdf`, `.png`, `.eps`, `.jpg`, `.svg`, `.tikz`

### If you find artifacts in a source directory

1. Flag: "I found build artifacts in the source directory — these should be in `out/`."
2. Offer to clean up and create `.latexmkrc` if missing.
3. Wait for confirmation before deleting anything.

## Source line-wrapping

**Default: one line per paragraph.** Write each prose paragraph as a single source line; separate paragraphs with a blank line; rely on the editor's soft-wrap for display. Keep a file internally consistent — mixed wrapping (some paragraphs hard-wrapped at ~80 cols, some on one line) is the annoyance this rule exists to prevent.

- **Leave structural content alone:** math environments, tables, `tikzpicture`, lists, and the preamble keep their own line breaks. Only prose paragraphs collapse to a single line.
- **Exception — git-tracked `.tex` where diffs matter:** prefer *semantic line breaks* (one sentence per line) so a one-word edit is a one-line diff. Overleaf-synced `paper/` dirs are gitignored, so that concern does not apply there → one-line-per-paragraph is correct.
- **Reflowing an existing file is whitespace-only and must not change output.** After reflowing: compile, then `pdftotext` the PDF before and after and diff with whitespace normalized — must be byte-identical. Never join across comments (`%`), `\\`, or into protected environments.

## Missing Packages

```bash
sudo tlmgr install <package-name>
```

If `sudo` requires an interactive password prompt (which it does inside Claude Code), ask the user to run the command themselves:

> "Missing package `<name>`. Please run: `! sudo tlmgr install <name>`"

### What NOT to do

- `curl` or `wget` a `.sty` file from CTAN
- Copy `.sty` files into the paper directory
- Generate `.sty` from `.dtx`/`.ins` in `/tmp` and copy it over
- Use any workaround that places package files in the project tree

### Inconsistent TeX Live install (format vs. package skew)

**Symptom:** a document that compiled yesterday now fails with `! Undefined control sequence` on a *kernel/array* macro (e.g. `\vcenter@text` inside `\@@array` at a `\begin{tabular}`), even on a minimal test doc. This is **not** a paper bug — it is a partial/interrupted `tlmgr` update that left the compiled format (`pdflatex.fmt`) older than the on-disk package (`array.sty`) or kernel (`latex.ltx`) that now calls a newer macro.

**Diagnose:** `kpsewhich <macro-file>`; compare `array.sty`/`latex.ltx` mtime against the format's. If `fmtutil` itself fails (e.g. `! I can't find file 'glyphtounicode-cmex'`), a pdftex support file is missing too.

**Fix (needs sudo — ask the user to run with `!`):**

```
! sudo tlmgr install --reinstall pdftex && sudo fmtutil-sys --all
```

If that still errors, `sudo tlmgr update --self --all` first, then re-run. Never mask the symptom with `\providecommand{\vcenter@text}{}` or similar — that silently garbles the affected tables. The actual submission compiles on Overleaf regardless (separate, healthy TeX install), so this only blocks *local* verification. (Incident: 2026-06-02/03, Mac Mini, competency-trap-dynamics.)

## Applies To

All LaTeX compilations on all machines: papers, proposals, presentations, teaching materials, standalone docs. Both Overleaf-linked `paper/` dirs and standalone projects. Both `/latex` and manual `latexmk`.

## Why This Matters

Build artifacts clutter source dirs, pollute git history, and break Overleaf sync. Downloaded `.sty` files are version-pinned, unmanaged, and invisible to TeX Live updates. Same root cause: putting generated or external files where only human-authored source belongs.

## Failure modes prevented

- **L4** build artifacts in source dir — see [`docs/reference/failure-modes.md`](../docs/reference/failure-modes.md)
