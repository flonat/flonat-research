# Shared project handoff protocol

Use `.context/ai-handoff.md` as the single project-level handshake for Claude-to-Claude, Codex-to-Codex, Claude-to-Codex, and Codex-to-Claude work. Keep native `CLAUDE.md` and `AGENTS.md` as durable client guidance; never overwrite either during a handoff.

## Schema

```markdown
---
schema_version: 1
handoff_id: YYYYMMDD-HHMMSS
updated_at: YYYY-MM-DDTHH:MM:SSZ
from: claude|codex|human
to: claude|codex|either
status: ready|accepted|in_progress|blocked|complete
source_machine: <hostname>
target_machine: same|macbook|mini|unknown
branch: <branch-or-none>
commit: <sha-or-none>
---

# AI project handoff

## Outcome
<specific result the receiving client should produce>

## Current state
- <completed work>
- <in-flight work>
- <blockers or surprises>

## Acceptance criteria
- [ ] <observable completion condition>

## Start here
1. <first concrete action>
2. <verification step>

## Files and commands
- `<path>` — <why it matters>
- Build: `<real command>`
- Test: `<real command>`

## Decisions and guardrails
- <locked decision or project-critical constraint>

## Working tree
- Changed files: <concise list or clean>
- Uncommitted work ownership: <who owns it and whether it is safe to edit>

## Open questions
- <question requiring judgment>

## Handoff log
- `<timestamp>` — `<client>` set status to `<status>`: <short note>
```

## Sender protocol

1. Read existing native guidance, the latest approved plan, current focus, recent log, and existing handshake.
2. Do not inspect restricted `data/raw/` content.
3. Reconcile the existing handshake instead of discarding useful decisions or log entries.
4. Set a new `handoff_id`, target client, current branch/commit, and `status: ready`.
5. State one outcome and observable acceptance criteria. Record uncommitted-file ownership precisely.
6. Verify that `.context/ai-handoff.md` parses as YAML frontmatter plus Markdown and contains no secrets.
7. Do not auto-commit or push. Offer to transport the handshake through the project's verified Git/Dropbox workflow. A private Git project may track the handshake when the user authorizes the normal commit/push flow; do not add it to `.gitignore` automatically.

## Receiver protocol

1. Read `CLAUDE.md`, `AGENTS.md`, and the handshake before editing.
2. Confirm that `to` is the current client or `either`; compare the recorded branch and commit with the working tree.
3. Update the handshake to `status: accepted` and append a log entry before substantive work.
4. Set `status: in_progress` when execution begins. Preserve earlier decisions unless new evidence requires an explicit revision.
5. On blockage, set `status: blocked`, record the precise blocker and safe next step, and stop expanding scope.
6. On completion, set `status: complete`, check the acceptance criteria, record verification evidence, and append the final log entry.
7. To pass work back, apply the sender protocol with a new `handoff_id` and the other target client.

## Multi-machine contract

- Git or Dropbox transports the project handshake; client home directories never do.
- The receiving machine must pull/sync the project and run its local shared-infrastructure deployment.
- Never put authentication, secrets, transcripts, caches, or restricted data in the handshake.
- A same-client restart uses the same state machine as a cross-client handoff; only `from`, `to`, and the machine fields differ.
