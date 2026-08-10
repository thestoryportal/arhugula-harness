"""Regression tests for Claude-to-Codex workflow parity."""

from __future__ import annotations

import errno
import importlib.util
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / ".codex" / "hooks" / "codex_hook_adapter.py"
RUNTIME_WITNESS = ROOT / "tools" / "codex_hook_runtime_witness.py"
# This module exercises normal adapters even when invoked from an isolated reviewer.
os.environ.pop("HARNESS_CODEX_REVIEW_ISOLATED", None)


def test_live_runtime_witness_is_provider_free_and_operator_runnable() -> None:
    source = RUNTIME_WITNESS.read_text(encoding="utf-8")
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")

    assert 'base_url = "http://127.0.0.1:' in source
    assert "requires_openai_auth = false" in source
    assert '"PreCompact",' in source
    assert '"PostCompact",' in source
    assert 'evidence["codex_version"]' in source
    assert 'for tool in ("Bash", "apply_patch")' in source
    assert "codex-hook-runtime-witness:" in justfile
    assert "/usr/bin/python3 tools/codex_hook_runtime_witness.py" in justfile


def test_hook_contract_documentation_preserves_codex_semantics() -> None:
    readme = (ROOT / ".codex" / "hooks" / "README.md").read_text(encoding="utf-8")
    parity = (ROOT / ".codex" / "notes" / "claude-codex-parity.md").read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    normalized_parity = " ".join(parity.split())
    plain_readme = normalized_readme.replace("`", "")
    plain_parity = normalized_parity.replace("`", "")

    assert "`PermissionRequest` decides approval" in readme
    assert "An allow carrying `updatedInput` is instead denied" in readme
    assert "allow-side rewrite as a structured deny" in normalized_readme
    assert "compact-context" in readme
    assert "equivalent effect" in readme
    assert "`PostCompact` | shared reinjection producer through the Codex adapter" in readme
    assert "`PostCompact` | Direct" not in readme
    assert (
        "real `PreToolUse:permission-guard` and `PostCompact:post-compact` adapters"
        in normalized_readme
    )
    assert (
        "the remaining handlers for SessionStart, PreToolUse, PostToolUse, PreCompact, "
        "Stop, and SessionEnd are recorder substitutes"
    ) in plain_readme
    assert "including PermissionRequest, are omitted from the live fixture" in plain_readme
    assert (
        "PostCompact translation validity is covered by shared-producer and "
        "adapter behavioral tests" in normalized_readme
    )
    assert "real `PreToolUse` permission and `PostCompact` adapters" in parity
    assert (
        "either real adapter is absent, duplicated, registered under a different event, "
        "or its canonical command shape changes"
    ) in normalized_parity
    assert "does not claim to detect general matcher, timeout, or status drift" in plain_parity


