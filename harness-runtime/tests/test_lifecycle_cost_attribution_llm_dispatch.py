"""U-OD-38 — cost-attribution at LLM dispatch site tests.

ACs per `Implementation_Plan_Operational_Discipline_v2_14.md` U-OD-38:
  #1 Cost-attribution invoked on every LLM dispatch (success + failure paths)
  #2 Cost-record uses gen_ai.usage.input_tokens + output_tokens per GenAI
     semconv 1.41.0
  #3 Idempotency-key attached pre-audit-write
  #4 PRICE_TABLE_REF resolution failure falls back per Decision (raises per
     §C-OD-28.2 default fail-closed)
  #5 1 LLM call → 1 cost-record + 1 audit-ledger entry
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core import PersonaTier, StepID
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.engine_class import EngineClass
from harness_cp.engine_namespace import REPLAY_DISPOSITION_MAPPING, ReplayDisposition
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import (
    StepExecutionContext,
    StepKind,
    WorkflowStep,
)
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_write import read_ledger
from harness_od.cost_record_otel_serializer import COST_ATTRIBUTED_DECIMAL_ATTR
from harness_od.rate_table_resolver import RateTableMissingError
from harness_od.rate_table_v1 import RATE_TABLE_V1
from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
from harness_runtime.lifecycle.cost_attribution_llm_dispatch import (
    attribute_llm_dispatch_cost,
)
from harness_runtime.lifecycle.llm_dispatch import (
    RuntimeLLMDispatcher,
)
from harness_runtime.lifecycle.state_ledger import LedgerWriter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class _RecordingAuditWriter:
    """Captures every audit-ledger append for AC #5 1-call-1-write assertion."""

    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


@pytest.fixture
def cost_chain() -> RuntimeCostAttributionChain:
    return RuntimeCostAttributionChain()


@pytest.fixture
def audit_writer() -> _RecordingAuditWriter:
    return _RecordingAuditWriter()


# ---------------------------------------------------------------------------
# AC #1 + AC #2 — Cost-attribution invoked; cost-record uses usage attrs
# ---------------------------------------------------------------------------


def test_attribute_llm_dispatch_cost_returns_attached_record_for_anthropic(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    attached = attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="0123456789abcdef",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=1000,
        output_tokens=500,
    )
    assert attached.span_id == "0123456789abcdef"
    assert attached.idempotency_key == "parent-idem-1"  # AC #3
    assert attached.gen_ai_provider_name == "anthropic"
    assert attached.gen_ai_request_model == "claude-haiku-4-5"
    assert attached.provider_discriminator is None  # v1.30 — no chain-level family tag
    assert attached.dispatch_kind == "llm"  # v1.30 — the PER_DISPATCH_KIND key
    # AC #2 — cost uses usage attrs; per claude-haiku-4-5 override $1/MTok in + $5/MTok out:
    # cost = 1000 * (1.00 / 1e6) + 500 * (5.00 / 1e6) = 0.001 + 0.0025 = 0.0035
    assert attached.total_cost == pytest.approx(0.0035, rel=1e-6)


@pytest.mark.parametrize(
    "engine_class",
    list(EngineClass),
)
def test_attribute_llm_dispatch_cost_threads_real_engine_replay_disposition(
    engine_class: EngineClass,
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """B-30 close-out step 4 — `engine_replay_disposition` is no longer
    hard-coded to `NO_REPLAY`; it resolves the workflow's real declared
    `run_engine_class` via the ADR-D1 v1.2 §1.1.1 `REPLAY_DISPOSITION_MAPPING`
    (total over `EngineClass` — every member round-trips to its mapped
    disposition, not just the PURE_PATTERN_NO_ENGINE default case)."""
    attached = attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="0123456789abcdef",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=1000,
        output_tokens=500,
        run_engine_class=engine_class,
    )
    assert attached.engine_replay_disposition == REPLAY_DISPOSITION_MAPPING[engine_class]


