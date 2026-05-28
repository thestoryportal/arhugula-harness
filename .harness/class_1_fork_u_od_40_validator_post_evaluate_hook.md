# Class 1 Fork — U-OD-40 ValidatorPostEvaluateHook Protocol extension

**Filed:** 2026-05-28 at U-OD-40 orientation (this session)
**Status:** RATIFIED (Q-set pre-ratified at operator AskUserQuestion 2026-05-28)
**Authority anchor:** Workspace `CLAUDE.md` §4.4 X-AL-3 (no silent H_T design extension at Phase 7 execution-time) + Phase 7 back-flow routing per `Project_Workflow_v1_10.md` §2.7.6
**Mirror precedent:** `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Reading B operator-opt-in hook Protocol pattern; runtime spec v1.32 §14.17 `SkillActivationHook`

---

## §1 — Trigger

U-OD-40 (cost-attribution at validator.evaluate site) requires a callback into harness-runtime cost-attribution helpers (which import harness_od types). The validator framework body lives at `harness-cp/src/harness_cp/validator_framework.py:130` (`ConcreteValidatorFramework`); the production invocation site is `ConcreteValidatorFramework.evaluate()` at line 167.

**Dep-graph constraint:** `harness-cp` deps = `harness-core` + `harness-as` ONLY (NOT `harness-od`). Therefore harness-cp cannot import harness_od cost-attribution helpers directly.

Two structural patterns satisfy U-OD-40 AC #1 (validator CPU-meter cost-record per Decision 2.D5):

- **(A) Wrap-at-factory decorator** — `materialize_validator_framework_stage` at harness-runtime constructs `ConcreteValidatorFramework`, wraps in `CostAttributingValidatorFramework` decorator implementing the harness-cp `ValidatorFramework` Protocol, delegates `evaluate()` and attributes cost after. ZERO harness-cp Protocol extension.
- **(B) Hook Protocol** — NEW `ValidatorPostEvaluateHook` Protocol added to harness-cp `ValidatorFramework` surface; `ConcreteValidatorFramework.evaluate()` fires hook post-evaluate; harness-runtime supplies cost-attributing hook implementation. EXTENDS harness-cp Protocol surface.

(B) is an H_T design extension at Phase 7 execution-time → Class 1 fork required per X-AL-3.

---

## §2 — Q-set ratification

Operator AskUserQuestion 2026-05-28 at U-OD-40 orientation arc.

**Q1 — Validator binding pattern:** Wrap-at-factory decorator (A) vs Hook Protocol (B).
- **Ratified: (B) Hook Protocol.** Operator selected hook surface pattern despite decorator alternative.
- **Rationale (operator):** Explicit observability seam in harness-cp Protocol surface; precedent shape from `SkillActivationHook` (U-RT-101); future readers see hook surface in CP contract rather than transparent wrap.

**Q2 — Hook surface ownership:** Authored at harness-cp (CP-axis spec surface) per consumer-axis primacy.
- **Ratified: harness-cp.** Hook Protocol declared at `harness-cp/src/harness_cp/validator_framework_types.py`; ConcreteValidatorFramework ctor accepts optional `post_evaluate_hook` param.

**Q3 — Hook firing semantics:** Async hook fired AFTER `ValidatorEvaluation` construction, BEFORE return. Best-effort error swallowing (cost attribution is observability, not contract — MUST NOT fail the dispatch).
- **Ratified: best-effort swallow** per `_attribute_tool_cost_best_effort` precedent at `runtime_tool_dispatcher.py:285`.

**Q4 — Operator opt-in shape:** `None` default preserves all existing ctor sites; non-`None` opts in. Same shape as `SkillActivationHookConfig` at runtime spec §14.17.
- **Ratified: optional ctor param `post_evaluate_hook: ValidatorPostEvaluateHook | None = None`.**

**Q5 — Cross-axis cascade:** Hook Protocol declared at harness-cp; harness-runtime supplies impl wiring through `materialize_validator_framework_stage` factory.
- **Ratified: NO new CXA edge** (factory binding is intra-axis runtime composition; Protocol declaration is intra-axis CP).

---

## §3 — Hook Protocol signature

```python
@runtime_checkable
class ValidatorPostEvaluateHook(Protocol):
    """Operator-supplied post-evaluate observability hook.

    Fires once per ConcreteValidatorFramework.evaluate() invocation, AFTER
    ValidatorEvaluation construction, BEFORE return. Receives elapsed
    wall-clock time + step + evaluation. Cost-attribution implementation
    lives at harness-runtime (importing harness_od types); hook surface
    declared at harness-cp keeps the Protocol independent of OD-axis
    vocabulary.

    Best-effort: hook failures swallowed at the firing site
    (ConcreteValidatorFramework.evaluate) per cost-attribution-is-
    observability discipline (mirror `_attribute_tool_cost_best_effort`
    at `harness_runtime/lifecycle/runtime_tool_dispatcher.py:285`).
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

---

## §4 — Downstream cascade (apply-pass scope)

| Layer | Change |
|---|---|
| CP spec (v1.23 → v1.24) | NEW §25.X (sub-section under C-CP-28 ValidatorFramework) authoring `ValidatorPostEvaluateHook` Protocol + ConcreteValidatorFramework optional `post_evaluate_hook` ctor param + post-evaluate firing site + best-effort invariant |
| CP plan (v2.26 → v2.27) | NEW U-CP-73 unit (or similar next-ID) decomposing Protocol + ctor extension + firing site + unit tests |
| Runtime spec | NO change — Protocol surface is CP-axis owned; harness-runtime supplies impl via factory binding (no NEW C-RT-NN contract needed; falls under existing C-RT-23 `materialize_validator_framework_stage` factory) |
| Runtime plan (v2.28 → v2.29) | Single-unit-body amendment at U-RT-84 adding NEW AC for cost-attribution hook construction + factory binding wire-up |
| OD plan (v2.22 → v2.23) | Single-unit-body amendment at U-OD-40 (already exists per `Implementation_Plan_Operational_Discipline_v2_14.md` §3.4) absorbing the hook binding pattern + LANDED status |
| harness-cp | NEW `ValidatorPostEvaluateHook` Protocol at `validator_framework_types.py`; `ConcreteValidatorFramework.__init__` extended (optional kw-only `post_evaluate_hook`); `evaluate()` measures elapsed time + fires hook best-effort |
| harness-runtime | NEW `lifecycle/cost_attribution_validator_dispatch.py` (CPU-meter helper); NEW concrete hook impl class binding helper through to cost_chain; factory extends to construct + inject hook |
| harness-od | ZERO change at carrier layer (cost-record + audit-write seam already operational from U-OD-39 / U-OD-41 cluster); ZERO new ledger row |
| CXA | NO new typed edge; convention seam at §0.4 if any — verify at apply arc |

---

## §5 — Alternative considered (Reading A — DECLINED at Q1)

**(A) Wrap-at-factory decorator** rejected at operator ratification 2026-05-28 in favor of explicit hook surface.

Architectural trade-off (A vs B):

| Axis | A — Decorator | B — Hook Protocol (ratified) |
|---|---|---|
| harness-cp Protocol surface | Unchanged | Extended (NEW Protocol) |
| X-AL-3 fork required | NO | YES (this doc) |
| Future-reader cognitive load at harness-cp | Lower (cost-attribution invisible at CP surface) | Higher (hook surface visible) |
| Factory complexity | Higher (wrap construction + SyncFacade ordering) | Lower (factory constructs hook impl + passes to ctor) |
| Symmetry with existing precedent | Decorator pattern less established in workspace | SkillActivationHook (U-RT-101) — same shape |
| Test substitution | Decorator harder to mock (must conform to Protocol) | Hook trivially mockable (any object with single async method) |

Operator selected (B) for symmetry with U-RT-101 + explicit observability seam.

---

## §6 — Scope discipline

- ZERO change to existing `ValidatorFramework` Protocol at `validator_framework_types.py:211` — extension is additive at NEW Protocol + ctor optional param.
- ZERO breaking change at any existing `ConcreteValidatorFramework(...)` call site — `post_evaluate_hook=None` default preserves all 6 existing construction sites verified via grep.
- ZERO change to `SyncValidatorFrameworkFacade` — wraps the decorated/hooked ConcreteValidatorFramework transparently.
- Hook fires AFTER `ValidatorEvaluation` construction; on hook exception, swallow and continue (return evaluation unchanged).

---

## §7 — Authority anchors

- Workspace `CLAUDE.md` §4.4 X-AL-3 (no silent H_T design extension)
- `Project_Workflow_v1_10.md` §2.7.6 back-flow routing (Class 1)
- `.harness/class_1_fork_as_8d_skill_activation_surface_absence.md` Reading B precedent
- Runtime spec v1.32 §14.17 `SkillActivationHook` Protocol shape
- `harness_runtime/lifecycle/runtime_tool_dispatcher.py:285` `_attribute_tool_cost_best_effort` best-effort pattern precedent
- U-OD-40 ACs at `design-substrate/Implementation_Plan_Operational_Discipline_v2_14.md` §3.4

---

## §8 — Status

PROPOSING → ✅ RATIFIED (Q-set pre-ratified at AskUserQuestion 2026-05-28; this doc is the canonical record).
Apply-pass: in progress this session.
