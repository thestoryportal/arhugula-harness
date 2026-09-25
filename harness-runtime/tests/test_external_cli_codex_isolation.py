"""Codex CLI isolation slice C: a private cwd, and typed refusal when the JSONL shows tool use.

Provider-free: the parser tests script `CLIProcessResult` stdout; the cwd tests run the DEFAULT
Codex runner against a fake `codex` executable. Nothing here proves the real CLI cannot start
a tool: refusal is detection after the fact, and the CLI's own tool/MCP switches stay HELD.
"""

from __future__ import annotations

import json
import logging
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from harness_runtime.lifecycle.external_cli_provider import (
    CLIProcessResult,
    ExternalCLICommandError,
    ExternalCLIOutputError,
    ExternalCLIProcessTimeout,
    construct_codex_cli_adapter,
)
from harness_runtime.types import ExternalCLIProviderConfig


@dataclass
class _FakeRunner:
    results: list[CLIProcessResult]

    async def run(
        self,
        argv: tuple[str, ...],
        *,
        stdin: str,
        timeout_seconds: float,
        on_wire: Callable[[], None] | None = None,
    ) -> CLIProcessResult:
        if on_wire is not None:
            on_wire()
        return self.results.pop(0)


def _config(command: str = "codex", timeout_seconds: float = 42.0) -> ExternalCLIProviderConfig:
    return ExternalCLIProviderConfig(
        provider="codex",
        kind="codex",
        command=command,
        timeout_seconds=timeout_seconds,
        auth_check=False,
    )


def _events(*events: dict[str, Any]) -> str:
    return "".join(json.dumps(event) + "\n" for event in events)


THREAD = {"type": "thread.started", "thread_id": "t"}
TURN_STARTED = {"type": "turn.started"}
REASONING = {"type": "item.completed", "item": {"id": "i0", "type": "reasoning", "text": "hm"}}
ANSWER = {"type": "item.completed", "item": {"id": "i2", "type": "agent_message", "text": "OK"}}
TURN_DONE = {"type": "turn.completed", "usage": {"input_tokens": 1}}


def _tool_item(item_type: object, phase: str = "item.completed") -> dict[str, Any]:
    return {"type": phase, "item": {"id": "i1", "type": item_type, "command": "ls"}}


async def _dispatch(stdout: str, exit_code: int = 0) -> str:
    runner = _FakeRunner([CLIProcessResult(exit_code=exit_code, stdout=stdout, stderr="boom")])
    adapter = await construct_codex_cli_adapter(_config(), runner=runner)
    return (await adapter.dispatch_text(model="gpt-5", prompt="p")).text


# --- tool evidence is a typed failure ---------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item_type",
    ["command_execution", "mcp_tool_call", "file_change", "web_search", "a_future_item_kind"],
)
@pytest.mark.parametrize("phase", ["item.started", "item.completed"])
async def test_a_tool_item_before_the_agent_message_is_refused(item_type: str, phase: str) -> None:
    stdout = _events(THREAD, TURN_STARTED, _tool_item(item_type, phase), ANSWER, TURN_DONE)

    with pytest.raises(ExternalCLIOutputError, match="tool item"):
        await _dispatch(stdout)


@pytest.mark.asyncio
async def test_a_tool_item_after_the_agent_message_is_refused_too() -> None:
    with pytest.raises(ExternalCLIOutputError, match="tool item"):
        await _dispatch(_events(THREAD, ANSWER, _tool_item("command_execution"), TURN_DONE))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item",
    [{"id": "i1"}, {"id": "i1", "type": 7}, {"id": "i1", "type": ["command_execution"]}, "str"],
    ids=["no-type", "non-string-type", "unhashable-type", "non-mapping-item"],
)
async def test_an_item_of_unrecognisable_type_fails_closed(item: object) -> None:
    stdout = _events(THREAD, {"type": "item.completed", "item": item}, ANSWER)

    with pytest.raises(ExternalCLIOutputError, match="tool item"):
        await _dispatch(stdout)


@pytest.mark.asyncio
async def test_the_refusal_names_no_command_or_output_from_the_tool() -> None:
    stdout = _events(
        {"type": "item.completed", "item": {"type": "command_execution", "command": "cat SECRET"}},
        ANSWER,
    )

    with pytest.raises(ExternalCLIOutputError) as caught:
        await _dispatch(stdout)

    assert "SECRET" not in str(caught.value) and "command_execution" in str(caught.value)


# --- Codex HOLD codex-cli-isolation-codex-1: malformed item events, untrusted type text ------

SENTINEL = "SECRET_SENTINEL"


