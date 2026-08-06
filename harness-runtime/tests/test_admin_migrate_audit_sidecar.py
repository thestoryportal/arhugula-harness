"""`python -m harness_runtime.admin.migrate_audit_sidecar` — migration CLI tests.

Codex round-48 P1 (PR B1): the round-46 `adopt_legacy_is_refs()` migration
had no supported invocation path — an operator upgrading a pre-sidecar
deployment could not run it without writing internal Python. This module
witnesses the supported `python -m` path end-to-end: a legacy ledger (IS
audit refs, no sidecar) is unwedged by `main()`, adoption refuses a second
run, and a mistyped path exits without creating anything.
"""

from __future__ import annotations

import contextlib
import subprocess
import sys
import time
from collections.abc import Generator
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


# ---------------------------------------------------------------------------
# B-93 — the two lock-timeout folds this CLI gained at the deadline arc.
# ---------------------------------------------------------------------------

_B93_HOLDER = """
import fcntl, os, sys, time
fd = os.open(sys.argv[1], os.O_CREAT | os.O_RDWR, 0o600)
fcntl.flock(fd, fcntl.LOCK_EX)
open(sys.argv[2], "w").close()
limit = time.monotonic() + 60
while not os.path.exists(sys.argv[3]) and time.monotonic() < limit:
    time.sleep(0.01)
fcntl.flock(fd, fcntl.LOCK_UN)
os.close(fd)
"""


@contextlib.contextmanager
def _b93_hold(tmp_path: Path, target: Path) -> Generator[None, None, None]:
    """Hold `target`'s flock from a GENUINE second OS process.

    A thread would contend only the in-process face and prove nothing about the
    cross-process lock the CLI actually takes.
    """
    ready = tmp_path / f"b93-ready-{target.name}"
    release = tmp_path / f"b93-release-{target.name}"
    proc = subprocess.Popen(
        [sys.executable, "-c", _B93_HOLDER, str(target), str(ready), str(release)]
    )
    try:
        limit = time.monotonic() + 30
        while not ready.exists() and time.monotonic() < limit:
            assert proc.poll() is None, "holder exited before acquiring"
            time.sleep(0.01)
        assert ready.exists(), "holder never acquired the lock"
        yield
    finally:
        release.write_text("go")
        proc.wait(timeout=30)


@pytest.mark.skipif(sys.platform == "win32", reason="fcntl.flock is POSIX-only (B-45)")
def test_b93_legacy_adoption_refuses_on_lock_timeout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-93 (merge-gate lens 3, G1) — the legacy-adoption fold at `main`.

    `adopt_legacy_is_refs` takes a cross-process write lock on the sidecar.
    B-93 made that acquisition deadline-bounded, and its timeout is
    deliberately NOT an `OSError`/`ValueError` — so without the widened arm
    ordinary contention would exit this operator-facing command with a
    TRACEBACK instead of its established refusal (exit 1).

    Mutation probe (run at this arc): reverting the arm to `except ValueError`
    makes `main` propagate the raw timeout and this test fails.
    """
    ledger_path, writer = _legacy_ledger(tmp_path)
    sidecar = writer.sidecar_path

    from harness_is.cross_process_ledger_lock import cross_process_write_lock as real_lock

    monkeypatch.setattr(
        "harness_runtime.lifecycle.audit_writer.cross_process_write_lock",
        lambda path, **_kw: real_lock(path, deadline_seconds=0.1),
    )

    with _b93_hold(tmp_path, sidecar):
        exit_code = main([str(ledger_path)])

    assert exit_code == 1, f"expected the refusal exit 1, got {exit_code}"
    assert "migration refused" in capsys.readouterr().err
    # Nothing was adopted — the deployment is unchanged and the run is retryable.
    assert not sidecar.is_file() or sidecar.read_text() == ""