def _runtime_witness_module():
    spec = importlib.util.spec_from_file_location(
        "codex_hook_runtime_witness_test", RUNTIME_WITNESS
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _hook_commands(payload: dict[str, Any]) -> list[str]:
    return [
        hook["command"]
        for groups in payload["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]


def test_runtime_witness_preserves_real_contract_adapters(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    recorder = tmp_path / "record_hook.py"

    hooks, real_handlers = witness._witness_hooks(recorder)

    real_command = (
        "/usr/bin/python3 "
        f"{shlex.quote(str(ROOT / '.codex' / 'hooks' / 'codex_hook_adapter.py'))} permission-guard"
    )
    post_compact_command = (
        "/usr/bin/python3 "
        f"{shlex.quote(str(ROOT / '.codex' / 'hooks' / 'codex_hook_adapter.py'))} post-compact"
    )
    recorder_command = f"{shlex.quote(sys.executable)} {shlex.quote(str(recorder))}"
    commands = _hook_commands(hooks)
    project_hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    expected_handler_count = sum(
        len(group["hooks"])
        for event in witness.TARGET_EVENTS
        for group in project_hooks["hooks"][event]
    )

    assert set(hooks["hooks"]) == set(witness.TARGET_EVENTS)
    assert len(commands) == expected_handler_count
    assert real_handlers == ["PostCompact:post-compact", "PreToolUse:permission-guard"]
    assert commands.count(real_command) == 1
    assert commands.count(post_compact_command) == 1
    assert all(
        command in {real_command, post_compact_command, recorder_command} for command in commands
    )
    assert all(
        command == recorder_command
        for command in commands
        if command not in {real_command, post_compact_command}
    )


@pytest.mark.parametrize("match_count", [0, 2])
def test_runtime_witness_refuses_missing_or_ambiguous_permission_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, match_count: int
) -> None:
    witness = _runtime_witness_module()
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    permission_hook = payload["hooks"]["PreToolUse"][-1]["hooks"][0]
    payload["hooks"]["PreToolUse"][-1]["hooks"] = [permission_hook] * match_count
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(witness, "ROOT", tmp_path)

    expected = sorted(
        [witness.REAL_POST_COMPACT_HANDLER] + [witness.REAL_PERMISSION_HANDLER] * match_count
    )
    with pytest.raises(RuntimeError) as exc_info:
        witness._witness_hooks(tmp_path / "record_hook.py")
    assert f"found {expected}" in str(exc_info.value)


@pytest.mark.parametrize("match_count", [0, 2])
def test_runtime_witness_refuses_missing_or_ambiguous_post_compact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, match_count: int
) -> None:
    witness = _runtime_witness_module()
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    post_compact_hook = payload["hooks"]["PostCompact"][0]["hooks"][0]
    payload["hooks"]["PostCompact"][0]["hooks"] = [post_compact_hook] * match_count
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(witness, "ROOT", tmp_path)

    expected = sorted(
        [witness.REAL_POST_COMPACT_HANDLER] * match_count + [witness.REAL_PERMISSION_HANDLER]
    )
    with pytest.raises(RuntimeError) as exc_info:
        witness._witness_hooks(tmp_path / "record_hook.py")
    assert f"found {expected}" in str(exc_info.value)


def test_runtime_witness_refuses_permission_guard_outside_witness_events(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    permission_hook = payload["hooks"]["PreToolUse"][-1]["hooks"].pop()
    payload["hooks"]["PreCompact"][0]["hooks"].append(permission_hook)
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(witness, "ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="permission-guard"):
        witness._witness_hooks(tmp_path / "record_hook.py")


def test_runtime_witness_refuses_permission_guard_command_shape_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    permission_hook = payload["hooks"]["PreToolUse"][-1]["hooks"][0]
    permission_hook["command"] = f"env FOO=1 {permission_hook['command']}"
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(witness, "ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="command shape"):
        witness._witness_hooks(tmp_path / "record_hook.py")


def test_runtime_witness_refuses_post_compact_command_shape_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    hook = payload["hooks"]["PostCompact"][0]["hooks"][0]
    hook["command"] = f"env FOO=1 {hook['command']}"
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex" / "hooks.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(witness, "ROOT", tmp_path)

    with pytest.raises(RuntimeError, match="command shape"):
        witness._witness_hooks(tmp_path / "record_hook.py")


def test_runtime_witness_environment_uses_synthetic_project_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    stripped_variables = (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "HARNESS_CODEX_REVIEW_ISOLATED",
    )
    for name in stripped_variables:
        monkeypatch.setenv(name, "must-not-reach-witness")

    environment = witness._witness_environment(tmp_path / "codex-home", tmp_path / "repo")

    assert environment["CODEX_HOME"] == str(tmp_path / "codex-home")
    assert environment["HARNESS_LOOP"] == "1"
    assert environment["CLAUDE_PROJECT_DIR"] == str(tmp_path / "repo")
    assert environment["HARNESS_CODEX_HOOK_WITNESS"] == "1"
    assert environment["HARNESS_CODEX_HOOK_WITNESS_FILE"] == str(
        tmp_path / "repo" / ".codex-hook-adapter-invocations"
    )
    assert not set(stripped_variables) & set(environment)


def test_hook_witness_trace_requires_sentinel_and_exact_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter_module()
    expected = tmp_path / adapter.WITNESS_TRACE_NAME
    other = tmp_path / "pyproject.toml"
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setenv(adapter.WITNESS_TRACE_ENV, str(other))

    assert adapter.record_witness_invocation("permission-guard")
    assert not other.exists()

    monkeypatch.setenv(adapter.WITNESS_MODE_ENV, "1")
    assert not adapter.record_witness_invocation("permission-guard")
    assert not other.exists()

    monkeypatch.setenv(adapter.WITNESS_TRACE_ENV, str(expected))
    assert adapter.record_witness_invocation("permission-guard")
    assert expected.read_text(encoding="utf-8") == "permission-guard\n"


def test_runtime_witness_resets_loopback_state() -> None:
    witness = _runtime_witness_module()
    witness._LoopbackResponsesHandler.request_count = 7
    witness._LoopbackResponsesHandler.errors = ["stale error"]

    witness._reset_loopback_state()

    assert witness._LoopbackResponsesHandler.request_count == 0
    assert witness._LoopbackResponsesHandler.errors == []


@pytest.mark.parametrize(
    ("stdout", "stderr"),
    [
        (diagnostic, "")
        for diagnostic in (
            "unsupported permissionDecision:allow",
            "PreToolUse Failed",
            "invalid PostCompact hook JSON output",
            "PostCompact Failed",
        )
    ]
    + [
        ("", diagnostic)
        for diagnostic in (
            "unsupported permissionDecision:allow",
            "PreToolUse Failed",
            "invalid PostCompact hook JSON output",
            "PostCompact Failed",
        )
    ],
)
def test_runtime_witness_rejects_prohibited_host_diagnostics(stdout: str, stderr: str) -> None:
    witness = _runtime_witness_module()

    with pytest.raises(RuntimeError, match="prohibited host diagnostic"):
        witness._assert_no_prohibited_host_diagnostics(stdout, stderr)


def test_runtime_witness_requires_real_handler_host_completions() -> None:
    witness = _runtime_witness_module()
    complete = "hook: PreToolUse Blocked\nhook: PostCompact Completed\n"

    witness._assert_real_handler_host_completions(complete)
    with pytest.raises(RuntimeError, match="PostCompact Completed"):
        witness._assert_real_handler_host_completions("hook: PreToolUse Blocked\n")
    with pytest.raises(RuntimeError, match="PreToolUse Blocked"):
        witness._assert_real_handler_host_completions("hook: PostCompact Completed\n")


def test_runtime_witness_requires_a_canonical_codex_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    witness = _runtime_witness_module()
    monkeypatch.setattr(
        witness.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["codex", "--version"], 0, "codex-cli 0.146.0\n", ""
        ),
    )

    assert witness._installed_codex_version("codex") == "codex-cli 0.146.0"


def test_live_runtime_witness_reports_empty_hook_stream(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text("", encoding="utf-8")

    with pytest.raises(RuntimeError, match="no hook events"):
        witness._assert_witness(
            tmp_path,
            events_path,
            0,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def test_live_runtime_witness_retries_directory_not_empty_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    calls = 0
    real_rmtree = witness.shutil.rmtree

    def racing_rmtree(path: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise OSError(errno.ENOTEMPTY, "Directory not empty", path)
        real_rmtree(path)

    monkeypatch.setattr(witness.shutil, "rmtree", racing_rmtree)
    witness._remove_temp_tree(tmp_path, attempts=2, delay=0)

    assert calls == 2
    assert not tmp_path.exists()


def _valid_runtime_witness_fixture(tmp_path: Path) -> tuple[Any, Path, list[dict[str, str]]]:
    witness = _runtime_witness_module()
    events = [
        {"hook_event_name": "SessionStart", "session_id": "one"},
        {"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": "one"},
        {"hook_event_name": "PreCompact", "session_id": "one", "trigger": "auto"},
        {"hook_event_name": "SessionStart", "session_id": "one", "source": "compact"},
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": "one"},
        {"hook_event_name": "PreToolUse", "tool_name": "apply_patch", "session_id": "one"},
        {"hook_event_name": "PostToolUse", "tool_name": "apply_patch", "session_id": "one"},
        {"hook_event_name": "Stop", "session_id": "one"},
        {"hook_event_name": "SessionEnd", "session_id": "one"},
    ]
    (tmp_path / "shell-marker.txt").write_text("codex-shell-witness", encoding="utf-8")
    (tmp_path / "patch-marker.txt").write_text("codex-patch-witness\n", encoding="utf-8")
    (tmp_path / ".codex-hook-adapter-invocations").write_text(
        "permission-guard\npost-compact-output:123\npermission-guard\npermission-guard\n",
        encoding="utf-8",
    )
    return witness, tmp_path / "events.jsonl", events


def _write_runtime_events(path: Path, events: list[dict[str, str]]) -> None:
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")


def test_live_runtime_witness_accepts_complete_fixture(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    evidence = witness._assert_witness(
        tmp_path,
        events_path,
        5,
        real_handlers=list(witness.REAL_HANDLERS),
    )

    assert evidence["status"] == "PASS"
    assert evidence["real_handlers"] == ["PostCompact:post-compact", "PreToolUse:permission-guard"]
    assert evidence["executed_handlers"] == [
        "permission-guard",
        "post-compact-output:123",
        "permission-guard",
        "permission-guard",
    ]
    assert evidence["post_compact_output_bytes"] == 123


@pytest.mark.parametrize("trace_entry", ["post-compact-output:0", "post-compact-output:nope"])
def test_live_runtime_witness_rejects_empty_or_invalid_post_compact_output(
    tmp_path: Path, trace_entry: str
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)
    (tmp_path / ".codex-hook-adapter-invocations").write_text(
        f"permission-guard\n{trace_entry}\npermission-guard\npermission-guard\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="PostCompact output"):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def test_live_runtime_witness_rejects_missing_adapter_execution_trace(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)
    (tmp_path / ".codex-hook-adapter-invocations").unlink()

    with pytest.raises(RuntimeError, match="execution trace"):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def test_live_runtime_witness_rejects_denied_command_effect(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)
    (tmp_path / "denied-marker.txt").write_text("guard failed open", encoding="utf-8")

    with pytest.raises(RuntimeError, match="denied Bash tool effect completed"):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


@pytest.mark.parametrize("real_handlers", [[], ["PreToolUse:another-handler"]])
def test_live_runtime_witness_rejects_untrusted_real_handler_evidence(
    tmp_path: Path, real_handlers: list[str]
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="real handler evidence"):
        witness._assert_witness(tmp_path, events_path, 5, real_handlers=real_handlers)


@pytest.mark.parametrize("missing", ["SessionStart", "PreCompact", "Stop", "SessionEnd"])
def test_live_runtime_witness_rejects_each_missing_lifecycle_event(
    tmp_path: Path, missing: str
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(
        events_path, [event for event in events if event["hook_event_name"] != missing]
    )

    with pytest.raises(RuntimeError):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


@pytest.mark.parametrize(
    ("phase", "tool"),
    [(phase, tool) for phase in ("PreToolUse", "PostToolUse") for tool in ("Bash", "apply_patch")],
)
def test_live_runtime_witness_rejects_each_missing_tool_phase(
    tmp_path: Path, phase: str, tool: str
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(
        events_path,
        [
            event
            for event in events
            if (event["hook_event_name"], event.get("tool_name")) != (phase, tool)
        ],
    )

    with pytest.raises(RuntimeError, match="missing tool hook dispatch"):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def test_live_runtime_witness_rejects_wrong_request_count(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="expected 5"):
        witness._assert_witness(
            tmp_path,
            events_path,
            2,
            real_handlers=list(witness.REAL_HANDLERS),
        )


@pytest.mark.parametrize("marker", ["shell-marker.txt", "patch-marker.txt"])
def test_live_runtime_witness_rejects_each_missing_effect(tmp_path: Path, marker: str) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)
    (tmp_path / marker).unlink()

    with pytest.raises((RuntimeError, FileNotFoundError)):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def test_live_runtime_witness_rejects_multiple_session_identities(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    events[-1]["session_id"] = "two"
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="multiple sessions"):
        witness._assert_witness(
            tmp_path,
            events_path,
            5,
            real_handlers=list(witness.REAL_HANDLERS),
        )


def _adapter_module():
    spec = importlib.util.spec_from_file_location("codex_hook_adapter_test", ADAPTER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(os.name != "posix", reason="process-group witness requires POSIX")
def test_hook_adapter_timeout_terminates_descendant_process_tree(tmp_path: Path) -> None:
    adapter = _adapter_module()
    child_pid_file = tmp_path / "child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

    started = time.monotonic()
    proc = adapter.run_bounded(
        [
            "/bin/sh",
            "-c",
            (
                '(trap "" TERM; sleep 30) & child=$!; '
                'printf "%s" "$child" > "$CHILD_PID_FILE"; wait "$child"'
            ),
        ],
        cwd=tmp_path,
        timeout=2,
        env=env,
    )
    elapsed = time.monotonic() - started

    assert proc.returncode == 124
    assert elapsed < 4
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"hook timeout left descendant alive: pid={child_pid}")


@pytest.mark.skipif(os.name != "posix", reason="process-group witness requires POSIX")
def test_hook_adapter_success_terminates_background_descendant(tmp_path: Path) -> None:
    adapter = _adapter_module()
    adapter.TERMINATION_GRACE_SECONDS = 0.2
    child_pid_file = tmp_path / "successful-child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

    proc = adapter.run_bounded(
        [
            "/bin/sh",
            "-c",
            (
                '(trap "" TERM; sleep 30) & child=$!; '
                'printf "%s" "$child" > "$CHILD_PID_FILE"; exit 0'
            ),
        ],
        cwd=tmp_path,
        timeout=5,
        env=env,
    )

    assert proc.returncode == 0
    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"successful hook left descendant alive: pid={child_pid}")


@pytest.mark.skipif(os.name != "posix", reason="signal-mask witness requires POSIX")
def test_hook_adapter_restores_original_signal_mask_in_producer(tmp_path: Path) -> None:
    adapter = _adapter_module()

    proc = adapter.run_bounded(
        [
            sys.executable,
            "-c",
            (
                "import json, signal; "
                "print(json.dumps([int(value) for value in "
                "signal.pthread_sigmask(signal.SIG_BLOCK, [])]))"
            ),
        ],
        cwd=tmp_path,
        timeout=5,
        env=os.environ.copy(),
    )

    assert proc.returncode == 0, proc.stderr
    inherited_mask = set(json.loads(proc.stdout))
    assert inherited_mask.isdisjoint(map(int, adapter.MANAGED_TERMINATION_SIGNALS))


@pytest.mark.skipif(os.name != "posix", reason="signal delivery witness requires POSIX")
def test_hook_adapter_timeout_delivers_cooperative_sigterm(tmp_path: Path) -> None:
    adapter = _adapter_module()
    marker = tmp_path / "producer-terminated"
    env = os.environ.copy()
    env["TERMINATION_MARKER"] = str(marker)

    proc = adapter.run_bounded(
        [
            sys.executable,
            "-c",
            (
                "import os, pathlib, signal, time\n"
                "def handle_term(*_args):\n"
                "    pathlib.Path(os.environ['TERMINATION_MARKER']).write_text('term')\n"
                "    raise SystemExit(0)\n"
                "signal.signal(signal.SIGTERM, handle_term)\n"
                "time.sleep(30)\n"
            ),
        ],
        cwd=tmp_path,
        timeout=0.2,
        env=env,
    )

    assert proc.returncode == 124
    assert marker.read_text(encoding="utf-8") == "term"


def test_hook_adapter_interrupt_terminates_detached_process_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter_module()
    adapter.TERMINATION_GRACE_SECONDS = 0

    class InterruptingProcess:
        pid = 434343
        returncode: int | None = None

        def wait(self, timeout: float) -> int:
            _ = timeout
            if self.returncode is None:
                raise KeyboardInterrupt
            return self.returncode

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.returncode = -15

        def kill(self) -> None:
            self.returncode = -9

    process = InterruptingProcess()
    signals: list[tuple[int, signal.Signals]] = []
    monkeypatch.setattr(adapter.subprocess, "Popen", lambda *_args, **_kwargs: process)
    monkeypatch.setattr(
        adapter.os,
        "killpg",
        lambda pid, sent_signal: signals.append((pid, sent_signal)) if sent_signal != 0 else None,
    )

    with pytest.raises(KeyboardInterrupt):
        adapter.run_bounded(["hook"], cwd=tmp_path, timeout=30, env=os.environ.copy())

    assert signals == [
        (process.pid, adapter.signal.SIGTERM),
        (process.pid, adapter.signal.SIGKILL),
    ]
    assert process.returncode == -15


def test_hook_adapter_teardown_tolerates_permission_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "TERMINATION_GRACE_SECONDS", 0)
    attempted: list[str] = []

    class PermissionDeniedProcess:
        pid = 454545

        def poll(self) -> None:
            return None

        def terminate(self) -> None:
            attempted.append("terminate")
            raise PermissionError

        def kill(self) -> None:
            attempted.append("kill")
            raise PermissionError

        def wait(self, timeout: float) -> int:
            raise subprocess.TimeoutExpired("hook", timeout)

    monkeypatch.setattr(
        adapter.os,
        "killpg",
        lambda _pid, sent_signal: (
            attempted.append(f"killpg:{sent_signal}") or (_ for _ in ()).throw(PermissionError)
        ),
    )

    adapter.terminate_bounded(PermissionDeniedProcess())
    assert attempted == [
        f"killpg:{signal.SIGTERM}",
        "terminate",
        f"killpg:{signal.SIGKILL}",
        "kill",
    ]


def test_hook_adapter_preserves_unnamed_inherited_signal_numbers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "can_manage_signal_handlers", lambda: True)
    monkeypatch.setattr(
        adapter.signal,
        "pthread_sigmask",
        lambda _operation, _signals: {999},
    )

    assert adapter.block_termination_signals() == {999}


def test_hook_adapter_teardown_replays_deferred_sigterm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "TERMINATION_GRACE_SECONDS", 0)

    class RepeatedSignalProcess:
        pid = 464646
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            signal.raise_signal(signal.SIGTERM)
            self.returncode = -signal.SIGTERM

        def kill(self) -> None:
            self.returncode = -signal.SIGKILL

        def wait(self, timeout: float) -> int:
            _ = timeout
            assert self.returncode is not None
            return self.returncode

    monkeypatch.setattr(adapter.os, "killpg", lambda _pid, _sent_signal: None)
    previous_sigterm = signal.signal(signal.SIGTERM, adapter.handle_termination_signal)
    previous_sigint = signal.getsignal(signal.SIGINT)
    try:
        process = RepeatedSignalProcess()
        with pytest.raises(adapter.TerminationRequested):
            adapter.terminate_bounded(process)
        assert signal.getsignal(signal.SIGTERM) is adapter.handle_termination_signal
        assert signal.getsignal(signal.SIGINT) is previous_sigint
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        signal.signal(signal.SIGINT, previous_sigint)

    assert process.returncode == -signal.SIGTERM


def test_hook_adapter_defers_sigterm_until_spawn_handle_is_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "TERMINATION_GRACE_SECONDS", 0)

    class SpawnedProcess:
        pid = 474747
        returncode: int | None = None

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            self.returncode = -signal.SIGTERM

        def kill(self) -> None:
            self.returncode = -signal.SIGKILL

        def wait(self, timeout: float) -> int:
            _ = timeout
            assert self.returncode is not None
            return self.returncode

    process = SpawnedProcess()

    def signal_during_spawn(*_args: object, **_kwargs: object) -> SpawnedProcess:
        signal.raise_signal(signal.SIGTERM)
        return process

    monkeypatch.setattr(adapter.subprocess, "Popen", signal_during_spawn)
    monkeypatch.setattr(adapter.os, "killpg", lambda _pid, _sent_signal: None)
    previous_sigterm = signal.signal(signal.SIGTERM, adapter.handle_termination_signal)
    previous_sigint = signal.getsignal(signal.SIGINT)
    try:
        with pytest.raises(adapter.TerminationRequested):
            adapter.run_bounded(["hook"], cwd=tmp_path, timeout=30, env=os.environ.copy())
        assert signal.getsignal(signal.SIGTERM) is adapter.handle_termination_signal
        assert signal.getsignal(signal.SIGINT) is previous_sigint
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)
        signal.signal(signal.SIGINT, previous_sigint)

    assert process.returncode == -signal.SIGTERM


@pytest.mark.skipif(os.name != "posix", reason="signal teardown witness requires POSIX")
def test_hook_adapter_sigterm_cleans_live_producer_process_group(tmp_path: Path) -> None:
    adapter = _adapter_module()
    cleanup_timeout = 2 * adapter.TERMINATION_GRACE_SECONDS + 3
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    producer = fake_bin / "uv"
    producer.write_text(
        "#!/bin/sh\n"
        'printf "%s" "$$" > "$PRODUCER_PID_FILE"\n'
        "trap '' TERM\n"
        "while :; do sleep 1; done\n",
        encoding="utf-8",
    )
    producer.chmod(0o755)
    producer_pid_file = tmp_path / "producer.pid"
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["PRODUCER_PID_FILE"] = str(producer_pid_file)
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    payload = {
        "cwd": str(tmp_path),
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m test"},
    }
    adapter_process = subprocess.Popen(
        [sys.executable, str(ADAPTER), "pre-commit"],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    producer_pid: int | None = None
    producer_pgid: int | None = None
    producer_survived = False
    returncode: int | None = None
    adapter_stdout = ""
    adapter_stderr = ""
    try:
        assert adapter_process.stdin is not None
        adapter_process.stdin.write(json.dumps(payload))
        adapter_process.stdin.close()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and not producer_pid_file.exists():
            time.sleep(0.02)
        assert producer_pid_file.exists(), "adapter never started its hook producer"
        producer_pid = int(producer_pid_file.read_text(encoding="utf-8"))
        producer_pgid = os.getpgid(producer_pid)

        adapter_process.send_signal(signal.SIGTERM)
        returncode = adapter_process.wait(timeout=cleanup_timeout)
        assert adapter_process.stdout is not None
        assert adapter_process.stderr is not None
        adapter_stdout = adapter_process.stdout.read()
        adapter_stderr = adapter_process.stderr.read()
        deadline = time.monotonic() + cleanup_timeout
        while time.monotonic() < deadline:
            try:
                os.kill(producer_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            producer_survived = True
    finally:
        if adapter_process.poll() is None:
            adapter_process.kill()
            adapter_process.wait(timeout=3)
        if producer_pgid is not None:
            try:
                os.killpg(producer_pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if adapter_process.stdout is not None:
            adapter_process.stdout.close()
        if adapter_process.stderr is not None:
            adapter_process.stderr.close()

    assert returncode == -signal.SIGTERM
    assert not producer_survived, f"SIGTERM left producer group alive: pgid={producer_pid}"
    assert adapter_stderr == ""
    assert adapter_stdout == ""


def _commands(event: str, matcher: str) -> list[str]:
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    return [
        hook["command"]
        for group in payload["hooks"].get(event, [])
        if group.get("matcher", "") == matcher
        for hook in group["hooks"]
    ]


def _event_commands(event: str) -> list[str]:
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    return [hook["command"] for group in payload["hooks"][event] for hook in group["hooks"]]


@pytest.mark.parametrize(
    ("event", "matcher", "fragments"),
    [
        (
            "SessionStart",
            "startup|resume|clear|compact",
            ["codex-session-start.sh"],
        ),
        (
            "PreToolUse",
            "Bash|apply_patch|Edit|Write",
            ["pre_tool_use_policy.py"],
        ),
        (
            "PreToolUse",
            "Bash",
            [
                "precmd-clear-cache.sh",
                "codex_hook_adapter.py pre-commit",
            ],
        ),
        ("PreToolUse", "*", ["codex_hook_adapter.py", "permission-guard"]),
        (
            "PermissionRequest",
            "*",
            ["permission_request.py", "permission-guard.sh"],
        ),
        ("PreCompact", "*", ["precompact-checkpoint.sh"]),
        ("PostCompact", "*", ["codex_hook_adapter.py", "post-compact"]),
        ("SessionEnd", "*", ["codex-session-end.sh"]),
        (
            "Stop",
            "",
            ["stop_gate.py", "stop-gate.sh", "git-arc-guard.sh", "stop-loop.sh"],
        ),
        ("SubagentStart", "*", ["subagent-validate.sh"]),
        ("SubagentStop", "*", ["subagent-validate.sh"]),
        (
            "UserPromptSubmit",
            "",
            ["prompt-context.sh", "skill-activation-check.sh", "prompt-lint.sh"],
        ),
        (
            "PostToolUse",
            "Bash",
            ["roadmap-audit/post-merge-refresh.sh"],
        ),
        ("PostToolUse", "*", ["codex_hook_adapter.py post-tool-use"]),
    ],
)
def test_codex_hooks_cover_supported_claude_lifecycle(
    event: str, matcher: str, fragments: list[str]
) -> None:
    commands = _commands(event, matcher)
    for fragment in fragments:
        assert any(fragment in command.replace('"', "") for command in commands), (
            event,
            fragment,
            commands,
        )


def test_codex_hook_map_tracks_every_canonical_claude_hook_command() -> None:
    claude = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))["hooks"]
    codex = json.loads((ROOT / ".codex/hooks.json").read_text(encoding="utf-8"))["hooks"]
    adapter = ADAPTER.read_text(encoding="utf-8")
    codex_commands = "\n".join(
        hook["command"] for groups in codex.values() for group in groups for hook in group["hooks"]
    )
    wrappers = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "tools" / "hooks" / "codex-session-start.sh",
            ROOT / "tools" / "hooks" / "codex-session-end.sh",
        ]
        if path.exists()
    )
    implementation = f"{codex_commands}\n{adapter}\n{wrappers}"
    wrapper_targets = {
        "tools/roadmap-audit/session-start.sh": "roadmap-audit/session-start.sh",
        "tools/hooks/loop-gc.sh": "loop-gc.sh",
        "tools/hooks/session-end-cleanup.sh": "session-end-cleanup.sh",
    }

    assert set(claude) - set(codex) == {"PostToolUseFailure", "StopFailure"}
    for groups in claude.values():
        for group in groups:
            for hook in group["hooks"]:
                command = hook["command"]
                prefix = "${CLAUDE_PROJECT_DIR}/"
                if command.startswith(prefix):
                    relative = command.removeprefix(prefix)
                    if relative in wrapper_targets:
                        assert wrapper_targets[relative] in wrappers
                    else:
                        assert relative in implementation
                else:
                    assert command == "uv run pyright && git rev-parse --show-toplevel"
                    assert '["uv", "run", "pyright"]' in adapter
                    assert '["git", "rev-parse", "--show-toplevel"]' in adapter


def _run_adapter(
    mode: str,
    payload: dict[str, object],
    *,
    cwd: Path,
    path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(cwd)
    if path is not None:
        env["PATH"] = path
    return subprocess.run(
        [sys.executable, str(ADAPTER), mode],
        cwd=cwd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )


def _checkpoint_repo(tmp_path: Path, session_id: str = "session-a") -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    harness = tmp_path / ".harness"
    checkpoints = harness / ".checkpoints"
    checkpoints.mkdir(parents=True)
    (harness / "roadmap_status.md").write_text(
        "# Test roadmap\n\n## Next action\n\nU-TEST-01\n",
        encoding="utf-8",
    )
    (checkpoints / f"precompact-latest-{session_id}.md").write_text(
        "test pre-compaction checkpoint\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", ".harness/roadmap_status.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "test checkpoint repository"], cwd=tmp_path, check=True)
    return tmp_path


def test_post_compact_adapter_emits_only_universal_output(tmp_path: Path) -> None:
    repo = _checkpoint_repo(tmp_path)
    checkpoint = ".harness/.checkpoints/precompact-latest-session-a.md"

    proc = _run_adapter(
        "post-compact",
        {"hook_event_name": "PostCompact", "session_id": "session-a", "cwd": str(repo)},
        cwd=repo,
    )

    assert proc.returncode == 0, proc.stderr
    output = json.loads(proc.stdout)
    assert set(output) == {"systemMessage"}
    assert checkpoint in output["systemMessage"]


@pytest.mark.parametrize(
    ("producer_result", "expected_detail"),
    [
        (subprocess.CompletedProcess(["hook"], 1, "", "producer failed"), "producer failed"),
        (subprocess.CompletedProcess(["hook"], 0, "not json", ""), "not json"),
        (subprocess.CompletedProcess(["hook"], 0, "[]", ""), "non-object JSON"),
        (
            subprocess.CompletedProcess(
                ["hook"],
                0,
                '{"hookSpecificOutput":'
                '{"hookEventName":"SessionStart","additionalContext":"wrong event"}}',
                "",
            ),
            "wrong hook event",
        ),
        (
            subprocess.CompletedProcess(
                ["hook"],
                0,
                '{"hookSpecificOutput":{"hookEventName":"PostCompact"}}',
                "",
            ),
            "no usable context",
        ),
        (
            subprocess.CompletedProcess(
                ["hook"],
                0,
                '{"hookSpecificOutput":{"hookEventName":"PostCompact","additionalContext":"  "}}',
                "",
            ),
            "no usable context",
        ),
    ],
)
def test_post_compact_adapter_preserves_invalid_producer_as_valid_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    producer_result: subprocess.CompletedProcess[str],
    expected_detail: str,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: producer_result,
    )

    assert adapter.post_compact({"cwd": str(ROOT)}) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    output = json.loads(captured.out)
    assert set(output) == {"systemMessage"}
    assert output["systemMessage"].startswith("post-compact adapter: ")
    assert expected_detail in output["systemMessage"]


def test_compact_context_prefers_valid_context_over_advisory_system_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: {
            "systemMessage": "advisory warning",
            "hookSpecificOutput": {
                "hookEventName": "PostCompact",
                "additionalContext": "checkpoint context",
            },
        },
    )

    assert adapter.compact_context({"cwd": str(ROOT)}) == "checkpoint context"


def test_compact_context_mode_returns_raw_model_context(tmp_path: Path) -> None:
    repo = _checkpoint_repo(tmp_path)
    checkpoint = ".harness/.checkpoints/precompact-latest-session-a.md"

    proc = _run_adapter(
        "compact-context",
        {
            "hook_event_name": "SessionStart",
            "source": "compact",
            "session_id": "session-a",
            "cwd": str(repo),
        },
        cwd=repo,
    )

    assert proc.returncode == 0, proc.stderr
    assert checkpoint in proc.stdout
    assert "hookSpecificOutput" not in proc.stdout


def test_compact_adapter_modes_use_separate_producer_timeouts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    timeouts: list[float] = []
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **kwargs: (
            timeouts.append(kwargs["timeout"])
            or subprocess.CompletedProcess(
                ["hook"],
                0,
                '{"hookSpecificOutput":{"hookEventName":"PostCompact","additionalContext":"context"}}',
                "",
            )
        ),
    )

    assert adapter.post_compact({"cwd": str(ROOT)}) == 0
    assert adapter.print_compact_context({"cwd": str(ROOT)}) == 0
    assert timeouts == [20, 2]


def test_permission_guard_uses_eight_second_producer_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    timeouts: list[float] = []
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **kwargs: (
            timeouts.append(kwargs["timeout"])
            or subprocess.CompletedProcess(
                ["hook"],
                0,
                '{"hookSpecificOutput":{"hookEventName":"PreToolUse",'
                '"permissionDecision":"allow"}}',
                "",
            )
        ),
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    assert timeouts == [8]


def test_nested_hook_supervisors_finish_before_outer_deadlines() -> None:
    adapter = _adapter_module()
    hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    permission_host_timeout = hooks["hooks"]["PreToolUse"][-1]["hooks"][0]["timeout"]
    post_compact_host_timeout = hooks["hooks"]["PostCompact"][0]["hooks"][0]["timeout"]

    assert (
        adapter.PERMISSION_PRODUCER_TIMEOUT_SECONDS + 2 * adapter.TERMINATION_GRACE_SECONDS
        < permission_host_timeout
    )
    assert (
        adapter.COMPACT_SESSION_PRODUCER_TIMEOUT_SECONDS + 2 * adapter.TERMINATION_GRACE_SECONDS < 4
    )
    assert (
        adapter.POST_COMPACT_PRODUCER_TIMEOUT_SECONDS + 2 * adapter.TERMINATION_GRACE_SECONDS
        < post_compact_host_timeout
    )


@pytest.mark.parametrize(
    "producer_result",
    [
        subprocess.CompletedProcess(["hook"], 1, "", "producer failed"),
        subprocess.CompletedProcess(["hook"], 0, "not json", ""),
        subprocess.CompletedProcess(["hook"], 0, "[]", ""),
        subprocess.CompletedProcess(
            ["hook"],
            0,
            '{"hookSpecificOutput":'
            '{"hookEventName":"SessionStart","additionalContext":"wrong event"}}',
            "",
        ),
        subprocess.CompletedProcess(
            ["hook"],
            0,
            '{"hookSpecificOutput":{"hookEventName":"PostCompact"}}',
            "",
        ),
        subprocess.CompletedProcess(
            ["hook"],
            0,
            '{"hookSpecificOutput":{"hookEventName":"PostCompact","additionalContext":"  "}}',
            "",
        ),
    ],
)
def test_compact_context_raw_mode_rejects_invalid_producer_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    producer_result: subprocess.CompletedProcess[str],
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "run_bounded", lambda *_args, **_kwargs: producer_result)

    assert adapter.print_compact_context({"cwd": str(ROOT)}) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err


def test_compact_context_raw_mode_preserves_timeout_status(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["hook"], 124, "", "command timed out after 2 seconds"
        ),
    )

    assert adapter.print_compact_context({"cwd": str(ROOT)}) == 124
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "timed out" in captured.err


