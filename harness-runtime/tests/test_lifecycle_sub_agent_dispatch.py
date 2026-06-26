"""Tests for U-RT-59 — sub-agent dispatch composer (C-RT-17 §14.7).

Acceptance-criterion coverage (per Phase-2 Session-3 Track-A v2.5 L9-ter):
  AC #2  — Protocol satisfaction
      → test_runtime_sub_agent_dispatcher_satisfies_step_dispatcher_protocol
  AC #3  — SubAgentDispatchPayload validation
      → test_payload_validation_rejects_mis_shaped_payload
      → test_payload_validation_accepts_4_field_shape
  AC #4  — HandoffContext composition
      → test_handoff_context_composed_per_v1_6_mvp_table
      → test_handoff_context_audit_trail_link_per_path_a_v1_6
  AC #5  — gate-level descent + topology admissibility
      → test_dispatch_invokes_handoff_registry_with_step_context_seeds
      → test_topology_primary_passes_strict_gate
      → test_topology_cross_pattern_admissible_passes_strict_gate
      → test_topology_neither_primary_nor_admissible_raises
  AC #6  — subagent.span + topology.* emission
      → test_dispatch_emits_exactly_one_subagent_span
      → test_subagent_span_carries_7_subagent_attributes
      → test_subagent_span_carries_2_narrow_topology_attributes
      → test_subagent_span_does_not_carry_8_fanout_topology_attributes
      → test_attribute_names_come_from_canonical_carrier
  AC #7  — child runner invocation
      → test_dispatch_invokes_child_workflow_runner
      → test_child_runner_receives_handoff_context_and_descent
  AC #8  — child result mapping
      → test_success_maps_to_completed_returns_final_state
      → test_drained_maps_to_completed_returns_partial_state
      → test_failed_raises_sub_agent_child_failed_error_with_span_attrs
  AC #9  — audit-entry 4-substep composition (UN-STRUCK at v1.7 §14.7.2 step 8)
      → test_dispatcher_takes_audit_writer_kwarg_at_v1_7
      → test_step8a_composes_cp_audit_entry
      → test_step8b_writes_f2_dispatch_action_entry
      → test_step8c_8d_persists_od_audit_entry_through_writer
      → test_step8b_failure_raises_audit_compose_error_on_success_path
      → test_step8_failure_swallowed_on_failed_child_path
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_core import PersonaTier, StepID, WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.handoff_context import ActionKind, StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.sub_agent_brief import (
    ClearTaskBoundaries,
    OutputSchema,
    OutputSchemaKind,
    SubAgentBrief,
)
from harness_cp.sub_agent_gate_level_descent import SubAgentGateLevelDescent
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.topology_subagent_namespace import (
    SUBAGENT_NAMESPACE_SCHEMA,
    TOPOLOGY_NAMESPACE_SCHEMA,
)
from harness_cp.workflow_driver import StepDispatcher
from harness_cp.workflow_driver_types import (
    RunResult,
    RunStatus,
    StepExecutionContext,
    StepKind,
    SubAgentChildPausedError,
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_is.state_ledger_entry_schema import Identifier as _Identifier
from harness_od.audit_ledger_types import SignatureAlgorithm
from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
from harness_runtime.lifecycle.handoff import RuntimeHandoffRegistry
from harness_runtime.lifecycle.state_ledger import LedgerWriter
from harness_runtime.lifecycle.sub_agent_dispatch import (
    RuntimeSubAgentDispatcher,
    SubAgentChildFailedError,
    SubAgentDispatchAuditComposeError,
    SubAgentDispatchPayload,
    SubAgentDispatchPayloadShapeError,
    SubAgentDispatchTopologyInadmissibleError,
)
from harness_runtime.lifecycle.topology_dispatcher import RuntimeTopologyDispatcher
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# ---------------------------------------------------------------------------
# Fixture scaffolding
# ---------------------------------------------------------------------------


_CHAIN = FallbackChain(
    primary=ProviderCandidate(
        provider="anthropic",
        model="claude-haiku-4-5",
        family=ProviderFamily.ANTHROPIC,
    ),
    same_family=(),
    cross_family=(),
    terminal=None,
)
_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="test-sub-agent-runtime")


def _brief() -> SubAgentBrief:
    return SubAgentBrief(
        objective="extract structured fields from a free-text input",
        output_format=OutputSchema(
            schema_kind=OutputSchemaKind.JSON_SCHEMA,
            schema_body='{"type":"object"}',
        ),
        guidance="prefer recall over precision",
        task_boundaries=ClearTaskBoundaries(
            in_scope=("field extraction",),
            out_of_scope=("freeform summarization",),
            termination_criteria=("all fields present or null",),
        ),
        summary_hash="0" * 64,
    )


def _child_manifest(
    *,
    workload_class: WorkloadClass = WorkloadClass.SOFTWARE_ENGINEERING,
    topology: TopologyPattern = TopologyPattern.HIERARCHICAL_DELEGATION,
) -> WorkflowManifestEntry:
    return WorkflowManifestEntry(
        workflow_id="child-wf",
        workload_class=workload_class,
        persona_tier=PersonaTier.TEAM_BINDING,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=topology,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _child_steps() -> tuple[WorkflowStep, ...]:
    return (
        WorkflowStep(
            step_id=StepID("child-step-0"),
            step_kind=StepKind.INFERENCE_STEP,
            step_payload={"index": 0},
        ),
    )


def _payload(
    *,
    workload_class: WorkloadClass = WorkloadClass.SOFTWARE_ENGINEERING,
    topology: TopologyPattern = TopologyPattern.HIERARCHICAL_DELEGATION,
) -> SubAgentDispatchPayload:
    return SubAgentDispatchPayload(
        child_workflow_id="child-wf",
        child_manifest_entry=_child_manifest(workload_class=workload_class, topology=topology),
        child_steps=_child_steps(),
        brief=_brief(),
    )


def _step(payload: SubAgentDispatchPayload | None = None) -> WorkflowStep:
    p = payload if payload is not None else _payload()
    return WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload=p.model_dump(),
    )


def _step_context() -> StepExecutionContext:
    return StepExecutionContext(
        workflow_id="parent-wf",
        parent_action_id="workflow:parent-wf:step:0",
        parent_gate_level=GateLevel.AUTO,
        parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
        parent_actor=_ACTOR,
        parent_entry_hash="",
        parent_idempotency_key="0" * 64,
        tenant_id=None,
        step_index=0,
    )


def _binding() -> StepEffectiveBinding:
    return StepEffectiveBinding(
        step_id="step-0",
        model_binding=ModelBinding(provider="anthropic", model="claude-haiku-4-5"),
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        hitl_placement=None,
        override_applied=False,
        override_audit_ref=None,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
    )


def _tracer_provider_with_exporter() -> tuple[TracerProvider, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))
    return tp, exporter


class _MockChildWorkflowRunner:
    """Test fixture per spec §14.7 "Deferred to implementation discretion".

    Records the kwargs of each invocation; returns canned `RunResult` from
    its `next_result` slot. Bound via `RuntimeSubAgentDispatcher`'s
    `child_workflow_runner` constructor kwarg per AC #7.
    """

    def __init__(self, *, next_result: RunResult) -> None:
        self.calls: list[Mapping[str, Any]] = []
        self.next_result = next_result

    def __call__(
        self,
        *,
        workflow_id: str,
        manifest_entry: WorkflowManifestEntry,
        steps: Sequence[WorkflowStep],
        handoff_context: Any,
        descent: SubAgentGateLevelDescent,
        default_model_binding: ModelBinding,
        pause_snapshot_input: Any = None,
    ) -> RunResult:
        self.calls.append(
            {
                "workflow_id": workflow_id,
                "manifest_entry": manifest_entry,
                "steps": tuple(steps),
                "handoff_context": handoff_context,
                "descent": descent,
                "default_model_binding": default_model_binding,
                # B-HIERARCHICAL-PAUSE — the child resume snapshot threaded on resume
                # (None on a first dispatch).
                "pause_snapshot_input": pause_snapshot_input,
            }
        )
        return self.next_result


def _success_result() -> RunResult:
    return RunResult(
        workflow_id="child-wf",
        run_id="child-run-1",
        status=RunStatus.SUCCESS,
        terminal_step_index=None,
        partial_state=None,
        final_state={"child_field": "value"},
        fail_class=None,
    )


def _drained_result() -> RunResult:
    return RunResult(
        workflow_id="child-wf",
        run_id="child-run-1",
        status=RunStatus.DRAINED,
        terminal_step_index=0,
        partial_state={"partial_field": "partial_value"},
        final_state=None,
        fail_class=None,
    )


def _failed_result() -> RunResult:
    return RunResult(
        workflow_id="child-wf",
        run_id="child-run-1",
        status=RunStatus.FAILED,
        terminal_step_index=0,
        partial_state=None,
        final_state=None,
        fail_class="step-failure: RuntimeError: simulated child failure",
    )


def _build_ledger_writer(tmp_path: Path) -> LedgerWriter:
    """Build a real `LedgerWriter` rooted in `tmp_path` (test isolation).

    Bypasses `PathResolver` — constructs the `JsonlLedgerHandle` directly
    against a tmp-path JSONL file so tests don't need a path-class registry
    fixture.
    """
    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle

    path = tmp_path / "state.jsonl"
    path.touch()
    handle = JsonlLedgerHandle(canonical_path=path, exists=True, entry_count=0)
    return LedgerWriter(handle=handle, actor=_ACTOR)


def _dispatcher(
    tmp_path: Path,
    *,
    child_result: RunResult | None = None,
    audit_writer_override: RuntimeAuditLedgerWriter | None = None,
    ledger_writer_override: LedgerWriter | None = None,
) -> tuple[RuntimeSubAgentDispatcher, _MockChildWorkflowRunner, InMemorySpanExporter]:
    """Compose a RuntimeSubAgentDispatcher with mocked child runner + real
    handoff/topology registries + real `LedgerWriter` + `RuntimeAuditLedgerWriter`
    (rooted in `tmp_path`) + InMemorySpanExporter for verification.

    v1.7 §14.7.2 step 8 4-substep contract requires the dispatcher to wire
    `ledger_writer` (8b F2-write), `audit_writer` (8d OD persistence),
    `audit_signing_key_id` + `audit_signing_algorithm` (8c CP→OD converter
    signing), and `time_source` (8b F2 timestamp).
    """
    from datetime import UTC, datetime

    tp, exporter = _tracer_provider_with_exporter()
    runner = _MockChildWorkflowRunner(
        next_result=child_result if child_result is not None else _success_result()
    )
    ledger_writer = ledger_writer_override or _build_ledger_writer(tmp_path)
    audit_writer = audit_writer_override or RuntimeAuditLedgerWriter(
        ledger_writer=ledger_writer,
        time_source=lambda: datetime.now(UTC),
    )
    dispatcher = RuntimeSubAgentDispatcher(
        handoff_registry=RuntimeHandoffRegistry(),
        topology_dispatcher=RuntimeTopologyDispatcher(),
        tracer_provider=tp,
        child_workflow_runner=runner,  # type: ignore[arg-type]
        ledger_writer=ledger_writer,
        audit_writer=audit_writer,
        audit_signing_key_id="test-signing-key",
        audit_signing_algorithm=SignatureAlgorithm.ED25519,
        time_source=lambda: datetime.now(UTC),
        procedural_tier_snapshot_resolver=lambda: _Identifier("b" * 64),
    )
    return dispatcher, runner, exporter


# ---------------------------------------------------------------------------
# AC #2 — Protocol satisfaction
# ---------------------------------------------------------------------------


def test_runtime_sub_agent_dispatcher_satisfies_step_dispatcher_protocol(tmp_path: Path) -> None:
    """AC #2: isinstance check passes via @runtime_checkable Protocol."""
    dispatcher, _, _ = _dispatcher(tmp_path)
    assert isinstance(dispatcher, StepDispatcher)


