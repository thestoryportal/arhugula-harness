# Specification — Operational Discipline v1.8

## Change-note (v1.7 → v1.8)

**Scope of revision.** Phase A.5 OD compound-irrelevance unblock + Phase A.4 forward-citation absorption per `.harness/Phase_A_2_Contract_Drafts_v1.md` + `.harness/Spec_Phase_A_2_Authoring_Log_v1.md` + `Cross_Axis_Composition_Document_v2_6.md`. Two scope tracks combined in a single v1.8 delta:

**Track A — Compound-irrelevance unblock (per Phase A.5 plan-file scope ratification):**
- C-OD-25 (NEW) — CP-driver workflow-envelope span emission contract. Unblocks the OD-3/4/5/6 compound-irrelevance pattern (per `.harness/phase-7d-retirement-ledger-v2.md` §6) where OD primitives are doubly-inactive because CP driver emits zero spans outside the injected dispatcher.
- C-OD-26 (NEW) — Cost-attribution invocation contract. Wires `CostAttributionChain.compute_cost(...)` (existing carrier per OD spec v1.5 §25.9) into production at workflow-envelope + LLM-dispatch + tool-dispatch span sites. Unblocks H_T-OD-5 retirement.
- C-OD-27 (NEW) — Sqlite write-path contract. Lifts U-RT-30 PARTIAL-LAND (sqlite write deferred per `[[fork-trace-storage-pathclass-gap]]`) to spec form; closes H_T-OD-6 partial retirement frontier.
- C-OD-28 (NEW) — `PRICE_TABLE_REF` rate-table format. Closes the bounded X-AL-2 carry-forward at `[[fork-price-table-ref-substitution-retirement]]` (rate-table authoring ~100-200 LOC deferred to sub-phase 7d).

**Track B — Canonical namespace schemas (forward-cited by CXA v2.6 §2.3.7 rows 3-7):**
- C-OD-29 (NEW) — `validator.*` 11-attribute namespace across 4 span sites + ValidatorEscalationAuditPayload row shape (CP spec v1.10 §25 producer; OD canonical schema). Per Phase B iteration-1 F1-01 absorption (count corrected from "4-attribute" framing).
- C-OD-30 (NEW) — `pause.*` + `resume.*` 8-attribute namespace + PauseResumeAuditPayload row shape (CP spec v1.10 §26 producer).
- C-OD-31 (NEW) — `mcp.trust.*` 5-attribute namespace + TrustEvaluationAuditPayload row shape (CP spec v1.10 §27 producer).
- C-OD-32 (NEW) — `hitl.webhook.*` 6-attribute namespace + WebhookDeliveryAuditPayload row shape (runtime spec v1.13 §14.10 producer).
- C-OD-33 (NEW) — `hitl.operator_burden.*` 4-attribute namespace + OperatorBurdenAuditPayload row shape (runtime spec v1.13 §14.10 producer).

All v1.7 content preserved verbatim. No signature change to any v1.7 contract; no field-projection table change at §24 (the existing AuditPayload field-projection extends via new namespaces; §24.6 row-additions enumerated in this delta).

**Source of fix.** Plan-orchestrated Remaining-Work Closure Arc Phase A.5 with prerequisites:
- Phase A.2 (`.harness/Spec_Phase_A_2_Authoring_Log_v1.md`) — Runtime spec v1.13 §14.9/§14.10 + CP spec v1.10 §25/§26/§27 + AS spec v1.4 §14.3/§15 producer-site references APPLIED.
- Phase A.4 (`Cross_Axis_Composition_Document_v2_6.md`) — 5 new genuine-typed-seam CXA edges at §2.3.7 forward-cited OD spec v1.8 §NN; this delta resolves those forward-citations.

**Sections preserved verbatim from v1.7.** All v1.7 substantive content + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 chain preserved. The v1.7 §24 audit-ledger schema + C-OD-24 4-section chain + `compute_entry_hash` helper materialization (per v1.7 §24.5 RESOLVED status) preserved verbatim.

**Status posture.** Proposed (v1.7) → **Proposed (v1.8)**. v1.8 is an additive patch — 9 new contracts (C-OD-25 through C-OD-33); no v1.7 contract re-decomposition; no acceptance criterion change.

