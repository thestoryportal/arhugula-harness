# Implementation Plan — Harness Runtime v2.12

## Change-note (v2.11 → v2.12)

**Scope of revision.** U-RT-68 Class 1 fork ratification absorption pass per `.harness/class_1_fork_u_rt_68_retry_wrap_shape_gap.md` (RATIFIED 2026-05-22 at session opened post-cluster L9-sexies close `e2cada0`). Absorbs runtime spec v1.14 → v1.15 (this session): NEW C-RT-21 §14.11 `RetryBreakerToolDispatcher` sibling carrier contract + NEW factory contracts at §14.9.3 (stage 3a `materialize_mcp_client_host_stage` + stage 5 `materialize_runtime_tool_dispatcher_stage`) + NEW optional fields at §3 C-RT-02 `RuntimeConfig` (`trust_policy`, `sandbox_decision_policy`) + NEW fields at §4 C-RT-04 `HarnessContext` (`mcp_client_host`, `tool_dispatcher`, `per_server_trust_evaluator`, `mcp_namespace_emitter`) + amended §14.9.2 inv 4 / §14.9.3 stage-5 prose / §14.9.6 inv 6 prose. Decomposes Q2=B2-ratified bootstrap-wiring chain into NEW cluster L9-septies (5 NEW atomic units U-RT-71..U-RT-75) + REWRITES U-RT-68 per Q1=B + Q1a=(i) + Q2=B2 ratification to consume the new stage-5 factory.

**Source of fix.** `.harness/class_1_fork_u_rt_68_retry_wrap_shape_gap.md` operator-ratified 2026-05-22 at this session:
- **Q1=B** — new sibling class `RetryBreakerToolDispatcher` (retry-only, no fallback chain, per-tool/server breaker scope deferred per Q1a)
- **Q1a=(i)** — retry-only MVP at v1.15; no breaker; breaker semantics deferred to future OD-axis-coordinated arc to avoid `BreakerScope` 2-value enum extension which would route to OD spec v1.10 + ADR-D6 v1.3 back-flow with U-OD-09 conformance break + OTel cardinality bump
- **Q2=B2** — decompose bootstrap-wiring chain into new atomic units U-RT-71..N (preserves atomic-unit discipline; ~600 LOC scope distributed across 5 units rather than collapsed into expanded U-RT-68 AC scope)
- **Q3=yes** — full U-RT-68 deferral at filing arc accepted (no code landed at L9-sexies cluster close 2026-05-22 commit `e2cada0`)
- **Q4=now** — resolution arc opens this session

**Spec authority chain.** Runtime spec v1.15 §3 C-RT-02 (RuntimeConfig schema extension) + §4 C-RT-04 (HarnessContext field extension) + §14.9.3 (stage-3a + stage-5 factory contracts) + §14.11 C-RT-21 (RetryBreakerToolDispatcher sibling carrier) + ADR-F4 v1.1 + ADR-D2 v1.2 + ADR-D6 v1.2. CP spec v1.11 §27 (PerServerTrustEvaluator + MCPClientNamespaceEmitter producer-side carriers) cross-axis consumed at U-RT-75 factory body.

**Plan shape preserved.** v2.11's axis-led structure preserved verbatim. New units land at L9-septies cluster (post-L9-sexies sequencing); rewritten U-RT-68 remains structurally located at L9-sexies but consumes the new L9-septies factory U-RT-75.

**Sections preserved verbatim from v2.11.** §1 — L9-sexies cluster — all units U-RT-63 / U-RT-64 / U-RT-65 / U-RT-66 / U-RT-67 / U-RT-69 / U-RT-70 preserved verbatim. **EXCEPTION: U-RT-68 REWRITTEN at v2.12** — per Q1=B + Q1a=(i) + Q2=B2 ratification 2026-05-22; new body at §1 below. v2.11 + v2.10 + v2.9 + ... + v2.0 + v2 chain preserved.

**Status posture.** Proposed (v2.11) → Proposed (v2.12). v2.12 is an additive-plus-rewrite patch — 5 new atomic units (U-RT-71..75) + 1 rewritten unit (U-RT-68); no other v2.11 unit re-decomposition.

