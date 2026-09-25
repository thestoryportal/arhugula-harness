"""B-104 Task 3b: durable, sticky resume claim admission."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import ResumeClaimStore

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")


def _capture(root: Path):
    journal = JournalWorkflowPauseStore(journal_dir=root, tenant_id=None)
    snapshot = PauseSnapshot(
        workflow_id="wf-claim",
        run_id="run-1",
        step_index=0,
        pause_reason=WorkflowPauseReason.HITL_PENDING,
        state_summary=StateSummary(
            relevant_entries=(),
            summary_text="",
            summary_hash="0" * 64,
            idempotency_key=Identifier(""),
            external_references=(),
        ),
        snapshot_hash="0" * 64,
        created_at=0,
        state_ledger_anchor="0" * 64,
    )
    return journal.capture(snapshot, depth=None)


def test_claim_is_sticky_after_holder_closes(tmp_path: Path) -> None:
    ref = _capture(tmp_path)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    with store.claim(ref) as held:
        assert held.token
    with pytest.raises(Exception):
        store.claim(ref)


def test_canonical_names_and_invalid_evidence_refuse(tmp_path: Path) -> None:
    from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError

    ref = _capture(tmp_path)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    paths = store.paths_for(ref)
    assert paths.claim.name.startswith(paths.journal.name + ".resume-claim-")
    assert paths.lease.name.startswith(paths.journal.name + ".resume-lease-")
    paths.claim.write_bytes(b"partial")
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)
    paths.claim.unlink()
    paths.lease.write_bytes(b"bad lease")
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)
    paths.lease.unlink()
    (tmp_path / (paths.tombstone_prefix + "any")).write_bytes(b"")
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)


def test_claim_parser_requires_complete_exact_frames(tmp_path: Path) -> None:
    from harness_runtime.lifecycle.resume_claim_store import (
        InvalidClaim,
        StartedOrUnknown,
        UnstartedProof,
        parse_claim,
    )

    ref = _capture(tmp_path)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    with store.claim(ref):
        raw = store.paths_for(ref).claim.read_bytes()
    parsed = parse_claim(raw, ref)
    assert isinstance(parsed, UnstartedProof)
    assert isinstance(parse_claim(raw[:-1], ref), InvalidClaim)
    assert isinstance(parse_claim(raw + b"junk", ref), InvalidClaim)
    assert isinstance(parse_claim(raw.replace(b'"claimed"', b'"unknown"'), ref), InvalidClaim)
    started = raw.replace(b'"claimed"', b'"started"')
    assert isinstance(parse_claim(raw + started, ref), StartedOrUnknown)
    unknown = raw.replace(b'"claimed"', b'"future"')
    assert isinstance(parse_claim(raw + unknown, ref), StartedOrUnknown)
    assert isinstance(parse_claim(raw + raw, ref), InvalidClaim)


def _die_during_claim(root: Path, ref, checkpoint: str) -> None:
    """A real child dies at an I/O boundary, then parent probes disk state."""
    import os

    import harness_runtime.lifecycle.resume_claim_store as module

    pid = os.fork()
    if pid == 0:
        try:
            original_write = module._write_all
            original_link = os.link
            calls = 0

            if checkpoint in ("temp-write", "partial-claim"):

                def crash_write(fd, data):
                    nonlocal calls
                    calls += 1
                    if (checkpoint == "temp-write" and calls == 1) or (
                        checkpoint == "partial-claim" and calls == 2
                    ):
                        os.write(fd, data[:7])
                        os._exit(33)
                    original_write(fd, data)

                module._write_all = crash_write
            if checkpoint == "temp-fsync":

                def crash_fsync(fd):
                    os._exit(33)

                os.fsync = crash_fsync
            if checkpoint == "after-link":

                def crash_link(src, dst, *, follow_symlinks=True):
                    original_link(src, dst, follow_symlinks=follow_symlinks)
                    os._exit(33)

                os.link = crash_link
            if checkpoint == "parent-fsync":

                def crash_dir(path):
                    os._exit(33)

                module._fsync_dir = crash_dir
            module.ResumeClaimStore(journal_dir=root, tenant_id=None).claim(ref)
        except BaseException:
            os._exit(44)
        os._exit(55)
    _, status = os.waitpid(pid, 0)
    assert os.WIFEXITED(status)
    assert os.WEXITSTATUS(status) == 33


@pytest.mark.parametrize(
    "checkpoint", ["temp-write", "temp-fsync", "after-link", "parent-fsync", "partial-claim"]
)
def test_process_death_never_reopens_a_partial_claim(tmp_path: Path, checkpoint: str) -> None:
    from harness_runtime.lifecycle.resume_claim_store import (
        ClaimRefusedError,
        UnstartedProof,
        parse_claim,
    )

    ref = _capture(tmp_path)
    _die_during_claim(tmp_path, ref, checkpoint)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    paths = store.paths_for(ref)
    if checkpoint == "partial-claim":
        assert paths.claim.exists()
        assert not isinstance(parse_claim(paths.claim.read_bytes(), ref), UnstartedProof)
        with pytest.raises(ClaimRefusedError):
            store.claim(ref)
    else:
        assert not paths.claim.exists()
        with store.claim(ref):
            assert paths.lease.stat().st_nlink == 1
        assert isinstance(parse_claim(paths.claim.read_bytes(), ref), UnstartedProof)


def test_noncreating_probe_and_held_lease(tmp_path: Path) -> None:
    from harness_runtime.lifecycle.resume_claim_store import LeaseBusy, LeaseMissing

    ref = _capture(tmp_path)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    assert isinstance(store.probe_lease(ref), LeaseMissing)
    paths = store.paths_for(ref)
    assert not paths.lease.exists()
    with store.claim(ref):
        assert isinstance(store.probe_lease(ref), LeaseBusy)
    probe = store.probe_lease(ref)
    assert hasattr(probe, "close")
    probe.close()


def test_two_process_claimants_admit_at_most_one(tmp_path: Path) -> None:
    import os
    import time

    from harness_runtime.lifecycle.resume_claim_store import ClaimBusyError, ClaimRefusedError

    ref = _capture(tmp_path)
    ready_read, ready_write = os.pipe()
    start_read, start_write = os.pipe()
    result_read, result_write = os.pipe()
    pids = []
    for _ in range(2):
        pid = os.fork()
        if pid == 0:
            os.close(ready_read)
            os.close(start_write)
            os.close(result_read)
            os.write(ready_write, b"r")
            os.read(start_read, 1)
            try:
                with ResumeClaimStore(journal_dir=tmp_path, tenant_id=None).claim(ref):
                    os.write(result_write, b"W")
                    time.sleep(0.15)
            except ClaimBusyError:
                os.write(result_write, b"B")
            except ClaimRefusedError:
                os.write(result_write, b"R")
            os._exit(0)
        pids.append(pid)
    os.close(ready_write)
    os.close(start_read)
    os.close(result_write)
    ready = b""
    while len(ready) < 2:
        ready += os.read(ready_read, 2 - len(ready))
    assert ready == b"rr"
    os.write(start_write, b"go")
    results = b""
    while len(results) < 2:
        results += os.read(result_read, 2 - len(results))
    assert sorted(results) in ([66, 87], [82, 87])
    for pid in pids:
        _, status = os.waitpid(pid, 0)
        assert os.WIFEXITED(status) and os.WEXITSTATUS(status) == 0
    paths = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None).paths_for(ref)
    assert paths.claim.exists()


def test_started_frame_format_and_legacy_unknown_depth(tmp_path: Path) -> None:
    import hashlib
    import json

    from harness_runtime.lifecycle.resume_claim_store import (
        StartedOrUnknown,
        parse_claim,
        started_frame,
    )

    ref = _capture(tmp_path)
    journal = JournalWorkflowPauseStore(journal_dir=tmp_path, tenant_id=None)
    path = journal._journal_file(ref.workflow_id)
    record = json.loads(path.read_bytes())
    del record["depth"]
    line = json.dumps(record, sort_keys=True).encode("utf-8")
    path.write_bytes(line + b"\n")
    legacy_ref = ref.model_copy(update={"latest_digest": hashlib.sha256(line).hexdigest()})
    exact = journal.read_exact(legacy_ref)
    assert exact is not None and exact.depth is None
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    with store.claim(legacy_ref) as held:
        claimed = store.paths_for(legacy_ref).claim.read_bytes()
        parsed = parse_claim(claimed + started_frame(held), legacy_ref)
        assert isinstance(parsed, StartedOrUnknown)
        assert parsed.phase == "started"


def test_archive_without_tombstone_does_not_bar_claim(tmp_path: Path) -> None:
    ref = _capture(tmp_path)
    store = ResumeClaimStore(journal_dir=tmp_path, tenant_id=None)
    paths = store.paths_for(ref)
    (tmp_path / (paths.archive_prefix + "prior")).write_bytes(b"prior")
    with store.claim(ref):
        assert paths.claim.exists()
