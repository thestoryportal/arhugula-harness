#!/usr/bin/env python3
"""Provider-free witness for Codex CLI lifecycle and tool-hook dispatch."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, ClassVar

ROOT = Path(__file__).resolve().parents[1]
TARGET_EVENTS = ("SessionStart", "PreToolUse", "PostToolUse", "Stop", "SessionEnd")


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


def _witness_hooks(recorder: Path) -> dict[str, Any]:
    project_hooks = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    recorder_command = f"{shlex.quote(sys.executable)} {shlex.quote(str(recorder))}"
    hooks: dict[str, list[dict[str, Any]]] = {}
    for event in TARGET_EVENTS:
        groups = project_hooks["hooks"].get(event)
        if not groups:
            raise RuntimeError(f"project hooks omit required witness event: {event}")
        hooks[event] = []
        for group in groups:
            witness_group = {key: value for key, value in group.items() if key != "hooks"}
            witness_group["hooks"] = [
                {"type": "command", "command": recorder_command, "timeout": 3}
            ]
            hooks[event].append(witness_group)
    return {"hooks": hooks}


def _assert_witness(repo: Path, events_path: Path, request_count: int) -> dict[str, Any]:
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
        (phase, tool)
        for phase in ("PreToolUse", "PostToolUse")
        for tool in ("Bash", "apply_patch")
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
    return {
        "status": "PASS",
        "provider": "loopback-responses-no-auth",
        "model_metadata": "gpt-5.6-sol",
        "model_requests": request_count,
        "events": event_names,
        "tool_events": sorted(f"{phase}:{tool}" for phase, tool in tool_events),
        "effects": ["shell-marker.txt", "patch-marker.txt"],
    }


def main() -> int:
    codex_bin = os.environ.get("CODEX_BIN") or shutil.which("codex")
    if not codex_bin:
        print("codex-hook-runtime-witness: Codex CLI not found", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="codex-hook-runtime-") as temp:
        witness_root = Path(temp)
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
        (codex_home / "hooks.json").write_text(
            json.dumps(_witness_hooks(recorder), indent=2) + "\n", encoding="utf-8"
        )

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

        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        for name in (
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_APPLICATION_CREDENTIALS",
        ):
            env.pop(name, None)
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

        if result.returncode != 0:
            print(result.stderr, file=sys.stderr)
            return result.returncode
        if _LoopbackResponsesHandler.errors:
            print("; ".join(_LoopbackResponsesHandler.errors), file=sys.stderr)
            return 1
        try:
            evidence = _assert_witness(
                repo, events_path, _LoopbackResponsesHandler.request_count
            )
        except (FileNotFoundError, KeyError, RuntimeError, json.JSONDecodeError) as exc:
            print(result.stderr, file=sys.stderr)
            print(f"codex-hook-runtime-witness: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(evidence, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
