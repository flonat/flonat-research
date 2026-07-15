---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/*.ipynb"
  - "**/uv.lock"
---

# Rule: Always Use uv for Python

## Principle

**Never invoke a machine-specific `python`, `python3`, or `pip` directly.** All
repository Python execution and package management goes through `uv`.

## Commands

| Instead of | Use |
|-----------|-----|
| `python script.py` | `uv run python script.py` |
| `pip install pkg` | `uv pip install pkg` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `python -m pytest` | `uv run python -m pytest` |
| `python -m venv .venv` | `uv venv` |

## When This Applies

- Every repository and session
- Interactive commands, scripts, hooks, and scheduled jobs
- Task Management, nested packages, and research projects

Bootstrap code that must run before `uv` is installed should be shell-only and
limited to locating or installing `uv`; it must not create a competing Python
environment.

## Automation reliability

Hooks and launchd jobs must not rely on a Homebrew Cellar Python path or on
network access during ordinary execution. Use a stable `uv run --project
<project>` invocation or a `uv tool` installation, resolve and lock dependencies
in advance, and prefer `--frozen` or `--no-sync` once the environment has been
provisioned. Keep launchd stdout and stderr under `~/Library/Logs`.

Test automation from a cold, non-interactive environment on every applicable
host. A hook that cannot start must fail visibly or degrade according to its
documented policy; it must not silently bypass the check it exists to perform.

## Why This Matters

All projects use uv-managed virtual environments. Bare `python` or `pip` may
resolve to the system Python or the wrong environment, causing silent dependency
mismatches. Using a pre-resolved uv environment also keeps scheduled automation
reproducible and offline-capable across machines.
