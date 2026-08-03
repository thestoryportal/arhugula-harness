"""Behavioral tests for the fail-closed Antigravity diff reviewer."""

from __future__ import annotations

import importlib.util
import os
import signal
import subprocess
import sys
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


def _fake_commands(
    tmp_path: Path,
    *,
    agy_output: str,
    agy_exit: int = 0,
    effective_model: str = "Gemini 3.1 Pro (High)",
    emit_completeness: bool = True,
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
    rendered_agy_output = agy_output
    if emit_completeness:
        output_lines = agy_output.splitlines()
        output_lines.insert(-1, "ARTIFACT: COMPLETE")
        rendered_agy_output = "\n".join(output_lines)
    agy.write_text(
        "#!/bin/sh\n"
        'pwd > "$AGY_CWD_CAPTURE"\n'
        'printf \'%s\\n\' "$@" > "$AGY_ARGS_CAPTURE"\n'
        "prev=''\n"
        "add_dir=''\n"
        "log_file=''\n"
        'for arg in "$@"; do\n'
        '  if [ "$prev" = \'-p\' ]; then printf \'%s\\n\' "$arg" > "$AGY_CAPTURE"; fi\n'
        '  if [ "$prev" = \'--add-dir\' ]; then add_dir="$arg"; fi\n'
        '  if [ "$prev" = \'--log-file\' ]; then log_file="$arg"; fi\n'
        '  prev="$arg"\n'
        "done\n"
        f"printf 'Propagating selected model override to backend: label=\"{effective_model}\"\\n' "
        '  > "$log_file"\n'
        'sed -n \'s/^[0-9][0-9]*\\. //p\' "$AGY_CAPTURE" > "$AGY_MANIFEST_CAPTURE"\n'
        '[ -s "$AGY_MANIFEST_CAPTURE" ] || exit 8\n'
        ': > "$AGY_DIFF_CAPTURE"\n'
        "while IFS= read -r diff_part; do "
        '[ -f "$diff_part" ] || exit 8; cat "$diff_part" >> "$AGY_DIFF_CAPTURE"; '
        'done < "$AGY_MANIFEST_CAPTURE"\n'
        'cat "$AGY_DIFF_CAPTURE" >> "$AGY_CAPTURE"\n'
        'if [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}${GOOGLE_GENAI_USE_VERTEXAI:-}'
        "${GOOGLE_APPLICATION_CREDENTIALS:-}${GOOGLE_CLOUD_PROJECT:-}"
        '${GOOGLE_CLOUD_LOCATION:-}" ]; then\n'
        "  echo 'provider environment leaked'\n"
        "  exit 9\n"
        "fi\n"
        f"printf '%b\\n' {rendered_agy_output!r}\n"
        f"exit {agy_exit}\n",
        encoding="utf-8",
    )
    agy.chmod(0o755)
    return bin_dir, capture


def _run(
    tmp_path: Path,
    *,
    agy_output: str,
    agy_exit: int = 0,
    untracked_path: str = "",
    diff_file: Path | None = None,
    effective_model: str = "Gemini 3.1 Pro (High)",
    emit_completeness: bool = True,
) -> subprocess.CompletedProcess[str]:
    bin_dir, capture = _fake_commands(
        tmp_path,
        agy_output=agy_output,
        agy_exit=agy_exit,
        effective_model=effective_model,
        emit_completeness=emit_completeness,
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
    prompt = (tmp_path / "agy-prompt.txt").read_text(encoding="utf-8")
    assert marker in prompt
    manifest = (tmp_path / "agy-manifest.txt").read_text(encoding="utf-8").splitlines()
    assert [Path(path).name for path in manifest] == [
        f"review-part-{index:03d}.diff" for index in range(1, len(manifest) + 1)
    ]
    assert len(manifest) > 1
    assert (tmp_path / "agy-diff.txt").read_bytes() == diff_file.read_bytes()
    args = (tmp_path / "agy-args.txt").read_text(encoding="utf-8")
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
