#!/usr/bin/env python3
"""Provider-free witness for Codex CLI lifecycle and tool-hook dispatch."""

from __future__ import annotations

import errno
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, ClassVar

ROOT = Path(__file__).resolve().parents[1]
TARGET_EVENTS = ("SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd")
REAL_PERMISSION_HANDLER = "PreToolUse:permission-guard"
CANONICAL_PERMISSION_GUARD_COMMAND = (
    '/usr/bin/python3 "$(git rev-parse --show-toplevel)/.codex/hooks/'
    'codex_hook_adapter.py" permission-guard'
)
PROHIBITED_HOST_DIAGNOSTICS = (
    "unsupported permissionDecision:allow",
    "PreToolUse Failed",
    "invalid PostCompact hook JSON output",
    "PostCompact Failed",
)


def _remove_temp_tree(path: Path, *, attempts: int = 40, delay: float = 0.1) -> None:
    """Remove a witness tree after delayed Codex background writers have exited."""
    for attempt in range(attempts):
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            if exc.errno != errno.ENOTEMPTY or attempt == attempts - 1:
                raise
            time.sleep(delay)


@contextmanager
def _temporary_witness_root() -> Iterator[Path]:
    root = Path(tempfile.mkdtemp(prefix="codex-hook-runtime-"))
    try:
        yield root
    finally:
        _remove_temp_tree(root)


def _sse(events: list[dict[str, Any]]) -> bytes:
    return "".join(
        f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events
    ).encode()


def _created(response_id: str) -> dict[str, Any]:
    return {"type": "response.created", "response": {"id": response_id}}


def _completed(response_id: str) -> dict[str, Any]:
    return {
        "type": "response.completed",
        "response": {
            "id": response_id,
            "usage": {
                "input_tokens": 0,
                "input_tokens_details": None,
                "output_tokens": 0,
                "output_tokens_details": None,
                "total_tokens": 0,
            },
        },
    }


def _response_events(call_number: int) -> list[dict[str, Any]]:
    if call_number == 1:
        return [
            _created("witness-response-1"),
            {
                "type": "response.output_item.done",
                "item": {
                    "type": "function_call",
                    "call_id": "witness-shell",
                    "name": "shell_command",
                    "arguments": json.dumps(
                        {"command": "printf codex-shell-witness > shell-marker.txt"}
                    ),
                },
            },
            _completed("witness-response-1"),
        ]
    if call_number == 2:
        # Responses custom-tool wire format carries the patch as raw `item.input`.
        # Codex normalizes that string to `tool_input.command` before hook dispatch;
        # the witness asserts the resulting apply_patch Pre/PostToolUse events below.
        return [
            _created("witness-response-2"),
            {
                "type": "response.output_item.done",
                "item": {
                    "type": "custom_tool_call",
                    "call_id": "witness-patch",
                    "name": "apply_patch",
                    "input": (
                        "*** Begin Patch\n"
                        "*** Add File: patch-marker.txt\n"
                        "+codex-patch-witness\n"
                        "*** End Patch"
                    ),
                },
            },
            _completed("witness-response-2"),
        ]
    if call_number == 3:
        return [
            _created("witness-response-3"),
            {
                "type": "response.output_item.done",
                "item": {
                    "type": "message",
                    "role": "assistant",
                    "id": "witness-message-3",
                    "content": [{"type": "output_text", "text": "witness complete"}],
                },
            },
            _completed("witness-response-3"),
        ]
    raise RuntimeError(f"unexpected model request {call_number}; expected exactly 3")


class _LoopbackResponsesHandler(BaseHTTPRequestHandler):
    request_count: ClassVar[int] = 0
    errors: ClassVar[list[str]] = []

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("content-length", "0"))
            self.rfile.read(length)
            type(self).request_count += 1
            body = _sse(_response_events(type(self).request_count))
        except (RuntimeError, ValueError) as exc:
            type(self).errors.append(str(exc))
            self.send_error(500, str(exc))
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def _reset_loopback_state() -> None:
    _LoopbackResponsesHandler.request_count = 0
    _LoopbackResponsesHandler.errors = []


