# Class 1 Fork — U-RT-104 admissibility-keying mismatch + carrier-defaults divergence

**Status:** ✅ APPLIED-AS-READING-β + Q2=APPLIED-AS-(i) (operator AskUserQuestion 2026-05-28 ratified Q1=(β) defer-to-runtime + Q2=(i) SF-1 doc-only reframe). Closes fork doc PROPOSING → APPLIED. Spec v1.35 → v1.36 + plan v2.31 → v2.32 + SF-1 canonical-reading addendum + workspace `CLAUDE.md` §2.3 + §2.4 row bumps co-published 2026-05-28. U-RT-104 implementation resumes against reframed AC #11 + U-RT-106 NEW AC #4.
**Filed:** 2026-05-28 at U-RT-104 implementation arc open (Phase 2b L9-sedecies cluster, third unit in sequence; U-RT-102 + U-RT-103 already landed at worktree branch `worktree-phase-2b-u-rt-102-cli-scaffolding`).
**Filing site:** `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md`.
**Halt point:** U-RT-104 (`WorkflowManifestLoader`) — implementation NOT started. Loader file + test file NOT authored.

---

## §0. Summary

Two distinct findings surfaced at empirical orientation for U-RT-104 (`WorkflowManifestLoader`). One structurally blocks implementation as specified; one is doc/code drift catalogued as a real production gap. Both routed via this single fork doc per workspace precedent for paired Class 1 + Class 3 surface (see `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap.md]]` precedent).

**Finding A — Class 1 (structurally blocking).** Spec v1.35 §14.19.2 + SF-1 §3.3 + plan v2.31 §1.4 AC #11 all declare `(workload_class, engine_class)` admissibility against the "U-CP-16 candidate mapping". Empirically, `ENGINE_CLASS_CANDIDATES` at `harness-cp/src/harness_cp/engine_class_candidate.py:57` is keyed by `deployment_surface`, NOT `workload_class`. `WorkloadBindingSelectionInput` at `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:65-70` makes this canonical ("`deployment_surface` ... keys the U-CP-16 candidate-set lookup"). The YAML/TOML manifest does NOT carry `deployment_surface` — that lives at `RuntimeConfig.deployment_surface` (sourced from env / harness.toml / CLI via U-RT-103). The spec-declared `load(path: Path) -> WorkflowObject` signature has no config / deployment-surface input. AC #11 as written is structurally unimplementable at U-RT-104.

**Finding B — Class 3 (informational + production gap).** SF-1 §3.1 declares `engine_class` / `topology_pattern` / `layer_budgets` / `fallback_chain` / `hitl_placements` / `per_step_overrides` as "OPTIONAL". SF-1 §3.3 "Default" column lists `()` empty tuples + `FallbackChain.default()` + `{}` empty dict + `None` etc. for those fields. Empirically, the `WorkflowManifestEntry` Pydantic carrier at `harness-cp/src/harness_cp/workflow_manifest_entry.py:68-160` has NO defaults for any of those 6 fields. Per spec §14.19.4 invariant 6 ("loader does NOT inject defaults; absence passes None / omitted-kwarg to carrier; Pydantic carrier defaults apply OR validation rejects"), the carrier-required reading wins and SF-1 §3.1's "OPTIONAL" tag is documentation drift. Additionally, SF-1 §3.3's `fallback_chain` default cite `FallbackChain.default()` is a phantom — no `default()` method exists at `harness-cp/src/harness_cp/cross_family_fallback_chain.py:52` (verified via grep).

---

## §1. Finding A — admissibility-keying mismatch (Class 1)

### §1.1 Authority surface

| Artifact | §-cite | Verbatim claim |
|---|---|---|
| Runtime spec v1.35 | §14.19.2 row 7 | `ManifestAdmissibilityError` triggered by "`(workload_class, engine_class)` not in U-CP-16 candidate mapping" |
| SF-1 fork doc | §3.3 row 5 + §4.2 row 7 | "`workflow.engine_class` ... admissibility verified against U-CP-16 candidate mapping" |
| Runtime plan v2.31 | §1.4 AC #11 | "Admissibility check: `(workload_class, engine_class)` not in U-CP-16 candidate mapping raises `ManifestAdmissibilityError`" |

### §1.2 Empirical contradiction

