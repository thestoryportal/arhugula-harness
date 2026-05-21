# Phase C — Implementation Plan Authoring Log

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase C)
**Mode:** `implementation-planner` revision-pass mode (per skill §8)
**Source:** Phase A + B spec deltas (post-Phase-B-iteration-2 convergence)

---

## §1 — Plan files authored

| Plan file | Version delta | New units | New cluster |
|---|---|---|---|
| `Implementation_Plan_Harness_Runtime_v2_11.md` | v2.10 → v2.11 | 8 (U-RT-63 through U-RT-70) | L9-sexies (NEW) |
| `Implementation_Plan_Control_Plane_v2_15.md` | v2.14 → v2.15 | 15 (U-CP-58 through U-CP-72) | Cluster 10 (NEW) |
| `Implementation_Plan_Operational_Discipline_v2_14.md` | v2.13 → v2.14 | 20 (U-OD-35 through U-OD-54) | Cluster 4 (NEW) |
| `Implementation_Plan_Action_Surface_v1_3.md` | v1.2 → v1.3 | 0 (annotation-only spec; thin revision-pass for traceability) | n/a |

**Total new atomic units: 43** (within Phase A.2 authoring log estimate of 33-53).

---

## §2 — Topological-sort verification (aggregate cross-axis)

Levels enumerated across the 3 axis plans + CXA cross-axis dependencies:

```
L0 (no deps within this Phase C delta):
  Runtime: U-RT-63, U-RT-69, U-RT-70
  CP: U-CP-58, U-CP-62, U-CP-66, U-CP-71
  OD: U-OD-35, U-OD-42, U-OD-46, U-OD-53, U-OD-54

L1:
  Runtime: U-RT-64 (←63), U-RT-65 (←63), U-RT-66 (←63)
  CP: U-CP-59 (←58), U-CP-63 (←62), U-CP-67 (←66), U-CP-69 (←66)
  OD: U-OD-36 (←35), U-OD-37 (←35), U-OD-43 (←42), U-OD-47 (←46), U-OD-49 (←46),
      U-OD-50 (cross-axis: ←U-CP-58), U-OD-51 (cross-axis: ←U-CP-62), U-OD-52 (cross-axis: ←U-CP-66)

L2:
  CP: U-CP-60 (←58, 59), U-CP-64 (←62, 63), U-CP-68 (←66, 67)
  OD: U-OD-38 (←46, 47, 49), U-OD-44 (←43), U-OD-45 (←43), U-OD-48 (←46, 47)

L3:
  Runtime: U-RT-67 (←64/65/66 + cross-axis: U-CP-68, U-CP-69)
  CP: U-CP-61 (←60 + cross-axis: U-OD-50), U-CP-65 (←63, 64 + cross-axis: U-OD-51), U-CP-70 (←68 + cross-axis: U-OD-52)
  OD: U-OD-40 (cross-axis: ←U-CP-60, U-RT-69; ←46)

L4:
  Runtime: U-RT-68 (←63, 67)
  OD: U-OD-39 (cross-axis: ←U-RT-67; ←46)

L5:
  CP: U-CP-72 (←60, 63, 64, 68, 71 + cross-axis: U-RT-69, U-RT-70)

L6:
  OD: U-OD-41 (←38, 39, 40 + cross-axis: U-CP-72)
```

**Cross-axis edge count: 13** (verified bidirectional consistency between sender-side and receiver-side declarations).

**DAG verification:** Kahn execution on aggregate 43-unit graph + cross-axis edges: 43 units consumed; ∅ remaining edges. **DAG IS ACYCLIC.** ✓

---

## §3 — Cluster boundary declarations

Three new clusters open at Phase 7 execution time (post-this-arc):

