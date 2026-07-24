"""U-RT-95 AC #9 — public-surface HITL resume-consume-cycle e2e (path (ii)).

Closes the FM-2-deferred gap the existing
`test_u_rt_95_hitl_pause_trigger_durable_async_full_execution_path.py` names at
its own lines 29-31 ("Paths (ii) resume-consume-cycle + (iv) webhook-exhausted
are deferred to a follow-on arc per FM-2"), per runtime plan v2.54 §2 AC #9 +
the B-39 impl-leg Codex [P2] finding on this branch: no existing test exercises
`api.resume()` through MCP, `execute_workflow`, and the REAL
`RuntimeHITLGateComposer` — the delivery-mechanism tests added this session
(`harness-cp/tests/test_workflow_driver_hitl_uniform_fallback_property4.py`)
preload a `HITLDeliveryCell` directly, at the CP-driver level, never through
the public surface.

## What this file proves

A workflow declares a `PRE_ACTION` HITL placement at `(TEAM_BINDING,
RECONCILER_LOOP)` — the C-CP-18 §18.1 `DURABLE_ASYNC` synchrony cell. Driven
through the REAL production stack:

`SOLO_DEVELOPER` was tried first and rejected empirically: `RuntimeConfig.
hitl_auto_approve_policy` defaults `solo_persona_floor_auto=True`
(`hitl_auto_approve_policy.py`), which — SOLO-scoped only — lowers the
persona-tier gate-level floor to `AUTO`; combined with the canonical
`BLAST_RADIUS_GATE_LEVEL_FLOOR[READ_ONLY] = AUTO` an INFERENCE_STEP always
resolves to (both floors already `AUTO`, `max()` composition per C-CP-19
§19.1), the gate silently auto-approves BEFORE Step 4-bis ever evaluates
synchrony class — no escalation, no pause. `TEAM_BINDING`'s persona floor is
NOT policy-overridable (`_policy_floor_overrides` in `hitl_gate_composer.py`
is `if persona_tier is not PersonaTier.SOLO_DEVELOPER: return None, None`),
so `PERSONA_TIER_GATE_LEVEL_FLOOR[TEAM_BINDING] = ASK` composes via `max()`
over the `AUTO` blast floor and the gate genuinely fires.

    api.run()/api.resume() -> in-process MCP `run_workflow` tool
    -> `harness_cp.workflow_driver.execute_workflow`
    -> `ctx.step_dispatchers[INFERENCE_STEP]`
       = SyncDispatcherFacade(RetryBreakerFallbackDispatcher(
             RuntimeHITLGateComposer(inner=bare LLM dispatcher)))

No `_FakeCtx` / `_MutableHarnessContext` shortcut anywhere in this chain. The
workflow object's `step_dispatchers` property is UNSET so the MCP tool handler
falls back to `ctx.step_dispatchers` (`lifecycle/mcp_server.py:424-429`) — the
SAME production registry bootstrap wires for every real `run_workflow` call.

Two "genuinely external" substrates are faked at their bootstrap-factory seam
(the established pattern across this suite — see `test_r300_cross_family_
fallback_e2e.py` for the provider-adapter precedent and `test_track_b_e2e.py`
AC #8 for the webhook-composer precedent):

- the Anthropic SDK leaf client (`adapter.client.messages.create`) — an LLM
  provider call, explicitly permitted to fake per the task's ground rules;
- the webhook composer's `httpx` transport + `WebhookConfig` — the v1.26
  empty-marker `materialize_webhook_delivery_composer_stage` factory binds NO
  `webhook_config` at all (FM-2-deferred; see that factory's own docstring),
  so `WebhookDeliveryComposer.deliver_webhook_for_brief` would unconditionally
  raise `RuntimeError` without this fake — this is exactly the "richer HTTP
  test-double... beyond the empty-marker v1.26 config" the deferred-path
  comment names.

Neither fake touches the CP driver, the HITL gate composer, or the resume
plumbing (`HITLDeliveryCell` / `ResumeContext.hitl_responses` /
`hitl_response_for`) — those are exactly what is under test.

## Tests

1. `test_hitl_resume_consume_cycle_reaches_composer_and_continues_past_gate` —
   pause on the DURABLE_ASYNC gate, resume via `api.resume(..., resume_context=
   ResumeContext(hitl_response=HITLResult(response=APPROVE, ...)))` — the
   UNIFORM field, since this is a depth-0 (not branch-scoped) pause and CP
   spec v1.106 §0's own text requires the root gate to consume `hitl_response`
   directly (`hitl_responses` addresses only recursively-dispatched children —
   codex round-4 [P2]) — assert the run reaches SUCCESS (continues past the
   gate), the fake Anthropic
   adapter's `create()` was invoked exactly once (proving `_dispatch_inner` —
   i.e. the REAL post-gate dispatch — fired, not a silent auto-approve), and
   exactly one webhook POST was captured across the whole run (the initial
   pause escalation; NOT a second one on resume — proves the resumed step
   short-circuited at composer Step 0 instead of re-firing the gate).

2. `test_hitl_resume_without_resolved_response_repauses` — a negative control:
   resuming the SAME paused run with an EMPTY `ResumeContext()` (no resolved
   value) re-pauses (2 webhook POSTs total: initial + re-escalation), proving
   test 1's SUCCESS is driven by the delivered value, not by some ambient
   auto-continue behaviour.

3. `test_hitl_resume_same_cycle_retry_does_not_resupply_resolved_value` — U-RT-
   94 AC #7's retry-replay guard, end-to-end. On resume, the fake Anthropic
   adapter's `create()` raises a plain transient `Exception` on its first
   (only) call — classified `TRANSIENT_RETRY` by `_classify_provider_exception`
   — so `RetryBreakerFallbackDispatcher` (which wraps the WHOLE composer:
   `ctx.llm_dispatcher = materialize_retry_breaker_fallback_dispatcher_stage
   (inner=hitl_inference, ...)`) retries by invoking `RuntimeHITLGateComposer.
   dispatch()` a SECOND time within the SAME resume cycle, over the SAME
   `step_context` (and thus the SAME one-shot `HITLDeliveryCell`). AC #7
   requires the mechanism NOT re-supply the already-consumed value on this
   second call — the composer's Step 0 sees `consume_and_clear()` return
   `None` and "falls through to the normal fire path" (§14.8.8.1 step 4-bis,
   DURABLE_ASYNC), i.e. it re-escalates via the webhook composer and raises
   `HITLPauseRequestedSignal` again (a `BaseException`, so it propagates past
   the retry loop's `except Exception` untouched, straight to the driver's
   outer pause-capture handler). Final status is PAUSED (re-paused), NOT
   SUCCESS; the mutation this proves load-bearing against is "unconditionally
   re-supply the same resolved value on every dispatch attempt" (the
   'falsified bare parameter' design named at plan v2.54 §1 AC #7) — under
   that mutation, attempt 2 would see the SAME APPROVE value again and route
   straight to `_dispatch_inner`, which (since the fake only fails on its
   first-ever call) would then run cleanly and complete the run — SUCCESS,
   not PAUSED. Assertions: final status PAUSED, exactly 2 webhook POSTs
   (initial pause + retry re-escalation), and the fake adapter's `create()`
   called exactly once (attempt 2 never reaches `_dispatch_inner` at all).

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
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_cp.workflow_manifest_entry import WorkflowManifestEntry
from harness_is.path_class_registry import PathClass
from harness_runtime.api import RunResult, resume
from harness_runtime.api import run as api_run
from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
from harness_runtime.bootstrap import stage_5_loop_init as _stage_5_mod
from harness_runtime.lifecycle.pause_resume_protocol_types import (
    PauseResumeProtocolConfig,
)
from harness_runtime.lifecycle.providers import ProviderClientsStage
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
_WORKFLOW_ID = "wf-u-rt-95-hitl-resume-consume-cycle-e2e"

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


# ---------------------------------------------------------------------------
# Config + workflow — TEAM_BINDING x RECONCILER_LOOP = DURABLE_ASYNC cell per
# C-CP-18 §18.1 (persona_engine_hitl_matrix.py), so the PRE_ACTION gate
# escalates to the webhook composer instead of the sync-blocking ctx.elicit
# path (avoids needing an in-process MCP-client elicitation callback at all).
# SOLO_DEVELOPER was tried and empirically rejected — see the module
# docstring's `hitl_auto_approve_policy` note.
# ---------------------------------------------------------------------------


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
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
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


class _Workflow:
    """A single-step INFERENCE_STEP workflow with a manifest-declared
    PRE_ACTION placement at the DURABLE_ASYNC (TEAM_BINDING,
    RECONCILER_LOOP) cell.

    `step_dispatchers` is deliberately NOT declared as a property — the MCP
    tool handler's `getattr(workflow, "step_dispatchers", None)` fallback
    (`lifecycle/mcp_server.py:424`) then resolves to `ctx.step_dispatchers`,
    the REAL production registry (the whole point of this file: exercise the
    production-wired `RuntimeHITLGateComposer`, not a hand-built stand-in).
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
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(HITLPlacement(position=HITLPlacementKind.PRE_ACTION),),
            per_step_overrides={},
        )

    @property
    def steps(self) -> Sequence[WorkflowStep]:
        return (
            WorkflowStep(
                step_id=StepID("step-0"),
                step_kind=StepKind.INFERENCE_STEP,
                step_payload={
                    "messages": [{"role": "user", "content": "Say 'a'"}],
                    "tools": [],
                    "params": {"max_tokens": 4},
                },
            ),
        )

    @property
    def default_model_binding(self) -> ModelBinding:
        return ModelBinding(provider="anthropic", model="claude-haiku-4-5")


