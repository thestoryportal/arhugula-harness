"""B-18-KEEPALIVE Step 2 tests — `RuntimeLLMDispatcher.prewarm()`.

Covers DDR §7 tests 7.2, 7.3, 7.7 (hermetic; NO paid Anthropic calls).

7.2 — opt-in boot ping: flag on, fake adapter → exactly one prewarm call;
      `max_tokens==1` on the wire AND a `cache_control` breakpoint on the tools.
7.3 — eligibility skip: various reasons → `SKIPPED_*` outcomes, no adapter call.
7.7 — cost record: prewarm appends a record to the sink with
      `idempotency_key="__prewarm__"` and `gen_ai_provider_name="anthropic"`.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import pytest
from harness_od.idempotency_join_dedup import SpanCostRecord
from harness_od.rate_table_v1 import RATE_TABLE_V1
from harness_runtime.lifecycle.cost_attribution import RuntimeCostAttributionChain
from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome, RuntimeLLMDispatcher
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

# ---------------------------------------------------------------------------
# Helpers to build a frozen_tool_superset that clears the ≥4096-tok floor.
# Floor = len(json.dumps(superset)) / 4 >= 4096  →  len(serialized) >= 16384.
# ---------------------------------------------------------------------------

_BIG_DESC = "x" * 16400
_LARGE_SUPERSET: tuple[dict[str, Any], ...] = (
    {
        "name": "big_tool",
        "description": _BIG_DESC,
        "input_schema": {"type": "object", "properties": {}},
    },
)
# Sanity: verify it clears the floor at module load time.
assert len(json.dumps(list(_LARGE_SUPERSET))) / 4 >= 4096, "test setup: superset too small"

_SMALL_SUPERSET: tuple[dict[str, Any], ...] = (
    {
        "name": "tiny",
        "description": "small",
        "input_schema": {"type": "object", "properties": {}},
    },
)


# ---------------------------------------------------------------------------
# Minimal fake Anthropic adapter.
# ---------------------------------------------------------------------------


@dataclass
class _FakeUsage:
    input_tokens: int = 1
    output_tokens: int = 1
    cache_creation_input_tokens: int = 1
    cache_read_input_tokens: int = 0


@dataclass
class _FakeAnthropicResponse:
    id: str
    usage: _FakeUsage

    def model_dump(self) -> dict[str, Any]:
        return {"id": self.id, "content": [{"text": "ok"}]}


class _RecordingMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> _FakeAnthropicResponse:
        self.calls.append(kwargs)
        return _FakeAnthropicResponse(id="msg_prewarm_001", usage=_FakeUsage())


class _FakeAnthropicClient:
    def __init__(self) -> None:
        self.messages = _RecordingMessages()


@dataclass
class _FakeAnthropicAdapter:
    client: _FakeAnthropicClient


class _RecordingCostSink:
    def __init__(self) -> None:
        self.records: list[SpanCostRecord] = []

    def append(self, record: SpanCostRecord) -> None:
        self.records.append(record)


class _RecordingAuditWriter:
    def __init__(self) -> None:
        self.appended: list[tuple[str | None, object]] = []

    def append(self, tenant_id: str | None, audit_entry: object) -> object:
        self.appended.append((tenant_id, audit_entry))
        return "appended"


# ---------------------------------------------------------------------------
# Tracer provider factory.
# ---------------------------------------------------------------------------


def _tp() -> TracerProvider:
    exporter = InMemorySpanExporter()
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(exporter))
    return tp


# ---------------------------------------------------------------------------
# 7.2 — opt-in boot ping
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prewarm_fires_one_call_max_tokens_1() -> None:
    """7.2 — single prewarm call reaches the fake adapter with max_tokens=1."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
    )

    outcome = await dispatcher.prewarm()

    assert outcome is PrewarmOutcome.WARMED
    assert len(adapter.client.messages.calls) == 1
    assert adapter.client.messages.calls[0]["max_tokens"] == 1


@pytest.mark.asyncio
async def test_prewarm_places_cache_breakpoint_on_tools() -> None:
    """7.2 — the `cache_control` breakpoint is present on the last tool block."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
    )

    await dispatcher.prewarm()

    tools = adapter.client.messages.calls[0].get("tools")
    assert tools is not None and len(tools) > 0
    last_tool = tools[-1]
    assert "cache_control" in last_tool, f"cache_control missing from last tool: {last_tool}"


# ---------------------------------------------------------------------------
# 7.3 — eligibility skip
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prewarm_skipped_no_anthropic() -> None:
    """7.3 — no anthropic provider → SKIPPED_NO_ANTHROPIC."""
    dispatcher = RuntimeLLMDispatcher(
        providers={},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
    )
    outcome = await dispatcher.prewarm()
    assert outcome is PrewarmOutcome.SKIPPED_NO_ANTHROPIC


@pytest.mark.asyncio
async def test_prewarm_skipped_no_frozen_tool_superset() -> None:
    """7.3 — frozen_tool_superset=None → SKIPPED_NOT_ELIGIBLE (no breakpoint would land)."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=None,
        prewarm_model="claude-haiku-4-5",
    )
    outcome = await dispatcher.prewarm()
    assert outcome is PrewarmOutcome.SKIPPED_NOT_ELIGIBLE
    assert len(adapter.client.messages.calls) == 0


