"""Runtime v1.134 §14.6.4 cell 10: a post-effect carrier the breaker does not charge.

Through the REAL C-RT-16 retry wrapper over the REAL C-RT-15 dispatcher and C-RT-38 loop,
observed at the wrapper's span exporter and the registry's transition emission seam:

- a WAIVED provider-origin carrier charges nothing: a closed breaker records nothing, a
  half-open trial re-arms OPEN with `trigger_count` 0;
- on a re-arm row (non-provider or waived provider origin), a failing transition emitter
  is noted on the SAME carrier, which still propagates with its original fault.

The chain carries a same-family fallback candidate, so one dispatch attempt also witnesses
"no advance". Provider-free source fixtures: the waived fault is a harness-internal
§14.6.3 waiver member INJECTED at the provider boundary after a tool turn. That proves the
wrapper's waiver arm on the post-effect path, not that a live SDK emits this fault.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from harness_cp.cross_family_fallback_chain import FallbackChain, ProviderCandidate, ProviderFamily
from harness_od.harness_breaker_schema import BreakerState
from harness_runtime.lifecycle.llm_dispatch import LLMDispatchPayloadShapeInternalError
from harness_runtime.lifecycle.post_tool_effect import PostToolEffectError
from harness_runtime.lifecycle.retry_breaker import RuntimeRetryBreaker
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from .test_post_tool_effect_replay import (
    _first_tool_turn,
    _provider_case,
    _run,
    _Tools,
    _ToolsFailingWithHttpShape,
)

_FAMILY = {"anthropic": ProviderFamily.ANTHROPIC, "ollama": ProviderFamily.LOCAL_OPEN_WEIGHT}


def _waived_fault() -> LLMDispatchPayloadShapeInternalError:
    """A named §14.6.3 waiver member, injected at the provider call (source fixture)."""
    return LLMDispatchPayloadShapeInternalError("cell-10 source fixture at the provider boundary")


@dataclass
class _Raised:
    """Records the exact exception object the dispatcher raised to the wrapper."""

    inner: Any
    raised: list[BaseException] = field(default_factory=list)

    async def dispatch(self, binding: Any, step: Any, *, step_context: Any = None) -> Any:
        try:
            return await self.inner.dispatch(binding, step, step_context=step_context)
        except BaseException as exc:
            self.raised.append(exc)
            raise


def _cell10_case(
    tmp_path: Path, provider: str, script: list[Any], tools: _Tools, *, half_open: bool
) -> tuple[Any, Any, Any, Any, _Raised, InMemorySpanExporter]:
    """The replay suite's real-path case, plus an exporter and a fallback candidate."""
    attempts, wrapper, breaker, step = _provider_case(tmp_path, provider, script, tools)
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    wrapper.tracer_provider = tracer_provider
    family = _FAMILY[provider]
    wrapper.fallback_chain = FallbackChain(
        primary=ProviderCandidate(provider=provider, model="m", family=family),
        same_family=(ProviderCandidate(provider=provider, model="m-fallback", family=family),),
        cross_family=(),
    )
    raised = _Raised(attempts)
    wrapper.inner = raised
    if half_open:
        for _ in range(breaker.fail_threshold):
            breaker.record_failure(now=0.0)
    return attempts, wrapper, breaker, step, raised, exporter


def _transitions(exporter: InMemorySpanExporter) -> list[tuple[str, str, int]]:
    """`(from_state, to_state, trigger_count)` of every emitted breaker transition."""
    return [
        (
            str(attributes["harness.breaker.from_state"]),
            str(attributes["harness.breaker.to_state"]),
            int(attributes["harness.breaker.trigger_count"]),  # type: ignore[arg-type]
        )
        for span in exporter.get_finished_spans()
        for event in span.events
        if event.name == "breaker.tripped"
        for attributes in [event.attributes or {}]
    ]


@pytest.mark.parametrize("half_open", [False, True], ids=["closed", "half-open"])
@pytest.mark.parametrize("provider", ["anthropic"])
async def test_a_waived_provider_fault_after_an_effect_is_carried_but_never_charged(
    tmp_path: Path, provider: str, half_open: bool
) -> None:
    tools, fault = _Tools(), _waived_fault()
    attempts, wrapper, breaker, step, raised, exporter = _cell10_case(
        tmp_path, provider, [_first_tool_turn(provider), fault], tools, half_open=half_open
    )
    before = breaker.fail_count

    outcome = await _run(wrapper, provider, step)

    assert (len(tools.calls), len(attempts.calls)) == (1, 1), "one effect, one attempt, no advance"
    assert isinstance(outcome, PostToolEffectError) and outcome is raised.raised[0]
    assert outcome.origin == "provider" and outcome.fault is fault
    assert breaker.fail_count == before, "a waived fault is never charged"
    if half_open:
        assert breaker.state is BreakerState.OPEN
        assert breaker.opened_at is not None and breaker.opened_at > 0.0, "fresh cooldown"
        assert _transitions(exporter) == [("open", "half_open", 0), ("half_open", "open", 0)]
    else:
        assert breaker.state is BreakerState.CLOSED
        assert _transitions(exporter) == []


class _EmitterFault(RuntimeError):
    pass


@pytest.mark.parametrize("origin", ["non-provider", "waived-provider"])
@pytest.mark.parametrize("provider", ["anthropic"])
async def test_a_failing_re_arm_emission_is_noted_on_the_carrier_that_still_propagates(
    tmp_path: Path, provider: str, origin: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Cell 10's re-arm rows: the emitter fault never replaces the carrier.

    (Charging rows 2/5 let an emitter fault replace the carrier; that is out of scope here.)"""
    if origin == "non-provider":
        tools: _Tools = _ToolsFailingWithHttpShape()
        script: list[Any] = [_first_tool_turn(provider)]
    else:
        tools, script = _Tools(), [_first_tool_turn(provider), _waived_fault()]
    attempts, wrapper, breaker, step, raised, exporter = _cell10_case(
        tmp_path, provider, script, tools, half_open=True
    )
    emitted: list[str] = []
    real_emit = RuntimeRetryBreaker.emit_breaker_transition_event

    def _emit(self: Any, transition: Any, parent_span: Any, **kwargs: Any) -> Any:
        emitted.append(f"{transition.from_state.value}->{transition.to_state.value}")
        if transition.from_state is BreakerState.HALF_OPEN:
            raise _EmitterFault("span exporter refused the re-arm event")
        return real_emit(self, transition, parent_span, **kwargs)

    monkeypatch.setattr(RuntimeRetryBreaker, "emit_breaker_transition_event", _emit)

    outcome = await _run(wrapper, provider, step)

    assert outcome is raised.raised[0], "the carrier object itself propagates"
    assert isinstance(outcome, PostToolEffectError)
    assert outcome.fault is outcome.__cause__ and not isinstance(outcome.fault, _EmitterFault)
    assert any("_EmitterFault" in note for note in getattr(outcome, "__notes__", []))
    assert (len(tools.calls), len(attempts.calls)) == (1, 1), "no retry, advance or replay"
    assert emitted == ["open->half_open", "half_open->open"]
    assert _transitions(exporter) == [("open", "half_open", 0)], "the re-arm emission failed"
    assert breaker.state is BreakerState.OPEN and breaker.fail_count == breaker.fail_threshold
