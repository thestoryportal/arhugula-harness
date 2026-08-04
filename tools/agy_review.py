#!/usr/bin/env python3
"""Run an OAuth-authenticated Antigravity CLI diff review and fail closed."""

from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

MODEL_ARGUMENT = "Gemini 3.1 Pro (High)"
EXPECTED_MODEL_LABEL = "Gemini 3.1 Pro (High)"
MAX_DIFF_PART_BYTES = 32 * 1024
MAX_REVIEW_SEGMENT_BYTES = 96 * 1024
MAX_REVIEW_RESULT_BYTES = 32 * 1024
TOTAL_REVIEW_TIMEOUT_SECONDS = 1260.0
MAX_AGY_PRINT_TIMEOUT_SECONDS = 1200
PARENT_TIMEOUT_GRACE_SECONDS = 5
ARTIFACT_COMPLETE_MARKER = "ARTIFACT: COMPLETE"
SEGMENT_COMPLETE_MARKER = "SEGMENT: COMPLETE"
PROVIDER_ENV = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
)
VERDICTS = {"VERDICT: APPROVE", "VERDICT: BLOCK"}
MODEL_LABEL_RE = re.compile(r'Propagating selected model override to backend: label="([^"]+)"')
TERMINATION_GRACE_SECONDS = 5.0


class TerminationRequested(BaseException):
    def __init__(self, signum: int) -> None:
        self.exit_code = 128 + signum


def handle_termination_signal(signum: int, _frame: object) -> None:
    raise TerminationRequested(signum)


def terminate_bounded(process: subprocess.Popen[str]) -> None:
    """Terminate the direct child and its original process group without an unbounded wait."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except (PermissionError, ProcessLookupError):
            pass
    if process.poll() is None:
        try:
            process.terminate()
        except (PermissionError, ProcessLookupError):
            pass
    deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
    while time.monotonic() < deadline:
        direct_alive = process.poll() is None
        group_alive = False
        if os.name == "posix":
            try:
                os.killpg(process.pid, 0)
                group_alive = True
            except (PermissionError, ProcessLookupError):
                pass
        if not direct_alive and not group_alive:
            return
        remaining = deadline - time.monotonic()
        if direct_alive:
            try:
                process.wait(timeout=min(0.05, remaining))
            except subprocess.TimeoutExpired:
                pass
        else:
            time.sleep(min(0.05, remaining))
    # The leader may exit on TERM while a background descendant ignores it. Escalate
    # the still-live original process group only after the real group grace period.
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (PermissionError, ProcessLookupError):
            pass
    if process.poll() is None:
        try:
            process.kill()
        except (PermissionError, ProcessLookupError):
            pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def run_bounded(
    args: list[str],
    *,
    cwd: Path,
    timeout: float,
    env: dict[str, str],
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run one command with bounded waits and best-effort process-group cleanup."""
    streams = []
    process: subprocess.Popen[str] | None = None
    try:
        stdin_stream = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
        streams.append(stdin_stream)
        stdout_stream = tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")
        streams.append(stdout_stream)
        stderr_stream = tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")
        streams.append(stderr_stream)
        if input_text is not None:
            stdin_stream.write(input_text)
            stdin_stream.seek(0)
        deferred_signal: int | None = None

        def defer_termination(signum: int, _frame: object) -> None:
            nonlocal deferred_signal
            deferred_signal = signum

        previous_sigterm_handler = None
        previous_sigint_handler = None
        if os.name == "posix" and threading.current_thread() is threading.main_thread():
            previous_sigterm_handler = signal.signal(signal.SIGTERM, defer_termination)
            previous_sigint_handler = signal.signal(signal.SIGINT, defer_termination)
        popen_error: OSError | None = None
        try:
            try:
                try:
                    process = subprocess.Popen(
                        args,
                        cwd=cwd,
                        stdin=stdin_stream,
                        stdout=stdout_stream,
                        stderr=stderr_stream,
                        text=True,
                        errors="replace",
                        env=env,
                        start_new_session=os.name == "posix",
                    )
                except OSError as exc:
                    popen_error = exc
            finally:
                if previous_sigterm_handler is not None:
                    signal.signal(signal.SIGTERM, previous_sigterm_handler)
                if previous_sigint_handler is not None:
                    signal.signal(signal.SIGINT, previous_sigint_handler)
            if deferred_signal is not None:
                raise TerminationRequested(deferred_signal)
            if popen_error is not None:
                return subprocess.CompletedProcess(args, 127, "", str(popen_error))
            assert process is not None
            timed_out = False
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_bounded(process)
            else:
                # Hooks/reviewers are one-shot commands: a successful leader must not leave a
                # background descendant holding the temporary stdio files open.
                terminate_bounded(process)
        except BaseException:
            if process is not None:
                terminate_bounded(process)
            raise
        stdout_stream.seek(0)
        stderr_stream.seek(0)
        stdout = stdout_stream.read()
        stderr = stderr_stream.read()
        if timed_out:
            detail = f"command timed out after {timeout} seconds"
            stderr = f"{stderr.rstrip()}\n{detail}".lstrip()
            return subprocess.CompletedProcess(args, 124, stdout, stderr)
        return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
    finally:
        for stream in streams:
            stream.close()


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )


