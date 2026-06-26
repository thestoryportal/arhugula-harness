# Deliverable — U-CP-22 Revision-Pass Absorption (Tension 002)

**Skill mode:** `implementation-planner` SKILL.md §8 revision-pass sub-mode. Trigger: a specification revision (Tension 002 resolution to the canonical C-CP-10 §10.1 `TopologyPattern` vocabulary) requires plan absorption at U-CP-22.

**Scope discipline (SKILL.md §2):** the plan absorbs the resolved spec contract; it does not extend it. Per the constraint, no repository file is modified — the revised unit content is produced below as the deliverable.

---

## 1. Revision trigger

Tension 002 is resolved. The canonical `TopologyPattern` enum is now the spec **C-CP-10 §10.1** six-pattern taxonomy verbatim:

`single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`

The U-CP-22 unit currently filed in `design-substrate/Implementation_Plan_Control_Plane_v2_1.md` (lines 1172–1212) declares an **obsolete** enum vocabulary (`SINGLE_AGENT`, `SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`, `RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES`). That vocabulary does not match the canonical spec §10.1 names and must be absorbed.

---

## 2. Change-note (SKILL.md §8.3)

### 2.1 Scope of revision

| Item | Disposition |
|---|---|
| Affected unit | **U-CP-22** only |
| Trigger | Tension 002 resolution — canonical `TopologyPattern` vocabulary = C-CP-10 §10.1 six-pattern taxonomy verbatim |
| Nature | Vocabulary absorption: enum identifiers + acceptance criteria re-aligned to the canonical §10.1 names and the §10.3 admissibility annotations. No new units, no new contracts, no new dependencies, no spec extension. |
| New architectural commitments | None |

### 2.2 Affected-unit identification (SKILL.md §8.2)

- **Coverage matrix:** §4.1.10 maps C-CP-10 §10.1 / §10.2 / §10.3 to U-CP-22 (sole covering unit). No other unit covers C-CP-10.
- **Dependency graph (downstream consumers of `TopologyPattern` enum, one hop):** U-CP-23, U-CP-25, U-CP-40, U-CP-43 (cross-axis), U-CP-50, U-CP-52 reference `TopologyPattern` enum (U-CP-22) as an *input*. They consume the enum by reference and do not re-declare its values, so the vocabulary change is contained at U-CP-22. **No substantive edit propagates to consumer units.** Consumer units' prose that names specific patterns (e.g. U-CP-23's per-workload commitment table) already uses the canonical spec §10.1 / §11.1 vocabulary and is unaffected. This is logged as a coherence-pass observation, not a delta.

### 2.3 Sections preserved verbatim

All U-CP-22 sub-sections **except** the `Signatures` block, `Acceptance criteria` #1 and #3, and `Tests` are preserved verbatim from v2.1: `Implements:`, `Depends on:`, `Inputs:`, `Files affected:`, `Acceptance criteria` #2 and #4, `Rollback boundary:`.

### 2.4 Sections revised

| Sub-section | Revision |
|---|---|
| `Signatures` — `TopologyPattern` enum | Six obsolete uppercase identifiers replaced with the canonical C-CP-10 §10.1 names (kebab-case string-valued, mirroring the spec §10.1 backtick form and the §10.2 `TopologyDeclaration.pattern` literal union). |
| `Acceptance criteria` #1 | Citation unchanged; values re-stated to the canonical §10.1 six-name vocabulary verbatim. |
| `Acceptance criteria` #3 | `is_admissible` admissibility statement re-derived from spec **§10.3 "Cross-pattern admissibility per workload class"** verbatim, replacing the obsolete-vocabulary admissibility prose. |
| `Tests` | Test names that embedded obsolete pattern identifiers renamed to the canonical vocabulary. |

### 2.5 Coverage-matrix delta

§4.1.10 row labels reference sub-section IDs, not pattern identifiers — **no coverage-matrix edit required**. The row label `§10.3 CascadePolicy 3-class enum` is a **pre-existing defect**, not introduced or corrected by this pass — see §4 Findings.

### 2.6 Dependency-graph delta

None. U-CP-22 remains `Depends on: (none)` (foundational substrate-supplying enum unit). Acyclic invariant unaffected.

---

## 3. Revised U-CP-22 unit (full unit content — deliverable)

```
#### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate

**Implements:** [C-CP-10 §10.1, §10.2, §10.3]

**Depends on:** (none)

**Inputs:** None (foundational; substrate-supplying enum unit).

**Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).

**Signatures:**

```
enum TopologyPattern {
  SINGLE_THREADED_LINEAR    = "single-threaded-linear"
  ORCHESTRATOR_WORKERS      = "orchestrator-workers"
  DECENTRALIZED_HANDOFF     = "decentralized-handoff"
  HIERARCHICAL_DELEGATION   = "hierarchical-delegation"
  EVALUATOR_OPTIMIZER       = "evaluator-optimizer"
  PARALLELIZATION           = "parallelization"
}

enum CascadePolicy {
  COMPLETE_ALL,                                       // wait for all siblings; aggregate
  CANCEL_ON_FIRST_FAIL,                               // cancel siblings on first failure
  PAUSE_ON_FIRST_FAIL                                 // pause workflow; route to HITL
}

function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
    // §10.3 cross-pattern admissibility per workload class; pre-conditions per pattern × workload pair
