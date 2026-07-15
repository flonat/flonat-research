# Hooks

> 9 optional Claude Code hook scripts over the shared files-first context layer.

Hook scripts live canonically in `hooks/`; the Claude adapter registers selected copies under its `"hooks"` key.
They are not active in Codex and are not required for cross-client continuity.

## Overview

| Hook | Trigger | What it does |
|------|---------|-------------|
| `block-destructive-git.sh` | Before Bash | catches dangerous git/shell commands |
| `context-monitor.py` | After tool use | tracks tool call count as a heuristic for context usage |
| `handoff-read.sh` | SessionStart | surface the shared project handoff when it targets Claude |
| `postcompact-restore.py` | After compact | restores state after context compression |
| `precompact-autosave.py` | Before compact | saves state before context compression |
| `promise-checker.sh` | Session stop | catches "performative compliance": Claude says it remembered/noted/saved |
| `protect-source-files.sh` | Before edit/write | prompts confirmation for files outside |
| `resume-context-loader.sh` | Session resume | surfaces current focus and latest session log |
| `startup-context-loader.sh` | Unknown | Compatibility-named, fail-open adapter to the files-first neutral context core |

## Hook Events

| Event | When it fires | Matcher options |
|-------|---------------|-----------------|
| `SessionStart` | Session begins | `startup` (fresh), `resume` (continuing), `compact` (after compaction) |
| `PreToolUse` | Before a tool runs | Tool name(s), e.g. `Bash`, `Edit\|Write` |
| `PostToolUse` | After a tool runs | Tool name(s), e.g. `Bash\|Task` |
| `Stop` | Claude stops responding | *(empty = always)* |
| `PreCompact` | Before context compression | *(empty = always)* |

## Configuration

All hooks are configured in `~/.claude/settings.json`. See the `settings.json` file for the full configuration.

## Creating New Hooks

1. Write a shell or Python script in the repository `hooks/` directory
2. Declare the Claude event mapping and a Codex strategy or explicit files-first fallback
3. Render, validate the matcher, and measure its latency before installation
