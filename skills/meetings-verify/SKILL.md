---
name: meetings-verify
description: Verify that the meeting-transcribe pipeline is properly set up — whisper/ffmpeg/uv binaries, models, package venv, watcher, and folders. Use when the user says "is transcription working", "check my meeting setup", "verify minutes", "why isn't transcription working", "meeting health check".
user_invocable: true
---

# meetings-verify

Run a health check on the **meeting-transcribe** pipeline (the local whisper.cpp + sherpa-onnx tool that replaced the old `minutes` transcription binary).

## How to verify

```bash
bash "<skills-root>/meetings-verify/scripts/verify-setup.sh"
```

The script prints PASS/WARN/FAIL per component on the Mini. On another host it
prints `SKIPPED(not this host)` for the Mini-only pipeline and verifies only the
Syncthing-delivered meeting output. Read the output and report results without
turning an intentional skip into a failure.

## What gets checked

| Check | What it verifies |
|-------|-----------------|
| Binaries | `whisper-cli`, `ffmpeg`, `uv` on PATH |
| Models | `ggml-large-v3.bin`, `ggml-silero-v6.2.0.bin`, diarization `segmentation.onnx` + `embedding.onnx` under `~/.config/meeting-transcribe/models/` |
| Package | `meeting_transcribe` + `sherpa_onnx` + `soundfile` import in the package venv |
| Watcher | `com.user.meeting-transcribe` launchd job loaded |
| Inbox | `MEETING_INBOX_DIR` or the launchd plist's first `WatchPaths` entry exists |
| Output | `~/vault/meetings/` exists |

## After verification

If checks fail:

- **Binary missing** → `brew install whisper-cpp ffmpeg`; install `uv`
- **Model missing** → whisper/VAD live in `~/.config/meeting-transcribe/models/`; diarization models download from sherpa-onnx releases (see the package README)
- **Package import fails** → `cd ~/Task-Management/packages/meeting-transcribe && uv sync` (needs Python 3.12 — sherpa-onnx wheels are broken on 3.13)
- **Watcher not loaded** → `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.meeting-transcribe.plist` (manual CLI `transcribe-meeting <file>` works regardless)
- **Inbox missing** → verify `MEETING_INBOX_DIR` or the launchd plist's `WatchPaths` entry, then create that configured directory

## Gotchas

- **Mac Mini only** — the watcher is a Mini launchd job; the inbox path is the Mini Dropbox path. The MacBook has no watcher.
- **Python 3.12 required** — sherpa-onnx's 3.13 wheel ships a broken onnxruntime dylib. The package pins 3.12 via `.python-version`.
- **WARN ≠ broken** — a missing watcher only means auto-processing is off; the `transcribe-meeting` CLI still works.
