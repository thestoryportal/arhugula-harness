"""C-RT-28 §14.20 — ManagedAgentsStepDispatcher + factory unit tests (arc M).

Provider-free: a configurable fake `ManagedAgentsClientProtocol` + a real
in-memory tracer exercise the dispatcher's dispatch flow + telemetry, and the
stage-5 factory's surface-gated opt-in. The live vendor path is the separate
skipif-gated `@pytest.mark.e2e` test (surfaced vendor-gate; never auto-fired).
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import pytest
from harness_core import StepID
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind, WorkflowStep
from harness_runtime.bootstrap.factories.managed_agents_dispatcher_factory import (
    materialize_managed_agents_dispatcher_stage,
)
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.managed_agents import (
    ManagedAgentEvent,
    ManagedAgentSession,
    ManagedAgentSessionStatus,
)
from harness_runtime.lifecycle.managed_agents_dispatch import (
    ManagedAgentsConfig,
    ManagedAgentsSessionError,
    ManagedAgentsStageMaterializeError,
    ManagedAgentsStepDispatcher,
)
from harness_runtime.types import (
    CollectorConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


class _FakeClient:
    """Configurable fake `ManagedAgentsClientProtocol`.

    `retrieve_statuses` is consumed one-per-`retrieve_session` call so a test
    can model a non-terminal→terminal poll sequence; the last value repeats.
    """

    def __init__(self, *, retrieve_statuses: list[ManagedAgentSessionStatus]) -> None:
        self._statuses = retrieve_statuses
        self._retrieve_calls = 0
        self.sent: list[ManagedAgentEvent] = []

    async def create_session(
        self,
        *,
        agent_id: str,
        environment_id: str,
        title: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> ManagedAgentSession:
        _ = (title, metadata)
        return ManagedAgentSession(
            session_id="session_test",
            agent_id=agent_id,
            environment_id=environment_id,
            status=ManagedAgentSessionStatus.CREATED,
            runtime_ms=0,
            billable_seconds=0.0,
        )

    async def send_event(self, *, session_id: str, event: ManagedAgentEvent) -> ManagedAgentEvent:
        _ = session_id
        self.sent.append(event)
        return event

    async def retrieve_session(self, *, session_id: str) -> ManagedAgentSession:
        idx = min(self._retrieve_calls, len(self._statuses) - 1)
        self._retrieve_calls += 1
        return ManagedAgentSession(
            session_id=session_id,
            agent_id="agent_test",
            environment_id="env_test",
            status=self._statuses[idx],
            runtime_ms=1250,
            billable_seconds=1.25,
        )

    async def cancel_session(self, *, session_id: str) -> ManagedAgentSession:
        return ManagedAgentSession(
            session_id=session_id,
            agent_id="agent_test",
            environment_id="env_test",
            status=ManagedAgentSessionStatus.CANCELED,
            runtime_ms=1500,
            billable_seconds=1.5,
        )


def _tracer_provider() -> tuple[TracerProvider, InMemorySpanExporter]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def _step(payload: dict[str, Any]) -> WorkflowStep:
    return WorkflowStep(
        step_id=StepID("step-0"),
        step_kind=StepKind.MANAGED_AGENTS,
        step_payload=payload,
    )


_VALID_PAYLOAD = {"agent_id": "agent_test", "environment_id": "env_test"}


@pytest.mark.asyncio
async def test_dispatch_success_returns_outcome_and_emits_span() -> None:
    provider, exporter = _tracer_provider()
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.IDLE])
    dispatcher = ManagedAgentsStepDispatcher(client=cast(Any, client), tracer_provider=provider)

    out = await dispatcher.dispatch(
        cast(Any, None), _step(dict(_VALID_PAYLOAD)), step_context=cast(Any, None)
    )

    assert out["session_id"] == "session_test"
    assert out["status"] == "idle"
    assert out["runtime_ms"] == 1250
    assert out["billable_seconds"] == 1.25
    assert len(client.sent) == 1
    spans = exporter.get_finished_spans()
    assert [s.name for s in spans] == ["managed_agents.runtime"]
    assert spans[0].attributes is not None
    assert spans[0].attributes["managed_agents.session_id"] == "session_test"


@pytest.mark.asyncio
async def test_dispatch_polls_until_terminal() -> None:
    provider, _ = _tracer_provider()
    # RUNNING twice, then COMPLETED — the poll loop must advance to terminal.
    client = _FakeClient(
        retrieve_statuses=[
            ManagedAgentSessionStatus.RUNNING,
            ManagedAgentSessionStatus.RUNNING,
            ManagedAgentSessionStatus.COMPLETED,
        ]
    )
    dispatcher = ManagedAgentsStepDispatcher(client=cast(Any, client), tracer_provider=provider)
    out = await dispatcher.dispatch(
        cast(Any, None),
        _step({**_VALID_PAYLOAD, "poll_interval_seconds": 0.0}),
        step_context=cast(Any, None),
    )
    assert out["status"] == "completed"


@pytest.mark.asyncio
async def test_dispatch_failed_status_raises_session_error() -> None:
    provider, _ = _tracer_provider()
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.FAILED])
    dispatcher = ManagedAgentsStepDispatcher(client=cast(Any, client), tracer_provider=provider)
    with pytest.raises(ManagedAgentsSessionError):
        await dispatcher.dispatch(
            cast(Any, None), _step(dict(_VALID_PAYLOAD)), step_context=cast(Any, None)
        )


@pytest.mark.asyncio
async def test_dispatch_missing_input_raises_session_error() -> None:
    provider, _ = _tracer_provider()
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.IDLE])
    dispatcher = ManagedAgentsStepDispatcher(client=cast(Any, client), tracer_provider=provider)
    with pytest.raises(ManagedAgentsSessionError):
        await dispatcher.dispatch(
            cast(Any, None), _step({"agent_id": "a"}), step_context=cast(Any, None)
        )


@pytest.mark.asyncio
async def test_dispatch_poll_budget_exhausted_raises() -> None:
    provider, _ = _tracer_provider()
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.RUNNING])
    dispatcher = ManagedAgentsStepDispatcher(client=cast(Any, client), tracer_provider=provider)
    with pytest.raises(ManagedAgentsSessionError):
        await dispatcher.dispatch(
            cast(Any, None),
            _step({**_VALID_PAYLOAD, "max_poll_attempts": 2, "poll_interval_seconds": 0.0}),
            step_context=cast(Any, None),
        )


# --- factory surface-gating ---------------------------------------------------


def _config(*, surface: DeploymentSurface, managed: ManagedAgentsConfig | None) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=surface,
        repository_root=Path("/tmp/arc-m-test"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        managed_agents_config=managed,
    )


@pytest.mark.asyncio
async def test_factory_optout_returns_none() -> None:
    cfg = _config(surface=DeploymentSurface.MANAGED_CLOUD, managed=None)
    ctx = _MutableHarnessContext()
    ctx.tracer_provider = _tracer_provider()[0]
    assert await materialize_managed_agents_dispatcher_stage(cfg, ctx) is None


@pytest.mark.asyncio
async def test_factory_non_managed_cloud_returns_none() -> None:
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.IDLE])
    cfg = _config(
        surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        managed=ManagedAgentsConfig(client=client),
    )
    ctx = _MutableHarnessContext()
    ctx.tracer_provider = _tracer_provider()[0]
    # Opted-in but NOT managed-cloud → silently not bound (the AS-8f exclusion).
    assert await materialize_managed_agents_dispatcher_stage(cfg, ctx) is None


@pytest.mark.asyncio
async def test_factory_optin_managed_cloud_returns_dispatcher() -> None:
    client = _FakeClient(retrieve_statuses=[ManagedAgentSessionStatus.IDLE])
    cfg = _config(
        surface=DeploymentSurface.MANAGED_CLOUD,
        managed=ManagedAgentsConfig(client=client),
    )
    ctx = _MutableHarnessContext()
    ctx.tracer_provider = _tracer_provider()[0]
    dispatcher = await materialize_managed_agents_dispatcher_stage(cfg, ctx)
    assert isinstance(dispatcher, ManagedAgentsStepDispatcher)


@pytest.mark.asyncio
async def test_factory_managed_cloud_no_client_raises() -> None:
    cfg = _config(
        surface=DeploymentSurface.MANAGED_CLOUD,
        managed=ManagedAgentsConfig(client=None),
    )
    ctx = _MutableHarnessContext()
    ctx.tracer_provider = _tracer_provider()[0]
    with pytest.raises(ManagedAgentsStageMaterializeError):
        await materialize_managed_agents_dispatcher_stage(cfg, ctx)
