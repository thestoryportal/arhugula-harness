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
    assert '"SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd"' in source
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
    assert "compact-context" in readme
    assert "equivalent effect" in readme
    assert "`PostCompact` | shared reinjection producer through the Codex adapter" in readme
    assert "`PostCompact` | Direct" not in readme
    assert "only for the single real `PreToolUse:permission-guard` adapter" in normalized_readme
    assert "including `PostCompact`, are recorder substitutes" in normalized_readme
    assert (
        "all other lifecycle handlers, including PostCompact, are recorder substitutes"
        in plain_readme
    )
    assert (
        "PostCompact translation validity is covered by shared-producer and "
        "adapter behavioral tests" in normalized_readme
    )
    assert "one real `PreToolUse` permission adapter" in parity
    assert (
        "permission adapter is absent, duplicated, registered under a different event, "
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


def test_runtime_witness_preserves_only_real_permission_guard_adapter(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    recorder = tmp_path / "record_hook.py"

    hooks, real_handlers = witness._witness_hooks(recorder)

    real_command = (
        f"{shlex.quote(sys.executable)} "
        f"{shlex.quote(str(ROOT / '.codex' / 'hooks' / 'codex_hook_adapter.py'))} permission-guard"
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
    assert real_handlers == ["PreToolUse:permission-guard"]
    assert commands.count(real_command) == 1
    assert all(command in {real_command, recorder_command} for command in commands)
    assert all(command == recorder_command for command in commands if command != real_command)


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

    with pytest.raises(RuntimeError, match="permission-guard"):
        witness._witness_hooks(tmp_path / "record_hook.py")


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


def test_runtime_witness_environment_uses_synthetic_project_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    witness = _runtime_witness_module()
    provider_variables = (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
    )
    for name in provider_variables:
        monkeypatch.setenv(name, "provider-credential")

    environment = witness._witness_environment(tmp_path / "codex-home", tmp_path / "repo")

    assert environment["CODEX_HOME"] == str(tmp_path / "codex-home")
    assert environment["HARNESS_LOOP"] == "1"
    assert environment["CLAUDE_PROJECT_DIR"] == str(tmp_path / "repo")
    assert not set(provider_variables) & set(environment)


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


def test_live_runtime_witness_reports_empty_hook_stream(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text("", encoding="utf-8")

    with pytest.raises(RuntimeError, match="no hook events"):
        witness._assert_witness(
            tmp_path,
            events_path,
            0,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
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
        {"hook_event_name": "PostToolUse", "tool_name": "Bash", "session_id": "one"},
        {"hook_event_name": "PreToolUse", "tool_name": "apply_patch", "session_id": "one"},
        {"hook_event_name": "PostToolUse", "tool_name": "apply_patch", "session_id": "one"},
        {"hook_event_name": "Stop", "session_id": "one"},
        {"hook_event_name": "SessionEnd", "session_id": "one"},
    ]
    (tmp_path / "shell-marker.txt").write_text("codex-shell-witness", encoding="utf-8")
    (tmp_path / "patch-marker.txt").write_text("codex-patch-witness\n", encoding="utf-8")
    return witness, tmp_path / "events.jsonl", events


def _write_runtime_events(path: Path, events: list[dict[str, str]]) -> None:
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")


def test_live_runtime_witness_accepts_complete_fixture(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    evidence = witness._assert_witness(
        tmp_path,
        events_path,
        3,
        real_handlers=[witness.REAL_PERMISSION_HANDLER],
    )

    assert evidence["status"] == "PASS"
    assert evidence["real_handlers"] == ["PreToolUse:permission-guard"]


@pytest.mark.parametrize("real_handlers", [[], ["PreToolUse:another-handler"]])
def test_live_runtime_witness_rejects_untrusted_real_handler_evidence(
    tmp_path: Path, real_handlers: list[str]
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="real handler evidence"):
        witness._assert_witness(tmp_path, events_path, 3, real_handlers=real_handlers)


@pytest.mark.parametrize("missing", ["SessionStart", "Stop", "SessionEnd"])
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
            3,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
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
            3,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
        )


def test_live_runtime_witness_rejects_wrong_request_count(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="expected 3"):
        witness._assert_witness(
            tmp_path,
            events_path,
            2,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
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
            3,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
        )


def test_live_runtime_witness_rejects_multiple_session_identities(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    events[-1]["session_id"] = "two"
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="multiple sessions"):
        witness._assert_witness(
            tmp_path,
            events_path,
            3,
            real_handlers=[witness.REAL_PERMISSION_HANDLER],
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
    adapter.TERMINATION_GRACE_SECONDS = 0.2
    child_pid_file = tmp_path / "child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

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

    assert proc.returncode == 124
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


def test_compact_context_uses_ten_second_producer_timeout(
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

    assert adapter.compact_context({"cwd": str(ROOT)}) == "context"
    assert timeouts == [10]


@pytest.mark.parametrize("handler_name", ["post_compact", "print_compact_context"])
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
def test_compact_context_adapter_modes_reject_invalid_producer_output(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    handler_name: str,
    producer_result: subprocess.CompletedProcess[str],
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "run_bounded", lambda *_args, **_kwargs: producer_result)

    assert getattr(adapter, handler_name)({"cwd": str(ROOT)}) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err


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
    decision = json.loads(proc.stdout)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "deny"
    assert decision["permissionDecisionReason"]


def test_permission_guard_adapter_fails_closed_on_non_decision_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: {"systemMessage": "shared producer failed: exact detail"},
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "shared producer failed: exact detail\n"


def test_permission_guard_adapter_rejects_malformed_allow_updated_input(
    monkeypatch: pytest.MonkeyPatch,
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

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 2


def test_permission_guard_adapter_fails_closed_on_non_object_shared_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(
        adapter,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(["hook"], 0, "[]", ""),
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 2


def test_permission_guard_adapter_passes_through_dict_updated_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    adapter = _adapter_module()
    shared_response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {"command": "git status"},
        }
    }
    monkeypatch.setattr(
        adapter,
        "run_claude_hook",
        lambda *_args, **_kwargs: shared_response,
    )

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 0
    assert json.loads(capsys.readouterr().out) == shared_response


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


def test_session_start_wrapper_routes_compact_context(tmp_path: Path) -> None:
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
    (tmp_path / checkpoint).write_text(
        "wrapper pre-compaction checkpoint\n",
        encoding="utf-8",
    )
    for script in (roadmap_dir / "session-start.sh", hook_dir / "loop-gc.sh"):
        script.chmod(0o755)
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", ".harness/roadmap_status.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "wrapper base"], cwd=tmp_path, check=True)
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)

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

    assert proc.returncode == 2, proc.stderr
    assert "compact producer failed" in proc.stderr
    assert proc.stdout == ""
    assert not list((tmp_path / ".git" / "codex-worktree-sessions").rglob("*.lease"))


def test_session_start_wrapper_routes_compact_through_four_second_bound() -> None:
    start = (ROOT / "tools" / "hooks" / "codex-session-start.sh").read_text(encoding="utf-8")

    assert 'hook_bounded "$' + '{HARNESS_SESSION_START_COMPACT_SECONDS:-4}"' in start


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
