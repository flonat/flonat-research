# System architecture

`flonat-research` separates client-neutral research practice from client
adapters and machine-local installation.

```text
AI.md + .context/ + MEMORY.md + skills/ + agents/ + rules/
                         |
                explicit capability contract
                 /                         \
        Claude adapter                 Codex adapter
 .claude/commands + agents/rules   .agents/skills + .codex/agents
        optional hooks                    AGENTS.md
                 \                         /
                  managed-copy installer
                           |
                 content-addressed receipt
```

## Canonical and generated surfaces

| Surface | Role |
|---|---|
| `AI.md` | Client-neutral project guidance |
| `skills/` | Canonical skill bodies |
| `agents/` | Canonical agent definitions |
| `rules/` | Canonical research and safety policies |
| `.context/`, `MEMORY.md` | Files-first continuity across clients and machines |
| `config/ai-contracts.yaml` | Public client/capability declaration |
| `config/install-manifest.json` | Exact install source-to-target mapping |
| `.claude/` | Generated Claude commands, agents, rules, and settings |
| `.codex/agents/` | Generated Codex TOML agents |
| `CLAUDE.md`, `AGENTS.md` | Generated client entry points |

## Skill discovery

Shared skill bodies are copied to `~/.claude/shared-skills/` for Claude and
`~/.agents/skills/` for Codex. Claude receives small command adapters under
`~/.claude/commands/`. Claude-only skills use `~/.claude/skills/`. Therefore a
shared name is not present in both roots inspected by Codex Desktop.

## Agents, rules, and hooks

Neutral Markdown agents render to Claude Markdown and, when compatible, Codex
TOML. `codex-research` is intentionally Claude-only: it delegates externally to
the Codex CLI and must not recursively become a Codex agent.

Claude loads its rule files and can run hooks. Codex receives applicable
guidance through `AGENTS.md`; the framework does not claim Claude hooks are
active in Codex. Both clients use the same handoff and context files.

## Installation safety

The installer expands every declared source to individual files. It refuses
unsafe paths, symlinked destination parents, unowned legacy links, and
unmanaged conflicts. Updates overwrite only files proven managed by the prior
receipt. Divergent managed copies are backed up first. A successful `--check`
requires both installed bytes and receipt hashes to match the checkout.

## Extending the framework

Add neutral content to `skills/`, `agents/`, or `rules/`, then declare its
clients and semantic requirements. Client-specific behavior belongs in a
generated adapter or an explicitly client-only asset. Any MCP-only instruction
intended for Codex must name a CLI fallback. Absolute user, volume, and cloud
storage paths are not portable public source.
