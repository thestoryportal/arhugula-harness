# Implementation Plan — Control Plane (v2.27)

*Delta over v2.26. v2.27 authors NEW singleton-cluster unit **U-CP-73** decomposing CP spec v1.23 → v1.24 NEW §28.10 `ValidatorPostEvaluateHook` Protocol surface per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified 2026-05-28 Q-set. Unit count 73 → **74**; +1 NEW unit at L4-within-axis (consumes existing ConcreteValidatorFramework at L3); ZERO new cluster (singleton extension at existing Cluster 10 ValidatorFramework substrate); ZERO DAG topology break; ZERO cross-axis cascade per Q5=β ratification.*

## §0 Change note (v2.26 → v2.27)

### §0.1 Revision context — NEW unit U-CP-73 authoring per X-AL-3 spec extension

Per CP spec v1.23 → v1.24 NEW §28.10 `ValidatorPostEvaluateHook` Protocol surface authoring (Class 1 fork resolution Reading (B) absorption per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` operator-ratified 2026-05-28 Q-set at U-OD-40 orientation arc AskUserQuestion): U-CP-73 decomposes the harness-cp impl scope into a single atomic unit covering Protocol declaration + ConcreteValidatorFramework ctor extension + post-evaluate firing site + 6 invariants enforcement + unit tests.

Trigger: U-OD-40 (cost-attribution at `validator.evaluate` site per OD spec v1.8 §C-OD-26.2 row "validator.evaluate") requires callback into harness-runtime cost-attribution helpers. Dep-graph constraint (harness-cp does NOT depend on harness-od) forecloses direct import. Operator ratified hook Protocol pattern (B) over factory decorator (A) at AskUserQuestion 2026-05-28.

Mirror precedent: U-RT-100 (L9-quindecies cluster at runtime plan v2.28) `SkillActivationSpanEmitter` + `SkillActivationHook` Protocol surface authoring shape; same operator-opt-in pattern; same `None` default preserves existing construction sites discipline.

### §0.2 Sections revised

§0 (this change note); NEW §2 unit body authoring at U-CP-73 (full template per CP plan v2.15 §2 pattern). All other unit bodies preserved verbatim from v2.26 per delta-only-plan-chain convention.

### §0.3 NEW unit U-CP-73 — ValidatorPostEvaluateHook Protocol surface authoring

See §2 for full unit body.

**Cluster placement:** Singleton-extension at existing Cluster 10 ValidatorFramework substrate. U-CP-73 sits at L4-within-axis depending on ConcreteValidatorFramework body at U-CP-58 (L0) + U-CP-59 (L1) + U-CP-60 (L2) + U-CP-61 (L3). NO new cluster created — singleton-extension under operator-opt-in RETIRE-READY pattern precedent (mirror runtime plan v2.20 L9-undecies single-cluster extension; runtime plan v2.28 L9-quindecies single-cluster extension).

### §0.4 Cross-axis dependency edges — preserved + 1 NEW intra-axis import

U-CP-73 cross-axis edges: NONE (per Q5=β ratification — Protocol declaration is intra-axis CP; factory binding is intra-axis runtime composition). U-CP-73 intra-axis imports: `harness_cp.validator_framework_types.ValidatorEvaluation` + `harness_cp.workflow_step_types.WorkflowStep` + `harness_cp.step_execution_context.StepExecutionContext` (Pattern-D intra-axis imports; no NEW cross-axis edge).

ZERO new CXA bucket touch; ZERO CP→AS / CP→IS / CP→OD / OD→CP edge change at canonical enumeration. CXA §0.4 convention-seam declaration NOT amended at this arc per Q5=β ratification.

### §0.5 DAG topology — additive at L4-within-axis

U-CP-73 sits at L4-within-axis Cluster 10 ValidatorFramework substrate depending on:

- U-CP-58 (L0 — `ValidatorOutcome` + `ValidatorFailClass` enums; `ValidatorResult` schema)
- U-CP-59 (L1 — `ValidatorEvaluation` envelope; `ValidatorNextAction` mapping)
- U-CP-60 (L2 — `Validator` Protocol; ValidatorRegistry mapping)
- U-CP-61 (L3 — `ConcreteValidatorFramework` body)

DAG verified acyclic at insertion: U-CP-73 → {U-CP-58, U-CP-59, U-CP-60, U-CP-61}; no back-edge to higher layers; no inversion at any consumer of the existing C-CP-28 surface (existing consumers preserved verbatim per the `post_evaluate_hook=None` default).

### §0.6 Status posture

Proposed (v2.26) → **Proposed (v2.27)**. v2.27 is a NEW unit authoring delta — first NEW unit since v2.21 L9-undecies cluster authoring at runtime plan (and L9-quindecies at v2.28); CP plan side first NEW unit since v2.15 Cluster 10 closing 15-unit batch at U-CP-72.

### §0.7 Adjacent defects surfaced (not patched per FM-2)

(i) **CXA §0.4 convention-seam declaration owed at future CXA touch arc.** Per Q5=β ratification, NO new typed CXA edge at canonical enumeration. The harness-cp `ValidatorPostEvaluateHook` Protocol ↔ harness-runtime cost-attribution hook impl pairing is convention-level seam candidate per CXA v2.11 + v2.12 + v2.14 convention-bucket precedent. NOT patched at v2.27 per FM-2 single-focus-arc scope.

(ii) **Runtime plan v2.28 → v2.29 single-unit-body amendment at U-RT-84 owed at apply-pass co-publication.** v2.27 publishes the CP-side Protocol-authoring unit; the runtime-side factory binding extension is owed at runtime plan v2.29 single-unit-body amendment at U-RT-84 (the existing `materialize_validator_framework_stage` factory unit). Co-published at this arc per X-AL-3 simultaneous-cascade discipline.

(iii) **OD plan v2.22 → v2.23 U-OD-40 LANDED status update owed.** U-OD-40 from `Implementation_Plan_Operational_Discipline_v2_14.md` §3.4 absorbs the hook binding pattern + LANDED status. Co-published at this arc.

### §0.8 Downstream absorption owed (post-v2.27)

(a) Workspace `CLAUDE.md` §2.4 CP plan row bump (v2.26 → v2.27). **Patched at v2.27 co-publication.**
(b) Co-published at v2.27 arc (CP spec v1.24 + harness-cp impl + harness-cp tests + harness-runtime cost helper + factory binding + integration tests + runtime plan v2.29 single-unit-body amendment at U-RT-84 + OD plan v2.23 + batch-28 retirement event filing). **Patched at v2.27 co-publication.**
(c) Retirement event filing — H_T-OD-5 surface coverage 2/4 → 4/4 (validator + webhook surfaces wire at this arc); PARTIAL → RETIRE-READY transit at batch-28 (separate retirement-event filing arc; operator-discretion timing per existing 7d cadence — landed at this arc).

---

## §1 — Cross-arc note (X-AL-3 spec extension)

This arc IS the X-AL-3 spec extension arc filed and ratified at `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md`. The fork doc enumerates the alternative (decorator pattern A) declined at Q1 ratification. Future revision passes MAY return to decorator pattern IF the operator-opt-in hook surface accumulates cognitive load (e.g., if multi-hook composition emerges as a pattern); v2.27 selects the singleton hook surface per current scope.

The fork doc §4 enumerates the full downstream cascade absorbed at this arc:

| Layer | Status at v2.27 co-publication |
|---|---|
| CP spec v1.23 → v1.24 NEW §28.10 | **Co-published** at this arc |
| CP plan v2.26 → v2.27 NEW U-CP-73 | **THIS arc** |
| Runtime spec | ZERO change (intra-axis CP Protocol; runtime supplies impl via existing C-RT-23 factory) |
| Runtime plan v2.28 → v2.29 single-unit-body amendment at U-RT-84 | **Co-published** at this arc |
| OD plan v2.22 → v2.23 U-OD-40 LANDED | **Co-published** at this arc |
| harness-cp impl | **Co-published** at this arc |
| harness-runtime impl (cost helper + hook impl + factory binding) | **Co-published** at this arc |
| harness-od | ZERO change (carrier already operational from U-OD-39 / U-OD-41) |
| CXA | NO new typed edge per Q5=β; convention-seam at §0.4 NOT amended at this arc per FM-2 |
| batch-28 retirement event H_T-OD-5 PARTIAL → RETIRE-READY | **Co-published** at this arc (surface coverage 4/4 at validator + webhook landing) |

---

## §2 — NEW unit body — U-CP-73

### U-CP-73 — ValidatorPostEvaluateHook Protocol surface + ConcreteValidatorFramework ctor extension + post-evaluate firing site

- **Implements:** CP spec v1.24 §28.10 NEW Protocol authoring per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified 2026-05-28
- **Files:** `harness-cp/src/harness_cp/validator_framework_types.py` (EXTEND) + `harness-cp/src/harness_cp/validator_framework.py` (EXTEND) + `harness-cp/tests/test_validator_framework_post_evaluate_hook.py` (NEW)
- **Signatures:** NEW `ValidatorPostEvaluateHook` Protocol with `async def on_post_evaluate(*, step, step_context, evaluation, execution_time_ms) -> None`; `ConcreteValidatorFramework.__init__` adds optional kw-only `post_evaluate_hook: ValidatorPostEvaluateHook | None = None`; `evaluate()` measures elapsed time + fires hook best-effort
- **Depends on:** [U-CP-58, U-CP-59, U-CP-60, U-CP-61] (within-axis; all landed at main per Cluster 10 closure 2026-05-24)
- **ACs:**
  1. `ValidatorPostEvaluateHook` Protocol declared at `validator_framework_types.py` with `@runtime_checkable` decoration + correct async signature per CP spec v1.24 §28.10.1
  2. `ConcreteValidatorFramework.__init__` accepts optional kw-only `post_evaluate_hook` param; `None` default preserves all 6 existing construction sites byte-identical
  3. Existing call sites verified via grep: no breaking change; all pre-v1.24 `ConcreteValidatorFramework(registry)` calls continue to work
  4. `evaluate()` fires hook EXACTLY ONCE per invocation when `post_evaluate_hook is not None`, AFTER `ValidatorEvaluation` construction, BEFORE return per §28.10.3
  5. `evaluate()` measures `execution_time_ms` via `time.monotonic_ns()` per §28.10.5 mechanism (a); scope covers validator-registry-lookup through ValidatorEvaluation construction
  6. `evaluate()` swallows ALL exceptions raised by `on_post_evaluate` per §28.10.4 invariant 2; logs nothing; returns evaluation unchanged
  7. Hook does NOT fire if `evaluate()` raises before `ValidatorEvaluation` construction (registry-lookup miss; validator.validate() exception) per §28.10.4 invariant 1
  8. `SyncValidatorFrameworkFacade` preserved verbatim; sync drivers receive same hook-firing behavior via async-to-sync bridge transparently
  9. `convert_revalidate_to_permanent_fail` does NOT fire the hook per §28.10.4 invariant 6
- **Tests:** `test_validator_post_evaluate_hook_protocol_runtime_checkable`, `test_validator_post_evaluate_hook_signature_matches_spec`, `test_concrete_validator_framework_ctor_optional_hook_default_none`, `test_concrete_validator_framework_ctor_optional_hook_explicit_value`, `test_evaluate_fires_hook_once_after_evaluation_construction`, `test_evaluate_fires_hook_with_correct_kwargs`, `test_evaluate_measures_execution_time_ms_via_monotonic_ns`, `test_evaluate_swallows_hook_exception_returns_evaluation_unchanged`, `test_evaluate_does_not_fire_hook_on_registry_miss`, `test_evaluate_does_not_fire_hook_on_validator_exception`, `test_sync_facade_transparent_hook_passthrough`, `test_convert_revalidate_does_not_fire_hook`

---

## §3 — DAG topology delta (v2.26 → v2.27)

NEW unit at U-CP-73 added at L4-within-Cluster-10. Topological sort acyclic:

```
Cluster 10 (extended at v2.27):
  L0: U-CP-58, U-CP-62, U-CP-66, U-CP-71 (preserved from v2.15)
  L1: U-CP-59 (←58), U-CP-67 (←66), U-CP-63 (←62), U-CP-69 (←66) (preserved)
  L2: U-CP-60 (←58, 59), U-CP-68 (←66, 67), U-CP-64 (←62, 63) (preserved)
  L3: U-CP-61 (←60 + U-OD-50 cross-axis), U-CP-65 (←63, 64 + U-OD-51 cross-axis), U-CP-70 (←68 + U-OD-52 cross-axis) (preserved)
  L4: U-CP-72 (←60, 63, 64, 68, 71 + U-RT-69, U-RT-70 cross-axis) (preserved)
  L4-NEW-at-v2.27: U-CP-73 (←58, 59, 60, 61) — singleton-extension under operator-opt-in hook Protocol
```

Cross-axis edges at U-CP-73: NONE per Q5=β ratification.

DAG verified Kahn-acyclic; 1 NEW unit consumed at L4 ValidatorFramework substrate; ∅ remaining edges.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Control_Plane_v2_27.md` |
| Version | v2.27 |
| Filing event | NEW unit U-CP-73 authoring per CP spec v1.24 §28.10 NEW `ValidatorPostEvaluateHook` Protocol surface; Class 1 fork resolution Reading (B) absorption per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` operator-ratified 2026-05-28 Q-set. 2026-05-28 |
| Predecessor | `Implementation_Plan_Control_Plane_v2_26.md` (preserved verbatim outside the §0 + §2 amendments at v2.27) |
| Successor | (none — current canonical) |
| Unit count | 73 → **74** (+1 NEW unit U-CP-73) |
| DAG topology | Extended per §3 (L4-within-Cluster-10; singleton-extension; NO new cluster; DAG Kahn-acyclic) |
| AC count delta | +9 NEW ACs at U-CP-73 (full unit authoring) |
| Cross-axis cascade | ZERO per Q5=β ratification (intra-axis CP Protocol; intra-axis runtime composition) |
| H_T-OD-5 status | Surface coverage 2/4 → 4/4 at this arc (validator + webhook surfaces wire); PARTIAL → RETIRE-READY transit at batch-28 retirement event filing co-published at this arc |
| Operator authority | `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Q-set ratification 2026-05-28 (Q1=B Hook Protocol; Q2=harness-cp Protocol home; Q3=best-effort swallow; Q4=optional ctor param None default; Q5=β NO new CXA edge) |
| Date | 2026-05-28 |
