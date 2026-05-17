# Deep Verification Mode (Parallel, Disk-Based)

Triggered by: `--deep-verify` flag, 40+ entries, or "deep verify" / "verify all references". Spawns parallel sub-agents that verify batches and write results to disk. Full architecture, batch JSON format, and assembly details are in `deep-verify.md`.

## Auto-trigger on entry count

When `.bib` has **≥40 entries**, deep-verify mode is **mandatory** — DO NOT run `scholarly scholarly-verify-dois` inline in main context. Spawn sub-agents per the deep-verify architecture immediately, even without an explicit `--deep-verify` flag.

If the user did not request deep-verify but the file crosses the threshold, offer once:

> "Your `.bib` has N entries (≥40). Deep-verify will parallelise DOI checks across sub-agents to avoid main-context bulk calls. Proceed with deep-verify? (recommended)"

For <40 entries, a single inline `scholarly-verify-dois` call (≤50 DOIs) is fine. For 40–80 entries that the user opts to keep inline, dispatch a single Bash sub-agent that runs the batched call and returns merged JSON — see `_shared/cli-dispatch-policy.md`.
