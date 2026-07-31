"""`B-97` half (a) — the (3b) adoption, the disposal, and the §13.4 inventory
(U-RT-149 AC #9, #10, #11).

Runtime spec v1.108 §14.14.8 ((3b)'s FIVE mechanical terms + refuse-where-degraded
+ the account) + §13.4 (the two NEW inventory rows) + §13.7 term 6 (disposal is
FORECLOSED from `harness-inspect` by the read-only invariant).

**Every one of (a)–(d-ter) asserts a REFUSAL, not merely a happy path** — the
failure mode this machinery exists for is silent and executes.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from harness_cp.handoff_context import StateSummary
from harness_cp.pause_resume_protocol_types import PauseSnapshot, WorkflowPauseReason
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.admin import pause_journal_adoption as adoption_module
from harness_runtime.admin.pause_journal_adoption import (
    AdoptionDisposition,
    adopt_pause_journals,
)
from harness_runtime.admin.pause_journal_disposal import main as disposal_main
from harness_runtime.admin.pause_journal_disposal import plan_disposal
from harness_runtime.admin.pause_journal_enumeration import JournalIdentityClass
from harness_runtime.lifecycle import journal_workflow_pause_store as store_module
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    PAUSE_JOURNAL_LOCK_SUFFIX,
    PAUSE_JOURNAL_SUBDIR,
    JournalWorkflowPauseStore,
    legacy_pause_journal_filename,
    pause_journal_filename,
)

_TENANT = "tenant-a"

requires_posix_flock = pytest.mark.skipif(
    sys.platform == "win32",
    reason="the exclusion primitive is a documented no-op on Windows, where the "
    "adoption REFUSES by default (asserted separately by the _IS_WINDOWS probe).",
)


def _snapshot(workflow_id: str, *, run_id: str = "run-1") -> PauseSnapshot:
    return PauseSnapshot(
        workflow_id=workflow_id,
        run_id=run_id,
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


def _record(workflow_id: str, *, wrapper_id: str | None = None, run_id: str = "run-1") -> str:
    return json.dumps(
        {
            "workflow_id": wrapper_id if wrapper_id is not None else workflow_id,
            "pause_snapshot": _snapshot(workflow_id, run_id=run_id).model_dump(mode="json"),
        }
    )


def _legacy(journal_dir: Path, workflow_id: str, *, run_id: str = "run-1") -> Path:
    journal_dir.mkdir(parents=True, exist_ok=True)
    path = journal_dir / legacy_pause_journal_filename(workflow_id)
    path.write_text(_record(workflow_id, run_id=run_id) + "\n")
    return path


def _run(
    journal_dir: Path, tmp_path: Path, **kwargs: object
) -> list[adoption_module.AdoptionOutcome]:
    return adopt_pause_journals(
        journal_dir,
        tenant_id=kwargs.pop("tenant_id", _TENANT),  # type: ignore[arg-type]
        account_path=tmp_path / "account.jsonl",
        **kwargs,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# AC #9(a) — LEGACY-SOURCE EXCLUSION: the lock IDENTITY, not "some lock".
# ---------------------------------------------------------------------------


@requires_posix_flock
def test_ac9a_the_adoption_locks_the_legacy_source_lock_file_inode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(a) — assert the **LOCK-FILE IDENTITY** (the inode a straggler
    appender contends on), not merely that some lock was taken.

    *Racing wall-clock proves nothing; lock identity does.* The source lock and
    the target lock are DIFFERENT inodes, and locking the target would exclude
    nothing that matters — a straggler computes the LEGACY key.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    expected_lock = source.with_name(source.name + PAUSE_JOURNAL_LOCK_SUFFIX)

    locked: list[tuple[int, int]] = []
    import fcntl

    real_flock = fcntl.flock

    def _spy_flock(fd: int, op: int) -> None:
        info = os.fstat(fd)
        locked.append((info.st_dev, info.st_ino))
        return real_flock(fd, op)

    monkeypatch.setattr(fcntl, "flock", _spy_flock)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert [o.disposition for o in outcomes] == [AdoptionDisposition.ADOPTED]
    lock_info = expected_lock.stat()
    assert (lock_info.st_dev, lock_info.st_ino) in locked, (
        "the adoption did not hold the LEGACY SOURCE's own lock inode"
    )
    # And NOT the target's lock — a second lock on the target is neither required
    # nor permitted (redundant with the atomic commit; adds a lock-ordering hazard).
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")
    target_lock = target.with_name(target.name + PAUSE_JOURNAL_LOCK_SUFFIX)
    assert not target_lock.exists(), "a second lock was taken on the TARGET"


def test_ac9a_no_directory_tree_scope_lock_is_used(tmp_path: Path) -> None:
    """AC #9(a) — a **directory-tree scope lock is NOT used.**

    `flock` contends only on the same inode, and the pause-journal appender does
    not take the house directory lock — a migration holding it would exclude
    **ZERO** writers. Asserted by intercepting the house primitive.
    """
    from harness_is import cross_process_ledger_lock as house_lock

    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    calls: list[object] = []
    monkey = pytest.MonkeyPatch()
    try:
        monkey.setattr(
            house_lock,
            "cross_process_scope_lock",
            lambda *a, **k: calls.append((a, k)),
        )
        _run(journal_dir, tmp_path)
    finally:
        monkey.undo()
    assert calls == [], "the adoption took the mechanically INERT directory-tree lock"


# ---------------------------------------------------------------------------
# AC #9(b) — READ-BACK, and it leaves the target UNPUBLISHED.
# ---------------------------------------------------------------------------


def test_ac9b_interference_inside_the_read_back_window_refuses_and_leaves_target_unpublished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(b) — interfere with the legacy source INSIDE the
    `[read, read-back]` window; the adoption **REFUSES and leaves the target
    UNPUBLISHED**.

    The interference is injected by appending on the SECOND read of the source —
    i.e. genuinely between the copy and the verify, not before the run.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")

    # Read #1 of the source is the ENUMERATION's (it computes the two scalars
    # from raw bytes); #2 is the adoption's COPY read, and #3 is its READ-BACK.
    # The straggler must append between #2 and #3 — injecting at #1 would land
    # BEFORE the copy and be invisible to the check under test, which is exactly
    # the vacuous-probe shape this comment exists to foreclose.
    _COPY_READ = 2
    reads = {"n": 0}
    real_read_bytes = Path.read_bytes

    def _interfering_read_bytes(self: Path) -> bytes:
        if self == source:
            reads["n"] += 1
            if reads["n"] == _COPY_READ:
                data = real_read_bytes(self)
                # A straggler appends between the copy and the read-back.
                with self.open("a", encoding="utf-8") as handle:
                    handle.write(_record("wf-legacy", run_id="straggler") + "\n")
                return data
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _interfering_read_bytes)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert [o.disposition for o in outcomes] == [AdoptionDisposition.REFUSED_ON_READ_BACK]
    assert not target.exists(), "the target was PUBLISHED despite a read-back refusal"
    assert reads["n"] > _COPY_READ, "the read-back never ran — the probe is vacuous"


def test_ac9b_the_run_does_not_claim_the_mixed_version_window_is_covered(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #9(b) — the run's own reporting does **NOT** claim the mixed-version
    window is covered.

    The read-back DETECTS interference within its window and thereby NARROWS,
    but does NOT CLOSE, the residual. Stating otherwise would commit the exact
    error the unverifiable-precondition rule names.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    assert adoption_module.main([str(journal_dir), "--tenant-id", _TENANT]) == 0
    output = capsys.readouterr().out + capsys.readouterr().err

    forbidden = ("mixed-version window is covered", "safe to run concurrently", "no writer can")
    for phrase in forbidden:
        assert phrase not in output
    # And the refusal text, where it fires, states the limit explicitly.
    detail = AdoptionDisposition.REFUSED_ON_READ_BACK
    assert detail.value == "refused-on-read-back"


# ---------------------------------------------------------------------------
# AC #9(c) — the write-once, crash-atomic, NO-REPLACE publication.
# ---------------------------------------------------------------------------


def test_ac9c_a_target_created_between_precheck_and_publish_makes_the_publish_fail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(c) — create the target BETWEEN the pre-check and the publish; the
    **publish FAILS rather than overwrites**.

    The no-replace commit closes the time-of-check/time-of-use race BY
    CONSTRUCTION, so any pre-check is advisory only. **This is what makes
    stale-over-newer impossible**: if an upgraded deployment already captured a
    pause at the new key, the adoption cannot publish over it.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")
    newer = _record("wf-legacy", run_id="newer-capture") + "\n"

    real_link = os.link

    def _racing_link(src: object, dst: object, **kwargs: object) -> None:
        # A concurrent writer wins the race, after every pre-check has passed.
        if not Path(str(dst)).exists():
            Path(str(dst)).write_text(newer)
        return real_link(src, dst, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "link", _racing_link)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert [o.disposition for o in outcomes] == [AdoptionDisposition.REFUSED_FOREIGN_TARGET]
    assert target.read_text() == newer, "the racing writer's record was OVERWRITTEN"


def test_ac9c_a_pre_commit_crash_leaves_no_target_and_no_canonical_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(c) — crash-atomicity, direction ONE: a **PRE-COMMIT crash leaves NO
    target**, and the write-aside artifact is not a canonical journal name (so
    §13.7 never counts it).
    """
    from harness_runtime.admin.pause_journal_enumeration import enumerate_pause_journals

    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")

    def _crash(*args: object, **kwargs: object) -> None:
        raise KeyboardInterrupt("crash before commit")

    monkeypatch.setattr(os, "link", _crash)
    with pytest.raises(KeyboardInterrupt):
        _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert not target.exists()
    assert [r.path.name for r in enumerate_pause_journals(journal_dir, tenant_scope=_TENANT)] == [
        legacy_pause_journal_filename("wf-legacy")
    ]


