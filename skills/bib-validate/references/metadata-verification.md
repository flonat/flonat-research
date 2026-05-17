# Optional Metadata Verification

When missing entries or suspicious metadata are flagged, check these sources in order:

1. **Paperpile** — call `paperpile search-library` by title. If found, use `paperpile export-bib` to get correct BibTeX.
2. **`scholarly` CLI** (multi-source scholarly search — shells out, works in main context AND sub-agents):
   - **`scholarly scholarly-search "<title>" --json`** — search by title across OpenAlex + S2 + Scopus + WoS
   - **`scholarly scholarly-verify-dois --dois D1,D2,... --json`** — batch-verify DOIs across all sources (preferred over manual DOI resolution)
   - **`scholarly scholarly-paper-detail <paper_id> --json`** — get full metadata including pre-formatted BibTeX (via S2 `citationStyles`), TLDR summary, and open access PDF link. Use for auto-generating BibTeX entries for missing references.
   - **`scholarly scholarly-citations <paper_id> --json`** / **`scholarly scholarly-references <paper_id> --json`** — check citation context (how many papers cite this? what does it cite?) to assess relevance when deciding whether to keep or drop questionable entries
   - **`scholarly openalex-lookup-doi <doi> --json`** — look up full metadata for a specific DOI

For Python client fallback (citation networks, institution analysis): see `openalex-verification.md`
