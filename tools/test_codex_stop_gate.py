"""Tests for the Codex Stop hook protocol wrapper."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# This module exercises normal hooks even when invoked from an isolated reviewer.
os.environ.pop("HARNESS_CODEX_REVIEW_ISOLATED", None)


def test_stop_gate_emits_valid_stop_hook_json() -> None:
    proc = subprocess.run(
        [sys.executable, ".codex/hooks/stop_gate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["continue"] is True
    assert "Codex stop posture:" in payload["systemMessage"]
    assert "Codex context guard" in payload["systemMessage"]


def test_stop_gate_allows_owed_roadmap_lag_only_for_main_push_ci(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)

    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        """#!/usr/bin/env python3
import json
import sys

allowed = "--allow-roadmap-drift" in sys.argv
if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    # The real guard reports on stdout; stop_gate forwards a failed report to stderr.
    print("checkpoint written" if allowed else "roadmap drift")
    raise SystemExit(0 if allowed else 1)
print(json.dumps({"root": ".", "branch": "main", "findings": []}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)

    env = os.environ.copy()
    env.update(
        {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/main",
        }
    )
    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["continue"] is True

    env["GITHUB_EVENT_NAME"] = "pull_request"
    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 1
    assert "roadmap drift" in proc.stderr


def test_stop_gate_is_inert_for_isolated_merge_gate_review() -> None:
    env = os.environ.copy()
    env["HARNESS_CODEX_REVIEW_ISOLATED"] = "1"

    proc = subprocess.run(
        [sys.executable, ".codex/hooks/stop_gate.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
        env=env,
    )

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""


def test_stop_gate_reports_incomplete_loop_without_failing_hook(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)

    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        """#!/usr/bin/env python3
import json
import sys

if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    print("checkpoint written")
    raise SystemExit(0)
finding = {
    "severity": "hard",
    "code": "CODEX_LOOP_INCOMPLETE",
    "message": "decorrelated_review missing",
}
print(json.dumps({"root": ".", "branch": "main", "findings": [finding]}))
raise SystemExit(1)
""",
        encoding="utf-8",
    )

    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    nested = tmp_path / "nested"
    nested.mkdir()
    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=nested,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["continue"] is True
    assert "HARD CODEX_LOOP_INCOMPLETE" in payload["systemMessage"]


def test_stop_gate_propagates_non_loop_hard_closeout(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)

    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        """#!/usr/bin/env python3
import json
import sys

if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    print("checkpoint written")
    raise SystemExit(0)
finding = {
    "severity": "hard",
    "code": "ROADMAP_STATUS_DRIFT",
    "message": "roadmap drift",
}
print(json.dumps({"root": ".", "branch": "main", "findings": [finding]}))
raise SystemExit(1)
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)

    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert proc.returncode == 1
    assert "ROADMAP_STATUS_DRIFT" in proc.stderr
    assert proc.stdout == ""


def test_stop_gate_rejects_unknown_finding_severity(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)

    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        """#!/usr/bin/env python3
import json
import sys

if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    print("checkpoint written")
    raise SystemExit(0)
finding = {
    "severity": "HARD",
    "code": "ROADMAP_STATUS_DRIFT",
    "message": "roadmap drift",
}
print(json.dumps({"root": ".", "branch": "main", "findings": [finding]}))
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)

    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert proc.returncode == 1
    assert "invalid context guard output" in proc.stderr
    assert proc.stdout == ""


def test_stop_gate_keeps_checkpoint_creation_failure_hard(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)
    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        "import sys\nprint('checkpoint storage failed')\nraise SystemExit(2)\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)

    proc = subprocess.run(
        [sys.executable, str(hook)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert proc.returncode == 2
    assert "checkpoint storage failed" in proc.stderr
