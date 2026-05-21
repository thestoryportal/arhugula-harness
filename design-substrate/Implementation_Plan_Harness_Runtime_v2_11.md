# Implementation Plan — Harness Runtime v2.11

## Change-note (v2.10 → v2.11)

**Scope of revision.** Phase C atomic-unit decomposition pass per Remaining-Work Closure Arc plan file. Absorbs runtime spec v1.13 (§14.9 C-RT-19 + §14.10 C-RT-20). Adds 8 new atomic units (U-RT-63 through U-RT-70). v2.10 substantive content (U-RT-00 through U-RT-62, all clusters, DAG topology, coverage matrix) preserved verbatim. No re-decomposition of existing units; no signature change to any v2.10 unit; no contract removal.

**Source of fix.** Plan-orchestrated Remaining-Work Closure Arc, Phase C with prerequisites:
- Phase A.2 + B (runtime spec v1.12 → v1.13 with new §14.9 + §14.10).
- Phase B iteration-2 absorption: F2-01 transport-neutral terminology (STDIO + HTTP + SSE all in scope at v1).

**Spec authority chain.** Runtime spec v1.13 §14.9 (C-RT-19 RuntimeToolDispatcher + MCPClientHost) + §14.10 (C-RT-20 WebhookDeliveryComposer + OperatorBurdenEvaluator) + ADR-F4 v1.1 + ADR-D2 v1.2 + ADR-D5 v1.4 + ADR-D6 v1.2.

**Plan shape preserved.** v2.10's axis-led structure preserved verbatim. New units land at L9-sexies cluster (post-U-RT-62 sequencing).

**Sections preserved verbatim from v2.10.** All v2.10 content outside the new L9-sexies cluster preserved verbatim. v2.10 + v2.9 + v2.8 + ... + v2.0 + v2 chain preserved.

**Status posture.** Proposed (v2.10) → Proposed (v2.11). v2.11 is an additive patch — 8 new atomic units; no v2.10 unit re-decomposition.

**Downstream absorption owed (post-v2.11).**
(a) Workspace `CLAUDE.md` §2.4 runtime row version bump (v2.10 → v2.11).
(b) Phase 7 cluster-open authorization at next session per `phase-7-implementation` skill discipline.

---

## §1 — L9-sexies cluster — Tool-invocation + HITL webhook composers (NEW at v2.11)

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

### U-RT-68 — Stage 5 TOOL_STEP binding + retry-wrap registry key

- **Implements:** Runtime spec v1.13 §14.9.3 lifecycle placement (stage 5 binding + step-dispatcher table extension) + C-RT-16 §14.6 D6 registry key `"tool_dispatch"`
- **Files:** `harness-runtime/src/harness_runtime/bootstrap/stage_5_loop_init.py` (EXTEND)
- **Signatures:** Stage 5 instantiates `RuntimeToolDispatcher`; rebinds via `RetryBreakerFallbackDispatcher(inner=tool_dispatcher)`; updates step-dispatcher table `TOOL_STEP → ctx.tool_dispatcher`
- **Depends on:** [U-RT-63, U-RT-67]
- **ACs:**
  1. Stage 5 invocation instantiates `RuntimeToolDispatcher` bound to `ctx.tool_dispatcher`
  2. Retry-wrap composition: `RetryBreakerFallbackDispatcher` with registry key `"tool_dispatch"` (matches `"llm_dispatch"` convention)
  3. `step_dispatchers.lookup(TOOL_STEP)` returns the wrapped dispatcher
  4. workflow_driver.py:379 invocation for `step.step_kind == TOOL_STEP` exercises full dispatch path
  5. End-to-end test: 2-step workflow with INFERENCE_STEP + TOOL_STEP both dispatch correctly

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

## §2 — DAG topology delta (v2.10 → v2.11)

8 new units added at L9-sexies cluster. Topological sort preserved acyclic:

```
L9-sexies (new at v2.11):
  L0-within-delta: U-RT-63, U-RT-69, U-RT-70 (no deps within delta)
  L1-within-delta: U-RT-64 (←63), U-RT-65 (←63), U-RT-66 (←63)
  L2-within-delta: U-RT-67 (←64/65/66 + U-CP-68/69 cross-axis)
  L3-within-delta: U-RT-68 (←63 + 67)
```

Cross-axis edges: U-RT-67 depends on U-CP-68 + U-CP-69 (CP plan v2.15 co-publication).

DAG verified acyclic via Kahn execution; 8 units consumed; remaining edge set ∅.

---

## §3 — Coverage matrix delta (v2.10 → v2.11)

| Contract | Units covering |
|---|---|
| C-RT-19 §14.9.1 (architectural surfaces) | U-RT-63 |
| C-RT-19 §14.9.1 (STDIO transport) | U-RT-64 |
| C-RT-19 §14.9.1 (HTTP transport) | U-RT-65 |
| C-RT-19 §14.9.1 (SSE transport) | U-RT-66 |
| C-RT-19 §14.9.2 (dispatch body) + §14.9.4 (span emission) | U-RT-67 |
| C-RT-19 §14.9.3 (lifecycle stage placement) | U-RT-68 |
| C-RT-20 §14.10 (WebhookDeliveryComposer) | U-RT-69 |
| C-RT-20 §14.10 (OperatorBurdenEvaluator) | U-RT-70 |

All C-RT-19 + C-RT-20 subsections covered by ≥ 1 unit. ✓

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_11.md` |
| Version | v2.11 |
| Filing event | Phase C atomic-unit decomposition pass, Remaining-Work Closure Arc, 2026-05-21 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_10.md` (v2.10 substantive content preserved verbatim) |
| New units | 8 (U-RT-63 through U-RT-70) |
| Cluster | L9-sexies (NEW at v2.11) |
| Cross-axis dependencies | 2 (U-RT-67 → U-CP-68 + U-CP-69) |
| DAG verification | Kahn-acyclic; 8 units consumed; ∅ remaining edges |
| Coverage verification | All C-RT-19 + C-RT-20 contract subsections covered ≥ 1 unit |
| Date | 2026-05-21 |
