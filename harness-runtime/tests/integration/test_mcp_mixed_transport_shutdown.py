"""#1756 — a stdio MCP client and a streamable-HTTP MCP client configured together
must shut down cleanly.

Each `MCPClientHost.start()` enters its transport context (the `mcp` SDK's
`stdio_client` / `streamable_http_client`, each an anyio task group) on an
`AsyncExitStack` in the bootstrap task. Stage 3a starts the hosts one after
another in that task, so every later host's cancel scope is nested inside the
earlier host's. Closing the hosts in start order exits an outer scope while an
inner one is still open: the first close fails with anyio's "Attempted to exit
a cancel scope that isn't the current tasks's current cancel scope", which
leaves the outer scope cancelled, and the next host's close is hit by that
cancellation, so `CancelledError` escapes `shutdown()` and the run ends with
no result. Any two hosts did this, whatever their transports.

These tests start real hosts the way bootstrap does (stage 3a with the real
host factory, a stdio host on the echo fixture and a streamable-HTTP host on
the HTTP echo fixture) and drain them through every path that shuts hosts
down: `shutdown()` step 4 (the end of `run()` and `resume()`, completed,
held or failed), the post-stage-3a bootstrap rollback, and stage 3a's own
partial-start drain. No model call; the servers are local subprocesses.
"""

from __future__ import annotations

import asyncio
import importlib
import sys
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_as.discriminators import MCPTransport
from harness_as.sandbox_tier import BlastRadiusTier
from harness_as.sandbox_tier_floor import MCPServerTrustLevel
from harness_core import ClientName
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_cp.topology_pattern import TopologyPattern
from harness_runtime.bootstrap import _rollback_cp_clients
from harness_runtime.bootstrap import stage_3a_cp_clients as stage_3a
from harness_runtime.bootstrap.mutable_context import _MutableHarnessContext
from harness_runtime.lifecycle.mcp_client_host import MCPHostStartupError
from harness_runtime.shutdown import FlushReport, shutdown
from harness_runtime.types import (
    CollectorConfig,
    MCPClientConfig,
    OTelConfig,
    PathBindingConfig,
    ProviderSecretsConfig,
    RuntimeConfig,
    ServerName,
)

from .fixtures.streamable_http_echo import streamable_http_echo_server

# The package re-exports the `shutdown` function under the module's name.
shutdown_mod = importlib.import_module("harness_runtime.shutdown")

_STDIO_FIXTURE = (Path(__file__).parent / "fixtures" / "mcp_echo_server.py").resolve()


@pytest.fixture(scope="module")
def http_url() -> Iterator[str]:
    with streamable_http_echo_server() as url:
        yield url


def _stdio_client(name: str) -> MCPClientConfig:
    return MCPClientConfig(
        client_name=ClientName(name),
        transport=MCPTransport.STDIO,
        trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url=f"stdio://{sys.executable} {_STDIO_FIXTURE}",
    )


def _http_client(name: str, url: str) -> MCPClientConfig:
    return MCPClientConfig(
        client_name=ClientName(name),
        transport=MCPTransport.STREAMABLE_HTTP_L3_AUDIT,
        trust_level=MCPServerTrustLevel.L3_ALLOW_WITH_AUDIT,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url=url,
    )


def _clients(kinds: tuple[str, ...], url: str) -> list[MCPClientConfig]:
    return [
        _stdio_client(f"stdio-{i}") if kind == "stdio" else _http_client(f"http-{i}", url)
        for i, kind in enumerate(kinds)
    ]


async def _start_hosts_as_bootstrap_does(
    clients: list[MCPClientConfig],
) -> dict[ServerName, Any]:
    """Stage 3a with the real host factory: hosts materialized from config and
    started sequentially in this task (no inference, so no provider clients)."""
    config = RuntimeConfig(
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        repository_root=Path("/tmp"),
        path_bindings=PathBindingConfig(),
        provider_secrets=ProviderSecretsConfig(),
        otel=OTelConfig(otlp_endpoint="http://localhost:4318"),
        collector=CollectorConfig(),
        default_topology=TopologyPattern.SINGLE_THREADED_LINEAR,
        mcp_clients=clients,
    )
    builder = _MutableHarnessContext()
    builder.keyring_resolver = object()  # type: ignore[assignment]
    builder.requires_inference = False
    await stage_3a.execute(builder, config, WorkloadClass.SOFTWARE_ENGINEERING)
    hosts: dict[ServerName, Any] = dict(builder.mcp_client_hosts or {})
    assert len(hosts) == len(clients)
    assert all(host.started for host in hosts.values())
    return hosts


async def _flush_ok(*_args: Any, **_kwargs: Any) -> FlushReport:
    return FlushReport(
        tracer_flushed=True,
        ledger_fsynced=True,
        cost_chain_noop=True,
        timed_out=False,
        failures=(),
    )


async def _stage_ok(*_args: Any, **_kwargs: Any) -> bool:
    return True


class _ShutdownCtx:
    """Plain class: `shutdown()` keeps a weak reference to its ctx."""