# ---------------------------------------------------------------------------
# Fake Anthropic SDK leaf client (the "genuinely external LLM provider call"
# per the task's ground rules) — mirrors the `_FakeAdapter` /
# `_SucceedingOpenAIClient` shape from `test_r300_cross_family_fallback_e2e.py`,
# adapted for the Anthropic `client.messages.create(...)` leaf.
# ---------------------------------------------------------------------------


class _FakeAnthropicUsage:
    input_tokens = 5
    output_tokens = 3


class _FakeAnthropicResponse:
    def __init__(self, model: str) -> None:
        self.id = "msg-fake-hitl-resume-e2e"
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
    """Always succeeds; records every `create(...)` call's kwargs."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, *, model: str, **kwargs: Any) -> _FakeAnthropicResponse:
        self.calls.append({"model": model, **kwargs})
        return _FakeAnthropicResponse(model)


class _SucceedingAnthropicClient:
    def __init__(self) -> None:
        self.messages = _SucceedingAnthropicMessages()


class _AlwaysRaisingAnthropicMessages:
    """Every `create(...)` call raises a plain transient `Exception` —
    `_classify_provider_exception` (retry_breaker_fallback.py) maps a bare
    `Exception` with no `.status_code` to `TRANSIENT_RETRY`, driving
    `RetryBreakerFallbackDispatcher`'s per-candidate retry loop."""

    def __init__(self) -> None:
        self.call_count = 0

    async def create(self, *, model: str, **kwargs: Any) -> Any:
        self.call_count += 1
        _ = kwargs
        raise RuntimeError(
            f"simulated transient anthropic dispatch failure for model {model!r} "
            "(U-RT-94 AC #7 same-cycle retry-replay probe)"
        )


