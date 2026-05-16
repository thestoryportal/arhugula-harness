# OD axis-stream worklist — Phase 7 sub-phase 7b

**Plan:** `Implementation_Plan_Operational_Discipline` — body resolution chain:
v2.1 §3 (base bodies for unrevised units) → v2.5 §3 (9 verbatim-conformed units:
U-OD-02/04/09/11/12/14/30/32/33) → v2.6 §3 (R5 materializability: M-1 carrier
re-points, M-2 edges, M-3, U-OD-00 NEW) → v2.7 (U-OD-00 carrier micro-revision).
**Spec:** `Spec_Operational_Discipline_v1_3.md` (C-OD-01..23).
**Materializability:** all 35 units CLEARED — 14 prior FORKs resolved by R5
(T2 = all M-1 types FACTOR-OUT, 0 design extensions). See
`.harness/materializability_audit_od_plan.md` + `revision_R5_od_plan.md`.

**Cross-axis posture:** OD is consumer-most-downstream. All cross-axis deps
(IS 17/17, AS 33/33, CP complete) are LANDED. Cross-axis edges cited by contract
section; placeholder unit-IDs resolve at 7c — NOT a 7b blocker (audit §rej-4).

## Topological levels (Kahn, v2.1 §4.4 + U-OD-00 at L0 per Q-R5-5)

| Level | Units | Status |
|---|---|---|
| L0 | U-OD-00, U-OD-01, U-OD-04 | ✅ LANDED |
| L1 | U-OD-02, U-OD-05, U-OD-15, U-OD-18 | pending |
| L2 | U-OD-03, U-OD-06, U-OD-07, U-OD-13, U-OD-16, U-OD-19, U-OD-23 | pending |
| L3 | U-OD-08, U-OD-09, U-OD-14, U-OD-20, U-OD-26 | pending |
| L4 | U-OD-10, U-OD-11, U-OD-21 | pending |
| L5 | U-OD-12, U-OD-17, U-OD-27 | pending |
| L6 | U-OD-22, U-OD-28, U-OD-32 | pending |
| L7 | U-OD-24, U-OD-29, U-OD-33 | pending |
| L8 | U-OD-25, U-OD-30 | pending |
| L9 | U-OD-31, U-OD-34 (terminal exporter) | pending |

32 units remaining. Execution: one sub-agent batch per level, sequential;
commit per unit; pyright strict 0 + pytest green before level close.

## Phase 1 / Phase 2 boundary watch (operator standing directive)

Flag any OD unit touching runtime / composition-root / DevEx-plane concerns —
must not pre-empt Phase 2. Candidates to watch: U-OD-27 (in-process OTLP
collector + TUI trace browser), U-OD-34 (terminal substrate seam manifest).
TUI/collector are observability *primitives*, not the harness runtime — but
flag if a unit reaches past primitive into "start the process".

## Progress log

- **L1 closed 2026-05-16.** U-OD-05/15/18 landed (pyright strict 0, 87 tests
  green). **U-OD-02 HALTED Class 1** — `.harness/class_1_tension_u_od_02_cell_4_5_alternation.md`:
  spec C-OD-02 §2.1 commits a cell-4/5 backend-class disjunction, plan signature
  `backend_class : BackendClass` is single-valued. Both prior audits missed it.
  Recommended fix = Option A (widen signature, plan-internal conform-to-spec, no
  spec change). DEFERRED for operator ratification — signature change, same
  review class as CP v2.8/v2.9.
- **Deferred U-OD-02 cluster** (blocked on U-OD-02 resolution): U-OD-02, U-OD-03
  (L2), U-OD-28 (L6), U-OD-30 (L7). All other units proceed.
- **L2 closed 2026-05-16.** U-OD-06/07/16 landed (first batch); U-OD-13/19/23
  landed (second batch) + U-OD-04 v2.6 carrier-growth applied. pyright strict 0,
  154 tests green. U-OD-13 stale-edge struck; U-OD-19/23 Span* carrier resolved.
  Phase-2 flag: U-OD-23 `emit_eval_as_child_span` uses the global tracer
  provider — real parent→child trace inheritance unverified until a Phase 2
  composition root wires `set_tracer_provider`. Class 3 informational; AC met.
- **L3 closed 2026-05-16.** U-OD-14/20/26 landed. pyright strict 0, 254 tests
  green. U-OD-08 HALTED (`F2_LIFECYCLE_EVENT_MAPPINGS` 8-set disjoint 5/8 from
  spec C-OD-06 §6.1 — plan-vs-spec divergence; conform-to-spec). U-OD-09 HALTED
  (FF-1 — AC #2 tier classification has no C-OD-07 §7.1 spec basis + the
  `AttributeTier` enum has no REQUIRED/CONDITIONAL members; strike AC #2).
- **Deferred cluster now 7 units** pending an OD-plan implementation-planner
  revision pass: U-OD-02 (widen signature), U-OD-03 (on 02), U-OD-08 (conform
  event set to spec), U-OD-09 (strike AC #2), U-OD-10 (on 08/09), U-OD-28
  (on 02), U-OD-30 (on 02). Corpus-hygiene note: F3 lifecycle event taxonomy
  appears in 3 divergent forms (plan / spec §6.1 / OD CLAUDE.md §1.1) —
  unpinned; flag for the revision pass.
- **OD landed: 15/35** (00,01,04,05,06,07,13,14,15,16,18,19,20,23,26).
  Remaining 20 — 13 buildable + 7 deferred.
