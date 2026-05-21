# Phase A.2 — Composer Contract Drafts (FOR OPERATOR RATIFICATION)

**Filed:** 2026-05-21 (Remaining-Work Closure Arc, Phase A sub-arc A.2)
**Mode:** **ARCHITECT-DRAFTS** (NOT spec-writer output). These are candidate contract shapes for operator review + ratification. Once ratified, `spec-writer` applies byte-exact to `design-substrate/` files.
**Authority chain:** ADR-F1 v1.2 / ADR-D1 v1.2 / ADR-D2 v1.2 / ADR-D5 v1.4 / ADR-D6 v1.2 / Runtime spec v1.12 §14.5 (C-RT-15) §14.6 (C-RT-16) §14.7 (C-RT-17) §14.8 (C-RT-18) / CP spec v1.9 / AS spec v1.3 / OD spec v1.7 / CXA v2.5.
**Scope:** 3 composer contracts (LLM-dispatch closed at A.0; Pattern-D inherited per A.1).

---

## How to read this document

Each draft contract has 7 sections:

1. **§ID + Name** — proposed contract ID + name
2. **Scope statement** — one paragraph; what surface this contract owns
3. **Canonical signature(s)** — Python type signatures + key kwargs
4. **Field sets / enums introduced** — typed schemas
5. **Lifecycle stage placement** — where in bootstrap this materializes
6. **Span emission + fail classes** — observability contract + new error taxonomy
7. **Invariants** — what must hold at every dispatch

