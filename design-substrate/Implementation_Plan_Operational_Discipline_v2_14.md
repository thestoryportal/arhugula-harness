# Implementation Plan — Operational Discipline v2.14

## Change-note (v2.13 → v2.14)

**Scope of revision.** Phase C atomic-unit decomposition pass per Remaining-Work Closure Arc plan file. Absorbs OD spec v1.8 (9 new contracts: C-OD-25 WorkflowEnvelopeSpan + C-OD-26 CostAttributionInvocation + C-OD-27 SqliteWritePath + C-OD-28 PRICE_TABLE_REF + C-OD-29 through C-OD-33 canonical namespace schemas). Adds 20 new atomic units (U-OD-35 through U-OD-54). v2.13 substantive content (U-OD-00 through U-OD-34) preserved verbatim.

**Source of fix.** Phase A.5 compound-irrelevance unblock + Phase B iteration-2 absorption (F2-02 Pattern-P1 alignment + F2-06 Decimal string-serialization invariant).

**Spec authority chain.** OD spec v1.8 §C-OD-25 through §C-OD-33 + CXA v2.6 §2.3.7 + ADR-D4 v1.1 + ADR-D6 v1.2 + ADR-F5 v1.1.

**Plan shape preserved.** v2.13's axis-led structure preserved verbatim. New units land at Cluster 4 (NEW — compound-irrelevance unblock + canonical schemas).

**Sections preserved verbatim from v2.13.** All v2.13 content outside the new Cluster 4 preserved. The v2.13 + v2.12 + v2.11 + v2.10 + ... + v2.0 chain preserved.

**Status posture.** Proposed (v2.13) → Proposed (v2.14). v2.14 is an additive patch.

**Downstream absorption owed (post-v2.14).** Workspace `CLAUDE.md` §2.4 OD row version bump (v2.13 → v2.14); `harness-od/CLAUDE.md` §4.1 retirement-table extensions.

---

## §1 — Cluster 4 — OD compound-irrelevance unblock + canonical namespace schemas (NEW at v2.14)

**Sub-cluster decomposition (Phase D iteration-1 F2-05 absorption — cluster sizing for single-arc landing feasibility):**
- **4-OD-A — WorkflowEnvelopeSpan (3 units): U-OD-35 / U-OD-36 / U-OD-37.** Workflow-envelope OTel integration at workflow_driver entry; unblocks OD-3/4/5/6 compound-irrelevance.
- **4-OD-B — SqliteWritePath (4 units): U-OD-42 / U-OD-43 / U-OD-44 / U-OD-45.** sqlite span store + retention + typed read; closes U-RT-30 PARTIAL-LAND.
- **4-OD-C — PRICE_TABLE_REF + Decimal serialization (4 units): U-OD-46 / U-OD-47 / U-OD-48 / U-OD-49.** Rate table + Decimal-boundary discipline; PRICE_TABLE_REF X-AL-2 carry-forward closure.
- **4-OD-D — CostAttribution invocations (4 units): U-OD-38 / U-OD-39 / U-OD-40 / U-OD-41.** Cost-attribution at LLM dispatch + tool dispatch + validator/webhook + audit-ledger write. Depends on 4-OD-A + 4-OD-C.
- **4-OD-E — Canonical namespace schemas (5 units): U-OD-50 / U-OD-51 / U-OD-52 / U-OD-53 / U-OD-54.** 5 Pattern-P1-aligned canonical schemas + AuditPayload dataclasses; consumer-side complement to CP plan v2.15 producer-side composers.

Each sub-cluster matches precedent landing size. 4-OD-D opens after 4-OD-A + 4-OD-C close. 4-OD-E can land in parallel with 4-OD-A through 4-OD-D (no within-axis deps to the others).

### U-OD-35 — workflow.envelope OTel tracer integration at workflow_driver entry

