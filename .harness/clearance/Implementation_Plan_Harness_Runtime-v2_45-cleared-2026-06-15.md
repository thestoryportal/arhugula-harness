---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_45.md
version: v2.45
cleared_at: 2026-06-15T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the WAL_SEGMENT (E-2) runtime-homed surfaces, impl-against-cleared-spec; R-FS-1 E-plan; runtime-axis leg)
back_reference:
  - .harness/r-fs-1-e-plan-decomposition.md (the E-plan decomposition summary + coverage matrix + DAG + the §5 R-CXA-2-owned-by-E-2 finding)
  - .harness/architect_recommendation_e_engine_fork_vs_impl.md (E-1/E-2 impl-against-cleared-spec)
  - design-substrate/Spec_Control_Plane_v1_2.md §7.1 row 5 + §7.4 (C-CP-07 WAL-segment substrate, deferred to impl-discretion) + §8.1 `segment_replay` + §8.2 row 5 (C-CP-08); CP §16.5 (C-CP-49/50 composers, cleared+built)
  - .harness/r-fs-1-e-engine-classes-design-v1.md §4/§6 (WAL_SEGMENT design; the line-181-respecting #475 extension; the built-but-unwired recovery-loop producer gap)
  - design-substrate/Implementation_Plan_Control_Plane_v2_34.md (co-published sibling — U-CP-93/94/95; the E aggregate DAG home at §3.5)
  - design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md (the delta base — preserved verbatim per delta-only-plan-chain)
  - .harness/adversarial-review-r-fs-1-e-plan.md (the pre-merge adversarial review report)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (main-agent, grounded at HEAD d7102a6) — produced the 2 NEW runtime units (U-RT-121 hand-rolled WAL segment-log `EnginePauseResumeSubstrate` extending #475; U-RT-122 R-CXA-2 engine-layer activation — durable factory bind + go-live e2e) + §3.1b DAG delta + §4.1b coverage; coverage-complete; acyclic; delta-only-preservation verified (U-RT-115..120 bodies byte-identical).
  - advisor() pre-substantive + the gating empirical probe — confirmed the durable-substrate (U-RT-121) and the R-CXA-2 activation (U-RT-122) are the separable Unit-B halves; the U-RT-122 go-live AC is by-execution (cp.pause-captured/cp.resume-attempted land against the DURABLE substrate, not "bound"); R-CXA-2 owns at E-2 (the probe resolved the recovery-loop snapshot surface composes with WAL_SEGMENT's append-then-resume, not EVENT_SOURCED's pure event-replay).
  - harness-adversarial-reviewer Phase-6 pre-merge review (dedicated agent, 37 tool-uses; full report .harness/adversarial-review-r-fs-1-e-plan.md) — VERDICT **APPROVE-WITH-CHANGES** (0 blocking / 1 substantive / 2 doc-hygiene; all findings on the CP sibling + companion, applied). Runtime-side: U-RT-121/122 verified — the U-RT-122 go-live AC is by-execution against the durable substrate (not "bound"); no CP→RT import; delta-only U-RT-01..120 byte-preserved. No runtime-specific finding.
  - out-of-family Codex review (`just codex-review`) — 1 [P2] applied at the CP sibling (the `test_u_rt_95` un-skip false-green; see the CP v2.34 marker). No runtime-side finding; the U-RT-122 go-live AC was already by-execution against the durable substrate.
supersedes: design-substrate/Implementation_Plan_Harness_Runtime_v2_44.md
superseded_by:
---

# Clearance — `Implementation Plan: Harness Runtime v2.45`

v2.45 is the **runtime-axis leg of R-FS-1 — E-plan** — the atomic-unit decomposition of the WAL_SEGMENT (E-2) runtime-homed surfaces, **impl-against-cleared-spec** (C-CP-07 §7.4 defers "specific WAL implementation" to impl-discretion; I-6 selects hand-rolled; firing the already-cleared C-CP-49/50 composers from a real driver is impl). **2 NEW runtime units:**

- **U-RT-121** — hand-rolled WAL segment-log `EnginePauseResumeSubstrate`, extending the proven #475 `JournalEnginePauseResumeSubstrate` (append-only segment writer + per-segment replay + idempotent consumer state + torn-write detection + fsync). Implements the existing Protocol; PathClass `STATE_LEDGER` (existing closed member; F-E-IS sub-fork only if no honest mapping).
- **U-RT-122** — R-CXA-2 engine-layer activation: bind U-RT-121 in `r_cxa_2_producer_loop_factory.py:208-214` (replace `DeterministicEnginePauseResumeSubstrate`), giving `RuntimeEngineRecoveryLoop` its **first production driver** → `cp.pause-captured`/`cp.resume-attempted` (C-CP-49/50) land → **R-CXA-2 CP→IS engine-layer seam goes LIVE** (a ratified bounded-residual; line-181 trigger fired). AC = by-execution e2e against the DURABLE substrate (foreclosing the cosmetic-Journal-swap anti-pattern). **This go-live e2e IS the Path-(i) `test_u_rt_95` materialization** (relocated here from U-CP-94 per the Codex 2nd-pass DAG/AC catch — it needs the durable substrate + the U-CP-95 firing, which the `(none)` U-CP-94 cannot depend on): author the vacuous `:368-375` body into the real cycle + un-skip `:347` + flip the Path-(i) fork CLOSED-DEFERRED → CLOSED-BUILT.

§3.1b is the runtime DAG delta (the E aggregate cross-axis home is CP plan v2.34 §3.5); the single cross-axis edge U-RT-122 → U-CP-95 (RT→CP downstream). **ZERO spec amendment; X-AL-3-clean.** Delta-only (U-RT-01..120 preserved verbatim). Co-published with CP plan v2.34.

## Notes
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- R-CXA-2 activation homes at E-2 (WAL_SEGMENT), NOT E-1 (CP plan v2.34 §6 O-CP-4 / companion §5).
- See `.harness/clearance/README.md` for marker discipline.