**Downstream absorption owed (post-v2.12).**
(a) Workspace `CLAUDE.md` §2.3 runtime spec row version bump (v1.14 → v1.15).
(b) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.11 → v2.12); unit count 71 → 76 (U-RT-00..U-RT-70 + U-RT-71..U-RT-75).
(c) Phase 7 cluster-open authorization for L9-septies at next session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-sexies closes 7/8 (U-RT-68 deferred at L9-sexies; lands at L9-septies close per dependency on U-RT-75).
(d) NO CXA v2.8 amendment owed at this arc per fork doc §5 (ZERO cross-axis cascade). U-RT-75 factory body consumes already-landed CP spec v1.11 §27 carriers (cluster 10-CP-C commits) without new CXA edge introduction.
(e) NO CP / OD / AS plan amendments owed at this arc per fork doc §5 (ZERO cross-axis cascade).

---

## §1 — L9-sexies cluster — Tool-invocation + HITL webhook composers (preserved verbatim from v2.11 EXCEPT U-RT-68 REWRITTEN)

**Cluster scope.** 8 units materializing C-RT-19 (RuntimeToolDispatcher + MCPClientHost) + C-RT-20 (WebhookDeliveryComposer + OperatorBurdenEvaluator). Cluster opens post-U-RT-62 (FastMCP H_T-as-MCP-server arc). Cluster anchor: workflow_driver.py:379 step-dispatcher table extension for TOOL_STEP.

### U-RT-63 — MCPClientHost class skeleton + transport selector

- **Implements:** Runtime spec v1.13 §14.9.1 architectural surfaces (`MCPClientHost` class declaration; `MCPHostHealth` dataclass; transport selection per per-server bootstrap config)
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py` (NEW)
- **Signatures:** `class MCPClientHost`, `@dataclass(frozen=True) class MCPHostHealth`, transport enum check at `start()` constructor preconditions
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `MCPClientHost.__init__` accepts `transport: Literal["stdio", "streamable_http", "sse"]` + per-transport config; raises `ValueError` on unknown transport
  2. `MCPHostHealth` dataclass instantiable with all 6 fields per §14.9.1
  3. `tool_registry` property raises `MCPHostNotStartedError` before `start()` invocation
  4. Importable; pyright strict mode passes
  5. Unit test coverage ≥ 90% on the class skeleton

### U-RT-64 — MCPClientHost.start() STDIO subprocess lifecycle + list_tools population

- **Implements:** Runtime spec v1.13 §14.9.1 (STDIO startup branch) + §14.9.5 fail class `RT-FAIL-MCP-HOST-STARTUP`
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py` (EXTEND)
- **Signatures:** `async def start(self) -> None` STDIO branch; subprocess spawn via `mcp` Python SDK (CLAUDE.md §3.1 commitment)
- **Depends on:** [U-RT-63]
- **ACs:**
  1. STDIO subprocess spawns + protocol handshake completes (protocol_version="2025-06-18")
  2. `list_tools` populates `ToolRegistry` (count > 0 for valid server)
  3. `start()` failure raises `RT-FAIL-MCP-HOST-STARTUP` with subprocess stderr captured
  4. Idempotent re-`start()` raises `MCPHostAlreadyStartedError`
  5. Integration test against mock MCP server passes

### U-RT-65 — MCPClientHost HTTP transport implementation

- **Implements:** Runtime spec v1.13 §14.9.1 (HTTP transport branch — Decision 1.D4 RATIFIED scope expansion) + §14.9.6 invariant 5
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py` (EXTEND)
- **Signatures:** `start()` HTTP branch; HTTP client + connection pool via `httpx` stdlib-adjacent or operator-supplied
- **Depends on:** [U-RT-63]
- **ACs:**
  1. HTTP transport opens client connection pool + completes auth handshake (if configured)
  2. `list_tools` via HTTP POST populates `ToolRegistry`
  3. `health_check()` via `GET /health` returns `MCPHostHealth(alive=True, ...)` on success
  4. `shutdown()` closes connection pool gracefully
  5. Integration test: HTTP mock server returns 200 + protocol_version="2025-06-18" on handshake; list_tools returns >= 1 tool; health_check returns alive=True; shutdown closes connections without leak

### U-RT-66 — MCPClientHost SSE transport implementation

- **Implements:** Runtime spec v1.13 §14.9.1 (SSE transport branch — Decision 1.D4 scope expansion)
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/mcp_client_host.py` (EXTEND)
- **Signatures:** `start()` SSE branch; event-stream consumer
- **Depends on:** [U-RT-63]
- **ACs:**
  1. SSE transport opens event stream + completes handshake
  2. `list_tools` populates `ToolRegistry` via SSE event channel
  3. `health_check()` returns `MCPHostHealth(alive=True, transport="sse", ...)` while event stream open
  4. `shutdown()` closes event stream gracefully
  5. Integration test: SSE mock server emits handshake event; list_tools returns >= 1 tool; health_check returns alive=True while stream open; shutdown closes stream without dangling connection

