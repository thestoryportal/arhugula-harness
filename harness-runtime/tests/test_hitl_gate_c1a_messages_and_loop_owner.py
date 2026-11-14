"""Every HITL gate site speaks C1a, and every ask lands on the loop that owns the session.

Runtime v1.144 C1a: the operator ingresses parse one deterministic gate message; a gate
site that sends free text is refused at the ingress before any operator sees it. The
validator-escalation gate (C-RT-25) and the model tool-call gate (C-RT-38) are the two
sites that did not compose it. `LoopOwnedAskUserQuestionSurface` is the stage-5 binding
that lets the CP driver's `asyncio.run` bridge ask through the session's own loop.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Sequence

import pytest
from harness_cp.hitl_response_palette import HITLResponse
from harness_cp.validator_framework_types import HITLEscalationBrief, ValidatorFailClass
from harness_runtime.lifecycle.ask_user_question_surface import (
    AskUserQuestionHoldRequestedError,
    AskUserQuestionResult,
    LoopOwnedAskUserQuestionSurface,
)
from harness_runtime.lifecycle.escalation_prompt import compose_escalation_prompt
from harness_runtime.lifecycle.operator_input import parse_operator_gate_message

_OPTIONS = ("approve", "edit", "reject", "respond", "hold", "cancel")


def test_the_escalation_prompt_is_the_c1a_gate_message_carrying_the_brief() -> None:
    brief = HITLEscalationBrief(
        parent_step_id="s-gated",
        parent_action_id="workflow:wf:step:0",
        fail_class=ValidatorFailClass.SEMANTIC_INCONSISTENCY,
        escalation_reason="operator must confirm this output",
    )
    palette = frozenset({HITLResponse.APPROVE, HITLResponse.REJECT})

    request = parse_operator_gate_message(compose_escalation_prompt(brief, palette), _OPTIONS)

    assert request.position == "post-dispatch"
    assert request.step_id == "s-gated"
    assert request.step_kind == "validator-escalation"
    assert request.payload == {
        "parent_action_id": "workflow:wf:step:0",
        "fail_class": "semantic_inconsistency",
        "fail_detail_hash": None,
        "escalation_reason": "operator must confirm this output",
        "responses": ["approve", "reject"],
    }


class _Inner:
    """Records the loop each ask ran on; answers, raises or waits as scripted."""

    def __init__(self) -> None:
        self.loops: list[asyncio.AbstractEventLoop] = []
        self.hold = False
        self.block: asyncio.Event | None = None
        self.cancelled = False

    async def ask(
        self, prompt: str, options: Sequence[HITLResponse], timeout: float | None
    ) -> AskUserQuestionResult:
        _ = options, timeout
        self.loops.append(asyncio.get_running_loop())
        if self.hold:
            raise AskUserQuestionHoldRequestedError(ingress="python")
        if self.block is not None:
            try:
                await self.block.wait()
            except asyncio.CancelledError:
                self.cancelled = True
                raise
        return AskUserQuestionResult(response=HITLResponse.APPROVE, latency_ms=1.0)


async def _from_a_foreign_loop(surface: LoopOwnedAskUserQuestionSurface, timeout: float | None):
    """Ask the way the CP driver does: a worker thread running its own `asyncio.run`."""
    outcome: list[object] = []

    def worker() -> None:
        async def ask() -> object:
            try:
                return await asyncio.wait_for(
                    surface.ask("p", (HITLResponse.APPROVE,), None), timeout
                )
            except BaseException as exc:  # the test reads the exception class
                return exc

        outcome.append(asyncio.run(ask()))

    thread = threading.Thread(target=worker)
    thread.start()
    while thread.is_alive():  # keep the owning loop serving while the worker waits
        await asyncio.sleep(0.01)
    return outcome[0]


def test_a_foreign_loop_ask_is_answered_on_the_owning_loop() -> None:
    inner = _Inner()

    async def owning() -> tuple[object, asyncio.AbstractEventLoop]:
        surface = LoopOwnedAskUserQuestionSurface(inner=inner, loop=asyncio.get_running_loop())
        return await _from_a_foreign_loop(surface, None), asyncio.get_running_loop()

    outcome, loop = asyncio.run(owning())

    assert isinstance(outcome, AskUserQuestionResult)
    assert outcome.response is HITLResponse.APPROVE
    assert inner.loops == [loop]


def test_an_ask_on_the_owning_loop_itself_still_answers() -> None:
    inner = _Inner()

    async def owning() -> AskUserQuestionResult:
        surface = LoopOwnedAskUserQuestionSurface(inner=inner, loop=asyncio.get_running_loop())
        return await surface.ask("p", (HITLResponse.APPROVE,), None)

    assert asyncio.run(owning()).response is HITLResponse.APPROVE
    assert len(inner.loops) == 1


def test_a_hold_raised_on_the_owning_loop_reaches_the_foreign_caller() -> None:
    inner = _Inner()
    inner.hold = True

    async def owning() -> object:
        surface = LoopOwnedAskUserQuestionSurface(inner=inner, loop=asyncio.get_running_loop())
        return await _from_a_foreign_loop(surface, None)

    outcome = asyncio.run(owning())

    assert isinstance(outcome, AskUserQuestionHoldRequestedError)
    assert outcome.ingress == "python"


def test_cancelling_the_foreign_wait_cancels_the_ask_on_the_owning_loop() -> None:
    inner = _Inner()

    async def owning() -> object:
        inner.block = asyncio.Event()
        surface = LoopOwnedAskUserQuestionSurface(inner=inner, loop=asyncio.get_running_loop())
        outcome = await _from_a_foreign_loop(surface, 0.2)
        for _ in range(100):  # the cancellation crosses threads; give the loop a few ticks
            if inner.cancelled:
                break
            await asyncio.sleep(0.01)
        return outcome

    outcome = asyncio.run(owning())

    assert isinstance(outcome, TimeoutError)
    assert inner.cancelled, "the scheduled ask kept waiting after its caller gave up"


@pytest.mark.parametrize(
    "text", ["Validator escalation at step s (action_id=a).", "HITL tool call t on s"]
)
def test_the_former_free_text_prompts_are_refused_at_the_ingress(text: str) -> None:
    with pytest.raises(ValueError, match="not a C1a HITL gate message"):
        parse_operator_gate_message(text, _OPTIONS)