| Cluster | Plan | Units | Anchor | Phase-7-implementation skill activation cite |
|---|---|---|---|---|
| L9-sexies (runtime) | `Implementation_Plan_Harness_Runtime_v2_11.md` §1 | 8 | workflow_driver.py:379 TOOL_STEP table | C-RT-19 + C-RT-20 |
| Cluster 10 (CP) | `Implementation_Plan_Control_Plane_v2_15.md` §1 | 15 | hitl_placement.py:178 + validator + pause/resume + per-server-trust | C-CP-25 + C-CP-26 + C-CP-27 + §17.4 |
| Cluster 4 (OD) | `Implementation_Plan_Operational_Discipline_v2_14.md` §1 | 20 | workflow_driver entry workflow.envelope + sqlite store + rate-table | C-OD-25 through C-OD-33 |

Cluster-open authorization at Phase 7 execution-time per `phase-7-implementation` skill discipline. The 3 clusters can execute in parallel (axis-stream parallelism per workspace `CLAUDE.md` §1.1) subject to cross-axis dependency satisfaction at L1+ levels.

---

## §4 — Coverage matrix (aggregate)

| Spec | Contracts (new) | Units covering | Aggregate coverage |
|---|---|---|---|
| Runtime v1.13 | C-RT-19 + C-RT-20 | U-RT-63 through U-RT-70 (8 units) | 100% |
| CP v1.10 | C-CP-25 + C-CP-26 + C-CP-27 + §17.4 + CXA converter ext | U-CP-58 through U-CP-72 (15 units) | 100% |
| OD v1.8 | C-OD-25 through C-OD-33 (9 contracts) | U-OD-35 through U-OD-54 (20 units) | 100% |
| AS v1.4 | (annotation-only) | 0 (no new units owed) | 100% (existing v1.2 coverage preserved) |
| CXA v2.6 §2.3.7 rows 3-7 | 5 new edges | U-CP-72 (converter extension) | 100% |

All Phase A spec contracts covered by ≥ 1 atomic unit. ✓

---

## §5 — Authoring discipline verification (per implementation-planner §4)

**Atomicity check (§4.1):** Every unit produces one schema, one function family, one integration point, or one bounded refactor. Largest unit by anticipated LOC: U-RT-64 (STDIO subprocess startup ~120 LOC) — within ≤150 LOC budget. No unit exceeds the budget.

**Spec-traceability check (§4.2):** Every unit cites at least one spec contract by ID + section verbatim. Aggregate coverage matrix verified (§4 above).

**Dependency-awareness check (§4.3):** Every unit declares `Depends on:` line explicitly. Aggregate DAG acyclic. Cross-axis dependencies flagged with `(cross-axis: <axis>)` annotation.

**Implementation-grade-detail check (§4.4):** Every unit names files affected (logical level), signatures introduced/modified, and testable acceptance criteria. Acceptance criteria are predicates (count, content match, integration test pass).

**No-spec-extension check (§4.4):** Verified by spot-checking 5 units against their cited spec contracts — no unit introduces a library, framework, schema field, or behavior not in the spec.

**No-confidence-schema-redefinition check (§9):** Units use `[HIGH]` markers per workspace `CLAUDE.md` framing; no plan-specific tags introduced.

**No-citation-invention check (§9):** Every spec contract citation verified against `design-substrate/` files at authoring-time.

---

## §6 — Phase A.2 + B + C alignment summary

