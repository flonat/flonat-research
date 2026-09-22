#!/usr/bin/env python3
"""verify_outputs.py — shared output-verification helper for file-producing skills.

Reads a manifest JSON emitted by a skill at the end of its run and aborts
(exit != 0) if any claimed output file is missing. Also appends a structured
entry to ~/.local/state/ai-workflows/skill-outcomes.jsonl so failing skills
surface on the shared skill-health dashboard.

Manifest schema (per skill invocation):
    {
      "skill":   "<skill-name>",
        "session": "<client session ID or hash>",
      "project": "<project-slug>",
      "claimed_outputs": ["relative/path/1", "relative/path/2", ...]
    }

Usage (inside a skill, just before auto-commit):

    uv run python <skills-root>/_shared/verify_outputs.py \
        --manifest <outputs-manifest.json> \
        --project-root <project>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class VerifyResult:
    ok: bool
    missing: list[str]
    manifest: dict


def verify_manifest(manifest_path: Path, project_root: Path) -> VerifyResult:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return VerifyResult(ok=False, missing=[f"<manifest unreadable: {e}>"], manifest={})

    claimed = data.get("claimed_outputs") or []
    missing: list[str] = []
    for rel in claimed:
        target = (project_root / rel).resolve()
        if not target.exists():
            missing.append(rel)
    return VerifyResult(ok=not missing, missing=missing, manifest=data)


def _bounded(value: str, limit: int) -> str:
    """Strip control characters and truncate, so a row can never fail schema validation."""
    cleaned = "".join(c for c in str(value or "") if ord(c) >= 32 and ord(c) != 127)
    return cleaned[:limit]


def log_outcome(skill: str, project: str, ok: bool, note: str) -> None:
    """Append one schema-valid outcome row.

    `skill` and `project` must be non-empty per rules/skill-outcome-logging.md —
    an empty value makes the row invalid and wedges `sync-push-memory.sh` for
    every later session, so both fall back rather than write through blank.
    """
    path = Path.home() / ".local" / "state" / "ai-workflows" / "skill-outcomes.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "skill": _bounded(skill, 128).strip() or "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "outcome": "success" if ok else "error",
        "session": _bounded(os.environ.get("AI_SESSION_ID", os.environ.get("CLAUDE_SESSION_ID", "")), 160),
        "project": _bounded(project, 256).strip() or "_no-project",
        "note": _bounded(note, 1024),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--project-root", type=Path, default=Path.cwd())
    args = p.parse_args()

    if not args.manifest.exists():
        print(f"[verify-outputs] manifest not found: {args.manifest}", file=sys.stderr)
        log_outcome("unknown", args.project_root.name, False, "manifest missing")
        return 2

    result = verify_manifest(args.manifest, args.project_root)
    # `.get(key, default)` returns a present-but-empty value, so fall through explicitly:
    # a manifest carrying "project": "" is exactly what produced the invalid rows.
    skill = str(result.manifest.get("skill") or "").strip() or "unknown"
    project = (
        str(result.manifest.get("project") or "").strip()
        or args.project_root.name
        or "_no-project"
    )

    if result.ok:
        print(f"[verify-outputs] OK — all {len(result.manifest.get('claimed_outputs', []))} "
              f"claimed outputs of {skill} present.")
        log_outcome(skill, project, True, "")
        return 0

    note = f"missing: {', '.join(result.missing[:5])}"
    print(f"[verify-outputs] ABORT — {skill} claimed outputs that are missing:", file=sys.stderr)
    for m in result.missing:
        print(f"  - {m}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Refusing to auto-commit. Re-run the skill or add the missing outputs manually.",
          file=sys.stderr)
    log_outcome(skill, project, False, note)
    return 1


if __name__ == "__main__":
    sys.exit(main())