def test_ac9c_a_post_commit_crash_leaves_a_complete_target_the_rerun_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(c) — crash-atomicity, direction TWO: a **POST-COMMIT crash leaves a
    COMPLETE, VALID target** that the (d) content-equality re-run **RECOGNIZES
    and SKIPS**.

    *A re-run MUST NOT delete or replace a committed target on the theory that
    its own prior run "did not finish"* — that would destroy a valid publication
    to recover from a crash the publication already survived, and because the
    store carries no hash chain, repeatability is the only available recovery.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")

    real_link = os.link
    crashed = {"done": False}

    def _crash_after_commit(src: object, dst: object, **kwargs: object) -> None:
        real_link(src, dst, **kwargs)  # type: ignore[arg-type]
        crashed["done"] = True
        raise KeyboardInterrupt("crash immediately after the commit")

    monkeypatch.setattr(os, "link", _crash_after_commit)
    with pytest.raises(KeyboardInterrupt):
        _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert crashed["done"]
    assert target.is_file()
    committed = target.read_bytes()
    assert committed == source.read_bytes(), "the committed target is not COMPLETE"

    # The re-run recognizes and SKIPS it — never republished, never deleted.
    # TWO rows now: the legacy source (skipped-as-already-published) and the
    # committed target itself, which the enumeration correctly classifies
    # CURRENT-FORMAT — ordinary state, never touched, and NOT a refusal.
    outcomes = {o.source: o.disposition for o in _run(journal_dir, tmp_path)}
    assert outcomes[source.name] is AdoptionDisposition.SKIPPED_ALREADY_PUBLISHED
    assert outcomes[target.name] is AdoptionDisposition.SKIPPED_NOT_ADOPTABLE
    assert target.read_bytes() == committed


def test_ac9c_the_destination_directory_entry_is_made_durable_after_the_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(c) — the destination directory entry is made durable **AFTER** the
    commit, not before (a pre-commit dirent fsync persists nothing that exists)."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")

    # Scoped to the DESTINATION directory's own inode: the account log lives in
    # a different directory and fsyncs its own dirent write-ahead of the commit,
    # so an unscoped "any dir-fsync" counter would compare the wrong two events.
    destination = journal_dir.stat()
    events: list[str] = []
    real_link = os.link
    real_fsync = os.fsync

    def _spy_link(src: object, dst: object, **kwargs: object) -> None:
        events.append("commit")
        return real_link(src, dst, **kwargs)  # type: ignore[arg-type]

    def _spy_fsync(fd: int) -> None:
        try:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) == (destination.st_dev, destination.st_ino):
                events.append("destination-dir-fsync")
        except OSError:  # pragma: no cover — defensive
            pass
        return real_fsync(fd)

    monkeypatch.setattr(os, "link", _spy_link)
    monkeypatch.setattr(os, "fsync", _spy_fsync)
    _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert "commit" in events
    assert "destination-dir-fsync" in events
    assert events.index("commit") < events.index("destination-dir-fsync")


# ---------------------------------------------------------------------------
# AC #9(d) — the re-run discriminator + directory-level partial completion.
# ---------------------------------------------------------------------------


