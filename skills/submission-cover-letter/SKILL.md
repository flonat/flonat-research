---
name: submission-cover-letter
description: Draft, revise, and compile evidence-grounded cover letters for journal and conference submissions. Use whenever a user asks to prepare a submission cover letter, revise an editor letter, adapt a past cover letter to a new venue, migrate editable cover-letter sources into Overleaf for coauthor collaboration, or complete cover-letter items identified by a submission checklist. Inventory the user's past submission correspondence, read the current venue requirements and manuscript metadata, preserve double-blind boundaries, and expose unresolved declarations instead of guessing.
---

# Submission Cover Letter

Create a venue-specific editorial letter from current evidence and the user's own correspondence precedents. Treat the letter as submission collateral: it may carry identities and declarations that must remain outside a blinded manuscript.

## Phase 1: Resolve the live submission

1. Read the project guidance, active handoff/current-focus files, and the applicable submission checklist or compliance report.
2. Identify the active `paper-<venue>/` directory and manuscript driver. Do not draft from a deferred, rejected, fallback, or archived paper arm when a live arm exists.
3. Determine whether the request is an initial submission, resubmission, or revision. A response-to-reviewers document is a different artifact; use the review-response workflow for that document.
4. If the project or active paper arm is ambiguous, ask before writing.

## Phase 2: Build the evidence packet

Build an inventory of prior submission correspondence before selecting precedents:

1. Use a project- or workspace-provided submission-collateral index when one exists, and refresh it with the documented workspace command.
2. Otherwise search only the user-authorized project and correspondence directories for prior cover letters and immutable as-sent archives. Do not crawl unrelated home directories.
3. If no precedents are accessible, say so and use a minimal venue-specific format rather than inventing a house style.

Select two or three cover-letter precedents and rank candidates in this order:

1. Same correspondence function: initial submission, revision, or resubmission.
2. Same venue, publisher family, or submission model.
3. Same paper type, research domain, and authorship shape.
4. Recency.

Read the source letters, not only their index entries. Use their structure and stable house style, but do not inherit obsolete titles, claims, affiliations, article types, editors, or declarations.

Read the current evidence in this authority order:

- official venue guidelines or a current project capture of them;
- the live manuscript's title, abstract, introduction, conclusion, and availability statements;
- the matching Research Vault submission record for venue, article type, author order, and status;
- author/person records and the current author block for affiliations and contact details;
- project checklists or coauthor-approved notes for contributions, acknowledgements, funding, competing interests, related manuscripts, and prior editor contact.

When a referenced venue page or rule may have changed and no current capture exists, verify it against the official venue source before drafting.

## Phase 3: Create a requirement ledger

Before writing prose, classify every potentially required item as `CONFIRMED`, `NEEDS CONFIRMATION`, or `NOT REQUIRED`:

- manuscript title, article type, and venue;
- editorial significance and venue fit;
- two or three contribution claims supported by the current manuscript;
- author names, order, affiliations, and corresponding-author contact;
- author contributions and any equal-contribution statement;
- acknowledgements and funding;
- complete competing-interests declaration;
- related manuscripts under consideration or in press;
- prior discussions with an editor;
- originality, exclusive consideration, and all-author approval;
- data, code, software-form, repository, DOI, or anonymous-artifact statements requested by the venue.

Do not infer declarations from silence. In particular, never invent CRediT roles, equal contribution, funding status, conflicts, related submissions, prior editor contact, or coauthor approval. Use a visible `[CONFIRM: ...]` marker in the draft when the fact is unresolved, and list the same blockers in the handoff.

## Phase 4: Draft the letter

When `paper-<venue>/paper/` is an Overleaf symlink, write or revise the canonical editable source at `paper-<venue>/paper/cover-letter/cover-letter.tex`. This dedicated Overleaf subfolder gives coauthors access without mixing the letter into the manuscript's root-file sequence. Maintain a relative compatibility symlink at `paper-<venue>/submission/cover-letter.tex` pointing to `../paper/cover-letter/cover-letter.tex`; verify that it resolves before compiling. If the paper has no Overleaf collaboration surface, use `paper-<venue>/submission/cover-letter.tex` as the canonical source instead.

