"""U-OD-40 — cost-attribution at validator.evaluate site tests.

ACs per `Implementation_Plan_Operational_Discipline_v2_14.md` U-OD-40:
  #1 Validator cost uses CPU-meter (execution_time_ms × $/CPU_ms) per
     Decision 2.D5 RATIFIED.
  #3 Cost-record attached at span exit
  #4 Audit-ledger entry written

Per CP spec v1.24 §28.10 the helper is invoked from the
ValidatorPostEvaluateHook firing site at ConcreteValidatorFramework.evaluate
(post-construction pre-return; best-effort exception swallow).

AC #2 (webhook cost) + AC #5 (integration: 1 validator + 1 webhook →
2 cost-records) covered separately in the webhook test module + the
factory-binding integration test.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import read_ledger
from harness_od.rate_table_types import RateTable, WebhookRate
from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
from harness_runtime.lifecycle.cost_attribution_validator_dispatch import (
    _compute_validator_cost,
    attribute_validator_dispatch_cost,
)
from harness_runtime.lifecycle.state_ledger import LedgerWriter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


def _make_rate_table(cpu_rate_per_ms: Decimal) -> RateTable:
    """RateTable with operator-supplied cpu_rate_per_ms substrate."""
    return RateTable(
        version="2026-05-28-test",
        providers={},
        tool_rates={},
        webhook_rate=WebhookRate(flat_per_attempt=Decimal("0"), plus_egress=False),
        cpu_rate_per_ms=cpu_rate_per_ms,
        egress_rate_per_byte=Decimal("0"),
    )


@pytest.fixture
def cost_chain() -> RuntimeCostAttributionChain:
    return RuntimeCostAttributionChain()


@pytest.fixture
def audit_writer() -> _RecordingAuditWriter:
    return _RecordingAuditWriter()


# ---------------------------------------------------------------------------
# AC #1 — CPU-meter formula (Decision 2.D5 RATIFIED)
# ---------------------------------------------------------------------------


def test_compute_validator_cost_cpu_meter_integer_ms() -> None:
    """AC #1 — cost = cpu_rate_per_ms × execution_time_ms (integer ms case)."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.001"))
    cost = _compute_validator_cost(rate_table, execution_time_ms=42.0)
    # 42 ms × 0.001 = 0.042
    assert cost == Decimal("0.042")


def test_compute_validator_cost_cpu_meter_fractional_ms() -> None:
    """AC #1 — sub-millisecond precision preserved via str(float) coercion."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.005"))
    cost = _compute_validator_cost(rate_table, execution_time_ms=3.5)
    # 3.5 ms × 0.005 = 0.0175 (preserved as Decimal)
    assert cost == Decimal("0.0175")
    assert isinstance(cost, Decimal)


def test_compute_validator_cost_zero_elapsed() -> None:
    """Edge: zero elapsed time → zero cost (validator returns immediately)."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("1.0"))
    cost = _compute_validator_cost(rate_table, execution_time_ms=0.0)
    assert cost == Decimal("0.0")


def test_compute_validator_cost_zero_rate() -> None:
    """Edge: zero cpu_rate (free-tier) → zero cost regardless of elapsed."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0"))
    cost = _compute_validator_cost(rate_table, execution_time_ms=1000.0)
    assert cost == Decimal("0")


def test_compute_validator_cost_decimal_precision_preserved() -> None:
    """§C-OD-28.4 invariant 2 — Decimal-precision-preserving arithmetic."""
    # 17 sig-digit rate × fractional-ms elapsed — float would lose precision
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.12345678901234567"))
    cost = _compute_validator_cost(rate_table, execution_time_ms=7.5)
    expected = Decimal("0.12345678901234567") * Decimal("7.5")
    assert cost == expected
    assert isinstance(cost, Decimal)


# ---------------------------------------------------------------------------
# AC #3 + AC #4 — full chain returns attached record + 1 audit write
# ---------------------------------------------------------------------------


def test_attribute_validator_dispatch_cost_returns_attached_record(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Helper returns idempotency-key-bearing SpanCostRecord per AC #3."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    attached = attribute_validator_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="abcdef0123456789",
        idempotency_key="validator-idem-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
    )
    assert attached.span_id == "abcdef0123456789"
    assert attached.idempotency_key == "parent-idem-1"  # joins to parent
    assert attached.provider_discriminator is None  # v1.30 — no chain-level family tag
    assert attached.dispatch_kind == "validator"  # v1.30 — the PER_DISPATCH_KIND key
    assert attached.gen_ai_provider_name == "validator:schema-validator"
    assert attached.gen_ai_request_model == ""
    assert attached.total_cost == pytest.approx(0.1, rel=1e-9)  # 10 ms × 0.01
    assert attached.total_latency_ms == 10


def test_attribute_validator_dispatch_cost_writes_audit_entry(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """AC #4 — Cost-record attached + audit-ledger entry written."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.001"))
    attribute_validator_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=5.0,
        span_id="0011223344556677",
        idempotency_key="validator-idem-1",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
    )
    assert len(audit_writer.appended) == 1
    tenant_id, audit_entry = audit_writer.appended[0]
    assert tenant_id is None
    assert hasattr(audit_entry, "payload")
    assert hasattr(audit_entry, "entry_hash")
    attrs = audit_entry.payload.audit_namespace_attrs
    # cost: action_id prefix per CXA v2.9 §0.3 row 8 / OD spec v1.10 §C-OD-26.6.1 step 2
    assert attrs["audit.cp.action_id"] == "cost:test-wf:workflow:test-wf:step:0"
    assert attrs["audit.cp.response"] == "cost_attributed"