def collect_diff(repo: Path, base: str) -> str:
    tracked = run_git(repo, "diff", "--merge-base", "--binary", base)
    if tracked.returncode != 0:
        raise RuntimeError(tracked.stderr.strip() or "git diff failed")

    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    if untracked.returncode != 0:
        raise RuntimeError(untracked.stderr.strip() or "git ls-files failed")

    parts = [tracked.stdout]
    for relative_path in filter(None, untracked.stdout.split("\0")):
        patch = run_git(
            repo,
            "diff",
            "--no-index",
            "--binary",
            "--",
            "/dev/null",
            relative_path,
        )
        if patch.returncode not in {0, 1}:
            raise RuntimeError(
                patch.stderr.strip() or f"could not diff untracked file: {relative_path}"
            )
        parts.append(patch.stdout)

    diff = "".join(parts).strip()
    if not diff:
        raise RuntimeError("review diff is empty")
    return diff


def write_diff_parts(directory: Path, diff: str) -> list[Path]:
    """Write ordered UTF-8 chunks small enough for Antigravity's file viewer."""
    encoded = diff.encode("utf-8")
    parts: list[Path] = []
    start = 0
    while start < len(encoded):
        end = min(start + MAX_DIFF_PART_BYTES, len(encoded))
        while True:
            try:
                encoded[start:end].decode("utf-8")
                break
            except UnicodeDecodeError as exc:
                end = start + exc.start
        path = directory / f"review-part-{len(parts) + 1:03d}.diff"
        path.write_bytes(encoded[start:end])
        parts.append(path)
        start = end
    return parts


def group_diff_parts(diff_paths: list[Path]) -> list[list[Path]]:
    """Build context-bounded windows with one raw part of boundary overlap."""
    groups: list[list[Path]] = []
    start = 0
    while start < len(diff_paths):
        current: list[Path] = []
        current_bytes = 0
        end = start
        while end < len(diff_paths):
            path = diff_paths[end]
            part_bytes = path.stat().st_size
            if part_bytes > MAX_REVIEW_SEGMENT_BYTES:
                raise ValueError(f"diff part exceeds review segment limit: {path}")
            if current and current_bytes + part_bytes > MAX_REVIEW_SEGMENT_BYTES:
                break
            current.append(path)
            current_bytes += part_bytes
            end += 1
        groups.append(current)
        if end == len(diff_paths):
            break
        start = end - 1 if len(current) > 1 else end
    return groups


