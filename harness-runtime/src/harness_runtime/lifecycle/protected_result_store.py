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
import hashlib
import logging
import os
import pickle
import tempfile
import time
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness_runtime.lifecycle.memory_tool_encrypted import FernetLike

__all__ = [
    "ProtectedResultStore",
    "ProtectedStoreCrossTenantError",
    "ProtectedStoreTamperError",
    "ResultRefValue",
    "UnresolvableResultRef",
    "compose_composite_key",
    "resolve_result_ref",
]

_UNTENANTED_TAG = "_untenanted"
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


def _encode_tenant_tag(tag: str) -> str:
    """codex [P2] on the B-65-A CP-side arc: hex-encode the tag before
    composing the key — a raw tag containing `:` (a valid tenant_id per
    `normalize_tenant_scope`, e.g. `"org:west"`) would otherwise collide with
    the key's own `tag:uuid` separator, making `read()`'s `split(":", 1)[0]`
    extract only `"org"` and wrongly refuse the OWNING tenant's own read.
    Hex is deterministic, reversible, and never contains `:`."""
    return tag.encode("utf-8").hex()


def compose_composite_key(tenant_id: str | None) -> str:
    """Full-strength tenant-composite key — widens the 48-bit
    `uuid4().hex[:12]` carrier default (spec v1.103 §14.8.11) to a full
    uuid4 composed with the normalized tenant scope."""
    tag = normalize_tenant_scope(tenant_id)
    encoded_tag = _encode_tenant_tag(tag if tag is not None else _UNTENANTED_TAG)
    return f"{encoded_tag}:{uuid.uuid4().hex}"


@dataclasses.dataclass(frozen=True, slots=True)
class _StoredEnvelope:
    """The versioned serialization envelope (spec v1.103 §14.8.11 — non-
    Mapping/arbitrary-object results stored as an OPAQUE byte-envelope +
    type tag, never lossy coercion)."""

    tenant_id: str | None
    type_tag: str
    serializer_version: int
    written_at: float
    payload: bytes


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
        self._root = root
        self._codec = codec
        self._ttl_seconds = ttl_seconds
        self._last_gc_at = 0.0

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
        tag = normalize_tenant_scope(tenant_id)
        composite_key = compose_composite_key(tenant_id)

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

        self._maybe_opportunistic_gc_sweep()
        return composite_key

    def _publish_atomic(self, entry_path: Path, data: bytes) -> None:
        """Crash-atomic durable publication (spec v1.103 §14.8.11, codex
        round-7 + round-10 on the spec PR): temp-bytes fsync -> atomic
        no-replace commit (`os.link` — raises `FileExistsError` if the
        destination already exists, the write-once guard itself, no
        TOCTOU-racy pre-check) -> DESTINATION-directory fsync AFTER the
        commit, before returning. A crash before the commit leaves NO
        destination entry; a crash after leaves a complete, retrievable one.
        """
        self._root.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=self._root, prefix=".tmp-")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.link(tmp_name, entry_path)
        finally:
            os.unlink(tmp_name)
        self._fsync_dir(self._root)

    def read(self, tenant_id: str | None, composite_key: str) -> object:
        """Idempotent, tenant-bound retrieval (spec v1.103 §14.8.11).

        A cross-tenant attempt or tampered/wrong-key ciphertext refuses
        TYPED before any deserialization runs.
        """
        owning_tag_encoded = composite_key.split(":", 1)[0]
        expected_tag = normalize_tenant_scope(tenant_id)
        expected_tag_str = expected_tag if expected_tag is not None else _UNTENANTED_TAG
        if owning_tag_encoded != _encode_tenant_tag(expected_tag_str):
            raise ProtectedStoreCrossTenantError(
                f"composite key owned by a different tenant scope than "
                f"retrieval attempted under {expected_tag_str!r}"
            )
        entry_path = self._entry_path(composite_key)
        ciphertext = entry_path.read_bytes()
        try:
            plaintext = self._codec.decrypt(ciphertext)
        except Exception as exc:
            raise ProtectedStoreTamperError(
                "ciphertext failed authentication — wrong key or tampered bytes"
            ) from exc
        envelope: _StoredEnvelope = pickle.loads(plaintext)
        # codex [P1] on this arc — the composite-key pre-check above only proves
        # the REQUESTED path claims the right tenant; under writable-disk
        # tampering (a valid ciphertext copied to a forged composite-key path),
        # the SHARED Fernet key still authenticates it, so decryption alone
        # cannot catch the swap. Bind the DECRYPTED envelope's own `tenant_id`
        # to the request too — the second half of tenant-bound retrieval.
        if envelope.tenant_id != expected_tag:
            raise ProtectedStoreCrossTenantError(
                "decrypted envelope tenant scope does not match the composite "
                "key's claimed scope or the retrieval request — refusing "
                "(disk-tamper / forged-reference guard)"
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
        """
        current_time = now if now is not None else time.time()
        expired: list[str] = []
        if not self._root.exists():
            return expired
        for entry_path in self._root.glob("*.entry"):
            try:
                plaintext = self._codec.decrypt(entry_path.read_bytes())
                envelope: _StoredEnvelope = pickle.loads(plaintext)
                written_at = envelope.written_at
                tenant_tag: str | None = envelope.tenant_id
            except Exception:
                # codex [P2] on this arc — an undecryptable entry (a DEK
                # rotation invalidating the key, or genuine corruption) must
                # NOT be skipped forever: without a fallback age signal it
                # would never expire, defeating the bounded-retention
                # guarantee. Fall back to the filesystem's own mtime (a
                # trusted, always-available age signal) rather than treating
                # "unreadable" as "immortal".
                try:
                    written_at = entry_path.stat().st_mtime
                except OSError:
                    continue
                tenant_tag = None
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
        self._last_gc_at = current_time
        return expired

    def _maybe_opportunistic_gc_sweep(self) -> None:
        now = time.time()
        if now - self._last_gc_at >= _OPPORTUNISTIC_GC_INTERVAL_SECONDS:
            self.gc_sweep(now=now)

    @staticmethod
    def _fsync_dir(directory: Path) -> None:
        """fsync a directory so a freshly-linked entry's dirent is durable.

        Best-effort: directory fsync is unsupported on some platforms/
        filesystems, where it is a no-op rather than a failure (mirrors
        `EngineOutputStore._fsync_dir`).
        """
        try:
            dir_fd = os.open(directory, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        except OSError:
            pass
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
