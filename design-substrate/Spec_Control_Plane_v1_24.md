# Spec: Control Plane — v1.24 (delta over v1.23)

---

## Change-note (v1.23 → v1.24)

**Scope of revision.** Substantive amendment authoring NEW §28.10 sub-section under C-CP-28 ValidatorFramework absorbing the `ValidatorPostEvaluateHook` Protocol surface per `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` Reading (B) operator-ratified 2026-05-28 Q-set at U-OD-40 orientation arc AskUserQuestion (Q1=B Hook Protocol over decorator; Q2=harness-cp Protocol home; Q3=best-effort swallow per `_attribute_tool_cost_best_effort` precedent; Q4=optional ctor param `None` default; Q5=NO new CXA edge).

**Trigger.** U-OD-40 (cost-attribution at `validator.evaluate` site per OD spec v1.8 §C-OD-26.2 row "validator.evaluate") requires a callback into harness-runtime cost-attribution helpers (which import `harness_od` types). The dep-graph constraint (`harness-cp` depends on `harness-core` + `harness-as` ONLY, NOT `harness-od`) forecloses direct import at harness-cp. Two structural patterns satisfy U-OD-40 AC #1: (A) wrap-at-factory decorator at harness-runtime (transparent observability; ZERO harness-cp Protocol extension); (B) hook Protocol authored at harness-cp + supplied at harness-runtime via factory binding (explicit observability seam at CP surface; H_T design extension under X-AL-3). Operator ratified (B) per symmetry with `SkillActivationHook` (U-RT-101 / runtime spec v1.32 §14.17) + explicit observability seam preference.

**Workspace `CLAUDE.md` §4.4 X-AL-3 compliance.** H_T design extension at Phase 7 execution-time → Class 1 fork required → filed at `.harness/class_1_fork_u_od_40_validator_post_evaluate_hook.md` → operator-ratified at AskUserQuestion 2026-05-28 → apply pass at this v1.24 amendment.

**Mirror precedent.** Runtime spec v1.32 §14.17 NEW `SkillActivationHook` Protocol surface + ConcreteValidatorFramework-analogous opt-in pattern (`SkillActivationHookConfig` empty-marker; operator-supplied hook impl; `None` default = opt-out preserves existing construction sites verbatim).

**v1.23 substantive content preserved verbatim.** All v1.23 content (§5.2 / §8.1 / §8.3 carrier-name harmonization + §1.2 emission-scope cite-correction at `workflow_driver.py:662`) preserved unchanged. The §28 ValidatorFramework body at v1.10 (renamed at v1.13) preserved verbatim — additive at NEW §28.10 sub-section; ZERO change to §28.1 through §28.9.

**Co-publication this session.** harness-cp impl (`validator_framework_types.py` NEW `ValidatorPostEvaluateHook` Protocol; `validator_framework.py` `ConcreteValidatorFramework.__init__` extended with optional kw-only `post_evaluate_hook` param + `evaluate()` post-evaluate hook firing site with best-effort swallow) + harness-runtime impl (NEW `lifecycle/cost_attribution_validator_dispatch.py` CPU-meter helper + cost-attributing hook impl + `materialize_validator_framework_stage` factory extension threading the hook) + CP plan v2.27 (NEW unit U-CP-73 absorbing the Protocol + ctor extension + firing site) + runtime plan v2.29 (single-unit-body amendment at U-RT-84 adding hook binding AC) + OD plan v2.23 (U-OD-40 LANDED status).

**ZERO breaking change.** All 6 existing `ConcreteValidatorFramework(...)` construction sites verified via grep preserved at `post_evaluate_hook=None` default. `SyncValidatorFrameworkFacade` preserved verbatim — wraps the hooked-or-unhooked ConcreteValidatorFramework transparently.

**ZERO cross-axis cascade.** Per Q5=β ratification: NO new typed CXA edge; convention seam at CXA §0.4 NOT amended (Protocol declaration is intra-axis CP; factory binding is intra-axis runtime composition; ZERO cite-cascade owed at AS spec / OD spec / runtime spec; OD spec §C-OD-26.2 row "validator.evaluate" already canonical and unchanged).

---

## §1 — NEW §28.10 — ValidatorPostEvaluateHook Protocol (X-AL-3 spec extension)

### §28.10.1 — Protocol declaration