| Code site | Verbatim | Implication |
|---|---|---|
| `harness-cp/src/harness_cp/engine_class_candidate.py:42-54` | `EngineClassCandidate.deployment_surface: DeploymentSurface` + `candidate_set: frozenset[EngineClass]` | Candidate mapping keyed by deployment_surface, NOT workload_class |
| `harness-cp/src/harness_cp/engine_class_candidate.py:57` | `ENGINE_CLASS_CANDIDATES: tuple[EngineClassCandidate, ...]` | 3-entry tuple per DeploymentSurface |
| `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:65-70` | `deployment_surface: DeploymentSurface` ... `"keys the U-CP-16 candidate-set lookup"` | Canonical doc-string on U-CP-16 keying |
| `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:117-126` | `_candidate_set_for(surface: DeploymentSurface)` | Lookup signature requires deployment_surface |

### §1.3 Why AC #11 is structurally unimplementable at v1.35 spec

`WorkflowManifestLoader.load(path: Path) -> WorkflowObject` has no config / deployment_surface argument. The YAML/TOML manifest body declared at SF-1 §3.1 + §3.2 does NOT include `deployment_surface` (deployment_surface belongs at `RuntimeConfig`, sourced through U-RT-103 `RuntimeConfigSource`). Without deployment_surface, the loader cannot perform the deployment-surface-keyed U-CP-16 admissibility check.

### §1.4 Adjacent observation supporting (β) as architect's intent

`is_topology_permitted_for_workload(topology: TopologyPattern, workload: WorkloadClass) -> bool` at `harness-cp/src/harness_cp/per_workload_class_topology.py:174` takes BOTH inputs from manifest (topology_pattern + workload_class), making AC #12 (topology admissibility) implementable cleanly at U-RT-104. This contrast suggests the architect deliberately authored a manifest-internal admissibility predicate for U-CP-22 because U-CP-16 admissibility CANNOT be performed without config. If so, the SF-1 + spec + plan ACs got the U-CP-16 cite shape wrong, and the intended design is **defer (deployment_surface, engine_class) admissibility to runtime** when config is bound.

### §1.5 Routing options

| Branch | Shape | Routing target | Cascade |
|---|---|---|---|
| (α) Widen signature | Amend spec §14.19.1 + plan §1.4 to `WorkflowManifestLoader.load(path, *, deployment_surface)` (or pass `RuntimeConfig`). Loader receives deployment_surface from caller (U-RT-106 supplies from `RuntimeConfigSource.load(...)`). AC #11 implementable as `engine_class in ENGINE_CLASS_CANDIDATES[deployment_surface].candidate_set`. | Spec v1.35 → v1.36 + plan v2.31 → v2.32 | Runtime plan U-RT-106 callsite passes `deployment_surface`. Production at `WorkflowManifestLoader.load(...)` signature change. NO cross-axis cascade (intra-runtime). |
| (β) Defer to runtime | Reframe AC #11 at U-RT-104: "engine_class is a valid EngineClass enum member" (covered by enum-validity check at AC #9). Full (deployment_surface, engine_class) admissibility lands at U-RT-106 one-shot when config is bound. Spec §14.19.4 invariant 2 (eager validation) gets a canonical-reading carve-out: "eager validation = enum + schema + step-uniqueness + workload-keyed topology; deployment-surface-keyed engine_class admissibility deferred to runtime caller per signature-without-config discipline". | Spec v1.35 → v1.36 (canonical-reading amendment at §14.19.2 row 7 + §14.19.4 invariant 2) + plan v2.31 → v2.32 (AC #11 reframe + U-RT-106 +AC carrying admissibility) | Runtime plan U-RT-106 +AC (engine_class admissibility at one-shot dispatch site). Spec §14.18.4 RT-FAIL-CLI-MANIFEST-ADMISSIBILITY emission relocates from U-RT-104 to U-RT-106. NO cross-axis cascade. |
| (γ) Author NEW (workload_class, engine_class) mapping | Treat the SF-1/spec cite as the AUTHORING of a workload-class-keyed mapping (NEW H_T design surface). Build NEW per-(workload_class) `EngineClassCandidate` table sibling to the deployment_surface-keyed one. | **X-AL-3 violation** — new H_T design surface at Phase 7 execution. Routes to design-phase ADR/spec back-flow. CP spec amendment authoring a new admissibility table. | CP spec + plan + impl. CXA may grow if the new mapping crosses axes. **NOT RECOMMENDED** — workspace already authored deployment_surface-keyed U-CP-16 at U-CP-17 (`workload_binding_engine_class_selection.py`); duplicating with workload-class keying is design churn. |

**Architect-leaning recommendation:** (β) defer-to-runtime — preserves spec §14.19.1 signature, aligns with the existing `is_topology_permitted_for_workload(topology, workload)` precedent, and matches the architecturally-sane reading that config-dependent checks belong at the config-bound caller.