def test_ac9d_identical_target_skipped_different_target_refused_as_foreign(
    tmp_path: Path,
) -> None:
    """AC #9(d) — the ONLY compatible discriminator is **CONTENT EQUALITY**.

    A no-replace commit yields one undifferentiated signal (*target exists*), and
    because the record shape is unchanged an adopted record and an upgraded
    writer's fresh capture are **structurally identical** — so treating every
    existing target as *done* would accept foreign or newer state, while refusing
    every existing target would break the promised recoverable retry.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-same")
    _legacy(journal_dir, "wf-different")

    first = _run(journal_dir, tmp_path)
    assert {o.disposition for o in first} == {AdoptionDisposition.ADOPTED}

    # Mutate ONE target so the re-run sees foreign content there.
    foreign_target = journal_dir / pause_journal_filename(_TENANT, "wf-different")
    foreign_target.write_text(_record("wf-different", run_id="someone-elses") + "\n")

    # Keyed on the SOURCE filename: after the first run each workflow has TWO
    # enumerated journals (the legacy orphan and the published target), so a
    # workflow_id-keyed dict would silently collapse them.
    second = {o.source: o.disposition for o in _run(journal_dir, tmp_path)}
    assert second[legacy_pause_journal_filename("wf-same")] is (
        AdoptionDisposition.SKIPPED_ALREADY_PUBLISHED
    )
    assert second[legacy_pause_journal_filename("wf-different")] is (
        AdoptionDisposition.REFUSED_FOREIGN_TARGET
    )
    # And this deployment's own published targets are ORDINARY STATE, not
    # refusals — the distinction that keeps an idempotent re-run from exiting 1.
    assert second[pause_journal_filename(_TENANT, "wf-same")] is (
        AdoptionDisposition.SKIPPED_NOT_ADOPTABLE
    )


def test_ac9d_a_directory_level_partial_migration_completes_on_rerun(tmp_path: Path) -> None:
    """AC #9(d) — a directory-level PARTIAL migration **completes on re-run**.

    Each journal is independently all-or-nothing while the operation as a whole
    is directory-non-atomic, so it must be idempotent and re-runnable.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    for name in ("wf-1", "wf-2", "wf-3"):
        _legacy(journal_dir, name)

    # Interrupt between journals: adopt only the first, by running against a
    # temporary directory holding just it, then restoring the rest.
    stash = tmp_path / "stash"
    stash.mkdir()
    for name in ("wf-2", "wf-3"):
        src = journal_dir / legacy_pause_journal_filename(name)
        src.rename(stash / src.name)
    partial = _run(journal_dir, tmp_path)
    assert [o.disposition for o in partial] == [AdoptionDisposition.ADOPTED]
    for path in stash.iterdir():
        path.rename(journal_dir / path.name)

    completed = {o.source: o.disposition for o in _run(journal_dir, tmp_path)}
    assert completed[legacy_pause_journal_filename("wf-1")] is (
        AdoptionDisposition.SKIPPED_ALREADY_PUBLISHED
    )
    assert completed[legacy_pause_journal_filename("wf-2")] is AdoptionDisposition.ADOPTED
    assert completed[legacy_pause_journal_filename("wf-3")] is AdoptionDisposition.ADOPTED
    for name in ("wf-1", "wf-2", "wf-3"):
        assert (journal_dir / pause_journal_filename(_TENANT, name)).is_file()


@requires_posix_flock
def test_ac9d_never_holds_two_journal_locks_at_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #9(d) — **never holding journal *i*'s lock while taking journal
    *i+1*'s**, so the instantaneous blocking footprint equals ONE append's and
    the cross-workflow blocking `B-97`(b) deliberately rejected is not
    reintroduced."""
    import fcntl

    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    for name in ("wf-1", "wf-2", "wf-3"):
        _legacy(journal_dir, name)

    held: set[tuple[int, int]] = set()
    peak = {"max": 0}
    real_flock = fcntl.flock

    def _spy_flock(fd: int, op: int) -> None:
        info = os.fstat(fd)
        key = (info.st_dev, info.st_ino)
        if op == fcntl.LOCK_EX:
            held.add(key)
            peak["max"] = max(peak["max"], len(held))
        elif op == fcntl.LOCK_UN:
            held.discard(key)
        return real_flock(fd, op)

    monkeypatch.setattr(fcntl, "flock", _spy_flock)
    _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert peak["max"] == 1, f"held {peak['max']} journal locks at once"


def test_refuse_where_the_exclusion_primitive_degrades(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """REFUSE WHERE THE PRIMITIVE DEGRADES — the `_IS_WINDOWS` monkeypatch
    ROUND-TRIP.

    Where the exclusion is a documented platform no-op the default is
    **REFUSAL**, and the read-back-only escape is reachable **only** under an
    explicit operator flag whose weaker guarantee appears in the refusal text.
    Silent degradation of the guard is PROHIBITED.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")

    monkeypatch.setattr(store_module, "_IS_WINDOWS", True)
    refused = _run(journal_dir, tmp_path)
    assert [o.disposition for o in refused] == [AdoptionDisposition.REFUSED_EXCLUSION_DEGRADED]
    assert not target.exists()
    detail = refused[0].detail
    assert "WEAKER" in detail, "the refusal text does not state the weaker guarantee"
    assert "--read-back-only" in detail
    assert "(3a)" in detail, "the refusal does not state that (3a) remains available"

    # The escape is reachable ONLY under the explicit flag.
    escaped = _run(journal_dir, tmp_path, allow_degraded_exclusion=True)
    assert [o.disposition for o in escaped] == [AdoptionDisposition.ADOPTED]
    assert target.is_file()

    # ROUND-TRIP: restore the platform and the default guard is back.
    monkeypatch.undo()
    assert store_module._IS_WINDOWS == (sys.platform == "win32")


# ---------------------------------------------------------------------------
# AC #9(d-ter) — the THREE-WAY classification + THE SHARPEST MUTATION PROBE.
# ---------------------------------------------------------------------------