- **Implements:** OD spec v1.8 §C-OD-25.1 canonical span shape + §C-OD-25.2 lifecycle placement
- **Files:** `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND — line ~373 post-drain-check)
- **Signatures:** `ctx.tracer.start_as_current_span("workflow.envelope")` context manager wrap of `execute_workflow` body
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `workflow.envelope` span opens at workflow_driver entry (post-drain-check)
  2. Single envelope per workflow (per §C-OD-25.4 invariant 1)
  3. Closes on normal SUCCESS / FAILED / DRAINED + on exception via OTel exception-status
  4. Head=1.0 always-sampled (per §C-OD-25.3)
  5. Integration test: assert `workflow.envelope` span emitted at OTel collector with non-null span_id + parent_span_id=null (root span) + status=OK on SUCCESS / status=ERROR on FAILED; subsequent child spans (LLM dispatch / tool dispatch / HITL / validator) carry the envelope as parent context

### U-OD-36 — workflow.envelope 12-attribute set population

- **Implements:** OD spec v1.8 §C-OD-25.1 attribute schema (12 attributes on outer span)
- **Files:** `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND)
- **Signatures:** `span.set_attribute(name, value)` calls per §C-OD-25.1 attribute list
- **Depends on:** [U-OD-35]
- **ACs:**
  1. All 12 attributes populated (workflow.id / run_id / idempotency_key / entry_version / topology_pattern / engine_class / workload_class / persona_tier / outcome / fail_class / terminal_step_index / step_count)
  2. `workflow.fail_class` null on DRAINED outcome (per §C-OD-25.5 deferred-to-impl-discretion default)
  3. `workflow.step_count` populated at terminal close (per §C-OD-25.5 default — single-attribute terminal-only)
  4. Enum values serialize via `.value` (string form)
  5. Integration test: assert all 12 attributes present on span at OTel collector

### U-OD-37 — workflow.envelope deterministic close path + exception handling

- **Implements:** OD spec v1.8 §C-OD-25.4 invariant 2 (deterministic close) + §C-OD-25.5 fresh-envelope-on-resumption default
- **Files:** `harness-cp/src/harness_cp/workflow_driver.py` (EXTEND)
- **Signatures:** Exception handler wraps span close with `Span.record_exception()` + `Span.set_status(StatusCode.ERROR)`
- **Depends on:** [U-OD-35]
- **ACs:**
  1. Exception during execute_workflow closes span with status=ERROR + exception recorded
  2. Resumption (per U-CP-56) opens FRESH envelope (per §C-OD-25.4 invariant 1)
  3. Span context propagation correctly nests child spans (LLM dispatch / tool dispatch / HITL gate / validator)
  4. `Span.end_time_ns` reflects actual workflow termination time
  5. Integration test: exception path + resumption path both produce well-formed envelope spans

### U-OD-38 — Cost-attribution invocation at LLM-dispatch site

- **Implements:** OD spec v1.8 §C-OD-26.1 invocation signature + §C-OD-26.2 billable-span enumeration row "llm_dispatch"
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (EXTEND — line ~445 post-provider-call)
- **Signatures:** `cost_record = ctx.cost_chain.compute_cost(...); attached = ctx.cost_chain.attach_idempotency_key(...); ctx.audit_writer.append(...)` per §C-OD-26.1 call-site convention
- **Depends on:** [U-OD-46, U-OD-47, U-OD-49]
- **ACs:**
  1. Cost-attribution invoked on every LLM dispatch (success + failure paths)
  2. Cost-record uses `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` per GenAI semconv 1.41.0
  3. Idempotency-key attached pre-audit-write
  4. `PRICE_TABLE_REF` resolution failure falls back per Decision (default = raise per §C-OD-28.2)
  5. Integration test: 1 LLM call → 1 cost-record + 1 audit-ledger entry

### U-OD-39 — Cost-attribution invocation at tool-dispatch site