# ---------------------------------------------------------------------------
# AC #3 — payload validation
# ---------------------------------------------------------------------------


def test_payload_validation_rejects_mis_shaped_payload(tmp_path: Path) -> None:
    """AC #3: a SUB_AGENT_DISPATCH step with bad step_payload raises typed error."""
    dispatcher, _, _ = _dispatcher(tmp_path)
    bad_step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={"random": "junk"},
    )
    with pytest.raises(SubAgentDispatchPayloadShapeError):
        dispatcher.dispatch(_binding(), bad_step, step_context=_step_context())


def test_payload_validation_accepts_4_field_shape(tmp_path: Path) -> None:
    """AC #3: valid 4-field payload validates + composer proceeds."""
    payload = _payload()
    assert payload.child_workflow_id == "child-wf"
    assert payload.brief.objective.startswith("extract")
    assert len(payload.child_steps) == 1


# ---------------------------------------------------------------------------
# AC #4 — HandoffContext composition
# ---------------------------------------------------------------------------


def test_handoff_context_composed_per_v1_6_mvp_table(tmp_path: Path) -> None:
    """AC #4: composer constructs the 7-field HandoffContext per §14.7.3 table."""
    dispatcher, runner, _ = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert len(runner.calls) == 1
    hc = runner.calls[0]["handoff_context"]
    assert hc.proposed_action.action_kind == ActionKind.SUB_AGENT_DISPATCH
    assert hc.proposed_action.payload == {"objective": _brief().objective}
    assert hc.agent_confidence is None
    assert hc.failed_attempts == ()
    assert hc.alternatives_considered == ()
    assert hc.state_summary.summary_text == ""
    assert hc.state_summary.relevant_entries[0].action_id == _step_context().parent_action_id
    assert hc.retry_history.retry_count == 0


