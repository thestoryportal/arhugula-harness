"""R-820 provider-free Managed Agents contract helpers.

This module opens the runtime-side Managed Agents boundary without constructing
a provider SDK client or making managed-cloud calls. It supplies:

- small provider-neutral agent session records,
- a protocol for future Anthropic Managed Agents adapters, and
- a `managed_agents.runtime` span helper carrying the AS `managed_agents.*`
  namespace.

The live session e2e remains gated on the R-820 managed-cloud arc.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

__all__ = [
    "ANTHROPIC_MANAGED_AGENTS_BETA",
    "ManagedAgentEvent",
    "ManagedAgentSession",
    "ManagedAgentSessionStatus",
    "ManagedAgentsClientProtocol",
    "managed_agents_runtime_span",
]


ANTHROPIC_MANAGED_AGENTS_BETA = "managed-agents-2026-04-01"
"""Anthropic Managed Agents beta header value used by the R-820 live path."""


class ManagedAgentSessionStatus(StrEnum):
    """Provider-neutral session lifecycle states for a managed agent run."""

    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass(frozen=True, slots=True)
class ManagedAgentSession:
    """Provider-neutral metadata for a Managed Agents session."""

    session_id: str
    agent_id: str
    environment_id: str
    status: ManagedAgentSessionStatus
    runtime_ms: int
    billable_seconds: float


@dataclass(frozen=True, slots=True)
class ManagedAgentEvent:
    """Provider-neutral event emitted to or from a Managed Agents session."""

    event_type: str
    payload: Mapping[str, Any]


class ManagedAgentsClientProtocol(Protocol):
    """Minimal async port for a future provider-backed Managed Agents adapter."""

    async def create_session(
        self,
        *,
        agent_id: str,
        environment_id: str,
        title: str | None = None,
        metadata: Mapping[str, str] | None = None,
    ) -> ManagedAgentSession: ...

    async def send_event(
        self,
        *,
        session_id: str,
        event: ManagedAgentEvent,
    ) -> ManagedAgentEvent: ...

    async def retrieve_session(self, *, session_id: str) -> ManagedAgentSession: ...

    async def cancel_session(self, *, session_id: str) -> ManagedAgentSession: ...


@asynccontextmanager
async def managed_agents_runtime_span(
    *,
    tracer: Any,
    session: ManagedAgentSession | None = None,
    session_id: str | None = None,
    runtime_ms: int | None = None,
    billable_seconds: float | None = None,
) -> AsyncGenerator[Any, None]:
    """Open a `managed_agents.runtime` span with AS namespace attributes.

    The helper accepts either a full `ManagedAgentSession` or explicit fields.
    This lets future live adapters emit metadata directly from provider session
    responses while provider-free tests can exercise telemetry without SDK calls.
    """

    resolved_session_id = session.session_id if session is not None else session_id
    resolved_runtime_ms = session.runtime_ms if session is not None else runtime_ms
    resolved_billable_seconds = (
        session.billable_seconds if session is not None else billable_seconds
    )

    with tracer.start_as_current_span("managed_agents.runtime") as span:
        if resolved_runtime_ms is not None:
            span.set_attribute("managed_agents.runtime_ms", resolved_runtime_ms)
        if resolved_session_id is not None:
            span.set_attribute("managed_agents.session_id", resolved_session_id)
        if resolved_billable_seconds is not None:
            span.set_attribute("managed_agents.billable_seconds", resolved_billable_seconds)
        yield span
