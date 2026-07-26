"""B-72 reproduction — does a fan-out branch's own `SUB_AGENT_BOUNDARY` HITL gate
correctly consume a resolved operator answer on resume, or does it re-fire
regardless of resolution state?

## Why this test, and why this shape

`.harness/post-phase-8-forward-register.md` B-72 (round-2 reframe, 2026-07-25):
`HITLDeliveryCell(` is constructed exactly once codebase-wide
(`workflow_driver.py:4777`), inside `_execute_workflow_body` — the
`SINGLE_THREADED_LINEAR`-only per-step loop. No equivalent construction exists
in `_execute_parallelization`/`_execute_orchestrator_workers`/
`_execute_hierarchical_delegation`. `pause_resume_protocol_types.py`'s
`hitl_response_for` docstring states the fan-out delivery mechanism is
deliberately unspecified, deferred to CP spec section 1.3.

This test targets the MOST SURGICAL isolation of that structural gap: a
fan-out (`PARALLELIZATION`) workflow with a single branch whose step is
`SUB_AGENT_DISPATCH`, carrying its own `HITLPlacement(position=
SUB_AGENT_BOUNDARY)`. No nested/recursive child pause is needed to observe the
gap — the branch's OWN gate firing and (on resume) either consuming or
re-firing is sufficient to pin the delivery-mechanism question. This is
DELIBERATELY simpler than B-72's original "forwarding an already-paused
descendant's cursor" framing — the round-2 grounding pass found the gap is
more fundamental than that specific scenario (no `HITLDeliveryCell`-equivalent
exists for ANY fan-out branch resume, first-level or nested).

Confirms the `hitl_placements` PRODUCER reaches fan-out branches (verified via
`fold_step_hitl_placements` call sites at `workflow_driver.py:7863-7864` and
`11707-11708`, inside the `ORCHESTRATOR_WORKERS`/`PARALLELIZATION` branch
dispatch construction) — so the gate SHOULD fire correctly on first dispatch;
what's unverified until this test runs is whether a resolved answer delivered
via `api.resume(..., resume_context=...)` is consumed on the SECOND dispatch.

Mirrors `test_u_rt_95_hitl_resume_consume_cycle_e2e.py`'s real-stack pattern:
`step_dispatchers` deliberately UNSET so the MCP tool handler falls back to
`ctx.step_dispatchers`, the REAL production registry (including the REAL
`RuntimeHITLGateComposer` wrapping the sub-agent dispatcher, per
`stage_5_loop_init.py:665`'s `hitl_sub_agent` construction). Only the
Anthropic SDK leaf client and the webhook HTTP transport are faked, per the
same established pattern `test_u_rt_95` and `test_r300_cross_family_
fallback_e2e.py` use.

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
_WORKFLOW_ID = "wf-b72-fanout-sub-agent-dispatch-hitl-gate-resume"
_CHILD_WORKFLOW_ID = "child-wf-b72"

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
    return PathBindingConfig(
        raw_entries=tuple(
            {
                "path_class": pc,
                "workflow_class": _WORKLOAD,
                "deployment_surface": _SURFACE,
                "path": str(tmp_path / pc.value.lower()),
            }
            for pc in PathClass
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
        default_topology=TopologyPattern.PARALLELIZATION,
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
    ANCESTOR branch's own gate; it does not need a nested-paused-descendant
    scenario to observe the delivery-mechanism gap (see module docstring)."""
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