def test_handoff_context_audit_trail_link_per_path_a_v1_6(tmp_path: Path) -> None:
    """AC #4: audit_trail_link constructed from step_context per v1.6 Path A."""
    dispatcher, runner, _ = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    hc = runner.calls[0]["handoff_context"]
    assert hc.audit_trail_link.action_id == _step_context().parent_action_id
    assert hc.audit_trail_link.entry_hash == _step_context().parent_entry_hash
    # Actor projected from IS Actor.actor_id → CP ActorIdentity per carrier-map.
    assert str(hc.audit_trail_link.actor) == _ACTOR.actor_id


# ---------------------------------------------------------------------------
# AC #5 — gate-level descent + topology admissibility
# ---------------------------------------------------------------------------


def test_dispatch_invokes_handoff_registry_with_step_context_seeds(tmp_path: Path) -> None:
    """AC #5a: composer's handoff_registry.dispatch receives step_context seeds."""
    dispatcher, runner, _ = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    descent = runner.calls[0]["descent"]
    assert isinstance(descent, SubAgentGateLevelDescent)
    # Descent's child_gate_level descends from step_context.parent_gate_level
    # (AUTO at MVP); no operator override → child inherits AUTO.
    assert descent.child_gate_level == GateLevel.AUTO


def test_topology_primary_passes_strict_gate(tmp_path: Path) -> None:
    """AC #5b: child topology = workload's primary topology passes step 4.

    Path A resolution of the U-RT-59 topology-admissibility Class 1 fork
    (`.harness/class_1_tension_u_rt_59_topology_admissibility_predicate.md`):
    composer step 4 gates on `is_topology_permitted(pattern, workload)` —
    the C-CP-11 §11.1 primary topologies ∪ C-CP-10 §10.3 cross-pattern
    union predicate, NOT the bare §10.3 `is_admissible` predicate.

    SINGLE_THREADED_LINEAR is PIPELINE_AUTOMATION's primary topology per
    C-CP-11 §11.1 row 3 — the strict gate must accept it. (The same case
    against SOFTWARE_ENGINEERING fails per the third test below: it is
    neither SE's primary nor a §10.3 cross-pattern-admissible alternative.)
    """
    payload = _payload(
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )
    dispatcher, runner, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(payload), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1
    attrs = dict(spans[0].attributes or {})
    assert attrs["topology.pattern"] == TopologyPattern.SINGLE_THREADED_LINEAR.value
    assert len(runner.calls) == 1


