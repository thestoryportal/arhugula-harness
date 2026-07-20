"""`U-RT-135` — MTC prewarm/keepalive DISABLE under fail-closed witnesses.

Implements `Implementation_Plan_Harness_Runtime_v2_49.md` §1.2 (Runtime spec
v1.101 surface C; OD v1.34 §21.2.3 row 8; fork gate item 8). The disable is
MTC-SCOPED: a lower-tier explicit `fail_closed=true` keeps the v1.99
prewarm/keepalive posture pending the `B-55` operator-gated disposition —
the last witness here is the mutation probe pinning exactly that boundary.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from harness_core import PersonaTier
from harness_core.deployment_surface import DeploymentSurface
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.cli.app import _keepalive_loop, _should_spawn_keepalive
from harness_runtime.lifecycle.audit_signing_fail_closed_validation import (
    mtc_audit_prewarm_disabled,
)
from harness_runtime.lifecycle.llm_dispatch import PrewarmOutcome, RuntimeLLMDispatcher
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

# The `harness_runtime.cli` package re-exports the Typer instance as `app`,
# shadowing the submodule in attribute lookup — importlib resolves the MODULE.
cli_app_mod = importlib.import_module("harness_runtime.cli.app")

# --------------------------------------------------------------------------
# Minimal fakes (mirrors test_b18_keepalive_prewarm.py's hermetic pattern).
# --------------------------------------------------------------------------

_BIG_DESC = "x" * 16400
_LARGE_SUPERSET: tuple[dict[str, Any], ...] = (
    {
        "name": "big_tool",
        "description": _BIG_DESC,
        "input_schema": {"type": "object", "properties": {}},
    },
)
assert len(json.dumps(list(_LARGE_SUPERSET))) / 4 >= 4096


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
        return _FakeAnthropicResponse(id="msg_prewarm_u135", usage=_FakeUsage())


class _FakeAnthropicClient:
    def __init__(self) -> None:
        self.messages = _RecordingMessages()


@dataclass
class _FakeAnthropicAdapter:
    client: _FakeAnthropicClient


def _tp() -> TracerProvider:
    tp = TracerProvider()
    tp.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
    return tp


def _dispatcher(*, policy_fail_closed: bool) -> tuple[RuntimeLLMDispatcher, _FakeAnthropicAdapter]:
    """A FULLY-ELIGIBLE dispatcher (adapter + big superset + model) so a
    fired ping is the default outcome — any skip is the gate under test."""
    adapter = _FakeAnthropicAdapter(_FakeAnthropicClient())
    dispatcher = RuntimeLLMDispatcher(
        providers={"anthropic": adapter},
        tracer_provider=_tp(),
        frozen_tool_superset=_LARGE_SUPERSET,
        prewarm_model="claude-haiku-4-5",
        prewarm_policy_fail_closed=policy_fail_closed,
    )
    return dispatcher, adapter


def _config(
    tmp_path: Path,
    *,
    persona_tier: PersonaTier,
    audit_signing_fail_closed: bool | None = None,
    prompt_cache_keepalive: bool = False,
) -> RuntimeConfig:
    return RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=tmp_path,
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4317"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=[],
        persona_tier=persona_tier,
        tenant_id="acme" if persona_tier is PersonaTier.MULTI_TENANT_COMPLIANCE else None,
        audit_signing_fail_closed=audit_signing_fail_closed,
        prompt_cache_keepalive=prompt_cache_keepalive,
    )


class _BareStub:
    """Spawn-predicate stub — only `cache_ttl` is consulted there."""

    cache_ttl = "5m"


# --------------------------------------------------------------------------
# Witness (b).1(i) — MTC + flag ON: the boot ping is NOT fired.
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mtc_flag_on_boot_prewarm_not_fired() -> None:
    """Criterion 1(i): with the policy disable bound (as stage 5 binds it at
    MTC + resolved-ON), `prewarm()` returns the POLICY skip BEFORE any
    eligibility gate — the adapter is never touched even though every
    eligibility condition holds (fully-eligible fake would otherwise WARM)."""
    dispatcher, adapter = _dispatcher(policy_fail_closed=True)
    outcome = await dispatcher.prewarm()
    assert outcome is PrewarmOutcome.SKIPPED_POLICY_FAIL_CLOSED
    assert adapter.client.messages.calls == []

    # Control: identical dispatcher without the policy bit fires the ping.
    control, control_adapter = _dispatcher(policy_fail_closed=False)
    assert await control.prewarm() is PrewarmOutcome.WARMED
    assert len(control_adapter.client.messages.calls) == 1


# --------------------------------------------------------------------------
# Witness (b).1(ii) — MTC + flag ON: the keepalive LOOP is never spawned.
# --------------------------------------------------------------------------


def test_mtc_flag_on_keepalive_spawn_predicate(tmp_path: Path) -> None:
    """Criterion 1(ii), predicate half: `_should_spawn_keepalive` (the ONLY
    guard on the daemon's `asyncio.create_task(_keepalive_loop(...))`) is
    False at MTC with the flag resolved ON — the loop's swallow-all outer
    catch is unreachable BY CONTRACT. v1.99 conditions preserved verbatim
    otherwise (opt-in flag, bare bound, 5m TTL)."""
    bare = _BareStub()
    mtc = _config(
        tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE, prompt_cache_keepalive=True
    )
    assert mtc_audit_prewarm_disabled(mtc) is True  # per-persona default ON
    assert _should_spawn_keepalive(mtc, bare) is False

    # v1.99 conditions still gate independently at MTC too.
    assert (
        _should_spawn_keepalive(
            _config(tmp_path, persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE), bare
        )
        is False
    )  # keepalive flag off


@pytest.mark.asyncio
async def test_mtc_flag_on_keepalive_loop_never_spawned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Criterion 1(ii), loop-level half through the REAL `_daemon_main`:
    with an MTC + keepalive-opt-in config, the `_keepalive_loop` coroutine
    is NEVER created; the solo-tier control run spawns it exactly once."""
    loop_spawns: list[object] = []

    async def _recording_loop(ctx: Any, bare: Any, **_k: Any) -> None:
        loop_spawns.append(bare)

    monkeypatch.setattr(cli_app_mod, "_keepalive_loop", _recording_loop)

    drained = asyncio.Event()
    state: dict[str, Any] = {}

    class _FakeFastMCP:
        def streamable_http_app(self) -> Any:
            return object()

    class _FakeMCPServer:
        def __init__(self) -> None:
            self._state = state
            self.server = _FakeFastMCP()

    class _FakeCtx:
        def __init__(self) -> None:
            self.drained_flag = drained
            self.mcp_server = _FakeMCPServer()
            self.bare_llm_dispatcher = _BareStub()

    async def _fake_bootstrap(*_a: Any, **_k: Any) -> Any:
        return _FakeCtx()

    async def _fake_shutdown(_ctx: Any, *, timeout: float = 30.0) -> Any:
        return object()

    class _FakeUvicornServer:
        def __init__(self, config: Any) -> None:
            self.should_exit = False
            self.force_exit = False

        async def serve(self) -> None:
            while not self.should_exit:
                await asyncio.sleep(0.01)

    class _FakeUvicornConfig:
        def __init__(self, *_a: Any, **kwargs: Any) -> None:
            self.uds = kwargs.get("uds")

    fake_uvicorn = type("uvicorn", (), {})()
    fake_uvicorn.Server = _FakeUvicornServer  # type: ignore[attr-defined]
    fake_uvicorn.Config = _FakeUvicornConfig  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "uvicorn", fake_uvicorn)

    import harness_runtime.bootstrap as _bootstrap_mod

    monkeypatch.setattr(_bootstrap_mod, "run_bootstrap", _fake_bootstrap)
    monkeypatch.setattr(sys.modules["harness_runtime.shutdown"], "shutdown", _fake_shutdown)

    async def _drain_soon() -> None:
        await asyncio.sleep(0.05)
        drained.set()

    # MTC + keepalive opt-in: the loop is never created.
    asyncio.create_task(_drain_soon())
    await cli_app_mod._daemon_main(
        runtime_config=_config(
            tmp_path,
            persona_tier=PersonaTier.MULTI_TENANT_COMPLIANCE,
            prompt_cache_keepalive=True,
        ),
        socket_path=tmp_path / "mtc.sock",
    )
    assert loop_spawns == []

    # Solo-tier control (same keepalive opt-in): spawned exactly once.
    drained.clear()
    asyncio.create_task(_drain_soon())
    await cli_app_mod._daemon_main(
        runtime_config=_config(
            tmp_path, persona_tier=PersonaTier.SOLO_DEVELOPER, prompt_cache_keepalive=True
        ),
        socket_path=tmp_path / "solo.sock",
    )
    assert len(loop_spawns) == 1


