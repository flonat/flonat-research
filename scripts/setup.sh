#!/usr/bin/env bash
# Thin launcher for the client-neutral installer.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v uv >/dev/null 2>&1; then
  echo "setup: uv is required (https://docs.astral.sh/uv/)" >&2
  exit 1
fi
exec uv run --no-project python "$REPO_DIR/scripts/install.py" "$@"
