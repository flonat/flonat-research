# LaTeX working-paper template

A clean LuaLaTeX template for academic working papers. The template is client-neutral: it can be used directly, through Claude Code, through Codex, or through other research automation without changing its source format. Client-specific hooks and deployment logic belong outside this repository.

## Included files

| File | Purpose |
|------|---------|
| `main.tex` | Document structure and section inputs |
| `your-template.sty` | Page layout, typography, mathematics, tables, figures, and theorem environments |
| `your-bib-template.sty` | BibLaTeX configuration, Harvard-style option, and the fail-closed `\CiteTodo` guard |
| `user-math.sty` | Shared math core — macros, operators, delimiters, theorem environments. Engine-agnostic and clash-safe, so **venue papers can load it too** |
| `paperpile.bib` | Project bibliography populated with verified citekeys |
| `citation-placeholders.tex` | Back-compat shim; the guard now ships inside `your-bib-template.sty` (loading both is safe) |
| `user-rev.sty` | Three-mode revision highlighting for revision (v2+) surfaces |
| `biblatex-preamble.tex` | Standalone bibliography configuration example |
| `.latexmkrc` | LuaLaTeX build configuration; writes intermediates to `out/` |
| `sections/` | Introduction, literature, data, results, discussion, and conclusion stubs |

## Requirements and compilation

The style uses `fontspec` and `unicode-math`, so LuaLaTeX is required. A TeX Live installation with `latexmk` and Biber is recommended.

```bash
latexmk
```

Build intermediates remain in `out/`. After a successful build, `.latexmkrc` copies the final PDF to the project root.

## Starting a paper

Copy the repository contents into a new LaTeX or Overleaf project, excluding `.git/` and any existing `out/` directory. Then replace the title, author, abstract, keywords, and section stubs in `main.tex` and `sections/`.

Optional Theory and Model section inputs are already present as comments in `main.tex`. New sections should use a dedicated file under `sections/` and an explicit `\label{}`.

## Citations

Use verified citekeys exported into `paperpile.bib`; never guess a citekey. When the intended source is known but its canonical key has not yet been resolved, use:

```latex
\CiteTodo{short-slug}{title; authors; year; DOI or lookup hint}
```

`\CiteTodo` fails the build by default. For an explicitly temporary draft, add `\draftcitationstodotrue` after `citation-placeholders.tex` is loaded; unresolved citations then render as visible warnings instead of silently appearing valid.

## Revision tracking

For an R&R or post-review revision, copy `user-rev.sty` into the paper project and load it with a mode option — `\usepackage[trackchanges]{user-rev}` (blue additions + red struck deletions, internal review), `\usepackage[revision]{user-rev}` (blue additions only — reviewer-facing, fits page limits), or `\usepackage[clean]{user-rev}` (no markup — final submission; also the fail-safe default when no option is given). Works with any document class; it only requires `xcolor`. Wrap additions in `\new{…}`, deletions in `\removed{…}` (`\removedm{…}` for math), rewording in `\rev{…}`, and block-level additions in the `revblock` environment.

## Framework integration

Research frameworks may copy this template into a project, but the template itself has no dependency on a particular AI client, startup hook, home-directory layout, or machine. Keep project code and data outside an Overleaf paper directory; only LaTeX sources, bibliography files, and rendered figures or tables belong in the paper project.


## Using the math core in a venue paper

`user-math.sty` is deliberately independent of `your-template`: it loads no
fonts and requires no particular engine, so an acmart / NeurIPS / ACL / LIPIcs
paper can copy it in and get the same macros the working-paper template uses,
instead of re-declaring `\E`, `\Prob`, `\R`, `\argmax` in every preamble.

```latex
\usepackage{user-math}               % macros + operators + theorem environments
\usepackage[notheorems]{user-math}   % macros only — the venue kit owns theorems
\usepackage[eqnsection]{user-math}   % also number equations per section
\usepackage[verbose]{user-math}      % log which macros were skipped as already-defined
```

Every definition is clash-safe: anything the document class or venue kit has
already defined is left untouched (load order does not matter), so adding the
package cannot change a venue's symbols or theorem styling. `your-template.sty`
loads it with `[eqnsection]`, so working papers are unchanged.

Provided: `\R \N \Z \Q \E \Prob \indicator`; operators `\argmin \argmax \Var
\Cov \Corr \sign \supp \diag \tr \plim`; paired delimiters `\abs \norm \ceil
\floorbr \set` (starred forms auto-size); `\given` for conditioning bars; and
the theorem/proposition/lemma/corollary/definition/assumption/example/remark/
hypothesis environments on a shared counter.

## Citation guard

`\CiteTodo` now ships with `your-bib-template.sty` — no separate `\input` needed:

```latex
\usepackage[harvard]{your-bib-template}       % guard included, fail-closed
\usepackage[nocitetodo]{your-bib-template}    % opt out of the guard
```
