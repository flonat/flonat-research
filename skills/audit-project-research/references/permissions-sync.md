# Phase 2.6: Claude Permissions Adapter Audit (Read-Only)

> Detailed check for the `audit-project-research` Claude-adapter phase. **This phase is read-only.** It flags missing permissions and names the `sync-permissions` skill as the optional repair path.

Compare the project's `.claude/settings.local.json` against the canonical Task Management `.claude/settings.json` to find permissions that are present globally but missing locally. This is an adapter check, not a requirement for a client-neutral project.

## Source of truth

Resolve Task Management first:

```bash
TM_ROOT="$(head -1 "$HOME/.config/task-mgmt/path")"
GLOBAL_SETTINGS="$TM_ROOT/.claude/settings.json"
```

The source of truth is `GLOBAL_SETTINGS`, under `permissions.allow` and `permissions.deny`. Do not compare against a deployed home-directory copy.

## Comparison logic

1. Resolve Task Management and read `GLOBAL_SETTINGS`.
2. Check if `<project>/.claude/settings.local.json` exists.
3. If the project has no Claude adapter → report `SKIPPED (Claude adapter unavailable)`.
4. If the adapter exists but the local settings file does not → flag the adapter as Degraded and recommend the `sync-permissions` skill.
5. If it exists → classify each global permission:

| Condition | Classification | Severity |
|-----------|---------------|----------|
| In global, not in local | **Missing** | Degraded |
| In both | **Synced** | — |
| In local, not in global | **Project-specific** | Info |

## Read-only check

```bash
# Read-only diff — never writes
diff <(jq -r '.permissions.allow[]?' "$GLOBAL_SETTINGS" | sort) \
     <(jq -r '.permissions.allow[]?' "<project>/.claude/settings.local.json" 2>/dev/null | sort)
```

The audit reports the diff. The user may invoke the `sync-permissions` skill separately to apply it.

## Report format

```
Permissions Audit:
  .claude/settings.local.json   synced (64/64 allow, 4/4 deny)
```

Or when missing entries are detected:

```
Permissions Audit:
  .claude/settings.local.json   3 allow permissions missing (web fetch, Skill(literature), Bash(jq*))
  .claude/settings.local.json   1 deny permission missing (Bash(pip*))
  Remediation: use the sync-permissions skill to merge.
```

Or when the file is missing entirely:

```
Permissions Audit:
  .claude/settings.local.json   DEGRADED — use the sync-permissions skill to seed from canonical settings (25 allow, 4 deny would be added).
```

## Edge cases

- **No `.claude/` directory at all:** report `SKIPPED (Claude adapter unavailable)`. Do not treat this as a shared-project defect.
- **`settings.local.json` has non-permissions keys (hooks, model):** report them under Info — they're preserved by `sync-permissions`, which only touches the `permissions` object.
- **Pre-template projects:** Phase 2.1 already flags these. Permissions audit can still run independently — having permissions without the rest of the scaffold is harmless.

## What this phase does NOT do

- Never modifies the project (read-only — see Critical Rule 1 in `SKILL.md`).
- Never modifies the canonical Task Management settings source or a deployed client copy.
- Never auto-runs the `sync-permissions` skill — that is a separate user-triggered action.