**Downstream absorption owed (post-v1.8).**
(a) Workspace `CLAUDE.md` §2.3 OD row version bump (v1.7 → v1.8).
(b) `harness-od/CLAUDE.md` §1.2 OD-axis spec version + §4.1 retirement-table extensions (H_T-OD-3/4/5/6 transitions pending implementation arc).
(c) `Cross_Axis_Composition_Document_v2_6.md` §2.3.7 rows 3-7 forward-citations RESOLVED via this delta (no v2.7 needed; the citations resolve byte-exact to the section numbers below).
(d) `Implementation_Plan_Operational_Discipline_v2_13.md` (or successor) — new atomic units for §C-OD-25 through §C-OD-33 materialization. Anticipated ~15-25 new units. Owed at Phase C implementation-planner pass.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).** None — apply pass is fidelity-pure transcription of A.2 producer-side specs + plan-file-ratified compound-irrelevance unblock scope.

**Architectural defaults embedded (operator review at Phase B adversarial review).** Several fine-grained choices use reasonable defaults; flagged inline at each contract section as `[Phase B review: default X; alternatives Y/Z]`. Adversarial review may surface changes; spec-writer would amend at v1.9.

---

## §C-OD-25 (NEW) — CP-driver workflow-envelope span emission contract

**Contract surface.** `WorkflowEnvelopeSpan` — every workflow execution opens exactly one outer span at the CP driver `workflow_driver.py:execute_workflow` entry; closes at workflow exit (SUCCESS, FAILED, DRAINED). Child spans (LLM dispatch / tool dispatch / sub-agent dispatch / HITL gate / validator / pause-resume / per-server-trust) nest under this envelope via OTel parent-context propagation.

**Unblocks compound-irrelevance.** Per `.harness/phase-7d-retirement-ledger-v2.md` §6: OD-3 (Composite Sampler) + OD-4 (redaction processor) + OD-5 (cost-attribution chain) + OD-6 (sqlite write) are doubly-inactive because the workflow-driver emits only 3 lifecycle-event-class boundaries (binary emit), not OTel-tracer spans. C-OD-25 mandates that workflow-driver opens an OTel span at workflow entry; every downstream OD primitive then has an envelope to sample / redact / attribute / persist.

**PRD enablement.** PRD v1.1 §"Observability invariant: every workflow envelope-observable end-to-end".

**ADR commitment.** ADR-D6 v1.2 (observability substrate; the workflow-envelope span is the canonical parent for all OD-axis instrumentation) + ADR-F5 v1.1 (observability primitive).

### §25.1 Canonical span shape

```
workflow.envelope (outer span; ALWAYS opened at workflow_driver.execute_workflow entry)
├── attributes:
│   ├── workflow.id (string)
│   ├── workflow.run_id (string)
│   ├── workflow.idempotency_key (string)
│   ├── workflow.entry_version (int; per WorkflowManifestEntry)
│   ├── workflow.topology_pattern (TopologyPattern enum)
│   ├── workflow.engine_class (EngineClass enum)
│   ├── workflow.workload_class (WorkloadClass enum)
│   ├── workflow.persona_tier (PersonaTier enum)
│   ├── workflow.outcome (RunStatus enum on close: SUCCESS | FAILED | DRAINED)
│   ├── workflow.fail_class (string; populated on FAILED)
│   ├── workflow.terminal_step_index (int | null)
│   └── workflow.step_count (int; cumulative steps executed before terminal)
├── child spans (nest via OTel parent-context):
│   ├── llm_dispatch (per C-RT-15 §14.5)
│   ├── retry_breaker_fallback envelope (per C-RT-16 §14.6)
│   ├── tool.dispatch (per C-RT-19 §14.9; runtime spec v1.13)
│   ├── subagent.span (per C-RT-17 §14.7)
│   ├── hitl.gate.evaluated (per C-RT-18 §14.8)
│   ├── validator.evaluate (per C-CP-25 §25; CP spec v1.10)
│   ├── pause.captured / resume.attempted (per C-CP-26 §26)
│   ├── mcp.trust.evaluate (per C-CP-27 §27)
│   ├── hitl.webhook.deliver (per C-RT-20 §14.10)
│   └── hitl.operator_burden.evaluated (per C-RT-20 §14.10)
```

### §25.2 Lifecycle stage placement

**Stage 5 (LOOP_INIT):** `ctx.tracer` (OTel `Tracer`) instantiated against the materialized `TracerProvider` (per existing C-OD-NN tracer provider materialization; preserved from v1.7).