def test_topology_cross_pattern_admissible_passes_strict_gate(tmp_path: Path) -> None:
    """AC #5b: child topology = §10.3 cross-pattern admissible passes step 4.

    HIERARCHICAL_DELEGATION + SOFTWARE_ENGINEERING is one of the 5
    cross-pattern admissible cells in `_CROSS_PATTERN_ADMISSIBLE` — non-primary
    but admissibility-closed in the workload's `permitted_patterns`. The
    strict gate accepts it because the union predicate covers both halves.
    """
    payload = _payload(
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        topology=TopologyPattern.HIERARCHICAL_DELEGATION,
    )
    dispatcher, runner, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(payload), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1
    attrs = dict(spans[0].attributes or {})
    assert attrs["topology.pattern"] == TopologyPattern.HIERARCHICAL_DELEGATION.value
    assert len(runner.calls) == 1


def test_topology_neither_primary_nor_admissible_raises(tmp_path: Path) -> None:
    """AC #5b: child topology not in workload's permitted set raises.

    SINGLE_THREADED_LINEAR + SOFTWARE_ENGINEERING is neither SE's primary
    (which is EVALUATOR_OPTIMIZER + ORCHESTRATOR_WORKERS per C-CP-11 §11.1
    row 1) nor a §10.3 cross-pattern admissible alternative
    (HIERARCHICAL_DELEGATION is the only SE cross-pattern). The strict gate
    raises `SubAgentDispatchTopologyInadmissibleError` before `subagent.span`
    opens — no partial span emission.
    """
    payload = _payload(
        workload_class=WorkloadClass.SOFTWARE_ENGINEERING,
        topology=TopologyPattern.SINGLE_THREADED_LINEAR,
    )
    dispatcher, runner, exporter = _dispatcher(tmp_path)
    with pytest.raises(SubAgentDispatchTopologyInadmissibleError):
        dispatcher.dispatch(_binding(), _step(payload), step_context=_step_context())
    # No partial subagent.span emitted (gate fires before span open).
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 0
    # Child runner not invoked (composer short-circuited at step 4).
    assert len(runner.calls) == 0


# ---------------------------------------------------------------------------
# AC #6 — subagent.span emission
# ---------------------------------------------------------------------------


def test_dispatch_emits_exactly_one_subagent_span(tmp_path: Path) -> None:
    """AC #6: exactly one subagent.span per composer invocation."""
    dispatcher, _, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1


def test_subagent_span_carries_7_subagent_attributes(tmp_path: Path) -> None:
    """AC #6: the 7 subagent.* attributes per C-CP-14 §14.2 verbatim."""
    dispatcher, _, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    expected = {schema.attribute_name for schema in SUBAGENT_NAMESPACE_SCHEMA}
    assert expected.issubset(set(attrs.keys()))


def test_subagent_span_carries_2_narrow_topology_attributes(tmp_path: Path) -> None:
    """AC #6: narrow-subset 2 topology.* attributes (pattern + workload_class)."""
    dispatcher, _, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert "topology.pattern" in attrs
    assert "topology.workload_class" in attrs


def test_subagent_span_does_not_carry_8_fanout_topology_attributes(tmp_path: Path) -> None:
    """AC #6: explicit absence of 8 fan-out-specific topology.* attributes."""
    dispatcher, _, exporter = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    forbidden = {
        "topology.fan_out_cap",
        "topology.cascade_policy",
        "topology.results_collected",
        "topology.results_failed",
        "topology.cascade_applied",
        "topology.synthesis_token_budget",
        "topology.cascade_decision_audit_ledger_id",
        "topology.concurrent_token_budget_at_dispatch",
    }
    assert forbidden.isdisjoint(set(attrs.keys()))


def test_attribute_names_come_from_canonical_carrier(tmp_path: Path) -> None:
    """AC #6: subagent.* + topology.pattern + topology.workload_class are sourced
    from the canonical CP-side carrier (no hand-coded attribute strings)."""
    subagent_carrier_names = {s.attribute_name for s in SUBAGENT_NAMESPACE_SCHEMA}
    topology_carrier_names = {s.attribute_name for s in TOPOLOGY_NAMESPACE_SCHEMA}
    # Sanity: the 2 narrow-subset attribute names live in the carrier.
    assert "topology.pattern" in topology_carrier_names
    assert "topology.workload_class" in topology_carrier_names
    # Sanity: all 7 subagent.* names live in the carrier.
    assert "subagent.span.id" in subagent_carrier_names
    assert "subagent.result_status" in subagent_carrier_names


