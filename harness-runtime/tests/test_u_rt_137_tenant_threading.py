"""`U-RT-137` ⊕ `U-CP-72` — tenant threading at converter-based production
call sites (runtime halves).

Implements `Implementation_Plan_Harness_Runtime_v2_49.md` §1.4 (Runtime spec
v1.101 surface D; OD v1.34 §21.2.1 rows 1-3; CP v1.101 §1 row 4). Plan-named
witnesses here:

- `test_converter_call_sites_thread_step_context_tenant_id_producing_five_segment_message`
  (parametrized over the six converter-based production call sites: the HITL
  8c-HITL compose, the four cost-attribution builders, and — via the
  lifecycle fixture file — the sub-agent 8c compose, whose sibling witness
  lives at `test_lifecycle_sub_agent_dispatch.py::test_u_rt_137_*`);
- `test_tenant_absent_call_sites_byte_identical_end_to_end` (acc 4 — the
  drop-when-`None` chain end-to-end: four-tuple canonical message
  byte-for-byte);
- `test_redaction_map_append_signs_five_tuple_with_tenant` (acc 3 — the
  redaction call-site rewire landed at U-OD-30/PR #1061; this is its
  plan-named end-to-end SIGNED-MESSAGE witness).

The converter-unit halves (CP witness (a)) live at
`harness-cxa/tests/test_u_cp_72_tenant_passthrough.py`.
"""

from __future__ import annotations

from typing import Any, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_cp.gate_level_rule import GateLevel
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind
from harness_cp.workflow_driver_types import StepExecutionContext
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_od.multi_tenant_trace_separation_and_audit_ledger import (
    canonical_od_signing_message,
    signing_token,
)
from harness_od.rate_table_v1 import RATE_TABLE_V1
from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
from harness_runtime.lifecycle.cost_attribution_llm_dispatch import (
    attribute_llm_dispatch_cost,
)
from harness_runtime.lifecycle.cost_attribution_tool_dispatch import (
    attribute_tool_dispatch_cost,
)
from harness_runtime.lifecycle.cost_attribution_validator_dispatch import (
    attribute_validator_dispatch_cost,
)
from harness_runtime.lifecycle.cost_attribution_webhook_dispatch import (
    attribute_webhook_dispatch_cost,
)

_TENANT = "tenant-137"


