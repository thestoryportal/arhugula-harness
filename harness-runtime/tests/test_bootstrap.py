"""U-RT-43 — 9-stage bootstrap orchestrator tests (opens L9).

Acceptance criteria per Phase 2 Session 3 atomic decomposition §3.8.4:

1. Full bootstrap returns a `HarnessContext` (frozen Pydantic at stage 7).
2. Injected stage failure at each of the 9 substages triggers reverse-order rollback.
3. Each stage emits exactly one lifecycle event (buffered until emitter exists at stage 5).

Additional coverage:
- `_MutableHarnessContext.freeze()` raises `IncompleteBootstrapError` on missing field.
- `WorkflowObject` Protocol structural check passes with `workflow_id` + `workload_class`.
- `api.run` calls `run_bootstrap` with `workflow.workload_class`.
- Post-Lane-6: `api.run()` delegates to the CP workflow driver and returns a `RunResult`.
- Lifecycle event buffer drains in arrival order at stage 5.
- Rollback handlers are best-effort (one handler's exception doesn't halt others).
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.cross_family_fallback_chain import (
    FallbackChain,
    ProviderCandidate,
    ProviderFamily,
)
from harness_cp.routing_manifest_residence import RoutingManifest
from harness_cp.topology_pattern import TopologyPattern
from harness_is.path_class_registry import PathClass
from harness_runtime.bootstrap import (
    BootstrapFailure,
    BootstrapStageCompleteEvent,
    IncompleteBootstrapError,
    run_bootstrap,
)
from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.providers import ProviderClientsStage
from harness_runtime.types import (
    BootstrapStage,
    CollectorConfig,
    HarnessContext,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)

# ---------------------------------------------------------------------------
# Fixtures.
# ---------------------------------------------------------------------------


_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_SURFACE = DeploymentSurface.LOCAL_DEVELOPMENT


def _path_bindings(tmp_path: Path) -> PathBindingConfig:
    """All 4 PathClass entries under `tmp_path` for stage 1 IS."""
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


def _config(tmp_path: Path) -> RuntimeConfig:
    """Minimal valid `RuntimeConfig` for bootstrap tests."""
    return RuntimeConfig(
        deployment_surface=_SURFACE,
        repository_root=tmp_path,
        path_bindings=_path_bindings(tmp_path),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        ollama_optional=True,
        routing_manifest=RoutingManifest(
            manifest_version=1,
            per_role_bindings={},
            per_workload_overrides={},
            fallback_chains=(_CHAIN,),
            retry_policies={},
        ),
    )


class _FakeProvider:
    """Minimal `ProviderClient` Protocol implementation for tests."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


def _patch_providers(monkeypatch: pytest.MonkeyPatch) -> dict[str, _FakeProvider]:
    """Replace `materialize_provider_clients_stage` with a no-op fake."""
    fakes = {
        "anthropic": _FakeProvider("anthropic"),
        "openai": _FakeProvider("openai"),
        "ollama": _FakeProvider("ollama"),
    }

    async def _fake(*_args: object, **_kwargs: object) -> ProviderClientsStage:
        return ProviderClientsStage(providers=dict(fakes))

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_3a_cp_clients.materialize_provider_clients_stage",
        _fake,
    )
    return fakes


class _FakeDaemon:
    """In-process collector daemon stub — records start/stop calls."""

    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True


def _patch_collector(monkeypatch: pytest.MonkeyPatch) -> _FakeDaemon:
    """Replace stage 4's collector materialization + ring buffer + tracer
    with no-op fakes. Tracer must not globally register (one-time-per-process
    invariant per C-RT-06 forbids repeated `set_tracer_provider`)."""
    daemon = _FakeDaemon()

    class _Stage:
        def __init__(self, d: _FakeDaemon) -> None:
            self.daemon = d

    class _TracerStage:
        def __init__(self) -> None:
            class _P:
                pass

            self.provider = _P()
            self.registered_globally = False

    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_collector_daemon_stage",
        lambda config, **_: _Stage(daemon),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_ring_buffer_stage",
        lambda config, _d: None,
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_: _TracerStage(),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_span_processor_stage",
        lambda config, _p, **_k: None,
    )
    return daemon


