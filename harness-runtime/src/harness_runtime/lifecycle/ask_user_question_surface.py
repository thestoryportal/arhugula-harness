"""`AskUserQuestionSurface` H_E delivery Protocol — stage 5 LOOP_INIT (U-RT-60 AC #2).

Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.1 item 2 + §14.8.3 H_E binding
mechanism pin (RATIFIED at HEAD `fb545ec` per c_rt_18 binding-mechanism fork
Q1). The Protocol is the H_T-canonical delivery primitive for HITL gate
invocation; v1.11 binds an MCP-server-backed implementation at bootstrap stage
5 per workspace `CLAUDE.md` invariant I-4 + `Phase_7_Meta_Architecture_v1.md`
§7 X-AL-1 ("H_E ↔ H_T substrate boundary at MCP server process; process
isolation, not convention"). Post-bootstrap durable-async swap surface
preserved per future C-RT-19 / U-RT-61 arc (Q4 ratification).

**Protocol surface (single async method).** `ask(prompt, options, timeout) →
AskUserQuestionResult` — pure delivery primitive; carries no placement-specific
semantics (those live at the composer body per §14.8.2).

**v1.11 4-span shape mirroring.** `AskUserQuestionResult.latency_ms` is the
basis for `hitl.response.latency_ms` attribute on the `hitl.invocation.responded`
span per ADR-D5 v1.3 §1.8 row 3 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA[2]`.
Timeout failure is surfaced via `AskUserQuestionTimeoutError` (typed exception)
which the composer maps to opening the canonical `hitl.invocation.timed_out`
dedicated span per ADR-D5 §1.8 row 4 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA[3]`.

**Test mock discipline (v1.11 MUST-language per Q3).** A Protocol-level mock
MUST satisfy `AskUserQuestionSurface` Protocol. The queue-of-canned-results
shape (`MockAskUserQuestionSurface` at the test layer) is the reference unit-
test fixture; the integration-test MCP-host-side handler fixture is impl
discretion.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

from harness_cp.hitl_response_palette import HITLResponse
from pydantic import BaseModel, ConfigDict

__all__ = [
    "HARNESS_OPERATOR_INGRESSES",
    "AskUserQuestionHoldRequestedError",
    "AskUserQuestionResult",
    "AskUserQuestionSurface",
    "AskUserQuestionTimeoutError",
    "LoopOwnedAskUserQuestionSurface",
    "OperatorIngress",
]

OperatorIngress = Literal[
    "python", "cli-tty", "daemon-client-tty", "unattended", "unreported", "none"
]
"""Where an operator answer came from (Runtime v1.144 C5). The first four are reported
by a harness ingress; `unreported` is a reply without the field (or an MCP-native
decline/cancel) and `none` is a silent elicitation deadline. Client-reported, not
authenticated."""

HARNESS_OPERATOR_INGRESSES: frozenset[OperatorIngress] = frozenset(
    {"python", "cli-tty", "daemon-client-tty", "unattended"}
)


class AskUserQuestionTimeoutError(Exception):
    """`placement.timeout` elapsed without operator response.

    Raised by the surface when its underlying H_E delivery primitive
    (MCP-server-backed at v1.11) does not return a response within the
    requested timeout. The composer at `hitl_gate_composer.py` step 4f
    catches this and opens the canonical `hitl.invocation.timed_out` span
    + raises `HITLGateTimeoutError` mapping to `RT-FAIL-HITL-GATE-TIMEOUT`
    per `Spec_Harness_Runtime_v1.md` v1.11 §14.8 failure-mode taxonomy.

    `ingress` records who ended the wait (Runtime v1.144 C5), because this path never
    opens the responded span that would otherwise carry it.
    """

    def __init__(self, message: str, *, ingress: OperatorIngress) -> None:
        super().__init__(message)
        self.ingress: OperatorIngress = ingress


class AskUserQuestionHoldRequestedError(Exception):
    """The operator asked to hold the gate (Runtime v1.144 C3).

    Not a palette response: the composer turns it into the existing escalate-pause
    when a durable pause is bound, else an audited REJECT.
    """

    def __init__(self, *, ingress: OperatorIngress) -> None:
        super().__init__(f"operator requested hold via {ingress}")
        self.ingress: OperatorIngress = ingress


class AskUserQuestionResult(BaseModel):
    """Operator's response to a HITL gate invocation (`AskUserQuestionSurface.ask`).

    Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.1 item 2: carries the
    operator's selected `HITLResponse` + per-response optional content
    fields + response latency. Composer body at `hitl_gate_composer.py`
    step 4g + step 4h reads:

    - `response` → 4i 4-response dispatch (APPROVE / EDIT / REJECT / RESPOND)
      + `hitl.response.class` span attribute on `hitl.invocation.responded`
    - `latency_ms` → `hitl.response.latency_ms` span attribute
    - `edited_proposal` → step 4i EDIT branch payload replacement +
      `edited_proposal_hash` audit field at 8a-HITL
    - `response_text` → `response_text_hash` audit field at 8a-HITL
    - `rejection_reason` → step 4i REJECT branch + `rejection_reason_hash`
      audit field at 8a-HITL
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    response: HITLResponse
    """Operator-selected response class from the 4-response palette per
    `Spec_Control_Plane_v1_9.md` C-CP-16 §16.1."""

    latency_ms: float
    """Wall-clock latency between surface invocation and operator response,
    in milliseconds. Surfaces on `hitl.invocation.responded` per
    ADR-D5 v1.3 §1.8 row 3."""

    edited_proposal: str | None = None
    """Operator-authored replacement payload. Populated only when
    `response == HITLResponse.EDIT`."""

    response_text: str | None = None
    """Operator-authored response text. Populated only when
    `response == HITLResponse.RESPOND`."""

    rejection_reason: str | None = None
    """Operator-authored rejection reason. Populated only when
    `response == HITLResponse.REJECT`."""

    ingress: OperatorIngress = "unreported"
    """The reply's validated ingress (Runtime v1.144 C5); surfaces that do not report
    one leave it `unreported`."""