@pytest.mark.asyncio
@pytest.mark.parametrize("phase", ["item.started", "item.completed"])
@pytest.mark.parametrize("shape", ["item-missing", "item-null"])
async def test_an_item_event_without_an_item_fails_closed(phase: str, shape: str) -> None:
    event: dict[str, Any] = (
        {"type": phase} if shape == "item-missing" else {"type": phase, "item": None}
    )

    with pytest.raises(ExternalCLIOutputError, match="malformed item event"):
        await _dispatch(_events(THREAD, event, ANSWER, TURN_DONE))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item_type",
    [f"command_execution {SENTINEL}", f"a_future_item_kind_{SENTINEL}", f"{SENTINEL}" * 10],
    ids=["known-prefix", "unknown", "long"],
)
async def test_the_refusal_never_echoes_an_unrecognised_item_type(item_type: str) -> None:
    with pytest.raises(ExternalCLIOutputError) as caught:
        await _dispatch(_events(THREAD, _tool_item(item_type), ANSWER))

    assert SENTINEL not in str(caught.value)
    assert "unrecognised item type" in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item", [{"id": "i1", "type": 7}, "str"], ids=["non-string-type", "non-mapping"]
)
async def test_a_malformed_item_is_classified_without_echoing_it(item: object) -> None:
    with pytest.raises(ExternalCLIOutputError, match="malformed item event"):
        await _dispatch(_events({"type": "item.completed", "item": item}, ANSWER))


# --- ordinary output stays valid ----------------------------------------------------------------


@pytest.mark.asyncio
async def test_lifecycle_reasoning_and_agent_message_events_are_accepted() -> None:
    stdout = _events(
        THREAD,
        TURN_STARTED,
        {"type": "item.started", "item": {"id": "i0", "type": "reasoning"}},
        REASONING,
        ANSWER,
        TURN_DONE,
    )

    assert await _dispatch(stdout) == "OK"


@pytest.mark.asyncio
async def test_a_nonzero_exit_stays_a_command_error_not_an_output_refusal() -> None:
    with pytest.raises(ExternalCLICommandError):
        await _dispatch(_events(_tool_item("command_execution"), ANSWER), exit_code=2)


@pytest.mark.asyncio
async def test_output_without_an_agent_message_is_still_an_output_error() -> None:
    with pytest.raises(ExternalCLIOutputError, match="agent text result"):
        await _dispatch(_events(THREAD, REASONING, TURN_DONE))


# --- the default runner uses a fresh empty private cwd ------------------------------------------


def _fake_codex(tmp_path: Path, *, sleeper: bool = False) -> tuple[str, Path]:
    script = tmp_path / "fake-codex"
    records = tmp_path / "codex-records.jsonl"
    script.write_text(
        f"#!{sys.executable}\n"
        "import json, pathlib, stat, sys, time\n"
        "cwd = pathlib.Path.cwd()\n"
        "record = {'cwd': str(cwd), 'mode': stat.S_IMODE(cwd.stat().st_mode), "
        "'entries': sorted(p.name for p in cwd.iterdir())}\n"
        f"with open({str(records)!r}, 'a') as stream: stream.write(json.dumps(record) + '\\n')\n"
        + ("time.sleep(300)\n" if sleeper else "")
        + "sys.stdin.read()\n"
        "print(json.dumps({'type': 'item.completed', "
        "'item': {'type': 'agent_message', 'text': 'OK'}}))\n"
    )
    script.chmod(0o700)
    return str(script), records


def _recorded(records: Path) -> dict[str, Any]:
    return json.loads(records.read_text().splitlines()[0])


@pytest.mark.asyncio
async def test_the_default_codex_runner_runs_in_a_fresh_empty_private_cwd_removed_afterwards(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "SECRET.txt").write_text("harness workspace content")
    monkeypatch.chdir(workspace)
    command, records = _fake_codex(tmp_path)
    adapter = await construct_codex_cli_adapter(_config(command))

    result = await adapter.dispatch_text(model="gpt-5", prompt="p")

    assert result.text == "OK"
    seen = _recorded(records)
    assert Path(seen["cwd"]).resolve() != workspace.resolve()
    assert seen["entries"] == [] and seen["mode"] == 0o700
    assert not Path(seen["cwd"]).exists()  # removed once the process settled
    assert (workspace / "SECRET.txt").exists()


@pytest.mark.asyncio
async def test_the_private_cwd_is_removed_after_a_timeout_settles_the_process(
    tmp_path: Path,
) -> None:
    command, records = _fake_codex(tmp_path, sleeper=True)
    adapter = await construct_codex_cli_adapter(_config(command, timeout_seconds=1.0))

    with pytest.raises(ExternalCLIProcessTimeout):
        await adapter.dispatch_text(model="gpt-5", prompt="p")

    assert not Path(_recorded(records)["cwd"]).exists()


@pytest.mark.asyncio
async def test_a_failed_scratch_removal_is_reported_without_replacing_the_outcome(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import harness_runtime.lifecycle.external_cli_provider as provider

    command, _records = _fake_codex(tmp_path)
    real_rmtree = shutil.rmtree

    def failing_rmtree(path: str) -> None:
        real_rmtree(path)
        raise OSError("secret-stderr-sentinel")

    monkeypatch.setattr(provider.shutil, "rmtree", failing_rmtree)
    adapter = await construct_codex_cli_adapter(_config(command))

    with caplog.at_level(logging.WARNING):
        result = await adapter.dispatch_text(model="gpt-5", prompt="p")

    assert result.text == "OK"
    assert "Codex scratch directory removal failed" in caplog.text
    assert "secret-stderr-sentinel" not in caplog.text