```

**Acceptance criteria:**
1. `TopologyPattern` declares exactly six values per C-CP-10 §10.1 verbatim: `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`. Each enum member's string value matches the spec §10.1 backtick spelling and the §10.2 `TopologyDeclaration.pattern` literal-union spelling exactly (kebab-case).
2. `CascadePolicy` declares exactly three values per C-CP-10 §10.3 verbatim.
3. `is_admissible` returns `true` per the §10.3 "Cross-pattern admissibility per workload class" annotations: `hierarchical-delegation` admissible at `software-engineering` and `research` workloads (scope-bounded recursion justified); `decentralized-handoff` admissible at `pipeline-automation` per-stage-expert workflows; `parallelization` admissible at `research` breadth-search and `content-creation` A/B-variant generation. The four primary-pattern × workload-class bindings (`software-engineering` → `evaluator-optimizer` / `orchestrator-workers`; `content-creation` → `evaluator-optimizer`; `pipeline-automation` → `single-threaded-linear` sequential default; `research` → `orchestrator-workers`) are admissible at their primary cells per §11.1. Non-primary patterns return `true` only at the cells §10.3 declares admissible; all other pattern × workload pairs return `false`.
4. Taxonomy closed at cardinality 6; extension requires Workflow §4.1.2 Class-2 D4 revision.

**Tests:** `test_topology_pattern_cardinality_six`, `test_topology_pattern_values_match_spec_10_1_verbatim`, `test_cascade_policy_cardinality_three`, `test_admissibility_per_workload_class_match_spec_10_3`, `test_hierarchical_delegation_se_research_only`, `test_decentralized_handoff_pipeline_only`, `test_parallelization_research_content_only`, `test_taxonomy_closed`.

**Rollback boundary:** Revert `TopologyPattern` + `CascadePolicy` enums + admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose topology discriminator; sub-agent dispatch loses pattern selection.
```

---

## 4. Findings surfaced (SKILL.md §2, §4.2 — not silently fixed)

The skill's atomic-decomposition discipline requires surfacing traceability gaps rather than inventing or silently patching them. Two pre-existing defects are visible at U-CP-22 and are **outside Tension 002 scope** — they are reported here for operator routing, not absorbed by this pass.

| # | Finding | Class |
|---|---|---|
| F-1 | **`§10.3 CascadePolicy` mis-citation.** U-CP-22 cites `C-CP-10 §10.3` for the `CascadePolicy` 3-class enum, and §4.1.10 coverage-matrix row labels §10.3 as "CascadePolicy 3-class enum". But spec C-CP-10 §10.3 is titled **"Cross-pattern admissibility per workload class"**. The spec §10 has only three sub-sections (§10.1 taxonomy, §10.2 workflow-definition surface declaration, §10.3 cross-pattern admissibility) — **there is no spec sub-section declaring a `CascadePolicy` enum**. The `cascade_policy` field appears in spec §10.2's `TopologyDeclaration` as a `"pause" \| "proceed" \| "cascade-cancel"` literal union, and cascade-policy *defaults* appear in §11.1. The `CascadePolicy` enum in U-CP-22's signatures (`COMPLETE_ALL` / `CANCEL_ON_FIRST_FAIL` / `PAUSE_ON_FIRST_FAIL`) traces to none of these and is a **spec-extension / mis-citation defect** (§4.2 trace-omission + §10 spec-extension anti-pattern). Routing: surface to operator; either re-anchor `CascadePolicy` to a verified spec contract or back-flow to Phase 5 if the enum is a genuine implementation surface the spec must commit. This pass left the §10.3 / `CascadePolicy` lines as filed (other than vocabulary) to avoid compounding the defect; absorbing it is a separate revision pass once the spec anchor is resolved. | 2 |
| F-2 | **`§10.2 admissibility predicate` mis-labelling.** U-CP-22's `Implements:` cites `§10.2` and §4.1.10 labels §10.2 "admissibility predicate", but spec §10.2 is "Workflow-definition surface declaration". The admissibility content lives at spec **§10.3**. The revised acceptance #3 above re-anchors `is_admissible` to §10.3 (the correct spec home for admissibility); the `Implements:` line and coverage-matrix label remain as filed pending the F-1 disposition since both findings touch the same §10.2/§10.3 mis-labelling and should be corrected in one coherent pass. | 3 |

Both findings predate Tension 002 and are not created by this revision. Per SKILL.md §2, the planner does not invent citation traces — F-1 in particular must route through operator decision before the coverage matrix and `Implements:` line can be corrected.

---

## 5. Coherence pass (SKILL.md §5 step 9)

- **Atomicity (§3):** U-CP-22 remains a single coherent change (one enum family + one predicate), single-session, independently testable, coherent rollback boundary. Unaffected by this pass.
- **Spec-traceability (§4.2):** Acceptance #1 and #3 now cite and quote canonical C-CP-10 §10.1 / §10.3 content verbatim. The §10.2 / §10.3 mis-citations are surfaced as F-1 / F-2, not silently corrected.
- **Dependency-awareness (§7):** `Depends on: (none)` preserved; acyclic invariant intact; no consumer-unit propagation.
- **Implementation-grade detail (§4.4):** Signatures and testable acceptance criteria retained; no library/framework introduced.
- **Status posture (§8):** `Status: Proposed` preserved — revision requires P6-CK clearance before status change.

---

## 6. Summary

U-CP-22's `TopologyPattern` enum absorbed the Tension 002 resolution: the six obsolete uppercase identifiers are replaced with the canonical C-CP-10 §10.1 vocabulary (`single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`), and acceptance criteria #1/#3 plus the test names are re-aligned to that vocabulary and the spec §10.3 admissibility annotations. Two pre-existing, out-of-scope citation defects (`CascadePolicy` enum spec-anchor, §10.2/§10.3 admissibility mis-label) are surfaced as findings F-1/F-2 for operator routing rather than silently patched.