def _shutdown_ctx(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, hosts: dict[ServerName, Any]
) -> _ShutdownCtx:
    """A ctx carrying only the MCP hosts; the observability stages before step 4
    are stubbed (they are witnessed in `test_shutdown.py`)."""
    monkeypatch.setattr(shutdown_mod, "flush_observability", _flush_ok)
    monkeypatch.setattr(shutdown_mod, "_close_collector_daemon", _stage_ok)
    monkeypatch.setattr(shutdown_mod, "_close_tracer_provider", _stage_ok)
    ledger = tmp_path / "state.jsonl"
    ledger.write_text("")
    ctx = _ShutdownCtx()
    ctx.ledger_writer = SimpleNamespace(handle=SimpleNamespace(canonical_path=ledger))  # type: ignore[attr-defined]
    ctx.drained_flag = asyncio.Event()  # type: ignore[attr-defined]
    ctx.providers = {}  # type: ignore[attr-defined]
    ctx.tracer_provider = None  # type: ignore[attr-defined]
    ctx.collector_daemon = None  # type: ignore[attr-defined]
    ctx.audit_writer = None  # type: ignore[attr-defined]
    ctx.mcp_client_hosts = hosts  # type: ignore[attr-defined]
    return ctx


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kinds",
    [("stdio",), ("http",), ("stdio", "http"), ("http", "stdio"), ("stdio", "http", "stdio")],
    ids=lambda kinds: "+".join(kinds),
)
async def test_shutdown_drains_started_hosts_of_any_mix(
    kinds: tuple[str, ...], http_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The witnessed failure: with both transports configured, `shutdown()` raised
    `CancelledError` (on `main`). One host of either kind alone still drains."""
    hosts = await _start_hosts_as_bootstrap_does(_clients(kinds, http_url))
    ctx = _shutdown_ctx(tmp_path, monkeypatch, hosts)

    report = await shutdown(ctx, timeout=30.0)  # type: ignore[arg-type]

    assert report.failures == ()
    assert report.timed_out is False
    assert not any(host.started for host in hosts.values())


@pytest.mark.asyncio
async def test_bootstrap_rollback_drains_mixed_hosts(http_url: str) -> None:
    """A post-stage-3a bootstrap abort drains the started hosts the same way."""
    hosts = await _start_hosts_as_bootstrap_does(_clients(("stdio", "http"), http_url))

    await _rollback_cp_clients(SimpleNamespace(mcp_client_hosts=hosts, providers=None))  # type: ignore[arg-type]

    assert not any(host.started for host in hosts.values())


@pytest.mark.asyncio
async def test_stage_3a_partial_start_drains_mixed_hosts(http_url: str) -> None:
    """A later host failing to start drains the hosts already started; the start
    failure propagates, not a `CancelledError` from the drain."""
    broken = MCPClientConfig(
        client_name=ClientName("broken"),
        transport=MCPTransport.STDIO,
        trust_level=MCPServerTrustLevel.L1_SIGNED_PINNED,
        blast_radius=BlastRadiusTier.READ_ONLY,
        connection_url="stdio:///nonexistent/mcp-server-for-1756",
    )
    clients = [*_clients(("stdio", "http"), http_url), broken]
    captured: dict[ServerName, Any] = {}
    real_materialize = stage_3a.materialize_mcp_client_host_stage

    async def _capture(*args: Any, **kwargs: Any) -> Any:
        captured.update(await real_materialize(*args, **kwargs))
        return captured

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(stage_3a, "materialize_mcp_client_host_stage", _capture)
        with pytest.raises(MCPHostStartupError):
            await _start_hosts_as_bootstrap_does(clients)

    assert len(captured) == 3
    assert not any(host.started for host in captured.values())


class _HangingHost:
    """A started host whose `shutdown()` never returns until released."""

    def __init__(self, release: asyncio.Event) -> None:
        self.started = True
        self.cancelled = False
        self._release = release

    async def shutdown(self) -> None:
        try:
            await self._release.wait()
        except asyncio.CancelledError:
            self.cancelled = True
            raise


@pytest.mark.asyncio
async def test_hanging_host_is_still_bounded_beside_mixed_hosts(
    http_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The shutdown timeout still bounds a host that hangs, reported as before,
    while the real stdio + HTTP hosts drain cleanly."""
    real = await _start_hosts_as_bootstrap_does(_clients(("stdio", "http"), http_url))
    release = asyncio.Event()
    hanging = _HangingHost(release)
    # Listed first: started first, so drained last, after the real pair.
    hosts: dict[ServerName, Any] = {ServerName("hanging"): hanging, **real}
    ctx = _shutdown_ctx(tmp_path, monkeypatch, hosts)
    try:
        report = await asyncio.wait_for(shutdown(ctx, timeout=3.0), timeout=20.0)  # type: ignore[arg-type]
    finally:
        release.set()

    assert report.failures == ("mcp_client_host",)
    assert report.timed_out is True
    assert hanging.cancelled is True
    assert not any(host.started for host in real.values())
