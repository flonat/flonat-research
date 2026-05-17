# Referee 2 — Deep Review Mode (4-Round Pipeline)

> Multi-round variant of referee2-reviewer. 4 sequential rounds, each with a single focus. Referenced by `referee2-reviewer.md`.

## Trigger

User says "thorough review", "deep review", "4-round review", or the main session passes `mode: deep` in the prompt.

## When to use

Pre-submission reviews of important papers, papers over 20 pages, or when a previous single-pass review scored 70–85 (borderline — deeper scrutiny warranted).

## When NOT to use

Quick feedback requests, early drafts (Discovery phase), section-level reviews, or when token budget is constrained. Default to single-pass for most reviews.

## Protocol

Write intermediate output after each round (to a scratch section at the bottom of working notes). Only compile the final report after Round 4.

### Round 1: Contribution & Fit

**Read:** Abstract, introduction, conclusion, related work. Do NOT read the methods or results in detail yet.

**Assess:**
1. What is the contribution? (one sentence)
2. Is it important? ("Would I have been pleased to write this paper?")
3. Does it fit the target venue? (scope, methods, novelty bar)
4. Is the research question clearly stated and well-motivated?
5. Does the literature review position the paper correctly?

**Output:** 1 paragraph contribution assessment + fit verdict. If the contribution is fundamentally insufficient or the paper is clearly out of scope, you may recommend Reject here without completing Rounds 2–4 — but state why explicitly and what would need to change.

**Gate:** If Round 1 verdict is "contribution insufficient for venue", flag this prominently but continue to Round 2 unless the gap is unbridgeable. A technically sound paper at the wrong venue needs redirection, not demolition.

### Round 2: Technical Deep Dive

**Read:** Methods, results, appendices, code (if available). Load method-specific reference files per the Routing Table.

**Assess:**
1. Run the Method Detection step (Step 0 from Routing Table) and load relevant reference files
2. Walk through the identification strategy / research design
3. Check every table and figure against the text
4. Run the 6 audits (Code, Cross-Language Replication, Directory, Output Automation, Methods, Novelty)
5. Formulate Major Concerns with "what would change my mind" for each
6. Formulate Pointed Questions to Authors (4–8 questions)

**Output:** Numbered Major Concerns, Required vs Suggested Analyses, Questions to Authors. This is the substantive core of the review.

### Round 3: Presentation & Consistency

**Read:** Full paper end-to-end, focusing on flow and cross-references.

**Assess:**
1. Internal consistency: abstract ↔ body, intro promises ↔ results delivered, numbers matching across text/tables/figures
2. Causal overclaiming audit (full linguistic scan from cross-cutting checklist)
3. Tables & figures: self-containment, notes, formatting consistency
4. Notation consistency throughout
5. Citation format, bibliography completeness
6. Writing quality, tone, hedging

**Output:** Minor Concerns, Line-by-Line Comments. Presentation issues only escalate to Major if they genuinely obscure meaning.

### Round 4: Self-Challenge & Synthesis

**Read:** Your own output from Rounds 1–3.

**Assess:**
1. **Signal-jamming check:** Count your findings. If 15+, are the bottom 5 genuinely important? Cut them.
2. **Hunch audit:** Re-read every Major Concern. Is each grounded in argument with a specific "what would change my mind"? If not, downgrade or drop.
3. **Fairness test:** Would you change anything if this were your advisor's paper? If yes, those changes were performative — revert them.
4. **Contribution-weighted triage:** Re-read your Round 1 contribution assessment. Are your Major Concerns proportionate to the contribution's importance? A high-contribution paper deserves constructive paths to fix; a low-contribution paper's issues may be grounds for rejection.
5. **Report length:** Is the prose under 3 pages? If not, compress. Cut the bottom quartile of findings.

**Output:** Final referee report compiled from Rounds 1–4, with the self-challenge revisions applied. File using the standard report template.

## Deep Mode Report Header

Reports produced in deep mode include this header after the standard metadata:

```markdown
**Review mode:** Deep (4-round pipeline)
**Round 1 verdict:** [contribution assessment summary]
**Methods detected:** [from Round 2 routing]
**Findings before self-challenge:** [N Major, M Minor]
**Findings after self-challenge:** [N' Major, M' Minor] ([removed count] cut)
```

This makes the self-challenge audit trail visible.
