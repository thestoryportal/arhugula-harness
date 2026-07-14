"""U-OD-40 — cost-attribution at hitl.webhook.deliver site tests.

ACs per `Implementation_Plan_Operational_Discipline_v2_14.md` U-OD-40:
  #2 Webhook cost uses WebhookRate.flat_per_attempt + egress
     (cost = flat_per_attempt + egress_rate_per_byte × bytes_sent if plus_egress)
  #3 Cost-record attached at span exit
  #4 Audit-ledger entry written

Production binding-arc concern: invocation at WebhookDeliveryComposer
.deliver_webhook (success + failure paths) covered at integration test
in test_lifecycle_webhook_delivery_composer_cost_attribution.py at task 7.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import read_ledger
from harness_od.rate_table_types import RateTable, WebhookRate
from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
from harness_runtime.lifecycle.cost_attribution_webhook_dispatch import (
    _compute_webhook_cost,
    attribute_webhook_dispatch_cost,
)
from harness_runtime.lifecycle.state_ledger import LedgerWriter


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


def _make_rate_table(
    flat_per_attempt: Decimal,
    plus_egress: bool,
    egress_rate_per_byte: Decimal = Decimal("0"),
) -> RateTable:
    return RateTable(
        version="2026-05-28-test",
        providers={},
        tool_rates={},
        webhook_rate=WebhookRate(
            flat_per_attempt=flat_per_attempt,
            plus_egress=plus_egress,
        ),
        cpu_rate_per_ms=Decimal("0"),
        egress_rate_per_byte=egress_rate_per_byte,
    )


@pytest.fixture
def cost_chain() -> RuntimeCostAttributionChain:
    return RuntimeCostAttributionChain()


@pytest.fixture
def audit_writer() -> _RecordingAuditWriter:
    return _RecordingAuditWriter()


# ---------------------------------------------------------------------------
# AC #2 — Webhook cost formula
# ---------------------------------------------------------------------------


def test_webhook_cost_flat_per_attempt_only() -> None:
    """plus_egress=False: bytes_sent ignored; cost = flat_per_attempt."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=False,
    )
    cost = _compute_webhook_cost(rate_table, bytes_sent=1024)
    assert cost == Decimal("0.01")


def test_webhook_cost_flat_plus_egress() -> None:
    """plus_egress=True: cost = flat + (egress_rate × bytes_sent)."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=True,
        egress_rate_per_byte=Decimal("0.0001"),
    )
    cost = _compute_webhook_cost(rate_table, bytes_sent=100)
    # 0.01 + 0.0001 * 100 = 0.01 + 0.01 = 0.02
    assert cost == Decimal("0.02")


def test_webhook_cost_zero_bytes_with_egress_enabled() -> None:
    """plus_egress=True but bytes_sent=0: cost = flat_per_attempt (egress
    contribution is zero)."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.05"),
        plus_egress=True,
        egress_rate_per_byte=Decimal("0.001"),
    )
    cost = _compute_webhook_cost(rate_table, bytes_sent=0)
    assert cost == Decimal("0.05")


def test_webhook_cost_zero_flat_with_egress() -> None:
    """plus_egress=True + flat=0: cost = egress only (free per-attempt; pay
    by byte)."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0"),
        plus_egress=True,
        egress_rate_per_byte=Decimal("0.0005"),
    )
    cost = _compute_webhook_cost(rate_table, bytes_sent=2000)
    # 0 + 0.0005 * 2000 = 1.0
    assert cost == Decimal("1.0")


def test_webhook_cost_decimal_precision_preserved() -> None:
    """§C-OD-28.4 invariant 2 — Decimal-precision-preserving arithmetic."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.12345678901234567"),
        plus_egress=True,
        egress_rate_per_byte=Decimal("0.00000000123456789"),
    )
    cost = _compute_webhook_cost(rate_table, bytes_sent=12345)
    expected = Decimal("0.12345678901234567") + Decimal("0.00000000123456789") * Decimal(12345)
    assert cost == expected
    assert isinstance(cost, Decimal)


# ---------------------------------------------------------------------------
# AC #3 + AC #4 — full chain returns attached record + 1 audit write
# ---------------------------------------------------------------------------


def test_attribute_webhook_dispatch_cost_returns_attached_record(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Helper returns idempotency-key-bearing SpanCostRecord per AC #3."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=False,
    )
    attached = attribute_webhook_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="https://ops.example.com/hitl",
        bytes_sent=512,
        span_id="abcdef0123456789",
        idempotency_key="webhook-idem-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="hitl:test-wf:gate:0",
    )
    assert attached.span_id == "abcdef0123456789"
    assert attached.idempotency_key == "parent-idem-1"
    assert attached.provider_discriminator is None  # v1.30 — no chain-level family tag
    assert attached.dispatch_kind == "webhook"  # v1.30 — the PER_DISPATCH_KIND key
    assert attached.gen_ai_provider_name == "webhook:https://ops.example.com/hitl"
    assert attached.gen_ai_request_model == ""
    assert attached.total_cost == pytest.approx(0.01, rel=1e-9)