- **Implements:** OD spec v1.8 §C-OD-26.2 billable-span enumeration row "tool.dispatch" / "mcp.tool.call"
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` (EXTEND — post-call)
- **Signatures:** Same convention as §C-OD-26.1
- **Depends on:** [U-RT-67 (cross-axis: runtime), U-OD-46]
- **ACs:**
  1. Cost-attribution invoked on every tool dispatch (success + failure)
  2. Tool-rate resolution per `ToolRate.cost_kind` formulas (Phase D iteration-1 F2-04 absorption): `flat_per_invocation` → `cost = rate` (constant per invocation; input/output bytes ignored); `per_input_byte` → `cost = rate × input_payload_byte_count` (where input_payload is canonical JSON serialization of the tool's input args); `per_output_byte` → `cost = rate × output_payload_byte_count`. All arithmetic in `Decimal` per §C-OD-28.4 invariant 2.
  3. mcp.tool.call cost piggybacks on parent tool.dispatch (per §C-OD-26.2 table)
  4. Cost-record attached + audit-ledger entry written
  5. Integration test: 1 tool call → 1 cost-record per each of 3 `cost_kind` values exercised + cost arithmetic verified Decimal-precision-preserving

### U-OD-40 — Cost-attribution invocation at validator.evaluate + webhook.deliver sites

- **Implements:** OD spec v1.8 §C-OD-26.2 billable-span enumeration rows "validator.evaluate" + "hitl.webhook.deliver"
- **Files:** `harness-cp/src/harness_cp/validator_framework.py` + `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py` (EXTEND)
- **Signatures:** Cost-attribution hook at span exit
- **Depends on:** [U-CP-60 (cross-axis: CP), U-RT-69 (cross-axis: runtime), U-OD-46]
- **ACs:**
  1. Validator cost uses CPU-meter (`execution_time_ms × $/CPU_ms`) per Decision 2.D5 RATIFIED (CPU-meter default)
  2. Webhook cost uses `WebhookRate.flat_per_attempt` + egress
  3. Cost-record attached at span exit
  4. Audit-ledger entry written
  5. Integration test: 1 validator + 1 webhook → 2 cost-records

### U-OD-41 — Cost-record audit-ledger write composition

- **Implements:** OD spec v1.8 §C-OD-26.3 audit-ledger write per cost-record
- **Files:** `harness-od/src/harness_od/cost_record_audit_writer.py` (NEW)
- **Signatures:** `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry`
- **Depends on:** [U-OD-38, U-OD-39, U-OD-40, U-CP-72 (cross-axis: CP)]
- **ACs:**
  1. Cost-record projects to audit entry with `audit.cp.action_id = f"cost:{span_id}"`
  2. `audit.cp.response = "cost_attributed"`
  3. Routes via `cp_audit_to_od_audit` converter (action_id prefix `cost:` added per U-CP-72 extension — note: covered by `cost:` discriminator as the 8th pattern; reviewer to confirm bucket sizing or extend U-CP-72)
  4. Idempotency-key joins to parent IS state-ledger entry per existing C-OD-24.4
  5. Integration test: cost-record write + audit ledger query

### U-OD-42 — sqlite schema migration + WAL-mode setup

- **Implements:** OD spec v1.8 §C-OD-27.1 sqlite schema + §C-OD-27.2 write-path discipline (WAL mode)
- **Files:** `harness-od/src/harness_od/sqlite_span_store.py` (NEW)
- **Signatures:** `def initialize_span_store(db_path: Path) -> sqlite3.Connection`; CREATE TABLE + CREATE INDEX DDL
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. `spans` table created with 12 columns per §C-OD-27.1
  2. 4 indexes created (idx_workflow / idx_idempotency / idx_trace / idx_time_range)
  3. WAL mode enabled (`PRAGMA journal_mode=WAL`)
  4. Idempotent re-initialization (no error on existing schema)
  5. Unit test: schema matches §C-OD-27.1 verbatim

### U-OD-43 — RingBufferStage → sqlite batch INSERT flush integration

- **Implements:** OD spec v1.8 §C-OD-27.2 (flush from in-memory ring-buffer to sqlite) + §C-OD-27.4 invariant 3 (idempotent writes via INSERT OR IGNORE)
- **Files:** `harness-od/src/harness_od/ring_buffer.py` (EXTEND) + `harness-od/src/harness_od/sqlite_span_store.py` (EXTEND)
- **Signatures:** `async def flush_to_sqlite(self, conn, spans: list[Span]) -> int`
- **Depends on:** [U-OD-42]; **Requires existing (landed at main per U-RT-30 PARTIAL-LAND):** `RingBufferStage` carrier at `harness-od/src/harness_od/ring_buffer.py` (in-memory operative per OD plan v2.13). Phase D iteration-1 F1-04 absorption.
- **ACs:**
  1. Batched INSERT every `flush_interval_ms` (default 1000ms)
  2. INSERT OR IGNORE on span_id primary key (idempotent re-flush)
  3. attributes_json + events_json JSON-serialized correctly
  4. Returns count of rows actually inserted
  5. Integration test: 100-span batch flush in < 100ms; subsequent re-flush is no-op

### U-OD-44 — Retention policy lazy-on-write implementation

- **Implements:** OD spec v1.8 §C-OD-27.2 retention policy (default 7 days) + §C-OD-27.5 lazy-on-write default
- **Files:** `harness-od/src/harness_od/sqlite_span_store.py` (EXTEND)
- **Signatures:** `def retention_cleanup_lazy(conn, retention_days: int = 7) -> int`; called during flush
- **Depends on:** [U-OD-43]
- **ACs:**
  1. DELETE WHERE end_time_ns < (now - retention_days * 86400 * 1e9)
  2. Runs lazy-on-write during flush_to_sqlite (no background cron task)
  3. Operator-configurable retention_days via bootstrap config
  4. Returns count of rows deleted
  5. Unit test: insert 100 spans across 14 days + flush → 50 spans remain after retention cleanup

### U-OD-45 — Typed read interface (no ad-hoc SQL)

- **Implements:** OD spec v1.8 §C-OD-27.3 read-path access (typed query interface)
- **Files:** `harness-od/src/harness_od/sqlite_span_store_reader.py` (NEW)
- **Signatures:** `def read_spans_by_workflow(conn, workflow_id, workflow_run_id) -> list[Span]`; `def read_spans_by_trace(conn, trace_id) -> list[Span]`
- **Depends on:** [U-OD-43]
- **ACs:**
  1. Read functions use parameterized SQL (no string concatenation)
  2. Returns typed `Span` objects (not raw rows)
  3. No ad-hoc SQL exposed to runtime
  4. Read during concurrent write (WAL mode) succeeds
  5. Unit test: write + read + assert typed objects returned

### U-OD-46 — RateTable + ProviderRates + ToolRate + WebhookRate dataclasses

- **Implements:** OD spec v1.8 §C-OD-28.1 canonical schema (4 dataclasses)
- **Files:** `harness-od/src/harness_od/rate_table_types.py` (NEW)
- **Signatures:** 4 frozen dataclasses; Decimal field types
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. All 4 dataclasses instantiable with Decimal-typed rate fields
  2. Pydantic v2 validation
  3. Frozen + hashable
  4. pyright strict mode passes
  5. Unit test: serialize → deserialize round-trip preserves Decimal precision

### U-OD-47 — rate_table_v1.py default rate authoring (anthropic + openai + ollama)

- **Implements:** OD spec v1.8 §C-OD-28.3 authoring substrate (default RateTable for 3 providers)
- **Files:** `harness-od/src/harness_od/rate_table_v1.py` (NEW)
- **Signatures:** Module-level `RATE_TABLE_V1: RateTable = RateTable(...)`
- **Depends on:** [U-OD-46]
- **ACs:**
  1. anthropic provider has input + output + cache_read + cache_write rates
  2. openai provider has input + output rates
  3. ollama provider has nominal rates (or zero for local-only deployment)
  4. cpu_rate_per_ms + egress_rate_per_byte populated with operator-configurable defaults
  5. RateTable.version = "2026-05-21" (matches authoring date)

### U-OD-48 — TrustPolicy.resolve_for() resolution method

- **Implements:** OD spec v1.8 §C-OD-28.2 resolution discipline + invariant 4 (provider-then-model resolution)
- **Files:** `harness-od/src/harness_od/rate_table_resolver.py` (NEW)
- **Signatures:** `def resolve_for(rate_table: RateTable, provider: str, model: str | None) -> ProviderRates`
- **Depends on:** [U-OD-46, U-OD-47]
- **ACs:**
  1. Per-model override resolves before falling back to provider-level
  2. Unknown provider raises `CP-FAIL-RATE-TABLE-MISSING` (or returns noop per operator config)
  3. Cached at workflow scope (immutable post-resolution)
  4. Decimal arithmetic throughout (no float coercion)
  5. Unit test: anthropic + claude-sonnet-4-6 resolves with model override

### U-OD-49 — Decimal string-serialization at OTel span attribute boundary

- **Implements:** OD spec v1.8 §C-OD-28.4 invariant 3 (string-serialize Decimal at OTel boundary per F2-06 RATIFIED)
- **Files:** `harness-od/src/harness_od/cost_record_otel_serializer.py` (NEW)
- **Signatures:** `def serialize_decimal_for_otel(value: Decimal) -> str`; `def deserialize_otel_decimal(s: str) -> Decimal`
- **Depends on:** [U-OD-46]
- **ACs:**
  1. `serialize_decimal_for_otel(Decimal("1.234567890123"))` returns `"1.234567890123"` (full precision)
  2. `deserialize_otel_decimal(s)` round-trips byte-exact
  3. OTel span attribute `cost.attributed_decimal` populated via string-form
  4. OD sqlite span store preserves string form in `attributes_json` column
  5. Property-based test: 1000 random Decimals round-trip without precision loss

### U-OD-50 — validator.* 11-attribute schema + ValidatorEscalationAuditPayload dataclass

- **Implements:** OD spec v1.8 §C-OD-29.1 (11 attributes across 4 span sites per F2-02 RATIFIED) + §C-OD-29.2 (ValidatorEscalationAuditPayload)
- **Files:** `harness-od/src/harness_od/validator_namespace.py` (NEW)
- **Signatures:** `VALIDATOR_SPAN_NAMESPACE_SCHEMA: Mapping[str, AttributeSpec]`; `@dataclass(frozen=True) class ValidatorEscalationAuditPayload(AuditPayload)`
- **Depends on:** [U-CP-58 (cross-axis: CP)]
- **ACs:**
  1. Schema declares all 11 attributes across 4 span sites per §C-OD-29.1
  2. ValidatorEscalationAuditPayload extends AuditPayload with 4 validator-specific fields
  3. Schema attribute names byte-exact match CP spec v1.10 §25.5 producer-side (Pattern-P1 alignment)
  4. Cardinality + type annotations match §C-OD-29.1
  5. Unit test: schema declaration matches §C-OD-29.1 row-by-row

### U-OD-51 — pause/resume schema + PauseResumeAuditPayload dataclass

- **Implements:** OD spec v1.8 §C-OD-30.1 (8 attributes) + §C-OD-30.2 (PauseResumeAuditPayload)
- **Files:** `harness-od/src/harness_od/pause_resume_namespace.py` (NEW)
- **Signatures:** `PAUSE_RESUME_SPAN_NAMESPACE_SCHEMA`; `@dataclass(frozen=True) class PauseResumeAuditPayload(AuditPayload)`
- **Depends on:** [U-CP-62 (cross-axis: CP)]
- **ACs:**
  1. Schema declares 8 attributes per §C-OD-30.1
  2. PauseResumeAuditPayload extends AuditPayload with 8 pause/resume-specific fields (pause OR resume path)
  3. Pattern-P1 byte-exact alignment with CP spec v1.10 §26.4
  4. Optional fields per path (pause_reason populated on pause path; resume_outcome on resume path)
  5. Unit test: schema verbatim match

### U-OD-52 — mcp.trust.* schema + TrustEvaluationAuditPayload dataclass

- **Implements:** OD spec v1.8 §C-OD-31.1 (5 attributes) + §C-OD-31.2 (TrustEvaluationAuditPayload)
- **Files:** `harness-od/src/harness_od/mcp_trust_namespace.py` (NEW)
- **Signatures:** `MCP_TRUST_SPAN_NAMESPACE_SCHEMA`; `@dataclass(frozen=True) class TrustEvaluationAuditPayload(AuditPayload)`
- **Depends on:** [U-CP-66 (cross-axis: CP)]
- **ACs:**
  1. Schema declares 5 attributes per §C-OD-31.1
  2. TrustEvaluationAuditPayload extends AuditPayload with 5 trust-specific fields
  3. Pattern-P1 byte-exact alignment with CP spec v1.10 §27.4
  4. `audit_required` always True when audit row written (redundant carry for query convenience)
  5. Unit test: schema verbatim match

### U-OD-53 — hitl.webhook.* schema + WebhookDeliveryAuditPayload dataclass

- **Implements:** OD spec v1.8 §C-OD-32.1 (6 attributes) + §C-OD-32.2 (WebhookDeliveryAuditPayload)
- **Files:** `harness-od/src/harness_od/hitl_webhook_namespace.py` (NEW)
- **Signatures:** `HITL_WEBHOOK_SPAN_NAMESPACE_SCHEMA`; `@dataclass(frozen=True) class WebhookDeliveryAuditPayload(AuditPayload)`
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. Schema declares 6 attributes per §C-OD-32.1 (3 outer + 3 per-attempt + retry.attempt_number reused from C-CP-03 §3.5)
  2. WebhookDeliveryAuditPayload extends AuditPayload with 5 webhook-specific fields
  3. Pattern-P1 byte-exact alignment with runtime spec v1.13 §14.10.3
  4. Audit row per delivery attempt (not per delivery)
  5. Unit test: schema verbatim match

### U-OD-54 — hitl.operator_burden.* schema + OperatorBurdenAuditPayload dataclass

- **Implements:** OD spec v1.8 §C-OD-33.1 (4 attributes) + §C-OD-33.2 (OperatorBurdenAuditPayload)
- **Files:** `harness-od/src/harness_od/hitl_operator_burden_namespace.py` (NEW)
- **Signatures:** `HITL_OPERATOR_BURDEN_SPAN_NAMESPACE_SCHEMA`; `@dataclass(frozen=True) class OperatorBurdenAuditPayload(AuditPayload)`
- **Depends on:** (none within this delta) [HIGH]
- **ACs:**
  1. Schema declares 4 attributes per §C-OD-33.1
  2. OperatorBurdenAuditPayload extends AuditPayload with 5 burden-specific fields
  3. Pattern-P1 byte-exact alignment with runtime spec v1.13 §14.10.3
  4. degradation_mode populated when degrade=true
  5. Unit test: schema verbatim match

---

## §2 — DAG topology delta (v2.13 → v2.14)

20 new units added at Cluster 4. Topological sort acyclic:

```
Cluster 4 (NEW at v2.14):
  L0-within-delta: U-OD-35, U-OD-42, U-OD-46, U-OD-53, U-OD-54
  L1-within-delta: U-OD-36 (←35), U-OD-37 (←35), U-OD-43 (←42), U-OD-47 (←46), U-OD-49 (←46),
                   U-OD-50 (← U-CP-58 cross-axis), U-OD-51 (← U-CP-62 cross-axis), U-OD-52 (← U-CP-66 cross-axis)
  L2-within-delta: U-OD-44 (←43), U-OD-45 (←43), U-OD-48 (←46, 47), U-OD-38 (←46, 47, 49)
  L3-within-delta: U-OD-39 (← U-RT-67 cross-axis, 46), U-OD-40 (← U-CP-60, U-RT-69 cross-axis, 46)
  L4-within-delta: U-OD-41 (←38, 39, 40 + U-CP-72 cross-axis)
