"""MCP-server-backed `AskUserQuestionSurface` — stage 5 LOOP_INIT (U-RT-60 AC #2).

Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 H_E binding mechanism pin
(RATIFIED at HEAD `fb545ec` per c_rt_18 binding-mechanism fork Q1). Concrete
implementation of the `AskUserQuestionSurface` Protocol that satisfies the
v1.11 MVP binding contract: H_E AskUserQuestion is delivered through the
MCP server process boundary per workspace `CLAUDE.md` invariant I-4 +
`Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 ("H_E ↔ H_T substrate boundary
at MCP server process; process isolation, not convention").

**Architecture.** The surface holds an `mcp_host: MCPHost` reference
(stage-5-materialized; placeholder at this arc per `mcp_host.py:58` —
`started=False` until FastMCP transport lands) + an injectable async
delivery callback `mcp_callback`. The callback's signature matches
`AskUserQuestionSurface.ask` byte-exact — the surface is a thin adapter
that captures latency + wraps timeouts to the typed
`AskUserQuestionTimeoutError`.

**Substitution surface (H_T-CP-20).** At this arc the surface ships with a
placeholder MCP callback (`_PlaceholderMCPCallback`) that raises
`NotImplementedError` on invocation. The wire is in place; the FastMCP
transport-level handler registration is bounded substitution carry-forward
(retired RETIRE-READY at this fork APPLIED landing per AC #14 batch 8).
Operator override path: replace `mcp_callback` at construction with a
FastMCP-host-bound async callable that delivers the prompt to the operator
process + awaits their response. Tests substitute their own callback via
the same construction path.

**Per spec §14.8 deferred-list MUST-language.** A Protocol-level mock
MUST satisfy `AskUserQuestionSurface`. This concrete impl satisfies the
Protocol via `ask(prompt, options, timeout) -> AskUserQuestionResult`;
the `_PlaceholderMCPCallback` is sentinel-only and is not invoked under
test fixtures (tests inject their own callback).

**Callback-abstraction impl-discretion citation.** The injectable
`mcp_callback: MCPAskCallback` abstraction is authorized by
`Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 Q3 ratification (v1.10
introduction; preserved verbatim at v1.11): "the integration-test harness
(MCP-host-side handler fixture against the MCP-server substitution-
mechanism category per §14.8.3 v1.10 pin) **is implementation discretion**
— mechanism-specific fixture shape (e.g., `InMemoryMCPHostFixture` or
equivalent) is not pinned at v1.10 to preserve future durable-async swap
testing flexibility." The callback shape preserves the future C-RT-19 /
U-RT-61 durable-async swap surface per Q4 ratification (transparent to
the H_T runtime above this surface).

**Future durable-async swap.** Per Q4 ratification at the c_rt_18 binding-
mechanism fork: durable-async swap surface (C-RT-19 / U-RT-61) stays
inside the MCP envelope — transparent to the H_T runtime above this
surface. The surface's Protocol contract is unchanged across the swap;
only the `mcp_callback` impl changes.
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass, field

from harness_cp.hitl_response_palette import HITLResponse

from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionResult,
    AskUserQuestionTimeoutError,
)
from harness_runtime.lifecycle.mcp_host import MCPHost

__all__ = [
    "MCPAskCallback",
    "MCPBackedAskUserQuestionSurface",
    "MCPSurfaceCallbackNotBoundError",
    "materialize_mcp_backed_ask_user_question_surface_stage",
]


# Type alias for the MCP-delivery callback.
MCPAskCallback = Callable[
    [str, Sequence[HITLResponse], float | None],
    Awaitable[AskUserQuestionResult],
]
"""Async delivery callback signature: `(prompt, options, timeout) -> result`.

