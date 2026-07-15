---
description: Use when you need to create a preprint / working-paper variant of a paper
  currently in conference or journal format. Forks the existing Overleaf project —
  adds a `preprint/` subfolder using the user's `your-template` Template, ports the
  body content from the source paper. The preprint is accessed locally via the existing
  `paper-{venue}/paper/preprint/` path (subfolder under the conference paper's symlink);
  no separate `paper-wp/` directory. Trigger on "set up a working paper", "create
  a preprint", "WP version", "arXiv-ready version", "ready to preprint". Never creates
  a new top-level Overleaf project — always nests inside the existing one. Never uses
  the conference's own style (.sty / .cls); always swaps to `your-template`.
---

# Shared skill adapter

Read and follow `~/.claude/shared-skills/preprint/SKILL.md`. Resolve bundled resources relative to `~/.claude/shared-skills/preprint/`.