def _loop_active_git_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    harness = tmp_path / ".harness"
    harness.mkdir()
    (harness / ".loop-active").touch()


def test_permission_guard_adapter_suppresses_bare_pretool_allow(tmp_path: Path) -> None:
    _loop_active_git_repo(tmp_path)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Grep",
        "tool_input": {"path": str(tmp_path / "src")},
    }

    proc = _run_adapter("permission-guard", payload, cwd=tmp_path)

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""


def test_permission_guard_adapter_preserves_supported_pretool_deny(tmp_path: Path) -> None:
    _loop_active_git_repo(tmp_path)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push --force origin main"},
    }

    proc = _run_adapter("permission-guard", payload, cwd=tmp_path)

    assert proc.returncode == 0, proc.stderr
    output = json.loads(proc.stdout)
    assert set(output) == {"hookSpecificOutput"}
    decision = output["hookSpecificOutput"]
    assert set(decision) == {
        "hookEventName",
        "permissionDecision",
        "permissionDecisionReason",
    }
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert decision["permissionDecisionReason"]


def test_permission_guard_adapter_normalizes_supported_pretool_deny(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: {
            "systemMessage": "Claude-only advisory",
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "unsafe command",
                "claudeOnlyField": True,
            },
        },
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    assert json.loads(capsys.readouterr().out) == {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "unsafe command",
        }
    }


