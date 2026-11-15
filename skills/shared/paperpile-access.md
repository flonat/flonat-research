# Shared: Paperpile Access — Modes and Authority

Single reference for **which Paperpile source is the authority for what**, in each of the two modes. The rule `rules/paperpile-citations.md` carries the short version; skills link here instead of restating it. Filing and key-reconciliation logic stays in [`reference-resolution.md`](reference-resolution.md).

## The idea

The mode decides who is the authority for **existence, keys and writes**. It never decides where **BibTeX text** comes from.

- **Live** is the authority for existence and keys: the plugin MCP reads Paperpile's backend, so a paper added a minute ago is visible.
- **Export** is the authority for text and offline work: only the local JSON export yields Paperpile-formatted BibTeX, and only the CLI works in scripts, cron and sub-agents. The export lags the backend by up to a day.

Check the current state: `bash scripts/bib/paperpile-mode.sh status` → e.g. `live (file) · export 5h old`. Switch: `paperpile-mode.sh set live|export` (per machine); one-off: `PAPERPILE_MODE=live …`. Default and fallback is `export`.

## Matrix

| Operation | `export` mode | `live` mode (main session only) | Always export-backed |
|---|---|---|---|
| Is X in the library? What is its key? | CLI chain via `scripts/bib/resolve-ref.py` | Connector first: `get_references_from_library` (`dois=[…]` or `citekeys=[…]`; `search_library` for title and DOI-less queries); run `resolve-ref.py` as the CLI cross-check | Scripts and sub-agents have no connector: CLI only |
| May I cite a key now? | Only keys the export knows | Any key the connector returns | |
| Add a new paper | Stage a verified-DOI `.bib` under `<project>/.paperpile-import/`; the user imports; minted export returns | `lookup_papers` (verify DOI) → show the list → on the user's yes `save_to_library` → read the key back | If `save_to_library` fails: staging flow |
| Organise: labels, folders, stars, notes | By hand in Paperpile | `update_references` / `update_collections` after showing the diff; folders by ID, never by name | |
| File cited papers in folders | By hand | Topic folder (working pool): after new citations or a rebuild, list the cited keys not directly in it and add them on the user's yes; add only. Output subfolder (one paper's final reference list): at submission, list additions and no-longer-cited papers and apply on his yes. Folder IDs come from the project `CLAUDE.md`. `rules/paperpile-citations.md` § Live mode, item 5 | |
| Trash a record, delete a folder or label | By hand | Only on an explicit yes | |
| Replace a record with a newer version | By hand | Save the new record, swap the key in every manuscript and bibliography, then trash the old one (the plugin can edit fields but not a record's `type`, and preprint to published is a type change) | |
| BibTeX text for the active `.bib` | `paperpile export-bib` | `paperpile export-bib` (the plugin has no BibTeX) | **Yes** |
| `citation_lint`, `rekey_to_canonical`, validator library check | Export | Export | **Yes** |
| Full-text PDF reading | `paperpile get-pdf-*` | Same (`get_text_content` is the connector's equivalent; the CLI is the tested path) | Yes |
| Sub-agents, cron, offline | CLI | CLI | **Yes** |

## Pending export (an expected state, not an error)

A key saved live but not yet in the export is **pending export**:

- It **can be cited at once**: live-minted keys equalled the export's keys 18/18 (verified 2026-11-06).
- Its `.bib` entry cannot come from `export-bib` yet: `rebuild_paperpile_bib.py` exports every other cited key and carries a pending key only if its entry sits below a `% PROVISIONAL` line at the end of the current `.bib`, replacing it once the export has the key. Do not hand-author the entry from memory or Crossref. If a provisional entry is unavoidable, build it only from the live record, mark it `% PROVISIONAL (from live record, <date>)`, and replace it with `export-bib` output after the next export.
- `citation_lint.py` and `rekey_to_canonical.py` flag such keys `NOT_FOUND` / `NON-CANONICAL-BUT-PRESENT` until the export catches up. Confirm them with the connector instead and move on; the flags self-clear.
- Sub-agents cannot see pending keys. Pass them in `APPROVED_CITATIONS`.

## Fallback (mandatory)

Any live call that times out or errors: say so in one line, continue with the export column of the matrix, never retry in a loop, never block citation work. First-call timeouts are normal (beta cold start); one retry is fine. On the Mini the OAuth tokens sit in the login keychain: a locked keychain makes live calls fail, so the fallback applies.

## Tool names

Bare names below; each client adds its own prefix (the plugin's MCP namespace in Claude Code, the `paperpile` server in Codex; exact forms are in the guide).

- Read, allow-listed in Claude: `get_libraries`, `get_collections_from_library`, `get_references_from_library`, `search_library`, `get_text_content`, `find_papers`, `lookup_papers`, `get_inbound_cites`, `get_outbound_references`.
- `search_library` (allow-listed 2026-11-07) is the connector route for DOI-less references (tested 2026-11-06: `title:"hypervolume knowledge gradient"` found `Daulton2023-rr`). Pass `search_full_text: false` for a metadata-only title search; it supports `title:`, `author:`, `year:` prefixes. Prefer `get_references_from_library` when you have a DOI or citekey.
- Write (prompt every time): `save_to_library`, `update_references`, `update_collections`, `highlight_text` (untested), `send_paperpile_feedback`.

## Known limits

- No BibTeX export. `update_references` handles folders, labels, stars, trash and notes, and also citation-field edits through `metadata` (checked 2026-11-14): one record per call, the supplied fields replace the old values, the call returns `previous_metadata` so an edit can be undone, `type` cannot be changed, and it cannot be combined with folder or label changes in the same call. Show the user the old and new values before applying a batch.
- `save_to_library` from official BibTeX (checked 2026-11-14): pass `skip_duplicates: false`, `find_pdfs: false` and `wait_for_pdf: false` (a PDF crawl redownloads preprints). Paperpile stores BibTeX case-protection braces literally, so write plain titles (`Bayesian`, not `{B}ayesian`). Set titles in sentence case: proceedings BibTeX is Title Case, the library is not. Read back the returned key and fix a title with `update_references` `metadata`.
- Who cites a key: search the Overleaf folders directly (`<Dropbox>/Apps/Overleaf`, TexLite; resolve the root per machine). `grep -r` from a project tree does not follow the `paper/` symlinks into Overleaf, so it misses live manuscripts. Do this before trashing any record.
- `save_to_library` by DOI can fail on malformed Crossref metadata (`invalid_field_format`, e.g. `conference_date`); saving from verified BibTeX worked.
- Several folders share one name (four "NeurIPS 26"): address by ID.
- Live writes change the real library: batch, list first, prefer reversible operations.

Guide with setup and per-machine state: `docs/guides/paperpile-live-mode.md`.
