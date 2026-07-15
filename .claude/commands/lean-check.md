---
description: 'Use when you need to MACHINE-CHECK a self-authored lemma/theorem by
  formalizing it in Lean 4 + mathlib and running `lake build` — the strongest verification
  (a clean build with no `sorry` IS a proof). R3 of the verification spectrum. Runs
  against the pre-seeded mathlib project at ~/lean-verify/mathlib_verify on the Mac
  Mini. Triggers: lean-check, ''formalize this lemma in Lean'', ''machine-check this
  theorem'', ''prove this in Lean''. NOT for stress-testing a distributional claim
  (use numerical-check), an algebra step (use symbolic-check), or claims too rich
  to faithfully state (escalate to domain-reviewer). The hard part is a FAITHFUL statement
  — a Lean lemma that doesn''t match the paper is false confidence.'
---

# Shared skill adapter

Read and follow `~/.claude/shared-skills/lean-check/SKILL.md`. Resolve bundled resources relative to `~/.claude/shared-skills/lean-check/`.
