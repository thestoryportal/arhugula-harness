# Specification — Operational Discipline v1.10

## Change-note (v1.9 → v1.10)

**Scope of revision.** Sub-arc B sequel landing per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` + OD plan v2.16 §0(d) operator preference (i) revise-signature at session checkpoint + CXA v2.9 §0.7(ii) adjacent-finding routing. NEW §C-OD-26.6 — `CostRecordAuditPayload` typed carrier declaration extending the established AuditPayload-subclass pattern (parallel to `PauseResumeAuditPayload` at §C-OD-30.2 + `ValidatorEscalationAuditPayload` at §C-OD-29.2 + `WebhookDeliveryAuditPayload` at §C-OD-32.2 + `OperatorBurdenAuditPayload` at §C-OD-33.2 + `TrustEvaluationAuditPayload` at §C-OD-31.2). Amendment at §C-OD-26.1 canonical invocation signature replacing the helper-shape (`_project_cost_record_to_audit_entry(attached)` — preserved at v1.8 + v1.9) with the canonical `cp_audit_to_od_audit` converter path consuming a `CostRecordAuditPayload` typed carrier per CXA v2.9 row 8 ratification.

**v1.9 substantive content preserved verbatim.** All v1.9 content (which preserved all v1.8 NEW C-OD-25 through C-OD-33 contracts) preserved unchanged outside the two amendment sites at §C-OD-26 (§26.1 invocation signature + §26.6 NEW CostRecordAuditPayload carrier). The v1.9 §C-OD-30.1 attribute-type-citation absorption preserved verbatim. The v1.7 + v1.6 + ... + v1 chain all preserved.

**Source of fix.** Sub-arc B of the 3-arc cascade per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6 + OD plan v2.16 §0(d). Companion artifacts at this arc: CXA v2.9 (`Cross_Axis_Composition_Document_v2_9.md` at HEAD `39e4f1c` 2026-05-24, §2.3.7 row 8 cost-attribution audit-write seam published). Companion arcs to follow within this same session: U-OD-41 plan revision (OD plan v2.16 → v2.17) absorbing the new CostRecordAuditPayload contract; U-CP-72 minor revision restoring `cost:` branch at `cp_audit_to_od_audit`.

**Two amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§C-OD-26.1 canonical invocation signature** | Replace `ctx.audit_writer.append(tenant_id, _project_cost_record_to_audit_entry(attached))` with the canonical converter path: `cost_payload = _project_cost_record_to_audit_payload(attached)` + `audit_entry = cp_audit_to_od_audit(cost_payload, key_id=ctx.audit_signing_key_id, entry_core=...)` + `ctx.audit_writer.append(tenant_id, audit_entry)`. Helper renamed from `_project_cost_record_to_audit_entry` → `_project_cost_record_to_audit_payload` (produces `CostRecordAuditPayload` instead of `CPAuditLedgerEntry`); the converter then projects to the OD-canonical `AuditLedgerEntry` via the `cost:` action_id prefix branch per CXA v2.9 §2.3.7 row 8 + U-CP-72 minor revision restoring the branch. | CXA v2.9 §2.3.7 row 8 ratification + §C-OD-24.6 sub-namespace tagging discipline (`audit.cost.*` for cost-attribution-sourced fields) + the established AuditPayload-subclass pattern at sibling §C-OD-29.2 / §30.2 / §31.2 / §32.2 / §33.2 |
| **§C-OD-26.6 (NEW) CostRecordAuditPayload typed carrier** | NEW sub-section declaring `CostRecordAuditPayload` Pydantic v2 BaseModel with the standard 4 `audit_cp_*` common fields shared across all CP-sourced AuditPayload subclasses (`audit_cp_action_id`, `audit_cp_prior_event_hash`, `audit_cp_actor`, `audit_cp_timestamp`) + cost-attribution-specific fields projected from `SpanCostRecord` per CXA v2.9 row 8 enumeration + C-OD-14 §14.4 carrier shape. | CXA v2.9 §2.3.7 row 8 + CXA v2.9 §0.3 "1-row audit shape includes ..." prose enumeration + SpanCostRecord 15-field shape at C-OD-14 §14.5 + adjacent §C-OD-29.2/§30.2/§31.2/§32.2/§33.2 typed-carrier pattern |

**Plan shape preserved.** v1.9's 11-NEW-contract-section structure preserved verbatim. NO new C-OD-NN top-level contract; ONLY a NEW §C-OD-26.6 sub-section under existing C-OD-26 (Cost-attribution invocation contract) + amendment at §C-OD-26.1 invocation prose. No new fail class; no new span site; no new attribute set at §C-OD-29 / §30 / §31 / §32 / §33; no sampling-discipline change.

**Status posture.** Proposed (v1.9) → **Proposed (v1.10)**. v1.10 is an additive contract authoring (NEW §C-OD-26.6) + minor amendment (§C-OD-26.1 invocation prose). No v1.9 contract removed; no acceptance criterion change at preserved sections.

**Adjacent defects surfaced (not patched per FM-2 no-extension discipline).**

(i) **CostRecordAuditPayload field-set canonical vs idealized.** CXA v2.9 §0.3 row 8 enumerates an idealized 7-field shape (provider + model_id + usage_input_tokens + usage_output_tokens + usage_total_cost_usd + step_action_id + cumulative_cost_usd). The empirical SpanCostRecord at `harness-od/src/harness_od/idempotency_join_dedup.py:134` carries different fields (12+3 fields including span_id, idempotency_key, total_cost, total_latency_ms, derived_keys, engine_replay_disposition, retry_attempt_number, retry_cause_attribution, is_replay_derived, provider_discriminator, gen_ai_provider_name, gen_ai_request_model). The §C-OD-26.6 declaration below pins the projectable subset — `gen_ai_provider_name` (CXA "provider"), `gen_ai_request_model` (CXA "model_id"), `total_cost` (CXA "usage_total_cost_usd"), `span_id` + `idempotency_key` (audit-trail join keys per C-OD-24.4); `usage_input_tokens` + `usage_output_tokens` + `cumulative_cost_usd` deferred to implementation discretion at U-OD-41 impl arc per `[[halt-route-split-AC-pattern]]` precedent (cumulative_cost_usd is a downstream rollup-time field per U-OD-21 `rollup_costs_by_axis` not computable at per-span audit-write moment; usage_input_tokens / usage_output_tokens are upstream from SpanCostRecord at SpanTotalCost layer per OD spec v1.7 §14.4 — projectable but require upstream attribution wiring). Surfaced; the canonical CXA cite at v2.9 row 8 is preserved as forward-cite; precise field enumeration at §C-OD-26.6 pins the v1.10 contract.

(ii) **CXA v2.9 §0.7(iii) U-OD-41 plan revision adjacent-finding.** CXA v2.9 explicitly enumerated U-OD-41 plan revision as a separately-owed sub-arc B deliverable. This v1.10 spec arc co-publishes with the U-OD-41 plan revision at the same session per OD plan v2.16 §0(d) sub-arc B sequel framing; the plan revision is companion-not-blocked-by this spec arc.

(iii) **CXA v2.9 §0.6 forward-cite resolution.** CXA v2.9 §2.3.7 row 8 cites `OD spec v1.10 §C-OD-NN` (placeholder). v1.10 pins the cite resolution: `§C-OD-26.6`. The CXA v2.9 file's forward-cite is RESOLVED at this v1.10 publication; no follow-on CXA amendment required if the pinned `§C-OD-26.6` is byte-exact at this spec.

**Downstream absorption owed (post-v1.10).**

(a) Workspace `CLAUDE.md` §2.3 OD row version bump (v1.9 → v1.10); description amendment to enumerate NEW §C-OD-26.6 + §C-OD-26.1 invocation prose amendment. APPLIED at this batch session.

(b) Co-published artifacts at this session: OD plan v2.16 → v2.17 U-OD-41 plan revision (separately-authored per implementation-planner skill) + U-CP-72 minor revision restoring `cost:` branch + impl code landings (cost_namespace.py NEW module + cp_audit_conversion.py extension + U-OD-41 helper landing + production wiring at cost_attribution_llm_dispatch.py callsite).

(c) Memory entry `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` description amendment: advance status from "PARTIALLY-RESOLVED (cost-axis CXA-side gate MET at CXA v2.9)" to "FULLY-RESOLVED cost-axis (OD spec v1.10 + U-OD-41 + U-CP-72 minor revisions all landed)" post-impl arc close.

(d) CXA v2.9 §0.8(d) sub-arc B sequel — at full impl close, future retirement-event batch may file H_T-OD-5 (cost-attribution chain) status advance per `phase-7-substitution-retirement` discipline (the chain now writes audit entries via the canonical converter path; criterion-B operational-MET shifts).

---

## §1 — §C-OD-26.6 NEW typed-carrier declaration (v1.10)

NEW sub-section under existing C-OD-26 (Cost-attribution invocation contract), positioned after §C-OD-26.5 (Deferred to implementation discretion). Pattern parallel to §C-OD-30.2 PauseResumeAuditPayload + §C-OD-29.2 ValidatorEscalationAuditPayload + §C-OD-31.2 TrustEvaluationAuditPayload + §C-OD-32.2 WebhookDeliveryAuditPayload + §C-OD-33.2 OperatorBurdenAuditPayload.

### §C-OD-26.6 — `CostRecordAuditPayload` typed carrier (NEW at v1.10)

**Contract surface.** Pydantic v2 BaseModel carrier consumed by `cp_audit_to_od_audit` at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` when a `cost:` action_id prefix fires. Production module-home: `harness-od/src/harness_od/cost_namespace.py` (NEW at U-OD-41 impl arc). Extends nothing (sibling Pydantic v2 BaseModel per the AuditPayload-subclass convention); composed at U-OD-41 helper `_project_cost_record_to_audit_payload(attached: SpanCostRecord) -> CostRecordAuditPayload` from the per-span `SpanCostRecord` carrier (existing at OD spec v1.7 §14.4 + 15-field shape per OD plan v2.8 §3.5.3 D-5 amendment).