def test_ac9d_ter_three_shapes_in_one_directory(tmp_path: Path) -> None:
    """AC #9(d-ter) — over **ONE** directory holding all three shapes.

    (1) LEGACY → adoptable; (2) CURRENT-FORMAT under this deployment's scope →
    ordinary state, **NOT** reported as mis-filed and **NOT** adopted; (3) a
    co-tenant journal under a DIFFERENT scope → NOT ATTRIBUTABLE FROM HERE.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id="other").capture(
        _snapshot("wf-cotenant")
    )
    current_before = (journal_dir / pause_journal_filename(_TENANT, "wf-current")).read_bytes()
    cotenant_before = (journal_dir / pause_journal_filename("other", "wf-cotenant")).read_bytes()

    outcomes = {o.workflow_id: o.disposition for o in _run(journal_dir, tmp_path)}

    assert outcomes["wf-legacy"] is AdoptionDisposition.ADOPTED
    # CURRENT-FORMAT is ORDINARY STATE — §13.7.1's own words — so it is SKIPPED,
    # not refused: describing this deployment's own healthy live state as a
    # refusal would make every idempotent re-run exit nonzero.
    assert outcomes["wf-current"] is AdoptionDisposition.SKIPPED_NOT_ADOPTABLE
    # The co-tenant's journal IS a mandated refusal: NOT-ATTRIBUTABLE FROM HERE,
    # and this surface does not guess whether it is mis-filed or foreign-scoped.
    assert outcomes["wf-cotenant"] is AdoptionDisposition.REFUSED_NOT_LEGACY
    # Neither was touched.
    assert (journal_dir / pause_journal_filename(_TENANT, "wf-current")).read_bytes() == (
        current_before
    )
    assert (journal_dir / pause_journal_filename("other", "wf-cotenant")).read_bytes() == (
        cotenant_before
    )


def test_ac9d_ter_a_mis_filed_record_is_dormant_and_stays_dormant(tmp_path: Path) -> None:
    """AC #9(d-ter) — the MIS-FILED case: a journal named `sha256(A)` whose
    wrapper is **B**.

    (i) the SHIPPED read of `A` still refuses it `workflow-mismatch` and the read
    of `B` never opens it — **dormant BY CONSTRUCTION**; (ii) the classification
    marks it not-LEGACY; (iii) the adoption **REFUSES that journal** and
    publishes it under **NEITHER** name.
    """
    from harness_runtime.lifecycle.journal_workflow_pause_store import PauseJournalReadCause

    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    misfiled = journal_dir / legacy_pause_journal_filename("A")
    misfiled.write_text(_record("A", wrapper_id="B") + "\n")

    # (i) dormant on the SHIPPED read, both ways. (Untenanted store, because the
    # legacy name is what the pre-v1.108 reader addressed.)
    legacy_reader = JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=None)
    monkey = pytest.MonkeyPatch()
    try:
        monkey.setattr(
            store_module,
            "pause_journal_filename",
            lambda scope, wf: legacy_pause_journal_filename(wf),
        )
        assert legacy_reader.read_latest_attributed("A").cause is (
            PauseJournalReadCause.WORKFLOW_MISMATCH
        )
        assert legacy_reader.read_latest_attributed("B").cause is PauseJournalReadCause.ABSENT
    finally:
        monkey.undo()

    # (ii) + (iii)
    outcomes = _run(journal_dir, tmp_path)
    assert [o.disposition for o in outcomes] == [AdoptionDisposition.REFUSED_NOT_LEGACY]
    assert not (journal_dir / pause_journal_filename(_TENANT, "A")).exists()
    assert not (journal_dir / pause_journal_filename(_TENANT, "B")).exists()


def test_ac9d_ter_mutation_probe_without_the_binding_check_dormant_becomes_live(
    tmp_path: Path,
) -> None:
    """AC #9(d-ter) — **THE MUTATION PROBE.** Remove the binding check and assert
    the adoption republishes the mis-filed record at `encode(tenant, B)`, where
    the snapshot-workflow match, step-index range and `snapshot_hash` guards
    **ALL PASS** — i.e. **dormant mis-filed state becomes LIVE state.**

    *This is the one place where the record shape being unchanged is not enough:
    the binding the old key carried implicitly must be checked explicitly before
    the new key replaces it.*

    **The mutation reverts BOTH enforcement points**, because since round 4 the
    binding term is enforced twice: once pre-lock on the enumeration's
    classification, and again under the exclusion on the bytes read there. Either
    one alone holds the record dormant, so mutating only the first would leave
    the probe passing for the wrong reason — it would be measuring the under-lock
    re-check rather than the term the probe names.
    """
    from harness_runtime.admin import pause_journal_enumeration as enum_module

    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    journal_dir.mkdir(parents=True)
    (journal_dir / legacy_pause_journal_filename("A")).write_text(
        _record("B", wrapper_id="B") + "\n"
    )

    real_classify = adoption_module.classify_journal_bytes

    def _trusting_classify(
        filename: str, raw: bytes, **kwargs: object
    ) -> tuple[str | None, JournalIdentityClass | None]:
        identity, _ = real_classify(filename, raw, **kwargs)  # type: ignore[arg-type]
        return identity, JournalIdentityClass.LEGACY

    # THE MUTATION: both checks trust the wrapper instead of the classification.
    monkey = pytest.MonkeyPatch()
    try:
        monkey.setattr(
            enum_module.EnumeratedJournal,
            "adoptable",
            property(lambda self: self.workflow_id is not None),
        )
        monkey.setattr(adoption_module, "classify_journal_bytes", _trusting_classify)
        outcomes = _run(journal_dir, tmp_path)
    finally:
        monkey.undo()

    assert [o.disposition for o in outcomes] == [AdoptionDisposition.ADOPTED], (
        "the mutation probe did not reproduce the promotion — the binding check "
        "is not actually what is holding the record dormant"
    )
    promoted = journal_dir / pause_journal_filename(_TENANT, "B")
    assert promoted.is_file()
    # And it is now LIVE: a tenant-scoped read of B resolves it and every shipped
    # guard passes, because the record was always internally consistent.
    live = JournalWorkflowPauseStore(
        journal_dir=journal_dir, tenant_id=_TENANT
    ).read_latest_attributed("B")
    assert live.snapshot is not None, "the promoted record is not readable — probe is vacuous"
    assert live.snapshot.workflow_id == "B"

    # RESTORE: with the real `adoptable`, the same directory refuses.
    for path in journal_dir.iterdir():
        if path.name != legacy_pause_journal_filename("A"):
            path.unlink()
    restored = _run(journal_dir, tmp_path)
    assert [o.disposition for o in restored] == [AdoptionDisposition.REFUSED_NOT_LEGACY]


# ---------------------------------------------------------------------------
# AC #9(e) — the account, TOTAL BY CONSTRUCTION.
# ---------------------------------------------------------------------------


def test_ac9e_every_journal_gets_exactly_one_durable_account_row(tmp_path: Path) -> None:
    """AC #9(e) — a **durable, operator-retrievable per-journal account**, so an
    interrupted or partial run is reconstructable **without** re-deriving it from
    the filesystem."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id="other").capture(
        _snapshot("wf-cotenant")
    )
    account = tmp_path / "account.jsonl"

    outcomes = adopt_pause_journals(journal_dir, tenant_id=_TENANT, account_path=account)

    rows = [json.loads(line) for line in account.read_text().splitlines() if line.strip()]
    outcome_rows = [row for row in rows if row["phase"] == "outcome"]
    intent_rows = [row for row in rows if row["phase"] == "publish-intent"]
    assert len(outcome_rows) == len(outcomes) == 2
    assert {row["disposition"] for row in outcome_rows} == {
        AdoptionDisposition.ADOPTED.value,
        AdoptionDisposition.REFUSED_NOT_LEGACY.value,
    }, "a co-tenant journal is NOT-ATTRIBUTABLE FROM HERE — a mandated refusal"
    assert all(row["source"] and row["recorded_at"] for row in rows)
    # Exactly ONE write-ahead intent row — the adopted journal's; a refusal
    # changes no durable state and therefore writes ahead of nothing.
    assert len(intent_rows) == 1
    assert intent_rows[0]["source"] == legacy_pause_journal_filename("wf-legacy")


