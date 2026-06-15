---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_35.md
version: v2.35
cleared_at: 2026-06-15T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of E-3 RECONCILER_LOOP — impl-against-cleared-spec post-CP-spec-v1_33; R-FS-1 E-plan-3; CP-axis leg)
back_reference:
  - .harness/r-fs-1-e3-plan-decomposition.md (the E-plan-3 decomposition summary + coverage matrix + DAG + findings O-E3-1/2/3)
  - design-substrate/Spec_Control_Plane_v1_33.md (E-spec-3 — the §7.4 reconciler-loop substrate-deferral that makes E-3 materialization impl-against-cleared-spec; operator-ratified 2026-06-15, PR #568)
  - .harness/architect_recommendation_e_engine_fork_vs_impl.md (E-3 = the one narrow §7.4 fork, now resolved at E-spec-3)
  - .harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md (RATIFIED-AND-APPLIED — the substrate decision)
  - design-substrate/Spec_Control_Plane_v1_2.md §7.1 row 4 / §7.4 (C-CP-07) + §8.1 reconciler_converge / §8.2 row 4 (C-CP-08) — the cleared engine-class taxonomy + resumption semantics this plan decomposes
  - design-substrate/Implementation_Plan_Control_Plane_v2_34.md (the delta base — preserved verbatim per delta-only-plan-chain; 0 prior unit-body lines changed)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (dedicated agent adopting the SKILL, 100 tool-uses, grounded at HEAD ac553b02) — produced the decomposition: 2 NEW CP units (U-CP-96 RECONCILER_LOOP engine materialization [level-triggered read/diff/converge resumption, CP/IS-only]; U-CP-97 RECONCILER_LOOP engine-layer recovery-loop firing branch → C-CP-49/50) + 2 RT units (runtime plan v2.46) + the E-3 aggregate cross-axis DAG (§3.6) + coverage matrix (§4.4) + findings O-CP-5(1/2/3). Mechanism (A) materialization / (B) recovery-loop-firing kept distinct (anti-fold). advisor() consulted pre-authoring — confirmed the 4-unit shape, resolved O-E3-1 substrate-coexistence as RT-internal impl-discretion (NAME-not-design), and sharpened the do-not-copy-WAL-prose semantics (reconciler_converge NOT segment_replay; CRD_RECONCILER_LEDGER NOT HARNESS_OVERLAY_LEDGER; CAS-lease as the genuine new capability; engine-owns-substrate per f2_substrate_join_discipline.py:9-12; NEW non-live e2e NOT a test_u_rt_95 reuse).
  - harness-adversarial-reviewer Phase-7 pre-merge review (dedicated agent adopting the SKILL, 29 tool-uses, 13 substantive attacks) — **CLEAR — 0 Class-3 / 0 Class-2 / 2 Class-1** (minor cite line-number offsets only, accepted-minor: cites resolve to the correct construct, impl re-grounds at E-impl-3). Verified BYTE-EXACT (the clearance basis): (1) X-AL-3-clean — RECONCILER_LOOP / RECONCILER_CONVERGE / CRD_RECONCILER_LEDGER all already-closed enum members consumed not minted (engine_class.py:46 / resumption_kind.py:65 / f2_substrate_join_discipline.py:85); `_IN_SCOPE` widening = the cleared U-CP-56/U-CP-94 "no spec bump" move; (2) consumers ALREADY enumerate RECONCILER_LOOP at HEAD (per_engine_class_topology_overlay / workload_binding_engine_class_selection / t_perm_3_composition.py:165) → consumer-wiring is AC-level VERIFICATION not new code; (3) test_u_rt_95 is WAL-only + explicitly excludes reconciler → U-RT-124's NEW non-live e2e correctly scoped; (4) spec-prose-vs-plan-body: every §7.4/§8.1/§8.2/§8.3 fragment byte-exact; (5) deferrals honest — O-E3-2 deployment-admissibility + O-E3-3 live-K8s carried as explicit AC-level open-questions, engine_class_candidate.py NOT edited; (6) O-E3-1 substrate-selection clean RT-internal impl-discretion (no contract/enum/Protocol widening); (7) DAG acyclic, single RT→CP cross-axis edge, no CP→RT import/cycle; (8) (A)/(B) NOT folded; (9) delta-only preservation honest (0 prior unit-body lines changed, full-file diff); (10) is_replay §8.3 sibling-consistency CARRIED (the E-plan-1/2 review's F3-02 fix propagated to U-CP-96, NOT a phantom).
  - out-of-family Codex review (just codex-review-uncommitted, $0 ChatGPT subscription, decorrelated) — 1 actionable [P2] + 1 [P3], both addressed: [P2] co-publish the plan-head pointers + clearance markers (the plan footers declare them) → THIS marker + the runtime v2.46 marker + root CLAUDE.md §2.4 + claude-artifact-pointers §2.4 bumps are co-published in this PR (resolving the finding); [P3] 3 untracked leftover files (sdlc-research + 2 B3 adversarial reviews) are prior-session artifacts NOT staged → excluded from this PR. Codex did NOT challenge the decomposition substance.
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_34.md
superseded_by:
---