class _FanOutSubAgentDispatchWorkflow:
    """A `PARALLELIZATION` workflow: ONE branch, whose step is
    `SUB_AGENT_DISPATCH` carrying its own `SUB_AGENT_BOUNDARY` HITL placement
    at the `TEAM_BINDING` x `RECONCILER_LOOP` `DURABLE_ASYNC` cell (same cell
    `test_u_rt_95` uses for `PRE_ACTION` — `matrix_cell_for` is placement-
    agnostic, keyed only on `(persona_tier, engine_class)`).

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
            topology_pattern=TopologyPattern.PARALLELIZATION,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(HITLPlacement(position=HITLPlacementKind.SUB_AGENT_BOUNDARY),),
            per_step_overrides={},
        )

    @property
    def steps(self) -> Sequence[WorkflowStep]:
        return (
            WorkflowStep(
                step_id=StepID("branch-0"),
                step_kind=StepKind.SUB_AGENT_DISPATCH,
                step_payload=_sub_agent_dispatch_payload().model_dump(),
            ),
        )

    @property
    def default_model_binding(self) -> ModelBinding:
        return ModelBinding(provider="anthropic", model="claude-haiku-4-5")


# ---------------------------------------------------------------------------
# Fakes — lifted by value from `test_u_rt_95_hitl_resume_consume_cycle_e2e.py`
# (the established pattern for this exact class of real-stack test).
# ---------------------------------------------------------------------------


class _FakeAnthropicUsage:
    input_tokens = 5
    output_tokens = 3


class _FakeAnthropicResponse:
    def __init__(self, model: str) -> None:
        self.id = "msg-fake-b72-fanout"
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
                webhook_id="b72-fanout-hook",
                endpoint_url="https://b72-fanout-e2e.invalid/hook",
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
        timestamp="2026-07-25T00:00:00Z",
        audit_ledger_entry_id=EntryID(f"e-b72-fanout-{entry_suffix}"),
        response_summary_hash="a" * 64,
    )


# ---------------------------------------------------------------------------
# Test 1 — the core B-72 structural-gap assertion.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fanout_branch_own_gate_pauses_on_first_dispatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """Precondition check: the fan-out branch's own `SUB_AGENT_BOUNDARY` gate
    DOES fire on first dispatch (confirms `fold_step_hitl_placements` reaches
    fan-out branches — the producer side is NOT the gap). If this fails, the
    B-72 finding needs revisiting at an earlier point than the round-2
    reframe assumed."""
    _install_fake_providers(monkeypatch, _SucceedingAnthropicClient())
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    config = _config(tmp_path)
    workflow = _FanOutSubAgentDispatchWorkflow()

    paused = await api_run(workflow, config=config)
    assert isinstance(paused, RunResult)
    assert paused.status == "paused", (
        f"expected the fan-out branch's own SUB_AGENT_BOUNDARY gate to pause "
        f"the run on first dispatch; got status={paused.status!r} "
        f"failure_cause={paused.failure_cause!r}"
    )
    assert paused.pause_snapshot is not None
    assert paused.pause_snapshot.pause_reason is WorkflowPauseReason.HITL_PENDING, (
        # B-72 impl leg — a pre-dispatch gate-owning branch is the operator-facing
        # signal that property 6's carrier is active; this must NOT read as the
        # generic EXPLICIT_OPERATOR branch-failure pause (`workflow_driver.py`'s
        # `_pause_reason` computation was amended alongside the carrier itself).
        f"expected the first pause to be labeled HITL_PENDING (a pre-dispatch "
        f"gate-owning branch is present); got "
        f"pause_reason={paused.pause_snapshot.pause_reason!r}"
    )
    assert len(_captured_webhook_requests) == 1, (
        f"expected exactly 1 webhook POST from the branch's own gate firing; "
        f"got {len(_captured_webhook_requests)}"
    )


@pytest.mark.asyncio
async def test_fanout_branch_gate_resume_with_resolved_answer_is_consumed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """THE B-72 CORE ASSERTION — CONFIRMS THE FIX (CP spec v1.108 §1 property 6 impl leg).

    Originally pinned the CONFIRMED-BROKEN behavior directly (a delivered
    answer was silently dropped, the gate re-fired forever) rather than a
    blanket `@pytest.mark.xfail` — per out-of-family review (codex round 1 on
    the original PR): a blanket `xfail` swallows ANY failure (an unrelated
    `resume()` regression would still report `xfailed`, hiding it), and
    asserting only `resumed.status` is too weak an oracle (an implementation
    that marked the branch "completed" WITHOUT actually reaching
    `_dispatch_inner` would satisfy it). Now pins the CONFIRMED-FIXED shape
    with the SAME independent oracles, so any of them drifting is a real,
    visible failure:

    1. `len(_captured_webhook_requests) == 1` (NOT re-escalated — the branch's
       own gate consumed the delivered answer on resume instead of re-firing
       a second webhook POST).
    2. `sub_agent_dispatcher_calls` has exactly 1 entry — a DIRECT spy on
       `RuntimeSubAgentDispatcher.dispatch` (not a proxy via the Anthropic
       client). Proves the real dispatcher WAS reached this time, i.e. the
       delivered `hitl_response` unblocked the gate rather than re-pausing it.
    3. `resumed.pause_snapshot is not None` (a caller-facing dead-end — status
       'paused' with no way to resume again — would slip through the other
       assertions unnoticed).
    4. `resumed.workflow_id == paused.workflow_id` (run identity preserved
       across the resume cycle).
    5. `resumed.pause_snapshot.pause_reason == EXPLICIT_OPERATOR`, NOT
       `HITL_PENDING` — see the SEPARATE-ISSUE note below for why the run
       re-pauses a SECOND time despite the HITL gate itself being genuinely
       consumed.

    Per `ResumeContext.hitl_responses`'s own docstring, `None` (the default)
    means every gate-owning branch resolves to the uniform `hitl_response`, so
    this single-gate-owning-branch case resolves via the uniform field alone
    — CP spec v1.108 §1.1(b)'s delivery-cell construction at the fan-out
    dispatch site, threaded onto the branch's `hitl_delivery_holder` exactly
    like the LINEAR path's resume_at reconstruction.

    SEPARATE ISSUE (pre-existing, confirmed via direct empirical
    re-verification per this module's own prior guidance — "do not assume
    `status == 'completed'` without first empirically re-checking"): the
    dispatcher spy confirms `RuntimeSubAgentDispatcher.dispatch` IS reached
    (assertion 2), but the run still ends `status='paused'` a SECOND time
    (`pause_reason='explicit_operator'`, `FanOutBranchResumeState.
    terminal_status='completed'` with `output=None` — an ordinary
    ran-and-errored branch, folded through the SAME `pause` cascade-policy
    path as any other branch failure). This is a DIFFERENT, unrelated
    behavior of this test's specific child shape
    (`EngineClass.PURE_PATTERN_NO_ENGINE`, zero-content child step) —
    orthogonal to B-72's HITL delivery-mechanism gap this test targets, and
    out of scope to chase down here (exactly as this module's docstring
    anticipated before the fix landed). Assertion 5 pins that the SECOND
    pause is a genuine, ordinary branch failure (EXPLICIT_OPERATOR) and NOT
    a re-fired HITL gate (HITL_PENDING) — the discriminator that proves this
    is the separate issue, not a recurrence of the fixed one.

    NOTE (codex round 1 on the original PR, still accurate): this
    single-branch, single-gate-owning reproduction confirms + fixes the
    LIVENESS symptom (the gate now consumes a delivered answer) but does NOT
    by itself close the multi-peer keyed-addressing case (`B-72` net-position
    items (2)/(3)/(4), `B-71`-gated) — see CP spec v1.108 §1.2's own scope
    note.
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
    workflow = _FanOutSubAgentDispatchWorkflow()

    paused = await api_run(workflow, config=config)
    assert paused.status == "paused"
    assert paused.pause_snapshot is not None
    assert len(_captured_webhook_requests) == 1
    assert sub_agent_dispatcher_calls == [], (
        "the branch's own SUB_AGENT_BOUNDARY gate must escalate BEFORE ever "
        "reaching the real RuntimeSubAgentDispatcher on the initial "
        "(pausing) run"
    )

    resume_context = ResumeContext(hitl_response=_resolved_hitl_result(entry_suffix="fanout-core"))
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert isinstance(resumed, RunResult)
    assert len(_captured_webhook_requests) == 1, (
        f"expected the branch's own gate to consume the delivered answer "
        f"(NO re-escalation, still 1 webhook POST total); got "
        f"{len(_captured_webhook_requests)} POST(s) — a 2nd POST would mean "
        f"the delivery-cell wiring regressed and the gate re-fired instead "
        f"of consuming the resolved response"
    )
    assert len(sub_agent_dispatcher_calls) == 1, (
        f"expected the real RuntimeSubAgentDispatcher to be reached exactly "
        f"once — the branch's own gate consumed the delivered answer and let "
        f"the dispatch through; got {len(sub_agent_dispatcher_calls)} "
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
        f"expected the SECOND pause to be an ORDINARY branch failure "
        f"(EXPLICIT_OPERATOR) — the separate, pre-existing child-dispatch-shape "
        f"issue this module's docstring documents — NOT a re-fired HITL gate "
        f"(HITL_PENDING), which would mean the B-72 fix regressed; got "
        f"pause_reason={resumed.pause_snapshot.pause_reason!r}"
    )
