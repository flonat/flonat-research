# Paper Critic — Council Mode

> Multi-model deliberation variant. 3 different LLM providers (Claude, GPT, Gemini) independently review the paper, cross-evaluate each other's assessments, and a chairman synthesises the final CRITIC-REPORT.md. Referenced by `paper-critic.md`.
>
> **This document is addressed to the main session, not the sub-agent.** When council mode is triggered (user says "council mode", "council review", or "thorough quality check"), the main session orchestrates using the `council-api` Python package (or `council-cli`) — it does NOT launch a single paper-critic agent.

## How to Orchestrate

1. Run **pre-flight**: hard gates (compilation, references, citations, page limit). If any fails, stop.
2. Read the shared council protocol: `~/.claude/skills/shared/council-protocol.md`
3. Read the reference files (siblings to this one):
   - Personas: `~/.claude/agents/references/paper-critic/council-personas.md`
   - Prompts: `~/.claude/agents/references/paper-critic/council-prompts.md`
4. Construct a **system prompt** from the agent's core instructions (Check Dimensions, Severity Tiers, Scoring, Report Format)
5. Construct a **user message** from the paper content (all `.tex` files, `.bib` files, `.log` warnings)
6. Invoke `council-api` via CLI or Python — the library handles all 3 stages via OpenRouter:
   ```bash
   uv run python -m council_api \
       --system-prompt-file /tmp/critic-system.txt \
       --user-message-file /tmp/critic-user.txt \
       --models "anthropic/claude-sonnet-4.5,openai/gpt-5,google/gemini-2.5-pro" \
       --chairman "anthropic/claude-sonnet-4.5" \
       --output /tmp/council-result.json
   ```
7. Parse the JSON result and format as CRITIC-REPORT.md (see `report-format.md`) with Council Notes and Metadata appended.

## Alternative: CLI Backend (Free with Subscriptions)

Instead of OpenRouter, use `council-cli` to run the council via local CLI tools (Gemini CLI, Codex CLI, Claude Code). Same 3-stage protocol, no per-token cost:

```bash
cd "$(cat ~/.config/task-mgmt/path)/packages/council-cli"
uv run python -m council_cli \
    --prompt-file /tmp/critic-prompt.txt \
    --context-file /tmp/critic-paper.txt \
    --output-md /tmp/critic-council-report.md \
    --chairman claude \
    --timeout 180
```

Where `--context-file` contains the paper content (`.tex` source) and `--prompt-file` contains the review instructions (derived from the agent's Check Dimensions and Scoring sections). Parse the markdown report and format as CRITIC-REPORT.md.

**When to use which:**
- **`council-cli`** (default) — free with existing subscriptions, good for routine reviews
- **`council-api`** (OpenRouter) — when you need structured JSON output or specific model versions

## Key Details

- **3 models from different providers** — diversity comes from architectural differences, not persona prompts
- **Personas** (Technical Rigour, Presentation, Scholarly Standards) are optional additional emphasis — defined in `council-personas.md`
- **Cross-dimension triage:** When the chairman synthesises reports, apply this priority order to resolve conflicts and rank issues: Internal Consistency > Notation > Citation > Tables & Figures > Grammar > Tone > LaTeX > TikZ. A Critical notation error outranks a Critical tone issue. This prevents surface-level issues from drowning out substantive ones in the final report.
- **Output:** Standard CRITIC-REPORT.md format with Council Notes and Council Metadata appended — fully compatible with the fixer agent
- **Cost:** `council-cli` = free (subscription-included); `council-api` = 7 OpenRouter API calls
