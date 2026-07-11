#!/bin/bash
# Compatibility-named, fail-open adapter to the files-first neutral context core.

set -u

REGISTRY="$HOME/.config/task-mgmt/path"
LOG_DIR="$HOME/Library/Logs"
LOG_FILE="$LOG_DIR/ai-context-hook.log"

[ -f "$REGISTRY" ] || exit 0
TM="$(head -1 "$REGISTRY" | tr -d '\n')"
[ -d "$TM" ] || exit 0
mkdir -p "$LOG_DIR"

ACTION="${1:-}"
CLIENT="${2:-}"
EVENT="${3:-}"
MODE="${4:-normal}"

case "$ACTION" in
  assemble)
    ARGS=(assemble --client "$CLIENT" --event "$EVENT" --mode "$MODE" --output hook)
    ;;
  save-compaction)
    ARGS=(save-compaction --client "$CLIENT" --mode "$MODE")
    ;;
  restore-compaction)
    ARGS=(restore-compaction --client "$CLIENT" --mode "$MODE" --output hook)
    ;;
  *)
    printf '{"systemMessage":"AI context adapter ignored an unknown action"}\n'
    exit 0
    ;;
esac

if ! uv run --project "$TM" python "$TM/scripts/ai-context.py" "${ARGS[@]}" 2>> "$LOG_FILE"; then
  printf '{"systemMessage":"Shared file context was unavailable; read project .context files directly"}\n'
fi
exit 0