def test_permission_guard_dispatch_denies_internal_adapter_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "permission-guard"])
    monkeypatch.setattr(adapter, "read_payload", lambda: {"hook_event_name": "PreToolUse"})
    monkeypatch.setattr(
        adapter,
        "permission_guard",
        lambda _payload: (_ for _ in ()).throw(OSError("temporary stream unavailable")),
    )

    assert adapter.dispatch() == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    decision = json.loads(captured.out)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert "internal failure" in decision["permissionDecisionReason"]


def test_permission_guard_dispatch_does_not_duplicate_an_emitted_deny(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "permission-guard"])
    monkeypatch.setattr(adapter, "read_payload", lambda: {"hook_event_name": "PreToolUse"})

    def emit_then_fail(_payload: dict[str, object]) -> int:
        adapter.emit_permission_deny("original denial")
        raise OSError("failure after emission")

    monkeypatch.setattr(adapter, "permission_guard", emit_then_fail)

    assert adapter.dispatch() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hookSpecificOutput"]["permissionDecisionReason"] == "original denial"


def test_permission_guard_dispatch_resets_emission_state_between_calls(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "permission-guard"])
    monkeypatch.setattr(adapter, "read_payload", lambda: {"hook_event_name": "PreToolUse"})
    monkeypatch.setattr(
        adapter,
        "permission_guard",
        lambda _payload: adapter.emit_permission_deny("first denial"),
    )
    assert adapter.dispatch() == 0
    assert json.loads(capsys.readouterr().out)["hookSpecificOutput"]

    monkeypatch.setattr(
        adapter,
        "permission_guard",
        lambda _payload: (_ for _ in ()).throw(OSError("second call failed")),
    )
    assert adapter.dispatch() == 0
    second = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert "internal failure" in second["permissionDecisionReason"]


