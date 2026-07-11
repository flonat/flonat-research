# Referee 2 — Council Mode (Optional)

> Multi-model deliberation variant of referee2-reviewer. 3 different LLM providers independently run the full audit protocol, cross-review each other's findings, and a chairman synthesises the final report. Referenced by `referee2-reviewer.md`.
>
> **This document is addressed to the main session, not the sub-agent.** When council mode is triggered (user says "council mode", "council review", or "thorough referee 2"), the main session orchestrates — it does NOT launch a single referee2-reviewer agent.

## Trigger

"Council referee 2", "thorough audit", "council code review" (in the formal audit sense).

## Why council mode is especially valuable here

The 5-audit protocol (code review, replication, paper critique, cross-reference, statistical) is where model diversity matters most. Different models have genuinely different strengths at finding bugs, statistical errors, and replication failures. A code bug that Claude misses, GPT or Gemini may catch — and vice versa.

## Invocation (CLI backend — default, free with existing subscriptions)

```bash
cd "$(cat ~/.config/task-mgmt/path)/packages/council-cli"
uv run python -m council_cli \
    --prompt-file /tmp/referee2-prompt.txt \
    --context-file /tmp/referee2-paper-and-code.txt \
    --output-md /tmp/referee2-council-report.md \
    --chairman claude \
    --timeout 300
```

## Invocation (API backend — structured JSON)

```bash
cd "$(cat ~/.config/task-mgmt/path)/packages/council-api"
uv run python -m council_api \
    --system-prompt-file /tmp/referee2-system.txt \
    --user-message-file /tmp/referee2-content.txt \
    --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
    --chairman "anthropic/claude-sonnet-4.5" \
    --output /tmp/referee2-council-result.json
```

See `skills/shared/council-protocol.md` for the full orchestration protocol.
