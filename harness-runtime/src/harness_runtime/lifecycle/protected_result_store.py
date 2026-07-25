"""Protected post-effect result store (RATIFIED B-65 Class 2 fork §3b).

Implements `Spec_Harness_Runtime_v1.md` v1.103 §14.8.11 — the DEDICATED
recovery store for `PostEffectAuditSigningError.result` (`audit_signing_
errors.py:65`) payloads. `EngineOutputStore` is FORECLOSED per the fork
(plaintext JSONL; no tenant-authorized lookup; Mapping-only; a signing-KMS
outage payload may hold tenant prompts/PII/credentials — plaintext storage
of that under an outage is the exact defect this store exists to close).

Encryption reuses the `FernetLike` structural codec already established by
`memory_tool_encrypted.py` (`B-MEMORY-SURFACE-BACKEND-IMPLS`, C-RT-22) rather
than introducing a second at-rest-encryption idiom — `cryptography` stays a
lazily-imported optional dependency at the composition-root factory (this
module never imports it directly, mirroring `memory_tool_registry_factory.
_create_fernet_from_key`).

Constructor performs NO I/O (effects at the boundaries) — directory creation
and encryption happen at `write_once`/`read`, never at construction.
"""

from __future__ import annotations

import dataclasses
import errno
import hashlib
import logging
import os
import pickle
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness_runtime.lifecycle.memory_tool_encrypted import FernetLike

__all__ = [
    "ProtectedResultStore",
    "ProtectedStoreCrossTenantError",
    "ProtectedStoreEntryNotFoundError",
    "ProtectedStoreTamperError",
    "ResultRefValue",
    "UnresolvableResultRef",
    "compose_composite_key",
    "resolve_result_ref",
]

#: Mirrors OD v1.34 §21.2.1 row 2's `_normalize_tenant_tag` None-passthrough /
#: empty-string-refused contract by CROSS-REFERENCE (Runtime cannot import
#: harness_od's private `_normalize_tenant_tag` across the axis boundary —
#: this is Runtime's own local normalization with the same semantics).
_RESERVED_SIDECAR_TENANT_TAG = "_single"

logger = logging.getLogger("harness.runtime.protected_result_store")

#: Opportunistic GC: a write triggers a sweep at most this often (periodic-
#: or-opportunistic per spec v1.103 §14.8.11, codex round-10 on the spec PR —
#: a long-lived daemon that never restarts must still bound the store).
_OPPORTUNISTIC_GC_INTERVAL_SECONDS = 300.0

#: B-68 codex round 2 [P1] x2: publication and `gc_sweep()` must mutually
#: exclude even across multiple `ProtectedResultStore` INSTANCES sharing one
#: on-disk directory — the daemon composition root constructs a FRESH
#: instance per `run()`/`resume()` bootstrap (`stage_4_od.py`), so an
#: instance-scoped `threading.Lock` attribute would not exclude a
#: concurrent BOOTSTRAP's sweep. Keyed by the resolved root path (module-
#: wide, not per-instance); `threading.Lock` (not `asyncio.Lock`) because
#: `gc_sweep` is invoked off-loop via `run_off_loop_detach_on_cancel` — a
#: real OS-thread boundary an asyncio-only lock would not cross.
_root_locks: dict[str, threading.Lock] = {}
_root_locks_guard = threading.Lock()


