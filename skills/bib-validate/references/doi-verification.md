# DOI Verification Protocol

## Hard Rules

1. Run only on `@article`, `@inproceedings`, `@incollection`, `@phdthesis`, `@mastersthesis` entries (skip `@misc`, `@unpublished`, `@manual`).
2. Batch DOI lookups via `scholarly scholarly-verify-dois --dois D1,D2,...` (CLI accepts ≤50 per call). For >50 entries, split into batches.
3. For each entry:
   - **Has DOI in .bib + resolves**: PASS
   - **Has DOI in .bib + does NOT resolve**: FAIL (likely typo'd or fabricated; flag for user review)
   - **No DOI in .bib + Crossref title-search returns ≥0.95 confidence match**: WARN (suggest adding the DOI)
   - **No DOI in .bib + no Crossref match**: WARN with HIGH severity (likely fabricated entry; recommend removing or replacing)

4. Output: `bib-doi-verification-{date}.md` table with columns: key, has_doi, resolves, suggested_doi, severity.
5. For new `.bib` entries (added in last commit or staged), run automatically without `--verify-doi` flag if the user invokes from `/session-close` Phase 4. Otherwise opt-in.

Performance: ~10 entries/sec via batched calls. A 100-entry bib takes ~10s.

**Citation key rule:** Existing keys in the project always take precedence. They come from the user's reference management system and are canonical. When suggesting replacements (typo corrections, preprint upgrades, metadata fixes), always keep the user's key and update the `.bib` entry metadata around it — never suggest renaming a key to match some "standard" format.

## DOI Resolution (optional — triggered by `--verify-dois` flag or when issues are suspected)

**Preferred method: `scholarly scholarly-verify-dois`.** Collect all DOIs from the `.bib` file and run the CLI (up to 50 per call):

```bash
scholarly scholarly-verify-dois --dois DOI1,DOI2,DOI3 --json
```

This batch-verifies each DOI against all enabled sources (OpenAlex, Scopus, WoS). Results:
- **VERIFIED** (2+ sources confirm) — DOI is valid, metadata can be trusted
- **SINGLE_SOURCE** (1 source only) — DOI exists but warrants a manual spot-check
- **NOT_FOUND** — DOI not found in any source; resolve manually via web fetch

**Fallback for NOT_FOUND DOIs:** Resolve via `https://doi.org/[DOI]` and confirm the returned metadata matches the entry:

1. **Title match**: Does the DOI landing page title match the `.bib` title?
2. **Author match**: Does the first author on the landing page match the `.bib` first author?
3. **Journal match**: Does the venue match?

Flag mismatches as:
- **Warning: DOI mismatch** — DOI resolves to a different paper than claimed. This usually means the DOI is wrong (adjacent DOI in the same journal volume) or the authors are wrong (conflation of researchers in the same subfield).

This check catches:
- Wrong DOIs (e.g., off-by-one in the DOI suffix)
- Author conflation (real researchers incorrectly attributed to a paper)
- Metadata copied from secondary sources without verification

For manual web fetch resolution, process in batches of 5 to avoid rate limiting. Only flag confirmed mismatches — if the DOI cannot be resolved (404, timeout), note it as "unresolvable" at Info level.

## Fabrication Detection (LLM-drafted bibliographies)

A `.bib` entry can be **internally consistent but externally false** — plausible-sounding title + plausible authors + plausible year, but no such paper exists. This pattern is common in bibliographies drafted with LLM assistance, where the model invents a citation that "would fit" the prose. Standard DOI checks miss it because the entry has no DOI to verify.

**Detection rule.** When `scholarly scholarly-verify-dois` returns NOT_FOUND for a DOI, OR when an entry has no DOI at all, run `scholarly scholarly-search "<title>" --json` and apply this matrix to the top result:

| Title agreement | First-author surname agreement | Year agreement | Verdict |
|-----------------|--------------------------------|----------------|---------|
| ✓ | ✓ | ✓ or ±1 | OK |
| ✓ | ✗ | any | **likely fabricated** (right title, wrong authors → invented citation glued to a real paper's title) |
| ✗ | ✓ | any | **likely fabricated** (right authors, wrong title → invented paper attributed to real researchers) |
| ✗ | ✗ | any | **likely fabricated or severely miscited** |
| no usable result (top score < 20) | — | — | **likely fabricated or unindexed** |

Flag fabricated entries as:
- **Major: likely fabricated reference** — entry has plausible structure but cannot be matched to a real publication. Common in LLM-drafted bibliographies. Verify the source manually before citing.

**Discipline.** Do not force a weak match to fill the cell, and do not silently "correct" what looks like a citation error — the user needs to see the failure and judge. Budget at most one reworded query per entry; after that, record the verdict and move on. If a large share of entries (say >10%) flag as likely fabricated, surface a single-line warning above the report (e.g. `7 of 51 entries flag as likely fabricated — review before submission`).

**What this catches that the existing DOI mismatch check misses:** entries that were never assigned a DOI (because they don't exist) but whose `title` / `author` / `year` happen to look reasonable.
