"""U-RT-49 — E2E bootstrap → shutdown smoke (PARTIAL-LAND).

Acceptance per session-3 atomic decomposition L11 U-RT-49 (operator-
ratified 2026-05-20 Path A — partial-land):

- LAND: green run touches each of the 9 `BootstrapStage` enum members
  (asserted via `BootstrapStageCompleteEvent` capture).
- LAND: clean shutdown leaves no resources open (`ShutdownReport.failures
  == ()`, pidfile removed, tracer + collector + providers closed).
- STRIKE: state-ledger workflow entries / collector spans / cost-attribution
  entries. All three extend `[[fork-u-rt-44-workflow-loop-drain]]` per
  `.harness/fork_u_rt_49_workflow_execution_extends_u_rt_44.md`.

Because `api.run()` raises `WorkflowExecutionNotYetLandedError` post-
bootstrap (and the executor surface is fork-bound), this test invokes the
two halves of the lifecycle directly:

1. `run_bootstrap(config, workload_class=...)` → real bootstrap; assert
   all 9 stage events captured + pidfile written.
2. `await shutdown(ctx, timeout=...)` → assert clean report + pidfile
   removed.

Fake provider + collector + tracer fixtures mirror `test_bootstrap.py`
(no network; in-process). When the CP workflow loop primitive lands,
this test extends per the fork's re-land plan.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

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
from harness_runtime.bootstrap import run_bootstrap
from harness_runtime.bootstrap import stage_4_od as _stage_4_od_mod
from harness_runtime.lifecycle.providers import ProviderClientsStage
from harness_runtime.shutdown import shutdown
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
# Fixture scaffolding (mirrors test_bootstrap.py).
# ---------------------------------------------------------------------------


_WORKLOAD = WorkloadClass.SOFTWARE_ENGINEERING
_SURFACE = DeploymentSurface.LOCAL_DEVELOPMENT

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
    def __init__(self, name: str) -> None:
        self.name = name
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class _FakeDaemon:
    def __init__(self) -> None:
        self.stopped = False

    async def start(self) -> None:
        return None

    async def stop(self, *, timeout_seconds: float = 5.0) -> None:
        _ = timeout_seconds
        self.stopped = True


class _FakeTracerProvider:
    def __init__(self) -> None:
        self.flushed = False
        self.shut_down = False

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        _ = timeout_millis
        self.flushed = True
        return True

    def shutdown(self) -> None:
        self.shut_down = True


@pytest.fixture
def _patched_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[dict[str, Any]]:
    """Patch providers + stage-4 OD + tracer with in-process fakes."""
    providers = {
        "anthropic": _FakeProvider("anthropic"),
        "openai": _FakeProvider("openai"),
        "ollama": _FakeProvider("ollama"),
    }

    async def _fake_clients(*_args: object, **_kwargs: object) -> ProviderClientsStage:
        return ProviderClientsStage(providers=dict(providers))

    monkeypatch.setattr(
        "harness_runtime.bootstrap.stage_3a_cp_clients.materialize_provider_clients_stage",
        _fake_clients,
    )

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
        lambda config, **_: _CollectorStage(daemon),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_ring_buffer_stage",
        lambda config, _d: None,
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_tracer_provider_stage",
        lambda config, **_: _TracerStage(tracer),
    )
    monkeypatch.setattr(
        _stage_4_od_mod,
        "materialize_span_processor_stage",
        lambda config, _p, **_k: None,
    )

    yield {
        "providers": providers,
        "daemon": daemon,
        "tracer": tracer,
    }


# ---------------------------------------------------------------------------
# E2E smoke.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_e2e_bootstrap_shutdown_round_trip(
    tmp_path: Path,
    _patched_runtime: dict[str, Any],
) -> None:
    """U-RT-49 happy-path: bootstrap → shutdown completes cleanly."""
    config = _config(tmp_path)

    # Phase 1: bootstrap.
    ctx = await run_bootstrap(config, workload_class=_WORKLOAD)
    assert isinstance(ctx, HarnessContext)

    # AC #1: all 9 BootstrapStage enum members emitted via lifecycle events.
    # `lifecycle_emitter` is the LifecycleEventEmitter Protocol (no
    # `emitted_bootstrap_stages` attribute); concrete is
    # `RuntimeLifecycleEventEmitter` which exposes the test-introspection
    # tuple per U-RT-43. Cast at the call site.
    from harness_runtime.lifecycle.lifecycle_emitter import (
        RuntimeLifecycleEventEmitter,
    )

    emitter = cast(RuntimeLifecycleEventEmitter, ctx.lifecycle_emitter)
    emitted: tuple[BootstrapStage, ...] = emitter.emitted_bootstrap_stages
    expected_stages = set(BootstrapStage)
    missing = expected_stages - set(emitted)
    assert not missing, f"missing bootstrap stage events: {missing}"
    assert len(emitted) == 9

    # Pidfile written at stage 7.
    pidfile = tmp_path / ".harness/runtime.pid"
    assert pidfile.is_file()

    # Phase 2: shutdown.
    report = await shutdown(ctx, timeout=5.0)

    # AC #2: clean shutdown — no failures, all resources released.
    assert report.failures == (), f"unexpected shutdown failures: {report.failures}"
    assert report.already_shutdown is False
    assert report.timed_out is False
    assert report.flush.tracer_flushed is True
    assert report.flush.ledger_fsynced is True
    # No workflow execution → audit ledger empty (struck AC).
    assert report.audit_ledger_head_hash is None

    # Pidfile removed at end of shutdown.
    assert not pidfile.exists(), "pidfile should be removed by shutdown()"

    # Resource closure verified via fake-side state.
    fakes = _patched_runtime
    assert fakes["daemon"].stopped is True
    assert fakes["tracer"].flushed is True
    assert fakes["tracer"].shut_down is True
    assert all(p.closed for p in fakes["providers"].values())


@pytest.mark.asyncio
async def test_e2e_shutdown_idempotent(
    tmp_path: Path,
    _patched_runtime: dict[str, Any],
) -> None:
    """Second shutdown returns cached report with already_shutdown=True."""
    _ = _patched_runtime
    config = _config(tmp_path)
    ctx = await run_bootstrap(config, workload_class=_WORKLOAD)

    r1 = await shutdown(ctx)
    r2 = await shutdown(ctx)

    assert r1.already_shutdown is False
    assert r2.already_shutdown is True
    # Cached body matches.
    assert r2.flush == r1.flush
    assert r2.failures == r1.failures