```python
from typing import Protocol, runtime_checkable

from harness_cp.validator_framework_types import ValidatorEvaluation
from harness_cp.workflow_step_types import WorkflowStep
from harness_cp.step_execution_context import StepExecutionContext


@runtime_checkable
class ValidatorPostEvaluateHook(Protocol):
    """Operator-supplied post-evaluate observability hook.

    Fires once per `ConcreteValidatorFramework.evaluate()` invocation,
    AFTER `ValidatorEvaluation` construction, BEFORE return. Receives
    elapsed wall-clock execution time + step + step_context + evaluation.

    Hook is observability-only; MUST NOT modify the evaluation; MUST NOT
    influence dispatch outcome. Implementation lives at harness-runtime
    (which can import `harness_od` types for cost-attribution); the
    Protocol surface declared here at harness-cp is independent of
    OD-axis vocabulary.

    Best-effort firing: hook exceptions swallowed at the firing site per
    cost-attribution-is-observability discipline (mirror
    `_attribute_tool_cost_best_effort` at
    `harness_runtime/lifecycle/runtime_tool_dispatcher.py:285`).
    """

    async def on_post_evaluate(
        self,
        *,
        step: WorkflowStep,
        step_context: StepExecutionContext,
        evaluation: ValidatorEvaluation,
        execution_time_ms: float,
    ) -> None: ...
```

### §28.10.2 — ConcreteValidatorFramework ctor extension

`ConcreteValidatorFramework.__init__` gains an optional kw-only param:

```python
def __init__(
    self,
    validator_registry: Mapping[StepID, Validator],
    *,
    post_evaluate_hook: ValidatorPostEvaluateHook | None = None,
) -> None: ...
```

`None` default preserves all existing construction sites verbatim (grep-verified at apply arc: 6 existing `ConcreteValidatorFramework(...)` call sites across harness-cp/tests/ + harness-runtime factory). Non-`None` opts in to post-evaluate hook firing.

### §28.10.3 — Firing site at `evaluate()`

`ConcreteValidatorFramework.evaluate()` post-evaluate firing site IS INSERTED AFTER `ValidatorEvaluation` construction (per §28.4 invocation discipline step 6 "Return ValidatorEvaluation") AND BEFORE return:

```python
async def evaluate(
    self,
    step: WorkflowStep,
    step_result: Mapping[str, Any],
    *,
    step_context: StepExecutionContext,
) -> ValidatorEvaluation:
    """Run the per-step Validator + wrap into ValidatorEvaluation.

    Per §28.4 invocation discipline + §28.10 post-evaluate hook firing.
    """
    import time

    start_monotonic_ns = time.monotonic_ns()
    validator = self._validator_registry[step.step_id]

    result: ValidatorResult = await validator.validate(...)

    # ... existing §28.4 steps 3, 4, 5 preserved verbatim ...

    evaluation = ValidatorEvaluation(
        result=result,
        span_attributes=span_attributes,
        next_action=next_action,
        burden_count=self._burden_count,
    )

    # §28.10 post-evaluate hook firing (best-effort swallow)
    if self._post_evaluate_hook is not None:
        execution_time_ms = (
            time.monotonic_ns() - start_monotonic_ns
        ) / 1_000_000.0
        try:
            await self._post_evaluate_hook.on_post_evaluate(
                step=step,
                step_context=step_context,
                evaluation=evaluation,
                execution_time_ms=execution_time_ms,
            )
        except Exception:
            pass  # observability-only; MUST NOT fail dispatch

    return evaluation
```

### §28.10.4 — Invariants

1. **Single firing per `evaluate()` invocation.** Hook fires exactly once at successful `ValidatorEvaluation` construction. If `evaluate()` raises before construction (e.g., `validator_registry` lookup miss), hook does NOT fire.
2. **Best-effort discipline.** Hook exceptions MUST be swallowed at the firing site. Failure of cost-attribution MUST NOT fail validator dispatch. Mirror `_attribute_tool_cost_best_effort` at `runtime_tool_dispatcher.py:285`.
3. **Observability-only.** Hook MUST NOT modify the `ValidatorEvaluation` instance; MUST NOT influence dispatch outcome; MUST NOT mutate framework state (`burden_count` already incremented at §28.4 step 3 pre-firing). Async `on_post_evaluate` returns `None` enforces this by signature.
4. **Opt-out preserves behavior.** `post_evaluate_hook=None` default produces byte-identical behavior to pre-v1.24 §28.4 invocation discipline. No hook firing; no elapsed-time measurement.
5. **Elapsed time measurement scope.** `execution_time_ms` measures from validator-registry lookup start through ValidatorEvaluation construction end — covers the validator's `validate()` call + burden-count update + span-attributes build. Excludes the hook firing itself (measurement closes before the hook fires).
6. **`convert_revalidate_to_permanent_fail` does NOT fire the hook.** Per §28.5 the conversion is a workflow-driver hook on retry-budget exhaustion — distinct surface from the per-evaluate observability hook. Cost attribution at conversion site (if owed in future) routes via separate hook surface or via factory-wrap of `convert_revalidate_to_permanent_fail`. Out of scope at v1.24.

