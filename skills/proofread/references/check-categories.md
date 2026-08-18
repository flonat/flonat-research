# Proofread — Check Categories

> The 11 check categories run by the `proofread` skill (Workflow step 3). Extracted from `SKILL.md` for leanness; this file is the authoritative catalogue.

## 1. Grammar & Spelling

- Spelling errors (including technical terms)
- Subject-verb agreement
- Sentence fragments or run-ons
- Misused words (e.g., "effect" vs "affect", "which" vs "that")
- American English is the default for all papers and conference articles. Flag any British English spellings (e.g., -ise, -our, -re, analyse, scepticism).

## 2. Notation Consistency

- Variable notation used consistently throughout (e.g., always `$x_i$` or always `$x_{i}$`, not both)
- Subscript/superscript style (e.g., `$\beta_1$` vs `$\beta_{OLS}$`)
- Matrix/vector formatting conventions (bold, uppercase, etc.)
- Consistent use of `\mathbb`, `\mathcal`, `\mathbf` for sets, operators, vectors
- Equation numbering: all referenced equations numbered, unreferenced ones unnumbered

## 3. Citation Format

- Consistent use of `\citet` (textual) vs `\citep` (parenthetical)
- No raw `\cite{}` when `\citet`/`\citep` is available
- Author name spelling matches between text mentions and citation keys
- Multiple citations in chronological or alphabetical order (check which convention)
- No "As shown by (Author, Year)" — should be "As shown by \citet{key}"

## 4. Academic Tone

