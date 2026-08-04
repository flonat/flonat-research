# Canonical `.latexmkrc`

Single source of truth for LaTeX build config across all projects.

## Files

| File | Purpose |
|------|---------|
| `.latexmkrc` | Robust auto-detecting build config (drop into any dir with `.tex` files) |
| `vscode-settings.json` | VS Code LaTeX Workshop config (drop into `.vscode/settings.json`) |

## What `.latexmkrc` does

- Builds to `out/` so source dir stays clean
- Auto-detects pdfLaTeX (default), XeLaTeX (Unicode/XeTeX requirements), or LuaLaTeX (LuaTeX requirements, including `user-beamer`)
- Recurses through local `\input{}`/`\include{}` files, packages, classes, and Beamer themes
- Treats `iftex`-style engine branches in compatible local classes/packages as conditional, not as engine requirements
- Honours `% !TEX program = pdflatex|xelatex|lualatex` in the driver
- Ignores commented commands and rejects conflicting engine requirements
- Restricts bare `latexmk` to real drivers containing both `\documentclass` and `\begin{document}`
- Lets `.latexmkrc.local` narrow a bare build through `@default_files` before engine inference, while explicit CLI targets remain authoritative
- Publishes only the requested PDF after a successful build, using a SHA-256-verified temporary copy and atomic rename
- Preserves a non-zero latexmk exit status and the last-good source PDF on failure
- Works with terminal latexmk, the supplied VS Code recipe, and Overleaf-synced folders

The supported unit is a directory containing one or more root-level drivers and
their local dependencies. If several requested drivers require different
engines, the config fails closed: build them separately or pass an explicit
`-pdflatex`, `-xelatex`, or `-lualatex` override.

## Usage

```bash
# Drop into any directory with .tex files
cp <task-mgmt>/templates/latexmkrc/.latexmkrc <target-dir>/

# For Overleaf-symlinked paper dirs, drop into the symlink TARGET (the Overleaf folder)
cp <task-mgmt>/templates/latexmkrc/.latexmkrc <overleaf-folder>/

# For VS Code support
mkdir -p <target-dir>/.vscode
cp <task-mgmt>/templates/latexmkrc/vscode-settings.json <target-dir>/.vscode/settings.json
```

## Overleaf interaction

When dropped into an Overleaf-synced folder, `.latexmkrc` is git-tracked by Overleaf and synced to the web compiler. The web compiler picks the engine from *Settings → Compiler*, not from `.latexmkrc` — the auto-detect Perl runs locally only. This is fine: web Overleaf ignores the engine logic but doesn't break.

## Override

Do not fork the config. Put a standard magic comment in the driver:

```tex
% !TEX program = lualatex
```

For a one-off terminal build, pass `-pdflatex`, `-xelatex`, or `-lualatex`.
Explicit CLI flags are processed after the rc file and remain authoritative.

Project-specific bibliography paths or custom latexmk dependencies go in an
optional `.latexmkrc.local` beside the driver. The canonical loads it only when
all requested drivers share one directory. The supplement must not set
`$pdf_mode`; engine choice remains visible in the driver or command line.
For a project with several root drivers, it may set `@default_files` to select
the intended bare-build driver without affecting an explicitly requested one.

## VS Code loading contract

Latexmk reads rc files before it processes `-cd`. Therefore `-cd` alone does
not load a `.latexmkrc` beside a document below the workspace root. The supplied
recipe uses `-norc -r %DIR%/.latexmkrc -cd %DOC%`: it disables ambient rc files,
loads the document-directory canonical explicitly, and then changes directory.
It deliberately omits `-f`, so a failed build remains a failed build.

## Source ownership

In the upstream authoring repository, this directory is the only source.
Template copies and installed skill bundles are generated distribution artifacts
and must remain byte-identical to these files. Tests enforce that contract.
