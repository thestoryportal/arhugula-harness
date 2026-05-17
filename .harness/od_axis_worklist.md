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
- **L4/L5 batch 2026-05-16.** U-OD-11/17/27 landed (pyright strict 0, 302 tests
  green). U-OD-27 partial-land — library surface only; live collector/TUI/sqlite
  Class 3 for Phase 2 per operator standing directive. U-OD-11's U-OD-09 dep is
  event-class-string-only (not blocked by the U-OD-09 halt). U-OD-21 HALTED
  Class 1 (`.harness/class_1_tension_u_od_21_span_cost_record_missing_rollup_keys.md`
  — `SpanCostRecord` carrier lacks provider/model/family-tag fields acc #3
  requires; v2.6 M-2 fixed the edge, not the carrier shape). U-OD-12 HALTED
  Class 1 (`.harness/class_1_tension_u_od_12_disjoint_set_string_collision.md`
  — acc #2 set-disjointness contradicted by the `files.operation` /
  `memory.operation` bare-string collision; regime is keyed on `(event_class,
  kind)`, signature on `event_class`). U-OD-10 not attempted (BLOCKED on halted
  U-OD-08/09).
- **Deferred cluster now 9 units** pending an OD-plan implementation-planner
  revision pass: U-OD-02, U-OD-03, U-OD-08, U-OD-09, U-OD-10, U-OD-12, U-OD-21,
  U-OD-28, U-OD-30.
- **OD landed: 18/35** (00,01,04,05,06,07,11,13,14,15,16,17,18,19,20,23,26,27).

## OD-7b HARD STOP 2026-05-16 — 18/35 landed; remaining 17 all blocked

Dependency analysis: the 9-unit deferred cluster transitively blocks **all 17**
remaining units. U-OD-12 → blocks U-OD-32, U-OD-33. U-OD-12 + U-OD-21 → block
U-OD-22 → U-OD-24 → U-OD-25 → U-OD-31. U-OD-28 → blocks U-OD-29. U-OD-34
(terminal exporter) depends on six deferred units. **Nothing more lands without
the revision pass.**

### 5 root defects — all one defect class (signature-vs-AC / plan-vs-spec)

Neither prior audit covered this axis: the verbatim audit checked cardinality,
the materializability audit checked type-carrier reachability. Signature-vs-
acceptance-criterion consistency was never audited — and it produced 5 halts.

| Unit | Defect | Fix direction | Tension record |
|---|---|---|---|
| U-OD-02 | single-valued `backend_class` vs spec §2.1 cell-4/5 disjunction | widen signature to set/tuple (Option A) | `class_1_tension_u_od_02_cell_4_5_alternation.md` |
| U-OD-08 | `F2_LIFECYCLE_EVENT_MAPPINGS` 8-set disjoint 5/8 from spec C-OD-06 §6.1 | conform plan event-set to spec | `class_1_tension_u_od_08_f3_lifecycle_event_set_divergence.md` |
| U-OD-09 | FF-1 — AC #2 tier classification no spec basis; `AttributeTier` enum lacks REQUIRED/CONDITIONAL | strike AC #2 (halt-route-split) | `class_1_tension_u_od_09_tier_classification_design_gap.md` |
| U-OD-12 | acc #2 set-disjointness vs `files.operation`/`memory.operation` collision; regime keyed `(event_class,kind)`, signature on `event_class` | re-key signature to `(event_class,kind)` | `class_1_tension_u_od_12_disjoint_set_string_collision.md` |
| U-OD-21 | `SpanCostRecord` carrier lacks provider/model/family fields acc #3 needs | grow `SpanCostRecord` at U-OD-20 (re-opens a LANDED unit) | `class_1_tension_u_od_21_span_cost_record_missing_rollup_keys.md` |

Plus corpus-hygiene: F3 lifecycle event taxonomy appears in 3 divergent forms
(plan / spec C-OD-06 §6.1 / OD `CLAUDE.md` §1.1) — canonical set unpinned;
needs an architectural call (spec is authoritative per the §1.3 chain).