---

## §2. Finding B — carrier-defaults divergence (Class 3 informational + production gap)

### §2.1 SF-1 §3.1 vs §3.3 vs carrier reality

| Manifest field | SF-1 §3.1 declares | SF-1 §3.3 "Default" column declares | Carrier reality at `workflow_manifest_entry.py:68-160` |
|---|---|---|---|
| `engine_class` | OPTIONAL | `(none — caller-supplied; no Pydantic default at v1.20 carrier)` ✓ self-consistent | NO default (required) ✓ matches §3.3 |
| `topology_pattern` | OPTIONAL | `(none — caller-supplied)` ✓ self-consistent | NO default (required) ✓ matches §3.3 |
| `layer_budgets` | OPTIONAL | `()` empty tuple | NO default (required) ✗ contradicts §3.3 |
| `fallback_chain` | OPTIONAL | `FallbackChain.default()` (per CP carrier default) | NO default + NO `FallbackChain.default()` method exists ✗ contradicts §3.3 + phantom cite |
| `hitl_placements` | OPTIONAL | `()` empty tuple | NO default (required) ✗ contradicts §3.3 |
| `per_step_overrides` | OPTIONAL | `{}` empty dict | NO default (required) ✗ contradicts §3.3 |

### §2.2 Spec §14.19.4 invariant 6 reading

> 6. **Default-supplying discipline.** Optional fields absent from manifest are passed through as `None` to `WorkflowManifestEntry` constructor; Pydantic carrier defaults apply OR validation rejects per carrier class discipline (no loader-side default-supplying that bypasses Pydantic).

This invariant + carrier reality combine to: absent-in-manifest → omit kwarg → Pydantic raises `ValidationError` for missing required field → loader maps to `ManifestSchemaError`. SF-1 §3.1's "OPTIONAL" tag is documentation drift; the operational reality is the 6 fields are REQUIRED.

### §2.3 `FallbackChain.default()` phantom cite

SF-1 §3.3 row `fallback_chain` cites `FallbackChain.default()` as the carrier-side default. Grep at `harness-cp/src/harness_cp/cross_family_fallback_chain.py:52-67` confirms ZERO `default()` method on the class. The cite is phantom.

### §2.4 Routing target

| Routing branch | Shape |
|---|---|
| (i) Reframe SF-1 §3.1 + §3.3 as documentation-only | Canonical-reading: SF-1 §3.1 "OPTIONAL" is aspirational shorthand for "MAY be omitted IF carrier extension lands at a future arc". Current carrier reality (required) wins. Phantom `FallbackChain.default()` cite at SF-1 §3.3 row strikes. Loader behavior unchanged: omit absent → Pydantic rejects → `ManifestSchemaError`. NO carrier extension. Class 3 informational doc-hygiene patch at SF-1 next revision. |
| (ii) Extend carrier with the SF-1 §3.3 defaults | Author `FallbackChain.default()` classmethod returning an empty fallback chain; add Pydantic defaults to `WorkflowManifestEntry` for `layer_budgets=()`, `hitl_placements=()`, `per_step_overrides={}`, `fallback_chain=FallbackChain.default()`. Keeps `engine_class` + `topology_pattern` required (per SF-1 §3.3 own annotations). CP spec v1.x + plan v2.x absorption owed. NOT trivially Class 3 — touches carrier surface. |

**Recommendation:** (i) doc-only reframe at SF-1 next revision; this is genuinely Class 3 informational once the Class 1 Finding A is routed. The loader implementation is unambiguous either way per invariant 6.

---

## §3. Operator surface