### U-RT-67 — RuntimeToolDispatcher.dispatch() body + sandbox span emission

- **Implements:** Runtime spec v1.13 §14.9.1 RuntimeToolDispatcher dispatch surface + §14.9.4 span emission (`tool.dispatch` + `sandbox.enter` + `mcp.tool.call` + `sandbox.violation` + `sandbox.exit`)
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` (NEW)
- **Signatures:** `class RuntimeToolDispatcher`, `async def dispatch(binding, step, *, step_context) -> StepOutput`
- **Depends on:** [U-RT-63, U-CP-68 (cross-axis: CP), U-CP-69 (cross-axis: CP)]
- **Requires at end-to-end landing:** at-least-one-of {U-RT-64, U-RT-65, U-RT-66} (per-server transport selection per runtime spec v1.13 §14.9.6 invariant 5 — one transport per `MCPClientHost`; U-RT-67 only needs U-RT-63 skeleton at unit-implementation time; integration tests against any single transport unit satisfy the dispatch path)
- **ACs:**
  1. Dispatch resolves `ToolContract` from `ctx.mcp_client_host.tool_registry` by `step.tool_id`; raises `RT-FAIL-TOOL-CONTRACT-UNKNOWN` on miss
  2. Per-server-trust evaluation invoked pre-call; raises `RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION` on deny
  3. `sandbox.*` 7-attribute namespace emitted on `sandbox.enter` per C-AS-15 §15
  4. `mcp.*` 7-attribute namespace emitted on `mcp.tool.call` per C-AS-14 §14.3 (via `MCPClientNamespaceEmitter`)
  5. Schema validation at both directions (input + output); raises `RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION` on breach

### U-RT-68 — Stage 5 TOOL_STEP wire-up via materialize_runtime_tool_dispatcher_stage factory (REWRITTEN at v2.12)

- **Rewrite provenance.** v2.11 shape STRUCK at U-RT-68 deferral arc 2026-05-22 (commit `e2cada0`). Original v2.11 AC #2 pinned literal `RetryBreakerFallbackDispatcher` reuse for tool-dispatch wrap, but the class is hard-typed to LLM-fallback shapes per fork doc §1. v2.12 shape per Q1=B + Q1a=(i) + Q2=B2 ratification 2026-05-22: U-RT-68 becomes the thin "stage-5 callsite invocation" unit consuming the new `materialize_runtime_tool_dispatcher_stage` factory authored at U-RT-75 (L9-septies cluster). All composition logic (wrap construction, ctx binding) moves into the factory body per atomic-discipline single-coherent-change criterion.
- **Implements:** Runtime spec v1.15 §14.9.3 stage-5 lifecycle placement (factory invocation + step-dispatcher table extension at `TOOL_STEP`); workflow-driver branching unchanged at `workflow_driver.py:379`.
- **Files:** `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (EXTEND).
- **Signatures:** Stage 5 body invokes `materialize_runtime_tool_dispatcher_stage(ctx, config)` (factory authored at U-RT-75; per spec v1.15 §14.9.3); factory return value binds to `ctx.tool_dispatcher` per factory body step 5. Step-dispatcher table updated: `TOOL_STEP → ctx.tool_dispatcher`.
- **Depends on:** [U-RT-75, U-RT-67] (factory body + bare RuntimeToolDispatcher class). U-RT-75's own dependency chain (U-RT-71 + U-RT-72 + U-RT-74 + U-CP-68 + U-CP-69) is transitively closed at U-RT-75; U-RT-68 declares only direct deps per dependency-graph discipline §7.
- **ACs:**
  1. Stage 5 body invokes `materialize_runtime_tool_dispatcher_stage(ctx, config)` exactly once during bootstrap, positioned after stage-5 LLM-dispatcher binding (mirrors existing `"llm_dispatch"` wrap site).
  2. Factory return value (a `RetryBreakerToolDispatcher` wrapper per spec v1.15 §14.11) binds to `ctx.tool_dispatcher`. The bare `RuntimeToolDispatcher` is NOT surfaced on `HarnessContext` at v1.15 (private constructor arg of the wrapper per spec v1.15 §14.9.6 invariant 6).
  3. Step-dispatcher table extended: `TOOL_STEP → ctx.tool_dispatcher`. Existing `INFERENCE_STEP → ctx.llm_dispatcher` binding preserved verbatim.
  4. `workflow_driver.py:379` invocation for `step.step_kind == TOOL_STEP` resolves to the wrapper via the typed step-dispatcher table without new conditional in `workflow_driver.py` body (per spec v1.15 §14.9.3 workflow-driver branching paragraph).
  5. End-to-end test: 2-step workflow with INFERENCE_STEP + TOOL_STEP both dispatch correctly through their respective C-RT-16 / C-RT-21 wrappers; both wrap-spans (`harness.runtime.retry_breaker_fallback` for LLM + `harness.runtime.retry_tool_dispatch` for tool) emit in trace output.