def test_permission_guard_main_converts_termination_to_deny(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "permission-guard"])
    monkeypatch.setattr(
        adapter,
        "dispatch",
        lambda: (_ for _ in ()).throw(adapter.TerminationRequested(signal.SIGTERM)),
    )
    original_emit_permission_deny = adapter.emit_permission_deny

    def emit_with_repeated_sigterm(reason: str) -> int:
        signal.raise_signal(signal.SIGTERM)
        return original_emit_permission_deny(reason)

    monkeypatch.setattr(adapter, "emit_permission_deny", emit_with_repeated_sigterm)

    assert adapter.main() == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    decision = json.loads(captured.out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "terminated by signal" in decision["permissionDecisionReason"]


@pytest.mark.skipif(os.name != "posix", reason="signal masking requires POSIX")
@pytest.mark.parametrize(
    "termination_signal",
    [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT],
)
def test_permission_guard_deny_emission_is_atomic_against_termination(
    termination_signal: signal.Signals, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "permission-guard"])

    class SignalDuringWrite:
        def __init__(self) -> None:
            self.parts: list[str] = []
            self.signaled = False
            self.flushed = False

        def write(self, value: str) -> int:
            self.parts.append(value)
            if value == "\n" and not self.signaled:
                self.signaled = True
                signal.raise_signal(termination_signal)
            return len(value)

        def flush(self) -> None:
            self.flushed = True

    stdout = SignalDuringWrite()
    monkeypatch.setattr(adapter.sys, "stdout", stdout)
    monkeypatch.setattr(
        adapter,
        "dispatch",
        lambda: adapter.emit_permission_deny("blocked during cancellation"),
    )

    assert adapter.main() == 0
    assert stdout.flushed
    decision = json.loads("".join(stdout.parts))["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert decision["permissionDecisionReason"] == "blocked during cancellation"


def test_permission_guard_adapter_denies_non_decision_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: {"systemMessage": "shared producer failed: exact detail"},
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    decision = json.loads(captured.out)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert decision["permissionDecisionReason"] == "shared producer failed: exact detail"


def test_hook_adapter_bounds_producer_diagnostics(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["hook"], 9, "", "x" * 5000),
    )

    result = adapter.run_claude_hook("tools/hooks/failing.sh", {}, ROOT)

    assert isinstance(result, adapter.HookFailure)
    assert result.message.endswith("...")
    assert len(result.message) < 4100


def test_hook_adapter_uses_stdout_when_stderr_is_only_whitespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["hook"], 9, "producer stdout detail", "  \n"
        ),
    )

    result = adapter.run_claude_hook("tools/hooks/failing.sh", {}, ROOT)

    assert isinstance(result, adapter.HookFailure)
    assert result.message.endswith("producer stdout detail")


def test_permission_guard_adapter_denies_allow_with_malformed_updated_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": "not-an-object",
            }
        },
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    decision = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "updatedInput" in decision["permissionDecisionReason"]


def test_permission_guard_adapter_denies_non_object_shared_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["hook"], 0, "[]", ""),
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    decision = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "non-object JSON" in decision["permissionDecisionReason"]


@pytest.mark.parametrize(
    "shared_response",
    [
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
            }
        },
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
            }
        },
        {"hookSpecificOutput": {"hookEventName": "PostToolUse"}},
    ],
)
def test_permission_guard_adapter_normalizes_invalid_decisions_to_deny(
    shared_response: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "run_claude_hook", lambda *_args, **_kwargs: shared_response)

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert output["hookSpecificOutput"]["permissionDecisionReason"]


def test_permission_guard_adapter_denies_allow_with_dict_updated_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    shared_response = {
        "systemMessage": "Claude-only advisory",
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {"command": "git status"},
            "claudeOnlyField": True,
        },
    }
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: shared_response,
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    decision = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "updatedInput" in decision["permissionDecisionReason"]


def test_post_compact_dispatch_normalizes_internal_failure_to_universal_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter.sys, "argv", [str(ADAPTER), "post-compact"])
    monkeypatch.setattr(
        adapter,
        "read_payload",
        lambda: (_ for _ in ()).throw(OSError("stdin unavailable")),
    )

    assert adapter.dispatch() == 0
    output = json.loads(capsys.readouterr().out)
    assert set(output) == {"systemMessage"}
    assert "internal failure" in output["systemMessage"]


def test_post_tool_adapter_captures_nonzero_bash_result(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "PostToolUse",
        "session_id": "session-a",
        "tool_name": "Bash",
        "tool_response": {"exit_code": 1, "output": "failed"},
    }

    first = _run_adapter("post-tool-use", payload, cwd=tmp_path)
    second = _run_adapter("post-tool-use", payload, cwd=tmp_path)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    rows = [
        json.loads(line)
        for line in (tmp_path / ".harness" / "session-issues.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert [row["event"] for row in rows] == [
        "PostToolUseFailure",
        "PostToolUseFailure",
    ]
    context = json.loads(second.stdout)["hookSpecificOutput"]
    assert context["hookEventName"] == "PostToolUse"
    assert "recurring failure" in context["additionalContext"]


def test_post_tool_adapter_does_not_misclassify_textual_success(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "mcp__example__read",
        "tool_response": "model-facing successful text",
    }

    proc = _run_adapter("post-tool-use", payload, cwd=tmp_path)

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""
    assert not (tmp_path / ".harness" / "session-issues.jsonl").exists()


def test_post_tool_adapter_preserves_underlying_hook_failure_message() -> None:
    adapter = _adapter_module()

    assert adapter.additional_context({"systemMessage": "underlying hook failed"}) == (
        "underlying hook failed"
    )


def test_post_tool_adapter_lints_python_files_from_apply_patch(tmp_path: Path) -> None:
    target = tmp_path / "sample.py"
    target.write_text("print('x')\n", encoding="utf-8")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    ruff = bin_dir / "ruff"
    ruff.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = check ]; then echo 'sample.py:1:1: E999 broken'; exit 1; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    ruff.chmod(0o755)
    payload = {
        "hook_event_name": "PostToolUse",
        "tool_name": "apply_patch",
        "tool_input": {"command": "*** Update File: sample.py\n@@\n"},
        "tool_response": {"status": "completed"},
    }

    proc = _run_adapter(
        "post-tool-use",
        payload,
        cwd=tmp_path,
        path=f"{bin_dir}:{os.environ['PATH']}",
    )

    assert proc.returncode == 0, proc.stderr
    context = json.loads(proc.stdout)["hookSpecificOutput"]
    assert context["hookEventName"] == "PostToolUse"
    assert "ruff findings on sample.py" in context["additionalContext"]


