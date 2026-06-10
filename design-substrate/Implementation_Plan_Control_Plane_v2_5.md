# Implementation Plan — Control Plane v2.5

**Status:** Proposed

**Date:** 2026-05-15

**Revision:** v2.5 — Phase 7 sub-phase 7b in-CLI plan revision absorbing the operator-resolved **Tension 003** (`WorkloadClass` undeclared by any plan unit). Adds foundational unit **U-CP-00**; amends **U-CP-22**.

**Revision date:** 2026-05-15

**Source set:** CP spec v1.3 + CP spec v1.2 (§10–§24 preserved-verbatim) + ADR-D1 v1.2 + ADR-D6 v1.2 + ADD v1.3 + PRD v1.1 (substrate versions unchanged from v2.4)

**Authority chain:** `Project_Workflow_v1_8.md` §7.4 fidelity-grammar; `implementation-planner` SKILL.md §8 revision-pass sub-mode; `CLAUDE.md` §1.3 authority chain.

**Entry authorization:** Operator decision 2026-05-15 — `.harness/archive/root-historical/Phase_7_Class_1_Tension_003_WorkloadClass_Undeclared.md` §6 RESOLVED (declare `WorkloadClass` in `harness-core` via new foundational unit U-CP-00).

---

## §0 Change-note (v2.4 → v2.5)

### §0.1 Scope

Absorbs the operator-resolved **Tension 003**. The CP plan consumed the foundational type `WorkloadClass` at ~11 unit signatures (U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-22, U-CP-23, and others) with **no atomic unit assigned to declare it** — a Phase-6 plan-coverage gap against `Spec_Control_Plane` C-CP-07 §7.3 (which commits the 4 workload-class values). This is a plan completeness defect (`implementation-planner` SKILL.md §2 — "if a spec contract is not covered by at least one unit, the plan is incomplete"), not a design extension: the values are spec-committed; only the declaring unit was missing.

v2.5 adds foundational unit **U-CP-00** to declare `WorkloadClass` (residing in `harness-core` per operator decision — cross-axis shared type) and amends **U-CP-22** to depend on it.

### §0.2 Sections preserved verbatim (from v2.4)

| Section | Preservation rationale |
|---|---|
| §0 change-note (v2.4) + §1 Spec inventory | Substrate versions unchanged at v2.5 |
| §2.1 Cluster 1 — U-CP-01 through U-CP-09 (v2.4 conformance at U-CP-01 preserved) | No v2.5 finding; U-CP-07 v2.3 body + U-CP-01 v2.4 body intact |
| §2.2–§2.9 Clusters 2–9 — U-CP-10 through U-CP-55 | v2.4 conformance amendments (U-CP-10/12/19/22/23/43/46/47/48) preserved intact; v2.5 re-revises **U-CP-22 only** (full body below) |
| §3 dependency graph | v2.5 delta per §0.5 (U-CP-00 node + edges added); all v2.4 edges preserved |
| §4 coverage matrix | v2.5 delta per §0.4 (C-CP-07 §7.3 cell added); all v2.4 cells preserved |

### §0.3 Sections revised / added (v2.4 → v2.5)

| Section | Shape | Resolves |
|---|---|---|
| **U-CP-00 (NEW)** | New foundational atomic unit — declares `WorkloadClass` closed 4-value enum; `Implements: C-CP-07 §7.3`; `Files affected: harness-core`; `Depends on: (none)` | Tension 003 |
| U-CP-22 `Depends on:` | `(none)` → `[U-CP-00]` | Tension 003 |
| U-CP-22 `Inputs:` | `None` → `WorkloadClass` enum (U-CP-00) | Tension 003 |

CP-plan unit inventory: 55 → **56** units (U-CP-00 added; U-CP-01–U-CP-55 unchanged).

### §0.4 Coverage matrix delta

| Coverage cell | At v2.4 | At v2.5 |
|---|---|---|
| C-CP-07 §7.3 workload-class taxonomy (4-value `WorkloadClass` enum) | **Not covered** — no declaring unit (Tension 003 gap) | ✅ Covered at U-CP-00 |

C-CP-07 §7.1/§7.4 remain covered at U-CP-15 (landed). No other cell change.

### §0.5 Dependency graph delta

- **U-CP-00 added** at Level 0 (foundational; `Depends on: (none)`; `harness-core` residence).
- **U-CP-22** gains edge → `[U-CP-00]`. U-CP-22 moves from L0 to L1 (consumer of one L0 unit).
- The ~10 other `WorkloadClass`-consuming units (U-CP-05, U-CP-06, U-CP-09, U-CP-13, U-CP-17, U-CP-21, U-CP-23, and others per Tension 003 §2) **also gain a `[U-CP-00]` dependency edge.** Their unit bodies are `[preserved verbatim]` pointers at this delta; the edge is recorded here and is materialized at each unit's next full-revision (none of the ~10 lands before its next revision-pass, so the deferred materialization does not gate any landing). Aggregate DAG remains acyclic — U-CP-00 is a pure source node (in-degree 0), so no cycle is introducible.