### U-RT-69 — WebhookDeliveryComposer + WebhookDeliveryResult carriers

- **Implements:** Runtime spec v1.13 §14.10.1 architectural surfaces (`WebhookDeliveryComposer` class + `WebhookDeliveryResult` dataclass) + §14.10.3 spans (`hitl.webhook.deliver` + `hitl.webhook.attempt`) + §14.10.4 fail classes (3 new)
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (NEW)
- **Signatures:** `class WebhookDeliveryComposer`, `async def deliver_webhook(webhook_config, payload, idempotency_key) -> WebhookDeliveryResult`, `@dataclass(frozen=True) class WebhookDeliveryResult`
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `deliver_webhook()` posts to webhook URL with idempotency-key header; retries per `ctx.retry_breaker.get_policy("hitl_webhook")`
  2. `hitl.webhook.deliver` outer span emits with 3 attributes (`webhook.url_hash`, `webhook.delivery_attempts`, `webhook.idempotency_key`)
  3. `hitl.webhook.attempt` per-attempt span emits with 3 attributes
  4. All retry attempts failed → raises `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED`
  5. Mock HTTP server integration test: 3 attempts, 2 failures + 1 success → returns `WebhookDeliveryResult(delivered=True, delivery_attempts=3)`

### U-RT-70 — OperatorBurdenEvaluator + DegradationDecision carriers