@pytest.mark.parametrize("command", ["git commit -m test", "rtk git commit -m test"])
def test_pre_commit_adapter_blocks_when_pyright_fails(tmp_path: Path, command: str) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text("#!/bin/sh\necho 'pyright failed' >&2\nexit 1\n", encoding="utf-8")
    uv.chmod(0o755)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": str(tmp_path),
    }

    proc = _run_adapter(
        "pre-commit",
        payload,
        cwd=tmp_path,
        path=f"{bin_dir}:{os.environ['PATH']}",
    )

    assert proc.returncode == 2
    assert "pyright failed" in proc.stderr


def test_pre_commit_adapter_uses_repo_safe_uv_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text(
        '#!/bin/sh\nprintf \'%s\' "${UV_CACHE_DIR:-}" > "$PWD/uv-cache-observed"\n',
        encoding="utf-8",
    )
    uv.chmod(0o755)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m test"},
        "cwd": str(tmp_path),
    }
    monkeypatch.delenv("UV_CACHE_DIR", raising=False)

    proc = _run_adapter(
        "pre-commit",
        payload,
        cwd=tmp_path,
        path=f"{bin_dir}:{os.environ['PATH']}",
    )

    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "uv-cache-observed").read_text(encoding="utf-8") == (
        "/tmp/arhugula-uv-cache"
    )


def test_pre_commit_adapter_blocks_outside_a_git_worktree(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    uv = bin_dir / "uv"
    uv.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    uv.chmod(0o755)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git commit -m test"},
        "cwd": str(tmp_path),
    }

    proc = _run_adapter(
        "pre-commit",
        payload,
        cwd=tmp_path,
        path=f"{bin_dir}:{os.environ['PATH']}",
    )

    assert proc.returncode == 2
    assert "not a git repository" in proc.stderr


def test_isolated_review_session_start_skips_shared_context_checkpoint() -> None:
    env = os.environ.copy()
    env["HARNESS_CODEX_REVIEW_ISOLATED"] = "1"

    proc = subprocess.run(
        [sys.executable, str(ROOT / ".codex" / "hooks" / "session_start.py")],
        cwd=ROOT,
        input=json.dumps({"session_id": "review-session", "cwd": str(ROOT)}),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""
    assert "Codex context guard" not in proc.stdout


def test_session_start_wrapper_registers_lease_before_posture(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = {"session_id": "wrapper-session", "cwd": str(tmp_path)}
    env = os.environ.copy()
    env["HARNESS_CODEX_REVIEW_ISOLATED"] = "1"
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    start = subprocess.run(
        ["bash", str(ROOT / "tools" / "hooks" / "codex-session-start.sh")],
        cwd=tmp_path,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert start.returncode == 0, start.stderr
    assert start.stdout == ""
    leases = list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))
    assert [path.name for path in leases] == ["session-wrapper-session.lease"]

    end = subprocess.run(
        ["bash", str(ROOT / "tools" / "hooks" / "codex-session-end.sh")],
        cwd=tmp_path,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )
    assert end.returncode == 0, end.stderr
    assert not list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))


def test_session_start_bounds_advisory_hygiene(tmp_path: Path) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    posture_dir = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    for name in ("codex-session-start.sh", "session-lease.sh", "lib.sh"):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    lib_path = hook_dir / "lib.sh"
    lib_source = lib_path.read_text(encoding="utf-8")
    assert "hook_bounded() {" in lib_source
    lib_path.write_text(
        lib_source.replace("hook_bounded() {", "_real_hook_bounded() {", 1)
        + """
hook_bounded() {
  if [ "${3##*/}" = "loop-gc.sh" ]; then
    printf '%s' "$1" > "$HYGIENE_BOUND_MARKER"
  fi
  _real_hook_bounded "$@"
}
""",
        encoding="utf-8",
    )
    (posture_dir / "session_start.py").write_text(
        "print('bounded posture')\n",
        encoding="utf-8",
    )
    (roadmap_dir / "session-start.sh").write_text(
        '#!/bin/sh\nprintf \'%s\\n\' \'{"hookSpecificOutput":{"additionalContext":"roadmap"}}\'\n',
        encoding="utf-8",
    )
    hygiene_term_marker = tmp_path / "hygiene-term"
    hygiene_bound_marker = tmp_path / "hygiene-bound"
    (hook_dir / "loop-gc.sh").write_text(
        "#!/bin/sh\n"
        'trap \'printf term > "$HYGIENE_TERM_MARKER"; '
        'kill "$sleeper" 2>/dev/null; wait "$sleeper" 2>/dev/null; exit 0\' TERM\n'
        'sleep 30 &\nsleeper=$!\nwait "$sleeper"\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = json.dumps(
        {"source": "startup", "session_id": "bounded-hygiene", "cwd": str(tmp_path)}
    )
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "HARNESS_SESSION_START_HYGIENE_SECONDS": "1",
            "HYGIENE_BOUND_MARKER": str(hygiene_bound_marker),
            "HYGIENE_TERM_MARKER": str(hygiene_term_marker),
        }
    )

    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert hygiene_bound_marker.read_text(encoding="utf-8") == "1"
    assert hygiene_term_marker.read_text(encoding="utf-8") == "term"
    assert "bounded posture" in proc.stdout
    assert "roadmap" in proc.stdout


def test_compaction_round_trip_routes_real_checkpoint_to_both_codex_consumers(
    tmp_path: Path,
) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    codex_hooks = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    codex_hooks.mkdir(parents=True)
    for name in (
        "codex-session-start.sh",
        "session-lease.sh",
        "lib.sh",
        "precompact-checkpoint.sh",
        "postcompact-reinject.sh",
    ):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    shutil.copy2(ADAPTER, codex_hooks / "codex_hook_adapter.py")
    (codex_hooks / "session_start.py").write_text("print('posture')\n", encoding="utf-8")
    (roadmap_dir / "session-start.sh").write_text(
        '#!/bin/sh\nprintf \'%s\\n\' \'{"hookSpecificOutput":{"additionalContext":"roadmap"}}\'\n',
        encoding="utf-8",
    )
    (hook_dir / "loop-gc.sh").write_text(
        '#!/bin/sh\nprintf \'%s\\n\' \'{"hookSpecificOutput":{"additionalContext":"hygiene"}}\'\n',
        encoding="utf-8",
    )
    harness = tmp_path / ".harness"
    checkpoints = harness / ".checkpoints"
    checkpoints.mkdir(parents=True)
    (harness / "roadmap_status.md").write_text(
        "# Test roadmap\n\n## Next action\n\nU-TEST-01\n",
        encoding="utf-8",
    )
    checkpoint = ".harness/.checkpoints/precompact-latest-wrapper-session.md"
    for script in (
        roadmap_dir / "session-start.sh",
        hook_dir / "loop-gc.sh",
        hook_dir / "precompact-checkpoint.sh",
    ):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", ".harness/roadmap_status.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "wrapper base"], cwd=tmp_path, check=True)
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    precompact = subprocess.run(
        ["bash", str(hook_dir / "precompact-checkpoint.sh")],
        cwd=tmp_path,
        input=json.dumps(
            {
                "hook_event_name": "PreCompact",
                "trigger": "auto",
                "session_id": "wrapper-session",
                "cwd": str(tmp_path),
            }
        ),
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
        env=env,
    )
    assert precompact.returncode == 0, precompact.stderr
    assert (tmp_path / checkpoint).is_file()

    post_compact = _run_adapter(
        "post-compact",
        {
            "hook_event_name": "PostCompact",
            "session_id": "wrapper-session",
            "cwd": str(tmp_path),
        },
        cwd=tmp_path,
    )
    assert post_compact.returncode == 0, post_compact.stderr
    assert checkpoint in json.loads(post_compact.stdout)["systemMessage"]

    def run_session(source: str, session_id: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["bash", str(hook_dir / "codex-session-start.sh")],
            cwd=tmp_path,
            input=json.dumps(
                {
                    "hook_event_name": "SessionStart",
                    "source": source,
                    "session_id": session_id,
                    "cwd": str(tmp_path),
                }
            ),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env=env,
        )

    startup = run_session("startup", "wrapper-startup")
    compact = run_session("compact", "wrapper-session")

    assert startup.returncode == 0, startup.stderr
    assert compact.returncode == 0, compact.stderr
    startup_context = json.loads(startup.stdout)["hookSpecificOutput"]["additionalContext"]
    compact_context = json.loads(compact.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "[CONTEXT] Post-compaction" not in startup_context
    assert checkpoint not in startup_context
    for earlier, later in zip(
        ("posture", "roadmap", "hygiene", "[CONTEXT] Post-compaction"),
        ("roadmap", "hygiene", "[CONTEXT] Post-compaction", checkpoint),
        strict=True,
    ):
        assert compact_context.index(earlier) < compact_context.index(later)
    leases = sorted(
        path.name for path in (tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease")
    )
    assert leases == ["session-wrapper-session.lease", "session-wrapper-startup.lease"]


def test_session_start_wrapper_routes_compact_producer_failure(tmp_path: Path) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    codex_hooks = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    codex_hooks.mkdir(parents=True)
    for name in (
        "codex-session-start.sh",
        "session-lease.sh",
        "lib.sh",
        "postcompact-reinject.sh",
    ):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    shutil.copy2(ADAPTER, codex_hooks / "codex_hook_adapter.py")
    (hook_dir / "postcompact-reinject.sh").write_text(
        "#!/bin/sh\necho 'compact producer failed' >&2\nexit 9\n",
        encoding="utf-8",
    )
    (codex_hooks / "session_start.py").write_text("print('posture')\n", encoding="utf-8")
    (roadmap_dir / "session-start.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (hook_dir / "loop-gc.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    for script in (
        hook_dir / "postcompact-reinject.sh",
        roadmap_dir / "session-start.sh",
        hook_dir / "loop-gc.sh",
    ):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=json.dumps(
            {
                "hook_event_name": "SessionStart",
                "source": "compact",
                "session_id": "producer-failure",
                "cwd": str(tmp_path),
            }
        ),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert "compact producer failed" in proc.stderr
    context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "posture" in context
    assert "compact checkpoint reinjection unavailable" in context
    leases = list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))
    assert len(leases) == 1


def test_session_start_wrapper_degrades_compact_producer_timeout(tmp_path: Path) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    codex_hooks = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    codex_hooks.mkdir(parents=True)
    for name in (
        "codex-session-start.sh",
        "session-lease.sh",
        "lib.sh",
        "postcompact-reinject.sh",
    ):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    shutil.copy2(ADAPTER, codex_hooks / "codex_hook_adapter.py")
    (hook_dir / "postcompact-reinject.sh").write_text(
        "#!/bin/sh\nsleep 30\n",
        encoding="utf-8",
    )
    (codex_hooks / "session_start.py").write_text("print('posture')\n", encoding="utf-8")
    (roadmap_dir / "session-start.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (hook_dir / "loop-gc.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    for script in (
        hook_dir / "postcompact-reinject.sh",
        roadmap_dir / "session-start.sh",
        hook_dir / "loop-gc.sh",
    ):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=json.dumps(
            {
                "hook_event_name": "SessionStart",
                "source": "compact",
                "session_id": "producer-timeout",
                "cwd": str(tmp_path),
            }
        ),
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "posture" in context
    assert "compact checkpoint reinjection timed out" in context
    assert "timed out" in proc.stderr
    leases = list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))
    assert len(leases) == 1