Move only editable source files when adopting this layout. Never relocate, replace, or relabel human-supplied as-sent PDFs under `submission/archive/`; those are immutable provenance records.

When migrating an already-sent letter, compare its rendered date with the immutable as-sent PDF. The standard LaTeX `letter` class inserts `\today` when no date is declared, so add an explicit `\date{<original submission date>}` when necessary. Treat this as provenance-preserving metadata: do not otherwise rewrite the historical source, and never modify the archive PDF.

Follow this argument order unless the venue prescribes another:

1. Address the editors and identify the manuscript, article type, and submission request.
2. Explain the problem and why it matters to the venue's readership.
3. State two or three supported contributions, using the paper's calibrated claim scope.
4. Explain venue fit with a concrete link to the journal's remit.
5. Provide required administrative disclosures and declarations.
6. Close briefly on behalf of the authors.

Use US English and sentence-case manuscript titles. Prefer one page; allow a second page when mandatory disclosures require it. Do not compress by dropping required declarations.

Use the closest precedent's restrained visual format. If no suitable source exists, use a minimal standard LaTeX `letter` document. Avoid decorative branding unless the precedent establishes it.

Do not paste the abstract or make unsupported promotional claims. Prefer qualitative result descriptions. If a numerical result is necessary, import it from a generated manuscript macro; when no reusable macro exists, keep the wording qualitative rather than retyping a computed result.

For double-blind submissions, follow the venue's editorial instructions. Author identities may appear in a cover letter seen only by editors when requested, but must not leak into the blinded manuscript, supplement, anonymous artifact, or reviewer-facing source bundle. Never `\input` the cover letter from the manuscript or supplement. When source files are uploaded for review, construct an explicit bundle that excludes the Overleaf `cover-letter/` subfolder; do not upload the whole Overleaf project blindly. Include an anonymous repository URL only when the venue permits it and the link has passed the anonymity workflow.

## Phase 5: Validate and compile

1. Check the title, venue, article type, author order, affiliations, and correspondence details against their current sources.
2. Trace every substantive claim to the live manuscript and remove claims inherited only from a precedent.
3. Search for unresolved markers. Treat each `[CONFIRM: ...]` item as a submission blocker, not a cosmetic TODO.
4. Invoke the `latex` skill through `paper-<venue>/submission/cover-letter.tex` when the compatibility symlink exists. This keeps build artifacts in `submission/out/` and the verified uploadable PDF at `submission/cover-letter.pdf` while the canonical source remains collaborative in Overleaf. For a non-Overleaf fallback, compile the canonical submission source directly.
5. Verify the PDF exists, inspect its page count and extracted text, and confirm that no content is clipped or replaced by unresolved LaTeX references.
6. For a double-blind submission, verify that neither the manuscript nor supplement inputs the cover letter and that any reviewer-facing source-bundle procedure excludes `cover-letter/`.
7. Report the selected precedents, canonical Overleaf source path or fallback path, uploadable PDF path, validation result, and unresolved confirmations.

Do not archive or label the draft as submitted. Only a human-supplied copy of the file actually uploaded to the venue may enter an as-submitted archive.

## Gotchas

- **Precedent contamination:** A polished old letter may contain a stale title, editor name, affiliation, word count, or declaration. Revalidate every variable fact.
- **Blindness boundary:** The cover letter and manuscript have different audiences. Keep editor-only identities and disclosures out of reviewer-facing files.
- **Whole-project source upload:** An Overleaf project that contains `cover-letter/` is not itself a safe reviewer bundle. Package reviewer source explicitly and exclude that subfolder.
- **Duplicate editable copies:** Do not retain independent sources in both `paper/cover-letter/` and `submission/`. Use the relative compatibility symlink so there is one canonical text.
- **False completion:** A compiling PDF with `[CONFIRM: ...]` markers is still a draft and must be reported as blocked.
- **Related-paper disclosure:** Similar prior or concurrent manuscripts may require explanation even when they are not duplicate submissions. Use current project and Vault records, not memory alone.
- **Archival confusion:** Files in `out/` or a locally compiled PDF are not evidence of what was uploaded.
- **Moving historical date:** A sent `letter` source without an explicit `\date{}` silently renders today's date. Pin the date evidenced by the as-sent PDF before using the source as an Overleaf precedent.
