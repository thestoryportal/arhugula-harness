"""B-104 Task 6: audited recovery of one exact resume claim (6a) or record (6b phase A).

A released or abandoned claim is an operator decision about possibly-executed work, so
every transition is bracketed by durable IS audit entries: a claim-scoped INTENT is
fsynced before the claim changes, the transition is made durable, then COMPLETE is
fsynced. A retry of the same action reconciles whichever phase persisted; it never
invents a phase from missing evidence.

- **release** (unstarted claim, current record): link the live claim to a deterministic
  archive, then unlink the live name. The canonical path frees for a later claim C2; the
  C1 archive stays as history and never authorizes C2.
- **abandon** (operator-attested quiescence): write a deterministic terminal tombstone and
  keep the claim bytes. Any tombstone bars every later claim of the record. A tombstone
  asserts refusal, never that earlier work did not run.
- **COMPLETE/none**: a pending INTENT whose action is now moot, proved against a
  byte- and inode-identical live claim, the exact original lease and no transition.
- **record abandon** (operator-attested quiescence; Task 6b phase A): for a record whose
  claim is absent, has no parseable token, or is unreadable, pin that typed observation
  in a record-scoped INTENT, write a deterministic record tombstone, then COMPLETE. The
  claim and lease files are preserved; the tombstone bars every later claim of the exact
  record, never a sibling or a later record. A released C1 archive with its completed
  claim release is expected history; any other archive holds.

Lock order: journal lock, then the exact lease by NONBLOCKING exclusive probe, then the IS
ledger lock inside `append_recovery_audit_entry`. Placement is revalidated before the
journal lock, by every lease probe, and before each filesystem mutation.

Claim-scoped requests refuse the three record-scoped states as HELD without audit, and a
record abandon refuses a claim with a parseable token. A token claim whose lease is
missing or invalid fits neither scope's typed observation and stays HELD (phase B).
One open action per record spans both scopes.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol

from harness_core import JournalRecordRef
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import (
    Actor,
    ActorClass,
    ClaimAbsentObservation,
    ClaimCompleteAudit,
    ClaimIntentAudit,
    ClaimNoTokenObservation,
    ClaimObservation,
    ClaimUnreadableObservation,
    Identifier,
    QuiescenceAttestation,
    RecordCompleteAudit,
    RecordIntentAudit,
    RecordObservation,
    RecoveryAudit,
    RecoveryRecordIdentity,
)
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    RecoveryAuditConflictError,
    RecoveryAuditIntegrityError,
    RecoveryAuditPayload,
    WriteKey,
    append_recovery_audit_entry,
    read_ledger,
    recovery_audit_idempotency_key,
)

from harness_runtime.config.state_placement import PlacedStateDir, require_inside_state_root
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    cross_process_journal_lock,
)
from harness_runtime.lifecycle.resume_claim_store import (
    HeldLease,
    InvalidClaim,
    LeaseBusy,
    ResumeClaimStore,
    StartedOrUnknown,
    UnstartedProof,
    parse_claim,
)

__all__ = [
    "ClaimAbandon",
    "ClaimRecoveryRequest",
    "ClaimRelease",
    "PauseClaimRecovery",
    "RecordAbandon",
    "RecoveryDisposition",
    "RecoveryOutcome",
    "RecoveryRequest",
    "claim_subject_id",
    "record_subject_id",
]

_MAX_CLAIM_BYTES = 65536
_OPEN_FLAGS = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC
_CREATE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC

ClaimAudit = ClaimIntentAudit | ClaimCompleteAudit
IntentAudit = ClaimIntentAudit | RecordIntentAudit
CompleteAudit = ClaimCompleteAudit | RecordCompleteAudit


class _ClaimPaths(Protocol):
    """The claim store's canonical names for one exact record (`paths_for`)."""

    journal: Path
    claim: Path
    archive_prefix: str
    tombstone_prefix: str


class RecoveryOutcome(StrEnum):
    RELEASED = "released"
    ABANDONED = "abandoned"
    COMPLETED_NONE = "completed_none"
    HELD = "held"
    """No mutation; the evidence does not support this action (a permanent hold under a
    pending INTENT, or a state only record-scoped recovery may handle)."""
    RETRYABLE_CONTENTION = "retryable_contention"
    INTEGRITY_FAULT = "integrity_fault"