def test_ac9e_the_disposition_vocabulary_is_total_over_the_mandated_refusals() -> None:
    """AC #9(e) — the vocabulary is **TOTAL over the refusals this unit
    mandates**, asserted PROGRAMMATICALLY over the shipped enum.

    The two the first draft of the spec's own list omitted — *refused-as-not-LEGACY*
    and *refused-because-the-exclusion-primitive-degraded* — are exactly the ones
    a hurried implementation swallows, so they are named here explicitly.
    """
    mandated = {
        "adopted",
        "skipped-as-already-published",
        "refused-as-foreign-target",
        "refused-on-read-back",
        "refused-as-not-LEGACY",
        "refused-because-the-exclusion-primitive-degraded",
    }
    shipped = {member.value for member in AdoptionDisposition}
    assert mandated <= shipped, f"a MANDATED disposition is missing: {mandated - shipped}"
    # The spec's list is explicitly a FLOOR ("at minimum"). Exactly ONE member is
    # added beyond it, and it is a NON-refusal — §13.7.1's CURRENT-FORMAT arm,
    # which that section itself calls "ordinary state" rather than a refusal.
    assert shipped - mandated == {"skipped-as-current-format-not-adoptable"}


def test_ac9e_totality_is_by_construction_not_by_enumeration() -> None:
    """AC #9(e) — **totality BY CONSTRUCTION**: every path that refuses a journal
    writes an account row, *and a test that adds a refusal without a disposition
    must fail.*

    Enforced at the TYPE: the per-journal function's only return type is
    `AdoptionOutcome`, whose `disposition` field is REQUIRED (no default), and the
    driver loop writes one row per returned outcome. There is therefore no
    reachable path that refuses without carrying a disposition — a new refusal
    that tried to would not construct.
    """
    import dataclasses
    import inspect

    fields = {f.name: f for f in dataclasses.fields(adoption_module.AdoptionOutcome)}
    assert fields["disposition"].default is dataclasses.MISSING
    assert fields["disposition"].default_factory is dataclasses.MISSING
    assert fields["disposition"].type in ("AdoptionDisposition", AdoptionDisposition)

    signature = inspect.signature(adoption_module._adopt_one)
    assert signature.return_annotation in ("AdoptionOutcome", adoption_module.AdoptionOutcome)

    # And the driver appends exactly one row per outcome — no branch skips it.
    source = inspect.getsource(adoption_module.adopt_pause_journals)
    assert source.count("_append_account_row(") == 1
    assert source.count("outcomes.append(") == 1


# ---------------------------------------------------------------------------
# AC #10 — the disposal action.
# ---------------------------------------------------------------------------


def test_ac10_disposal_is_dry_run_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #10 — **DRY-RUN BY DEFAULT**: assert nothing is removed absent an
    explicit non-dry-run flag."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id="other").capture(
        _snapshot("wf-cotenant")
    )
    before = sorted(p.name for p in journal_dir.iterdir())

    assert disposal_main([str(journal_dir), "--tenant-id", _TENANT]) == 0

    assert sorted(p.name for p in journal_dir.iterdir()) == before
    assert "DRY RUN" in capsys.readouterr().out