class _RaisingAnthropicClient:
    def __init__(self) -> None:
        self.messages = _AlwaysRaisingAnthropicMessages()


class _FakeAdapter:
    """Provider adapter shape the C-RT-15 bare dispatcher consumes
    (`adapter.client.messages.create`); mirrors `test_r300_cross_family_
    fallback_e2e.py::_FakeAdapter`."""

    def __init__(self, name: str, client: Any) -> None:
        self.name = name
        self.client = client
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class _FakeProvider:
    """Bare placeholder for the non-anthropic provider slots (never
    dispatched — the fallback chain has no same/cross-family candidates)."""

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
    """`get_tracer`-capable fake — `api.run`/`api.resume` build `ctx`
    internally so there is no post-bootstrap patch point (mirrors
    `test_r_cc_1_api_resume.py::_FakeTracerProvider`)."""

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        _ = timeout_millis
        return True

    def shutdown(self) -> None:
        return None

    def get_tracer(self, instrumenting_module_name: str, /) -> object:
        from opentelemetry.trace import NoOpTracer

        _ = instrumenting_module_name
        return NoOpTracer()


# ---------------------------------------------------------------------------
# Webhook composer fake — the v1.26 empty-marker
# `materialize_webhook_delivery_composer_stage` factory (bootstrap/factories/
# webhook_delivery_composer_factory.py) binds NO `webhook_config` at all
# (FM-2-deferred per its own docstring), so a real DURABLE_ASYNC escalation
# would unconditionally raise `RuntimeError` from `deliver_webhook_for_brief`
# without this fake. Patched at the SAME seam `test_r300_cross_family_
# fallback_e2e.py` patches provider construction — the bootstrap factory
# import site inside `stage_5_loop_init.py` — so the REAL
# `RuntimeHITLGateComposer` still receives a REAL `WebhookDeliveryComposer`
# instance (only its HTTP transport + config are faked, mirroring
# `test_track_b_e2e.py` AC #8's post-bootstrap `object.__setattr__` technique,
# adapted to a pre-bootstrap factory patch since `api.run`/`api.resume` do not
# expose the `ctx` between bootstrap and execute).
# ---------------------------------------------------------------------------


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
                webhook_id="u-rt-95-resume-e2e-hook",
                endpoint_url="https://u-rt-95-resume-e2e.invalid/hook",
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
        timestamp="2026-07-24T00:00:00Z",
        audit_ledger_entry_id=EntryID(f"e-u-rt-95-resume-{entry_suffix}"),
        response_summary_hash="a" * 64,
    )