def review_prompt(
    repo: Path,
    diff_paths: list[Path],
    *,
    segment_index: int | None = None,
    segment_count: int | None = None,
) -> str:
    numbered_paths = "\n".join(f"{index}. {path}" for index, path in enumerate(diff_paths, start=1))
    if segment_index is None or segment_count is None:
        scope = (
            f"The authoritative workspace root is {repo}. The complete diff is split into "
            f"{len(diff_paths)} ordered parts so every read stays below the file-view limit. Use "
        )
        completion_marker = ARTIFACT_COMPLETE_MARKER
        concatenation_scope = "the complete diff"
        synopsis = ""
    else:
        scope = (
            f"The authoritative workspace root is {repo}. This is review segment "
            f"{segment_index} of {segment_count} for one complete diff. This segment is split into "
            f"{len(diff_paths)} ordered parts so every read stays below the file-view limit. Use "
        )
        completion_marker = SEGMENT_COMPLETE_MARKER
        concatenation_scope = "this assigned review segment"
        synopsis = (
            "Adjacent review segments share one complete 32 KiB raw part so evidence crossing a "
            "window boundary remains visible; treat duplicated boundary text as context and report "
            "each finding once. "
            "Before the completion marker, include a concise SEGMENT SYNOPSIS of changed "
            "contracts, definitions, references, and open questions needed for a later "
            "cross-segment synthesis.\n"
        )
    return (
        "You are an out-of-family code reviewer for an agent-harness monorepo.\n"
        f"{scope}"
        f"exactly {len(diff_paths)} read-only view_file calls, one for each numbered part in "
        f"order. The parts concatenate byte-for-byte into {concatenation_scope}:\n"
        f"{numbered_paths}\n"
        "Do not open surrounding workspace files, grep or search, or "
        "inspect any other path.\n"
        "Review that concrete artifact for real defects: correctness, hook and permission "
        "semantics, contract drift, unsafe state handling, and tests that would stay green if "
        "the change were reverted. Report at most 5 findings, numbered F1..Fn and tagged\n"
        "[P1]/[P2]/[P3] with file:line; no style nits. Do not edit files. Finish immediately "
        "after analyzing that diff.\n"
        "Only report a finding proven entirely by the supplied diff. Do not infer helper semantics "
        "when its definition is absent from the diff. Test-only regression coverage for behavior "
        "outside a scoped delta is valid and need not repeat the implementation change.\n"
        "The --add-dir exposes the absolute diff path inside the Antigravity sandbox; successful "
        "access to this artifact is required before analysis.\n"
        "Do not invoke terminal commands or request command permission. Do not invoke URL, "
        "browser, or MCP tools.\n"
        "Do not read dotfiles, environment files, or user configuration. "
        f"{synopsis}"
        "Only after every numbered part was read completely without truncation, emit the exact "
        "line\n"
        f"{completion_marker}\n"
        "immediately before the verdict. If any part is incomplete or unreadable, omit that "
        "marker and use VERDICT: BLOCK. End with exactly\n"
        "VERDICT: APPROVE or VERDICT: BLOCK as the final non-empty line.\n\n"
        "Apply the current official Codex hook protocol when reviewing hook code:\n"
        "Shell and unified-exec hooks match as Bash; apply_patch matches apply_patch, Edit, "
        "or Write.\n"
        "Those aliases affect matcher selection only.\n"
        'A matcher of "Bash" already covers Shell and unified-exec aliases.\n'
        'Hook payload still reports exactly tool_name: "apply_patch" or "Bash".\n'
        "Both canonical names and documented aliases are valid in matcher regexes; neither "
        "form is a defect.\n"
        "The *** Add File: and *** Update File: markers are Codex apply_patch command syntax, "
        "not Antigravity schema.\n"
        "Bash/apply_patch arguments are in tool_input.command.\n"
        "The provider-free Codex runtime witness is also a local Responses API model double. "
        "At that model wire boundary, an apply_patch custom_tool_call correctly carries the raw "
        "patch string in item.input; Codex then normalizes it into hook tool_input.command. Do "
        "not require the Responses custom-tool input string to be a JSON object.\n"
        "The common cwd is a runtime-supplied common field for the session, not a value inside "
        "agent-supplied tool_input. A successful git rev-parse check mirrors the Claude "
        "pre-commit gate; root comparison is optional hardening, not a Claude-parity requirement "
        "unless a concrete Codex path can replace the runtime session cwd. Do not substitute "
        "Antigravity, IDE, or app-server tool schemas for this Codex hook schema.\n\n"
        "The Antigravity --model display label is intentional and empirically required: the "
        "programmatic-looking slug silently selected Flash on this CLI, while this label selected "
        "Pro. The wrapper independently parses the route log and fails closed unless the effective "
        "backend label is exactly Gemini 3.1 Pro (High).\n\n"
        "The standing operator authorization requires this OAuth review to run headlessly with no "
        "permission gate. The agy invocation therefore deliberately combines --sandbox, plan mode, "
        "and --dangerously-skip-permissions while the reviewer brief forbids tool use. "
        "Do not report "
        "that approved flag combination by itself; report only a concrete sandbox escape or an "
        "actual unauthorized effect reachable through it.\n"
    )


