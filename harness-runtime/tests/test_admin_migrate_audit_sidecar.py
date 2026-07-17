"""`python -m harness_runtime.admin.migrate_audit_sidecar` — migration CLI tests.

Codex round-48 P1 (PR B1): the round-46 `adopt_legacy_is_refs()` migration
had no supported invocation path — an operator upgrading a pre-sidecar
deployment could not run it without writing internal Python. This module
witnesses the supported `python -m` path end-to-end: a legacy ledger (IS
audit refs, no sidecar) is unwedged by `main()`, adoption refuses a second
run, and a mistyped path exits without creating anything.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_core.workload_class import WorkloadClass
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathResolver
from harness_is.state_ledger_entry_schema import Actor, ActorClass
from harness_od.audit_ledger_types import (
    AuditLedgerEntry,
    AuditPayload,
    AuditSignatureAttributes,
    SignatureAlgorithm,
    StateLedgerEntryRef,
    compute_entry_hash,
)
from harness_runtime.admin.migrate_audit_sidecar import build_parser, main
from harness_runtime.config.path_bindings import build_path_binding
from harness_runtime.lifecycle.audit_writer import RuntimeAuditLedgerWriter
from harness_runtime.lifecycle.state_ledger import materialize_state_ledger
from harness_runtime.types import PathBindingConfig


def _make_audit_entry(seed: str) -> AuditLedgerEntry:
    payload = AuditPayload(
        entry_core=StateLedgerEntryRef(f"entry-ref-{seed[:8]}"),
        audit_namespace_attrs={"audit.actor": "test-emission-site", "audit.seed": seed},
        prior_entry_hash="0" * 64,
    )
    return AuditLedgerEntry(
        payload=payload,
        signature_attrs=AuditSignatureAttributes(
            audit_signature_value=f"sig:{seed[:8]}",
            audit_signature_algorithm=SignatureAlgorithm.ED25519,
            audit_signature_key_id="test-key",
            audit_signature_key_period="2026-Q2",
        ),
        entry_hash=compute_entry_hash(payload),
    )


def _legacy_ledger(tmp_path: Path) -> tuple[Path, RuntimeAuditLedgerWriter]:
    """Build a ledger in the pre-sidecar state: audit refs, no sidecar."""
    ledger_path = tmp_path / "state.jsonl"
    config = PathBindingConfig(
        raw_entries=(
            {
                "path_class": PathClass.STATE_LEDGER,
                "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                "path": str(ledger_path),
            },
        ),
    )
    ledger = materialize_state_ledger(
        PathResolver(build_path_binding(config)),
        workflow_class=WorkloadClass.SOFTWARE_ENGINEERING,
        deployment_surface=DeploymentSurface.LOCAL_DEVELOPMENT,
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="test-runtime"),
    )
    state = {"now": datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)}

    def _tick() -> datetime:
        state["now"] = state["now"] + timedelta(microseconds=1)
        return state["now"]

    writer = RuntimeAuditLedgerWriter(ledger_writer=ledger, time_source=_tick)
    writer.append("tenant-A", _make_audit_entry("1" * 64))
    writer.append(None, _make_audit_entry("2" * 64))
    writer.sidecar_path.unlink()  # the pre-sidecar runtime never wrote it
    # The resolver may canonicalize the bound path — hand main() the SAME
    # path the writer actually uses.
    return ledger.handle.canonical_path, writer


def test_migration_unwedges_a_legacy_ledger(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ledger_path, writer = _legacy_ledger(tmp_path)

    # Wedged before migration.
    with pytest.raises(ValueError, match="migrate_audit_sidecar"):
        writer.read_full_entries_for_tenant("tenant-A")

    assert main([str(ledger_path)]) == 0
    out = capsys.readouterr().out
    assert "baselined 2 legacy audit reference(s)" in out

    # A fresh writer (new process) reads and appends cleanly now.
    fresh = RuntimeAuditLedgerWriter(
        ledger_writer=writer.ledger_writer,
        time_source=writer.time_source,
    )
    assert fresh.read_full_entries_for_tenant("tenant-A") == []
    new_entry = _make_audit_entry("3" * 64)
    fresh.append("tenant-A", new_entry)
    hashes = [e.entry_hash for e in fresh.read_full_entries_for_tenant("tenant-A")]
    assert hashes == [new_entry.entry_hash]


def test_migration_refuses_second_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ledger_path, _writer = _legacy_ledger(tmp_path)
    assert main([str(ledger_path)]) == 0
    assert main([str(ledger_path)]) == 1
    assert "migration refused" in capsys.readouterr().err


def test_migration_rejects_missing_ledger_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "nope" / "state.jsonl"
    assert main([str(missing)]) == 2
    assert "not found" in capsys.readouterr().err
    assert not missing.parent.exists()  # nothing created on a mistyped path


def test_parser_shape() -> None:
    parser = build_parser()
    args = parser.parse_args(["/tmp/ledger.jsonl"])
    assert isinstance(args.ledger, Path)


def test_module_runnable_via_python_m(tmp_path: Path) -> None:
    """B-47 item (k) — the documented operator invocation is `python -m`;
    the `if __name__ == "__main__"` guard is the only thing making that
    real. Run the module AS __main__ and pin the exit path."""
    import runpy
    import sys
    from unittest import mock

    argv = ["migrate_audit_sidecar", str(tmp_path / "missing" / "state.jsonl")]
    # Drop the already-imported module first: runpy re-executes the source,
    # and the stale sys.modules entry triggers a RuntimeWarning otherwise.
    already = sys.modules.pop("harness_runtime.admin.migrate_audit_sidecar", None)
    try:
        with mock.patch.object(sys, "argv", argv), pytest.raises(SystemExit) as excinfo:
            runpy.run_module("harness_runtime.admin.migrate_audit_sidecar", run_name="__main__")
    finally:
        if already is not None:
            sys.modules["harness_runtime.admin.migrate_audit_sidecar"] = already
    assert excinfo.value.code == 2