# ---------------------------------------------------------------------------
# Test 1 — the AC #9 core scenario.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hitl_resume_consume_cycle_reaches_composer_and_continues_past_gate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """A workflow paused on the workflow-layer DURABLE_ASYNC HITL gate, resumed
    via the PUBLIC `api.resume()` surface with a `resume_context` carrying a
    resolved `HITLResult` keyed by the paused run's own `run_id`
    (`ResumeContext.hitl_responses` / `hitl_response_for`, CP spec v1.106 §0),
    reaches `RuntimeHITLGateComposer.dispatch()`'s Step 0 consume and the
    workflow continues past the gate to SUCCESS — production `run_bootstrap` +
    `execute_workflow` + the REAL composer, no shortcuts.
    """
    _install_fake_providers(monkeypatch, _SucceedingAnthropicClient())
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    config = _config(tmp_path)
    workflow = _Workflow()

    # ---- "Pause" — a real run through api.run() hits the DURABLE_ASYNC cell,
    # escalates to the (faked-transport) webhook composer, and PAUSES.
    paused = await api_run(workflow, config=config)
    assert isinstance(paused, RunResult)
    assert paused.status == "paused", (
        f"expected the DURABLE_ASYNC PRE_ACTION gate to pause the run; got "
        f"status={paused.status!r} failure_cause={paused.failure_cause!r}"
    )
    assert paused.pause_snapshot is not None
    assert paused.pause_snapshot.pause_reason == WorkflowPauseReason.HITL_PENDING, (
        f"expected a workflow-layer HITL_PENDING pause; got {paused.pause_snapshot.pause_reason!r}"
    )
    assert len(_captured_webhook_requests) == 1, (
        f"expected exactly 1 webhook POST from the initial pause escalation; "
        f"got {len(_captured_webhook_requests)}"
    )

    # ---- "Resume" — the PUBLIC api.resume() surface. This is a depth-0 (NOT
    # branch-scoped) pause, so per CP spec v1.106 §0's own text the gate
    # always consumes the uniform `hitl_response` field directly (`hitl_
    # responses` addresses only recursively-dispatched children — codex
    # round-4 [P2]; see `test_workflow_driver_hitl_uniform_fallback_
    # property4.py::test_depth_0_root_never_consults_map_even_on_matching_
    # run_id` for the carrier-level witness of this same distinction).
    resume_context = ResumeContext(hitl_response=_resolved_hitl_result(entry_suffix="approve"))
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert isinstance(resumed, RunResult)
    assert resumed.status == "completed", (
        f"expected the resolved APPROVE response to reach the composer and "
        f"the run to continue past the gate to SUCCESS; got "
        f"status={resumed.status!r} failure_cause={resumed.failure_cause!r}"
    )
    assert resumed.pause_snapshot is None
    # The load-bearing dispatch-count mutation-probe assertion (the
    # `_dispatch_inner` reached-exactly-once claim) needs a handle on the
    # fake Anthropic client's own call count, which this test does not keep;
    # see `test_hitl_resume_consume_cycle_dispatches_inner_exactly_once`
    # immediately below for that companion assertion.


@pytest.mark.asyncio
async def test_hitl_resume_consume_cycle_dispatches_inner_exactly_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """Companion assertion to the test above, isolated because it needs a
    handle on the fake Anthropic client's own call-count (the prior test
    constructs it inline via `_install_fake_providers`). Proves
    `_dispatch_inner` — i.e. the REAL LLM dispatch behind the composer — was
    reached exactly once on the resumed step; a composer that silently
    auto-approved without dispatching, or that double-dispatched, both fail
    this assertion."""
    anthropic_client = _SucceedingAnthropicClient()
    _install_fake_providers(monkeypatch, anthropic_client)
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    config = _config(tmp_path)
    workflow = _Workflow()

    paused = await api_run(workflow, config=config)
    assert paused.status == "paused"
    assert paused.pause_snapshot is not None
    assert len(anthropic_client.messages.calls) == 0, (
        "the DURABLE_ASYNC gate must escalate BEFORE ever reaching the inner "
        "LLM dispatcher on the initial (pausing) run"
    )

    # Depth-0 pause — the uniform `hitl_response` field, not `hitl_responses`
    # (codex round-4 [P2]; see the core-scenario test above for the full note).
    resume_context = ResumeContext(
        hitl_response=_resolved_hitl_result(entry_suffix="dispatch-count")
    )
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert resumed.status == "completed", (
        f"expected SUCCESS; got status={resumed.status!r} failure_cause={resumed.failure_cause!r}"
    )
    assert len(anthropic_client.messages.calls) == 1, (
        f"expected the resumed step to reach the inner LLM dispatcher exactly "
        f"once; got {len(anthropic_client.messages.calls)} calls "
        f"({anthropic_client.messages.calls!r})"
    )
    # Still exactly 1 webhook POST total — the resume did NOT re-escalate.
    assert len(_captured_webhook_requests) == 1, (
        f"resume must consume the delivered value at composer Step 0 and "
        f"short-circuit BEFORE the gate-FIRE branch; a second webhook POST "
        f"means the resumed step re-fired the DURABLE_ASYNC escalation "
        f"instead of consuming the resolved response. got "
        f"{len(_captured_webhook_requests)}"
    )


# ---------------------------------------------------------------------------
# Test — negative control: an unresolved resume re-pauses (proves the SUCCESS
# above is driven by the delivered value, not ambient auto-continuation).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hitl_resume_without_resolved_response_repauses(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """Resuming with an EMPTY `ResumeContext()` (no `hitl_responses` /
    `hitl_response`) re-pauses — `hitl_delivery_holder` resolves to `None`, so
    the composer's Step 0 sees nothing to consume and falls through to Step 1
    (placement matching) -> Step 4-bis (DURABLE_ASYNC) -> re-escalates via the
    webhook composer and re-raises `HITLPauseRequestedSignal`. Proves the
    prior tests' SUCCESS genuinely required the delivered `HITLResult` — not
    that resume() unconditionally continues a paused workflow."""
    _install_fake_providers(monkeypatch, _SucceedingAnthropicClient())
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    config = _config(tmp_path)
    workflow = _Workflow()

    paused = await api_run(workflow, config=config)
    assert paused.status == "paused"
    assert paused.pause_snapshot is not None
    assert len(_captured_webhook_requests) == 1

    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=ResumeContext(),
        config=config,
    )

    assert resumed.status == "paused", (
        f"expected re-pause with no resolved response delivered; got "
        f"status={resumed.status!r} failure_cause={resumed.failure_cause!r}"
    )
    assert resumed.pause_snapshot is not None
    assert resumed.pause_snapshot.pause_reason == WorkflowPauseReason.HITL_PENDING
    assert len(_captured_webhook_requests) == 2, (
        f"expected a SECOND webhook POST (the re-escalation on the "
        f"unresolved resume); got {len(_captured_webhook_requests)}"
    )


# ---------------------------------------------------------------------------
# Test 2 — U-RT-94 AC #7's same-cycle retry-replay guard, end-to-end.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_hitl_resume_same_cycle_retry_does_not_resupply_resolved_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _captured_webhook_requests: list[httpx.Request],
) -> None:
    """A resumed step whose (only) inner-dispatch attempt fails transiently
    retries within the SAME resume cycle — `RetryBreakerFallbackDispatcher`
    wraps the WHOLE `RuntimeHITLGateComposer`, so a retry re-invokes
    `composer.dispatch()` a second time over the SAME `step_context` /
    `HITLDeliveryCell`. AC #7 requires the already-consumed value NOT be
    re-supplied on that second call; instead the gate "falls through to the
    normal fire path" (re-escalates + re-raises `HITLPauseRequestedSignal`,
    which is a `BaseException` and so propagates past the retry loop's
    `except Exception` untouched straight to the driver's pause-capture
    handler).

    Mutation-probe framing: reverting to "unconditionally re-supply the same
    resolved value on every dispatch attempt" (plan v2.54 §1 AC #7's
    'falsified bare parameter' design) would make attempt 2 see the SAME
    APPROVE value again and dispatch straight to `_dispatch_inner` — which,
    since the fake only ever fails, would ALSO fail there, but under a
    DIFFERENT (successful-second-call) fake it would silently complete twice.
    The assertions below pin the WITH-fix shape precisely: final status
    PAUSED (not completed), exactly 2 webhook POSTs (initial pause + retry
    re-escalation), and the fake adapter's `create()` invoked exactly once
    (attempt 2 never reaches the inner dispatcher at all — it re-escalates
    BEFORE Step 1 placement matching would even consider dispatching).
    """
    anthropic_client = _RaisingAnthropicClient()
    _install_fake_providers(monkeypatch, anthropic_client)
    _install_fake_od_stage4(monkeypatch)
    _install_fake_webhook_composer_factory(monkeypatch, _captured_webhook_requests)

    config = _config(tmp_path)
    workflow = _Workflow()

    paused = await api_run(workflow, config=config)
    assert paused.status == "paused"
    assert paused.pause_snapshot is not None
    assert len(_captured_webhook_requests) == 1
    assert anthropic_client.messages.call_count == 0

    # Depth-0 pause — the uniform `hitl_response` field, not `hitl_responses`
    # (codex round-4 [P2]; see the core-scenario test above for the full note).
    resume_context = ResumeContext(hitl_response=_resolved_hitl_result(entry_suffix="retry-replay"))
    resumed = await resume(
        workflow,
        pause_snapshot=paused.pause_snapshot,
        resume_context=resume_context,
        config=config,
    )

    assert resumed.status == "paused", (
        f"expected the same-cycle retry to RE-PAUSE (the already-consumed "
        f"value must NOT be re-supplied to the retry attempt); got "
        f"status={resumed.status!r} failure_cause={resumed.failure_cause!r}"
    )
    assert resumed.pause_snapshot is not None
    assert resumed.pause_snapshot.pause_reason == WorkflowPauseReason.HITL_PENDING

    # attempt 1 consumed the resolved value -> routed to `_dispatch_inner` ->
    # the fake's ONLY call, which raised transiently -> retry. attempt 2 sees
    # the cell already cleared -> re-escalates WITHOUT ever calling `create()`
    # again.
    assert anthropic_client.messages.call_count == 1, (
        f"expected the inner LLM dispatcher to be reached exactly once (the "
        f"first, failing attempt); a second call would mean the retry "
        f"attempt re-supplied the already-consumed resolved value and "
        f"dispatched again. got {anthropic_client.messages.call_count} calls"
    )
    assert len(_captured_webhook_requests) == 2, (
        f"expected exactly 2 webhook POSTs (the initial pause escalation + "
        f"the retry attempt's re-escalation, since the retry-replay guard "
        f"correctly did NOT re-supply the consumed value); got "
        f"{len(_captured_webhook_requests)}"
    )