### §0.6 Substrate-version-citation table

No substrate-version delta from v2.4. CP spec v1.3 / v1.2; ADR-D1 v1.2; ADR-D6 v1.2; ADD v1.3; PRD v1.1; Workflow v1.8.

### §0.7 Status

`Status: Proposed` per `implementation-planner` SKILL.md §8 — promotion to `Accepted` requires P6-CK / Phase-7 pre-implementation re-clearance.

### §0.8 Forward-flagged concerns (v2.5)

All v2.4 §0.8 forward-flagged concerns carry unchanged (U-CP-08, U-CP-11, U-CP-43 input-set divergence + `MCP_TRUST` under-spec, U-CP-23 structural mismatch, U-CP-13/U-CP-52 marginal drift). v2.5 adds none. **Tension 003 is RESOLVED at v2.5** (was carried open at v2.4 §0.8) — removed from the forward-flagged set.

Deferred-materialization note: the ~10 `WorkloadClass`-consuming units' `Depends on:` edges (§0.5) are recorded but not yet written into the pointer-preserved bodies. This is tracked as a v2.5 plan-internal completeness item, not a fork.

### §0.9 v2.5 coherence-pass summary

| Pass | Status |
|---|---|
| §1 Spec inventory | ✅ PASS — no substrate-version delta |
| §2 Atomic-unit decomposition | ✅ PASS — U-CP-00 is a single coherent change (one enum declaration; SKILL.md §3.1); U-CP-22 re-revised for the dependency edge only; all other units preserved verbatim |
| §3 Dependency graph | ✅ PASS — U-CP-00 added as L0 source node; acyclic invariant preserved (§0.5) |
| §4 Spec-traceability | ✅ PASS — U-CP-00 cites C-CP-07 §7.3 (verified — workload-class taxonomy); U-CP-22 citations unchanged from v2.4 |
| §4.4 No spec extension | ✅ PASS — U-CP-00 declares values already committed at C-CP-07 §7.3; no value invented. `extension-class` (§7.3 open-extension option) is documented, not materialized as an enum member |
| Verbatim-claim check | ✅ PASS — U-CP-00 acc #1 4-value enumeration verified byte-exact against C-CP-07 §7.3 (`software-engineering | content-creation | pipeline-automation | research`) |

---

## §1 Spec inventory

[Preserved verbatim from v2.4 → v2.3 → v2.2. v2.5 adds the C-CP-07 §7.3 coverage cell per §0.4.]

---

## §2 Atomic-unit decomposition

### §2.0 Foundational pre-anchor (v2.5 — Tension 003 resolution)

#### U-CP-00 — Declare `WorkloadClass` closed 4-value enum (v2.5 — new foundational unit per Tension 003 resolution; resides in `harness-core` as a cross-axis shared type)

**Implements:** [C-CP-07 §7.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying enum unit).

**Files affected:** `harness-core` workload-class enum (logical: `workload-class-enum`).

**Residence rationale (v2.5).** `WorkloadClass` is referenced across all four axes' plans (IS / AS / CP / OD all reference workload classes per ADR-D4 + Persona §3.1); per the operator's Tension 003 resolution it resides in **`harness-core`** (the shared-types + cross-axis-utilities package) rather than inside `harness-cp`. The CP plan carries the declaring unit because C-CP-07 §7.3 is the spec contract that commits the taxonomy; the unit's `Files affected` targets `harness-core`.

**Signatures:**

```
enum WorkloadClass {
  SOFTWARE_ENGINEERING,                              // C-CP-07 §7.3 `software-engineering`
  CONTENT_CREATION,                                  // C-CP-07 §7.3 `content-creation`
  PIPELINE_AUTOMATION,                               // C-CP-07 §7.3 `pipeline-automation`
  RESEARCH                                           // C-CP-07 §7.3 `research`
}
```

**Acceptance criteria:**

