# Tension 002 Absorption — U-CP-22 Updated Unit Content

**Deliverable type:** Updated implementation-plan unit content. Per task constraints, the real plan file
(`design-substrate/Implementation_Plan_Control_Plane_v2_1.md`) was **NOT** modified; the revised U-CP-22 block
is produced below as the deliverable.

---

## Follow-up observation (out of scope — flagged, not fixed)

While absorbing Tension 002 two **pre-existing inherited inconsistencies** in the plan were found that the
absorbing edit does not resolve (they are separate findings):

1. **CascadePolicy section-anchor drift.** The original U-CP-22 cites the `CascadePolicy` enum as
   `C-CP-10 §10.3`. In the canonical spec (`Spec_Control_Plane_v1_2.md`, §10 preserved verbatim at v1.3),
   the `cascade_policy` value set (`"pause" | "proceed" | "cascade-cancel"`) lives in **§10.2**
   (TopologyDeclaration surface). Canonical **§10.3** is *"Cross-pattern admissibility per workload class"* —
   the admissibility content, not CascadePolicy. The plan's traceability matrix (line 3447–3449) carries the
   same swap (`§10.2 admissibility predicate` / `§10.3 CascadePolicy 3-class enum`). The §-anchors below are
   corrected to match the canonical spec, but the **traceability matrix at line 3447–3449 is left untouched**
   (separate finding; out of this task's scope).

2. **Fabricated admissibility matrix.** The original AC3 asserted an admissibility matrix
   (`SEQUENTIAL_HANDOFF`/`PARENT_FANOUT_AGGREGATE` admissible for all four workload classes, etc.) that does
   **not** appear in canonical spec §10.3. Canonical §10.3 annotates admissibility for only **three** patterns.
   AC3 below is rewritten to the canonical §10.3 text. This correction is entailed by Tension 002 (the old AC3
   used the now-retired vocabulary), so it is in scope.

---

## Updated U-CP-22 (replacement block, lines 1172–1212)

#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate

**Implements:** [C-CP-10 §10.1, §10.2, §10.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying enum unit).

**Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).

**Signatures:**

```
enum TopologyPattern {
  SINGLE_THREADED_LINEAR    = "single-threaded-linear"     // sole agent owns full lifecycle
  ORCHESTRATOR_WORKERS      = "orchestrator-workers"        // lead decomposes; workers concurrent; lead synthesizes
  DECENTRALIZED_HANDOFF     = "decentralized-handoff"       // each agent owns until handoff; recipient owns post-handoff
  HIERARCHICAL_DELEGATION   = "hierarchical-delegation"     // parent owns until delegation; child owns sub-task; recursion permitted
  EVALUATOR_OPTIMIZER       = "evaluator-optimizer"         // generator + evaluator(s) in loop until convergence
  PARALLELIZATION           = "parallelization"             // independent agents on independent sub-tasks; aggregator merges
}

enum CascadePolicy {
  PAUSE          = "pause"            // pause workflow; route to HITL
  PROCEED        = "proceed"          // continue; lossy synthesis acceptable
  CASCADE_CANCEL = "cascade-cancel"   // cancel siblings on failure
}

function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
    // §10.3 cross-pattern admissibility per workload class; pre-conditions per pattern × workload pair
```

**Acceptance criteria:**
1. `TopologyPattern` declares exactly six values whose serialized form matches C-CP-10 §10.1 verbatim: `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`. The kebab-case string literal is the contract surface (per §10.2 `TopologyDeclaration.pattern`).
2. `CascadePolicy` declares exactly three values whose serialized form matches C-CP-10 §10.2 `TopologyDeclaration.cascade_policy` verbatim: `pause`, `proceed`, `cascade-cancel`.
3. `is_admissible` returns `true` per C-CP-10 §10.3 cross-pattern admissibility annotations: `hierarchical-delegation` admissible at `software-engineering` and `research` workloads (scope-bounded recursion justified; fan-out cap 3 per parent); `decentralized-handoff` admissible at `pipeline-automation` per-stage-expert workflows (single-owner-at-a-time invariant); `parallelization` admissible at `research` breadth-search and `content-creation` A/B-variant generation (cap 3–5). Patterns not carrying an explicit §10.3 annotation are admissible at their per-workload-class primary cells only (per C-CP-11 §11.1 commitment table); non-primary patterns are admissible but not primary per §10.3.
4. Taxonomy closed at cardinality 6 per C-CP-10 §10.1 (taxonomy closed at D4 §1.1); extension requires Workflow §4.1.2 Class-2 D4 revision.

**Tests:** `test_topology_pattern_cardinality_six`, `test_topology_pattern_values_match_spec_kebab_case`, `test_cascade_policy_cardinality_three`, `test_cascade_policy_values_match_spec`, `test_hierarchical_delegation_admissible_swe_research`, `test_decentralized_handoff_admissible_pipeline_automation`, `test_parallelization_admissible_research_content_creation`, `test_taxonomy_closed`.

**Rollback boundary:** Revert `TopologyPattern` + `CascadePolicy` enums + admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose topology discriminator; sub-agent dispatch loses pattern selection.

---

## Change summary (what was absorbed)

| Element | Before (retired) | After (canonical C-CP-10 §10.1 / §10.2 / §10.3) |
|---|---|---|
| `TopologyPattern` values | `SINGLE_AGENT`, `SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`, `RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES` | `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization` |
| `CascadePolicy` values | `COMPLETE_ALL`, `CANCEL_ON_FIRST_FAIL`, `PAUSE_ON_FIRST_FAIL` | `pause`, `proceed`, `cascade-cancel` (canonical §10.2 `TopologyDeclaration.cascade_policy`) |
| AC3 admissibility | Fabricated 4-workload matrix using retired pattern names | Canonical §10.3 three-pattern annotation (hierarchical-delegation / decentralized-handoff / parallelization) |
| `is_admissible` doc-comment | `§10.2 admissibility predicate` | `§10.3 cross-pattern admissibility per workload class` (corrected §-anchor) |
| AC2 / AC4 §-citations | `§10.3` for CascadePolicy | `§10.2` for CascadePolicy; `§10.1` for taxonomy closure |
| Tests | `test_admissibility_per_workload_class_match_spec`, `test_pipeline_stages_pipeline_only`, `test_cascade_policy_cardinality_three` | Renamed/added to the canonical three-pattern admissibility set + kebab-case value-match tests |

Notes:
- Enum **type names** (`TopologyPattern`, `CascadePolicy`) are unchanged — downstream units (U-CP-23, U-CP-24,
  U-CP-25, U-CP-30 et al.) reference them by type identifier. Only the **member set / serialized values** change,
  matching the canonical spec's string-literal contract surface.
- The traceability matrix at plan lines 3447–3449 still carries the §10.2/§10.3 label swap; not corrected here
  (out of scope — see follow-up observation 1).