@dataclass(frozen=True)
class RecoveryDisposition:
    outcome: RecoveryOutcome
    reason: str
    """Stable machine code naming why, e.g. `evidence-lost` or `payload-conflict`."""


@dataclass(frozen=True)
class ClaimRelease:
    """Free an unstarted claim of a current record for a later claim."""

    record_ref: JournalRecordRef
    action_id: str
    operator_uid: int
    reason_digest: str


@dataclass(frozen=True)
class ClaimAbandon:
    """Terminally abandon the record; requires the operator's quiescence attestation."""

    record_ref: JournalRecordRef
    action_id: str
    operator_uid: int
    reason_digest: str
    quiescence_attestation: QuiescenceAttestation

    def __post_init__(self) -> None:
        # The annotation alone does not stop `None` at runtime; refuse it at the boundary
        # so an unattested abandon never reaches the audit or a tombstone.
        if not isinstance(self.quiescence_attestation, QuiescenceAttestation):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("claim abandon requires a QuiescenceAttestation")


@dataclass(frozen=True)
class RecordAbandon:
    """Terminally abandon a record whose claim is absent, tokenless or unreadable."""

    record_ref: JournalRecordRef
    action_id: str
    operator_uid: int
    reason_digest: str
    quiescence_attestation: QuiescenceAttestation

    def __post_init__(self) -> None:
        # [LAW:parse-dont-validate] The request is the boundary: an unattested or
        # another operator's attestation never reaches the audit or a tombstone.
        if not isinstance(self.quiescence_attestation, QuiescenceAttestation):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("record abandon requires a QuiescenceAttestation")
        if self.quiescence_attestation.operator_uid != self.operator_uid:
            raise ValueError("quiescence attestation operator must match recovery operator")


# [LAW:types-are-the-program] Each scope is its own request type with its own audited
# path; a record abandon is never a relabelled claim abandon.
ClaimRecoveryRequest = ClaimRelease | ClaimAbandon
RecoveryRequest = ClaimRecoveryRequest | RecordAbandon


class _DispositionError(Exception):
    """Carries a final, mutation-free disposition out of the locked section."""

    def __init__(self, disposition: RecoveryDisposition) -> None:
        super().__init__(disposition.reason)
        self.disposition = disposition


def _held(reason: str) -> _DispositionError:
    return _DispositionError(RecoveryDisposition(RecoveryOutcome.HELD, reason))


def _fault(reason: str) -> _DispositionError:
    return _DispositionError(RecoveryDisposition(RecoveryOutcome.INTEGRITY_FAULT, reason))


# --- deterministic identities (one recipe each) ------------------------------------------


