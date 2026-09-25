"""Crash-durable, at-most-once admission for one exact pause-journal record.

This module owns the lease, the sticky ``claimed`` frame and the durable ``started``
transition (``mark_started``). Gateway wiring and audited recovery transitions are separate
consumers.

The store exists only over a journal directory placed under a verified external
state root (``PlacedStateDir``), and re-proves that placement before its first
lock, on every lease probe and at the final barrier before a claim is created. A
placement fault surfaces as ``StateRootPlacementError``, never as a claim refusal
or contention.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
import uuid
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, assert_never, cast

from harness_core import JournalRecordRef
from harness_cp.pause_resume_protocol import (
    _compute_snapshot_hash,  # pyright: ignore[reportPrivateUsage]
)
from harness_cp.pause_resume_protocol_types import PauseSnapshot
from pydantic import ValidationError

from harness_runtime.config.state_placement import PlacedStateDir
from harness_runtime.lifecycle.journal_workflow_pause_store import (
    JournalWorkflowPauseStore,
    cross_process_journal_lock,
    journal_exclusion_is_degraded,
    pause_journal_filename,
)
from harness_runtime.lifecycle.protected_result_store import normalize_tenant_scope

__all__ = [
    "Admission",
    "ClaimBusyError",
    "ClaimRefusedError",
    "HeldClaim",
    "HeldLease",
    "InvalidClaim",
    "LeaseBusy",
    "LeaseCapability",
    "LeaseInvalid",
    "LeaseMissing",
    "LeaseProbe",
    "ParentCarriedAdmission",
    "ResumeClaimStore",
    "RootLatestAdmission",
    "StartedClaim",
    "StartedOrUnknown",
    "UnstartedProof",
    "parse_claim",
    "started_frame",
]

_OPEN_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_OPEN_FLAGS_NO_ACCESS = getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
_CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
)


class ClaimBusyError(Exception):
    """The live lease holder may finish; no claim was created by this attempt."""


class ClaimRefusedError(Exception):
    """The exact record is ineligible or the durable evidence is not trustworthy."""


@dataclass(frozen=True)
class UnstartedProof:
    """A complete claimed frame with no later bytes; recovery must add its own proof."""

    token: str
    record_ref: JournalRecordRef


@dataclass(frozen=True)
class StartedOrUnknown:
    """Execution may have begun; ordinary release is forbidden."""

    token: str
    phase: str
    record_ref: JournalRecordRef


@dataclass(frozen=True)
class InvalidClaim:
    """Unparseable or partial evidence; never infer non-execution."""

    reason: str


def _object_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate claim key")
        result[key] = value
    return result


def _frame(raw: bytes) -> dict[str, Any]:
    if not raw.endswith(b"\n"):
        raise ValueError("incomplete frame")
    raw_obj = cast(object, json.loads(raw[:-1], object_pairs_hook=_object_no_duplicates))
    if not isinstance(raw_obj, dict):
        raise ValueError("invalid frame object")
    obj = cast(dict[str, Any], raw_obj)
    if set(obj) != {"version", "phase", "token", "record_ref"}:
        raise ValueError("invalid frame keys")
    if type(obj["version"]) is not int or obj["version"] != 1:
        raise ValueError("invalid frame version")
    if not isinstance(obj["phase"], str) or not obj["phase"]:
        raise ValueError("invalid phase")
    if not isinstance(obj["token"], str) or len(obj["token"]) != 32:
        raise ValueError("invalid claim token")
    try:
        uuid.UUID(hex=obj["token"])
        obj["record_ref"] = JournalRecordRef.model_validate(obj["record_ref"], strict=True)
    except (ValueError, ValidationError) as exc:
        raise ValueError("invalid frame identity") from exc
    return obj


def _encode_frame(phase: str, token: str, ref: JournalRecordRef) -> bytes:
    return (
        json.dumps(
            {
                "version": 1,
                "phase": phase,
                "token": token,
                "record_ref": ref.model_dump(mode="json"),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def parse_claim(
    raw: bytes, ref: JournalRecordRef
) -> UnstartedProof | StartedOrUnknown | InvalidClaim:
    """Parse complete v1 frames; any ambiguity remains sticky.

    [LAW:parse-dont-validate] The returned variant carries the only authorized
    conclusion about the bytes; a caller cannot treat malformed bytes as unstarted.
    """
    try:
        lines = raw.splitlines(keepends=True)
        if not lines or len(lines) > 2:
            raise ValueError("frame count")
        first = _frame(lines[0])
        if first["phase"] != "claimed" or first["record_ref"] != ref:
            raise ValueError("claimed identity")
        if len(lines) == 1:
            return UnstartedProof(first["token"], ref)
        second = _frame(lines[1])
        if second["token"] != first["token"] or second["record_ref"] != ref:
            raise ValueError("phase identity")
        if second["phase"] == "claimed":
            raise ValueError("duplicate claimed frame")
        return StartedOrUnknown(first["token"], second["phase"], ref)
    except (UnicodeDecodeError, ValueError, TypeError):
        return InvalidClaim("invalid-or-partial-frame")


class LeaseProbe(StrEnum):
    BUSY = "busy"
    MISSING = "missing"
    INVALID = "invalid"


@dataclass(frozen=True)
class LeaseBusy:
    status: LeaseProbe = LeaseProbe.BUSY


@dataclass(frozen=True)
class LeaseMissing:
    status: LeaseProbe = LeaseProbe.MISSING


@dataclass(frozen=True)
class LeaseInvalid:
    status: LeaseProbe = LeaseProbe.INVALID


_MINT = object()


class LeaseCapability:
    """The store-issued, still-live hold on one lease flock, from `claim` to the worker's close.

    [LAW:types-are-the-program] Ownership is provenance, not a lock taken on demand: an
    instance can only be minted by `ResumeClaimStore.claim`, which hands it the fd that took
    the flock, and only `close` releases that fd. A validator that flock()s a presented fd
    would turn any unlocked descriptor into an owner the moment the real holder lets go, so
    admission asks whether the capability is one the store issued and that is still open.

    Trust assumption: `_MINT` is module-private, so this stops any caller working through the
    public API, including a `HeldClaim` rebuilt from the readable token and a fresh fd. It is
    not a hostile same-process boundary; code that reaches into this module's privates or
    closes the fd behind the capability's back is outside the model. Across processes the
    only way to hold the flock is to inherit the fd, which is the worker handoff itself.
    """

    __slots__ = ("_fd",)

    def __init__(self, mint: object, fd: int) -> None:
        if mint is not _MINT:
            raise TypeError("a lease capability is issued only by ResumeClaimStore.claim")
        self._fd = fd

    @property
    def fd(self) -> int:
        return self._fd

    def close(self) -> None:
        if self._fd >= 0:
            os.close(self._fd)
            self._fd = -1


@dataclass
class HeldClaim:
    """The lease capability stays live until the actual executing worker closes it."""

    token: str
    record_ref: JournalRecordRef
    lease: LeaseCapability

    @property
    def lease_fd(self) -> int:
        return self.lease.fd

    def close(self) -> None:
        self.lease.close()

    def __enter__(self) -> HeldClaim:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


@dataclass
class HeldLease:
    fd: int
    token: str
    record_ref: JournalRecordRef

    def close(self) -> None:
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


@dataclass
class StartedClaim:
    """A claim whose ``started`` frame is durable; the only value that may lead to a body.

    [LAW:types-are-the-program] Produced solely by `ResumeClaimStore.mark_started`. It wraps
    (aliases) the SAME `HeldClaim`, so the lease fd stays with the caller: closing either
    object closes the one descriptor, once.
    """

    claim: HeldClaim

    @property
    def token(self) -> str:
        return self.claim.token

    @property
    def record_ref(self) -> JournalRecordRef:
        return self.claim.record_ref

    @property
    def lease_fd(self) -> int:
        return self.claim.lease_fd

    def close(self) -> None:
        self.claim.close()

    def __enter__(self) -> StartedClaim:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


@dataclass(frozen=True)
class RootLatestAdmission:
    """Direct root input: the ref must name the journal's CURRENT latest record."""


