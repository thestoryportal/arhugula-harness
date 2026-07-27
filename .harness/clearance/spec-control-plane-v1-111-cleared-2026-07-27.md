---
artifact: design-substrate/Spec_Control_Plane_v1_111.md
version: v1.111
cleared_at: 2026-07-27T00:00:00-07:00
clearance_type: Phase-7-absorbed-via-advisor-directed-reread
back_reference:
  - .harness/forward-register.yaml (B-79 row, unchanged; B-80 row, unchanged)
  - PR #1130 (filled at merge)
merge_commit: <filled at merge>
reviewer_chain:
  - advisor() consulted before opening the B-79/B-80 impl leg; recommended a fresh full re-read of the just-merged v1.110 body against 3 specific consistency risks
  - out-of-family just codex-review-uncommitted (to run before merge)
supersedes: design-substrate/Spec_Control_Plane_v1_110.md
superseded_by:
---

# Clearance — `Spec_Control_Plane_v1_111`

This delta is a prose-only miscount correction, self-caught during a fresh full re-read of `Spec_Control_Plane_v1_110.md` performed at `advisor()`'s explicit direction before the next `roadmap-continue` iteration opened the B-79/B-80 impl leg. `advisor()` flagged that PR #1129's 6-round out-of-family review had converged on individual claim-correctness at each round but had never been checked as a single coherent document read fresh end-to-end, and named three specific consistency risks to verify before building against the merged spec.

Of the three: (1) §1.1(d)'s sentence "ALL FOUR of LINEAR/EO/DH carry NO per-step HITL-configuration identity check of any kind today" names only three sites (LINEAR, `EVALUATOR_OPTIMIZER`, `DECENTRALIZED_HANDOFF`) while asserting "FOUR" — confirmed a genuine miscount (the very next sentence in the same paragraph already correctly says "all three"), fixed by this delta; (2) the Revision-shape line's placement of a codex-correction narrative — checked against the `v1.106` delta's own precedent, which already places correction narrative in its Revision-shape line, so this is NOT a deviation from convention; (3) a possible reader confusion between `PreDispatchGateOwningBranchResumeState` (bound by property 7) and `PausedChildBranchResumeState` (explicitly excluded) — checked against the surrounding text, which names both carriers precisely and gives the reasoning for the exclusion, so this is NOT an actual contradiction.

Only finding (1) required a fix. No contract, carrier, method-signature, or enum change results — properties 7 and 8's text is otherwise PRESERVED VERBATIM; the property still binds the same 4 total sites (fan-out `PreDispatchGateOwningBranchResumeState` consult site + 3 sequential sites), and the §1.3a carrier-reuse authorization for the 3 sequential sites is unchanged.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The B-79/B-80 impl leg (deferred, per the `Implementation_Plan_Control_Plane_v2_46.md` coverage-matrix rows) should read against this version, not v1.110, once opened.
