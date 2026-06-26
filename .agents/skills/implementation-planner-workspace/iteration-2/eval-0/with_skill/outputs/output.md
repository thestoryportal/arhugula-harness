# Revision-Pass Deliverable — U-CP-22 absorption of Tension 002 resolution

**Mode:** Revision-pass (implementation-planner SKILL.md §1, §8).
**Target plan:** `design-substrate/Implementation_Plan_Control_Plane_v2_1.md`, unit `U-CP-22`.
**Revision trigger:** Phase-7 `Class_N_Tension` resolution — Tension 002. Canonical `TopologyPattern` vocabulary is the spec **C-CP-10 §10.1** taxonomy: `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`.
**Constraint:** No repository file modified. The corrected U-CP-22 content is delivered below; it is the content that would replace U-CP-22 in the plan file.

---

## 1. Change-note

| Field | Value |
|---|---|
| Scope | Absorb Tension 002 resolution into `U-CP-22`. Replace the fabricated SCREAMING_CASE `TopologyPattern` member names with the canonical C-CP-10 §10.1 six-value string-literal vocabulary. Re-align acceptance criteria and tests to that vocabulary. Correct the §-citation drift in acceptance criteria 2 and 3 (see §3 findings). |
| Sections preserved verbatim | All units other than `U-CP-22`. The unit's `Implements`, `Depends on`, `Inputs`, and `Files affected` lines are preserved verbatim — only `Signatures`, `Acceptance criteria`, `Tests`, and `Rollback boundary` member-name references change. |
| Sections revised | `U-CP-22` only — `Signatures` block, `Acceptance criteria` (1, 2, 3), `Tests`, `Rollback boundary`. |
| Coverage matrix delta | None. `U-CP-22` continues to cover C-CP-10 §10.1 / §10.2 / §10.3 (matrix rows at plan §[coverage] `§10.1 TopologyPattern 6-class enum → U-CP-22`, `§10.2 admissibility predicate → U-CP-22`, `§10.3 CascadePolicy 3-class enum → U-CP-22`). See finding F-2 — those matrix row *labels* are themselves mis-cited and flagged, but no cell mark changes. |
| Dependency graph delta | None. `U-CP-22` remains `Depends on: (none)`; it remains an L0 foundational unit. No edge added or removed. Acyclic invariant unaffected. |
| Status posture | `Status: Proposed` (preserved until P6-CK / tension-clearance per SKILL.md §8). |

---

## 2. Revised unit — U-CP-22 (proposed replacement content)

> #### U-CP-22 — Declare 6-pattern `TopologyPattern` enum + admissibility predicate
>
> **Implements:** [C-CP-10 §10.1, §10.2, §10.3]
>
> **Depends on:** (none)
>
> **Inputs:** None (foundational; substrate-supplying enum unit).
>
> **Files affected:** CP-axis topology pattern enum (logical: `topology-pattern-enum`); CP-axis topology admissibility predicate (logical: `topology-admissibility-predicate`).
>
> **Signatures:**
>
> ```
> enum TopologyPattern {
>   SINGLE_THREADED_LINEAR,    // "single-threaded-linear"  — sole agent owns full lifecycle
>   ORCHESTRATOR_WORKERS,      // "orchestrator-workers"    — lead decomposes; workers concurrent; lead synthesizes
>   DECENTRALIZED_HANDOFF,     // "decentralized-handoff"   — each agent owns until handoff; recipient owns post-handoff
>   HIERARCHICAL_DELEGATION,   // "hierarchical-delegation" — parent owns until delegation; child owns sub-task; recursion permitted
>   EVALUATOR_OPTIMIZER,       // "evaluator-optimizer"     — generator + evaluator(s) in loop until convergence
>   PARALLELIZATION            // "parallelization"         — independent agents on independent sub-tasks; aggregator merges
> }
> // Wire/manifest representation is the C-CP-10 §10.1 string literal shown in each comment;
> // the manifest TopologyDeclaration.pattern field (C-CP-10 §10.2) accepts exactly these six
> // string literals. Member-identifier casing is a stack-binding detail (Python 3.12 enum),
> // deferred to execution per SKILL.md §3.4; the spec-canonical surface is the string literal.
>
> function is_admissible(pattern: TopologyPattern, workload: WorkloadClass) -> bool
>     // §10.3 cross-pattern admissibility per workload class; pre-conditions per pattern × workload pair
> ```
>
> **Acceptance criteria:**
> 1. `TopologyPattern` declares exactly six values per C-CP-10 §10.1 verbatim — the string literals `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization`. No additional value; no renamed value.
> 2. The manifest-facing representation of each `TopologyPattern` value is the C-CP-10 §10.1 string literal; the six literals are exactly the admissible values of `TopologyDeclaration.pattern` per C-CP-10 §10.2.
> 3. `is_admissible` evaluates per C-CP-10 §10.3 cross-pattern admissibility: `single-threaded-linear` and the per-workload-class primary patterns are admissible at every workload class per the C-CP-11 §11.1 mapping; `hierarchical-delegation` admissible at `software-engineering` and `research` (scope-bounded recursion); `decentralized-handoff` admissible at `pipeline-automation` per-stage-expert workflows; `parallelization` admissible at `research` breadth-search and `content-creation` A/B-variant generation. Non-primary patterns are admissible-but-not-primary and MUST be accepted at the cells where §10.3 declares them admissible.
> 4. Taxonomy closed at cardinality 6; extension requires a Workflow §4.1.2 Class-2 D4 revision.
>
> **Tests:** `test_topology_pattern_cardinality_six`, `test_topology_pattern_string_literals_match_spec_10_1`, `test_admissibility_per_workload_class_match_spec_10_3`, `test_hierarchical_delegation_se_research_only`, `test_taxonomy_closed`.
>
> **Rollback boundary:** Revert the `TopologyPattern` enum + `is_admissible` admissibility predicate. All downstream D4 units (Cluster 4 + Cluster 5) lose the topology discriminator; sub-agent dispatch loses pattern selection.

