"""Subprocess witnesses for the installed Codex pre-tool path guard."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_POLICY = Path(__file__).resolve().parents[1] / ".codex/hooks/pre_tool_use_policy.py"


def _check(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_POLICY)],
        input=json.dumps({"tool_input": {"cmd": command}}),
        text=True,
        capture_output=True,
        check=False,
    )


def test_mixed_design_and_cp_tests_edit_is_refused() -> None:
    result = _check(
        "git add design-substrate/Spec_Control_Plane_v1_120.md "
        "harness-cp/cp_tests/test_memory_access_mode.py"
    )
    assert result.returncode == 2
    assert "mix design-substrate/spec/plan" in result.stderr


def test_single_medium_and_existing_source_mix_controls() -> None:
    assert _check("git add design-substrate/Spec_Control_Plane_v1_120.md").returncode == 0
    assert _check("git add harness-cp/cp_tests/test_memory_access_mode.py").returncode == 0
    assert (
        _check(
            "git add design-substrate/Spec_Control_Plane_v1_120.md "
            "harness-cp/src/harness_cp/workflow_driver.py"
        ).returncode
        == 2
    )