- **Implements:** Runtime spec v1.13 §14.10.1 (`OperatorBurdenEvaluator` class + `OperatorBurdenScore` + `DegradationDecision` + `SpanWindow` dataclasses) + §14.10.3 spans (`hitl.operator_burden.evaluated`) + §14.10.4 fail class `RT-FAIL-HITL-OPERATOR-BURDEN-DEGRADATION-CONFLICT`
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/operator_burden_evaluator.py` (NEW)
- **Signatures:** `class OperatorBurdenEvaluator`, `async def compute_operator_burden(span_window, persona_tier)`, `async def should_degrade(score, degradation_policy)`
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `compute_operator_burden()` aggregates HITL spans within `span_window` per `persona_tier` configuration
  2. `should_degrade()` returns `DegradationDecision(degrade=True, ...)` when cumulative_invocations exceeds policy threshold
  3. `hitl.operator_burden.evaluated` span emits with 4 attributes per §14.10.3 (single span per F1-03 absorption)
  4. Sampling: head=1.0 on `degrade=true`; else head=0.1
  5. Burden window default 1-hour rolling; tunable via `ctx.surface_config.burden_window_overrides`

---

## §1B — L9-septies cluster — Bootstrap-wiring chain (NEW at v2.12)

**Cluster scope.** 5 NEW units decomposing the Q2=B2-ratified bootstrap-wiring chain per runtime spec v1.15 §3 + §4 + §14.9.3 + §14.11 contract authority. Materializes the operator-config-to-runtime-instance wiring chain that was undecomposed at L9-sexies cluster close. Cluster opens at U-RT-68 fork resolution arc landing (this session); enables U-RT-68 wire-up landing per dependency chain.

### U-RT-71 — RuntimeConfig schema extension: trust_policy + sandbox_decision_policy optional fields

- **Implements:** Runtime spec v1.15 §3 C-RT-02 field-table extension (rows for `trust_policy: TrustPolicy | None` + `sandbox_decision_policy: SandboxDecisionPolicy | None`). Both fields default `None` → factories use type defaults (`TrustPolicy.default()` + `SandboxDecisionPolicy.default()`).
- **Files:** `harness-runtime/src/harness_runtime/config.py` (EXTEND — `RuntimeConfig` Pydantic v2 BaseModel field-table extension).
- **Signatures:** `class RuntimeConfig`: append optional fields `trust_policy: TrustPolicy | None = None` + `sandbox_decision_policy: SandboxDecisionPolicy | None = None`. `TrustPolicy` imported from CP package per CP spec v1.11 §27 carrier home. `SandboxDecisionPolicy` imported from AS package per AS spec v1.3 §15 carrier home.
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `RuntimeConfig(deployment_surface=..., ..., trust_policy=None, sandbox_decision_policy=None)` instantiates without ValidationError.
  2. `RuntimeConfig(...)` instantiated WITHOUT the new fields preserves v1.14-shape backwards-compatibility (both fields default to `None` per Pydantic field default; existing callers do not break).
  3. `RuntimeConfig(..., trust_policy=TrustPolicy(...), ...)` accepts an operator-supplied TrustPolicy instance and stores it on the frozen model.
  4. `RuntimeConfig(..., trust_policy="not_a_policy", ...)` raises typed `ValidationError` per Pydantic field validation (type mismatch).
  5. Importable; pyright strict mode passes. Per-field minor-version-bump invariant per C-RT-02 v1.1 version-evolution clause preserved (both new fields are optional → minor bump v1.14 → v1.15).

### U-RT-72 — HarnessContext schema extension: 4 new fields for tool-dispatch chain

- **Implements:** Runtime spec v1.15 §4 C-RT-04 field-table extension (rows for `mcp_client_host: MCPClientHost` stage 3a + `tool_dispatcher: RetryBreakerToolDispatcher` stage 5 + `per_server_trust_evaluator: PerServerTrustEvaluator` stage 5 + `mcp_namespace_emitter: MCPClientNamespaceEmitter` stage 5).
- **Files:** `harness-runtime/src/harness_runtime/context.py` (EXTEND — `HarnessContext` Pydantic v2 BaseModel field-table extension; `_MutableHarnessContext` builder extended in parallel).
- **Signatures:** `class HarnessContext`: append fields `mcp_client_host: MCPClientHost` + `tool_dispatcher: RetryBreakerToolDispatcher` + `per_server_trust_evaluator: PerServerTrustEvaluator` + `mcp_namespace_emitter: MCPClientNamespaceEmitter`. Forward references resolved at module-load via class registration (mirrors existing pattern for `EngineSelector` / `FallbackChain` etc.).
- **Depends on:** [U-RT-63 (MCPClientHost class), U-RT-74 (RetryBreakerToolDispatcher class), U-CP-68 (cross-axis: CP — PerServerTrustEvaluator class), U-CP-69 (cross-axis: CP — MCPClientNamespaceEmitter class)]
- **ACs:**
  1. `HarnessContext` frozen-model instantiation with all 4 new fields present at the appropriate post-bootstrap stages produces a valid model instance.
  2. `_MutableHarnessContext` builder accepts setter calls for all 4 new fields during bootstrap; finalize() into frozen `HarnessContext` succeeds when all 4 fields are populated.
  3. `_MutableHarnessContext` finalize() raises typed `ValidationError` if any of the 4 new fields is `None` at finalize-time (per spec §4 invariant "Every field is non-`None` at stage 7 EXCEPT `mcp_clients` and `tenant_id`-derived audit-writer scoping").
  4. Distinct-primitive invariant verified at test: `ctx.mcp_host` (server-side FastMCP per stage 2) is NOT the same object as `ctx.mcp_client_host` (client-side per stage 3a).
  5. Importable; pyright strict mode passes; existing HarnessContext callers (every U-RT-NN consumer reaching `ctx.X` field) continue to type-check.

### U-RT-73 — Stage 3a factory: materialize_mcp_client_host_stage(config) → MCPClientHost

- **Implements:** Runtime spec v1.15 §14.9.3 stage-3a factory contract. Factory ingests `config.mcp_clients: list[MCPClientConfig]` (per-server transport_config; existing field preserved from v1.14) and constructs an `MCPClientHost` instance per the per-server transport selection per spec §14.9.1.
- **Files:** `harness-runtime/src/harness_runtime/bootstrap/stage_3a_loop_init_prereqs.py` (EXTEND — add factory function + invocation site in stage-3a body) + `harness-runtime/src/harness_runtime/bootstrap/factories/mcp_client_host_factory.py` (NEW — factory body module).
- **Signatures:** `async def materialize_mcp_client_host_stage(config: RuntimeConfig) -> MCPClientHost`. Factory body: instantiate `MCPClientHost(transport=config.mcp_clients[i].transport, ...)` per per-server entry; if `config.mcp_clients` is empty, return a sentinel `MCPClientHost.empty()` (no servers — tool dispatch attempts will raise `RT-FAIL-TOOL-CONTRACT-UNKNOWN` at dispatch time per spec §14.9.5).
- **Depends on:** [U-RT-71 (config field for type discipline), U-RT-72 (ctx field to bind into), U-RT-63 (MCPClientHost class), U-RT-64 (start() STDIO branch — host startup), U-RT-65 (start() HTTP branch), U-RT-66 (start() SSE branch)]
- **ACs:**
  1. `materialize_mcp_client_host_stage(config)` returns an `MCPClientHost` instance when `config.mcp_clients` is non-empty.
  2. Empty `config.mcp_clients` → returns `MCPClientHost.empty()` sentinel (or per-axis discretion: a host with empty `tool_registry`); does NOT raise.
  3. Stage 3a body invokes the factory exactly once during bootstrap; binds return value to `ctx.mcp_client_host` via the `_MutableHarnessContext` builder.
  4. Factory-startup failure (per spec §14.9.5 `RT-FAIL-MCP-HOST-STARTUP`) propagates out of stage 3a → bootstrap aborts per spec §14.9.3 (fail-closed per ADR-F4 v1.1 §Consequences (c)).
  5. Per-server transport heterogeneity supported: a config with 2 servers (1 STDIO + 1 HTTP) results in an `MCPClientHost` with both transports' `tool_registry` populated (integration test).

### U-RT-74 — RetryBreakerToolDispatcher class body (C-RT-21 §14.11 materialization)

- **Implements:** Runtime spec v1.15 §14.11 C-RT-21 contract — `RetryBreakerToolDispatcher` sibling carrier to §14.6 C-RT-16 `RetryBreakerFallbackDispatcher`. Retry-only semantics (no fallback chain, no breaker at v1.15 MVP per Q1a=(i) ratification). New fail class `RT-FAIL-TOOL-RETRY-EXHAUSTED` added to §14 taxonomy.
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_tool.py` (NEW — sibling to existing `retry_breaker_fallback.py` per spec §14.11 composer module residence).
- **Signatures:** `class RetryBreakerToolDispatcher`: `inner: StepDispatcher` (bare RuntimeToolDispatcher); `retry_breaker: RetryBreakerRegistry`; `tracer_provider: Any`. `async def dispatch(binding, step, *, step_context) -> StepOutput` body per spec §14.11 step-by-step (lookup `"tool_dispatch"` policy → start outer span `harness.runtime.retry_tool_dispatch` → per-attempt loop with inner span `harness.runtime.tool_retry_attempt` carrying canonical `retry.*` 6-attribute namespace → success/transient-retry/fail-fast/exhaustion paths). NEW typed `RetryToolExhaustedError` mapped to `RT-FAIL-TOOL-RETRY-EXHAUSTED` fail class per spec §14.11 fail-mode taxonomy.
- **Depends on:** (none within this delta) [HIGH] — wrapper consumes existing `RetryBreakerRegistry` API (`get_policy` + `advance_staircase`) per spec §14.11; the inner-dispatcher reference is supplied at construction time (typed against `StepDispatcher` Protocol so no concrete-class compile-time dep on RuntimeToolDispatcher).
- **ACs:**
  1. `RetryBreakerToolDispatcher(inner=<mock_step_dispatcher>, retry_breaker=<registry_with_tool_dispatch_policy>, tracer_provider=<test_tracer>)` instantiable.
  2. Successful inner dispatch on first attempt: outer span `harness.runtime.retry_tool_dispatch` + inner span `harness.runtime.tool_retry_attempt` (attempt_number=1, terminal="success") both emit; wrapper returns inner's `StepOutput` verbatim.
  3. Transient-fail then success on attempt 2: 2 inner spans emit (attempt_number=1 terminal="retry" + attempt_number=2 terminal="success"); jittered backoff sleep occurs between attempts per `compute_full_jitter_delay_seconds`.
  4. `max_attempts` exhaustion on `RT-FAIL-TOOL-INVOCATION-TIMEOUT` (the transient class per §14.9.5): `tool_retry.exhausted` event emitted on outer span; raises `RetryToolExhaustedError` mapped to `RT-FAIL-TOOL-RETRY-EXHAUSTED`.
  5. Fail-fast on permanent fail class (`RT-FAIL-TOOL-INVOCATION-PROTOCOL-ERROR`): single inner span emits with terminal="fail-fast"; wrapper re-raises the typed error verbatim (no retry consumption).
  6. NO breaker interaction at v1.15: wrapper does NOT call `ctx.retry_breaker.get_breaker(...)` or `breaker.record_failure()` / `record_success()`; no `harness.breaker.*` namespace emission from this composer (verified by negative-assertion test).
  7. NO fallback-chain interaction at v1.15: wrapper does NOT consume `ctx.fallback_chain`; does NOT emit `fallback.exhausted`; does NOT iterate `ProviderCandidate` (verified by absence-of-import test).
  8. Wrapper satisfies `isinstance(wrapper, StepDispatcher)` via `@runtime_checkable` introspection.