@pytest.mark.asyncio
async def test_prewarm_skipped_sub_floor_superset() -> None:
    """7.3 — superset below 4096-tok floor → SKIPPED_NOT_ELIGIBLE, no adapter call."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_SMALL_SUPERSET,
        prewarm_model="claude-haiku-4-5",
    )
    outcome = await dispatcher.prewarm()
    assert outcome is PrewarmOutcome.SKIPPED_NOT_ELIGIBLE
    assert len(adapter.client.messages.calls) == 0


@pytest.mark.asyncio
async def test_prewarm_adapter_raise_returns_failed() -> None:
    """7.3 — adapter raises on the paid call → FAILED (never re-raises)."""

    class _RaisingMessages:
        async def create(self, **kwargs: Any) -> Any:
            raise RuntimeError("synthetic Anthropic failure")

    class _RaisingClient:
        def __init__(self) -> None:
            self.messages = _RaisingMessages()

    @dataclass
    class _RaisingAdapter:
        client: _RaisingClient

    adapter = _RaisingAdapter(_RaisingClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
    )

    outcome = await dispatcher.prewarm()  # must not raise
    assert outcome is PrewarmOutcome.FAILED


@pytest.mark.asyncio
async def test_prewarm_skipped_no_model() -> None:
    """7.3 — no prewarm_model + no routing manifest → SKIPPED_NOT_ELIGIBLE."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model=None,
    )
    outcome = await dispatcher.prewarm()
    assert outcome is PrewarmOutcome.SKIPPED_NOT_ELIGIBLE
    assert len(adapter.client.messages.calls) == 0