```
CLASS 1 FORK DETECTED — HALT PHASE 7 SUB-PHASE EXECUTION

Defect locus:
  Finding A — Runtime spec v1.35 §14.19.2 + SF-1 §3.3/§4.2 + Runtime plan v2.31 §1.4 AC #11
  Finding B — SF-1 §3.1 + §3.3 + plan §1.4 AC text vs WorkflowManifestEntry carrier

Defect description:
  A. (workload_class, engine_class) admissibility cite is wrong shape; actual mapping
     is (deployment_surface, engine_class) and deployment_surface is not at the
     manifest layer. AC #11 structurally unimplementable at U-RT-104 signature.
  B. SF-1 §3.1 OPTIONAL annotations + §3.3 default column drift from carrier reality;
     `FallbackChain.default()` cite is phantom. Doc/code drift.

Routing target:
  A — Spec v1.35 → v1.36 + Plan v2.31 → v2.32 (canonical-reading amendment)
      OR Spec §14.19.1 signature widening + Plan U-RT-104 AC #11 + U-RT-106 AC cascade
  B — SF-1 next revision (Class 3 informational doc-hygiene)
      OR CP spec/plan/impl carrier extension (if (ii) chosen)

Halt point:
  U-RT-104 implementation — `WorkflowManifestLoader` file + test file NOT authored.
  U-RT-102 + U-RT-103 already landed at worktree branch
  worktree-phase-2b-u-rt-102-cli-scaffolding (commits 176d262 + f129390).

Resumption requires:
  A — Operator ratification of (α) / (β) / (γ) + spec v1.36 + plan v2.32 publication.
  B — Disposition decision tied to A (if A picks β, B routes as (i) doc-only).

Operator decision required (Q1):
  (α) Spec §14.19.1 signature widening — load(path, *, deployment_surface)
  (β) Defer (deployment_surface, engine_class) admissibility to U-RT-106 [RECOMMENDED]
  (γ) Author NEW (workload_class, engine_class) admissibility table — X-AL-3 violation
  (δ) Re-classify finding A as Class 2 (operator decision between alternatives)
  (ε) Re-classify finding A as Class 3 (informational; non-blocking)

Operator decision required (Q2 — only relevant if Q1=α or Q1=β):
  Q2 disposition for Finding B:
    (i)  SF-1 next-revision doc-only reframe [RECOMMENDED if Q1=β]
    (ii) CP carrier extension + FallbackChain.default() authoring [larger arc]
```

---

## §4. Adjacent observations

(a) **`is_topology_permitted_for_workload(topology, workload)` precedent supports (β).** The U-CP-22 admissibility predicate was authored with BOTH inputs from the manifest layer, making AC #12 implementable cleanly at U-RT-104. Symmetric design intent would have authored a similar workload-keyed engine_class admissibility predicate if engine_class admissibility were meant to be load-time. The asymmetry — workload-keyed topology vs deployment_surface-keyed engine_class — is the architect's signal that engine_class admissibility is config-bound, not manifest-bound.

(b) **U-RT-103 RuntimeConfigSource already at worktree.** RuntimeConfig (and therefore deployment_surface) is loaded by U-RT-103 at `harness-runtime/src/harness_runtime/config_source.py` (landed in this same worktree branch at commit `f129390`). U-RT-106 caller has both config + workflow available at one-shot dispatch site — branch (β) is operationally feasible at U-RT-106's existing sequencing.

(c) **U-RT-104 AC #1-#10 + #12-#14 unaffected by Finding A.** AC #1 file-extension dispatch, AC #2 TOML dispatch, AC #3 unsupported-format error, AC #4 version field check, AC #5 parse error, AC #6/#7 closed-schema, AC #8 required-field check, AC #9 enum validation, AC #10 step-id uniqueness, AC #12 topology admissibility (workload-keyed), AC #13 eager validation, AC #14 idempotency are all unaffected — only AC #11 is structurally blocked. Cluster impact is bounded.

(d) **Plan §3(j) PR-per-cluster recommendation still holds.** Whichever routing chosen, U-RT-104 + U-RT-105 + U-RT-106 (..U-RT-109) can land in a single PR after spec/plan re-issue. Worktree branch `worktree-phase-2b-u-rt-102-cli-scaffolding` is durable; the halt is at U-RT-104 NEXT step, not mid-implementation rollback.

(e) **Pre-substantive empirical-verification discipline applied.** 25th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture — advisor consulted at empirical orientation, before any loader file or test file authored. Memory entry validates again: structurally-blocking cross-axis defects ARE catchable before implementation if and only if advisor is called BEFORE substantive work. Workspace pattern continues.

(f) **Memory-update candidate.** NEW pattern entry — Phase 7 scoping arc shape "Class 1 fork at empirical-orientation BEFORE substantive code, paired Class 3 informational at adjacent observation" replays the precedent at `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap.md]]` + `[[fork-h-t-cp-19-default-gate-level-spec-extension.md]]`. Catalogue at memory after operator ratification.

---

## §5. Sections of canonical artifacts to amend (if Q1=β + Q2=i recommended path ratified)

