"""Process-boundary exit contracts for the installed ``harness`` entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _invoke_main(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    source = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source), env.get("PYTHONPATH", "")) if part
    )
    # [LAW:behavior-not-structure] The subprocess observes the shell exit contract.
    return subprocess.run(
        [sys.executable, "-c", "from harness_runtime.cli import main; main()", *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_config_failure_exits_three_from_process_boundary(tmp_path: Path) -> None:
    result = _invoke_main(
        tmp_path,
        "run",
        str(tmp_path / "workflow.toml"),
        "--config",
        str(tmp_path / "missing.toml"),
    )

    assert result.returncode == 3, result.stdout + result.stderr
    assert "RT-FAIL-CLI-CONFIG-LOAD" in result.stderr


def test_help_exits_zero_from_process_boundary(tmp_path: Path) -> None:
    result = _invoke_main(tmp_path, "--help")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Usage:" in result.stdout
