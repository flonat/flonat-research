#!/usr/bin/env bash
# meeting-transcribe pipeline health check.
# Checks binaries, models, package venv, watcher, and folders.

PASS="PASS"; FAIL="FAIL"; WARN="WARN"; SKIP="SKIPPED(not this host)"
errors=0

check() {
  local label="$1" status="$2" detail="${3:-}"
  printf "  %-26s %s" "$label" "$status"
  [ -n "$detail" ] && printf "  — %s" "$detail"
  printf "\n"
  [ "$status" = "$FAIL" ] && errors=$((errors + 1))
  return 0
}

TM="$(head -1 "$HOME/.config/task-mgmt/path" 2>/dev/null)"
PKG="$TM/packages/meeting-transcribe"
MODELS="${MEETING_MODEL_DIR:-$HOME/.config/meeting-transcribe/models}"
PLIST="$PKG/launchd/com.user.meeting-transcribe.plist"
INBOX="${MEETING_INBOX_DIR:-}"
if [ -z "$INBOX" ] && [ -f "$PLIST" ]; then
  INBOX="$(/usr/libexec/PlistBuddy -c 'Print :WatchPaths:0' "$PLIST" 2>/dev/null || true)"
fi
OUTPUT="${MEETING_OUTPUT_DIR:-$HOME/vault/meetings}"
HOST_ROLE="${TM_HOST_ROLE:-}"
if [ -z "$HOST_ROLE" ]; then
  host_name="$(scutil --get LocalHostName 2>/dev/null || hostname -s)"
  case "$(printf '%s' "$host_name" | tr '[:upper:]' '[:lower:]')" in
    *mini*) HOST_ROLE="mini" ;;
    *) HOST_ROLE="non-mini" ;;
  esac
fi

echo "meeting-transcribe health check"
echo "================================"

if [ "$HOST_ROLE" != "mini" ]; then
  check "pipeline host" "$SKIP" "watcher, models, and inbox are Mini-only"
  [ -d "$OUTPUT" ] && check "synced meetings output" "$PASS" "$OUTPUT" \
                   || check "synced meetings output" "$WARN" "missing: $OUTPUT"
  echo "================================"
  echo "No local failure: run the full verifier on the Mac mini."
  exit 0
fi

# Binaries
for bin in whisper-cli ffmpeg uv; do
  if command -v "$bin" >/dev/null 2>&1; then
    check "binary: $bin" "$PASS" "$(command -v "$bin")"
  else
    check "binary: $bin" "$FAIL" "not on PATH"
  fi
done

# Models — large-v3 is required; turbo is optional (only needed for --fast).
for m in "ggml-large-v3.bin" "ggml-silero-v6.2.0.bin" \
         "diarization/segmentation.onnx" "diarization/embedding.onnx"; do
  if [ -f "$MODELS/$m" ]; then
    check "model: $m" "$PASS"
  else
    check "model: $m" "$FAIL" "missing at $MODELS/$m"
  fi
done
if [ -f "$MODELS/ggml-large-v3-turbo.bin" ]; then
  check "model: turbo (--fast)" "$PASS"
else
  check "model: turbo (--fast)" "$WARN" "not installed (--fast disabled; large-v3 still works)"
fi

# Package venv + imports
if [ -d "$PKG" ]; then
  if (cd "$PKG" && uv run python -c "import meeting_transcribe, sherpa_onnx, soundfile" >/dev/null 2>&1); then
    check "package venv + imports" "$PASS"
  else
    check "package venv + imports" "$FAIL" "uv run import failed in $PKG"
  fi
else
  check "package dir" "$FAIL" "missing: $PKG"
fi

# Watcher launchd job
if launchctl list 2>/dev/null | grep -q com.user.meeting-transcribe; then
  check "watcher (launchd)" "$PASS" "com.user.meeting-transcribe loaded"
else
  check "watcher (launchd)" "$WARN" "not loaded (manual CLI still works)"
fi

# Folders
if [ -n "$INBOX" ]; then
  [ -d "$INBOX" ] && check "inbox folder" "$PASS" "$INBOX" \
                  || check "inbox folder" "$WARN" "missing: $INBOX"
else
  check "inbox folder" "$WARN" "MEETING_INBOX_DIR/WatchPaths not configured"
fi
[ -d "$OUTPUT" ] && check "meetings output dir" "$PASS" "$OUTPUT" \
                 || check "meetings output dir" "$WARN" "missing: $OUTPUT"

echo "================================"
if [ "$errors" -eq 0 ]; then
  echo "All critical checks passed."
else
  echo "$errors critical check(s) FAILED."
fi
exit "$errors"