# ---------------------------------------------------------------------------
# 7.7 — cost record
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_prewarm_appends_cost_record_with_prewarm_ids() -> None:
    """7.7 — prewarm appends one cost record with idempotency_key + model sentinel."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    sink = _RecordingCostSink()
    audit_writer = _RecordingAuditWriter()

    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=audit_writer,
        rate_table=RATE_TABLE_V1,
        cost_record_sink=sink,
    )

    outcome = await dispatcher.prewarm()

    assert outcome is PrewarmOutcome.WARMED
    assert len(sink.records) == 1
    record = sink.records[0]
    assert record.idempotency_key == "__prewarm__"
    assert record.gen_ai_provider_name == "anthropic"
    assert record.gen_ai_request_model == "claude-haiku-4-5"


# ---------------------------------------------------------------------------
# 7.4 — keep-alive fake clock
# ---------------------------------------------------------------------------


class _FakeCtx:
    """Minimal ctx stub for _keepalive_loop: just a drained_flag."""

    def __init__(self, *, drained: bool = False) -> None:
        self.drained_flag = asyncio.Event()
        if drained:
            self.drained_flag.set()


@dataclass
class _CountingBare:
    """Fake bare dispatcher — counts prewarm() calls; returns configurable outcome."""

    outcome: Any = None  # set after construction; PrewarmOutcome value
    calls: int = 0

    async def prewarm(self) -> Any:
        self.calls += 1
        return self.outcome


@pytest.mark.asyncio
async def test_keepalive_fires_each_interval() -> None:
    """7.4 — keep-alive calls prewarm() once per interval (fake sleep)."""
    from harness_runtime.cli.app import _keepalive_loop
    from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome

    ctx = _FakeCtx()
    bare = _CountingBare(outcome=PrewarmOutcome.WARMED)

    sleep_calls: list[float] = []

    async def _fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)
        if len(sleep_calls) >= 3:
            # Drain after 3 intervals so the loop exits cleanly.
            ctx.drained_flag.set()

    await _keepalive_loop(ctx, bare, sleep_fn=_fake_sleep, interval=240.0)

    assert bare.calls == 2  # sleep fires 3× but drain check stops after 2 prewarms
    assert all(s == 240.0 for s in sleep_calls)


@pytest.mark.asyncio
async def test_keepalive_exits_immediately_when_pre_drained() -> None:
    """7.4 — ctx.drained_flag already set before loop starts → zero prewarm calls.

    Note: the 1h-TTL spawn gate (`bare.cache_ttl == "5m"` check in `_daemon_main`)
    is not exercised by this test — that gate prevents task creation at the CLI
    level; this test covers the loop-body drain-check for an already-drained ctx.
    """
    from harness_runtime.cli.app import _keepalive_loop
    from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome

    ctx = _FakeCtx(drained=True)  # already drained → loop exits immediately
    bare = _CountingBare(outcome=PrewarmOutcome.WARMED)

    await _keepalive_loop(ctx, bare, sleep_fn=asyncio.sleep, interval=240.0)

    assert bare.calls == 0  # drained before first sleep completes


# ---------------------------------------------------------------------------
# 7.5 — self-disable after 3 consecutive failures
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_keepalive_self_disables_after_3_failures(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """7.5 — consecutive FAILED outcomes → loop stops after exactly 3 calls."""
    import logging

    from harness_runtime.cli.app import _keepalive_loop
    from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome

    ctx = _FakeCtx()
    bare = _CountingBare(outcome=PrewarmOutcome.FAILED)

    sleep_count = 0

    async def _instant_sleep(_: float) -> None:
        nonlocal sleep_count
        sleep_count += 1

    with caplog.at_level(logging.WARNING, logger="harness.runtime.keepalive"):
        await _keepalive_loop(ctx, bare, sleep_fn=_instant_sleep, interval=0.0)

    assert bare.calls == 3
    assert any("self-disabled" in r.message for r in caplog.records)


@pytest.mark.asyncio
async def test_keepalive_resets_failure_counter_on_success() -> None:
    """7.5 — a WARMED outcome resets the consecutive-failure counter."""
    from harness_runtime.cli.app import _keepalive_loop
    from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome

    ctx = _FakeCtx()
    bare = _CountingBare(outcome=PrewarmOutcome.WARMED)
    outcomes = [
        PrewarmOutcome.FAILED,
        PrewarmOutcome.FAILED,
        PrewarmOutcome.WARMED,  # resets counter
        PrewarmOutcome.FAILED,
        PrewarmOutcome.FAILED,
        PrewarmOutcome.FAILED,  # 3rd failure after reset → self-disable
    ]
    call_idx = 0

    async def _patched_prewarm() -> Any:
        nonlocal call_idx
        result = outcomes[call_idx]
        call_idx += 1
        return result

    bare.prewarm = _patched_prewarm  # type: ignore[method-assign]

    sleep_count = 0

    async def _instant_sleep(_: float) -> None:
        nonlocal sleep_count
        sleep_count += 1

    await _keepalive_loop(ctx, bare, sleep_fn=_instant_sleep, interval=0.0)

    assert call_idx == 6  # consumed all 6 outcomes; stopped at 3rd failure post-reset


# ---------------------------------------------------------------------------
# 7.6 — drain cancels cleanly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_keepalive_drain_cancels_cleanly() -> None:
    """7.6 — cancel() + await terminates the loop; no 'Task destroyed pending'."""
    from harness_runtime.cli.app import _keepalive_loop
    from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome

    ctx = _FakeCtx()
    bare = _CountingBare(outcome=PrewarmOutcome.WARMED)

    # Sleep that blocks indefinitely until cancelled.
    async def _blocking_sleep(_: float) -> None:
        await asyncio.Event().wait()

    task = asyncio.create_task(_keepalive_loop(ctx, bare, sleep_fn=_blocking_sleep))
    # Give the task a chance to enter the blocking sleep.
    await asyncio.sleep(0)
    task.cancel()
    # The key invariant: no exception other than CancelledError escapes the task.
    results = await asyncio.gather(task, return_exceptions=True)
    assert results[0] is None or isinstance(results[0], asyncio.CancelledError)
    assert task.done()
    assert bare.calls == 0  # cancelled before first prewarm


@pytest.mark.asyncio
async def test_prewarm_cost_audit_signs_with_configured_backend() -> None:
    """Merge-gate round-2 BLOCK (PR B2a) — USE-half witness for the PREWARM
    call site's `signing_backend=self.signing_backend` kwarg: the dispatch
    site and the shared builder hop were pinned, but deleting the
    prewarm-site kwarg silently reverted __prewarm__ cost-audit records to
    placeholder signing with the whole suite green."""

    class _CountingBackend:
        algorithm = "ed25519"

        def __init__(self) -> None:
            self.sign_calls = 0

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            self.sign_calls += 1
            return b"c" * 64

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            return True

    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    backend = _CountingBackend()
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
        cost_chain=RuntimeCostAttributionChain(),
        audit_writer=_RecordingAuditWriter(),
        rate_table=RATE_TABLE_V1,
        cost_record_sink=_RecordingCostSink(),
        signing_backend=backend,
    )

    outcome = await dispatcher.prewarm()

    assert outcome is PrewarmOutcome.WARMED
    assert backend.sign_calls >= 1
