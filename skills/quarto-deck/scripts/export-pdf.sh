#!/usr/bin/env bash
# Export a Quarto Reveal.js deck to PDF (and optionally PNG pages for a visual
# check) with the locally installed Chrome.
#
# Usage:
#   bash export-pdf.sh <deck.qmd|deck.html> [out.pdf] [--profile NAME] [--png DIR]
#
#   deck.qmd        rendered first with `quarto render --to revealjs` (plus the
#                   profile, if given), then the newest <stem>.html is printed
#   deck.html       printed as-is (already rendered)
#   --profile NAME  Quarto profile for the render, e.g. a static "handout"
#                   profile in a project whose live decks use webR
#   --png DIR       also write one PNG per page (pdftoppm, 60 dpi) to DIR
#
# Needs Node.js and Google Chrome (CHROME=/path/to/chrome overrides the macOS
# default). puppeteer-core is installed once into a cache directory outside the
# skill and the project; it downloads no browser.

set -euo pipefail

SKILL_SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/quarto-deck-print"
export CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

INPUT=""; OUT=""; PROFILE=""; PNG_DIR=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="${2:?--profile needs a name}"; shift 2 ;;
    --png) PNG_DIR="${2:?--png needs a directory}"; shift 2 ;;
    -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
    *) if [[ -z "$INPUT" ]]; then INPUT="$1"; elif [[ -z "$OUT" ]]; then OUT="$1"; else echo "unexpected argument: $1" >&2; exit 2; fi; shift ;;
  esac
done
[[ -n "$INPUT" && -f "$INPUT" ]] || { echo "usage: bash export-pdf.sh <deck.qmd|deck.html> [out.pdf] [--profile NAME] [--png DIR]" >&2; exit 2; }
[[ -x "$CHROME" ]] || { echo "error: Chrome not found at: $CHROME (set CHROME=...)" >&2; exit 2; }
command -v node >/dev/null 2>&1 || { echo "error: Node.js not found" >&2; exit 2; }

INPUT="$(cd "$(dirname "$INPUT")" && pwd)/$(basename "$INPUT")"
STEM="$(basename "${INPUT%.*}")"
DECK_DIR="$(dirname "$INPUT")"

if [[ "$INPUT" == *.qmd ]]; then
  command -v quarto >/dev/null 2>&1 || { echo "error: quarto not found" >&2; exit 2; }
  STAMP="$(mktemp)"
  echo "==> Rendering $STEM${PROFILE:+ (profile $PROFILE)}"
  (cd "$DECK_DIR" && quarto render "$(basename "$INPUT")" --to revealjs ${PROFILE:+--profile "$PROFILE"})
  # The HTML may land in a project output-dir; take the newest match rendered now.
  HTML="$(find "$DECK_DIR" -maxdepth 4 -name "$STEM.html" -newer "$STAMP" -print 2>/dev/null | head -1)"
  rm -f "$STAMP"
  [[ -n "$HTML" ]] || { echo "error: render produced no $STEM.html under $DECK_DIR" >&2; exit 2; }
else
  HTML="$INPUT"
fi

OUT="${OUT:-$DECK_DIR/$STEM.pdf}"
mkdir -p "$(dirname "$OUT")"

# One-time install of puppeteer-core next to a copy of the print script (an ES
# module resolves node_modules relative to its own location).
mkdir -p "$CACHE"
cp "$SKILL_SCRIPTS/print-pdf.mjs" "$CACHE/print-pdf.mjs"
if [[ ! -d "$CACHE/node_modules/puppeteer-core" ]] || ! cmp -s "$SKILL_SCRIPTS/package.json" "$CACHE/package.json"; then
  echo "==> Installing puppeteer-core into $CACHE (first run only)"
  cp "$SKILL_SCRIPTS/package.json" "$CACHE/package.json"
  (cd "$CACHE" && npm install --silent --no-audit --no-fund)
fi

echo "==> Printing to PDF"
rm -f "$OUT"
node "$CACHE/print-pdf.mjs" "$HTML" "$OUT"

# A blank export is ~1 KB; a real deck is tens of KB or more.
if [[ ! -s "$OUT" || "$(wc -c < "$OUT")" -lt 20000 ]]; then
  rm -f "$OUT"
  echo "error: PDF missing or blank" >&2
  exit 1
fi

if [[ -n "$PNG_DIR" ]]; then
  command -v pdftoppm >/dev/null 2>&1 || { echo "error: pdftoppm not found (brew install poppler)" >&2; exit 2; }
  mkdir -p "$PNG_DIR"
  pdftoppm -png -r 60 "$OUT" "$PNG_DIR/$STEM"
  echo "==> $(ls "$PNG_DIR"/"$STEM"-*.png | wc -l | tr -d ' ') page images in $PNG_DIR"
fi

echo "PDF: $OUT"