# Clearance — `Implementation Plan: Control Plane v2.35`

v2.35 is the **CP-axis leg of R-FS-1 — E-plan-3** — the atomic-unit decomposition of the E sub-program's **LAST** engine class (**E-3 RECONCILER_LOOP**), now **impl-against-cleared-spec** after PR #568 landed CP spec v1_33 (the E-spec-3 §7.4 reconciler-loop substrate-deferral, operator-ratified — hand-rolled etcd-style per I-6 as the spec-blessed candidate). **2 NEW CP units:**

- **U-CP-96** — RECONCILER_LOOP engine materialization (level-triggered read/diff/converge resumption; CP/IS-only): `_IN_SCOPE_ENGINE_CLASSES` += RECONCILER_LOOP + a `reconciler-converge` driver dispatch branch + `resumption.kind=reconciler_converge` (C-CP-08 §8.1) + the F2 `CRD_RECONCILER_LEDGER` read (§8.2 row 4) + 4 F3-floor ACs (incl. the **CAS lease** — the genuine new capability over WAL) + consumer-VERIFICATION (the consumers already enumerate RECONCILER_LOOP) + the SINGLE_THREADED_LINEAR byte-unchanged guard. Does NOT fire the recovery loop.
- **U-CP-97** — RECONCILER_LOOP engine-layer recovery-loop firing branch (`ctx.engine_recovery_loop` → C-CP-49/50, duck-typed, no CP→RT import) → the R-CXA-2 CP→IS engine-layer seam goes live for the reconciler path. Depends on U-CP-96.

Semantically distinct from WAL_SEGMENT (NOT prefix-replay): reconciler-loop is a level-triggered control loop, engine-owns-substrate (`f2_substrate_join_discipline.py:9-12`), with a compare-and-swap lease. ZERO spec amendment, ZERO new contract ID, X-AL-3-clean (consumes the closed `EngineClass`/`ResumptionKind`/`F2JoinKind` enums). All prior units (U-CP-00..95) byte-identical; v2.34 untouched.

**Caveat for E-impl-3 consumers.** Three within-impl dispositions carried as open-questions (NOT resolved here): **O-E3-1** the engine-class-aware substrate-selection mechanism (RT-internal impl-discretion, NAMED-not-designed); **O-E3-2** the §7.2/ADR-D1 §1.2 deployment-admissibility of the hand-rolled reconciler (`engine_class_candidate.py:69-71` K8s exclusion now stale, but deferred to E-impl-3 per v1_33 §7.4 — §7.2 stands verbatim, the plan does NOT edit it); **O-E3-3** the live-K8s e2e (a separate downstream deployment-surface gate; U-RT-124's buildable AC is a NEW non-live in-memory/filesystem reconciler e2e). With E-impl-3, all 5 engine classes are materialized and the E sub-program closes.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