def test_ac10_disposal_refuses_while_3b_adoption_remains_possible(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """AC #10 — **refuses while (3b) adoption remains possible** absent an
    explicit acknowledgement that recoverable state is being discarded.

    *An operator who upgrades, learns from §13.7 that pauses were abandoned, and
    reaches for disposal must not thereby destroy their only (3b) recovery path
    using the very tool that told them the records existed.*
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    orphans, retained = plan_disposal(journal_dir, tenant_id=_TENANT)
    # The ORPHAN set and the (3b)-RECOVERABLE set are the SAME SET — which is
    # exactly why this refusal term exists. There is no third category safe to
    # delete without acknowledgement.
    assert len(orphans) == 1 and retained == []

    assert disposal_main([str(journal_dir), "--tenant-id", _TENANT, "--delete"]) == 1
    assert (journal_dir / legacy_pause_journal_filename("wf-legacy")).is_file()
    assert "refused" in capsys.readouterr().err

    # With the explicit acknowledgement it proceeds.
    assert (
        disposal_main(
            [
                str(journal_dir),
                "--tenant-id",
                _TENANT,
                "--delete",
                "--acknowledge-discarding-recoverable-state",
            ]
        )
        == 0
    )
    assert not (journal_dir / legacy_pause_journal_filename("wf-legacy")).exists()


def test_ac10_disposal_does_not_live_on_harness_inspect(tmp_path: Path) -> None:
    """AC #10 — the disposal lives on a **SEPARATE** admin action, **NOT** on
    `harness-inspect` — the §13 read-only invariant would reject it there
    (§13.7 term 6: *"a DISPOSAL action is a destructive write and is therefore
    FORECLOSED FROM THIS SURFACE BY THAT INVARIANT"*)."""
    from harness_runtime.admin.inspect import build_parser

    flags = {action.dest for action in build_parser()._actions}
    for forbidden in ("delete", "dispose", "remove", "acknowledge_discarding_recoverable_state"):
        assert forbidden not in flags, f"harness-inspect grew a destructive flag: {forbidden}"


# ---------------------------------------------------------------------------
# AC #11 — the §13.4 inventory, against SHIPPED reality and nothing more.
# ---------------------------------------------------------------------------


def test_ac11_the_adoption_action_is_registered_in_the_dispatcher_by_exact_name() -> None:
    """AC #11 — the (3b) adoption action — the one this unit is REQUIRED to build
    — is reachable under the flat `harness <subcommand>` namespace and **present
    in the dispatcher's registry by EXACT NAME**.

    *A doc row nobody dispatches is the defect the §13.4 inventory exists to
    prevent — which is exactly why this assertion is per-action-actually-owed,
    not per-row-declared.*
    """
    from harness_runtime.cli.app import app

    registered = {command.name for command in app.registered_commands}
    assert "adopt-pause-journals" in registered
    # The disposal was BUILT, so it is asserted too (AC #11's conditional half).
    assert "dispose-pause-journals" in registered
    # NO nested subcommands at v1 — the §13.4 flat-namespace invariant.
    assert not app.registered_groups


def test_ac11_both_actions_are_reachable_as_python_m_modules() -> None:
    """§13.4 permits the implementation to stay `python -m`, on the
    `migrate-audit-sidecar` precedent. Asserted by ACTUALLY INVOKING both."""
    for module in (
        "harness_runtime.admin.pause_journal_adoption",
        "harness_runtime.admin.pause_journal_disposal",
    ):
        completed = subprocess.run(
            [sys.executable, "-m", module, "--help"], capture_output=True, check=False
        )
        assert completed.returncode == 0, completed.stderr.decode()
        assert b"pause-journal" in completed.stdout.lower().replace(b"_", b"-")


def test_ac11_the_preexisting_migrate_audit_sidecar_gap_is_not_absorbed() -> None:
    """AC #11 — the §13.4 DECLARED count and the shipped dispatcher registry are
    **separate facts**, and this unit does not conflate them.

    Recorded so a later session does not read this AC as having taken on the
    pre-existing `migrate-audit-sidecar` spec-vs-shipped gap, and so nobody
    "fixes" a count by making the OPTIONAL disposal action mandatory.
    """
    from harness_runtime.cli.app import app

    registered = {command.name for command in app.registered_commands}
    # 5 shipped before this unit + the 2 it adds.
    assert registered == {
        "run",
        "daemon",
        "inspect",
        "shutdown",
        "migrate-audit-sidecar",
        "adopt-pause-journals",
        "dispose-pause-journals",
    }


# ---------------------------------------------------------------------------
# Cross-check: the account + the enumeration agree on the two scalars.
# ---------------------------------------------------------------------------


def test_the_adopted_target_is_byte_identical_to_the_legacy_source(tmp_path: Path) -> None:
    """Under Reading A this is a **pure RELOCATION** — the RECORD SHAPE is
    UNCHANGED, so the five-member vocabulary and the no-wrapper-key promise both
    hold, and the legacy source is left UNTOUCHED as an unread orphan."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    source_bytes = source.read_bytes()

    _run(journal_dir, tmp_path)

    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")
    assert target.read_bytes() == source_bytes
    assert source.read_bytes() == source_bytes, "the legacy source was modified"
    record = json.loads(target.read_text().splitlines()[-1])
    assert set(record) == {"workflow_id", "pause_snapshot"}
    assert record["pause_snapshot"]["snapshot_hash"] == "0" * 64
    assert (
        hashlib.sha256(target.read_text().splitlines()[-1].encode()).hexdigest()
        == hashlib.sha256(source.read_text().splitlines()[-1].encode()).hexdigest()
    )


# ---------------------------------------------------------------------------
# Out-of-family review round 1 — the fixes, each with its own witness.
# ---------------------------------------------------------------------------


def test_the_skip_verdict_never_bypasses_the_read_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 1 [P2] — an identical target does NOT short-circuit the read-back.

    A lockless pre-#1167 straggler appending after the source read used to
    produce a confident `SKIPPED_ALREADY_PUBLISHED` over a target that is now
    **STALE relative to its own source**. The read-back exists to detect exactly
    that writer, so no branch may bypass it — the skip verdict is now deferred
    until after it.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")
    # Pre-publish an IDENTICAL target — the exact state that reached the skip.
    target.write_bytes(source.read_bytes())

    copy_read = 2  # #1 enumeration, #2 adoption copy, #3 adoption read-back
    reads = {"n": 0}
    real_read_bytes = Path.read_bytes

    def _interfering_read_bytes(self: Path) -> bytes:
        if self == source:
            reads["n"] += 1
            if reads["n"] == copy_read:
                data = real_read_bytes(self)
                with self.open("a", encoding="utf-8") as handle:
                    handle.write(_record("wf-legacy", run_id="straggler") + "\n")
                return data
        return real_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", _interfering_read_bytes)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    dispositions = {o.disposition for o in outcomes}
    assert reads["n"] > copy_read, "the read-back never ran — the probe is vacuous"
    assert AdoptionDisposition.REFUSED_ON_READ_BACK in dispositions
    assert AdoptionDisposition.SKIPPED_ALREADY_PUBLISHED not in dispositions, (
        "a stale target was declared ALREADY PUBLISHED while its source had moved"
    )


def test_disposal_never_removes_a_journal_it_cannot_prove_is_an_orphan(
    tmp_path: Path,
) -> None:
    """Round 1 [P1] — **the delete set is the ORPHAN set and only that.**

    The first draft computed it as `not adoptable`, the exact INVERSE: it swept
    in this deployment's own CURRENT-FORMAT live journals, a CO-TENANT's valid
    journals, and every unreadable-identity row — and would have deleted all of
    them under `--delete` with **no acknowledgement at all**, since none of them
    counts as "recoverable" under that reading.

    *A predicate that reads as "everything not worth saving" is never a safe
    deletion set — only one that PROVES orphanhood is.*
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    legacy = _legacy(journal_dir, "wf-legacy")
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id="other").capture(
        _snapshot("wf-cotenant")
    )
    unreadable = journal_dir / pause_journal_filename(None, "wf-unreadable")
    unreadable.write_bytes(b"\xff\xfe\n")
    survivors = [
        journal_dir / pause_journal_filename(_TENANT, "wf-current"),
        journal_dir / pause_journal_filename("other", "wf-cotenant"),
        unreadable,
    ]

    orphans, retained = plan_disposal(journal_dir, tenant_id=_TENANT)
    assert [o.path.name for o in orphans] == [legacy.name]
    assert {r.path.name for r in retained} == {p.name for p in survivors}

    # Even the MOST permissive invocation removes ONLY the orphan.
    assert (
        disposal_main(
            [
                str(journal_dir),
                "--tenant-id",
                _TENANT,
                "--delete",
                "--acknowledge-discarding-recoverable-state",
            ]
        )
        == 0
    )
    assert not legacy.exists()
    for survivor in survivors:
        assert survivor.is_file(), f"disposal removed a NON-ORPHAN: {survivor.name}"


def test_disposal_dry_run_names_the_retained_set_explicitly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The dry run reports what it will NOT touch as well as what it will — so an
    operator can see that their live journals are out of scope rather than infer
    it from silence."""
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    JournalWorkflowPauseStore(journal_dir=journal_dir, tenant_id=_TENANT).capture(
        _snapshot("wf-current")
    )
    assert disposal_main([str(journal_dir), "--tenant-id", _TENANT]) == 0
    out = capsys.readouterr().out
    assert "RETAINED (never a disposal candidate)" in out
    assert "current-format" in out
    assert "0 journal(s) would be removed" in out


@pytest.mark.parametrize("command", ["adopt-pause-journals", "dispose-pause-journals"])
def test_parent_cli_maps_admin_arg_parse_failures_to_the_flat_cli_contract(
    command: str, tmp_path: Path
) -> None:
    """Round 1 [P2] — argparse `SystemExit(2)` must NOT escape the wrappers.

    The flat-CLI contract maps parse failures to `RT-FAIL-CLI-ARG-INVALID` and
    exit 3, as the adjacent `migrate-audit-sidecar` wrapper already does. Both
    new wrappers returned a bare 2 with no fail class.
    """
    from harness_runtime.cli.app import app
    from typer.testing import CliRunner

    result = CliRunner().invoke(app, [command, str(tmp_path), "--no-such-flag"])

    assert result.exit_code == 3, (
        f"expected the RT-FAIL-CLI-ARG-INVALID exit, got {result.exit_code}"
    )


# ---------------------------------------------------------------------------
# Out-of-family review round 2 — the fixes, each with its own witness.
# ---------------------------------------------------------------------------


def test_the_publish_intent_row_is_durable_before_the_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 2 [P1] — **WRITE-AHEAD**: a crash between the commit and the outcome
    row must still leave the ADOPTED fact reconstructable.

    An outcome row written only after `_adopt_one` returns leaves a window in
    which the target is committed and durable while NO row exists — and a re-run
    then records `skipped-as-already-published`, losing the ADOPTED fact
    PERMANENTLY and leaving the operator to infer it from the filesystem, the
    exact thing the account exists to avoid.

    The probe crashes immediately after the commit and asserts the account
    already names this source and target.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "wf-legacy")
    target = journal_dir / pause_journal_filename(_TENANT, "wf-legacy")
    account = tmp_path / "account.jsonl"

    real_link = os.link

    def _crash_after_commit(src: object, dst: object, **kwargs: object) -> None:
        real_link(src, dst, **kwargs)  # type: ignore[arg-type]
        raise KeyboardInterrupt("crash between the commit and the outcome row")

    monkeypatch.setattr(os, "link", _crash_after_commit)
    with pytest.raises(KeyboardInterrupt):
        adopt_pause_journals(journal_dir, tenant_id=_TENANT, account_path=account)
    monkeypatch.undo()

    assert target.is_file(), "the probe did not actually commit — it would be vacuous"
    rows = [json.loads(line) for line in account.read_text().splitlines() if line.strip()]
    intent = [row for row in rows if row["phase"] == "publish-intent"]
    outcomes = [row for row in rows if row["phase"] == "outcome"]
    assert len(intent) == 1, "no write-ahead row survived the crash"
    assert intent[0]["source"] == source.name
    assert intent[0]["target"] == target.name
    assert intent[0]["workflow_id"] == "wf-legacy"
    # An intent row with NO matching outcome row is the reconstruction signal.
    assert outcomes == []


def test_the_account_directory_entry_is_made_durable_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 2 [P2] — fsyncing a NEWLY-CREATED account file does not persist its
    DIRENT on POSIX.

    A power loss could otherwise leave the adopted target journals durable while
    the entire account file disappears — the state the account exists to make
    impossible. Asserted by observing that a DIRECTORY fd is fsynced during the
    first account write.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    account = tmp_path / "acct" / "account.jsonl"

    dir_fsyncs: list[int] = []
    real_fsync = os.fsync

    def _spy_fsync(fd: int) -> None:
        try:
            if os.fstat(fd).st_mode & 0o040000:  # S_IFDIR
                dir_fsyncs.append(fd)
        except OSError:  # pragma: no cover — defensive
            pass
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _spy_fsync)
    adopt_pause_journals(journal_dir, tenant_id=_TENANT, account_path=account)
    monkeypatch.undo()

    assert account.is_file()
    assert dir_fsyncs, "no directory fsync ran — the account dirent is not durable"


def test_the_dry_run_previews_legacy_journals_without_an_acknowledgement(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Round 2 [P2] — the DRY RUN must work on exactly the directory the tool
    exists for.

    Every LEGACY journal is both the only disposal candidate AND the thing that
    triggers the refuse-while-recoverable gate, so ordering that gate before the
    preview made the default invocation refuse on every real target — an
    operator had to acknowledge DESTROYING recoverable state merely to SEE what
    would be destroyed. That is a dry run in name only.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    legacy = _legacy(journal_dir, "wf-legacy")

    assert disposal_main([str(journal_dir), "--tenant-id", _TENANT]) == 0
    out = capsys.readouterr().out

    assert f"would remove: {legacy.name}" in out
    assert "1 journal(s) would be removed" in out
    # ... and it says, in the preview, that --delete alone will still refuse.
    assert "--delete alone will REFUSE" in out
    assert legacy.is_file(), "the DRY RUN removed something"

    # The gate still bites on the DESTRUCTIVE path.
    assert disposal_main([str(journal_dir), "--tenant-id", _TENANT, "--delete"]) == 1
    assert legacy.is_file()


# ---------------------------------------------------------------------------
# Out-of-family review ROUND 4 — the three adoption/disposal witnesses.
# ---------------------------------------------------------------------------


@requires_posix_flock
def test_round4_the_source_is_reclassified_under_the_lock_not_before_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 4 [P1] — **the identity that decides the target is re-derived from
    the bytes read UNDER the lock**, never carried over from the enumeration.

    The enumeration necessarily classifies BEFORE any lock is taken, so a
    LOCK-RESPECTING appender can land between the two and change the wrapper
    identity. Publishing under the PRE-LOCK identity would then write the CURRENT
    source bytes to the STALE key — an unusable target under a name whose record
    says something else, reported as ADOPTED, with every re-run refusing the
    source. Here the interfering append is injected at the exact instant the
    adoption reaches for the lock, which is the whole window.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "A")
    real_lock = adoption_module.cross_process_journal_lock
    interfered: list[str] = []

    def _append_then_lock(journal_path: Path) -> object:
        # A lock-RESPECTING writer: it appends before the adoption acquires, so
        # no exclusion is violated and the read-back cannot see it move either.
        if not interfered:
            interfered.append(journal_path.name)
            with journal_path.open("a", encoding="utf-8") as handle:
                handle.write(_record("B", wrapper_id="B") + "\n")
        return real_lock(journal_path)

    monkeypatch.setattr(adoption_module, "cross_process_journal_lock", _append_then_lock)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert interfered == [source.name], "the interference never ran — the probe is vacuous"
    assert [o.disposition for o in outcomes] == [AdoptionDisposition.REFUSED_NOT_LEGACY]
    # NOTHING is published — not at the stale key, and not at the new identity's
    # key either (this run never proved the new identity is adoptable at all).
    assert not (journal_dir / pause_journal_filename(_TENANT, "A")).exists()
    assert not (journal_dir / pause_journal_filename(_TENANT, "B")).exists()


@requires_posix_flock
def test_round4_mutation_probe_without_the_under_lock_recheck_the_stale_key_is_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 4 [P1] — **THE MUTATION PROBE** for the witness above.

    The mutation makes the under-lock re-classification return the PRE-LOCK
    answer, which is exactly what the code did before the round-4 fix. The
    stale-key publication reappears: the target is committed at
    `encode(tenant, "A")` carrying bytes whose latest wrapper says `"B"`.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    source = _legacy(journal_dir, "A")
    real_lock = adoption_module.cross_process_journal_lock
    interfered: list[str] = []

    def _append_then_lock(journal_path: Path) -> object:
        if not interfered:
            interfered.append(journal_path.name)
            with journal_path.open("a", encoding="utf-8") as handle:
                handle.write(_record("B", wrapper_id="B") + "\n")
        return real_lock(journal_path)

    # THE MUTATION: the re-check yields the enumeration's stale answer.
    def _stale_classification(
        filename: str, raw: bytes, **kwargs: object
    ) -> tuple[str | None, JournalIdentityClass | None]:
        return "A", JournalIdentityClass.LEGACY

    monkeypatch.setattr(adoption_module, "cross_process_journal_lock", _append_then_lock)
    monkeypatch.setattr(adoption_module, "classify_journal_bytes", _stale_classification)
    outcomes = _run(journal_dir, tmp_path)
    monkeypatch.undo()

    assert interfered == [source.name]
    assert [o.disposition for o in outcomes] == [AdoptionDisposition.ADOPTED], (
        "the mutation did not reproduce the publication — the under-lock re-check "
        "is not actually what is refusing"
    )
    stale_target = journal_dir / pause_journal_filename(_TENANT, "A")
    assert stale_target.is_file(), "no stale-key publication — the probe is vacuous"
    latest = json.loads(stale_target.read_text().splitlines()[-1])
    assert latest["workflow_id"] == "B", (
        "the target committed at A's key does not carry B's record, so the probe "
        "did not actually demonstrate the stale-key hazard"
    )

    # RESTORE: with the real re-check, the same interference refuses.
    stale_target.unlink()
    interfered.clear()
    monkeypatch.setattr(adoption_module, "cross_process_journal_lock", _append_then_lock)
    restored = _run(journal_dir, tmp_path)
    monkeypatch.undo()
    assert [o.disposition for o in restored] == [AdoptionDisposition.REFUSED_NOT_LEGACY]
    assert not stale_target.exists()


def test_round4_a_newly_created_account_parent_has_its_own_dirent_fsynced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 4 [P2] — a directory the account write CREATES needs its OWN dirent
    made durable in ITS parent.

    Fsyncing only `account_path.parent` persists the account file's entry INSIDE
    a directory whose own entry may still be unflushed, so a power loss could
    preserve the adopted targets and lose the WHOLE account directory — the same
    total loss the round-2 file-dirent fix closed one level down. Asserted per
    INODE, over a two-deep account path, so the two newly-created ancestors are
    distinguished from the leaf directory the round-2 fix already covered.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    _legacy(journal_dir, "wf-legacy")
    outer = tmp_path / "acct"
    inner = outer / "nested"
    account = inner / "account.jsonl"

    root_id = (tmp_path.stat().st_dev, tmp_path.stat().st_ino)
    fsynced: set[tuple[int, int]] = set()
    real_fsync = os.fsync

    def _spy_fsync(fd: int) -> None:
        try:
            info = os.fstat(fd)
            fsynced.add((info.st_dev, info.st_ino))
        except OSError:  # pragma: no cover — defensive
            pass
        return real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _spy_fsync)
    adopt_pause_journals(journal_dir, tenant_id=_TENANT, account_path=account)
    monkeypatch.undo()

    assert account.is_file()
    inner_id = (inner.stat().st_dev, inner.stat().st_ino)
    outer_id = (outer.stat().st_dev, outer.stat().st_ino)
    # The leaf — already covered at round 2, asserted here so the probe is not
    # silently measuring the wrong directory.
    assert inner_id in fsynced
    # The two NEW ones: each created ancestor's dirent, made durable in ITS parent.
    assert outer_id in fsynced, "the created account parent's own dirent is not durable"
    assert root_id in fsynced, "the outermost created directory's dirent is not durable"


def test_round4_disposal_fsyncs_the_journal_directory_after_the_unlinks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Round 4 [P3] — an unlink is a directory-entry change like any other.

    Without a directory fsync afterwards the command reports success and the
    orphan REAPPEARS after a power loss — a disposal tool whose deletions do not
    survive a reboot is worse than one that refuses. Scoped to the journal
    directory's own inode and ORDERED against the unlinks, so a fsync that ran
    before the removals would not satisfy it.
    """
    journal_dir = tmp_path / PAUSE_JOURNAL_SUBDIR
    legacy = _legacy(journal_dir, "wf-legacy")

    target_id = (journal_dir.stat().st_dev, journal_dir.stat().st_ino)
    events: list[str] = []
    real_unlink = os.unlink
    real_fsync = os.fsync

    def _spy_unlink(path: object, **kwargs: object) -> None:
        events.append("unlink")
        return real_unlink(path, **kwargs)  # type: ignore[arg-type]

    def _spy_fsync(fd: int) -> None:
        try:
            info = os.fstat(fd)
            if (info.st_dev, info.st_ino) == target_id:
                events.append("journal-dir-fsync")
        except OSError:  # pragma: no cover — defensive
            pass
        return real_fsync(fd)

    monkeypatch.setattr(os, "unlink", _spy_unlink)
    monkeypatch.setattr(os, "fsync", _spy_fsync)
    exit_code = disposal_main(
        [
            str(journal_dir),
            "--tenant-id",
            _TENANT,
            "--delete",
            "--acknowledge-discarding-recoverable-state",
        ]
    )
    monkeypatch.undo()

    assert exit_code == 0
    assert not legacy.exists(), "nothing was removed — the probe is vacuous"
    assert "unlink" in events
    assert "journal-dir-fsync" in events, "the removals were never made durable"
    assert events.index("journal-dir-fsync") > events.index("unlink"), (
        "the directory fsync ran BEFORE the unlinks, which persists nothing that "
        "the removals changed"
    )
