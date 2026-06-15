---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_46.md
version: v2.46
cleared_at: 2026-06-15T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of E-3 RECONCILER_LOOP runtime-homed surfaces — impl-against-cleared-spec post-CP-spec-v1_33; R-FS-1 E-plan-3; runtime-axis leg)
back_reference:
  - .harness/r-fs-1-e3-plan-decomposition.md (the E-plan-3 decomposition summary + coverage matrix + DAG + findings O-RT-4/5/6)
  - design-substrate/Spec_Control_Plane_v1_33.md (E-spec-3 — the §7.4 reconciler-loop substrate-deferral; hand-rolled etcd-style per I-6 the spec-blessed candidate)
  - .harness/architect_recommendation_e_engine_fork_vs_impl.md + .harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md (RATIFIED-AND-APPLIED)
  - design-substrate/Spec_Control_Plane_v1_2.md §7.1 row 4 / §7.4 floor (i)-(iv) (C-CP-07) — the cleared lifecycle/floor (CAS lease) this runtime substrate realizes hand-rolled
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_45.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (dedicated agent adopting the SKILL, 100 tool-uses, grounded at HEAD ac553b02) — produced 2 NEW RT units (U-RT-123 hand-rolled etcd-style reconciliation `EnginePauseResumeSubstrate` [CAS lease over own-format durable store, parallel to U-RT-121 per I-6]; U-RT-124 R-CXA-2 engine-layer activation [engine-class-aware factory bind + NEW non-live durable reconciler e2e]) + §3.1c DAG delta + §4.1c coverage + findings O-RT-4/5/6. The substrate parallels the landed U-RT-121 WAL substrate (`wal_segment_pause_resume_substrate.py`) implementing the cleared `EnginePauseResumeSubstrate`/`ResumableEngineSubstrate` Protocol — no Protocol widening.
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent, 29 tool-uses, 13 attacks) — **CLEAR — 0 Class-3 / 0 Class-2 / 2 Class-1** (minor cite line-offsets, accepted-minor — resolve to the correct construct, impl re-grounds). Runtime-specific byte-exact verifications: U-RT-123 implements the cleared Protocol exactly as U-RT-121 (no enum/contract/Protocol widening); U-RT-124's go-live e2e is a NEW non-live (in-memory/filesystem) reconciler e2e (test_u_rt_95 is WAL-only, explicitly excludes reconciler); O-RT-4 substrate-selection is engine-class-aware RT-internal impl-discretion (engine_recovery_loop is engine-class-agnostic; factory binds one substrate — making it class-aware touches only harness_runtime internals); O-RT-5 deployment-admissibility + O-RT-6 live-K8s = honest AC-level deferrals to E-impl-3; runtime preservation honest (0 prior unit-body/open-item lines changed, full-file diff); the single cross-axis edge U-RT-124→U-CP-97 runs RT→CP (downstream package direction), no cycle. See the CP v2.35 clearance marker for the shared decomposition-soundness verifications.
  - out-of-family Codex review (just codex-review-uncommitted, $0 subscription, decorrelated) — [P2] co-publish pointer bumps + clearance markers → resolved (this marker + the CP v2.35 marker + the §2.4 pointer bumps co-published in this PR); [P3] untracked leftover files excluded. No challenge to the substance.
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_45.md
superseded_by:
---

# Clearance — `Implementation Plan: Harness Runtime v2.46`

v2.46 is the **runtime-axis leg of R-FS-1 — E-plan-3** — the atomic-unit decomposition of the runtime-homed surfaces of E-3 RECONCILER_LOOP (the E sub-program's last engine class), now impl-against-cleared-spec post-CP-spec-v1_33. **2 NEW RT units:**

- **U-RT-123** — Hand-rolled etcd-style reconciliation `EnginePauseResumeSubstrate` (per I-6, NO vendored K8s): a level-triggered read/diff/converge reconcile loop with a **compare-and-swap (CAS) lease** over an own-format durable store, joined to the F2 state-ledger on `idempotency_key` (v1_33 §7.4 reconciliation note). Parallel to the landed U-RT-121 WAL substrate; implements the cleared `EnginePauseResumeSubstrate`/`ResumableEngineSubstrate` Protocol (no Protocol widening). Leaf.
- **U-RT-124** — R-CXA-2 engine-layer activation (RECONCILER_LOOP): make the recovery-loop factory binding **engine-class-aware** (so a RECONCILER_LOOP workflow fires against U-RT-123 while WAL_SEGMENT keeps firing against U-RT-121 — no cross-contamination) + a NEW non-live (in-memory/filesystem) durable reconciler e2e proving the engine-layer seam fires. Depends on [U-RT-123, U-CP-97 (cross-axis: CP)].

ZERO spec amendment, ZERO new contract ID, X-AL-3-clean. All prior units (U-RT-01..122) byte-identical; v2.45 untouched.

**Caveat for E-impl-3 consumers.** The **live-K8s e2e is a separate downstream deployment-surface gate** (O-RT-6), NOT built by U-RT-124 — U-RT-124's buildable AC is the non-live proof; the live proof is a distinct operator/infra gate. The §7.2/ADR-D1 §1.2 deployment-admissibility (O-RT-5) and the engine-class-aware substrate-selection mechanism (O-RT-4, RT-internal impl-discretion) are carried as open-questions resolved at E-impl-3.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