# ---------------------------------------------------------------------------
# AC #1 — Full bootstrap returns frozen HarnessContext.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bootstrap_returns_frozen_harness_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert isinstance(ctx, HarnessContext)
    assert ctx.model_config["frozen"] is True


@pytest.mark.asyncio
async def test_bootstrap_writes_pidfile_at_stage_7(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """U-RT-48: stage 7 INGRESS_ACCEPT writes the pidfile per spec §13."""
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    pidfile = tmp_path / ".harness/runtime.pid"
    assert not pidfile.exists()

    await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)

    assert pidfile.is_file()
    assert pidfile.read_text().strip() == str(os.getpid())


@pytest.mark.asyncio
async def test_bootstrap_populates_every_required_harness_context_field(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    # Spot-check one field from each stage.
    assert ctx.config is not None  # stage 0
    assert ctx.path_resolver is not None  # stage 1
    assert ctx.sandbox_dispatch is not None  # stage 2
    assert ctx.mcp_host is not None  # stage 2 (U-RT-15)
    assert ctx.mcp_server is not None  # stage 2 (U-RT-62 — H_T-as-MCP-server)
    assert ctx.mcp_server.started is True  # U-RT-62 AC #2
    assert "anthropic" in ctx.providers  # stage 3a
    assert ctx.routing_manifest is not None  # stage 3b
    assert ctx.audit_writer is not None  # stage 4
    assert ctx.lifecycle_emitter is not None  # stage 5


@pytest.mark.asyncio
async def test_bootstrap_stage_5_binds_inference_and_sub_agent_dispatchers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """U-RT-59 AC #11 + U-RT-60 AC #13 (v1.11 wrap-asymmetry chain): stage 5
    binds both step kinds through the C-RT-18 wrap chain.

    Verifies the post-U-RT-60-wrap-asymmetry-fork-APPLIED stage 5 wiring per
    ``.harness/class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md``
    §7.2 Q1 materialized chain:

    Row 1 (INFERENCE_STEP):
        bare C-RT-15 → HITL(PRE_ACTION) → C-RT-16 retry → SyncDispatcherFacade

    Row 2 (SUB_AGENT_DISPATCH):
        bare C-RT-17 sub_agent_dispatcher → HITL(SUB_AGENT_BOUNDARY)
          → SyncDispatcherFacade

    AC #13 stage-5 post-condition:
    - ``ctx.step_dispatchers`` is a populated ``StepKindDispatcherRegistry``.
    - ``INFERENCE_STEP`` resolves to a ``SyncDispatcherFacade`` wrapping
      ``ctx.llm_dispatcher`` (the C-RT-16 wrapper) whose ``inner`` is
      a ``RuntimeHITLGateComposer`` with
      ``applicable_placements={PRE_ACTION}``.
    - ``SUB_AGENT_DISPATCH`` resolves to a ``SyncDispatcherFacade`` wrapping
      a ``RuntimeHITLGateComposer`` with
      ``applicable_placements={SUB_AGENT_BOUNDARY}`` whose ``inner`` is the
      bare ``RuntimeSubAgentDispatcher``.
    - ``ctx.sub_agent_dispatcher`` is the row-2 HITL composer (field type
      widened from sync ``_CpStepDispatcher`` to async ``Any`` per fork
      §7.2 Q3 ratification).
    - ``ctx.ask_user_question_surface`` is bound to a
      ``MCPBackedAskUserQuestionSurface`` per spec §14.8.3 v1.11 pin.
    - The 3 unbound step kinds (TOOL / HITL / DECLARATIVE) raise
      ``StepKindDispatcherNotBoundError`` on lookup per registry contract.
    """
    from harness_cp.hitl_placement import HITLPlacementKind
    from harness_cp.workflow_driver_types import StepKind
    from harness_runtime.lifecycle.hitl_gate_composer import (
        RuntimeHITLGateComposer,
    )
    from harness_runtime.lifecycle.mcp_backed_ask_user_question_surface import (
        MCPBackedAskUserQuestionSurface,
    )
    from harness_runtime.lifecycle.step_dispatchers import (
        StepKindDispatcherNotBoundError,
    )
    from harness_runtime.lifecycle.sub_agent_dispatch import (
        RuntimeSubAgentDispatcher,
    )
    from harness_runtime.lifecycle.sync_dispatcher_facade import (
        SyncDispatcherFacade,
    )

    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)

    assert ctx.step_dispatchers is not None

    # AC #13: ask_user_question_surface bound to MCP-backed concrete impl.
    assert isinstance(ctx.ask_user_question_surface, MCPBackedAskUserQuestionSurface)

    # AC #13 row 1: SyncDispatcherFacade(C-RT-16(HITL(PRE_ACTION)(bare C-RT-15)))
    inference_dispatcher = ctx.step_dispatchers.lookup(StepKind.INFERENCE_STEP)
    assert isinstance(inference_dispatcher, SyncDispatcherFacade)
    assert inference_dispatcher.inner is ctx.llm_dispatcher
    assert inference_dispatcher.result_timeout_seconds == ctx.config.drain_timeout_seconds
    # ctx.llm_dispatcher.inner is the PRE_ACTION HITL composer per the wrap chain
    hitl_inference = ctx.llm_dispatcher.inner  # type: ignore[attr-defined]
    assert isinstance(hitl_inference, RuntimeHITLGateComposer)
    assert hitl_inference.applicable_placements == frozenset(
        {HITLPlacementKind.PRE_ACTION}
    )

    # AC #13 row 2: SyncDispatcherFacade(HITL(SUB_AGENT_BOUNDARY)(bare sub_agent))
    sub_agent_step = ctx.step_dispatchers.lookup(StepKind.SUB_AGENT_DISPATCH)
    assert isinstance(sub_agent_step, SyncDispatcherFacade)
    # Field-type-widened ctx.sub_agent_dispatcher is the HITL composer (not
    # the bare sub-agent dispatcher) per fork §7.2 Q3 ratification.
    assert isinstance(ctx.sub_agent_dispatcher, RuntimeHITLGateComposer)
    assert ctx.sub_agent_dispatcher.applicable_placements == frozenset(
        {HITLPlacementKind.SUB_AGENT_BOUNDARY}
    )
    assert isinstance(
        ctx.sub_agent_dispatcher.inner, RuntimeSubAgentDispatcher
    )
    assert sub_agent_step.inner is ctx.sub_agent_dispatcher

    for unbound in (StepKind.TOOL_STEP, StepKind.HITL_STEP, StepKind.DECLARATIVE_STEP):
        with pytest.raises(StepKindDispatcherNotBoundError):
            ctx.step_dispatchers.lookup(unbound)