**Field set (Pydantic v2 BaseModel, `model_config = ConfigDict(extra="forbid", frozen=True)`).**

```python
class CostRecordAuditPayload(BaseModel):
    """Cost-attribution per-span audit payload — Sub-arc B carrier.

    Projected from SpanCostRecord (existing C-OD-14 §14.4 12+3-field carrier
    at harness-od/src/harness_od/idempotency_join_dedup.py) at every billable-
    span exit per §C-OD-26.1 canonical invocation. Consumed by the
    `cp_audit_to_od_audit` converter via the `cost:` action_id prefix branch
    per CXA v2.9 §2.3.7 row 8. Output is the OD-canonical AuditLedgerEntry
    signed and ready for `audit_writer.append`.

    Pattern: parallel to PauseResumeAuditPayload (§C-OD-30.2) +
    ValidatorEscalationAuditPayload (§C-OD-29.2) + the 3 other CP-sourced
    AuditPayload subclasses. The 4 audit_cp_* common fields are the shared
    field-set per C-OD-24.6 `audit.cp.*` sub-namespace discipline.

    Sub-namespace tagging: `audit.cost.*` per CXA v2.9 §0.4 attribution
    convention (cost-attribution is OD-axis-owned namespace per harness-od/
    CLAUDE.md cost-attribution chain ownership; §C-OD-24.6 sub-namespace
    extends OD-canonical audit.* per C-OD-05 §5.1).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    # --- 4 audit_cp_* common fields (shared across all CP-sourced AuditPayload subclasses per §C-OD-24.6 — empirical pattern at sibling PauseResumeAuditPayload at harness-od/src/harness_od/pause_resume_namespace.py:216-227) ---

    audit_cp_action_id: str
    """CP-side action_id with `cost:` prefix per CXA v2.9 §2.3.7 row 8 +
    discriminator-table action_id pattern `cost:<workflow_id>:<step_action_id>`.
    Discriminator at OD audit-trace consumers."""

    audit_cp_response: str
    """`"cost_attributed"` per OD spec v1.8 §C-OD-26.3 prose (preserved
    verbatim at v1.9 + v1.10). Mirrors `audit_cp_response` convention at
    sibling PauseResumeAuditPayload (`"paused"` / `"resumed"` /
    `"diff_detected"` values) + other AuditPayload subclasses."""

    audit_cp_timestamp: str
    """ISO-8601 UTC timestamp at cost-attribution moment (per-span exit) OR
    `""` at MVP per v1.7 §24.4 NOTE 8a-iii (sentinel-empty-string when
    timestamp source not yet wired). String-typed per existing convention at
    sibling subclasses (Pydantic v2 serialization at audit-ledger row write)."""

    audit_cp_prior_event_hash: str
    """SHA-256 hex (64 chars) prior CP-event hash per the SHA-256 chain per
    C-IS-06 + C-IS-13 §13.5. `"0"*64` at MVP when prior is absent (first
    cost-record in workflow). String-typed (not `str | None`) per the
    empirical sibling-subclass convention — sentinel zero-hash rather than
    None per pause_resume_namespace.py:226-227 precedent."""

    # --- cost-attribution-specific fields (per CXA v2.9 §0.3 row 8 prose enumeration; projectable subset of SpanCostRecord) ---

    span_id: str
    """The span_id from SpanCostRecord (idempotency_join_dedup.py:135). Maps
    to CXA v2.9 row 8 audit-trail join key per C-OD-24.4."""

    idempotency_key: str
    """The parent span's idempotency_key from SpanCostRecord (idempotency_join_dedup.py:136
    + §14.4 join key). Maps to CXA v2.9 row 8 idempotency-anchor per
    C-OD-24.4 invariant."""

    provider: str
    """The gen_ai_provider_name from SpanCostRecord (D-5 v2.8 amendment).
    Maps to CXA v2.9 row 8 `provider` field (C-OD-04 §4.3 base-layer
    attribute)."""

    model_id: str
    """The gen_ai_request_model from SpanCostRecord. Maps to CXA v2.9 row 8
    `model_id` field (C-OD-04 §4.3 base-layer attribute)."""

    usage_total_cost_usd: float
    """The total_cost from SpanCostRecord (U-OD-19 SpanTotalCost.total_cost
    USD). Maps to CXA v2.9 row 8 `usage_total_cost_usd` field. Always
    populated at billable-span exit per §C-OD-26.1 canonical invocation."""

    # --- deferred to implementation discretion at U-OD-41 impl arc per change-note (i) ---

    # usage_input_tokens / usage_output_tokens — upstream from SpanCostRecord
    # at SpanTotalCost layer per OD spec v1.7 §14.4; projectable but require
    # upstream attribution wiring at U-OD-41 helper construction. May be
    # added as Optional fields at U-OD-41 impl OR carried via gen_ai.usage.*
    # span attribute pass-through. Implementer-discretion per FM-2.

    # cumulative_cost_usd — downstream rollup field per U-OD-21
    # rollup_costs_by_axis; NOT available at per-span audit-write moment.
    # Deferred indefinitely; carried at separate rollup-event audit shape
    # if needed at future arc.
```