def test_attribute_llm_dispatch_cost_defaults_to_no_replay_when_engine_class_unset(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """`run_engine_class` omitted (e.g. a direct unit-test call) preserves the
    pre-existing NO_REPLAY default rather than raising."""
    attached = attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="0123456789abcdef",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=1000,
        output_tokens=500,
    )
    assert attached.engine_replay_disposition == ReplayDisposition.NO_REPLAY


def test_attribute_llm_dispatch_cost_writes_audit_entry(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """AC #5 — 1 LLM call → 1 cost-record + 1 audit-ledger entry."""
    attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="abcdef0123456789",
        parent_idempotency_key="parent-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=100,
        output_tokens=50,
    )
    assert len(audit_writer.appended) == 1
    tenant_id, audit_entry = audit_writer.appended[0]
    assert tenant_id is None
    # Audit entry shape per cp_audit_to_od_audit converter
    assert hasattr(audit_entry, "payload")
    assert hasattr(audit_entry, "entry_hash")
    attrs = audit_entry.payload.audit_namespace_attrs
    # Per OD spec v1.10 §C-OD-26.6.1 step 2 canonical pattern:
    # cost:<workflow_id>:<step_action_id>; response=cost_attributed
    assert attrs["audit.cp.action_id"] == "cost:test-wf:workflow:test-wf:step:0"
    assert attrs["audit.cp.response"] == "cost_attributed"


# ---------------------------------------------------------------------------
# AC #3 — Idempotency key attached pre-audit-write
# ---------------------------------------------------------------------------


