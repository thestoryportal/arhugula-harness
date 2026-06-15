---
artifact: design-substrate/Implementation_Plan_Control_Plane_v2_34.md
version: v2.34
cleared_at: 2026-06-15T00:00:00-06:00
clearance_type: Phase-6-plan-amendment (atomic-unit decomposition of the impl-against-cleared-spec engine classes E-1 EVENT_SOURCED_REPLAY + E-2 WAL_SEGMENT; R-FS-1 E-plan; CP-axis leg)
back_reference:
  - .harness/r-fs-1-e-plan-decomposition.md (the E-plan decomposition summary + coverage matrix + DAG + the §5 R-CXA-2-owned-by-E-2 finding)
  - .harness/architect_recommendation_e_engine_fork_vs_impl.md (authoritative on fork-vs-impl — E-1/E-2 = impl-against-cleared-spec, NO spec leg; only E-3 = narrow §7.4 fork)
  - design-substrate/Spec_Control_Plane_v1_2.md §7.1/§7.4 (C-CP-07) + §8.1/§8.2/§8.3 (C-CP-08) — the cleared engine-class taxonomy + resumption semantics this plan decomposes (preserved verbatim through the CP delta chain to head)
  - .harness/r-fs-1-e-engine-classes-design-v1.md §2-§6 (the E design — engine semantics, hand-roll-per-I-6, slice sequence, anti-pattern foreclosures)
  - design-substrate/Implementation_Plan_Control_Plane_v2_33.md (the delta base — preserved verbatim per delta-only-plan-chain)
  - .harness/adversarial-review-r-fs-1-e-plan.md (the pre-merge adversarial review report)
  - PR (pending — this arc)
merge_commit: (pending)
reviewer_chain:
  - implementation-planner discipline (main-agent, grounded at HEAD d7102a6) — produced the decomposition: 3 NEW CP units (U-CP-93 EVENT_SOURCED_REPLAY; U-CP-94 WAL_SEGMENT resumption + test_u_rt_95 un-skip; U-CP-95 WAL_SEGMENT recovery-loop firing branch) + the E aggregate cross-axis DAG (§3.5) + coverage matrix (§4.3) + the O-CP-4 R-CXA-2-owned-by-E-2 finding; coverage-matrix-complete; acyclic; delta-only-preservation verified (U-CP-01..92 headers byte-identical).
  - advisor() pre-substantive + the gating empirical probe — advisor (transcript-aware) confirmed the track + flagged the load-bearing decomposition rule (keep "materialize resumption semantics" Unit A and "fire the recovery loop → C-CP-49/50 → R-CXA-2" Unit B SEPARATE — the U-CP-56 precedent materialized save-point resumption WITHOUT firing the loop), the determinism contract carry (now plan-owned since E-spec-1 dropped), and "check which class owns R-CXA-2 — may not be E-1". The gating probe (direct read of workflow_driver.py:1200/1351/1445/1493 + engine_recovery_loop.py + test_u_rt_95:129-131) RESOLVED it: R-CXA-2 owns at E-2 (WAL_SEGMENT, the DURABLE_ASYNC pause-trigger class), NOT E-1 (pure event-replay has no snapshot-pause boundary) → O-CP-4.
  - harness-adversarial-reviewer Phase-6 pre-merge review — (pending this PR's review pass; report at .harness/adversarial-review-r-fs-1-e-plan.md)
  - out-of-family Codex review (`just codex-review`) — (pending this PR's review pass)
supersedes: design-substrate/Implementation_Plan_Control_Plane_v2_33.md
superseded_by:
---

# Clearance — `Implementation Plan: Control Plane v2.34`

v2.34 is the **CP-axis leg of R-FS-1 — E-plan** — the atomic-unit decomposition of the two **impl-against-cleared-spec** engine classes (E-1 EVENT_SOURCED_REPLAY + E-2 WAL_SEGMENT) per the architect recommendation (`.harness/architect_recommendation_e_engine_fork_vs_impl.md`: C-CP-07 §7.4 defers their substrate to impl-discretion; the U-CP-56 precedent materialized save-point-checkpoint as impl, "no spec bump required"; only E-3 RECONCILER_LOOP carries a narrow §7.4 fork, OUT of this plan). **3 NEW CP units + 1 open-item:**

- **U-CP-93** — EVENT_SOURCED_REPLAY engine materialization (deterministic event-history replay): `_IN_SCOPE_ENGINE_CLASSES` widening + `:1445` dispatch fork + `resumption.kind=engine_replay` + F2 join + the **determinism contract AC** (replayed activity does NOT re-fire — plan-owned now E-spec-1 is dropped) + 4 F3-floor ACs + consumer updates. Does NOT fire the recovery loop; does NOT un-skip `test_u_rt_95` (not a DURABLE_ASYNC cell).
- **U-CP-94** — WAL_SEGMENT engine materialization (segment replay + per-segment dedup) + **Path-(i) `test_u_rt_95` un-skip** (WAL_SEGMENT = canonical DURABLE_ASYNC class). Resumption-semantics half (Unit A).
- **U-CP-95** — WAL_SEGMENT engine-layer recovery-loop firing branch (fire `ctx.engine_recovery_loop` → C-CP-49/50 → R-CXA-2 go-live). The Unit-B CP-half; kept separate from U-CP-94 per the advisor decomposition (avoid the built-but-vacuous trap). Consumes `ctx.engine_recovery_loop` duck-typed (no CP→runtime import).
- **O-CP-4** (open-item, NOT a unit) — R-CXA-2 engine-layer activation homes at **E-2 (WAL_SEGMENT), NOT E-1** (correcting the design doc's E-1 attribution). A within-impl-against-cleared-spec re-sequencing (recorded-not-gated), not a fork.

§3.5 is the E aggregate cross-axis DAG home (5 nodes — 3 CP + 2 RT — acyclic; single cross-axis edge U-RT-122 → U-CP-95, RT→CP downstream). **ZERO spec amendment; ZERO new contract ID; X-AL-3-clean** (closed `EngineClass`/`ResumptionKind` enums consumed). Delta-only (U-CP-01..92 preserved verbatim). Co-published with runtime plan v2.45.

## Notes
- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Next: E-impl-1 (U-CP-93 alone) → E-impl-2 (U-CP-94 + U-RT-121 + U-CP-95 + U-RT-122 coupled cluster) → (separate) E-spec-3 → E-impl-3 (RECONCILER_LOOP). Per companion §6.
- See `.harness/clearance/README.md` for marker discipline.
