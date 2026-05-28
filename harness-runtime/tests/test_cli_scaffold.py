"""Tests for U-RT-102 — operator-facing CLI scaffolding (C-RT-29 / spec v1.35 §14.18).

Maps to acceptance criteria 1–7 at runtime plan v2.31 §1.2.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

import pytest
from typer.testing import CliRunner

from harness_runtime.cli import main
from harness_runtime.cli.app import app

runner = CliRunner()

# Typer renders help text via Rich, which interleaves ANSI escape codes inside
# words (e.g. `--config` → `\x1b[1;36m-\x1b[0m\x1b[1;36m-config\x1b[0m`).
# Stripping escapes restores the literal text for substring assertions.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


# AC #1
def test_harness_top_help_lists_run_and_daemon_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    out = _plain(result.stdout)
    assert "run" in out
    assert "daemon" in out


# AC #2
def test_harness_run_help_shows_flag_inventory() -> None:
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    out = _plain(result.stdout)
    # Positional + 6 declared flags per spec §14.18.1.
    assert "WORKFLOW_FILE" in out or "workflow_file" in out.lower()
    for flag in ("--config", "--daemon", "--output", "--provider", "--model", "--tenant-id"):
        assert flag in out, f"missing flag {flag} in `harness run --help`"


# AC #3
def test_harness_daemon_help_shows_flag_inventory() -> None:
    result = runner.invoke(app, ["daemon", "--help"])
    assert result.exit_code == 0
    assert "--config" in _plain(result.stdout)


# AC #4 — SUPERSEDED at U-RT-106 (one-shot mode body landed at runtime plan
# v2.31 §1.6 / v2.32 §2). The U-RT-102 stub message is no longer emitted by
# `harness run <file>`; the concrete one-shot body + the 11 ACs at
# `test_cli_one_shot.py` supersede this scaffolding-stage assertion. The
# `harness run --daemon` flag remains a stub (U-RT-108) and is covered at
# U-RT-108 landing.


# AC #5
def test_harness_daemon_stub_exits_code_4() -> None:
    result = runner.invoke(app, ["daemon"])
    assert result.exit_code == 4
    assert "Not yet implemented" in _plain(result.stderr)


# AC #6 — Track A admin stubs are PRESERVED VERBATIM under `harness-inspect` +
# `harness-shutdown` standalone binaries (spec v1.35 §13.4 + §14.18.6).
def test_harness_inspect_and_shutdown_remain_standalone_binaries() -> None:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    scripts = data["project"]["scripts"]
    assert scripts["harness-inspect"] == "harness_runtime.admin.inspect:main"
    assert scripts["harness-shutdown"] == "harness_runtime.admin.shutdown_cli:main"
    # And the operator-facing parent dispatcher lives alongside, not as a replacement.
    assert scripts["harness"] == "harness_runtime.cli:main"


# AC #7
def test_unknown_flag_exits_code_3_with_arg_invalid_fail_class(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unknown flag → Click UsageError → RT-FAIL-CLI-ARG-INVALID → exit 3."""
    monkeypatch.setattr(sys, "argv", ["harness", "run", "--no-such-flag", "wf.yaml"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 3
    captured = capsys.readouterr()
    assert "RT-FAIL-CLI-ARG-INVALID" in captured.err
