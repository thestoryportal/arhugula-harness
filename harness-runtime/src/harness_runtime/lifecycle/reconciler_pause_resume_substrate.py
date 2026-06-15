"""Durable etcd-style reconciler engine pause/resume substrate (R-FS-1 E-3 / U-RT-123).

A hand-rolled (I-6 — **no vendored K8s / etcd-operator**) level-triggered
read/diff/converge reconciler ``EnginePauseResumeSubstrate`` for the
``RECONCILER_LOOP`` engine class (C-CP-07 §7.1 row 4: "lifecycle = harness-hosted
reconciler control-loop" per the v1_33 §7.4 reading; concurrent-resume mitigation =
"etcd compare-and-swap"). It **extends the proven #475
``JournalEnginePauseResumeSubstrate``** (the real durable filesystem-journal
substrate, append-JSONL / fsync / fail-closed) into a **resource-version-stamped
converged-state store with an etcd-style compare-and-swap (CAS) lease**, per the
operator-ratified v1_33 §7.4 reconciliation note: *"a level-triggered, read/diff/
converge reconcile loop with a compare-and-swap lease over an own-format durable
store, joined to the F2 state-ledger on ``idempotency_key``."*

**What RECONCILER_LOOP adds over the #475 JOURNAL / U-RT-121 WAL substrates** (the
load-bearing distinctions, not a cosmetic swap):

- **Resource-version stamping (the etcd revision analogue).** Each captured
  converged-state ``PauseEvent`` is written as a **checksummed,
  monotonically-``resource_version``-stamped** record. The version makes this a
  genuine reconciler convergence log (each converge bumps the revision); the
  SHA-256 checksum makes torn writes detectable per record.
- **Level-triggered converge replay + torn-write recovery.** ``attempt_resume``
  re-derives the **latest committed converged state** (the highest valid
  ``resource_version`` = the last record of the contiguous valid prefix), stopping
  at the FIRST record whose checksum / ordering / parse fails. A half-written
  trailing record (a crash mid-converge: truncated line, partial JSON, bad
  checksum) is **discarded** and replay recovers to the last *committed*
  convergence — the standard recovery property (an un-``fsync``-acknowledged
  trailing write was never durable). A corrupt **middle** record is NOT skipped
  (the prefix scan stops at the gap → replay never resumes *past* a corruption;
  gap-safe). This mirrors the U-RT-121 WAL recovery semantics (both are
  multi-record logs where the last *valid* record is the authoritative latest
  committed state).
- **Compare-and-swap (CAS) lease — the genuine NEW capability over WAL
  (floor (iii); §7.1 row 4 "concurrent-resume mitigation = etcd compare-and-swap").**
  ``attempt_resume`` atomically **claims** the resume against the
  ``resource_version`` it observed, via a POSIX ``O_CREAT | O_EXCL`` claim file
  stamped with an **owner token** (the resume's ``resume_request_actor`` — a real
  etcd lease has an owner, so the holder can re-enter and a stranger cannot; no
  vendored etcd). The owner token is the load-bearing distinction:
    - A **DIFFERENT owner** racing the same ``resource_version`` LOSES → its resume
      **ABORTS** (``ABORT_REVALIDATION_FAILED``). THIS is the genuine
      concurrent-resume mitigation: two *distinct* reconcilers converging the same
      workflow → only one applies.
    - A re-acquire by the **SAME owner** — a crash-then-retry by the same logical
      reconciler over the durable directory (a restarted process) — is **ALLOWED**.
      A permanent, owner-blind claim would deadlock this exact crash-recovery path
      (floor (i) "durable replay across restart"); the owner token re-admits it.
  It maps a lost race onto the **closed** ``ResumeOutcomeKind`` enum (no new
  primitive — X-AL-3-clean): a lost concurrent race IS a revalidation failure (the
  converged state is being resumed by another reconciler) → §22.1 escalation, the
  honest surface for a genuine two-reconciler anomaly.

Drop-in for ``RuntimeEngineRecoveryLoop`` (implements the same C-CP-22
``EnginePauseResumeSubstrate`` Protocol: ``capture_pause_snapshot`` /
``attempt_resume`` / ``has_pause_record``). PathClass placement: the on-disk
convergence log + claim files map to the existing closed-enum
``PathClass.STATE_LEDGER`` member — IS-AL-1-clean, no IS extension (mirrors
U-RT-121's reading).

**Engine-class-aware binding is U-RT-124** (O-E3-1): this substrate is a drop-in
for the engine recovery loop exactly as U-RT-121 was; the binding that fires
RECONCILER_LOOP workflows against THIS substrate while WAL_SEGMENT keeps firing
against the WAL substrate (no cross-contamination) is the activation unit. The
**live-K8s e2e + the §7.2/ADR-D1 deployment-admissibility (O-E3-2/3) are separate
downstream gates**, not built here — this substrate is the hand-rolled
non-live durable proof.

Authority: C-CP-07 §7.1 row 4 + §7.4 (v1_33 substrate-deferral, hand-rolled
etcd-style per I-6); C-CP-08 §8.1 ``reconciler_converge`` + §8.2 row 4;
``.harness/r-fs-1-e3-plan-decomposition.md`` §2 (U-RT-123). Mirrors the
``WALSegmentEnginePauseResumeSubstrate`` (U-RT-121) structure.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

from harness_core import WorkflowID
from harness_cp.pause_resume_protocol import (
    PauseEvent,
    ResumeAttempt,
    ResumeOutcome,
    ResumeOutcomeKind,
    classify_resume,
)
from pydantic import ValidationError

from harness_runtime.lifecycle.journal_pause_resume_substrate import (
    JournalEnginePauseResumeSubstrate,
    json_default,
    json_object_hook,
)

__all__ = ["ReconcilerEnginePauseResumeSubstrate"]


class ReconcilerEnginePauseResumeSubstrate(JournalEnginePauseResumeSubstrate):
    """Durable etcd-style reconciler ``EnginePauseResumeSubstrate`` (extends #475).

    ``capture_pause_snapshot`` appends one checksummed, ``resource_version``-stamped
    converged-state record (durably ``fsync``-ed); ``attempt_resume`` replays the
    contiguous valid prefix to the last committed convergence, then **acquires a
    compare-and-swap lease** on that ``resource_version`` (atomic ``O_EXCL`` claim)
    before proceeding — a concurrent resume that already claimed the revision makes
    THIS resume abort (``ABORT_REVALIDATION_FAILED``; the converged state was
    superseded). Because the log is on disk, a fresh instance over the same
    directory resumes a convergence captured by a prior process (the #475
    durability property, extended per-revision with the CAS concurrent-resume
    mitigation).

    ``reconcile_log_dir`` is the durable directory (aliases the base's
    ``journal_dir``); the injected providers mirror the base so this is a drop-in
    durable replacement for ``RuntimeEngineRecoveryLoop``.
    """

    @property
    def reconcile_log_dir(self) -> Path:
        """The durable convergence-log directory (the base's ``journal_dir``)."""
        return self._journal_dir

    # -- per-workflow serialization (read-modify-write atomicity) -----------

    def _lock_file(self, workflow_id: WorkflowID) -> Path:
        """The per-workflow advisory-lock file (filesystem-safe, collision-free)."""
        digest = hashlib.sha256(str(workflow_id).encode("utf-8")).hexdigest()
        return self._journal_dir / f"{digest}.lock"

    @contextmanager
    def _workflow_lock(self, workflow_id: WorkflowID) -> Generator[None, None, None]:
        """Hold an exclusive per-workflow advisory ``flock`` for a critical section.

        Makes the substrate's read-modify-write operations **atomic w.r.t. concurrent
        same-host operations on the same workflow**: ``_append`` (read-prefix → assign
        ``resource_version`` → write) and the resume's read-prefix → CAS-claim both run
        under this lock, so (a) two concurrent captures cannot pick the same
        ``resource_version`` and clobber each other's replay (a durably-returned
        capture is never lost), and (b) a converge cannot interleave between a resume's
        prefix read and its claim (so the CAS always claims the then-current head, not
        a stale revision). Released promptly (the resume holds it only around read +
        claim, NOT around the injected diff/revalidate providers — so a provider can
        never deadlock on re-entry).

        ``flock`` is POSIX advisory + same-host; it provides single-host-linearizable
        single-writer semantics. The **cross-reconciler / split-brain** case (a second
        reconciler on another host racing the same workflow) is guarded by the durable
        owner-token CAS claim (``_acquire_cas_lease``), which persists on shared
        storage. True multi-host linearizability (etcd/Raft-grade) is beyond a
        filesystem substrate; this combination — same-host flock + durable owner-CAS —
        is the operative model for the harness-hosted reconciler (one owner per
        workflow per the lease discipline).
        """
        path = self._lock_file(workflow_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

    # -- CAS lease (the genuine new capability) -----------------------------

    def _claim_file(self, workflow_id: WorkflowID, resource_version: int) -> Path:
        """The atomic CAS claim file for one (workflow, resource_version) pair."""
        digest = hashlib.sha256(str(workflow_id).encode("utf-8")).hexdigest()
        return self._journal_dir / f"{digest}.v{resource_version}.claim"

    def _acquire_cas_lease(
        self, workflow_id: WorkflowID, resource_version: int, owner: str
    ) -> bool:
        """Acquire the per-(workflow, revision) CAS lease for ``owner``; True iff held.

        The etcd compare-and-swap concurrent-resume mitigation, hand-rolled via the
        POSIX ``O_CREAT | O_EXCL`` atomic-create primitive **plus an owner token**
        (the standard lease-owner pattern — a real etcd lease has an owner, so the
        holder can re-enter and a stranger cannot):

        - The FIRST owner to create the per-revision claim file wins (its owner token
          is written + ``fsync``-ed).
        - A re-acquire by the **SAME owner** — a crash-then-retry / re-entrant resume
          by the same logical reconciler over the durable directory (a fresh process
          of the same reconciler) — is **ALLOWED** (the recorded owner matches →
          ``True``). This is the floor-(i) "durable replay across restart" path: a
          restarted reconciler MUST be able to resume its own paused workflow.
        - A **DIFFERENT owner** racing the same revision **LOSES** (``False``) → its
          resume aborts. THIS is the genuine concurrent-resume mitigation: two
          *distinct* reconcilers converging the same workflow → only one applies.

        **Crash-atomic publish (no empty-claim window).** The claim is published
        *with* its owner token in a single atomic step: write the token to a temp
        file (``fsync``-ed), then ``os.link`` it into place — ``link`` is atomic and
        fails with ``FileExistsError`` if the claim already exists. So a crash can
        only ever leave an orphan temp (ignored / cleaned up), NEVER a durable EMPTY
        claim — which would otherwise permanently deadlock the same-owner crash-retry
        (an empty token reads as ≠ owner). After winning, the claim's directory entry
        is ``fsync``-ed (mirroring the journal new-file dir-fsync) so a crash cannot
        lose the dirent and let a different owner re-create the claim and double-resume.

        - SAME owner re-acquire (crash-retry over the durable directory) → the recorded
          token matches → ``True`` (floor-(i) "durable replay across restart").
        - DIFFERENT owner racing the same revision → loses → ``False`` → aborts. The
          genuine concurrent-resume mitigation (only one of two distinct reconcilers
          applies).
        """
        path = self._claim_file(workflow_id, resource_version)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.parent / f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        try:
            fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            try:
                os.write(fd, owner.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            try:
                # Atomic create-with-content: link fails if the claim already exists.
                os.link(tmp, path)
            except FileExistsError:
                # Claim already published — re-entrant iff the recorded owner matches
                # (same logical reconciler retrying); a different owner is a race loss.
                try:
                    return path.read_text(encoding="utf-8").strip() == owner
                except OSError:
                    return False
            # Won — make the new claim's dirent durable (survive a crash).
            self._fsync_dir(path.parent)
            return True
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    # -- Protocol: resume with the CAS lease --------------------------------

    def attempt_resume(self, attempt: ResumeAttempt) -> ResumeOutcome:
        """Replay the latest committed convergence, then CAS-claim the resume.

        Order: (1) read the latest committed converged state + its
        ``resource_version`` (``None`` → ``ABORT_SNAPSHOT_CORRUPTED``, fail closed);
        (2) acquire the owner-scoped CAS lease on that revision — a re-acquire by the
        SAME owner (crash-then-retry) is allowed (floor-(i) crash-recovery), but a
        DIFFERENT owner racing the same revision makes THIS one
        ``ABORT_REVALIDATION_FAILED`` (a genuine concurrent-resume race);
        (3) on the held lease, run the inherited diff / revalidate / classify flow.
        """
        # Hold the per-workflow lock around read-prefix → CAS-claim so the claimed
        # revision is the then-current head (no converge interleaves between the read
        # and the claim — fixes the resume-side TOCTOU) and so a concurrent capture
        # cannot clobber the version. Released BEFORE the injected diff/revalidate
        # providers below (so a provider can never deadlock on lock re-entry).
        with self._workflow_lock(attempt.paused_workflow_id):
            prefix = self._valid_prefix(attempt.paused_workflow_id)
            if not prefix:
                return ResumeOutcome(
                    outcome_kind=ResumeOutcomeKind.ABORT_SNAPSHOT_CORRUPTED,
                    material_diff=(),
                    context_revalidated=False,
                    resume_audit_entry_id=None,
                )
            resource_version = len(prefix) - 1
            event = prefix[-1]
            owner = str(attempt.resume_request_actor)
            claimed = self._acquire_cas_lease(attempt.paused_workflow_id, resource_version, owner)
        if not claimed:
            # A DIFFERENT owner already holds this revision's lease → a genuine
            # concurrent-resume race lost (NOT a same-owner crash-retry, which the
            # owner-scoped lease re-admits). Maps onto the CLOSED ResumeOutcomeKind
            # enum (no new primitive): a lost concurrent race is a revalidation
            # failure — the converged state is being resumed by another reconciler,
            # so this attempt must not also apply (→ §22.1 escalation, the honest
            # surface for a genuine two-reconciler anomaly).
            return ResumeOutcome(
                outcome_kind=ResumeOutcomeKind.ABORT_REVALIDATION_FAILED,
                material_diff=(),
                context_revalidated=False,
                resume_audit_entry_id=(
                    self._resume_audit_entry_id_provider(
                        attempt, ResumeOutcomeKind.ABORT_REVALIDATION_FAILED
                    )
                    if self._resume_audit_entry_id_provider is not None
                    else None
                ),
            )
        diff = self._diff_provider(event, attempt)
        revalidated = self._revalidation_succeeded(attempt, diff)
        # Reuse the canonical C-CP-22 §22.1 decision core (one source of truth;
        # it keys on `d.is_material`, not bare emptiness) — identical to the base
        # `attempt_resume` classify, so the only divergence is the CAS lease above.
        outcome_kind = classify_resume(diff, revalidation_succeeded=revalidated)
        resume_audit_entry_id = (
            self._resume_audit_entry_id_provider(attempt, outcome_kind)
            if self._resume_audit_entry_id_provider is not None
            else None
        )
        return ResumeOutcome(
            outcome_kind=outcome_kind,
            material_diff=diff,
            context_revalidated=(outcome_kind is ResumeOutcomeKind.RESUME_AFTER_REVALIDATION),
            resume_audit_entry_id=resume_audit_entry_id,
        )

    # -- durable per-revision convergence-log I/O (overrides the base) ------

    @staticmethod
    def _canonical_payload(
        workflow_id: WorkflowID, resource_version: int, event: PauseEvent
    ) -> str:
        """The exact serialized record payload the checksum is computed over."""
        return json.dumps(
            {
                "workflow_id": str(workflow_id),
                "resource_version": resource_version,
                "pause_event": event.model_dump(mode="python"),
            },
            default=json_default,
            sort_keys=True,
        )

    def _valid_prefix(self, workflow_id: WorkflowID) -> list[PauseEvent]:
        """Scan the contiguous valid convergence-record prefix → events.

        Byte-robust (reads bytes, decodes each newline-terminated chunk
        individually) so an invalid-UTF-8 or partial trailing record ends the prefix
        without crashing. A *complete* record is a ``b"...\\n"`` chunk that decodes,
        is non-blank, passes checksum, matches its expected ``resource_version``
        (= position), and validates as a ``PauseEvent``. The scan stops at a torn
        tail (no final ``\\n``) or the first corrupt record (gap-safe — replay never
        resumes past a corruption).
        """
        path = self._journal_file(workflow_id)
        if not path.exists():
            return []
        try:
            raw = path.read_bytes()
        except OSError:
            return []
        events: list[PauseEvent] = []
        offset = 0
        index = 0
        total = len(raw)
        while offset < total:
            newline = raw.find(b"\n", offset)
            if newline == -1:
                break  # torn tail: no trailing newline → incomplete write
            chunk = raw[offset:newline]
            try:
                line = chunk.decode("utf-8")
            except UnicodeDecodeError:
                break  # invalid UTF-8 → corruption, stop the prefix
            if not line.strip():
                break  # blank line ends the valid prefix (defensive)
            parsed = self._parse_record(line, str(workflow_id), index)
            if parsed is None:
                break  # first corruption ends the contiguous valid prefix
            events.append(parsed)
            offset = newline + 1
            index += 1
        return events

    def _valid_extent(self, workflow_id: WorkflowID) -> int:
        """Byte offset where the contiguous valid record prefix ends (truncation point)."""
        path = self._journal_file(workflow_id)
        if not path.exists():
            return 0
        try:
            raw = path.read_bytes()
        except OSError:
            return 0
        offset = 0
        index = 0
        total = len(raw)
        while offset < total:
            newline = raw.find(b"\n", offset)
            if newline == -1:
                break
            chunk = raw[offset:newline]
            try:
                line = chunk.decode("utf-8")
            except UnicodeDecodeError:
                break
            if not line.strip():
                break
            if self._parse_record(line, str(workflow_id), index) is None:
                break
            offset = newline + 1
            index += 1
        return offset

    def _append(self, workflow_id: WorkflowID, event: PauseEvent) -> None:
        """Append one checksummed convergence record to the workflow's log, durably.

        **Recovery-on-open:** before appending, truncate any torn/garbage tail back
        to the contiguous valid prefix (otherwise a crash that left a partial
        trailing record would corrupt the next append). The new ``resource_version``
        is the count of valid prefix records, so it stays monotonic over *committed*
        convergences (a torn write is discarded, not counted). Write-ahead
        durability: the record is ``fsync``-ed before returning; a new file's
        directory entry is also ``fsync``-ed (best-effort, POSIX).
        """
        # Serialize the read-prefix → assign-version → append critical section per
        # workflow so two concurrent captures cannot pick the same resource_version
        # (which replay would treat as a corrupt gap, silently losing a
        # durably-returned capture). The lock file lives beside the log.
        with self._workflow_lock(workflow_id):
            path = self._journal_file(workflow_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            prefix = self._valid_prefix(workflow_id)
            resource_version = len(prefix)
            if path.exists():
                valid_extent = self._valid_extent(workflow_id)
                if path.stat().st_size != valid_extent:
                    with path.open("r+b") as handle:
                        handle.truncate(valid_extent)
                        handle.flush()
                        os.fsync(handle.fileno())
            payload = self._canonical_payload(workflow_id, resource_version, event)
            checksum = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            record = json.dumps({"checksum": checksum, "payload": payload}, sort_keys=True)
            is_new_file = not path.exists()
            with path.open("a", encoding="utf-8") as handle:
                handle.write(record + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            if is_new_file:
                self._fsync_dir(path.parent)

    def _read_latest(self, workflow_id: WorkflowID) -> PauseEvent | None:
        """Return the last committed convergence's ``PauseEvent``, or ``None``.

        Replays the contiguous valid prefix (torn tail discarded; corrupt middle NOT
        skipped — gap-safe). ``None`` when the workflow has no log OR not even its
        first record is valid. (``attempt_resume`` overrides the base to add the CAS
        lease, but this primitive stays consistent for ``has_pause_record`` parity.)
        """
        prefix = self._valid_prefix(workflow_id)
        return prefix[-1] if prefix else None

    @staticmethod
    def _parse_record(
        line: str, expected_workflow_id: str, expected_index: int
    ) -> PauseEvent | None:
        """Parse + integrity-check one convergence record; ``None`` if invalid.

        Validates, in order: outer JSON shape (``checksum`` + ``payload`` string);
        SHA-256 checksum over the exact payload bytes; payload JSON shape;
        ``workflow_id`` match; ``resource_version`` == position (ordering integrity);
        ``PauseEvent`` validation. Any failure → ``None`` (fail closed).
        """
        try:
            outer = json.loads(line)
            if not isinstance(outer, dict):
                return None
            frame = cast("dict[str, object]", outer)
            checksum = frame.get("checksum")
            payload = frame.get("payload")
            if not isinstance(checksum, str) or not isinstance(payload, str):
                return None
            if hashlib.sha256(payload.encode("utf-8")).hexdigest() != checksum:
                return None
            loaded = json.loads(payload, object_hook=json_object_hook)
            if not isinstance(loaded, dict):
                return None
            record = cast("dict[str, object]", loaded)
            if record.get("workflow_id") != expected_workflow_id:
                return None
            if record.get("resource_version") != expected_index:
                return None
            return PauseEvent.model_validate(record["pause_event"])
        except (ValueError, ValidationError, KeyError, TypeError):
            return None
