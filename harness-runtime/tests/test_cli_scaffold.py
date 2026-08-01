"""Tests for U-RT-102 — operator-facing CLI scaffolding (C-RT-29 / spec v1.35 §14.18).

Maps to acceptance criteria 1–7 at runtime plan v2.31 §1.2.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

import pytest
from harness_runtime.cli import main
from harness_runtime.cli.app import app
from typer.testing import CliRunner

runner = CliRunner()

# Typer renders help text via Rich, which interleaves ANSI escape codes inside
# words (e.g. `--config` → `\x1b[1;36m-\x1b[0m\x1b[1;36m-config\x1b[0m`).
# Stripping escapes restores the literal text for substring assertions.
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _plain(text: str) -> str:
    return _ANSI_RE.sub("", text)


# AC #1 — extended at PR #84 Reading A apply: parent app now registers all
# 4 subcommands per spec §13.4 + §14.18.1 5-subcommand promise (Track A
# admin: inspect + shutdown; Track B operator: run + daemon).
def test_harness_top_help_lists_all_flat_subcommands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    out = _plain(result.stdout)
    # §13.4 flat namespace at v1.108. B-53 added migrate-audit-sidecar; `B-97`
    # half (a) adds the two pause-journal admin actions (the REQUIRED (3b)
    # adoption and the OPTIONAL disposal, both declared at §13.4). The
    # spec-side DECLARED-row count and the shipped registry remain SEPARATE
    # FACTS — the `migrate-audit-sidecar` row was declared at v1.101 for an
    # impl arc that has not yet registered its own `python -m` implementation
    # under a distinct name; that pre-existing gap is NOT absorbed here.
    for subcommand in (
        "run",
        "daemon",
        "inspect",
        "shutdown",
        "migrate-audit-sidecar",
        "adopt-pause-journals",
        "dispose-pause-journals",
    ):
        assert subcommand in out, f"parent app help missing {subcommand!r}"
    # EXACT registry names — a renamed/misregistered command must fail this,
    # not slip through a substring match.
    registered = {command.name for command in app.registered_commands}
    assert registered == {
        "run",
        "daemon",
        "inspect",
        "shutdown",
        "migrate-audit-sidecar",
        "adopt-pause-journals",
        "dispose-pause-journals",
    }


# PR #84 Reading A — `harness inspect --help` delegates to admin module's
# argparse parser (typer auto-help disabled via help_option_names=[]).
def test_harness_inspect_help_delegates_to_admin_argparse() -> None:
    result = runner.invoke(app, ["inspect", "--help"])
    assert result.exit_code == 0
    out = _plain(result.output)
    # argparse help shows the admin module's actual flag inventory.
    for flag in ("--ledger-path", "--collector-path", "--last-n", "--json"):
        assert flag in out, (
            f"`harness inspect --help` missing {flag!r} — "
            "delegation to admin/inspect.py main() may have regressed"
        )


# PR #84 Reading A — `harness shutdown --help` delegates to admin module's
# argparse parser.
def test_harness_shutdown_help_delegates_to_admin_argparse() -> None:
    result = runner.invoke(app, ["shutdown", "--help"])
    assert result.exit_code == 0
    out = _plain(result.output)
    for flag in ("--pidfile-path", "--wait", "--json"):
        assert flag in out, (
            f"`harness shutdown --help` missing {flag!r} — "
            "delegation to admin/shutdown_cli.py main() may have regressed"
        )


# PR #84 Reading A — `harness inspect <path>` actually runs the admin body
# against a real ledger fixture, verifying the wrapper is not just plumbing
# help but the full body.
def test_harness_inspect_runs_admin_body_against_real_ledger(
    tmp_path: Path,
) -> None:
    # Minimal ledger fixture — genesis entry with valid F2 hash chain.
    import hashlib
    import json

    entry = {
        "action_id": "test:probe",
        "idempotency_key": "k" * 64,
        "actor": {"actor_class": "agent", "actor_id": "test"},
        "response_hash": hashlib.sha256(b"r").hexdigest(),
        "timestamp": "2026-05-29T00:00:00+00:00",
        "prior_event_hash": "0" * 64,
    }
    ledger_path = tmp_path / "state.jsonl"
    ledger_path.write_text(json.dumps(entry) + "\n")

    result = runner.invoke(app, ["inspect", "--ledger-path", str(ledger_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["total_entries"] == 1
    assert payload["entries"][0]["action_id"] == "test:probe"


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


# AC #5 — SUPERSEDED at U-RT-107 (daemon entrypoint body landed at runtime
# plan v2.31 §1.7). The U-RT-102 stub message is no longer emitted by
# `harness daemon`; the concrete daemon body + 8 ACs at `test_cli_daemon.py`
# supersede this scaffolding-stage assertion.


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


# U-RT-102 amendment (plan v2.49 §1.6 / spec v1.101 §13.4 row 6, B-53):
# `harness migrate-audit-sidecar` dispatches the EXISTING migration module's
# main under the flat namespace — no logic duplicated into the CLI layer.
def test_harness_migrate_audit_sidecar_dispatches_existing_module_main_under_flat_namespace(
    tmp_path: Path,
) -> None:
    # Half 1 — help delegation: the admin module's argparse inventory shows
    # through (typer auto-help disabled), proving the pass-through reaches
    # `harness_runtime.admin.migrate_audit_sidecar:main`.
    result = runner.invoke(app, ["migrate-audit-sidecar", "--help"])
    assert result.exit_code == 0
    out = _plain(result.output)
    for flag in ("--retag", "--author", "--runtime-config", "--attestation", "--tofu-quarantine"):
        assert flag in out, (
            f"`harness migrate-audit-sidecar --help` missing {flag!r} — "
            "delegation to admin/migrate_audit_sidecar.py main() may have regressed"
        )

    # Half 2 — the real BODY runs (not just help plumbing): the
    # legacy-baseline adoption mode against a real pre-sidecar ledger.
    # Mutation probe: rewiring the dispatch to a different module main (or
    # dropping the arg forwarding) fails the exit-0 + baseline assertions.
    from datetime import UTC, datetime

    from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
    from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
    from harness_is.state_ledger_write import EntryPayload, WriteKey, append_ledger_entry

    ledger_path = tmp_path / "state.jsonl"
    ledger_path.touch()
    handle = JsonlLedgerHandle(canonical_path=ledger_path, exists=True, entry_count=0)
    append_ledger_entry(
        handle,
        EntryPayload(
            action_id=Identifier("audit:_single:" + "a" * 64),
            idempotency_key=Identifier("idem-0"),
            actor=Actor(actor_class=ActorClass.AGENT, actor_id="test"),
            timestamp=datetime(2026, 7, 21, tzinfo=UTC),
        ),
        WriteKey(
            thread_id=Identifier("thread-0"),
            step_id=Identifier("step-0"),
            idempotency_key=Identifier("idem-0"),
        ),
    )
    result = runner.invoke(app, ["migrate-audit-sidecar", str(ledger_path)])
    assert result.exit_code == 0, result.output
    assert "baselined 1 legacy audit reference" in _plain(result.output)
    sidecar = ledger_path.parent / "audit-entries.jsonl"
    assert sidecar.is_file()
    assert "legacy_baseline" in sidecar.read_text()


# Codex on the B-53 promotion: argparse PARSE failures under the parent CLI
# honor the §14.18.4 contract (RT-FAIL-CLI-ARG-INVALID → exit 3); body
# return codes pass through unchanged.
def test_harness_migrate_audit_sidecar_parse_failure_maps_to_arg_invalid(
    tmp_path: Path,
) -> None:
    result = runner.invoke(app, ["migrate-audit-sidecar", "--no-such-option"])
    assert result.exit_code == 3
    assert "RT-FAIL-CLI-ARG-INVALID" in _plain(result.output)

    # Body-level usage return (exit 2 by the module contract) is preserved.
    ledger = tmp_path / "state.jsonl"
    ledger.touch()
    result = runner.invoke(app, ["migrate-audit-sidecar", str(ledger), "--retag"])
    assert result.exit_code == 2  # module body: --retag requires --runtime-config