def _is_permission_guard_adapter(command: object) -> bool:
    return (
        isinstance(command, str)
        and "codex_hook_adapter.py" in command
        and command.rstrip().endswith("permission-guard")
    )


def _permission_guard_adapter_command() -> str:
    adapter = ROOT / ".codex" / "hooks" / "codex_hook_adapter.py"
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(adapter))} permission-guard"


def _registered_permission_handlers(project_hooks: dict[str, Any]) -> list[str]:
    handlers: list[str] = []
    for event, groups in project_hooks["hooks"].items():
        for group in groups:
            for hook in group["hooks"]:
                command = hook.get("command")
                if not _is_permission_guard_adapter(command):
                    continue
                if command != CANONICAL_PERMISSION_GUARD_COMMAND:
                    raise RuntimeError("unexpected permission-guard command shape")
                handlers.append(f"{event}:permission-guard")
    return handlers


def _witness_hooks(recorder: Path) -> tuple[dict[str, Any], list[str]]:
    project_hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    registered_handlers = _registered_permission_handlers(project_hooks)
    if registered_handlers != [REAL_PERMISSION_HANDLER]:
        raise RuntimeError(
            "expected exactly one Codex permission-guard adapter registration; "
            f"found {len(registered_handlers)}"
        )
    recorder_command = f"{shlex.quote(sys.executable)} {shlex.quote(str(recorder))}"
    hooks: dict[str, list[dict[str, Any]]] = {}
    real_handlers: list[str] = []
    for event in TARGET_EVENTS:
        groups = project_hooks["hooks"].get(event)
        if not groups:
            raise RuntimeError(f"project hooks omit required witness event: {event}")
        hooks[event] = []
        for group in groups:
            witness_group = {key: value for key, value in group.items() if key != "hooks"}
            witness_group["hooks"] = []
            for hook in group["hooks"]:
                if _is_permission_guard_adapter(hook.get("command")):
                    real_handlers.append(f"{event}:permission-guard")
                    witness_hook = dict(hook)
                    witness_hook["command"] = _permission_guard_adapter_command()
                else:
                    witness_hook = {"type": "command", "command": recorder_command, "timeout": 3}
                witness_group["hooks"].append(witness_hook)
            hooks[event].append(witness_group)
    if real_handlers != registered_handlers:
        raise RuntimeError(
            "expected exactly one Codex permission-guard adapter registration; "
            f"found {len(real_handlers)}"
        )
    return {"hooks": hooks}, real_handlers


