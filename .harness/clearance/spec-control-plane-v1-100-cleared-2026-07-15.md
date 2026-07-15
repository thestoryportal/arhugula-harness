---
artifact: design-substrate/Spec_Control_Plane_v1_100.md
version: v1.100
cleared_at: 2026-07-15T06:30:00-06:00
clearance_type: Phase-7-absorbed-via-retirement-event
back_reference:
  - .harness/forward-register.yaml (B-32, B-39)
  - .harness/post-phase-8-forward-register.md (B-32, B-39)
  - PR #1015
merge_commit: <filled at merge>
reviewer_chain:
  - out-of-family Codex (just codex-review-uncommitted), 3 rounds
  - merge-gate 3-lens review (concurrency: APPROVE; spec-conformance: BLOCK -> this delta; test-witness: BLOCK -> second-site tests added)
  - advisor() at the false-affordance decision fork
  - impl-time grounding pass (direct grep confirming pause_reason has exactly one non-telemetry reader and the composer never branches on it)
supersedes:
superseded_by:
---

# Clearance — `Spec_Control_Plane_v1_100`

This delta corrects a stale-carry-text defect in v1.97's Change-note (v1.96→v1.97) registered-forward-work paragraph (unheaded prose, not a numbered section — near the B-21 arc's own §25.15.1/§26.2 discussion). That note asserted gaps (b) [per-child HITL response routing] and (c) [nested pause_reason propagation] were "coupled ... travel together as one forward arc" and that propagating (c) alone would be a "false affordance." The `B-32` arc closed (c) independently — a merge-gate spec-conformance reviewer correctly flagged that the PR shipping (c) alone contradicted that paragraph's own canonical text without a matching spec delta, citing the `B-31`/v1.99 precedent (which closed a different registered gap from the same v1.97 Change-note with its own delta) as the established discipline for this exact situation.

The underlying safety question was resolved by direct code grounding, not by re-opening a design decision: `pause_reason` has exactly one non-telemetry reader in `harness_cp` (the `_pause_reason` derivation itself), and the composer's resume path (`ResumeContextHolder.consume_and_clear`) never branches on `pause_reason` — nothing auto-dispatches a response off the label. This delta records that grounding and revises that paragraph's framing from "coupled" to "sequential" — (c) is the honest, weaker half that closes without (b); (b) remains open at `B-39` with 3 concrete design constraints from a reverted first attempt.

No contract, carrier, exception, or cross-axis surface changed. This is a prose-only correction to a change-note's registered-forward-work text, not an amendment to any numbered `C-CP-NN` contract clause.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