def _lock_for_root(root: Path) -> threading.Lock:
    # codex round 3 [P2]: keyed by RESOLVED path, not the raw `str(root)` —
    # two filesystem-equivalent spellings of the same directory (e.g. a
    # `..`-containing alias) would otherwise key different lock objects,
    # reopening the exact GC/publication race this lock exists to close.
    # `resolve()` is a read-only stat, not a mutating effect — it doesn't
    # create the directory or touch the codec, so it doesn't violate this
    # class's "constructor performs no I/O" discipline (module docstring);
    # `strict=False` (the default) never raises for a not-yet-existing path.
    #
    # codex round 6 [P2]: `resolve()` alone still under-normalizes on a
    # case-INSENSITIVE filesystem (macOS APFS default volumes) — two
    # differently-cased spellings of the same directory (e.g. `/Users/...`
    # vs `/users/...`) resolve to two DISTINCT strings even though they
    # name the identical inode, reopening the same aliasing race. Key on
    # true filesystem identity instead (`st_dev`, `st_ino` — the same pair
    # `os.path.samefile` compares).
    #
    # `_publish_lock` is now a PROPERTY (see `ProtectedResultStore`) rather
    # than a construction-time-cached attribute, specifically so this
    # function is never called before the directory is guaranteed to
    # exist — an earlier draft fell back to the resolved-path STRING when
    # `stat()` raised on a not-yet-created directory, but that reopened a
    # NEW race: a caller that accessed the lock before creation (the
    # string-keyed fallback) and one that accessed it after (the
    # inode-keyed identity) would get two DIFFERENT lock objects for the
    # SAME logical root. `mkdir` here — unconditional, before the stat —
    # closes that window by guaranteeing every access keys on identity;
    # `exist_ok=True` tolerates concurrent create-create races safely.
    resolved = root.resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    try:
        st = resolved.stat()
        key = f"{st.st_dev}:{st.st_ino}"
    except OSError:
        key = str(resolved)
    with _root_locks_guard:
        lock = _root_locks.get(key)
        if lock is None:
            lock = threading.Lock()
            _root_locks[key] = lock
        return lock


def normalize_tenant_scope(tenant_id: str | None) -> str | None:
    """The store's own tenant-tag normalization (Runtime-local; mirrors OD
    v1.34 §21.2.1 row 2's rule-set without importing OD's private helper).

    `None` passes through as `None` (the untenanted/single-tenant case); the
    empty string and the reserved `_single` sidecar literal are REFUSED — a
    caller must never hand a real tenant_id colliding with either sentinel.
    """
    if tenant_id is None:
        return None
    if tenant_id in ("", _RESERVED_SIDECAR_TENANT_TAG):
        raise ValueError(
            f"tenant_id must not be empty or the reserved sidecar tag "
            f"{_RESERVED_SIDECAR_TENANT_TAG!r} — pass None for the "
            f"untenanted/single-tenant case (got {tenant_id!r})"
        )
    return tenant_id


@dataclasses.dataclass(frozen=True, slots=True)
class UnresolvableResultRef:
    """Discriminated declaration replacing a live key when the store write
    (or the versioned serializer) fails (spec v1.103 §14.8.11 FAIL-CLOSED
    store-write disposition). Distinguishable from a resolvable `str` ref at
    the carrier field itself — CP folds (CP spec v1.103 §1 row 4) carry this
    value VERBATIM, never reading it as a live reference.
    """

    reason: str


#: The carrier's `result_ref` field type: a live resolvable key, or the
#: discriminated unresolvable declaration above.
ResultRefValue = str | UnresolvableResultRef


class ProtectedStoreCrossTenantError(RuntimeError):
    """Retrieval attempted under a tenant scope that does not own the entry
    (spec v1.103 §14.8.11 tenant-bound lookup — REFUSED TYPED)."""


class ProtectedStoreTamperError(RuntimeError):
    """Ciphertext failed authentication (wrong key or tampered bytes) —
    refused typed BEFORE any deserialization runs (spec v1.103 §14.8.11)."""


class ProtectedStoreEntryNotFoundError(FileNotFoundError):
    """`read()` found no entry at the requested composite key — refused
    TYPED (B-68 optional interim hardening) rather than a raw
    `FileNotFoundError` leaking `Path.read_bytes()`'s implementation detail.
    Subclasses `FileNotFoundError` so existing `except FileNotFoundError` /
    `pytest.raises(FileNotFoundError)` callers keep working unchanged."""


def _encode_tenant_tag(tag: str) -> str:
    """codex [P2] on the B-65-A CP-side arc: hex-encode the tag before
    composing the key — a raw tag containing `:` (a valid tenant_id per
    `normalize_tenant_scope`, e.g. `"org:west"`) would otherwise collide with
    the key's own `tag:uuid` separator, making `read()`'s `split(":", 1)[0]`
    extract only `"org"` and wrongly refuse the OWNING tenant's own read.
    Hex is deterministic, reversible, and never contains `:`."""
    return tag.encode("utf-8").hex()