### U-RT-75 — Stage 5 factory: materialize_runtime_tool_dispatcher_stage(ctx, config) → RetryBreakerToolDispatcher

- **Implements:** Runtime spec v1.15 §14.9.3 stage-5 factory contract — 5-step composition body: (1) construct `PerServerTrustEvaluator` consuming `config.trust_policy`; (2) construct `MCPClientNamespaceEmitter` consuming `ctx.mcp_client_host.tool_registry`; (3) construct bare `RuntimeToolDispatcher` with ctx refs + `config.sandbox_decision_policy`; (4) construct `RetryBreakerToolDispatcher` per §14.11 wrapping the bare dispatcher; (5) bind wrapper to `ctx.tool_dispatcher`.
- **Files:** `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py` (NEW — factory body module; mirrors existing factory-module pattern at `harness-runtime/src/harness_runtime/bootstrap/factories/`).
- **Signatures:** `async def materialize_runtime_tool_dispatcher_stage(ctx: _MutableHarnessContext, config: RuntimeConfig) -> RetryBreakerToolDispatcher`. Factory body executes 5 steps verbatim per spec §14.9.3 stage-5 prose; binds intermediate carriers to `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` during composition; returns the wrapper for the stage-5 callsite (U-RT-68) to bind to `ctx.tool_dispatcher`.
- **Depends on:** [U-RT-71 (config fields), U-RT-72 (ctx fields), U-RT-67 (bare RuntimeToolDispatcher class), U-RT-74 (RetryBreakerToolDispatcher wrapper class), U-CP-68 (cross-axis: CP — PerServerTrustEvaluator), U-CP-69 (cross-axis: CP — MCPClientNamespaceEmitter)]
- **ACs:**
  1. `materialize_runtime_tool_dispatcher_stage(ctx, config)` with valid ctx (post-stage-3a) + config returns a `RetryBreakerToolDispatcher` instance.
  2. Factory step 1: `ctx.per_server_trust_evaluator` bound to a `PerServerTrustEvaluator` instance consuming `config.trust_policy` (or `TrustPolicy.default()` if `None`).
  3. Factory step 2: `ctx.mcp_namespace_emitter` bound to an `MCPClientNamespaceEmitter` instance consuming `ctx.mcp_client_host.tool_registry`.
  4. Factory step 3: a bare `RuntimeToolDispatcher` constructed with refs to `ctx.mcp_client_host` + `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` + `config.sandbox_decision_policy` (or `SandboxDecisionPolicy.default()`); NOT bound to `ctx.tool_dispatcher` (private to wrapper).
  5. Factory step 4: a `RetryBreakerToolDispatcher` constructed wrapping the bare dispatcher with `inner=<bare_dispatcher>` + `retry_breaker=ctx.retry_breaker` + `tracer_provider=ctx.tracer_provider`.
  6. Factory step 5: returns the wrapper (caller U-RT-68 binds to `ctx.tool_dispatcher`).
  7. Integration test: full stage-3a + stage-5 invocation with mock MCP server config produces a wired `ctx.tool_dispatcher` that dispatches a known tool through wrapper → bare dispatcher → MCP host successfully; all 4 ctx fields populated post-factory.