def test_session_start_wrapper_routes_compact_through_four_second_bound() -> None:
    start = (ROOT / "tools" / "hooks" / "codex-session-start.sh").read_text(encoding="utf-8")

    assert 'hook_bounded "$' + '{HARNESS_SESSION_START_COMPACT_SECONDS:-4}"' in start
    assert "compact_rc=0" in start
    assert ") || compact_rc=$?" in start


@pytest.mark.parametrize(
    ("source_payload", "label"),
    [
        ({"source": 1}, "number"),
        ({"source": False}, "bool"),
        ({"source": []}, "list"),
        ({"source": {}}, "dict"),
    ],
)
def test_session_start_wrapper_routes_compact_rejects_invalid_source(
    tmp_path: Path, source_payload: dict[str, object], label: str
) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    posture_dir = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    for name in ("codex-session-start.sh", "session-lease.sh", "lib.sh"):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    (posture_dir / "session_start.py").write_text("print('posture')\n", encoding="utf-8")
    (roadmap_dir / "session-start.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (hook_dir / "loop-gc.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    for script in (roadmap_dir / "session-start.sh", hook_dir / "loop-gc.sh"):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = {
        "hook_event_name": "SessionStart",
        "session_id": f"invalid-source-{label}",
        "cwd": str(tmp_path),
        **source_payload,
    }
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 2, proc.stderr
    assert "invalid SessionStart payload source" in proc.stderr
    assert not list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))


@pytest.mark.parametrize(
    ("source_payload", "label"),
    [({}, "missing"), ({"source": None}, "null")],
)
def test_session_start_wrapper_routes_compact_accepts_absent_or_null_source(
    tmp_path: Path, source_payload: dict[str, object], label: str
) -> None:
    hook_dir = tmp_path / "tools" / "hooks"
    roadmap_dir = tmp_path / "tools" / "roadmap-audit"
    posture_dir = tmp_path / ".codex" / "hooks"
    hook_dir.mkdir(parents=True)
    roadmap_dir.mkdir(parents=True)
    posture_dir.mkdir(parents=True)
    for name in ("codex-session-start.sh", "session-lease.sh", "lib.sh"):
        shutil.copy2(ROOT / "tools" / "hooks" / name, hook_dir / name)
    (posture_dir / "session_start.py").write_text("print('posture')\n", encoding="utf-8")
    (posture_dir / "codex_hook_adapter.py").write_text(
        "raise SystemExit('compact-context must not run')\n",
        encoding="utf-8",
    )
    (roadmap_dir / "session-start.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    (hook_dir / "loop-gc.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    for script in (roadmap_dir / "session-start.sh", hook_dir / "loop-gc.sh"):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = {
        "hook_event_name": "SessionStart",
        "session_id": f"absent-source-{label}",
        "cwd": str(tmp_path),
        **source_payload,
    }
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    output = json.loads(proc.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "SessionStart"
    assert output["additionalContext"] == "posture"
    lease = next(
        (tmp_path / ".git" / "codex-worktree-sessions").rglob(
            f"session-absent-source-{label}.lease"
        )
    )
    assert lease.read_text(encoding="utf-8").splitlines()[0] == "active"


def test_registered_session_lifecycle_round_trips_active_lease(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    (tmp_path / "tools").symlink_to(ROOT / "tools", target_is_directory=True)
    payload = json.dumps({"session_id": "registered-round-trip", "cwd": str(tmp_path)})
    env = os.environ.copy()
    env.update(
        {
            "HARNESS_CODEX_REVIEW_ISOLATED": "1",
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "HOME": str(tmp_path / "home"),
        }
    )

    for command in _event_commands("SessionStart"):
        proc = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=tmp_path,
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env=env,
        )
        assert proc.returncode == 0, (command, proc.stderr)

    leases = list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))
    assert len(leases) == 1
    assert leases[0].read_text(encoding="utf-8").splitlines()[0] == "active"

    for command in _event_commands("SessionEnd"):
        proc = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=tmp_path,
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env=env,
        )
        assert proc.returncode == 0, (command, proc.stderr)

    assert not list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))


def test_session_lifecycle_wrappers_order_registration_and_release() -> None:
    start = (ROOT / "tools" / "hooks" / "codex-session-start.sh").read_text(encoding="utf-8")
    end = (ROOT / "tools" / "hooks" / "codex-session-end.sh").read_text(encoding="utf-8")

    assert start.index("lease_action start") < start.index("session_start.py")
    assert start.index("session_start.py") < start.index("roadmap-audit/session-start.sh")
    assert start.index("roadmap-audit/session-start.sh") < start.index("loop-gc.sh")
    assert start.index("loop-gc.sh") < start.index("compact-context")
    assert start.index("compact-context") < start.rindex("lease_action activate")
    assert "lease_action end" in start
    assert end.index('session-lease.sh" end') < end.index("session-end-cleanup.sh")


def test_session_start_hygiene_is_report_only_and_never_reaps() -> None:
    hygiene = (ROOT / "tools" / "hooks" / "loop-gc.sh").read_text(encoding="utf-8")

    assert "loop_gc_worktrees report" in hygiene
    assert "loop_gc_worktrees reap" not in hygiene


def test_parity_regressions_are_blocking_locally_and_in_ci() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    )
    test_steps = workflow["jobs"]["test"]["steps"]

    assert "codex-parity-check" in justfile
    assert "bash tools/codex-parity-check.sh" in justfile
    assert any(
        "bash tools/codex-parity-check.sh" in str(step.get("run") or "") for step in test_steps
    )
    assert any(
        str(step.get("uses") or "").startswith("actions/checkout@")
        and str((step.get("with") or {}).get("fetch-depth")) == "0"
        for step in test_steps
    )


def test_local_premerge_gates_match_ci_format_check() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")

    assert "fmt-check:\n    uv run ruff format --check ." in justfile
    assert "check: codex-sync lint fmt-check typecheck" in justfile
    assert "codex-check: codex-sync lint fmt-check typecheck" in justfile


def test_session_end_hook_uses_supported_timeout() -> None:
    payload = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    hooks = [hook for group in payload["hooks"]["SessionEnd"] for hook in group["hooks"]]

    assert len(hooks) == 1
    assert hooks[0]["timeout"] <= 3


