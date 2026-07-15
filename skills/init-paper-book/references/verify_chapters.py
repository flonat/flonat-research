#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Deterministic Phase 4 verifier for init-paper-book.

Runs four mechanical checks on a drafted book against its source paper + bib:
    1. Citation key existence
    2. Self-cite fabrication (first-author lastname + year)
    3. Numeric token fidelity
    4. Acronym expansion + equation-prose pairing

Outputs JSON. Exit code 0 = pass, 1 = block.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Acronyms that need only one expansion across the book (or are universally known)
BASELINE_ACRONYMS = {
    # Project / paper-specific
    "DM", "GP", "BO", "MOBO", "ABM", "EI", "EHVI", "MCDM", "VOI", "MAP",
    "MSR", "ETS", "DTLZ", "BC", "NSGA", "CAPE", "PS", "IA",
    # Statistics / ML
    "SE", "KG", "CV", "AR", "GPFS", "MCMC", "BFGS", "ELBO", "KL", "CDF",
    "PDF", "MAP", "MLE", "EM", "SGD", "RL", "NN", "GP", "GAN", "VAE",
    # File / format
    "JSON", "YAML", "XML", "CSV", "TSV", "PNG", "JPG", "SVG", "WEBP",
    "PDF", "TEX", "BIB", "MD", "HTML", "CSS", "JS",
    # Universally-understood proper-noun acronyms (not the domain jargon this floor targets)
    "AI", "EU", "ACM", "AIES",
    # Generic / status / dimensions
    "DOI", "URL", "API", "CLI", "GUI", "ID", "UI", "ON", "OFF", "YES", "NO",
    "OK", "OS", "IO", "HTTP", "HTTPS", "TCP", "UDP", "IP",
    # Common docs
    "README", "TODO", "FIXME", "NOTE", "WARN", "INFO", "DEBUG", "ERROR",
    # Roman numerals (avoid flagging NSGA-II, CAPE-II etc.)
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
}

CHAPTER_NAMES = [
    "intro", "background", "setup", "method", "results",
    "limitations", "extend", "appendix",
]

CITE_RE = re.compile(r"\{cite:[tp]\}`([^`]+)`")
NUMERIC_RE = re.compile(r"[-+]?\d+\.\d+(?:[eE][-+]?\d+)?(?:\s*[±]\s*\d+\.?\d*)?|\d+%")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([A-Za-z0-9_:.-]+)\s*,")
# Acronyms — match hyphenated compounds (NSGA-II, CAPE-MOBO, L-BFGS-B) as units, but
# strip the parts so each component gets checked against the baseline.
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:[-/][A-Z0-9]+)*\b")
DISPLAY_MATH_RE = re.compile(r"\$\$.+?\$\$", re.DOTALL)


def parse_bib_keys(bib_path: Path) -> set[str]:
    if not bib_path.exists():
        return set()
    text = bib_path.read_text(encoding="utf-8", errors="ignore")
    return set(BIB_KEY_RE.findall(text))


def strip_math(text: str) -> str:
    """Remove math segments to avoid extracting numbers inside equations."""
    text = re.sub(r"\$\$.+?\$\$", " ", text, flags=re.DOTALL)
    text = re.sub(r"\$[^$\n]+\$", " ", text)
    return text


