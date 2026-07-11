#!/bin/bash
# handoff-read.sh
# SessionStart hook — surface the shared project handoff when it targets Claude.
# The shared handoff is persistent; the receiving client maintains its lifecycle.
#
# A legacy root handoff.md remains one-shot during migration.

HANDOFF="$(pwd)/.context/ai-handoff.md"
LEGACY_HANDOFF="$(pwd)/handoff.md"

if [ -f "$HANDOFF" ]; then
    TO=$(awk -F ': *' '$1 == "to" {print $2; exit}' "$HANDOFF")
    STATUS=$(awk -F ': *' '$1 == "status" {print $2; exit}' "$HANDOFF")

    case "$TO" in
        claude|either) ;;
        *) exit 0 ;;
    esac

    [ "$STATUS" = "complete" ] && exit 0

    CONTENT=$(cat "$HANDOFF")
    [ -z "$CONTENT" ] && exit 0

    WRAPPED="# Shared project handoff

(Auto-injected from .context/ai-handoff.md. This file persists; acknowledge it and maintain its status/log.)

$CONTENT"
elif [ -f "$LEGACY_HANDOFF" ]; then
    CONTENT=$(cat "$LEGACY_HANDOFF")
    [ -z "$CONTENT" ] && { rm -f "$LEGACY_HANDOFF"; exit 0; }
    rm -f "$LEGACY_HANDOFF"
    WRAPPED="# Legacy handoff from previous Claude session

(Auto-injected from handoff.md and deleted. New handoffs use .context/ai-handoff.md.)

$CONTENT"
else
    exit 0
fi

CONTEXT_ESCAPED=$(printf '%s' "$WRAPPED" | jq -Rs .)

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": $CONTEXT_ESCAPED
  }
}
EOF

exit 0