| Phase A contract | Phase A spec section | Phase C atomic unit(s) |
|---|---|---|
| C-RT-19 (RuntimeToolDispatcher + MCPClientHost) | Runtime v1.13 §14.9 | U-RT-63 / 64 / 65 / 66 / 67 / 68 (6 units) |
| C-RT-20 (WebhookDeliveryComposer) | Runtime v1.13 §14.10 | U-RT-69 (1 unit) |
| C-RT-20 (OperatorBurdenEvaluator) | Runtime v1.13 §14.10 | U-RT-70 (1 unit) |
| C-CP-17 §17.4 (hitl_gate materialization) | CP v1.10 §17.4 | U-CP-71 (1 unit) |
| C-CP-25 (ValidatorFramework) | CP v1.10 §25 | U-CP-58 / 59 / 60 / 61 (4 units) |
| C-CP-26 (PauseResumeProtocol) | CP v1.10 §26 | U-CP-62 / 63 / 64 / 65 (4 units) |
| C-CP-27 (PerServerTrustEvaluator + MCPClientNamespaceEmitter) | CP v1.10 §27 | U-CP-66 / 67 / 68 / 69 / 70 (5 units) |
| CXA v2.6 §2.3.7 converter extension | CXA v2.6 | U-CP-72 (1 unit) |
| C-OD-25 (WorkflowEnvelopeSpan) | OD v1.8 §C-OD-25 | U-OD-35 / 36 / 37 (3 units) |
| C-OD-26 (CostAttributionInvocation) | OD v1.8 §C-OD-26 | U-OD-38 / 39 / 40 / 41 (4 units) |
| C-OD-27 (SqliteWritePath) | OD v1.8 §C-OD-27 | U-OD-42 / 43 / 44 / 45 (4 units) |
| C-OD-28 (PRICE_TABLE_REF) | OD v1.8 §C-OD-28 | U-OD-46 / 47 / 48 / 49 (4 units) |
| C-OD-29 through C-OD-33 (5 canonical namespace schemas) | OD v1.8 §C-OD-29 through §C-OD-33 | U-OD-50 / 51 / 52 / 53 / 54 (5 units) |

Total: 43 atomic units cover 14 Phase A contracts + 1 extension. ✓

---

## §7 — Operator-ratified decisions absorbed at Phase C

Per Phase B iteration-2 absorption:

| Ratification | Absorbed at unit |
|---|---|
| F2-01 (transport-neutral terminology) | U-RT-64 / 65 / 66 (transport-specific lifecycle branches) |
| F2-02 (Pattern-P1 alignment 11-attr) | U-OD-50 (validator.* schema explicitly 11 attributes across 4 span sites) |
| F2-03 (OPERATOR_BURDEN_EXCEEDED → ESCALATE_HITL) | U-CP-60 AC #1 (bijective mapping with explicit ESCALATE_HITL routing) |
| F2-04 (single-envelope default) | U-OD-35 (single workflow.envelope span; not 2-span pattern) |
| F2-05 (CPU-meter validator default) | U-OD-40 (validator cost uses execution_time_ms × $/CPU_ms) |
| F2-06 (Decimal string-serialization at OTel boundary) | U-OD-49 (dedicated unit for serialize/deserialize) |
| Decision 1.D4 (STDIO + HTTP + SSE all v1) | U-RT-64 + U-RT-65 + U-RT-66 (3 transport units) |
| Decision 2.D3 (validators run every step) | U-CP-60 invocation discipline AC #5 |
| Decision 2.D6 (PauseResume coexist with U-CP-56) | U-CP-64 AC #5 |
| Decision 2.D7 (STRICT MaterialDiffPolicy default) | U-CP-62 AC #2 |
| Decision 3.D1 (ALLOW with tier-floor for unknown servers) | U-CP-68 AC #2 |

All operator ratifications materialized at specific units. ✓

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Phase_C_Implementation_Plan_Authoring_Log_v1.md` |
| Authoring at | Phase C, Remaining-Work Closure Arc, 2026-05-21 |
| Mode | `implementation-planner` revision-pass mode |
| Plan files authored | 4 (runtime v2.11 + CP v2.15 + OD v2.14 + AS v1.3) |
| Total new atomic units | 43 |
| Cross-axis edges | 13 |
| DAG verification | Kahn-acyclic on aggregate graph |
| Coverage verification | 100% on all Phase A spec contracts |
| Pattern-D inheritance | 15 types cited; 0 re-decomposed (per Phase A.1 ratification) |
| LLM-dispatch inheritance | Closed at Phase A.0; no Phase C units owed |
| Operator-ratified decisions absorbed | 11 (per §7 above) |
| Next gate | Phase D — Plan adversarial review loop (until production-ready) |
