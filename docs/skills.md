# Skills

> 94 reusable workflow definitions available across all projects.

Skills are client-neutral instruction sets (`SKILL.md` files). The contract exposes each skill only to clients with the capabilities it requires.

## Overview

| Skill | Description |
|-------|-------------|
| `beamer-deck` | Create an academic Beamer presentation with original theme and multi-agent review. Use when the user requests this operation or its stated output |
| `bib-coverage` | Compare a project .bib against a Paperpile project/topic folder to find uncited papers or unfiled entries. Use when the user asks to compare a project .bib against a Paperpile project/topic folder to find uncited papers or unfiled entries |
| `bib-filter` | Filter a .bib file to only entries actually cited in a .tex project. Use when the user asks to filter a .bib file to only entries actually cited in a .tex project |
| `bib-parse` | Extract citations from a PDF and generate a validated .bib file. Use when the user asks to extract citations from a PDF and generate a validated .bib file. Reads the PDF, identifies referenced works, constructs BibTeX entries, and verifies metadata |
| `brief-compliance-check` | Check a LaTeX submission against a PDF assessment brief. Use when the user requests this operation or its stated output |
| `camera-ready` | Convert an accepted anonymous-submission LaTeX paper (AAAI/AIES/ACM-style) to camera-ready and implement the accepted reviews. Use when a paper is accepted with no rebuttal and you need to de-anonymize, add copyright, turn on section numbering, implement each reviewer's minor revisions, optionally move proofs to a non-counted appendix, and QA. Not for R&R/revise-and-resubmit (use strategic-revision --external) or for preprints (use preprint) |
| `causal-design` | Design or audit the identification strategy for an observational study. Use when the task concerns estimands, causal assumptions, threats to identification, or defensible research design rather than model implementation |
| `checkpoint` | Save session state to survive context compaction or handoff between sessions. Use when the user requests this operation or its stated output |
| `code-archaeology` | Recover the structure, intent, and lineage of old code, data, or analysis files. Use when inherited or dormant research code must be understood before it is changed. Not for a quality review of already-understood code |
| `compile-knowledge` | Compile raw inputs (literature, meeting notes, session logs, code findings) into a per-project knowledge wiki. Use when the user requests this operation or its stated output. Supports --autonomous / -y for end-to-end runs without prompts (used by the Saturday wiki-grow cron) |
| `computational-experiments` | Scaffold, execute, analyse, and publish computational research experiments through a reproducible staged workflow. Use when a research question requires simulations or computational sweeps rather than a one-off script |
| `cross-language-check` | Replicate a quantitative analysis in a second language (R↔Python↔Stata↔Julia) to verify correctness. Use when the user requests this operation or its stated output. Level 1 of the verification hierarchy |
| `data-analysis` | Deliver an end-to-end analysis pipeline: EDA, estimation, or publication output. Use when the user requests an end-to-end analysis pipeline: EDA, estimation, or publication output |
| `devils-advocate` | Adversarially challenge research assumptions, mechanisms, and arguments in writing. Use when stress-testing a claim or design before committing to it. Not for an interactive oral drill or a full referee report; use $grill-me or a review agent |
| `docs-consistency` | Review user-facing documentation for accuracy, consistency, and completeness across private, public, nested repos, and the user manual. Use when docs feel stale, after major changes, or before sharing. (Replaces `repo-doc-audit`) |
| `docx` | Create, read, edit, or convert Microsoft Word documents while preserving professional document structure. Use when a .docx file is a primary input or requested output, including tracked changes, comments, images, headings, page furniture, or polished reports and letters. Not for PDFs, spreadsheets, Google Docs, or unrelated coding tasks |
| `experiment-design` | Design empirical studies through power analysis, pre-analysis planning, QSF parsing, and survey architecture. Use when specifying sampling, measurement, treatment, or analysis before data collection. Not for causal identification alone; use $causal-design |
| `grill-me` | Run an interactive one-question-at-a-time oral drill for research defence or active-recall study, escalating around weak answers and ending with a study sheet. Use when the user asks to be grilled, quizzed, or prepared for a viva, job talk, seminar, or exam. Not for a written critique; use $devils-advocate or a review agent |
| `handoff` | Create, accept, or update the persistent `.context/ai-handoff.md` state shared by AI sessions and machines. Use when continuing in a new Claude or Codex session, transferring work between clients, or recording ownership and restart state |
| `ideas` | Capture and integrate improvement ideas for the shared Claude Code and Codex infrastructure. Use when recording an infrastructure enhancement for later review rather than implementing it immediately |
| `init-project` | Bootstrap a new research project. Interview for details, scaffold directory structure, create Overleaf symlink, initialise git, and create project context files |
| `init-project-course` | Bootstrap a university course or module folder. Use when the user requests this operation or its stated output |
| `init-project-light` | Bootstrap a lightweight project with minimal structure. Use when the user requests this operation or its stated output |
| `init-project-orchestration` | Create or migrate project-level agents, repeatable project workflows, and planning state from one client-neutral contract, then render repository-scoped adapters for both Claude Code and Codex. Use when a research project needs role separation, project commands, formal phase tracking, or conversion from an existing Claude-only .claude/agents and .claude/commands setup |
| `insights-deck` | Archive an exported Claude Code insights HTML report and turn it into a timestamped Beamer presentation usable from either client. Use when the insights export is the source artifact for a presentation. Not for a general research talk; use $talk-deck |
| `interview-me` | Conduct a structured interview to extract knowledge or preferences. Use when the user requests this operation or its stated output |
| `knowledge-lint` | Check compiled knowledge for contradictions, uncited claims, missing connections, stale articles, and orphaned concepts. Use when the user requests this operation or its stated output |
| `latex` | Compile a LaTeX document — includes autonomous error resolution, citation audit, and quality scoring. Use when the user requests this operation or its stated output |
| `latex-diff` | See what changed between two versions of a LaTeX document — two files, two project directories, or two git revisions. Use when the user requests this operation or its stated output. Produces a human-readable change summary plus a machine-readable, severity-graded list of semantic changes, and persists requested diff bundles under the canonical research-project review route |
| `latex-health-check` | Compile all LaTeX projects and report cross-project build consistency. Use when checking whether a collection of papers builds cleanly. Not for rendered visual inspection after a clean build; use $latex-polish |
| `latex-polish` | Inspect a cleanly compiling LaTeX document for source pathologies and rendered visual defects by linting and viewing selected PDF pages. Use when compilation succeeds but title pages, floats, tables, figures, or layout still need publication-quality review. Not for basic compilation health; use $latex-health-check |
| `latex-posters` | Create a research poster in LaTeX (beamerposter, tikzposter, or baposter). Use when the user requests this operation or its stated output |
| `latex-scaffold` | Convert a Markdown draft into a buildable LaTeX project. Use when the user requests this operation or its stated output |
| `latex-template` | Compare a project's LaTeX preamble and conventions against the canonical working-paper template. Use when diagnosing template drift without converting venue formats or editing prose |
| `lean-check` | Formalize a self-authored lemma or theorem in Lean 4/mathlib and require a clean `lake build` without `sorry`. Use when the mathematical claim can be stated faithfully and machine-checked. For numerical falsification or symbolic algebra, use $numerical-check or $symbolic-check |
| `math-proof` | Write clear, detailed mathematical proofs for academic papers. Use when the user asks to prove a result, derive an equation, justify a claim analytically, or expand a proof sketch into a full proof. Also trigger on "prove", "show analytically", derive", "justify mathematically", or "write a proof" |
| `mcp-builder` | Guide for creating MCP servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK) |
| `meetings-cleanup` | Manage old recordings — find large files, archive old meetings, delete processed originals. Use when the user says "clean up recordings", "how much space are meetings using", "delete old recordings", "archive meetings", "manage meeting storage", or asks about disk space from minutes |
| `meetings-debrief` | Post-meeting debrief — analyzes what happened, compares outcomes to your prep intentions, tracks decision evolution. Use when the user says "debrief", "what just happened in that meeting", "what did we decide", "debrief that call", "post-meeting", "what changed", or right after stopping a recording |
| `meetings-list` | List recent meetings and voice memos. Use when the user asks "what meetings did I have", "show my recent recordings", "any meetings today", "list my voice memos", or wants an overview of their meeting history. Also use when they need to find a specific meeting by browsing rather than searching |
| `meetings-prep` | Interactive meeting preparation — builds a relationship brief and talking points before a call. Use when the user says "prep me for my call with", "I'm meeting with X", "prepare me for", "what should I bring up with", "meeting prep", "get ready for my call", or wants to review history with someone before a meeting |
| `meetings-recap` | Generate a daily digest of today's meetings and voice memos — key decisions, action items, and themes across all recordings. Use when the user asks "recap my day", "what happened in my meetings today", "daily summary", "what did I discuss today", "any action items from today", or wants a consolidated view of the day's conversations |
| `meetings-search` | Search meeting transcripts and voice memos for people, topics, decisions, commitments, or remembered ideas. Use when the user asks what was discussed, decided, or said across their meeting history. Not for preparing an upcoming meeting; use $meetings-prep |
| `meetings-weekly` | Weekly meeting synthesis — themes, decision arcs, stale commitments, and what deserves your attention next week. Use when the user says "weekly review", "what happened this week", "weekly summary", "recap my week", "any outstanding items", "week in review", or at the end of a work week |
| `method-audit` | Extract and compare data-collection methods across a set of empirical papers. Use when the user needs a cross-paper methods matrix or wants to assess how a literature gathers evidence |
| `multi-perspective` | Explore a research question through several independent analytical perspectives and synthesize their agreements and disagreements. Use when one line of reasoning is insufficient and distinct viewpoints should be preserved |
| `numerical-check` | Numerically stress-test a self-authored mathematical claim over its parameter space to seek counterexamples or characterize violations. Use when checking monotonicity, thresholds, inequalities, comparative statics, or limits computationally. For algebraic proof or Lean formalization, use $symbolic-check or $lean-check |
| `pdf` | Read, create, combine, split, rotate, OCR, watermark, secure, or extract content from PDF files. Use when a PDF is a primary input or requested output. Not for LaTeX source editing or Word and spreadsheet deliverables |
| `pipeline-manifest` | Map scripts to their inputs, outputs, and paper figures/tables. Use when the user requests this operation or its stated output |
| `playwright-cli` | Automate browser interactions and inspect or test web pages through Playwright commands. Use when the task requires deterministic browser navigation, screenshots, selectors, or Playwright-test work. For a full local-webapp test workflow, use $webapp-testing |
| `postmortem` | Deliver a structured post-mortem after incidents, mistakes, or stuck sessions. Use when the user requests a structured post-mortem after incidents, mistakes, or stuck sessions |
| `pre-commit-audit` | Deliver a fast pre-commit safety scan: file size, anonymity (author / affiliation strings in tex/bib), and hardcoded secrets. Use when the user requests a fast pre-commit safety scan: file size, anonymity (author / affiliation strings in tex/bib), and hardcoded secrets. Triggers: 'audit before commit', 'check before push', 'pre-commit scan', 'safety check' |
| `pre-submission-report` | Run the final, comprehensive submission-readiness gate and consolidate all checks into one dated report; citation-integrity-only mode is also supported. Use when a paper and submission package are nearly final. Not for a mid-draft adversarial review; use $review-cluster |
| `project-deck` | Create a presentation deck to communicate project status. Use when the user requests this operation or its stated output |
| `project-safety` | Set up safety rules and folder structures for a research project. Use when the user requests this operation or its stated output |
| `proof-readability` | Improve the exposition and readability of a mathematical proof already verified as correct without changing its mathematics. Use when polishing a lemma, theorem, proof, or appendix after correctness checks. Not for verifying the proof; use $verify-math |
| `proofread` | Proofread a LaTeX academic paper across eleven language, notation, citation, and consistency categories. Use when the requested task is bounded proofreading rather than substantive rewriting, clarity stress-testing, or venue compliance |
| `python-env` | Create and maintain Python environments and dependencies with uv. Use when installing packages, creating a virtual environment, resolving Python dependency state, or migrating away from pip. Not for general Python coding |
| `quarto-deck` | Generate a Reveal.js HTML presentation from Markdown. Use when the user asks to generate a Reveal.js HTML presentation from Markdown |
| `reorg` | Propose and, after approval, execute content-aware file reorganization or deduplication using a local Mac Mini model with a reversible undo record. Use when sorting a folder by file contents or finding exact and near duplicates. Always dry-runs first |
| `replication-audit` | Audit which findings in a literature have been replicated or failed. Use when the user requests this operation or its stated output |
| `replication-package` | Assemble, anonymize, validate, or audit a research replication package. Use when preparing code and permitted data for reviewer or public release. Not for auditing code quality alone; use $code-suite or $replication-audit as appropriate |
| `retarget-journal` | Retarget a paper to a different journal (rename, swap bib, update citations). Use when the user requests this operation or its stated output |
| `review-cluster` | Deliver a mid-draft adversarial review of a paper — runs paper-critic + domain-reviewer + claim-verify + blindspot in parallel, optionally adds clarity-reviewer, then auto-synthesises into a prioritised revision plan. Use when the user requests a mid-draft adversarial review of a paper — runs paper-critic + domain-reviewer + claim-verify + blindspot in parallel, optionally adds clarity-reviewer, then auto-synthesises into a prioritised revision plan. Distinct from pre-submission-report (final-gate kitchen sink, 14 checks) — this is the active-drafting feedback loop. Triggers: 'review my draft', 'adversarial review', 'cluster review', 'mid-draft critique', 'feedback before pre-submission' |
| `review-response` | Systematic reviewer response workflow: parse comments, classify by severity, develop response strategy, write structured rebuttal. Use when asked to 'write rebuttal', 'respond to reviewers', 'draft review response', or 'handle R&R' |
| `session-health` | Check current context status and session health. Use when the user requests this operation or its stated output |
| `session-log` | Create a timestamped progress log for a research session. Use when the user requests this operation or its stated output |
| `skill-creator` | Create, revise, and evaluate reusable AI workflow skills, including trigger-quality tests. Use when authoring a new skill, repairing an existing skill, or measuring whether its metadata routes correctly |
| `skill-extract` | Extract reusable knowledge from the current session into a persistent skill.\nUse when you discover something non-obvious, create a workaround, or develop\na multi-step workflow that future sessions would benefit from |
| `skill-preflight` | Deliver a pre-flight duplicate check before creating new skills or agents. Use when the user requests a pre-flight duplicate check before creating new skills or agents |
| `split-pdf` | Download, split, and deeply read an academic PDF that is not available through Paperpile. Use when a long external PDF needs page-wise ingestion. For Paperpile items, use the Paperpile text-extraction route instead |
| `strategic-revision` | Turn external referee correspondence or internal pre-submission feedback into a provenance-safe, DAG-validated revision master plan with atomic tasks, dependency mapping, critical-path analysis, and execution blocks. Use when the user requests this operation or its stated output |
| `symbolic-check` | Use SymPy to prove or refute a self-authored algebraic identity, derivative, limit, comparative-static sign, or closed form. Use when exact symbolic manipulation can settle the claim. For parameter sweeps or full theorem proving, use $numerical-check or $lean-check |
| `sync-permissions` | Sync global permissions into the current project. Use when the user requests this operation or its stated output |
| `synthesise-reviews` | Synthesise parallel review reports into a prioritised revision plan. Use when the user requests this operation or its stated output |
| `synthetic-data` | Generate structurally realistic synthetic datasets for pilot testing or power analysis. Use when the user requests this operation or its stated output |
| `tailscale-mosh-recover` | Diagnose and recover Mac Mini remote-access failures across Tailscale, mosh, resolver state, and public relays. Use when mosh hangs, the headless Mini disappears after a Tailscale change, or RustDesk/VNC/AnyDesk cannot reach its relay. Not for ordinary machine synchronization |
| `task-management` | Query and update recorded planning and research-portfolio state across tasks, topics, papers, outputs, submissions, venues, people, institutions, and deadlines. Use when asking what is already recorded, including institution- or venue-associated topics, or when doing daily planning and weekly review. For venue suitability recommendations, inspect recorded state first and then use the venue-recommendation workflow |
| `test-iterate-loop` | Autonomously diagnose a codebase, apply minimal fixes, and rerun tests until they pass or a real blocker is reached. Use when the user explicitly requests an iterative fix-until-green loop across Python, R, Julia, or HPC workflows |
| `tikz` | Diagnose and fix residual TikZ label, arrow, box, and Bézier-path collisions with geometric calculations. Use when a generated .tex figure has overlapping labels or crossed arrows. Not for generating a new figure; use $figure or the upstream deck workflow |
| `update-focus` | Update current-focus.md with a structured session summary. Use when the user asks to update current-focus.md with a structured session summary |
| `update-project-doc` | Update a project's own CLAUDE.md, README.md, or docs/ to reflect current state. Use when the user asks to update a project's own CLAUDE.md, README.md, or docs/ to reflect current state |
| `venue-fork` | Fork an existing paper into a concurrent second-venue submission variant with policy checks, separate Overleaf ownership, format conversion, budget refit, QA, and Atlas/Vault writeback. Use when submitting the same work concurrently to another permitted venue. Not for preprints, ordinary retargeting, or camera-ready work |
| `venue-guidelines-compliance` | Audit a paper and submission package against current official venue requirements for its venue, track, article type, cycle, and stage. Use when checking templates, limits, anonymity, declarations, or required files before submission or inside $pre-submission-report. Not for venue recommendations |
| `verify-math` | VERIFY a self-authored mathematical result end-to-end — route each claim to the right rung of the verification spectrum (R0 adversarial review, R1 numerical falsification, R2 symbolic/CAS, R3 Lean proof) and aggregate into one verification report. Use when the user requests this operation or its stated output. The umbrella over numerical-check, symbolic-check, lean-check, and the domain-reviewer agent. Triggers: verify-math, 'verify this theorem/proposition/conjecture', 'check all the math in my paper', 'is this result correct'. Use when you have a claim and want the right method(s) chosen and combined; for a single known method, call that skill directly |
| `voice-analyzer` | Analyze representative writing samples into a portable personal voice profile and style guide. Use when establishing voice-matched editing for a new project or refreshing an outdated profile. Not for a target journal's editorial style; use $journal-voice |
| `voice-editor` | Edit draft or auto-generated prose to match an existing personal voice profile. Use when transforming generic text into the profiled author's wording, cadence, and style. Not for creating the profile or matching a journal; use $voice-analyzer or $journal-voice |
| `weakness-scanner` | Identify the weakest arguments across a literature. Use when the user requests this operation or its stated output |
| `webapp-testing` | Exercise and verify a local web application through Playwright, including user flows and rendered behaviour. Use when testing a running local app rather than issuing an isolated browser command. For ad hoc automation, use $playwright-cli |
| `wiki-curate` | Audit the vault wiki (~/vault/concepts/) for fragmentation, missing tags, write-only concepts, and draft/anatomy conformance. Use when the user requests this operation or its stated output. Read-only — produces a markdown report at /tmp/wiki-curate-report.md. Companion to wiki-grow (which writes) and wiki-merge (which fixes overlap clusters) |
| `wiki-grow` | Auto-promote eligible project knowledge articles into Research Vault concepts with generated provenance metadata. Use when running the scheduled knowledge-corpus promotion or previewing candidates interactively. Not for consolidating overlapping concepts; use $wiki-merge |
| `wiki-merge` | Merge an overlap cluster of Vault concepts into one canonical concept, rewrite wikilinks, and preserve a dry-run/apply boundary. Use when $wiki-curate has identified a winner and fold-in slugs. Not for general wiki auditing or automatic article promotion |
| `wire-shared-package` | Wire a shared Python package as an editable dependency across projects. Use when the user requests this operation or its stated output |
| `xlsx` | Create, read, edit, clean, format, chart, or convert spreadsheet files while preserving spreadsheet-native deliverables. Use when .xlsx, .xlsm, .csv, or .tsv data is the primary input or a spreadsheet is the requested output. Not for Word documents, HTML reports, standalone scripts, database pipelines, or Google Sheets API work |

## Using Skills

| Method | Example |
|--------|---------|
| Claude command | `latex` |
| Codex skill | `$latex` |
| Natural language | "Compile my paper" or "Proofread this" |

See [`availability.md`](availability.md) for the generated client-by-client inventory.

## Skill Structure

Each skill is a directory in `skills/` containing a `SKILL.md` file with:

1. **YAML frontmatter** — name, description, and allowed tools
2. **Markdown body** — structured, client-neutral workflow instructions

## Creating New Skills

1. Create a directory: `skills/<skill-name>/`
2. Add a `SKILL.md` with YAML frontmatter and markdown instructions
3. Declare its clients and requirements in the capability contract

See any existing skill for the format.
