"""Regression tests for Claude-to-Codex workflow parity."""

from __future__ import annotations

import errno
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

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


def _runtime_witness_module():
    spec = importlib.util.spec_from_file_location(
        "codex_hook_runtime_witness_test", RUNTIME_WITNESS
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_live_runtime_witness_reports_empty_hook_stream(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    events_path = tmp_path / "events.jsonl"
    events_path.write_text("", encoding="utf-8")

    with pytest.raises(RuntimeError, match="no hook events"):
        witness._assert_witness(tmp_path, events_path, 0)


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

    assert witness._assert_witness(tmp_path, events_path, 3)["status"] == "PASS"


@pytest.mark.parametrize("missing", ["SessionStart", "Stop", "SessionEnd"])
def test_live_runtime_witness_rejects_each_missing_lifecycle_event(
    tmp_path: Path, missing: str
) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(
        events_path, [event for event in events if event["hook_event_name"] != missing]
    )

    with pytest.raises(RuntimeError):
        witness._assert_witness(tmp_path, events_path, 3)


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
        witness._assert_witness(tmp_path, events_path, 3)


def test_live_runtime_witness_rejects_wrong_request_count(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="expected 3"):
        witness._assert_witness(tmp_path, events_path, 2)


@pytest.mark.parametrize("marker", ["shell-marker.txt", "patch-marker.txt"])
def test_live_runtime_witness_rejects_each_missing_effect(tmp_path: Path, marker: str) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    _write_runtime_events(events_path, events)
    (tmp_path / marker).unlink()

    with pytest.raises((RuntimeError, FileNotFoundError)):
        witness._assert_witness(tmp_path, events_path, 3)


def test_live_runtime_witness_rejects_multiple_session_identities(tmp_path: Path) -> None:
    witness, events_path, events = _valid_runtime_witness_fixture(tmp_path)
    events[-1]["session_id"] = "two"
    _write_runtime_events(events_path, events)

    with pytest.raises(RuntimeError, match="multiple sessions"):
        witness._assert_witness(tmp_path, events_path, 3)


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
        ("PreToolUse", "*", ["permission-guard.sh"]),
        (
            "PermissionRequest",
            "*",
            ["permission_request.py", "permission-guard.sh"],
        ),
        ("PreCompact", "*", ["precompact-checkpoint.sh"]),
        ("PostCompact", "*", ["postcompact-reinject.sh"]),
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
    (posture_dir / "session_start.py").write_text(
        "print('bounded posture')\n",
        encoding="utf-8",
    )
    (roadmap_dir / "session-start.sh").write_text(
        '#!/bin/sh\nprintf \'%s\\n\' \'{"hookSpecificOutput":{"additionalContext":"roadmap"}}\'\n',
        encoding="utf-8",
    )
    (hook_dir / "loop-gc.sh").write_text("#!/bin/sh\nsleep 30\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    payload = json.dumps({"session_id": "bounded-hygiene", "cwd": str(tmp_path)})
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_PROJECT_DIR": str(tmp_path),
            "HARNESS_SESSION_START_HYGIENE_SECONDS": "1",
        }
    )

    started = time.monotonic()
    proc = subprocess.run(
        ["bash", str(hook_dir / "codex-session-start.sh")],
        cwd=tmp_path,
        input=payload,
        capture_output=True,
        text=True,
        check=False,
        timeout=6,
        env=env,
    )
    elapsed = time.monotonic() - started

    assert proc.returncode == 0, proc.stderr
    assert elapsed < 5
    assert "bounded posture" in proc.stdout
    assert "roadmap" in proc.stdout


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
    assert start.index("loop-gc.sh") < start.rindex("lease_action activate")
    assert "lease_action end" in start
    assert end.index('session-lease.sh" end') < end.index("session-end-cleanup.sh")


def test_session_start_hygiene_is_report_only_and_never_reaps() -> None:
    hygiene = (ROOT / "tools" / "hooks" / "loop-gc.sh").read_text(encoding="utf-8")

    assert "loop_gc_worktrees report" in hygiene
    assert "loop_gc_worktrees reap" not in hygiene


def test_parity_regressions_are_blocking_locally_and_in_ci() -> None:
    justfile = (ROOT / "justfile").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "codex-parity-check" in justfile
    assert "bash tools/codex-parity-check.sh" in justfile
    assert "bash tools/codex-parity-check.sh" in workflow


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
