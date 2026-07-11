# Class 2 Fork: B-18-3C-PREWARM-COHORTKEY — Fork A vs Fork B (CohortKeyCapable Protocol shape)

**Type:** Class 2 (in-execution operator decision)
**Filed:** 2026-07-10
**Arc:** B-18-3C-PREWARM-COHORTKEY
**Parent arc:** B-18-3C-PREWARM (PR #924, merged 2026-07-10)
**Status:** PROBE-RESOLVED at grounding; operator ratification recorded inline.

---

## 1. Context

DDR §11.4 Q1 registers `B-18-3C-PREWARM-COHORTKEY`: add `cohort_key() -> str | None`
to the dispatcher Protocol so the CP driver can attest cache-prefix stability
without the operator-asserted residual (DDR §11.2). Two implementation shapes exist.

---

## 2. Fork A — Add `cohort_key()` to `StepDispatcher` (existing Protocol)

`cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None`
added directly to the `StepDispatcher` Protocol at `workflow_driver.py:357`.

**Blast radius:** ALL 8+ implementors of `StepDispatcher` must add a `cohort_key()`
method (or inherit a default `return None`). Identified implementors:
`RuntimeLLMDispatcher`, `RuntimeHITLGateComposer`, `RetryBreakerFallbackDispatcher`,
`SyncDispatcherFacade`, `SyncSubAgentDispatcher`, plus all test stubs
(`_RecordingDispatcher`, `_SuccessDispatcher`, `_FailDispatcher`, etc. across ~15
test files). Protocol-structural non-implementors would satisfy the check if Python
allowed a default, but `StepDispatcher` is `@runtime_checkable` and used with
`isinstance` — adding a method forces ALL structural satisfiers to carry it.

**Concern:** `cohort_key()` has no semantics for sub-agent, HITL, tool, handoff, or
synthetic test dispatchers. Making it mandatory on `StepDispatcher` conflates a
cache-warm-up capability with the step dispatch contract.

---

## 3. Fork B — Separate `CohortKeyCapable` optional Protocol (CHOSEN)

`CohortKeyCapable` is a new `@runtime_checkable Protocol` with a single method
`cohort_key(self, binding: StepEffectiveBinding, step: WorkflowStep) -> str | None`.

The CP driver gates with `isinstance(dispatcher, CohortKeyCapable)` (attribute-
presence check via `@runtime_checkable`). Only dispatchers that have semantic
business with cache-cohort keys implement it:
- `RuntimeLLMDispatcher` — logic-bearing: checks `memory_runtime is None` and
  `frozen_tool_superset is not None`; else returns stable sha256 hash.
- `RuntimeHITLGateComposer`, `RetryBreakerFallbackDispatcher`, `SyncDispatcherFacade`
  — delegation stubs: `isinstance(self.inner, CohortKeyCapable) and
  self.inner.cohort_key(binding, step)`.

**Blast radius on `StepDispatcher`:** 0 (no change to the existing Protocol).
**Blast radius on dispatch wrappers:** 3 delegation stubs in `harness-runtime`
(confirmed at grounding — the advisory roadmap "blast radius 0" referred to the
Protocol modification blast radius, not the delegation chain in the runtime wrappers).
No test stubs require modification.

---

## 4. Grounding finding: wrapper chain

Session probe at `stage_5_loop_init.py:411-614` confirmed the production binding:

```
dispatchers[INFERENCE_STEP] = SyncDispatcherFacade(
    inner = RetryBreakerFallbackDispatcher(
        inner = RuntimeHITLGateComposer(
            inner = RuntimeLLMDispatcher(...)
        )
    )
)
```

`isinstance(SyncDispatcherFacade(...), CohortKeyCapable)` is True (via
`@runtime_checkable` attribute-presence check) only when `SyncDispatcherFacade`
carries `cohort_key`. If `SyncDispatcherFacade` does NOT carry it, the check is
False → gate never fires → the arc's purpose (machine-attested cohort gating) is
never exercised. The delegation stubs in the 3 wrappers are therefore REQUIRED for
the gate to be non-vacuous.

For `SUB_AGENT_DISPATCH`: `SyncDispatcherFacade` wraps `RuntimeHITLGateComposer`
wrapping `SyncSubAgentDispatcher`. `SyncSubAgentDispatcher` has no `cohort_key` →
`RuntimeHITLGateComposer.cohort_key()` returns None → delegation returns None →
warmup gate stays False. Correct.

---

## 5. Operator ratification

Fork B is RATIFIED by probe: the advisor confirmed the wrapper-chain blocker and the
delegation-chain solution before implementation. The "blast radius 0" description in
the roadmap_status.md referred to Protocol modification blast radius, not the
runtime-side delegation stubs. Both advisor and implementer agree Fork B with
delegation stubs is the correct shape.

**Decision:** Fork B, CohortKeyCapable separate Protocol + 3 delegation stubs in
runtime wrappers.

---

## 6. Implementation scope (registered)

Files modified:
- `harness-cp/src/harness_cp/workflow_driver.py` — add `CohortKeyCapable` Protocol;
  update `_same_prefix_cohort()` to use it (replaces all per-attribute checks)
- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` — implement
  `cohort_key()` on `RuntimeLLMDispatcher`
- `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py` — delegation stub
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` — delegation stub
- `harness-runtime/src/harness_runtime/lifecycle/sync_dispatcher_facade.py` — delegation stub

Tests:
- `harness-runtime/tests/test_cohort_key_rtllm.py` — `RuntimeLLMDispatcher.cohort_key()` unit witnesses
- `harness-cp/tests/test_cohort_key_capable.py` — `CohortKeyCapable` Protocol + `_same_prefix_cohort()` witnesses including the production-chain test (advisor §1)

CP spec amendment: v1.87 → v1.88 adding `CohortKeyCapable` contract to §25.15.
Arc-ledger: B-18-3C-PREWARM-COHORTKEY `registered` → `closed`.
