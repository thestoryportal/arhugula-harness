# Class 2 Fork — B-65: post-effect signing carrier disposition at CP topology cascade handlers

**Status: FILED (draft) — awaiting out-of-family review + operator selection at §4.** Registered
at the U-RT-136/U-CP-73 impl arc (out-of-family codex round-2 [P1]); the register row's
close_out routes the cascade-disposition question to the CP spec (Class 2 fork or rider
amendment over C-CP-25 §25.10+/§25.15) BEFORE wiring. Filed per the no-parking discipline;
the operator answers §4.

## §1 The defect

Under `audit_signing_fail_closed=ON`, a `PostEffectAuditSigningError` (the result-preserving
carrier: the child's PAID effect COMPLETED; only the post-effect audit signing failed — OD
v1.34 §21.2.3's post-effect result-preserving bypass) raised at a fan-out BRANCH reaches the
CP workflow driver's topology cascade handling as a GENERIC branch failure:

- Under `cascade_policy=pause` it converts to a resumable PAUSED whose resume RE-DISPATCHES
  the same step — RE-FIRING the already-completed paid effect the carrier exists to protect
  (the at-most-once violation).
- Under PROCEED-tier handling it reduces to PARTIAL WITHOUT the carrier's `result_ref` — the
  completed effect's result is dropped from the fold even though the carrier preserved it.

The v1.101 CP rider's catch-ordering contract enumerates the per-attempt classifiers and
forbids TRANSIENT_RETRY / candidate-advance / breaker-failure for the carrier (all closed at
that arc); it does NOT specify branch-vs-workflow terminality under each cascade_policy.

## §2 The prescription shape (from the register close_out)

Once the spec question is decided: wire a name-match fence
(`type(exc).__name__ == "PostEffectAuditSigningError"` — the established
StepDispatchTimeoutError precedent; harness-cp cannot import the runtime type) AHEAD of the
branch-failure → PAUSED/PARTIAL conversions in `workflow_driver.py`, so the condition stays
TERMINAL and RESULT-REFERENCED. Witness: a fan-out run under flag-ON whose branch raises the
carrier asserts (a) no resumable PAUSED snapshot is minted for that branch, (b) the surfaced
failure carries the result_ref, (c) no re-dispatch path can re-fire the effect.

## §3 The spec question (what §25.15 must say)

Proposed rider over C-CP-25 §25.15 (one row): "A branch failing with the post-effect
audit-signing carrier is TERMINAL-with-result for that branch under EVERY cascade_policy —
`pause` MUST NOT mint a resume path that re-dispatches it (the branch enters the terminal
disposition set, mirroring the scoped-abort precedent); `proceed`/`cascade-cancel` folds
carry the carrier's result_ref into the PARTIAL/FAILED report. The run-level status still
follows the policy for the REMAINING branches." Rationale: the carrier is definitionally
"effect landed, audit incomplete" — at-most-once (C-RT effect discipline) dominates
resumability; the audit gap is an operator-repair item (the migrate/inspect surfaces), not a
re-dispatch trigger.

## §4 The operator selection (ONE decision)

- **(A) RECOMMENDED — adopt the §3 rider: carrier is branch-terminal-with-result under every
  cascade_policy; wire the name-match fence + witnesses per §2.**
- (B) policy-split variant: terminal under `pause`/`cascade-cancel` but under `proceed` keep
  the current PARTIAL while ADDING the result_ref to the fold (weaker — still no re-fire, but
  the branch reads degraded rather than terminal-with-result).
- (C) reject — keep current behavior and flip B-65 to a documented-residual queryable record
  (accepts the pause-tier re-fire hazard; NOT recommended: it is a live at-most-once
  violation, not a dormant edge).