### Recommendation

One `implementation-planner` OD-plan revision pass (→ v2.8) resolving the 5 root
defects, same review class as CP v2.8/v2.9. Operator ratifies (esp. U-OD-02
widening, U-OD-21 landed-unit re-open, the F3-taxonomy canonical call). On
re-clear: the 17 blocked units land in 2-3 sub-agent batches (L4 leftover →
L9 terminal).

### Deferred cluster (17 units, all blocked on the revision pass)
Root: U-OD-02, 08, 09, 12, 21. Cascade: U-OD-03, 10, 22, 24, 25, 28, 29, 30,
31, 32, 33, 34.

## ✅ REVISION PASS COMPLETE — OD plan v2.8 filed 2026-05-16

`design-substrate/Implementation_Plan_Operational_Discipline_v2_8.md` —
`implementation-planner` revision pass, operator-ratified 2026-05-16. All five
root defects resolved:

- **U-OD-02** — `backend_class` + `select_backend_class` return widened to
  `Set<BackendClass>` (Option A, forced). acc #3/#7 materializable.
- **U-OD-08** — `F3LifecycleEventClass` + `F3_LIFECYCLE_EVENT_MAPPINGS` conformed
  to spec §6.1's eight-event table; `LifecycleEventMapping` grown with
  span-placement + sampling-posture fields (Option A, forced).
- **U-OD-09** — acc #2 (tier split, no spec basis) STRUCK; `HARNESS_BREAKER_ATTRIBUTES`
  re-typed `List<GenAiAttribute>` → `List<string>`; acc #9 re-worded to the §7.2
  all-seven-required invariant (Option B, forced).
- **U-OD-12** — acc #2 re-scoped to honest disjointness over non-`kind`-discriminated
  classes; `files.operation`/`memory.operation` documented dual-regime
  (Option B — implementation-planner recommendation; no signature change,
  **U-OD-11 NOT re-opened**).
- **U-OD-21** — `SpanCostRecord` grown 9→12 fields at U-OD-20 (Option A;
  **re-opens landed U-OD-20** — carrier-field growth only, additive). `rollup_costs_by_axis`
  materializable. New `string`-typed fields avoid a U-OD-20↔U-OD-21 cycle.
- **F3 taxonomy pinned** — `harness-od/CLAUDE.md` §1.1 corrected to spec §6.1
  (the stale third form struck).

No dependency-graph edge changed; unit count 35; coverage complete.

### OD-7b resume plan
Deferred cluster cleared. The 17 blocked units land in topological order
(L4 leftover U-OD-10 → L9 terminal U-OD-34). **U-OD-20 re-lands first**
(carrier growth) ahead of U-OD-21. Per-unit: pyright strict 0, pytest green,
commit-per-unit on `main`.

## OD-7b RESUME PROGRESS 2026-05-16 — 29/35 landed; U-OD-28 FF-2 halt

- **U-OD-20 re-landed** — `SpanCostRecord` grown 9→12 fields (v2.8 D-5).
- **Batch 1** — U-OD-02/08/09/12/21 landed (the 5 v2.8-revised units). 379 tests.
- **Batch 2** — U-OD-03/10/22/32 landed; **U-OD-28 HALTED Class 1 (FF-2)**.
  444 tests.
- **Batch 3** — U-OD-24/25 landed. 477 tests, pyright strict 0.
- **OD landed: 29/35** (prior 18 + U-OD-02/03/08/09/10/12/21/22/24/25/32).
- **U-OD-28 FF-2 HALT** — `.harness/class_1_tension_u_od_28_collector_placement_ff2.md`.
  Plan declares a 7-value deployment-topology `CollectorPlacement` enum; spec
  §1.2 commits a 6-value architectural-class enum; spec §20.1 is an 8-row
  prose matrix with no enum + a cell-2/cell-4 "backend's own collector" gap
  §1.2's 6 values don't cover. Three-way mismatch; needs a spec fix +
  plan-revision. **Operator decision owed.**
