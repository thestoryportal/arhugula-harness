# Spec: Control Plane — v1.88 (delta over v1.87)

*Delta-only file. The v1.87 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta records the B-18-3C-PREWARM-COHORTKEY bundled-absorption arc: materializing the dispatcher-oracle `CohortKeyCapable` Protocol, refactoring `_same_prefix_cohort()` from CP-visible per-attribute checks to dispatcher-attested cacheability, and delegating the oracle through the production inference wrapper chain.*

## Change-note (v1.87 → v1.88)

**What this materializes.** The v1.87 `_same_prefix_cohort()` predicate checked six CP-visible per-attribute comparisons (step_kind, provider, model, agent_role, prompt_version_sha, extended_thinking) against the operator-asserted residual scope caveat. B-18-3C-PREWARM-COHORTKEY replaces this with a **dispatcher-oracle** approach: a new `@runtime_checkable CohortKeyCapable(Protocol)` allows each dispatcher to attest its own cache-prefix stability (including the v1.87 operator-asserted residuals) via a `cohort_key(binding, step) -> str | None` method. `None` means "not stable — do not warm." The predicate is now machine-checkable end-to-end.

**Scope of revision.**

**§25.15 amendment — `_same_prefix_cohort()` refactored to dispatcher-oracle:**

The v1.87 five-attribute implementation is replaced by:

```python
def _same_prefix_cohort() -> bool:
    if len(branch_plan) < 2:        # H3: live plan length, NOT cell cap
        return False
    keys: list[str] = []
    for branch_index, step, _child, _writer, binding in branch_plan:
        dispatcher = branch_dispatchers[branch_index]
        if not isinstance(dispatcher, CohortKeyCapable):
            return False
        key = dispatcher.cohort_key(binding, step)
        if key is None:
            return False
        keys.append(key)
    return len(set(keys)) == 1
```

Pre-flight lookup: `branch_dispatchers = {bi: step_dispatchers.lookup(step.step_kind) for bi, step, _child, _writer, _binding in branch_plan}` is computed once before `_same_prefix_cohort()` is called.

The H3 length guard (`len(branch_plan) < 2`) is preserved as the first check. All remaining prior-predicate v1.87 dimensions (step_kind, provider, model, agent_role, prompt_version_sha, extended_thinking) are subsumed by the dispatcher's `cohort_key()` hash encoding.

**§25.16 (NEW) — `CohortKeyCapable` Protocol:**

```python
@runtime_checkable
class CohortKeyCapable(Protocol):
    def cohort_key(
        self, binding: StepEffectiveBinding, step: WorkflowStep
    ) -> str | None:
        """Return a stable cohort key, or None if this dispatch is not cache-stable."""
        ...
```

`CohortKeyCapable` is exported from `harness_cp.workflow_driver` (added to `__all__`). A dispatcher returning a non-None key attests that ALL of the following hold for the given binding + step:

- The prompt-cache prefix is deterministic (provider, model, agent_role, prompt_version_sha, thinking, cache_ttl stable)
- `frozen_tool_superset` is bound (stable tools-block marker at the C-RT-46 breakpoint)
- `memory_runtime` is None (no per-branch memory context — memory-bound dispatch destabilizes the prefix)

When `cohort_key()` returns None, `_same_prefix_cohort()` immediately returns False → `_warmup_gate=False` → all-concurrent baseline (byte-identical to the pre-v1.87 path).

**`RuntimeLLMDispatcher` implements `CohortKeyCapable`** (`harness_runtime.lifecycle.llm_dispatch`):

- Returns `None` when `self.memory_runtime is not None` (memory-bound → unstable prefix)
- Returns `None` when `self.frozen_tool_superset is None` (no stable tools-block marker → no cache breakpoint; the MVP state where no tools-block has been delivered)
- Otherwise returns `hashlib.sha256(b"\x00".join([provider, model, agent_role, prompt_version_sha, thinking, cache_ttl, b"fts_bound"])).hexdigest()[:16]` — 16-char lowercase hex cohort key

The 16-hex key encodes the full cache-prefix stability claim. Two branches sharing the identical key attest that their prompt-cache prefixes are equivalent under the dispatcher's stable-dispatch policy. (Carve-out: when `routing_activation` is enabled on `RetryBreakerFallbackDispatcher`, content-sensitive routing may promote different models per branch despite equal cohort keys — warmup fires but provides no cache benefit on that path; latency-only consequence, registered as a known sharpening alongside `B-18-EPOCH-PARTITION`.)

**Delegation wrappers** — production inference chain above `RuntimeLLMDispatcher` each implement `CohortKeyCapable` via delegation stubs:

| Wrapper | Module |
|---|---|
| `RuntimeHITLGateComposer.cohort_key()` | `harness_runtime.lifecycle.hitl_gate_composer` |
| `RetryBreakerFallbackDispatcher.cohort_key()` | `harness_runtime.lifecycle.retry_breaker_fallback` |
| `SyncDispatcherFacade.cohort_key()` | `harness_runtime.lifecycle.sync_dispatcher_facade` |

Each delegation stub:
1. Local-imports `CohortKeyCapable` from `harness_cp.workflow_driver` inside the method body (avoids module-level circular imports; H_E ↔ H_T boundary safe)
2. Checks `isinstance(self.inner, CohortKeyCapable)` — delegates if True, returns None if False
3. For `RuntimeHITLGateComposer`, the `binding` parameter is typed `Any` per C-RT-04 (HITL gate receives `StepEffectiveBinding | Any`)

The CP driver calls `cohort_key()` on the outermost wrapper it receives (`SyncDispatcherFacade` in production). The delegation chain ensures the call propagates to `RuntimeLLMDispatcher`'s real hash computation. Non-inference dispatchers (sub-agent, declarative) wired below the production wrappers have no `cohort_key()` method on the wrapper's `inner`. The delegation stub's `isinstance(self.inner, CohortKeyCapable)` check returns False → stub returns None → predicate returns False → warmup correctly disabled. (The wrappers themselves DO implement `CohortKeyCapable` via the delegation stubs; warmup is disabled because the delegation chain bottoms out at a non-capable inner, not because the wrappers lack the method.)

**Invariants preserved.** NO §5.2 IS-hash change. NO new contract / ADR / enum / fail-class / CXA edge. `CohortKeyCapable` is an additive Protocol — it does NOT widen `StepDispatcher` (Fork B rationale, `.harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md`). All existing v1.87 warmup tests pass; 16 new witnesses added:
- CK-1 / CK-2 / CK-3: CP driver integration via `execute_workflow` (uniform / None / non-uniform cohort keys)
- RK-1 through RK-13: unit witnesses for `RuntimeLLMDispatcher.cohort_key()` (RK-1..6), delegation stubs (RK-7..12), and full production-chain end-to-end (RK-13)

**MVP note.** At MVP, `frozen_tool_superset` is None on most deployments. `RuntimeLLMDispatcher.cohort_key()` returns None in that state → `_same_prefix_cohort()` returns False → `_warmup_gate=False` → all-concurrent baseline. This is correct machine-attestation behavior: warmup does not fire unless the stable tools-block marker is present. The B-18-3C-PREWARM-DEFAULT-ON follow-on arc requires `CohortKeyCapable` to land first and explicitly handles the MVP-vs-production distinction.

**Registered follow-ons (SPINE `B-*`) — updated status.**

| Follow-on | Scope | Status |
|---|---|---|
| `B-18-3C-PREWARM-COHORTKEY` | This delta | **CLOSED** (this arc) |
| `B-18-3C-PREWARM-CASCADE` | warm-up on CASCADE_CANCEL + PAUSE paths | Registered, open |
| `B-18-3C-PREWARM-DEFAULT-ON` | flip to required-at-cap>1 per ADR §1.8(f); requires COHORTKEY landed | Registered, open (COHORTKEY prerequisite now met) |
| `B-18-EPOCH-PARTITION` | version_sha cohort HASH + heterogeneous partition (warm one per cohort) | Registered, open |

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_88.md` (delta over v1.87) |
| Arc | B-18-3C-PREWARM-COHORTKEY — dispatcher-oracle `CohortKeyCapable` Protocol |
| Committed source | `.harness/class_2_fork_b18_cohortkey_fork_a_vs_b.md` (Fork B ratified); ADR-D4 §1.8 machine-checkable attestation extension |
| Disposition | Additive `CohortKeyCapable` Protocol (§25.16); `_same_prefix_cohort()` refactored (§25.15); three delegation stubs in `harness_runtime`; 16 new witnesses |
| Decorrelated review | Pending `just codex-review` pre-merge (§13.1) |
| IS / OD / AS / ADR | UNCHANGED. CXA v2.20 UNCHANGED (`CohortKeyCapable` is a new Protocol, not a new CXA seam) |
| Runtime spec | UNCHANGED (delegation stubs are impl-to-cleared-spec; no new runtime contract) |
| Follow-on status | B-18-3C-PREWARM-COHORTKEY CLOSED; B-18-3C-PREWARM-DEFAULT-ON prerequisite now met |
