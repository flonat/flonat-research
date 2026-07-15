<!-- Governed by: skills/shared/project-documentation.md -->

# Council mode

Claude Code or Codex can invoke other model providers' CLI tools as subprocess
reviewers. A different model then reviews the work, providing architectural
diversity through different training data, reasoning patterns, and blind spots.
The system is extensible: any CLI tool that accepts a prompt and returns text
can be wrapped as a backend.

Council mode coordinates this into a structured three-stage protocol:
independent assessments, anonymised cross-review, then chair synthesis. It is
used by the `paper-critic` agent and can be called from skills such as
`proofread`, `devils-advocate`, `code-review`, and `multi-perspective`.

See `skills/shared/council-protocol.md` for the full orchestration protocol.

## CLI council (`packages/council-cli/`)

Uses local CLI tools with existing subscriptions (no per-token cost). Backends are pluggable — adding a new provider follows the `BackendSpec` pattern:

```bash
cd packages/council-cli
uv run python -m council_cli --check
```

Currently available backends:
- [Gemini CLI](https://github.com/google-gemini/gemini-cli) — `npm install -g @google/gemini-cli`
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — useful for fresh context (same model, different session)
- Additional backends can be added by implementing a `BackendSpec` in `config.py` and a thin async wrapper in `backends/`

## API council (`packages/council-api/`)

Uses OpenRouter for structured JSON output and programmatic integration:

```bash
cd packages/council-api
uv run python -m council_api --help
```

The API package requires a compatible provider credential, commonly an
[OpenRouter](https://openrouter.ai/) key. Keep the credential in your operating
system's secret store or environment, never in this repository. See the
package's `README.md` for current providers and the Python API.
