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

import hashlib
import json
import os
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from harness_is.cross_process_ledger_lock import (
    cross_process_read_lock,
    cross_process_write_lock,
)
from harness_is.state_ledger_entry_schema import Identifier, StateLedgerEntry, Timestamp
from harness_is.state_ledger_write import (
    EntryPayload,
    WriteKey,
    WriteResult,
    read_ledger,
)
from harness_od.audit_ledger_types import AuditLedgerEntry, compute_entry_hash

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

    __slots__ = ("digests", "inode", "mtime_ns", "offset")

    def __init__(self) -> None:
        self.digests: dict[tuple[str, str], str] = {}
        self.offset: int = 0
        self.inode: int = -1
        self.mtime_ns: int = -1


def _full_entry_digest(entry: AuditLedgerEntry) -> str:
    """Canonical digest over the COMPLETE signed entry (round-19 identity)."""
    return hashlib.sha256(entry.model_dump_json().encode("utf-8")).hexdigest()


_SIDECAR_LOCKS: dict[str, threading.Lock] = {}
_SIDECAR_LOCKS_GUARD = threading.Lock()


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

    @classmethod
    def _tenant_tag(cls, tenant_id: str | None) -> str:
        """Resolve the tenant scoping tag for an append/read call."""
        return tenant_id if tenant_id else cls._SINGLE_TENANT_TAG

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
        self._append_sidecar_line_if_missing(tenant_id, audit_entry)
        return self.ledger_writer.append(payload, write_key)

    def _sidecar_line_for(self, tenant_id: str | None, audit_entry: AuditLedgerEntry) -> str:
        return json.dumps(
            {
                "tenant_tag": self._tenant_tag(tenant_id),
                "entry": audit_entry.model_dump(mode="json"),
            },
            separators=(",", ":"),
        )

    def _open_sidecar_for_append(self) -> int:
        """Open (creating 0600 if absent) the sidecar for appending.

        Owner-only permissions at creation (out-of-family Codex P1 on the
        PR-B1 landing): the redaction-token path persists ORIGINAL PII /
        secret text under `audit.redaction_token.raw_value`, so under the
        common `022` umask a plain `open("a")` would land that content
        world-readable on shared hosts. `os.open` applies the 0600 mode only
        at creation — an operator who deliberately re-permissioned an
        existing sidecar is not fought.
        """
        return os.open(self._sidecar_path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)

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
        """
        if not self._sidecar_path.exists():
            return
        size = self._sidecar_path.stat().st_size
        if size == 0:
            return
        with self._sidecar_path.open("rb") as fh:
            fh.seek(-1, os.SEEK_END)
            if fh.read(1) == b"\n":
                return
            fh.seek(0)
            data = fh.read()
        keep = data.rfind(b"\n") + 1  # 0 when no completed record exists
        os.truncate(self._sidecar_path, keep)

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
        tag = self._tenant_tag(tenant_id)
        line = self._sidecar_line_for(tenant_id, audit_entry)
        with self._sidecar_thread_lock, cross_process_write_lock(self._sidecar_path):
            self._heal_torn_tail_locked()
            self._refresh_sidecar_index_locked()
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
                return
            encoded = (line + "\n").encode("utf-8")
            created = not self._sidecar_path.exists()
            with os.fdopen(self._open_sidecar_for_append(), "ab") as fh:
                fh.write(encoded)
                fh.flush()
                # Durability BEFORE the IS ref lands (codex round-23): a bare
                # write+close only reaches the page cache — power loss after
                # the IS append could keep the ref while the signature row
                # was never durable, defeating the sidecar-first guarantee.
                os.fsync(fh.fileno())
            if created and sys.platform != "win32":
                # Directory-entry durability for the newly created file
                # (mirrors the shutdown-path dir-fsync; POSIX-only per the
                # documented B-45 Windows posture).
                dir_fd = os.open(str(self._sidecar_path.parent), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            # Our own write never needs re-parsing: record it in the index
            # and advance past it.
            self._sidecar_index.digests[identity] = incoming_digest
            self._sidecar_index.offset += len(encoded)
            post = self._sidecar_path.stat()
            self._sidecar_index.inode = post.st_ino
            self._sidecar_index.mtime_ns = post.st_mtime_ns

    def _refresh_sidecar_index_locked(self) -> None:
        """Incrementally fold NEW sidecar bytes into the membership index —
        MUST be called with both locks held, after the torn-tail heal.

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
        if truncated or inode_changed or same_size_mutated:
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
        if st is not None and size == index.offset:
            index.inode = st.st_ino
            index.mtime_ns = st.st_mtime_ns
            return
        if st is None:
            return
        with self._sidecar_path.open("rb") as fh:
            fh.seek(index.offset)
            delta = fh.read(size - index.offset)
        # The heal ran under this same lock, so the region ends on a newline;
        # every split segment is a complete record.
        for raw in delta.split(b"\n"):
            if not raw.strip():
                continue
            row = json.loads(raw)
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
            index.digests[(row["tenant_tag"], entry.entry_hash)] = _full_entry_digest(entry)
        index.offset = size
        post = self._sidecar_path.stat()
        index.inode = post.st_ino
        index.mtime_ns = post.st_mtime_ns

    def read_full_entries_for_tenant(self, tenant_id: str | None) -> list[AuditLedgerEntry]:
        """Tenant-scoped FULL-entry reader over the item-(e) sidecar.

        Rehydrates every persisted `AuditLedgerEntry` (payload +
        signature_attrs + entry_hash) for `tenant_id` — the surface a
        verifier needs to check real signatures after restart, which the
        ref-only `read_for_tenant` cannot provide. Returns `[]` when the
        sidecar does not exist yet (no audit entry has ever been appended
        through this writer). A malformed line fails loud — a corrupt
        audit-entry sidecar must never be silently skipped.
        """
        tag = self._tenant_tag(tenant_id)
        if not self._sidecar_path.exists():
            return []
        entries: list[AuditLedgerEntry] = []
        # B-40 shared read lock (side-effect-free: never O_CREAT, never mkdir)
        # — excludes a concurrent writer's partial line once the lock file
        # exists; the brand-new-file window carries the documented B-46
        # residual, identical to the main-ledger read path. The per-path
        # thread lock adds the SAME-PROCESS half (codex round-26): on
        # Windows the cross-process lock is a no-op, so a verifier racing a
        # writer thread in one process needs this to never observe a
        # partially written record.
        with self._sidecar_thread_lock, cross_process_read_lock(self._sidecar_path):
            with self._sidecar_path.open(encoding="utf-8") as fh:
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
                    if row["tenant_tag"] != tag:
                        continue
                    entries.append(AuditLedgerEntry.model_validate(row["entry"]))
        return entries

    def read_for_tenant(self, tenant_id: str | None) -> list[StateLedgerEntry]:
        """Tenant-scoped reader (C-OD-21 §21.1 cross-tenant separation surface).

        Returns every IS entry whose `action_id` begins with the tenant's
        `audit:<tag>:` prefix. Entries from other tenants are excluded.
        Reads the underlying JSONL file fresh (no in-process cache); safe
        across concurrent writers (the IS read returns a snapshot).
        """
        tag = self._tenant_tag(tenant_id)
        prefix = f"{self._ACTION_ID_PREFIX}:{tag}:"
        entries = read_ledger(self.ledger_writer.handle)
        return [e for e in entries if e.action_id.startswith(prefix)]

    def read_all(self) -> list[StateLedgerEntry]:
        """Cross-tenant reader — returns every persisted audit-wrapped entry.

        Use restricted to runtime-internal verification surfaces (e.g.,
        `RunResult.audit_ledger_head_hash` derivation per C-RT-09 §9.1).
        Tenant-scoped consumers must use `read_for_tenant`.
        """
        entries = read_ledger(self.ledger_writer.handle)
        prefix = f"{self._ACTION_ID_PREFIX}:"
        return [e for e in entries if e.action_id.startswith(prefix)]


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