def test_attribute_webhook_dispatch_cost_writes_audit_entry(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """AC #4 — Cost-record attached + audit-ledger entry written."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=True,
        egress_rate_per_byte=Decimal("0.0001"),
    )
    attribute_webhook_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="target-A",
        bytes_sent=100,
        span_id="0011223344556677",
        idempotency_key="webhook-idem-1",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="hitl:test-wf:gate:0",
    )
    assert len(audit_writer.appended) == 1
    tenant_id, audit_entry = audit_writer.appended[0]
    assert tenant_id is None
    attrs = audit_entry.payload.audit_namespace_attrs
    assert attrs["audit.cp.action_id"] == "cost:test-wf:hitl:test-wf:gate:0"
    assert attrs["audit.cp.response"] == "cost_attributed"


def test_attribute_webhook_dispatch_cost_writes_with_tenant(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Multi-tenant routing: tenant_id propagates to audit_writer.append."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=False,
    )
    attribute_webhook_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="t",
        bytes_sent=0,
        span_id="x" * 16,
        idempotency_key="k",
        parent_idempotency_key="p",
        workflow_id="wf",
        parent_action_id="action",
        tenant_id="tenant-B",
    )
    assert audit_writer.appended[0][0] == "tenant-B"


def test_three_webhook_dispatches_produce_three_audit_writes(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """3 sequential webhook dispatches → 3 cost-records + 3 audit entries."""
    rate_table = _make_rate_table(
        flat_per_attempt=Decimal("0.01"),
        plus_egress=False,
    )
    for i in range(3):
        attribute_webhook_dispatch_cost(
            rate_table=rate_table,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            webhook_target=f"target-{i}",
            bytes_sent=100,
            span_id=f"{i:016x}",
            idempotency_key=f"key-{i}",
            parent_idempotency_key=f"parent-{i}",
            workflow_id="wf",
            parent_action_id=f"hitl:wf:gate:{i}",
        )
    assert len(audit_writer.appended) == 3
    action_ids = [
        e[1].payload.audit_namespace_attrs["audit.cp.action_id"] for e in audit_writer.appended
    ]
    assert len(set(action_ids)) == 3


# ---------------------------------------------------------------------------
# B-23 — F2-write entry_core (real IS anchor, not fabricated cp-audit: marker)
# ---------------------------------------------------------------------------

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-cost-attribution")


def _build_ledger_writer(tmp_path: Path) -> LedgerWriter:
    """Real `LedgerWriter` rooted in `tmp_path` — mirrors
    `test_lifecycle_sub_agent_dispatch.py`'s `_build_ledger_writer`."""
    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle

    path = tmp_path / "state.jsonl"
    path.touch()
    handle = JsonlLedgerHandle(canonical_path=path, exists=True, entry_count=0)
    return LedgerWriter(handle=handle, actor=_ACTOR)


def test_ledger_writer_bound_produces_real_entry_core_full_chain(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """B-23 full-chain witness: when `ledger_writer` is bound, the F2 entry
    actually lands in the IS ledger AND the audit entry's `entry_core`
    references that real action_id — not the fabricated
    `cp-audit:<action_id>` marker."""
    rate_table = _make_rate_table(flat_per_attempt=Decimal("0.01"), plus_egress=False)
    ledger_writer = _build_ledger_writer(tmp_path)
    attribute_webhook_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="https://ops.example.com/hitl",
        bytes_sent=512,
        span_id="f2-span-1",
        idempotency_key="webhook-idem-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="hitl:test-wf:gate:0",
        ledger_writer=ledger_writer,
    )
    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 1
    real_action_id = str(cost_entries[0].action_id)
    assert not real_action_id.startswith("cp-audit:")

    _, audit_entry = audit_writer.appended[0]
    assert str(audit_entry.payload.entry_core) == real_action_id


def test_ledger_writer_unbound_preserves_fabricated_marker_fallback(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Backward compatibility — omitting `ledger_writer` preserves the
    converter's pre-existing `cp-audit:<action_id>` fallback."""
    rate_table = _make_rate_table(flat_per_attempt=Decimal("0.01"), plus_egress=False)
    attribute_webhook_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="t",
        bytes_sent=0,
        span_id="f2-span-2",
        idempotency_key="k",
        parent_idempotency_key="p",
        workflow_id="wf",
        parent_action_id="action",
    )
    _, audit_entry = audit_writer.appended[0]
    assert str(audit_entry.payload.entry_core).startswith("cp-audit:")


def test_repeat_delivery_same_step_gets_distinct_f2_entries_not_noop_dropped(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard — two webhook-delivery attempts sharing the same
    (workflow_id, parent_action_id) MUST persist two DISTINCT F2 entries,
    not silently collapse via `IDEMPOTENT_NOOP`."""
    rate_table = _make_rate_table(flat_per_attempt=Decimal("0.01"), plus_egress=False)
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        webhook_target="target",
        bytes_sent=100,
        parent_idempotency_key="parent-retry",
        workflow_id="wf",
        parent_action_id="hitl:wf:gate:0",
        ledger_writer=ledger_writer,
    )
    attribute_webhook_dispatch_cost(span_id="attempt-1", idempotency_key="idem-1", **common)
    attribute_webhook_dispatch_cost(span_id="attempt-2", idempotency_key="idem-2", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"expected 2 distinct F2 entries for 2 retry attempts; got {len(cost_entries)}"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2
