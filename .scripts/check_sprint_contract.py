#!/usr/bin/env python3
"""Validate a Sprint Contract JSON against the schema.

Usage:
    python3 .scripts/check_sprint_contract.py <contract.json> [<contract.json> ...]
    python3 .scripts/check_sprint_contract.py --all   # validate every templates/contracts/examples/*.json

Exits 0 if all contracts pass, 1 if any fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    sys.stderr.write("jsonschema not installed. Run: uv pip install jsonschema\n")
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "templates" / "contracts" / "sprint_contract.schema.json"
EXAMPLES_DIR = REPO_ROOT / "templates" / "contracts" / "examples"


def load_schema() -> dict:
    with SCHEMA_PATH.open() as f:
        return json.load(f)


def validate_one(path: Path, schema: dict) -> list[str]:
    """Return list of error messages; empty list means valid."""
    try:
        with path.open() as f:
            contract = json.load(f)
    except json.JSONDecodeError as e:
        return [f"JSON parse error: {e}"]

    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(contract), key=lambda e: e.path)
    return [f"{'.'.join(str(p) for p in err.path) or '<root>'}: {err.message}" for err in errors]


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__)
        return 0

    schema = load_schema()

    if argv[0] == "--all":
        paths = sorted(EXAMPLES_DIR.glob("*.json"))
        if not paths:
            sys.stderr.write(f"No contracts found in {EXAMPLES_DIR}\n")
            return 1
    else:
        paths = [Path(p) for p in argv]

    failed = 0
    for path in paths:
        if not path.exists():
            sys.stderr.write(f"FAIL {path}: file not found\n")
            failed += 1
            continue
        errors = validate_one(path, schema)
        if errors:
            sys.stderr.write(f"FAIL {path.name}:\n")
            for err in errors:
                sys.stderr.write(f"    {err}\n")
            failed += 1
        else:
            sys.stdout.write(f"OK   {path.name}\n")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
