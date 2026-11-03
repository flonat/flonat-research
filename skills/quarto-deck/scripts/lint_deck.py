#!/usr/bin/env python3
"""Mechanical lint for a Quarto Reveal.js deck (.qmd).

Cheap, deterministic checks that run before the rhetoric review. They catch
problems an LLM review is bad at noticing (missing files, broken fragment
classes, stray inline styles) and flag slides worth a human look. Judgement
calls (narrative, one idea per slide, title quality) stay with the review.

Understands Quarto structure: YAML front matter, fenced code chunks (so R and
Python `## comments` are never mistaken for slide titles), `::: notes` in both
spellings, and nested `:::` divs such as columns.

Exit status: 1 if any ERROR (or any WARN with --strict), else 0.

Usage:
    uv run python lint_deck.py deck.qmd [--strict] [--json]
                                        [--max-words 70] [--max-bullets 6]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import unquote

FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^(#{1,2})\s+(.*?)\s*(\{.*\})?\s*$")
DIV_OPEN_RE = re.compile(r"^(:{3,})\s*(.*)$")
NOTES_OPEN_RE = re.compile(r"^:{3,}\s*(\{[^}]*\.notes\b[^}]*\}|notes)\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)[^)]*\)(\{[^}]*\})?")
BULLET_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+\S")
INLINE_STYLE_RE = re.compile(r"\bstyle\s*=\s*\"")
STAT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
CITE_RE = re.compile(r"@[A-Za-z][\w:-]+|\[\^|\bsource\b", re.IGNORECASE)
# Placeholders from templates/deck.qmd that must never reach a delivered deck.
PLACEHOLDER_RE = re.compile(
    r"\[(?:XX|Claim|Assertion|Act I|Step\]|One line|One sentence|First point|Second point|"
    r"Last point|Point that|What the|What you say|Presenter\]|Venue or course|Short deck name|"
    r"author, year|data or @|figure\]|Never ship)"
)
# Body markers: a blank line, and a `:::` div boundary (columns end a list).
BLANK = ""
DIV_BREAK = "\x00"

# Titles that name a section instead of stating a claim (assertion-evidence).
LABEL_TITLES = {
    "introduction", "intro", "motivation", "background", "outline", "agenda",
    "overview", "method", "methods", "methodology", "data", "results",
    "findings", "discussion", "conclusion", "conclusions", "summary",
    "limitations", "future work", "next steps", "questions", "thank you",
    "thanks", "references", "appendix", "contributions", "related work",
    "literature review", "research question", "research questions",
}


@dataclass
class Slide:
    index: int
    level: int
    title: str
    line: int
    body: list[tuple[int, str]] = field(default_factory=list)  # visible prose lines
    attrs: list[tuple[int, str]] = field(default_factory=list)  # `::: {...}` div openers
    has_notes: bool = False
    code_lines: int = 0


@dataclass
class Finding:
    severity: str  # ERROR, WARN, INFO
    slide: int
    line: int
    title: str
    message: str


def strip_front_matter(lines: list[str]) -> int:
    """Return the index of the first body line after YAML front matter."""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() in ("---", "..."):
                return i + 1
    return 0


def has_content(slide: Slide) -> bool:
    return any(text not in (BLANK, DIV_BREAK) for _, text in slide.body)


def parse(text: str) -> tuple[list[Slide], list[tuple[int, str]]]:
    """Split the deck into slides; also return unclosed fences and divs.

    An unclosed `::: notes` or div would otherwise hide every later slide from
    the lint without a word, so the caller reports them as errors.
    """
    lines = text.splitlines()
    start = strip_front_matter(lines)
    slides: list[Slide] = []
    current = Slide(index=0, level=0, title="(title slide)", line=1)
    fence: str | None = None
    fence_line = 0
    notes_depth: int | None = None
    div_stack: list[tuple[int, bool]] = []  # (opening line, is notes)

    def push(slide: Slide) -> None:
        if slide.index > 0 or has_content(slide) or slide.code_lines:
            slides.append(slide)

    for number, raw in enumerate(lines[start:], start=start + 1):
        line = raw.rstrip("\n")
        stripped = line.strip()

        if fence is not None:
            current.code_lines += 1
            if stripped.startswith(fence):
                fence = None
            continue
        match = FENCE_RE.match(stripped)
        if match:
            fence = match.group(1)
            fence_line = number
            continue

        if notes_depth is None and NOTES_OPEN_RE.match(stripped):
            div_stack.append((number, True))
            notes_depth = len(div_stack)
            current.has_notes = True
            continue
        div = DIV_OPEN_RE.match(stripped)
        if div:
            if div.group(2):
                div_stack.append((number, False))
                if notes_depth is None:
                    current.attrs.append((number, line))
            elif div_stack:
                if notes_depth == len(div_stack):
                    notes_depth = None
                div_stack.pop()
            if notes_depth is None:
                current.body.append((number, DIV_BREAK))
            continue
        if notes_depth is not None:
            continue  # speaker notes are not projected

        heading = HEADING_RE.match(line)
        if heading and not div_stack:
            # A `---` rule directly before a heading is one boundary, not two.
            if not (current.title == "(untitled)" and not has_content(current) and not current.code_lines):
                push(current)
            current = Slide(index=len(slides) + 1, level=len(heading.group(1)),
                            title=heading.group(2).strip(), line=number)
            continue
        if stripped in ("---", "***") and not div_stack:
            push(current)
            current = Slide(index=len(slides) + 1, level=2, title="(untitled)", line=number)
            continue
        current.body.append((number, line if stripped else BLANK))
    push(current)
    for position, slide in enumerate(slides, start=1):
        slide.index = position

    unclosed: list[tuple[int, str]] = []
    if fence is not None:
        unclosed.append((fence_line, f"code fence {fence} is never closed; the rest of the deck was not linted"))
    for opened, is_notes in div_stack:
        kind = "::: notes block" if is_notes else "::: div"
        unclosed.append((opened, f"{kind} is never closed; the rest of the deck was not linted"))
    return slides, unclosed


def visible_words(slide: Slide) -> int:
    words = 0
    for _, line in slide.body:
        if line.lstrip().startswith(("{{<", "<!--", "|---", "|:--")):
            continue
        words += len(re.findall(r"[A-Za-z0-9][\w'’-]*", IMAGE_RE.sub("", line)))
    return words


def bullet_runs(slide: Slide) -> list[int]:
    """Sizes of contiguous top-level list blocks (columns are separate blocks).

    A wrapped item's continuation (indented, or a lazy line straight after the
    item) and blank lines between items stay in the block; a `:::` boundary or
    an unindented paragraph after a blank line ends it.
    """
    runs: list[int] = []
    count = 0
    previous_blank = False

    def close() -> None:
        nonlocal count
        if count:
            runs.append(count)
        count = 0

    for _, line in slide.body:
        if line == DIV_BREAK:
            close()
            previous_blank = False
            continue
        if line == BLANK:
            previous_blank = True
            continue
        match = BULLET_RE.match(line)
        if match and len(match.group(1)) == 0:
            count += 1
        elif match or (count and (line[:1].isspace() or not previous_blank)):
            pass  # nested item or continuation of the current item
        else:
            close()
        previous_blank = False
    close()
    return runs


def resolve_image(deck: Path, target: str) -> Path:
    """Filesystem path of an image reference as Quarto resolves it."""
    clean = unquote(re.split(r"[?#]", target, maxsplit=1)[0])
    if clean.startswith("/"):
        # Project-root-relative: the nearest directory holding _quarto.yml.
        root = deck.parent
        for candidate in (deck.parent, *deck.parent.parents):
            if (candidate / "_quarto.yml").exists() or (candidate / "_quarto.yaml").exists():
                root = candidate
                break
        return root / clean.lstrip("/")
    return deck.parent / clean


def lint(path: Path, max_words: int, max_bullets: int) -> tuple[list[Slide], list[Finding]]:
    text = path.read_text(encoding="utf-8")
    slides, unclosed = parse(text)
    findings: list[Finding] = [Finding("ERROR", 0, number, "(deck)", message) for number, message in unclosed]

    def add(severity: str, slide: Slide, line: int, message: str) -> None:
        findings.append(Finding(severity, slide.index, line, slide.title[:60], message))

    for slide in slides:
        content_slide = slide.level == 2
        if content_slide and slide.title.lower().strip(" .:?!") in LABEL_TITLES:
            add("WARN", slide, slide.line,
                "label title; state the slide's claim instead (assertion-evidence)")

        for number, line in slide.body:
            for alt, target, attrs in IMAGE_RE.findall(line):
                if not re.match(r"^(https?:|data:)", target) and not resolve_image(path, target).exists():
                    add("ERROR", slide, number, f"image not found: {target}")
                if not alt.strip() and "fig-alt" not in (attrs or ""):
                    add("WARN", slide, number, f"image without alt text: {target} (add fig-alt=\"...\")")
            prose = re.sub(r"\{[^}]*\}", "", line)  # drop {width="68%"}-style attributes
            if STAT_RE.search(prose) and not CITE_RE.search(prose) and not prose.lstrip().startswith("|"):
                add("INFO", slide, number, "percentage in prose with no citation on the line; check it is sourced")

        for number, line in slide.body + slide.attrs:
            if re.search(r"\.semi-fade-out\b", line):
                add("WARN", slide, number,
                    ".semi-fade-out starts fully visible; for 'show, then dim' use .fade-in-then-semi-out")
            if INLINE_STYLE_RE.search(line):
                add("WARN", slide, number, "inline style= attribute; move it to a class in the theme .scss")

        if content_slide:
            words = visible_words(slide)
            if words > max_words:
                add("WARN", slide, slide.line, f"{words} projected words (limit {max_words}); split or move to notes")
            for run in bullet_runs(slide):
                if run > max_bullets:
                    add("WARN", slide, slide.line, f"list of {run} items (limit {max_bullets}); split, group or use columns")

    for number, line in enumerate(text.splitlines(), start=1):
        if PLACEHOLDER_RE.search(line):
            findings.append(Finding("ERROR", 0, number, "(deck)",
                                    f"template placeholder left in: {line.strip()[:60]}"))

    content = [s for s in slides if s.level == 2]
    missing_notes = [s for s in content if not s.has_notes]
    if content and missing_notes:
        names = ", ".join(str(s.index) for s in missing_notes[:12])
        more = "" if len(missing_notes) <= 12 else f" (+{len(missing_notes) - 12} more)"
        findings.append(Finding("INFO", 0, 0, "(deck)",
                                f"{len(missing_notes)}/{len(content)} content slides have no speaker notes: {names}{more}"))
    return slides, findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("deck", type=Path)
    parser.add_argument("--strict", action="store_true", help="fail on warnings too")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--max-words", type=int, default=70)
    parser.add_argument("--max-bullets", type=int, default=6)
    args = parser.parse_args()

    if not args.deck.is_file():
        print(f"error: {args.deck} not found", file=sys.stderr)
        raise SystemExit(2)
    slides, findings = lint(args.deck, args.max_words, args.max_bullets)
    errors = sum(f.severity == "ERROR" for f in findings)
    warns = sum(f.severity == "WARN" for f in findings)

    if args.json:
        print(json.dumps({"deck": str(args.deck), "slides": len(slides), "errors": errors,
                          "warnings": warns, "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        sections = sum(s.level == 1 for s in slides)
        print(f"{args.deck}: {len(slides)} slides ({sections} section, {len(slides) - sections} other)")
        for finding in findings:
            if finding.slide:
                where = f"slide {finding.slide} (line {finding.line})"
            else:
                where = f"line {finding.line}" if finding.line else "deck"
            print(f"  {finding.severity:5} {where}: {finding.message}")
        print(f"{errors} error(s), {warns} warning(s)")

    failed = errors > 0 or (args.strict and warns > 0)
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