def synthesis_prompt(repo: Path, result_paths: list[Path]) -> str:
    numbered_paths = "\n".join(f"{index}. {path}" for index, path in enumerate(result_paths, 1))
    return (
        "You are the final out-of-family synthesis reviewer for an agent-harness monorepo.\n"
        "Synthesize the completed segment reviews into one final verdict.\n"
        f"The authoritative workspace root is {repo}. Independent Gemini 3.1 Pro review "
        "segments covered every byte of one ordered diff under a fail-closed wrapper. Their "
        f"validated results are in {len(result_paths)} files. Use exactly {len(result_paths)} "
        "read-only view_file calls, one for each numbered result in order:\n"
        f"{numbered_paths}\n"
        "Do not open surrounding workspace files, grep or search, or inspect any other path. "
        "Do not invoke terminal, URL, browser, or MCP tools. Adjacent raw-review windows overlap "
        "by one complete 32 KiB part. Reconcile duplicate findings from that overlap and "
        "compare the segment synopses for cross-segment contract drift, incompatible definitions, "
        "or inconsistent references. Preserve any proven blocking finding. Report at most 5 "
        "findings, numbered F1..Fn and tagged [P1]/[P2]/[P3] with file:line; no style nits. "
        "Only report findings supported by the segment results. If any segment verdict is BLOCK, "
        "the synthesis verdict must also be BLOCK. After every numbered result was read "
        "completely, emit the exact line\n"
        f"{ARTIFACT_COMPLETE_MARKER}\n"
        "immediately before the verdict. If any result is incomplete or unreadable, omit that "
        "marker and use VERDICT: BLOCK. End with exactly VERDICT: APPROVE or VERDICT: BLOCK as "
        "the final non-empty line.\n"
    )


def verify_effective_model(log_path: Path) -> str | None:
    try:
        log = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"could not read Antigravity route log: {exc}"
    labels = MODEL_LABEL_RE.findall(log)
    if not labels:
        return "Antigravity did not report an effective backend model"
    selected = sorted(set(labels))
    if selected != [EXPECTED_MODEL_LABEL]:
        return f"effective model mismatch: expected {EXPECTED_MODEL_LABEL}; observed {selected}"
    return None


def agy_print_timeout(timeout: float) -> str:
    seconds = max(
        1,
        min(MAX_AGY_PRINT_TIMEOUT_SECONDS, int(timeout) - PARENT_TIMEOUT_GRACE_SECONDS),
    )
    return "20m" if seconds == MAX_AGY_PRINT_TIMEOUT_SECONDS else f"{seconds}s"


def agy_command(scratch: str, log_path: Path, prompt: str, *, timeout: float) -> list[str]:
    return [
        "agy",
        "--sandbox",
        "--dangerously-skip-permissions",
        "--new-project",
        "--mode",
        "plan",
        "--model",
        MODEL_ARGUMENT,
        "--add-dir",
        scratch,
        "--log-file",
        str(log_path),
        "--print-timeout",
        agy_print_timeout(timeout),
        "-p",
        prompt,
    ]


def validate_review_output(output: str, marker: str) -> tuple[str | None, str | None]:
    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    marker_name = "artifact" if marker == ARTIFACT_COMPLETE_MARKER else "segment"
    if marker not in output_lines:
        return f"missing exact {marker_name}-completeness marker", None
    if len(output_lines) < 2 or output_lines[-2] != marker:
        return f"{marker_name}-completeness marker must immediately precede verdict", None
    final_line = output_lines[-1] if output_lines else ""
    if final_line not in VERDICTS:
        return "missing exact final verdict", None
    return None, final_line


def report_process_failure(proc: subprocess.CompletedProcess[str]) -> int:
    output = proc.stdout.strip()
    if output:
        print(output)
    detail = proc.stderr.strip() or f"exit {proc.returncode}"
    if proc.returncode in {124, 127}:
        print(f"agy-review: reviewer unavailable: {detail}", file=sys.stderr)
        return 2
    print(f"agy-review: reviewer failed: {detail}", file=sys.stderr)
    return proc.returncode


def remaining_review_timeout(deadline: float) -> float | None:
    remaining = deadline - time.monotonic()
    return remaining if remaining > PARENT_TIMEOUT_GRACE_SECONDS else None


