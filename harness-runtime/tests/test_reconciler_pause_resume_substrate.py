"""Durable etcd-style reconciler engine pause/resume substrate tests (R-FS-1 E-3 / U-RT-123).

The load-bearing proofs:

- ``test_resume_after_fresh_instance`` — cross-process durability (a fresh instance
  resumes a convergence captured by a prior one; the #475 property, per revision).
- ``test_torn_tail_recovers_to_last_committed`` / ``..._then_append_recovers`` /
  ``test_corrupt_middle_record_stops_at_gap`` — WAL-style torn-write + gap-safe
  recovery (shared with U-RT-121).
- **``test_cas_lease_concurrent_resume_one_wins_one_aborts``** — THE KEYSTONE: the
  genuine NEW capability over WAL. Two resumes of the SAME committed
  ``resource_version`` → the first wins the compare-and-swap lease (RESUME_CLEAN),
  the second loses it (ABORT_REVALIDATION_FAILED — the converged state was
  superseded). This is the etcd compare-and-swap concurrent-resume mitigation
  (C-CP-07 §7.1 row 4 / §7.4 floor (iii)), hand-rolled via the POSIX ``O_EXCL``
  atomic-create primitive — no vendored etcd.
- ``test_cas_lease_new_convergence_resumes_again`` — the CAS is per-revision: a NEW
  converge (new ``resource_version``) is resumable again (the lease is revision-scoped,
  not a permanent freeze).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from harness_core import WorkflowID
from harness_cp.cp_shared_types import ActorIdentity
from harness_cp.handoff_context import ExternalReference, ReferenceClass, StateSummary
from harness_cp.pause_resume_protocol import (
    PauseReason,
    ResumeAttempt,
    ResumeOutcomeKind,
)
from harness_is.state_ledger_entry_schema import Identifier
from harness_runtime.lifecycle.reconciler_pause_resume_substrate import (
    ReconcilerEnginePauseResumeSubstrate,
)

_ACTOR = ActorIdentity("reconciler-loop")


def _state_summary(version: str = "v1") -> StateSummary:
    return StateSummary(
        relevant_entries=(),
        summary_text=version,
        summary_hash=hashlib.sha256(version.encode()).hexdigest(),
        idempotency_key=Identifier("idem-" + version),
        external_references=(
            ExternalReference(
                reference_class=ReferenceClass.FILESYSTEM_STATE,
                reference_id="state-" + version,
                snapshot_capture_at_pause=b"snapshot-" + version.encode("utf-8"),
            ),
        ),
    )


def _resume_attempt(workflow_id: str, *, actor: ActorIdentity = _ACTOR) -> ResumeAttempt:
    return ResumeAttempt(
        paused_workflow_id=WorkflowID(workflow_id),
        resume_at="2026-06-15T12:00:00Z",
        resume_request_actor=actor,
    )


def _substrate(
    reconcile_log_dir: Path,
    *,
    state_summary_provider: Callable[[], StateSummary] | None = None,
    **kwargs: object,
) -> ReconcilerEnginePauseResumeSubstrate:
    return ReconcilerEnginePauseResumeSubstrate(
        journal_dir=reconcile_log_dir,
        state_summary_provider=state_summary_provider or _state_summary,
        **kwargs,  # type: ignore[arg-type]
    )


def _versioned_substrate(reconcile_log_dir: Path) -> ReconcilerEnginePauseResumeSubstrate:
    versions = iter(f"v{i}" for i in range(1, 100))
    return ReconcilerEnginePauseResumeSubstrate(
        journal_dir=reconcile_log_dir,
        state_summary_provider=lambda: _state_summary(next(versions)),
    )


# --- capture / durability ---------------------------------------------------


def test_capture_writes_durable_checksummed_record(tmp_path: Path) -> None:
    substrate = _substrate(tmp_path)
    event = substrate.capture_pause_snapshot(WorkflowID("wf-1"), PauseReason.ENGINE_NATIVE_PAUSE)

    log = substrate._journal_file(WorkflowID("wf-1"))  # type: ignore[attr-defined]
    assert log.exists(), "capture must persist to disk"
    lines = [line for line in log.read_text().splitlines() if line.strip()]
    assert len(lines) == 1
    outer = json.loads(lines[0])
    assert set(outer) == {"checksum", "payload"}
    assert hashlib.sha256(outer["payload"].encode("utf-8")).hexdigest() == outer["checksum"]
    assert json.loads(outer["payload"])["resource_version"] == 0
    assert substrate._read_latest(WorkflowID("wf-1")) == event  # type: ignore[attr-defined]


def test_resource_version_is_monotonic_per_workflow(tmp_path: Path) -> None:
    substrate = _versioned_substrate(tmp_path)
    for _ in range(3):
        substrate.capture_pause_snapshot(WorkflowID("wf-seq"), PauseReason.ENGINE_NATIVE_PAUSE)

    log = substrate._journal_file(WorkflowID("wf-seq"))  # type: ignore[attr-defined]
    lines = [line for line in log.read_text().splitlines() if line.strip()]
    versions = [json.loads(json.loads(line)["payload"])["resource_version"] for line in lines]
    assert versions == [0, 1, 2]


def test_resume_after_fresh_instance(tmp_path: Path) -> None:
    """Cross-process durability — a fresh instance resumes a prior-process convergence."""
    capturing = _substrate(tmp_path)
    captured = capturing.capture_pause_snapshot(
        WorkflowID("wf-crash"), PauseReason.ENGINE_NATIVE_PAUSE
    )
    del capturing

    resuming = _substrate(tmp_path)
    outcome = resuming.attempt_resume(_resume_attempt("wf-crash"))

    assert outcome.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN
    assert resuming._read_latest(WorkflowID("wf-crash")) == captured  # type: ignore[attr-defined]


def test_multiple_records_resume_latest_committed(tmp_path: Path) -> None:
    substrate = _versioned_substrate(tmp_path)
    first = substrate.capture_pause_snapshot(
        WorkflowID("wf-multi"), PauseReason.ENGINE_NATIVE_PAUSE
    )
    second = substrate.capture_pause_snapshot(
        WorkflowID("wf-multi"), PauseReason.ENGINE_NATIVE_PAUSE
    )
    assert first != second
    assert substrate._read_latest(WorkflowID("wf-multi")) == second  # type: ignore[attr-defined]


def test_no_record_aborts_snapshot_corrupted(tmp_path: Path) -> None:
    """No convergence record → ABORT_SNAPSHOT_CORRUPTED (fail closed)."""
    substrate = _substrate(tmp_path)
    outcome = substrate.attempt_resume(_resume_attempt("wf-absent"))
    assert outcome.outcome_kind is ResumeOutcomeKind.ABORT_SNAPSHOT_CORRUPTED


def test_has_pause_record_presence(tmp_path: Path) -> None:
    substrate = _substrate(tmp_path)
    assert not substrate.has_pause_record(WorkflowID("wf-h"))
    substrate.capture_pause_snapshot(WorkflowID("wf-h"), PauseReason.ENGINE_NATIVE_PAUSE)
    assert substrate.has_pause_record(WorkflowID("wf-h"))


# --- CAS lease (the genuine new capability over WAL) -------------------------


def test_cas_lease_concurrent_resume_one_wins_one_aborts(tmp_path: Path) -> None:
    """KEYSTONE — floor (iii) etcd compare-and-swap concurrent-resume mitigation.

    Two DIFFERENT reconcilers (distinct owner tokens) resume the SAME committed
    resource_version: the first wins the owner-scoped CAS lease (RESUME_CLEAN), the
    second — a DIFFERENT owner — loses it (ABORT_REVALIDATION_FAILED; the converged
    state is being resumed by another reconciler, so this attempt must not also
    apply). This is the genuine distinguishing RECONCILER_LOOP capability over
    WAL_SEGMENT (whose repeated resume is idempotent-RESUME_CLEAN). Realized via a
    POSIX O_EXCL atomic-create claim file + owner token (no vendored etcd).
    """
    substrate = _substrate(tmp_path)
    substrate.capture_pause_snapshot(WorkflowID("wf-cas"), PauseReason.ENGINE_NATIVE_PAUSE)

    first = substrate.attempt_resume(_resume_attempt("wf-cas", actor=ActorIdentity("reconciler-A")))
    second = substrate.attempt_resume(
        _resume_attempt("wf-cas", actor=ActorIdentity("reconciler-B"))
    )

    assert first.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN, "first owner wins the CAS"
    assert second.outcome_kind is ResumeOutcomeKind.ABORT_REVALIDATION_FAILED, (
        "a DIFFERENT owner racing the same revision loses the CAS → aborts"
    )
    # The claim file for revision 0 exists and is published ATOMICALLY WITH its owner
    # token (the temp+link crash-atomic publish — never an empty claim that would
    # deadlock a same-owner crash-retry).
    claim = substrate._claim_file(WorkflowID("wf-cas"), 0)  # type: ignore[attr-defined]
    assert claim.exists()
    assert claim.read_text().strip() == "reconciler-A"


def test_cas_lease_same_owner_crash_retry_is_admitted(tmp_path: Path) -> None:
    """Floor (i) crash-recovery — the SAME owner re-resuming the same committed
    revision is ADMITTED (RESUME_CLEAN both times), NOT false-aborted. A restarted
    reconciler (fresh substrate instance over the same durable dir) MUST be able to
    resume its own paused workflow; an owner-blind permanent claim would deadlock
    this exact crash-recovery path (the F2-01 fix)."""
    capturing = _substrate(tmp_path)
    capturing.capture_pause_snapshot(WorkflowID("wf-retry"), PauseReason.ENGINE_NATIVE_PAUSE)
    # Reconciler-X resumes (wins, completes), then "crashes" — fresh instance below.
    first = capturing.attempt_resume(
        _resume_attempt("wf-retry", actor=ActorIdentity("reconciler-X"))
    )
    del capturing
    # A restarted reconciler-X over the SAME durable dir retries the SAME revision.
    restarted = _substrate(tmp_path)
    retry = restarted.attempt_resume(
        _resume_attempt("wf-retry", actor=ActorIdentity("reconciler-X"))
    )
    assert first.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN
    assert retry.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN, (
        "same-owner crash-retry of the same revision must be re-admitted (floor (i))"
    )


def test_cas_lease_is_per_workflow(tmp_path: Path) -> None:
    """A CAS claim for one workflow's revision does NOT block another workflow's
    resume at the same revision number (the lease is keyed per (workflow, revision))."""
    substrate = _substrate(tmp_path)
    substrate.capture_pause_snapshot(WorkflowID("wf-a"), PauseReason.ENGINE_NATIVE_PAUSE)
    substrate.capture_pause_snapshot(WorkflowID("wf-b"), PauseReason.ENGINE_NATIVE_PAUSE)

    assert substrate.attempt_resume(_resume_attempt("wf-a")).outcome_kind is (
        ResumeOutcomeKind.RESUME_CLEAN
    )
    # wf-b at the same revision 0 is unaffected by wf-a's claim.
    assert substrate.attempt_resume(_resume_attempt("wf-b")).outcome_kind is (
        ResumeOutcomeKind.RESUME_CLEAN
    )


def test_cas_lease_new_convergence_resumes_again(tmp_path: Path) -> None:
    """The CAS is per-revision, NOT a permanent freeze: after the first resume claims
    revision 0, a NEW converge (revision 1) is resumable again (RESUME_CLEAN) — the
    lease is revision-scoped (etcd semantics: a new revision is a fresh CAS target)."""
    substrate = _versioned_substrate(tmp_path)
    substrate.capture_pause_snapshot(WorkflowID("wf-rev"), PauseReason.ENGINE_NATIVE_PAUSE)
    # First resume claims revision 0.
    assert substrate.attempt_resume(_resume_attempt("wf-rev")).outcome_kind is (
        ResumeOutcomeKind.RESUME_CLEAN
    )
    # A new converge bumps to revision 1 → resumable again (fresh CAS target), and
    # the same owner re-entering revision 1 is admitted (crash-retry).
    substrate.capture_pause_snapshot(WorkflowID("wf-rev"), PauseReason.ENGINE_NATIVE_PAUSE)
    assert (
        substrate.attempt_resume(
            _resume_attempt("wf-rev", actor=ActorIdentity("owner-1"))
        ).outcome_kind
        is ResumeOutcomeKind.RESUME_CLEAN
    )
    # The mitigation still holds per-revision: a DIFFERENT owner racing revision 1
    # loses the CAS (the per-revision concurrent-resume guard is intact).
    assert (
        substrate.attempt_resume(
            _resume_attempt("wf-rev", actor=ActorIdentity("owner-2"))
        ).outcome_kind
        is ResumeOutcomeKind.ABORT_REVALIDATION_FAILED
    )


def test_concurrent_captures_serialize_no_lost_records(tmp_path: Path) -> None:
    """P2.2 — the per-workflow flock serializes concurrent same-workflow captures so
    no two pick the same resource_version. N threads each capture the same workflow;
    the flock serializes the read-assign-append critical section, so the log holds
    exactly N records with monotonic resource_versions 0..N-1 (a durably-returned
    capture is never lost to a same-version collision that replay would treat as a
    corrupt gap)."""
    substrate = _substrate(tmp_path)  # fixed (thread-safe) state-summary provider
    n = 12
    with ThreadPoolExecutor(max_workers=n) as pool:
        list(
            pool.map(
                lambda _: substrate.capture_pause_snapshot(
                    WorkflowID("wf-concurrent"), PauseReason.ENGINE_NATIVE_PAUSE
                ),
                range(n),
            )
        )
    log = substrate._journal_file(WorkflowID("wf-concurrent"))  # type: ignore[attr-defined]
    lines = [line for line in log.read_text().splitlines() if line.strip()]
    versions = [json.loads(json.loads(line)["payload"])["resource_version"] for line in lines]
    assert versions == list(range(n)), "all N captures land with monotonic versions (none lost)"
    # The full prefix replays cleanly — no gap from a collided/duplicate version.
    assert substrate.attempt_resume(_resume_attempt("wf-concurrent")).outcome_kind is (
        ResumeOutcomeKind.RESUME_CLEAN
    )


# --- torn-write / recovery semantics (shared with U-RT-121) -----------------


def test_torn_tail_recovers_to_last_committed(tmp_path: Path) -> None:
    """A half-written trailing record is discarded; replay recovers to the last
    committed convergence (RESUME_CLEAN — a torn tail is an uncommitted write)."""
    substrate = _versioned_substrate(tmp_path)
    substrate.capture_pause_snapshot(WorkflowID("wf-torn"), PauseReason.ENGINE_NATIVE_PAUSE)
    second = substrate.capture_pause_snapshot(
        WorkflowID("wf-torn"), PauseReason.ENGINE_NATIVE_PAUSE
    )
    log = substrate._journal_file(WorkflowID("wf-torn"))  # type: ignore[attr-defined]
    with log.open("a", encoding="utf-8") as handle:
        handle.write('{"checksum": "deadbeef", "payload": "{partial')

    outcome = substrate.attempt_resume(_resume_attempt("wf-torn"))
    assert outcome.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN
    assert substrate._read_latest(WorkflowID("wf-torn")) == second  # type: ignore[attr-defined]


def test_torn_tail_then_append_recovers_and_continues(tmp_path: Path) -> None:
    """Recovery-on-open: after a crash leaves a torn trailing record, the next
    capture truncates it and appends cleanly — replay sees the NEW committed record."""
    substrate = _versioned_substrate(tmp_path)
    substrate.capture_pause_snapshot(WorkflowID("wf-recover"), PauseReason.ENGINE_NATIVE_PAUSE)
    log = substrate._journal_file(WorkflowID("wf-recover"))  # type: ignore[attr-defined]
    with log.open("a", encoding="utf-8") as handle:
        handle.write('{"checksum": "x", "payload": "{torn-no-newline')

    third = substrate.capture_pause_snapshot(
        WorkflowID("wf-recover"), PauseReason.ENGINE_NATIVE_PAUSE
    )
    assert substrate._read_latest(WorkflowID("wf-recover")) == third  # type: ignore[attr-defined]
    assert substrate.attempt_resume(_resume_attempt("wf-recover")).outcome_kind is (
        ResumeOutcomeKind.RESUME_CLEAN
    )
    lines = [line for line in log.read_text().splitlines() if line.strip()]
    assert len(lines) == 2
    versions = [json.loads(json.loads(line)["payload"])["resource_version"] for line in lines]
    assert versions == [0, 1]


def test_corrupt_middle_record_stops_at_gap(tmp_path: Path) -> None:
    """Gap-safe: a corrupt MIDDLE record is not skipped — replay stops at the gap and
    recovers the prefix BEFORE it, never resuming past a corruption."""
    substrate = _versioned_substrate(tmp_path)
    first = substrate.capture_pause_snapshot(WorkflowID("wf-gap"), PauseReason.ENGINE_NATIVE_PAUSE)
    substrate.capture_pause_snapshot(WorkflowID("wf-gap"), PauseReason.ENGINE_NATIVE_PAUSE)
    substrate.capture_pause_snapshot(WorkflowID("wf-gap"), PauseReason.ENGINE_NATIVE_PAUSE)

    log = substrate._journal_file(WorkflowID("wf-gap"))  # type: ignore[attr-defined]
    lines = [line for line in log.read_text().splitlines() if line.strip()]
    corrupt = json.loads(lines[1])
    corrupt["checksum"] = "0" * 64
    lines[1] = json.dumps(corrupt, sort_keys=True)
    log.write_text("\n".join(lines) + "\n")

    outcome = substrate.attempt_resume(_resume_attempt("wf-gap"))
    assert outcome.outcome_kind is ResumeOutcomeKind.RESUME_CLEAN
    assert substrate._read_latest(WorkflowID("wf-gap")) == first  # type: ignore[attr-defined]
