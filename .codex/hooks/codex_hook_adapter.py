#!/usr/bin/env python3
"""Adapt the few Claude hook behaviors whose Codex payloads differ."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_UV_CACHE_DIR = "/tmp/arhugula-uv-cache"
PATCH_FILE_RE = re.compile(r"^\*\*\* (?:Add|Update) File:\s+(.+?)\s*$", re.MULTILINE)
COMMIT_RE = re.compile(r"^\s*(?:(?:/usr/local/bin/)?rtk\s+)?(?:/usr/bin/)?git\s+commit(?:\s|$)")


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
    relative_path: str, payload: dict[str, Any], cwd: Path
) -> dict[str, Any] | None:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(cwd)
    env.setdefault("UV_CACHE_DIR", DEFAULT_UV_CACHE_DIR)
    proc = subprocess.run(
        ["/bin/bash", str(ROOT / relative_path)],
        cwd=cwd,
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
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
    return value if isinstance(value, dict) else None


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
        proc = subprocess.run(
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
            env=env,
        )
        if proc.returncode != 0:
            detail = proc.stdout.strip() or proc.stderr.strip() or f"exit {proc.returncode}"
            print(detail, file=sys.stderr)
            return 2
    return 0


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"post-tool-use", "pre-commit"}:
        print("usage: codex_hook_adapter.py post-tool-use|pre-commit", file=sys.stderr)
        return 2
    if os.environ.get("HARNESS_CODEX_REVIEW_ISOLATED") == "1":
        return 0
    payload = read_payload()
    return post_tool_use(payload) if sys.argv[1] == "post-tool-use" else pre_commit(payload)


if __name__ == "__main__":
    raise SystemExit(main())
