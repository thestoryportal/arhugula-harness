"""B-104 Task 3b: durable, sticky resume claim admission."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.config.state_placement import (
    MARKER_NAME,
    PlacedStateDir,
    place_state_dir,
)
from harness_runtime.lifecycle.journal_workflow_pause_store import JournalWorkflowPauseStore
from harness_runtime.lifecycle.resume_claim_store import ResumeClaimStore
from harness_runtime.types import RuntimeConfig, VerifiedStateRoot

from .test_state_placement import world  # noqa: F401  (fixture: scratch dir with no .git above)
from .test_state_placement_bootstrap import Site

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="claim leases require POSIX flock")

JOURNAL_WHAT = "pause journal directory"


def _ext4(_path: Path) -> str | None:
    return "ext4"


@dataclass
class Placed:
    """A verified external state root with the pause journal directory under it."""

    site: Site
    config: RuntimeConfig
    stamp: VerifiedStateRoot
    journal_dir: Path

    def placement(self) -> PlacedStateDir:
        return place_state_dir(
            self.journal_dir, self.config, self.stamp, what=JOURNAL_WHAT, filesystem_type=_ext4
        )

    def store(self) -> ResumeClaimStore:
        return ResumeClaimStore(placement=self.placement(), tenant_id=None)


@pytest.fixture
def placed(world: Path) -> Placed:  # noqa: F811
    site = Site(world / "site")
    config = site.config(placement=True)
    stamp = site.stamp(config)
    journal_dir = site.root / "state-ledger" / "pause-journal"
    journal_dir.mkdir(parents=True, mode=0o700)
    return Placed(site, config, stamp, journal_dir)


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


def test_stale_record_refuses_after_later_valid_append(placed: Placed) -> None:
    from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError

    stale = _capture(placed.journal_dir)
    current = _capture(placed.journal_dir)
    journal = JournalWorkflowPauseStore(journal_dir=placed.journal_dir, tenant_id=None)
    assert journal.read_exact(stale) is not None  # Positional reads remain valid.
    store = placed.store()
    with pytest.raises(ClaimRefusedError, match="stale"):
        store.claim(stale)
    assert not store.paths_for(stale).claim.exists()
    with store.claim(current):
        assert store.paths_for(current).claim.exists()


def test_stale_append_between_lease_and_final_admission_refuses(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError

    stale = _capture(placed.journal_dir)
    store = placed.store()
    original_probe = store.probe_lease

    def append_then_probe(ref):
        _capture(placed.journal_dir)
        return original_probe(ref)

    monkeypatch.setattr(store, "probe_lease", append_then_probe)
    with pytest.raises(ClaimRefusedError, match="stale"):
        store.claim(stale)
    assert not store.paths_for(stale).claim.exists()


def test_noncanonical_lease_bytes_refuse_before_claim(placed: Placed) -> None:
    from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError

    ref = _capture(placed.journal_dir)
    store = placed.store()
    paths = store.paths_for(ref)
    token = "1" * 32
    canonical = store._lease_bytes(ref, token)
    paths.lease.write_bytes(canonical[:-1] + b"  \n")
    with pytest.raises(ClaimRefusedError, match="noncanonical lease bytes"):
        store.claim(ref)
    assert paths.lease.read_bytes() == canonical[:-1] + b"  \n"
    assert not paths.claim.exists()


def test_claim_is_sticky_after_holder_closes(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref) as held:
        assert held.token
    with pytest.raises(Exception):
        store.claim(ref)


def test_canonical_names_and_invalid_evidence_refuse(placed: Placed) -> None:
    from harness_runtime.lifecycle.resume_claim_store import ClaimRefusedError

    ref = _capture(placed.journal_dir)
    store = placed.store()
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
    (placed.journal_dir / (paths.tombstone_prefix + "any")).write_bytes(b"")
    with pytest.raises(ClaimRefusedError):
        store.claim(ref)


def test_claim_parser_requires_complete_exact_frames(placed: Placed) -> None:
    from harness_runtime.lifecycle.resume_claim_store import (
        InvalidClaim,
        StartedOrUnknown,
        UnstartedProof,
        parse_claim,
    )

    ref = _capture(placed.journal_dir)
    store = placed.store()
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


def _die_during_claim(placed: Placed, ref, checkpoint: str) -> None:
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
            placed.store().claim(ref)
        except BaseException:
            os._exit(44)
        os._exit(55)
    _, status = os.waitpid(pid, 0)
    assert os.WIFEXITED(status)
    assert os.WEXITSTATUS(status) == 33


@pytest.mark.parametrize(
    "checkpoint", ["temp-write", "temp-fsync", "after-link", "parent-fsync", "partial-claim"]
)
def test_process_death_never_reopens_a_partial_claim(placed: Placed, checkpoint: str) -> None:
    from harness_runtime.lifecycle.resume_claim_store import (
        ClaimRefusedError,
        UnstartedProof,
        parse_claim,
    )

    ref = _capture(placed.journal_dir)
    _die_during_claim(placed, ref, checkpoint)
    store = placed.store()
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


def test_noncreating_probe_and_held_lease(placed: Placed) -> None:
    from harness_runtime.lifecycle.resume_claim_store import LeaseBusy, LeaseMissing

    ref = _capture(placed.journal_dir)
    store = placed.store()
    assert isinstance(store.probe_lease(ref), LeaseMissing)
    paths = store.paths_for(ref)
    assert not paths.lease.exists()
    with store.claim(ref):
        assert isinstance(store.probe_lease(ref), LeaseBusy)
    probe = store.probe_lease(ref)
    assert hasattr(probe, "close")
    probe.close()


def test_two_process_claimants_admit_at_most_one(placed: Placed) -> None:
    import os
    import time

    from harness_runtime.lifecycle.resume_claim_store import ClaimBusyError, ClaimRefusedError

    ref = _capture(placed.journal_dir)
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
                with placed.store().claim(ref):
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
    paths = placed.store().paths_for(ref)
    assert paths.claim.exists()


def test_started_frame_format_and_legacy_unknown_depth(placed: Placed) -> None:
    import hashlib
    import json

    from harness_runtime.lifecycle.resume_claim_store import (
        StartedOrUnknown,
        parse_claim,
        started_frame,
    )

    ref = _capture(placed.journal_dir)
    journal = JournalWorkflowPauseStore(journal_dir=placed.journal_dir, tenant_id=None)
    path = journal._journal_file(ref.workflow_id)
    record = json.loads(path.read_bytes())
    del record["depth"]
    line = json.dumps(record, sort_keys=True).encode("utf-8")
    path.write_bytes(line + b"\n")
    legacy_ref = ref.model_copy(update={"latest_digest": hashlib.sha256(line).hexdigest()})
    exact = journal.read_exact(legacy_ref)
    assert exact is not None and exact.depth is None
    store = placed.store()
    with store.claim(legacy_ref) as held:
        claimed = store.paths_for(legacy_ref).claim.read_bytes()
        parsed = parse_claim(claimed + started_frame(held), legacy_ref)
        assert isinstance(parsed, StartedOrUnknown)
        assert parsed.phase == "started"


def test_archive_without_tombstone_does_not_bar_claim(placed: Placed) -> None:
    ref = _capture(placed.journal_dir)
    store = placed.store()
    paths = store.paths_for(ref)
    (placed.journal_dir / (paths.archive_prefix + "prior")).write_bytes(b"prior")
    with store.claim(ref):
        assert paths.claim.exists()


# --- placement: the store runs only against a verified external root ---------------------


def _tree(path: Path) -> list[tuple[str, int, int]]:
    """Every entry under `path` with its size and mtime: any write shows up here."""
    return sorted(
        (str(p.relative_to(path)), p.lstat().st_size, p.lstat().st_mtime_ns)
        for p in path.rglob("*")
    )


def _swap_marker(placed: Placed) -> None:
    """Same root directory, different root identity (a valid marker, new root id)."""
    marker = placed.site.root / MARKER_NAME
    new_id = "f" * 32 if marker.read_text() != "f" * 32 else "e" * 32
    marker.write_text(new_id)


def _captured_without_lock_file(placed: Placed):
    """A current record whose journal lock file is absent, so taking the lock would show."""
    ref = _capture(placed.journal_dir)
    for lock in placed.journal_dir.glob("*.lock"):
        lock.unlink()
    return ref


def _refusal(exc_info: pytest.ExceptionInfo[BaseException]):
    from harness_runtime.config.state_placement import StateRootPlacementError
    from harness_runtime.lifecycle.resume_claim_store import ClaimBusyError, ClaimRefusedError

    exc = exc_info.value
    assert isinstance(exc, StateRootPlacementError)
    # A placement fault is neither bad claim evidence nor contention.
    assert not isinstance(exc, ClaimRefusedError | ClaimBusyError)
    return exc.reason


def test_store_cannot_be_built_from_a_bare_journal_directory(placed: Placed) -> None:
    with pytest.raises(TypeError):
        ResumeClaimStore(journal_dir=placed.journal_dir, tenant_id=None)  # type: ignore[call-arg]


def test_undeclared_placement_refuses_before_any_store_exists(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    config = placed.site.config(placement=False)
    before = _tree(placed.site.base)
    with pytest.raises(Exception) as exc_info:
        place_state_dir(placed.journal_dir, config, None, what=JOURNAL_WHAT, filesystem_type=_ext4)
    assert _refusal(exc_info) is StatePlacementRefusal.PLACEMENT_REQUIRED
    assert _tree(placed.site.base) == before


def test_declared_placement_without_a_stamp_refuses(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    with pytest.raises(Exception) as exc_info:
        place_state_dir(
            placed.journal_dir, placed.config, None, what=JOURNAL_WHAT, filesystem_type=_ext4
        )
    assert _refusal(exc_info) is StatePlacementRefusal.UNVERIFIED_PLACEMENT


def test_journal_directory_outside_the_root_refuses(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    outside = placed.site.repo / ".harness" / "pause-journal"
    with pytest.raises(Exception) as exc_info:
        place_state_dir(
            outside, placed.config, placed.stamp, what=JOURNAL_WHAT, filesystem_type=_ext4
        )
    assert _refusal(exc_info) is StatePlacementRefusal.PATH_OUTSIDE_ROOT


def test_marker_swap_before_the_first_lock_refuses_and_writes_nothing(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    ref = _captured_without_lock_file(placed)
    store = placed.store()
    _swap_marker(placed)
    before = _tree(placed.journal_dir)
    with pytest.raises(Exception) as exc_info:
        store.claim(ref)
    assert _refusal(exc_info) is StatePlacementRefusal.IDENTITY_CHANGED
    # No journal lock file, lease, temp lease or claim was created.
    assert _tree(placed.journal_dir) == before


def test_root_replaced_at_the_same_path_refuses_and_writes_nothing(placed: Placed) -> None:
    import os

    from harness_runtime.config.state_placement import StatePlacementRefusal

    ref = _captured_without_lock_file(placed)
    store = placed.store()
    root = placed.site.root
    root.rename(root.with_name("root-moved"))
    root.mkdir(mode=0o700)
    fd = os.open(root / MARKER_NAME, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(fd, b"d" * 32)
    os.close(fd)
    (root / "state-ledger" / "pause-journal").mkdir(parents=True, mode=0o700)
    before = _tree(root)
    with pytest.raises(Exception) as exc_info:
        store.claim(ref)
    assert _refusal(exc_info) is StatePlacementRefusal.IDENTITY_CHANGED
    assert _tree(root) == before


def test_root_swap_between_lock_sections_refuses_the_claim_and_keeps_the_lease(
    placed: Placed, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    ref = _capture(placed.journal_dir)
    store = placed.store()
    paths = store.paths_for(ref)
    original_probe = store.probe_lease
    original_marker = (placed.site.root / MARKER_NAME).read_text()

    def probe_then_swap(probe_ref):
        held = original_probe(probe_ref)
        _swap_marker(placed)
        return held

    monkeypatch.setattr(store, "probe_lease", probe_then_swap)
    with pytest.raises(Exception) as exc_info:
        store.claim(ref)
    assert _refusal(exc_info) is StatePlacementRefusal.IDENTITY_CHANGED
    assert not paths.claim.exists()
    published = paths.lease.read_bytes()
    monkeypatch.undo()

    # The lease published before the refusal is valid, sticky evidence: once the stamped
    # root is back, the same lease inode admits the claim.
    (placed.site.root / MARKER_NAME).write_text(original_marker)
    with store.claim(ref):
        assert paths.claim.exists()
    assert paths.lease.read_bytes() == published


def test_journal_directory_swapped_for_a_symlink_outside_refuses(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    ref = _captured_without_lock_file(placed)
    store = placed.store()
    outside = placed.site.home / "elsewhere"
    placed.journal_dir.rename(outside)
    placed.journal_dir.symlink_to(outside, target_is_directory=True)
    before = _tree(outside)
    for attempt in (store.claim, store.probe_lease):
        with pytest.raises(Exception) as exc_info:
            attempt(ref)
        assert _refusal(exc_info) is StatePlacementRefusal.PATH_OUTSIDE_ROOT
    assert _tree(outside) == before


def test_probe_reports_a_placement_fault_not_a_lease_state(placed: Placed) -> None:
    from harness_runtime.config.state_placement import StatePlacementRefusal

    ref = _capture(placed.journal_dir)
    store = placed.store()
    with store.claim(ref):
        pass
    _swap_marker(placed)
    with pytest.raises(Exception) as exc_info:
        store.probe_lease(ref)
    assert _refusal(exc_info) is StatePlacementRefusal.IDENTITY_CHANGED
