# Contributing to flonat-research

Canonical public content is client-neutral. Add research workflows to
`skills/`, agents to `agents/`, policies to `rules/`, and durable context to
files. `.claude/`, `.codex/`, `CLAUDE.md`, and `AGENTS.md` are adapter surfaces.

Every distributed skill and agent must declare:

- supported `clients` with no implicit `both` default;
- semantic `requires` capabilities;
- its public path and transformation; and
- a short targeting rationale.

Use relative sibling paths in canonical bodies. Do not embed `/Users/<name>/`,
`/Volumes/...`, cloud-storage home paths, client-home paths, credentials,
transcripts, or machine inventory. If a workflow names an MCP-only operation,
either provide a CLI fallback for Codex in the same instructions or mark the
asset Claude-only.

Before proposing a change:

1. validate the capability contract;
2. render twice and confirm byte-identical output;
3. install into isolated Claude, Codex, and both-client homes;
4. run `--check` and confirm shared skill names are disjoint;
5. run documentation and leak checks; and
6. inspect generated adapters rather than editing them directly.

Report suspected private identifiers or secrets without reproducing the value
in a public issue. Existing user settings and unmanaged home files must remain
outside the renderer's ownership.
