---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md
version: v2.44
cleared_at: 2026-06-14T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the cleared B3 spec legs + design impl-against-cleared-spec gaps; R-FS-1 arc #20 / B3-plan; runtime-axis leg)
back_reference:
  - .harness/r-fs-1-b3-plan-decomposition.md (the B3-plan decomposition summary + coverage matrix + DAG + homing rationale)
  - design-substrate/Spec_Harness_Runtime_v1.md §3.8 (B3-spec-1, cleared v1.49) + §14.8.9 (B3-spec-2, cleared v1.50) — the cleared specs this plan decomposes
  - .harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md (F-B3-1) + .harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md (F-B3-2)
  - .harness/r-fs-1-b3-smart-hitl-design-v1.md §3.2/§4.1/§5/§6.1/§8.2/§8.3 (the gap-set + sequence authority); cleared #549
  - design-substrate/Implementation_Plan_Control_Plane_v2_33.md (the co-published CP leg — the aggregate-graph home; U-CP-91/92 the cross-axis dependencies of U-RT-116/119)
  - .harness/adversarial-review-r-fs-1-b3-plan.md (the filed pre-merge adversarial review report)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md (the delta base — preserved verbatim per delta-only-plan-chain)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner (genuine dedicated-agent invocation, 67 tool-uses) — the runtime-leg decomposition: 6 NEW units U-RT-115..120 (the smart-HITL gate-site logic, **runtime-homed** because `RuntimeHITLGateComposer` lives in `harness-runtime/.../hitl_gate_composer.py`, verified at HEAD): U-RT-115 `resolve_step_blast_radius` (G1-blast) / U-RT-116 `HITLAutoApprovePolicy` stage-5 + in-`max()` floor-override (G1-skip, §3.8) / U-RT-117 gate_level-once + palette-thread (G2) / U-RT-118 `degradation_mode_applied` attr (G4a) / U-RT-119 timeout dispatch-on-mode (§14.8.9, G4b) / U-RT-120 EDIT replace-not-merge (G3).
  - main-agent integrity verification (direct read): all 6 new units present; prior U-RT-01..114 preserved verbatim (v2.44 314 lines vs v2.43 158); no impossible-path framing leaked into U-RT-116 (the GateLevelInput carrier-shape is delegated to U-CP-91).
  - harness-adversarial-reviewer Phase-6 pre-merge review (dedicated-agent, 34 tool-uses) — VERDICT **APPROVE-WITH-CLASS-3** (shared report `.harness/adversarial-review-r-fs-1-b3-plan.md`); all 9 claims verified; the homing decision (gate-site units runtime-homed) confirmed by direct read of the composer's package; the carried ACs (F-B3-1 audit-not-vacuous + EXTERNAL_REVERSIBLE-not-representable → U-RT-116; F-B3-2 dispatch-not-vacuous per-mode e2e → U-RT-119) verified to preserve "by execution, not green-unit-test."
  - out-of-family Codex review (`just codex-review-uncommitted`) — 3 [P2] ALL applied (the impossible-GateLevelInput-path was in the CP-leg U-CP-91, fixed there; the clearance-markers + pointer-bumps fixed across both legs). Decorrelation payoff recorded at the CP v2.33 marker.
  - advisor() — the planner's pre-done check (DAG/coverage/homing sound).
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md
superseded_by:
---

# Clearance — `Implementation Plan: Harness Runtime v2.44`

v2.44 is the **runtime-axis leg of R-FS-1 arc #20 (B3-plan)** — 6 NEW units (U-RT-115..120) decomposing the smart-HITL gate-site logic that the cleared B3 specs mandate. **Runtime-homed** because the `RuntimeHITLGateComposer` (the gate composer) lives in `harness-runtime`, so the blast resolver, the `HITLAutoApprovePolicy` in-`max()` consumption, the gate_level-once-thread, the timeout dispatch-on-mode, and the EDIT replace-not-merge are runtime units; the CP package (v2.33) carries only the `GateLevelInput` carrier-shape (U-CP-91) + the `TimeoutDegradationKind` vocab reconciliation (U-CP-92); the AS package owes the G2c producer (registered O-CP-3 at CP v2.33 §6).

**ZERO spec amendment** (the B3 specs are canonical at runtime v1.50); **ZERO new contract ID**; delta-only (U-RT-01..114 preserved verbatim). Co-published with CP plan v2.33 (the aggregate-graph home).

## Notes
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- B3-impl sequence (design §8.3): B3-impl-1 (U-RT-115/116/117 + U-CP-91 — coupled; G2 inert-but-harmless without G2c/O-CP-3) → B3-impl-2 (U-RT-118/119 + U-CP-92) → B3-impl-3 (U-RT-120).
- See `.harness/clearance/README.md` for marker discipline.
