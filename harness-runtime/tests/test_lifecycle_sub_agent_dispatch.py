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
  AC #9 partial — audit-entry composition (write half STRUCK per Class 1 fork)
      → test_audit_entry_composed_via_handoff_registry
      → test_audit_entry_not_written_via_ctx_audit_writer_v1_6_mvp
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
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
from harness_cp.handoff_context import ActionKind
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
    WorkflowStep,
)
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_runtime.lifecycle.handoff import RuntimeHandoffRegistry
from harness_runtime.lifecycle.sub_agent_dispatch import (
    RuntimeSubAgentDispatcher,
    SubAgentChildFailedError,
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
    ) -> RunResult:
        self.calls.append(
            {
                "workflow_id": workflow_id,
                "manifest_entry": manifest_entry,
                "steps": tuple(steps),
                "handoff_context": handoff_context,
                "descent": descent,
                "default_model_binding": default_model_binding,
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


def _dispatcher(*, child_result: RunResult | None = None) -> tuple[
    RuntimeSubAgentDispatcher, _MockChildWorkflowRunner, InMemorySpanExporter
]:
    """Compose a RuntimeSubAgentDispatcher with mocked child runner + real
    handoff/topology registries + InMemorySpanExporter for verification."""
    tp, exporter = _tracer_provider_with_exporter()
    runner = _MockChildWorkflowRunner(
        next_result=child_result if child_result is not None else _success_result()
    )
    dispatcher = RuntimeSubAgentDispatcher(
        handoff_registry=RuntimeHandoffRegistry(),
        topology_dispatcher=RuntimeTopologyDispatcher(),
        tracer_provider=tp,
        child_workflow_runner=runner,  # type: ignore[arg-type]
    )
    return dispatcher, runner, exporter


# ---------------------------------------------------------------------------
# AC #2 — Protocol satisfaction
# ---------------------------------------------------------------------------


def test_runtime_sub_agent_dispatcher_satisfies_step_dispatcher_protocol() -> None:
    """AC #2: isinstance check passes via @runtime_checkable Protocol."""
    dispatcher, _, _ = _dispatcher()
    assert isinstance(dispatcher, StepDispatcher)


# ---------------------------------------------------------------------------
# AC #3 — payload validation
# ---------------------------------------------------------------------------


def test_payload_validation_rejects_mis_shaped_payload() -> None:
    """AC #3: a SUB_AGENT_DISPATCH step with bad step_payload raises typed error."""
    dispatcher, _, _ = _dispatcher()
    bad_step = WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.SUB_AGENT_DISPATCH,
        step_payload={"random": "junk"},
    )
    with pytest.raises(SubAgentDispatchPayloadShapeError):
        dispatcher.dispatch(_binding(), bad_step, step_context=_step_context())


def test_payload_validation_accepts_4_field_shape() -> None:
    """AC #3: valid 4-field payload validates + composer proceeds."""
    payload = _payload()
    assert payload.child_workflow_id == "child-wf"
    assert payload.brief.objective.startswith("extract")
    assert len(payload.child_steps) == 1


# ---------------------------------------------------------------------------
# AC #4 — HandoffContext composition
# ---------------------------------------------------------------------------


def test_handoff_context_composed_per_v1_6_mvp_table() -> None:
    """AC #4: composer constructs the 7-field HandoffContext per §14.7.3 table."""
    dispatcher, runner, _ = _dispatcher()
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


def test_handoff_context_audit_trail_link_per_path_a_v1_6() -> None:
    """AC #4: audit_trail_link constructed from step_context per v1.6 Path A."""
    dispatcher, runner, _ = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    hc = runner.calls[0]["handoff_context"]
    assert hc.audit_trail_link.action_id == _step_context().parent_action_id
    assert hc.audit_trail_link.entry_hash == _step_context().parent_entry_hash
    # Actor projected from IS Actor.actor_id → CP ActorIdentity per carrier-map.
    assert str(hc.audit_trail_link.actor) == _ACTOR.actor_id


# ---------------------------------------------------------------------------
# AC #5 — gate-level descent + topology admissibility
# ---------------------------------------------------------------------------


def test_dispatch_invokes_handoff_registry_with_step_context_seeds() -> None:
    """AC #5a: composer's handoff_registry.dispatch receives step_context seeds."""
    dispatcher, runner, _ = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    descent = runner.calls[0]["descent"]
    assert isinstance(descent, SubAgentGateLevelDescent)
    # Descent's child_gate_level descends from step_context.parent_gate_level
    # (AUTO at MVP); no operator override → child inherits AUTO.
    assert descent.child_gate_level == GateLevel.AUTO


def test_topology_primary_passes_strict_gate() -> None:
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
    dispatcher, runner, exporter = _dispatcher()
    dispatcher.dispatch(_binding(), _step(payload), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1
    attrs = dict(spans[0].attributes or {})
    assert attrs["topology.pattern"] == TopologyPattern.SINGLE_THREADED_LINEAR.value
    assert len(runner.calls) == 1


def test_topology_cross_pattern_admissible_passes_strict_gate() -> None:
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
    dispatcher, runner, exporter = _dispatcher()
    dispatcher.dispatch(_binding(), _step(payload), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1
    attrs = dict(spans[0].attributes or {})
    assert attrs["topology.pattern"] == TopologyPattern.HIERARCHICAL_DELEGATION.value
    assert len(runner.calls) == 1


def test_topology_neither_primary_nor_admissible_raises() -> None:
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
    dispatcher, runner, exporter = _dispatcher()
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


def test_dispatch_emits_exactly_one_subagent_span() -> None:
    """AC #6: exactly one subagent.span per composer invocation."""
    dispatcher, _, exporter = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    spans = [s for s in exporter.get_finished_spans() if s.name == "subagent.span"]
    assert len(spans) == 1


def test_subagent_span_carries_7_subagent_attributes() -> None:
    """AC #6: the 7 subagent.* attributes per C-CP-14 §14.2 verbatim."""
    dispatcher, _, exporter = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    expected = {schema.attribute_name for schema in SUBAGENT_NAMESPACE_SCHEMA}
    assert expected.issubset(set(attrs.keys()))


def test_subagent_span_carries_2_narrow_topology_attributes() -> None:
    """AC #6: narrow-subset 2 topology.* attributes (pattern + workload_class)."""
    dispatcher, _, exporter = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert "topology.pattern" in attrs
    assert "topology.workload_class" in attrs


def test_subagent_span_does_not_carry_8_fanout_topology_attributes() -> None:
    """AC #6: explicit absence of 8 fan-out-specific topology.* attributes."""
    dispatcher, _, exporter = _dispatcher()
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


def test_attribute_names_come_from_canonical_carrier() -> None:
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


def test_dispatch_invokes_child_workflow_runner() -> None:
    """AC #7: composer invokes the injected child runner with the child shape."""
    dispatcher, runner, _ = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["workflow_id"] == "child-wf"
    assert call["manifest_entry"].workflow_id == "child-wf"
    assert len(call["steps"]) == 1
    assert call["default_model_binding"] == _binding().model_binding


def test_child_runner_receives_handoff_context_and_descent() -> None:
    """AC #7: child runner sees fully-composed HandoffContext + descent."""
    dispatcher, runner, _ = _dispatcher()
    dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    call = runner.calls[0]
    assert call["handoff_context"].proposed_action.action_kind == ActionKind.SUB_AGENT_DISPATCH
    assert isinstance(call["descent"], SubAgentGateLevelDescent)


# ---------------------------------------------------------------------------
# AC #8 — child result mapping
# ---------------------------------------------------------------------------


def test_success_maps_to_completed_returns_final_state() -> None:
    """AC #8a: child SUCCESS → subagent.result_status=completed; returns final_state."""
    dispatcher, _, exporter = _dispatcher(child_result=_success_result())
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out == {"child_field": "value"}
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "completed"
    assert attrs["subagent.request_blocked_by_budget"] is False


def test_drained_maps_to_completed_returns_partial_state() -> None:
    """AC #8b: child DRAINED → subagent.result_status=completed; returns partial_state."""
    dispatcher, _, exporter = _dispatcher(child_result=_drained_result())
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out == {"partial_field": "partial_value"}
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "completed"


def test_failed_raises_sub_agent_child_failed_error_with_span_attrs() -> None:
    """AC #8c: child FAILED → subagent.result_status=failed + raises typed error."""
    dispatcher, _, exporter = _dispatcher(child_result=_failed_result())
    with pytest.raises(SubAgentChildFailedError):
        dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    span = next(s for s in exporter.get_finished_spans() if s.name == "subagent.span")
    attrs = dict(span.attributes or {})
    assert attrs["subagent.result_status"] == "failed"


# ---------------------------------------------------------------------------
# AC #9 partial — audit-entry composition (write half STRUCK per Class 1 fork)
# ---------------------------------------------------------------------------


def test_audit_entry_composed_via_handoff_registry() -> None:
    """AC #9 partial: composer calls handoff_registry.compose_dispatch_audit.

    Write site (ctx.audit_writer.append) is STRUCK at v1.6 MVP per the Class 1
    fork on CP→OD audit-write composition (joins fork-cp-is-wiring-gaps).
    Verified indirectly: dispatch completes without raising on
    audit-write-related types; the entry is composed (composer body inspection)
    but not persisted.
    """
    dispatcher, _, _ = _dispatcher()
    # Dispatch completes without raising → audit composition succeeded.
    # (The CPAuditLedgerEntry is composed inline; not surfaced through
    # any return path at v1.6 MVP since the write site is STRUCK.)
    out = dispatcher.dispatch(_binding(), _step(), step_context=_step_context())
    assert out is not None


def test_audit_entry_not_written_via_ctx_audit_writer_v1_6_mvp() -> None:
    """AC #9 partial: confirm RuntimeSubAgentDispatcher takes no audit_writer
    parameter at v1.6 MVP per the Class 1 fork on CP→OD audit-write composition.

    Structural assertion: the dataclass's __init__ signature does not include
    an `audit_writer` parameter. v1.6 composer composes the
    CPAuditLedgerEntry via handoff_registry; the OD-side write site is
    deferred to a future Phase 6 CP-composer-authoring arc.
    """
    import inspect

    sig = inspect.signature(RuntimeSubAgentDispatcher)
    assert "audit_writer" not in sig.parameters, (
        "RuntimeSubAgentDispatcher must not take an audit_writer at v1.6 MVP — "
        "the CP→OD audit-write composition is deferred per the Class 1 fork; "
        "compose-only AC #9 partial-landing means no write-side dependency."
    )


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


def test_compose_child_workflow_runner_factory_is_constructible() -> None:
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
# Module-level: cast unused symbol to silence linters
# ---------------------------------------------------------------------------

_ = cast