def normalize_for_numeric_match(text: str) -> str:
    """Normalize LaTeX vs Markdown for cross-document string comparison.

    Paper uses `\\pm`, `\\%`, `--`, `\\mathbf{...}`, etc.
    Book uses `±`, `%`, `–`, plain text.
    """
    # ± symbol
    text = text.replace("\\pm", "±")
    text = re.sub(r"\$\\pm\$", "±", text)
    # percent
    text = text.replace("\\%", "%")
    # En-dash, em-dash
    text = text.replace("---", "—").replace("--", "–")
    # Strip LaTeX boldface/math wrappers
    text = re.sub(r"\\mathbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    # Collapse whitespace around ±
    text = re.sub(r"\s*±\s*", " ± ", text)
    return text


# Patterns that are section references, not data values
SECTION_REF_RE = re.compile(r"(?:§|paper\s*§|Section\s*|Sec\.?\s*|paper\s*Eq\.?\s*|Eq\.?\s*|paper\s*Table\s*|Table\s*|paper\s*Figure\s*|Figure\s*|Fig\.?\s*)\s*\d+(?:\.\d+)?")


def check_citations(chapter_text: str, bib_keys: set[str], first_author: str) -> tuple[list, list]:
    """Return (missing_keys, self_cite_keys) — each a list of dicts."""
    missing = []
    self_cite = []
    self_cite_re = re.compile(rf"(?i)^{re.escape(first_author)}\d{{4}}")
    for line_no, line in enumerate(chapter_text.splitlines(), start=1):
        for match in CITE_RE.finditer(line):
            # Each match may have comma-separated keys
            for key in match.group(1).split(","):
                key = key.strip()
                if key not in bib_keys:
                    missing.append({"key": key, "line": line_no})
                if self_cite_re.match(key):
                    self_cite.append({"key": key, "line": line_no})
    return missing, self_cite


def check_numerics(chapter_text: str, paper_text: str) -> list:
    """Find numeric tokens in chapter not present in paper.

    Applies LaTeX↔Markdown normalization on both sides before comparison.
    """
    drift = []
    # Normalize and de-math the paper for comparison
    paper_norm = normalize_for_numeric_match(paper_text)
    paper_norm_squashed = re.sub(r"\s+", " ", paper_norm)
    chapter_stripped = strip_math(chapter_text)

    for line_no, line in enumerate(chapter_stripped.splitlines(), start=1):
        # Skip figure paths and URLs
        if "figures/" in line or "](http" in line:
            continue
        # Skip lines that are pure section-ref pointers (e.g. "paper §3.3")
        line_for_refs = line
        # Mask out section references before extracting numbers
        line_masked = SECTION_REF_RE.sub("§REF", line_for_refs)
        for match in NUMERIC_RE.finditer(line_masked):
            value = match.group(0).strip()
            # Skip years
            if YEAR_RE.fullmatch(value):
                continue
            # Skip line ordinals
            if re.match(rf"^\s*{re.escape(value)}\b", line):
                continue
            # Skip small integers (likely counts, not data) that are <=12 unless decimal
            if "." not in value and "%" not in value and "±" not in value:
                try:
                    if abs(int(value)) <= 12:
                        continue
                except ValueError:
                    pass
            # Normalize value for paper search
            value_norm = normalize_for_numeric_match(value)
            value_norm_squashed = re.sub(r"\s+", " ", value_norm)
            if value_norm in paper_norm or value_norm_squashed in paper_norm_squashed:
                continue
            # Last resort: try without spaces
            alt = value_norm.replace(" ", "")
            if alt in paper_norm.replace(" ", ""):
                continue
            context = line.strip()[:120]
            drift.append({"value": value, "line": line_no, "context": context})
    return drift


def check_acronyms(chapter_text: str) -> list:
    """Flag acronyms used without expansion."""
    violations = []
    # Build the set of acronyms expanded in this chapter
    # Expansion pattern: "<phrase> (ACRONYM)" or "<phrase> (ACRONYMs)"
    expanded = set()
    for m in re.finditer(r"\(([A-Z]{2,})s?\)", chapter_text):
        expanded.add(m.group(1))
    expanded |= BASELINE_ACRONYMS

    # Also expand baseline by splitting compound acronyms in expanded set
    # (e.g. if "CAPE-MOBO" is mentioned, accept "CAPE" and "MOBO" as expanded too)
    for compound in list(expanded):
        for part in re.split(r"[-/]", compound):
            if len(part) >= 2 and part.isupper():
                expanded.add(part)

    seen_acronyms: dict[str, int] = {}
    for line_no, line in enumerate(chapter_text.splitlines(), start=1):
        # Skip frontmatter
        if line.startswith("---"):
            continue
        for m in ACRONYM_RE.finditer(line):
            acr = m.group(0)
            # Skip if the compound or any meaningful part is baseline/expanded
            parts = re.split(r"[-/]", acr)
            if acr in expanded or all(part in expanded or len(part) < 2 or part.isdigit() for part in parts):
                continue
            if acr not in seen_acronyms:
                seen_acronyms[acr] = line_no
                violations.append({
                    "issue": "missing_acronym_expansion",
                    "detail": acr,
                    "line": line_no,
                })
                expanded.add(acr)  # only flag once per acronym
    return violations


def check_equation_prose(chapter_text: str) -> list:
    """Flag display equations not followed by ≥60 non-math characters."""
    violations = []
    for m in DISPLAY_MATH_RE.finditer(chapter_text):
        tail = chapter_text[m.end():m.end() + 250]
        # Count non-math characters
        tail_stripped = strip_math(tail)
        prose_chars = sum(1 for c in tail_stripped if c.isalpha() or c == " ")
        if prose_chars < 60:
            # Compute line number of the equation
            line_no = chapter_text[: m.start()].count("\n") + 1
            violations.append({
                "issue": "equation_no_prose",
                "detail": "display equation followed by <60 prose chars",
                "line": line_no,
            })
    return violations


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--book-dir", required=True, type=Path)
    p.add_argument("--paper-tex", required=True, type=Path)
    p.add_argument("--bib", required=True, type=Path)
    p.add_argument("--first-author-lastname", required=True, help="e.g. smith — for self-cite fabrication check")
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    paper_text = args.paper_tex.read_text(encoding="utf-8", errors="ignore")
    bib_keys = parse_bib_keys(args.bib)

    report = {
        "verdict": "PASS",
        "counts": {
            "missing_cite_keys": 0,
            "numeric_drift": 0,
            "out_of_scope_self_cite": 0,
            "accessibility_block": 0,
        },
        "missing_cite_keys": [],
        "numeric_drift": [],
        "out_of_scope_self_cite": [],
        "accessibility_block": [],
    }

    for chapter in CHAPTER_NAMES:
        path = args.book_dir / f"{chapter}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")

        missing, self_cite = check_citations(text, bib_keys, args.first_author_lastname)
        for item in missing:
            report["missing_cite_keys"].append({"chapter": chapter, **item})
        for item in self_cite:
            report["out_of_scope_self_cite"].append({"chapter": chapter, **item})

        for item in check_numerics(text, paper_text):
            report["numeric_drift"].append({"chapter": chapter, **item})

        for item in check_acronyms(text):
            report["accessibility_block"].append({"chapter": chapter, **item})
        for item in check_equation_prose(text):
            report["accessibility_block"].append({"chapter": chapter, **item})

    for key in report["counts"]:
        report["counts"][key] = len(report[key])

    if any(report["counts"].values()):
        report["verdict"] = "BLOCK"

    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["counts"], indent=2))
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
