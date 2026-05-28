# Implementation Plan — Harness Runtime (v2.32)

*Delta over v2.31. v2.32 is a Class 1 fork resolution Reading (β) apply pass per `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md` Q1=(β) defer-to-runtime + Q2=(i) doc-only operator-ratified 2026-05-28. Single-arc absorption of runtime spec v1.35 → v1.36 canonical-reading amendment at §14.19.2 row 7 + §14.19.4 invariant 2 + §14.18.4 emission-site relocation. ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade per spec §14.19.6.*

## §0 Change note (v2.31 → v2.32)

### §0.1 Revision context — admissibility-keying mismatch resolution

Per `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md` filed 2026-05-28 at U-RT-104 implementation halt + operator AskUserQuestion 2026-05-28 ratification of Q1=(β) defer-to-runtime + Q2=(i) doc-only. Empirical orientation at U-RT-104 implementation arc surfaced that the v2.31 §1.4 AC #11 admissibility cite `(workload_class, engine_class) U-CP-16 candidate mapping` is structurally unimplementable at the spec-declared `load(path: Path) -> WorkflowObject` signature — `ENGINE_CLASS_CANDIDATES` at `harness-cp/src/harness_cp/engine_class_candidate.py:57` is keyed by `deployment_surface` (not `workload_class`), and `deployment_surface` lives at `RuntimeConfig` (not at the YAML/TOML manifest body).

Reading (β) reframes AC #11 at U-RT-104 to enum-validity only (already covered by AC #9) + lands the deployment-surface-keyed engine_class admissibility check at U-RT-106 NEW AC #N when `RuntimeConfig.deployment_surface` is bound. Architecturally-symmetric with the existing `is_topology_permitted_for_workload(topology, workload)` pattern at `harness-cp/src/harness_cp/per_workload_class_topology.py:174` — manifest-internal admissibility predicates take manifest-internal inputs only; config-dependent checks belong at the config-bound caller.

### §0.2 Sections revised

§0 (this change note); §1 U-RT-104 AC #11 single-unit-body canonical-reading amendment; §2 U-RT-106 single-unit-body NEW AC absorption; §3 adjacent observations. All v2.31 unit bodies PRESERVED VERBATIM at sites §1.2 (U-RT-102) + §1.3 (U-RT-103) + §1.5 (U-RT-105) + §1.7 (U-RT-107) + §1.8 (U-RT-108) + §1.9 (U-RT-109) per delta-only-plan-chain convention. Cluster framing at §1.1 PRESERVED VERBATIM. DAG at §2 PRESERVED VERBATIM. v2.30 + v2.29 + ... + v1 lineage PRESERVED VERBATIM.

### §0.3 ZERO cross-axis cascade

Per spec v1.36 §14.19.6 re-verified at v2.32 publication: intra-runtime-axis. NO CP / AS / OD / IS / CXA / ADR / ADD / PRD plan or spec amendment owed. Workspace `CLAUDE.md` §2.3 runtime spec row + §2.4 runtime plan row bumps owed at v2.32 publication (sibling co-publication this arc).

---

## §1 U-RT-104 AC #11 canonical-reading amendment

### §1.1 Site

Runtime plan v2.31 §1.4 U-RT-104 Acceptance criteria #11 (line ~144):

> 11. Admissibility check: `(workload_class, engine_class)` not in U-CP-16 candidate mapping raises `ManifestAdmissibilityError`

### §1.2 Amendment

CANONICAL-READING AMENDMENT at v2.32 — body text at v2.31 §1.4 AC #11 PRESERVED VERBATIM; canonical interpretation at v2.32 reframes the AC scope:

> 11. **REFRAMED at v2.32 (Reading β).** Enum-validity check: `engine_class` value MUST parse as a valid `harness_cp.engine_class.EngineClass` enum member (covered by AC #9 enum-strictness invariant). Deployment-surface-keyed admissibility check (`engine_class in ENGINE_CLASS_CANDIDATES[deployment_surface].candidate_set`) is DEFERRED to U-RT-106 one-shot dispatch site per spec v1.36 §14.19.2 row 7 + §14.19.4 invariant 2 carve-out. Effectively merges with AC #9 at U-RT-104 scope — no separate implementation work owed at U-RT-104 for AC #11 beyond AC #9 enum-validity.

**Tests-line absorption at U-RT-104.** The v2.31 test `test_admissibility_check_workload_class_engine_class_not_in_u_cp_16` (per v2.31 §1.4 Tests line) REFRAMES to `test_engine_class_invalid_enum_value_raises_manifest_enum_value_error` — coverage-equivalent to AC #9's existing enum-validity test. Net test cardinality at U-RT-104 unchanged (14 ACs map to 14 tests + 5 fixture-driven valid manifests).

### §1.3 Files-line at U-RT-104

PRESERVED VERBATIM. The loader at `harness-runtime/src/harness_runtime/lifecycle/workflow_manifest_loader.py` performs enum-validity at AC #9 coverage; ZERO `ENGINE_CLASS_CANDIDATES` import owed at U-RT-104. The U-CP-22 admissibility surface (`is_topology_permitted_for_workload`) at AC #12 remains imported as v2.31 specified.

---

## §2 U-RT-106 NEW AC — deployment-surface-keyed engine_class admissibility at dispatch site

### §2.1 Site

Runtime plan v2.31 §1.6 U-RT-106 (one-shot mode body — `harness run <file>` synchronous invocation). v2.31 declared 7 ACs; v2.32 extends to 8 ACs with NEW AC #N (slotting at #4 sibling to existing config-load + manifest-load ACs per v2.31 sequencing — see §2.3 below for v2.31 numbering reference).

### §2.2 NEW AC #4 (slots after manifest-load AC) — admissibility check at dispatch site

> 4. **NEW at v2.32.** After `RuntimeConfigSource.load(...)` returns `config` AND `WorkflowManifestLoader.load(path)` returns `workflow`, BEFORE invoking `harness_runtime.api.run(workflow, config)`: verify `workflow.manifest_entry.engine_class in harness_cp.engine_class_candidate.ENGINE_CLASS_CANDIDATES[config.deployment_surface].candidate_set`. If admissibility fails, raise `harness_runtime.lifecycle.workflow_manifest_loader.ManifestAdmissibilityError` carrying `(deployment_surface, engine_class, candidate_set)` context. Map to `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` at the CLI layer per spec v1.36 §14.18.4 → exit code 2.

### §2.3 v2.31 AC renumbering at U-RT-106

v2.31 §1.6 U-RT-106 AC sequence (7 ACs): config-load → manifest-load → dispatch → exit-code-success → exit-code-failure → SIGINT-drain → output-format. v2.32 inserts the NEW admissibility-check AC at position #4 (sibling to config + manifest load; before dispatch). v2.31 ACs #4–#7 renumber to #5–#8 at v2.32 canonical reading. Body text at v2.31 §1.6 ACs PRESERVED VERBATIM; canonical reading at v2.32 maps the renumbering.

### §2.4 Tests-line at U-RT-106

v2.31 §1.6 Tests-line PRESERVED VERBATIM; NEW test owed at v2.32 implementation arc:

- `test_engine_class_not_admissible_for_deployment_surface_raises_admissibility_error` — fixture: manifest with `engine_class=RECONCILER_LOOP`, config with `deployment_surface=LOCAL_DEVELOPMENT` (RECONCILER_LOOP excluded per §7.2 "requires K8s control plane"); assert `ManifestAdmissibilityError` raised + exit code 2 + fail-class `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` echoed.

### §2.5 Files-line at U-RT-106

v2.31 PRESERVED VERBATIM. The dispatch-site admissibility check lives at `harness-runtime/src/harness_runtime/cli/app.py` `@app.command("run")` body (replacing the U-RT-102 stub) per v2.31 §1.6 Signatures line. NEW import `from harness_cp.engine_class_candidate import ENGINE_CLASS_CANDIDATES` at the CLI body.

---

## §3 Adjacent observations + carry-forward

(a) **U-RT-102 + U-RT-103 PRESERVED VERBATIM.** Already LANDED at worktree branch `worktree-phase-2b-u-rt-102-cli-scaffolding` (commits `176d262` + `f129390`). ZERO amendment owed at v2.32. v2.31 §1.2 + §1.3 unit bodies PRESERVED VERBATIM.

(b) **U-RT-105 + U-RT-107 + U-RT-108 + U-RT-109 PRESERVED VERBATIM at v2.32.** Unit bodies at v2.31 §1.5 + §1.7 + §1.8 + §1.9 unchanged. The admissibility relocation only affects U-RT-104 (load-time scope reduction) + U-RT-106 (dispatch-time +1 AC). Downstream units unaffected per spec v1.36 §14.19.6 ZERO cross-axis cascade + intra-cluster scope analysis.

(c) **Plan §3(j) PR-per-cluster recommendation PRESERVED.** Worktree branch durable; U-RT-104 implementation resumes post-publication; full 8-unit cluster lands at single PR per v2.31 §3(j) precedent (mirrors L9-decies through L9-quindecies cluster shapes).

(d) **Fork doc `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md` Status PROPOSING → ✅ APPLIED-AS-READING-β + Q2=APPLIED-AS-(i)** at v2.32 publication. Sub-species 3 candidate `3.pre-substantive-empirical-orientation-surfaces-cross-artifact-divergence-against-production-code` catalogued at fork doc §6 — memory entry owed at follow-on arc per `[[fork-h-t-cp-19-default-gate-level-spec-extension]]` precedent.

(e) **SF-1 fork doc canonical-reading note owed.** `.harness/class_1_fork_harness_run_yaml_manifest_schema.md` §3.3 row 5 + §4.2 row 7 admissibility cite shape clarification (Finding A); §3.1 + §3.3 OPTIONAL/Default columns canonical-reading note + phantom `FallbackChain.default()` cite strike (Finding B + Q2=(i)). Co-published this arc.

(f) **Workspace `CLAUDE.md` §2.3 + §2.4 row bumps owed.** Runtime spec row v1.35 → v1.36; runtime plan row v2.31 → v2.32. Co-published this arc.

(g) **ZERO retirement event filing at this arc.** No `H_T-*` retirement-tier transit at fork resolution; AS-8d + OD-5 RETIRE-READY status preserved at batch-28 disposition per existing `[[fork-webhook-composer-per-workflow-context-threading]]` close discipline.

(h) **25th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Pre-substantive advisor consultation at U-RT-104 implementation arc empirical orientation caught the structural-blocking defect BEFORE any loader code authored. Memory posture continues to validate operationally; defect-detection-at-empirical-orientation is the workspace-canonical discipline for Phase 7 implementer arcs.

(i) **Same-session triple-carry pattern observed.** SF-1 + spec v1.35 + plan v2.31 carry the same admissibility-keying defect three times in the SAME session (2026-05-28). Catalogue candidate at workflow v1.12 §7.4.7.2 species-4 (authoring-time stale carry) sub-species column — "session-coherence drift" sub-species where multiple sibling artifacts in the same session inherit each other's unverified claims without independent empirical verification at HEAD. Workflow doc revision owed at separate arc per cross-catalogue scope discipline.

---

## §4 Filing footer

| State | Value |
|---|---|
| Document | `Implementation_Plan_Harness_Runtime_v2_32.md` (this file) |
| Authored | 2026-05-28, Phase 7 Phase 2b implementation arc |
| Authority | Operator AskUserQuestion 2026-05-28 Q1=(β) + Q2=(i) ratification of `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md` |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_31.md` (v2.31 — Phase 2a G5 NEW L9-sedecies cluster) |
| Successor consumption | U-RT-104 implementation resumes against reframed AC #11 + U-RT-106 NEW AC #4 |
| Cross-axis cascade | ZERO (intra-runtime-axis per spec v1.36 §14.19.6) |
| Unit count | 107 PRESERVED VERBATIM (no new units) |
| DAG | PRESERVED VERBATIM (no edge changes) |
| Test cardinality | NET +0 at U-RT-104 (rename) + NET +1 at U-RT-106 |