---

## 3. Findings surfaced during absorption (NOT silently absorbed)

Per SKILL.md §2 / §4.2 / §10, the planner does not invent or extend a spec commitment. Two defects beyond Tension 002's stated scope surfaced while absorbing the resolution. They are surfaced as findings, not silently rewritten.

**F-1 — `CascadePolicy` enum in U-CP-22 is a spec extension (Class-1 finding).**
The v2_1 U-CP-22 declares an `enum CascadePolicy { COMPLETE_ALL, CANCEL_ON_FIRST_FAIL, PAUSE_ON_FIRST_FAIL }` cited to "C-CP-10 §10.3 verbatim". Verified against `Spec_Control_Plane_v1_2.md` (the canonical §10 body; v1_3 §10 is "preserved verbatim from v1.2"): **there is no `CascadePolicy` enum in C-CP-10, and §10.3 is the cross-pattern admissibility section, not a CascadePolicy declaration.** The spec's `cascade_policy` is a three-value *string-literal field* — `"pause" | "proceed" | "cascade-cancel"` — declared on `TopologyDeclaration` at C-CP-10 §10.2 and owned by **C-CP-17 §17.1.1**. The v2_1 `CascadePolicy` member names (`COMPLETE_ALL` etc.) match no spec value. This is a spec-extension / citation-fabrication defect (anti-pattern "Spec extension" + "Citation invention", SKILL.md §10).
Recommended routing: surface to operator; the fix is a plan-side correction (remove the fabricated `CascadePolicy` enum from U-CP-22; the `cascade_policy` string-literal field belongs to whichever unit implements C-CP-17 §17.1.1). The corrected U-CP-22 above therefore omits the `CascadePolicy` enum entirely rather than carry a fabricated one. Track in a `Phase_7_Class_N_Tension` record per `CLAUDE.md` §4.3.

**F-2 — §-citation drift in v2_1 acceptance criteria and the §[coverage] matrix labels.**
v2_1 acceptance criterion 2 cited "C-CP-10 §10.3 verbatim" for `CascadePolicy`; acceptance criterion 3 cited "§10.2 admissibility matrix". Per spec: §10.1 = taxonomy, §10.2 = workflow-definition surface declaration, §10.3 = cross-pattern admissibility. The v2_1 criteria invert §10.2 and §10.3. The corrected criteria above cite §10.2 for the workflow-surface representation and §10.3 for admissibility. The plan §[coverage] matrix row `§10.3 CascadePolicy 3-class enum → U-CP-22` carries the same mis-label and should be corrected to `§10.3 cross-pattern admissibility → U-CP-22` when F-1 is cleared. No coverage *cell* changes.

---

## 4. Sub-discipline verification (SKILL.md §4) on the revised U-CP-22

| Sub-discipline | Result |
|---|---|
| Atomicity (§3) | PASS — single coherent change (one enum + one predicate); single focused session; independently testable (`Depends on: (none)`); coherent rollback boundary. |
| Spec-traceability (§4.2) | PASS for the revised content — cites C-CP-10 by ID and §10.1 / §10.2 / §10.3. Pre-existing F-1 mis-citation removed, not preserved. |
| Dependency-awareness (§4.3) | PASS — `Depends on: (none)`; L0 foundational; graph remains acyclic; no edge delta. |
| Implementation-grade-detail (§4.4) | PASS — names the two logical files, the enum + predicate signatures, and testable acceptance criteria. No library/framework introduced. Member-casing flagged as stack-binding deferred to execution per §3.4. |