**Workflow-driver integration:** `workflow_driver.py:execute_workflow` at line ~373 (post drain-check), open `workflow.envelope` span via `ctx.tracer.start_as_current_span("workflow.envelope")`; populate attributes per §25.1; the entire `execute_workflow` body executes within the context manager; close on normal return + on exception via OTel default exception-status discipline.

### §25.3 Sampling discipline

`workflow.envelope` head=1.0 (always-sampled — every workflow envelope-observable per PRD). Tail-keep policies per existing C-OD-3 composite sampler defer to per-child-span sampling; the envelope ALWAYS persists.

### §25.4 Invariants

1. **Exactly one envelope per workflow.** Resumption (per U-CP-56 prefix-replay) re-opens a NEW envelope; the prior envelope is closed at pause-snapshot capture (per C-CP-26 §26). State-ledger anchor cross-link via `workflow.run_id` + `workflow.idempotency_key` attributes.
2. **Envelope closes deterministically.** Normal SUCCESS / FAILED / DRAINED close path emits `workflow.outcome`; exception path emits via OTel `Span.record_exception()` + `Span.set_status(StatusCode.ERROR)`.
3. **Child-span propagation via OTel parent-context only.** No manual parent-id management; trust OTel's context-management discipline.

### §25.5 Deferred to implementation discretion

- **`workflow.step_count` granularity** — runtime spec v1.13 implementation may choose to emit at terminal close only (single attribute) OR at each step boundary (counter-style attribute updates per step). Default: terminal-close-only (simpler).
- **`workflow.fail_class` content shape on DRAINED outcome** — null vs `"drained"`. Default: null (DRAINED is not a fail).
- **Per-resumption envelope re-open semantics** — does a resumption from `U-CP-56` open a fresh envelope or extend the prior? Default: fresh envelope per §25.4 invariant 1.

`[Phase B review: workflow.envelope is the LOAD-BEARING span for compound-irrelevance unblock. Reviewers should verify per-attribute necessity + invariant completeness. Alternative shape: split workflow.envelope into workflow.entry + workflow.exit two-span pattern (rejected default; single-envelope simpler).]`

---

## §C-OD-26 (NEW) — Cost-attribution invocation contract

**Contract surface.** `CostAttributionChain.compute_cost(...)` (existing carrier per OD spec v1.5 §25.9) invoked at every billable-span exit. Production invocation sites: `llm_dispatch.py:445`, `tool_invocation.py:NN` (post-A.2 §14.9), `mcp.trust.evaluate` exit (if cost-meterable), `hitl.webhook.deliver` exit.

**Unblocks H_T-OD-5 retirement.** Per ledger §6, the cost-attribution chain exists at axis-package level but is never invoked at production. C-OD-26 closes that gap.

### §26.1 Canonical invocation signature (call-site convention; not new code)

```python
# At every billable span exit:
cost_record = ctx.cost_chain.compute_cost(
    span_ref=current_span_ref,
    parent_idempotency_key=step_context.parent_idempotency_key,
    span_attributes=current_span_attributes,
)
attached = ctx.cost_chain.attach_idempotency_key(
    span_ref=current_span_ref,
    parent_idempotency_key=step_context.parent_idempotency_key,
    cost_record=cost_record,
)
ctx.audit_writer.append(tenant_id, _project_cost_record_to_audit_entry(attached))
```

### §26.2 Billable-span enumeration

| Span | Billable? | Cost-meter (suggested) |
|---|---|---|
| `workflow.envelope` | NO (envelope only; aggregates children) | n/a |
| `llm_dispatch` | YES | tokens_in × $/MTok_in + tokens_out × $/MTok_out |
| `tool.dispatch` | YES (if tool has cost) | per-invocation flat OR per-input-size |
| `mcp.tool.call` | YES (same as parent tool.dispatch) | piggyback on parent |
| `hitl.gate.evaluated` | NO (operator-time, not infra-cost) | n/a |
| `validator.evaluate` | YES (CPU only; modest) | execution_time_ms × $/CPU_ms |
| `pause.captured` / `resume.attempted` | NO | n/a |
| `mcp.trust.evaluate` | NO (cheap) | n/a |
| `hitl.webhook.deliver` | YES (egress + HTTP cost) | per-attempt flat |
| `hitl.operator_burden.evaluated` | NO | n/a |