**Ratification options per contract:** RATIFY (apply byte-exact) / RATIFY-WITH-EDITS (specify deltas) / SEND-BACK (specify what's wrong).

---

# DRAFT 1 — Tool-invocation runtime composer

## §1.1 ID + Name

**Proposed ID:** `C-RT-19` (next contract slot after C-RT-18 HITL gate composer per U-RT-60 landing)
**Proposed name:** `RuntimeToolDispatcher` (mirrors `RuntimeLLMDispatcher` / `RuntimeSubAgentDispatcher` naming)
**Filed at:** Runtime spec v1.12 → v1.13, new §14.9
**Authority anchor:** Class 2 fork C.1 ratified Path X (Phase-7 deferred runtime unit, U-RT-58 shape) per `.harness/class_2_fork_tool_invocation_composer_scope.md` + operator ratification 2026-05-21 in plan file.

## §1.2 Scope statement

`RuntimeToolDispatcher` owns the `TOOL_STEP` dispatch path. Production callsite at `workflow_driver.py:379` invokes the step-dispatcher table; for `step.step_kind == TOOL_STEP`, dispatch resolves to a `RuntimeToolDispatcher` instance bound at bootstrap stage 5. The composer satisfies the same `StepDispatcher` Protocol as `RuntimeLLMDispatcher`, executing: pre-flight per-server-trust gate evaluation, FastMCP `call_tool` invocation against the started subprocess, sandbox-event span emission, post-call result envelope construction, and fail-class composition. The MCP server subprocess lifecycle (start/health/shutdown) is owned by a sibling `MCPClientHost` composer materialized at bootstrap stage 3a (alongside provider construction).

## §1.3 Canonical signature(s)

```python
# Stage 3a — subprocess lifecycle owner (sibling to providers)
class MCPClientHost:
    async def start(self) -> None: ...                 # spawn STDIO subprocess; handshake; populate ToolRegistry via list_tools
    async def health_check(self) -> MCPHostHealth: ...  # liveness probe; called per-dispatch
    async def shutdown(self) -> None: ...              # graceful drain + subprocess termination
    @property
    def tool_registry(self) -> ToolRegistry: ...        # immutable after start()

# Stage 5 — TOOL_STEP dispatcher
class RuntimeToolDispatcher:
    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> StepOutput:
        # 1. Resolve tool contract from ToolRegistry by step.tool_id
        # 2. Per-server-trust gate evaluation (raises ToolInvocationTrustViolation if denied)
        # 3. Open sandbox.enter span; emit sandbox.* 7-attribute namespace
        # 4. Compose idempotency_key per parent step
        # 5. Invoke MCPClientHost.call_tool(name, args, idempotency_key)
        # 6. Close sandbox.exit span; emit mcp.tool.call span with mcp.* 7-attribute namespace
        # 7. Wrap response in StepOutput; return
```

**StepDispatcher Protocol** (existing per C-RT-15 §14.5) — both signatures satisfy:

```python
async def dispatch(binding: StepEffectiveBinding, step: WorkflowStep, *, step_context: StepExecutionContext) -> StepOutput
```

## §1.4 Field sets / enums introduced

**New:** `MCPHostHealth` — typed health envelope:

```python
@dataclass(frozen=True)
class MCPHostHealth:
    alive: bool
    last_ping_ms: int
    protocol_version: str   # "2025-06-18" per C-AS-14
    transport: Literal["stdio", "streamable_http"]
    server_name: str        # per-deployment registry ID
    trust_tier: MCPTrustTier  # from C-CP-00c carrier
```

**Existing (reused, NOT re-authored):**
- `ToolContract` from AS spec C-AS-12 §12 (7-field carrier — `name`, `description`, `input_schema`, `output_schema`, `minimum_tier`, `blast_radius_tier`, `required_secrets`)
- `ToolRegistry` from `harness-as/src/harness_as/tool_contract.py` (lookup surface)
- `MCPTrustTier` from CP plan v2.8 U-CP-00c
- `SandboxTier` from AS spec C-AS-12 §12
- `BlastRadiusTier` from AS spec
- `StepEffectiveBinding` / `WorkflowStep` / `StepExecutionContext` / `StepOutput` from runtime spec §14.4

## §1.5 Lifecycle stage placement

**Stage 3a (LOOP_INIT prereqs):** `MCPClientHost` materialized alongside provider construction. Subprocess spawn + protocol handshake + `list_tools` registry population happen here. Failure to start raises `MCPHostStartupError` → bootstrap aborts (fail-closed per ADR-F4 v1.1 §Consequences (c)).

**Stage 5 (LOOP_INIT):** `RuntimeToolDispatcher` instantiated with reference to `ctx.mcp_client_host`. Bound to `ctx.tool_dispatcher`. Step-dispatcher table updated: `TOOL_STEP → ctx.tool_dispatcher`.

**Workflow-driver branching:** At `workflow_driver.py:379`, step-kind table now resolves both `INFERENCE_STEP → ctx.llm_dispatcher` (U-RT-58 wrapper, existing) and `TOOL_STEP → ctx.tool_dispatcher` (new). No new conditional in workflow_driver — dispatch dispatched via existing typed table.

## §1.6 Span emission + fail classes

**Spans emitted per dispatch (nested, in order):**

1. `tool.dispatch` (outer envelope; mirrors `harness.runtime.retry_breaker_fallback` shape) — covers full envelope; attributes: `step.id`, `step.step_kind="TOOL_STEP"`, `tool.contract.name`
2. `sandbox.enter` — opens at tier-floor evaluation; emits full `sandbox.*` 7-attribute namespace per C-AS-15 §15: `sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.fail.class` (initially null), and any `sandbox.tier_escalation` event if monotonic ascent required
3. `mcp.tool.call` — opens at FastMCP `call_tool` invocation; emits full `mcp.*` 7-attribute namespace per C-AS-14 §14.3: `mcp.server.name`, `mcp.server.trust_tier`, `mcp.protocol_version`, `mcp.transport`, `mcp.auth_present` (False on STDIO), `mcp.primitive.kind="tool"`, `mcp.primitive.signature.sha256`
4. `sandbox.violation` — emitted only if blast-radius / capability / egress policy hit during call; always-sampled (head=1.0 per C-AS-15 §15)
5. `sandbox.exit` — closes at call return; emits final `sandbox.fail.class` (null on success)

**Sampling discipline:** `mcp.tool.call` + `sandbox.violation` + `sandbox.tier_escalation` are head=1.0 (preserved from C-AS-15). `tool.dispatch` outer span follows engine-class sampling (D6 §1.3).

**New fail classes (added to runtime spec error taxonomy):**

| Fail class | Trigger | Permanent? |
|---|---|---|
| `RT-FAIL-TOOL-CONTRACT-UNKNOWN` | `step.tool_id` not in ToolRegistry | YES |
| `RT-FAIL-TOOL-INVOCATION-TRUST-VIOLATION` | Per-server-trust gate denies the call | YES |
| `RT-FAIL-TOOL-INVOCATION-TIMEOUT` | FastMCP `call_tool` exceeds tool-contract timeout | NO (retryable per C-RT-16) |
| `RT-FAIL-TOOL-INVOCATION-PROTOCOL-ERROR` | MCP protocol error from subprocess | YES |
| `RT-FAIL-TOOL-INVOCATION-SCHEMA-VIOLATION` | Response fails ToolContract.output_schema validation | YES |
| `RT-FAIL-MCP-HOST-STARTUP` | `MCPClientHost.start()` failure at stage 3a | YES (bootstrap aborts) |
| `RT-FAIL-MCP-HOST-UNREACHABLE` | Health check fails mid-dispatch | NO (retryable; transient) |
| `RT-FAIL-SANDBOX-TIER-FLOOR-VIOLATION` | Computed tier < ToolContract.minimum_tier | YES |

## §1.7 Invariants

1. **Subprocess started exactly once per bootstrap.** Stage 3a starts; stage 7 SHUTDOWN drains; idempotent restart out of scope at v1 MVP (deferred to operator-driven restart arc).
2. **Tier-floor monotonic ascent.** Computed `sandbox.tier` ≥ ToolContract.minimum_tier always; floor-violation raises before subprocess invocation.
3. **Per-server-trust evaluated EVERY dispatch.** No caching of trust verdicts across dispatches (operator may revoke between calls).
4. **Schema validation at both directions.** Args validated against `ToolContract.input_schema` pre-call; response validated against `ToolContract.output_schema` post-call.
5. **STDIO + HTTP + SSE all supported at v1** (operator-ratified 2026-05-21, Decision 1.D4 RATIFY-WITH-EDIT). `MCPClientHost.start()` selects transport per `WebhookConfig.transport` or per-server bootstrap config; all 3 must implement subprocess/protocol lifecycle, list_tools/call_tool, and health-check. `mcp.transport` span attribute populates accordingly (stdio | streamable_http | sse).
6. **No retry inside `RuntimeToolDispatcher`.** Retry/breaker/fallback wrapping applied at the same C-RT-16 layer that wraps `RuntimeLLMDispatcher` — by extension, a `RetryBreakerFallbackDispatcher` with `inner=ctx.tool_dispatcher` (registry key `"tool_dispatch"`) materializes at stage 5 alongside the existing `"llm_dispatch"` wrap. Specified per C-RT-16 §14.6 D6.

## §1.8 Decisions requiring operator ratification

| # | Decision | Default proposed | Alternative |
|---|---|---|---|
| 1.D1 | Contract ID | `C-RT-19` | Could be `C-AS-NN` if operator views tool-invocation as AS-axis-owned. Default is runtime-spec-owned because the composer lives at `harness-runtime/lifecycle/`. |
| 1.D2 | `MCPClientHost` stage | 3a (alongside providers) | Could be stage 4 (after providers, before LLM dispatcher build). 3a chosen because subprocess + protocol handshake are independent of LLM clients. |
| 1.D3 | Restart-on-failure | Out of scope at v1 (fail-closed bootstrap) | Could include retry-during-startup loop. Out-of-scope keeps MVP tight. |
| 1.D4 | HTTP/SSE transport | **STDIO + HTTP + SSE all in scope at v1** (RATIFIED 2026-05-21) | Was: Deferred (X-AL-2). Operator-elected full transport coverage at v1 MVP. |
| 1.D5 | Registry key for retry wrap | `"tool_dispatch"` | Could be `"tool_invocation"`. `"tool_dispatch"` matches existing `"llm_dispatch"` naming convention. |
| 1.D6 | Health-check cadence | Every dispatch (no caching) | Could be probe interval + cache. Per-dispatch chosen for trust-revocation safety. |

---

# DRAFT 2 — HITL delivery + timeout-degradation + validator framework

This draft introduces **3 new CP contracts** at v1.10 plus extensions to existing C-CP-17 and a new runtime composer C-RT-20. Authoring is bundled because the validator framework + HITL delivery + pause/resume are tightly coupled (validator-fail escalates to HITL; HITL timeout degrades to validator-fail or pause; pause/resume operates against the same audit substrate).

## §2A — Validator framework

### §2A.1 ID + Name

**Proposed ID:** `C-CP-25` (next contract slot after C-CP-24)
**Proposed name:** `ValidatorFramework`
**Filed at:** CP spec v1.9 → v1.10, new §25
**Authority anchor:** CP plan U-CP-21 + U-CP-22 (validator framework + revalidation arc); substitution H_T-CP-21 STILL-BOUNDED per `harness-cp/CLAUDE.md` §4.1.

### §2A.2 Scope statement

`ValidatorFramework` owns the per-step deterministic validation gate fired between LLM dispatch (or tool dispatch) and step result acceptance. Validation that fails routes per `ValidatorFailClass` taxonomy: TRANSIENT → C-RT-16 retry wrapper; PERMANENT → workflow abort with fail-class propagation; ESCALATE → HITL gate composition; REVALIDATE → next-attempt re-entry with mutated payload; OPERATOR_BURDEN_EXCEEDED → degradation per persona-tier policy.

### §2A.3 Canonical signature(s)

```python
# ValidatorProtocol — operator-supplied
class Validator(Protocol):
    async def validate(
        self,
        step: WorkflowStep,
        step_result: StepOutput,
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorResult: ...

# ValidatorResult — typed envelope
@dataclass(frozen=True)
class ValidatorResult:
    outcome: ValidatorOutcome   # see §2A.4
    fail_class: ValidatorFailClass | None  # None if outcome=PASS
    revalidation_payload: Mapping[str, Any] | None  # populated on REVALIDATE
    escalation_brief: HITLEscalationBrief | None    # populated on ESCALATE
    fail_detail_hash: str | None                    # sha256 of fail-reason text

# ValidatorFramework — runtime-side composer
class ValidatorFramework:
    async def evaluate(
        self,
        step: WorkflowStep,
        step_result: StepOutput,
        *,
        step_context: StepExecutionContext,
    ) -> ValidatorEvaluation: ...
```

### §2A.4 Field sets / enums introduced

**`ValidatorOutcome`** (5-class enum):

```python
class ValidatorOutcome(Enum):
    PASS = "pass"
    REVALIDATE = "revalidate"             # mutate + retry
    ESCALATE = "escalate"                 # HITL gate composition
    PERMANENT_FAIL = "permanent_fail"     # abort workflow
    OPERATOR_BURDEN_EXCEEDED = "operator_burden_exceeded"  # degrade per persona-tier
```

**`ValidatorFailClass`** (5-class taxonomy per substitution H_T-CP-21):

```python
class ValidatorFailClass(Enum):
    SCHEMA_VIOLATION = "schema_violation"           # output doesn't match input_schema
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"  # contradicts prior step state
    SAFETY_POLICY = "safety_policy"                 # operator-defined policy hit
    RESOURCE_CONSTRAINT = "resource_constraint"     # cost/latency budget exceeded
    EXTERNAL_REJECTION = "external_rejection"       # downstream service rejected
```

**`ValidatorEvaluation`** (composer output):

```python
@dataclass(frozen=True)
class ValidatorEvaluation:
    result: ValidatorResult
    span_attributes: Mapping[str, Any]  # validator.fail.* namespace per §2A.6
    next_action: ValidatorNextAction    # PROCEED | RETRY | ESCALATE_HITL | ABORT
    burden_count: int                   # cumulative operator-burden score at this gate
```

**`HITLEscalationBrief`** — typed payload passed to HITL gate when validator escalates:

```python
@dataclass(frozen=True)
class HITLEscalationBrief:
    parent_step_id: str
    parent_action_id: str
    fail_class: ValidatorFailClass
    fail_detail_hash: str
    escalation_reason: str          # operator-readable summary
    proposed_response_palette: frozenset[HITLResponse]  # default = full palette
```

### §2A.5 Lifecycle stage placement

**Stage 5 (LOOP_INIT):** `ValidatorFramework` instantiated with reference to `ctx.validator_registry` (operator-populated registry of per-step `Validator` instances). Bound to `ctx.validator_framework`. Step-dispatcher table extended: after `INFERENCE_STEP` / `TOOL_STEP` dispatch returns, `validator_framework.evaluate()` invoked before result is accepted.

**Workflow-driver integration:** At `workflow_driver.py` post-dispatch step (currently `_append_step_ledger_entry`), add pre-ledger-append validation hook: `evaluation = await ctx.validator_framework.evaluate(...); if evaluation.next_action != PROCEED: branch per-action`.

### §2A.6 Span emission + fail classes

**Spans emitted per validator evaluation:**

1. `validator.evaluate` — outer envelope; attributes: `step.id`, `validator.outcome`, `validator.burden_count_cumulative`
2. `validator.fail` — emitted only on non-PASS outcome; emits `validator.fail.*` namespace:
   - `validator.fail.class` (ValidatorFailClass enum)
   - `validator.fail.detail_hash` (sha256)
   - `validator.fail.next_action` (next_action enum)
   - `validator.fail.escalation_owed` (bool; true on ESCALATE)
3. `validator.revalidation` — emitted on REVALIDATE outcome; attributes: `validator.revalidation.payload_size_bytes`, `validator.revalidation.attempt_number`
4. `validator.escalation` — emitted on ESCALATE outcome; links to subsequent `hitl.gate.evaluated` span via parent-context propagation

**Sampling discipline:** All `validator.*` spans head=1.0 (always-sampled per OD spec C-OD-NN if it exists, else newly committed at OD v1.8). Operator-visibility requirement.

**New CP fail classes:**

| Fail class | Trigger |
|---|---|
| `CP-FAIL-VALIDATOR-PERMANENT` | ValidatorOutcome.PERMANENT_FAIL |
| `CP-FAIL-VALIDATOR-OPERATOR-BURDEN-EXCEEDED` | OPERATOR_BURDEN_EXCEEDED with no degradation policy match |

### §2A.7 Invariants

1. **Every step has at most one Validator.** Multi-validator per step deferred to future arc.
2. **Validation runs after dispatch, before ledger append.** State-ledger entry is the canonical commit point.
3. **REVALIDATE bounded by C-RT-16 retry policy.** A REVALIDATE outcome routes back through retry-wrapper; if retry budget exhausted, escalates to PERMANENT_FAIL.
4. **ESCALATE always emits HITL gate.** Escalation cannot be silently dropped.
5. **Burden count monotonic per workflow.** Tracked on `ctx.operator_burden_counter`; reset only at workflow boundary.

## §2B — Webhook delivery + operator-burden composer

### §2B.1 ID + Name

**Proposed ID:** `C-RT-20` (next runtime contract after C-RT-19)
**Proposed name:** `WebhookDeliveryComposer` + `OperatorBurdenEvaluator` (paired)
**Filed at:** Runtime spec v1.13 (added concurrently with C-RT-19), new §14.10
**Authority anchor:** Substitution H_T-CP-20 RETIRED batch 9 close note + C-CP-17 §17 NOTE on `deliver_webhook` deferral.

### §2B.2 Scope statement

`WebhookDeliveryComposer` owns asynchronous out-of-process HITL delivery via HTTP POST when the operator's `AskUserQuestionSurface` is configured for webhook mode (vs the default MCP-server-elicit mode bound at U-RT-60). `OperatorBurdenEvaluator` owns the cross-step burden aggregation — spans counted per persona-tier configuration; degradation policy fires when threshold exceeded.

### §2B.3 Canonical signature(s)

```python
class WebhookDeliveryComposer:
    async def deliver_webhook(
        self,
        webhook_config: WebhookConfig,        # from CP plan v2.9 T2 factor-out
        payload: WebhookPayload,              # from CP plan v2.9 T2 factor-out
        idempotency_key: str,
    ) -> WebhookDeliveryResult: ...

class OperatorBurdenEvaluator:
    async def compute_operator_burden(
        self,
        span_window: SpanWindow,              # time-bounded span aggregation
        persona_tier: PersonaTier,
    ) -> OperatorBurdenScore: ...

    async def should_degrade(
        self,
        score: OperatorBurdenScore,
        degradation_policy: DegradationPolicy,
    ) -> DegradationDecision: ...
```

### §2B.4 Field sets / enums introduced

**`WebhookDeliveryResult`:**

```python
@dataclass(frozen=True)
class WebhookDeliveryResult:
    delivered: bool
    status_code: int | None
    response_idempotency_key: str
    delivery_attempts: int
    final_attempt_at: int  # epoch ms
```

**`OperatorBurdenScore`** + **`DegradationDecision`** + **`SpanWindow`**:

```python
@dataclass(frozen=True)
class OperatorBurdenScore:
    cumulative_invocations: int
    window_start: int  # epoch ms
    window_end: int    # epoch ms
    persona_tier: PersonaTier

@dataclass(frozen=True)
class DegradationDecision:
    degrade: bool
    degradation_mode: Literal["auto_approve", "auto_reject", "pause_workflow", "operator_notify"] | None
    reason: str  # operator-readable

@dataclass(frozen=True)
class SpanWindow:
    start: int  # epoch ms
    end: int    # epoch ms
```

**Reused (NOT re-authored):**
- `WebhookConfig` / `WebhookPayload` from CP plan v2.9 T2 X-AL-3 FACTOR-OUT
- `PersonaTier` from CP plan v2.8 U-CP-00c
- `DegradationPolicy` from CP plan U-CP-25 (CP_ROUTING registry — `on_hitl_timeout`)

### §2B.5 Lifecycle stage placement

**Stage 5:** Both composers instantiated; bound to `ctx.webhook_delivery_composer` + `ctx.operator_burden_evaluator`. `MCPBackedAskUserQuestionSurface` (existing per U-RT-60) extended to delegate to webhook composer if `ctx.surface_config.mode == "webhook"`.

### §2B.6 Span emission + fail classes

**Spans (webhook):**

1. `hitl.webhook.deliver` — outer envelope; attributes: `webhook.url_hash`, `webhook.delivery_attempts`, `webhook.idempotency_key`
2. `hitl.webhook.attempt` — per-attempt inner span (mirrors `harness.runtime.retry_attempt`); attributes: `retry.attempt_number`, `webhook.status_code`, `webhook.attempt_latency_ms`

**Spans (burden):**

1. `hitl.operator_burden.evaluated` — emitted per-evaluation; attributes: `hitl.operator_burden.cumulative_invocations`, `hitl.operator_burden.window_ms`, `hitl.operator_burden.persona_tier`, `hitl.operator_burden.degrade`

**Sampling discipline:** Webhook spans head=1.0. Burden evaluations head=1.0 only on `degrade=true`; otherwise head=0.1 (tail-keep on degradation).

**New fail classes:**

| Fail class | Trigger |
|---|---|
| `RT-FAIL-HITL-WEBHOOK-DELIVERY-EXHAUSTED` | All retry attempts failed |
| `RT-FAIL-HITL-WEBHOOK-SCHEMA-VIOLATION` | Response doesn't match WebhookConfig schema |
| `RT-FAIL-HITL-OPERATOR-BURDEN-DEGRADATION-CONFLICT` | DegradationDecision.degrade=true but no policy match |

### §2B.7 Invariants

1. **Webhook delivery idempotent.** Same `idempotency_key` → same outcome (within retention window).
2. **Burden window operator-configurable.** Default 1-hour rolling window; tunable per persona-tier.
3. **Degradation deterministic.** Same (score, policy) → same DegradationDecision.
4. **No webhook in test mode.** Test fixtures inject mock surfaces; webhook composer is production-only.

## §2C — Pause/resume protocol

### §2C.1 ID + Name

**Proposed ID:** `C-CP-26` (next CP contract slot after §2A C-CP-25)
**Proposed name:** `PauseResumeProtocol`
**Filed at:** CP spec v1.10, new §26
**Authority anchor:** Substitution H_T-CP-22 STILL-BOUNDED per CP CLAUDE.md §4.1.

### §2C.2 Scope statement

`PauseResumeProtocol` owns explicit-pause + resume mechanics distinct from the prefix-replay resumption landed at U-CP-56 (Path A-modified). Captures snapshot at pause point; resumes from snapshot + material-diff detection.

### §2C.3 Canonical signature(s)

```python
class PauseResumeProtocol:
    async def capture_pause_snapshot(
        self,
        workflow_id: str,
        run_id: str,
        step_index: int,
        pause_reason: PauseReason,
    ) -> PauseSnapshot: ...

    async def attempt_resume(
        self,
        snapshot: PauseSnapshot,
        *,
        material_diff_policy: MaterialDiffPolicy,
    ) -> ResumeResult: ...
```

### §2C.4 Field sets / enums introduced

**`PauseReason`** (5-class enum):

```python
class PauseReason(Enum):
    EXPLICIT_OPERATOR = "explicit_operator"
    HITL_PENDING = "hitl_pending"
    VALIDATOR_ESCALATION = "validator_escalation"
    TIMEOUT_BOUNDARY = "timeout_boundary"
    EXTERNAL_DEPENDENCY = "external_dependency"
```

**`PauseSnapshot`:**

```python
@dataclass(frozen=True)
class PauseSnapshot:
    workflow_id: str
    run_id: str
    step_index: int
    pause_reason: PauseReason
    state_summary: StateSummary       # from CP plan v2.9 (HandoffContext family)
    snapshot_hash: str                # sha256 of canonical serialization
    created_at: int                   # epoch ms
    state_ledger_anchor: str          # entry_hash at pause point
```

**`MaterialDiffPolicy`** + **`ResumeResult`**:

```python
class MaterialDiffPolicy(Enum):
    STRICT = "strict"          # any diff abort
    LENIENT = "lenient"        # only behavior-changing diff abort
    OPERATOR_ARBITRATE = "operator_arbitrate"   # HITL on any diff

@dataclass(frozen=True)
class ResumeResult:
    resumed: bool
    diff_detected: bool
    diff_summary_hash: str | None
    new_run_id: str | None    # if resume requires fresh run_id
    fail_class: str | None
```

### §2C.5 Lifecycle stage placement

**Stage 5:** `PauseResumeProtocol` instantiated with reference to `ctx.state_ledger_writer` + `ctx.state_ledger_reader`. Bound to `ctx.pause_resume_protocol`.

**Workflow-driver integration:** Pause invocation surfaces at any step boundary; resume invocation lives at workflow re-entry (alongside U-CP-56 replay-resumption check).

### §2C.6 Span emission + fail classes

**Spans:**

1. `pause.captured` — attributes: `pause.reason`, `pause.snapshot_hash`, `pause.step_index`, `pause.state_ledger_anchor`
2. `resume.attempted` — attributes: `resume.snapshot_hash`, `resume.diff_detected`, `resume.diff_policy`, `resume.outcome`

**New fail classes:**

| Fail class | Trigger |
|---|---|
| `CP-FAIL-PAUSE-SNAPSHOT-CORRUPTION` | snapshot_hash doesn't validate on resume |
| `CP-FAIL-RESUME-MATERIAL-DIFF-DETECTED` | STRICT policy + diff detected |
| `CP-FAIL-RESUME-OPERATOR-ARBITRATION-OWED` | OPERATOR_ARBITRATE policy + diff → HITL escalation owed |

### §2C.7 Invariants

1. **Snapshot is immutable once captured.** No mutation after pause.
2. **Resume must validate snapshot hash.** Corruption → fail-closed.
3. **Material diff defined as state-ledger-anchor divergence.** If `state_ledger_anchor` no longer reachable from current entry chain, diff detected.
4. **Per-pause-reason routing.** Each `PauseReason` has its own resume policy default.

## §2D — Existing C-CP-17 §17 hitl_gate signature materialization

### §2D.1 Scope

The existing `hitl_gate(...)` Protocol at `harness-cp/src/harness_cp/hitl_placement.py:178` currently raises `NotImplementedError`. This is NOT a new contract — it's materializing an existing C-CP-17 §17 surface that was left as a `Protocol` declaration. The materialization extends C-CP-17 §17.4 (new sub-section).

### §2D.2 Materialization

```python
# C-CP-17 §17.4 (NEW) — hitl_gate canonical signature
async def hitl_gate(
    placement: HITLPlacement,
    step: WorkflowStep,
    step_context: StepExecutionContext,
    *,
    surface: AskUserQuestionSurface,         # injected per U-RT-60
    palette: frozenset[HITLResponse],        # from placement or C-CP-16 default
    timeout: Duration | None,
) -> HITLGateResult: ...
```

**`HITLGateResult`** (reuses existing 4-response palette):

```python
@dataclass(frozen=True)
class HITLGateResult:
    response: HITLResponse                   # APPROVE | EDIT | REJECT | RESPOND
    edited_proposal: Mapping[str, Any] | None
    rejection_reason: str | None
    response_text: str | None
    response_latency_ms: int
    timed_out: bool
```

(Identifies decided semantics; spec-writer applies byte-exact.)

## §2E — Decisions requiring operator ratification (across §2A-D)

| # | Decision | Default proposed | Alternative |
|---|---|---|---|
| 2.D1 | `ValidatorFailClass` taxonomy size | 5-class (per substitution H_T-CP-21) | Could be 7 if SAFETY_POLICY split into POLICY_HARD/POLICY_SOFT or RESOURCE_CONSTRAINT split into COST/LATENCY |
| 2.D2 | `ValidatorOutcome.OPERATOR_BURDEN_EXCEEDED` placement | At outcome level (validator-fired) | Could be evaluated separately at `OperatorBurdenEvaluator` post-validation. Default unifies the decision surface. |
| 2.D3 | Validator runs every step | YES (every step) | Could be opt-in (per WorkflowManifestEntry flag). Default favors safety; opt-out via no-op validator. |
| 2.D4 | Webhook delivery retry policy | Inherit from `ctx.retry_breaker.get_policy("hitl_webhook")` | Could be hardcoded 3-attempt linear backoff. Inheritance matches retry-policy registry convention. |
| 2.D5 | `OperatorBurdenScore` window default | 1-hour rolling | Could be 10-minute or 24-hour. 1-hour matches typical operator-shift granularity. |
| 2.D6 | `PauseResumeProtocol` vs U-CP-56 replay-resumption | Coexist (distinct semantics) | Could be unified. Coexist preserves U-CP-56 Path A-modified ratification. |
| 2.D7 | `MaterialDiffPolicy` default | STRICT | Could be LENIENT or OPERATOR_ARBITRATE. STRICT favors safety. |
| 2.D8 | Contract IDs (C-CP-25/26 + C-RT-20) | Sequential after current high-water | Could be alphabetized or grouped. Sequential matches existing convention. |

---

# DRAFT 3 — Per-server-trust evaluator + mcp.* namespace at H_T-as-MCP-client

## §3.1 ID + Name

**Proposed ID:** `C-CP-27` (after §2C C-CP-26)
**Proposed name:** `PerServerTrustEvaluator` + `MCPClientNamespaceEmitter` (paired)
**Filed at:** CP spec v1.10, new §27 — formalizes the H_T-as-MCP-client second-gate arc that U-RT-62 Q5 disjointness-pinned out of scope (closes that pin)
**Authority anchor:** Substitution H_T-CP-18 STILL-BOUNDED per CP CLAUDE.md §4.1.

## §3.2 Scope statement

`PerServerTrustEvaluator` owns runtime per-server trust evaluation when H_T acts as MCP **client** (consuming external MCP servers). Distinct from the H_T-as-MCP-server role landed at U-RT-62 (where H_T is the server CC consumes). The evaluator consumes the `MCPTrustTier` carrier from CP plan v2.8 U-CP-00c and applies per-call gating based on (server_name, primitive_kind, tool_contract, operator_policy). `MCPClientNamespaceEmitter` owns `mcp.*` 7-attribute namespace emission from the CP/AS/OD drivers when H_T-as-MCP-client invokes a tool.

## §3.3 Canonical signature(s)

```python
class PerServerTrustEvaluator:
    async def evaluate(
        self,
        server_name: str,
        primitive: MCPPrimitive,        # tool | resource | prompt | sampling
        tool_contract: ToolContract | None,  # populated when primitive=tool
        operator_policy: TrustPolicy,
    ) -> TrustEvaluation: ...

class MCPClientNamespaceEmitter:
    def emit_mcp_call_span(
        self,
        span: Span,
        server_name: str,
        primitive: MCPPrimitive,
        signature_hash: str,
    ) -> None: ...   # mutates span with mcp.* 7-attribute namespace per C-AS-14 §14.3
```

## §3.4 Field sets / enums introduced

**`MCPPrimitive`** (4-class enum per C-AS-14):

```python
class MCPPrimitive(Enum):
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"
    SAMPLING = "sampling"
```

**`TrustEvaluation`:**

```python
@dataclass(frozen=True)
class TrustEvaluation:
    permitted: bool
    trust_tier_evaluated: MCPTrustTier
    decision_reason: TrustDecisionReason   # see below
    audit_required: bool                   # tail-keep when True
```

**`TrustPolicy`** (operator-configured at bootstrap):

```python
@dataclass(frozen=True)
class TrustPolicy:
    default_tier: MCPTrustTier              # ALLOW-with-tier-floor threshold for unknown servers
    per_server_overrides: Mapping[str, MCPTrustTier]
    allow_list: frozenset[str]              # exact server names always permitted (bypass tier-floor)
    deny_list: frozenset[str]               # exact server names always denied (deny-wins)
    require_audit_below_tier: MCPTrustTier  # any call below this tier always audited
    tier_derivation: TierDerivationRule     # how to compute tier for unknown servers (per-protocol-version table; default conservative)

class TierDerivationRule(Enum):
    CONSERVATIVE = "conservative"   # unknown-server tier = MIN(MCPTrustTier members)
    PROTOCOL_VERSION_TABLE = "protocol_version_table"  # operator-supplied mapping protocol_version → tier
    OPERATOR_HOOK = "operator_hook"  # call operator-supplied callable
```

**`TrustDecisionReason`** (5-class enum):

```python
class TrustDecisionReason(Enum):
    EXPLICIT_ALLOW = "explicit_allow"                      # allow_list match
    EXPLICIT_DENY = "explicit_deny"                        # deny_list match
    TIER_FLOOR_PASS = "tier_floor_pass"                    # known server, tier >= floor
    TIER_FLOOR_VIOLATION = "tier_floor_violation"          # known server, tier < floor
    UNKNOWN_SERVER_TIER_FLOOR_PASS = "unknown_server_tier_floor_pass"        # unknown server, resolved tier >= default floor (operator-ratified ALLOW-with-tier-floor)
    UNKNOWN_SERVER_TIER_FLOOR_VIOLATION = "unknown_server_tier_floor_violation"  # unknown server, resolved tier < default floor
```

**Reused (NOT re-authored):**
- `MCPTrustTier` from CP plan U-CP-00c (canonical carrier already landed)
- `ToolContract` from AS spec C-AS-12

## §3.5 Lifecycle stage placement

**Stage 3a:** `PerServerTrustEvaluator` + `MCPClientNamespaceEmitter` instantiated alongside `MCPClientHost` (per §1.5). Bound to `ctx.per_server_trust_evaluator` + `ctx.mcp_client_namespace_emitter`. Trust policy loaded from bootstrap config.

**Stage 5:** `RuntimeToolDispatcher` (§1) invokes `ctx.per_server_trust_evaluator.evaluate(...)` PRE-call; `ctx.mcp_client_namespace_emitter.emit_mcp_call_span(...)` mutates the `mcp.tool.call` span DURING dispatch.

## §3.6 Span emission + fail classes

**Spans (in addition to §1.6 tool-invocation spans):**

1. `mcp.trust.evaluate` — emitted per evaluation; attributes: `mcp.trust.server_name`, `mcp.trust.primitive_kind`, `mcp.trust.decision_reason`, `mcp.trust.audit_required`, `mcp.trust.tier_evaluated`
2. Existing `mcp.tool.call` span mutation: namespace emitter populates `mcp.*` 7-attribute set per C-AS-14 §14.3 (the substrate)

**Sampling discipline:** `mcp.trust.evaluate` head=1.0 if `audit_required=true`, else head=0.1.

**New fail classes:**

| Fail class | Trigger |
|---|---|
| `CP-FAIL-TRUST-EVALUATION-EXPLICIT-DENY` | Server in deny_list |
| `CP-FAIL-TRUST-EVALUATION-TIER-FLOOR-VIOLATION` | Known server, resolved tier < policy floor |
| `CP-FAIL-TRUST-EVALUATION-UNKNOWN-SERVER-TIER-FLOOR-VIOLATION` | Unknown server, resolved tier < default floor (ALLOW-with-tier-floor rejection) |

## §3.7 Invariants

1. **Trust policy immutable per workflow.** Loaded at bootstrap; no live mutation during workflow run.
2. **Every MCP-as-client call goes through evaluator.** No bypass path.
3. **Deny-list wins over allow-list.** If a server is in both, DENY.
4. **Unknown server policy = ALLOW-with-tier-floor** (operator-ratified 2026-05-21, Decision 3.D1 RATIFY-WITH-EDIT). Unknown server permitted iff resolved tier >= TrustPolicy.default_tier; resolution uses operator-configured tier-derivation rule (per-protocol-version table at TrustPolicy.tier_derivation; default conservative). `audit_required=true` auto-set on every UNKNOWN_SERVER_TIER_FLOOR_PASS for operator visibility.
5. **Audit-required calls always emit `mcp.trust.evaluate` span.** Tail-keep on `audit_required=true`. UNKNOWN_SERVER decisions always audit-required regardless of permitted outcome.

## §3.8 Decisions requiring operator ratification

| # | Decision | Default proposed | Alternative |
|---|---|---|---|
| 3.D1 | Unknown-server default | **ALLOW with tier-floor** (RATIFIED 2026-05-21) | Was: DENY. Operator-elected ALLOW-with-tier-floor; resolved tier must pass `TrustPolicy.default_tier`. UNKNOWN decisions always audit-required. |
| 3.D2 | Deny-list vs allow-list precedence | Deny wins | Could be allow wins. Deny-wins is more defensive. |
| 3.D3 | Trust policy mutable mid-workflow | NO | Could allow operator-triggered mid-run revoke. Default avoids race conditions; mid-run revoke deferred to future arc. |
| 3.D4 | `mcp.trust.evaluate` sampling | head=1.0 when audit_required; else 0.1 | Could be uniform 1.0. Sampling reduces span volume for routine evals. |
| 3.D5 | Contract IDs (C-CP-27) | After §2 contracts | Could place differently. Sequential matches convention. |

---

# Cross-draft decisions

| # | Decision | Default proposed | Alternative |
|---|---|---|---|
| X.D1 | Spec version bumps | runtime v1.12→v1.13 + CP v1.9→v1.10 + AS v1.3→v1.4 (sandbox/mcp namespace extensions referenced from §1) | Could batch all into a single v1.13/v1.10/v1.4 bump or split across multiple bumps. Default single-bump per spec per Phase. |
| X.D2 | New CXA edges surfaced | Tool-invocation → IS (audit secret-fetch); Tool-invocation → OD (sandbox observability); ValidatorFramework → OD (validator.* audit); PerServerTrust → OD (mcp.trust audit) | These will be authored in Phase A.4 (CXA v2.5→v2.6) per plan. |
| X.D3 | Adversarial review timing | After ALL 3 drafts ratified (Phase B) | Could review per-draft. Single review pass matches plan file Phase B. |
| X.D4 | Pattern-D inheritance citation strategy | Inline citation at each consumer (CPAuditLedgerEntry, RetryPolicy, etc.) | Could centralize in a single "Pattern-D inheritance" appendix. Inline is more local to read. |

---

# Ratification summary table

| Draft | Contract IDs proposed | New fail classes | New spans | Decisions needing ratification | Recommendation |
|---|---|---|---|---|---|
| 1 — Tool-invocation | C-RT-19 | 8 | 5 | 6 (1.D1–1.D6) | RATIFY |
| 2A — Validator framework | C-CP-25 | 2 | 4 | 3 (2.D1–2.D3) | RATIFY |
| 2B — Webhook + burden | C-RT-20 | 3 | 3 | 2 (2.D4–2.D5) | RATIFY |
| 2C — Pause/resume | C-CP-26 | 3 | 2 | 2 (2.D6–2.D7) | RATIFY |
| 2D — hitl_gate materialization | C-CP-17 §17.4 (extension) | 0 | 0 | 0 (mechanical) | RATIFY |
| 3 — Per-server-trust | C-CP-27 | 3 | 1 | 5 (3.D1–3.D5) | RATIFY |
| **Cross-draft** | — | — | — | 4 (X.D1–X.D4) | RATIFY |

**Total decisions requiring ratification:** 22 (per-draft) + 4 (cross-draft) = **26**.

---

# §X Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/Phase_A_2_Contract_Drafts_v1.md` |
| Authored at | Phase A sub-arc A.2, Remaining-Work Closure Arc, 2026-05-21 |
| Mode | ARCHITECT-DRAFTS (NOT spec-writer output) |
| Decided fix? | NO — these are CANDIDATE shapes for operator ratification |
| Authority chain | ADR-F1 v1.2 / ADR-D1 v1.2 / ADR-D2 v1.2 / ADR-D5 v1.4 / ADR-D6 v1.2 / Runtime spec v1.12 / CP spec v1.9 / AS spec v1.3 / OD spec v1.7 / CXA v2.5 |
| Inherited (NOT re-authored) | Pattern-D 13 types per Phase A.1 §4.2; LLM-dispatch contracts per Phase A.0 |
| Next sub-arc | OPERATOR RATIFICATION (this session) → spec-writer applies byte-exact (still Phase A.2) → Phase A.3 |
| Estimated spec-writer apply effort | ~3 spec files (runtime v1.13 / CP v1.10 / AS v1.4) + change-notes + back-reference reconciliation. 1 pass once ratified. |
