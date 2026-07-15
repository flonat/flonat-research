# Init Project Research — Scaffold Tree

> Detailed reference extracted from `SKILL.md` Phase 3.

## Common Core (always created)

```
<Folder Name>/
├── CLAUDE.md
├── README.md
├── MEMORY.md
├── REVIEW-STATE.md      # Per-project review log; populated by 20 review tools; rendered by review-recap
├── .gitignore
├── .context/
│   ├── current-focus.md
│   ├── field-calibration.md
│   └── project-recap.md
├── .claude/
│   ├── hooks/
│   │   └── copy-paper-pdf.sh   # PostToolUse hook — copies paper-*/paper/main.pdf → backup/*_vcurrent.pdf
│   └── settings.local.json
├── docs/
│   ├── literature-review/  # .gitkeep
│   ├── readings/           # .gitkeep
│   └── venues/             # .gitkeep (submission/venue material only)
├── log/                   # .gitkeep
├── paper-{venue}/         # Paper directory (Phase 5):
│   ├── paper/             #   Symlink → Overleaf — LaTeX source ONLY
│   │                      #   Venue-specific files (checklists, cover letters) live in parent
│   └── correspondence/
│       └── referee-reviews/  # .gitkeep (see scaffold-details.md for review structure)
├── backup/                # Local backups of Overleaf paper directories (subdirs per paper)
├── github-repo/           # (Optional) Separate git repo for public GitHub code release
├── knowledge/             # .gitkeep (LLM-maintained wiki — compiled by compile-knowledge)
├── correspondence/
│   └── internal-reviews/  # .gitkeep (HUMAN internal reviews — co-author feedback, supervisor notes; NOT agent reports)
├── reviews/               # .gitkeep — canonical home for ALL agent/skill review reports.
│                          # Sub-folders auto-created on first run: reviews/{check-name}/<YYYY-MM-DD-HHMM>.md
│                          # Schema: ~/Task-Management/docs/reference/review-state-schema.md
└── to-sort/               # .gitkeep
```

## Conditional Structure

**Experimental** — add: `code/python/`, `code/R/`, `data/raw/`, `data/processed/`, `output/figures/`, `output/tables/`, `output/logs/`

**Computational** — add: `src/<project-name>/` (with `__init__.py`), `tests/`, `experiments/configs/`, `results/`, `output/logs/`, `pyproject.toml`, `.python-version`

**Theoretical** — nothing extra.

**Mixed** — present elements and ask which to include.

**Venues:** When a target venue is known, seed `docs/venues/<venue-slug>/submission/`. For conference venues, also seed a submission checklist. Full venue structure and checklist template: [`scaffold-details.md`](scaffold-details.md).

## Python Tooling

**Always use `uv` — never bare `pip`, `python`, or `requirements.txt`.** For computational projects, init with `uv init`. For experimental projects, add `pyproject.toml` when dependencies are first needed.

## Implementation

```bash
mkdir -p <dir> && touch <dir>/.gitkeep  # Create all directories
mkdir -p .claude/hooks                   # Create hook, chmod +x
mkdir -p .claude/state                   # Machine-specific memory (gitignored)
```