class _CapturingEd25519Backend:
    """TEST-ONLY C-CP-20 §20.2.1 `SigningBackend` double (real Ed25519) that
    RECORDS every message it signs — the witness surface for the canonical
    four-vs-five-segment signing message."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        self._private_key = Ed25519PrivateKey.generate()
        self.messages: list[bytes] = []

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_id, key_period
        self.messages.append(message)
        return self._private_key.sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del message, signature, key_id, key_period
        return True


def _segments(message: bytes) -> list[str]:
    """Parse the length-prefixed `len:part` segments joined by `|`."""
    out: list[str] = []
    rest = message.decode()
    while rest:
        length_str, _, tail = rest.partition(":")
        n = int(length_str)
        out.append(tail[:n])
        rest = tail[n:]
        if rest.startswith("|"):
            rest = rest[1:]
    return out


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None = None, audit_entry: object = None, **kwargs: Any):
        if kwargs:
            tenant_id = kwargs.get("tenant_id", tenant_id)
            audit_entry = kwargs.get("audit_entry", audit_entry)
        self.appended.append((tenant_id, audit_entry))
        return "appended"


class _MockLedgerWriter:
    def append(self, payload: Any, key: Any) -> Any:
        return ("entry-hash", payload, key)


def _step_context(tenant_id: str | None) -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="test-wf-137",
        parent_action_id="workflow:test-wf-137:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-u-rt-137"),
        parent_entry_hash="",
        parent_idempotency_key="u137-idem",
        tenant_id=tenant_id,
        step_index=0,
    )


# ---------------------------------------------------------------------------
# The call-site triggers. Each drives the REAL production code path that
# invokes `cp_audit_to_od_audit` and returns the capturing backend.
# ---------------------------------------------------------------------------


def _site_hitl(tenant_id: str | None) -> _CapturingEd25519Backend:
    from harness_runtime.lifecycle.hitl_gate_composer import RuntimeHITLGateComposer

    backend = _CapturingEd25519Backend()
    composer = RuntimeHITLGateComposer(
        inner=cast(Any, object()),
        applicable_placements=frozenset({HITLPlacementKind.PRE_ACTION}),
        ask_user_question_surface=cast(Any, object()),
        ledger_writer=cast(Any, _MockLedgerWriter()),
        audit_writer=cast(Any, _RecordingAuditWriter()),
        tracer_provider=None,
        audit_signing_key_id="harness-runtime-test",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        procedural_tier_snapshot_resolver=lambda: Identifier("b" * 64),
        signing_backend=cast(Any, backend),
    )
    cp_entry, write_result = composer._compose_and_persist_audit(
        parent_action_id=cast(Any, "workflow:test-wf-137:step:0"),
        placement=HITLPlacement(position=HITLPlacementKind.PRE_ACTION),
        cell=cast(Any, None),
        gate_result=None,
        step_context=_step_context(tenant_id),
        raise_on_failure=True,
        auto_approved=True,
    )
    assert cp_entry is not None and write_result is not None
    return backend


def _site_cost_llm(tenant_id: str | None) -> _CapturingEd25519Backend:
    backend = _CapturingEd25519Backend()
    attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=cast(Any, _RecordingAuditWriter()),
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="0123456789abcdef",
        parent_idempotency_key="u137-idem",
        workflow_id="test-wf-137",
        parent_action_id="workflow:test-wf-137:step:0",
        input_tokens=1000,
        output_tokens=500,
        tenant_id=tenant_id,
        signing_backend=cast(Any, backend),
    )
    return backend


def _site_cost_tool(tenant_id: str | None) -> _CapturingEd25519Backend:
    from decimal import Decimal

    from harness_od.rate_table_types import RateTable, ToolRate, WebhookRate

    backend = _CapturingEd25519Backend()
    tool_rate_table = RateTable(
        version="2026-07-20-u137-test",
        providers={},
        tool_rates={"echo": ToolRate(cost_kind="flat_per_invocation", rate=Decimal("0.005"))},
        webhook_rate=WebhookRate(flat_per_attempt=Decimal("0"), plus_egress=False),
        cpu_rate_per_ms=Decimal("0"),
        egress_rate_per_byte=Decimal("0"),
    )
    attribute_tool_dispatch_cost(
        rate_table=tool_rate_table,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=cast(Any, _RecordingAuditWriter()),
        tool_id="echo",
        tool_args={"message": "hi"},
        response={"ok": True},
        span_id="0123456789abcdef",
        idempotency_key="u137-tool-idem",
        parent_idempotency_key="u137-idem",
        workflow_id="test-wf-137",
        parent_action_id="workflow:test-wf-137:step:0",
        tenant_id=tenant_id,
        signing_backend=cast(Any, backend),
    )
    return backend


def _site_cost_webhook(tenant_id: str | None) -> _CapturingEd25519Backend:
    backend = _CapturingEd25519Backend()
    attribute_webhook_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=cast(Any, _RecordingAuditWriter()),
        webhook_target="https://ops.example.com/hitl",
        bytes_sent=128,
        span_id="0123456789abcdef",
        idempotency_key="u137-webhook-idem",
        parent_idempotency_key="u137-idem",
        workflow_id="test-wf-137",
        parent_action_id="workflow:test-wf-137:step:0",
        tenant_id=tenant_id,
        signing_backend=cast(Any, backend),
    )
    return backend


def _site_cost_validator(tenant_id: str | None) -> _CapturingEd25519Backend:
    backend = _CapturingEd25519Backend()
    attribute_validator_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=cast(Any, _RecordingAuditWriter()),
        validator_id="validator-1",
        execution_time_ms=12.5,
        span_id="0123456789abcdef",
        idempotency_key="u137-validator-idem",
        parent_idempotency_key="u137-idem",
        workflow_id="test-wf-137",
        parent_action_id="workflow:test-wf-137:step:0",
        tenant_id=tenant_id,
        signing_backend=cast(Any, backend),
    )
    return backend


_SITES = [
    ("hitl_gate_composer 8c-HITL", _site_hitl),
    ("cost_attribution_llm_dispatch", _site_cost_llm),
    ("cost_attribution_tool_dispatch", _site_cost_tool),
    ("cost_attribution_webhook_dispatch", _site_cost_webhook),
    ("cost_attribution_validator_dispatch", _site_cost_validator),
]


@pytest.mark.parametrize(("site_name", "trigger"), _SITES, ids=[s for s, _ in _SITES])
def test_converter_call_sites_thread_step_context_tenant_id_producing_five_segment_message(
    site_name: str,
    trigger: Any,
) -> None:
    """Acc 1 (pairs with CP witness (a) / OD witness (a)): every
    converter-based production call site threads the tenant RAW to signing —
    the backend-observed canonical message carries FIVE length-prefixed
    segments whose fifth is the OD-normalized `signing_token` of the
    step-context tenant (normalization at signing, never at the call site).

    Mutation probe (per site): deleting the site's `tenant_id=` argument
    reverts signing to the four-tuple → the segment-count assertion FAILS.

    (The sixth site — sub-agent 8c — is witnessed with its own fixtures at
    `test_lifecycle_sub_agent_dispatch.py::test_u_rt_137_sub_agent_compose_signs_five_segment_with_tenant`.)
    """
    backend = trigger(_TENANT)
    assert backend.messages, f"{site_name}: the signing backend was never consulted"
    segments = _segments(backend.messages[-1])
    assert len(segments) == 5, f"{site_name}: expected the five-segment message, got {segments}"
    assert segments[4] == signing_token(_TENANT), (
        f"{site_name}: the fifth segment must be the OD-normalized tenant token"
    )


@pytest.mark.parametrize(("site_name", "trigger"), _SITES, ids=[s for s, _ in _SITES])
def test_tenant_absent_call_sites_byte_identical_end_to_end(
    site_name: str,
    trigger: Any,
) -> None:
    """Acc 4 (pairs with OD witness (b)): tenant absent (single-tenant
    deployments) → the signed canonical message is the pre-amendment
    FOUR-tuple byte-for-byte (the drop-when-`None` chain end-to-end),
    reconstructed via the exported `canonical_od_signing_message` with no
    tenant segment."""
    backend = trigger(None)
    assert backend.messages, f"{site_name}: the signing backend was never consulted"
    message = backend.messages[-1]
    segments = _segments(message)
    assert len(segments) == 4, f"{site_name}: tenant-absent must stay the four-tuple"
    entry_hash, key_id, algo_value, key_period_token = segments
    assert message == canonical_od_signing_message(
        entry_hash,
        key_id=key_id,
        algo_value=algo_value,
        key_period_token=key_period_token,
        tenant_tag=None,
    ), f"{site_name}: four-tuple must be byte-identical to the canonical helper output"


# ---------------------------------------------------------------------------
# Acc 3 — the redaction call-site rewire's end-to-end SIGNED-MESSAGE witness
# (the rewire itself landed at U-OD-30 / PR #1061; U-RT-137 owns the witness).
# ---------------------------------------------------------------------------


def test_redaction_map_append_signs_five_tuple_with_tenant() -> None:
    """Acc 3: an MTC-configured `AuditLedgerRedactionTokenMap` append produces
    a FIVE-segment-signed entry whose tenant tag matches the map's tenant —
    `self._tenant_id` flows through `compose_redaction_token_audit_entry` to
    signing at both compose call sites.

    Mutation probe: dropping the call-site tenant argument
    (`redaction_token_audit_map.py`) leaves the four-tuple and FAILS."""
    from harness_od.redaction_tokenizer import OpaqueRedactionTokenizer
    from harness_runtime.lifecycle.redaction_token_audit_map import (
        AuditLedgerRedactionTokenMap,
    )

    # --- Site 1: the duck-typed cached-position compose (pre-B-50 fallback).
    backend = _CapturingEd25519Backend()
    audit_writer = _RecordingAuditWriter()
    token_map = AuditLedgerRedactionTokenMap(
        audit_writer=cast(Any, audit_writer),
        tenant_id="tenant-r008",
        signing_key_id="redaction-token-test-key",
        signing_backend=cast(Any, backend),
    )
    tokenizer = OpaqueRedactionTokenizer(token_map=token_map)
    tokenizer.tokenize(
        attribute_key="mcp.tool.call.arguments",
        raw_value='{"secret":"value"}',
        trace_id="trace-137",
        span_id="span-137",
    )

    assert backend.messages, "the redaction append must consult the signing backend"
    segments = _segments(backend.messages[-1])
    assert len(segments) == 5, f"expected the five-segment message, got {segments}"
    assert segments[4] == signing_token("tenant-r008")
    assert len(audit_writer.appended) == 1

    # --- Site 2: the B-50 transaction compose (the PRODUCTION runtime-writer
    # path — the writer exposes `tenant_transaction`; both compose call sites
    # must thread the tenant, so each is pinned independently).
    class _TxnWriter:
        def __init__(self) -> None:
            self.appended: list[object] = []

        class _Txn:
            def __init__(self, outer: Any) -> None:
                self._outer = outer

            def __enter__(self) -> Any:
                return self

            def __exit__(self, *_a: Any) -> None:
                return None

            def redaction_family_tail(self) -> str | None:
                return None

            def append(self, audit_entry: object) -> None:
                self._outer.appended.append(audit_entry)

        def tenant_transaction(self, _tenant_id: str | None) -> Any:
            return self._Txn(self)

        def append(self, tenant_id: str | None, audit_entry: object) -> object:
            raise AssertionError("transaction path must not use the bare append")

    txn_backend = _CapturingEd25519Backend()
    txn_writer = _TxnWriter()
    txn_map = AuditLedgerRedactionTokenMap(
        audit_writer=cast(Any, txn_writer),
        tenant_id="tenant-r008",
        signing_key_id="redaction-token-test-key",
        signing_backend=cast(Any, txn_backend),
    )
    OpaqueRedactionTokenizer(token_map=txn_map).tokenize(
        attribute_key="mcp.tool.call.arguments",
        raw_value='{"secret":"value2"}',
        trace_id="trace-137b",
        span_id="span-137b",
    )
    assert txn_backend.messages, "the transaction compose must consult the signing backend"
    txn_segments = _segments(txn_backend.messages[-1])
    assert len(txn_segments) == 5, f"expected the five-segment message, got {txn_segments}"
    assert txn_segments[4] == signing_token("tenant-r008")
    assert len(txn_writer.appended) == 1