---

## §2 — DAG topology delta (v2.11 → v2.12)

5 new units added at L9-septies cluster + 1 rewritten unit (U-RT-68 dependency edges changed). Topological sort preserved acyclic:

```
L9-septies (new at v2.12):
  L0-within-delta: U-RT-71 (no deps within delta), U-RT-74 (no deps within delta —
                   RetryBreakerRegistry consumed from existing infra; StepDispatcher Protocol from existing infra)
  L1-within-delta: U-RT-72 (←74 for tool_dispatcher field type annotation; ←63 L9-sexies for mcp_client_host
                   field type; ←U-CP-68/69 cross-axis for per_server_trust_evaluator + mcp_namespace_emitter field types)
  L2-within-delta: U-RT-73 (←71, ←72, ←63 L9-sexies, ←64/65/66 L9-sexies for transport branches),
                   U-RT-75 (←71, ←72, ←67 L9-sexies, ←74, ←U-CP-68 cross-axis, ←U-CP-69 cross-axis)

L9-sexies (rewrite delta):
  L3-within-delta: U-RT-68 REWRITTEN (←75 L9-septies, ←67 L9-sexies) — dependency edges replaced
                   (v2.11 deps [63, 67] → v2.12 deps [75, 67])
```

Cross-axis edges: U-RT-75 depends on U-CP-68 + U-CP-69 (already cross-axis at U-RT-67 in v2.11). NO new cross-axis edges introduced at v2.12 per fork doc §5 (ZERO cross-axis cascade). U-RT-72 also cross-edges to U-CP-68 + U-CP-69 (HarnessContext field type imports) — same producer-side carriers; no new edge count delta in CXA v2.8 (relationship cardinality preserved at producer-side per existing CXA §2.3 rows).