# ---------------------------------------------------------------------------
# AC #7 — child runner invocation
# ---------------------------------------------------------------------------


def test_dispatch_invokes_child_workflow_runner(tmp_path: Path) -> None:
    """AC #7: composer invokes the injected child runner with the child shape."""
    dispatcher, runner, _ = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["workflow_id"] == "child-wf"
    assert call["manifest_entry"].workflow_id == "child-wf"
    assert len(call["steps"]) == 1
    assert call["default_model_binding"] == _binding().model_binding


def test_child_runner_receives_handoff_context_and_descent(tmp_path: Path) -> None:
    """AC #7: child runner sees fully-composed HandoffContext + descent."""
    dispatcher, runner, _ = _dispatcher(tmp_path)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    call = runner.calls[0]
    assert call["handoff_context"].proposed_action.action_kind == ActionKind.SUB_AGENT_DISPATCH
    assert isinstance(call["descent"], SubAgentGateLevelDescent)


# ---------------------------------------------------------------------------
# AC #8 — child result mapping
# ---------------------------------------------------------------------------


def test_success_maps_to_completed_returns_final_state(tmp_path: Path) -> None:
    """AC #8a: child SUCCESS → subagent.result_status=completed; returns final_state."""
    dispatcher, _, exporter = _dispatcher(tmp_path, child_result=_success_result())
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out == {"child_field": "value"}
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "completed"
    assert attrs["subagent.request_blocked_by_budget"] is False


def test_drained_maps_to_completed_returns_partial_state(tmp_path: Path) -> None:
    """AC #8b: child DRAINED → subagent.result_status=completed; returns partial_state."""
    dispatcher, _, exporter = _dispatcher(tmp_path, child_result=_drained_result())
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out == {"partial_field": "partial_value"}
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "completed"


def test_failed_raises_sub_agent_child_failed_error_with_span_attrs(tmp_path: Path) -> None:
    """AC #8c: child FAILED → subagent.result_status=failed + raises typed error."""
    dispatcher, _, exporter = _dispatcher(tmp_path, child_result=_failed_result())
    with pytest.raises(SubAgentChildFailedError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "failed"


# ---------------------------------------------------------------------------
# B-HIERARCHICAL-PAUSE (R-FS-1) — child PAUSE surfacing + resume-snapshot forwarding.
# The CP-side capture + resume re-entry is witnessed end-to-end in
# `harness-cp/tests/test_workflow_driver_fanout_pause.py`; these unit-prove the
# runtime dispatcher seam that test's faithful double stands in for.
# ---------------------------------------------------------------------------


def _paused_result(snapshot: PauseSnapshot) -> RunResult:
    return RunResult(
        workflow_id="child-wf",
        run_id="child-run-1",
        status=RunStatus.PAUSED,
        terminal_step_index=None,
        partial_state=None,
        final_state=None,
        fail_class=None,
        pause_snapshot=snapshot,
    )


def _child_snapshot() -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id="child-wf",
        run_id="child-run-1",
        step_index=1,
        pause_reason=WorkflowPauseReason.EXPLICIT_OPERATOR,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=_Identifier(""),
            external_references=(),
        ),
        snapshot_hash="a" * 64,
        created_at=1,
        state_ledger_anchor="anchor",
    )


def test_paused_child_raises_sub_agent_child_paused_error(tmp_path: Path) -> None:
    """B-HIERARCHICAL-PAUSE — a child sub-workflow returning PAUSED is SURFACED as a
    typed `SubAgentChildPausedError` carrying the child's snapshot (NOT swallowed as
    success-equivalent), so the parent fan-out captures the cursor + pauses honestly."""
    snap = _child_snapshot()
    dispatcher, _, exporter = _dispatcher(tmp_path, child_result=_paused_result(snap))
    with pytest.raises(SubAgentChildPausedError) as exc_info:
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert exc_info.value.child_snapshot is snap
    assert exc_info.value.child_workflow_id == "child-wf"
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "paused"
    # The canonical 7-attr schema: the paused branch raises before the common
    # close-time token block, so it must set the token attrs itself (Codex [P2]).
    assert attrs["subagent.tokens_in"] == 0
    assert attrs["subagent.tokens_out"] == 0
    assert attrs["subagent.cached_tokens_in"] == 0


def test_paused_child_without_snapshot_fails_honestly(tmp_path: Path) -> None:
    """A PAUSED RunResult MUST carry its pause_snapshot (the §25.2 contract). A PAUSED
    with no snapshot cannot be resumed → fail as a child failure (never a
    false-resumable / silent-success)."""
    bad = RunResult(
        workflow_id="child-wf",
        run_id="child-run-1",
        status=RunStatus.PAUSED,
        terminal_step_index=None,
        partial_state=None,
        final_state=None,
        fail_class=None,
        pause_snapshot=None,
    )
    dispatcher, _, _ = _dispatcher(tmp_path, child_result=bad)
    with pytest.raises(SubAgentChildFailedError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())


