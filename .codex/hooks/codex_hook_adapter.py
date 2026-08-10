#!/usr/bin/env python3
"""Adapt the few Claude hook behaviors whose Codex payloads differ."""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_UV_CACHE_DIR = "/tmp/arhugula-uv-cache"
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update) File:\s+(.+?)\s*$", re.MULTILINE)
COMMIT_RE = re.compile(r"^\s*(?:(?:/usr/local/bin/)?rtk\s+)?(?:/usr/bin/)?git\s+commit(?:\s|$)")
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
    """Run one hook command with bounded waits and best-effort process-group cleanup."""
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
            # Hooks are one-shot commands: a successful leader must not leave a background
            # descendant holding the temporary stdio files open.
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


def read_payload() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def project_dir(payload: dict[str, Any]) -> Path:
    candidate = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd")
    return Path(candidate).resolve() if isinstance(candidate, str) and candidate else ROOT


def run_claude_hook(
    relative_path: str, payload: dict[str, Any], cwd: Path, *, timeout: float = 30
) -> dict[str, Any] | None:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(cwd)
    env.setdefault("UV_CACHE_DIR", DEFAULT_UV_CACHE_DIR)
    proc = run_bounded(
        ["/bin/bash", str(ROOT / relative_path)],
        cwd=cwd,
        input_text=json.dumps(payload),
        timeout=timeout,
        env=env,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        return {"systemMessage": f"Codex hook adapter: {relative_path} failed: {detail}"}
    if not proc.stdout.strip():
        return None
    try:
        value = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "systemMessage": (
                f"Codex hook adapter: {relative_path} returned invalid JSON: {proc.stdout.strip()}"
            )
        }
    if not isinstance(value, dict):
        return {
            "systemMessage": (
                f"Codex hook adapter: {relative_path} returned non-object JSON: "
                f"{proc.stdout.strip()}"
            )
        }
    return value


def additional_context(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    message = value.get("systemMessage")
    if isinstance(message, str) and message.strip():
        return message
    specific = value.get("hookSpecificOutput")
    if not isinstance(specific, dict):
        return None
    context = specific.get("additionalContext")
    return context if isinstance(context, str) and context.strip() else None


def response_failed(response: Any) -> bool:
    # Codex documents tool_response as any JSON value; successful local tools may return
    # model-facing text. Text alone carries no reliable success discriminator, so only the
    # structured failure fields below can be normalized into PostToolUseFailure.
    if not isinstance(response, dict):
        return False
    for key in ("exit_code", "exitCode", "returncode"):
        code = response.get(key)
        if isinstance(code, int):
            return code != 0
    if response.get("success") is False:
        return True
    status = response.get("status")
    if isinstance(status, str) and status.lower() in {
        "declined",
        "error",
        "failed",
        "failure",
    }:
        return True
    return bool(response.get("error"))


def error_type(response: Any) -> str:
    if not isinstance(response, dict):
        return "tool_failed"
    for key in ("error_type", "status", "error"):
        value = response.get(key)
        if isinstance(value, str) and value:
            return value
    for key in ("exit_code", "exitCode", "returncode"):
        value = response.get(key)
        if isinstance(value, int):
            return f"exit_{value}"
    return "tool_failed"


def edited_files(payload: dict[str, Any]) -> list[str]:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return []
    path = tool_input.get("file_path")
    if isinstance(path, str) and path:
        return [path]
    if payload.get("tool_name") == "apply_patch":
        for key in ("command", "patch", "patch_content"):
            patch = tool_input.get(key)
            if isinstance(patch, str):
                return list(dict.fromkeys(PATCH_FILE_RE.findall(patch)))
    return []


def post_tool_use(payload: dict[str, Any]) -> int:
    cwd = project_dir(payload)
    contexts: list[str] = []

    response = payload.get("tool_response")
    if response_failed(response):
        failure_payload = dict(payload)
        failure_payload["hook_event_name"] = "PostToolUseFailure"
        failure_payload["error_type"] = error_type(response)
        context = additional_context(
            run_claude_hook("tools/hooks/capture-failure.sh", failure_payload, cwd)
        )
        if context:
            contexts.append(context)

    for path in edited_files(payload):
        lint_payload = dict(payload)
        lint_payload["hook_event_name"] = "PostToolUse"
        lint_payload["tool_input"] = {"file_path": path}
        context = additional_context(
            run_claude_hook("tools/hooks/postedit-lint.sh", lint_payload, cwd)
        )
        if context:
            contexts.append(context)

    if contexts:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": "\n\n".join(contexts),
                    }
                },
                separators=(",", ":"),
            )
        )
    return 0