1. `WorkloadClass` declares exactly four values per C-CP-07 §7.3 verbatim — the SCREAMING_SNAKE_CASE rendering of the §7.3 workload-class taxonomy `software-engineering | content-creation | pipeline-automation | research`.
2. The enum is **closed** at cardinality 4. `extension-class` — the C-CP-07 §7.3 binding-time open-extension option ("extension-class per Persona §3.2") — is the escape hatch for a workload class beyond the 4 canonical; it is NOT an enum member of the closed `WorkloadClass` set. Documented at the unit; not materialized as a 5th value (no spec extension — Persona §3.2's extension mechanism is out of this foundational enum's scope).
3. `WorkloadClass` resides in `harness-core` (cross-axis shared type); CP / IS / AS / OD axis units consume it by import.
4. Member string values are the §7.3 lowercase-hyphen identifiers verbatim (`software-engineering`, etc.) — the SCREAMING_SNAKE_CASE Python member names are a stack naming convention; the string values match §7.3 byte-exact.

**Tests:** `test_workload_class_cardinality_four`; `test_workload_class_values_match_spec_7_3_verbatim`; `test_workload_class_resides_in_harness_core`; `test_workload_class_closed_no_extension_class_member`.

**Rollback boundary:** Revert the `WorkloadClass` enum declaration. Downstream impact: U-CP-22 `is_admissible` signature loses its `workload` parameter type; the ~10 other `WorkloadClass`-consuming CP units lose the foundational type; Tension 003 reopens.

### §2.1 Cluster 1 — Routing, fallback, breaker, retry (C-CP-01 through C-CP-04)

[Preserved verbatim from v2.4 — U-CP-01 (v2.4 conformance) through U-CP-09; U-CP-07 v2.3 body intact.]

### §2.2 Cluster 2 — F3 lifecycle + manifest (C-CP-05, C-CP-06)

[Preserved verbatim from v2.4 — U-CP-10 / U-CP-12 (v2.4 conformance) + U-CP-11 / U-CP-13.]

### §2.3 Cluster 3 — D1 engine + replay (C-CP-07, C-CP-08, C-CP-09)

[Preserved verbatim from v2.4 — U-CP-14 through U-CP-21. Note: C-CP-07 §7.1/§7.4 covered at U-CP-15 (landed); §7.3 now covered at U-CP-00 (§2.0).]

### §2.4 Cluster 4 — Topology (C-CP-10, C-CP-11)

[U-CP-23 preserved verbatim from v2.4 (v2.4 conformance). **U-CP-22 re-revised at v2.5 — full body below.** U-CP-24 through U-CP-25 preserved verbatim from v2.4.]

#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate (v2.5 amendment — `Depends on:` / `Inputs:` amended to consume `WorkloadClass` from U-CP-00 per Tension 003 resolution; v2.4 §10.1/§10.2 conformance body preserved verbatim)

**Implements:** [C-CP-10 §10.1, §10.2, §10.3]

**Depends on:** [U-CP-00]

**Inputs:** `WorkloadClass` enum (U-CP-00) — consumed by the `is_admissible` predicate's `workload` parameter.

**Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).

**Signatures (v2.4 conformance — preserved verbatim at v2.5):**

```
enum TopologyPattern {
  SINGLE_THREADED_LINEAR,                             // spec §10.1 pattern 1 `single-threaded-linear`
  ORCHESTRATOR_WORKERS,                               // spec §10.1 pattern 2 `orchestrator-workers`
  DECENTRALIZED_HANDOFF,                              // spec §10.1 pattern 3 `decentralized-handoff`
  HIERARCHICAL_DELEGATION,                            // spec §10.1 pattern 4 `hierarchical-delegation`
  EVALUATOR_OPTIMIZER,                                // spec §10.1 pattern 5 `evaluator-optimizer`
  PARALLELIZATION                                     // spec §10.1 pattern 6 `parallelization`
}

// CP spec §10.2 declares `cascade_policy` as a string-literal FIELD DOMAIN on
// TopologyDeclaration, not a named enum. The plan materializes the domain as a
// named enum CascadePolicy whose values are the §10.2 domain literals verbatim.
enum CascadePolicy {
  PAUSE,                                              // spec §10.2 domain literal "pause"
  PROCEED,                                            // spec §10.2 domain literal "proceed"
  CASCADE_CANCEL                                      // spec §10.2 domain literal "cascade-cancel"
}

function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
    // §10.3 cross-pattern admissibility per workload class
    // (v2.5 — `WorkloadClass` resolves to U-CP-00 per Tension 003 resolution)
```

**Acceptance criteria (v2.4 conformance — preserved verbatim at v2.5):**

