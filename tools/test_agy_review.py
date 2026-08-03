"""Behavioral tests for the fail-closed Antigravity diff reviewer."""

from __future__ import annotations

import importlib.util
import itertools
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REVIEWER = ROOT / "tools" / "agy_review.py"


def _reviewer_module():
    spec = importlib.util.spec_from_file_location("agy_review_test", REVIEWER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(os.name != "posix", reason="process-group witness requires POSIX")
def test_reviewer_timeout_terminates_descendant_process_tree(tmp_path: Path) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0.2
    child_pid_file = tmp_path / "child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

    proc = reviewer.run_bounded(
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
        pytest.fail(f"reviewer timeout left descendant alive: pid={child_pid}")


@pytest.mark.skipif(os.name != "posix", reason="process-group witness requires POSIX")
def test_reviewer_success_terminates_background_descendant(tmp_path: Path) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0.2
    child_pid_file = tmp_path / "successful-child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

    proc = reviewer.run_bounded(
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
        pytest.fail(f"successful reviewer left descendant alive: pid={child_pid}")


def test_reviewer_interrupt_terminates_detached_process_group(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0

    class InterruptingProcess:
        pid = 424242
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
    monkeypatch.setattr(reviewer.subprocess, "Popen", lambda *_args, **_kwargs: process)
    monkeypatch.setattr(
        reviewer.os,
        "killpg",
        lambda pid, sent_signal: signals.append((pid, sent_signal)) if sent_signal != 0 else None,
    )

    with pytest.raises(KeyboardInterrupt):
        reviewer.run_bounded(["agy"], cwd=tmp_path, timeout=30, env=os.environ.copy())

    assert signals == [
        (process.pid, reviewer.signal.SIGTERM),
        (process.pid, reviewer.signal.SIGKILL),
    ]
    assert process.returncode == -15


def test_reviewer_closes_partial_temp_streams_when_input_write_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviewer = _reviewer_module()

    class FailingStream:
        def __init__(self, fail_write: bool) -> None:
            self.fail_write = fail_write
            self.closed = False

        def write(self, _value: str) -> int:
            if self.fail_write:
                raise OSError("disk full")
            return 0

        def seek(self, _offset: int) -> int:
            return 0

        def close(self) -> None:
            self.closed = True

    streams = [FailingStream(True), FailingStream(False), FailingStream(False)]
    pending = iter(streams)
    monkeypatch.setattr(reviewer.tempfile, "TemporaryFile", lambda **_kwargs: next(pending))

    with pytest.raises(OSError, match="disk full"):
        reviewer.run_bounded(
            ["agy"], cwd=tmp_path, timeout=30, env=os.environ.copy(), input_text="review"
        )

    assert all(stream.closed for stream in streams)


@pytest.mark.skipif(os.name != "posix", reason="signal-mask witness requires POSIX")
def test_reviewer_child_does_not_inherit_blocked_sigterm(tmp_path: Path) -> None:
    reviewer = _reviewer_module()

    proc = reviewer.run_bounded(
        [
            sys.executable,
            "-c",
            (
                "import signal; "
                "print(signal.SIGTERM in signal.pthread_sigmask(signal.SIG_BLOCK, set()))"
            ),
        ],
        cwd=tmp_path,
        timeout=5,
        env=os.environ.copy(),
    )

    assert proc.returncode == 0
    assert proc.stdout.strip() == "False"


@pytest.mark.parametrize("reviewer_returncode", [124, 127])
def test_reviewer_unavailable_exit_maps_to_two(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    reviewer_returncode: int,
) -> None:
    reviewer = _reviewer_module()
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: "+bounded timeout")
    monkeypatch.setattr(
        reviewer,
        "run_bounded",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["agy"], reviewer_returncode, "", "reviewer unavailable"
        ),
    )

    assert reviewer.run_review(tmp_path, "HEAD") == 2
    assert "agy-review: reviewer unavailable:" in capsys.readouterr().err


def test_collect_diff_rejects_empty_tracked_and_untracked_diff(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    monkeypatch.setattr(
        reviewer,
        "run_git",
        lambda _repo, *_args: subprocess.CompletedProcess(["git"], 0, "", ""),
    )

    with pytest.raises(RuntimeError, match="review diff is empty"):
        reviewer.collect_diff(tmp_path, "main")


def _fake_commands(
    tmp_path: Path,
    *,
    agy_output: str,
    agy_outputs: tuple[str, ...] | None = None,
    agy_exit: int = 0,
    effective_model: str = "Gemini 3.1 Pro (High)",
    emit_completeness: bool = True,
    required_synthesis_tokens: tuple[str, ...] = (),
) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    capture = tmp_path / "agy-prompt.txt"
    review_root = tmp_path / "main-root"
    (review_root / ".git").mkdir(parents=True)

    git = bin_dir / "git"
    git.write_text(
        "#!/bin/sh\n"
        "if [ \"$1 $2 $3\" = 'rev-parse --path-format=absolute --git-common-dir' ]; then\n"
        "  printf '%s\\n' \"$AGY_REVIEW_ROOT/.git\"\n"
        "  exit 0\n"
        "fi\n"
        "if [ \"$1\" = 'ls-files' ]; then\n"
        '  [ -n "${AGY_UNTRACKED_PATH:-}" ] && printf \'%s\\0\' "$AGY_UNTRACKED_PATH"\n'
        "  exit 0\n"
        "fi\n"
        "if [ \"$1 $2\" = 'diff --no-index' ]; then\n"
        "  printf '%s\\n' 'diff --git a/dev/null b/new.py' '+untracked witness'\n"
        "  exit 1\n"
        "fi\n"
        'if [ -n "${AGY_DIFF_FILE:-}" ]; then cat "$AGY_DIFF_FILE"; exit 0; fi\n'
        "printf '%s\\n' 'diff --git a/a.py b/a.py' '+new line'\n",
        encoding="utf-8",
    )
    git.chmod(0o755)

    agy = bin_dir / "agy"

    def render_output(output: str) -> str:
        output_lines = output.splitlines()
        output_prefix = "\n".join(output_lines[:-1])
        output_verdict = output_lines[-1]
        if emit_completeness:
            return (
                f"printf '%b\\n' {output_prefix!r}\n"
                'if grep -q "This is review segment" "$capture"; then\n'
                "  printf '%s\\n' 'SEGMENT: COMPLETE'\n"
                "else\n"
                "  printf '%s\\n' 'ARTIFACT: COMPLETE'\n"
                "fi\n"
                f"printf '%b\\n' {output_verdict!r}\n"
            )
        return f"printf '%b\\n' {output!r}\n"

    outputs = agy_outputs or (agy_output,)
    if len(outputs) == 1:
        rendered_output_script = render_output(outputs[0])
    else:
        cases = "".join(
            f"{index})\n{render_output(output)};;\n"
            for index, output in enumerate(outputs, start=1)
        )
        rendered_output_script = f'case "$count" in\n{cases}*) exit 11 ;;\nesac\n'
    synthesis_token_checks = "".join(
        f'grep -Fq {token!r} "$diff_capture" || exit 10\n' for token in required_synthesis_tokens
    )
    if synthesis_token_checks:
        synthesis_token_checks = (
            f'if [ "$count" -eq "{len(outputs)}" ]; then\n{synthesis_token_checks}fi\n'
        )
    agy.write_text(
        "#!/bin/sh\n"
        "count=1\n"
        'if [ -f "$AGY_COUNTER" ]; then count=$(( $(cat "$AGY_COUNTER") + 1 )); fi\n'
        'printf \'%s\\n\' "$count" > "$AGY_COUNTER"\n'
        'capture="$AGY_CAPTURE"\n'
        'diff_capture="$AGY_DIFF_CAPTURE"\n'
        'manifest_capture="$AGY_MANIFEST_CAPTURE"\n'
        'args_capture="$AGY_ARGS_CAPTURE"\n'
        'cwd_capture="$AGY_CWD_CAPTURE"\n'
        'if [ "$count" -gt 1 ]; then\n'
        '  capture="${AGY_CAPTURE%.txt}-$count.txt"\n'
        '  diff_capture="${AGY_DIFF_CAPTURE%.txt}-$count.txt"\n'
        '  manifest_capture="${AGY_MANIFEST_CAPTURE%.txt}-$count.txt"\n'
        '  args_capture="${AGY_ARGS_CAPTURE%.txt}-$count.txt"\n'
        '  cwd_capture="${AGY_CWD_CAPTURE%.txt}-$count.txt"\n'
        "fi\n"
        'pwd > "$cwd_capture"\n'
        'printf \'%s\\n\' "$@" > "$args_capture"\n'
        "prev=''\n"
        "add_dir=''\n"
        "log_file=''\n"
        'for arg in "$@"; do\n'
        '  if [ "$prev" = \'-p\' ]; then printf \'%s\\n\' "$arg" > "$capture"; fi\n'
        '  if [ "$prev" = \'--add-dir\' ]; then add_dir="$arg"; fi\n'
        '  if [ "$prev" = \'--log-file\' ]; then log_file="$arg"; fi\n'
        '  prev="$arg"\n'
        "done\n"
        f"printf 'Propagating selected model override to backend: label=\"{effective_model}\"\\n' "
        '  > "$log_file"\n'
        'sed -n \'s/^[0-9][0-9]*\\. //p\' "$capture" > "$manifest_capture"\n'
        '[ -s "$manifest_capture" ] || exit 8\n'
        ': > "$diff_capture"\n'
        "while IFS= read -r diff_part; do "
        '[ -f "$diff_part" ] || exit 8; cat "$diff_part" >> "$diff_capture"; '
        'done < "$manifest_capture"\n'
        'cat "$diff_capture" >> "$capture"\n'
        'if [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}${GOOGLE_GENAI_USE_VERTEXAI:-}'
        "${GOOGLE_APPLICATION_CREDENTIALS:-}${GOOGLE_CLOUD_PROJECT:-}"
        '${GOOGLE_CLOUD_LOCATION:-}" ]; then\n'
        "  echo 'provider environment leaked'\n"
        "  exit 9\n"
        "fi\n"
        f"{synthesis_token_checks}"
        f"{rendered_output_script}"
        f"exit {agy_exit}\n",
        encoding="utf-8",
    )
    agy.chmod(0o755)
    return bin_dir, capture


def _run(
    tmp_path: Path,
    *,
    agy_output: str,
    agy_outputs: tuple[str, ...] | None = None,
    agy_exit: int = 0,
    untracked_path: str = "",
    diff_file: Path | None = None,
    effective_model: str = "Gemini 3.1 Pro (High)",
    emit_completeness: bool = True,
    required_synthesis_tokens: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    bin_dir, capture = _fake_commands(
        tmp_path,
        agy_output=agy_output,
        agy_outputs=agy_outputs,
        agy_exit=agy_exit,
        effective_model=effective_model,
        emit_completeness=emit_completeness,
        required_synthesis_tokens=required_synthesis_tokens,
    )
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "AGY_CAPTURE": str(capture),
            "AGY_DIFF_CAPTURE": str(tmp_path / "agy-diff.txt"),
            "AGY_MANIFEST_CAPTURE": str(tmp_path / "agy-manifest.txt"),
            "AGY_ARGS_CAPTURE": str(tmp_path / "agy-args.txt"),
            "AGY_CWD_CAPTURE": str(tmp_path / "agy-cwd.txt"),
            "AGY_COUNTER": str(tmp_path / "agy-counter.txt"),
            "AGY_REVIEW_ROOT": str(tmp_path / "main-root"),
            "AGY_UNTRACKED_PATH": untracked_path,
            "AGY_DIFF_FILE": str(diff_file) if diff_file is not None else "",
            "GEMINI_API_KEY": "must-not-leak",
            "GOOGLE_API_KEY": "must-not-leak",
            "GOOGLE_GENAI_USE_VERTEXAI": "must-not-leak",
            "GOOGLE_APPLICATION_CREDENTIALS": "must-not-leak",
            "GOOGLE_CLOUD_PROJECT": "must-not-leak",
            "GOOGLE_CLOUD_LOCATION": "must-not-leak",
        }
    )
    return subprocess.run(
        [sys.executable, str(REVIEWER), "--base", "main"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )


def test_review_passes_actual_diff_and_accepts_exact_verdict(tmp_path: Path) -> None:
    proc = _run(tmp_path, agy_output="F1 none\nVERDICT: APPROVE")

    assert proc.returncode == 0, proc.stderr
    prompt = (tmp_path / "agy-prompt.txt").read_text(encoding="utf-8")
    assert "diff --git a/a.py b/a.py" in prompt
    assert "Do not invoke terminal commands" in prompt
    assert "Do not invoke URL, browser, or MCP tools" in prompt
    assert "read-only view_file calls, one for each numbered part" in prompt
    assert "parts concatenate byte-for-byte into the complete diff" in prompt
    assert "ARTIFACT: COMPLETE" in prompt
    assert "Do not open surrounding workspace files" in prompt
    assert "Report at most 5 findings" in prompt
    assert "Finish immediately after analyzing that diff" in prompt
    assert "Only report a finding proven entirely by the supplied diff" in prompt
    assert "Test-only regression coverage for behavior outside a scoped delta is valid" in prompt
    assert "Do not infer helper semantics when its definition is absent from the diff" in prompt
    assert "--add-dir exposes the absolute diff path inside the Antigravity sandbox" in prompt
    assert "Shell and unified-exec hooks match as Bash" in prompt
    assert "tool_input.command" in prompt
    assert "aliases affect matcher selection only" in prompt
    assert 'payload still reports exactly tool_name: "apply_patch" or "Bash"' in prompt
    assert 'A matcher of "Bash" already covers Shell and unified-exec aliases' in prompt
    assert "Both canonical names and documented aliases are valid in matcher regexes" in prompt
    assert "Codex apply_patch command syntax, not Antigravity schema" in prompt
    assert "apply_patch custom_tool_call correctly carries the raw patch string" in prompt
    assert "Codex then normalizes it into hook tool_input.command" in prompt
    assert "cwd is a runtime-supplied common field for the session" in prompt
    assert "root comparison is optional hardening, not a Claude-parity requirement" in prompt
    assert "display label is intentional and empirically required" in prompt
    assert "standing operator authorization" in prompt
    assert "concrete sandbox escape" in prompt
    args = (tmp_path / "agy-args.txt").read_text(encoding="utf-8").splitlines()
    assert "--sandbox" in args
    assert "--dangerously-skip-permissions" in args
    assert "--new-project" in args
    assert "--add-dir" in args
    assert Path(args[args.index("--add-dir") + 1]).name.startswith("arhugula-agy-review-")
    assert args[args.index("--model") + 1] == "Gemini 3.1 Pro (High)"
    assert args[args.index("--print-timeout") + 1] == "20m"
    route_log = Path(args[args.index("--log-file") + 1])
    assert route_log.name == "route.log"
    assert route_log.parent.name.startswith("arhugula-agy-review-")
    assert f"authoritative workspace root is {tmp_path}" in prompt
    assert (tmp_path / "agy-cwd.txt").read_text(encoding="utf-8").strip() == str(tmp_path)
    assert "agy-review: effective model: Gemini 3.1 Pro (High)" in proc.stdout
    assert proc.stdout.rstrip().endswith("VERDICT: APPROVE")


def test_review_rejects_approval_without_complete_artifact_marker(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output=(
            "The system truncated the file reading at 46,080 bytes; no defects in the "
            "visible portion.\nVERDICT: APPROVE"
        ),
        emit_completeness=False,
    )

    assert proc.returncode == 2
    assert "missing exact artifact-completeness marker" in proc.stderr


def test_diff_parts_are_bounded_and_reconstruct_the_exact_utf8_diff(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("abc🙂\n" * 20_000)
    monkeypatch.setattr(
        Path,
        "write_text",
        lambda *_args, **_kwargs: pytest.fail("diff parts must be written as raw bytes"),
    )

    paths = reviewer.write_diff_parts(tmp_path, diff)

    assert len(paths) > 1
    assert reviewer.MAX_DIFF_PART_BYTES == 32 * 1024
    assert all(len(path.read_bytes()) <= reviewer.MAX_DIFF_PART_BYTES for path in paths)
    assert b"".join(path.read_bytes() for path in paths) == diff.encode("utf-8")


def test_large_diff_parts_use_bounded_windows_with_raw_boundary_overlap(tmp_path: Path) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 438_333)
    paths = reviewer.write_diff_parts(tmp_path, diff)

    groups = reviewer.group_diff_parts(paths)

    assert len(groups) > 1
    assert reviewer.MAX_REVIEW_SEGMENT_BYTES == 96 * 1024
    assert all(
        sum(path.stat().st_size for path in group) <= reviewer.MAX_REVIEW_SEGMENT_BYTES
        for group in groups
    )
    assert groups[0][0] == paths[0]
    assert groups[-1][-1] == paths[-1]
    assert set(path for group in groups for path in group) == set(paths)
    assert all(left[-1] == right[0] for left, right in itertools.pairwise(groups))


def test_large_review_shares_one_deadline_across_segments_and_synthesis(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 150_000)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    clock = iter([100.0, 110.0, 500.0, 900.0])
    monkeypatch.setattr(reviewer.time, "monotonic", lambda: next(clock))
    observed_timeouts: list[float] = []
    observed_print_timeouts: list[str] = []

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed_timeouts.append(float(kwargs["timeout"]))
        observed_print_timeouts.append(args[args.index("--print-timeout") + 1])
        prompt = args[args.index("-p") + 1]
        Path(args[args.index("--log-file") + 1]).write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        marker = (
            "ARTIFACT: COMPLETE"
            if "Synthesize the completed segment reviews" in prompt
            else "SEGMENT: COMPLETE"
        )
        return subprocess.CompletedProcess(args, 0, f"{marker}\nVERDICT: APPROVE", "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 0
    assert observed_timeouts == [1250.0, 860.0, 460.0]
    assert observed_print_timeouts == ["20m", "855s", "455s"]


def test_large_review_refuses_stage_when_only_cleanup_grace_remains(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reviewer = _reviewer_module()
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: "+small diff")
    clock = iter([100.0, 1356.0])
    monkeypatch.setattr(reviewer.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(
        reviewer,
        "run_bounded",
        lambda *_args, **_kwargs: pytest.fail("review stage started inside cleanup grace"),
    )

    assert reviewer.run_review(tmp_path, "main") == 2
    assert "whole-review deadline expired" in capsys.readouterr().err


def test_large_review_refuses_stage_at_cleanup_grace_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reviewer = _reviewer_module()
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: "+small diff")
    clock = iter([100.0, 1355.0])
    monkeypatch.setattr(reviewer.time, "monotonic", lambda: next(clock))
    monkeypatch.setattr(
        reviewer,
        "run_bounded",
        lambda *_args, **_kwargs: pytest.fail("review stage started without cleanup reserve"),
    )

    assert reviewer.run_review(tmp_path, "main") == 2
    assert "whole-review deadline expired" in capsys.readouterr().err


def test_large_review_starts_stage_just_above_cleanup_grace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: "+small diff")
    clock = iter([100.0, 1354.999])
    monkeypatch.setattr(reviewer.time, "monotonic", lambda: next(clock))
    observed_timeouts: list[float] = []

    def fake_run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed_timeouts.append(float(kwargs["timeout"]))
        Path(args[args.index("--log-file") + 1]).write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(
            args,
            0,
            "ARTIFACT: COMPLETE\nVERDICT: APPROVE",
            "",
        )

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 0
    assert observed_timeouts == pytest.approx([5.001])


def test_sigterm_handler_turns_controller_termination_into_bounded_unwind() -> None:
    reviewer = _reviewer_module()

    with pytest.raises(reviewer.TerminationRequested) as raised:
        reviewer.handle_termination_signal(signal.SIGTERM, None)

    assert raised.value.exit_code == 128 + signal.SIGTERM


@pytest.mark.skipif(os.name != "posix", reason="signal/process-group witness requires POSIX")
def test_sigterm_during_popen_construction_reaps_spawned_process_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0.2
    real_popen = subprocess.Popen
    spawned: list[subprocess.Popen[str]] = []

    def popen_then_sigterm(*args: object, **kwargs: object) -> subprocess.Popen[str]:
        process = real_popen(*args, **kwargs)  # type: ignore[arg-type]
        spawned.append(process)
        os.kill(os.getpid(), signal.SIGTERM)
        return process

    monkeypatch.setattr(reviewer.subprocess, "Popen", popen_then_sigterm)
    previous = signal.signal(signal.SIGTERM, reviewer.handle_termination_signal)
    orphaned = False
    try:
        with pytest.raises(reviewer.TerminationRequested):
            reviewer.run_bounded(
                ["/bin/sh", "-c", 'trap "" TERM; sleep 30'],
                cwd=tmp_path,
                timeout=30,
                env=os.environ.copy(),
            )
    finally:
        signal.signal(signal.SIGTERM, previous)
        if spawned:
            if spawned[0].poll() is None:
                orphaned = True
                spawned[0].kill()
                spawned[0].wait(timeout=3)

    assert spawned
    assert not orphaned


@pytest.mark.skipif(os.name != "posix", reason="signal/process-group witness requires POSIX")
def test_sigint_during_popen_construction_reaps_spawned_process_group(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0.2
    real_popen = subprocess.Popen
    spawned: list[subprocess.Popen[str]] = []

    def popen_then_sigint(*args: object, **kwargs: object) -> subprocess.Popen[str]:
        process = real_popen(*args, **kwargs)
        spawned.append(process)
        os.kill(os.getpid(), signal.SIGINT)
        return process

    monkeypatch.setattr(reviewer.subprocess, "Popen", popen_then_sigint)
    orphaned = False
    try:
        with pytest.raises(reviewer.TerminationRequested) as raised:
            reviewer.run_bounded(
                ["/bin/sh", "-c", 'trap "" TERM; sleep 30'],
                cwd=tmp_path,
                timeout=30,
                env=os.environ.copy(),
            )
        assert raised.value.exit_code == 128 + signal.SIGINT
    finally:
        if spawned and spawned[0].poll() is None:
            orphaned = True
            spawned[0].kill()
            spawned[0].wait(timeout=3)

    assert spawned
    assert not orphaned


@pytest.mark.skipif(os.name != "posix", reason="signal/process-group witness requires POSIX")
def test_reviewer_sigterm_terminates_detached_descendant(
    tmp_path: Path,
) -> None:
    reviewer = _reviewer_module()
    reviewer.TERMINATION_GRACE_SECONDS = 0.2
    child_pid_file = tmp_path / "sigterm-child.pid"
    env = os.environ.copy()
    env["CHILD_PID_FILE"] = str(child_pid_file)

    def terminate_after_child_starts() -> None:
        deadline = time.monotonic() + 3
        while not child_pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        os.kill(os.getpid(), signal.SIGTERM)

    previous = signal.signal(signal.SIGTERM, reviewer.handle_termination_signal)
    trigger = threading.Thread(target=terminate_after_child_starts)
    trigger.start()
    try:
        with pytest.raises(reviewer.TerminationRequested):
            reviewer.run_bounded(
                [
                    "/bin/sh",
                    "-c",
                    (
                        '(trap "" TERM; sleep 30) & child=$!; '
                        'printf "%s" "$child" > "$CHILD_PID_FILE"; wait "$child"'
                    ),
                ],
                cwd=tmp_path,
                timeout=30,
                env=env,
            )
    finally:
        trigger.join(timeout=4)
        signal.signal(signal.SIGTERM, previous)

    child_pid = int(child_pid_file.read_text(encoding="utf-8"))
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail(f"SIGTERM left detached reviewer descendant alive: pid={child_pid}")


def test_large_review_uses_bounded_segments_then_synthesizes_one_verdict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 438_333)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    prompts: list[str] = []

    def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        prompt = args[args.index("-p") + 1]
        prompts.append(prompt)
        log_path = Path(args[args.index("--log-file") + 1])
        log_path.write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        if "Synthesize the completed segment reviews" in prompt:
            output = "No blocking findings.\nARTIFACT: COMPLETE\nVERDICT: APPROVE"
        else:
            output = "No local findings.\nSEGMENT: COMPLETE\nVERDICT: APPROVE"
        return subprocess.CompletedProcess(args, 0, output, "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 0

    segment_prompts = prompts[:-1]
    assert len(segment_prompts) == 7
    assert "Synthesize the completed segment reviews" in prompts[-1]
    referenced_parts = [
        line.split(". ", 1)[1]
        for prompt in segment_prompts
        for line in prompt.splitlines()
        if line.split(". ", 1)[0].isdigit() and line.endswith(".diff")
    ]
    assert [Path(path).name for path in referenced_parts] == [
        "review-part-001.diff",
        "review-part-002.diff",
        "review-part-003.diff",
        "review-part-003.diff",
        "review-part-004.diff",
        "review-part-005.diff",
        "review-part-005.diff",
        "review-part-006.diff",
        "review-part-007.diff",
        "review-part-007.diff",
        "review-part-008.diff",
        "review-part-009.diff",
        "review-part-009.diff",
        "review-part-010.diff",
        "review-part-011.diff",
        "review-part-011.diff",
        "review-part-012.diff",
        "review-part-013.diff",
        "review-part-013.diff",
        "review-part-014.diff",
    ]
    assert all("SEGMENT: COMPLETE" in prompt for prompt in segment_prompts)
    assert "ARTIFACT: COMPLETE" in prompts[-1]
    output = capsys.readouterr().out
    assert "agy-review: effective model: Gemini 3.1 Pro (High)" in output
    assert output.rstrip().endswith("ARTIFACT: COMPLETE\nVERDICT: APPROVE")


def test_large_review_round_trips_segment_outputs_into_synthesis(tmp_path: Path) -> None:
    diff_file = tmp_path / "large-round-trip.diff"
    diff_file.write_text(
        "diff --git a/large.py b/large.py\n" + ("x" * 150_000),
        encoding="utf-8",
    )

    proc = _run(
        tmp_path,
        agy_output="unused\nVERDICT: APPROVE",
        agy_outputs=(
            "F1 [P2] segment-one-witness\nVERDICT: APPROVE",
            "F2 [P2] segment-two-witness\nVERDICT: APPROVE",
            "Both segment findings received\nVERDICT: APPROVE",
        ),
        diff_file=diff_file,
        required_synthesis_tokens=("segment-one-witness", "segment-two-witness"),
    )

    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "agy-counter.txt").read_text(encoding="utf-8").strip() == "3"


@pytest.mark.parametrize(
    ("synthesis_verdict", "expected_returncode", "expected_error"),
    [
        ("VERDICT: APPROVE", 2, "synthesis contradicted a blocking segment verdict"),
        ("VERDICT: BLOCK", 1, "blocking findings require resolution"),
    ],
)
def test_large_review_preserves_blocking_segment_verdict(
    tmp_path: Path,
    synthesis_verdict: str,
    expected_returncode: int,
    expected_error: str,
) -> None:
    diff_file = tmp_path / "large-block.diff"
    diff_file.write_text(
        "diff --git a/large.py b/large.py\n" + ("x" * 150_000),
        encoding="utf-8",
    )

    proc = _run(
        tmp_path,
        agy_output="unused\nVERDICT: APPROVE",
        agy_outputs=(
            "F1 [P1] blocking-segment-witness\nVERDICT: BLOCK",
            "No local findings\nVERDICT: APPROVE",
            f"Synthesis result\n{synthesis_verdict}",
        ),
        diff_file=diff_file,
    )

    assert proc.returncode == expected_returncode
    assert expected_error in proc.stderr


@pytest.mark.parametrize("invalid_stage", [1, 2, 3])
@pytest.mark.parametrize("invalid_surface", ["model", "completeness"])
def test_large_review_fails_closed_for_invalid_stage(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    invalid_stage: int,
    invalid_surface: str,
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 150_000)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    observed_stages = 0

    def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal observed_stages
        observed_stages += 1
        is_synthesis = "Synthesize the completed segment reviews" in args[args.index("-p") + 1]
        label = (
            "Gemini 3.6 Flash (High)"
            if invalid_surface == "model" and observed_stages == invalid_stage
            else "Gemini 3.1 Pro (High)"
        )
        Path(args[args.index("--log-file") + 1]).write_text(
            f'Propagating selected model override to backend: label="{label}"\n',
            encoding="utf-8",
        )
        marker = "ARTIFACT: COMPLETE" if is_synthesis else "SEGMENT: COMPLETE"
        if invalid_surface == "completeness" and observed_stages == invalid_stage:
            marker = "COMPLETENESS OMITTED"
        return subprocess.CompletedProcess(args, 0, f"{marker}\nVERDICT: APPROVE", "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 2
    assert observed_stages == invalid_stage
    error = capsys.readouterr().err
    if invalid_surface == "model":
        assert "effective model mismatch" in error
    else:
        expected_marker = "artifact" if invalid_stage == 3 else "segment"
        assert f"missing exact {expected_marker}-completeness marker" in error


@pytest.mark.skipif(os.name != "posix", reason="signal/process-group witness requires POSIX")
def test_cli_sigterm_reaps_reviewer_tree(tmp_path: Path) -> None:
    bin_dir, capture = _fake_commands(
        tmp_path,
        agy_output="unused\nVERDICT: APPROVE",
    )
    child_pid_file = tmp_path / "cli-sigterm-child.pid"
    (bin_dir / "agy").write_text(
        "#!/bin/sh\n"
        '(trap "" TERM; sleep 30) & child=$!\n'
        'printf "%s" "$child" > "$REVIEWER_CHILD_PID"\n'
        'wait "$child"\n',
        encoding="utf-8",
    )
    (bin_dir / "agy").chmod(0o755)
    env = os.environ.copy()
    env.update(
        {
            "PATH": f"{bin_dir}:{env['PATH']}",
            "AGY_CAPTURE": str(capture),
            "AGY_REVIEW_ROOT": str(tmp_path / "main-root"),
            "REVIEWER_CHILD_PID": str(child_pid_file),
        }
    )
    controller = subprocess.Popen(
        [sys.executable, str(REVIEWER), "--base", "main"],
        cwd=tmp_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    orphaned = False
    try:
        deadline = time.monotonic() + 5
        while not child_pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert child_pid_file.exists(), "fake reviewer did not start its descendant"
        controller.send_signal(signal.SIGTERM)
        controller.communicate(timeout=10)
        child_pid = int(child_pid_file.read_text(encoding="utf-8"))
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            orphaned = True
    finally:
        if controller.poll() is None:
            controller.kill()
            controller.wait(timeout=3)
        if orphaned:
            os.kill(child_pid, signal.SIGKILL)

    assert controller.returncode == 128 + signal.SIGTERM
    assert not orphaned


def test_large_review_accepts_segment_result_at_exact_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 150_000)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    suffix = "\nSEGMENT: COMPLETE\nVERDICT: APPROVE"
    exact_output = ("x" * (reviewer.MAX_REVIEW_RESULT_BYTES - len(suffix.encode("utf-8")))) + suffix
    assert len(exact_output.encode("utf-8")) == reviewer.MAX_REVIEW_RESULT_BYTES
    observed_stages = 0

    def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal observed_stages
        observed_stages += 1
        is_synthesis = "Synthesize the completed segment reviews" in args[args.index("-p") + 1]
        Path(args[args.index("--log-file") + 1]).write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        output = "ARTIFACT: COMPLETE\nVERDICT: APPROVE" if is_synthesis else exact_output
        return subprocess.CompletedProcess(args, 0, output, "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 0
    assert observed_stages == 3


def test_large_review_rejects_segment_result_one_byte_over_32_kib(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 150_000)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    suffix = "\nSEGMENT: COMPLETE\nVERDICT: APPROVE"
    output = ("x" * ((32 * 1024 + 1) - len(suffix.encode("utf-8")))) + suffix
    observed_stages = 0

    def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal observed_stages
        observed_stages += 1
        Path(args[args.index("--log-file") + 1]).write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(args, 0, output, "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert len(output.encode("utf-8")) == 32 * 1024 + 1
    assert reviewer.run_review(tmp_path, "main") == 2
    assert observed_stages == 1
    assert "segment review output exceeds synthesis limit" in capsys.readouterr().err


def test_large_review_rejects_oversized_segment_result_before_synthesis(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    reviewer = _reviewer_module()
    diff = "diff --git a/a b/a\n+" + ("x" * 150_000)
    monkeypatch.setattr(reviewer, "collect_diff", lambda _repo, _base: diff)
    prompts: list[str] = []

    def fake_run(args: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
        prompt = args[args.index("-p") + 1]
        prompts.append(prompt)
        Path(args[args.index("--log-file") + 1]).write_text(
            'Propagating selected model override to backend: label="Gemini 3.1 Pro (High)"\n',
            encoding="utf-8",
        )
        output = ("oversized synopsis\n" + ("x" * (32 * 1024))) + (
            "\nSEGMENT: COMPLETE\nVERDICT: APPROVE"
        )
        return subprocess.CompletedProcess(args, 0, output, "")

    monkeypatch.setattr(reviewer, "run_bounded", fake_run)

    assert reviewer.run_review(tmp_path, "main") == 2
    assert len(prompts) == 1
    assert "segment review output exceeds synthesis limit" in capsys.readouterr().err


def test_review_requires_completeness_marker_immediately_before_verdict(
    tmp_path: Path,
) -> None:
    proc = _run(
        tmp_path,
        agy_output=("ARTIFACT: COMPLETE\nunexpected line after marker\nVERDICT: APPROVE"),
        emit_completeness=False,
    )

    assert proc.returncode == 2
    assert "artifact-completeness marker must immediately precede verdict" in proc.stderr


def test_review_fails_closed_when_backend_selects_another_model(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output="F1 none\nVERDICT: APPROVE",
        effective_model="Gemini 3.6 Flash (High)",
    )

    assert proc.returncode == 2
    assert "effective model mismatch" in proc.stderr
    assert "Gemini 3.6 Flash (High)" in proc.stderr


def test_review_streams_large_diff_without_putting_payload_in_argv(tmp_path: Path) -> None:
    diff_file = tmp_path / "large.diff"
    marker = "+large-diff-witness-"
    diff_file.write_text(
        "diff --git a/large.py b/large.py\n" + marker + ("x" * 150_000),
        encoding="utf-8",
    )

    proc = _run(
        tmp_path,
        agy_output="F1 none\nVERDICT: APPROVE",
        diff_file=diff_file,
    )

    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "agy-counter.txt").read_text(encoding="utf-8").strip() == "3"
    segment_prompts = [
        (tmp_path / "agy-prompt.txt").read_text(encoding="utf-8"),
        (tmp_path / "agy-prompt-2.txt").read_text(encoding="utf-8"),
    ]
    assert marker in segment_prompts[0]
    manifests = [
        (tmp_path / "agy-manifest.txt").read_text(encoding="utf-8").splitlines(),
        (tmp_path / "agy-manifest-2.txt").read_text(encoding="utf-8").splitlines(),
    ]
    manifest = [path for paths in manifests for path in paths]
    assert [Path(path).name for path in manifest] == [
        "review-part-001.diff",
        "review-part-002.diff",
        "review-part-003.diff",
        "review-part-003.diff",
        "review-part-004.diff",
        "review-part-005.diff",
    ]
    first_window = (tmp_path / "agy-diff.txt").read_bytes()
    second_window = (tmp_path / "agy-diff-2.txt").read_bytes()
    overlap_bytes = 32 * 1024
    assert first_window[-overlap_bytes:] == second_window[:overlap_bytes]
    assert first_window + second_window[overlap_bytes:] == diff_file.read_bytes()
    synthesis = (tmp_path / "agy-prompt-3.txt").read_text(encoding="utf-8")
    assert "Synthesize the completed segment reviews" in synthesis
    args = "".join(
        path.read_text(encoding="utf-8")
        for path in [
            tmp_path / "agy-args.txt",
            tmp_path / "agy-args-2.txt",
            tmp_path / "agy-args-3.txt",
        ]
    )
    assert marker not in args


def test_review_rejects_permission_denial_even_when_agy_exits_zero(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output=(
            "jetski: no output produced - a tool required the command permission "
            "that headless mode cannot prompt for"
        ),
    )

    assert proc.returncode != 0
    assert "missing exact final verdict" in proc.stderr


def test_review_preserves_findings_on_nonzero_agy_exit(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output="F1 [P1] concrete defect\nVERDICT: BLOCK",
        agy_exit=7,
    )

    assert proc.returncode == 7
    assert proc.stdout.rstrip().endswith("VERDICT: BLOCK")
    assert "agy-review: reviewer failed: exit 7" in proc.stderr


def test_review_rejects_exact_block_verdict(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output="F1 [P1] concrete defect\nVERDICT: BLOCK",
        agy_exit=0,
    )

    assert proc.returncode != 0
    assert proc.stdout.rstrip().endswith("VERDICT: BLOCK")
    assert "blocking findings require resolution" in proc.stderr


def test_review_includes_untracked_file_patch(tmp_path: Path) -> None:
    proc = _run(
        tmp_path,
        agy_output="F1 none\nVERDICT: APPROVE",
        untracked_path="new.py",
    )

    assert proc.returncode == 0, proc.stderr
    prompt = (tmp_path / "agy-prompt.txt").read_text(encoding="utf-8")
    assert "diff --git a/dev/null b/new.py" in prompt
    assert "+untracked witness" in prompt