### §26.3 Audit-ledger write per cost-record

Each billable-span cost-record writes one audit entry with `audit.cp.action_id = f"cost:{span_id}"` + `audit.cp.response = "cost_attributed"` (via the converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`). The cost-record's `idempotency_key` field (from existing OD §25.9 carrier) joins to the parent IS state-ledger entry per existing C-OD-24.4 invariant.

### §26.4 Invariants

1. **No cost-record without idempotency_key.** `attach_idempotency_key()` MUST precede `audit_writer.append()`.
2. **Cost-records produced even on FAILED dispatches.** Cost is incurred at the API call, not the success-path.
3. **`PRICE_TABLE_REF` resolved at workflow start.** Per C-OD-28 below; resolution failures fall back to `cost_chain_noop` (existing carrier; no error raised at compute_cost call).

### §26.5 Deferred to implementation discretion

- **Per-billable-span cost-meter algorithm details** — defer to per-provider rate-table at `C-OD-28 PRICE_TABLE_REF`.
- **Span-attribute → cost-record-input mapping** — implementation maps `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` (per GenAI semconv 1.41.0) for LLM dispatch; per-tool conventions for tool dispatch.

`[Phase B review: validator cost-meter is LOW-CONFIDENCE default; some validators are heavy (semantic-inconsistency check may invoke another LLM). Reviewers may prefer marking validator NON-BILLABLE or distinguishing validator.simple vs validator.llm_check.]`

---

## §C-OD-27 (NEW) — Sqlite write-path contract

**Contract surface.** `LocalOTLPCollectorDaemon` (existing carrier per OD spec v1.5 §6) is extended at v1.8 with a sqlite write path. Spans persist to a local sqlite DB at a deterministic per-deployment path (`.harness/observability/spans.db`) via the existing ring-buffer flush mechanism.

**Unblocks H_T-OD-6 PARTIAL.** Per ledger §6 + U-RT-30 PARTIAL-LAND status: in-memory ring-buffer operative at U-RT-30; sqlite write path deferred. C-OD-27 closes the partial.

### §27.1 Canonical schema

```sql
CREATE TABLE spans (
    span_id TEXT PRIMARY KEY,           -- OTel 16-hex
    trace_id TEXT NOT NULL,             -- OTel 32-hex
    parent_span_id TEXT NULL,           -- OTel 16-hex (null at root)
    name TEXT NOT NULL,                 -- span name (e.g., "workflow.envelope")
    kind INTEGER NOT NULL,              -- OTel SpanKind enum value
    start_time_ns INTEGER NOT NULL,     -- nanoseconds since epoch
    end_time_ns INTEGER NOT NULL,
    status_code INTEGER NOT NULL,       -- OTel StatusCode enum value (UNSET=0, OK=1, ERROR=2)
    status_message TEXT NULL,
    attributes_json TEXT NOT NULL,      -- JSON serialization of full attribute set
    events_json TEXT NOT NULL,          -- JSON serialization of span events
    workflow_id TEXT NULL,              -- indexed; null for non-workflow spans
    workflow_run_id TEXT NULL,          -- indexed
    workflow_idempotency_key TEXT NULL  -- indexed
);

CREATE INDEX idx_workflow ON spans(workflow_id, workflow_run_id);
CREATE INDEX idx_idempotency ON spans(workflow_idempotency_key);
CREATE INDEX idx_trace ON spans(trace_id);
CREATE INDEX idx_time_range ON spans(start_time_ns, end_time_ns);
```

### §27.2 Write-path discipline

1. **Flush from in-memory ring-buffer.** Existing `RingBufferStage` (per U-RT-30) flushes to sqlite via batched INSERT every `flush_interval_ms` (default 1000ms).
2. **WAL mode + foreign-keys off.** Performance-optimized for write-heavy load.
3. **Retention policy.** Operator-configurable; default 7 days. Cleanup via background DELETE on span timestamp.

### §27.3 Read-path access

Reads via existing `read_state_ledger` shape: typed query interface, no ad-hoc SQL exposed to runtime. Read path used by TUI (per OD spec v1.5 §6; TUI deferred to future arc).

### §27.4 Invariants

1. **Sqlite DB at per-deployment path.** No cross-deployment span pollution.
2. **WAL mode.** Concurrent reads during writes.
3. **Idempotent writes.** Span-id is primary key; re-flush of same span (rare) ignored via `INSERT OR IGNORE`.

### §27.5 Deferred to implementation discretion

- **Flush-interval tunability** — default 1000ms; operator may tune via bootstrap config.
- **Retention policy implementation** — cron-style background task vs lazy-on-write. Default: lazy-on-write.

---

## §C-OD-28 (NEW) — `PRICE_TABLE_REF` rate-table format

**Contract surface.** `PRICE_TABLE_REF` carrier (per existing CP/OD references) is a typed `RateTable` resolved at workflow start from operator bootstrap config. Closes the bounded X-AL-2 carry-forward at `[[fork-price-table-ref-substitution-retirement]]`.

### §28.1 Canonical schema

```python
@dataclass(frozen=True)
class RateTable:
    version: str                                      # e.g., "2026-05-21"
    providers: Mapping[str, ProviderRates]            # keyed by provider name (e.g., "anthropic")
    tool_rates: Mapping[str, ToolRate]                # keyed by tool.contract.name; cost per invocation OR per byte
    webhook_rate: WebhookRate                         # flat per-attempt cost
    cpu_rate_per_ms: Decimal                          # for CPU-bound spans (validator)
    egress_rate_per_byte: Decimal                     # for egress-bearing spans (webhook)

@dataclass(frozen=True)
class ProviderRates:
    input_token_rate: Decimal                         # $/MTok input
    output_token_rate: Decimal                        # $/MTok output
    cache_read_rate: Decimal                          # $/MTok cached read (anthropic-specific)
    cache_write_rate: Decimal                         # $/MTok cache write
    per_model_overrides: Mapping[str, ProviderRates] | None  # model-specific overrides (nested resolution)

@dataclass(frozen=True)
class ToolRate:
    cost_kind: Literal["flat_per_invocation", "per_input_byte", "per_output_byte"]
    rate: Decimal                                     # interpreted per cost_kind

@dataclass(frozen=True)
class WebhookRate:
    flat_per_attempt: Decimal                         # base cost
    plus_egress: bool                                 # add egress_rate_per_byte if True
```

### §28.2 Resolution discipline

`PRICE_TABLE_REF` resolved at workflow_driver entry via `ctx.rate_table.resolve_for(provider, model)`. Cached at workflow scope (immutable post-resolution). Resolution failure (rate-table missing OR provider/model not in table) raises `CP-FAIL-RATE-TABLE-MISSING` (NEW) OR falls back to `cost_chain_noop` (operator-configurable; default fail-closed = raise).

### §28.3 Authoring substrate

A v1 rate-table at `harness-od/src/harness_od/rate_table_v1.py` ships with operator-default rates for `anthropic` + `openai` + `ollama` providers (matching the 3 providers per ADR-F1 v1.2). Format: Python module export of a `RateTable` instance. Operator overrides via bootstrap config.

### §28.4 Invariants

1. **Rate-table version immutable per workflow.** Resolved at start; no live mutation.
2. **`Decimal` arithmetic.** All rate computations use Python `Decimal` (not float) for cost-attribution audit precision.
3. **Decimal serialization at OTel span attribute boundary (operator-ratified 2026-05-21 per Phase B iteration-1 F2-06).** Cost values emitted as OTel span attributes are **string-serialized** (not float-serialized) to preserve Decimal precision through the OTel exporter pipeline. Pattern: `span.set_attribute("cost.attributed_decimal", str(decimal_value))`. Consumer-side parses via `Decimal(span_attr_string)` to recover the canonical value. Non-standard OTel pattern but audit-correct; the OD span store (per C-OD-27 sqlite write-path) preserves the string form in the `attributes_json` column. Float-serialization would defeat invariant 2 at the observability boundary.
4. **Provider-then-model resolution.** `per_model_overrides` resolves before falling back to provider-level rate.

### §28.5 Deferred to implementation discretion

- **Default rate values** — placeholder values at `rate_table_v1.py`; operator updates per their billing arrangements.
- **Per-model override granularity** — `per_model_overrides` opens nested resolution; depth unlimited at v1 MVP.

`[Phase B review: PRICE_TABLE_REF was operator-flagged ~100-200 LOC of rate-table authoring as bounded X-AL-2 residual. Reviewers should confirm Decimal vs float invariant + version-immutability is sufficient.]`

---

## §C-OD-29 (NEW) — `validator.*` 4-attribute namespace

**Contract surface.** Canonical schema for the `validator.*` namespace emitted by CP spec v1.10 §25 `ValidatorFramework` per the D6 ingestion pattern (CP emits; OD canonical).

### §29.1 Canonical attribute set

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `step.id` | string | `validator.evaluate` outer | 1 |
| `validator.outcome` | enum (`ValidatorOutcome` per CP spec v1.10 §25.2: PASS / REVALIDATE / ESCALATE / PERMANENT_FAIL / OPERATOR_BURDEN_EXCEEDED) | `validator.evaluate` outer | 1 |
| `validator.burden_count_cumulative` | int | `validator.evaluate` outer | 1 |
| `validator.fail.class` | enum (`ValidatorFailClass` per CP spec v1.10 §25.2) | `validator.fail` event | 0–1 (null if outcome=PASS) |
| `validator.fail.detail_hash` | string (sha256 hex) | `validator.fail` event | 0–1 |
| `validator.fail.next_action` | enum (`ValidatorNextAction`: PROCEED / RETRY / ESCALATE_HITL / ABORT) | `validator.fail` event | 0–1 |
| `validator.fail.escalation_owed` | bool | `validator.fail` event | 0–1 |
| `validator.revalidation.payload_size_bytes` | int | `validator.revalidation` event | 0–1 |
| `validator.revalidation.attempt_number` | int | `validator.revalidation` event | 0–1 |
| `validator.escalation.parent_hitl_span_id` | string (16-hex OTel span id) | `validator.escalation` event | 0–1 (populated when outcome=ESCALATE; links to subsequent `hitl.gate.evaluated` span via parent-context per CP spec v1.10 §25.5) |
| `validator.escalation.fail_class` | enum (`ValidatorFailClass`) | `validator.escalation` event | 0–1 (mirrors `validator.fail.class` for downstream-consumer convenience) |

(Attribute count: 11 across 4 span sites — `validator.evaluate` outer carries 3; `validator.fail` event carries 5; `validator.revalidation` event carries 2; `validator.escalation` event carries 2. The change-note v1.7 → v1.8 "4-attribute namespace" framing was a misnomer; the canonical schema is 11 attributes across span-site decomposition. Change-note count framing corrected at v1.8 per Phase B iteration-1 F1-01 absorption.)

### §29.2 Audit-ledger projection (`ValidatorEscalationAuditPayload`)

When `validator.outcome ∈ {ESCALATE, PERMANENT_FAIL, OPERATOR_BURDEN_EXCEEDED}`, the converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` writes via `validator:` action_id prefix (per CXA v2.6 §0.3 discriminator table):

```python
@dataclass(frozen=True)
class ValidatorEscalationAuditPayload(AuditPayload):  # extends per C-OD-24.6
    # Inherited from AuditPayload:
    audit_cp_action_id: str         # f"validator:{parent_action_id}:{fail_class.value}"
    audit_cp_response: str          # validator outcome enum value
    audit_cp_timestamp: str         # "" at MVP per existing v1.7 NOTE 8a-iii
    audit_cp_prior_event_hash: str  # "0"*64 at MVP

    # New v1.8 fields:
    validator_fail_class: str       # ValidatorFailClass enum value
    validator_fail_detail_hash: str
    validator_next_action: str      # ValidatorNextAction enum value
    validator_escalation_owed: bool
```

### §29.3 Sampling discipline

All `validator.*` spans head=1.0 (always-sampled per operator-visibility requirement, mirrors CP spec v1.10 §25.5).

---

## §C-OD-30 (NEW) — `pause.*` + `resume.*` 8-attribute namespace

**Contract surface.** Canonical schema for the `pause.*` + `resume.*` namespaces emitted by CP spec v1.10 §26 `PauseResumeProtocol`.

### §30.1 Canonical attribute set

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `pause.reason` | enum (`PauseReason` per CP spec v1.10 §26.2) | `pause.captured` | 1 |
| `pause.snapshot_hash` | string (sha256 hex) | `pause.captured` | 1 |
| `pause.step_index` | int | `pause.captured` | 1 |
| `pause.state_ledger_anchor` | string (entry_hash) | `pause.captured` | 1 |
| `resume.snapshot_hash` | string (sha256 hex) | `resume.attempted` | 1 |
| `resume.diff_detected` | bool | `resume.attempted` | 1 |
| `resume.diff_policy` | enum (`MaterialDiffPolicy`: STRICT / LENIENT / OPERATOR_ARBITRATE) | `resume.attempted` | 1 |
| `resume.outcome` | enum (resumed / diff_aborted / arbitration_owed) | `resume.attempted` | 1 |

### §30.2 Audit-ledger projection (`PauseResumeAuditPayload`)

```python
@dataclass(frozen=True)
class PauseResumeAuditPayload(AuditPayload):
    # Inherited per C-OD-24.6
    audit_cp_action_id: str        # f"pause:{workflow_id}:{step_index}" OR f"resume:{workflow_id}:{step_index}"
    audit_cp_response: str         # "paused" | "resumed" | "diff_detected"
    audit_cp_timestamp: str
    audit_cp_prior_event_hash: str

    # New v1.8 fields (populated per pause OR resume row):
    pause_reason: str | None       # PauseReason enum value (pause path)
    snapshot_hash: str             # always populated (both paths share this)
    step_index: int                # always populated
    state_ledger_anchor: str | None  # pause path
    diff_detected: bool | None     # resume path
    diff_policy: str | None        # resume path
    diff_summary_hash: str | None  # resume path
    resume_outcome: str | None     # resume path
```

### §30.3 Sampling discipline

`pause.captured` head=1.0 (always-sampled — operator-explicit pause is audit-critical). `resume.attempted` head=1.0.

---

## §C-OD-31 (NEW) — `mcp.trust.*` 5-attribute namespace

**Contract surface.** Canonical schema for the `mcp.trust.*` namespace emitted by CP spec v1.10 §27 `PerServerTrustEvaluator`.

### §31.1 Canonical attribute set

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `mcp.trust.server_name` | string | `mcp.trust.evaluate` | 1 |
| `mcp.trust.primitive_kind` | enum (`MCPPrimitive`: TOOL / RESOURCE / PROMPT / SAMPLING) | `mcp.trust.evaluate` | 1 |
| `mcp.trust.decision_reason` | enum (`TrustDecisionReason` 6-class per CP spec v1.10 §27.2) | `mcp.trust.evaluate` | 1 |
| `mcp.trust.audit_required` | bool | `mcp.trust.evaluate` | 1 |
| `mcp.trust.tier_evaluated` | enum (`MCPTrustTier`) | `mcp.trust.evaluate` | 1 |

### §31.2 Audit-ledger projection (`TrustEvaluationAuditPayload`)

```python
@dataclass(frozen=True)
class TrustEvaluationAuditPayload(AuditPayload):
    audit_cp_action_id: str        # f"mcp_trust:{server_name}:{primitive_kind.value}"
    audit_cp_response: str         # "permitted" | "denied"
    audit_cp_timestamp: str
    audit_cp_prior_event_hash: str

    # New v1.8 fields:
    server_name: str
    primitive_kind: str
    decision_reason: str           # TrustDecisionReason enum value
    audit_required: bool           # always True when audit row written; redundant carry for query convenience
    tier_evaluated: str            # MCPTrustTier enum value
```

### §31.3 Sampling discipline

`mcp.trust.evaluate` head=1.0 if `audit_required=true`; head=0.1 otherwise (per CP spec v1.10 §27.4 + Decision 3.D1 RATIFIED — UNKNOWN_SERVER decisions always audit-required).

---

## §C-OD-32 (NEW) — `hitl.webhook.*` 6-attribute namespace

**Contract surface.** Canonical schema for the `hitl.webhook.*` namespace emitted by runtime spec v1.13 §14.10 `WebhookDeliveryComposer`.

### §32.1 Canonical attribute set

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `webhook.url_hash` | string (sha256 hex of URL) | `hitl.webhook.deliver` outer | 1 |
| `webhook.delivery_attempts` | int | `hitl.webhook.deliver` outer | 1 |
| `webhook.idempotency_key` | string | `hitl.webhook.deliver` outer | 1 |
| `retry.attempt_number` | int (reuses C-CP-03 §3.5 retry.* namespace) | `hitl.webhook.attempt` per-attempt | 1 per attempt |
| `webhook.status_code` | int | `hitl.webhook.attempt` per-attempt | 1 per attempt |
| `webhook.attempt_latency_ms` | int | `hitl.webhook.attempt` per-attempt | 1 per attempt |

### §32.2 Audit-ledger projection (`WebhookDeliveryAuditPayload`)

```python
@dataclass(frozen=True)
class WebhookDeliveryAuditPayload(AuditPayload):
    audit_cp_action_id: str        # f"hitl_webhook:{parent_action_id}:{idempotency_key}"
    audit_cp_response: str         # "delivered" | "failed"
    audit_cp_timestamp: str
    audit_cp_prior_event_hash: str

    # New v1.8 fields:
    url_hash: str
    delivery_attempts: int
    idempotency_key: str
    final_status_code: int | None
    final_attempt_latency_ms: int | null
```

### §32.3 Sampling discipline

Webhook spans head=1.0 (always-sampled — HITL delivery audit-critical).

---

## §C-OD-33 (NEW) — `hitl.operator_burden.*` 4-attribute namespace

**Contract surface.** Canonical schema for the `hitl.operator_burden.*` namespace emitted by runtime spec v1.13 §14.10 `OperatorBurdenEvaluator`.

### §33.1 Canonical attribute set

| Attribute | Type | Span site | Cardinality |
|---|---|---|---|
| `hitl.operator_burden.cumulative_invocations` | int | `hitl.operator_burden.evaluated` | 1 |
| `hitl.operator_burden.window_ms` | int | `hitl.operator_burden.evaluated` | 1 |
| `hitl.operator_burden.persona_tier` | enum (`PersonaTier`) | `hitl.operator_burden.evaluated` | 1 |
| `hitl.operator_burden.degrade` | bool | `hitl.operator_burden.evaluated` | 1 |

### §33.2 Audit-ledger projection (`OperatorBurdenAuditPayload`)

```python
@dataclass(frozen=True)
class OperatorBurdenAuditPayload(AuditPayload):
    audit_cp_action_id: str        # f"operator_burden:{workflow_id}:{window_end_epoch_ms}"
    audit_cp_response: str         # "burden_evaluated" | "burden_degraded"
    audit_cp_timestamp: str
    audit_cp_prior_event_hash: str

    # New v1.8 fields:
    cumulative_invocations: int
    window_ms: int
    persona_tier: str              # PersonaTier enum value
    degrade: bool
    degradation_mode: str | None   # populated when degrade=true
```

### §33.3 Sampling discipline

Burden evaluations head=1.0 only on `degrade=true`; otherwise head=0.1 (per runtime spec v1.13 §14.10.3 — tail-keep on degradation).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_8.md` |
| Version | v1.8 |
| Filing event | Phase A.5 OD compound-irrelevance unblock + Phase A.4 forward-citation absorption, Remaining-Work Closure Arc, 2026-05-21 |
| Predecessor | `Spec_Operational_Discipline_v1_7.md` (v1.7 preserved verbatim; helper-materialization NOTE deferred → RESOLVED status held) |
| Successor | Workspace `CLAUDE.md` §2.3 OD row version bump (v1.7 → v1.8); future implementation arcs per Phase C |
| New contracts | 9 (C-OD-25 through C-OD-33) — 4 compound-irrelevance unblock + 5 canonical namespace schemas |
| Pattern | Additive; no v1.7 content modified |
| Cross-citation resolution | CXA v2.6 §2.3.7 rows 3-7 forward-cited `OD spec v1.8 §NN` — RESOLVED via this delta (rows 3-7 resolve to §C-OD-32 / §C-OD-33 / §C-OD-29 / §C-OD-30 / §C-OD-31 respectively) |
| Architectural defaults embedded | Yes — `[Phase B review: ...]` markers at §25.5 + §26.5 + §28.5 flag operator-review items. None block apply; all surface to adversarial review. |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-21 |

*Filed at Phase 7 sub-phase 7b/7c as the OD-side Phase A.5 compound-irrelevance unblock + canonical namespace schema absorption per `.harness/Phase_A_2_Contract_Drafts_v1.md` apply chain. v1.7 substantive content preserved verbatim; 9 new contracts at §C-OD-25 through §C-OD-33. Co-published with `Spec_Drift_Reconciliation_v1.md` (Phase A.3) + `Cross_Axis_Composition_Document_v2_6.md` (Phase A.4) as the final A-sub-arc landing.*
