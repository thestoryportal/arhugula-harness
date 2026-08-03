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
import time
from pathlib import Path

MODEL_ARGUMENT = "Gemini 3.1 Pro (High)"
EXPECTED_MODEL_LABEL = "Gemini 3.1 Pro (High)"
MAX_DIFF_PART_BYTES = 32 * 1024
ARTIFACT_COMPLETE_MARKER = "ARTIFACT: COMPLETE"
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


def terminate_bounded(process: subprocess.Popen[str]) -> None:
    """Terminate the direct child and its original process group without an unbounded wait."""
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        try:
            process.terminate()
        except ProcessLookupError:
            pass
    deadline = time.monotonic() + TERMINATION_GRACE_SECONDS
    while time.monotonic() < deadline:
        direct_alive = process.poll() is None
        group_alive = False
        if os.name == "posix":
            try:
                os.killpg(process.pid, 0)
                group_alive = True
            except ProcessLookupError:
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
        except ProcessLookupError:
            pass
    if process.poll() is None:
        try:
            process.kill()
        except ProcessLookupError:
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
            return subprocess.CompletedProcess(args, 127, "", str(exc))
        timed_out = False
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            terminate_bounded(process)
        except BaseException:
            terminate_bounded(process)
            raise
        else:
            # Hooks/reviewers are one-shot commands: a successful leader must not leave a
            # background descendant holding the temporary stdio files open.
            terminate_bounded(process)
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


def review_prompt(repo: Path, diff_paths: list[Path]) -> str:
    numbered_paths = "\n".join(f"{index}. {path}" for index, path in enumerate(diff_paths, start=1))
    return (
        "You are an out-of-family code reviewer for an agent-harness monorepo.\n"
        f"The authoritative workspace root is {repo}. The complete diff is split into "
        f"{len(diff_paths)} ordered parts so every read stays below the file-view limit. Use "
        f"exactly {len(diff_paths)} read-only view_file calls, one for each numbered part in "
        "order. The parts concatenate byte-for-byte into the complete diff:\n"
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
        "Do not read dotfiles, environment files, or user configuration. Only after every "
        "numbered part was read completely without truncation, emit the exact line\n"
        f"{ARTIFACT_COMPLETE_MARKER}\n"
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


def run_review(repo: Path, base: str) -> int:
    try:
        diff = collect_diff(repo, base)
    except RuntimeError as exc:
        print(f"agy-review: {exc}", file=sys.stderr)
        return 2

    env = os.environ.copy()
    for name in PROVIDER_ENV:
        env.pop(name, None)
    model_error: str | None = None
    try:
        with tempfile.TemporaryDirectory(prefix="arhugula-agy-review-") as scratch:
            diff_paths = write_diff_parts(Path(scratch), diff)
            log_path = Path(scratch) / "route.log"
            # The reviewed artifact is outside the workspace sandbox, so the agy command
            # below exposes this exact scratch directory with --add-dir.
            proc = run_bounded(
                [
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
                    "20m",
                    "-p",
                    review_prompt(repo, diff_paths),
                ],
                cwd=repo,
                timeout=1260,
                env=env,
            )
            if proc.returncode == 0:
                # This value is enforced below after the temporary route log is read.
                model_error = verify_effective_model(log_path)
    except OSError as exc:
        print(f"agy-review: reviewer unavailable: {exc}", file=sys.stderr)
        return 2

    output = proc.stdout.strip()
    if proc.returncode != 0:
        if output:
            print(output)
        detail = proc.stderr.strip() or f"exit {proc.returncode}"
        if proc.returncode in {124, 127}:
            print(f"agy-review: reviewer unavailable: {detail}", file=sys.stderr)
            return 2
        print(f"agy-review: reviewer failed: {detail}", file=sys.stderr)
        return proc.returncode

    if model_error is not None:
        # Fail closed if Antigravity routed anywhere except the required Pro tier.
        print(f"agy-review: {model_error}", file=sys.stderr)
        return 2

    output_lines = [line.strip() for line in output.splitlines() if line.strip()]
    if ARTIFACT_COMPLETE_MARKER not in output_lines:
        if output:
            print(output, file=sys.stderr)
        print("agy-review: missing exact artifact-completeness marker", file=sys.stderr)
        return 2
    if len(output_lines) < 2 or output_lines[-2] != ARTIFACT_COMPLETE_MARKER:
        if output:
            print(output, file=sys.stderr)
        print(
            "agy-review: artifact-completeness marker must immediately precede verdict",
            file=sys.stderr,
        )
        return 2

    final_line = output_lines[-1] if output_lines else ""
    if final_line not in VERDICTS:
        if output:
            print(output, file=sys.stderr)
        print("agy-review: missing exact final verdict", file=sys.stderr)
        return 2

    print(f"agy-review: effective model: {EXPECTED_MODEL_LABEL}")
    print(output)
    if final_line == "VERDICT: BLOCK":
        print("agy-review: blocking findings require resolution", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    return run_review(Path.cwd(), args.base)


if __name__ == "__main__":
    raise SystemExit(main())
