"""Deterministic audit for invisible / confusable Unicode in research sources.

Finds characters that are *invisible or near-invisible on screen* but change
what a machine reads: zero-width carriers, bidi controls, tag characters,
variation selectors, and space homoglyphs. These survive copy-paste from
Word, PDFs, browsers, and generated output, then break things silently — a U+200B
inside a citekey makes BibTeX drop the entry with no error, a U+00A0 makes an
exact-match string edit fail on a line that looks identical, a U+FEFF at the
head of a .tex file can defeat driver detection.

Codepoint tables adapted 2026-08-13 from guillaumemeyer/watermarks-remover
(`text_unicode.py`, MIT). Layer A only. The upstream project's file-metadata
cleaner and statistical-watermark rewrite layer are deliberately out of scope:
this checker reports edit-based invisible carriers and does not infer authorship.

What this stack adds over upstream:

  - **Severity tiers.** Upstream treats every hit alike. Here a zero-width
    char inside `\\cite{}` is critical; a no-break space in prose is a
    warning. The two need different responses.
  - **LaTeX/BibTeX context.** A hit is located to line:col AND to the
    fragile construct containing it (citekey, \\label/\\ref, \\input path,
    URL, bib field). Context is most of the signal.
  - **Emoji rescue.** Upstream strips U+200D and U+FE0F unconditionally,
    which corrupts legitimate emoji sequences. Here a ZWJ or VS16 between
    pictographic characters is reported as `info` and never rewritten.

Contract boundaries:

  - **Report-only by default.** `--apply` is opt-in, per `audit-before-fix`.
  - **Necessary, not sufficient.** Detects edit-based carriers only. It says
    nothing about who or what wrote the text, and must never be cited as
    authorship evidence.
  - **Never writes under `data/raw/`** (`data-sensitivity`), and refuses to
    `--apply` to an Overleaf-canonical path without an explicit flag
    (`reconcile-before-rewriting`).

Usage:
    uv run --no-sync python "<skill-dir>/scripts/check_invisible_unicode.py" paper/main.tex
    uv run --no-sync python "<skill-dir>/scripts/check_invisible_unicode.py" <project>/ --check
    uv run --no-sync python "<skill-dir>/scripts/check_invisible_unicode.py" main.tex --diff
    uv run --no-sync python "<skill-dir>/scripts/check_invisible_unicode.py" main.tex --apply
    uv run --no-sync python "<skill-dir>/scripts/check_invisible_unicode.py" <dir>/ --format json
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Codepoint tables (adapted from watermarks-remover, MIT)
# --------------------------------------------------------------------------

# Zero-width family — the classic silent carriers.
ZERO_WIDTH: frozenset[int] = frozenset(
    {
        0x200B,  # zero width space
        0x200C,  # zero width non-joiner
        0x200D,  # zero width joiner
        0x2060,  # word joiner
        0xFEFF,  # BOM / zero width no-break space
        0x180E,  # Mongolian vowel separator
    }
)

# Bidi / directional overrides. Essentially never legitimate in this corpus,
# and can make a line render in an order that differs from its byte order.
BIDI: frozenset[int] = frozenset(
    {
        0x061C,  # Arabic letter mark
        0x200E,  # LRM
        0x200F,  # RLM
        0x202A,  # LRE
        0x202B,  # RLE
        0x202C,  # PDF (pop directional formatting)
        0x202D,  # LRO
        0x202E,  # RLO
        0x2066,  # LRI
        0x2067,  # RLI
        0x2068,  # FSI
        0x2069,  # PDI
    }
)

# Invisible math operators — render as nothing, parse as structure.
INVISIBLE_MATH: frozenset[int] = frozenset(
    {
        0x2061,  # function application
        0x2062,  # invisible times
        0x2063,  # invisible separator
        0x2064,  # invisible plus
    }
)

# Other format/filler controls with no visible width.
OTHER_INVISIBLE: frozenset[int] = frozenset(
    {
        0x00AD,  # soft hyphen
        0x034F,  # combining grapheme joiner
        0x115F,  # Hangul choseong filler
        0x1160,  # Hangul jungseong filler
        0x17B4,  # Khmer vowel inherent AQ
        0x17B5,  # Khmer vowel inherent AA
        0x206A,  # inhibit symmetric swapping
        0x206B,
        0x206C,
        0x206D,
        0x206E,
        0x206F,
        0xFFF9,  # interlinear annotation anchor
        0xFFFA,
        0xFFFB,
    }
)

# Spaces that look like U+0020 but are not.
SPACE_HOMOGLYPHS: dict[int, str] = {
    0x00A0: " ",  # no-break space
    0x1680: " ",  # Ogham space mark
    0x2000: " ",  # en quad
    0x2001: " ",  # em quad
    0x2002: " ",  # en space
    0x2003: " ",  # em space
    0x2004: " ",  # three-per-em space
    0x2005: " ",  # four-per-em space
    0x2006: " ",  # six-per-em space
    0x2007: " ",  # figure space
    0x2008: " ",  # punctuation space
    0x2009: " ",  # thin space
    0x200A: " ",  # hair space
    0x202F: " ",  # narrow no-break space
    0x205F: " ",  # medium mathematical space
    0x3000: " ",  # ideographic space
}

_VS_BMP = range(0xFE00, 0xFE10)  # variation selectors 1-16
_VS_SUPPLEMENT = range(0xE0100, 0xE01F0)  # variation selectors 17-256
_MONGOLIAN_FVS = range(0x180B, 0x180E)
_TAG_CHARS = range(0xE0001, 0xE0080)  # deprecated tag chars, stego-favoured

# Emoji-ish ranges, for the ZWJ/VS16 rescue. Deliberately broad: the cost of
# a false rescue is one unfixed invisible char, the cost of a false strip is
# a corrupted emoji sequence in someone's notes.
_PICTOGRAPHIC_RANGES: tuple[tuple[int, int], ...] = (
    (0x00A9, 0x00A9),
    (0x00AE, 0x00AE),
    (0x203C, 0x3299),
    (0x1F000, 0x1FAFF),
    (0x1F1E6, 0x1F1FF),
)

# --------------------------------------------------------------------------
# Severity
# --------------------------------------------------------------------------

CRITICAL = "critical"
WARNING = "warning"
INFO = "info"

_SEVERITY_ORDER = {INFO: 0, WARNING: 1, CRITICAL: 2}


def _is_pictographic(ch: str | None) -> bool:
    if not ch:
        return False
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in _PICTOGRAPHIC_RANGES)


def classify(cp: int) -> tuple[str, str] | None:
    """Return (kind, base_severity) for a suspicious codepoint, else None."""
    if cp in ZERO_WIDTH:
        return "zero_width", CRITICAL
    if cp in BIDI:
        return "bidi", CRITICAL
    if cp in INVISIBLE_MATH:
        return "invisible_math", CRITICAL
    if cp in _TAG_CHARS:
        return "tag_char", CRITICAL
    if cp in _VS_BMP or cp in _VS_SUPPLEMENT or cp in _MONGOLIAN_FVS:
        return "variation_selector", WARNING
    if cp in OTHER_INVISIBLE:
        return "invisible_format", WARNING
    if cp in SPACE_HOMOGLYPHS:
        return "space_homoglyph", WARNING
    # Catch-all for format characters not enumerated above.
    if unicodedata.category(chr(cp)) == "Cf":
        return "other_format", CRITICAL
    return None


# --------------------------------------------------------------------------
# LaTeX / BibTeX fragile-context detection
# --------------------------------------------------------------------------

_CONTEXT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("citekey", re.compile(r"\\[a-zA-Z]*cite[a-zA-Z]*\s*(?:\[[^\]]*\])*\s*\{([^}]*)\}")),
    ("crossref", re.compile(r"\\(?:label|ref|eqref|autoref|cref|Cref|pageref)\s*\{([^}]*)\}")),
    ("path", re.compile(r"\\(?:input|include|includegraphics|bibliography|addbibresource)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")),
    ("url", re.compile(r"\\(?:url|href)\s*\{([^}]*)\}")),
    ("bib_entry_key", re.compile(r"@\w+\s*\{\s*([^,\s]+)")),
    ("bib_doi", re.compile(r"(?i)\b(?:doi|url|eprint)\s*=\s*[{\"]([^}\"]*)")),
)


def fragile_spans(text: str) -> list[tuple[int, int, str]]:
    """Character spans where an invisible char corrupts a machine-read token."""
    spans: list[tuple[int, int, str]] = []
    for name, pattern in _CONTEXT_PATTERNS:
        for m in pattern.finditer(text):
            spans.append((m.start(1), m.end(1), name))
    return spans


def context_at(offset: int, spans: list[tuple[int, int, str]]) -> str | None:
    for start, end, name in spans:
        if start <= offset < end:
            return name
    return None


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------


@dataclass
class Finding:
    path: str
    line: int
    col: int
    codepoint: int
    kind: str
    severity: str
    context: str | None
    line_text: str
    rescued: bool = False

    @property
    def label(self) -> str:
        ch = chr(self.codepoint)
        return f"U+{self.codepoint:04X} {unicodedata.name(ch, 'UNNAMED')}"

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "line": self.line,
            "col": self.col,
            "codepoint": f"U+{self.codepoint:04X}",
            "name": unicodedata.name(chr(self.codepoint), "UNNAMED"),
            "kind": self.kind,
            "severity": self.severity,
            "context": self.context,
            "rescued": self.rescued,
        }


@dataclass
class FileReport:
    path: Path
    findings: list[Finding] = field(default_factory=list)
    error: str | None = None

    @property
    def actionable(self) -> list[Finding]:
        return [f for f in self.findings if not f.rescued]


def _line_index(text: str) -> list[int]:
    """Start offset of each line."""
    starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _locate(offset: int, starts: list[int]) -> tuple[int, int]:
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= offset:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1, offset - starts[lo] + 1


def scan_text(text: str, path: str) -> list[Finding]:
    spans = fragile_spans(text)
    starts = _line_index(text)
    lines = text.splitlines()
    findings: list[Finding] = []

    for i, ch in enumerate(text):
        cp = ord(ch)
        # Fast path: ASCII printable + newline/tab are overwhelmingly common.
        if 0x20 <= cp < 0x7F or ch in "\n\t\r":
            continue
        result = classify(cp)
        if result is None:
            continue
        kind, severity = result

        rescued = False
        if cp == 0x200D:  # ZWJ between pictographs = legitimate emoji sequence
            prev_ch = text[i - 1] if i > 0 else None
            next_ch = text[i + 1] if i + 1 < len(text) else None
            if _is_pictographic(prev_ch) and _is_pictographic(next_ch):
                rescued, severity = True, INFO
        elif cp == 0xFE0F:  # VS16 = emoji presentation selector
            prev_ch = text[i - 1] if i > 0 else None
            if _is_pictographic(prev_ch):
                rescued, severity = True, INFO

        ctx = context_at(i, spans)
        # A warning-level char inside a machine-read token is critical there.
        if ctx and not rescued and severity == WARNING:
            severity = CRITICAL
        # A BOM is only benign as the very first character of a file.
        if cp == 0xFEFF and i == 0:
            severity = WARNING

        line_no, col = _locate(i, starts)
        findings.append(
            Finding(
                path=path,
                line=line_no,
                col=col,
                codepoint=cp,
                kind=kind,
                severity=severity,
                context=ctx,
                line_text=lines[line_no - 1] if line_no - 1 < len(lines) else "",
                rescued=rescued,
            )
        )
    return findings


def clean_text(text: str) -> str:
    """Remove invisible carriers, fold space homoglyphs. Preserves emoji."""
    out: list[str] = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        if 0x20 <= cp < 0x7F or ch in "\n\t\r":
            out.append(ch)
            continue
        result = classify(cp)
        if result is None:
            out.append(ch)
            continue
        kind, _ = result

        if cp == 0x200D:
            prev_ch = text[i - 1] if i > 0 else None
            next_ch = text[i + 1] if i + 1 < len(text) else None
            if _is_pictographic(prev_ch) and _is_pictographic(next_ch):
                out.append(ch)
                continue
        elif cp == 0xFE0F:
            if _is_pictographic(text[i - 1] if i > 0 else None):
                out.append(ch)
                continue

        if kind == "space_homoglyph":
            out.append(SPACE_HOMOGLYPHS[cp])
            continue
        # Everything else in a suspicious class is dropped.
    return "".join(out)


# --------------------------------------------------------------------------
# File discovery
# --------------------------------------------------------------------------

DEFAULT_EXTENSIONS = {
    ".tex", ".bib", ".sty", ".cls", ".bbl",
    ".md", ".markdown", ".txt", ".rst",
    ".yml", ".yaml", ".json", ".toml", ".cff",
    ".py", ".r", ".R", ".jl", ".do", ".sh", ".m",
}

EXCLUDE_DIRS = {
    ".git", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "out", "build", "dist", ".archive", "_minted",
}

# Never read, never write — see rules/data-sensitivity.md
PROTECTED_PARTS = ("data/raw",)

OVERLEAF_MARKERS = ("Apps/Overleaf",)


def is_protected(path: Path) -> bool:
    posix = path.as_posix()
    return any(part in posix for part in PROTECTED_PARTS)


def is_live_surface(path: Path) -> bool:
    resolved = path.resolve().as_posix()
    return any(marker in resolved for marker in OVERLEAF_MARKERS)


def discover(target: Path, extensions: set[str]) -> list[Path]:
    if target.is_file():
        return [target]
    found: list[Path] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if is_protected(p):
            continue
        if p.suffix in extensions:
            found.append(p)
    return found


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

_KIND_HINTS = {
    "zero_width": "invisible; silently corrupts identifiers and exact-match edits",
    "bidi": "reorders rendering relative to byte order",
    "invisible_math": "parses as structure, renders as nothing",
    "tag_char": "deprecated tag character; a steganographic carrier",
    "variation_selector": "invisible glyph-variant selector",
    "invisible_format": "zero-width formatting control",
    "space_homoglyph": "looks like a space, is not U+0020",
    "other_format": "unenumerated format character",
}


def render_human(reports: list[FileReport], *, verbose: bool) -> str:
    lines: list[str] = []
    total_files = len([r for r in reports if r.actionable])
    all_findings = [f for r in reports for f in r.actionable]
    rescued = [f for r in reports for f in r.findings if f.rescued]

    if not all_findings:
        lines.append(f"CLEAN — scanned {len(reports)} file(s), no invisible-Unicode findings.")
        if rescued:
            lines.append(f"  ({len(rescued)} legitimate emoji sequence(s) rescued, unchanged.)")
        return "\n".join(lines)

    crit = [f for f in all_findings if f.severity == CRITICAL]
    warn = [f for f in all_findings if f.severity == WARNING]

    lines.append(
        f"{len(all_findings)} finding(s) in {total_files} file(s): "
        f"{len(crit)} critical, {len(warn)} warning"
    )
    lines.append("")

    for report in reports:
        actionable = report.actionable
        if not actionable:
            continue
        lines.append(f"{report.path}")
        for f in sorted(actionable, key=lambda x: (-_SEVERITY_ORDER[x.severity], x.line, x.col)):
            tag = "CRIT" if f.severity == CRITICAL else "warn"
            where = f":{f.line}:{f.col}"
            ctx = f"  [in {f.context}]" if f.context else ""
            lines.append(f"  {tag} {where:>12}  {f.label}{ctx}")
            if verbose:
                hint = _KIND_HINTS.get(f.kind, "")
                if hint:
                    lines.append(f"       {hint}")
                lines.append(f"       {f.line_text.strip()[:100]!r}")
        lines.append("")

    if rescued:
        lines.append(f"{len(rescued)} legitimate emoji sequence(s) rescued — not counted, never rewritten.")
        lines.append("")

    lines.append("Re-run with --diff to preview fixes, or --apply to write them.")
    return "\n".join(lines)


def render_json(reports: list[FileReport]) -> str:
    payload = {
        "files_scanned": len(reports),
        "findings": [f.to_dict() for r in reports for f in r.findings],
        "summary": {
            "critical": sum(1 for r in reports for f in r.actionable if f.severity == CRITICAL),
            "warning": sum(1 for r in reports for f in r.actionable if f.severity == WARNING),
            "rescued": sum(1 for r in reports for f in r.findings if f.rescued),
        },
        "errors": [{"path": str(r.path), "error": r.error} for r in reports if r.error],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("targets", nargs="+", type=Path, help="Files or directories to scan")
    p.add_argument("--check", action="store_true",
                   help="Exit non-zero when findings at or above --fail-on are present")
    p.add_argument("--diff", action="store_true", help="Show a unified diff of proposed fixes")
    p.add_argument("--apply", action="store_true", help="Write fixes in place")
    p.add_argument("--fail-on", choices=[INFO, WARNING, CRITICAL], default=CRITICAL,
                   help="Severity floor for --check (default: critical)")
    p.add_argument("--format", choices=["human", "json"], default="human")
    p.add_argument("--ext", help="Comma-separated extension allowlist (default: research sources)")
    p.add_argument("--verbose", "-v", action="store_true", help="Show hints and source lines")
    p.add_argument("--yes-live-surface", action="store_true",
                   help="Permit --apply on an Overleaf-canonical path")
    args = p.parse_args()

    if args.apply and args.diff:
        print("error: --diff and --apply are mutually exclusive", file=sys.stderr)
        return 2

    extensions = (
        {e if e.startswith(".") else f".{e}" for e in args.ext.split(",")}
        if args.ext else DEFAULT_EXTENSIONS
    )

    paths: list[Path] = []
    for target in args.targets:
        if not target.exists():
            print(f"error: no such path: {target}", file=sys.stderr)
            return 2
        if is_protected(target):
            print(f"refusing to read protected path (data-sensitivity): {target}", file=sys.stderr)
            return 2
        paths.extend(discover(target, extensions))

    if not paths:
        print("No matching files found.", file=sys.stderr)
        return 0

    reports: list[FileReport] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            reports.append(FileReport(path=path, error=str(exc)))
            continue
        reports.append(FileReport(path=path, findings=scan_text(text, str(path))))

    # --- diff / apply -----------------------------------------------------
    if args.diff or args.apply:
        changed = 0
        for report in reports:
            if not report.actionable:
                continue
            original = report.path.read_text(encoding="utf-8")
            cleaned = clean_text(original)
            if cleaned == original:
                continue

            if args.diff:
                diff = difflib.unified_diff(
                    original.splitlines(keepends=True),
                    cleaned.splitlines(keepends=True),
                    fromfile=f"{report.path} (current)",
                    tofile=f"{report.path} (cleaned)",
                )
                sys.stdout.writelines(diff)
                changed += 1
                continue

            if is_live_surface(report.path) and not args.yes_live_surface:
                print(
                    f"skipped (Overleaf-canonical live surface): {report.path}\n"
                    f"  Re-run with --yes-live-surface once you are out of the Overleaf editor.",
                    file=sys.stderr,
                )
                continue
            report.path.write_text(cleaned, encoding="utf-8")
            print(f"fixed {len(report.actionable)} finding(s): {report.path}", file=sys.stderr)
            changed += 1

        if args.apply:
            print(f"\n{changed} file(s) modified.", file=sys.stderr)
            return 0
        if changed == 0:
            print("No changes to preview.", file=sys.stderr)
        return 0

    # --- report -----------------------------------------------------------
    if args.format == "json":
        print(render_json(reports))
    else:
        print(render_human(reports, verbose=args.verbose))

    for report in reports:
        if report.error:
            print(f"error reading {report.path}: {report.error}", file=sys.stderr)

    if args.check:
        floor = _SEVERITY_ORDER[args.fail_on]
        hits = [
            f for r in reports for f in r.actionable
            if _SEVERITY_ORDER[f.severity] >= floor
        ]
        return 1 if hits else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
