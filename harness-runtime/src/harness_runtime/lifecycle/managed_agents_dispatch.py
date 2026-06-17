"""C-RT-28 §14.20 — Managed Agents step dispatcher (R-FS-1 arc M).

Production-wiring surface over the R-820-built carrier `managed_agents.py`:
a `StepDispatcher` for `StepKind.MANAGED_AGENTS` (CP spec v1.39 §5.2/§25.2)
that executes a workflow step's body via a **vendor-run** Managed Agents
session (Anthropic `beta.sessions.*`) rather than a harness-orchestrated loop.

The dispatch is **async** (the client port is async) → it satisfies the
`AsyncStepDispatcher` Protocol and is bound to the CP driver's sync
`StepDispatcher` Protocol via `SyncDispatcherFacade` at stage 5 (the
C-RT-15 inner / C-RT-17 sub-agent precedent).

Architectural distinction from `SUB_AGENT_DISPATCH` (C-RT-17): the harness does
NOT orchestrate the agent loop here — the vendor does. No topology-admissibility
check, no `subagent.*`/`topology.*` spans, no child-manifest recursion. The
dispatcher creates the session, sends the step's event, polls to a terminal
status, emits the `managed_agents.runtime` span, and returns the outcome.

Per `Spec_Harness_Runtime_v1.md` §14.20 (C-RT-28) + the paired CP spec v1.39
`StepKind.MANAGED_AGENTS` extension (operator-ratified 2026-06-17, Option B).
"""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from harness_cp.per_step_override_evaluator import StepEffectiveBinding
from harness_cp.workflow_driver_types import StepExecutionContext, WorkflowStep

from harness_runtime.lifecycle.managed_agents import (
    ManagedAgentEvent,
    ManagedAgentsClientProtocol,
    ManagedAgentSessionStatus,
    managed_agents_runtime_span,
)

__all__ = [
    "ManagedAgentsConfig",
    "ManagedAgentsSessionError",
    "ManagedAgentsStageMaterializeError",
    "ManagedAgentsStepDispatcher",
]


# Terminal statuses (the poll loop stops on these); success subset returns a
# step output, the rest map to RT-FAIL-MANAGED-AGENTS-SESSION (§14.20.2 step 7).
_TERMINAL_STATUSES: frozenset[ManagedAgentSessionStatus] = frozenset(
    {
        ManagedAgentSessionStatus.IDLE,
        ManagedAgentSessionStatus.COMPLETED,
        ManagedAgentSessionStatus.FAILED,
        ManagedAgentSessionStatus.CANCELED,
        ManagedAgentSessionStatus.TERMINATED,
    }
)
_SUCCESS_STATUSES: frozenset[ManagedAgentSessionStatus] = frozenset(
    {ManagedAgentSessionStatus.IDLE, ManagedAgentSessionStatus.COMPLETED}
)


@dataclass(frozen=True)
class ManagedAgentsConfig:
    """Operator opt-in marker + supplied client for managed-agents dispatch.

    Presence (non-``None`` at ``RuntimeConfig.managed_agents_config``) +
    ``DeploymentSurface.MANAGED_CLOUD`` signals operator opt-in (the
    H_T-AS-8f local-development exclusion remains TRUE — the dispatcher binds
    only on managed-cloud). ``client`` is the concrete
    ``ManagedAgentsClientProtocol`` implementation (e.g.
    ``AnthropicManagedAgentsClient`` over a live SDK client), supplied
    out-of-band at the operator-controlled bootstrap site — NO credentials are
    embedded in this config. Typed ``Any`` (instead of the structural
    ``ManagedAgentsClientProtocol | None``) so Pydantic v2 schema-generation at
    ``RuntimeConfig.managed_agents_config`` introspection succeeds (the
    runtime_checkable Protocol is duck-typed at dispatch, not validated at the
    dataclass layer) — the same pattern as ``SkillActivationHookConfig.hook``.

    ``step_timeout_seconds`` is the ``SyncDispatcherFacade``
    ``result_timeout_seconds`` bound used **only** for the
    ``StepKind.MANAGED_AGENTS`` facade binding — intentionally DECOUPLED from
    the shared ``RuntimeConfig.step_dispatch_timeout_seconds`` (30s default).
    A vendor-run managed-agents session runs **minutes**, not seconds; binding
    the facade to the shared 30s bound would fire ``RT-FAIL-STEP-DISPATCH-
    TIMEOUT`` at 30s (wrong fail class) while the vendor session keeps running,
    billable, never cancelled (the abandoned coroutine's poll loop never
    reaches its cancel-on-give-up path). The default 600s must exceed the
    per-step poll budget (``max_poll_attempts × poll_interval_seconds`` +
    create/send/retrieve latency headroom); the operator sizes both together.

    Per runtime spec v1.55 §14.20.1 / §14.20.3.
    """

    client: Any = None
    step_timeout_seconds: float = 600.0


class ManagedAgentsStageMaterializeError(Exception):
    """Stage-5 factory cannot construct the managed-agents dispatcher.

    Fail class ``RT-FAIL-MANAGED-AGENTS-STAGE-MATERIALIZE`` (permanent →
    bootstrap rollback per ADR-F4 v1.1 / C-RT-02). Raised when opted-in on
    ``MANAGED_CLOUD`` but the tracer provider is unbound at stage-5 entry, the
    operator-supplied client is absent, or dispatcher construction raises.
    Per runtime spec v1.55 §14.20.4.
    """