Bootstrap stage 5 binds `_PlaceholderMCPCallback` by default; operator-
replaceable at construction time with a FastMCP-host-bound delivery
primitive. Signature matches `AskUserQuestionSurface.ask` byte-exact so
the surface body is a thin adapter."""


class MCPSurfaceCallbackNotBoundError(NotImplementedError):
    """Default MCP callback invoked — operator did not bind a real delivery primitive.

    Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.3 binding pin: the MCP-
    backed surface's `mcp_callback` field defaults to a sentinel placeholder
    that raises this typed error on invocation. The wire is in place at
    stage 5 (composer + registry binding satisfy the Protocol contracts);
    what's deferred is the FastMCP transport-level handler registration.

    H_T-CP-20 substitution carry-forward: RETIRE-READY at the U-RT-60
    wrap-asymmetry fork APPLIED landing; the binding mechanism is pinned
    + the wrap chain is materialized; the FastMCP host wiring lands at
    a follow-on arc per Phase 7d retirement batch 8 record.
    """


class _PlaceholderMCPCallback:
    """Default MCP callback — raises `MCPSurfaceCallbackNotBoundError` on invocation.

    Sentinel placeholder bound at bootstrap stage 5 when the operator
    does not override `mcp_callback`. Tests replace with their own async
    callable; production replaces with a FastMCP-host-bound delivery
    primitive when the FastMCP host wiring arc lands.
    """

    async def __call__(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        _ = (prompt, options, timeout)
        raise MCPSurfaceCallbackNotBoundError(
            "MCPBackedAskUserQuestionSurface: no operator-bound MCP callback "
            "installed. Bootstrap stage 5 binds the sentinel placeholder per "
            "spec §14.8.3 v1.11 binding pin; the FastMCP host wiring lands "
            "at a follow-on arc per H_T-CP-20 retirement event (Phase 7d "
            "batch 8 record)."
        )


@dataclass(frozen=True)
class MCPBackedAskUserQuestionSurface:
    """AskUserQuestionSurface bound to an MCP-server-backed delivery callback.

    Satisfies `AskUserQuestionSurface` Protocol per spec §14.8.1 item 2.
    `ask(...)` delegates to `mcp_callback` + wraps `TimeoutError` (raised by
    the callback when the operator delivery deadline elapses) to the typed
    `AskUserQuestionTimeoutError` the composer step 4f catches.

    Fields
    ------
    mcp_host :
        Stage-5-materialized MCP host (placeholder at this arc per
        `mcp_host.py:58`). Field holds the reference for X-AL-1
        process-isolation discipline traceability; not invoked directly
        at v1.11 MVP (the callback layer handles transport).
    mcp_callback :
        Async delivery callback. Defaults to `_PlaceholderMCPCallback()`
        which raises `MCPSurfaceCallbackNotBoundError` on invocation.
        Tests + operator-bound production deployments replace at
        construction time.
    """

    mcp_host: MCPHost
    mcp_callback: MCPAskCallback = field(default_factory=_PlaceholderMCPCallback)

    async def ask(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        """Deliver the prompt via the MCP-backed callback + return the result.

        Wraps the callback's `TimeoutError` (Python builtin, raised by
        `asyncio.wait_for` or equivalent in the callback impl) to the
        typed `AskUserQuestionTimeoutError` the composer body catches at
        step 4f per spec §14.8.2.

        Latency capture: if the callback's returned `result.latency_ms`
        is non-positive (sentinel zero), the surface fills it from the
        wall-clock elapsed at the call site.
        """
        start = time.monotonic()
        try:
            result = await self.mcp_callback(prompt, options, timeout)
        except TimeoutError as exc:
            raise AskUserQuestionTimeoutError(
                f"MCP-backed AskUserQuestion timed out after timeout={timeout}s"
            ) from exc

        if result.latency_ms <= 0.0:
            elapsed_ms = (time.monotonic() - start) * 1000.0
            return AskUserQuestionResult(
                response=result.response,
                latency_ms=elapsed_ms,
                edited_proposal=result.edited_proposal,
                response_text=result.response_text,
                rejection_reason=result.rejection_reason,
            )
        return result


def materialize_mcp_backed_ask_user_question_surface_stage(
    mcp_host: MCPHost,
    *,
    mcp_callback: MCPAskCallback | None = None,
) -> MCPBackedAskUserQuestionSurface:
    """Construct the MCP-backed surface at bootstrap stage 5 LOOP_INIT.

    Operator override path: pass `mcp_callback=` to bind a FastMCP-host-
    bound delivery primitive. Defaults to the sentinel placeholder per
    H_T-CP-20 substitution carry-forward.
    """
    if mcp_callback is None:
        return MCPBackedAskUserQuestionSurface(mcp_host=mcp_host)
    return MCPBackedAskUserQuestionSurface(
        mcp_host=mcp_host,
        mcp_callback=mcp_callback,
    )
