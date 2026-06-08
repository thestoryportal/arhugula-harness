"""R-820 provider-free Managed Agents contract tests."""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from harness_runtime.lifecycle.managed_agents import (
    ANTHROPIC_MANAGED_AGENTS_BETA,
    ManagedAgentEvent,
    ManagedAgentsClientProtocol,
    ManagedAgentSession,
    ManagedAgentSessionStatus,
    managed_agents_runtime_span,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)


class FakeManagedAgentsClient:
    def __init__(self) -> None:
        self.events: list[tuple[str, ManagedAgentEvent]] = []

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

    async def send_event(
        self,
        *,
        session_id: str,
        event: ManagedAgentEvent,
    ) -> ManagedAgentEvent:
        self.events.append((session_id, event))
        return ManagedAgentEvent(
            event_type="agent.message",
            payload={"text": "done", "source": event.event_type},
        )

    async def retrieve_session(self, *, session_id: str) -> ManagedAgentSession:
        return ManagedAgentSession(
            session_id=session_id,
            agent_id="agent_test",
            environment_id="environment_test",
            status=ManagedAgentSessionStatus.RUNNING,
            runtime_ms=1250,
            billable_seconds=1.25,
        )

    async def cancel_session(self, *, session_id: str) -> ManagedAgentSession:
        return ManagedAgentSession(
            session_id=session_id,
            agent_id="agent_test",
            environment_id="environment_test",
            status=ManagedAgentSessionStatus.CANCELED,
            runtime_ms=1500,
            billable_seconds=1.5,
        )


@pytest.fixture
def tracer_with_exporter() -> tuple[TracerProvider, InMemorySpanExporter]:
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider, exporter


def test_beta_header_constant_tracks_anthropic_managed_agents() -> None:
    assert ANTHROPIC_MANAGED_AGENTS_BETA == "managed-agents-2026-04-01"


@pytest.mark.asyncio
async def test_managed_agents_protocol_is_provider_free() -> None:
    client: ManagedAgentsClientProtocol = FakeManagedAgentsClient()

    created = await client.create_session(
        agent_id="agent_test",
        environment_id="environment_test",
        title="test",
        metadata={"roadmap_item": "R-820"},
    )
    assert created == ManagedAgentSession(
        session_id="session_test",
        agent_id="agent_test",
        environment_id="environment_test",
        status=ManagedAgentSessionStatus.CREATED,
        runtime_ms=0,
        billable_seconds=0.0,
    )

    response = await client.send_event(
        session_id=created.session_id,
        event=ManagedAgentEvent(event_type="user.message", payload={"text": "run"}),
    )
    assert response.event_type == "agent.message"
    assert response.payload == {"text": "done", "source": "user.message"}
    assert client.events == [
        ("session_test", ManagedAgentEvent(event_type="user.message", payload={"text": "run"}))
    ]

    retrieved = await client.retrieve_session(session_id=created.session_id)
    assert retrieved.status is ManagedAgentSessionStatus.RUNNING
    assert retrieved.runtime_ms == 1250

    canceled = await client.cancel_session(session_id=created.session_id)
    assert canceled.status is ManagedAgentSessionStatus.CANCELED


@pytest.mark.asyncio
async def test_managed_agents_runtime_span_emits_session_namespace(
    tracer_with_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    provider, exporter = tracer_with_exporter
    tracer = provider.get_tracer(__name__)
    session = ManagedAgentSession(
        session_id="session_test",
        agent_id="agent_test",
        environment_id="environment_test",
        status=ManagedAgentSessionStatus.COMPLETED,
        runtime_ms=2500,
        billable_seconds=2.5,
    )

    async with managed_agents_runtime_span(tracer=tracer, session=session):
        pass

    spans = [
        span for span in exporter.get_finished_spans() if span.name == "managed_agents.runtime"
    ]
    assert len(spans) == 1
    attrs = spans[0].attributes or {}
    assert attrs["managed_agents.runtime_ms"] == 2500
    assert attrs["managed_agents.session_id"] == "session_test"
    assert attrs["managed_agents.billable_seconds"] == 2.5


@pytest.mark.asyncio
async def test_managed_agents_runtime_span_accepts_explicit_fields(
    tracer_with_exporter: tuple[TracerProvider, InMemorySpanExporter],
) -> None:
    provider, exporter = tracer_with_exporter
    tracer = provider.get_tracer(__name__)

    async with managed_agents_runtime_span(
        tracer=tracer,
        session_id="session_test",
        runtime_ms=750,
        billable_seconds=0.75,
    ):
        pass

    spans = [
        span for span in exporter.get_finished_spans() if span.name == "managed_agents.runtime"
    ]
    assert len(spans) == 1
    attrs = spans[0].attributes or {}
    assert attrs["managed_agents.runtime_ms"] == 750
    assert attrs["managed_agents.session_id"] == "session_test"
    assert attrs["managed_agents.billable_seconds"] == 0.75
