# Paper Critic — Specialist Mode (`--specialist`)

> Multi-sub-agent variant of the paper-critic agent. The main session splits the 9 check dimensions across **6 parallel sub-agents**, each with a single focused responsibility. Trades token cost for thoroughness — each sub-agent can be exhaustive because it has one job. Referenced by `paper-critic.md`.

## Triggers

User says "specialist review", "technical review", "deep review", or explicitly passes `--specialist`.

## When to use

Large papers (20+ pages), pre-submission reviews, or when a previous single-agent review scored 70–85 (borderline — deeper scrutiny warranted).

## Architecture

| Sub-agent | Dimensions | Persona |
|-----------|-----------|---------|
| **Style & Language** | 1 (Grammar), 4 (Tone) | Copy editor |
| **Consistency & Cross-Refs** | 7 (Internal Consistency), 8 (Tables & Figures) | Fact-checker |
| **Causal Claims & Overclaiming** | 9 (Causal Overclaiming) | Skeptical econometrician |
| **Mathematics & Notation** | 2 (Notation), 10 (Equation Completeness from proofread) | Technical reviewer |
| **LaTeX & Presentation** | 3 (Citation Format), 5 (LaTeX-Specific), 6 (TikZ) | Production editor |
| **Contribution & Scope** | Overall assessment, journal fit, literature gaps | Adversarial referee |

## Orchestration

Done by the main session, not the sub-agent.

1. Read all `.tex` files and construct a single content payload
2. Launch all 6 sub-agents in parallel via the Agent tool, each with its dimension checklist and the paper content
3. Each sub-agent returns findings tagged `[CRITICAL]`, `[MAJOR]`, `[MINOR]` with exact quotes
4. The main session consolidates with this priority order:
   - `[CRITICAL]` from Causal Claims first (highest reviewer attack surface)
   - `[CRITICAL]` from Consistency second
   - `[CRITICAL]` from remaining agents by order
   - All `[MAJOR]` by agent order
   - All `[MINOR]` by agent order
5. Deduplicate (same issue found by multiple agents = higher confidence, not double-counted)
6. Write the standard CRITIC-REPORT.md (see `report-format.md`)

## Standard Forbid-List for Specialist Sub-Agents

Per `~/.claude/rules/subagent-prompt-discipline.md`, sub-agents do not inherit global rules. Include this block in each of the 6 specialist sub-agent prompts:

```
## Scope of action — DO NOT do these things

This sub-agent has a narrow scope: produce findings tagged
[CRITICAL]/[MAJOR]/[MINOR] with exact quotes for the assigned
dimension. Do NOT do any of the following:

- Do NOT modify any `.tex` file. You are read-only on the paper.
- Do NOT run `git add`, `git commit`, `git push`, or any other git
  write command.
- Do NOT run `latexmk` or any build command.
- Do NOT edit `.context/`, `MEMORY.md`, `CLAUDE.md`, `README.md`,
  or any project-level documentation.
- Do NOT edit the project's `.bib` file.
- Do NOT report findings outside your assigned dimension(s).
- Do NOT create files outside your final response.

Return findings only. The main session writes the consolidated report.
```

## When NOT to use

Short papers (<10 pages), discovery-phase drafts, or when token budget is constrained. The standard single-agent mode is sufficient for most reviews.

## Specialist vs. Generalist (Council) Mode

| Mode | Agents | Diversity source | Best for |
|------|--------|-----------------|----------|
| **Standard** (default) | 1 paper-critic agent | — | Quick reviews, short papers |
| **Specialist** (`--specialist`) | 6 focused sub-agents | Role specialisation | Deep technical audit, pre-submission |
| **Generalist council** | 3 LLM providers | Architectural differences | Broad perspective, catching blind spots |

The modes are complementary: specialist mode finds more issues per dimension (depth), while council mode catches issues a single architecture might miss (breadth). For maximum coverage, run specialist mode first, then council mode on the revised draft.

## Parallel Independent Review

For maximum coverage, launch paper-critic alongside `domain-reviewer` and `referee2-reviewer` in parallel (3 Agent tool calls in one message). Each agent checks different dimensions — paper-critic handles grammar, notation, citation, tone, LaTeX, and TikZ. Run `fatal-error-check` first as a pre-flight gate, then launch all three in parallel. After all return, run `/synthesise-reviews` to produce a unified `REVISION-PLAN.md`. See `skills/shared/council-protocol.md` for the full pattern.
