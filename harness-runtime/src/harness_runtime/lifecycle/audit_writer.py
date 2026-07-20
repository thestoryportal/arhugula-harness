"""Audit-ledger writer instantiation — stage 4 OD (U-RT-32, closes L6).

Per `Spec_Harness_Runtime_v1.md` v1.1 §6 (C-RT-04 `audit_writer` field) + §7
(C-RT-07 stage 4 invariants) + the cross-axis edge at §700:
`ctx.audit_writer.append(tenant_id, audit_entry)` wraps an
`AuditLedgerEntry` (OD-spec'd at `harness_od.audit_ledger_types`) into a
`StateLedgerEntry` (IS C-IS-10 §10.1) so the OD audit-ledger reaches the IS
hash-chain durability substrate and `chain_verification` passes per
C-IS-06 §6.4.

**Wrap design.** The `AuditLedgerEntry` arrives pre-signed — the OD emission
site (U-OD-30) runs `sign_audit_entry` before handing the entry to the
runtime writer; this module is pure persistence. The wrap encodes:

- `EntryPayload.action_id = "audit:<tag>:<entry_hash>"` — tag is `tenant_id`
  or `_single`; entry_hash is the OD-computed `AuditLedgerEntry.entry_hash`.
- `EntryPayload.idempotency_key = "audit:<tag>:<entry_hash>"` — identical to
  action_id; the entry_hash already uniquely identifies the audit entry,
  but the tenant prefix scopes idempotency per-tenant (so two tenants can
  in principle reference the same OD entry without dedup-conflating them).
- `EntryPayload.actor` = the runtime's bound IS actor (from
  `LedgerWriter.actor` — committed at materialize_state_ledger time).
- `EntryPayload.timestamp` = `time_source()` (default `datetime.now(UTC)`).
- `WriteKey.thread_id = "audit:<tag>"`; `step_id = action_id`;
  `idempotency_key = action_id`.

**Cross-tenant separation discipline (C-OD-21 §21.1).** The OD spec commits
per-tenant TRACE separation (OTLP-collector-routing / backend-partition),
not per-tenant audit-ledger STORAGE. The audit ledger persists all tenants'
entries into one IS chain; tenant separation at the READ surface is
enforced by `read_for_tenant(tenant_id)`, which filters by the
`audit:<tag>:` prefix. The `cross_tenant_aggregation_forbidden=True` rule
at §21.1's `PerTenantSeparation` model holds at the reader API surface —
tenant A's reader does not return tenant B's entries.

**Signing is deferred (not at writer).** `sign_audit_entry` (C-OD-21 §21.2)
runs at the OD emission site and produces the `AuditSignatureAttributes`
that already live on the `AuditLedgerEntry` this module receives. The
writer does not re-sign and does not consult signing config; the live
signing backend is composition-root-injected at the emission sites per OD
spec v1.33 §21.2.1 (`B-47`), never here.

**Full-entry sidecar (`B-47` item (e)).** The IS wrap above persists only
the `audit:<tag>:<entry_hash>` REFERENCE (the six-field C-IS-05 shape is
ADR-F2-committed and carries no content field), so the writer additionally
lands every entry — payload + signature_attrs + entry_hash — as one JSON
line in an `audit-entries.jsonl` sidecar beside the IS ledger file. The
chain's embedded `entry_hash` binds each sidecar row to exactly one
tamper-evident chain entry; writes are sidecar-first + membership-checked
(a crash between the two writes leaves at worst a detectable surplus row,
never a lost signature; replays never duplicate). Reads rehydrate via
`read_full_entries_for_tenant` — the surface a signature verifier needs
after restart.

**Verification.** `verify_hash_chain_integrity` (C-OD-21 §21.2) verifies
the OD audit-chain links via `AuditPayload.prior_entry_hash` / `entry_hash`.
The IS `verify_chain` (C-IS-06 §6.4) verifies the underlying IS chain.
Both pass independently; the writer composes them by ensuring every audit
entry round-trips through the IS chain via `append_ledger_entry`.

**Module convention.** One module per unit. `materialize_audit_writer_stage`
composer returns a frozen `AuditWriterStage` dataclass with `slots=True`.
Typed `AuditWriterBindError` for bootstrap-time failures. Mirrors the L6
stage shape established at U-RT-27..31.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import stat
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from harness_is.cross_process_ledger_lock import (
    cross_process_read_lock,
    cross_process_write_lock,
)
from harness_is.state_ledger_entry_schema import Identifier, StateLedgerEntry, Timestamp
from harness_is.state_ledger_write import (
    EntryPayload,
    NonMonotonicTimestampError,
    WriteKey,
    WriteResult,
    read_ledger,
)
from harness_od.audit_ledger_types import AuditLedgerEntry, compute_entry_hash
from harness_od.multi_tenant_trace_separation_and_audit_ledger import sidecar_tag
from harness_od.per_family_audit_verification import REDACTION_TOKEN_NAMESPACE_PREFIX

from harness_runtime.lifecycle.state_ledger import LedgerWriter
from harness_runtime.types import RuntimeConfig


class AuditWriterBindError(Exception):
    """Raised when audit-writer stage materialization fails."""


class _SidecarMembershipIndex:
    """Mutable holder for the incremental sidecar membership index.

    `digests` — for every `(tenant_tag, entry_hash)` seen up to `offset`, the
    SHA-256 over the canonically re-serialized FULL signed entry (payload +
    signature_attrs + entry_hash — codex round-19: identity keyed on the
    content hash alone let a row with mutated `signature_attrs` silently
    satisfy membership for the legitimate entry). `offset` — the byte
    position up to which the sidecar has been folded in. A plain class (not
    a dataclass field pair) so the frozen writer can mutate it in place.
    """

    __slots__ = (
        "digests",
        "inode",
        "legacy_exempt",
        "mtime_ns",
        "offset",
        "prefix_hash",
        "redaction_tails",
        "unsnapshotted",
    )

    def __init__(self) -> None:
        self.digests: dict[tuple[str, str], str] = {}
        self.legacy_exempt: set[tuple[str, str]] = set()
        # Per-tenant-tag durable tail of the redaction-token family (B-50
        # item (i), codex round-1): maintained transactionally during folds
        # and our own appends so the token map's per-append tail lookup is
        # O(delta), not an O(history) full rehydration. Legacy-baselined
        # ledgers have no recoverable tails (full entries were dropped
        # pre-sidecar) — absent means the family restarts from genesis.
        self.redaction_tails: dict[str, str] = {}
        self.offset: int = 0
        self.inode: int = -1
        self.mtime_ns: int = -1
        # Index mutations (rows folded or appended) since the on-disk
        # snapshot was last written — the B-50 item (g) write cadence.
        self.unsnapshotted: int = 0
        # Running SHA-256 over the folded sidecar bytes [0:offset] (codex
        # round-5 P1 on the item-(g) landing): persisted in the snapshot as
        # `prefix_digest` and re-derived by a raw-byte streaming read at
        # adoption, binding the cache to the AUTHORITATIVE bytes it vouches
        # for — silent bit rot in the folded prefix (size/inode/mtime
        # intact) would otherwise pass adoption's metadata checks and let a
        # legitimate replay NOOP against a digest computed from the
        # pre-rot row. Maintained incrementally (O(1) amortized per
        # append), so snapshot writes never re-read history.
        self.prefix_hash = hashlib.sha256()


def _has_redaction_namespace_keys(entry: AuditLedgerEntry) -> bool:
    """Redaction-family discriminator — namespace keys, never entry_core
    prefix (PR B1 codex round-39; shared constant from the B-49 verifier)."""
    return any(
        key.startswith(REDACTION_TOKEN_NAMESPACE_PREFIX)
        for key in entry.payload.audit_namespace_attrs
    )


def _full_entry_digest(entry: AuditLedgerEntry) -> str:
    """Canonical digest over the COMPLETE signed entry (round-19 identity)."""
    return hashlib.sha256(entry.model_dump_json().encode("utf-8")).hexdigest()


def _snapshot_body_digest(body: dict[str, Any]) -> str:
    """Integrity self-digest over a snapshot body (canonical JSON).

    Catches CORRUPTION (torn write, bit rot), not tampering — an adversary
    with filesystem write access can recompute it. That tier is the same
    adversarial-filesystem tier as a forged `legacy_baseline` row or a
    mutate-and-restore-mtime edit (codex round-46 posture) — dispositioned
    to the B-47 read-time verifier arc, and bounded here by the fact that
    the snapshot is a DERIVED CACHE: discarding it on any anomaly always
    degrades to the correct full refold, never to wrong state.
    """
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


_SIDECAR_LOCKS: dict[str, threading.Lock] = {}
_SIDECAR_LOCKS_GUARD = threading.Lock()

_APPEND_LOCKS: dict[str, threading.Lock] = {}
_APPEND_LOCKS_GUARD = threading.Lock()


def _append_lock_for(path: Path) -> threading.Lock:
    """One in-process lock per ledger path serializing the WHOLE append.

    Codex round-4 P1 (PR B2a): with audit composition on the offload pool
    plus the loop-thread paths, two appenders could sample timestamps in
    one order and commit in the other — the later timestamp persisting
    first left the earlier append raising NonMonotonicTimestampError AFTER
    its sidecar row was written (an unanchored row). Timestamp sampling and
    the sidecar+IS commits now happen inside ONE ordered critical section.
    (Cross-process timestamp ordering remains the pre-existing B-40-tier
    residual — the cross-process locks serialize the file writes, not the
    sampling.)
    """
    key = str(path.resolve())
    with _APPEND_LOCKS_GUARD:
        lock = _APPEND_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _APPEND_LOCKS[key] = lock
        return lock


@contextlib.contextmanager
def _combined_sidecar_read_locks(thread_lock: threading.Lock, sidecar_path: Path) -> Any:
    """Thread + cross-process read locks as one context (reader lock shape)."""
    with thread_lock, cross_process_read_lock(sidecar_path):
        yield


def _sidecar_lock_for(path: Path) -> threading.Lock:
    """One in-process lock per resolved sidecar path (rounds 4 + 25)."""
    key = str(path.resolve())
    with _SIDECAR_LOCKS_GUARD:
        lock = _SIDECAR_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _SIDECAR_LOCKS[key] = lock
        return lock


@dataclass(frozen=True, slots=True)
class RuntimeAuditLedgerWriter:
    """Runtime multi-tenant audit-ledger writer (C-RT-04 `audit_writer`).

    Wraps the IS `LedgerWriter` (U-RT-12). Persists OD `AuditLedgerEntry`
    instances into the underlying IS hash-chained JSONL ledger; provides a
    tenant-scoped reader surface for C-OD-21 §21.1 cross-tenant separation.
    """

    ledger_writer: LedgerWriter
    """IS state-ledger writer (U-RT-12) — durable substrate for audit entries."""

    time_source: Callable[[], Timestamp]
    """Timestamp injection point (test determinism). Default: `datetime.now(UTC)`."""

    @property
    def _sidecar_thread_lock(self) -> threading.Lock:
        """In-process half of the sidecar critical section, SHARED across all
        writer instances targeting the same sidecar path (out-of-family Codex
        rounds 4 + 25): `cross_process_write_lock` degrades to a no-op on
        Windows and its contract says callers retain their own
        `threading.Lock` — a per-INSTANCE lock left two writers over one
        sidecar unserialized in the same process. Keyed on the resolved path
        via a module-level registry (the IS writer's module-level-lock
        pattern)."""
        return _sidecar_lock_for(self._sidecar_path)

    _sidecar_index: _SidecarMembershipIndex = field(
        default_factory=lambda: _SidecarMembershipIndex(), init=False
    )
    """Incremental membership index over the sidecar (codex round-12 P2 —
    kills the O(N²) full-scan-per-append on the span-finalization hot path).
    Mutated only under `_sidecar_thread_lock` + the cross-process write lock."""

    _SINGLE_TENANT_TAG: ClassVar[str] = "_single"
    _ACTION_ID_PREFIX: ClassVar[str] = "audit"

    _SNAPSHOT_FILENAME: ClassVar[str] = "audit-entries.index-snapshot.json"
    """B-50 item (g) — the disk-backed membership-index snapshot.

    A DERIVED CACHE of the fold state (`_SidecarMembershipIndex`) written
    beside the sidecar so a fresh process adopts it and folds only the
    delta, instead of re-parsing + re-validating the full O(history)
    sidecar at every cold start. The sidecar remains the single source of
    truth: adoption discards the snapshot on ANY anomaly (self-digest
    mismatch, inode change, offset past the current size, same-size mtime
    drift) and falls back to the correct full refold — a bad snapshot can
    cost time, never correctness. Chosen over a second storage engine
    (stdlib `sqlite3`) to stay inside the ADR-D5 v1.4 JSONL-canonical
    posture: one authority, one derived JSON cache."""

    _SNAPSHOT_EVERY_APPENDS: ClassVar[int] = 64
    """Write-cadence FLOOR: persist the snapshot once at least this many
    index mutations (own appends + folded rows) have accumulated — but see
    `_SNAPSHOT_GROWTH_DIVISOR`: for a large index the threshold is
    proportional to the index size, so each rewrite is amortized against
    real growth. A fixed cadence alone rewrote the O(N) snapshot every 64
    appends — Θ(N²/64) cumulative checkpoint bytes on the audit hot path
    (codex round-1 P1 on this landing). The snapshot is also written
    immediately after any from-zero fold or legacy adoption so the
    expensive refold is paid at most once."""

    _SNAPSHOT_GROWTH_DIVISOR: ClassVar[int] = 8
    """Proportional half of the cadence: rewrite only once the index has
    grown by at least `len(digests) / 8` mutations since the last snapshot.
    Geometric checkpointing — total snapshot bytes over a ledger's life are
    O(N · divisor), i.e. amortized O(1) per append, and the (rare) O(N)
    rewrite stall shrinks in frequency as the ledger grows. A cold start
    then folds at most ~1/8 of history as delta."""

    _SIDECAR_FILENAME: ClassVar[str] = "audit-entries.jsonl"
    """`B-47` close-out item (e) — the full-entry durable sidecar.

    The IS wrap persists only the `audit:<tag>:<entry_hash>` reference (the
    six-field C-IS-05 entry shape is ADR-F2-committed and carries no content
    field), so before this sidecar existed the OD `AuditLedgerEntry`'s
    `payload` + `signature_attrs` were produced then dropped — a real KMS
    signature could never be recovered or verified after restart
    (out-of-family Codex round-3 P1 on PR #1033, verified directly). Each
    APPENDED write lands one JSON line `{"tenant_tag", "entry"}` in this
    sidecar (same directory as the IS ledger file); the IS chain's action_id
    embeds the OD `entry_hash`, binding every sidecar row to exactly one
    tamper-evident chain entry. Writes are sidecar-first + membership-checked
    under the exclusive lock — replays and crash-retries never duplicate a
    row, and a crash between the sidecar write and the IS append leaves a
    detectable surplus row rather than a lost signature.
    """

    @property
    def sidecar_path(self) -> Path:
        """Public path handle — the shutdown flush (`flush_observability`)
        fsyncs this file alongside the IS ledger (a durable-signature claim
        that survives power loss requires BOTH files flushed)."""
        return self.ledger_writer.handle.canonical_path.parent / self._SIDECAR_FILENAME

    @property
    def _sidecar_path(self) -> Path:
        return self.sidecar_path

    @property
    def _snapshot_path(self) -> Path:
        return self.ledger_writer.handle.canonical_path.parent / self._SNAPSHOT_FILENAME

    def _write_index_snapshot_locked(self) -> None:
        """Persist the membership index as the item-(g) snapshot — MUST be
        called with both sidecar write locks held.

        Atomic replace (temp file in the same directory, fsync, `os.replace`,
        directory fsync) so a crash mid-write leaves either the previous
        snapshot or the new one, never a torn file — and a symlink planted at
        either path is refused (`O_NOFOLLOW` on the temp create; `os.replace`
        swaps the snapshot NAME, never writing through a link). Failures
        propagate: the sidecar row is already durable when this runs, so an
        abort here lands on the established crash-retry path (fold sees the
        row, membership-hit, continue) — never a torn commit.
        """
        index = self._sidecar_index
        body: dict[str, Any] = {
            "version": 1,
            "offset": index.offset,
            "inode": index.inode,
            "mtime_ns": index.mtime_ns,
            "digests": [[tag, entry_hash, d] for (tag, entry_hash), d in index.digests.items()],
            "legacy_exempt": sorted([tag, entry_hash] for tag, entry_hash in index.legacy_exempt),
            "redaction_tails": index.redaction_tails,
            # Binds the cache to the AUTHORITATIVE bytes it vouches for
            # (codex round-5 P1): adoption re-derives this by a raw-byte
            # streaming read of sidecar[0:offset] and discards on mismatch.
            "prefix_digest": index.prefix_hash.hexdigest(),
        }
        payload = {"body": body, "self_digest": _snapshot_body_digest(body)}
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        tmp_path = self._snapshot_path.with_name(self._SNAPSHOT_FILENAME + ".tmp")
        # O_NONBLOCK (codex round-2 P1 on this landing): a FIFO planted at
        # the fixed .tmp path would otherwise BLOCK this open awaiting a
        # reader while the append, sidecar-thread, and cross-process locks
        # are all held — one planted FIFO stalls every audit writer the
        # moment the cadence fires. Nonblocking, a writer-side FIFO open
        # fails immediately (ENXIO, loud); the fstat check below rejects
        # any other non-regular or foreign-owned plant, and O_TRUNC is
        # deferred to ftruncate AFTER validation so a refused plant is
        # never modified. O_NONBLOCK has no effect on regular-file writes.
        flags = os.O_CREAT | os.O_WRONLY | getattr(os, "O_NONBLOCK", 0)
        if sys.platform != "win32":
            flags |= os.O_NOFOLLOW
        fd = os.open(tmp_path, flags, 0o600)
        try:
            tmp_st = os.fstat(fd)
            if not stat.S_ISREG(tmp_st.st_mode):
                raise ValueError(
                    f"snapshot temp file {tmp_path} is not a regular file "
                    f"(mode={tmp_st.st_mode:o}) — refusing to write the index "
                    f"snapshot over a planted special file"
                )
            if sys.platform != "win32" and tmp_st.st_uid != os.geteuid():
                raise ValueError(
                    f"snapshot temp file {tmp_path} is owned by uid "
                    f"{tmp_st.st_uid}, not the effective uid {os.geteuid()} — "
                    f"refusing to write over another account's file"
                )
            if tmp_st.st_nlink > 1:
                # Codex round-3 P1 on this landing: a HARD LINK planted at
                # the fixed .tmp path passes the regular-file and uid
                # checks (O_NOFOLLOW only rejects symlinks; a same-uid link
                # to the sidecar or IS ledger is trivially plantable), and
                # the ftruncate below would destroy the linked
                # AUTHORITATIVE file to install a cache. A legitimate temp
                # file always has exactly one link.
                raise ValueError(
                    f"snapshot temp file {tmp_path} has {tmp_st.st_nlink} "
                    f"hard links — refusing to truncate a file linked "
                    f"elsewhere (possible plant over the sidecar or ledger)"
                )
            if sys.platform != "win32" and stat.S_IMODE(tmp_st.st_mode) & 0o077:
                # Codex round-6 P2 on this landing: os.open's 0o600 mode is
                # ignored for a PRE-EXISTING temp file, so a reused 0644
                # plant would ride os.replace into a group/world-readable
                # installed snapshot (tenant tags + entry hashes). Clamp on
                # the open fd before any bytes are written.
                os.fchmod(fd, 0o600)
            os.ftruncate(fd, 0)
        except BaseException:
            os.close(fd)
            raise
        # Buffered writer, not a bare os.write (codex round-1 P2 on this
        # landing): a single os.write may return SHORT on a regular file,
        # silently installing truncated JSON that every cold start then
        # discards — correctness survives (self-digest → refold) but the
        # cache is defeated; BufferedWriter.write loops until complete.
        with os.fdopen(fd, "wb") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, self._snapshot_path)
        if sys.platform != "win32":
            dir_fd = os.open(str(self._snapshot_path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        index.unsnapshotted = 0

    def _maybe_write_index_snapshot_locked(self) -> None:
        index = self._sidecar_index
        # Threshold over ALL serialized membership state, not digests alone
        # (codex round-2 P2 on this landing): a migrated ledger's
        # `legacy_exempt` baseline can dominate the snapshot — a
        # digests-only threshold stayed at the floor and re-sorted +
        # rewrote the whole baseline every 64 appends, recreating exactly
        # the O(history) lock-held stalls the geometric cadence removes.
        serialized_members = (
            len(index.digests) + len(index.legacy_exempt) + len(index.redaction_tails)
        )
        threshold = max(
            self._SNAPSHOT_EVERY_APPENDS,
            serialized_members // self._SNAPSHOT_GROWTH_DIVISOR,
        )
        if index.unsnapshotted >= threshold:
            self._write_index_snapshot_locked()

    def _try_adopt_index_snapshot_locked(self, st: os.stat_result) -> None:
        """Adopt the on-disk index snapshot into a ZERO-offset index — MUST
        be called with both sidecar write locks held, `st` the current
        sidecar stat.

        Discard-on-any-anomaly: parse failure, self-digest mismatch, shape
        violation, inode change (sidecar replaced since the snapshot),
        offset past the current size (sidecar truncated since), a
        same-size mtime drift (in-place mutation — the `same_size_mutated`
        mirror), or a covered-prefix digest mismatch (raw sidecar bytes
        diverge from what the snapshot vouches for — codex round-5 P1) all
        silently fall back to the full refold. Silence is the
        correct posture here, not a swallowed failure: every discard
        degrades to the exact behavior that existed before this cache, and
        the anomalies are EXPECTED states (a snapshot goes stale the moment
        another process heals a torn tail). The index is only mutated after
        every validation passes — no partial adoption.
        """
        snapshot_path = self._snapshot_path
        if not snapshot_path.exists():
            return
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)
        if sys.platform != "win32":
            flags |= os.O_NOFOLLOW
        try:
            fd = os.open(snapshot_path, flags)
            try:
                snap_st = os.fstat(fd)
                if not stat.S_ISREG(snap_st.st_mode):
                    return
                if sys.platform != "win32" and snap_st.st_uid != os.geteuid():
                    return
                with os.fdopen(fd, encoding="utf-8") as fh:
                    fd = -1
                    payload = json.load(fh)
            finally:
                if fd >= 0:
                    os.close(fd)
            body = payload["body"]
            if payload["self_digest"] != _snapshot_body_digest(body):
                return
            if body["version"] != 1:
                return
            offset = body["offset"]
            inode = body["inode"]
            mtime_ns = body["mtime_ns"]
            if not (isinstance(offset, int) and isinstance(inode, int)):
                return
            if not isinstance(mtime_ns, int):
                return
            if inode != st.st_ino or offset > st.st_size:
                return
            if offset == st.st_size and mtime_ns != st.st_mtime_ns:
                return
            digests = {
                (str(tag), str(entry_hash)): str(digest)
                for tag, entry_hash, digest in body["digests"]
            }
            legacy_exempt = {
                (str(tag), str(entry_hash)) for tag, entry_hash in body["legacy_exempt"]
            }
            redaction_tails = {str(tag): str(tail) for tag, tail in body["redaction_tails"].items()}
            prefix_digest = str(body["prefix_digest"])
            # Bind the cache to the AUTHORITATIVE bytes it vouches for
            # (codex round-5 P1): metadata checks alone accept silent bit
            # rot in the folded prefix (size/inode/mtime intact), letting a
            # legitimate replay NOOP against a digest computed from the
            # pre-rot row. A raw-byte streaming read of sidecar[0:offset]
            # restores the cold-refold's detection parity WITHOUT the
            # expensive part (no JSON parse, no schema validation, no
            # per-row re-serialization) — mismatch discards the snapshot,
            # and the forced full refold then fails loud on the rotted row.
            prefix_hash = hashlib.sha256()
            if offset > 0:
                fd = self._open_sidecar_validated(os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
                try:
                    remaining = offset
                    while remaining > 0:
                        chunk = os.read(fd, min(remaining, 1 << 20))
                        if not chunk:
                            return
                        prefix_hash.update(chunk)
                        remaining -= len(chunk)
                finally:
                    os.close(fd)
            if prefix_hash.hexdigest() != prefix_digest:
                return
        except (OSError, ValueError, KeyError, TypeError):
            # json.JSONDecodeError is a ValueError; ELOOP (planted symlink)
            # and permission errors are OSError — all are discard-anomalies,
            # not failures (see docstring).
            return
        index = self._sidecar_index
        index.digests = digests
        index.legacy_exempt = legacy_exempt
        index.redaction_tails = redaction_tails
        index.offset = offset
        index.inode = inode
        index.mtime_ns = mtime_ns
        index.prefix_hash = prefix_hash
        index.unsnapshotted = 0

    @classmethod
    def _tenant_tag(cls, tenant_id: str | None) -> str:
        """Resolve the tenant scoping tag for an append/read call.

        Delegates to `harness_od.sidecar_tag` (OD spec v1.34 §21.2.1 row 2 —
        out-of-family Codex P2, PR #1061 round 3: the writer previously
        duplicated this rule-set instead of calling the newly-declared
        normalization authority, an enforcement criterion the plan text
        pins explicitly — "the runtime writer's `_tenant_tag` MUST delegate
        to it"). `sidecar_tag` shares the SAME injective encoding this
        writer already relied on (codex round-45 P1): `None` -> the writer's
        `_SINGLE_TENANT_TAG` literal; the empty string and the reserved
        literal itself are refused — a real tenant may never alias the
        single-tenant audit scope. Delegating (rather than duplicating)
        means signing's fifth-segment tag and this sidecar/action-ID join
        key cannot drift out of sync.
        """
        return sidecar_tag(tenant_id)

    @classmethod
    def _action_id_for(cls, tenant_id: str | None, audit_entry: AuditLedgerEntry) -> Identifier:
        """Build the IS action_id for an audit-entry wrap."""
        tag = cls._tenant_tag(tenant_id)
        return Identifier(f"{cls._ACTION_ID_PREFIX}:{tag}:{audit_entry.entry_hash}")

    def append(
        self,
        tenant_id: str | None,
        audit_entry: AuditLedgerEntry,
    ) -> WriteResult:
        """Persist one pre-signed `AuditLedgerEntry` into the IS hash chain.

        Returns the IS `WriteResult` — `APPENDED` on a fresh entry,
        `IDEMPOTENT_NOOP` on a replay of the same audit entry within the same
        tenant scope. The OD-computed `entry_hash` provides the deduplication
        key (scoped by tenant via the action_id prefix).
        """
        # ONE ordered critical section per ledger path (codex round-4
        # P1): timestamp sampling + sidecar write + IS append serialize
        # together, so commit order always matches timestamp order.
        with _append_lock_for(self.ledger_writer.handle.canonical_path):
            return self._append_core(tenant_id, audit_entry, sidecar_locks_held=False)

    def _append_core(
        self,
        tenant_id: str | None,
        audit_entry: AuditLedgerEntry,
        *,
        sidecar_locks_held: bool,
    ) -> WriteResult:
        """Append core — caller holds the per-ledger append lock; when
        `sidecar_locks_held`, the sidecar thread+process locks too (the
        B-50 item (i) transaction path)."""
        recomputed = compute_entry_hash(audit_entry.payload)
        if recomputed != audit_entry.entry_hash:
            # Write-side mirror of the fold's content-integrity check (codex
            # round-27): a schema-valid entry whose stored hash does not match
            # its payload would persist fine, then wedge EVERY post-restart
            # append when the fold rescans it. In the core so the B-50
            # transaction path is covered too.
            raise ValueError(
                f"audit_entry fails content-integrity before write: stored "
                f"entry_hash={audit_entry.entry_hash!r} but recomputed "
                f"{recomputed!r} — refusing to persist an entry that would "
                f"wedge the sidecar fold after restart"
            )
        action_id = self._action_id_for(tenant_id, audit_entry)
        # R-003: `procedural_tier_snapshot_ref` is left `None`-canonical here
        # (IS spec v1.3 §C-IS-05 §5.1). This append wraps pre-signed OD audit
        # entries — a separate ledger family, not an active-workflow-context
        # producer emission — so the D-derivative sidecar does not apply.
        payload = EntryPayload(
            action_id=action_id,
            idempotency_key=action_id,
            actor=self.ledger_writer.actor,
            timestamp=self.time_source(),
        )
        write_key = WriteKey(
            thread_id=Identifier(f"{self._ACTION_ID_PREFIX}:{self._tenant_tag(tenant_id)}"),
            step_id=action_id,
            idempotency_key=action_id,
        )
        # Item (e): persist the FULL signed entry SIDECAR-FIRST (out-of-family
        # Codex round-3 finding on the PR-B1 landing). IS-first ordering lost
        # the signed entry PERMANENTLY when the process died between the two
        # writes and the exact event was never replayed (span-redaction and
        # cost side effects do not replay) — and a later NEW event then seeded
        # its chain from the pre-loss tail, forking the OD chain against the
        # IS refs. Sidecar-first inverts the failure: the valuable data (the
        # full signed entry) is durable before the chain ref lands; a crash
        # between the writes leaves at worst a SURPLUS sidecar row with no IS
        # ref — detectable by a verifier cross-checking refs, prunable, and
        # chain-consistent (the row was genuinely signed at that position, so
        # tail seeding keeps verifying). The membership-checked write keeps
        # every path idempotent (a retry after either crash window never
        # duplicates a row); the IS append remains the dedup authority for
        # the RESULT the caller sees.
        if sidecar_locks_held:
            self._append_sidecar_line_if_missing_locked(tenant_id, audit_entry)
        else:
            self._append_sidecar_line_if_missing(tenant_id, audit_entry)
        # Bounded resample-retry (codex round-8 P1): this lock
        # serializes AUDIT appends, but ordinary `LedgerWriter.append`
        # F2/state writes to the SAME ledger do not take it — one can
        # commit a newer timestamp between our sampling and our IS
        # append, which then raises NonMonotonicTimestampError AFTER
        # the sidecar row is durable (an unanchored signature). The IS
        # append is retry-safe here: the OD entry (and so the sidecar
        # identity) is timestamp-independent, and the idempotency key
        # is unchanged — resample a fresh timestamp and retry. Bounded:
        # a hot ledger could starve an unbounded loop; exhaustion
        # propagates the error loudly (the sidecar row is preserved and
        # the NEXT append's crash-repair path re-anchors it).
        attempts_left = 5
        while True:
            try:
                return self.ledger_writer.append(payload, write_key)
            except NonMonotonicTimestampError:
                attempts_left -= 1
                if attempts_left <= 0:
                    raise
                payload = EntryPayload(
                    action_id=payload.action_id,
                    idempotency_key=payload.idempotency_key,
                    actor=payload.actor,
                    timestamp=self.time_source(),
                )

    def _sidecar_line_for(self, tenant_id: str | None, audit_entry: AuditLedgerEntry) -> str:
        return json.dumps(
            {
                "tenant_tag": self._tenant_tag(tenant_id),
                "entry": audit_entry.model_dump(mode="json"),
            },
            separators=(",", ":"),
        )

    def _open_sidecar_for_append(self) -> int:
        """Open (creating 0600 if absent) the sidecar for appending — refusing
        unsafe pre-existing targets.

        Owner-only permissions at creation (out-of-family Codex P1 on the
        PR-B1 landing): the redaction-token path persists ORIGINAL PII /
        secret text under `audit.redaction_token.raw_value`, so under the
        common `022` umask a plain `open("a")` would land that content
        world-readable on shared hosts.

        Pre-existing targets are VERIFIED, not trusted (codex round-31 P1):
        `O_CREAT` does not change an existing file's mode and a plain open
        follows symlinks, so on a shared state directory another account
        could pre-create a symlink or a permissively-readable file and
        harvest appended raw values. POSIX opens use `O_NOFOLLOW` (symlink →
        `ELOOP`, fails loud) and the opened fd is `fstat`-checked: must be a
        regular file, owned by the effective uid, with no group/other
        permission bits. A deliberately re-permissioned file therefore fails
        loud rather than silently receiving secrets — the operator's remedy
        is explicit (chmod 600 or relocate), never a silent downgrade.
        Windows carries the documented B-45 platform posture (no O_NOFOLLOW;
        ACL semantics differ).
        """
        return self._open_sidecar_validated(os.O_CREAT | os.O_WRONLY | os.O_APPEND)

    def _open_sidecar_validated(self, flags: int) -> int:
        """The ONE validated open every sidecar fd goes through (rounds 31/32)."""
        if sys.platform != "win32":
            flags |= os.O_NOFOLLOW
        fd = os.open(self._sidecar_path, flags, 0o600)
        if sys.platform == "win32":
            return fd
        try:
            st = os.fstat(fd)
            if not stat.S_ISREG(st.st_mode):
                raise ValueError(
                    f"sidecar {self._sidecar_path} is not a regular file "
                    f"(mode={st.st_mode:o}) — refusing to append raw values"
                )
            if st.st_uid != os.geteuid():
                raise ValueError(
                    f"sidecar {self._sidecar_path} is owned by uid {st.st_uid}, "
                    f"not the effective uid {os.geteuid()} — refusing to append "
                    f"raw values to another account's file"
                )
            if st.st_mode & 0o077:
                raise ValueError(
                    f"sidecar {self._sidecar_path} is group/other-accessible "
                    f"(mode={stat.S_IMODE(st.st_mode):o}) — raw redaction values "
                    f"must stay owner-only; chmod 600 it (or remove it) and retry"
                )
        except BaseException:
            os.close(fd)
            raise
        return fd

    def _heal_torn_tail_locked(self) -> None:
        """Truncate an unterminated final record (crash mid-write) — MUST be
        called with the exclusive cross-process lock held.

        Out-of-family Codex P2 on the PR-B1 landing: a process/disk failure
        interrupting a sidecar write can leave a partial JSON fragment with
        no trailing newline. Left in place it wedges every subsequent read
        and repair (`json.loads` raises on the torn tail), and a later
        append would MERGE its line into the fragment. A file that does not
        end in `\\n` is by construction a torn tail (every completed write
        ends with one); truncate back to the last completed record. The
        truncated entry's IS chain ref survives, so the NOOP repair path
        re-lands it whole.

        ALL operations go through one `O_NOFOLLOW`-validated descriptor
        (codex round-32 P1): the earlier path-based `exists`/`stat`/`open`/
        `os.truncate` sequence followed a pre-created symlink and truncated
        an ATTACKER-CHOSEN writable target before the append-time validation
        ever ran.
        """
        try:
            fd = self._open_sidecar_validated(os.O_RDWR)
        except FileNotFoundError:
            return
        try:
            size = os.fstat(fd).st_size
            if size == 0:
                return
            os.lseek(fd, -1, os.SEEK_END)
            if os.read(fd, 1) == b"\n":
                return
            os.lseek(fd, 0, os.SEEK_SET)
            # Drain the FULL file before choosing a truncation point (codex
            # round-38 P1): a short os.read here made rfind search only a
            # prefix — ftruncate then destroyed every valid signed record
            # after it.
            chunks: list[bytes] = []
            remaining = size
            while remaining > 0:
                chunk = os.read(fd, remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            data = b"".join(chunks)
            if len(data) != size:
                raise OSError(
                    f"could not drain sidecar for torn-tail heal: read "
                    f"{len(data)} of {size} bytes — refusing to truncate on "
                    f"partial knowledge"
                )
            keep = data.rfind(b"\n") + 1  # 0 when no completed record exists
            os.ftruncate(fd, keep)
        finally:
            os.close(fd)

    def sidecar_expected(self) -> bool:
        """True iff the IS ledger holds audit refs — i.e. the sidecar SHOULD
        exist. Public so the shutdown flush can distinguish genuine first use
        from deletion-after-use (codex round-43), consistent with the
        writer's own missing-sidecar guard."""
        return any(
            entry.action_id.startswith(f"{self._ACTION_ID_PREFIX}:")
            for entry in read_ledger(self.ledger_writer.handle)
        )

    def _assert_absence_is_first_use(self) -> None:
        """A MISSING sidecar is only legitimate before any audit entry ever
        landed (codex round-36 P1): after entries exist, deletion — cleanup,
        corruption, tampering — must fail loud, not silently present an empty
        history and let the next append mint a REPLACEMENT sidecar (IS refs
        old + new, only new signatures recoverable — exactly the loss the
        sidecar exists to prevent). The IS chain is the authority for
        \"has anything ever been appended\": its `audit:` refs are hash-chained
        and cannot be silently removed the way a plain file can.
        """
        if self.sidecar_expected():
            raise ValueError(
                f"audit sidecar {self._sidecar_path} is MISSING but the IS "
                f"ledger holds audit references — the durable signed-entry "
                f"history has been deleted or lost; refusing to continue "
                f"(restore the sidecar from backup; for a PRE-SIDECAR ledger "
                f"upgraded in place, run `python -m "
                f"harness_runtime.admin.migrate_audit_sidecar "
                f"<state-ledger.jsonl>` once to baseline the legacy "
                f"references; or intentionally reset BOTH ledgers together)"
            )

    def _assert_is_refs_covered_locked(self, *, allowed_gap: tuple[str, str] | None = None) -> None:
        """Every IS `audit:<tag>:<hash>` ref must have a sidecar row (codex
        round-40 P1) — run after a FULL index fold, so bulk truncation to a
        newline boundary (heal-invisible, absence-check-invisible) fails loud
        instead of silently losing signed history. `allowed_gap` names the
        one identity the caller is about to (re-)land — the legitimate
        single-entry crash-repair path. Runs only on full rescans, never on
        the incremental hot path.
        """
        for is_entry in read_ledger(self.ledger_writer.handle):
            action_id = is_entry.action_id
            if not action_id.startswith(f"{self._ACTION_ID_PREFIX}:"):
                continue
            # Parse the hash from the RIGHT (codex round-41): a tenant id
            # containing ':' (e.g. "tenant:west") made the left-split report
            # valid history as missing. entry_hash is hex-64 — never ':'.
            prefix_and_tag, entry_hash = action_id.rsplit(":", 1)
            tag = prefix_and_tag[len(f"{self._ACTION_ID_PREFIX}:") :]
            identity = (tag, entry_hash)
            if identity == allowed_gap:
                continue
            if identity in self._sidecar_index.legacy_exempt:
                # Pre-sidecar refs explicitly baselined by
                # `adopt_legacy_is_refs()` (codex round-46 P1) — their full
                # entries were produced then dropped by the pre-sidecar
                # runtime and can never be recovered; the baseline records
                # that as an operator-acknowledged fact, not a loss event.
                continue
            if identity not in self._sidecar_index.digests:
                raise ValueError(
                    f"IS ledger references audit entry {entry_hash!r} for "
                    f"tenant_tag={tag!r} but the sidecar holds no such row — "
                    f"signed history has been truncated or lost; refusing to "
                    f"continue (restore the sidecar from backup, or "
                    f"intentionally reset BOTH ledgers together)"
                )

    def _append_sidecar_line_if_missing(
        self, tenant_id: str | None, audit_entry: AuditLedgerEntry
    ) -> None:
        """Membership-checked sidecar append — every write path (item (e)).

        Guarded by the same B-40 cross-process write lock the IS ledger uses
        (keyed on the sidecar's own path): the torn-tail heal, the membership
        check, and the conditional append happen under ONE exclusive lock, so
        two concurrent writers/replays of the same entry cannot both append
        and cannot interleave partial lines. Membership keys on
        `(tenant_tag, entry_hash)`, the same identity the IS chain's
        action_id embeds. The OD carrier is JSON-clean
        (`audit_signature_value` is base64/placeholder text, never raw bytes
        — the PR-A representation discipline), so `model_dump(mode="json")`
        round-trips losslessly.
        """
        with self._sidecar_thread_lock, cross_process_write_lock(self._sidecar_path):
            self._append_sidecar_line_if_missing_locked(tenant_id, audit_entry)

    def _append_sidecar_line_if_missing_locked(
        self, tenant_id: str | None, audit_entry: AuditLedgerEntry
    ) -> None:
        """Sidecar-append core — caller holds BOTH sidecar locks (B-50
        item (i): the unlocked-inner shape a `tenant_transaction` composes
        under one outer hold; POSIX flock is non-reentrant, so the core
        must never reacquire)."""
        tag = self._tenant_tag(tenant_id)
        line = self._sidecar_line_for(tenant_id, audit_entry)
        if not self._sidecar_path.exists():
            # Round-36 P1: creating a REPLACEMENT sidecar after the
            # original disappeared would silently split history (old IS
            # refs unrecoverable). Absence is only legitimate at genuine
            # first use.
            self._assert_absence_is_first_use()
        self._heal_torn_tail_locked()
        folded_from_zero = self._sidecar_index.offset == 0
        rescanned_from_zero = self._refresh_sidecar_index_locked()
        if folded_from_zero or rescanned_from_zero:
            # `rescanned_from_zero` (codex round-45 P1): a WARM index
            # (offset > 0) whose file was truncated/replaced resets to
            # zero INSIDE the refresh — gating on the pre-refresh offset
            # alone skipped the coverage check exactly when truncation
            # was detected, extending an incomplete history.
            # Round-40 P1: truncation to a NEWLINE BOUNDARY (or to zero
            # with the file kept) leaves only valid-looking rows — the
            # torn-tail heal sees nothing to fix and round-36's absence
            # check never fires. After any full fold, every IS audit ref
            # must be covered by sidecar membership, EXCEPT the identity
            # being appended right now (that one gap is the legitimate
            # single-entry crash-repair path, rounds 1/3).
            self._assert_is_refs_covered_locked(allowed_gap=(tag, audit_entry.entry_hash))
        identity = (tag, audit_entry.entry_hash)
        incoming_digest = _full_entry_digest(audit_entry)
        stored_digest = self._sidecar_index.digests.get(identity)
        if stored_digest is not None:
            if stored_digest != incoming_digest:
                # Codex round-19: a durable row whose signature_attrs
                # were mutated (payload + entry_hash intact) must not
                # silently satisfy membership for the legitimate entry —
                # the corrupted signature would remain the only durable
                # copy. Fail loud; the row is preserved as evidence.
                raise ValueError(
                    f"sidecar row for tenant_tag={tag!r} "
                    f"entry_hash={audit_entry.entry_hash!r} diverges from "
                    f"the entry being appended (signature_attrs or other "
                    f"non-payload fields differ) — tampered or corrupt "
                    f"row preserved as evidence, append refused"
                )
            # Re-establish durability on the membership-hit path (codex
            # round-28): if a prior attempt wrote this row but its fsync
            # raised, the retry lands here — returning without another
            # fsync would let the IS reference commit while the row (or
            # its directory entry) is still only page-cached.
            fd = self._open_sidecar_validated(os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            if sys.platform != "win32":
                dir_fd = os.open(str(self._sidecar_path.parent), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            return
        encoded = (line + "\n").encode("utf-8")
        with os.fdopen(self._open_sidecar_for_append(), "ab") as fh:
            fh.write(encoded)
            fh.flush()
            # Durability BEFORE the IS ref lands (codex round-23): a bare
            # write+close only reaches the page cache — power loss after
            # the IS append could keep the ref while the signature row
            # was never durable, defeating the sidecar-first guarantee.
            os.fsync(fh.fileno())
        if sys.platform != "win32":
            # Directory-entry durability on EVERY append (codex round-33
            # P2 — a `created`-gated dir-fsync missed the retry after a
            # crash between O_CREAT and the first write: the file already
            # existed, so its directory entry was never made durable
            # before the IS ref landed). One extra fsync per audit write
            # is cheap; POSIX-only per the documented B-45 posture.
            dir_fd = os.open(str(self._sidecar_path.parent), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        # Our own write never needs re-parsing: record it in the index
        # and advance past it.
        self._sidecar_index.digests[identity] = incoming_digest
        if _has_redaction_namespace_keys(audit_entry):
            self._sidecar_index.redaction_tails[tag] = audit_entry.entry_hash
        self._sidecar_index.offset += len(encoded)
        self._sidecar_index.prefix_hash.update(encoded)
        post = self._sidecar_path.stat()
        self._sidecar_index.inode = post.st_ino
        self._sidecar_index.mtime_ns = post.st_mtime_ns
        self._sidecar_index.unsnapshotted += 1
        self._maybe_write_index_snapshot_locked()

    def _refresh_sidecar_index_locked(self) -> bool:
        """Incrementally fold NEW sidecar bytes into the membership index —
        MUST be called with both locks held, after the torn-tail heal.
        Returns True when a truncation / replacement / mutation forced the
        index back to zero for a full rescan (the caller must then re-check
        IS-ref coverage — codex round-45 P1).

        Out-of-family Codex round-12 P2: a full scan-per-append is O(N²)
        JSON parsing on the span-finalization hot path of a long-running
        compliance deployment. Each byte is now parsed at most once per
        process: only the delta since `offset` (another process's appends)
        is read; our own appends advance the offset directly. A file smaller
        than the recorded offset means a truncation happened (torn-tail heal
        in another process) — full rescan, rare by construction.
        """
        index = self._sidecar_index
        st = self._sidecar_path.stat() if self._sidecar_path.exists() else None
        size = st.st_size if st is not None else 0
        truncated = size < index.offset
        inode_changed = index.offset > 0 and st is not None and st.st_ino != index.inode
        same_size_mutated = (
            index.offset > 0
            and st is not None
            and size == index.offset
            and st.st_mtime_ns != index.mtime_ns
        )
        reset_to_zero = truncated or inode_changed or same_size_mutated
        if reset_to_zero:
            index.legacy_exempt.clear()
            index.redaction_tails.clear()
            # Full rescan ONLY for: truncation (torn-tail heal elsewhere),
            # file replacement (inode change), or a same-size in-place
            # mutation (codex round-21: size-equality alone trusted a stale
            # index over a tampered row). Plain GROWTH on the same inode
            # folds just the suffix below (codex round-22: clearing on every
            # foreign append restored the O(N²) behavior this index removes —
            # alternating same-host writers must stay incremental). A
            # mutate-in-folded-region-then-grow on the same inode, or a
            # mutation that also restores mtime_ns, is adversarial-filesystem
            # territory — the read-time verifier arc (B-47 remainder) owns
            # that tier.
            index.digests.clear()
            index.offset = 0
            index.prefix_hash = hashlib.sha256()
        if index.offset == 0 and st is not None:
            # B-50 item (g): a zero-offset index (cold start, or the reset
            # above) adopts the on-disk snapshot when every validation
            # passes, folding only the delta below instead of the full
            # history. Adoption after the reset is deliberate — the
            # snapshot's own inode/offset/mtime checks decide staleness
            # independently of why the offset is zero.
            self._try_adopt_index_snapshot_locked(st)
        if st is not None and size == index.offset:
            index.inode = st.st_ino
            index.mtime_ns = st.st_mtime_ns
            return reset_to_zero
        if st is None:
            return reset_to_zero
        # Validated fd (codex round-33 P1): a plain path open here followed
        # symlinks and would block forever on a pre-created FIFO.
        pre_fold_offset = index.offset
        fd = self._open_sidecar_validated(os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        try:
            os.lseek(fd, index.offset, os.SEEK_SET)
            # Drain to the snapshot size (codex round-37): a single os.read
            # may return SHORT; advancing the offset to `size` would mark the
            # unread suffix as folded, so a replay whose identity sits there
            # would duplicate its sidecar row.
            chunks: list[bytes] = []
            remaining = size - index.offset
            while remaining > 0:
                chunk = os.read(fd, remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            delta = b"".join(chunks)
        finally:
            os.close(fd)
        # Fold only COMPLETE records and advance by bytes actually consumed —
        # never by the snapshot size.
        if not delta.endswith(b"\n"):
            delta = delta[: delta.rfind(b"\n") + 1]
        if not delta:
            return reset_to_zero
        # The heal ran under this same lock, so the region ends on a newline;
        # every split segment is a complete record.
        for raw in delta.split(b"\n"):
            if not raw.strip():
                continue
            index.unsnapshotted += 1
            row = json.loads(raw)
            if "legacy_baseline" in row:
                # `adopt_legacy_is_refs()` baseline (codex round-46 P1):
                # pre-sidecar IS refs whose full entries the old runtime
                # dropped — exempt from coverage, never members (no entry).
                index.legacy_exempt.update((pair[0], pair[1]) for pair in row["legacy_baseline"])
                continue
            # Validate the WHOLE entry before accepting the row as membership
            # (codex round-15, PR B1): a newline-terminated row with valid
            # identity keys but corrupt remaining fields must not silently
            # suppress a legitimate re-append of the real signed entry —
            # that would land an IS ref whose only full copy is the corrupt
            # row. Fail-loud matches the reader's posture and preserves the
            # corrupt row as evidence (auto-replacing it would destroy what
            # may be tampering). Validation happens once per folded byte —
            # no O(N²) regression.
            entry = AuditLedgerEntry.model_validate(row["entry"])
            # Content-integrity check (codex round-17): a schema-valid row
            # whose payload was altered with the stale entry_hash left in
            # place must not enter the index — a replay of the legitimate
            # entry would NOOP against the stale hash, leaving the tampered
            # payload as the only full copy. Mirrors
            # verify_hash_chain_integrity's recompute-before-trust posture.
            recomputed = compute_entry_hash(entry.payload)
            if recomputed != entry.entry_hash:
                raise ValueError(
                    f"sidecar row for tenant_tag={row['tenant_tag']!r} fails "
                    f"content-integrity: stored entry_hash={entry.entry_hash!r} "
                    f"but recomputed {recomputed!r} — tampered or corrupt row "
                    f"preserved as evidence, append refused"
                )
            identity = (row["tenant_tag"], entry.entry_hash)
            digest = _full_entry_digest(entry)
            existing = index.digests.get(identity)
            if existing is not None:
                # Duplicate identity (codex round-47 P1): silently letting
                # the last row win would make a replay of the legitimate
                # entry NOOP against a tampered digest while the reader
                # returns both rows — bypassing the fail-loud posture. No
                # write path ever duplicates an identity (membership-checked
                # under the exclusive lock; even our own crash-retries fold
                # the durable row before appending), so ANY duplicate —
                # conflicting or byte-identical — is external mutation;
                # preserved as evidence, fold refused.
                detail = (
                    "signature_attrs or other non-payload fields differ"
                    if existing != digest
                    else "byte-identical copy"
                )
                raise ValueError(
                    f"sidecar holds duplicate rows for "
                    f"tenant_tag={row['tenant_tag']!r} "
                    f"entry_hash={entry.entry_hash!r} ({detail}) — tampered "
                    f"or corrupt rows preserved as evidence"
                )
            index.digests[identity] = digest
            if _has_redaction_namespace_keys(entry):
                index.redaction_tails[row["tenant_tag"]] = entry.entry_hash
        index.offset += len(delta)
        index.prefix_hash.update(delta)
        post = self._sidecar_path.stat()
        index.inode = post.st_ino
        index.mtime_ns = post.st_mtime_ns
        if pre_fold_offset == 0:
            # A from-zero fold is the O(history) event the item-(g)
            # snapshot amortizes — persist immediately so it is paid at
            # most once per anomaly, not once per process start.
            self._write_index_snapshot_locked()
        else:
            self._maybe_write_index_snapshot_locked()
        return reset_to_zero

    def read_full_entries_for_tenant(self, tenant_id: str | None) -> list[AuditLedgerEntry]:
        return self._read_full_entries_core(tenant_id, sidecar_locks_held=False)

    def _read_full_entries_core(
        self, tenant_id: str | None, *, sidecar_locks_held: bool
    ) -> list[AuditLedgerEntry]:
        """Tenant-scoped FULL-entry reader over the item-(e) sidecar.

        Rehydrates every persisted `AuditLedgerEntry` (payload +
        signature_attrs + entry_hash) for `tenant_id` — the surface a
        verifier needs to check real signatures after restart, which the
        ref-only `read_for_tenant` cannot provide.

        **The returned sequence is NOT one verifiable hash chain** (codex
        round-30, B-47 close-out item (h)): a tenant's entries come from
        INDEPENDENT producer families — the CXA converter's entries chain on
        CP-side event hashes, the redaction-token map chains within itself,
        cost/HITL families likewise — discriminated by the CXA §0.3
        action-id prefix on `payload.entry_core`. Running
        `verify_hash_chain_integrity` over the raw per-tenant sequence fails
        by construction once two families interleave; the PR-B2 verifier
        must partition by family first. Per-entry signature verification and
        content-hash recomputation remain valid over this sequence as-is. Returns `[]` when the
        sidecar does not exist yet (no audit entry has ever been appended
        through this writer). A malformed line fails loud — a corrupt
        audit-entry sidecar must never be silently skipped.
        """
        tag = self._tenant_tag(tenant_id)
        # Snapshot the IS refs BEFORE reading the sidecar (codex round-44):
        # writes are sidecar-first, so every ref in this snapshot already has
        # its row durable — a concurrent append between the two reads can add
        # rows (harmless superset) but never a ref this snapshot contains
        # without its row, eliminating the false history-loss report the
        # reverse order produced.
        is_ref_hashes = {
            is_entry.action_id.rsplit(":", 1)[1] for is_entry in self.read_for_tenant(tenant_id)
        }
        # Sample the IS-refs predicate BEFORE the existence check (merge-gate
        # round-1 concurrency lens, B-47 item (k)): exists()-then-refs let a
        # FIRST-EVER append land file+ref between the two samples and
        # falsely raise the round-36 loss error. Refs-at-T0 with
        # not-exists-at-T1 is sound under sidecar-first ordering: a ref at
        # T0 implies its sidecar file existed at T0, so absence later is
        # genuine deletion.
        refs_existed = self.sidecar_expected()
        if not self._sidecar_path.exists():
            if refs_existed:
                self._assert_absence_is_first_use()
            return []
        entries: list[AuditLedgerEntry] = []
        seen_hashes: set[str] = set()
        exempt_hashes: set[str] = set()
        # B-40 shared read lock (side-effect-free: never O_CREAT, never mkdir)
        # — excludes a concurrent writer's partial line once the lock file
        # exists; the brand-new-file window carries the documented B-46
        # residual, identical to the main-ledger read path. The per-path
        # thread lock adds the SAME-PROCESS half (codex round-26): on
        # Windows the cross-process lock is a no-op, so a verifier racing a
        # writer thread in one process needs this to never observe a
        # partially written record.
        lock_ctx: Any = (
            contextlib.nullcontext()
            if sidecar_locks_held
            else _combined_sidecar_read_locks(self._sidecar_thread_lock, self._sidecar_path)
        )
        with lock_ctx:
            # Validated fd (codex round-33 P1): the token map's SEEDING read
            # runs before its first append, so a plain path open here let a
            # pre-created FIFO hang span completion and a symlink supply
            # attacker-controlled rows before the validated append path ever
            # ran. O_NONBLOCK makes a FIFO open return instead of blocking;
            # the fstat check then rejects it as not-a-regular-file.
            fd = self._open_sidecar_validated(os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
            with os.fdopen(fd, encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    if not line.endswith("\n"):
                        # Torn tail (crash mid-write): every completed record
                        # ends with a newline, so an unterminated final line
                        # is a partial fragment, not corruption. Skipped —
                        # reads are side-effect-free (never truncate; the
                        # `harness-inspect` read-only contract) and the
                        # entry's IS ref survives, so the next write-path
                        # call heals it. A malformed line that DOES end in
                        # `\n` still fails loud below (real corruption).
                        continue
                    row = json.loads(line)
                    if "legacy_baseline" in row:
                        # Pre-sidecar refs baselined by adopt_legacy_is_refs()
                        # (codex round-46 P1) — no full entry exists to
                        # rehydrate; exempt them from the coverage check.
                        exempt_hashes.update(
                            pair[1] for pair in row["legacy_baseline"] if pair[0] == tag
                        )
                        continue
                    if row["tenant_tag"] != tag:
                        continue
                    entry = AuditLedgerEntry.model_validate(row["entry"])
                    # Round-42 codex: the reader needs the same round-17
                    # content recompute as the append-side fold — a payload
                    # modified with its stale entry_hash retained still
                    # passes schema validation AND the coverage check (the
                    # unchanged hash matches the IS ref), silently feeding
                    # tampered content to verifiers and chain tail seeding.
                    recomputed = compute_entry_hash(entry.payload)
                    if recomputed != entry.entry_hash:
                        raise ValueError(
                            f"sidecar row for tenant_tag={tag!r} fails "
                            f"content-integrity on read: stored "
                            f"entry_hash={entry.entry_hash!r} but recomputed "
                            f"{recomputed!r} — tampered or corrupt row"
                        )
                    if entry.entry_hash in seen_hashes:
                        # Reader mirror of the fold's conflicting-duplicate
                        # rejection (codex round-47 P1): no write path ever
                        # duplicates an identity, so a second row for the
                        # same hash is external mutation — returning both
                        # would feed verifiers a sequence no legitimate
                        # writer produced. Set lookup, not a rescan of
                        # `entries` (codex round-48 P2: the map's tail-seed
                        # read runs on the first token after each restart —
                        # O(N²) there stalls span completion on long-lived
                        # compliance ledgers).
                        raise ValueError(
                            f"sidecar holds duplicate rows for "
                            f"tenant_tag={tag!r} "
                            f"entry_hash={entry.entry_hash!r} — tampered or "
                            f"corrupt rows preserved as evidence"
                        )
                    seen_hashes.add(entry.entry_hash)
                    entries.append(entry)
        # Round-40 P1 (reader half): a sidecar truncated to a newline
        # boundary rehydrates only the surviving rows — every IS ref for
        # this tenant must still be covered, or the verifier is silently
        # reading a partial history.
        rehydrated = seen_hashes
        for entry_hash in is_ref_hashes:
            if entry_hash not in rehydrated and entry_hash not in exempt_hashes:
                raise ValueError(
                    f"IS ledger references audit entry {entry_hash!r} for "
                    f"tenant_tag={tag!r} but the sidecar holds no such row — "
                    f"signed history has been truncated or lost"
                )
        return entries

    def adopt_legacy_is_refs(self) -> int:
        """One-time EXPLICIT migration for pre-sidecar ledgers (codex
        round-46 P1) — returns the number of legacy references baselined.

        A deployment upgraded in place has IS `audit:` references written by
        the pre-sidecar runtime, which produced then DROPPED every full
        signed entry — no sidecar can exist, so the round-36 absence guard
        (correctly protecting against deletion) would wedge every append and
        full-entry read permanently, and the only documented escape (reset
        BOTH ledgers) would destroy unrelated workflow history in the shared
        IS ledger. This method creates the sidecar with a single
        `legacy_baseline` record enumerating every existing IS audit
        reference; those identities are thereafter exempt from coverage
        checks (their entries are unrecoverable BY CONSTRUCTION, an
        operator-acknowledged fact, not a loss event) while every
        post-adoption append gets full round-40 coverage protection.

        Adoption is deliberately NOT automatic: silently baselining on first
        touch would let a genuinely deleted sidecar masquerade as a legacy
        upgrade, re-opening the exact loss-masking hole round-36 closed. The
        operator runs this once, per upgraded deployment, while no writer is
        active. Refuses to run when a sidecar already exists. A forged
        baseline written by an attacker with sidecar write access sits in
        the same adversarial-filesystem tier as mutate-and-restore-mtime —
        dispositioned to the B-47 read-time verifier arc.
        """
        with self._sidecar_thread_lock, cross_process_write_lock(self._sidecar_path):
            if self._sidecar_path.exists():
                raise ValueError(
                    f"audit sidecar {self._sidecar_path} already exists — "
                    f"adopt_legacy_is_refs() is only for pre-sidecar ledgers "
                    f"upgraded in place; a missing-entry condition on an "
                    f"EXISTING sidecar is loss, not legacy"
                )
            legacy: list[list[str]] = []
            for is_entry in read_ledger(self.ledger_writer.handle):
                action_id = is_entry.action_id
                if not action_id.startswith(f"{self._ACTION_ID_PREFIX}:"):
                    continue
                prefix_and_tag, entry_hash = action_id.rsplit(":", 1)
                tag = prefix_and_tag[len(f"{self._ACTION_ID_PREFIX}:") :]
                legacy.append([tag, entry_hash])
            encoded = (
                json.dumps({"legacy_baseline": legacy}, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            with os.fdopen(self._open_sidecar_for_append(), "ab") as fh:
                fh.write(encoded)
                fh.flush()
                os.fsync(fh.fileno())
            if sys.platform != "win32":
                dir_fd = os.open(str(self._sidecar_path.parent), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            index = self._sidecar_index
            index.digests.clear()
            index.redaction_tails.clear()
            index.legacy_exempt = {(pair[0], pair[1]) for pair in legacy}
            index.offset = len(encoded)
            index.prefix_hash = hashlib.sha256(encoded)
            post = self._sidecar_path.stat()
            index.inode = post.st_ino
            index.mtime_ns = post.st_mtime_ns
            # Item (g): a legacy adoption rebuilds the index wholesale —
            # persist immediately so the (rare, potentially huge) baseline
            # fold never repeats at the next cold start.
            self._write_index_snapshot_locked()
            return len(legacy)

    @contextlib.contextmanager
    def tenant_transaction(self, tenant_id: str | None) -> Any:
        """Atomic tail-read + compose + append transaction — B-50 item (i).

        Holds the FULL writer lock stack — the per-ledger append lock, the
        sidecar thread lock, and the cross-process sidecar write flock —
        across everything done inside the `with` block, so two processes
        can no longer both read the same durable family tail and sign
        different successors against one predecessor (the pre-B-50 residual
        documented since PR B1 round 13). The yielded handle exposes
        UNLOCKED-INNER variants (POSIX `flock` is non-reentrant across
        separately opened descriptors — a plain outer hold around the
        locking public methods would self-deadlock; codex round-6 on the
        disposition leg). POSIX-only atomicity: the flock half is a win32
        no-op per the documented B-45 platform posture.
        """
        with _append_lock_for(self.ledger_writer.handle.canonical_path):
            with self._sidecar_thread_lock, cross_process_write_lock(self._sidecar_path):
                yield _AuditWriterTenantTransaction(self, tenant_id)

    def read_for_tenant(self, tenant_id: str | None) -> list[StateLedgerEntry]:
        """Tenant-scoped reader (C-OD-21 §21.1 cross-tenant separation surface).

        Returns every IS entry whose `action_id` scopes EXACTLY to the
        tenant's tag. Matching parses from the right (codex round-45 P2):
        `entry_hash` is hex-64 and never contains ':', so
        `action_id.rsplit(":", 1)[0]` recovers `audit:<tag>` exactly — a
        plain `audit:<tag>:` prefix test also matched tenants whose IDs are
        colon-extensions of `tag` (e.g. `tenant:west` under `tenant`),
        leaking refs across the C-OD-21 §21.1 separation surface and making
        the sidecar coverage check falsely report intact history as
        truncated. Reads the underlying JSONL file fresh (no in-process
        cache); safe across concurrent writers (the IS read returns a
        snapshot).
        """
        scope = f"{self._ACTION_ID_PREFIX}:{self._tenant_tag(tenant_id)}"
        entries = read_ledger(self.ledger_writer.handle)
        return [e for e in entries if e.action_id.rsplit(":", 1)[0] == scope]

    def read_all(self) -> list[StateLedgerEntry]:
        """Cross-tenant reader — returns every persisted audit-wrapped entry.

        Use restricted to runtime-internal verification surfaces (e.g.,
        `RunResult.audit_ledger_head_hash` derivation per C-RT-09 §9.1).
        Tenant-scoped consumers must use `read_for_tenant`.
        """
        entries = read_ledger(self.ledger_writer.handle)
        prefix = f"{self._ACTION_ID_PREFIX}:"
        return [e for e in entries if e.action_id.startswith(prefix)]


class _AuditWriterTenantTransaction:
    """Handle yielded by `RuntimeAuditLedgerWriter.tenant_transaction`.

    Both operations assume the transaction's lock stack is HELD — they call
    the writer's unlocked-inner cores and must never be used outside the
    `with` block (the handle is deliberately private and unexported).
    """

    __slots__ = ("_tenant_id", "_writer")

    def __init__(self, writer: RuntimeAuditLedgerWriter, tenant_id: str | None) -> None:
        self._writer = writer
        self._tenant_id = tenant_id

    def append(self, audit_entry: AuditLedgerEntry) -> WriteResult:
        return self._writer._append_core(  # pyright: ignore[reportPrivateUsage]
            self._tenant_id, audit_entry, sidecar_locks_held=True
        )

    def redaction_family_tail(self) -> str | None:
        """The durable redaction-family tail hash for this tenant, or None
        when the family has no (recoverable) entries — O(delta): heals +
        folds any bytes other processes appended (under the held flock),
        then answers from the transactionally maintained index (codex
        round-1 on the B-50 landing: a full rehydration per append was
        O(history) on the span-finalization hot path).
        """
        writer = self._writer
        if not writer._sidecar_path.exists():  # pyright: ignore[reportPrivateUsage]
            return None
        # Mirror the append core's coverage gate (codex round-2 on the B-50
        # landing): a full fold performed HERE warms the index, so the
        # subsequent txn.append() would see offset > 0 and skip ITS
        # round-40 coverage check — a boundary-truncated sidecar folded at
        # tail-lookup time would mask incomplete history.
        folded_from_zero = writer._sidecar_index.offset == 0  # pyright: ignore[reportPrivateUsage]
        writer._heal_torn_tail_locked()  # pyright: ignore[reportPrivateUsage]
        rescanned = writer._refresh_sidecar_index_locked()  # pyright: ignore[reportPrivateUsage]
        if folded_from_zero or rescanned:
            writer._assert_is_refs_covered_locked()  # pyright: ignore[reportPrivateUsage]
        tag = writer._tenant_tag(self._tenant_id)  # pyright: ignore[reportPrivateUsage]
        return writer._sidecar_index.redaction_tails.get(tag)  # pyright: ignore[reportPrivateUsage]


@dataclass(frozen=True, slots=True)
class AuditWriterStage:
    """Frozen result of stage 4 OD audit-writer materialization.

    The bootstrap orchestrator (U-RT-43) binds `writer` to
    `HarnessContext.audit_writer`. Mirrors the L5 / L6 stage shape.
    """

    writer: RuntimeAuditLedgerWriter


def materialize_audit_writer_stage(
    config: RuntimeConfig,
    ledger_writer: LedgerWriter,
    *,
    time_source: Callable[[], Timestamp] | None = None,
) -> AuditWriterStage:
    """Build the stage 4 OD audit-writer registry.

    The writer is constructed against the pre-existing IS `LedgerWriter`
    from stage 1 (U-RT-12); no new IS handle is created here — the audit
    ledger shares the IS hash chain with the runtime's other audit/event
    emissions per the cross-axis edge §700 commitment.

    `config` is read for API consistency with the L5 / L6 composers; no
    field is consumed at HEAD (the writer is stateless beyond its bound
    `LedgerWriter` + injected `time_source`).
    """
    _ = config
    ts: Callable[[], Timestamp] = (
        time_source if time_source is not None else lambda: datetime.now(UTC)
    )
    return AuditWriterStage(
        writer=RuntimeAuditLedgerWriter(ledger_writer=ledger_writer, time_source=ts),
    )