1. **(v2.4 amendment — 6-pattern taxonomy conformed to CP spec §10.1 verbatim per Tension 002 / §4A cluster resolution; the v2.1/v2.3 enum carried the divergent values `SINGLE_AGENT`/`SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE`/`RECONCILER_MESH`/`ROUTER_DELEGATE`/`PIPELINE_STAGES`.)** `TopologyPattern` declares exactly six values per C-CP-10 §10.1 verbatim — the SCREAMING_SNAKE_CASE rendering of the §10.1 six-pattern taxonomy table "Pattern" column: `SINGLE_THREADED_LINEAR` (`single-threaded-linear`), `ORCHESTRATOR_WORKERS` (`orchestrator-workers`), `DECENTRALIZED_HANDOFF` (`decentralized-handoff`), `HIERARCHICAL_DELEGATION` (`hierarchical-delegation`), `EVALUATOR_OPTIMIZER` (`evaluator-optimizer`), `PARALLELIZATION` (`parallelization`).
2. **(v2.4 amendment — `CascadePolicy` domain conformed to CP spec §10.2 verbatim; section citation corrected §10.3 → §10.2.)** `CascadePolicy` declares exactly three values — the SCREAMING_SNAKE_CASE rendering of the CP spec §10.2 `TopologyDeclaration.cascade_policy` string-literal field domain `"pause" | "proceed" | "cascade-cancel"`: `PAUSE` (`pause`), `PROCEED` (`proceed`), `CASCADE_CANCEL` (`cascade-cancel`). The spec declares a *field domain*, not a named enum — `enum CascadePolicy` is the permitted plan-side materialization.
3. **(v2.4 amendment — admissibility conformed to CP spec §10.3 verbatim.)** `is_admissible` returns `true` per C-CP-10 §10.3 cross-pattern admissibility annotations:
   - `HIERARCHICAL_DELEGATION` — admissible at `SOFTWARE_ENGINEERING` and `RESEARCH` workloads when scope-bounded recursion is justified (fan-out cap 3 per parent; cascade-policy inherits parent cell)
   - `DECENTRALIZED_HANDOFF` — admissible at `PIPELINE_AUTOMATION` per-stage-expert workflows (cascade-policy `CASCADE_CANCEL`; single-owner-at-a-time invariant)
   - `PARALLELIZATION` — admissible at `RESEARCH` breadth-search and `CONTENT_CREATION` A/B-variant generation (cap 3–5; voting aggregator at synthesis)
   Per §10.3: non-primary patterns are admissible but not primary; the per-workload-class *primary* pattern is committed at C-CP-11 §11.1 (consumed at U-CP-23). **(v2.5 — the `workload` parameter is typed `WorkloadClass` per U-CP-00.)**
4. Taxonomy closed at cardinality 6; extension requires Workflow §4.1.2 Class-2 D4 revision. **[Preserved from v2.3.]**

**Tests (v2.4 — preserved verbatim at v2.5):** `test_topology_pattern_cardinality_six`; `test_topology_pattern_values_match_spec_10_1_verbatim`; `test_cascade_policy_cardinality_three`; `test_cascade_policy_values_match_spec_10_2_verbatim`; `test_admissibility_per_workload_class_match_spec_10_3`; `test_taxonomy_closed`. **(v2.5 adds:** `test_is_admissible_accepts_workload_class_from_u_cp_00` — verifies the `workload` parameter binds the U-CP-00 `WorkloadClass` enum.**)**

**Rollback boundary:** Revert `TopologyPattern` + `CascadePolicy` enums + admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose topology discriminator. Reverting reintroduces the Tension 002 / §4A verbatim divergence and de-conforms CP-AL-1. **(v2.5 — the `Depends on: [U-CP-00]` edge releases on revert; U-CP-00 itself is unaffected.)**

### §2.5–§2.9 Clusters 5–9

[U-CP-26 through U-CP-55 preserved verbatim from v2.4.]

---

## §3 Dependency graph

[Preserved verbatim from v2.4 in structure. v2.5 delta per §0.5: U-CP-00 added at Level 0 (`Depends on: (none)`); U-CP-22 gains edge → [U-CP-00] (moves L0 → L1); ~10 other consuming units gain the [U-CP-00] edge (recorded; materialized at next full-revision per §0.5). Aggregate DAG acyclic — U-CP-00 is a pure source node.]

---

## §4 Coverage matrix

[Preserved verbatim from v2.4 in structure. v2.5 delta per §0.4: C-CP-07 §7.3 workload-class taxonomy cell now covered at U-CP-00.]

---

## §[carry-forwards]

[Preserved verbatim from v2.4. Tension 003 RESOLVED at v2.5 — removed from open carries.]

---

*End of Implementation Plan — Control Plane v2.5. Filed at Phase 7 sub-phase 7b. Absorbs the operator-resolved Tension 003 — adds foundational unit U-CP-00 (`WorkloadClass` in `harness-core`), amends U-CP-22. `Status: Proposed` pending pre-implementation re-clearance.*