def run_review(repo: Path, base: str) -> int:
    try:
        diff = collect_diff(repo, base)
    except RuntimeError as exc:
        print(f"agy-review: {exc}", file=sys.stderr)
        return 2

    env = os.environ.copy()
    for name in PROVIDER_ENV:
        env.pop(name, None)
    deadline = time.monotonic() + TOTAL_REVIEW_TIMEOUT_SECONDS
    try:
        with tempfile.TemporaryDirectory(prefix="arhugula-agy-review-") as scratch:
            diff_paths = write_diff_parts(Path(scratch), diff)
            groups = group_diff_parts(diff_paths)
            if len(groups) == 1:
                review_specs = [
                    (
                        review_prompt(repo, groups[0]),
                        ARTIFACT_COMPLETE_MARKER,
                        Path(scratch) / "route.log",
                    )
                ]
            else:
                review_specs = [
                    (
                        review_prompt(
                            repo,
                            group,
                            segment_index=index,
                            segment_count=len(groups),
                        ),
                        SEGMENT_COMPLETE_MARKER,
                        Path(scratch) / f"route-segment-{index:03d}.log",
                    )
                    for index, group in enumerate(groups, 1)
                ]

            accepted_outputs: list[str] = []
            accepted_verdicts: list[str] = []
            result_paths: list[Path] = []
            for index, (prompt, marker, log_path) in enumerate(review_specs, 1):
                timeout = remaining_review_timeout(deadline)
                if timeout is None:
                    print(
                        "agy-review: reviewer unavailable: whole-review deadline expired",
                        file=sys.stderr,
                    )
                    return 2
                proc = run_bounded(
                    agy_command(scratch, log_path, prompt, timeout=timeout),
                    cwd=repo,
                    timeout=timeout,
                    env=env,
                )
                if proc.returncode != 0:
                    return report_process_failure(proc)
                model_error = verify_effective_model(log_path)
                if model_error is not None:
                    print(f"agy-review: {model_error}", file=sys.stderr)
                    return 2
                output = proc.stdout.strip()
                validation_error, verdict = validate_review_output(output, marker)
                if validation_error is not None:
                    if output:
                        print(output, file=sys.stderr)
                    print(f"agy-review: {validation_error}", file=sys.stderr)
                    return 2
                assert verdict is not None
                if marker == SEGMENT_COMPLETE_MARKER and len(output.encode("utf-8")) > (
                    MAX_REVIEW_RESULT_BYTES
                ):
                    print(
                        "agy-review: segment review output exceeds synthesis limit",
                        file=sys.stderr,
                    )
                    return 2
                accepted_outputs.append(output)
                accepted_verdicts.append(verdict)
                if len(groups) > 1:
                    result_path = Path(scratch) / f"review-result-{index:03d}.txt"
                    covered = ", ".join(path.name for path in groups[index - 1])
                    result_path.write_text(
                        f"SEGMENT {index}/{len(groups)}\nCOVERED PARTS: {covered}\n{output}\n",
                        encoding="utf-8",
                    )
                    result_paths.append(result_path)

            if len(groups) > 1:
                log_path = Path(scratch) / "route-synthesis.log"
                timeout = remaining_review_timeout(deadline)
                if timeout is None:
                    print(
                        "agy-review: reviewer unavailable: whole-review deadline expired",
                        file=sys.stderr,
                    )
                    return 2
                proc = run_bounded(
                    agy_command(
                        scratch,
                        log_path,
                        synthesis_prompt(repo, result_paths),
                        timeout=timeout,
                    ),
                    cwd=repo,
                    timeout=timeout,
                    env=env,
                )
                if proc.returncode != 0:
                    return report_process_failure(proc)
                model_error = verify_effective_model(log_path)
                if model_error is not None:
                    print(f"agy-review: {model_error}", file=sys.stderr)
                    return 2
                output = proc.stdout.strip()
                validation_error, verdict = validate_review_output(output, ARTIFACT_COMPLETE_MARKER)
                if validation_error is not None:
                    if output:
                        print(output, file=sys.stderr)
                    print(f"agy-review: {validation_error}", file=sys.stderr)
                    return 2
                assert verdict is not None
                if "VERDICT: BLOCK" in accepted_verdicts and verdict != "VERDICT: BLOCK":
                    print(output, file=sys.stderr)
                    print(
                        "agy-review: synthesis contradicted a blocking segment verdict",
                        file=sys.stderr,
                    )
                    return 2
            else:
                output = accepted_outputs[0]
                verdict = accepted_verdicts[0]
    except OSError as exc:
        print(f"agy-review: reviewer unavailable: {exc}", file=sys.stderr)
        return 2

    print(f"agy-review: effective model: {EXPECTED_MODEL_LABEL}")
    print(output)
    if verdict == "VERDICT: BLOCK":
        print("agy-review: blocking findings require resolution", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    previous_sigterm = signal.signal(signal.SIGTERM, handle_termination_signal)
    try:
        return run_review(Path.cwd(), args.base)
    except TerminationRequested as exc:
        return exc.exit_code
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