| Site | Amendment shape |
|---|---|
| Runtime spec v1.35 §14.19.2 row 7 `ManifestAdmissibilityError` | CANONICAL-READING AMENDMENT: trigger reframed from "`(workload_class, engine_class)` not in U-CP-16 candidate mapping OR `topology_pattern` not in U-CP-22 admissibility" → "`topology_pattern` not in U-CP-22 admissibility per `is_topology_permitted_for_workload(topology, workload)`". `(deployment_surface, engine_class)` admissibility deferred to runtime caller (U-RT-106). |
| Runtime spec v1.35 §14.19.4 invariant 2 (eager validation) | CANONICAL-READING AMENDMENT carve-out: "eager validation at `.load()` = schema + enum + step-uniqueness + workload-keyed topology admissibility. Deployment-surface-keyed engine_class admissibility deferred to runtime caller per signature-without-config discipline; runtime caller is required to perform admissibility before workflow execution." |
| Runtime spec v1.35 §14.18.4 | NEW row OR re-routing: `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` emission site relocates from U-RT-104 load-time to U-RT-106 dispatch-time when engine_class admissibility fails. |
| Runtime plan v2.31 §1.4 U-RT-104 AC #11 | REFRAME: "engine_class is a valid EngineClass enum member (covered by AC #9 enum-validity)" + REMOVE U-CP-16 admissibility check at U-RT-104. |
| Runtime plan v2.31 §1.6 U-RT-106 | EXTEND with NEW AC: "engine_class admissibility per (deployment_surface, engine_class) against `ENGINE_CLASS_CANDIDATES[config.deployment_surface].candidate_set` performed at one-shot dispatch site BEFORE `api.run(workflow, config)` invocation; failure raises `ManifestAdmissibilityError` mapped to `RT-FAIL-CLI-MANIFEST-ADMISSIBILITY` → exit code 2." |
| SF-1 fork doc §3.3 row 5 `engine_class` | CANONICAL-READING NOTE: U-CP-16 admissibility cite shape clarified — admissibility is `(deployment_surface, engine_class)` keyed (deployment_surface from RuntimeConfig); load-time check is enum-validity only. |
| SF-1 fork doc §3.1 + §3.3 "OPTIONAL"/"Default" columns | CANONICAL-READING NOTE: 4 of 6 fields' "OPTIONAL" annotations are aspirational; carrier reality requires them. Phantom `FallbackChain.default()` cite strikes. |

---

## §6. Sub-species catalogue

**Species 3 sub-species catalogue candidate.** Per Workflow v1.12 §7.4.7.2 species-3 (resolved-but-carry-stale-inherited) sub-species enumeration:

NEW sub-species candidate: **3.pre-substantive-empirical-orientation-surfaces-cross-artifact-divergence-against-production-code** — the carry text at SF-1 §3.3 + spec §14.19.2 was authored at SF-1 ratification + spec v1.35 publication (2026-05-28, this same session) without empirical verification at HEAD against `engine_class_candidate.py`. The divergence existed at SF-1/spec authoring time and was carried into plan v2.31 §1.4 AC #11 verbatim. Distinct from prior species-3 sub-species in that the carry is detected by Phase 7 implementer at empirical orientation BEFORE substantive code authoring (rather than after a downstream landing reveals it).

NEW adjacent finding catalogue candidate at species 4 (authoring-time stale carry per OD spec v1.18 §5): the SF-1 + spec + plan authoring arcs at the SAME SESSION 2026-05-28 carry the same defect three times without empirical verification. Same-session triple-carry is a strengthened form of species 4 — a "session-coherence drift" sub-species candidate where multiple sibling artifacts authored in the same session inherit each other's unverified claims.

Catalogue at memory after operator ratification + workflow doc revision (separate arc).

---

## §7. Status

**PROPOSING** — awaiting operator AskUserQuestion ratification per §3 Q1 + Q2.

| State | Owner |
|---|---|
| Fork doc | This file — filed at U-RT-104 implementation halt |
| U-RT-102 | LANDED at worktree commit `176d262` |
| U-RT-103 | LANDED at worktree commit `f129390` |
| U-RT-104 | HALTED at implementation-not-started |
| U-RT-105 through U-RT-109 | BLOCKED on U-RT-104 close |
| Spec v1.35 → v1.36 | NOT FILED — owed at routing ratification |
| Plan v2.31 → v2.32 | NOT FILED — owed at routing ratification |
| SF-1 next revision | NOT FILED — owed at Finding B routing |
| Cross-axis cascade | ZERO verified at fork doc filing (intra-runtime-axis per spec §14.19.6) |

---

*Filed by Phase 7 implementer at U-RT-104 halt point per skill `phase-7-back-flow-routing` §4. Awaits operator routing ratification before re-opening the implementation arc.*