**Path discipline.** No operator-supplied paths; the payload is composed entirely from `SpanCostRecord` + the parent's `step_context.parent_action_id` (for `audit_cp_action_id` pattern `cost:<workflow_id>:<step_action_id>`).

### §C-OD-26.6.1 Per-payload composition discipline

1. **Helper-composed.** The `CostRecordAuditPayload` is constructed only via the canonical helper `_project_cost_record_to_audit_payload(attached: SpanCostRecord) -> CostRecordAuditPayload` at U-OD-41 impl. Direct construction at other call sites is forbidden (the helper enforces the action_id prefix pattern + ISO-8601 timestamp formatting + provider-name normalization).
2. **`audit_cp_action_id` pattern.** `cost:<workflow_id>:<step_action_id>` per CXA v2.9 §0.3 row 8 discriminator-table extension. The `<workflow_id>` is the parent workflow's identifier from `step_context.workflow_id`; the `<step_action_id>` is the billable span's parent step action_id (the LLM dispatch / tool dispatch / etc. that caused the cost attribution).
3. **`audit_cp_prior_event_hash` chain.** Joins via `idempotency_key` per existing C-OD-24.4 invariant; the helper extracts the prior CP event hash from `step_context.parent_event_hash` if available, otherwise the `"0"*64` sentinel (first cost-record in workflow). String-typed (not Optional) per sibling-subclass convention at PauseResumeAuditPayload.
4. **`audit_cp_response` constant.** Hard-coded to `"cost_attributed"` per §C-OD-26.3 prose-mandated value. The helper sets the field at construction (NOT a Pydantic field-with-default — preserves sibling-subclass uniformity where the response value is helper-set per subclass: PauseResumeAuditPayload sets `"paused"`/`"resumed"`/`"diff_detected"`; CostRecordAuditPayload sets `"cost_attributed"`).
5. **Frozen / extra-forbid.** `model_config = ConfigDict(extra="forbid", frozen=True)` per the established AuditPayload-subclass convention (immutable; rejects unknown fields at construction to catch CXA cite drift early).

