---
artifact: design-substrate/Spec_Control_Plane_v1_109.md
version: v1.109
cleared_at: 2026-07-26T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-merge-gate-finding
back_reference:
  - .harness/forward-register.yaml (B-78 row, closed; B-79 row, scope broadened)
  - PR #1117
merge_commit: <filled at merge>
reviewer_chain:
  - out-of-family just codex-review main, 5 rounds to convergence
  - merge-gate 3-lens review (concurrency: APPROVE; test-witness: APPROVE; spec-conformance: BLOCK -> this delta)
supersedes: design-substrate/Spec_Control_Plane_v1_108.md
superseded_by:
---

# Clearance — `Spec_Control_Plane_v1_109`

This delta corrects a stale-carry-text defect the `merge-gate` skill's spec-conformance lens caught while reviewing PR #1117 (the `B-78` impl leg). CP spec v1.108 §1.2's closing paragraph asserted the `EVALUATOR_OPTIMIZER`/`DECENTRALIZED_HANDOFF` gap was "ungrounded... not yet even reproduced" and named it "forward work for a future arc" — while the PR under review WAS that future arc, already landed with a real reproduction (real-stack integration tests against `harness-runtime`) and fix.

The underlying fix required no CP-spec carrier amendment: `EvaluatorOptimizerResumeState`/`HandoffResumeState` have no branch-ordinal ambiguity (unlike the fan-out topologies property 6's new field was built for), so mirroring the already-cleared LINEAR delivery-cell mechanism at these two topologies' own resumed-step dispatch sites was plain Phase-7 impl work. This delta records that closure in the canonical spec text — no contract, carrier, method-signature, or enum change; property 6's text (§1.1/§1.2b/§1.3/§1.3a) is otherwise PRESERVED VERBATIM.

A residual finding from the same review round (an unanswered `HITL_PENDING` resume proceeding to dispatch rather than staying inert) was NOT introduced by this fix — confirmed via direct grep to be the identical pre-existing shape already present at the already-shipped LINEAR `resume_at` site — and is tracked at `.harness/forward-register.yaml`'s `B-79` row (scope broadened, not a new row) rather than fixed as part of this closure.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