@dataclass(frozen=True)
class ParentCarriedAdmission:
    """A child ref admitted through its live, STARTED parent claim.

    The child may be positional (not the journal latest) only because its parent's own
    hash-covered snapshot carries this exact child exactly once.
    """

    parent: StartedClaim


Admission = RootLatestAdmission | ParentCarriedAdmission
"""How a claim's recency is proven.

The `claim` default is the conservative root-latest form (the pre-5a behavior, kept so the
Task 3b/6 callers are untouched); the child form must be requested explicitly."""
_ROOT_LATEST = RootLatestAdmission()


def started_frame(claim: HeldClaim) -> bytes:
    """The Task 5 writer's exact v1 phase bytes; this function does not write them."""
    return _encode_frame("started", claim.token, claim.record_ref)


class _Paths:
    def __init__(self, journal: Path, ref: JournalRecordRef) -> None:
        digest = hashlib.sha256(
            f"resume-claim:v1:{ref.record_count}:{ref.latest_digest}".encode("ascii")
        ).hexdigest()
        self.journal = journal
        self.claim = journal.with_name(f"{journal.name}.resume-claim-{digest}")
        self.lease = journal.with_name(f"{journal.name}.resume-lease-{digest}")
        self.temp_prefix = self.lease.name + ".tmp-"
        self.tombstone_prefix = f"{journal.name}.resume-tombstone-{digest}-"
        self.archive_prefix = f"{journal.name}.resume-archive-{digest}-"