# ---------------------------------------------------------------------------
# AC #3 — Each stage emits exactly one lifecycle event (9 total).
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_bootstrap_emits_nine_lifecycle_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    emitted = ctx.lifecycle_emitter.emitted_bootstrap_stages  # type: ignore[attr-defined]
    assert len(emitted) == 9


@pytest.mark.asyncio
async def test_bootstrap_emits_events_in_canonical_stage_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    emitted = ctx.lifecycle_emitter.emitted_bootstrap_stages  # type: ignore[attr-defined]
    assert list(emitted) == list(BootstrapStage)


# ---------------------------------------------------------------------------
# AC #2 — Rollback at each stage failure.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_failure_at_stage_0_raises_bootstrap_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 0 boom")

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_0_preamble.execute",
        _boom,
    )
    with pytest.raises(BootstrapFailure) as excinfo:
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert excinfo.value.failed_stage is BootstrapStage.PREAMBLE
    assert isinstance(excinfo.value.cause, RuntimeError)


@pytest.mark.asyncio
async def test_failure_at_stage_1_rolls_back_stage_0(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage 1 failure → rollback handler for stage 0 invoked."""
    rollback_calls: list[BootstrapStage] = []

    from harness_runtime.bootstrap import _rollback_preamble  # type: ignore[attr-defined]

    async def _rec_rollback_preamble(ctx: Any) -> None:
        rollback_calls.append(BootstrapStage.PREAMBLE)
        await _rollback_preamble(ctx)

    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 1 boom")

    import harness_runtime.bootstrap as _boot

    monkeypatch.setattr(
        "harness_runtime.bootstrap._ROLLBACK_HANDLERS",
        {**_boot._ROLLBACK_HANDLERS, BootstrapStage.PREAMBLE: _rec_rollback_preamble},
    )
    monkeypatch.setattr("harness_runtime.bootstrap.stage_1_is.execute", _boom)
    with pytest.raises(BootstrapFailure):
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert rollback_calls == [BootstrapStage.PREAMBLE]


@pytest.mark.asyncio
async def test_failure_at_stage_3a_closes_already_constructed_providers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage 3a failure after partial provider construction → close those providers."""
    # Construct fakes via patch; then arrange stage 3b to fail; rollback should
    # close all providers since their stage completed before the failure.
    fakes = _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)

    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 3b boom")

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_3b_cp_routing.execute",
        _boom,
    )
    with pytest.raises(BootstrapFailure) as excinfo:
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert excinfo.value.failed_stage is BootstrapStage.CP_ROUTING
    # All 3 providers closed (best-effort rollback).
    assert all(p.closed for p in fakes.values())