def _digest(*parts: Any) -> str:
    encoded = json.dumps(list(parts), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def claim_subject_id(ref: JournalRecordRef, claim_name: str, token: str) -> str:
    """The audit subject of one intact claim: exact record, canonical name and token.

    A later claim C2 of the same record has a different token, hence its own subject and
    its own action namespace.
    """
    return _digest(
        "harness-runtime/resume-claim-subject/v1", ref.model_dump(mode="json"), claim_name, token
    )


def record_subject_id(ref: JournalRecordRef, claim_name: str) -> str:
    """The audit subject of a record-scoped action: exact record and canonical claim name."""
    return _digest(
        "harness-runtime/resume-record-subject/v1", ref.model_dump(mode="json"), claim_name
    )


def _archive_path(prefix_of: Path, archive_prefix: str, audit: ClaimAudit) -> Path:
    suffix = _digest("harness-runtime/resume-claim-archive/v1", audit.subject_id, audit.action_id)
    return prefix_of.with_name(archive_prefix + suffix)


def _tombstone_kind(
    audit: RecoveryAudit,
) -> Literal["claim_tombstone", "record_tombstone"]:
    return "claim_tombstone" if audit.scope == "claim" else "record_tombstone"


def _tombstone_path(prefix_of: Path, tombstone_prefix: str, audit: RecoveryAudit) -> Path:
    # Under the claim store's per-record tombstone prefix, so admission of exactly this
    # record refuses whichever scope wrote it.
    suffix = _digest(
        f"harness-runtime/resume-{audit.scope}-tombstone/v1", audit.subject_id, audit.action_id
    )
    return prefix_of.with_name(tombstone_prefix + suffix)


def _tombstone_bytes(audit: RecoveryAudit) -> bytes:
    # A claim tombstone names the claim bytes it barred; a record tombstone names the
    # whole typed observation, since there may be no claim bytes at all.
    evidence = (
        {"claim_bytes_digest": audit.observation.claim_bytes_digest}
        if isinstance(audit.observation, ClaimObservation)
        else {"observation": audit.observation.model_dump(mode="json")}
    )
    body = {
        "version": 1,
        "kind": _tombstone_kind(audit),
        "subject_id": audit.subject_id,
        "action_id": audit.action_id,
        "record_identity": audit.record_identity.model_dump(mode="json"),
        **evidence,
    }
    return (json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _release_digest(archive: Path, observation: ClaimObservation) -> str:
    return _digest(
        "harness-runtime/resume-claim-transition/release-archive/v1",
        archive.name,
        observation.claim_bytes_digest,
        observation.claim_st_dev,
        observation.claim_st_ino,
    )


def _tombstone_digest(kind: str, tombstone: Path, body: bytes) -> str:
    return _digest(
        f"harness-runtime/resume-claim-transition/{kind.replace('_', '-')}/v1",
        tombstone.name,
        hashlib.sha256(body).hexdigest(),
    )


def _none_digest(observation: ClaimObservation) -> str:
    return _digest(
        "harness-runtime/resume-claim-transition/none/v1", observation.model_dump(mode="json")
    )


# --- filesystem effects (fault-injection seams) --------------------------------------------


def _fsync_dir(path: Path) -> None:
    # [LAW:no-silent-failure] A transition is durable only once its directory is synced.
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _fsync_file(fd: int) -> None:
    os.fsync(fd)


def _sync_file(path: Path) -> None:
    fd = os.open(path, _OPEN_FLAGS)
    try:
        _fsync_file(fd)
    finally:
        os.close(fd)


def _link_archive(live: Path, archive: Path) -> None:
    """No-replace hard link: an existing archive is judged, never overwritten."""
    os.link(live, archive, follow_symlinks=False)


def _write_new_file(path: Path, body: bytes) -> None:
    """Exclusive create and full write; durability is the caller's file+directory sync."""
    fd = os.open(path, _CREATE_FLAGS, 0o600)
    try:
        view = memoryview(body)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("short tombstone write")
            view = view[written:]
    finally:
        os.close(fd)


@dataclass(frozen=True)
class _LiveClaim:
    raw: bytes
    st_dev: int
    st_ino: int


def _read_live_claim(path: Path) -> _LiveClaim | None:
    """`None` when absent; `OSError` when present but not a readable regular file."""
    try:
        fd = os.open(path, _OPEN_FLAGS)
    except FileNotFoundError:
        return None
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise OSError("claim is not a regular file")
        raw = os.read(fd, _MAX_CLAIM_BYTES + 1)
        if len(raw) > _MAX_CLAIM_BYTES:
            raise OSError("oversized claim")
        return _LiveClaim(raw, st.st_dev, st.st_ino)
    finally:
        os.close(fd)


def _matches(observation: ClaimObservation, path: Path, live: _LiveClaim | None) -> bool:
    return (
        live is not None
        and str(path) == observation.canonical_claim_path
        and hashlib.sha256(live.raw).hexdigest() == observation.claim_bytes_digest
        and (live.st_dev, live.st_ino) == (observation.claim_st_dev, observation.claim_st_ino)
    )


def _observe_record(
    claim: Path, ref: JournalRecordRef
) -> RecordObservation | UnstartedProof | StartedOrUnknown:
    """Classify the claim name as one typed record observation, or its parsed token claim.

    [LAW:parse-dont-validate] A claim with a parseable token comes back as that parse,
    so it cannot be mistaken for, or relabelled as, a record-scoped state.
    """
    parent = os.stat(claim.parent, follow_symlinks=False)
    path, dev, ino = str(claim), parent.st_dev, parent.st_ino
    try:
        live = _read_live_claim(claim)
    except OSError:
        st = os.lstat(claim)
        return ClaimUnreadableObservation(
            kind="claim_unreadable",
            canonical_claim_path=path,
            parent_st_dev=dev,
            parent_st_ino=ino,
            claim_st_dev=st.st_dev,
            claim_st_ino=st.st_ino,
        )
    if live is None:
        return ClaimAbsentObservation(
            kind="claim_absent", canonical_claim_path=path, parent_st_dev=dev, parent_st_ino=ino
        )
    parsed = parse_claim(live.raw, ref)
    if isinstance(parsed, InvalidClaim):
        return ClaimNoTokenObservation(
            kind="claim_no_token",
            canonical_claim_path=path,
            parent_st_dev=dev,
            parent_st_ino=ino,
            claim_st_dev=live.st_dev,
            claim_st_ino=live.st_ino,
            raw_digest=hashlib.sha256(live.raw).hexdigest(),
        )
    return parsed


def _pending(audits: list[RecoveryAudit], scope: Literal["claim", "record"]) -> set[str]:
    """Action IDs of one scope with a durable INTENT and no COMPLETE."""
    scoped = [a for a in audits if a.scope == scope]
    return {a.action_id for a in scoped if a.phase == "intent"} - {
        a.action_id for a in scoped if a.phase == "complete"
    }


def _lease_is_original(lease: HeldLease, observation: ClaimObservation) -> bool:
    st = os.fstat(lease.fd)
    return lease.token == observation.lease_generation and (st.st_dev, st.st_ino) == (
        observation.lease_st_dev,
        observation.lease_st_ino,
    )


def _completed(audit: CompleteAudit) -> RecoveryDisposition:
    outcome = {
        "release_archive": RecoveryOutcome.RELEASED,
        "claim_tombstone": RecoveryOutcome.ABANDONED,
        "record_tombstone": RecoveryOutcome.ABANDONED,
        "none": RecoveryOutcome.COMPLETED_NONE,
    }[audit.transition_kind]
    return RecoveryDisposition(outcome, audit.transition_kind)


def _requested(
    request: RecoveryRequest,
) -> tuple[Literal["claim", "record"], Literal["release", "abandon"], QuiescenceAttestation | None]:
    match request:
        case ClaimRelease():
            return "claim", "release", None
        case ClaimAbandon(quiescence_attestation=attestation):
            return "claim", "abandon", attestation
        case RecordAbandon(quiescence_attestation=attestation):
            return "record", "abandon", attestation


# --- the coordinator -----------------------------------------------------------------------


class PauseClaimRecovery:
    """Claim-scoped INTENT → transition → COMPLETE over one placed pause journal."""

    def __init__(
        self,
        *,
        placement: PlacedStateDir,
        tenant_id: str | None,
        ledger: JsonlLedgerHandle,
        deadline_seconds: float | None = None,
    ) -> None:
        # The audit ledger is recovery state too: it must live under the same verified root.
        require_inside_state_root(
            ledger.canonical_path,
            placement.config,
            placement.stamp,
            what="recovery audit ledger",
        )
        self._placement = placement
        self._claims = ResumeClaimStore(placement=placement, tenant_id=tenant_id)
        self._journal = JournalWorkflowPauseStore(journal_dir=placement.path, tenant_id=tenant_id)
        self._ledger = ledger
        self._deadline = deadline_seconds

    def recover(self, request: RecoveryRequest) -> RecoveryDisposition:
        """Run or reconcile one action. Durability failures raise; they are not outcomes."""
        paths = self._claims.paths_for(request.record_ref)
        self._placement.revalidate()
        with cross_process_journal_lock(paths.journal, deadline_seconds=self._deadline):
            try:
                return self._recover_locked(request)
            except _DispositionError as disposed:
                return disposed.disposition

    # -- locked section ----------------------------------------------------------------

    def _recover_locked(self, request: RecoveryRequest) -> RecoveryDisposition:
        # Every audit of the record, both scopes: an action ID names one action per record.
        audits = self._record_audits(request.record_ref)
        mine = [a for a in audits if a.action_id == request.action_id]
        completes = [a for a in mine if isinstance(a, ClaimCompleteAudit | RecordCompleteAudit)]
        intents = [a for a in mine if isinstance(a, ClaimIntentAudit | RecordIntentAudit)]
        if len(completes) > 1 or len(intents) > 1:
            raise _fault("ambiguous-action")
        if completes:
            self._require_same_request(completes[0], request)
            # An identical retry re-syncs the persisted COMPLETE before reporting it.
            self._append(completes[0])
            return _completed(completes[0])
        if intents:
            self._require_same_request(intents[0], request)
            # Re-sync an INTENT whose first sync may have failed before acting on it.
            self._append(intents[0])
            match intents[0]:
                case ClaimIntentAudit() as intent:
                    return self._reconcile(intent, request.record_ref)
                case RecordIntentAudit() as intent:
                    return self._reconcile_record(intent, request.record_ref, audits)
        match request:
            case RecordAbandon():
                return self._begin_record(request, audits)
            case ClaimRelease() | ClaimAbandon():
                return self._begin(request, audits)

    def _record_audits(self, ref: JournalRecordRef) -> list[RecoveryAudit]:
        identity = self._identity(ref)
        try:
            entries = read_ledger(self._ledger) if self._ledger.canonical_path.exists() else []
        except (ValueError, KeyError, TypeError, UnicodeError) as exc:
            raise _fault(f"ledger-integrity: {type(exc).__name__}") from exc
        return [
            e.recovery_audit
            for e in entries
            if e.recovery_audit is not None and e.recovery_audit.record_identity == identity
        ]

    @staticmethod
    def _identity(ref: JournalRecordRef) -> RecoveryRecordIdentity:
        return RecoveryRecordIdentity(
            tenant_id=ref.tenant,
            workflow_id=ref.workflow_id,
            record_count=ref.record_count,
            latest_digest=ref.latest_digest,
            snapshot_hash=ref.snapshot_hash,
        )

    @staticmethod
    def _require_same_request(audit: RecoveryAudit, request: RecoveryRequest) -> None:
        scope, action, attestation = _requested(request)
        stable = (
            audit.scope,
            audit.action,
            audit.operator_uid,
            audit.reason_digest,
            audit.quiescence_attestation,
        )
        if stable != (scope, action, request.operator_uid, request.reason_digest, attestation):
            raise _fault("payload-conflict")

    def _tombstoned(self, ref: JournalRecordRef) -> bool:
        paths = self._claims.paths_for(ref)
        return any(
            entry.name.startswith(paths.tombstone_prefix)
            for entry in os.scandir(paths.journal.parent)
        )

    def _is_current(self, ref: JournalRecordRef) -> bool:
        latest = self._journal.read_latest_attributed(ref.workflow_id)
        return (latest.record_count, latest.latest_record_digest) == (
            ref.record_count,
            ref.latest_digest,
        )

    def _exact_lease(self, ref: JournalRecordRef) -> HeldLease:
        probe = self._claims.probe_lease(ref)
        if isinstance(probe, LeaseBusy):
            raise _DispositionError(
                RecoveryDisposition(RecoveryOutcome.RETRYABLE_CONTENTION, "lease-holder-active")
            )
        if not isinstance(probe, HeldLease):
            raise _held("lease-missing-or-invalid")
        return probe

    # -- a new action -----------------------------------------------------------------

    def _begin(
        self, request: ClaimRecoveryRequest, audits: list[RecoveryAudit]
    ) -> RecoveryDisposition:
        ref = request.record_ref
        paths = self._claims.paths_for(ref)
        if self._tombstoned(ref):
            raise _held("record-tombstoned")
        if _pending(audits, "record"):
            raise _held("record-action-pending")
        try:
            lease = self._exact_lease(ref)
        except _DispositionError as disposed:
            if disposed.disposition.outcome is RecoveryOutcome.HELD:
                raise _held("record-scope-required: lease missing or invalid") from None
            raise
        try:
            # Read under the held lease: only a lease holder can append `started`.
            try:
                live = _read_live_claim(paths.claim)
            except OSError:
                raise _held("record-scope-required: claim unreadable") from None
            if live is None:
                raise _held("record-scope-required: claim absent")
            parsed = parse_claim(live.raw, ref)
            if isinstance(parsed, InvalidClaim):
                raise _held("record-scope-required: claim has no token")
            subject = claim_subject_id(ref, paths.claim.name, parsed.token)
            self._require_no_other_action(subject, request, audits)
            if self._journal.read_exact(ref) is None:
                raise _held("record-evidence-lost")
            if isinstance(request, ClaimRelease):
                if isinstance(parsed, StartedOrUnknown):
                    raise _held("release-forbidden: execution may have begun")
                if not self._is_current(ref):
                    raise _held("release-moot: record is not current")
            lease_st = os.fstat(lease.fd)
            _, action, attestation = _requested(request)
            intent = ClaimIntentAudit(
                schema_version=1,
                scope="claim",
                phase="intent",
                action=action,
                action_id=request.action_id,
                record_identity=self._identity(ref),
                subject_id=subject,
                operator_uid=request.operator_uid,
                reason_digest=request.reason_digest,
                quiescence_attestation=attestation,
                observation=ClaimObservation(
                    claim_bytes_digest=hashlib.sha256(live.raw).hexdigest(),
                    canonical_claim_path=str(paths.claim),
                    claim_st_dev=live.st_dev,
                    claim_st_ino=live.st_ino,
                    lease_generation=lease.token,
                    lease_st_dev=lease_st.st_dev,
                    lease_st_ino=lease_st.st_ino,
                ),
            )
            self._placement.revalidate()
            self._append(intent)
            return self._transition(intent, paths)
        finally:
            lease.close()

    @staticmethod
    def _require_no_other_action(
        subject: str, request: ClaimRecoveryRequest, audits: list[RecoveryAudit]
    ) -> None:
        """One open action per claim; a closed action admits only an abandon after `none`."""
        others = [a for a in audits if a.subject_id == subject and a.action_id != request.action_id]
        closed = {a.action_id: a for a in others if isinstance(a, ClaimCompleteAudit)}
        if {a.action_id for a in others} - closed.keys():
            raise _held("other-action-pending")
        for done in closed.values():
            if not (done.transition_kind == "none" and isinstance(request, ClaimAbandon)):
                raise _held("claim-already-recovered")

    # -- reconcile a durable INTENT ---------------------------------------------------

    def _reconcile(self, intent: ClaimIntentAudit, ref: JournalRecordRef) -> RecoveryDisposition:
        paths = self._claims.paths_for(ref)
        observation = intent.observation
        # Whatever transition persisted, completing this INTENT requires the exact original
        # lease: a missing, invalid or replaced lease is a permanent hold, never COMPLETE,
        # and a live holder (including a later claim C2's worker) is retryable contention.
        try:
            lease = self._exact_lease(ref)
        except _DispositionError as refused:
            if refused.disposition.outcome is RecoveryOutcome.HELD:
                raise _held("evidence-lost: lease missing or invalid") from None
            raise
        try:
            if not _lease_is_original(lease, observation):
                raise _held("evidence-lost: lease is not the original")
            if intent.action == "release":
                archive = _archive_path(paths.journal, paths.archive_prefix, intent)
                if os.path.lexists(archive):
                    return self._finish_release(intent, paths, archive)
            else:
                tombstone = _tombstone_path(paths.journal, paths.tombstone_prefix, intent)
                if os.path.lexists(tombstone):
                    return self._finish_abandon(intent, paths, tombstone)
            # No transition persisted. Every piece of pinned evidence must be exactly
            # intact, or the INTENT stays held: missing evidence never proves non-execution.
            if self._tombstoned(ref):
                raise _held("evidence-changed: a tombstone appeared")
            # Read under the held lease: no claimant or worker can change the claim now.
            try:
                live = _read_live_claim(paths.claim)
            except OSError:
                live = None
            if not _matches(observation, paths.claim, live):
                raise _held("evidence-lost: claim changed or unreadable")
            if self._journal.read_exact(ref) is None:
                raise _held("evidence-lost: journal record")
            if intent.action == "release" and not self._is_current(ref):
                # The intended release is moot; the locked comparison above proves nothing
                # changed, so the action closes without a transition.
                return self._complete(intent, "none", _none_digest(observation))
            return self._transition(intent, paths)
        finally:
            lease.close()

    # -- record-scoped abandon --------------------------------------------------------

    def _record_lease(self, ref: JournalRecordRef) -> HeldLease | None:
        """The exact lease if valid and free; `None` if missing or invalid (record scope
        tolerates both); a live holder is retryable contention."""
        probe = self._claims.probe_lease(ref)
        if isinstance(probe, LeaseBusy):
            raise _DispositionError(
                RecoveryDisposition(RecoveryOutcome.RETRYABLE_CONTENTION, "lease-holder-active")
            )
        return probe if isinstance(probe, HeldLease) else None

    def _record_observation(
        self, ref: JournalRecordRef, paths: _ClaimPaths, lease: HeldLease | None
    ) -> RecordObservation:
        observed = _observe_record(paths.claim, ref)
        if isinstance(observed, UnstartedProof | StartedOrUnknown):
            if lease is None:
                # Phase B gap: no typed record observation pins a token claim together
                # with its missing or invalid lease, so it is not relabelled as one.
                raise _held("record-scope-gap: token claim with lease missing or invalid")
            raise _held("claim-scope-required: claim has a token")
        return observed

    def _require_expected_archives(self, paths: _ClaimPaths, audits: list[RecoveryAudit]) -> None:
        """Every archive of this record is a claim release that COMPLETEd; else hold."""
        released = {
            _archive_path(paths.journal, paths.archive_prefix, a).name
            for a in audits
            if isinstance(a, ClaimCompleteAudit) and a.transition_kind == "release_archive"
        }
        present = {
            entry.name
            for entry in os.scandir(paths.journal.parent)
            if entry.name.startswith(paths.archive_prefix)
        }
        if present - released:
            raise _held("unexpected-archive")

    def _begin_record(
        self, request: RecordAbandon, audits: list[RecoveryAudit]
    ) -> RecoveryDisposition:
        ref = request.record_ref
        paths = self._claims.paths_for(ref)
        if self._tombstoned(ref):
            raise _held("record-tombstoned")
        if _pending(audits, "claim") or _pending(audits, "record"):
            raise _held("other-action-pending")
        lease = self._record_lease(ref)
        try:
            observation = self._record_observation(ref, paths, lease)
            self._require_expected_archives(paths, audits)
            if self._journal.read_exact(ref) is None:
                raise _held("record-evidence-lost: journal record does not match")
            intent = RecordIntentAudit(
                schema_version=1,
                scope="record",
                phase="intent",
                action="abandon",
                action_id=request.action_id,
                record_identity=self._identity(ref),
                subject_id=record_subject_id(ref, paths.claim.name),
                operator_uid=request.operator_uid,
                reason_digest=request.reason_digest,
                quiescence_attestation=request.quiescence_attestation,
                observation=observation,
            )
            self._placement.revalidate()
            self._append(intent)
            return self._tombstone(intent, paths)
        finally:
            if lease is not None:
                lease.close()

    def _reconcile_record(
        self, intent: RecordIntentAudit, ref: JournalRecordRef, audits: list[RecoveryAudit]
    ) -> RecoveryDisposition:
        paths = self._claims.paths_for(ref)
        lease = self._record_lease(ref)
        try:
            tombstone = _tombstone_path(paths.journal, paths.tombstone_prefix, intent)
            if os.path.lexists(tombstone):
                return self._finish_abandon(intent, paths, tombstone)
            # No transition persisted: the pinned observation must hold exactly, or the
            # INTENT stays held — changed evidence never becomes a tombstone.
            if self._tombstoned(ref):
                raise _held("evidence-changed: a tombstone appeared")
            if _observe_record(paths.claim, ref) != intent.observation:
                raise _held("evidence-lost: claim observation changed")
            self._require_expected_archives(paths, audits)
            if self._journal.read_exact(ref) is None:
                raise _held("evidence-lost: journal record")
            return self._tombstone(intent, paths)
        finally:
            if lease is not None:
                lease.close()

    # -- transitions (lease held, INTENT durable) -----------------------------------

    def _transition(self, intent: ClaimIntentAudit, paths: _ClaimPaths) -> RecoveryDisposition:
        if intent.action == "release":
            archive = _archive_path(paths.journal, paths.archive_prefix, intent)
            self._placement.revalidate()
            _link_archive(paths.claim, archive)
            _fsync_dir(paths.journal.parent)  # the link is durable before the unlink
            return self._finish_release(intent, paths, archive)
        return self._tombstone(intent, paths)

    def _tombstone(self, intent: IntentAudit, paths: _ClaimPaths) -> RecoveryDisposition:
        tombstone = _tombstone_path(paths.journal, paths.tombstone_prefix, intent)
        self._placement.revalidate()
        _write_new_file(tombstone, _tombstone_bytes(intent))
        return self._finish_abandon(intent, paths, tombstone)

    # The finish steps run on the first pass AND on every retry. Each re-establishes the
    # durability of the persisted transition (file, then directory) before COMPLETE, so
    # a retry after a failed sync never records a transition that may not have persisted.

    def _finish_release(
        self, intent: ClaimIntentAudit, paths: _ClaimPaths, archive: Path
    ) -> RecoveryDisposition:
        observation = intent.observation
        try:
            archived = _read_live_claim(archive)
        except OSError:
            archived = None
        if not _matches(
            observation.model_copy(update={"canonical_claim_path": str(archive)}), archive, archived
        ):
            raise _fault("foreign-archive")
        # A live name still on the pinned inode is the C1 claim itself: finish the move.
        # A different live inode is a later claim C2 and is left alone.
        live = os.lstat(paths.claim) if os.path.lexists(paths.claim) else None
        if live is not None and (live.st_dev, live.st_ino) == (
            observation.claim_st_dev,
            observation.claim_st_ino,
        ):
            self._placement.revalidate()
            os.unlink(paths.claim)
        _sync_file(archive)
        _fsync_dir(paths.journal.parent)
        return self._complete(intent, "release_archive", _release_digest(archive, observation))

    def _finish_abandon(
        self, intent: IntentAudit, paths: _ClaimPaths, tombstone: Path
    ) -> RecoveryDisposition:
        body = _tombstone_bytes(intent)
        try:
            fd = os.open(tombstone, _OPEN_FLAGS)
        except OSError:
            raise _fault("foreign-tombstone") from None
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode) or os.read(fd, len(body) + 1) != body:
                raise _fault("foreign-tombstone")
            _fsync_file(fd)
        finally:
            os.close(fd)
        _fsync_dir(paths.journal.parent)
        kind = _tombstone_kind(intent)
        return self._complete(intent, kind, _tombstone_digest(kind, tombstone, body))

    def _complete(
        self,
        intent: IntentAudit,
        kind: Literal["release_archive", "claim_tombstone", "record_tombstone", "none"],
        transition_digest: str,
    ) -> RecoveryDisposition:
        complete_type = (
            ClaimCompleteAudit if isinstance(intent, ClaimIntentAudit) else RecordCompleteAudit
        )
        complete = complete_type.model_validate(
            {
                **intent.model_dump(),
                "phase": "complete",
                "transition_kind": kind,
                "transition_digest": transition_digest,
            }
        )
        self._append(complete)
        return _completed(complete)

    # -- helpers ----------------------------------------------------------------------

    def _append(self, audit: RecoveryAudit) -> None:
        key = recovery_audit_idempotency_key(audit)
        payload = RecoveryAuditPayload(
            action_id=Identifier(f"recovery:{audit.scope}:{audit.phase}:{audit.action_id}"),
            idempotency_key=key,
            actor=Actor(actor_class=ActorClass.OPERATOR, actor_id=f"uid:{audit.operator_uid}"),
            timestamp=WRITER_OWNED_TIMESTAMP,
            recovery_audit=audit,
        )
        write_key = WriteKey(
            thread_id=Identifier(audit.record_identity.workflow_id),
            step_id=Identifier(f"recovery:{audit.scope}:{audit.phase}"),
            idempotency_key=key,
        )
        try:
            append_recovery_audit_entry(self._ledger, payload, write_key)
        except RecoveryAuditConflictError as exc:
            raise _fault("payload-conflict") from exc
        except RecoveryAuditIntegrityError as exc:
            raise _fault(f"ledger-integrity: {exc}") from exc
