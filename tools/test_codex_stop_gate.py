"""Tests for the Codex Stop hook protocol wrapper."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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


def test_stop_gate_reports_incomplete_loop_without_failing_hook(tmp_path: Path) -> None:
    hook = tmp_path / ".codex" / "hooks" / "stop_gate.py"
    hook.parent.mkdir(parents=True)
    shutil.copy2(ROOT / ".codex" / "hooks" / "stop_gate.py", hook)

    guard = tmp_path / "tools" / "codex_context_guard.py"
    guard.parent.mkdir()
    guard.write_text(
        """#!/usr/bin/env python3
import sys

if len(sys.argv) > 1 and sys.argv[1] == "checkpoint":
    print("checkpoint written")
    raise SystemExit(0)
print("HARD CODEX_LOOP_INCOMPLETE: decorrelated_review missing")
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
