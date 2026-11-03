#!/usr/bin/env bash
# Scaffold a standalone Quarto Reveal.js deck from the skill's template.
#
# Usage: bash init-deck.sh <target-dir> [deck-name]
#   Creates <target-dir>/<deck-name>.qmd (default: deck), theme.scss, figures/.
#   Never overwrites an existing file. Inside an existing Quarto project (a
#   _quarto.yml in the target or a parent), it copies only the .qmd and keeps
#   the project's own theme and formats.

set -euo pipefail

TARGET="${1:?usage: bash init-deck.sh <target-dir> [deck-name]}"
NAME="${2:-deck}"
TEMPLATES="$(cd "$(dirname "${BASH_SOURCE[0]}")/../templates" && pwd)"

mkdir -p "$TARGET/figures"
TARGET="$(cd "$TARGET" && pwd)"

project_root=""
dir="$TARGET"
while [[ "$dir" != "/" ]]; do
  if [[ -f "$dir/_quarto.yml" ]]; then project_root="$dir"; break; fi
  dir="$(dirname "$dir")"
done

copy_new() {  # copy_new <src> <dest>: refuse to overwrite
  if [[ -e "$2" ]]; then echo "skip (exists): $2"; else cp "$1" "$2"; echo "created: $2"; fi
}

copy_new "$TEMPLATES/deck.qmd" "$TARGET/$NAME.qmd"
if [[ -n "$project_root" ]]; then
  echo "Quarto project found at $project_root: using its theme and formats."
  echo "Edit the format block in $NAME.qmd to match the project (or delete it to inherit)."
else
  copy_new "$TEMPLATES/theme.scss" "$TARGET/theme.scss"
fi

echo
echo "Preview:  quarto preview \"$TARGET/$NAME.qmd\""
echo "Lint:     uv run python <this-skill>/scripts/lint_deck.py \"$TARGET/$NAME.qmd\""