def test_merge_gate_honors_operator_authorized_ten_pass_ceiling() -> None:
    for path in [
        ROOT / ".agents" / "skills" / "merge-gate" / "SKILL.md",
        ROOT / ".claude" / "skills" / "merge-gate" / "SKILL.md",
        ROOT / ".claude" / "skills" / "ship-pr" / "SKILL.md",
    ]:
        merge_gate = path.read_text(encoding="utf-8")
        assert "ten rounds" in merge_gate, path
        assert "eleventh" in merge_gate.lower(), path
        assert "disagreement" in merge_gate, path

    codex_merge_gate = (ROOT / ".agents" / "skills" / "merge-gate" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "just codex-hook-runtime-witness" in codex_merge_gate
    assert "both tool phase pairs" in codex_merge_gate


def test_every_shared_state_hook_is_inert_for_isolated_review(tmp_path: Path) -> None:
    shell_hooks = [
        ROOT / path
        for path in [
            "tools/hooks/git-arc-guard.sh",
            "tools/hooks/loop-gc.sh",
            "tools/hooks/permission-guard.sh",
            "tools/hooks/postcompact-reinject.sh",
            "tools/hooks/precmd-clear-cache.sh",
            "tools/hooks/precompact-checkpoint.sh",
            "tools/hooks/prompt-context.sh",
            "tools/hooks/prompt-lint.sh",
            "tools/hooks/session-end-cleanup.sh",
            "tools/hooks/skill-activation-check.sh",
            "tools/hooks/stop-gate.sh",
            "tools/hooks/stop-loop.sh",
            "tools/roadmap-audit/post-merge-refresh.sh",
            "tools/roadmap-audit/session-start.sh",
        ]
    ]
    python_hooks = [
        (ROOT / ".codex" / "hooks" / "codex_hook_adapter.py", ["post-tool-use"]),
        (ROOT / ".codex" / "hooks" / "session_start.py", []),
        (ROOT / ".codex" / "hooks" / "stop_gate.py", []),
    ]
    env = os.environ.copy()
    env.update(
        {
            "HARNESS_CODEX_REVIEW_ISOLATED": "1",
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "HOME": str(tmp_path / "home"),
        }
    )
    payload = json.dumps(
        {
            "hook_event_name": "PostToolUse",
            "session_id": "isolated",
            "cwd": str(tmp_path),
            "tool_name": "Bash",
            "tool_input": {"command": "git status"},
            "tool_response": {"exit_code": 1},
        }
    )

    for path in shell_hooks:
        assert "hook_review_isolated && exit 0" in path.read_text(encoding="utf-8")
        before = sorted(str(item.relative_to(tmp_path)) for item in tmp_path.rglob("*"))
        proc = subprocess.run(
            ["bash", str(path)],
            cwd=tmp_path,
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=env,
        )
        after = sorted(str(item.relative_to(tmp_path)) for item in tmp_path.rglob("*"))
        assert proc.returncode == 0, (path, proc.stderr)
        assert proc.stdout == "", path
        assert after == before, path

    for path, args in python_hooks:
        before = sorted(str(item.relative_to(tmp_path)) for item in tmp_path.rglob("*"))
        proc = subprocess.run(
            [sys.executable, str(path), *args],
            cwd=tmp_path,
            input=payload,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
            env=env,
        )
        after = sorted(str(item.relative_to(tmp_path)) for item in tmp_path.rglob("*"))
        assert proc.returncode == 0, (path, proc.stderr)
        assert proc.stdout == "", path
        assert after == before, path


def test_every_tracked_claude_skill_has_a_codex_entrypoint() -> None:
    def declared_name(path: Path) -> str:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                return line.removeprefix("name:").strip()
        raise AssertionError(f"missing skill name: {path}")

    claude_names = {
        declared_name(path)
        for path in (ROOT / ".claude" / "skills").rglob("SKILL.md")
        if subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
            cwd=ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    }
    codex_names = {declared_name(path) for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")}

    assert claude_names <= codex_names


def test_every_non_native_skill_bridge_preserves_its_canonical_source_contract() -> None:
    def declared_name(path: Path) -> str:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("name:"):
                return line.removeprefix("name:").strip()
        raise AssertionError(f"missing skill name: {path}")

    claude_skills = {
        declared_name(path): path
        for path in (ROOT / ".claude" / "skills").rglob("SKILL.md")
        if subprocess.run(
            ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
            cwd=ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    }
    codex_skills = {
        declared_name(path): path for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md")
    }
    native_codex_workflows = {"merge-gate", "roadmap-continue", "ship-pr"}

    for name, canonical in claude_skills.items():
        if name in native_codex_workflows:
            continue
        bridge = codex_skills[name].read_text(encoding="utf-8")
        canonical_relative = str(canonical.relative_to(ROOT))
        assert canonical_relative in bridge, (name, canonical_relative)
        lowered = bridge.lower()
        assert "complete" in lowered, name
        assert "source of truth" in lowered or "full workflow" in lowered, name
        assert "runner translations only" in lowered or "translate only runner" in lowered, name


@pytest.mark.parametrize(
    "name",
    ["frontend-design", "impeccable", "taste-skill", "ui-ux-pro-max"],
)
def test_operator_installed_design_skill_has_a_codex_bridge(name: str) -> None:
    bridge = ROOT / ".agents" / "skills" / name / "SKILL.md"
    text = bridge.read_text(encoding="utf-8")

    assert f"name: {name}" in text
    assert f".claude/skills/{name}/SKILL.md" in text
    assert "--git-common-dir" in text
    assert "/Users/" not in text
    assert "complete canonical skill" in text


@pytest.mark.parametrize(
    "path",
    [
        ".claude/skills/frontend-design/SKILL.md",
        ".claude/skills/impeccable/SKILL.md",
        ".claude/skills/taste-skill/SKILL.md",
        ".claude/skills/ui-ux-pro-max/SKILL.md",
        ".harness/memory/semantic/index.jsonl",
        ".impeccable/live/config.json",
        "tools/dashboard/public/index.html",
        "tools/dashboard/.DS_Store",
    ],
)
def test_local_skill_and_runtime_state_does_not_dirty_root(path: str) -> None:
    proc = subprocess.run(["git", "check-ignore", "--no-index", "-q", path], cwd=ROOT, check=False)
    assert proc.returncode == 0, path


def test_codex_shipping_skills_encode_current_review_and_ci_fixed_point() -> None:
    combined = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            ".agents/skills/codex-autonomous-loop/SKILL.md",
            ".agents/skills/roadmap-continue/SKILL.md",
            ".agents/skills/ship-pr/SKILL.md",
            ".agents/skills/merge-gate/SKILL.md",
        ]
    )
    for required in [
        "just gemini-review",
        "Antigravity",
        "three-lens",
        "base `main` HEAD",
        "stale prior",
        "main CI",
        "context-save",
    ]:
        assert required in combined

    merge_gate = (ROOT / ".agents/skills/merge-gate/SKILL.md").read_text(encoding="utf-8")
    assert "--sandbox read-only" in merge_gate
    assert "-s read-only" not in merge_gate


def test_forward_profile_template_preserves_current_codex_home_and_review_boundary() -> None:
    profile = (ROOT / ".codex" / "notes" / "arhugula-forward.config.toml.example").read_text(
        encoding="utf-8"
    )
    parity = (ROOT / ".codex" / "notes" / "claude-codex-parity.md").read_text(encoding="utf-8")

    assert 'approval_policy = "on-request"' in profile
    assert 'approvals_reviewer = "auto_review"' in profile
    assert 'sandbox_mode = "danger-full-access"' in profile
    assert "CODEX_HOME" not in profile
    assert "codex --profile arhugula-forward" in parity
    assert "managed requirements" in parity
    assert "leaving the worktree" in parity
    assert "~/.codex-arhugula/CODEX_HOME/" in parity
    assert "overlays" in parity


def test_controller_and_implementer_profiles_pin_parity_models() -> None:
    forward = (ROOT / ".codex" / "notes" / "arhugula-forward.config.toml.example").read_text(
        encoding="utf-8"
    )
    implementer = (
        ROOT / ".codex" / "notes" / "arhugula-implementer.config.toml.example"
    ).read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    loop = (ROOT / ".agents" / "skills" / "codex-autonomous-loop" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert 'model = "gpt-5.6-sol"' in forward
    assert 'model_reasoning_effort = "high"' in forward
    assert 'model = "gpt-5.6-terra"' in implementer
    assert 'model_reasoning_effort = "high"' in implementer
    for text in (agents, loop):
        assert "Fable 5" in text
        assert "Opus 5" in text
        assert "gpt-5.6-sol" in text
        assert "gpt-5.6-terra" in text
        assert "arhugula-implementer" in text

    brief = (ROOT / ".codex" / "notes" / "leg-brief-template.md").read_text(encoding="utf-8")
    assert "codex exec --profile arhugula-implementer" in brief
    assert "gpt-5.6-sol" in brief
    assert "gpt-5.6-terra" in brief
    assert "gpt-5.6-codex" not in brief


def test_reconciled_hardening_docs_do_not_preserve_superseded_gc_or_path_claims() -> None:
    review = (
        ROOT / ".harness" / "hardening-workflow" / "hook-advisor-workflow-review.md"
    ).read_text(encoding="utf-8")
    inventory = (
        ROOT / ".harness" / "hardening-workflow" / "inventory-hooks-skills-disciplines.md"
    ).read_text(encoding="utf-8")

    assert "it reaps at the *next* session's **SessionStart**" not in review
    assert "tools/loop/run.sh" not in inventory
    assert "tools/loop/defer.sh" not in inventory
    assert "tools/loop/halt.sh" not in inventory
    assert "## B. LOOP RUNNER (`tools/04-loop/`)" in inventory


def test_antigravity_review_is_read_only_and_uses_writable_operational_log() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")
    recipe = justfile.split("gemini-review base='main':", 1)[1].split("\n_require-antigravity:", 1)[
        0
    ]
    reviewer = (ROOT / "tools" / "agy_review.py").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "tools/agy_review.py" in recipe
    assert "--mode" in reviewer and '"plan"' in reviewer
    assert 'Path(scratch) / "route.log"' in reviewer
    assert "/tmp/arhugula-agy-review.log" not in reviewer
    assert "GEMINI_API_KEY" in reviewer and "GOOGLE_API_KEY" in reviewer
    assert "VERDICT: APPROVE" in reviewer and "VERDICT: BLOCK" in reviewer
    assert "standing authorization" in agents.lower()