### §C-OD-26.6.2 Converter integration (cp_audit_to_od_audit `cost:` branch restoration)

The `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` MUST be extended at U-CP-72 minor revision per CXA v2.9 §0.7(i) un-STRIKE adjacent-finding routing:

1. **Import added:** `from harness_od.cost_namespace import CostRecordAuditPayload` (NEW module per U-OD-41 impl).
2. **Namespace prefix constant added:** `COST_AUDIT_NAMESPACE_PREFIX = "audit.cost"` per the established sub-namespace pattern at sibling 5 constants (`WEBHOOK_AUDIT_NAMESPACE_PREFIX`, `OPERATOR_BURDEN_AUDIT_NAMESPACE_PREFIX`, `VALIDATOR_AUDIT_NAMESPACE_PREFIX`, `MCP_TRUST_AUDIT_NAMESPACE_PREFIX`, `PAUSE_RESUME_AUDIT_NAMESPACE_PREFIX`).
3. **`CpAuditCarrier` union extended:** Add `| CostRecordAuditPayload` to the union member list.
4. **isinstance branch added:** Parallel to the existing 5 producer-specific branches — `elif isinstance(cp_entry, CostRecordAuditPayload):` constructs `AuditPayload` with `_project_producer_namespace_attrs(cp_entry, COST_AUDIT_NAMESPACE_PREFIX)` and `cp_entry.audit_cp_action_id` for `entry_core` resolution.
5. **`cost:` STRUCK fallback removed:** The TypeError message at `cp_audit_conversion.py:293-299` referencing "cost: prefix STRUCK per .harness/class_1_fork_u_cp_72_cost_and_pause_resume_prefix_gap.md §2.2 — Sub-arc B owed" is replaced with the standard "unsupported carrier type" error message (no longer cost-specific; the cost branch is reachable post-Sub-arc B close).