- No informal contractions (don't, can't, won't → do not, cannot, will not)
- No first-person overuse (some "we" is fine; excessive "I think" is not)
- No casual hedging ("pretty much", "kind of", "a lot")
- Appropriate use of hedging language ("suggests" vs "proves")
- No exclamation marks in body text
- Consistent tense (present for established facts, past for specific studies)
- **Filler hedge phrases to flag** (delete on sight): "interestingly", "importantly", "it is worth noting", "it should be noted that", "needless to say", "of course", "obviously", "clearly" (unless something is literally clear from a figure)
- **Vague quantifiers to flag**: "very", "quite", "rather", "somewhat", "fairly" — replace with specific magnitudes or delete
- **Tautological constructions**: "significant and important", "novel and new", "unique and distinctive" — one adjective suffices

## 5. LaTeX-Specific Issues

- **Overfull hbox**: Check `.log` file for `Overfull \hbox` warnings — report line numbers and severity (badness)
- **Equation overflow**: Long equations that exceed column/page width
- **Float placement**: Check for `[h!]` or `[H]` overuse; prefer `[tbp]`
- **Missing labels**: Figures/tables/equations referenced but without `\label{}`
- **Orphan/widow lines**: Check for `\\` abuse that creates bad page breaks
- **Unresolved references**: `??` in output indicating broken `\ref{}` or `\cite{}`

## 6. Citation Voice Balance

Check the ratio of in-line (`\citet`) to parenthetical (`\citep`) citations:

- **Count in-line vs parenthetical citations** across the full document
- **Flag if ratio exceeds 1:1** (in-line should be the minority) — Major
- **Flag runs of 3+ consecutive in-line citations** in a paragraph or section — Major
- **Flag paragraphs that open with an in-line citation** when the author's identity isn't the point — Minor
- **Flag "As shown by \citet{}" patterns** where parenthetical would be more natural — Minor
- **Report the overall ratio** (e.g., "42 parenthetical, 28 in-line — ratio 1.5:1")

See `docs/reference/conventions.md` § Citation Voice Balance for the full convention.

## 7. TikZ Diagram Review

If the document contains TikZ code (`\begin{tikzpicture}` or `\tikz`):

- **Label positioning**: Labels not overlapping nodes or edges
- **Geometric accuracy**: Coordinates and angles consistent with intended layout
- **Visual semantics**: Arrow styles match meaning (solid = direct, dashed = indirect, etc.)
- **Spacing**: Nodes not too cramped or too spread out
- **Consistency**: Style matches across all diagrams in the document
- **Standalone compilability**: Each diagram should compile independently

For detailed spatial verification (Bezier depth calculations, gap minimums, shape boundary clearance), see [`../../shared/tikz-rules.md`](../../shared/tikz-rules.md).

## 8. Numeric Text↔Table Cross-Check

Cross-check every number mentioned in the prose against the corresponding table or figure. Flag ANY discrepancy, no matter how small.

- **Coefficient claims**: "a 3.2 percentage point increase" in text vs coefficient of 0.031 in the table — flag the mismatch
- **Sample sizes**: "N = 1,247" in text vs N row in table — must match exactly
- **Significance claims**: "statistically significant at the 5% level" in text vs the actual stars/p-value in the table
- **Summary statistics**: means, medians, standard deviations mentioned in prose must match the descriptive statistics table
- **Figure references**: claims about trends or magnitudes must be consistent with what the figure shows
- **Table/figure existence**: every table/figure referenced in text must exist; every table/figure in the document must be referenced in text
- **N consistency**: the number of observations should be consistent across related specifications unless there's an explained reason for differences

## 9. Causal Language Audit

Audit causal claims against the stated identification strategy. The strength of causal language must match the strength of the research design.

- **Flag "X causes Y"** or "the causal effect of X" when the identification strategy is observational (OLS with controls, correlational) — should be "is associated with" or "predicts"
- **Flag "proves"** — almost never appropriate; use "provides evidence consistent with"
- **Match language to design**:
  - DiD/RDD/IV → "we estimate the causal effect" is acceptable with qualifiers
  - OLS with controls → "we find a relationship" or "our estimates suggest"
  - Correlational → never use causal language
- **Flag "significant" ambiguity** — must always be clear whether "statistically significant" or "economically meaningful/large"
- **Flag coefficient descriptions without units or scale** — "a coefficient of 0.031" means nothing without knowing the units of X and Y
- **Flag correlation/causation conflation** — any statement that slides from an association to a causal claim without an identification argument

## 10. Equation Completeness

Verify that mathematical notation is complete and internally consistent.

- **Every variable in an equation must be defined** in the text (either before or immediately after the equation)
- **Error terms**: properly specified (ε_it vs u_i vs e_ij) and consistent with the econometric framework described
- **Equation numbering**: sequential, and all cross-references to equations are correct
- **Subscript/index structure must match the level of observation** — e.g., if the text describes individual-level variation, the equation should have individual subscripts, not county-level
- **Summation/expectation indices**: verify bounds match the described sample
- **Consistent notation across equations**: don't switch between β and b for the same coefficient, or between X_i and x_i

## 11a. Anonymity (double-blind venues only)

If the project's vault submission frontmatter or CLAUDE.md indicates a double-blind venue (CCS, NDSS, S&P, USENIX, ICML, NeurIPS, ICLR, FAccT, AAAI, etc.), run paper-side checks P1–P8 from `<skills-root>/_shared/double-blind-anonymity-checklist.md` and flag every FAIL as **Critical**:

- **P1** title page anonymized (no `\author{}` with real names)
- **P2** no `\thanks{}`, `\acknowledgements`, funding, or grant references in body
- **P3** body uses third-person self-reference (no "we previously showed", "in our prior work")
- **P4** self-citations are cited in the third person with the **real bib entry kept** — do *not* flag a named self-cite entry as a violation; naming the authors in a third-person citation is correct (anonymity comes from the author block, not the bibliography). Blind the entry only if the venue's CFP explicitly requires it (rare; some security venues). See `rules/double-blind-self-citation.md`.
- **P5** self-references use third-person *voice*: flag first-person ("we previously showed", "in our prior work [N]") near a self-cite — **not** the author names themselves ("[Author] and [Collaborator] [N] show X" is fine)
- **P6** no identifying URLs (personal websites, GitHub repos with handles)
- **P7** PDF metadata clean (`pdfinfo` shows no Author / identifying Subject)
- **P8** figures/screenshots have no identifying watermarks

Skip this section only when the user explicitly says single-blind / non-blind.

## 11. Preprint Staleness

For every citation that looks like a preprint or working paper, check whether a peer-reviewed version has since been published. Flag stale preprints as Major issues.

- **Detection signals**: URL contains `arxiv.org`, `ssrn.com`, `nber.org`; journal field says "Working Paper", "mimeo"; entry type is `@techreport` or `@unpublished`
- **Action**: note the stale citation and suggest the published venue/year
- **This is a light preprint check** — flag only obvious cases visible from the `.bib` or `\bibitem` entries. For thorough checking, recommend a configured bibliography validator or authoritative metadata lookup.