def _witness_environment(codex_home: Path, repo: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    env["HARNESS_LOOP"] = "1"
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    for name in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        env.pop(name, None)
    return env


def _assert_no_prohibited_host_diagnostics(stdout: str, stderr: str) -> None:
    combined_output = f"{stdout}\n{stderr}"
    diagnostics = [
        diagnostic for diagnostic in PROHIBITED_HOST_DIAGNOSTICS if diagnostic in combined_output
    ]
    if diagnostics:
        raise RuntimeError(f"prohibited host diagnostic: {', '.join(diagnostics)}")


def _assert_witness(
    repo: Path,
    events_path: Path,
    request_count: int,
    *,
    real_handlers: list[str],
) -> dict[str, Any]:
    events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
    if not events:
        raise RuntimeError("Codex CLI emitted no hook events")
    event_names = [event["hook_event_name"] for event in events]
    tool_events = {
        (event["hook_event_name"], event.get("tool_name"))
        for event in events
        if event["hook_event_name"] in {"PreToolUse", "PostToolUse"}
    }
    required_tools = {
        (phase, tool) for phase in ("PreToolUse", "PostToolUse") for tool in ("Bash", "apply_patch")
    }
    if event_names[0] != "SessionStart":
        raise RuntimeError(f"first hook was {event_names[0]!r}, not SessionStart")
    if "Stop" not in event_names or event_names[-1] != "SessionEnd":
        raise RuntimeError(f"missing terminal lifecycle hooks: {event_names}")
    if not required_tools.issubset(tool_events):
        raise RuntimeError(f"missing tool hook dispatch: {sorted(required_tools - tool_events)}")
    if request_count != 3:
        raise RuntimeError(f"local model received {request_count} requests; expected 3")
    if (repo / "shell-marker.txt").read_text(encoding="utf-8") != "codex-shell-witness":
        raise RuntimeError("Bash tool effect did not complete")
    if (repo / "patch-marker.txt").read_text(encoding="utf-8") != "codex-patch-witness\n":
        raise RuntimeError("apply_patch tool effect did not complete")
    session_ids = {event["session_id"] for event in events}
    if len(session_ids) != 1:
        raise RuntimeError(f"hook events span multiple sessions: {sorted(session_ids)}")
    if real_handlers != [REAL_PERMISSION_HANDLER]:
        raise RuntimeError(f"invalid real handler evidence: {real_handlers}")
    return {
        "status": "PASS",
        "provider": "loopback-responses-no-auth",
        "model_metadata": "gpt-5.6-sol",
        "model_requests": request_count,
        "events": event_names,
        "tool_events": sorted(f"{phase}:{tool}" for phase, tool in tool_events),
        "effects": ["shell-marker.txt", "patch-marker.txt"],
        "real_handlers": real_handlers,
    }


def main() -> int:
    codex_bin = os.environ.get("CODEX_BIN") or shutil.which("codex")
    if not codex_bin:
        print("codex-hook-runtime-witness: Codex CLI not found", file=sys.stderr)
        return 2

    with _temporary_witness_root() as witness_root:
        codex_home = witness_root / "codex-home"
        repo = witness_root / "repo"
        events_path = witness_root / "events.jsonl"
        recorder = witness_root / "record_hook.py"
        codex_home.mkdir()
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        recorder.write_text(
            "import pathlib,sys\n"
            f"path = pathlib.Path({str(events_path)!r})\n"
            "with path.open('a', encoding='utf-8') as stream:\n"
            "    stream.write(sys.stdin.read().strip() + '\\n')\n",
            encoding="utf-8",
        )
        hooks, real_handlers = _witness_hooks(recorder)
        (codex_home / "hooks.json").write_text(json.dumps(hooks, indent=2) + "\n", encoding="utf-8")

        _reset_loopback_state()
        server = ThreadingHTTPServer(("127.0.0.1", 0), _LoopbackResponsesHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        port = server.server_address[1]
        (codex_home / "config.toml").write_text(
            (
                'model = "gpt-5.6-sol"\n'
                'model_provider = "witness"\n\n'
                "[model_providers.witness]\n"
                'name = "Local hook witness"\n'
                f'base_url = "http://127.0.0.1:{port}/v1"\n'
                'wire_api = "responses"\n'
                "requires_openai_auth = false\n\n"
                "[features]\n"
                "hooks = true\n"
            ),
            encoding="utf-8",
        )

        env = _witness_environment(codex_home, repo)
        try:
            result = subprocess.run(
                [
                    codex_bin,
                    "exec",
                    "--dangerously-bypass-hook-trust",
                    "--skip-git-repo-check",
                    "--sandbox",
                    "workspace-write",
                    "--cd",
                    str(repo),
                    "Run the supplied local lifecycle and tool-hook witness sequence.",
                ],
                env=env,
                text=True,
                capture_output=True,
                timeout=45,
            )
        except subprocess.TimeoutExpired as exc:
            print(f"codex-hook-runtime-witness: Codex CLI timed out: {exc}", file=sys.stderr)
            return 1
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join(timeout=2)

        try:
            _assert_no_prohibited_host_diagnostics(result.stdout, result.stderr)
        except RuntimeError as exc:
            print(f"codex-hook-runtime-witness: {exc}", file=sys.stderr)
            return 1
        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        if _LoopbackResponsesHandler.errors:
            print("; ".join(_LoopbackResponsesHandler.errors), file=sys.stderr)
            return 1
        try:
            evidence = _assert_witness(
                repo,
                events_path,
                _LoopbackResponsesHandler.request_count,
                real_handlers=real_handlers,
            )
        except (FileNotFoundError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
            print(result.stderr, file=sys.stderr)
            print(f"codex-hook-runtime-witness: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(evidence, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