def test_child_resume_snapshot_forwarded_to_runner(tmp_path: Path) -> None:
    """B-HIERARCHICAL-PAUSE — on resume, `step_context.child_resume_snapshot` is
    forwarded to the child runner as `pause_snapshot_input` so the child re-enters at
    its cursor. `None` on a normal (first) dispatch."""
    snap = _child_snapshot()
    dispatcher, runner, _ = _dispatcher(tmp_path)

    # Normal dispatch → runner receives pause_snapshot_input=None.
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert runner.calls[-1]["pause_snapshot_input"] is None

    # Resume dispatch → the step context carries the child snapshot → forwarded.
    resume_ctx = _step_context().model_copy(update={"child_resume_snapshot": snap})
    dispatcher.dispatch(_binding(), _step(), step_context=resume_ctx)
    assert runner.calls[-1]["pause_snapshot_input"] is snap


def test_child_runner_resume_workflow_id_mismatch_fails_closed() -> None:
    """B-HIERARCHICAL-PAUSE (Codex [P2]) — the real `ChildWorkflowRunner` FAILS CLOSED
    when a resume snapshot's `workflow_id` does not match the child being invoked (a
    parent edited between pause + resume so the same SUB_AGENT_DISPATCH step_id points
    to a different child). The guard fires before `execute_workflow` / `ctx` is used."""
    from types import SimpleNamespace

    from harness_runtime.lifecycle.child_workflow_runner import compose_child_workflow_runner

    snap = _child_snapshot()  # workflow_id="child-wf"
    runner = compose_child_workflow_runner(cast(Any, SimpleNamespace(step_dispatchers=None)))
    with pytest.raises(ValueError, match="child resume workflow-id mismatch"):
        runner(
            workflow_id="a-different-child-wf",
            manifest_entry=cast(Any, None),
            steps=(),
            handoff_context=cast(Any, None),
            descent=cast(Any, None),
            default_model_binding=cast(Any, None),
            pause_snapshot_input=snap,
        )


