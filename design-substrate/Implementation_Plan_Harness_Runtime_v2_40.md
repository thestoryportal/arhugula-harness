# Implementation Plan — Harness Runtime — v2.40

*Delta over v2.39. v2.40 is a Class 1 fork resolution Reading (A) apply pass per `.harness/class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md` operator-ratified 2026-05-29 absorbing runtime spec v1.37 → v1.38 §14.19.4 invariant 2 canonical-reading amendment + production retirement of `_check_topology_admissibility` at the loader. Single-unit-body amendment at U-RT-104 retiring AC #12 (load-time topology admissibility check); runtime sub-agent-dispatch site (`sub_agent_dispatch.py:585`) becomes sole enforcement authority per spec v1.38 Reading A. Pattern-consistent extension of spec v1.36 → plan v2.32 Reading β precedent at U-RT-104 AC #11. ZERO new units; ZERO DAG topology change; ZERO cross-axis cascade per Q5=β. Unit count 109 UNCHANGED. v2.39 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

## §0 Change note (v2.39 → v2.40)

### §0.1 What changed

| Element | v2.39 | v2.40 |
|---|---|---|
| U-RT-104 AC #12 (load-time topology admissibility) | LANDED — production at `workflow_manifest_loader.py:212` invokes `_check_topology_admissibility`; test at `test_workflow_manifest_loader.py:344` asserts rejection. | **RETIRED at v2.40 per Reading A.** Production `_check_topology_admissibility` removed; call at `:212` dropped; import of `is_topology_permitted_for_workload` dropped. Runtime sub-agent-dispatch site (`sub_agent_dispatch.py:585`) becomes sole enforcement authority. Test flipped from rejection-assertion to acceptance-assertion + sibling test added covering `(RESEARCH, SINGLE_THREADED_LINEAR)`. |
| U-RT-104 AC count | 14 ACs | **13 ACs** (AC #12 retired; AC #1-#11 + #13-#14 preserved verbatim) |
| §1 unit count | 109 | 109 (UNCHANGED) |
| §2 DAG | UNCHANGED | UNCHANGED |
| H_T-RT-35 transit framing | STAYS PARTIAL post-v2.39 plan-doc + 5 upstream blockers | UNCHANGED — STAYS PARTIAL per v2.39 §0.1 framing; topology admissibility deferral is intra-U-RT-104 scope, not a §16.5 composer arc transit |
| CXA v2.16 → v2.17 transit | 6 PENDING → 1 LANDED + 5 carry per v2.38 | UNCHANGED — ZERO CXA transit at v2.40 (topology admissibility is not a §16.5 composer surface) |

### §0.2 Scope discipline

§0 (this change note); §1 U-RT-104 unit-body canonical-reading amendment retiring AC #12; §2 DAG preservation (ZERO edge changes); §3 adjacent observations + carry-forward; §4 filing footer. All v2.39 + v2.38 + ... + v1 lineage PRESERVED VERBATIM per delta-only-plan-chain convention except: (a) U-RT-104 AC #12 RETIRED; (b) §3 (j) extended with 56th advisor application narrative.

### §0.3 Authoring rationale + the v2.40 reframing

Use-the-product probe finding #14 (PR #80) catalogued the structural inconsistency: `is_topology_permitted_for_workload` enforced at load-time at the YAML/TOML loader but not uniformly at runtime — only at sub-agent dispatch (`sub_agent_dispatch.py:585`). Single-step workflows that don't dispatch sub-agents (e.g., `INFERENCE_STEP`) escape the runtime check entirely; integration test `test_ac1_real_anthropic_single_step_succeeds` empirically demonstrates `(SOFTWARE_ENGINEERING, SINGLE_THREADED_LINEAR)` runs successfully via Protocol-conformant bypass.

Reading A operator-ratified 2026-05-29: defer load-time admissibility check to runtime authority. Pattern-consistent extension of v1.36 Reading β (engine_class admissibility loader → U-RT-106). Loader becomes purely a schema-validation surface; admissibility (both axes) is runtime-authoritative.

Q-set ratification: Q1=A (defer-to-runtime); Q2=α (fixture switches to `pipeline-automation` + `single-threaded-linear` — handled at PR #79 apply arc); Q3=i (sole enforcement at site #585); Q4=c (runtime spec amendment); Q5=β (runtime spec + plan cascade only — no CP spec amendment owed; matrix design-intent at C-CP-22 §11.1 preserved verbatim).

## §1 U-RT-104 unit-body amendment

| Field | v2.39 | v2.40 |
|---|---|---|
| Implements | runtime spec v1.36 §14.19 C-RT-30 WorkflowManifestLoader (canonical-reading amendment at §14.19.4 invariant 2 + §14.19.2 row 7) | **runtime spec v1.38 §14.19 C-RT-30 WorkflowManifestLoader** (canonical-reading amendment at §14.19.4 invariant 2 retiring topology admissibility from load-time scope; spec body PRESERVED VERBATIM) |
| Files | `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` + 7 typed exception subclasses (preserved verbatim) | UNCHANGED |
| Signatures | `WorkflowManifestLoader.load(path: Path) -> WorkflowManifest` + `_check_step_id_uniqueness(...)` + ~~`_check_topology_admissibility(...)`~~ + `_check_version(...)` + `_build_carrier(...)` | **`_check_topology_admissibility(...)` RETIRED at v2.40.** Other signatures PRESERVED VERBATIM. Import of `is_topology_permitted_for_workload` at line 42-44 RETIRED. |
| Depends on | enum-validity carriers (TopologyPattern, WorkloadClass, EngineClass, PersonaTier, GateLevel, ModelBinding, BlastRadiusTier) + WorkflowManifest Pydantic carrier | UNCHANGED |
| AC #12 (load-time topology admissibility) | Loader calls `is_topology_permitted_for_workload(topology, workload)` post-`_build_carrier`; raises `ManifestAdmissibilityError` with `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` on rejection. | **RETIRED at v2.40.** Per spec v1.38 Reading A. Loader no longer invokes the predicate. Runtime sub-agent-dispatch site (`sub_agent_dispatch.py:585`) is sole enforcement authority. |
| AC #1-#11 + #13-#14 | PRESERVED VERBATIM | PRESERVED VERBATIM |
| Test names | `test_topology_pattern_not_admissible_for_workload_raises_admissibility_error` (asserted load-time rejection) | **RETIRED.** Replaced with two NEW tests: `test_topology_pattern_admissibility_deferred_to_runtime_per_v1_38_reading_a` (asserts `(SOFTWARE_ENGINEERING, SINGLE_THREADED_LINEAR)` loads successfully) + `test_topology_pattern_admissibility_deferred_for_research_workload` (asserts `(RESEARCH, SINGLE_THREADED_LINEAR)` loads successfully). Both combos are matrix-impermitted per C-CP-22 §11.1 but now accepted at load-time per Reading A. |

## §2 DAG preservation

ZERO node addition / removal. ZERO edge addition / removal. v2.39 DAG PRESERVED VERBATIM.

## §3 Adjacent observations + carry-forward

(a) **v1.36 Reading β precedent extended.** v1.36 deferred engine_class admissibility (U-RT-104 AC #11 reframed to enum-validity only; U-RT-106 NEW AC). v1.38 defers topology_pattern admissibility (U-RT-104 AC #12 RETIRED; sub-agent-dispatch site is the runtime authority — no NEW unit owed because sub_agent_dispatch.py:585 was already the runtime authority pre-v1.38; the load-time check was redundant defense-in-depth). Both deferrals follow the same architectural principle: loader is schema-validation; runtime is admissibility authority.

(b) **MVP-scope SE-workload runnability closed.** SE workload's matrix-permitted topologies `{EVALUATOR_OPTIMIZER, ORCHESTRATOR_WORKERS}` are both unmaterialized at C-CP-25 v1.4 MVP. Pre-v1.38: SE workflows structurally unrunnable via YAML/TOML manifest path. Post-v1.38: SE workflows with `SINGLE_THREADED_LINEAR` topology load + run successfully (runtime enforces shape constraints only where they apply — at sub-agent dispatch, which a single-step workflow never reaches). Closes probe findings #5 + #6 + #14 from PR #79 §4(a) catalogue.

(c) **Test-bypass-as-runtime-truth pattern catalogued.** Integration test `test_ac1_real_anthropic_single_step_succeeds` empirically demonstrated runtime acceptance differs from loader strictness. Per workspace pattern `[[verification-shape-sharpened-grep-vs-e2e]]`: integration tests are higher authority for runtime correctness; loader's stricter check at v1.36 was design-time hygiene that did not match runtime authority. v2.40 absorbs the reading at the plan layer. NEW pattern catalogued at fork doc §4(e).

(d) **ManifestAdmissibilityError class preserved in taxonomy.** Per v1.36 Reading β, the class is still used at CLI app (`harness-runtime/src/harness_runtime/cli/app.py:110-115`) for engine_class admissibility at U-RT-106 dispatch site. v1.38 + v2.40 retire the LOAD-TIME use of the class at the loader; the class itself stays in the typed-exception taxonomy at §14.19.2 row 7.

(e) **ZERO cross-axis cascade per Q5=β.** Intra-runtime-spec amendment. CP spec C-CP-22 §11.1 PRESERVED VERBATIM (matrix design-intent unchanged). CP plan PRESERVED VERBATIM (U-CP-22 admissibility predicate signature + body unchanged). AS / OD / IS / CXA / ADR / ADD / PRD PRESERVED VERBATIM.

(j) **56th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture.** Pre-substantive advisor consultation 2026-05-29 caught: (1) apply order — PR #80 first (smaller blast radius) then PR #79 (larger); (2) Q-set ratification record discipline (write Q1-Q5 into fork doc Status block, not just "Reading A"); (3) apply-PR shape (sequential separate PRs per fork). Empirical pyyaml-shim feasibility check (78 LOC; 10/10 tests pass) pre-positioned PR #79 apply per advisor's most-discriminating-single-check recommendation. All 3 surfaced gaps closed pre-code; ZERO false-starts.

(k) **NEW pattern catalogued — `landed-ac-retired-via-spec-amendment`.** First explicit instance at this workspace where a LANDED atomic-unit acceptance criterion is RETIRED via downstream spec amendment (not via implementation-time STRIKE pattern at v2.35-v2.38). Distinct from species 2 `strike-revision-on-refined-second-tier-reason` (workflow v1.13 §7.4.7.2 species-2 sub-species) — operates on retirement via deferral-to-existing-runtime-authority, not on revised STRIKE narrative. Sub-species candidate at workflow §7.4.7.2 — `4.ac-retired-via-spec-deferral-to-existing-runtime-authority`. Cardinality 1; await second instance before workflow-doc revision.

## §4 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.40 (delta over v2.39) |
| Authored at | 2026-05-29 |
| Authoring authority | runtime spec v1.38 §14.19.4 invariant 2 canonical-reading amendment + Reading A operator ratification at fork doc Status block (`.harness/class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md`) |
| Net delta | U-RT-104 AC #12 RETIRED; AC count 14 → 13; ZERO new unit; ZERO DAG change; ZERO cross-axis cascade |
| Production binding | Co-published this arc: `harness-runtime/.../workflow_manifest_loader.py` — drop import + drop call + retire method. Tests updated at `test_workflow_manifest_loader.py`. 1301/1301 harness-runtime + 794/794 harness-cp tests pass. |
| Cross-axis cascade | NONE per Q5=β. CP spec C-CP-22 §11.1 PRESERVED VERBATIM. |
| Downstream artifacts owed | workspace `CLAUDE.md` §2.3 + §2.4 row bumps (runtime spec v1.37 → v1.38; runtime plan v2.39 → v2.40) — co-published this arc; fork doc Status PROPOSING → ✅ APPLIED-AS-READING-A — co-published this arc; clearance marker at `.harness/clearance/Spec_Harness_Runtime-v1_38-cleared-2026-05-29.md` per CLAUDE.md §4.5 — co-published this arc |