def _fsync_dir(path: Path) -> None:
    # [LAW:no-silent-failure] Claim durability requires the directory fsync to succeed.
    fd = os.open(
        path,
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise OSError("short durable claim write")
        view = view[written:]


def _read_fd(fd: int) -> bytes:
    os.lseek(fd, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while part := os.read(fd, 65536):
        chunks.append(part)
        if sum(map(len, chunks)) > 65536:
            raise ValueError("oversized lease")
    return b"".join(chunks)


def _snapshot_hash_of(snapshot: PauseSnapshot) -> str:
    """CP's own canonical hash over a snapshot's fields, for the carrier-coverage check."""
    return _compute_snapshot_hash(
        workflow_id=snapshot.workflow_id,
        run_id=snapshot.run_id,
        step_index=snapshot.step_index,
        state_summary=snapshot.state_summary,
        fan_out_resume=snapshot.fan_out_resume,
        peer_fan_out_resume=snapshot.peer_fan_out_resume,
        handoff_resume=snapshot.handoff_resume,
        evaluator_optimizer_resume=snapshot.evaluator_optimizer_resume,
        effect_fence_resume=snapshot.effect_fence_resume,
        orchestrator_effect_fence_resume=snapshot.orchestrator_effect_fence_resume,
        hitl_gate_config_hash=snapshot.hitl_gate_config_hash,
    )


def _read_regular_no_follow(path: Path) -> bytes:
    """Read a small regular single-link file without following a final symlink."""
    fd = os.open(path, _OPEN_FLAGS)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise ValueError("invalid claim inode")
        return _read_fd(fd)
    finally:
        os.close(fd)


class ResumeClaimStore:
    """Lease publication and one-shot claim admission for an exact journal ref."""

    def __init__(self, *, placement: PlacedStateDir, tenant_id: str | None) -> None:
        self._placement = placement
        self._journal = JournalWorkflowPauseStore(journal_dir=placement.path, tenant_id=tenant_id)
        self._journal_dir = placement.path
        self._tenant = normalize_tenant_scope(tenant_id)

    def paths_for(self, ref: JournalRecordRef) -> _Paths:
        if ref.tenant != self._tenant:
            raise ClaimRefusedError("wrong tenant scope")
        return _Paths(self._journal_dir / pause_journal_filename(ref.tenant, ref.workflow_id), ref)

    @staticmethod
    def _tombstoned(paths: _Paths) -> bool:
        return any(
            entry.name.startswith(paths.tombstone_prefix)
            for entry in os.scandir(paths.journal.parent)
        )

    @staticmethod
    def _lease_bytes(ref: JournalRecordRef, token: str) -> bytes:
        return _encode_frame("lease", token, ref)

    @staticmethod
    def _valid_lease(fd: int, ref: JournalRecordRef) -> str:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
            raise ValueError("invalid lease inode")
        data = _read_fd(fd)
        frame = _frame(data)
        if frame["phase"] != "lease" or frame["record_ref"] != ref:
            raise ValueError("invalid lease identity")
        # [LAW:one-source-of-truth] The encoded frame is the sole accepted lease evidence.
        if data != ResumeClaimStore._lease_bytes(ref, frame["token"]):
            raise ValueError("noncanonical lease bytes")
        return frame["token"]

    @staticmethod
    def _same_inode(fd: int, path: Path) -> bool:
        own = os.fstat(fd)
        current = os.stat(path, follow_symlinks=False)
        return (own.st_dev, own.st_ino) == (current.st_dev, current.st_ino)

    def _require_lease_live(self, lease: object, path: Path) -> None:
        """Admit only a store-issued capability that is still open on the canonical lease.

        The single flock attempt is on a FRESH open and can only refuse: if it acquires, the
        capability's lock is gone (closed or released behind its back) and the transient lock
        drops on close. Nothing here ever locks the presented fd, so no unlocked descriptor
        can become a holder by winning a lock that was just freed.
        """
        import fcntl  # POSIX-only; the degraded platform refuses before any caller gets here.

        # [LAW:parse-dont-validate] A forged HeldClaim carries a stand-in, never a capability.
        if not isinstance(lease, LeaseCapability) or lease.fd < 0:
            raise ValueError("lease is not a live store-issued capability")
        if not self._same_inode(lease.fd, path):
            raise ValueError("lease is not the canonical live lease")
        probe = os.open(path, _OPEN_FLAGS)
        try:
            try:
                fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno not in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EACCES):
                    raise
            else:
                raise ValueError("lease lock is not held by anyone")
        finally:
            os.close(probe)  # also drops a transient lock taken by the probe

    def _publish_lease(self, paths: _Paths, ref: JournalRecordRef) -> None:
        """Call only under the journal lock; never replace the canonical inode."""
        token = uuid.uuid4().hex
        temp = paths.journal.with_name(paths.temp_prefix + uuid.uuid4().hex)
        fd = os.open(temp, _CREATE_FLAGS, 0o600)
        try:
            _write_all(fd, self._lease_bytes(ref, token))
            os.fsync(fd)
            try:
                os.link(temp, paths.lease, follow_symlinks=False)
            except FileExistsError:
                pass
            else:
                _fsync_dir(paths.journal.parent)
        finally:
            os.close(fd)
            # A failed write leaves only an untrusted temp. Canonical lease is never touched.
            os.unlink(temp)
            _fsync_dir(paths.journal.parent)

    def _prepare_lease(self, paths: _Paths, ref: JournalRecordRef) -> None:
        try:
            fd = os.open(paths.lease, _OPEN_FLAGS)
        except FileNotFoundError:
            self._publish_lease(paths, ref)
            try:
                fd = os.open(paths.lease, _OPEN_FLAGS)
            except OSError as exc:
                raise ClaimRefusedError("invalid canonical lease") from exc
        except OSError as exc:
            raise ClaimRefusedError("invalid canonical lease") from exc
        try:
            own = os.fstat(fd)
            # [LAW:single-enforcer] Only a temp with the canonical inode is cleanup-eligible.
            for entry in os.scandir(paths.journal.parent):
                if not entry.name.startswith(paths.temp_prefix):
                    continue
                suffix = entry.name[len(paths.temp_prefix) :]
                if len(suffix) != 32 or any(c not in "0123456789abcdef" for c in suffix):
                    continue
                st = entry.stat(follow_symlinks=False)
                if (st.st_dev, st.st_ino) == (own.st_dev, own.st_ino):
                    os.unlink(entry.path)
                    _fsync_dir(paths.journal.parent)
            if not self._same_inode(fd, paths.lease):
                raise ClaimRefusedError("lease inode changed")
            self._valid_lease(fd, ref)
            _fsync_dir(paths.journal.parent)
        except (OSError, ValueError) as exc:
            raise ClaimRefusedError(f"invalid canonical lease: {exc}") from exc
        finally:
            os.close(fd)

    def probe_lease(
        self, ref: JournalRecordRef
    ) -> HeldLease | LeaseBusy | LeaseMissing | LeaseInvalid:
        """Noncreating, nonblocking shared probe; a successful caller owns the fd."""
        paths = self.paths_for(ref)
        # A replaced root is a placement fault, not a missing or invalid lease.
        self._placement.revalidate()
        if (
            journal_exclusion_is_degraded()
            or not hasattr(os, "O_NOFOLLOW")
            or not hasattr(os, "O_CLOEXEC")
        ):
            return LeaseInvalid()
        import fcntl  # POSIX-only; the degraded platform refuses above.

        try:
            fd = os.open(paths.lease, _OPEN_FLAGS)
        except FileNotFoundError:
            return LeaseMissing()
        except OSError:
            return LeaseInvalid()
        acquired = False
        try:
            # [LAW:no-ambient-temporal-coupling] The lock is taken BEFORE the bytes are
            # trusted: a live holder can leave damaged bytes, and only the lock says "live".
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EACCES):
                    return LeaseBusy()
                raise
            token = self._valid_lease(fd, ref)
            if not self._same_inode(fd, paths.lease):
                raise ValueError("lease inode changed")
            acquired = True
            return HeldLease(fd, token, ref)
        except (OSError, ValueError):
            return LeaseInvalid()
        finally:
            if not acquired:
                os.close(fd)

    def _require_current_exact(self, ref: JournalRecordRef) -> None:
        """Check latest identity and exact validity while the caller holds journal lock."""
        # [LAW:single-enforcer] Claim admission alone requires a current record;
        # positional read_exact remains available to other journal consumers.
        latest = self._journal.read_latest_attributed(ref.workflow_id)
        if (
            latest.record_count != ref.record_count
            or latest.latest_record_digest != ref.latest_digest
        ):
            raise ClaimRefusedError("stale or missing journal record")
        if self._journal.read_exact(ref) is None:
            raise ClaimRefusedError("invalid exact journal record")

    def _require_parent_carried(self, ref: JournalRecordRef, parent: StartedClaim) -> None:
        """Admit a positional child ref only through a live STARTED parent that carries it once."""
        # [LAW:single-enforcer] The one place child recency is decided; every fault refuses.
        if parent.record_ref.tenant != ref.tenant:
            raise ClaimRefusedError("parent claim is in another tenant scope")
        parent_paths = self.paths_for(parent.record_ref)
        try:
            self._require_lease_live(parent.claim.lease, parent_paths.lease)
            self._valid_lease(parent.lease_fd, parent.record_ref)
            state = parse_claim(_read_regular_no_follow(parent_paths.claim), parent.record_ref)
        except (OSError, ValueError) as exc:
            raise ClaimRefusedError("parent claim evidence is not trustworthy") from exc
        if not (
            isinstance(state, StartedOrUnknown)
            and state.phase == "started"
            and state.token == parent.token
        ):
            raise ClaimRefusedError("parent claim is not started")
        parent_record = self._journal.read_exact(parent.record_ref)
        child_record = self._journal.read_exact(ref)
        if parent_record is None or child_record is None:
            raise ClaimRefusedError("parent or child journal record is not exact")
        if parent_record.depth is None or child_record.depth != parent_record.depth + 1:
            raise ClaimRefusedError("child depth is not the parent's depth plus one")
        parent_snapshot = parent_record.snapshot
        if _snapshot_hash_of(parent_snapshot) != parent_snapshot.snapshot_hash:
            raise ClaimRefusedError("parent snapshot hash does not cover its carriers")
        carriers = [
            *(
                parent_snapshot.fan_out_resume.paused_child_branches
                if parent_snapshot.fan_out_resume is not None
                else ()
            ),
            *(
                parent_snapshot.peer_fan_out_resume.paused_child_branches
                if parent_snapshot.peer_fan_out_resume is not None
                else ()
            ),
        ]
        # This base predates the Task 4b `child_record_ref` carrier field, so the carrier is
        # matched by the FULL child snapshot equalling the exact journal record's snapshot
        # (workflow, run, hash and content). Once 4b is integrated this must tighten to
        # ref equality so two byte-identical records at different positions cannot both match.
        matching = [c for c in carriers if c.child_snapshot == child_record.snapshot]
        if len(matching) != 1:
            raise ClaimRefusedError("parent does not carry this child exactly once")

    def _require_admitted(self, ref: JournalRecordRef, admission: Admission) -> None:
        match admission:
            case RootLatestAdmission():
                self._require_current_exact(ref)
            case ParentCarriedAdmission(parent):
                self._require_parent_carried(ref, parent)
            case _ as unreachable:
                assert_never(unreachable)

    def claim(
        self,
        ref: JournalRecordRef,
        admission: Admission = _ROOT_LATEST,
        *,
        deadline_seconds: float | None = None,
    ) -> HeldClaim:
        """Return a held sticky claim; busy is retryable, all evidence faults refuse.

        [LAW:no-ambient-temporal-coupling] Publication holds only journal;
        admission holds lease then journal. The reverse direction uses NB probe.
        """
        if (
            journal_exclusion_is_degraded()
            or not hasattr(os, "O_NOFOLLOW")
            or not hasattr(os, "O_CLOEXEC")
        ):
            raise ClaimRefusedError("journal exclusion or safe open flags are unavailable")
        paths = self.paths_for(ref)
        # The journal lock creates its lock file, so placement is proved before it.
        self._placement.revalidate()
        with cross_process_journal_lock(paths.journal, deadline_seconds=deadline_seconds):
            self._require_admitted(ref, admission)
            if self._tombstoned(paths) or os.path.lexists(paths.claim):
                raise ClaimRefusedError("record is ineligible")
            self._prepare_lease(paths, ref)
        probe = self.probe_lease(ref)
        if isinstance(probe, LeaseBusy):
            raise ClaimBusyError("lease holder is active")
        if not isinstance(probe, HeldLease):
            raise ClaimRefusedError("lease is missing or invalid")
        try:
            with cross_process_journal_lock(paths.journal, deadline_seconds=deadline_seconds):
                # [LAW:no-ambient-temporal-coupling] Recency is checked under the
                # same journal lock as O_EXCL creation, after taking the lease lock.
                self._require_admitted(ref, admission)
                if (
                    self._tombstoned(paths)
                    or os.path.lexists(paths.claim)
                    or not self._same_inode(probe.fd, paths.lease)
                    or self._valid_lease(probe.fd, ref) != probe.token
                ):
                    raise ClaimRefusedError("record changed before admission")
                # The last barrier before O_EXCL: a root swapped between the two lock
                # sections must not receive the claim (the published lease stays).
                self._placement.revalidate()
                token = uuid.uuid4().hex
                fd = os.open(paths.claim, _CREATE_FLAGS, 0o600)
                try:
                    _write_all(fd, _encode_frame("claimed", token, ref))
                    os.fsync(fd)
                finally:
                    os.close(fd)
                _fsync_dir(paths.journal.parent)
                return HeldClaim(token, ref, LeaseCapability(_MINT, probe.fd))
        except BaseException:
            probe.close()
            raise

    def mark_started(
        self, held: HeldClaim, *, deadline_seconds: float | None = None
    ) -> StartedClaim:
        """Durably record ``started`` for a held claim; only the result may lead to a body.

        Under lease then journal lock it revalidates the placed root, proves the live
        lease fd still names the canonical lease inode, requires the claim file to be an
        exact `UnstartedProof` for THIS token and ref, appends the v1 ``started`` frame
        (no symlink followed) and fsyncs before returning. Missing, closed, changed,
        already-started, tampered or ambiguous evidence refuses (`ClaimRefusedError`,
        never the retryable busy). The lease stays with the caller on every outcome.

        [LAW:no-silent-failure] A failed write/fsync raises and leaves whatever bytes reached
        the file; they parse as started or invalid, never as an unstarted claim.
        """
        if (
            journal_exclusion_is_degraded()
            or not hasattr(os, "O_NOFOLLOW")
            or not hasattr(os, "O_CLOEXEC")
        ):
            raise ClaimRefusedError("journal exclusion or safe open flags are unavailable")
        paths = self.paths_for(held.record_ref)
        self._placement.revalidate()
        with cross_process_journal_lock(paths.journal, deadline_seconds=deadline_seconds):
            # The last barrier before the append: a swapped root must not receive it.
            self._placement.revalidate()
            try:
                # The lease frame carries the LEASE token (distinct from the claim token,
                # which the claim file proves below): the fd must name the canonical inode
                # and hold a canonical lease frame for this exact ref.
                self._require_lease_live(held.lease, paths.lease)
                self._valid_lease(held.lease_fd, held.record_ref)
                fd = os.open(paths.claim, os.O_RDWR | os.O_APPEND | _OPEN_FLAGS_NO_ACCESS)
            except (OSError, ValueError) as exc:
                raise ClaimRefusedError(f"claim evidence unavailable: {exc}") from exc
            try:
                st = os.fstat(fd)
                if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                    raise ClaimRefusedError("invalid claim inode")
                state = parse_claim(_read_fd(fd), held.record_ref)
                if not (
                    isinstance(state, UnstartedProof)
                    and state.token == held.token
                    and state.record_ref == held.record_ref
                ):
                    raise ClaimRefusedError("claim is not an exact unstarted proof")
                if self._tombstoned(paths):
                    raise ClaimRefusedError("record is ineligible")
                try:
                    _write_all(fd, started_frame(held))
                    os.fsync(fd)
                except OSError as exc:
                    raise ClaimRefusedError("started frame was not made durable") from exc
            finally:
                os.close(fd)
        return StartedClaim(held)