### §C-OD-26.6.3 Failure-mode taxonomy

No new fail class introduced at v1.10. The `cost_chain_noop` fallback per §C-OD-26.4 invariant 3 (existing — `PRICE_TABLE_REF` resolution failures fall back to cost_chain_noop without error) preserves the existing failure-mode behavior. CostRecordAuditPayload construction at the helper is guarded by Pydantic v2 validation (`extra="forbid"` catches drift; type validation catches mis-projected SpanCostRecord fields); construction failures surface as `pydantic.ValidationError` which the U-OD-41 helper MAY catch and log per implementer discretion (no fail-class commitment at v1.10).

### §C-OD-26.6.4 Invariants

1. **CostRecordAuditPayload constructed only via helper.** Per §26.6.1; direct construction is forbidden.
2. **`audit_cp_action_id` always carries `cost:` prefix.** Enforced at helper construction (Pydantic v2 validator MAY be added at impl OR helper inlines the prefix-format string).
3. **Audit-write idempotent via `idempotency_key`.** Joins to parent IS state-ledger entry per existing C-OD-24.4 invariant; downstream `audit_writer.append` is idempotent on idempotency_key.
4. **No spec-extension at carrier-deferred fields.** Per change-note (i): `usage_input_tokens`/`usage_output_tokens`/`cumulative_cost_usd` are NOT in the v1.10 field set; they MAY be added at a future v1.x revision when SpanCostRecord upstream attribution wiring lands at U-OD-41 impl arc. v1.10 explicitly disclaims their inclusion.

### §C-OD-26.6.5 Deferred to implementation discretion

