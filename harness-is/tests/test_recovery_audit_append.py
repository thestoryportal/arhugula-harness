"""Behavioral witnesses for C-IS-07 durable recovery-audit append."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass, ClaimIntentAudit, Identifier
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    RecoveryAuditPayload,
    WriteKey,
    WriteResult,
    append_recovery_audit_entry,
    read_ledger,
    recovery_audit_idempotency_key,
)


def _handle(tmp_path: Path) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(canonical_path=tmp_path / "state.jsonl", exists=False, entry_count=0)


def _audit() -> ClaimIntentAudit:
    return ClaimIntentAudit.model_validate(
        {
            "schema_version": 1,
            "scope": "claim",
            "phase": "intent",
            "action": "release",
            "action_id": "a1",
            "record_identity": {
                "tenant_id": None,
                "workflow_id": "w1",
                "record_count": 1,
                "latest_digest": "a" * 64,
                "snapshot_hash": "b" * 64,
            },
            "subject_id": "c" * 64,
            "operator_uid": 1000,
            "reason_digest": "d" * 64,
            "observation": {
                "claim_bytes_digest": "e" * 64,
                "canonical_claim_path": "/state/claim",
                "claim_st_dev": 1,
                "claim_st_ino": 2,
                "lease_generation": "f" * 32,
                "lease_st_dev": 1,
                "lease_st_ino": 3,
            },
        }
    )


def _request(audit: ClaimIntentAudit | None = None) -> tuple[RecoveryAuditPayload, WriteKey]:
    audit = audit or _audit()
    key = recovery_audit_idempotency_key(audit)
    return (
        RecoveryAuditPayload(
            action_id=Identifier("recovery:claim:intent:a1"),
            idempotency_key=key,
            actor=Actor(actor_class=ActorClass.OPERATOR, actor_id="uid:1000"),
            timestamp=WRITER_OWNED_TIMESTAMP,
            recovery_audit=audit,
        ),
        WriteKey(thread_id=Identifier("thread"), step_id=Identifier("step"), idempotency_key=key),
    )


def test_recovery_append_and_identical_retry_preserve_original_entry(tmp_path: Path) -> None:
    handle = _handle(tmp_path)
    payload, key = _request()
    assert append_recovery_audit_entry(handle, payload, key) is WriteResult.APPENDED
    original = handle.canonical_path.read_bytes()
    [entry] = read_ledger(handle)
    assert entry.recovery_audit == payload.recovery_audit
    assert entry.timestamp != WRITER_OWNED_TIMESTAMP
    assert append_recovery_audit_entry(handle, payload, key) is WriteResult.IDEMPOTENT_NOOP
    assert handle.canonical_path.read_bytes() == original
    assert read_ledger(handle) == [entry]
    assert json.loads(original)["action_id"] == "recovery:claim:intent:a1"


def test_ordinary_append_refuses_audit_and_preserves_legacy_line(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from harness_is.state_ledger_write import EntryPayload, RecoveryAuditError, append_ledger_entry

    handle = _handle(tmp_path)
    ordinary = EntryPayload(
        action_id=Identifier("legacy"),
        idempotency_key=Identifier("legacy-key"),
        actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent"),
        timestamp=datetime(2026, 5, 16, tzinfo=UTC),
    )
    key = WriteKey(
        thread_id=Identifier("t"), step_id=Identifier("s"), idempotency_key=ordinary.idempotency_key
    )
    assert append_ledger_entry(handle, ordinary, key) is WriteResult.APPENDED
    original = handle.canonical_path.read_bytes()
    assert original == (
        b'{"action_id":"legacy","idempotency_key":"legacy-key","actor":'
        b'{"actor_class":"agent","actor_id":"agent"},"response_hash":'
        b'"89f2ba88ad0bda63c00423bcffdf08f898bc5a917c2b70e32c6172d9c28160d0",'
        b'"timestamp":"2026-05-16T00:00:00+00:00","prior_event_hash":' + b'"' + b"0" * 64 + b'"}\n'
    )
    audit_payload, audit_key = _request()
    with pytest.raises(RecoveryAuditError):
        append_ledger_entry(handle, audit_payload, audit_key)
    assert handle.canonical_path.read_bytes() == original


def test_durable_rejects_missing_sidecar_and_wrong_key(tmp_path: Path) -> None:
    from harness_is.state_ledger_write import (
        EntryPayload,
        RecoveryAuditError,
        WriteKeyMismatchError,
    )

    handle = _handle(tmp_path)
    payload, key = _request()
    with pytest.raises(RecoveryAuditError):
        append_recovery_audit_entry(
            handle, EntryPayload(**payload.model_dump(exclude={"recovery_audit"})), key
        )  # type: ignore[arg-type]
    with pytest.raises(WriteKeyMismatchError):
        append_recovery_audit_entry(
            handle, payload.model_copy(update={"idempotency_key": Identifier("wrong")}), key
        )
    with pytest.raises(WriteKeyMismatchError):
        append_recovery_audit_entry(
            handle, payload, key.model_copy(update={"idempotency_key": Identifier("wrong")})
        )
    assert not handle.canonical_path.exists()


def test_non_recovery_key_collision_and_changed_payload_conflict(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from harness_is.state_ledger_write import (
        EntryPayload,
        RecoveryAuditConflictError,
        append_ledger_entry,
    )

    handle = _handle(tmp_path)
    payload, key = _request()
    ordinary = EntryPayload(
        action_id=Identifier("ordinary"),
        idempotency_key=key.idempotency_key,
        actor=payload.actor,
        timestamp=datetime(2026, 5, 16, tzinfo=UTC),
    )
    append_ledger_entry(handle, ordinary, key)
    original = handle.canonical_path.read_bytes()
    with pytest.raises(RecoveryAuditConflictError):
        append_recovery_audit_entry(handle, payload, key)
    assert handle.canonical_path.read_bytes() == original

    second = _handle(tmp_path / "second")
    append_recovery_audit_entry(second, payload, key)
    original = second.canonical_path.read_bytes()
    changed = payload.model_copy(
        update={"actor": Actor(actor_class=ActorClass.OPERATOR, actor_id="uid:1001")}
    )
    with pytest.raises(RecoveryAuditConflictError):
        append_recovery_audit_entry(second, changed, key)
    assert second.canonical_path.read_bytes() == original


def test_sync_order_on_append_and_retry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import os

    from harness_is import state_ledger_write as writer

    handle = _handle(tmp_path / "state" / "ledger")
    payload, key = _request()
    synced: list[str] = []
    original_fsync = writer._fsync_recovery_target

    def record(fd: int) -> None:
        synced.append(os.readlink(f"/proc/self/fd/{fd}"))
        original_fsync(fd)

    monkeypatch.setattr(writer, "_fsync_recovery_target", record)
    append_recovery_audit_entry(handle, payload, key)
    assert synced == [
        str(handle.canonical_path),
        str(handle.canonical_path.parent),
        str(handle.canonical_path.parent.parent),
    ]
    synced.clear()
    append_recovery_audit_entry(handle, payload, key)
    assert synced == [
        str(handle.canonical_path),
        str(handle.canonical_path.parent),
        str(handle.canonical_path.parent.parent),
    ]


@pytest.mark.parametrize("mutation", ["torn", "predecessor", "tail_content", "tail_hash"])
def test_durable_refuses_untrusted_prior_ledger(tmp_path: Path, mutation: str) -> None:
    from datetime import UTC, datetime

    from harness_is.state_ledger_write import (
        EntryPayload,
        RecoveryAuditIntegrityError,
        append_ledger_entry,
    )

    handle = _handle(tmp_path)
    for index in range(2):
        payload = EntryPayload(
            action_id=Identifier(f"ordinary-{index}"),
            idempotency_key=Identifier(f"ordinary-key-{index}"),
            actor=Actor(actor_class=ActorClass.AGENT, actor_id="agent"),
            timestamp=datetime(2026, 5, 16, index, tzinfo=UTC),
        )
        key = WriteKey(
            thread_id=Identifier("t"),
            step_id=Identifier("s"),
            idempotency_key=payload.idempotency_key,
        )
        append_ledger_entry(handle, payload, key)
    lines = handle.canonical_path.read_bytes().splitlines()
    if mutation == "torn":
        damaged = b"\n".join(lines)  # no final newline
    else:
        records = [json.loads(line) for line in lines]
        if mutation == "predecessor":
            records[0]["action_id"] = "altered"
        elif mutation == "tail_content":
            records[1]["action_id"] = "altered"
        else:
            records[1]["response_hash"] = "f" * 64
        damaged = b"".join(
            json.dumps(row, separators=(",", ":")).encode() + b"\n" for row in records
        )
    handle.canonical_path.write_bytes(damaged)
    payload, key = _request()
    with pytest.raises(RecoveryAuditIntegrityError):
        append_recovery_audit_entry(handle, payload, key)
    assert handle.canonical_path.read_bytes() == damaged


@pytest.mark.parametrize("sync_call", [1, 2, 3])
def test_each_sync_failure_refuses_then_retry_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sync_call: int,
) -> None:
    from harness_is import state_ledger_write as writer

    handle = _handle(tmp_path)
    payload, key = _request()
    original_fsync = writer._fsync_recovery_target
    calls = 0

    def fail_once(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == sync_call:
            raise OSError("injected sync failure")
        original_fsync(fd)

    monkeypatch.setattr(writer, "_fsync_recovery_target", fail_once)
    with pytest.raises(writer.RecoveryAuditDurabilityError):
        append_recovery_audit_entry(handle, payload, key)
    assert append_recovery_audit_entry(handle, payload, key) is WriteResult.IDEMPOTENT_NOOP
    assert len(read_ledger(handle)) == 1


def test_short_write_refuses_and_torn_tail_blocks_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os

    from harness_is import state_ledger_write as writer

    handle = _handle(tmp_path)
    payload, key = _request()

    def short(fd: int, data: bytes) -> int:
        return os.write(fd, data[:-1])

    monkeypatch.setattr(writer, "_write_recovery_line", short)
    with pytest.raises(writer.RecoveryAuditDurabilityError):
        append_recovery_audit_entry(handle, payload, key)
    with pytest.raises(writer.RecoveryAuditIntegrityError):
        append_recovery_audit_entry(handle, payload, key)


def _exit_at_sync(path: Path, sync_call: int) -> None:
    import os

    from harness_is import state_ledger_write as writer

    calls = 0
    original = writer._fsync_recovery_target

    def exit_at_seam(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == sync_call:
            os._exit(70 + sync_call)
        original(fd)

    writer._fsync_recovery_target = exit_at_seam
    payload, key = _request()
    append_recovery_audit_entry(
        JsonlLedgerHandle(canonical_path=path, exists=False, entry_count=0),
        payload,
        key,
    )


@pytest.mark.parametrize("sync_call", [1, 2])
def test_process_exit_at_sync_seam_retries_once(tmp_path: Path, sync_call: int) -> None:
    import multiprocessing

    handle = _handle(tmp_path)
    child = multiprocessing.get_context("fork").Process(
        target=_exit_at_sync,
        args=(handle.canonical_path, sync_call),
    )
    child.start()
    child.join(timeout=15)
    assert child.exitcode == 70 + sync_call
    payload, key = _request()
    assert append_recovery_audit_entry(handle, payload, key) is WriteResult.IDEMPOTENT_NOOP
    assert len(read_ledger(handle)) == 1


def _contend(path: Path, start: object, results: object) -> None:
    handle = JsonlLedgerHandle(canonical_path=path, exists=False, entry_count=0)
    payload, key = _request()
    start.wait()  # type: ignore[attr-defined]
    results.put(append_recovery_audit_entry(handle, payload, key).value)  # type: ignore[attr-defined]


def test_two_processes_same_key_append_once(tmp_path: Path) -> None:
    import multiprocessing

    handle = _handle(tmp_path)
    ctx = multiprocessing.get_context("fork")
    start, results = ctx.Event(), ctx.Queue()
    children = [
        ctx.Process(target=_contend, args=(handle.canonical_path, start, results)) for _ in range(2)
    ]
    for child in children:
        child.start()
    start.set()
    for child in children:
        child.join(timeout=15)
        assert child.exitcode == 0
    assert {results.get(timeout=2) for _ in children} == {
        WriteResult.APPENDED.value,
        WriteResult.IDEMPOTENT_NOOP.value,
    }
    assert len(read_ledger(handle)) == 1


def test_is_writer_has_no_runtime_import() -> None:
    import ast
    import inspect

    from harness_is import state_ledger_write as writer

    tree = ast.parse(inspect.getsource(writer))
    imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert all(not (name or "").startswith("harness_runtime") for name in imports)


def test_changed_audit_same_derived_key_conflicts(tmp_path: Path) -> None:
    from harness_is.state_ledger_write import RecoveryAuditConflictError

    handle = _handle(tmp_path)
    payload, key = _request()
    append_recovery_audit_entry(handle, payload, key)
    original = handle.canonical_path.read_bytes()
    changed_audit = payload.recovery_audit.model_copy(update={"reason_digest": "1" * 64})
    changed = payload.model_copy(update={"recovery_audit": changed_audit})
    assert recovery_audit_idempotency_key(changed_audit) == key.idempotency_key
    with pytest.raises(RecoveryAuditConflictError):
        append_recovery_audit_entry(handle, changed, key)
    assert handle.canonical_path.read_bytes() == original


@pytest.mark.parametrize("sync_call", [1, 2, 3])
def test_duplicate_sync_failure_refuses_without_new_line(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    sync_call: int,
) -> None:
    from harness_is import state_ledger_write as writer

    handle = _handle(tmp_path)
    payload, key = _request()
    append_recovery_audit_entry(handle, payload, key)
    original = handle.canonical_path.read_bytes()
    original_fsync = writer._fsync_recovery_target
    calls = 0

    def fail(fd: int) -> None:
        nonlocal calls
        calls += 1
        if calls == sync_call:
            raise OSError("injected retry sync failure")
        original_fsync(fd)

    monkeypatch.setattr(writer, "_fsync_recovery_target", fail)
    with pytest.raises(writer.RecoveryAuditDurabilityError):
        append_recovery_audit_entry(handle, payload, key)
    assert handle.canonical_path.read_bytes() == original
    assert append_recovery_audit_entry(handle, payload, key) is WriteResult.IDEMPOTENT_NOOP
    assert handle.canonical_path.read_bytes() == original


def test_duplicate_key_in_prior_ledger_is_integrity_fault(tmp_path: Path) -> None:
    from datetime import UTC, datetime

    from harness_is import state_ledger_write as writer

    handle = _handle(tmp_path)
    payload, key = _request()
    append_recovery_audit_entry(handle, payload, key)
    ordinary = writer.EntryPayload(
        action_id=Identifier("ordinary"),
        idempotency_key=Identifier("other"),
        actor=payload.actor,
        timestamp=datetime.now(UTC),
    )
    other_key = key.model_copy(update={"idempotency_key": Identifier("other")})
    writer.append_ledger_entry(handle, ordinary, other_key)
    lines = handle.canonical_path.read_text().splitlines()
    duplicate = json.loads(lines[1])
    duplicate["idempotency_key"] = key.idempotency_key
    entry = writer._deserialize_entry(json.dumps(duplicate))
    duplicate["response_hash"] = writer.compute_response_hash(entry).hex()
    damaged = (lines[0] + "\n" + json.dumps(duplicate, separators=(",", ":")) + "\n").encode()
    handle.canonical_path.write_bytes(damaged)
    with pytest.raises(writer.RecoveryAuditIntegrityError, match="more than once"):
        append_recovery_audit_entry(handle, payload, key)
    assert handle.canonical_path.read_bytes() == damaged


def test_oversize_recovery_line_refuses_before_mutation(tmp_path: Path) -> None:
    from harness_is.state_ledger_write import RecoveryAuditError

    handle = _handle(tmp_path)
    payload, key = _request()
    huge = payload.model_copy(
        update={"actor": Actor(actor_class=ActorClass.OPERATOR, actor_id="a" * (1024 * 1024))}
    )
    with pytest.raises(RecoveryAuditError, match="1 MiB"):
        append_recovery_audit_entry(handle, huge, key)
    assert not handle.canonical_path.exists()