class ManagedAgentsSessionError(Exception):
    """A managed-agents dispatch did not reach a success terminal status.

    Fail class ``RT-FAIL-MANAGED-AGENTS-SESSION`` (step-failure; NOT a
    bootstrap fail). Raised on a terminal ``FAILED`` / ``CANCELED`` /
    ``TERMINATED`` status, poll-budget exhaustion, or a missing required
    ``step_payload`` input. The CP driver maps the type name to
    ``step-failure: RT-FAIL-MANAGED-AGENTS-SESSION`` per the §14.20.4 /
    §25.3.3.4 try/except discipline (name-match per the
    ``StepDispatchTimeoutError`` precedent — harness-cp cannot import from
    harness-runtime). Per runtime spec v1.55 §14.20.4.
    """


@dataclass(frozen=True)
class ManagedAgentsStepDispatcher:
    """Async ``StepDispatcher`` for ``StepKind.MANAGED_AGENTS`` (C-RT-28).

    Constructed at bootstrap stage 5 by
    ``materialize_managed_agents_dispatcher_stage`` (§14.20.3). Holds a
    ``ManagedAgentsClientProtocol`` + the ``ctx.tracer_provider`` (typed
    ``Any`` per the C-RT-04 OTel-SDK-type-deferral pattern). Bound to the CP
    driver's sync ``StepDispatcher`` Protocol via ``SyncDispatcherFacade``.
    """

    client: ManagedAgentsClientProtocol
    tracer_provider: Any

    async def dispatch(
        self,
        binding: StepEffectiveBinding,
        step: WorkflowStep,
        *,
        step_context: StepExecutionContext,
    ) -> Mapping[str, Any]:
        """Run a managed-agents session for one ``MANAGED_AGENTS`` step.

        Per §14.20.2: read ``step_payload`` → create session → send the step
        event → poll to terminal → emit the ``managed_agents.runtime`` span →
        return the outcome mapping. Raises ``ManagedAgentsSessionError`` on a
        non-success terminal status / poll-budget exhaustion / missing input.
        """
        _ = (binding, step_context)  # not consumed by managed-agents dispatch at v1.55
        payload = step.step_payload

        agent_id = payload.get("agent_id")
        environment_id = payload.get("environment_id")
        if not agent_id or not environment_id:
            raise ManagedAgentsSessionError(
                "managed-agents step_payload requires non-empty 'agent_id' + "
                f"'environment_id' (got agent_id={agent_id!r}, "
                f"environment_id={environment_id!r})"
            )

        event = ManagedAgentEvent(
            event_type=str(payload.get("event_type", "user.message")),
            payload=dict(payload.get("event_payload", {})),
        )
        metadata_raw = payload.get("metadata")
        metadata: Mapping[str, str] | None = (
            cast("Mapping[str, str]", metadata_raw) if isinstance(metadata_raw, Mapping) else None
        )
        title_raw = payload.get("title")

        session = await self.client.create_session(
            agent_id=str(agent_id),
            environment_id=str(environment_id),
            title=str(title_raw) if title_raw is not None else None,
            metadata=metadata,
        )
        await self.client.send_event(session_id=session.session_id, event=event)

        # Bounded poll to a terminal status (§14.20.7 — budget is impl
        # discretion; defaults bound the loop; the fake client in unit tests
        # returns terminal on the first retrieve so no sleep fires).
        max_poll_attempts = max(1, int(payload.get("max_poll_attempts", 30)))
        poll_interval = float(payload.get("poll_interval_seconds", 1.0))
        reached_terminal = False
        for attempt in range(max_poll_attempts):
            session = await self.client.retrieve_session(session_id=session.session_id)
            if session.status in _TERMINAL_STATUSES:
                reached_terminal = True
                break
            if attempt + 1 < max_poll_attempts:
                await asyncio.sleep(poll_interval)

        # §14.20.5 invariant 3 — emit the managed_agents.runtime span at every
        # dispatch (success or failure), carrying the final session metadata.
        tracer = self.tracer_provider.get_tracer("harness.runtime.managed_agents")
        async with managed_agents_runtime_span(tracer=tracer, session=session):
            pass

        if not reached_terminal:
            # §14.20.2 step 4 — the session is still running server-side and
            # billable; the harness has given up waiting. Best-effort cancel to
            # avoid orphaning a billable vendor session before raising. A cancel
            # failure must NOT mask the primary (budget-exhausted) error — it is
            # the load-bearing signal — so swallow only the cancel exception.
            try:
                await self.client.cancel_session(session_id=session.session_id)
            except Exception as cancel_exc:  # best-effort cleanup on give-up
                raise ManagedAgentsSessionError(
                    f"managed-agents session {session.session_id} did not reach a "
                    f"terminal status within {max_poll_attempts} polls "
                    f"(last status={session.status.value}); the best-effort cancel "
                    f"also failed ({cancel_exc!r}) — the session may be orphaned"
                ) from cancel_exc
            raise ManagedAgentsSessionError(
                f"managed-agents session {session.session_id} did not reach a "
                f"terminal status within {max_poll_attempts} polls "
                f"(last status={session.status.value}); cancelled to avoid "
                f"orphaning a billable session"
            )
        if session.status not in _SUCCESS_STATUSES:
            raise ManagedAgentsSessionError(
                f"managed-agents session {session.session_id} terminated "
                f"non-successfully (status={session.status.value})"
            )

        return {
            "session_id": session.session_id,
            "agent_id": session.agent_id,
            "environment_id": session.environment_id,
            "status": session.status.value,
            "runtime_ms": session.runtime_ms,
            "billable_seconds": session.billable_seconds,
        }
