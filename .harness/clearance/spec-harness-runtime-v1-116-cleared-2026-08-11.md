---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.116
cleared_at: 2026-08-11T19:30:00-07:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_b145_gap2a_escalate_clause_phantom_api.md
  - .harness/b145-grounding-split-2026-08-11.md
  - .harness/forward-register.yaml B-145 row (GAP-2a leg)
  - "PR #1306 (dispatch-path branch-contract witness that routed the discrepancy here)"
merge_commit: pending (this leg's PR merge; recorded at the PR)
reviewer_chain:
  - "loop-mode /resolve decorrelated adjudication: out-of-family Codex = OPTION B; transcript advisor = VOTE B (agreement; RESOLVE row at .harness/loop_status.md)"
  - out-of-family `just codex-review` at this leg's PR (to convergence)
  - merge-gate 3-lens (code-touching PR)
supersedes: spec-harness-runtime-v1-115-cleared-2026-08-11.md
---

# Clearance — Spec_Harness_Runtime v1.116 (B-145 GAP-2a escalate carve-out)

**What v1.116 changes.** Two in-place bullet edits — the §14.6 step-4 transient
bullet and the §14.9 step-3 transient bullet:

1. **Call-shape correction.** Both bullets ordered `advance_staircase(policy,
   attempt_count, validator_fail_class)` — an attempt-indexed signature that
   never existed. Corrected to the landed stage-keyed API
   (`harness_cp.validator_fail_transient_staircase.advance_staircase(current,
   cause, attempt)`), consulted STAGE-FRESH (`STAGE_1` per call) as a
   cause-class classifier — the documented as-built reading both shipped
   composers carry.
2. **Escalate clause ratified a DEFENSIVE BRANCH CONTRACT.** `retry.terminal =
   "escalate"` fires iff a composer's transient classifier ever yields a
   transition beyond `STAGE_2`; UNREACHABLE BY CONSTRUCTION at the v1.116
   classifiers, witness-pinned on BOTH composers (dispatch: PR #1306's
   `test_b145_terminal_escalate_branch_contract`; tool: this leg's paired impl
   companion splits the collapsed exhaustion `else` and adds
   `test_b145_tool_terminal_escalate_branch_contract` +
   `test_b145_tool_escalate_is_unreachable_at_current_classifier`).

**Why carve-out, not stage-threading (the rejected alternative, decided not
defaulted).** Threading makes a 2nd consecutive transient hit `(STAGE_2,
TRANSIENT_RETRY) → STAGE_3` = escalate — capping effective attempts at 2 and
dead-lettering the operator-supplied `RetryPolicy.max_attempts` bound these
same sections contract; `CROSS_FAMILY_FALLBACK` is semantically void on the
tool path (no model candidates); stages 3–5 are already realized structurally
on the dispatch path (candidate-chain advance / chain floor / driver terminal
mapping); and C-CP-21 §21.2 is a *validator*-fail staircase that does not bind
these transport-error call sites (the ADR-D3 commitment is "same library API",
which the stage-fresh call satisfies). Making staircase-driven escalation
genuinely reachable is declared a future design arc requiring its own
back-flow. Decorrelated adjudication: codex and advisor independently selected
the carve-out.

**Not a design extension (X-AL-3).** No attribute added/removed/resemanticized;
the five `retry.terminal` values unchanged; C-CP-21 §21.2 untouched (stays
canonical for the validator surface); zero reachable-path behavior change —
the impl companion only splits an existing collapsed branch into its two
constituent cases with identical reachable semantics.

**Not touched here.** The B-150 collector half (C-RT-10 step-3a ordering) and
the B-144 §24.1.B venue fork remain open legs. B-145 itself CLOSES at this
leg (GAP-1 closed at v1.115/#1308; GAP-2b closed at #1306; GAP-2a is this
leg — the last open half).
