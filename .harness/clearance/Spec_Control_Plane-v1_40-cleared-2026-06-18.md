---
artifact: design-substrate/Spec_Control_Plane_v1_40.md
version: v1.40
cleared_at: 2026-06-18T00:00:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc (NO operator gate — impl-to-cleared-spec on the §6.6 provenance contract + a stale-note refresh; no committed-invariant sacrifice)
back_reference:
  - .harness/class_1_fork_b_nonlinear_override_provenance.md
  - .harness/beyond-mvp-capability-boundary-ledger.md (B-NONLINEAR-OVERRIDE-PROVENANCE spine registration)
  - design-substrate/Spec_Control_Plane_v1_38.md (the §6.6 provenance contract + the superseded honest-scope note)
merge_commit: <pending — co-published bundled-absorption PR>
reviewer_chain:
  - advisor (pre-substantive, full-transcript) — recommended Design A (buffered-branch path) over driver-thread direct emission (thread-model-agnostic correctness inherited from the buffer→drain discipline); flagged the idempotency-key identity decision + the §6.6 stale-note disposition + the repeated-step_id test obligation
  - standing FULL-SPEC operator directive 2026-06-12 (design back-flow pre-authorized; no operator gate owed — nothing committed is sacrificed)
  - out-of-family Codex review at the impl-diff PR (decorrelated; pending)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane v1.40`

v1.40 is a prose-refresh delta over v1.39 absorbing the **R-FS-1 standalone arc `B-NONLINEAR-OVERRIDE-PROVENANCE`**. It refreshes the **C-CP-06 §6.6 topology-scope note** (authored at v1.38, preserved through v1.39): the per-step override-ledger entry (`cp.per-step-override-application`) now fires on **all six** topology patterns — `SINGLE_THREADED_LINEAR` inline on the driver thread, the 5 non-linear strategies **through the buffered-branch path** (`append_branch_override_ledger_entry` → `BufferingLedgerWriter` → `drain_branch_buffers`, realizing the ADR-F2 v1.2 single-threaded-write boundary). The v1.38 honest-scope note that registered "the non-linear topologies do not emit a per-step override-ledger entry" as a forward item is superseded.

**NO operator gate.** Unlike the v1.38 §14.5.3-relaxation gate, this closure **sacrifices no committed invariant**: it fulfills the existing §6.6 provenance contract (paragraph 1 — general, never "linear only"), reuses the **§16.5.4 idempotency-key formula VERBATIM** (per-`(step, outcome)`, not branch-scoped — branch-scoping would be the X-AL-3 change, foreclosed), and is additive (an absent override → byte-identical pre-arc behavior). Refreshing the now-falsified present-tense disclosure is the `[[stale-carry-text-disposition]]` discipline. FULL-SPEC pre-authorized the build + back-flow.

Reviewed during clearance: Design A (buffered-branch) over Design B (driver-thread direct) — A inherits single-threaded-write correctness from the buffer→drain discipline regardless of which thread a branch runs on, whereas B would require per-site proof the emission is on the single write thread outside the drain capture-window (advisor-decisive); the per-`(step, outcome)` idempotency identity (an override is a static binding property → repeated `(step, outcome)` dedups to one entry, the §16.5.4 designed semantic — verified by the EVALUATOR_OPTIMIZER repeated-step test asserting exactly one entry); byte-shape-identical persisted entry across topologies (both paths compose via the factored-out `compose_override_entry_payload`); no §5.2 hash-recipe / §16.5.4 key change; no new CXA edge (rides the landed §16.5 CP→IS composer seam).

## Notes

- Phase 7 consumers may rely on this version as canonical after the bundled harness-cp impl + tests land together (`merge_commit` pinned at the post-merge refresh).
- See `.harness/clearance/README.md` for marker discipline.