def test_attribute_validator_dispatch_cost_writes_with_tenant(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Multi-tenant routing: tenant_id propagates to audit_writer.append."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.001"))
    attribute_validator_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="v1",
        execution_time_ms=1.0,
        span_id="x" * 16,
        idempotency_key="k",
        parent_idempotency_key="p",
        workflow_id="wf",
        parent_action_id="action",
        tenant_id="tenant-A",
    )
    assert audit_writer.appended[0][0] == "tenant-A"


def test_three_validator_dispatches_produce_three_audit_writes(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """3 sequential validator dispatches → 3 cost-records + 3 audit entries."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.001"))
    for i in range(3):
        attribute_validator_dispatch_cost(
            rate_table=rate_table,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            validator_id=f"validator-{i}",
            execution_time_ms=float(i + 1),
            span_id=f"{i:016x}",
            idempotency_key=f"key-{i}",
            parent_idempotency_key=f"parent-{i}",
            workflow_id="wf",
            parent_action_id=f"workflow:wf:step:{i}",
        )
    assert len(audit_writer.appended) == 3
    # Each audit entry has distinct action_id (per-step parent_action_id)
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
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    attribute_validator_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="validator-evaluate-test-wf-step-0",
        idempotency_key="validator-idem-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        dispatch_disambiguator="0-pass-0",
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
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    attribute_validator_dispatch_cost(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="validator-evaluate-test-wf-step-0",
        idempotency_key="validator-idem-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
    )
    _, audit_entry = audit_writer.appended[0]
    assert str(audit_entry.payload.entry_core).startswith("cp-audit:")


def test_revalidate_retry_same_synthesized_span_id_gets_distinct_f2_entries(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard — a REVALIDATE retry loop invokes `evaluate()` on the
    SAME step multiple times, and this composer's `span_id` is a
    *synthesized* `f"validator-evaluate-{workflow_id}-{step_id}"` string
    that repeats IDENTICALLY across those calls (unlike the tool/LLM/webhook
    composers' real per-attempt OTel span). Using that synthesized span_id
    as the F2 disambiguator would collide and silently `IDEMPOTENT_NOOP`-
    drop the second cost event. Two consecutive REVALIDATE outcomes get
    strictly-increasing `burden_count` values, disambiguating naturally."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    same_synthesized_span_id = "validator-evaluate-test-wf-step-0"
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id=same_synthesized_span_id,
        idempotency_key="validator-idem-revalidate",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        ledger_writer=ledger_writer,
    )
    # First evaluate() call: REVALIDATE outcome → burden_count=1 on this call.
    attribute_validator_dispatch_cost(dispatch_disambiguator="1-revalidate-0", **common)
    # Retry evaluate() call on the SAME step: REVALIDATE again → burden_count=2.
    attribute_validator_dispatch_cost(dispatch_disambiguator="2-revalidate-0", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"expected 2 distinct F2 entries for a 2-attempt REVALIDATE retry loop "
        f"sharing the same synthesized span_id; got {len(cost_entries)} "
        "(a span_id-keyed disambiguator would collide here)"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2, (
        "each REVALIDATE attempt's audit entry must reference its OWN F2 anchor"
    )


def test_revalidate_then_pass_shares_burden_count_but_gets_distinct_f2_entries(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard (out-of-family Codex [P1]) — `burden_count` alone is
    NOT a safe disambiguator: per CP spec §25.4 invariant 5, `burden_count`
    increments only on NON-PASS outcomes, so a REVALIDATE call
    (burden_count=1) immediately followed by the terminal PASS call
    (burden_count STILL 1) would collide on a `burden_count`-only key. The
    outcome token in `dispatch_disambiguator` must break that tie."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    same_synthesized_span_id = "validator-evaluate-test-wf-step-0"
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id=same_synthesized_span_id,
        idempotency_key="validator-idem-revalidate-then-pass",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        ledger_writer=ledger_writer,
    )
    # REVALIDATE call: burden_count increments to 1.
    attribute_validator_dispatch_cost(dispatch_disambiguator="1-revalidate-0", **common)
    # Terminal PASS call on the retry: burden_count does NOT increment — still 1.
    attribute_validator_dispatch_cost(dispatch_disambiguator="1-pass-0", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        "REVALIDATE (burden_count=1) then PASS (burden_count still 1) must NOT "
        f"collapse to 1 F2 entry via IDEMPOTENT_NOOP; got {len(cost_entries)}"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2


def test_sibling_fanout_branches_sharing_parent_action_id_get_distinct_f2_entries(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard (out-of-family Codex [P1]) — sibling fan-out
    branches of the SAME declared validator step share one
    `parent_action_id` (per `StepExecutionContext.branch_index`'s own
    docstring: "Branch identity is (parent_action_id, branch_index)"), the
    same collision class `sub_agent_dispatch.py`'s `child_index` guards
    against. `branch_index` in `dispatch_disambiguator` must disambiguate."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="validator-evaluate-test-wf-step-0",
        idempotency_key="validator-idem-fanout",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        ledger_writer=ledger_writer,
    )
    attribute_validator_dispatch_cost(dispatch_disambiguator="0-pass-0", **common)
    attribute_validator_dispatch_cost(dispatch_disambiguator="0-pass-1", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2


def test_two_tenants_sharing_identifiers_get_distinct_f2_entries(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard (out-of-family Codex [P1]) — the underlying
    `LedgerWriter` is SHARED across tenants. Two tenants dispatching a
    validator step that happens to share `(workflow_id, parent_action_id,
    dispatch_disambiguator)` — plausible here since the validator's
    disambiguator is DETERMINISTIC (`burden_count`-derived), not a random
    per-attempt span_id — must NOT collide via `IDEMPOTENT_NOOP`, or the
    second tenant's audit entry would silently reference the first
    tenant's F2 anchor (a cross-tenant leak)."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="validator-evaluate-test-wf-step-0",
        idempotency_key="validator-idem-tenant",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        dispatch_disambiguator="0-pass-0",
        ledger_writer=ledger_writer,
    )
    attribute_validator_dispatch_cost(tenant_id="tenant-A", **common)
    attribute_validator_dispatch_cost(tenant_id="tenant-B", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"two tenants sharing identical (workflow_id, parent_action_id, "
        f"dispatch_disambiguator) must get 2 distinct F2 entries, not "
        f"collapse cross-tenant via IDEMPOTENT_NOOP; got {len(cost_entries)}"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2, "each tenant's audit entry must reference its OWN F2 anchor"


def test_two_runs_of_same_workflow_definition_get_distinct_f2_entries(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard (out-of-family Codex [P1], round 3) —
    `workflow_id` is the operator-authored `WorkflowManifestEntry.workflow_id`,
    a STABLE per-definition identifier reused across every invocation of
    "that workflow" (CP's own `run_idempotency_key = sha256(run_id,
    workflow_id, entry_version)` composition treats `run_id` and
    `workflow_id` as distinct components — `workflow_id` alone is not
    run-unique). Re-running the SAME workflow definition a second time with
    an identical validator outcome sequence (same deterministic
    `dispatch_disambiguator`) MUST NOT collapse via `IDEMPOTENT_NOOP` onto
    the first run's F2 anchor — `parent_idempotency_key` (already
    run-scoped, since CP composes step-level idempotency keys from the
    run's own idempotency key) disambiguates."""
    rate_table = _make_rate_table(cpu_rate_per_ms=Decimal("0.01"))
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        rate_table=rate_table,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        validator_id="schema-validator",
        execution_time_ms=10.0,
        span_id="validator-evaluate-daily-report-step-0",
        idempotency_key="validator-idem-1",
        workflow_id="daily-report",  # SAME operator-authored workflow_id both runs
        parent_action_id="workflow:daily-report:step:0",
        dispatch_disambiguator="0-pass-0",  # SAME deterministic outcome both runs
        ledger_writer=ledger_writer,
    )
    # Run 1 of "daily-report".
    attribute_validator_dispatch_cost(parent_idempotency_key="run-2026-07-13", **common)
    # Run 2 of the SAME workflow definition, a day later — different run_id
    # flows through to a different parent_idempotency_key.
    attribute_validator_dispatch_cost(parent_idempotency_key="run-2026-07-14", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"two separate runs of the same workflow_id, sharing an identical "
        f"deterministic dispatch_disambiguator, must get 2 distinct F2 "
        f"entries, not collapse cross-run via IDEMPOTENT_NOOP; "
        f"got {len(cost_entries)}"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2, "each run's audit entry must reference its OWN F2 anchor"
