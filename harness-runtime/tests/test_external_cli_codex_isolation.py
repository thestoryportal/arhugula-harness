"""Codex CLI isolation slice C: a private cwd, and typed refusal when the JSONL shows tool use.

Provider-free: the parser tests script `CLIProcessResult` stdout; the cwd tests run the DEFAULT
Codex runner against a fake `codex` executable. The argv regression in test_external_cli_provider pins the installed CLI's tool-disable
switches. Parser refusal remains a second boundary for unexpected output.
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


# --- Codex delta HOLD: one closed envelope grammar over the whole stream ----------------------
#
# Grammar (from the canonical stream in this file and the recorded Codex `exec --json` shape;
# no live CLI was run): no-item lifecycle events are exactly `thread.started`, `turn.started`
# and `turn.completed`; item events are exactly `item.started|updated|completed` carrying a
# mapping item of a recognised type. Anything else refuses with a fixed label.

INNER_ANSWER = {"id": "i2", "type": "agent_message", "text": "LEAKED"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event",
    [
        {"type": ["item.completed"], "item": INNER_ANSWER},
        {"type": "command_execution", "item": INNER_ANSWER},
        {"type": "thread.started", "item": INNER_ANSWER},
    ],
    ids=["outer-type-list", "tool-like-outer-type", "thread-event-carrying-item"],
)
async def test_a_malformed_outer_envelope_is_refused_even_around_an_agent_message(
    event: dict[str, Any],
) -> None:
    with pytest.raises(ExternalCLIOutputError, match="tool item or unverifiable") as caught:
        await _dispatch(_events(event))

    assert "LEAKED" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event",
    [
        {"type": "agent_message", "text": "LEAKED"},
        {"type": "message", "text": "LEAKED"},
        {"type": "response", "text": "LEAKED"},
        {"text": "LEAKED"},
        {"type": "turn.completed", "text": "LEAKED"},
    ],
    ids=["agent_message", "message", "response", "untyped", "lifecycle-with-text"],
)
async def test_top_level_text_is_never_an_answer(event: dict[str, Any]) -> None:
    with pytest.raises(ExternalCLIOutputError):
        await _dispatch(_events(THREAD, TURN_STARTED, event, TURN_DONE))


@pytest.mark.asyncio
async def test_top_level_text_after_a_real_answer_is_refused_not_preferred() -> None:
    stdout = _events(THREAD, ANSWER, {"type": "message", "text": "LEAKED"}, TURN_DONE)

    with pytest.raises(ExternalCLIOutputError) as caught:
        await _dispatch(stdout)

    assert "LEAKED" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("stream", ["stdout", "stderr"])
async def test_a_nonzero_codex_exit_carries_no_cli_output(stream: str) -> None:
    secret = f"{SENTINEL} " + json.dumps(_tool_item("command_execution"))
    result = CLIProcessResult(
        exit_code=2,
        stdout=secret if stream == "stdout" else "",
        stderr=secret if stream == "stderr" else "",
    )
    adapter = await construct_codex_cli_adapter(_config(), runner=_FakeRunner([result]))

    with pytest.raises(ExternalCLICommandError) as caught:
        await adapter.dispatch_text(model="gpt-5", prompt="p")

    error = caught.value
    assert error.exit_code == 2 and "2" in str(error)
    assert SENTINEL not in str(error) and SENTINEL not in error.stdout + error.stderr
    assert not error.stdout and not error.stderr


@pytest.mark.asyncio
async def test_a_nonzero_exit_of_another_provider_keeps_its_diagnostic() -> None:
    from harness_runtime.lifecycle.external_cli_provider import construct_claude_code_cli_adapter

    config = ExternalCLIProviderConfig(
        provider="claude-code",
        kind="claude-code",
        command="claude",
        timeout_seconds=42.0,
        auth_check=False,
    )
    result = CLIProcessResult(exit_code=2, stdout="", stderr="claude said no")
    adapter = await construct_claude_code_cli_adapter(config, runner=_FakeRunner([result]))

    with pytest.raises(ExternalCLICommandError, match="claude said no"):
        await adapter.dispatch_text(model="m", prompt="p")


# --- boundaries of the grammar ------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("inner", ["agent_message", "reasoning"])
@pytest.mark.parametrize("phase", ["item.started", "item.updated", "item.completed"])
async def test_every_item_phase_with_a_recognised_inner_type_is_accepted(
    inner: str, phase: str
) -> None:
    event = {"type": phase, "item": {"id": "i", "type": inner, "text": "partial"}}

    assert await _dispatch(_events(THREAD, event, ANSWER, TURN_DONE)) == "OK"


@pytest.mark.asyncio
async def test_only_a_completed_agent_message_is_the_answer() -> None:
    updated = {"type": "item.updated", "item": {"id": "i2", "type": "agent_message", "text": "P"}}
    started = {"type": "item.started", "item": {"id": "i2", "type": "agent_message", "text": "S"}}

    assert await _dispatch(_events(THREAD, ANSWER, updated, started, TURN_DONE)) == "OK"
    with pytest.raises(ExternalCLIOutputError, match="agent text result"):
        await _dispatch(_events(THREAD, started, updated, REASONING, TURN_DONE))


@pytest.mark.asyncio
async def test_the_last_completed_agent_message_wins() -> None:
    later = {"type": "item.completed", "item": {"id": "i3", "type": "agent_message", "text": "B"}}

    assert await _dispatch(_events(THREAD, ANSWER, later, TURN_DONE)) == "B"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event",
    [
        {"type": "item.deleted", "item": INNER_ANSWER},
        {"type": "item", "item": INNER_ANSWER},
        {"type": None, "item": INNER_ANSWER},
        {"item": INNER_ANSWER},
        {"type": 7, "item": INNER_ANSWER},
        {"type": "turn.started", "item": None},
        {"type": "turn.completed", "item": INNER_ANSWER},
        {"type": "turn.failed"},
        {"type": "error", "message": "x"},
        {"type": "thread.resumed"},
    ],
    ids=[
        "unknown-item-phase",
        "bare-item",
        "null-type",
        "missing-type",
        "int-type",
        "lifecycle-item-null",
        "turn-carrying-item",
        "turn-failed",
        "error-event",
        "unknown-thread-event",
    ],
)
async def test_unknown_or_malformed_envelopes_fail_closed(event: dict[str, Any]) -> None:
    with pytest.raises(ExternalCLIOutputError, match="tool item or unverifiable") as caught:
        await _dispatch(_events(THREAD, event, ANSWER, TURN_DONE))

    assert "LEAKED" not in str(caught.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "item",
    [None, "str", 7, ["agent_message"], {"id": "i"}, {"type": None}, {"type": ["agent_message"]}],
    ids=["null", "string", "int", "list", "no-type", "null-type", "list-type"],
)
async def test_malformed_item_lifecycle_values_fail_closed(item: object) -> None:
    for phase in ("item.started", "item.updated", "item.completed"):
        with pytest.raises(ExternalCLIOutputError, match="malformed item event"):
            await _dispatch(_events(THREAD, {"type": phase, "item": item}, ANSWER))


@pytest.mark.asyncio
async def test_a_completed_agent_message_with_non_string_text_is_no_answer() -> None:
    bad = {"type": "item.completed", "item": {"id": "i", "type": "agent_message", "text": 7}}

    with pytest.raises(ExternalCLIOutputError, match="agent text result"):
        await _dispatch(_events(THREAD, bad, TURN_DONE))


# --- Codex JSON boundary HOLD: duplicate keys and non-finite numbers never reach the grammar --
#
# `json.loads` keeps the LAST duplicate key, so a tool item could vanish before classification.
# The Codex route parses the whole stream with duplicate rejection at every depth (after escape
# decoding), refuses non-finite numbers and malformed lines, and only then classifies.

_DUP_OUTER_ITEM = (
    '{"type":"item.completed","item":{"type":"command_execution","command":"SECRET"},'
    '"item":{"type":"agent_message","text":"LEAKED"}}'
)
_DUP_OUTER_TYPE = (
    '{"type":"command_execution","type":"item.completed",'
    '"item":{"type":"agent_message","text":"LEAKED"}}'
)
_ANSWER_LINE = json.dumps(ANSWER)


async def _refusal_of(stdout: str) -> ExternalCLIOutputError:
    with pytest.raises(ExternalCLIOutputError) as caught:
        await _dispatch(stdout)
    return caught.value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "line",
    [
        _DUP_OUTER_ITEM,
        _DUP_OUTER_TYPE,
        # duplicate only after JSON escape decoding: "type" is "type"
        '{"type":"item.completed","\\u0074ype":"command_execution",'
        '"item":{"type":"agent_message","text":"LEAKED"}}',
        '{"type":"item.completed","item":{"type":"agent_message","text":"LEAKED"},'
        '"\\u0069tem":{"type":"command_execution"}}',
        # nested duplicates, at depth 2 and inside an array of objects
        '{"type":"item.completed","item":{"type":"agent_message","text":"LEAKED","text":"B"}}',
        '{"type":"turn.completed","usage":{"input_tokens":1,"input_tokens":2}}',
        '{"type":"turn.completed","usage":{"rows":[{"a":1},{"b":1,"b":2}]}}',
    ],
    ids=[
        "sealed-duplicate-item",
        "sealed-duplicate-type",
        "escaped-duplicate-type",
        "escaped-duplicate-item",
        "nested-duplicate-text",
        "nested-duplicate-usage",
        "duplicate-inside-array",
    ],
)
async def test_a_duplicate_object_key_at_any_depth_is_refused(line: str) -> None:
    error = await _refusal_of(f"{json.dumps(THREAD)}\n{line}\n")

    assert "LEAKED" not in str(error) and "SECRET" not in str(error)
    assert "duplicate" in str(error)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value", ["NaN", "Infinity", "-Infinity", "1e999", "-1e999"], ids=lambda v: v.strip("-")
)
async def test_a_non_finite_number_is_refused(value: str) -> None:
    line = '{"type":"turn.completed","usage":{"input_tokens":' + value + "}}"
    error = await _refusal_of(f"{_ANSWER_LINE}\n{line}\n")

    assert "non-finite" in str(error)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "line",
    [
        f'{{"type":"{SENTINEL}"',
        f'{{"type":"item.completed" {SENTINEL}}}',
        f"[{json.dumps(ANSWER)}]",
        f'"{SENTINEL}"',
        SENTINEL,
        "7",
        "null",
    ],
    ids=["truncated", "junk", "array", "string", "bare-word", "number", "null"],
)
async def test_a_malformed_or_non_object_line_after_a_safe_answer_refuses_the_stream(
    line: str,
) -> None:
    error = await _refusal_of(f"{_ANSWER_LINE}\n{line}\n")

    assert SENTINEL not in str(error) and "OK" not in str(error)
    assert "line 2" in str(error)


@pytest.mark.asyncio
async def test_a_late_duplicate_key_line_refuses_an_earlier_safe_answer() -> None:
    error = await _refusal_of(f"{_ANSWER_LINE}\n{_DUP_OUTER_ITEM}\n")

    assert "line 2" in str(error) and "LEAKED" not in str(error)


@pytest.mark.asyncio
async def test_a_canonical_stream_with_nested_and_repeated_shapes_is_still_accepted() -> None:
    usage = {"type": "turn.completed", "usage": {"input_tokens": 1, "rows": [{"a": 1}, {"a": 2}]}}
    stdout = _events(THREAD, TURN_STARTED, REASONING, ANSWER, usage) + "\n\n"

    assert await _dispatch(stdout) == "OK"


@pytest.mark.asyncio
async def test_a_raw_unicode_line_separator_inside_a_json_string_is_not_a_line_break() -> None:
    answer = {"type": "item.completed", "item": {"type": "agent_message", "text": "a b"}}

    assert await _dispatch(json.dumps(answer, ensure_ascii=False) + "\n") == "a b"


def test_the_shared_line_parser_and_its_last_key_wins_behavior_are_unchanged() -> None:
    from harness_runtime.lifecycle.external_cli_provider import (
        _parse_json_lines,  # pyright: ignore[reportPrivateUsage]
    )

    assert _parse_json_lines('{"a":1,"a":2}\n', "x")[0]["a"] == 2


@pytest.mark.asyncio
async def test_pathologically_deep_nesting_is_refused_without_a_crash() -> None:
    line = '{"type":"turn.completed","usage":' + "[" * 100_000 + "]" * 100_000 + "}"

    error = await _refusal_of(f"{_ANSWER_LINE}\n{line}\n")

    assert "line 2" in str(error) and "not valid JSON" in str(error)
