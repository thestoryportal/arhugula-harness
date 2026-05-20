# U-RT-43 — Bootstrap Orchestrator: Implementation Plan

**Filed:** 2026-05-20 (Phase 2 Session 7 cont.)
**Risk-gate:** CLEARED (composer signatures clean; rollback semantics for collector daemon documented; tracer rollback deferred to U-RT-44/45)
**Advisor:** consulted; locked plan = `bootstrap(config, workload_class) → HarnessContext` per Track A (spec §16 #7); WorkflowObject Protocol grows with `workload_class` (authorized by api.py:110-112)

---

## 1. Scope (per session-3 atomic decomposition §3.8.4)

- `bootstrap/__init__.py` runs the 9 stage modules in C-RT-01 fixed order
- Hands resulting `HarnessContext` to `api.run`
- Stage failures roll back initialized resources in reverse order
- Removes `BootstrapNotYetLandedError` stub at `api.py:213`

**Acceptance criteria:**
1. Full bootstrap returns `HarnessContext` (frozen Pydantic at stage 7).
2. Injected stage failure at each of the 9 substages triggers reverse-order rollback.
3. Each stage emits exactly one lifecycle event via `LifecycleEventEmitter` (when present; stage 5 lands the emitter, so stages 0..4 buffer and emit at stage 5+ — see §6).

---

## 2. File inventory (new files)

| File | LOC est. | Purpose |
|---|---:|---|
| `harness_runtime/bootstrap/__init__.py` | 220 | Orchestrator (run_bootstrap) + rollback |
| `harness_runtime/bootstrap/mutable_context.py` | 110 | `_MutableHarnessContext` builder + `freeze()` |
| `harness_runtime/bootstrap/stage_0_preamble.py` | 70 | Config normalize + KeyringResolver + Actor + drained_flag |
| `harness_runtime/bootstrap/stage_1_is.py` | 90 | path_registry + state_ledger + shadow_git + index_cache |
| `harness_runtime/bootstrap/stage_2_as.py` | 80 | skills + tool_registry + mcp_host + sandbox_dispatch |
| `harness_runtime/bootstrap/stage_3a_cp_clients.py` | 50 | providers (async) |
| `harness_runtime/bootstrap/stage_3b_cp_routing.py` | 90 | routing_manifest + engine_selector + fallback_chain + retry_breaker + hitl + handoff |
| `harness_runtime/bootstrap/stage_4_od.py` | 100 | tracer + span_processor + collector_daemon + ring_buffer + cost + audit_writer |
| `harness_runtime/bootstrap/stage_5_loop_init.py` | 50 | override_evaluator + topology_dispatcher + lifecycle_emitter |
| `harness_runtime/bootstrap/stage_6_cxa_wiring.py` | 80 | cxa_terminal_imports + 5 wiring composers |
| `harness_runtime/bootstrap/stage_7_ingress.py` | 30 | freeze `_MutableHarnessContext` → `HarnessContext` |
| `harness_runtime/bootstrap/types.py` | 60 | `StageResult`, `RollbackHandle`, `BootstrapFailure` |
| `tests/test_bootstrap.py` | 400 | Happy path + 9 rollback paths + lifecycle event count |
| **Total** | **~1430** | |

**Files modified:**
| File | Change |
|---|---|
| `harness_runtime/api.py` | Grow `WorkflowObject` Protocol with `workload_class`; replace `BootstrapNotYetLandedError` body with orchestrator call + shutdown plumb (shutdown deferred to U-RT-44+; for now: bootstrap → execute stub → return RunResult) |
| `harness_runtime/__init__.py` | Re-export `run_bootstrap`, `HarnessContext` (already exported) |
| `tests/test_api.py` | Update test #5 — `BootstrapNotYetLandedError` no longer raised; replace with `WorkflowExecutionNotYetLandedError` (the U-RT-44+ stub) |

---

## 3. `_MutableHarnessContext` shape

Plain `dataclass(slots=True)` with all fields `Optional[...]` defaulting to `None`. One `freeze()` method that constructs the frozen `HarnessContext`; raises `IncompleteBootstrapError` if any required field is None.

```python
@dataclass(slots=True)
class _MutableHarnessContext:
    config: RuntimeConfig | None = None
    drained_flag: asyncio.Event | None = None
    # Stage 1
    path_resolver: PathResolver | None = None
    worktree_manager: WorktreeIsolationManager | None = None
    shadow_git: ShadowGitSupervisor | None = None
    ledger_writer: LedgerWriter | None = None
    index: ContentAddressedIndex | None = None
    cache: SemanticCache | None = None
    # Stage 2
    skills: dict[SkillID, Skill] | None = None
    tool_contracts: dict[ToolName, ToolContract] | None = None
    mcp_host: MCPHost | None = None
    mcp_clients: dict[ClientName, MCPClient] | None = None
    sandbox_dispatch: SandboxDispatchTable | None = None
    # Stage 3a
    providers: dict[str, ProviderClient] | None = None
    # Stage 3b
    routing_manifest: RoutingManifest | None = None
    engine_selector: EngineSelector | None = None
    fallback_chain: FallbackChain | None = None
    retry_breaker: RetryBreakerRegistry | None = None
    hitl_registry: HITLPlacementRegistry | None = None
    handoff_registry: HandoffRegistry | None = None
    # Stage 4
    tracer_provider: object | None = None
    collector_daemon: CollectorDaemonHandle | None = None
    cost_chain: CostAttributionChain | None = None
    audit_writer: AuditLedgerWriter | None = None
    # Stage 5
    override_evaluator: PerStepOverrideEvaluator | None = None
    topology_dispatcher: TopologyDispatcher | None = None
    lifecycle_emitter: LifecycleEventEmitter | None = None
    # Rollback bookkeeping (not in HarnessContext)
    completed_stages: list[BootstrapStage] = field(default_factory=list)

    def freeze(self) -> HarnessContext: ...
```

Stage 6 (CXA wiring) and stage 7 (freeze) don't add fields — they verify + freeze. Wiring composers' return values are stored on `_MutableHarnessContext` for stage_7 to discard (informational only — wiring is side-effect; manifest imports are side-effect).

---

## 4. Per-stage module shape (uniform pattern)

Each `stage_N_*.py` exposes:

```python
async def execute(ctx: _MutableHarnessContext, *, workload_class: WorkloadClass) -> None:
    """Stage N: <name>. Populates <fields>. Raises <typed stage exception> on failure."""
    # 1. Validate prerequisites (prior-stage fields non-None)
    # 2. Call composer(s) with required upstream handles
    # 3. Assign results onto ctx
    # 4. Append BootstrapStage.<NAME> to ctx.completed_stages
```

Stage 0 doesn't need `workload_class`; stage 1 (state_ledger) and stage 3b (routing_manifest) do.

**Stage 3a** is the only `async` composer (provider construction is async); all other stage modules await trivially.

**Stage 6** CXA wiring composers return `*Stage` dataclasses; orchestrator stashes them on a dict (`_cxa_stages: dict[str, Any]`) for verification + freeze-time discard. The CXA wiring side-effects (manifest imports + cross-axis edge resolution) are what matters.

---

## 5. Orchestrator algorithm (`bootstrap/__init__.py`)

```python
async def run_bootstrap(
    config: RuntimeConfig,
    *,
    workload_class: WorkloadClass,
) -> HarnessContext:
    """Execute 9-stage bootstrap. On stage N failure, reverse-rollback stages 0..N-1."""
    ctx = _MutableHarnessContext()
    stages = [
        (BootstrapStage.PREAMBLE,        stage_0_preamble.execute),
        (BootstrapStage.IS,              stage_1_is.execute),
        (BootstrapStage.AS,              stage_2_as.execute),
        (BootstrapStage.CP_CLIENTS,      stage_3a_cp_clients.execute),
        (BootstrapStage.CP_ROUTING,      stage_3b_cp_routing.execute),
        (BootstrapStage.OD,              stage_4_od.execute),
        (BootstrapStage.LOOP_INIT,       stage_5_loop_init.execute),
        (BootstrapStage.CXA_WIRING,      stage_6_cxa_wiring.execute),
        (BootstrapStage.INGRESS_ACCEPT,  stage_7_ingress.execute),
    ]
    pending_events: list[BootstrapStage] = []
    for stage, executor in stages:
        try:
            await executor(ctx, workload_class=workload_class, config=config)
        except Exception as exc:  # noqa: BLE001 — convert to typed BootstrapFailure
            await _rollback(ctx, failed_stage=stage)
            raise BootstrapFailure(failed_stage=stage, cause=exc) from exc
        ctx.completed_stages.append(stage)
        pending_events.append(stage)
        # Emit lifecycle events for buffered stages once emitter exists.
        if ctx.lifecycle_emitter is not None:
            for buffered in pending_events:
                ctx.lifecycle_emitter.emit_bootstrap_stage_complete(buffered)
            pending_events.clear()
    return ctx.freeze()
```

### 5.1 Rollback

```python
async def _rollback(ctx: _MutableHarnessContext, *, failed_stage: BootstrapStage) -> None:
    """Reverse-order shutdown of stages 0..N-1 (the stages that completed)."""
    for stage in reversed(ctx.completed_stages):
        try:
            await _rollback_handlers[stage](ctx)
        except Exception:  # noqa: BLE001 — rollback is best-effort; log but continue
            pass  # actually: emit via lifecycle_emitter if present; deferred to U-RT-45
```

**Per-stage rollback handlers** (one per BootstrapStage; small table):
- PREAMBLE: clear drained_flag (no-op for empty asyncio.Event)
- IS: no rollback (ledger reattach is non-destructive; shadow_git checkpoint is opt-in per workload manifest)
- AS: MCP clients have no clean disconnect API at HEAD; deferred to U-RT-46
- CP_CLIENTS: `await provider.close()` for each provider that has `close()` (anthropic + openai async clients do)
- CP_ROUTING: no rollback (pure data structures)
- OD: `await collector_daemon.stop()` (idempotent per supervisor STOPPED state); tracer provider rollback DEFERRED per Class 3 note below; cost_chain + audit_writer no rollback
- LOOP_INIT: no rollback (pure data)
- CXA_WIRING: no rollback (side-effect imports cannot be undone; manifest references are read-only)
- INGRESS_ACCEPT: unreachable (freeze is last; if freeze fails, all stages already completed)

**Tracer rollback note (Class 3 informational, inline in stage_4_od.py):** OTel doesn't expose `unset_tracer_provider`. Once globally registered, subsequent process invocations replace via `set_tracer_provider`. Rollback at stage 4 failure leaves the provider registered (idempotent harmless). Surfaces at U-RT-44/45 shutdown work if a true unregister API is needed.

---

## 6. Lifecycle event emission discipline

**Problem:** AC #3 says "each stage emits exactly one lifecycle event," but `LifecycleEventEmitter` is materialized at stage 5. Stages 0..4 cannot emit until 5 completes.

**Resolution:** Buffer per-stage completion events; emit on stage 5 success for all buffered stages; emit synchronously thereafter. AC #3 satisfied at total-count granularity (one event per stage; for 9 stages, exactly 9 events post-bootstrap).

The 9 emitted events use a runtime-local `BootstrapStageCompleteEvent` (not a CP WorkflowEventClass — `WorkflowEventClass` is closed at 8 per `[[fork-drained-event-class]]`). The emitter's `emit_bootstrap_stage_complete(stage)` is a new method on `LifecycleEventEmitter` — small surface growth bounded to runtime.

**Alternative considered + rejected:** Don't emit stages 0..4. Rejected because AC #3 says "each of the 9 substages" — buffering preserves spec compliance without back-flow.

If the buffering pattern surfaces an architectural concern (operator wants events at the *moment* of stage completion, not post-stage-5), file as Class 3 and revisit at L9 close.

---

## 7. `WorkflowObject` Protocol growth

Add one read-only property:

```python
@runtime_checkable
class WorkflowObject(Protocol):
    @property
    def workflow_id(self) -> str: ...
    @property
    def workload_class(self) -> WorkloadClass: ...   # NEW per U-RT-43
```

Authorized inline at api.py:110-112 ("growth is non-breaking when fields are optional or read-only"). `workload_class` is read-only via `@property`.

`run()` extracts `workload_class = workflow.workload_class` and passes to `run_bootstrap`.

---

## 8. `api.py` `run()` body

```python
async def run(workflow, *, config=None):
    # ... existing pre-bootstrap validation + concurrency guard ...
    async with _run_lock:
        ctx = await run_bootstrap(
            config or RuntimeConfig(),
            workload_class=workflow.workload_class,
        )
        # U-RT-44+ will land workflow execution + shutdown sequence here.
        raise WorkflowExecutionNotYetLandedError(
            "Bootstrap succeeded; workflow execution lands at U-RT-44+."
        )
```

**Decision point:** Should `run()` at HEAD return success without executing the workflow, OR raise a `WorkflowExecutionNotYetLandedError`?

**Recommendation:** Raise `WorkflowExecutionNotYetLandedError` (mirroring the U-RT-42 `BootstrapNotYetLandedError` pattern). Returning success would be a lie — no workflow ran. Update `test_api.py` test #5 to expect the new error post-bootstrap. U-RT-44 removes the new stub.

---

## 9. Test plan (~30 tests, file `test_bootstrap.py`)

**Happy path (3 tests):**
1. `run_bootstrap(config, workload_class)` returns a frozen `HarnessContext` with every field non-None
2. All 9 stages execute in declared order
3. Exactly 9 lifecycle events emitted (after stage 5 buffer drain)

**Per-stage rollback (9 tests, one per stage):**
4..12. Inject failure at each stage N; verify (a) `BootstrapFailure(failed_stage=N)` raised; (b) `completed_stages` matches stages 0..N-1; (c) rollback handlers for stages 0..N-1 called in reverse order

**Composer integration (6 tests):**
13. `_MutableHarnessContext.freeze()` raises `IncompleteBootstrapError` when any required field None
14. WorkflowObject Protocol structural check passes for objects with `workflow_id` + `workload_class`
15. `WorkloadClass` flows from `run()` argument → stage_1 state_ledger composer
16. `Actor` constructed at stage 0 (runtime identity); state_ledger receives it
17. KeyringSecretResolver constructed at stage 0; providers at stage 3a receive it
18. CXA wiring at stage 6 resolves manifest references against the 5 imported terminal manifests

**Lifecycle event buffer (3 tests):**
19. Stages 0..4 buffered; 0 emit calls until stage 5 completes
20. After stage 5, buffered events flushed in arrival order
21. Stages 6, 7 emit synchronously (no buffer)

**Rollback edge cases (4 tests):**
22. Rollback handler exception doesn't halt rollback (best-effort)
23. CollectorDaemon `stop()` on partial-start (STOPPED) is safe
24. Provider close on construction failure (anthropic-only constructed when openai fails) closes only the constructed
25. Stage 0 failure → no completed stages → no rollback called

**API integration (5 tests):**
26. `run(workflow)` calls `run_bootstrap` with correct workload_class
27. `run(workflow)` raises `WorkflowExecutionNotYetLandedError` post-bootstrap (replaces `BootstrapNotYetLandedError`)
28. `BootstrapNotYetLandedError` symbol removed from api.py
29. `run()` propagates `BootstrapFailure` to caller
30. Concurrency guard still rejects second concurrent `run()` (U-RT-42 carryover)

---

## 10. Risks + open questions surfaced at landing time

| Risk | Surface | Resolution |
|---|---|---|
| Provider close at rollback may not be uniform across SDKs | Stage 3a rollback handler | Use duck-typing: `if hasattr(provider, 'close') and inspect.iscoroutinefunction(provider.close): await provider.close()` |
| Tracer global registration cannot be cleanly unset | Stage 4 rollback | Class 3 inline; defer to U-RT-44/45 |
| CXA wiring composer order may matter | Stage 6 | Per spec C-RT-12, terminal imports run first (side-effect); the 5 wiring composers run in any order; verify at landing |
| `_cxa_stages` dict for wiring results may need to be on `HarnessContext` if downstream wants verification | Stage 6 | Track on `_MutableHarnessContext` only at HEAD; lift to `HarnessContext` if U-RT-44+ surfaces a need |
| State-ledger `Actor` value | Stage 1 | Use `Actor(actor_class=ActorClass.AGENT, actor_id="harness-runtime")` — runtime is the agent; alternative is to add a `RUNTIME` actor class to IS schema (Class 1 IS spec change; avoid) |

If any of these surface as Class 1 at landing, apply `halt-route-split-AC` per `[[halt-route-split-ac-pattern]]`.

---

## 11. Commit plan

Single commit: `feat(runtime): U-RT-43 bootstrap orchestrator (L9 opens, closes U-RT-42's bootstrap stub)`

Body:
- Lands 9-stage bootstrap at `harness_runtime/bootstrap/` per C-RT-01/C-RT-02
- `_MutableHarnessContext` builder; `freeze()` materializes `HarnessContext`
- Per-stage rollback in reverse order on stage failure
- 9 buffered `BootstrapStageCompleteEvent` emit at stage 5+
- `WorkflowObject` Protocol grown with `workload_class` (authorized per api.py:110)
- `run()` calls `run_bootstrap`; new `WorkflowExecutionNotYetLandedError` stub at execution site (U-RT-44 lands the body)
- 30 tests; test_api.py #5 updated

**Test count delta target:** +30 tests (2006 → 2036).

---

## 12. Out of scope (defer to follow-ups)

- Workflow execution after bootstrap (U-RT-44 drain semantics; U-RT-45 shutdown)
- Tracer provider unregister (U-RT-44/45 shutdown)
- MCP client disconnect (U-RT-46)
- Per-step bootstrap-internal retries (suggested 200ms × 2^attempt per spec §2 deferred-to-discretion) — implement when a real transient surfaces
- BootstrapStageCompleteEvent permanent home (currently runtime-local; if OD wants to consume, route to C-OD-NN at design time)
