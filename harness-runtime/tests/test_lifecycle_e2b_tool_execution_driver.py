"""R-412 E2B managed full-VM tool execution driver tests."""

from __future__ import annotations

import importlib
import json
import shlex
from typing import Any, ClassVar, cast

import pytest
from harness_as.sandbox_tier import SandboxTier
from harness_runtime.lifecycle.e2b_tool_execution_driver import (
    E2BManagedFullVMToolRunnerExecutionDriver,
)
from harness_runtime.lifecycle.mcp_client_host import MCPClientHost
from harness_runtime.lifecycle.runtime_tool_dispatcher import (
    SandboxDispatchDecision,
    ToolInvocationProtocolError,
)


class _Result:
    def __init__(self, stdout: str, *, exit_code: int = 0, stderr: str = "") -> None:
        self.stdout = stdout
        self.exit_code = exit_code
        self.stderr = stderr


class _Commands:
    calls: ClassVar[list[tuple[str, int]]] = []

    def run(self, command: str, *, timeout: int) -> _Result:
        self.calls.append((command, timeout))
        prefix, sep, _runner = command.partition(" | ")
        assert sep == " | "
        assert prefix.startswith("printf %s ")
        payload = json.loads(shlex.split(prefix)[2])
        return _Result(
            json.dumps(
                {
                    "content": [{"type": "text", "text": f"e2b:{payload['tool_args']['message']}"}],
                    "isError": False,
                    "structuredContent": {"sandbox": payload["sandbox"]},
                }
            )
        )


class _Sandbox:
    create_kwargs: ClassVar[dict[str, object]] = {}

    def __init__(self) -> None:
        self.commands = _Commands()

    @classmethod
    def create(cls, **kwargs: object) -> _Sandbox:
        cls.create_kwargs = kwargs
        return cls()

    def __enter__(self) -> _Sandbox:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


def _decision(tier: SandboxTier = SandboxTier.TIER_4_FULL_VM) -> SandboxDispatchDecision:
    return SandboxDispatchDecision(
        tier=tier,
        tech="e2b-firecracker",
        provider="e2b-managed",
        assigned_tier_reason="r412-managed-full-vm",
        cost_tier_overhead_ms=150,
    )


@pytest.mark.asyncio
async def test_e2b_driver_runs_json_runner_in_tier4_sandbox() -> None:
    _Commands.calls.clear()
    driver = E2BManagedFullVMToolRunnerExecutionDriver(
        command=("python", "-m", "tool_runner"),
        sandbox_cls=_Sandbox,
        timeout_seconds=17,
        sandbox_timeout_seconds=61,
        metadata={"trace": "unit"},
    )

    response = await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=_decision(),
        tool_id="echo",
        tool_args={"message": "ok"},
        idempotency_key="idem",
    )

    assert response["content"][0]["text"] == "e2b:ok"
    assert response["structuredContent"]["sandbox"] == {
        "tier": "tier-4-full-vm",
        "tech": "e2b-firecracker",
        "provider": "e2b-managed",
        "assigned_tier_reason": "r412-managed-full-vm",
    }
    assert _Sandbox.create_kwargs == {
        "timeout": 61,
        "allow_internet_access": False,
        "metadata": {
            "roadmap_item": "R-412-sandbox-tier-4-full-vm-execution",
            "sandbox_tier": "tier-4-full-vm",
            "trace": "unit",
        },
    }
    assert _Commands.calls == [
        (
            'printf %s \'{"tool_id": "echo", "tool_args": {"message": "ok"}, '
            '"idempotency_key": "idem", "sandbox": {"tier": "tier-4-full-vm", '
            '"tech": "e2b-firecracker", "provider": "e2b-managed", '
            '"assigned_tier_reason": "r412-managed-full-vm"}}\' | '
            "python -m tool_runner",
            17,
        )
    ]


class _SlowCommands:
    """`.run()` blocks synchronously — simulates the real E2B SDK's blocking
    network call, used to prove `call_tool` doesn't freeze the event loop."""

    def run(self, command: str, *, timeout: int) -> _Result:
        del command, timeout
        import time as _time

        _time.sleep(0.2)
        return _Result(json.dumps({"content": [], "isError": False}))


class _SlowSandbox:
    def __init__(self) -> None:
        self.commands = _SlowCommands()

    @classmethod
    def create(cls, **kwargs: object) -> _SlowSandbox:
        del kwargs
        return cls()

    def __enter__(self) -> _SlowSandbox:
        return self

    def __exit__(self, *_exc: object) -> None:
        return None


@pytest.mark.asyncio
async def test_e2b_driver_does_not_block_event_loop() -> None:
    """Regression — `call_tool` must dispatch the blocking E2B SDK calls off
    the event loop. Previously `sandbox_cls.create(...)` and
    `sandbox.commands.run(...)` ran directly inline in the coroutine, so a
    TIER_4_FULL_VM tool dispatch froze the entire process event loop for the
    duration — starving every other concurrent workflow, HITL retry, MCP
    health-check, and OTel export.

    Proven by racing a concurrent asyncio task's tick counter against the
    "blocking" sandbox call: a frozen loop means the counter cannot advance
    while `call_tool` is in flight.
    """
    import asyncio

    driver = E2BManagedFullVMToolRunnerExecutionDriver(
        command=("python", "-m", "tool_runner"),
        sandbox_cls=_SlowSandbox,
    )

    ticks = 0
    stop = False

    async def _ticker() -> None:
        nonlocal ticks
        while not stop:
            ticks += 1
            await asyncio.sleep(0.01)

    ticker_task = asyncio.create_task(_ticker())
    await driver.call_tool(
        mcp_client_host=cast(MCPClientHost, object()),
        sandbox_decision=_decision(),
        tool_id="echo",
        tool_args={"message": "ok"},
        idempotency_key="idem",
    )
    stop = True
    await ticker_task

    assert ticks >= 5, "event loop was frozen during the blocking sandbox call"


@pytest.mark.asyncio
async def test_e2b_driver_rejects_non_tier4_decision() -> None:
    driver = E2BManagedFullVMToolRunnerExecutionDriver(
        command=("python", "-m", "tool_runner"),
        sandbox_cls=_Sandbox,
    )

    with pytest.raises(ToolInvocationProtocolError, match="tier-4-full-vm"):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(SandboxTier.TIER_3_MICROVM),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )


@pytest.mark.asyncio
async def test_e2b_driver_reports_missing_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    def missing(_name: str) -> Any:
        raise ImportError("missing")

    monkeypatch.setattr(importlib, "import_module", missing)
    driver = E2BManagedFullVMToolRunnerExecutionDriver(command=("python", "-m", "runner"))

    with pytest.raises(ToolInvocationProtocolError, match="module 'e2b' is not importable"):
        await driver.call_tool(
            mcp_client_host=cast(MCPClientHost, object()),
            sandbox_decision=_decision(),
            tool_id="echo",
            tool_args={},
            idempotency_key="idem",
        )


def test_e2b_driver_rejects_non_json_stdout() -> None:
    driver = E2BManagedFullVMToolRunnerExecutionDriver(command=("runner",))

    with pytest.raises(ToolInvocationProtocolError, match="non-JSON stdout"):
        driver._parse_result(_Result("not json"))


def test_e2b_driver_rejects_nonzero_exit() -> None:
    driver = E2BManagedFullVMToolRunnerExecutionDriver(command=("runner",))

    with pytest.raises(ToolInvocationProtocolError, match="exited 42"):
        driver._parse_result(_Result("", exit_code=42, stderr="boom"))