DAG verified acyclic via Kahn execution (delta layer): 5 new units consumed + 1 rewritten unit re-consumed; remaining edge set ∅.

---

## §3 — Coverage matrix delta (v2.11 → v2.12)

| Contract (spec v1.15) | Units covering | Change at v2.12 |
|---|---|---|
| C-RT-02 §3 RuntimeConfig (2 new optional fields) | U-RT-71 | NEW row at v2.12 |
| C-RT-04 §4 HarnessContext (4 new fields) | U-RT-72 | NEW row at v2.12 |
| C-RT-19 §14.9.1 architectural surfaces | U-RT-63 | preserved verbatim from v2.11 |
| C-RT-19 §14.9.1 STDIO transport | U-RT-64 | preserved verbatim from v2.11 |
| C-RT-19 §14.9.1 HTTP transport | U-RT-65 | preserved verbatim from v2.11 |
| C-RT-19 §14.9.1 SSE transport | U-RT-66 | preserved verbatim from v2.11 |
| C-RT-19 §14.9.2 dispatch body + §14.9.4 span emission | U-RT-67 | preserved verbatim from v2.11 |
| C-RT-19 §14.9.3 stage-3a lifecycle placement (factory) | U-RT-73 | NEW row at v2.12 (was implicit at U-RT-68 v2.11; factory body moved out per Q2=B2 decomposition) |
| C-RT-19 §14.9.3 stage-5 lifecycle placement (factory body) | U-RT-75 | NEW row at v2.12 |
| C-RT-19 §14.9.3 stage-5 lifecycle placement (callsite invocation + step-dispatcher table extension) | U-RT-68 (REWRITTEN at v2.12) | row preserved; AC body replaced per rewrite |
| C-RT-20 §14.10 WebhookDeliveryComposer | U-RT-69 | preserved verbatim from v2.11 |
| C-RT-20 §14.10 OperatorBurdenEvaluator | U-RT-70 | preserved verbatim from v2.11 |
| C-RT-21 §14.11 RetryBreakerToolDispatcher class body | U-RT-74 | NEW row at v2.12 |
| C-RT-21 §14.11 fail class `RT-FAIL-TOOL-RETRY-EXHAUSTED` | U-RT-74 (AC #4) | covered by U-RT-74 |

All v1.15 spec amendments covered by ≥ 1 unit. ✓
All v2.11-preserved units retain ≥ 1 contract citation. ✓
Coverage gap audit: none surfaced at coherence pass.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_12.md` |
| Version | v2.12 |
| Filing event | U-RT-68 Class 1 fork resolution arc absorption pass; runtime spec v1.14 → v1.15 co-published; 2026-05-22 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_11.md` (v2.11 substantive content preserved verbatim EXCEPT U-RT-68 rewritten per Q1=B + Q1a=(i) + Q2=B2 ratification 2026-05-22) |
| New units | 5 (U-RT-71 through U-RT-75) |
| Rewritten units | 1 (U-RT-68 — per fork ratification 2026-05-22) |
| Cluster | L9-septies (NEW at v2.12); L9-sexies preserved with U-RT-68 rewritten |
| Cross-axis dependencies | 2 new edges (U-RT-72 + U-RT-75 → U-CP-68; U-RT-72 + U-RT-75 → U-CP-69); NO new CXA v2.8 edge enumeration count delta per fork doc §5 (same producer-side carriers as existing U-RT-67 cross-axis edges; relationship cardinality preserved) |
| DAG verification | Kahn-acyclic; 5 new units consumed + 1 rewritten unit re-consumed; ∅ remaining edges |
| Coverage verification | All v1.15 spec amendments covered ≥ 1 unit; all v2.11-preserved units retain ≥ 1 contract citation |
| Fork ratification | `.harness/class_1_fork_u_rt_68_retry_wrap_shape_gap.md` RATIFIED 2026-05-22 |
| Date | 2026-05-22 |