@pytest.mark.asyncio
async def test_failure_at_stage_5_stops_collector_daemon(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stage 5 failure → stage 4 rollback stops the daemon."""
    _patch_providers(monkeypatch)
    daemon = _patch_collector(monkeypatch)

    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 5 boom")

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_5_loop_init.execute",
        _boom,
    )
    with pytest.raises(BootstrapFailure) as excinfo:
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert excinfo.value.failed_stage is BootstrapStage.LOOP_INIT
    assert daemon.stopped is True


@pytest.mark.asyncio
async def test_stage_0_failure_skips_rollback_entirely(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If stage 0 fails, no stage completed → no rollback handlers called."""
    rollback_calls: list[BootstrapStage] = []

    import harness_runtime.bootstrap as boot

    original_handlers = boot._ROLLBACK_HANDLERS  # type: ignore[attr-defined]

    async def _record(stage: BootstrapStage, ctx: Any) -> None:
        rollback_calls.append(stage)

    monkeypatch.setattr(
        boot,
        "_ROLLBACK_HANDLERS",
        {s: (lambda c, _s=s: _record(_s, c)) for s in original_handlers},
    )

    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 0 boom")

    monkeypatch.setattr("harness_runtime.bootstrap.stage_0_preamble.execute", _boom)
    with pytest.raises(BootstrapFailure):
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    assert rollback_calls == []


@pytest.mark.asyncio
async def test_rollback_continues_when_handler_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A raising rollback handler does not halt later handlers in the reverse order."""
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)

    handler_calls: list[BootstrapStage] = []

    import harness_runtime.bootstrap as boot

    async def _failing(ctx: Any) -> None:
        handler_calls.append(BootstrapStage.AS)
        raise RuntimeError("rollback handler failure")

    async def _ok_is(ctx: Any) -> None:
        handler_calls.append(BootstrapStage.IS)

    async def _ok_preamble(ctx: Any) -> None:
        handler_calls.append(BootstrapStage.PREAMBLE)

    patched = dict(boot._ROLLBACK_HANDLERS)  # type: ignore[attr-defined]
    patched[BootstrapStage.PREAMBLE] = _ok_preamble
    patched[BootstrapStage.IS] = _ok_is
    patched[BootstrapStage.AS] = _failing
    monkeypatch.setattr(boot, "_ROLLBACK_HANDLERS", patched)

    async def _boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("stage 3a boom")

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_3a_cp_clients.execute",
        _boom,
    )
    with pytest.raises(BootstrapFailure):
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    # Order is reverse: AS (raises) → IS → PREAMBLE.
    assert handler_calls == [
        BootstrapStage.AS,
        BootstrapStage.IS,
        BootstrapStage.PREAMBLE,
    ]


# ---------------------------------------------------------------------------
# _MutableHarnessContext + freeze.
# ---------------------------------------------------------------------------


def test_freeze_raises_incomplete_when_required_field_none() -> None:
    ctx = _MutableHarnessContext()
    with pytest.raises(IncompleteBootstrapError) as excinfo:
        ctx.freeze()
    # All 32 required fields are missing (U-RT-52 +1 for `llm_dispatcher`;
    # U-RT-59 +2 for `sub_agent_dispatcher` + `step_dispatchers`;
    # U-RT-60 +1 for `ask_user_question_surface`).
    assert "config" in excinfo.value.missing_fields
    assert "lifecycle_emitter" in excinfo.value.missing_fields
    assert "ledger_reader" in excinfo.value.missing_fields
    assert "llm_dispatcher" in excinfo.value.missing_fields
    assert "sub_agent_dispatcher" in excinfo.value.missing_fields
    assert "step_dispatchers" in excinfo.value.missing_fields
    assert "ask_user_question_surface" in excinfo.value.missing_fields
    assert len(excinfo.value.missing_fields) == 32


def test_bootstrap_stage_complete_event_is_frozen() -> None:
    event = BootstrapStageCompleteEvent(stage=BootstrapStage.PREAMBLE)
    with pytest.raises(Exception):  # noqa: B017 — Pydantic frozen-violation
        event.stage = BootstrapStage.IS  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Lifecycle-event buffering discipline.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_events_for_stages_0_to_4_buffered_until_stage_5(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stages 0-4 complete before the emitter exists; events buffer."""
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)

    # Stop bootstrap right after stage 4 by injecting a stage-5 failure;
    # capture the pending buffer state via the orchestrator's internal stash.
    # We intercept via a stage_5 wrapper that records ctx state before failing.
    captured: dict[str, Any] = {}

    async def _capture_then_fail(ctx: Any, config: Any, wc: Any) -> None:
        captured["stages_completed_pre_emit"] = list(ctx.completed_stages)
        captured["emitter_present"] = ctx.lifecycle_emitter is not None
        raise RuntimeError("stop here")

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_5_loop_init.execute",
        _capture_then_fail,
    )
    with pytest.raises(BootstrapFailure):
        await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    # At the moment LOOP_INIT (BootstrapStage value 6) began, stages 0-5
    # (PREAMBLE..OD = 6 stages) had completed but the emitter did not yet
    # exist (LOOP_INIT had not populated it).
    assert captured["emitter_present"] is False
    assert len(captured["stages_completed_pre_emit"]) == 6