# --------------------------------------------------------------------------
# Witness (b).2 — policy skip is SKIPPED_* family; never feeds consec_fail.
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_policy_skip_is_skipped_family_and_never_increments_consec_fail(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Criterion 2: the member is in the `SKIPPED_*` family, and inside a
    running keepalive loop it RESETS (never increments) `consec_fail` — a
    FAILED,FAILED,SKIP,FAILED,FAILED sequence must NOT self-disable (the
    skip breaks the streak; 3-consecutive is never reached)."""
    import logging

    assert PrewarmOutcome.SKIPPED_POLICY_FAIL_CLOSED.value.startswith("skipped_")

    outcomes = iter(
        [
            PrewarmOutcome.FAILED,
            PrewarmOutcome.FAILED,
            PrewarmOutcome.SKIPPED_POLICY_FAIL_CLOSED,
            PrewarmOutcome.FAILED,
            PrewarmOutcome.FAILED,
        ]
    )
    ticks = 0

    class _Ctx:
        class _Flag:
            @staticmethod
            def is_set() -> bool:
                return ticks >= 5

        drained_flag = _Flag()

    class _Bare:
        async def prewarm(self) -> PrewarmOutcome:
            return next(outcomes)

    async def _fake_sleep(_s: float) -> None:
        nonlocal ticks
        ticks += 1

    with caplog.at_level(logging.WARNING, logger="harness.runtime.keepalive"):
        await _keepalive_loop(_Ctx(), _Bare(), sleep_fn=_fake_sleep, interval=240.0)

    assert "self-disabled" not in caplog.text  # streak broken by the skip


# --------------------------------------------------------------------------
# Witness (b).3 — non-MTC byte preservation + the B-55 boundary control.
# --------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_mtc_byte_preservation_control(tmp_path: Path) -> None:
    """Flag UNSET at solo/team: the v1.99 posture verbatim — predicate
    False, spawn predicate True under the v1.99 conditions, and a
    fully-eligible dispatcher WARMS."""
    for tier in (PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING):
        cfg = _config(tmp_path, persona_tier=tier, prompt_cache_keepalive=True)
        assert mtc_audit_prewarm_disabled(cfg) is False
        assert _should_spawn_keepalive(cfg, _BareStub()) is True
    dispatcher, adapter = _dispatcher(policy_fail_closed=False)
    assert await dispatcher.prewarm() is PrewarmOutcome.WARMED
    assert len(adapter.client.messages.calls) == 1


@pytest.mark.asyncio
async def test_lower_tier_explicit_true_prewarm_still_active_pending_b55(
    tmp_path: Path,
) -> None:
    """Criterion 3 (the ratified gate-item-8 letter): an EXPLICIT lower-tier
    `fail_closed=true` keeps prewarm/keepalive ACTIVE with the v1.99
    posture — the `B-55` register row HOLDS the extend/propagate/ratify
    disposition. Mutation probe: extending the MTC disable to the resolved
    flag at any tier pre-decides that operator-gated fork and FAILS this."""
    for tier in (PersonaTier.SOLO_DEVELOPER, PersonaTier.TEAM_BINDING):
        cfg = _config(
            tmp_path,
            persona_tier=tier,
            audit_signing_fail_closed=True,  # explicit lower-tier opt-in
            prompt_cache_keepalive=True,
        )
        assert mtc_audit_prewarm_disabled(cfg) is False
        assert _should_spawn_keepalive(cfg, _BareStub()) is True
