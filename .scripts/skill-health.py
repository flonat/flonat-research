#!/usr/bin/env python3
"""
Skill Health Assessment — Phase A, Step 2

Reads observation events from the shared AI-workflow state directory and the
legacy Claude event directory,
correlates pre/post events, computes per-skill health metrics,
and outputs a structured report.

Usage:
    uv run python .scripts/skill-health.py                    # full report
    uv run python .scripts/skill-health.py --skill proofread  # single skill
    uv run python .scripts/skill-health.py --health failing   # filter by health
    uv run python .scripts/skill-health.py --activity dormant # filter by activity
    uv run python .scripts/skill-health.py --top 10           # top N most-used
    uv run python .scripts/skill-health.py --purge            # run maintenance
    uv run python .scripts/skill-health.py --json             # JSON output
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median

STATE_DIR = Path(os.environ.get(
    "AI_WORKFLOW_STATE_DIR",
    Path.home() / ".local" / "state" / "ai-workflows",
)).expanduser()
LEGACY_ECC_DIR = Path.home() / ".claude" / "ecc"
OBSERVATION_DIRS = tuple(dict.fromkeys((STATE_DIR, LEGACY_ECC_DIR)))
ROLLING_WINDOW_DAYS = 30
PURGE_DAYS = 90
MAX_TOTAL_SIZE_MB = 50


def load_disk_skills() -> set[str]:
    """Set of on-disk skill names (basename of each SKILL.md's parent dir).

    Used to reconcile logged labels against reality: separate real-skill signal
    from noise (agents/rules/session-labels/renamed skills logged as if skills)
    and from blind spots (on-disk skills that have never logged an outcome).
    Returns an empty set if the skills dir can't be located (callers then skip
    reconciliation and fall back to the raw, unpartitioned report).
    """
    candidates = [Path(__file__).resolve().parent.parent / "skills"]
    cfg = Path.home() / ".config" / "task-mgmt" / "path"
    if cfg.exists():
        try:
            candidates.append(Path(cfg.read_text().strip()) / "skills")
        except OSError:
            pass
    for skills_dir in candidates:
        if skills_dir.is_dir():
            return {p.parent.name for p in skills_dir.glob("**/SKILL.md")}
    return set()


def parse_args():
    p = argparse.ArgumentParser(description="Skill health assessment")
    p.add_argument("--skill", help="Show detail for a single skill")
    p.add_argument("--health", choices=["failing", "declining", "watch", "healthy", "insufficient_data", "low_observability"],
                   help="Filter by health status")
    p.add_argument("--activity", choices=["active", "regular", "dormant"],
                   help="Filter by activity status")
    p.add_argument("--top", type=int, help="Show top N most-used skills")
    p.add_argument("--purge", action="store_true", help="Run maintenance (delete old files)")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--all-time", action="store_true", help="Use all data, not rolling window")
    p.add_argument("--alert", action="store_true",
                   help="Print failing/declining/watch recognized skills, one per line "
                        "(empty if none). For cron alerting — quiet when all healthy.")
    return p.parse_args()


def load_events(window_start: datetime | None = None) -> list[dict]:
    """Load all events from daily JSONL files, optionally filtered by date."""
    events = []
    files = sorted({
        filepath
        for directory in OBSERVATION_DIRS
        if directory.exists()
        for filepath in directory.glob("observations-*.jsonl")
    })
    for filepath in files:
        # Extract date from filename for quick filtering
        try:
            file_date_str = filepath.stem.replace("observations-", "")
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if window_start and file_date < window_start - timedelta(days=1):
                continue
        except ValueError:
            continue

        try:
            with open(filepath) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                        if event.get("schema") == "skill-event.v1":
                            events.append(event)
                    except json.JSONDecodeError:
                        print(f"  Warning: malformed line {line_num} in {filepath.name}", file=sys.stderr)
        except OSError as e:
            print(f"  Warning: cannot read {filepath}: {e}", file=sys.stderr)

    # Also load rule-based outcome logs
    outcomes_file = STATE_DIR / "skill-outcomes.jsonl"
    if outcomes_file.exists():
        try:
            with open(outcomes_file) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        # Convert outcome log to skill-event.v1 format
                        if "skill" in record and "outcome" in record:
                            ts = record.get("timestamp", "")
                            if window_start and ts:
                                try:
                                    record_dt = datetime.fromisoformat(ts)
                                    if record_dt.tzinfo is None:
                                        record_dt = record_dt.replace(tzinfo=timezone.utc)
                                    if record_dt < window_start:
                                        continue
                                except ValueError:
                                    pass
                            events.append({
                                "schema": "skill-event.v1",
                                "phase": "outcome",
                                "skill": record["skill"],
                                "timestamp": ts,
                                "outcome": record["outcome"],
                                "outcome_source": "rule",
                                "heuristic_version": 1,
                                "error_class": record.get("note", "")[:100] if record.get("outcome") != "success" else None,
                                "session_hash": record.get("session", ""),
                                "project_label": record.get("project", ""),
                                "project_hash": record.get("project", ""),
                            })
                    except json.JSONDecodeError:
                        print(f"  Warning: malformed line {line_num} in skill-outcomes.jsonl", file=sys.stderr)
        except OSError:
            pass

    return events


def correlate_events(events: list[dict]) -> dict:
    """
    Group events by skill, correlate pre/post by invocation_id.
    Returns: {skill_name: {"pre": [...], "post": [...], "paired": [...]}}
    """
    by_skill: dict[str, dict] = defaultdict(lambda: {"pre": [], "post": [], "paired": [], "mined": []})

    # Index by invocation_id for correlation
    pre_index: dict[str, dict] = {}
    post_index: dict[str, dict] = {}

    for event in events:
        skill = event.get("skill", "unknown")
        phase = event.get("phase", "")
        inv_id = event.get("invocation_id", "")

        if phase == "pre":
            by_skill[skill]["pre"].append(event)
            if inv_id:
                pre_index[inv_id] = event
        elif phase == "post":
            by_skill[skill]["post"].append(event)
            if inv_id:
                post_index[inv_id] = event
        elif phase == "mined":
            by_skill[skill]["mined"].append(event)
        elif phase == "outcome":
            by_skill[skill]["post"].append(event)  # outcome events have the same shape as post events

    # Pair pre/post events by invocation_id
    for inv_id, pre_event in pre_index.items():
        if inv_id in post_index:
            post_event = post_index[inv_id]
            skill = pre_event.get("skill", "unknown")
            try:
                pre_ts = datetime.fromisoformat(pre_event["timestamp"])
                post_ts = datetime.fromisoformat(post_event["timestamp"])
                duration_ms = int((post_ts - pre_ts).total_seconds() * 1000)
                by_skill[skill]["paired"].append({
                    "pre": pre_event,
                    "post": post_event,
                    "duration_ms": max(0, duration_ms),
                })
            except (KeyError, ValueError):
                pass

    return dict(by_skill)


def _windowed_success_rate(post_events: list[dict], now: datetime, days: int) -> float | None:
    """Compute success rate over the last N days from post/outcome events."""
    cutoff = now - timedelta(days=days)
    success = 0
    classified = 0
    for post in post_events:
        ts_str = post.get("timestamp", "")
        if not ts_str:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if ts < cutoff:
            continue
        outcome = post.get("outcome", "unknown")
        if outcome in ("success", "error"):
            classified += 1
            if outcome == "success":
                success += 1
    return success / classified if classified >= 3 else None


TREND_THRESHOLD = 0.10  # 10% drop triggers "worsening"


def compute_metrics(skill_data: dict, now: datetime) -> dict:
    """Compute health metrics for a single skill."""
    pre_events = skill_data["pre"]
    post_events = skill_data["post"]
    paired = skill_data["paired"]
    mined_events = skill_data.get("mined", [])

    # Total invocations: prefer hook data, fall back to mined
    total = len(pre_events)
    if total == 0:
        total = len(post_events)
    # Add mined invocations (each mined event = 1 session mention)
    total += len(mined_events)

    # Outcome classification
    outcomes = defaultdict(int)
    error_classes = defaultdict(int)
    for post in post_events:
        outcome = post.get("outcome", "unknown")
        outcomes[outcome] += 1
        if outcome == "error" and post.get("error_class"):
            error_classes[post["error_class"]] += 1

    classified = outcomes.get("success", 0) + outcomes.get("error", 0)
    unknown_count = outcomes.get("unknown", 0)

    success_rate = outcomes["success"] / classified if classified > 0 else None
    error_rate = outcomes["error"] / total if total > 0 else 0.0
    unknown_rate = unknown_count / total if total > 0 else 1.0

    # --- Trend detection (7d vs 30d windowed success rates) ---
    rate_7d = _windowed_success_rate(post_events, now, 7)
    rate_30d = _windowed_success_rate(post_events, now, 30)

    if rate_7d is not None and rate_30d is not None:
        delta = rate_7d - rate_30d
        if delta <= -TREND_THRESHOLD:
            trend = "worsening"
            declining = True
        elif delta >= TREND_THRESHOLD:
            trend = "improving"
            declining = False
        else:
            trend = "stable"
            declining = False
    else:
        trend = "insufficient_data"
        declining = False

    # Duration from paired events
    durations = [p["duration_ms"] for p in paired if p["duration_ms"] > 0]
    median_duration = median(durations) if durations else None

    # Last used
    timestamps = []
    for e in pre_events + post_events + mined_events:
        try:
            timestamps.append(datetime.fromisoformat(e["timestamp"]))
        except (KeyError, ValueError):
            pass
    last_used = max(timestamps) if timestamps else None

    # Project diversity
    project_hashes = set()
    for e in pre_events + mined_events:
        ph = e.get("project_hash")
        if ph:
            project_hashes.add(ph)

    # Re-invocation rate (from hook data only — mined data is per-session)
    sessions = defaultdict(int)
    for e in pre_events:
        sh = e.get("session_hash")
        if sh:
            sessions[sh] += 1
    # Mined events with mention_count > 1 suggest re-invocation
    for e in mined_events:
        sh = e.get("session_hash")
        mc = e.get("mention_count", 1)
        if sh:
            sessions[sh] += mc
    sessions_with_reinvoke = sum(1 for count in sessions.values() if count >= 2)
    reinvoke_rate = sessions_with_reinvoke / len(sessions) if sessions else 0.0

    # Top errors
    top_errors = sorted(error_classes.items(), key=lambda x: -x[1])[:3]

    # Skill mtime (most recent)
    mtimes = [e.get("skill_mtime") for e in pre_events if e.get("skill_mtime")]
    latest_mtime = max(mtimes) if mtimes else None

    # Health status
    if classified < 10:
        health = "insufficient_data"
    elif unknown_rate > 0.7:
        health = "low_observability"
    elif error_rate >= 0.3:
        health = "failing"
    elif declining:
        health = "declining"
    elif error_rate >= 0.1:
        health = "watch"
    else:
        health = "healthy"

    # Activity status
    if last_used:
        days_since = (now - last_used).days
        if days_since <= 7:
            activity = "active"
        elif days_since <= 30:
            activity = "regular"
        else:
            activity = "dormant"
    else:
        activity = "dormant"

    return {
        "total_invocations": total,
        "classified_invocations": classified,
        "success_rate": round(success_rate, 3) if success_rate is not None else None,
        "error_rate": round(error_rate, 3),
        "unknown_rate": round(unknown_rate, 3),
        "error_count": outcomes.get("error", 0),
        "rate_7d": round(rate_7d, 3) if rate_7d is not None else None,
        "rate_30d": round(rate_30d, 3) if rate_30d is not None else None,
        "trend": trend,
        "declining": declining,
        "median_duration_ms": int(median_duration) if median_duration else None,
        "last_used": last_used.isoformat() if last_used else None,
        "project_count": len(project_hashes),
        "re_invocation_rate": round(reinvoke_rate, 3),
        "top_errors": [{"class": cls, "count": cnt} for cls, cnt in top_errors],
        "health": health,
        "activity": activity,
        "latest_skill_mtime": latest_mtime,
    }


def purge_old_files():
    """Delete observation files older than PURGE_DAYS. Enforce total size cap."""
    if not STATE_DIR.exists():
        print("No shared AI-workflow state directory found.")
        return

    cutoff = datetime.now() - timedelta(days=PURGE_DAYS)
    files = sorted(STATE_DIR.glob("observations-*.jsonl"))
    deleted = 0

    # Phase 1: delete by age
    for f in files:
        try:
            date_str = f.stem.replace("observations-", "")
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if file_date < cutoff:
                f.unlink()
                deleted += 1
                print(f"  Purged: {f.name} (older than {PURGE_DAYS} days)")
        except (ValueError, OSError):
            pass

    # Phase 2: enforce size cap
    remaining = sorted(STATE_DIR.glob("observations-*.jsonl"))
    total_size = sum(f.stat().st_size for f in remaining if f.exists())
    max_bytes = MAX_TOTAL_SIZE_MB * 1024 * 1024

    while total_size > max_bytes and remaining:
        oldest = remaining.pop(0)
        size = oldest.stat().st_size
        oldest.unlink()
        total_size -= size
        deleted += 1
        print(f"  Purged: {oldest.name} (size cap)")

    print(f"Maintenance complete. {deleted} files purged. "
          f"{len(list(STATE_DIR.glob('observations-*.jsonl')))} files remaining.")


def format_table(report: dict, args) -> str:
    """Format the health report as a readable table."""
    if not report:
        return "No observation data found. Client hooks are optional; record an outcome " \
               "in the shared AI-workflow state directory and retry."

    # Sort by total invocations descending
    items = sorted(report.items(), key=lambda x: -x[1]["total_invocations"])

    if args.top:
        items = items[:args.top]

    lines = []
    lines.append(f"{'Skill':<30} {'Invocations':>11} {'Success':>8} {'Errors':>7} {'Trend':<13} {'Health':<18} {'Activity':<10} {'Last Used':<12}")
    lines.append("-" * 115)

    for skill, m in items:
        sr = f"{m['success_rate']:.0%}" if m["success_rate"] is not None else "n/a"
        ec = str(m["error_count"])
        lu = m["last_used"][:10] if m["last_used"] else "never"

        # Trend indicator
        trend = m.get("trend", "")
        if trend == "worsening":
            trend_display = "!! DECLINING"
        elif trend == "improving":
            trend_display = "^  improving"
        elif trend == "stable":
            trend_display = "-- stable"
        else:
            trend_display = "   n/a"

        # Health indicator
        health_display = m["health"]
        if m["health"] == "failing":
            health_display = "!! FAILING"
        elif m["health"] == "declining":
            health_display = "!! DECLINING"
        elif m["health"] == "watch":
            health_display = "?  WATCH"
        elif m["health"] == "healthy":
            health_display = "ok HEALTHY"

        lines.append(f"{skill:<30} {m['total_invocations']:>11} {sr:>8} {ec:>7} {trend_display:<13} {health_display:<18} {m['activity']:<10} {lu:<12}")

    # Summary
    total_skills = len(report)
    failing = sum(1 for m in report.values() if m["health"] == "failing")
    declining_count = sum(1 for m in report.values() if m["health"] == "declining")
    watching = sum(1 for m in report.values() if m["health"] == "watch")
    healthy = sum(1 for m in report.values() if m["health"] == "healthy")
    insufficient = sum(1 for m in report.values() if m["health"] in ("insufficient_data", "low_observability"))

    lines.append("")
    lines.append(f"Summary: {total_skills} skills observed | "
                 f"{failing} failing | {declining_count} declining | {watching} watch | {healthy} healthy | {insufficient} insufficient data")

    return "\n".join(lines)


def format_reconciliation(unrecognized: dict, blind_spots: list[str],
                          disk_total: int, recognized_count: int) -> str:
    """Render coverage + blind-spot + unrecognized-label sections below the table."""
    if disk_total == 0:
        return ""  # couldn't locate skills dir — skip reconciliation
    pct = (100 * recognized_count // disk_total) if disk_total else 0
    lines = ["", "=" * 60,
             f"Coverage: {recognized_count}/{disk_total} on-disk skills have logged ({pct}%)."]

    lines.append("")
    lines.append(f"Blind spots — {len(blind_spots)} on-disk skills with NO outcome data "
                 f"(invisible to health, can't be classified):")
    lines.append("  " + (", ".join(blind_spots) if blind_spots else "(none)"))

    u = sorted(unrecognized.items(), key=lambda x: -x[1]["total_invocations"])
    lines.append("")
    lines.append(f"Unrecognized labels — {len(u)} logged names that are NOT on-disk skills "
                 f"(agents/rules/session-labels/renamed; excluded from health):")
    lines.append("  " + (", ".join(f"{k}({v['total_invocations']})" for k, v in u) if u else "(none)"))
    return "\n".join(lines)


def format_detail(skill: str, metrics: dict) -> str:
    """Format detailed view for a single skill."""
    lines = [f"Skill: {skill}", "=" * 40]

    for key, val in metrics.items():
        if key == "top_errors" and val:
            lines.append(f"  top_errors:")
            for err in val:
                lines.append(f"    - {err['class']} ({err['count']}x)")
        else:
            lines.append(f"  {key}: {val}")

    return "\n".join(lines)


def main():
    args = parse_args()

    if args.purge:
        purge_old_files()
        return

    now = datetime.now(timezone.utc)
    window_start = None if args.all_time else now - timedelta(days=ROLLING_WINDOW_DAYS)

    events = load_events(window_start)
    if not events:
        if args.json:
            print(json.dumps({"skills": {}, "meta": {"event_count": 0}}))
        else:
            print(f"No observation data found in {STATE_DIR} or the legacy adapter store.")
            print("Client hooks are optional; explicit outcome logging remains the portable source.")
        return

    # Filter by window
    if window_start:
        events = [e for e in events
                  if datetime.fromisoformat(e.get("timestamp", "2000-01-01T00:00:00+00:00")) >= window_start]

    by_skill = correlate_events(events)

    # Compute metrics for every logged label
    full_report = {}
    for skill_name, data in by_skill.items():
        full_report[skill_name] = compute_metrics(data, now)

    # --skill inspects ANY logged label (incl. noise), against the full data
    if args.skill:
        if args.skill in full_report:
            if args.json:
                print(json.dumps({args.skill: full_report[args.skill]}, indent=2))
            else:
                print(format_detail(args.skill, full_report[args.skill]))
        else:
            print(f"No data for skill '{args.skill}' in the current window.")
        return

    # Reconcile logged labels against on-disk skills:
    #   recognized   = real skills with data  -> the trustworthy health signal
    #   unrecognized = logged labels not on disk (agents/rules/session-labels/renamed)
    #   blind_spots  = on-disk skills that never logged (no observability)
    disk_skills = load_disk_skills()
    if disk_skills:
        recognized = {k: v for k, v in full_report.items() if k in disk_skills}
        unrecognized = {k: v for k, v in full_report.items() if k not in disk_skills}
        blind_spots = sorted(disk_skills - set(full_report.keys()))
    else:
        recognized, unrecognized, blind_spots = full_report, {}, []

    # --alert: one line per actionable recognized skill, nothing if all healthy
    if args.alert:
        order = {"failing": 0, "declining": 1, "watch": 2}
        bad = sorted(
            ((k, v) for k, v in recognized.items() if v["health"] in order),
            key=lambda kv: (order[kv[1]["health"]], -kv[1]["error_rate"]),
        )
        for k, v in bad:
            print(f"- {k}: {v['health']} (err {v['error_rate']:.0%}, "
                  f"{v['error_count']}/{v['classified_invocations']} classified)")
        return

    # Health table + filters operate on recognized real skills only
    report = recognized
    if args.health:
        report = {k: v for k, v in report.items() if v["health"] == args.health}
    if args.activity:
        report = {k: v for k, v in report.items() if v["activity"] == args.activity}

    if args.json:
        print(json.dumps({
            "skills": report,
            "unrecognized_labels": {k: v["total_invocations"] for k, v in
                                    sorted(unrecognized.items(), key=lambda x: -x[1]["total_invocations"])},
            "blind_spots": blind_spots,
            "meta": {
                "event_count": len(events),
                "window_days": ROLLING_WINDOW_DAYS if not args.all_time else "all",
                "generated_at": now.isoformat(),
                "disk_skill_count": len(disk_skills),
                "recognized_count": len(recognized),
                "unrecognized_count": len(unrecognized),
                "blind_spot_count": len(blind_spots),
            }
        }, indent=2))
    else:
        print(format_table(report, args))
        # Only show reconciliation on the unfiltered full view
        if not (args.health or args.activity or args.top):
            print(format_reconciliation(unrecognized, blind_spots,
                                        len(disk_skills), len(recognized)))


if __name__ == "__main__":
    main()