@pytest.mark.asyncio
async def test_buffered_events_flush_in_arrival_order_at_stage_5(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When LOOP_INIT (stage 6) completes, buffered events 0..6 flush in order."""
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    ctx = await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    emitted = ctx.lifecycle_emitter.emitted_bootstrap_stages  # type: ignore[attr-defined]
    # The first 7 events were buffered through LOOP_INIT's completion (6 buffered
    # while emitter was None + LOOP_INIT itself); they flush in arrival order.
    assert list(emitted[:7]) == [
        BootstrapStage.PREAMBLE,
        BootstrapStage.IS,
        BootstrapStage.AS,
        BootstrapStage.CP_CLIENTS,
        BootstrapStage.CP_ROUTING,
        BootstrapStage.OD,
        BootstrapStage.LOOP_INIT,
    ]


# ---------------------------------------------------------------------------
# api.run integration.
# ---------------------------------------------------------------------------


class _Workflow:
    """Structural `WorkflowObject` carrying the full Lane 6 property set."""

    def __init__(
        self,
        workflow_id: str = "wf-bootstrap-test",
        workload_class: WorkloadClass = _WORKLOAD,
    ) -> None:
        from harness_core.identity import StepID
        from harness_core.persona_tier import PersonaTier
        from harness_cp.cp_shared_types import ModelBinding
        from harness_cp.engine_class import EngineClass
        from harness_cp.workflow_driver_types import StepKind, WorkflowStep
        from harness_cp.workflow_manifest_entry import WorkflowManifestEntry

        self._wid = workflow_id
        self._wc = workload_class
        self._manifest = WorkflowManifestEntry(
            workflow_id=workflow_id,
            workload_class=workload_class,
            persona_tier=PersonaTier.TEAM_BINDING,
            engine_class=EngineClass.PURE_PATTERN_NO_ENGINE,
            topology_pattern=TopologyPattern.SINGLE_THREADED_LINEAR,
            layer_budgets=(),
            fallback_chain=_CHAIN,
            hitl_placements=(),
            per_step_overrides={},
        )
        self._steps = (
            WorkflowStep(
                step_id=StepID("step-0"),
                step_kind=StepKind.INFERENCE_STEP,
                step_payload={},
            ),
        )
        self._binding = ModelBinding(provider="anthropic", model="claude-haiku-4-5")

        class _Noop:
            def dispatch(self, binding: object, step: object) -> dict[str, object]:
                _ = binding, step
                return {}

        self._dispatcher = _Noop()

    @property
    def workflow_id(self) -> str:
        return self._wid

    @property
    def workload_class(self) -> WorkloadClass:
        return self._wc

    @property
    def manifest_entry(self) -> Any:
        return self._manifest

    @property
    def steps(self) -> Any:
        return self._steps

    @property
    def step_dispatcher(self) -> Any:
        return self._dispatcher

    @property
    def step_dispatchers(self) -> Any:
        # U-RT-59 (C-RT-17 §14.7.7): workflow-supplied registry overrides
        # ctx.step_dispatchers per the api.py override path. v1.6 MVP test
        # registry binds INFERENCE_STEP → workflow's noop dispatcher so the
        # test step routes through the driver.
        from harness_cp.workflow_driver_types import StepKind

        class _Reg:
            def __init__(self, kind: Any, disp: Any) -> None:
                self._kind = kind
                self._disp = disp

            def lookup(self, step_kind: Any) -> Any:
                return self._disp

        return _Reg(StepKind.INFERENCE_STEP, self._dispatcher)

    @property
    def default_model_binding(self) -> Any:
        return self._binding


@pytest.mark.asyncio
async def test_api_run_passes_workload_class_into_bootstrap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`run(workflow)` extracts `workflow.workload_class` and threads to bootstrap."""
    captured: dict[str, Any] = {}

    async def _fake_bootstrap(config: Any, *, workload_class: Any) -> None:
        captured["workload_class"] = workload_class
        return None

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(
        "harness_runtime.api._default_config",
        lambda: _config(tmp_path),
    )
    # Short-circuit the driver + shutdown — this test only verifies that
    # `run()` threads `workflow.workload_class` into bootstrap. Real
    # bootstrap-to-shutdown end-to-end is exercised in test_run_smoke.py.
    # U-RT-62 AC #5 — `api.run()` now delegates execution via the in-
    # process MCP tool path; the fake bootstrap must carry a `mcp_server`
    # namespace + the stub site moves from `asyncio.to_thread` to
    # `_invoke_run_workflow_via_in_process_mcp` per the v1.12 internal
    # layout.
    import sys
    from types import SimpleNamespace
    _shutdown_mod = sys.modules["harness_runtime.shutdown"]
    from harness_runtime import api as _api_mod
    from harness_runtime.api import run

    # Wrap the existing `_fake_bootstrap` to return a ctx carrying
    # `mcp_server` (the original captured the workload_class via closure;
    # we preserve that behavior by re-using the same captured dict).
    _original_fake_bootstrap = _fake_bootstrap

    async def _wrapped_fake_bootstrap(config: Any, *, workload_class: Any) -> Any:
        await _original_fake_bootstrap(config, workload_class=workload_class)
        return SimpleNamespace(
            mcp_server=SimpleNamespace(
                server=object(),
                _state={},
                workflow_registry={},
            )
        )

    monkeypatch.setattr(
        "harness_runtime.bootstrap.run_bootstrap", _wrapped_fake_bootstrap
    )

    async def _fake_invoke(fastmcp_server: Any, workflow_id: str) -> Any:
        _ = fastmcp_server, workflow_id
        from harness_cp.workflow_driver_types import (
            RunResult as _CpRR,
        )
        from harness_cp.workflow_driver_types import (
            RunStatus as _CpRS,
        )

        return _CpRR(
            workflow_id="wf-bootstrap-test",
            run_id="run-fake",
            status=_CpRS.SUCCESS,
            final_state={},
        )

    async def _fake_shutdown(ctx: Any, *, timeout: float = 5.0) -> Any:  # noqa: ASYNC109 — mirrors real signature
        _ = ctx, timeout
        return _shutdown_mod.ShutdownReport(
            already_shutdown=False,
            timed_out=False,
            flush=_shutdown_mod.FlushReport(
                tracer_flushed=True,
                ledger_fsynced=True,
                cost_chain_noop=True,
                timed_out=False,
                failures=(),
            ),
            failures=(),
            audit_ledger_head_hash=None,
        )

    monkeypatch.setattr(
        _api_mod, "_invoke_run_workflow_via_in_process_mcp", _fake_invoke
    )
    monkeypatch.setattr(_shutdown_mod, "shutdown", _fake_shutdown)

    result = await run(_Workflow(workload_class=WorkloadClass.RESEARCH))
    assert result.status == "completed"
    assert captured["workload_class"] is WorkloadClass.RESEARCH


@pytest.mark.asyncio
async def test_api_run_propagates_bootstrap_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing `run_bootstrap` surfaces `BootstrapFailure` through `run()`."""

    async def _fake_bootstrap(*_a: object, **_k: object) -> None:
        raise BootstrapFailure(
            failed_stage=BootstrapStage.OD,
            cause=RuntimeError("synthetic"),
        )

    monkeypatch.setattr("harness_runtime.bootstrap.run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(
        "harness_runtime.api._default_config",
        lambda: _config(tmp_path),
    )
    from harness_runtime.api import run

    with pytest.raises(BootstrapFailure):
        await run(_Workflow())


# ---------------------------------------------------------------------------
# WorkflowObject Protocol growth.
# ---------------------------------------------------------------------------


def test_workflow_object_protocol_requires_workload_class() -> None:
    """A workflow missing `workload_class` fails the structural check."""
    from harness_runtime.api import WorkflowObject

    class _Half:
        @property
        def workflow_id(self) -> str:
            return "x"

    assert not isinstance(_Half(), WorkflowObject)
    assert isinstance(_Workflow(), WorkflowObject)


# ---------------------------------------------------------------------------
# Smoke — orchestrator records emitted events on the mutable context.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_orchestrator_stages_complete_in_canonical_order(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`completed_stages` post-bootstrap matches `list(BootstrapStage)`."""
    _patch_providers(monkeypatch)
    _patch_collector(monkeypatch)
    # Pre-build the orchestrator's ctx via a wrapper around stage_7 so we can
    # snapshot it before it gets frozen out of reach.
    snapshot: dict[str, Any] = {}

    from harness_runtime.bootstrap import stage_7_ingress as _stage_7

    original = _stage_7.execute

    async def _wrap(ctx: Any, config: Any, wc: Any) -> None:
        snapshot["completed_stages"] = list(ctx.completed_stages)
        await original(ctx, config, wc)

    monkeypatch.setattr(_stage_7, "execute", _wrap)
    await run_bootstrap(_config(tmp_path), workload_class=_WORKLOAD)
    # At INGRESS_ACCEPT (stage 8) entry, stages 0-7 (PREAMBLE..CXA_WIRING =
    # 8 stages) have completed; INGRESS_ACCEPT itself has not yet appended.
    assert snapshot["completed_stages"] == list(BootstrapStage)[:8]


_ = Awaitable, Callable  # silence unused-import; reserved for future helper types