### §28.10.5 — Deferred to implementation discretion

- **Hook implementation home.** Harness-runtime supplies the cost-attributing hook impl at `lifecycle/cost_attribution_validator_dispatch.py` per dep-graph constraint (harness-runtime → harness-od import legal; harness-cp → harness-od import illegal). The hook impl class is constructed at `materialize_validator_framework_stage` factory binding time when `ctx.cost_chain` is bound; passed into `ConcreteValidatorFramework` via the ctor kw-only param.
- **Factory wiring shape.** Mechanism (a) recommended default: factory constructs `CostAttributingValidatorHook(cost_chain=ctx.cost_chain, rate_table=ctx.rate_table)` at binding time; passes via ctor. Mechanism (b) alternative: factory accepts operator-supplied hook in `ValidatorFrameworkConfig` (mirror `SkillActivationHookConfig` pattern); cost-attributing hook becomes one of multiple opt-in hooks. v1.24 spec authors mechanism (a) at U-RT-84 amendment; mechanism (b) reserved as FM-2 follow-on if multi-hook composition surface emerges.
- **Elapsed-time clock choice.** `time.monotonic_ns()` recommended (immune to wall-clock jumps). `time.perf_counter_ns()` acceptable alternative. Sub-millisecond precision sufficient per CPU-meter granularity at RATE_TABLE_V1.

### §28.10.6 — Producer-side reference

This Protocol surface is the producer-site canonical declaration. Consumer-site (harness-runtime cost-attribution hook impl + factory wiring) at runtime plan v2.29 single-unit-body amendment at U-RT-84.

OD spec §C-OD-26.2 row "validator.evaluate" cost-meter contract (CPU-meter `execution_time_ms × cpu_rate_per_ms` per Decision 2.D5) is the orthogonal consumer-side contract; the harness-runtime hook impl bridges this Protocol firing to OD-axis cost-record construction.

### §28.10.7 — Status posture

NEW Protocol at v1.24. Adoption gated on operator opt-in via factory binding (per Q4 ratification optional ctor param `None` default). H_T-OD-5 surface coverage at validator.evaluate row LANDED when factory binding lands at runtime plan v2.29 + harness-runtime impl.

---

## §2 — Adjacent observations

- **(a)** CXA §0.4 convention-seam declaration NOT amended at this arc per Q5=β ratification (intra-axis CP Protocol declaration + intra-axis runtime composition). If future CXA touch arc surveys cross-axis observability seam coverage, the harness-cp `ValidatorPostEvaluateHook` Protocol ↔ harness-runtime cost-attribution hook impl pairing is convention-level seam candidate. NOT patched per FM-2.

- **(b)** OD spec §C-OD-26.2 row "validator.evaluate" cost-meter formula at Decision 2.D5 RATIFIED (CPU-meter `execution_time_ms × cpu_rate_per_ms`) — production hook impl computes per the formula; v1.24 spec amendment is independent of the cost-meter formula choice (the formula is OD-axis canonical at OD spec). If Decision 2.D5 is re-litigated at future arc, only the harness-runtime hook impl body changes; the harness-cp Protocol surface is unaffected.

- **(c)** `SyncValidatorFrameworkFacade` at `harness-cp/src/harness_cp/validator_framework.py:323` preserved verbatim. The facade wraps the hooked `ConcreteValidatorFramework` transparently; the sync `evaluate` method calls the async `evaluate` via the async-to-sync bridge, which in turn fires the hook async. Sync drivers receive the same cost-attribution behavior as async drivers without facade-level changes. Surfaced as orientation note; NOT patched.

- **(d)** Hook impl class at harness-runtime SHOULD live at `lifecycle/cost_attribution_validator_dispatch.py` (mirror `cost_attribution_tool_dispatch.py` precedent from U-OD-39); alternative homes (`lifecycle/cost_attributing_validator_hook.py`, sibling-of-decorator naming) acceptable but the cost-attribution-helper-module precedent is canonical per `[[u-od-39-tool-dispatch-cost-attribution]]` lineage.

---

## §3 — Status

NEW Protocol at v1.24 §28.10. Apply pass: this arc (co-publication with harness-cp impl + harness-runtime impl + CP plan v2.27 + runtime plan v2.29 + OD plan v2.23 + harness-od/CLAUDE.md + workspace CLAUDE.md row bumps). v1.23 + earlier PRESERVED VERBATIM per delta-only-spec-file convention.

2026-05-28.