- **FF-2 blocks 5 units:** U-OD-28 + dependents U-OD-29, U-OD-30, U-OD-31,
  U-OD-34 (terminal exporter). OD-7b cannot fully close until FF-2 resolves.

## OD-7b CLOSE 2026-05-16 — 34/35 landed; U-OD-29 FF-3 pending

- **FF-2 resolved** — operator ratified Option A. OD spec v1.4 + plan v2.9
  filed (`CollectorPlacement` 7-value enum formalized). See
  `class_1_tension_u_od_28_collector_placement_ff2.md` (RESOLVED).
- **Final batch** — U-OD-28 (against v2.9) / U-OD-30 / U-OD-31 / **U-OD-34
  (terminal aggregate exporter)** landed. pyright strict 0, **563 tests green**,
  ruff clean.
- **OD landed: 34/35.** Only **U-OD-29** outstanding — halted Class 1 on the
  **FF-3** carried fork (`class_1_tension_u_od_29_sandbox_tier_ff3.md`):
  U-OD-29 declares an in-unit 0-indexed `SandboxTier {TIER_0..3}`; the AS axis
  owns + landed `SandboxTier` 1-indexed (`TIER_1_PROCESS..TIER_4_FULL_VM`);
  the v2.6 R5 audit reclassified it as a cross-axis AS edge. U-OD-29 is a
  **leaf** — nothing depends on it; OD-7b closed at 34/35 without it.
  **Operator decision owed** — FF-3 Option A (plan v2.10 micro-revision, land
  at 7b) vs Option B (defer U-OD-29 to 7c cross-axis composition).
- **OD axis-stream 7b is functionally complete** — terminal exporter U-OD-34
  landed. Remaining: resolve FF-3 (1 leaf unit), then 7c cross-axis composition.

## ✅ OD-7b COMPLETE 2026-05-16 — 35/35

- **FF-3 resolved** — operator ratified "resolve now". OD plan v2.10 filed
  (U-OD-29 §3.7.3 conformed: in-unit `SandboxTier` struck, consumed from the
  AS-owned enum; reachability re-keyed to OD spec §20.3). FF-3 tension record
  RESOLVED.
- **U-OD-29 landed** (`per_sandbox_tier_otlp_reachability.py`). `harness-as`
  added as a uv-workspace dependency of `harness-od` for the cross-axis
  `SandboxTier` import (operator-authorized at 7b per v2.10).
- **OD axis-stream 7b: 35/35 landed.** harness-od: pyright strict 0,
  **584 tests green**, ruff clean. All four 7b axis-streams complete
  (IS 17/17, AS 33/33, CP complete, OD 35/35).
- **Next:** sub-phase 7c — cross-axis composition (CXA v2.1, 101 typed edges).
  Note: U-OD-29 acc #6 egress-policy arm is structurally unreachable against
  the current `CollectorPlacement` enum (no public-ingestion value) — retained
  as a forward guard; documented in code. Non-blocking Class 3 observation.

## ⚠️ CORRECTION 2026-05-17 — the "35/35" above was an arithmetic error

At 7c, the cross-axis audit found **U-OD-33 was never landed** at 7b. The
"34/35 → 35/35" close arithmetic double-miscounted: the landed set was 33
units, +U-OD-29 = 34, not 35. U-OD-33 (`§3.8.2` per-dimension preservation
invariants — a within-axis leaf, so no test caught its absence) was missed.
**U-OD-33 landed 2026-05-17** (`per_dimension_preservation_invariants.py` +
15 tests; harness-od now **599 tests green**, pyright 0, ruff clean). OD-7b is
**now genuinely 35/35**. See `.harness/class_1_tension_u_od_33_not_landed.md`.
