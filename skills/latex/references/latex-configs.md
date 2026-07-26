# LaTeX Configuration Reference

> VS Code integration, the canonical `.latexmkrc`, and reference checking scripts.
> Referenced from `SKILL.md` — the parent file has a summary + pointer.

## Canonical `.latexmkrc`

Maintainers edit the repository's top-level `templates/latexmkrc/.latexmkrc`.
The installed `latex` skill exposes that artifact at
`templates/build-config/.latexmkrc`: the private source tree uses a reviewed
symlink, while published distributions receive a dereferenced byte-identical
copy. The bundle is a deployment surface, not a second authoring source.

It auto-detects the engine, builds to `out/`, and copies the PDF back to the source dir. Drop it into any directory with `.tex` files — including Overleaf-symlinked paper folders (the file goes into the symlink target so it syncs to Overleaf's web compiler too):

```bash
LATEX_SKILL_DIR="<installed latex skill directory>"
cp "$LATEX_SKILL_DIR/templates/build-config/.latexmkrc" <target-dir>/.latexmkrc
```

Stop if the installed bundle is unavailable. Compare existing files
byte-for-byte before any migration; `.latexmkrc.local` is the only
project-specific supplement.

See `../templates/build-config/README.md` for the full fail-closed contract and
rationale.

## VS Code LaTeX Workshop Setup

Two gotchas to know:

1. **`.latexmkrc` in subdirectories is NOT picked up by default.** Latexmk reads rc files before processing `-cd`, so `-cd` alone cannot fix this. The canonical recipe uses `-norc -r %DIR%/.latexmkrc -cd %DOC%` to load the document-directory config explicitly and exclude ambient rc files.
2. **`% !TEX program` magic comments override custom recipes.** Set `latex-workshop.latex.build.forceRecipeUsage: true` (the canonical config does this).

### Canonical `.vscode/settings.json`

Use the generated bundle at
`../templates/build-config/vscode-settings.json`; maintainers edit its
top-level `templates/latexmkrc/vscode-settings.json` authoring source.

```bash
mkdir -p .vscode
cp /path/to/canonical/vscode-settings.json .vscode/settings.json
```

This config loads the document-directory canonical explicitly before `-cd`, so the project's `.latexmkrc` is the single authority. No engine flag appears in the VS Code config — auto-detection happens in `.latexmkrc`.

## Explicit engine selection

Do not fork or replace the canonical config. When source inspection cannot infer
the intended engine—for example, a font happens to resolve only through
LuaTeX—declare it in the driver:

```tex
% !TEX program = lualatex
```

Accepted values are `pdflatex`, `xelatex`, and `lualatex`. For a one-off terminal
build, pass the matching latexmk flag. An explicit CLI flag wins over automatic
detection.

---

## Reference Checking

Every compilation must verify that all references resolve correctly. After compilation, check the log and report any issues found.

### Reference Check Script

After running latexmk, check for issues and display them as warnings:

```bash
# Compile
latexmk document.tex

# Check for reference issues and report exact problems
LOGFILE="out/document.log"
ISSUES=$(grep -E "(Reference.*undefined|Citation.*undefined|multiply defined)" "$LOGFILE" 2>/dev/null)

if [ -n "$ISSUES" ]; then
    echo ""
    echo "⚠️  REFERENCE ISSUES DETECTED:"
    echo "================================"
    echo "$ISSUES" | while read -r line; do
        echo "  • $line"
    done
    echo "================================"
    echo ""
fi
```

### What to Check For

| Pattern | Meaning |
|---------|---------|
| `Reference .* undefined` | `\ref{}` or `\autoref{}` pointing to non-existent label |
| `Citation .* undefined` | `\cite{}` referencing missing BibTeX entry |
| `Label .* multiply defined` | Same `\label{}` used more than once |

### Manual Compilation (if not using latexmk)

For biblatex (default in working paper template):
```bash
mkdir -p out
xelatex -output-directory=out document.tex
biber out/document
xelatex -output-directory=out document.tex
xelatex -output-directory=out document.tex
cp out/document.pdf ./document.pdf
```

For natbib (if using that instead):
```bash
mkdir -p out
pdflatex -output-directory=out document.tex
bibtex out/document
pdflatex -output-directory=out document.tex
pdflatex -output-directory=out document.tex
cp out/document.pdf ./document.pdf
```