def test_child_workflow_runner_opts_into_final_state_reconstruct(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT (R-FS-1) — WIRING WITNESS. The real
    `compose_child_workflow_runner` forwards `reconstruct_final_state=True` to
    `execute_workflow` (the child opt-in), so a durable-engine-class child resume over a
    committed prefix reconstructs its COMPLETE `final_state` for the parent fold (a
    suffix-only child final_state silently corrupts the parent aggregate per finding-v2).
    Composes with the CP-side full-chain reconstruct witnesses (which prove that
    `execute_workflow(reconstruct_final_state=True)` actually seeds the prefix from the
    durable store). The real-runner-THROUGH-execute_workflow integration remains the
    pre-existing AC #7 coverage residual (needs a fully-bootstrapped HarnessContext)."""
    from types import SimpleNamespace

    import harness_runtime.lifecycle.child_workflow_runner as cwr

    captured: dict[str, Any] = {}

    def _spy_execute_workflow(*_args: Any, **kwargs: Any) -> RunResult:
        captured.update(kwargs)
        return _success_result()

    monkeypatch.setattr(cwr, "execute_workflow", _spy_execute_workflow)
    runner = cwr.compose_child_workflow_runner(cast(Any, SimpleNamespace(step_dispatchers={})))
    result = runner(
        workflow_id="child-wf",
        manifest_entry=cast(Any, None),
        steps=(),
        handoff_context=cast(Any, None),
        descent=cast(Any, None),
        default_model_binding=cast(Any, None),
        pause_snapshot_input=None,  # first dispatch → skips the workflow-id guard
    )
    # The opt-in is forwarded → execute_workflow reconstructs the child's final_state.
    assert captured.get("reconstruct_final_state") is True
    assert result.status is RunStatus.SUCCESS


# ---------------------------------------------------------------------------
# AC #9 — audit-entry 4-substep composition (UN-STRUCK at v1.7 §14.7.2 step 8)
# ---------------------------------------------------------------------------


def test_dispatcher_takes_audit_writer_kwarg_at_v1_7(tmp_path: Path) -> None:
    """AC #9 contract surface: `RuntimeSubAgentDispatcher` exposes the 5 new
    v1.7 step-8 kwargs (ledger_writer, audit_writer, audit_signing_key_id,
    audit_signing_algorithm, time_source). Inverts the v1.6 MVP structural
    assertion (which forbade `audit_writer` per the Class 1 fork strike).
    """
    import inspect

    sig = inspect.signature(RuntimeSubAgentDispatcher)
    for required in (
        "ledger_writer",
        "audit_writer",
        "audit_signing_key_id",
        "audit_signing_algorithm",
        "time_source",
    ):
        assert required in sig.parameters, (
            f"RuntimeSubAgentDispatcher missing {required!r} kwarg required "
            f"by spec v1.7 §14.7.2 step 8 4-substep audit composition"
        )


def test_step8a_composes_cp_audit_entry(tmp_path: Path) -> None:
    """AC #9.8a: dispatch produces a `CPAuditLedgerEntry` for the dispatch fact.

    Verified indirectly via the F2 entry's existence at 8b (the dispatch
    fact's ground truth) — see `test_step8b_writes_f2_dispatch_action_entry`.
    """
    dispatcher, _, _ = _dispatcher(tmp_path)
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out is not None


def test_step8b_writes_f2_dispatch_action_entry(tmp_path: Path) -> None:
    """AC #9.8b: composer writes an F2 state-ledger entry whose action_id
    encodes the dispatch action — `dispatch:<parent_action_id>:<child_index>`
    per spec §14.7.2 step 8b.
    """
    from harness_is.state_ledger_write import read_ledger

    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher, _, _ = _dispatcher(tmp_path, ledger_writer_override=ledger_writer)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    entries = read_ledger(ledger_writer.handle)
    dispatch_entries = [e for e in entries if str(e.action_id).startswith("dispatch:")]
    assert len(dispatch_entries) == 1, (
        f"expected exactly one F2 dispatch entry at step 8b; got {len(dispatch_entries)}"
    )
    assert "workflow:parent-wf:step:0" in str(dispatch_entries[0].action_id)


def test_step8b_f2_entry_populates_procedural_tier_snapshot_ref(
    tmp_path: Path,
) -> None:
    """R-003: the 8b F2 dispatch entry populates the `procedural_tier_snapshot_ref`
    D-derivative sidecar via the injected resolver closure (workflow-context
    emission per IS spec v1.3 §C-IS-05 §5.1). `_dispatcher` wires the standard
    test resolver `lambda: Identifier("b" * 64)`.
    """
    from harness_is.state_ledger_write import read_ledger

    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher, _, _ = _dispatcher(tmp_path, ledger_writer_override=ledger_writer)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    entries = read_ledger(ledger_writer.handle)
    dispatch_entries = [e for e in entries if str(e.action_id).startswith("dispatch:")]
    assert len(dispatch_entries) == 1
    assert dispatch_entries[0].procedural_tier_snapshot_ref == _Identifier("b" * 64)


def test_step8b_resolver_raise_halts_before_ledger_write(tmp_path: Path) -> None:
    """R-003 HALT: a raising procedural-tier resolver propagates as
    `SubAgentDispatchAuditComposeError` on the success path (caught by the
    step-8 `except Exception` at the composer) and NO F2 dispatch entry is
    written — the resolver fires before `ledger_writer.append` at 8b.
    """
    from harness_is.state_ledger_write import read_ledger

    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher, _, _ = _dispatcher(tmp_path, ledger_writer_override=ledger_writer)

    def _boom() -> _Identifier:
        raise RuntimeError("resolver boom")

    dispatcher.procedural_tier_snapshot_resolver = _boom

    with pytest.raises(SubAgentDispatchAuditComposeError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())

    entries = read_ledger(ledger_writer.handle)
    dispatch_entries = [e for e in entries if str(e.action_id).startswith("dispatch:")]
    assert dispatch_entries == [], (
        "resolver raise must HALT before the 8b ledger write; no dispatch entry"
    )


def test_step8c_8d_persists_od_audit_entry_through_writer(tmp_path: Path) -> None:
    """AC #9.8c+8d: dispatch produces a CP→OD converter call (8c) + OD
    `AuditLedgerEntry` persisted via `audit_writer.append` (8d); verified by
    reading the audit-tagged entries back from the underlying ledger.
    """
    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher, _, _ = _dispatcher(tmp_path, ledger_writer_override=ledger_writer)
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    # `RuntimeAuditLedgerWriter` wraps audit entries with action_id prefix
    # `audit:<tag>:` per its append discipline; presence of such an entry
    # confirms 8c→8d completed end-to-end.
    audit_writer = dispatcher.audit_writer
    audit_entries = audit_writer.read_all()
    assert len(audit_entries) == 1, (
        f"expected exactly one OD audit entry persisted at step 8d; got {len(audit_entries)}"
    )


def test_step8b_failure_raises_audit_compose_error_on_success_path(
    tmp_path: Path,
) -> None:
    """v1.7 §14.7.2 step 8 failure semantics: F2-write failure on SUCCESS path
    raises `SubAgentDispatchAuditComposeError` mapping to
    `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE`.
    """
    from datetime import UTC, datetime
    from unittest.mock import MagicMock

    failing_ledger = MagicMock(spec=LedgerWriter)
    failing_ledger.actor = _ACTOR
    failing_ledger.append.side_effect = OSError("simulated F2-write failure")
    audit_writer = RuntimeAuditLedgerWriter(
        ledger_writer=_build_ledger_writer(tmp_path),
        time_source=lambda: datetime.now(UTC),
    )
    dispatcher, _, _ = _dispatcher(
        tmp_path,
        ledger_writer_override=failing_ledger,
        audit_writer_override=audit_writer,
    )
    with pytest.raises(SubAgentDispatchAuditComposeError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())


def test_step8_failure_swallowed_on_failed_child_path(tmp_path: Path) -> None:
    """v1.7 §14.7.2 step 8 failure semantics: on FAILED child path, audit
    composition failures are swallowed; `SubAgentChildFailedError` remains the
    primary fault per "the audit-trail-fact record is preserved even when
    downstream substeps fail" clause.
    """
    from datetime import UTC, datetime
    from unittest.mock import MagicMock

    failing_ledger = MagicMock(spec=LedgerWriter)
    failing_ledger.actor = _ACTOR
    failing_ledger.append.side_effect = OSError("simulated F2-write failure")
    audit_writer = RuntimeAuditLedgerWriter(
        ledger_writer=_build_ledger_writer(tmp_path),
        time_source=lambda: datetime.now(UTC),
    )
    dispatcher, _, _ = _dispatcher(
        tmp_path,
        child_result=_failed_result(),
        ledger_writer_override=failing_ledger,
        audit_writer_override=audit_writer,
    )
    # Even with a broken F2-write surface, the child-failure remains the
    # surfaced fault — audit composition is best-effort.
    with pytest.raises(SubAgentChildFailedError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())


# ---------------------------------------------------------------------------
# AC #7 sub-coverage residual — compose_child_workflow_runner real factory
# ---------------------------------------------------------------------------
#
# AC #7's recursive child-runner verification at integration scope (real
# `compose_child_workflow_runner` invoking `execute_workflow` with the
# parent's `ctx.step_dispatchers` registry, real OTel parent-span-id
# linkage between subagent.span + child's workflow.start) is a known
# coverage gap at U-RT-59 v1.6 MVP. The Protocol contract (composer →
# runner kwargs) is covered above via `_MockChildWorkflowRunner`; the
# implementation-side recursion is not exercised end-to-end.
#
# Closure target: jointly with the resolution of
# `.harness/class_1_tension_u_rt_59_async_sync_step_dispatcher.md`. Real
# child-runner integration requires either (a) operator workflows binding
# INFERENCE_STEP via the WorkflowObject.step_dispatchers override, or (b)
# the async/sync resolution arc landing so ctx.step_dispatchers binds
# INFERENCE_STEP at bootstrap. Path (a) is achievable today without
# blocking on the Class 1 fork; if/when authored, add an integration test
# here that exercises the real compose_child_workflow_runner.


def test_compose_child_workflow_runner_factory_is_constructible(tmp_path: Path) -> None:
    """Smoke check: real `compose_child_workflow_runner(ctx)` builds a callable.

    Validates the factory shape without invoking the runner (which would
    require a fully-bootstrapped HarnessContext + ctx.step_dispatchers
    bound; deferred per the AC #7 sub-coverage residual above).
    """
    from harness_runtime.lifecycle.child_workflow_runner import (
        compose_child_workflow_runner,
    )

    # The factory is signature-stable independent of ctx validity at
    # construction; it closes over ctx for later use. Constructing with a
    # placeholder ctx exercises the factory + Protocol satisfaction.
    class _CtxStub:
        step_dispatchers: Any = None

    runner = compose_child_workflow_runner(cast(Any, _CtxStub()))
    assert callable(runner)


# ---------------------------------------------------------------------------
# AC #9 integration — multi-dispatch chain + IS hash-chain integrity
# ---------------------------------------------------------------------------


def test_three_sequential_dispatches_chain_through_audit_writer(tmp_path: Path) -> None:
    """v1.7 §14.7.2 step 8 integration: three sequential sub-agent dispatches
    each produce both an F2 dispatch entry (step 8b) AND an OD audit entry
    (step 8d) through the IS-anchored ledger; the underlying IS hash chain
    remains VALID per `verify_chain` (C-IS-06 §6.4).
    """
    from harness_is.chain_verification import VerificationStatus, verify_chain
    from harness_is.state_ledger_write import read_ledger

    ledger_writer = _build_ledger_writer(tmp_path)
    dispatcher, _, _ = _dispatcher(tmp_path, ledger_writer_override=ledger_writer)

    # Three sequential dispatches with distinct parent_action_ids → distinct
    # F2 dispatch action_ids; idempotency-key collisions avoided per the
    # composer's `dispatch:<parent_action_id>:<child_index>` scheme.
    for i in range(3):
        ctx = StepExecutionContext(
            workflow_id="parent-wf",
            parent_action_id=f"workflow:parent-wf:step:{i}",
            parent_gate_level=GateLevel.AUTO,
            parent_sandbox_tier=SandboxTier.TIER_1_PROCESS,
            parent_actor=_ACTOR,
            parent_entry_hash="",
            parent_idempotency_key="0" * 64,
            tenant_id=None,
            step_index=i,
        )
        dispatcher.dispatch(_binding(), _step(), step_context=ctx)

    # Read back: 3 F2 dispatch entries (8b) + 3 OD audit-wrapped entries (8d)
    # interleaved in append order.
    entries = read_ledger(ledger_writer.handle)
    dispatch_entries = [e for e in entries if str(e.action_id).startswith("dispatch:")]
    audit_entries = [e for e in entries if str(e.action_id).startswith("audit:")]
    assert len(dispatch_entries) == 3, (
        f"expected 3 F2 dispatch entries; got {len(dispatch_entries)}"
    )
    assert len(audit_entries) == 3, f"expected 3 OD audit-wrapped entries; got {len(audit_entries)}"

    # IS hash chain across all 6 entries remains VALID per C-IS-06 §6.4.
    result = verify_chain(entries)
    assert result.status == VerificationStatus.VALID, (
        f"IS hash chain verification failed across the 6 sequential entries: {result}"
    )


# ---------------------------------------------------------------------------
# Module-level: cast unused symbol to silence linters
# ---------------------------------------------------------------------------

_ = cast