@runtime_checkable
class AskUserQuestionSurface(Protocol):
    """H_E delivery surface for HITL gate invocations at sub-phase 7b.

    Per `Spec_Harness_Runtime_v1.md` v1.11 §14.8.1 item 2: H_T-canonical
    Protocol with a single async method. Bound at bootstrap stage 5 to an
    MCP-server-backed implementation per §14.8.3 v1.11 pin (Q1 ratification).

    Implementations MUST satisfy this Protocol (`@runtime_checkable` enables
    `isinstance(impl, AskUserQuestionSurface)` introspection). v1.11 binds
    a single synchronous-from-the-composer-POV implementation; future
    durable-async swap at C-RT-19 / U-RT-61 stays inside the MCP envelope
    per Q4 ratification (transparent to H_T runtime).
    """

    async def ask(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        """Deliver a HITL gate invocation to the operator + return their response.

        Parameters
        ----------
        prompt
            Composed gate prompt per `compose_gate_prompt(placement,
            handoff_context)`. Composition shape is impl discretion at v1.11
            per spec §14.8 deferred-list.
        options
            4-response palette as a sequence of `HITLResponse` enum values
            per `Spec_Control_Plane_v1_9.md` C-CP-16 §16.1. v1.11 MVP passes
            the canonical full palette `frozenset(HITLResponse)`. (Spec
            narrative references `HITLResponseOption` — that carrier is not
            yet landed at the CP axis; v1.11 MVP uses the `HITLResponse`
            enum directly. Label-bearing option carrier is impl-discretion
            per spec §14.8 deferred-list.)
        timeout
            Operator-response deadline in seconds. `None` = no deadline (test
            fixtures); in production, set from `placement.timeout` per spec
            §14.8.2 step 4f.

        Returns
        -------
        AskUserQuestionResult
            Operator's response + per-response optional content + latency.

        Raises
        ------
        AskUserQuestionTimeoutError
            `timeout` elapsed before operator responded.
        """
        ...


@dataclass(frozen=True)
class LoopOwnedAskUserQuestionSurface:
    """`inner` answered on `loop`, whichever event loop the caller awaits from.

    The MCP session that carries an operator elicitation lives on one event loop (the
    loop running `api.run` or the daemon), and the reply is delivered to that loop. The
    CP driver fires the validator-escalation gate from its worker thread through
    `asyncio.run`, a second loop: an `ask` awaited there sends the request but never sees
    the reply, so the gate hangs until its deadline.

    [LAW:no-ambient-temporal-coupling] The owning loop is named once, at stage-5 binding,
    and every `ask` is scheduled there and awaited through a loop-safe future; which loop
    the caller happens to be on is not part of the contract. Cancelling the caller's wait
    cancels the scheduled ask.
    """

    inner: AskUserQuestionSurface
    loop: asyncio.AbstractEventLoop

    async def ask(
        self,
        prompt: str,
        options: Sequence[HITLResponse],
        timeout: float | None,
    ) -> AskUserQuestionResult:
        pending = asyncio.run_coroutine_threadsafe(
            self.inner.ask(prompt, options, timeout), self.loop
        )
        return await asyncio.wrap_future(pending)
