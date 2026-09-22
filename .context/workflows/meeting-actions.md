# Meeting action extraction

Plaud is the primary provider; the Mini imports source-labelled records into the Syncthing-backed Vault. The local transcription fallback remains available. Resolve current paths and operations from [the meeting guide](../../docs/guides/minutes.md).

| Intent | Skill |
|---|---|
| Locate a meeting or search a discussion | meetings-find |
| Read an original or cleaned recording | meetings-read |
| Prepare for a call | meetings-prep |
| Analyze one meeting or draft a follow-up | meetings-debrief |
| Synthesize a period | meetings-digest |
| Correct and file a transcript | meetings-cleanup |
| Manage storage | meetings-storage |
| Diagnose import/transcription | meetings-verify |

Use [the retrieval contract](../../skills/meetings-find/references/retrieval.md) for scoped source selection, provider identity, and linked cleaned documents. Do not mix the user's affiliations in a university-specific output or assume the compatibility minutes CLI searches linked project text.

Extract explicit commitments, requests, agreed next steps, and stated deadlines. Distinguish a request from its acceptance. Capture task, supported owner/due date, project, source recording ID/date/version, and context. Unknown values stay unknown; absence of completion evidence does not prove a task is open.

Present extracted actions in chat. Task creation is a separate explicitly authorized operation: resolve the current Vault task schema and destination, show concrete proposed tasks, preserve source links, and avoid duplicates. Do not infer a task-creation mandate from debrief, digest, or cleanup. Apply the approved scope to metadata and links as well as prose.

The meeting-analyst agent remains read-only and response-only. It can synthesize eligible records using the shared retrieval contract; it cannot persist tasks, relationship profiles, or corrected transcripts.
