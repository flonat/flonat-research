# Phase 1: Read + Plan

Read in this order:

1. **Atlas topic frontmatter** — title, theme, status, paper title, paper-path, co-authors, institution, **`overleaf_link:`** (top-level or per-output), **`outputs[].status`** (per-venue submission status). These set the book's metadata.
2. **Paper tex** — title, abstract, section structure, headline numerical claims, figure list, theorem statements.
3. **Project README + CLAUDE.md** if they exist — context for the spine.

Produce a one-paragraph plan in your reasoning trace covering:
- Exactly which 8 chapter titles you will write (default skeleton is fine; deviate if the paper structure demands).
- Which figures to copy (paper-cited figures only — don't copy the entire `output/figures/` dir).
- Audience tier (students / practitioners / adjacent-researchers / the user-future-self).
- Whether the paper has executable artefacts to reference, or it's a pure-theory book where chapters cite paper sections.