class CompactContextError(ValueError):
    """The shared PostCompact producer returned unusable output."""


def compact_context(payload: dict[str, Any]) -> str | None:
    value = run_claude_hook(
        "tools/hooks/postcompact-reinject.sh", payload, project_dir(payload), timeout=10
    )
    if value is None:
        return None
    if "systemMessage" in value:
        detail = value["systemMessage"]
        raise CompactContextError(
            detail
            if isinstance(detail, str) and detail.strip()
            else "producer returned a diagnostic"
        )
    specific = value.get("hookSpecificOutput")
    if not isinstance(specific, dict):
        raise CompactContextError("producer returned no PostCompact output")
    if specific.get("hookEventName") != "PostCompact":
        raise CompactContextError("producer returned the wrong hook event")
    context = specific.get("additionalContext")
    if not isinstance(context, str) or not context.strip():
        raise CompactContextError("producer returned no usable context")
    return context


def post_compact(payload: dict[str, Any]) -> int:
    try:
        context = compact_context(payload)
    except CompactContextError as exc:
        print(f"post-compact adapter: {exc}", file=sys.stderr)
        return 2
    if context:
        print(json.dumps({"systemMessage": context}, separators=(",", ":")))
    return 0


def print_compact_context(payload: dict[str, Any]) -> int:
    try:
        context = compact_context(payload)
    except CompactContextError as exc:
        print(f"compact-context adapter: {exc}", file=sys.stderr)
        return 2
    if context:
        print(context)
    return 0


def permission_guard(payload: dict[str, Any]) -> int:
    if payload.get("hook_event_name") != "PreToolUse":
        print("permission-guard adapter requires PreToolUse", file=sys.stderr)
        return 2

    value = run_claude_hook("tools/hooks/permission-guard.sh", payload, project_dir(payload))
    if value is None:
        return 0
    specific = value.get("hookSpecificOutput")
    if not isinstance(specific, dict) or specific.get("hookEventName") != "PreToolUse":
        diagnostic = value.get("systemMessage")
        if isinstance(diagnostic, str) and diagnostic.strip():
            print(diagnostic, file=sys.stderr)
        else:
            print("permission-guard adapter received invalid PreToolUse output", file=sys.stderr)
        return 2

    decision = specific.get("permissionDecision")
    if decision == "allow":
        if "updatedInput" not in specific:
            return 0
        if isinstance(specific["updatedInput"], dict):
            print(json.dumps(value, separators=(",", ":")))
            return 0
        print(
            "permission-guard adapter received allow with non-object updatedInput",
            file=sys.stderr,
        )
        return 2
    if decision == "deny":
        reason = specific.get("permissionDecisionReason")
        if isinstance(reason, str) and reason.strip():
            print(json.dumps(value, separators=(",", ":")))
            return 0
        print("permission-guard adapter received deny without a reason", file=sys.stderr)
        return 2

    print("permission-guard adapter received unsupported permission decision", file=sys.stderr)
    return 2


def pre_commit(payload: dict[str, Any]) -> int:
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if payload.get("tool_name") != "Bash" or not isinstance(command, str):
        return 0
    if not COMMIT_RE.search(command):
        return 0

    cwd = project_dir(payload)
    env = os.environ.copy()
    env.setdefault("UV_CACHE_DIR", DEFAULT_UV_CACHE_DIR)
    # Preserve the canonical Claude hook's two independent gates: static typing and an
    # explicit proof that the command runs inside the intended Git worktree.
    for argv in (["uv", "run", "pyright"], ["git", "rev-parse", "--show-toplevel"]):
        proc = run_bounded(
            argv,
            cwd=cwd,
            timeout=120,
            env=env,
        )
        if proc.returncode != 0:
            detail = proc.stdout.strip() or proc.stderr.strip() or f"exit {proc.returncode}"
            print(detail, file=sys.stderr)
            return 2
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {
        "post-tool-use",
        "pre-commit",
        "permission-guard",
        "post-compact",
        "compact-context",
    }:
        print(
            "usage: codex_hook_adapter.py "
            "post-tool-use|pre-commit|permission-guard|post-compact|compact-context",
            file=sys.stderr,
        )
        return 2
    if os.environ.get("HARNESS_CODEX_REVIEW_ISOLATED") == "1":
        return 0
    payload = read_payload()
    if sys.argv[1] == "post-tool-use":
        return post_tool_use(payload)
    if sys.argv[1] == "pre-commit":
        return pre_commit(payload)
    if sys.argv[1] == "permission-guard":
        return permission_guard(payload)
    if sys.argv[1] == "post-compact":
        return post_compact(payload)
    return print_compact_context(payload)


if __name__ == "__main__":
    raise SystemExit(main())
