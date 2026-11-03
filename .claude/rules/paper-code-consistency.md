# Rule: Paper-vs-Code Consistency Check

## Principle

**Before committing edits to §experiments or §methods, grep the actual code against the prose claim.** Paper-vs-code drift surfaces at peer-review time as a "soundness" or "reproducibility" objection; by then the fix is harder than catching it at commit time. AI reviewers and careful human reviewers both catch these — the lesson is that they shouldn't be there to catch.

## When this applies

- Editing `§experiments`, `§methods`, `§setup`, `§appendix-implementation` of an empirical paper
- Editing a method paragraph that describes a hyperparameter grid, optimisation procedure, search strategy, threshold, or filter
- Adding a constraint to a displayed equation (`s.t. …`) that is supposed to mirror a runtime check
- Auto-generated tables / macros that depend on a CSV — verify the macro values match a fresh CSV recompute, not a stale one
- Cross-referencing equation labels (e.g. "the utility floor in Eq. 2") — the label and the code path must agree

## When to skip

- Bibliography, related work, discussion sections (no code claims)
- Pure proof / theory sections
- Prose the user explicitly says is aspirational ("the formulation; implementation defers to follow-on")
- Trivial polish: rewording without changing claims

## Check protocol (≈60 s per claim)

1. **For every quantitative claim in the prose** (grid size, search space values, threshold, regularisation range, optimiser choice, number of seeds), open the code location that produces it. Grep is fine. The values in code and prose must match exactly.
2. **For every constraint in formal notation** (e.g. Eq. 2 with `s.t. Acc(f) ≥ α`), find the runtime check that enforces it. If there is no runtime check, the prose must say so (e.g. "we report the post-hoc utility distribution rather than filtering at search time").
3. **For every "the auditee does X" or "we use X" claim**, confirm X actually appears in the merged code (not a planned version, not a branch, not a stale `__pycache__`).
4. **For auto-generated tables**, recompute the source CSV before committing, then regenerate the table. Stale `\input{generated/foo.tex}` files cause silent number-drift across edits.

## Anti-Patterns

- **Don't** treat "the code probably does what the paragraph says" as a check. The whole point of the rule is that "probably" lies.
- **Don't** rely on a `__pycache__` file to confirm a behaviour. Read the `.py`.
- **Don't** regenerate a table from an old CSV "to save time" — that's exactly the drift the rule catches.
- **Don't** assume that because §experiments compiled, the claims in it are still valid. LaTeX compilation tells you about syntax, not about whether the code does what you said.

**Related:** `code-paper-auditor`, `mark-unverified`, `proofread`, `pre-submission-report` · **Background:** incidents and full cross-references