- **`usage_input_tokens` / `usage_output_tokens` projection.** Upstream from SpanCostRecord at SpanTotalCost layer per OD spec v1.7 §14.4. May be added as Optional fields at U-OD-41 impl OR carried via gen_ai.usage.* span attribute pass-through. Implementer-discretion per FM-2.
- **`cumulative_cost_usd` projection.** Downstream rollup field per U-OD-21 rollup_costs_by_axis; NOT available at per-span audit-write moment. Carried at separate rollup-event audit shape if needed at future arc.
- **Helper module location.** `harness-od/src/harness_od/cost_namespace.py` is the recommended-default per the sibling-namespace-module pattern; implementer MAY select a different module path at U-OD-41 impl per package-internal organization discretion.
- **Production callsite migration timing.** The §C-OD-26.1 v1.10 invocation pattern is the canonical shape post-v1.10. Current production code at `cost_attribution_llm_dispatch.py:198-202` (operational since U-OD-38 landing) uses the pre-v1.10 CPAuditLedgerEntry path with `cost:{span_id}` action_id pattern (documented placeholder per the function's docstring at line 222). Migration of production code to the v1.10 typed CostRecordAuditPayload path + NEW `cost:{workflow_id}:{step_action_id}` pattern requires widening `attribute_llm_dispatch_cost` signature to accept `workflow_id` + `parent_action_id` kwargs; migration is OPERATIONAL refinement (not spec-correctness gate) deferred per FM-2 to a follow-on arc per `[[halt-route-split-AC-pattern]]`. Both paths produce valid audit entries; the v1.8 §C-OD-26.3 prose preserved verbatim at v1.10 covers the CPAuditLedgerEntry path; the v1.10 §C-OD-26.6 NEW contract covers the typed path.

---

## §2 — §C-OD-26.1 canonical invocation signature amendment (v1.10)

The v1.8 §C-OD-26.1 canonical invocation signature (preserved verbatim through v1.9) is amended at v1.10 to route through the canonical `cp_audit_to_od_audit` converter consuming a `CostRecordAuditPayload` typed carrier:

**Pre-v1.10 (preserved through v1.9):**

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

**v1.10:**

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
# v1.10: project to typed CostRecordAuditPayload + route through canonical
# `cp_audit_to_od_audit` converter per CXA v2.9 §2.3.7 row 8 + §C-OD-26.6.
cost_payload = _project_cost_record_to_audit_payload(
    attached,
    workflow_id=step_context.workflow_id,
    parent_action_id=step_context.parent_action_id,
    prior_event_hash=step_context.parent_event_hash or "0" * 64,
    timestamp=step_context.timestamp or "",
)
audit_entry = cp_audit_to_od_audit(
    cost_payload,
    key_id=ctx.audit_signing_key_id,
    algo=ctx.audit_signing_algorithm,
    entry_core=StateLedgerEntryRef(<step's F2 state-ledger entry_hash>),
)
ctx.audit_writer.append(tenant_id, audit_entry)
```

**Helper signature change:** `_project_cost_record_to_audit_entry(attached: SpanCostRecord) -> CPAuditLedgerEntry` (v1.8 prose) → `_project_cost_record_to_audit_payload(attached: SpanCostRecord, *, workflow_id: str, parent_action_id: str, prior_event_hash: str, timestamp: str = "") -> CostRecordAuditPayload` (v1.10). The helper renames from `*_audit_entry` → `*_audit_payload` to reflect the output type change (CPAuditLedgerEntry → CostRecordAuditPayload); the additional keyword args (`workflow_id`, `parent_action_id`, `prior_event_hash`, `timestamp`) are needed to compose the 4 `audit_cp_*` common fields per §C-OD-26.6. The `audit_cp_response` field is hard-coded to `"cost_attributed"` inside the helper per §C-OD-26.3 prose-mandated value (not passed as an arg). The `prior_event_hash` arg type is `str` (NOT `str | None`) per the sibling-subclass empirical convention (`"0"*64` sentinel when prior is absent). The `timestamp` arg defaults to `""` (MVP sentinel per §24.4 NOTE 8a-iii).

All other §C-OD-26 sub-sections (§26.2 Billable-span enumeration; §26.3 Audit-ledger write per cost-record prose; §26.4 Invariants; §26.5 Deferred to implementation discretion) preserved verbatim from v1.9 (which preserved verbatim from v1.8). The §26.3 prose "Each billable-span cost-record writes one audit entry with `audit.cp.action_id = f"cost:{span_id}"` + `audit.cp.response = "cost_attributed"` (via the converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`)" remains canonical — the v1.10 amendment at §26.1 OPERATIONALIZES the §26.3 contract via the typed CostRecordAuditPayload + canonical converter path.

**Note on §26.3 `action_id` pattern.** §26.3 prose says `audit.cp.action_id = f"cost:{span_id}"` — at v1.10 implementation, the §C-OD-26.6 `audit_cp_action_id` field uses the more-specific pattern `cost:<workflow_id>:<step_action_id>` per CXA v2.9 §0.3 row 8 discriminator-table (workflow-scoped + step-anchored). The `span_id` in the §26.3 prose maps to `<step_action_id>` at impl (the billable span's parent step action_id, not the cost-record's own span_id). The §26.3 prose is preserved verbatim per FM-2; the more-specific pattern is operationalized at §C-OD-26.6 + helper construction. Adjacent finding: §26.3 prose may be tightened at a future v1.x revision to align byte-exact with the CXA v2.9 §0.3 pattern; surfaced at this v1.10 change-note (i) for future routing.

---

## §3 — Preservation guarantees

| Section | Preservation |
|---|---|
| All v1.9 contracts (C-OD-25 through C-OD-33 including v1.8 NEW + v1.9 absorbed amendments) | Preserved verbatim outside the two amendment sites at §C-OD-26.1 + §C-OD-26.6 |
| v1.9 §C-OD-30.1 attribute-type-citation absorption (`WorkflowPauseReason per CP spec v1.11 §26.2`) | Preserved verbatim |
| v1.8 §C-OD-30.2 `PauseResumeAuditPayload` declaration | Preserved verbatim |
| v1.8 §C-OD-30.3 sampling discipline | Preserved verbatim |
| v1.8 §24 audit-ledger schema + C-OD-24 4-section chain + `compute_entry_hash` helper | Preserved verbatim |
| All v1.8 NEW contracts (C-OD-25, C-OD-27, C-OD-28, C-OD-29, C-OD-31, C-OD-32, C-OD-33) | Preserved verbatim |
| §C-OD-26.1 v1.9 invocation signature | **AMENDED at v1.10** per §2 above (canonical converter path replaces helper-only shape) |
| §C-OD-26.2 Billable-span enumeration | Preserved verbatim from v1.9 (which preserved verbatim from v1.8) |
| §C-OD-26.3 Audit-ledger write per cost-record prose | Preserved verbatim |
| §C-OD-26.4 Invariants | Preserved verbatim |
| §C-OD-26.5 Deferred to implementation discretion | Preserved verbatim |
| §C-OD-26.6 (NEW) CostRecordAuditPayload typed carrier | **NEW at v1.10** per §1 above |

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_10.md` |
| Version | v1.10 |
| Filing event | Sub-arc B sequel landing per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §6 + OD plan v2.16 §0(d) operator preference (i) revise-signature + CXA v2.9 §0.7(ii) adjacent-finding routing. 2026-05-24 |
| Predecessor | `Spec_Operational_Discipline_v1_9.md` (v1.9 substantive content preserved verbatim outside the §C-OD-26.1 amendment + §C-OD-26.6 NEW sub-section) |
| Successor | (none — current canonical) |
| Co-published with | `Cross_Axis_Composition_Document_v2_9.md` (already landed at HEAD `39e4f1c` 2026-05-24, §2.3.7 row 8 cost-attribution audit-write seam + forward-cite OD spec v1.10 §C-OD-NN — RESOLVED at this v1.10 publication to §C-OD-26.6) + `Implementation_Plan_Operational_Discipline_v2_17.md` (companion U-OD-41 plan revision at this session) + impl arc landings (cost_namespace.py NEW + cp_audit_conversion.py extension + U-OD-41 helper + production wiring) |
| Status posture | Proposed (v1.9) → Proposed (v1.10). v1.10 is an additive contract authoring (NEW §C-OD-26.6) + minor amendment (§C-OD-26.1 invocation prose). |
| Operator authority | `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6 + OD plan v2.16 §0(d) operator preference (i) revise-signature noted at session checkpoint |
| Related forks | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (cost-axis advance — Sub-arc B publishing CostRecordAuditPayload class; cp_audit_to_od_audit `cost:` branch un-STRIKE owed at U-CP-72 minor revision impl arc) |
| Related memory | `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` (advance status); `[[halt-route-split-AC-pattern]]` (cumulative_cost_usd / usage_input_tokens / usage_output_tokens deferred at §C-OD-26.6 per FM-2); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` (post-arc retirement-event batch may file H_T-OD-5 status advance per CXA v2.9 §0.8(d) + this v1.10 cost-axis chain close) |
| Date | 2026-05-24 |
