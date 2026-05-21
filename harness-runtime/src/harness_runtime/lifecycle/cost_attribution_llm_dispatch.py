"""U-OD-38 — cost-attribution helper for LLM dispatch.

Per OD spec v1.8 §C-OD-26.1 + §26.2 row "llm_dispatch": every LLM dispatch
must invoke the cost-attribution chain post-provider-call and write one
audit-ledger entry. This helper packs the §26.1 5-substep convention into a
single callable invoked from `RuntimeLLMDispatcher.dispatch`:

  1. Resolve per-(provider, model) rates from the RateTable
     (`harness_od.rate_table_resolver.resolve_for`).
  2. Bridge Decimal ProviderRates → float PriceRateEntry
     (`harness_od.rate_table_bridge.provider_rates_to_price_rate_entry`).
  3. Compute per-attempt cost via the cost chain
     (`CostAttributionChain.compute_per_attempt_cost`).
  4. Build a SpanCostRecord; attach idempotency_key joining to the IS state
     ledger parent entry (`CostAttributionChain.attach_idempotency_key`).
  5. Project the cost-record to a CPAuditLedgerEntry shape and pass through
     the `cp_audit_to_od_audit` converter to obtain a signed
     AuditLedgerEntry; append via `audit_writer.append`.

Home rationale: this helper composes OD types (SpanCostInputs / PriceRateEntry /
SpanCostRecord) + CXA converter + runtime Protocols. OD's downstream-consumer
invariant (`harness-od/CLAUDE.md` §1.1 — 0 outbound cross-axis edges)
prohibits OD importing runtime; the helper lives at runtime instead.

Per AC #5 (U-OD-38): "1 LLM call → 1 cost-record + 1 audit-ledger entry".
The helper returns the cost-record for caller-side telemetry attribute
emission via U-OD-49 string-form serialization at the OTel boundary.

Per AC #1 + AC #4 (U-OD-38): cost-attribution invoked on every LLM dispatch
(success + failure paths). PRICE_TABLE_REF resolution failure raises
`RateTableMissingError` (CP-FAIL-RATE-TABLE-MISSING) per §C-OD-28.2 default
fail-closed.

Authority:
- `Spec_Operational_Discipline_v1_8.md` §C-OD-26 + §C-OD-28
- `Implementation_Plan_Operational_Discipline_v2_14.md` U-OD-38
- `Cross_Axis_Composition_Document_v2_6.md` §2.3.7 (CP→OD audit seam)
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from harness_core.identity import ActionID
from harness_cp.engine_namespace import ReplayDisposition
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import CPAuditLedgerEntry
from harness_cxa.cp_audit_conversion import cp_audit_to_od_audit
from harness_od.audit_ledger_types import AuditLedgerEntry
from harness_od.cost_formula import PriceRateKey, SpanCostInputs
from harness_od.idempotency_join_dedup import SpanCostRecord
from harness_od.rate_table_bridge import provider_rates_to_price_rate_entry
from harness_od.rate_table_resolver import resolve_for
from harness_od.rate_table_types import RateTable

from harness_runtime.types import AuditLedgerWriter, CostAttributionChain

#: Canonical signing key id used for cost-attribution audit entries at v1.
#: Operator overrides via bootstrap config in production per ADR-D5 v1.4
#: §1.4.1 + C-OD-21 §21.2. Same convention as the U-RT-59 Fork 2 sub-agent
#: dispatch audit-write path at `sub_agent_dispatch.py`.
_DEFAULT_SIGNING_KEY_ID = "harness-cost-attribution-v1"

#: Default ReplayDisposition for live LLM dispatches outside a replay
#: context. Per ADR-D1 v1.2 §1.1.1, NO_REPLAY is the PURE_PATTERN_NO_ENGINE
#: disposition — the dominant case for at-the-edge LLM calls.
_DEFAULT_REPLAY_DISPOSITION = ReplayDisposition.NO_REPLAY

#: Family tag for LLM-dispatch cost records per C-OD-05 §5.1 row 15
#: provider_discriminator family taxonomy. Matches the
#: SpanCostRecord.provider_discriminator carrier (str-typed to avoid
#: U-OD-20 → U-OD-21 cycle per the field's docstring).
_LLM_FAMILY_TAG = "llm"


def attribute_llm_dispatch_cost(
    *,
    rate_table: RateTable,
    cost_chain: CostAttributionChain,
    audit_writer: AuditLedgerWriter,
    provider_name: str,
    model: str,
    span_id: str,
    parent_idempotency_key: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation: int = 0,
    cache_read: int = 0,
    tokenizer_version: str | None = None,
    tenant_id: str | None = None,
) -> SpanCostRecord:
    """Run the §C-OD-26.1 5-substep cost-attribution chain for one LLM dispatch.

    Resolves rates → computes cost → attaches idempotency key → projects to
    CPAuditLedgerEntry → converts → appends to audit ledger. Returns the
    idempotency-key-bearing SpanCostRecord so the caller can emit the
    cost.attributed_decimal OTel span attribute per U-OD-49.

    Parameters
    ----------
    rate_table
        The resolved PRICE_TABLE_REF for this workflow's execution (immutable
        post-resolution per §C-OD-28.4 invariant 1).
    cost_chain
        Concrete cost-attribution chain (`RuntimeCostAttributionChain` at v1).
    audit_writer
        Audit-ledger writer (`RuntimeAuditLedgerWriter` at v1).
    provider_name
        LLM provider name from `binding.model_binding.provider` per C-CP-01.
    model
        LLM model id from `binding.model_binding.model`.
    span_id
        The current dispatch span's OTel span_id (hex form) — becomes the
        `cost:{span_id}` action_id.
    parent_idempotency_key
        Parent's `idempotency_key` per C-IS-05 (the F2 state-ledger join key).
        Sourced from `step_context.parent_idempotency_key`.
    input_tokens
        Per-attempt input token count from `gen_ai.usage.input_tokens`.
    output_tokens
        Per-attempt output token count from `gen_ai.usage.output_tokens`.
    cache_creation
        Anthropic-specific cache-creation input tokens (defaults to 0).
    cache_read
        Anthropic-specific cache-read input tokens (defaults to 0).
    tokenizer_version
        anthropic.tokenizer_version attribute; defaults to `"v0"` when absent
        (openai / ollama don't carry this attribute at v1).
    tenant_id
        Tenant scope for audit-ledger append (None → single-tenant).

    Returns
    -------
    SpanCostRecord
        The idempotency-key-bearing cost record — caller emits the
        cost.attributed_decimal OTel attribute via
        `cost_record_otel_serializer.serialize_decimal_for_otel`.

    Raises
    ------
    RateTableMissingError
        Provider not in rate table — CP-FAIL-RATE-TABLE-MISSING per
        §C-OD-28.2 default fail-closed.
    """
    # Substep 1 — resolve rates per (provider, model). Per §C-OD-28.4 inv 4,
    # per-model overrides resolve before falling back to provider-level.
    rates = resolve_for(rate_table, provider=provider_name, model=model)

    # Substep 2 — bridge Decimal ProviderRates → float PriceRateEntry.
    # Class 3 drift: cost_formula.py uses float arithmetic; full-Decimal
    # chain migration deferred (precision loss bounded at ~15 sig digits).
    rate_key = PriceRateKey(
        provider_name=provider_name,
        model=model,
        tokenizer_version=tokenizer_version or "v0",
    )
    rate_entry = provider_rates_to_price_rate_entry(rates, rate_key)

    # Substep 3 — compute per-attempt cost via the chain.
    cost_inputs = SpanCostInputs(
        input_tokens=input_tokens,
        cache_creation=cache_creation,
        cache_read=cache_read,
        output_tokens=output_tokens,
        rate_key=rate_key,
    )
    span_cost = cost_chain.compute_per_attempt_cost(cost_inputs, rate_entry)

    # Substep 4 — build SpanCostRecord; attach idempotency key joining to
    # the IS state-ledger parent entry per C-IS-05 / C-OD-14 §14.4.
    # `SpanRef` (`harness_od.otel_genai_base.SpanRef`) is a TypeAlias for
    # the live OTel-SDK span handle but is unused in attach_idempotency_key
    # body beyond correlation threading (per its docstring). We pass the
    # span_id string itself as the correlation marker; the actual join key
    # is parent_idempotency_key.
    cost_record = SpanCostRecord(
        span_id=span_id,
        idempotency_key="",  # populated at attach_idempotency_key
        total_cost=float(span_cost),
        total_latency_ms=0,  # latency observability deferred to follow-on arc
        derived_keys=(),
        engine_replay_disposition=_DEFAULT_REPLAY_DISPOSITION,
        retry_attempt_number=None,
        retry_cause_attribution=None,
        is_replay_derived=False,
        provider_discriminator=_LLM_FAMILY_TAG,
        gen_ai_provider_name=provider_name,
        gen_ai_request_model=model,
    )
    attached = cost_chain.attach_idempotency_key(
        span_id, parent_idempotency_key, cost_record
    )

    # Substep 5 — project to CPAuditLedgerEntry shape; convert via CXA seam;
    # append to audit ledger. Per §C-OD-26.3, action_id=cost:{span_id},
    # response=cost_attributed.
    audit_entry = _project_and_convert_audit_entry(
        cost_record=attached,
        provider_name=provider_name,
    )
    audit_writer.append(tenant_id, audit_entry)

    # Return the attached SpanCostRecord for caller-side OTel attribute
    # emission via U-OD-49 string-form serialization at the OTel boundary.
    return attached  # type: ignore[no-any-return]


def _project_and_convert_audit_entry(
    *,
    cost_record: object,
    provider_name: str,
) -> AuditLedgerEntry:
    """Project a SpanCostRecord-shape into CPAuditLedgerEntry + convert.

    Per §C-OD-26.3 + the CXA v2.6 §2.3.7 CP→OD audit-seam discipline:
    cost-records project to an audit entry with audit.cp.action_id =
    f"cost:{span_id}" + audit.cp.response = "cost_attributed". The
    CPAuditLedgerEntry shape was designed for HITL audit (gate_level field is
    HITL-semantic) but the cp_audit_to_od_audit converter is generic over
    action_id; we set gate_level=AUTO as a no-op default for non-HITL
    cost-attribution entries. U-CP-72 will canonicalize this projection at
    the converter producer-side rewrite.

    Hash-chain link: `prior_event_hash=""` placeholder follows the existing
    pattern at `RuntimeHandoffRegistry.compose_dispatch_audit` (handoff.py:
    216-218 docstring — placeholder filled at write-time discipline). The OD
    audit chain validity is a follow-on concern; this commit prioritizes
    cost-record emission + audit-ledger persistence over chain-link
    accuracy. Class 3 drift candidate.
    """
    cr: SpanCostRecord = cost_record  # type: ignore[assignment]
    cp_entry = CPAuditLedgerEntry(
        action_id=ActionID(f"cost:{cr.span_id}"),
        gate_level=GateLevel.AUTO,
        response="cost_attributed",
        timestamp=datetime.now(UTC).isoformat(),
        prior_event_hash="",
    )
    _ = provider_name  # reserved for future use (per-provider sub-namespace)
    return cp_audit_to_od_audit(
        cp_entry,
        key_id=_DEFAULT_SIGNING_KEY_ID,
    )


__all__ = [
    "attribute_llm_dispatch_cost",
]


# Pleaser for unused import warnings — Mapping is used at type-annotation
# layer for future extension to per-tenant rate-overrides.
_ = Mapping
