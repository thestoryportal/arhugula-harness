"""B-78 — an `EVALUATOR_OPTIMIZER` generate-step's own `SUB_AGENT_BOUNDARY`
HITL gate now pauses cleanly and resumes correctly, mirroring the B-72 fix for
the fan-out topologies (`PARALLELIZATION` / `ORCHESTRATOR_WORKERS` /
`HIERARCHICAL_DELEGATION`).

## History (read before trusting stale framing elsewhere)

`.harness/forward-register.yaml` B-78 (`registered_finding`) was originally
framed as a symmetric sibling of the B-72 livelock: "does a resolved operator
answer get silently dropped on resume, causing the gate to re-fire forever?"

A first grounding pass found that framing did not even get to fire: EO's
`_dispatch_and_buffer` (and DH's stage-dispatch try/except) had NO
`except BaseException` catch at all for the runtime's `HITLPauseRequestedSignal`
(a `BaseException` subclass, deliberately NOT an `Exception` subclass,
`hitl_gate_composer.py:381` — specifically so it survives generic
`except Exception` handlers and reaches a dedicated name-matched catch,
harness-cp cannot import the harness-runtime type). 4 of 6 `TopologyPattern`
strategies already had that catch (LINEAR `workflow_driver.py:5161`,
`_execute_parallelization` `:9591`, `_execute_orchestrator_workers` `:13700`,
and `HIERARCHICAL_DELEGATION` via the latter's recursive reuse); EO and DH had
none — the signal propagated past both functions' `except SubAgentChildPausedError`
/ `except Exception` clauses (both `Exception` subtypes, bypassed by a
`BaseException` subclass), out of the `asyncio.to_thread` worker, and crashed
the entire in-process MCP session (`api_run`/`resume` raised a
`BaseExceptionGroup`, never returning a `RunResult` at all) — **gap 1**.

A follow-up mutation probe found a SECOND, independent gap sitting right
behind the first: even with gap 1's crash fixed, resuming with a resolved
`ResumeContext.hitl_response` still re-escalated (never delivered the answer)
because EO/DH never constructed a `HITLDeliveryCell`/set `hitl_delivery_holder`
on any `StepExecutionContext` — the exact mechanism the `SINGLE_THREADED_LINEAR`
path already has at `workflow_driver.py:4830-4859` — **gap 2**.

## The fix (this file now pins the FIXED shape for both gaps)

`_execute_evaluator_optimizer`'s `_dispatch_and_buffer` now carries a
name-matched `except BaseException` clause (mirroring
`_execute_parallelization`'s own per-branch catch) that wraps a genuine
`HITLPauseRequestedSignal` into a typed `_EvaluatorOptimizerHITLPauseError`,
handled by a dedicated outer `except` clause that pauses UNCONDITIONALLY
(whenever a `pause_resume_protocol` is bound — not gated on `cascade_policy`,
which governs step-FAILURE reactions, not HITL gate REQUESTS) with
`pause_reason=WorkflowPauseReason.HITL_PENDING` (gap 1). A `hitl_delivery_cell`
is now constructed near the resume-recovery block (mirroring
`workflow_driver.py:4830-4859` exactly) and threaded onto the FIRST
`_dispatch_and_buffer` call made this resume cycle via
`hitl_delivery_holder=(hitl_delivery_cell if entry_index ==
_resume_completed_count else None)` (gap 2). `_execute_decentralized_handoff`
received the structurally identical fix (see that function's own
`except BaseException` clause and the `hitl_delivery_cell` construction near
its `_resume_completed_count`, plus the `stage_ctx` trailing `model_copy`
override — `compose_branch_child_context` unconditionally resets
`hitl_delivery_holder` to `None` for every composed child, so the cell must be
re-applied AFTER that composer call, not merely set on `spawning`).

EO/DH are strictly sequential single-owner topologies (no fan-out, no
branch-ordinal ambiguity per CP spec v1.108 §1's property-6 framing — that
carrier exists only for peer-branch topologies), so the LINEAR path's simpler,
unconditional mechanism applies directly; no new carrier field was needed on
`EvaluatorOptimizerResumeState`/`HandoffResumeState`.

## Empirically observed post-fix shape (verified by direct execution, not assumed)

The initial dispatch pauses cleanly: `status='paused'`,
`pause_reason=HITL_PENDING`, exactly 1 webhook POST, the real
`RuntimeSubAgentDispatcher.dispatch` never reached. Resuming with a resolved
`ResumeContext.hitl_response` delivers the answer: still exactly 1 webhook POST
total (no re-escalation) and the real dispatcher IS reached exactly once — but
the run re-pauses a SECOND time with `pause_reason=EXPLICIT_OPERATOR` (an
ordinary post-delivery dispatch outcome, folded through EO's/DH's existing
`cascade_policy=pause` step-failure path), rather than completing to SUCCESS.
This is the SAME shape the B-72 precedent's own resume test documents for the
identical trivial-child fixture (see that file's "SEPARATE ISSUE" note) — a
pre-existing, orthogonal behavior of this test's child shape, not a regression
of the B-78 fix. The discriminating oracle (mirroring B-72) is that the SECOND
pause is labeled `EXPLICIT_OPERATOR`, never a re-fired `HITL_PENDING`.

## DECENTRALIZED_HANDOFF reachability

`_execute_decentralized_handoff`'s own docstring states each stage dispatches
"NEVER `SUB_AGENT_DISPATCH`" (a design-intent statement) — but
`step_dispatchers.lookup(step.step_kind)` does not enforce that; a manifest CAN
declare a `SUB_AGENT_DISPATCH` stage under DH and reach the identical gate,
confirmed empirically by `test_dh_stage_own_gate_pauses_and_resumes` below.

Mirrors `test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py`'s real-stack
pattern verbatim (fakes lifted by value): `step_dispatchers` deliberately
UNSET so `api_run` falls back to `ctx.step_dispatchers`, the REAL production
`StepDispatcherRegistry` including the REAL `RuntimeHITLGateComposer` wrapping
the sub-agent dispatcher. Only the Anthropic SDK leaf client and the webhook
HTTP transport are faked.

Per `[[verification-shape-sharpened-grep-vs-e2e]]`: every assertion here is
by-execution against the production stack, not a grep for wiring presence.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import httpx
import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.identity import EntryID, StepID
from harness_core.persona_tier import PersonaTier
from harness_core.workload_class import WorkloadClass
from harness_cp.cp_shared_types import ModelBinding
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.engine_class import EngineClass
from harness_cp.hitl_placement import HITLPlacement, HITLPlacementKind, HITLResult
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.hitl_timeout_degradation import WebhookConfig
from harness_cp.pause_resume_protocol_types import ResumeContext, WorkflowPauseReason
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.sub_agent_brief import (
    ClearTaskBoundaries,
    OutputSchema,
    OutputSchemaKind,
    SubAgentBrief,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.path_class_registry import PathClass
from harness_runtime.api import RunResult, resume
from harness_runtime.api import run as api_run
from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
from harness_runtime.bootstrap import stage_5_loop_init as _stage_5_mod
from harness_runtime.lifecycle import sub_agent_dispatch
from harness_runtime.lifecycle.pause_resume_protocol_types import (
    PauseResumeProtocolConfig,
)
from harness_runtime.lifecycle.providers import ProviderClientsStage
from harness_runtime.lifecycle.sub_agent_dispatch import SubAgentDispatchPayload
from harness_runtime.lifecycle.webhook_delivery_composer import WebhookDeliveryComposer
from harness_runtime.lifecycle.webhook_delivery_composer_types import (
    WebhookDeliveryComposerConfig,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_SURFACE = DeploymentSurface.LOCAL_DEVELOPMENT
_WORKFLOW_ID = "wf-b78-eo-sub-agent-dispatch-hitl-gate-resume"
_CHILD_WORKFLOW_ID = "child-wf-b78-eo"

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


def _path_bindings(tmp_path: Path) -> PathBindingConfig:
    # Covers both `_WORKLOAD` (SOFTWARE_ENGINEERING, the EO fixtures' workload
    # class) and PIPELINE_AUTOMATION (the DH fixture's workload class — DH is
    # only §10.3 cross-pattern admissible there; see
    # `_DecentralizedHandoffSubAgentDispatchWorkflow`'s own docstring). One
    # shared `_config()` covers all three tests in this module.
    return PathBindingConfig(
        raw_entries=tuple(
            {
                "path_class": pc,
                "workflow_class": wc,
                "deployment_surface": _SURFACE,
                "path": str(tmp_path / wc.value.lower() / pc.value.lower()),
            }
            for pc in PathClass
            for wc in (_WORKLOAD, WorkloadClass.PIPELINE_AUTOMATION)
        ),
    )


def _config(tmp_path: Path) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=_SURFACE,
        repository_root=tmp_path,
        path_bindings=_path_bindings(tmp_path),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.EVALUATOR_OPTIMIZER,
        mcp_clients=[],
        openai_optional=True,
        ollama_optional=True,
        pause_resume_protocol_config=PauseResumeProtocolConfig.default(),
        webhook_delivery_composer_config=WebhookDeliveryComposerConfig.default(),
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(_CHAIN,),
            retry_policies={},
        ),
    )


def _child_brief() -> SubAgentBrief:
    return SubAgentBrief(
        objective="say a single token",
        output_format=OutputSchema(
            schema_kind=OutputSchemaKind.JSON_SCHEMA,
            schema_body='{"type":"object"}',
        ),
        guidance="minimal — trivial child, no nested HITL gate of its own",
        task_boundaries=ClearTaskBoundaries(
            in_scope=("say a token",),
            out_of_scope=("anything else",),
            termination_criteria=("token emitted",),
        ),
        summary_hash="0" * 64,
    )


def _child_manifest() -> WorkflowManifestEntry:
    """A TRIVIAL child — no HITL gate of its own. This test isolates the
    GENERATE step's own gate; it does not need a nested-paused-descendant
    scenario to observe the gap (see module docstring)."""
    return WorkflowManifestEntry(
        workflow_id=_CHILD_WORKFLOW_ID,
        workload_class=_WORKLOAD,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _sub_agent_dispatch_payload() -> SubAgentDispatchPayload:
    return SubAgentDispatchPayload(
        child_workflow_id=_CHILD_WORKFLOW_ID,
        child_manifest_entry=_child_manifest(),
        child_steps=(
            WorkflowStep(
                step_id=StepID("child-step-0"),
                step_kind=StepKind.INFERENCE_STEP,
                step_payload={
                    "messages": [{"role": "user", "content": "Say 'a'"}],
                    "tools": [],
                    "params": {"max_tokens": 4},
                },
            ),
        ),
        brief=_child_brief(),
    )


class _EvaluatorOptimizerSubAgentDispatchWorkflow:
    """An `EVALUATOR_OPTIMIZER` workflow: `steps[0]` (generate) is
    `SUB_AGENT_DISPATCH` carrying its own `SUB_AGENT_BOUNDARY` HITL placement
    at the `TEAM_BINDING` x `RECONCILER_LOOP` `DURABLE_ASYNC` cell (SAME cell
    the B-72 fan-out precedent uses — `matrix_cell_for` is placement-agnostic,
    keyed only on `(persona_tier, engine_class)`). `steps[1]` (evaluate) is a
    trivial `INFERENCE_STEP`, never reached by this test (the crash happens
    inside the FIRST dispatch of `steps[0]`).

    `step_dispatchers` deliberately NOT declared — falls back to
    `ctx.step_dispatchers`, the REAL production registry.
    """

    @property
    def workflow_id(self) -> str:
        return _WORKFLOW_ID

    @property
    def workload_class(self) -> WorkloadClass:
        return _WORKLOAD

    @property
    def manifest_entry(self) -> WorkflowManifestEntry:
        return WorkflowManifestEntry(
            workflow_id=_WORKFLOW_ID,
            workload_class=_WORKLOAD,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.RECONCILER_LOOP,
            topology_pattern=TopologyPattern.EVALUATOR_OPTIMIZER,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY),),
            per_step_overrides={},
        )

    @property
    def steps(self) -> Sequence[WorkflowStep]:
        return (
            WorkflowStep(
                step_id=StepID("generate-0"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload=_sub_agent_dispatch_payload().model_dump(),
            ),
            WorkflowStep(
                step_id=StepID("evaluate-0"),
                step_kind=StepKind.INFERENCE_STEP,
                step_payload={
                    "messages": [{"role": "user", "content": "Evaluate the draft"}],
                    "tools": [],
                    "params": {"max_tokens": 4},
                },
            ),
        )

    @property
    def default_model_binding(self) -> ModelBinding:
        return ModelBinding(provider="anthropic", model="claude-haiku-4-5")


_DH_WORKFLOW_ID = "wf-b78-dh-sub-agent-dispatch-hitl-gate-resume"
_DH_CHILD_WORKFLOW_ID = "child-wf-b78-dh"


def _dh_child_manifest() -> WorkflowManifestEntry:
    """A TRIVIAL child — no HITL gate of its own (mirrors `_child_manifest`)."""
    return WorkflowManifestEntry(
        workflow_id=_DH_CHILD_WORKFLOW_ID,
        workload_class=WorkloadClass.PIPELINE_AUTOMATION,
        persona_tier=PersonaTier.SOLO_DEVELOPER,
        engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
        topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
        layer_budgets=(),
        fallback_chain=_CHAIN,
        hitl_placements=(),
        per_step_overrides={},
    )


def _dh_sub_agent_dispatch_payload() -> SubAgentDispatchPayload:
    return SubAgentDispatchPayload(
        child_workflow_id=_DH_CHILD_WORKFLOW_ID,
        child_manifest_entry=_dh_child_manifest(),
        child_steps=(
            WorkflowStep(
                step_id=StepID("child-step-0"),
                step_kind=StepKind.INFERENCE_STEP,
                step_payload={
                    "messages": [{"role": "user", "content": "Say 'a'"}],
                    "tools": [],
                    "params": {"max_tokens": 4},
                },
            ),
        ),
        brief=_child_brief(),
    )


class _DecentralizedHandoffSubAgentDispatchWorkflow:
    """A `DECENTRALIZED_HANDOFF` workflow: ONE stage, whose step is
    `SUB_AGENT_DISPATCH` carrying its own `SUB_AGENT_BOUNDARY` HITL placement
    at the SAME `TEAM_BINDING` x `RECONCILER_LOOP` `DURABLE_ASYNC` matrix cell
    the EO/B-72 fixtures use (`matrix_cell_for` is placement-agnostic, keyed
    only on `(persona_tier, engine_class)`).

    `DECENTRALIZED_HANDOFF` is only §10.3 cross-pattern admissible at
    `WorkloadClass.PIPELINE_AUTOMATION` (`topology_pattern.py`'s
    `_CROSS_PATTERN_ADMISSIBLE` set) — a DIFFERENT workload class than the
    EO/B-72 fixtures' `SOFTWARE_ENGINEERING`, purely a topology-admissibility
    requirement, orthogonal to the HITL gate mechanism this test targets.
    `d4_tunable`'s `cascade_policy` selection keys ONLY on `persona_tier`
    (`TEAM_BINDING` → `PAUSE`), so the workload-class swap does not change the
    cascade-policy shape verified against the EO/B-72 fixtures.

    Proves `_execute_decentralized_handoff`'s own docstring claim that stages
    are "NEVER `SUB_AGENT_DISPATCH`" is a design-intent statement, NOT a
    code-enforced constraint — this manifest declares exactly that, and
    `step_dispatchers.lookup(step.step_kind)` dispatches it regardless.

    `step_dispatchers` deliberately NOT declared — falls back to
    `ctx.step_dispatchers`, the REAL production registry.
    """

    @property
    def workflow_id(self) -> str:
        return _DH_WORKFLOW_ID

    @property
    def workload_class(self) -> WorkloadClass:
        return WorkloadClass.PIPELINE_AUTOMATION

    @property
    def manifest_entry(self) -> WorkflowManifestEntry:
        return WorkflowManifestEntry(
            workflow_id=_DH_WORKFLOW_ID,
            workload_class=WorkloadClass.PIPELINE_AUTOMATION,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.RECONCILER_LOOP,
            topology_pattern=TopologyPattern.DECENTRALIZED_HANDOFF,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY),),
            per_step_overrides={},
        )

    @property
    def steps(self) -> Sequence[WorkflowStep]:
        return (
            WorkflowStep(
                step_id=StepID("stage-0"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload=_dh_sub_agent_dispatch_payload().model_dump(),
            ),
        )

    @property
    def default_model_binding(self) -> ModelBinding:
        return ModelBinding(provider="anthropic", model="claude-haiku-4-5")


# ---------------------------------------------------------------------------
# Fakes — lifted by value from `test_b72_fanout_sub_agent_dispatch_hitl_gate_
# resume.py` (itself lifted from `test_u_rt_95_hitl_resume_consume_cycle_e2e.py`).
# ---------------------------------------------------------------------------


class _FakeAnthropicUsage:
    input_tokens = 5
    output_tokens = 3


class _FakeAnthropicResponse:
    def __init__(self, model: str) -> None:
        self.id = "msg-fake-b78-eo"
        self.model = model
        self.usage = _FakeAnthropicUsage()
        self.stop_reason = "end_turn"
        self.content = [{"type": "text", "text": "ok"}]

    def model_dump(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "model": self.model,
            "content": self.content,
            "stop_reason": self.stop_reason,
        }


class _SucceedingAnthropicMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, *, model: str, **kwargs: Any) -> _FakeAnthropicResponse:
        self.calls.append({"model": model, **kwargs})
        return _FakeAnthropicResponse(model)


class _SucceedingAnthropicClient:
    def __init__(self) -> None:
        self.messages = _SucceedingAnthropicMessages()


class _FakeAdapter:
    def __init__(self, name: str, client: Any) -> None:
        self.name = name
        self.client = client
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class _FakeProvider:
    def __init__(self, name: str) -> None:
        self.name = name

    async def aclose(self) -> None:
        return None


class _FakeDaemon:
    async def start(self) -> None:
        return None

    async def stop(self, *, timeout_seconds: float = 5.0) -> None:
        _ = timeout_seconds


class _FakeTracerProvider:
    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        _ = timeout_millis
        return True

    def shutdown(self) -> None:
        return None

    def get_tracer(self, instrumenting_module_name: str, /) -> object:
        from opentelemetry.trace import NoOpTracer

        _ = instrumenting_module_name
        return NoOpTracer()


def _install_fake_webhook_composer_factory(
    monkeypatch: pytest.MonkeyPatch,
    captured_requests: list[httpx.Request],
) -> None:
    def _handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, json={"ack": True})

    transport = httpx.MockTransport(_handler)

    async def _fake_materialize_webhook_delivery_composer_stage(
        config: RuntimeConfig, ctx: Any
    ) -> WebhookDeliveryComposer | None:
        if config.webhook_delivery_composer_config is None:
            return None
        return WebhookDeliveryComposer(
            webhook_config=WebhookConfig(
                webhook_id="b78-eo-hook",
                endpoint_url="https://b78-eo-e2e.invalid/hook",
                timeout=5,
                degradation_mode="fail-closed",
            ),
            http_client_factory=lambda: httpx.AsyncClient(transport=transport),
        )

    monkeypatch.setattr(
        _stage_5_mod,
        "materialize_webhook_delivery_composer_stage",
        _fake_materialize_webhook_delivery_composer_stage,
    )


def _install_fake_od_stage4(monkeypatch: pytest.MonkeyPatch) -> None:
    daemon = _FakeDaemon()
    tracer = _FakeTracerProvider()

    class _CollectorStage:
        def __init__(self, d: _FakeDaemon) -> None:
            self.daemon = d

    class _TracerStage:
        def __init__(self, p: _FakeTracerProvider) -> None:
            self.provider = p
            self.registered_globally = False

    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_collector_daemon_stage",
        lambda config, **_kw: _CollectorStage(daemon),
    )
    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_ring_buffer_stage", lambda config, _d, **_kw: None
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_kw: _TracerStage(tracer),
    )
    monkeypatch.setattr(
        _stage_4_od_mod, "materialize_span_processor_stage", lambda config, _p, **_kw: None
    )


def _install_fake_providers(monkeypatch: pytest.MonkeyPatch, anthropic_client: Any) -> None:
    providers = {
        "anthropic": _FakeAdapter("anthropic", anthropic_client),
        "openai": _FakeProvider("openai"),
        "ollama": _FakeProvider("ollama"),
    }

    async def _fake_clients(*_a: object, **_k: object) -> ProviderClientsStage:
        return ProviderClientsStage(providers=dict(providers))

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_3a_cp_clients.materialize_provider_clients_stage",
        _fake_clients,
    )


@pytest.fixture
def _captured_webhook_requests() -> Iterator[list[httpx.Request]]:
    yield []


def _resolved_hitl_result(*, entry_suffix: str) -> HITLResult:
    return HITLResult(
        response=HITLResponse.APPROVE,
        timestamp="2026-07-26T00:00:00Z",
        audit_ledger_entry_id=EntryID(f"e-b78-{entry_suffix}"),
        response_summary_hash="a" * 64,
    )


# ---------------------------------------------------------------------------
# Test 1 — the generate step's own gate pauses cleanly on first dispatch
# (gap 1, FIXED).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_eo_generate_step_own_gate_pauses_on_first_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """B-78 gap 1 FIXED: the EO generate step's own `SUB_AGENT_BOUNDARY` gate
    fires (producer side confirmed working) and `_execute_evaluator_optimizer`
    now converts the resulting `HITLPauseRequestedSignal` into a clean
    `RunStatus.PAUSED` result — no more `BaseExceptionGroup` crash.

    Mirrors `test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py::
    test_fanout_branch_own_gate_pauses_on_first_dispatch`.
    """
    _install_fake_providers(monkeypatch, _SucceedingAnthropicClient())
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    sub_agent_dispatcher_calls: list[Any] = []
    _original_dispatch = sub_agent_dispatch.RuntimeSubAgentDispatcher.dispatch

    def _spying_dispatch(self: Any, *args: Any, **kwargs: Any) -> Any:
        sub_agent_dispatcher_calls.append((args, kwargs))
        return _original_dispatch(self, *args, **kwargs)

    monkeypatch.setattr(sub_agent_dispatch.RuntimeSubAgentDispatcher, "dispatch", _spying_dispatch)

    config = _config(tmp_path)
    workflow = _EvaluatorOptimizerSubAgentDispatchWorkflow()

    paused = await api_run(workflow, config=config)
    assert isinstance(paused, RunResult)
    assert paused.status == "paused", (
        f"expected the generate step's own SUB_AGENT_BOUNDARY gate to pause "
        f"the run on first dispatch; got status={paused.status!r} "
        f"failure_cause={paused.failure_cause!r}"
    )
    assert paused.pause_snapshot is not None
    assert paused.pause_snapshot.pause_reason is WorkflowPauseReason.HITL_PENDING, (
        f"expected the pause to be labeled HITL_PENDING (a genuine HITL gate "
        f"request, not an ordinary step failure); got "
        f"pause_reason={paused.pause_snapshot.pause_reason!r}"
    )
    assert len(_captured_webhook_requests) == 1, (
        f"expected exactly 1 webhook POST from the generate step's own gate "
        f"firing; got {len(_captured_webhook_requests)}"
    )
    assert sub_agent_dispatcher_calls == [], (
        "the generate step's own SUB_AGENT_BOUNDARY gate must escalate BEFORE "
        "ever reaching the real RuntimeSubAgentDispatcher — got "
        f"{len(sub_agent_dispatcher_calls)} dispatcher call(s)."
    )


# ---------------------------------------------------------------------------
# Test 2 — the resumed gate consumes a delivered answer instead of
# re-escalating (gap 2, FIXED).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_eo_generate_step_gate_resume_with_resolved_answer_is_consumed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """B-78 gap 2 FIXED — mirrors
    `test_b72_fanout_sub_agent_dispatch_hitl_gate_resume.py::
    test_fanout_branch_gate_resume_with_resolved_answer_is_consumed` exactly.

    1. `len(_captured_webhook_requests) == 1` (NOT re-escalated — the
       generate step's own gate consumed the delivered answer on resume
       instead of re-firing a second webhook POST).
    2. `sub_agent_dispatcher_calls` has exactly 1 entry — a DIRECT spy on
       `RuntimeSubAgentDispatcher.dispatch` proves the real dispatcher WAS
       reached this time, i.e. the delivered `hitl_response` unblocked the
       gate rather than re-pausing it.
    3. `resumed.pause_snapshot is not None` (a caller-facing dead-end would
       slip through the other assertions unnoticed).
    4. `resumed.workflow_id == paused.workflow_id` (run identity preserved
       across the resume cycle).
    5. `resumed.pause_snapshot.pause_reason == EXPLICIT_OPERATOR`, NOT
       `HITL_PENDING` — the SAME "separate, pre-existing issue" the B-72
       precedent's own resume test documents for the identical trivial-child
       fixture shape (child `EngineClass.PURE_PATTERN_NO_ENGINE`): the
       delivered answer IS consumed and the real dispatcher IS reached
       (assertions 1-2 above), but this test's child shape then produces an
       ordinary ran-and-errored outcome, folded through the SAME
       `cascade_policy=pause` step-failure path as any other step failure —
       a SECOND, unrelated pause. This assertion pins that the second pause
       is a genuine ordinary step outcome and NOT a re-fired HITL gate,
       which is the discriminator that proves the B-78 fix, not the B-72
       precedent's separate pre-existing behavior, is what's under test.
    """
    anthropic_client = _SucceedingAnthropicClient()
    _install_fake_providers(monkeypatch, anthropic_client)
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    sub_agent_dispatcher_calls: list[Any] = []
    _original_dispatch = sub_agent_dispatch.RuntimeSubAgentDispatcher.dispatch

    def _spying_dispatch(self: Any, *args: Any, **kwargs: Any) -> Any:
        sub_agent_dispatcher_calls.append((args, kwargs))
        return _original_dispatch(self, *args, **kwargs)

    monkeypatch.setattr(sub_agent_dispatch.RuntimeSubAgentDispatcher, "dispatch", _spying_dispatch)

    config = _config(tmp_path)
    workflow = _EvaluatorOptimizerSubAgentDispatchWorkflow()

    paused = await api_run(workflow, config=config)
    assert paused.status == "paused"
    assert paused.pause_snapshot is not None
    assert len(_captured_webhook_requests) == 1
    assert sub_agent_dispatcher_calls == [], (
        "the generate step's own SUB_AGENT_BOUNDARY gate must escalate BEFORE "
        "ever reaching the real RuntimeSubAgentDispatcher on the initial "
        "(pausing) run"
    )

    resume_context = ResumeContext(hitl_response=_resolved_hitl_result(entry_suffix="eo-core"))
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert isinstance(resumed, RunResult)
    assert len(_captured_webhook_requests) == 1, (
        f"expected the generate step's own gate to consume the delivered "
        f"answer (NO re-escalation, still 1 webhook POST total); got "
        f"{len(_captured_webhook_requests)} POST(s) — a 2nd POST would mean "
        f"the delivery-cell wiring regressed and the gate re-fired instead "
        f"of consuming the resolved response"
    )
    assert len(sub_agent_dispatcher_calls) == 1, (
        f"expected the real RuntimeSubAgentDispatcher to be reached exactly "
        f"once — the generate step's own gate consumed the delivered answer "
        f"and let the dispatch through; got {len(sub_agent_dispatcher_calls)} "
        f"dispatcher call(s)"
    )
    assert resumed.pause_snapshot is not None, (
        "expected the re-pause to carry a fresh, resumable pause_snapshot — "
        "status='paused' with pause_snapshot=None would mean the run "
        "silently became unresumable"
    )
    assert resumed.workflow_id == paused.workflow_id, (
        "expected the re-paused run to preserve its workflow identity across the resume cycle"
    )
    assert resumed.pause_snapshot.pause_reason is WorkflowPauseReason.EXPLICIT_OPERATOR, (
        f"expected the SECOND pause to be an ORDINARY step outcome "
        f"(EXPLICIT_OPERATOR) — the separate, pre-existing child-dispatch-shape "
        f"issue this module's docstring documents — NOT a re-fired HITL gate "
        f"(HITL_PENDING), which would mean the B-78 fix regressed; got "
        f"pause_reason={resumed.pause_snapshot.pause_reason!r}"
    )


# ---------------------------------------------------------------------------
# Test 3 — DECENTRALIZED_HANDOFF reachability: the identical fix, applied to
# a stage-based topology instead of a generate/evaluate loop.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dh_stage_own_gate_pauses_and_resumes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """Confirms DH's `SUB_AGENT_DISPATCH`-stage gate is genuinely REACHABLE
    (contrary to `_execute_decentralized_handoff`'s own docstring design-intent
    note that stages are "NEVER SUB_AGENT_DISPATCH" — that note is NOT
    code-enforced) and that the identical two-gap fix applies: the stage's own
    `SUB_AGENT_BOUNDARY` gate pauses cleanly on first dispatch, and a resumed
    answer is consumed (not re-escalated) rather than re-firing.
    """
    anthropic_client = _SucceedingAnthropicClient()
    _install_fake_providers(monkeypatch, anthropic_client)
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    sub_agent_dispatcher_calls: list[Any] = []
    _original_dispatch = sub_agent_dispatch.RuntimeSubAgentDispatcher.dispatch

    def _spying_dispatch(self: Any, *args: Any, **kwargs: Any) -> Any:
        sub_agent_dispatcher_calls.append((args, kwargs))
        return _original_dispatch(self, *args, **kwargs)

    monkeypatch.setattr(sub_agent_dispatch.RuntimeSubAgentDispatcher, "dispatch", _spying_dispatch)

    config = _config(tmp_path)
    workflow = _DecentralizedHandoffSubAgentDispatchWorkflow()

    paused = await api_run(workflow, config=config)
    assert isinstance(paused, RunResult)
    assert paused.status == "paused", (
        f"expected the stage's own SUB_AGENT_BOUNDARY gate to pause the run "
        f"on first dispatch; got status={paused.status!r} "
        f"failure_cause={paused.failure_cause!r}"
    )
    assert paused.pause_snapshot is not None
    assert paused.pause_snapshot.pause_reason is WorkflowPauseReason.HITL_PENDING, (
        f"expected the pause to be labeled HITL_PENDING; got "
        f"pause_reason={paused.pause_snapshot.pause_reason!r}"
    )
    assert len(_captured_webhook_requests) == 1, (
        f"expected exactly 1 webhook POST from the stage's own gate firing; "
        f"got {len(_captured_webhook_requests)}"
    )
    assert sub_agent_dispatcher_calls == [], (
        "the stage's own SUB_AGENT_BOUNDARY gate must escalate BEFORE ever "
        "reaching the real RuntimeSubAgentDispatcher on the initial "
        "(pausing) run"
    )

    resume_context = ResumeContext(hitl_response=_resolved_hitl_result(entry_suffix="dh-core"))
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert isinstance(resumed, RunResult)
    assert len(_captured_webhook_requests) == 1, (
        f"expected the stage's own gate to consume the delivered answer (NO "
        f"re-escalation, still 1 webhook POST total); got "
        f"{len(_captured_webhook_requests)} POST(s)"
    )
    assert len(sub_agent_dispatcher_calls) == 1, (
        f"expected the real RuntimeSubAgentDispatcher to be reached exactly "
        f"once; got {len(sub_agent_dispatcher_calls)} dispatcher call(s)"
    )
    assert resumed.workflow_id == paused.workflow_id
