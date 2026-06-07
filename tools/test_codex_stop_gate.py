"""Tests for the Codex Stop hook protocol wrapper."""

from __future__ import annotations

import json
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
