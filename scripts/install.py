#!/usr/bin/env python3
"""Content-addressed installer for the flonat-research client adapters."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Iterable


WINDOWS_JUNCTION_TAG = 0xA0000003


def is_junction(path: Path) -> bool:
    """Return whether *path* is a Windows directory junction.

    ``Path.is_junction`` is available on Python 3.12+.  The reparse-tag
    fallback keeps the documented Python 3.11 minimum working on Windows.
    """
    checker = getattr(path, "is_junction", None)
    if callable(checker):
        try:
            return bool(checker())
        except OSError:
            return False
    if os.name != "nt":
        return False
    try:
        return getattr(os.lstat(path), "st_reparse_tag", 0) == WINDOWS_JUNCTION_TAG
    except OSError:
        return False


def is_link(path: Path) -> bool:
    return path.is_symlink() or is_junction(path)


def remove_link(path: Path) -> None:
    if is_junction(path) and not path.is_symlink():
        path.rmdir()
    else:
        path.unlink()


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def real_files(root: Path) -> Iterable[tuple[Path, Path]]:
    if is_link(root):
        raise ValueError(f"source must not be a symlink or junction: {root}")
    if root.is_file():
        yield root, Path(root.name)
        return
    if not root.is_dir():
        raise ValueError(f"source is missing: {root}")
    for path in sorted(root.rglob("*")):
        if is_link(path):
            raise ValueError(f"source tree contains a symlink or junction: {path}")
        if path.is_file():
            yield path, path.relative_to(root)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    try:
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def safe_destination(home: Path, relative: str) -> Path:
    relative_path = Path(relative)
    candidate = home / relative_path
    if not relative_path.parts or relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"unsafe install target: {relative}")
    parent = candidate.parent
    while parent != home:
        if is_link(parent):
            raise ValueError(f"install target has a symlinked parent or junction parent: {parent}")
        parent = parent.parent
    return candidate


def desired_files(repo: Path, home: Path, manifest: dict[str, Any], clients: set[str]) -> dict[str, dict[str, Any]]:
    desired: dict[str, dict[str, Any]] = {}
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("install manifest entries must be a list")
    for row in entries:
        if not isinstance(row, dict) or row.get("client") not in {"claude", "codex"}:
            raise ValueError("invalid install manifest entry")
        if row["client"] not in clients:
            continue
        source = repo / str(row.get("source", ""))
        target_root = safe_destination(home, str(row.get("target", "")))
        for source_file, relative in real_files(source):
            target = target_root if source.is_file() else target_root / relative
            target = safe_destination(home, str(target.relative_to(home)))
            key = str(target)
            if key in desired:
                raise ValueError(f"duplicate install target: {target}")
            desired[key] = {
                "source": str(source_file.relative_to(repo)),
                "sha256": digest(source_file),
                "mode": source_file.stat().st_mode & 0o777,
            }
    return desired


def migrate_legacy_links(repo: Path, home: Path, enabled: bool) -> list[str]:
    migrated: list[str] = []
    legacy = {
        home / ".claude/skills": (repo / "skills",),
        home / ".claude/agents": (repo / ".claude/agents", repo / "agents"),
        home / ".claude/rules": (repo / ".claude/rules", repo / "rules"),
        home / ".claude/hooks": (repo / "hooks",),
    }
    for target, expected_candidates in legacy.items():
        if not is_link(target):
            continue
        try:
            owned = any(target.resolve() == expected.resolve() for expected in expected_candidates)
        except OSError:
            owned = False
        if not owned:
            raise ValueError(f"unowned legacy link requires manual review: {target}")
        if not enabled:
            raise ValueError(f"legacy link found; rerun with --migrate-legacy: {target}")
        remove_link(target)
        migrated.append(str(target))
    return migrated


def check_install(desired: dict[str, dict[str, Any]], receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    saved = receipt.get("files", {}) if isinstance(receipt, dict) else {}
    for target, row in desired.items():
        path = Path(target)
        if not path.is_file() or is_link(path):
            errors.append(f"missing or unsafe: {target}")
        elif digest(path) != row["sha256"]:
            errors.append(f"content drift: {target}")
        if not isinstance(saved, dict) or saved.get(target, {}).get("sha256") != row["sha256"]:
            errors.append(f"receipt drift: {target}")
    return errors


def install(repo: Path, home: Path, desired: dict[str, dict[str, Any]], receipt_path: Path, product: str) -> tuple[int, int, Path | None]:
    previous = load_json(receipt_path) if receipt_path.is_file() else {}
    previous_files = previous.get("files", {}) if isinstance(previous.get("files", {}), dict) else {}
    backup_root: Path | None = None
    changed = 0
    unchanged = 0

    stale = sorted(set(previous_files) - set(desired))
    for target_text in stale:
        target = safe_destination(home, str(Path(target_text).relative_to(home)))
        prior = previous_files[target_text]
        if target.is_file() and not is_link(target) and digest(target) == prior.get("sha256"):
            target.unlink()

    for target_text, row in desired.items():
        target = safe_destination(home, str(Path(target_text).relative_to(home)))
        source = repo / row["source"]
        current_hash = digest(target) if target.is_file() and not is_link(target) else None
        if current_hash == row["sha256"]:
            unchanged += 1
            continue
        if target.exists() or is_link(target):
            prior_hash = previous_files.get(target_text, {}).get("sha256")
            if not prior_hash:
                raise ValueError(f"refusing to overwrite unmanaged target: {target}")
            if current_hash != prior_hash:
                if backup_root is None:
                    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
                    backup_root = receipt_path.parent / "backups" / stamp
                backup = backup_root / target.relative_to(home)
                backup.parent.mkdir(parents=True, exist_ok=True)
                if is_link(target):
                    raise ValueError(f"refusing divergent managed symlink or junction: {target}")
                shutil.copy2(target, backup)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as handle:
            temporary = Path(handle.name)
        try:
            shutil.copyfile(source, temporary)
            os.chmod(temporary, int(row["mode"]))
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        changed += 1

    atomic_json(receipt_path, {
        "version": 1,
        "product": product,
        "installed_at": dt.datetime.now(dt.UTC).isoformat(),
        "files": desired,
    })
    return changed, unchanged, backup_root


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--client", choices=("claude", "codex", "both"), default="both")
    value.add_argument("--check", action="store_true")
    value.add_argument(
        "--update",
        action="store_true",
        help="Deprecated compatibility flag; every normal install already reconciles managed copies",
    )
    value.add_argument("--migrate-legacy", action="store_true")
    value.add_argument("--home", help=argparse.SUPPRESS)
    return value


def main() -> int:
    args = parser().parse_args()
    repo = Path(__file__).resolve().parents[1]
    home = Path(args.home).expanduser().resolve() if args.home else Path.home().resolve()
    try:
        manifest = load_json(repo / "config/install-manifest.json")
        product = str(manifest.get("product") or "flonat-research")
        clients = {"claude", "codex"} if args.client == "both" else {args.client}
        receipt_path = home / f".config/{product}/install-receipt.json"
        if args.check:
            # Preview legacy ownership before destination-safety checks so old
            # installations receive the exact, actionable migration command.
            migrate_legacy_links(repo, home, enabled=False)
            desired = desired_files(repo, home, manifest, clients)
            receipt = load_json(receipt_path) if receipt_path.is_file() else {}
            errors = check_install(desired, receipt)
            if errors:
                for error in errors:
                    print(f"FAIL {error}")
                return 1
            print(f"PASS {product}: {len(desired)} managed files are current")
            return 0
        migrated = migrate_legacy_links(repo, home, args.migrate_legacy)
        desired = desired_files(repo, home, manifest, clients)
        changed, unchanged, backup = install(repo, home, desired, receipt_path, product)
        print(f"Installed {product} for {args.client}: {changed} changed, {unchanged} current")
        if migrated:
            print(f"Migrated {len(migrated)} legacy repository-owned links")
        if backup:
            print(f"Preserved divergent managed files in {backup}")
        if "claude" in clients:
            source = repo / ".claude/settings.json"
            if not source.is_file():
                source = repo / "settings.json"
            target = safe_destination(home, ".claude/settings.json")
            if source.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                print("Installed conservative Claude settings (existing settings are always preserved)")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
