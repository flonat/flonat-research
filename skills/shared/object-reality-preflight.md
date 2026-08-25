# Shared: Object-reality preflight

**Run these four questions BEFORE any correctness lens.** They ask whether the object of
study is real — known, non-degenerate, non-empty, and soundly delivered — rather than
whether the work about it is correct. A paper can be internally flawless and still fail
every one of them.

## Why this exists

Added 2026-08-19 from the reviewer-gap corpus. Six `gap` signals — objections real
referees raised on papers **our own agents had already reviewed** — turned out to share
one shape: none of them was a correctness error, and none of our lenses asked the
question. In one case (`collusion-resistant-compliance-auctions`) `domain-reviewer`
inspected the exact construct and *endorsed* it as "a principled bootstrap approach
(exogenous OR fixed-point) rather than ad hoc"; a WINE referee read the same pages and
found it circular. That defect later became the paper's headline result.

Two of the six were caught by referees whose self-rated expertise was **lower** than the
lenses we bring. The gap was not knowledge. It was the question.

## The four questions

### 1. Is it named?
Does the paper's core construction already exist in the literature under a standard
name? Search for the term before accepting a novelty claim. **A rediscovery can be
entirely correct** — every theorem valid, every proof sound — and still carry no
contribution.

*Evidence: three WINE referees independently identified an "RA-VCG" mechanism as
maximal-in-range, studied since Nisan & Ronen (2000). Neither the manuscript nor its
bibliography cited MIR. `domain-reviewer` ran eight times on that paper and never
raised it.*

### 2. Is it non-degenerate?
Could the central quantity be pinned to a constant, or defined in terms of itself?

- Ask what the comparator returns **if the mechanism under test is removed**. If the
  answer is "the same value", it is not measuring the mechanism.
- Trace every normaliser to its definition. A denominator defined in terms of a
  parameter that is itself defined in terms of that denominator is circular, and
  contaminates every ratio in the paper.
- A benchmark pinned to an exogenous constant the author chose is not an endogenous
  comparator, however reasonable the constant.

### 3. Is it non-empty?
Does every category, class, or condition the paper defines actually occur?

- A classifier category that **never fires anywhere in the experimental grid** indicates
  a mis-specified instrument or threshold, not a property of the world.
- A characterization covering "all X containing motif M" is vacuous if almost every X
  contains M. Ask what fraction of the domain the condition actually excludes.
- A defined-but-unreported quantity (a composite index with weights and a sensitivity
  analysis that never appears in results) is a declared deliverable that is absent.

### 4. Is the artifact sound as submitted?
Review the compiled artifact the reviewers received, not only the source.

- Unresolved cross-references (`??`) reach reviewers **inside theorem statements** even
  when the source builds locally.
- Generated tables and macros can be stale relative to the data that produced them.
- If only the source is available, say so rather than implying the artifact was checked.

## How to report

A failure here is not a "minor" or "presentation" issue. It goes at the top of the
report, ahead of correctness findings, because it changes what the correctness findings
are *about*. If question 2 or 3 fails, say explicitly which downstream results are
contaminated — usually all of them.

Passing all four is worth one line, not a section.

## Why the first version failed (2026-08-19)

The first version asked the four questions conceptually and was deployed to six agents. A
regression test against a paper with known defects returned **four PASSes on all four
questions**, including on a comparator that returns an author-chosen constant.

Two specific failure modes, now guarded against in the Step 0 procedure:

- **Q2 answered about the mechanism, not the comparator.** The agent read
  `return penalty if shortfall_expected > 0 else 0.0` and passed by discussing whether
  adaptive learning was necessary for the reported effects. "Is the mechanism interesting"
  is a different question from "can the comparator take a value the author did not choose".
  Q2 now requires naming the comparator, quoting its line, and writing the determination
  chain explicitly.
- **Q3 enumerated from the results, not the definition.** The agent listed the four
  categories that appeared, said "all reported categories appear", and passed — while two
  of the six the classifier can emit never fired in 315 cells. Q3 now requires enumerating
  from the classifier definition first, then counting instances, and reporting a row per
  emittable category including the zeros.

The general lesson: a conceptual question invites a conceptual answer, and a conceptual
answer can be confidently wrong while sounding right. Each check now specifies what to
open, what operation to perform, and the shape the answer must take. **A PASS that cannot
be evidenced in the required shape is not a PASS.**

A preflight that fires and does not detect is worse than none: it writes "4/4 PASS" into
the review record and manufactures the assurance it was built to remove.

The regression fixture is a git-archived copy of the paper and code as submitted, with the
defects present and the ground truth known. Re-test against it after any change here.

## Orchestrator responsibility (Q2 and Q3)

The deterministic Q2/Q3 checks are the **orchestrator's** job, not the agent's. Shell access
does not make an agent's self-adjudication reliable, and per
`rules/stamp-after-review-dispatch.md` a YAML grant is not a runtime guarantee. The
orchestrator runs the checks and pastes both outputs into the dispatch prompt under `Q2 check:`
and `Q3 verdict:`; the agent then *reports* them rather than *judging* them, which is the whole
point.

**If no verdict was supplied to you, mark Q2/Q3 `UNVERIFIED`. Do not substitute your own
PASS.** This has been tested directly and is the failure mode this preflight exists to stop:
across four runs and three architectures the agent reliably found the evidence and reliably
declined to fail on it.

The orchestrator-side procedure, the check invocations, and the evidence behind that finding
are in the companion file `object-reality-orchestrator.md` in this directory — kept separate
so its commands do not enter the agent bundle.