def _encode_scope_prefix(tag: str | None) -> str:
    """Discriminated composite-key prefix for the untenanted (`None`) vs a
    real tenant scope — collision-free BY CONSTRUCTION regardless of the
    tenant's literal string value (codex [P2] round 11 on this arc). The
    round-7 scheme hex-encoded a reserved sentinel STRING for the `None`
    case and rejected any real tenant_id equal to that string to avoid a
    collision — but `RuntimeConfig.tenant_id`'s own validator reserves only
    `""`/`"_single"`, so a config-valid deployment named `_untenanted`
    silently lost ALL post-effect recovery (every write degraded to
    `UnresolvableResultRef`) under that fix. Prefixing with a marker
    character (`u`/`t`) outside `_encode_tenant_tag`'s hex alphabet
    (`0-9a-f`) makes the two branches disjoint for EVERY possible tenant
    string, so no literal needs reserving at all."""
    if tag is None:
        return "u"
    return f"t{_encode_tenant_tag(tag)}"


def compose_composite_key(tenant_id: str | None) -> str:
    """Full-strength tenant-composite key — widens the 48-bit
    `uuid4().hex[:12]` carrier default (spec v1.103 §14.8.11) to a full
    uuid4 composed with the normalized tenant scope."""
    tag = normalize_tenant_scope(tenant_id)
    encoded_tag = _encode_scope_prefix(tag)
    return f"{encoded_tag}:{uuid.uuid4().hex}"


@dataclasses.dataclass(frozen=True, slots=True)
class _StoredEnvelope:
    """The versioned serialization envelope (spec v1.103 §14.8.11 — non-
    Mapping/arbitrary-object results stored as an OPAQUE byte-envelope +
    type tag, never lossy coercion).

    `composite_key` (codex [P1] round 5 on this arc) binds the envelope to
    the EXACT reference it was written under — `tenant_id` alone only binds
    it to the tenant SCOPE, so under a writable-disk threat, copying tenant
    A's ciphertext from reference B's path onto reference A's path would
    still pass Fernet authentication AND the tenant-only check (both refs
    share tenant A), silently returning B's payload for a request naming
    A. Checking the full composite key at `read()` closes that gap.
    """

    tenant_id: str | None
    type_tag: str
    serializer_version: int
    #: Forensic/debugging record of when this write STARTED — NOT the TTL
    #: age authority (B-68: it's stamped before the encrypt+publish latency
    #: that can itself exceed a short TTL). `gc_sweep` ages entries off the
    #: entry file's own filesystem mtime instead; see `gc_sweep`'s docstring.
    written_at: float
    payload: bytes
    composite_key: str