```

Cross-axis edges: U-OD-39 → U-RT-67; U-OD-40 → U-CP-60, U-RT-69; U-OD-41 → U-CP-72; U-OD-50 → U-CP-58; U-OD-51 → U-CP-62; U-OD-52 → U-CP-66.

DAG verified Kahn-acyclic; 20 units consumed; ∅ remaining edges.

---

## §3 — Coverage matrix delta (v2.13 → v2.14)

| Contract | Units covering |
|---|---|
| C-OD-25 §C-OD-25 (WorkflowEnvelopeSpan) | U-OD-35, U-OD-36, U-OD-37 |
| C-OD-26 §C-OD-26 (CostAttributionInvocation) | U-OD-38, U-OD-39, U-OD-40, U-OD-41 |
| C-OD-27 §C-OD-27 (SqliteWritePath) | U-OD-42, U-OD-43, U-OD-44, U-OD-45 |
| C-OD-28 §C-OD-28 (PRICE_TABLE_REF) | U-OD-46, U-OD-47, U-OD-48, U-OD-49 |
| C-OD-29 (validator.* schema) | U-OD-50 |
| C-OD-30 (pause/resume schema) | U-OD-51 |
| C-OD-31 (mcp.trust.* schema) | U-OD-52 |
| C-OD-32 (hitl.webhook.* schema) | U-OD-53 |
| C-OD-33 (hitl.operator_burden.* schema) | U-OD-54 |

All 9 OD contracts covered ≥ 1 unit. ✓

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Operational_Discipline_v2_14.md` |
| Version | v2.14 |
| Filing event | Phase C atomic-unit decomposition pass, 2026-05-21 |
| Predecessor | `Implementation_Plan_Operational_Discipline_v2_13.md` |
| New units | 20 (U-OD-35 through U-OD-54) |
| New cluster | 4 (NEW at v2.14) |
| Cross-axis dependencies | 6 (U-OD-39→U-RT-67; U-OD-40→U-CP-60, U-RT-69; U-OD-41→U-CP-72; U-OD-50→U-CP-58; U-OD-51→U-CP-62; U-OD-52→U-CP-66) |
| DAG verification | Kahn-acyclic; 20 units consumed; ∅ remaining edges |
| Coverage verification | All 9 OD contracts covered ≥ 1 unit |
| Date | 2026-05-21 |