def test_idempotency_key_attached_before_audit_write(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Cost-record idempotency_key must be the parent's join key per
    C-IS-05 / C-OD-14 §14.4 BEFORE the audit-ledger write."""
    attached = attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="openai",
        model="gpt-5",
        span_id="ffff000011112222",
        parent_idempotency_key="WORKFLOW-PARENT-KEY-42",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=10,
        output_tokens=5,
    )
    # Parent's idempotency_key is attached on the returned record
    assert attached.idempotency_key == "WORKFLOW-PARENT-KEY-42"
    # AND the audit ledger received exactly 1 entry
    assert len(audit_writer.appended) == 1


# ---------------------------------------------------------------------------
# AC #4 — PRICE_TABLE_REF resolution failure raises (fail-closed default)
# ---------------------------------------------------------------------------


def test_unknown_provider_raises_rate_table_missing(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """Per §C-OD-28.2: resolution failure raises CP-FAIL-RATE-TABLE-MISSING
    by default (fail-closed); operator may flip to fail-open via bootstrap
    config (not at v1 scope)."""
    with pytest.raises(RateTableMissingError) as exc_info:
        attribute_llm_dispatch_cost(
            rate_table=RATE_TABLE_V1,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            provider_name="cohere",  # not in RATE_TABLE_V1
            model="command-r",
            span_id="0000000000000000",
            parent_idempotency_key="parent-x",
            workflow_id="test-wf",
            parent_action_id="workflow:test-wf:step:0",
            input_tokens=1,
            output_tokens=1,
        )
    assert "CP-FAIL-RATE-TABLE-MISSING" in str(exc_info.value)
    # No audit entry written on failure
    assert audit_writer.appended == []


# ---------------------------------------------------------------------------
# Provider coverage — all 3 ADR-F1 providers
# ---------------------------------------------------------------------------


def test_cost_attribution_works_for_all_3_adr_f1_providers(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    for provider in ("anthropic", "openai", "ollama"):
        attribute_llm_dispatch_cost(
            rate_table=RATE_TABLE_V1,
            cost_chain=cost_chain,
            audit_writer=audit_writer,
            provider_name=provider,
            model=f"test-{provider}-model",
            span_id=f"{'a' * 16}",
            parent_idempotency_key=f"parent-{provider}",
            workflow_id="test-wf",
            parent_action_id="workflow:test-wf:step:0",
            input_tokens=100,
            output_tokens=50,
        )
    assert len(audit_writer.appended) == 3


# ---------------------------------------------------------------------------
# AC #1 — End-to-end via RuntimeLLMDispatcher with cost-attribution wiring
# ---------------------------------------------------------------------------


_DEFAULT_BINDING = ModelBinding(provider="anthropic", model="claude-haiku-4-5")
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-cost-attr")


class _FakeAnthropicAdapter:
    """Mock anthropic adapter returning a fixed usage shape."""

    def __init__(self) -> None:
        self.client = MagicMock()
        usage = MagicMock(
            input_tokens=1000,
            output_tokens=500,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0,
        )
        response = MagicMock(usage=usage, id="msg_test_001")
        response.model_dump = lambda: {"id": "msg_test_001", "content": []}

        async def _create(model: str, **kwargs: Any) -> Any:
            return response

        self.client.messages.create = _create


def test_end_to_end_dispatch_emits_cost_attribution_audit_entry(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """AC #1 + AC #5 end-to-end: RuntimeLLMDispatcher.dispatch on a mocked
    anthropic provider produces exactly 1 audit-ledger entry."""
    import asyncio

    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))

    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _FakeAnthropicAdapter()},
        tracer_provider=tp,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=RATE_TABLE_V1,
    )
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=_DEFAULT_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 1},
        },
    )
    step_context = StepExecutionContext(
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key="parent-e2e-key",
        tenant_id=None,
        step_index=0,
    )
    asyncio.run(dispatcher.dispatch(binding, step, step_context=step_context))

    # AC #5 — exactly 1 audit-ledger entry written
    assert len(audit_writer.appended) == 1

    # cost.attributed_decimal OTel attribute emitted on the dispatch span
    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    cost_attr = (spans[0].attributes or {}).get(COST_ATTRIBUTED_DECIMAL_ATTR)
    assert cost_attr is not None
    assert isinstance(cost_attr, str)
    # Round-trip the Decimal-form string
    recovered = Decimal(cost_attr)
    # haiku rates: 1000 * 1.00/1e6 + 500 * 5.00/1e6 = 0.0035
    assert recovered == pytest.approx(Decimal("0.0035"), rel=Decimal("1e-6"))


def test_end_to_end_dispatch_threads_real_run_engine_class_into_disposition(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
) -> None:
    """B-30 close-out step 4 witness (merge-gate test-witness lens finding) —
    proves the PRODUCTION call site (`RuntimeLLMDispatcher.dispatch`) actually
    threads `step_context.run_engine_class` through to the composed
    `SpanCostRecord`, not just that `attribute_llm_dispatch_cost` resolves the
    mapping correctly when called directly with a manual kwarg. A revert of
    the `run_engine_class=step_context.run_engine_class` threading at
    `llm_dispatch.py`'s dispatch-site call into `_attribute_cost_off_loop_best_effort`
    would leave `engine_replay_disposition` at the pre-fix `NO_REPLAY` default
    here and fail this assertion."""
    import asyncio

    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
    cost_records: list[object] = []

    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _FakeAnthropicAdapter()},
        tracer_provider=tp,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=RATE_TABLE_V1,
        cost_record_sink=cost_records,
    )
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=_DEFAULT_BINDING,
        engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 1},
        },
    )
    step_context = StepExecutionContext(
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key="parent-e2e-key",
        tenant_id=None,
        step_index=0,
        run_engine_class=EngineClass.SAVE_POINT_CHECKPOINT,
    )
    asyncio.run(dispatcher.dispatch(binding, step, step_context=step_context))

    assert len(cost_records) == 1
    assert cost_records[0].engine_replay_disposition == ReplayDisposition.CHECKPOINT_RESUME


def test_dispatcher_without_cost_substrate_silently_skips_cost_attribution() -> None:
    """Backward-compat: dispatcher constructed without cost_chain/audit_writer/
    rate_table proceeds without cost-attribution (unit-test ergonomics).

    B-28 finding #13 (test-quality preflight 2026-07-12) — the prior body
    asserted nothing about the claimed "silently skips" behavior beyond "no
    exception raised"; assert the actual skip — no `cost.attributed_decimal`
    attribute lands on the dispatch span (the early-return guard at
    `llm_dispatch.py` fires when `cost_chain`/`audit_writer`/`rate_table` are
    absent, before any cost-attribution attempt)."""
    import asyncio

    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))

    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _FakeAnthropicAdapter()},
        tracer_provider=tp,
        # cost-attribution substrate omitted
    )
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=_DEFAULT_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 1},
        },
    )
    step_context = StepExecutionContext(
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key="parent-x",
        tenant_id=None,
        step_index=0,
    )
    asyncio.run(dispatcher.dispatch(binding, step, step_context=step_context))

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert COST_ATTRIBUTED_DECIMAL_ATTR not in (spans[0].attributes or {})


# ---------------------------------------------------------------------------
# B-23 — F2-write entry_core (real IS anchor, not fabricated cp-audit: marker)
# ---------------------------------------------------------------------------


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
    ledger_writer = _build_ledger_writer(tmp_path)
    attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="f2-span-1",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=1000,
        output_tokens=500,
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
    attribute_llm_dispatch_cost(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        span_id="f2-span-2",
        parent_idempotency_key="parent-idem-1",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=1000,
        output_tokens=500,
    )
    _, audit_entry = audit_writer.appended[0]
    assert str(audit_entry.payload.entry_core).startswith("cp-audit:")


def test_repeat_dispatch_same_step_gets_distinct_f2_entries_not_noop_dropped(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """Regression guard — two LLM-dispatch attempts (e.g. a retry) sharing
    the same (workflow_id, parent_action_id) MUST persist two DISTINCT F2
    entries, not silently collapse via `IDEMPOTENT_NOOP`."""
    ledger_writer = _build_ledger_writer(tmp_path)
    common = dict(
        rate_table=RATE_TABLE_V1,
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        provider_name="anthropic",
        model="claude-haiku-4-5",
        parent_idempotency_key="parent-retry",
        workflow_id="test-wf",
        parent_action_id="workflow:test-wf:step:0",
        input_tokens=100,
        output_tokens=50,
        ledger_writer=ledger_writer,
    )
    attribute_llm_dispatch_cost(span_id="attempt-1", **common)
    attribute_llm_dispatch_cost(span_id="attempt-2", **common)

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 2, (
        f"expected 2 distinct F2 entries for 2 retry attempts; got {len(cost_entries)}"
    )
    entry_cores = {str(e.payload.entry_core) for _, e in audit_writer.appended}
    assert len(entry_cores) == 2


def test_end_to_end_dispatch_with_ledger_writer_produces_real_entry_core(
    cost_chain: RuntimeCostAttributionChain,
    audit_writer: _RecordingAuditWriter,
    tmp_path: Path,
) -> None:
    """End-to-end through `RuntimeLLMDispatcher.dispatch` (real active
    workflow step) — the wired `ledger_writer` produces a real F2 entry_core,
    not a fabricated marker."""
    import asyncio

    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": _FakeAnthropicAdapter()},
        tracer_provider=TracerProvider(),
        cost_chain=cost_chain,
        audit_writer=audit_writer,
        rate_table=RATE_TABLE_V1,
        ledger_writer=ledger_writer,
    )
    binding = StepEffectiveBinding(
        step_id="step-0",
        model_binding=_DEFAULT_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        override_applied=False,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )
    step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.INFERENCE_STEP,
        step_payload={
            "messages": [{"role": "user", "content": "hi"}],
            "tools": None,
            "params": {"max_tokens": 1},
        },
    )
    step_context = StepExecutionContext(
        workflow_id="wf",
        parent_action_id="workflow:wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key="parent-e2e-key",
        tenant_id=None,
        step_index=0,
    )
    asyncio.run(dispatcher.dispatch(binding, step, step_context=step_context))

    entries = read_ledger(ledger_writer.handle)
    cost_entries = [e for e in entries if str(e.action_id).startswith("cost:")]
    assert len(cost_entries) == 1
    _, audit_entry = audit_writer.appended[0]
    assert str(audit_entry.payload.entry_core) == str(cost_entries[0].action_id)


_ = Mapping