class ProtectedResultStore:
    """Outage-independent, tenant-bound, encrypted-at-rest recovery store.

    The envelope path is INDEPENDENT of the audit-signing KMS by
    construction — the caller supplies a `FernetLike` codec wrapping a
    LOCALLY-held DEK (provisioning-time-wrapped), never the signing backend
    (spec v1.103 §14.8.11 — the carrier's primary trigger IS a signing-KMS
    outage; routing recovery through that same boundary loses the payload
    in exactly the scenario the store exists for).
    """

    _SERIALIZER_VERSION = 1

    def __init__(self, root: Path, *, codec: FernetLike, ttl_seconds: float) -> None:
        # codex round 4 [P2]: resolve ONCE here and use the SAME resolved
        # path for both all on-disk I/O (`self._root`) and the lock key —
        # otherwise a symlink retargeted between two constructions could
        # let two instances do I/O in the SAME new directory under
        # DIFFERENT locks, reopening the race this lock exists to close.
        self._root = root.resolve()
        self._codec = codec
        self._ttl_seconds = ttl_seconds
        self._last_gc_at = 0.0

    @property
    def _publish_lock(self) -> threading.Lock:
        # B-68 codex round 2 — module-wide, keyed by the root's filesystem
        # identity (not a fresh per-instance lock); see `_lock_for_root`'s
        # docstring. codex round 6 [P2]: recomputed on EVERY access rather
        # than cached once at construction, deliberately NOT because the
        # constructor avoids I/O (that's `_lock_for_root`'s own `mkdir`'s
        # job — see its docstring for why a cached, possibly-pre-creation
        # key would reopen a race) but because `_lock_for_root` is a
        # cheap, idempotent registry lookup, not a fresh allocation — a
        # property is the correct shape for a value that's always
        # re-derivable and never needs its own state.
        return _lock_for_root(self._root)

    def _entry_path(self, composite_key: str) -> Path:
        digest = hashlib.sha256(composite_key.encode("utf-8")).hexdigest()
        return self._root / f"{digest}.entry"

    def write_once(self, tenant_id: str | None, result: object) -> ResultRefValue:
        """Write `result` under a fresh tenant-composite key exactly once.

        Never raises for an expected failure class (collision / serializer /
        encryption / durable-publication I/O) — each converts to the
        discriminated `UnresolvableResultRef` so the ORIGINAL
        `PostEffectAuditSigningError` still propagates unobstructed at the
        raise site (spec v1.103 §14.8.11 FAIL-CLOSED write disposition).
        """
        # codex [P2] on this arc — sweep BEFORE composing/publishing THIS entry,
        # never after: a post-publish sweep call would see the just-written
        # entry too, and under a deployment-configured TTL shorter than this
        # write's own serialize+encrypt+fsync latency (valid per `gt=0.0`), it
        # would immediately GC the entry this same call is about to return a
        # live-looking ref for. Sweeping first can only ever touch OLDER
        # entries — this one doesn't exist yet.
        self._maybe_opportunistic_gc_sweep()
        # codex [P1] round 8 on this arc — this helper is reached ONLY via
        # the post-effect raise-site helper `resolve_result_ref`, itself
        # only called while constructing a `PostEffectAuditSigningError`
        # for an ALREADY-completed paid effect. An illegal `tenant_id` (the
        # `normalize_tenant_scope`-refused sentinel collision) is a real
        # caller-contract violation, but letting it raise HERE — inside the
        # danger window this whole store exists to guard — would replace
        # the typed carrier construction with a raw `ValueError`, which
        # `resolve_result_ref_off_loop`'s narrower catch doesn't fold, so
        # the caller's own `except AUDIT_SIGNING_HARD_FAILURES` never fires
        # and CP could treat an already-completed effect as an ordinary
        # resumable failure and redispatch it. Degrading to the same
        # `UnresolvableResultRef` disposition as every other expected
        # failure class below closes that gap without weakening the
        # boundary itself — `normalize_tenant_scope` called directly (or via
        # `read()`) outside this raise-site context still raises loudly.
        try:
            tag = normalize_tenant_scope(tenant_id)
            composite_key = compose_composite_key(tenant_id)
        except ValueError as exc:
            logger.error(
                "protected result store: illegal tenant_id (%r) at write-once raise site: %s",
                tenant_id,
                exc,
            )
            return UnresolvableResultRef(reason=f"illegal tenant_id: {exc}")

        try:
            serialized = pickle.dumps(result, protocol=self._SERIALIZER_VERSION + 4)
        except Exception as exc:
            logger.error(
                "protected result store: serialization failed for tenant=%s: %s",
                tag,
                exc,
            )
            return UnresolvableResultRef(reason=f"serialization failed: {type(exc).__name__}")

        envelope = _StoredEnvelope(
            tenant_id=tag,
            type_tag=type(result).__qualname__,
            serializer_version=self._SERIALIZER_VERSION,
            written_at=time.time(),
            payload=serialized,
            composite_key=composite_key,
        )
        try:
            ciphertext = self._codec.encrypt(
                pickle.dumps(envelope, protocol=self._SERIALIZER_VERSION + 4)
            )
        except Exception as exc:
            logger.error(
                "protected result store: encryption failed for tenant=%s: %s",
                tag,
                exc,
            )
            return UnresolvableResultRef(reason=f"encryption failed: {type(exc).__name__}")

        entry_path = self._entry_path(composite_key)
        try:
            self._publish_atomic(entry_path, ciphertext)
        except FileExistsError:
            # Write-once collision-safe refusal (spec v1.103 §14.8.11) — not
            # reachable in practice (composite key includes a fresh uuid4),
            # but the guard is a real contract term, PD-8-probed directly.
            logger.error(
                "protected result store: write-once collision at composite key for tenant=%s",
                tag,
            )
            return UnresolvableResultRef(reason="write-once refused: composite key already exists")
        except OSError as exc:
            logger.error(
                "protected result store: durable publication failed for tenant=%s: %s",
                tag,
                exc,
            )
            return UnresolvableResultRef(reason=f"store write failed: {type(exc).__name__}")

        return composite_key

    def _publish_atomic(self, entry_path: Path, data: bytes) -> None:
        """Crash-atomic durable publication (spec v1.103 §14.8.11, codex
        round-7 + round-10 on the spec PR): temp-bytes fsync -> atomic
        no-replace commit (`os.link` — raises `FileExistsError` if the
        destination already exists, the write-once guard itself, no
        TOCTOU-racy pre-check) -> DESTINATION-directory fsync AFTER the
        commit, before returning. A crash before the commit leaves NO
        destination entry; a crash after leaves a complete, retrievable one.

        B-68 codex round 2 [P1] x2 + round 4 [P1]: the WHOLE temp-file
        lifetime — creation, write+fsync, the commit, the mtime refresh
        (`gc_sweep`'s age authority), and that refresh's OWN durability —
        runs under `self._publish_lock`, the SAME lock `gc_sweep` holds for
        its whole sweep (including its `.tmp-*` crash-orphan reclaim loop).
        Round 2/3's fix locked only from `os.link` onward: a concurrent
        sweep could still classify this method's OWN in-flight `.tmp-*`
        file as a crash orphan (stale mtime under a short TTL + slow
        fsync) and unlink it before `os.link` ever ran, losing recovery
        for an already-completed paid effect when the subsequent `os.link`
        then raised `FileNotFoundError`. Holding the lock for the entire
        method closes that: `gc_sweep`'s tmp-cleanup loop can never run
        while a temp file is still in active use.
        """
        self._root.mkdir(parents=True, exist_ok=True)
        with self._publish_lock:
            fd, tmp_name = tempfile.mkstemp(dir=self._root, prefix=".tmp-")
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.link(tmp_name, entry_path)
                self._fsync_dir(self._root)
                # Refresh mtime to "now" — the temp file's mtime (set at
                # `handle.write()` above) predates this commit by however
                # long the fsync+link just took; `gc_sweep`'s age
                # authority must not under-report the true publish moment
                # (B-68 [P1] round 1).
                os.utime(entry_path, None)
                # Durably persist that refresh BEFORE releasing the lock —
                # a crash between `os.utime` and an fsync of its own could
                # lose the update on some filesystems (round 2 [P1]),
                # reintroducing the exact race on the NEXT process's
                # bootstrap sweep. `fsync` on an O_RDONLY fd is valid and
                # flushes the inode's metadata (including mtime).
                entry_fd = os.open(entry_path, os.O_RDONLY)
                try:
                    os.fsync(entry_fd)
                finally:
                    os.close(entry_fd)
            finally:
                os.unlink(tmp_name)

    def read(self, tenant_id: str | None, composite_key: str) -> object:
        """Idempotent, tenant-bound retrieval (spec v1.103 §14.8.11).

        A cross-tenant attempt or tampered/wrong-key ciphertext refuses
        TYPED before any deserialization runs.
        """
        owning_tag_encoded = composite_key.split(":", 1)[0]
        expected_tag = normalize_tenant_scope(tenant_id)
        if owning_tag_encoded != _encode_scope_prefix(expected_tag):
            raise ProtectedStoreCrossTenantError(
                f"composite key owned by a different tenant scope than "
                f"retrieval attempted under {expected_tag!r}"
            )
        entry_path = self._entry_path(composite_key)
        try:
            ciphertext = entry_path.read_bytes()
        except FileNotFoundError as exc:
            # B-68 optional interim hardening — refuse TYPED rather than
            # leak `Path.read_bytes()`'s raw `FileNotFoundError` (reached
            # e.g. after `ack_delete()`, TTL GC, or a caller-supplied
            # composite_key that was never written).
            raise ProtectedStoreEntryNotFoundError(
                f"no entry at composite key {composite_key!r}"
            ) from exc
        try:
            plaintext = self._codec.decrypt(ciphertext)
        except Exception as exc:
            raise ProtectedStoreTamperError(
                "ciphertext failed authentication — wrong key or tampered bytes"
            ) from exc
        envelope: _StoredEnvelope = pickle.loads(plaintext)
        # codex [P1] round 5 on this arc — a tenant-ONLY check (the prior
        # `envelope.tenant_id != expected_tag` form) only proves the
        # decrypted envelope belongs to the right TENANT, not the right
        # ENTRY: under writable-disk tampering, copying tenant A's
        # ciphertext from reference B's path onto reference A's path still
        # authenticates (same Fernet key) and still passes a tenant-only
        # check (both refs are tenant A's), silently returning B's payload
        # for a `read(tenant_a, ref_a)` call. Binding to the FULL
        # `composite_key` the envelope was written under is strictly
        # stronger (it already encodes the tenant tag as its prefix) and
        # closes that gap — the mismatch is refused before the wrong
        # payload is ever deserialized.
        if envelope.composite_key != composite_key:
            raise ProtectedStoreCrossTenantError(
                "decrypted envelope's composite key does not match the "
                "requested reference — refusing (disk-tamper / "
                "forged-reference guard)"
            )
        return pickle.loads(envelope.payload)

    def ack_delete(self, composite_key: str) -> None:
        """Deletion ONLY after an explicit durable repair acknowledgement —
        the caller is the repair flow's own completion marker (spec v1.103
        §14.8.11). Idempotent: deleting an already-absent entry is a no-op.
        """
        self._entry_path(composite_key).unlink(missing_ok=True)

    def gc_sweep(self, *, now: float | None = None) -> list[str]:
        """TTL sweep for unacknowledged entries (spec v1.103 §14.8.11).

        Expiry is a TYPED report-log line, never silent loss — the caller
        (bootstrap/shutdown hook, or the opportunistic in-write trigger)
        gets the expired composite-key digests back for its own reporting.

        Age is measured from the entry FILE's own filesystem mtime, never
        the encrypted envelope's embedded `written_at` (B-68 registered
        finding: `written_at` is stamped BEFORE serialization/encryption/
        `_publish_atomic`'s fsync+commit — a real, non-instantaneous gap
        under load or a large payload. A short deployment-configured TTL
        could then see a just-published, still-live entry as already
        expired the instant it becomes visible on disk, regardless of any
        concurrent sweep. `_publish_atomic` refreshes the entry's mtime to
        "now" AFTER its durable commit — the same trusted, always-available
        age signal already used below for undecryptable entries, now
        applied unconditionally rather than only as a decrypt-failure
        fallback. This sweep and that refresh mutually exclude via
        `self._publish_lock` (codex round 2 [P1] x2 — round 1's plain
        `os.utime` refresh still left a window between `os.link` (visible)
        and the refresh itself for a genuinely CONCURRENT sweep to observe
        the stale pre-fsync mtime, and didn't fsync the refresh, so a crash
        right after could lose it): closed for concurrent callers WITHIN
        this process (the lock is keyed by resolved root path, shared
        across every `ProtectedResultStore` instance the daemon constructs
        for the same on-disk directory — this daemon builds a FRESH
        instance per `run()`/`resume()` bootstrap, not one shared object).
        A separate OS PROCESS sharing this same directory is NOT covered by
        an in-process lock; that residual is registered, not silently
        assumed closed.
        """
        current_time = now if now is not None else time.time()
        expired: list[str] = []
        if not self._root.exists():
            return expired
        # B-68 codex round 2 [P1]: the whole sweep runs under the SAME lock
        # `_publish_atomic` holds around its commit + mtime refresh — a
        # sweep in progress can never observe an entry mid-publish (stale
        # pre-fsync mtime), and a publish in progress can never race a
        # sweep's read of its own just-refreshed mtime.
        with self._publish_lock:
            for entry_path in self._root.glob("*.entry"):
                try:
                    written_at = entry_path.stat().st_mtime
                except OSError:
                    continue
                tenant_tag: str | None = None
                try:
                    plaintext = self._codec.decrypt(entry_path.read_bytes())
                    envelope: _StoredEnvelope = pickle.loads(plaintext)
                    tenant_tag = envelope.tenant_id
                except Exception:
                    # codex [P2] on this arc — an undecryptable entry (a DEK
                    # rotation invalidating the key, or genuine corruption) must
                    # NOT be skipped forever: without a fallback age signal it
                    # would never expire, defeating the bounded-retention
                    # guarantee. `tenant_tag` stays `None` (unreadable) — the
                    # log line below still reports it, just without identity.
                    pass
                if current_time - written_at > self._ttl_seconds:
                    digest = entry_path.stem
                    try:
                        entry_path.unlink(missing_ok=True)
                    except OSError as exc:
                        # codex [P1] on this arc — a sweep-time unlink failure (e.g.
                        # permission denied) must NEVER propagate: `write_once()` calls
                        # this opportunistically, and an uncaught OSError here would
                        # replace the caller's typed `PostEffectAuditSigningError` with
                        # an unrelated GC error, defeating the at-most-once carrier
                        # entirely. Log + skip this entry; the sweep continues.
                        logger.error(
                            "protected result store: TTL-expired entry GC unlink failed "
                            "(digest=%s, tenant=%s): %s",
                            digest,
                            tenant_tag,
                            exc,
                        )
                        continue
                    expired.append(digest)
                    logger.warning(
                        "protected result store: TTL-expired entry GC'd "
                        "(digest=%s, tenant=%s, age_s=%.1f)",
                        digest,
                        tenant_tag,
                        current_time - written_at,
                    )
            # codex [P2] round 5 on this arc — a process KILLED between
            # `_publish_atomic`'s temp-write and its `finally: os.unlink(tmp_name)`
            # leaves a `.tmp-*` file behind indefinitely: this loop (and every
            # bootstrap/shutdown/opportunistic sweep, which all funnel through
            # this method) previously enumerated only `*.entry`, so repeated
            # crashes could accumulate stale ciphertext or exhaust disk with no
            # bound. `.tmp-*` files carry no envelope to decrypt (a crash mid-
            # write may leave them incomplete) — mtime is the only available age
            # signal, same fallback already used for undecryptable `.entry`
            # files above. Reuses the store's own TTL rather than a new config
            # surface (temp files never survive a normal write for more than
            # milliseconds, so any bound this generous only ever catches
            # genuine crash orphans).
            for tmp_entry_path in self._root.glob(".tmp-*"):
                try:
                    tmp_mtime = tmp_entry_path.stat().st_mtime
                except OSError:
                    continue
                if current_time - tmp_mtime > self._ttl_seconds:
                    try:
                        tmp_entry_path.unlink(missing_ok=True)
                    except OSError as exc:
                        logger.error(
                            "protected result store: crash-orphaned temp-file GC "
                            "unlink failed (%s): %s",
                            tmp_entry_path.name,
                            exc,
                        )
                        continue
                    logger.warning(
                        "protected result store: crash-orphaned temp-file GC'd (%s, age_s=%.1f)",
                        tmp_entry_path.name,
                        current_time - tmp_mtime,
                    )
        self._last_gc_at = current_time
        return expired

    def _maybe_opportunistic_gc_sweep(self) -> None:
        """Best-effort in-write housekeeping — never blocks the write.

        codex [P1] round 7 on this arc: called from `write_once` BEFORE its
        own try/except block, so an uncaught sweep exception (e.g. a
        directory-enumeration `PermissionError` inside `gc_sweep`) would
        propagate out of `write_once` entirely, replacing the caller's
        typed `UnresolvableResultRef` degradation with an unrelated raw
        exception — risking the raise-site caller (fed by an ALREADY-
        completed paid effect) falling through to generic retry/fallback
        handling instead of the fail-closed carrier path. The
        bootstrap/`shutdown()`-step-5b callers of `gc_sweep()` directly are
        unaffected — they already handle/report its exceptions themselves.
        """
        now = time.time()
        if now - self._last_gc_at >= _OPPORTUNISTIC_GC_INTERVAL_SECONDS:
            try:
                self.gc_sweep(now=now)
            except Exception as exc:
                logger.error(
                    "protected result store: opportunistic in-write GC sweep "
                    "failed (write proceeds regardless): %s",
                    exc,
                )

    #: Errno values meaning "directory fsync is unsupported here" — safe to
    #: swallow. Anything else (EIO, ENOSPC, ...) is a genuine durability
    #: failure and must propagate (codex [P1] round 5 on this arc).
    _FSYNC_UNSUPPORTED_ERRNOS = frozenset({errno.EINVAL, errno.ENOTSUP, errno.EOPNOTSUPP})

    @classmethod
    def _fsync_dir(cls, directory: Path) -> None:
        """fsync a directory so a freshly-linked entry's dirent is durable.

        Best-effort ONLY for genuinely-unsupported directory fsync (some
        platforms/filesystems raise EINVAL/ENOTSUP/EOPNOTSUPP rather than
        succeeding — the `EngineOutputStore._fsync_dir` precedent this
        mirrors swallows EVERY `OSError`, which let a REAL durability
        failure here — EIO, ENOSPC, a dying disk — pass silently, so
        `write_once` would publish a live-looking `composite_key` for an
        entry that might not survive a crash. Any OTHER `OSError`
        propagates to the caller's EXISTING typed-unresolvable path
        (`write_once`'s `except OSError` around `_publish_atomic`) —
        this method adds no new degradation path, it just stops
        swallowing the one case that path already exists to catch.
        """
        try:
            dir_fd = os.open(directory, os.O_RDONLY)
        except OSError as exc:
            # codex [P1] round 6 on this arc — the sole caller
            # (`_publish_atomic`) only reaches here AFTER `mkdir` +
            # `os.link` already succeeded on this SAME directory, so a
            # real open failure here (EIO, EMFILE, a permission change
            # mid-flight) is a genuine durability signal, not a
            # "directory fsync unsupported" case — swallowing it
            # unconditionally (the pre-fix behavior) let `write_once`
            # publish a live ref with no durability guarantee at all.
            # Same errno carve-out as the `fsync()` call below, for
            # symmetry — no platform is expected to hit it here.
            if exc.errno not in cls._FSYNC_UNSUPPORTED_ERRNOS:
                raise
            return
        try:
            os.fsync(dir_fd)
        except OSError as exc:
            if exc.errno not in cls._FSYNC_UNSUPPORTED_ERRNOS:
                raise
        finally:
            os.close(dir_fd)


def resolve_result_ref(
    store: ProtectedResultStore | None, tenant_id: str | None, result: object
) -> ResultRefValue:
    """The shared raise-site helper (all four `PostEffectClass` dispatchers):
    write `result` to `store` under `tenant_id` and return the resolved ref.

    `store is None` mirrors the composition-root's established
    "`None` = unit-test ergonomics, production wiring injects a real
    instance" convention (`RuntimeLLMDispatcher.cost_chain` et al.) — a
    dispatcher constructed without the store still raises the ORIGINAL
    `PostEffectAuditSigningError` correctly, just with an unresolvable ref
    naming why, rather than raising a second, unrelated error.
    """
    if store is None:
        return UnresolvableResultRef(reason="no protected result store configured")
    return store.write_once(tenant_id, result)
