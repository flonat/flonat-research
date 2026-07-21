# Strategic Revision Modes and Provenance Contract

The `strategic-revision` skill has one analytical engine and two surrounding workflows. Choose the workflow from the provenance of the feedback source, not its tone, severity, filename, or claimed reviewer persona.

## Mode selection

| Question | External R&R mode | Internal revision mode |
|---|---|---|
| Who authored the feedback? | A human reviewer/editor acting for a journal or conference | An AI tool/agent/skill, or a supervisor/co-author/collaborator acting informally |
| Where does the source remain? | `correspondence/referee-reviews/` or `correspondence/editorial/` | AI: `reviews/<scope>/<source>/`; human collaborator: `correspondence/internal/` |
| Where does the derived plan go? | `correspondence/referee-reviews/{venue}-round{n}/` | `reviews/<scope>/strategic-revision/{YYYY-MM-DD-HHMM}/` |
| Is a response owed to a venue? | Yes | No |

Examples:

- A report downloaded from OpenReview, Editorial Manager, or a journal portal: **external**.
- A `referee2-reviewer` agent report: **internal**, even when it imitates a hostile referee.
- ChatGPT or Claude.ai feedback pasted by the user: **internal**.
- A co-author's informal annotated draft: source in `correspondence/internal/`; derived plan is **internal**.
- A programme chair's decision letter: **external**.

If authorship or institutional role is uncertain, stop before writing and ask. Do not infer external provenance from phrases such as "Reviewer 2" or "major revision."

## Shared analytical core

Both modes must:

1. preserve every source finding with a stable SourceID and anchor;
2. atomize compound requests;
3. verify actionable findings against the manuscript or evidence they cite;
4. classify Category and revision routing;
5. map hard dependencies separately from collateral risks;
6. reject cyclic task graphs;
7. assign execution blocks A--E;
8. compute parallel batches, critical path, bottlenecks, and block inversions;
9. record explicit author decisions for Major/Critical findings; and
10. version later same-draft additions rather than overwriting the first plan.

## External R&R contract

External mode additionally:

- copies, never moves, the venue-supplied source into the round workspace;
- writes the required searchable `{venue}-round{n}-reviews.md` companion to the preserved PDF;
- preserves reviewer/editor roles and wording;
- compiles a verbatim LaTeX transcription;
- creates an empty rebuttal scaffold;
- records response deadline, revision round, and coordinating author;
- performs response-risk coaching for Major/Critical comments;
- writes venue strategy when relevant; and
- appends the `reviews-in` submission-history event required by `submission-file-archive.md`.

The response letter may refer only to actual venue comments. Internal audit findings cannot be relabelled as reviewer requests.

## Internal revision contract

Internal mode:

- consumes one grounded report directly or, for multiple reports, normally consumes a `synthesise-reviews` output plus its listed sources;
- writes a timestamped plan package under `reviews/<scope>/strategic-revision/`;
- records source paths, provenance type, review dates, draft identity, and SHA-256 hashes in `source-manifest.md`;
- links to source reports in place rather than copying them;
- records Adopt / Adapt / Reject / Defer decisions and rationales;
- concludes with `SUBMIT`, `HOLD`, or `DEFER`, blocking tasks, scope boundary, and re-review gate; and
- creates no rebuttal, referee-verbatim file, venue event, or alternative-venue analysis by default.

Any source report referenced by an active internal `source-manifest.md` is provenance-bearing and must not be moved to `archived/` until the plan is closed. If it is archived later, update the manifest path while retaining the recorded hash.

Internal mode does not replace `synthesise-reviews`: synthesis decides the consolidated issue set; strategic revision turns that set into an executable DAG.

## Cross-mode boundary

Fold-in is same-mode only.

- Internal followed by internal on the same draft: extend the internal DAG.
- External followed by external in the same venue round: extend the external DAG.
- Internal preparation followed by genuine venue reviews: create a new external package. The external plan may link to completed internal task IDs as prior work, but it must not copy internal review text into correspondence or claim the venue requested it.
- An internal audit during an active R&R: keep the audit and its derived tasks in the internal package. The external master plan may cross-reference a completed internal task when it also resolves a genuine referee request.

Cross-references must include the source package path and task ID. They do not merge SourceIDs, reviewer quotes, history events, or response-letter provenance.

## No-overwrite and draft identity

Use fold-in versioning only when the new review covers roughly the same manuscript state. Record a draft identity using the best stable evidence available: Git revision, archived submission file hash, or a manifest of manuscript file hashes. If the draft changed materially, create a new timestamped internal package or a new external venue round rather than extending the old DAG.
