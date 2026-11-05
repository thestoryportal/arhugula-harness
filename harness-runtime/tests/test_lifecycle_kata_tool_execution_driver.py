"""859 local Kata Containers TIER_4_FULL_VM carrier tests.

The Kata driver runs the shared Docker JSON tool runner under a registered Kata
runtime. Its refusal witness (`docker info` Runtimes carrying a Kata identity)
must precede every container effect; a refused call never falls back to runc,
gVisor, E2B or in-process execution.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_runtime.lifecycle.docker_tool_execution_driver import (
    KataMicroVMToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    SandboxDispatchDecision,
    ToolInvocationProtocolError,
)

_EXEC = "harness_runtime.lifecycle.docker_tool_execution_driver.asyncio.create_subprocess_exec"


class _FakeProcess:
    def __init__(self, *, stdout: bytes, stderr: bytes = b"", returncode: int = 0) -> None:
        self._stdout = stdout
        self._stderr = stderr
        self.returncode = returncode
        self.stdin_payload: bytes | None = None

    async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
        self.stdin_payload = stdin_payload
        return self._stdout, self._stderr

    def kill(self) -> None:
        return None

    async def wait(self) -> int:
        return self.returncode


def _decision(tier: SandboxTier = SandboxTier.TIER_4_FULL_VM) -> SandboxDispatchDecision:
    return SandboxDispatchDecision(
        tier=tier,
        tech="microvm",
        provider="kata",
        assigned_tier_reason="test",
        cost_tier_overhead_ms=0,
    )


def _driver(**overrides: Any) -> KataMicroVMToolRunnerExecutionDriver:
    base: dict[str, Any] = dict(image="runner:local", command=("python", "runner.py"))
    base.update(overrides)
    return KataMicroVMToolRunnerExecutionDriver(**base)


def _fake_docker(
    calls: list[Sequence[str]],
    *,
    info: _FakeProcess,
    run_payloads: list[dict[str, Any]] | None = None,
) -> Any:
    async def fake_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        calls.append(argv)
        if argv[1] == "info":
            return info
        if argv[1] == "inspect":
            return _FakeProcess(stdout=b"sha256:runner-image\n")
        assert argv[1] == "run", argv

        class _RunProcess(_FakeProcess):
            async def communicate(self, stdin_payload: bytes) -> tuple[bytes, bytes]:
                if run_payloads is not None:
                    run_payloads.append(json.loads(stdin_payload.decode("utf-8")))
                return await super().communicate(stdin_payload)

        return _RunProcess(
            stdout=json.dumps({"content": [{"type": "text", "text": "kata:ok"}]}).encode()
        )

    return fake_exec


def _runtimes(payload: object) -> _FakeProcess:
    return _FakeProcess(stdout=json.dumps(payload).encode("utf-8"))


async def _call(driver: KataMicroVMToolRunnerExecutionDriver, **kwargs: Any) -> Any:
    return await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=kwargs.pop("sandbox_decision", _decision()),
        tool_id="echo",
        tool_args={"message": "hello"},
        idempotency_key="idem",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "registration",
    [
        {"runtimeType": "io.containerd.kata.v2"},
        {"path": "/opt/kata/bin/kata-runtime"},
    ],
)
async def test_witnessed_kata_runtime_runs_tier4_under_kata(
    monkeypatch: pytest.MonkeyPatch, registration: dict[str, str]
) -> None:
    calls: list[Sequence[str]] = []
    run_payloads: list[dict[str, Any]] = []
    info = _runtimes({"runc": {"path": "runc"}, "kata": registration})
    monkeypatch.setattr(_EXEC, _fake_docker(calls, info=info, run_payloads=run_payloads))

    response = await _call(_driver())

    assert response["content"][0]["text"] == "kata:ok"
    assert calls[0] == ("docker", "info", "--format", "{{json .Runtimes}}")
    assert calls[1][:2] == ("docker", "inspect")
    run = calls[2]
    assert run[:3] == ("docker", "run", "--rm")
    assert run[run.index("--runtime") + 1] == "kata"
    assert run[run.index("--network") + 1] == "none"
    assert run[run.index("-i") + 1] == "sha256:runner-image"
    assert run_payloads[0]["sandbox"]["tier"] == "tier-4-full-vm"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("info", "detail"),
    [
        (_runtimes({"runc": {"path": "runc"}}), "runtime not registered"),
        (_runtimes({"kata": {"path": "runc"}}), "registered as 'runc'"),
        (_runtimes({"kata": {"runtimeType": "io.containerd.runsc.v1"}}), "registered as"),
        (_runtimes(["kata"]), "runtime not registered"),
        (_FakeProcess(stdout=b"not json"), "unreadable docker info output"),
        (_FakeProcess(stdout=b"", stderr=b"daemon down", returncode=1), "docker info exited 1"),
    ],
)
async def test_unwitnessed_runtime_refuses_before_any_container_effect(
    monkeypatch: pytest.MonkeyPatch, info: _FakeProcess, detail: str
) -> None:
    calls: list[Sequence[str]] = []
    monkeypatch.setattr(_EXEC, _fake_docker(calls, info=info))

    with pytest.raises(ToolInvocationProtocolError, match="FULL-VM-CARRIER-UNWITNESSED") as exc:
        await _call(_driver())

    assert detail in str(exc.value)
    # Only the read-only witness ran: no image resolution, no `docker run`.
    assert [argv[1] for argv in calls] == ["info"]


@pytest.mark.asyncio
async def test_custom_runtime_name_is_witnessed_and_used(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[Sequence[str]] = []
    info = _runtimes({"kata-fc": {"runtimeType": "io.containerd.kata-fc.v2"}})
    monkeypatch.setattr(_EXEC, _fake_docker(calls, info=info))

    await _call(_driver(runtime="kata-fc"))

    run = calls[-1]
    assert run[run.index("--runtime") + 1] == "kata-fc"


@pytest.mark.asyncio
async def test_non_tier4_decision_refuses_without_any_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def no_exec(*argv: str, **_kwargs: Any) -> _FakeProcess:
        raise AssertionError(f"unexpected subprocess: {argv!r}")

    monkeypatch.setattr(_EXEC, no_exec)

    with pytest.raises(ToolInvocationProtocolError, match="tier-4-full-vm"):
        await _call(_driver(), sandbox_decision=_decision(SandboxTier.TIER_3_MICROVM))


@pytest.mark.parametrize("runtime", [None, "", "  "])
def test_runtime_must_be_named(runtime: str | None) -> None:
    with pytest.raises(ValueError, match="runtime must be non-empty"):
        _driver(runtime=runtime)


@pytest.mark.parametrize("network", ["host", "bridge", ""])
def test_network_must_stay_none(network: str) -> None:
    """859 F1: the Kata microVM is egress-restricted; no other network mode constructs."""
    with pytest.raises(ValueError, match="network must be 'none'"):
        _driver(network=network)
