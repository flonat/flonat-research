# MCP registrations and CLI routes

MCP is one client adapter, not the framework's context or credential layer.
`flonat-research` does not publish private registrations or secrets.

## Client boundary

Claude Code and Claude Desktop can register MCP servers in their documented
configuration surfaces. Codex-compatible workflows must provide a plain CLI
route for the same operation; a workflow that only names an MCP tool is
classified Claude-only. Both clients can always read `AI.md`, `.context/`,
`MEMORY.md`, and `.context/ai-handoff.md` without MCP.

| Capability | Claude route | Codex route |
|---|---|---|
| Scholarly search | Bibliography MCP when configured | `scholarly` CLI |
| Reference library | Library MCP when configured | documented library CLI |
| Task or vault data | Task MCP when configured | documented task CLI |
| Files and project context | Native files or MCP | Native files |
| Web/documentation lookup | Configured MCP or web tools | CLI or native web tools |

The exact available integrations depend on what the user installs. Do not infer
that a registration exists merely because a skill mentions it.

## Safe configuration process

1. Install the service or CLI from its authoritative documentation.
2. Register it only in the selected client's supported configuration surface.
3. Store tokens in the operating-system credential manager or a narrowly scoped
   service account, never in this repository.
4. Verify registrations separately from credentials.
5. If Codex support is claimed, run the CLI fallback from a normal subprocess.

Configuration files and credential values are machine-local. Context and
handoff files remain portable through ordinary project or repository sync.
