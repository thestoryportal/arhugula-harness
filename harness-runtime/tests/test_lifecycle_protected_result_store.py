"""`ProtectedResultStore` unit tests (RATIFIED B-65 Class 2 fork §3b; Runtime
spec v1.103 §14.8.11). All tests exercise a real `cryptography` Fernet — this
module never monkeypatches the codec.
"""

from __future__ import annotations

import errno
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import (
    ProtectedResultStore,
    ProtectedStoreCrossTenantError,
    ProtectedStoreEntryNotFoundError,
    ProtectedStoreTamperError,
    UnresolvableResultRef,
    _encode_scope_prefix,
    compose_composite_key,
    normalize_tenant_scope,
)


def _store(tmp_path: Path, *, ttl_seconds: float = 86400.0) -> ProtectedResultStore:
    return ProtectedResultStore(
        tmp_path / "store", codec=Fernet(Fernet.generate_key()), ttl_seconds=ttl_seconds
    )


class _Unserializable:
    """Holds a live generator — `pickle.dumps` raises `TypeError` on it."""

    def __init__(self) -> None:
        self.gen = (x for x in range(3))


#: B-73 cross-process regression tests: standalone scripts run via
#: `subprocess` (a genuine separate OS process, its own fresh interpreter —
#: avoids both `multiprocessing`'s `fork`-after-lock-held deadlock hazard
#: and `spawn`'s pickle-by-module-name resolution, which this monorepo's
#: several same-named `tests` packages make ambiguous). A cold child
#: interpreter's own import of `cryptography` + `harness_runtime` alone
#: takes ~5s in this environment. Each script wraps `fcntl.flock` itself
#: (a codex [P2]-driven fix on the B-73 arc, round 3 — writing the
#: `ready_marker` any earlier, even "right before the call that contends
#: on the lock," only proves the child reached that call, not that it's
#: AT the `flock` attempt: `write_once()` still does real serialization +
#: Fernet encryption first, a genuine scheduling window a descheduled
#: child could stall in past the parent's bounded wait, letting a broken
#: fix's absence go undetected) — the wrapper writes `ready_marker` the
#: instant `fcntl.flock` is actually called, before delegating to the
#: real syscall, closing that window entirely. A `done_marker` written
#: after the call returns lets the parent observe completion, all
#: without any IPC primitive shared across the process boundary.
_B73_FLOCK_SIGNAL_WRAPPER = """
import fcntl as _fcntl
_real_flock = _fcntl.flock
def _signaling_flock(fd, op):
    Path(ready_marker).write_text("ready")
    return _real_flock(fd, op)
_fcntl.flock = _signaling_flock
"""

_B73_CHILD_WRITE_SCRIPT = (
    """
import sys
import time
from pathlib import Path
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore

store_dir, key, done_marker, ready_marker = sys.argv[1:5]
"""
    + _B73_FLOCK_SIGNAL_WRAPPER
    + """
store = ProtectedResultStore(Path(store_dir), codec=Fernet(key.encode()), ttl_seconds=86400.0)
# codex [P2] on the B-73 arc: a fresh store's _last_gc_at is 0.0, so this
# write_once() would otherwise ALSO trigger _maybe_opportunistic_gc_sweep()
# first -- which acquires the SAME cross-process lock via gc_sweep(),
# making this test pass even if _publish_atomic's OWN lock use were
# removed. Suppressing it isolates the assertion to _publish_atomic.
store._last_gc_at = time.time()
store.write_once("tenant-a", "written by a separate OS process")
Path(done_marker).write_text("done")
"""
)

_B73_CHILD_SWEEP_SCRIPT = (
    """
import sys
from pathlib import Path
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore

store_dir, key, done_marker, ready_marker = sys.argv[1:5]
"""
    + _B73_FLOCK_SIGNAL_WRAPPER
    + """
store = ProtectedResultStore(Path(store_dir), codec=Fernet(key.encode()), ttl_seconds=86400.0)
store.gc_sweep()
Path(done_marker).write_text("done")
"""
)


class _ProviderResponse:
    """Module-level (pickle requires a class resolvable by qualified name —
    a locally-defined class inside a test function is NOT picklable)."""

    def __init__(self, text: str) -> None:
        self.text = text

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _ProviderResponse) and other.text == self.text


# --- normalize_tenant_scope / compose_composite_key -------------------------


def test_normalize_tenant_scope_none_passes_through() -> None:
    assert normalize_tenant_scope(None) is None


def test_normalize_tenant_scope_refuses_empty_string() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        normalize_tenant_scope("")


def test_normalize_tenant_scope_refuses_reserved_sidecar_tag() -> None:
    with pytest.raises(ValueError, match="reserved sidecar tag"):
        normalize_tenant_scope("_single")


def test_compose_composite_key_is_full_strength_not_48_bit() -> None:
    """Widens the carrier's `uuid4().hex[:12]` (48 bits) to a full uuid4 (128
    bits) — mutation probe: truncating back to [:12] shrinks the hex segment
    below 32 chars and fails this witness."""
    key = compose_composite_key("tenant-a")
    hex_part = key.split(":", 1)[1]
    assert len(hex_part) == 32


def test_compose_composite_key_two_calls_never_collide() -> None:
    keys = {compose_composite_key("tenant-a") for _ in range(1000)}
    assert len(keys) == 1000


# --- write_once / read round trip -------------------------------------------


def test_write_once_then_read_round_trips_under_owning_tenant(tmp_path: Path) -> None:
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", {"payload": "value"})
    assert isinstance(ref, str)
    assert store.read("tenant-a", ref) == {"payload": "value"}


def test_write_once_none_tenant_round_trips_under_none(tmp_path: Path) -> None:
    store = _store(tmp_path)
    ref = store.write_once(None, "untenanted result")
    assert isinstance(ref, str)
    assert store.read(None, ref) == "untenanted result"


def test_cross_tenant_read_refused_typed(tmp_path: Path) -> None:
    """Fork §2 witness (d) half — dropping the tenant component from the key
    would let a cross-tenant read resolve; mutation probe: a `read()` that
    skips the owning-tag comparison lets this pass and fails."""
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", "secret payload")
    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read("tenant-b", ref)


def test_tenant_id_containing_colon_round_trips_under_owning_tenant(tmp_path: Path) -> None:
    """codex [P2] on the B-65-A CP-side arc: a tenant_id containing `:` (a
    valid tenant_id per `normalize_tenant_scope` — only the empty string and
    the reserved sidecar tag are refused, e.g. `"org:west"`) must still
    round-trip under its OWN tenant. Before the hex-encoding fix, the raw tag
    collided with the key's own `tag:uuid` separator, so `read()`'s
    `split(":", 1)[0]` extracted only `"org"` and the OWNING tenant got a
    false cross-tenant refusal reading its own data."""
    store = _store(tmp_path)
    ref = store.write_once("org:west", "the owning tenant's own payload")
    assert store.read("org:west", ref) == "the owning tenant's own payload"
    # A genuinely different tenant is still refused (the fix must not widen
    # the refusal to a no-op).
    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read("org:east", ref)


def test_disk_tampered_forged_reference_refused_after_decrypt(tmp_path: Path) -> None:
    """codex [P1] on the B-65-A CP-side arc: the composite-key pre-check alone
    only proves the REQUESTED path claims the right tenant — it cannot catch
    a writable-disk tamper where tenant-A's REAL encrypted entry is copied to
    a path whose composite key claims tenant-B's ownership (the shared Fernet
    key still authenticates it, so decryption succeeds). `read()` must ALSO
    bind the DECRYPTED envelope's own `tenant_id` to the request.

    Mutation probe: removing the post-decrypt `envelope.tenant_id` check
    makes this test return tenant-A's payload under tenant-B's read instead
    of raising."""
    store = _store(tmp_path)
    real_ref = store.write_once("tenant-a", "tenant-a's real secret")
    real_entry_path = store._entry_path(real_ref)  # type: ignore[arg-type]

    # Forge a composite key that CLAIMS tenant-b ownership, then copy tenant-a's
    # REAL ciphertext to that forged path (the disk-tamper threat model — the
    # attacker controls the filesystem but not the shared Fernet key).
    forged_ref = _encode_scope_prefix("tenant-b") + ":" + "f" * 32
    forged_entry_path = store._entry_path(forged_ref)  # type: ignore[arg-type]
    forged_entry_path.write_bytes(real_entry_path.read_bytes())

    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read("tenant-b", forged_ref)


def test_same_tenant_forged_reference_refused_by_composite_key_binding(
    tmp_path: Path,
) -> None:
    """codex [P1] round 5 on the B-65-A CP-side arc: the tenant-ONLY envelope
    check above closes the CROSS-tenant disk-tamper case but not the
    SAME-tenant one — copying tenant-a's real ciphertext from ref B's path
    onto ref A's path still authenticates (same Fernet key) AND still
    passes a tenant-only check (both refs are tenant-a's own), so
    `read(tenant_a, ref_a)` would silently return ref_b's payload instead
    of ref_a's. Binding the envelope to the FULL composite key it was
    written under closes this.

    Mutation probe: reverting the `envelope.composite_key != composite_key`
    check back to the tenant-only `envelope.tenant_id != expected_tag` form
    makes this test return ref_b's payload under ref_a's identity instead
    of raising."""
    store = _store(tmp_path)
    ref_a = store.write_once("tenant-a", "ref-a's real secret")
    ref_b = store.write_once("tenant-a", "ref-b's real secret")
    entry_a_path = store._entry_path(ref_a)  # type: ignore[arg-type]
    entry_b_path = store._entry_path(ref_b)  # type: ignore[arg-type]

    # Copy ref_b's real ciphertext onto ref_a's path — both belong to the
    # SAME tenant, so the tenant-only check alone would accept this.
    entry_a_path.write_bytes(entry_b_path.read_bytes())

    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read("tenant-a", ref_a)


def test_result_ref_resolves_preserved_payload_under_owning_tenant(tmp_path: Path) -> None:
    """Fork §2 witness (d): the preserved effect payload is recoverable via
    the ref under the OWNING tenant scope."""
    store = _store(tmp_path)
    payload = {"provider_response": "the completed effect result", "n": 42}
    ref = store.write_once("tenant-recovery", payload)
    assert store.read("tenant-recovery", ref) == payload


# --- write-once collision refusal -------------------------------------------


def test_write_once_existing_key_refused_typed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Collision-safe write-once (spec v1.103 §14.8.11): a write against an
    existing composite key is refused, never overwritten. Composite keys
    include a fresh uuid4 so natural collision is unreachable — force it by
    monkeypatching `compose_composite_key` to return a fixed key twice.
    Mutation probe: an implementation using `open(..., 'w')` (truncate-
    overwrite) instead of `os.link` no-replace would silently succeed here
    and fail this witness."""
    store = _store(tmp_path)
    fixed_key = _encode_scope_prefix("tenant-a") + ":" + "0" * 32
    monkeypatch.setattr(
        "harness_runtime.lifecycle.protected_result_store.compose_composite_key",
        lambda tenant_id: fixed_key,
    )
    first = store.write_once("tenant-a", "first payload")
    assert first == fixed_key
    second = store.write_once("tenant-a", "second payload — must NOT overwrite")
    assert isinstance(second, UnresolvableResultRef)
    assert "write-once" in second.reason
    # The original entry is untouched.
    assert store.read("tenant-a", fixed_key) == "first payload"


# --- fail-closed serialization / encryption ---------------------------------


def test_unserializable_result_composes_with_fail_closed_write_typed_serialization_failure(
    tmp_path: Path,
) -> None:
    """Runtime v1.103 §14.8.11 serialization-failure disposition (codex
    round-1 on the spec PR): a generator/open-handle/unsupported value's
    versioned-serializer failure composes with the fail-closed write
    disposition — the carrier surfaces without a resolvable ref, the typed
    declaration NAMES the serialization failure, the store persists nothing.
    Mutation probe: lossy coercion (e.g. `str(result)`) or a crash on the
    unsupported value fails this witness."""
    store = _store(tmp_path)
    before = list((tmp_path / "store").glob("*.entry")) if (tmp_path / "store").exists() else []
    ref = store.write_once("tenant-a", _Unserializable())
    assert isinstance(ref, UnresolvableResultRef)
    assert "serialization failed" in ref.reason
    after = list((tmp_path / "store").glob("*.entry")) if (tmp_path / "store").exists() else []
    assert after == before


def test_store_write_failure_carrier_surfaces_typed_unresolvable_ref(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The DISCRIMINATED unresolvable declaration replaces the live key when
    durable publication fails (I/O error). Mutation probe: swallowing the
    write failure and returning a plain string (that then reads as live)
    fails this witness."""
    store = _store(tmp_path)

    def _boom(self: ProtectedResultStore, entry_path: Path, data: bytes) -> None:
        raise OSError("simulated disk-full during publication")

    monkeypatch.setattr(ProtectedResultStore, "_publish_atomic", _boom)
    ref = store.write_once("tenant-a", "payload that cannot be recovered")
    assert isinstance(ref, UnresolvableResultRef)
    assert "store write failed" in ref.reason


# --- non-Mapping arbitrary-object round trip --------------------------------


def test_non_mapping_result_round_trips_via_byte_envelope_and_type_tag(tmp_path: Path) -> None:
    """AC 5 — non-Mapping/arbitrary-object results round-trip via an opaque
    byte-envelope + type tag, never lossy coercion."""
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", _ProviderResponse("recovered content"))
    resolved = store.read("tenant-a", ref)
    assert isinstance(resolved, _ProviderResponse)
    assert resolved.text == "recovered content"


# --- encrypted-at-rest confidentiality + tamper refusal ---------------------


def test_persisted_bytes_disclose_nothing(tmp_path: Path) -> None:
    """Encrypted-at-rest ENFORCED (codex round-5 on the spec PR): the on-disk
    bytes contain neither the plaintext payload nor a trivially-decodable
    encoding of it. Mutation probe: plaintext or base64-only storage through
    an independent local path fails this witness."""
    import base64

    store = _store(tmp_path)
    sentinel = "SENTINEL-8f3a2c-do-not-leak-this-tenant-prompt"
    store.write_once("tenant-a", sentinel)
    store_dir = tmp_path / "store"
    entry_paths = list(store_dir.glob("*.entry"))
    assert len(entry_paths) == 1
    raw = entry_paths[0].read_bytes()
    assert sentinel.encode("utf-8") not in raw
    assert base64.b64encode(sentinel.encode("utf-8")) not in raw
    assert sentinel.encode("ascii", errors="ignore") not in raw.lower()


def test_wrong_key_or_tampered_ciphertext_fails_typed_before_deserialization(
    tmp_path: Path,
) -> None:
    """A flipped ciphertext byte or a wrong DEK refuses typed BEFORE any
    deserialization runs. Mutation probe: deserializing tampered ciphertext
    (or silently returning it) fails this witness."""
    key = Fernet.generate_key()
    store = ProtectedResultStore(tmp_path / "store", codec=Fernet(key), ttl_seconds=86400.0)
    ref = store.write_once("tenant-a", "payload")
    entry_path = next((tmp_path / "store").glob("*.entry"))

    # Tampered ciphertext under the SAME key.
    original = entry_path.read_bytes()
    tampered = original[:-4] + bytes([b ^ 0xFF for b in original[-4:]])
    entry_path.write_bytes(tampered)
    with pytest.raises(ProtectedStoreTamperError):
        store.read("tenant-a", ref)

    # Wrong DEK entirely.
    entry_path.write_bytes(original)
    wrong_key_store = ProtectedResultStore(
        tmp_path / "store", codec=Fernet(Fernet.generate_key()), ttl_seconds=86400.0
    )
    with pytest.raises(ProtectedStoreTamperError):
        wrong_key_store.read("tenant-a", ref)


# --- outage-independence (the store's reason for being) ---------------------


def test_envelope_resolves_during_simulated_signing_kms_outage(tmp_path: Path) -> None:
    """The store's reason-for-being: retrieval succeeds while the signing
    backend is unavailable. Mutation probe: routing the envelope through the
    signing KMS fails this witness — this test constructs the store with
    ONLY a local Fernet codec (never a KMS-backed one) and never touches any
    signing backend, proving the envelope path has no such dependency."""
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", {"provider_response": "completed during outage"})

    def _kms_is_down() -> None:
        raise RuntimeError("signing KMS unreachable (simulated outage)")

    with pytest.raises(RuntimeError, match="signing KMS unreachable"):
        _kms_is_down()
    # The store's own read path never calls anything KMS-related — it
    # resolves regardless of the (simulated) outage above.
    assert store.read("tenant-a", ref) == {"provider_response": "completed during outage"}


# --- crash-atomic durable publication ---------------------------------------


def test_crash_between_temp_write_and_commit_leaves_no_destination_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Crash-atomic durable publication (codex round-7 on the spec PR):
    interrupt the publication after the temp write but before the atomic
    no-replace commit — the destination key does NOT exist, the write-once
    existence check does not wedge on a partial entry, and a subsequent
    write against the same key succeeds. Mutation probe: direct
    write-in-place publication (no temp-then-commit) fails this witness."""
    store = _store(tmp_path)
    fixed_key = _encode_scope_prefix("tenant-a") + ":" + "1" * 32
    monkeypatch.setattr(
        "harness_runtime.lifecycle.protected_result_store.compose_composite_key",
        lambda tenant_id: fixed_key,
    )

    real_link = os.link
    call_count = {"n": 0}

    def _link_then_crash(src: str, dst: object, **kwargs: object) -> None:
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise OSError("simulated crash between temp write and commit")
        real_link(src, dst, **kwargs)

    monkeypatch.setattr(os, "link", _link_then_crash)
    first = store.write_once("tenant-a", "first attempt — crashes before commit")
    assert isinstance(first, UnresolvableResultRef)
    assert not any((tmp_path / "store").glob("*.entry"))

    second = store.write_once("tenant-a", "second attempt — succeeds")
    assert second == fixed_key
    assert store.read("tenant-a", fixed_key) == "second attempt — succeeds"


# --- bounded retention: idempotent read / ack-gated deletion / TTL ----------


def test_retrieval_idempotent_across_repeated_reads(tmp_path: Path) -> None:
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", "read me twice")
    assert store.read("tenant-a", ref) == "read me twice"
    assert store.read("tenant-a", ref) == "read me twice"


def test_deletion_only_after_durable_repair_ack(tmp_path: Path) -> None:
    """Mutation probe: deleting on first read destroys the only recoverable
    copy and fails the re-read — this store's `read()` never deletes; only
    the explicit `ack_delete()` does."""
    store = _store(tmp_path)
    ref = store.write_once("tenant-a", "repair target")
    store.read("tenant-a", ref)  # a read alone must not delete
    assert store.read("tenant-a", ref) == "repair target"
    store.ack_delete(ref)
    with pytest.raises(FileNotFoundError):
        store.read("tenant-a", ref)


def test_read_missing_entry_raises_typed_not_found(tmp_path: Path) -> None:
    """B-68 optional interim hardening: a missing entry (never written, or
    already GC'd/ack-deleted) refuses via the discoverable typed subclass,
    not a bare `Path.read_bytes()` `FileNotFoundError`.

    Mutation probe: reverting `read()` to call `entry_path.read_bytes()`
    unguarded still satisfies `pytest.raises(FileNotFoundError)` (the typed
    class subclasses it) but fails the `isinstance` check below, since the
    raised instance would be the plain builtin, not the typed subclass."""
    store = _store(tmp_path)
    fake_ref = compose_composite_key("tenant-a")
    with pytest.raises(ProtectedStoreEntryNotFoundError) as exc_info:
        store.read("tenant-a", fake_ref)
    assert isinstance(exc_info.value, FileNotFoundError)


def test_ttl_expiry_gc_sweep_emits_typed_report_line(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Mutation probe: silent expiry (no log line) fails this witness."""
    store = _store(tmp_path, ttl_seconds=1.0)
    ref = store.write_once("tenant-a", "will expire")
    entry_path = next((tmp_path / "store").glob("*.entry"))
    assert entry_path.exists()

    import logging

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    expired = store.gc_sweep(now=time.time() + 10.0)
    assert len(expired) == 1
    assert not entry_path.exists()
    assert any("TTL-expired" in record.message for record in caplog.records)
    with pytest.raises(FileNotFoundError):
        store.read("tenant-a", ref)


def test_gc_sweep_expires_undecryptable_entry_via_mtime_fallback(tmp_path: Path) -> None:
    """codex [P2] on the B-65-A CP-side arc: an entry that fails to decrypt
    (a DEK rotation invalidating the key, or genuine corruption) must NOT be
    skipped forever — without a fallback age signal it would accumulate
    indefinitely, defeating the bounded-retention guarantee. `gc_sweep()`
    falls back to the filesystem's own mtime when decryption fails.

    Mutation probe: removing the `except Exception` fallback (reverting to a
    bare `continue`) makes this entry never expire — the assertion below
    would then fail."""
    store = _store(tmp_path, ttl_seconds=1.0)
    ref = store.write_once("tenant-a", "will become undecryptable")
    entry_path = store._entry_path(ref)  # type: ignore[arg-type]
    # Simulate a DEK rotation / corruption: overwrite with garbage bytes that
    # fail Fernet authentication, backdating the file's mtime past the TTL.
    entry_path.write_bytes(b"not valid ciphertext at all")
    old_time = time.time() - 10.0
    os.utime(entry_path, (old_time, old_time))

    expired = store.gc_sweep(now=time.time())
    assert len(expired) == 1
    assert not entry_path.exists()


def test_gc_sweep_ages_off_filesystem_mtime_not_embedded_written_at(tmp_path: Path) -> None:
    """B-68 registered finding: `write_once()` stamps `_StoredEnvelope.
    written_at` via `time.time()` BEFORE serialization/encryption/
    `_publish_atomic`'s fsync+commit — a real, non-instantaneous gap. Under
    a deployment TTL shorter than that latency, a naive `written_at`-
    authority sweep would GC a just-published, still-live entry the instant
    it becomes visible on disk. `gc_sweep()` now ages every entry off the
    entry file's own filesystem mtime (set at durable-write time), not the
    embedded, pre-latency `written_at` — this constructs a decryptable
    entry whose embedded `written_at` is already far outside the TTL while
    its real file mtime is fresh, and asserts the sweep does NOT collect it.

    Mutation probe: reverting `gc_sweep` to read `envelope.written_at` as
    the age authority (the pre-fix behavior) makes this entry expire."""
    import pickle

    from harness_runtime.lifecycle.protected_result_store import _StoredEnvelope

    store = _store(tmp_path, ttl_seconds=1.0)
    composite_key = compose_composite_key("tenant-a")
    envelope = _StoredEnvelope(
        tenant_id="tenant-a",
        type_tag="str",
        serializer_version=store._SERIALIZER_VERSION,  # type: ignore[attr-defined]
        written_at=time.time() - 10.0,  # far outside the 1s TTL
        payload=pickle.dumps("still live"),
        composite_key=composite_key,
    )
    ciphertext = store._codec.encrypt(pickle.dumps(envelope))  # type: ignore[attr-defined]
    entry_path = store._entry_path(composite_key)  # type: ignore[arg-type]
    store._publish_atomic(entry_path, ciphertext)  # type: ignore[arg-type]
    # The file's real mtime is "now" (just written) — fresh, well inside the TTL.

    expired = store.gc_sweep(now=time.time())
    assert expired == []
    assert entry_path.exists()
    assert store.read("tenant-a", composite_key) == "still live"


def test_write_once_survives_immediate_sweep_under_slow_fsync_and_short_ttl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-68 out-of-family Codex round 1 [P1], empirically reproduced by the
    reviewer: mtime-from-write-time (the fix above) still under-reports the
    true publish moment by however long `_publish_atomic`'s own fsync+link
    commit takes — the temp file's mtime is set at `handle.write()`,
    BEFORE that commit. A 20ms TTL with a 100ms-slowed fsync let `gc_sweep`
    collect a just-published, still-live entry immediately after
    `write_once()` returned. `_publish_atomic` now refreshes the entry's
    mtime to "now" AFTER the durable commit, closing that remaining gap.

    Mutation probe: removing the post-commit `os.utime` refresh reproduces
    the exact codex-verified failure — `gc_sweep` collects the entry."""
    store = _store(tmp_path, ttl_seconds=0.02)
    real_fsync = os.fsync
    seen = {"slowed": False}

    def _slow_first_fsync(fd: int) -> None:
        if not seen["slowed"]:
            seen["slowed"] = True
            time.sleep(0.10)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _slow_first_fsync)
    ref = store.write_once("tenant-a", "just published")
    assert isinstance(ref, str)

    expired = store.gc_sweep(now=time.time())
    assert expired == []
    assert store.read("tenant-a", ref) == "just published"


def test_publish_lock_shared_across_instances_of_same_root(tmp_path: Path) -> None:
    """B-68 codex round 2 [P1] x2 precondition: `_publish_atomic` and
    `gc_sweep` must mutually exclude even across multiple
    `ProtectedResultStore` INSTANCES pointed at the same on-disk
    directory — this daemon constructs a FRESH instance per
    `run()`/`resume()` bootstrap (`stage_4_od.py`), not one shared object.
    `_lock_for_root` is keyed by root path specifically so this holds.

    Mutation probe: keying the lock registry by `id(self)`/a fresh
    per-instance `threading.Lock()` instead of the resolved root path
    makes this identity check fail."""
    store_a = _store(tmp_path)
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,
        ttl_seconds=1.0,  # type: ignore[attr-defined]
    )
    assert store_a._publish_lock is store_b._publish_lock  # type: ignore[attr-defined]


def test_publish_lock_shared_across_filesystem_equivalent_path_aliases(
    tmp_path: Path,
) -> None:
    """codex round 3 [P2]: two filesystem-equivalent spellings of the SAME
    directory (a `..`-containing alias vs. the direct path) must key the
    SAME lock — `RuntimeConfig` doesn't guarantee a single canonical
    spelling across bootstraps, and keying by raw `str(root)` alone would
    let such an alias silently reopen the GC/publication race this lock
    exists to close.

    Mutation probe: keying `_lock_for_root` by the raw, un-resolved
    `str(root)` makes this identity check fail (the alias below is
    textually different from the direct path)."""
    store_direct = _store(tmp_path)
    aliased_root = tmp_path / "unrelated" / ".." / "store"
    assert aliased_root != tmp_path / "store"  # textually distinct...
    store_aliased = ProtectedResultStore(
        aliased_root,
        codec=store_direct._codec,  # type: ignore[attr-defined]
        ttl_seconds=1.0,
    )
    # ...but filesystem-equivalent, so the lock must still be shared.
    assert store_direct._publish_lock is store_aliased._publish_lock  # type: ignore[attr-defined]


def test_publish_lock_shared_across_case_insensitive_path_spellings(
    tmp_path: Path,
) -> None:
    """merge-gate round-6 out-of-family Codex review (PR #1103): on a
    case-INSENSITIVE filesystem (macOS APFS default volumes), two
    differently-cased spellings of the SAME directory name the identical
    inode but `Path.resolve()` alone preserves the caller's casing —
    keying the lock registry by the resolved-path STRING (round-3's fix)
    would still let this alias reopen the GC/publication race. Skipped
    on a case-SENSITIVE filesystem (most CI runners), where the two
    spellings genuinely name different, unrelated paths.

    Mutation probe: keying `_lock_for_root` by the resolved-path string
    instead of filesystem identity (`st_dev`/`st_ino`) makes this
    identity check fail on a case-insensitive volume."""
    store_direct = _store(tmp_path)
    direct_root = tmp_path / "store"
    direct_root.mkdir(parents=True, exist_ok=True)
    cased_root = Path(str(direct_root).swapcase())
    if not (cased_root.exists() and os.path.samefile(direct_root, cased_root)):
        pytest.skip("filesystem under tmp_path is not case-insensitive")
    store_cased = ProtectedResultStore(
        cased_root,
        codec=store_direct._codec,  # type: ignore[attr-defined]
        ttl_seconds=1.0,
    )
    assert store_direct._publish_lock is store_cased._publish_lock  # type: ignore[attr-defined]


def test_gc_sweep_blocks_while_publish_lock_held(tmp_path: Path) -> None:
    """B-68 codex round 2 [P1]: round 1's plain post-commit `os.utime`
    refresh still left a window between `os.link` (the entry becomes
    visible) and the refresh where a genuinely CONCURRENT `gc_sweep()` —
    from a SEPARATE instance sharing this directory — could observe the
    stale pre-fsync mtime. `gc_sweep` now acquires `self._publish_lock`
    (the SAME lock `_publish_atomic` holds across its commit + refresh)
    for its whole sweep. Verifies the mechanism directly: while the lock
    is held (simulating a publish mid-flight), a concurrent `gc_sweep()`
    call on a SEPARATE instance pointed at the same directory must block
    until the lock releases, not run past the held section.

    Mutation probe: removing `with self._publish_lock:` from `gc_sweep`
    lets the sweep complete immediately instead of blocking."""
    store_a = _store(tmp_path, ttl_seconds=86400.0)
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,
        ttl_seconds=86400.0,  # type: ignore[attr-defined]
    )
    # `gc_sweep` short-circuits (never touching the lock) if the store
    # directory doesn't exist yet — the constructor performs NO I/O, so it
    # must be created first (mirroring what a real `write_once()` would
    # have already done in production).
    (tmp_path / "store").mkdir(parents=True)
    sweep_started = threading.Event()
    sweep_done = threading.Event()

    def _run_sweep() -> None:
        sweep_started.set()
        store_b.gc_sweep(now=time.time())
        sweep_done.set()

    with store_a._publish_lock:  # type: ignore[attr-defined]
        sweeper = threading.Thread(target=_run_sweep)
        sweeper.start()
        assert sweep_started.wait(timeout=5.0)
        # Bounded wait for a chance to run past the held lock — it must
        # still be blocked, not merely "hasn't gotten there yet".
        assert not sweep_done.wait(timeout=0.3)

    sweeper.join(timeout=5.0)
    assert sweep_done.is_set()


def test_write_once_blocks_while_publish_lock_held(tmp_path: Path) -> None:
    """Companion to the test above: `_publish_atomic`'s commit + mtime-
    refresh critical section acquires the SAME `self._publish_lock`, so a
    concurrent publish is blocked out exactly as a concurrent sweep is —
    closing codex round 2 [P1]'s window from the writer's side.

    Mutation probe: removing `with self._publish_lock:` from
    `_publish_atomic` lets `write_once()` complete immediately instead of
    blocking."""
    store = _store(tmp_path)
    write_started = threading.Event()
    write_results: list[object] = []

    def _run_write() -> None:
        write_started.set()
        write_results.append(store.write_once("tenant-a", "payload"))

    with store._publish_lock:  # type: ignore[attr-defined]
        writer = threading.Thread(target=_run_write)
        writer.start()
        assert write_started.wait(timeout=5.0)
        writer.join(timeout=0.3)
        assert write_results == []
        assert writer.is_alive()

    writer.join(timeout=5.0)
    assert len(write_results) == 1
    assert isinstance(write_results[0], str)
    assert store.read("tenant-a", write_results[0]) == "payload"


def test_write_once_does_not_block_on_a_sweep_stalled_in_its_decrypt_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """merge-gate round-2 out-of-family Codex review (PR #1103, round 7
    [P1]): `gc_sweep()` is invoked via `run_off_loop_detach_on_cancel`
    (`audit_offload.py`), whose entire design intent is that a slow/hung
    worker gets DETACHED rather than blocking anything else — "the
    caller's own `asyncio.wait_for(..., timeout=...)` is the only bound
    that matters" (that function's own docstring). An earlier version of
    this fix held `self._publish_lock` across the WHOLE sweep body,
    including the per-entry decrypt+`pickle.loads` pass — so a detached,
    still-running sweep (stalled decrypting a large backlog, or a genuine
    hang) would keep the NEXT `write_once()`/`gc_sweep()` call on the SAME
    root blocked indefinitely, defeating the detach design on a long-lived
    daemon (`shutdown()` runs every `run()`/`resume()`, not just process
    exit). `gc_sweep()` now only holds the lock for the fast `stat()`-only
    candidate-selection phase; decrypt + unlink happen after it releases.

    This test pins that: it stalls a sweep INSIDE its (unlocked) decrypt
    phase (`pickle.loads`, not the codec — this module never monkeypatches
    the codec, see the module docstring) and asserts a concurrent
    `write_once()` on a second instance completes promptly rather than
    blocking on the stalled sweep.

    Mutation probe: re-wrapping the whole sweep body (decrypt phase
    included) back under `self._publish_lock` makes the write block for
    the full stall duration instead of completing promptly."""
    import pickle

    store_a = _store(tmp_path, ttl_seconds=0.01)
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,  # type: ignore[attr-defined]
        ttl_seconds=0.01,
    )
    # Suppress store_b's OWN opportunistic sweep (a fresh instance's
    # `_last_gc_at` starts at 0.0, so its first `write_once()` would
    # otherwise ALSO trigger a nested `gc_sweep()` that hits the same
    # stalled mock below — a confound this test doesn't intend to exercise;
    # the property under test is a WRITE not blocking on ANOTHER thread's
    # stalled sweep, not on its own.
    store_b._last_gc_at = time.time()  # type: ignore[attr-defined]
    ref = store_a.write_once("tenant-a", "will be swept")
    assert isinstance(ref, str)
    time.sleep(0.05)  # comfortably past the 0.01s TTL

    decrypt_phase_entered = threading.Event()
    decrypt_may_proceed = threading.Event()
    real_pickle_loads = pickle.loads

    def _stalled_pickle_loads(data: bytes) -> object:
        decrypt_phase_entered.set()
        decrypt_may_proceed.wait(timeout=5.0)
        return real_pickle_loads(data)

    monkeypatch.setattr(pickle, "loads", _stalled_pickle_loads)

    sweep_results: list[list[str]] = []

    def _run_sweep() -> None:
        sweep_results.append(store_a.gc_sweep())

    sweeper = threading.Thread(target=_run_sweep)
    sweeper.start()
    assert decrypt_phase_entered.wait(timeout=5.0), "sweep never reached its decrypt phase"

    # Run the write on its OWN thread and check with a SHORT bounded join —
    # calling `write_once()` directly and merely timing how long it takes
    # would not discriminate: under the pre-fix whole-body lock it still
    # eventually completes (once the mock's own 5s wait times out), just
    # slower, so a synchronous call passes either way. A short join window
    # well under the mock's 5s stall is what actually distinguishes
    # "blocked on the stalled sweep" from "completed promptly".
    write_results: list[object] = []

    def _run_write() -> None:
        write_results.append(store_b.write_once("tenant-b", "must not block on the stalled sweep"))

    writer = threading.Thread(target=_run_write)
    writer.start()
    writer.join(timeout=0.3)
    assert not writer.is_alive(), (
        "write_once() was still blocked 0.3s after starting — it waited on "
        "the stalled sweep's lock instead of completing promptly"
    )
    assert len(write_results) == 1

    decrypt_may_proceed.set()
    sweeper.join(timeout=5.0)
    assert not sweeper.is_alive()

    write_result = write_results[0]
    assert isinstance(write_result, str)
    assert store_b.read("tenant-b", write_result) == "must not block on the stalled sweep"
    assert len(sweep_results) == 1
    assert sweep_results[0] != []


def test_write_once_temp_file_protected_from_concurrent_sweep_before_commit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-68 out-of-family Codex round 4 [P1]: round 2/3's lock covered only
    `os.link` onward — a concurrent `gc_sweep()` (from a SEPARATE instance
    sharing this directory) could still classify THIS method's own
    in-flight `.tmp-*` file as a crash orphan (stale mtime under a short
    TTL + a slow fsync) and unlink it before `os.link` ever ran, losing
    recovery for an already-completed paid effect once the subsequent
    `os.link` raised `FileNotFoundError` (surfaced as
    `UnresolvableResultRef`, not the intended live ref). `_publish_atomic`
    now holds `self._publish_lock` for its ENTIRE body — starting before
    `tempfile.mkstemp`, not just from the commit onward — so a concurrent
    sweep can never run at all while a temp file is still in active use.

    Mutation probe: narrowing `_publish_atomic`'s `with self._publish_lock:`
    back to start at `os.link` (the round 2/3 shape) reproduces the exact
    codex-verified failure — a concurrent sweep unlinks the still-in-flight
    temp file and `write_once()` returns `UnresolvableResultRef`.

    merge-gate round-1 test-witness lens (PR #1103): an earlier version of
    this test signaled the sweeper via a sleep-then-set inside the mocked
    `os.fsync`, relying on the writer thread losing the GIL during the
    REAL `fsync()` syscall for the sweeper to actually run before the
    writer reached `os.link` — empirically only ~80% reliable (confirmed
    by repeated runs against a shadow copy with the round-2/3 regression
    reinstated: 2/11 runs passed despite the bug). Rewritten so the WRITER
    thread deterministically PARKS (via a second `Event`, not a sleep)
    inside the paused `fsync` call — i.e. still holding `self._publish_lock`
    under the fix — so which thread runs when no longer depends on
    scheduler timing. The `time.sleep` below is a one-directional wait
    (make the temp file look stale before the sweeper scans it), not a
    race for CPU time, so it does not reintroduce nondeterminism."""
    store_a = _store(tmp_path, ttl_seconds=0.02)
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,  # type: ignore[attr-defined]
        ttl_seconds=0.02,
    )

    real_fsync = os.fsync
    fsync_seen = {"n": 0}
    temp_file_created = threading.Event()
    writer_may_continue = threading.Event()

    def _paused_first_fsync(fd: int) -> None:
        fsync_seen["n"] += 1
        if fsync_seen["n"] == 1:
            # Deterministically park the writer INSIDE the publish critical
            # section, right after the temp file is created but before
            # `os.link` — rather than relying on the writer losing the GIL
            # during a real fsync syscall for a concurrent sweeper to run.
            temp_file_created.set()
            writer_may_continue.wait(timeout=5.0)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _paused_first_fsync)

    write_result: list[object] = []

    def _run_write() -> None:
        write_result.append(store_a.write_once("tenant-a", "must survive a concurrent sweep"))

    writer = threading.Thread(target=_run_write)
    writer.start()

    assert temp_file_created.wait(timeout=5.0), "writer never reached the paused fsync point"
    # One-directional: make the temp file's mtime genuinely stale relative
    # to the TTL before the sweeper scans it. Not a race — the writer is
    # already parked and cannot advance until `writer_may_continue` fires.
    time.sleep(0.05)

    sweep_results: list[list[str]] = []
    sweep_done = threading.Event()

    def _concurrent_sweep() -> None:
        sweep_results.append(store_b.gc_sweep(now=time.time()))
        sweep_done.set()

    sweeper = threading.Thread(target=_concurrent_sweep)
    sweeper.start()

    # Under the fix, `gc_sweep()` blocks trying to acquire the SAME
    # publish lock the parked writer still holds — it must NOT complete
    # while the writer's temp file is still in flight. Under the round-2/3
    # regression, the sweeper acquires the lock immediately (the writer
    # hasn't reached it yet) and returns well within this window.
    assert not sweep_done.wait(timeout=0.3), (
        "gc_sweep() completed while the writer's temp file was still "
        "in-flight — the publish lock did not protect the pre-os.link window"
    )

    writer_may_continue.set()
    writer.join(timeout=5.0)
    sweeper.join(timeout=5.0)

    assert write_result and isinstance(write_result[0], str)
    ref = write_result[0]
    assert sweep_results == [[]]
    assert store_a.read("tenant-a", ref) == "must survive a concurrent sweep"


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="_cross_process_lock() deliberately no-ops on Windows (C-STK-10; no fcntl); "
    "the blocking assertion below does not hold there.",
)
def test_write_once_blocks_across_separate_processes_via_cross_process_lock(
    tmp_path: Path,
) -> None:
    """B-73 (split from B-68 at its close, out-of-family Codex round 5):
    `_root_locks`' `threading.Lock` only serializes callers WITHIN one
    process — the daemon composition root constructs a FRESH
    `ProtectedResultStore` per bootstrap, so two separate OS PROCESSES
    sharing this same directory each hold their own independent
    `_root_locks` dict and are not mutually excluded by it at all.
    `_cross_process_lock` (`fcntl.flock` on a dedicated lockfile, acquired
    INSIDE `self._publish_lock`) closes that gap.

    Direct analog of `test_write_once_blocks_while_publish_lock_held`
    (which holds `store._publish_lock` directly to simulate an in-process
    concurrent publisher): here the lock is held directly via
    `store._cross_process_lock()`, standing in for a genuinely separate
    process's in-flight publish, and the blocked caller is a GENUINE
    separate OS process (`subprocess` running `_B73_CHILD_WRITE_SCRIPT` —
    a fresh interpreter, no shared Python state, so it cannot be serialized
    by the in-process `_root_locks` dict at all). No TTL/staleness timing
    is exercised here — that race is already covered in-process by
    `test_write_once_temp_file_protected_from_concurrent_sweep_before_
    commit`; this test isolates the cross-process mutual-exclusion
    mechanism itself.

    Mutation probe: removing `self._cross_process_lock()` from
    `_publish_atomic`'s `with` statement lets the child process's
    `write_once()` complete immediately instead of blocking on the
    parent-held flock — a manual mutation-probe run against a reverted
    copy of the fix (before this handshake was added) reproduced a false
    pass caused by the child's own cold-start import cost (~5s for
    `cryptography` + `harness_runtime` in this environment) masking the
    missing lock; the `ready_marker` handshake below closes that gap by
    timing the "still blocked" check from the moment the child is
    actually about to contend on the lock, not from process spawn.

    out-of-family Codex [P2]: a fresh child store's `_last_gc_at` is `0.0`,
    so `write_once()` would otherwise ALSO trigger
    `_maybe_opportunistic_gc_sweep()` first — which acquires the SAME
    cross-process lock via `gc_sweep()`, so this test would still pass
    even with `_cross_process_lock()` removed from `_publish_atomic`
    ALONE (the opportunistic sweep's own lock use would still block it).
    `_B73_CHILD_WRITE_SCRIPT` suppresses that sweep so this test isolates
    `_publish_atomic`'s own critical section specifically."""
    key = Fernet.generate_key()
    store_dir = tmp_path / "store"
    store_dir.mkdir(parents=True)
    store = ProtectedResultStore(store_dir, codec=Fernet(key), ttl_seconds=86400.0)
    done_marker = tmp_path / "child_done_marker"
    ready_marker = tmp_path / "child_ready_marker"

    with store._cross_process_lock():  # type: ignore[attr-defined]
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _B73_CHILD_WRITE_SCRIPT,
                str(store_dir),
                key.decode("ascii"),
                str(done_marker),
                str(ready_marker),
            ]
        )
        try:
            deadline = time.monotonic() + 10.0
            while not ready_marker.exists():
                assert time.monotonic() < deadline, "child never signaled readiness"
                time.sleep(0.02)
            # Bounded wait for a chance to run past the held lock, timed
            # from the moment the child is actually about to contend on
            # it — the marker file must still be absent, not merely
            # "hasn't gotten there yet".
            time.sleep(0.5)
            assert not done_marker.exists(), (
                "a separate OS process's write_once() completed while the "
                "parent held the cross-process lock"
            )
        except BaseException:
            child.kill()
            child.wait(timeout=5.0)
            raise

    assert child.wait(timeout=30.0) == 0
    assert done_marker.exists()


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="_cross_process_lock() deliberately no-ops on Windows (C-STK-10; no fcntl); "
    "the blocking assertion below does not hold there.",
)
def test_gc_sweep_blocks_across_separate_processes_via_cross_process_lock(
    tmp_path: Path,
) -> None:
    """Companion to the test above: `gc_sweep`'s candidate-selection phase
    acquires the SAME `_cross_process_lock`, so a concurrent sweep from a
    genuinely separate OS process is blocked out exactly as a concurrent
    publish is.

    Mutation probe: removing `self._cross_process_lock()` from `gc_sweep`'s
    `with` statement lets the child process's `gc_sweep()` complete
    immediately instead of blocking on the parent-held flock — see the
    companion write-side test's docstring for why the `ready_marker`
    handshake below is load-bearing (a cold child interpreter's own import
    cost can otherwise mask a missing lock)."""
    key = Fernet.generate_key()
    store_dir = tmp_path / "store"
    store_dir.mkdir(parents=True)
    store = ProtectedResultStore(store_dir, codec=Fernet(key), ttl_seconds=86400.0)
    done_marker = tmp_path / "child_done_marker"
    ready_marker = tmp_path / "child_ready_marker"

    with store._cross_process_lock():  # type: ignore[attr-defined]
        child = subprocess.Popen(
            [
                sys.executable,
                "-c",
                _B73_CHILD_SWEEP_SCRIPT,
                str(store_dir),
                key.decode("ascii"),
                str(done_marker),
                str(ready_marker),
            ]
        )
        try:
            deadline = time.monotonic() + 10.0
            while not ready_marker.exists():
                assert time.monotonic() < deadline, "child never signaled readiness"
                time.sleep(0.02)
            time.sleep(0.5)
            assert not done_marker.exists(), (
                "a separate OS process's gc_sweep() completed while the "
                "parent held the cross-process lock"
            )
        except BaseException:
            child.kill()
            child.wait(timeout=5.0)
            raise

    assert child.wait(timeout=30.0) == 0
    assert done_marker.exists()


def test_gc_sweep_does_not_collect_unexpired_entries(tmp_path: Path) -> None:
    store = _store(tmp_path, ttl_seconds=86400.0)
    store.write_once("tenant-a", "fresh entry")
    expired = store.gc_sweep(now=time.time())
    assert expired == []
    assert len(list((tmp_path / "store").glob("*.entry"))) == 1


def test_opportunistic_gc_runs_on_write_after_interval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Periodic-or-opportunistic runtime sweep (codex round-10 on the spec
    PR): a write triggers a sweep once the opportunistic interval has
    elapsed, without requiring a bootstrap/shutdown hook or a background
    task."""
    store = _store(tmp_path, ttl_seconds=1.0)
    monkeypatch.setattr(
        "harness_runtime.lifecycle.protected_result_store._OPPORTUNISTIC_GC_INTERVAL_SECONDS",
        0.0,
    )
    ref_a = store.write_once("tenant-a", "expires soon")
    entry_a = store._entry_path(ref_a)  # type: ignore[arg-type]
    assert entry_a.exists()

    real_time = time.time

    def _later() -> float:
        return real_time() + 10.0

    monkeypatch.setattr(time, "time", _later)
    store.write_once("tenant-a", "triggers the opportunistic sweep")
    assert not entry_a.exists()


def test_write_sweeps_before_publishing_never_sees_its_own_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """codex [P2] on the B-65-A CP-side arc: `write_once()` must run its
    opportunistic sweep BEFORE composing/publishing THIS entry, never after
    — else a deployment-configured TTL shorter than the write's own
    serialize+encrypt+fsync latency (valid under `gt=0.0`) would let the
    sweep immediately collect the entry the same call is about to return a
    live-looking ref for. Verified directly by ORDER: the sweep is spied to
    record how many `.entry` files exist in the store root at the moment it
    runs — for a store's FIRST-ever write, that count must be zero (the new
    entry cannot exist yet if the sweep genuinely ran first).

    Mutation probe: reverting to a post-publish sweep call makes the spied
    count 1 (the just-published entry is already on disk when the sweep
    that would see it runs) instead of 0."""
    store = _store(tmp_path, ttl_seconds=1.0)
    monkeypatch.setattr(
        "harness_runtime.lifecycle.protected_result_store._OPPORTUNISTIC_GC_INTERVAL_SECONDS",
        0.0,
    )
    entry_counts_at_sweep_time: list[int] = []
    real_sweep = store._maybe_opportunistic_gc_sweep

    def _spying_sweep() -> None:
        entry_counts_at_sweep_time.append(len(list((tmp_path / "store").glob("*.entry"))))
        real_sweep()

    monkeypatch.setattr(store, "_maybe_opportunistic_gc_sweep", _spying_sweep)

    ref = store.write_once("tenant-a", "the store's first-ever write")
    assert entry_counts_at_sweep_time == [0]
    assert isinstance(ref, str)
    assert store.read("tenant-a", ref) == "the store's first-ever write"


def test_gc_unlink_failure_does_not_propagate_or_replace_the_carrier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """codex [P1] on the B-65-A CP-side arc: `write_once()` calls the opportunistic
    sweep UNGUARDED — if `gc_sweep()`'s unlink of an expired entry raises OSError
    (e.g. permission denied), that error must NOT propagate out of `write_once()`.
    `write_once()` is called from `resolve_result_ref()`, evaluated as a kwarg
    expression while CONSTRUCTING `PostEffectAuditSigningError` at every raise
    site — an uncaught OSError there would replace the typed carrier with an
    unrelated GC error, and retry/pause handling would then treat the completed
    effect as an ordinary failure and RE-DISPATCH it (the exact at-most-once
    violation this whole store exists to prevent).

    Mutation probe: removing the `try/except OSError` around the sweep's unlink
    makes this test raise `OSError` instead of returning a valid `str` ref."""
    store = _store(tmp_path, ttl_seconds=1.0)
    monkeypatch.setattr(
        "harness_runtime.lifecycle.protected_result_store._OPPORTUNISTIC_GC_INTERVAL_SECONDS",
        0.0,
    )
    store.write_once("tenant-a", "will expire and fail to unlink")

    real_time = time.time
    monkeypatch.setattr(time, "time", lambda: real_time() + 10.0)

    real_unlink = Path.unlink

    def _raise_on_unlink(self: Path, *, missing_ok: bool = False) -> None:
        if self.suffix == ".entry":
            raise OSError("permission denied (simulated)")
        real_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", _raise_on_unlink)

    import logging

    caplog.set_level(logging.ERROR, logger="harness.runtime.protected_result_store")
    # The SECOND write's opportunistic sweep tries to GC the first (now-expired)
    # entry, whose unlink is rigged to fail — this call must still return a
    # valid ref for the SECOND write, never raise.
    ref_b = store.write_once("tenant-a", "an unrelated second write")
    assert isinstance(ref_b, str)
    assert store.read("tenant-a", ref_b) == "an unrelated second write"
    assert any("GC unlink failed" in record.message for record in caplog.records)


def test_directory_fsync_durability_failure_degrades_to_unresolvable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """codex [P2] round 5 on the B-65-A CP-side arc: `_fsync_dir`'s prior
    swallow-every-`OSError` behavior let a REAL durability failure (EIO,
    ENOSPC, a dying disk) on the destination-directory fsync pass silently
    AFTER `os.link` already committed the entry — `write_once` would then
    return a live-looking `composite_key` for an entry that might not
    survive a crash. A genuine I/O error must reach the EXISTING typed-
    unresolvable path instead.

    Mutation probe: reverting `_fsync_dir` to swallow every `OSError`
    makes this test return a `str` ref instead of `UnresolvableResultRef`.
    """
    store = _store(tmp_path)
    real_fsync = os.fsync
    calls = {"n": 0}

    def _flaky_fsync(fd: int) -> None:
        calls["n"] += 1
        # First call is the temp-file's own fsync (inside `_publish_atomic`,
        # before the `os.link` commit); second is the DESTINATION-directory
        # fsync (`_fsync_dir`, after the commit) — the one this fix targets.
        if calls["n"] == 2:
            raise OSError(errno.EIO, "simulated disk failure")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _flaky_fsync)
    ref = store.write_once("tenant-a", "payload")
    assert isinstance(ref, UnresolvableResultRef)
    assert "store write failed" in ref.reason


def test_directory_fsync_unsupported_errno_still_degrades_gracefully(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Companion to the test above — a genuinely-UNSUPPORTED directory
    fsync (EINVAL/ENOTSUP/EOPNOTSUPP, real on some platforms/filesystems)
    must stay best-effort, not regress into a false failure.

    Mutation probe: broadening the fix to raise on EVERY `OSError`
    (over-correcting past what codex asked for) makes this test return
    `UnresolvableResultRef` instead of a valid `str` ref."""
    store = _store(tmp_path)
    real_fsync = os.fsync
    calls = {"n": 0}

    def _unsupported_fsync(fd: int) -> None:
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError(errno.ENOTSUP, "directory fsync not supported (simulated)")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _unsupported_fsync)
    ref = store.write_once("tenant-a", "payload")
    assert isinstance(ref, str)
    assert store.read("tenant-a", ref) == "payload"


def test_gc_sweep_reclaims_crash_orphaned_temp_files(tmp_path: Path) -> None:
    """codex [P2] round 5 on the B-65-A CP-side arc: a process KILLED
    between `_publish_atomic`'s temp-write and its own `finally:
    os.unlink(tmp_name)` cleanup leaves a `.tmp-*` file behind indefinitely
    — every sweep (bootstrap/shutdown/opportunistic, all funneling through
    `gc_sweep`) previously enumerated only `*.entry`, so repeated crashes
    could accumulate stale ciphertext or exhaust disk with no bound.

    Mutation probe: removing the `.tmp-*` glob loop from `gc_sweep` makes
    this stale temp file survive the sweep instead of being reclaimed."""
    store = _store(tmp_path, ttl_seconds=1.0)
    store_root = tmp_path / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    orphan = store_root / ".tmp-crash-orphan-abc123"
    orphan.write_bytes(b"partial ciphertext from a killed write")
    old_time = time.time() - 10.0
    os.utime(orphan, (old_time, old_time))

    store.gc_sweep(now=time.time())
    assert not orphan.exists()


def test_gc_sweep_does_not_reclaim_fresh_temp_files(tmp_path: Path) -> None:
    """A temp file mid-write (well within the TTL) must NOT be reclaimed —
    only a genuinely stale (crash-orphaned) one."""
    store = _store(tmp_path, ttl_seconds=86400.0)
    store_root = tmp_path / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    fresh = store_root / ".tmp-in-progress-write"
    fresh.write_bytes(b"a write still in flight")

    store.gc_sweep(now=time.time())
    assert fresh.exists()


def test_directory_open_durability_failure_degrades_to_unresolvable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """codex [P1] round 6 on the B-65-A CP-side arc: `_fsync_dir`'s directory-
    OPEN failure (as opposed to the fsync call round 5 already fixed) ALSO
    swallowed every `OSError` unconditionally. The sole caller
    (`_publish_atomic`) only reaches this AFTER `mkdir` + `os.link` already
    succeeded on the SAME directory, so a real open failure here (EIO,
    EMFILE, a permission change mid-flight) is a genuine durability signal,
    not a "fsync unsupported" case — it must reach the existing typed-
    unresolvable path too.

    Mutation probe: reverting the directory-open branch to swallow every
    `OSError` unconditionally makes this test return a `str` ref instead of
    `UnresolvableResultRef`."""
    store = _store(tmp_path)
    real_open = os.open

    def _flaky_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        # `_fsync_dir` opens `store._root` with exactly `os.O_RDONLY`; B-68
        # round 2 [P1] added a SECOND `os.O_RDONLY` open (the entry's own
        # post-refresh fsync) — flags alone no longer discriminate the two,
        # so key on the PATH (the directory vs. the entry file) instead.
        # `tempfile.mkstemp` (the SAME write's temp-file creation, earlier
        # in the call chain) uses neither this path nor these flags.
        if flags == os.O_RDONLY and Path(path) == store._root:  # type: ignore[arg-type]
            raise OSError(errno.EIO, "simulated disk failure opening directory")
        return real_open(path, flags, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "open", _flaky_open)
    ref = store.write_once("tenant-a", "payload")
    assert isinstance(ref, UnresolvableResultRef)
    assert "store write failed" in ref.reason


def test_directory_open_unsupported_errno_still_degrades_gracefully(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Companion to the test above — a genuinely-UNSUPPORTED directory open
    (EINVAL/ENOTSUP/EOPNOTSUPP) must stay best-effort.

    Mutation probe: broadening the fix to raise on EVERY `OSError` makes
    this test return `UnresolvableResultRef` instead of a valid `str` ref."""
    store = _store(tmp_path)
    real_open = os.open

    def _unsupported_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        # See the discrimination note in the test above — key on the
        # directory PATH, not flags alone (B-68 round 2 [P1] added a second
        # `os.O_RDONLY` open for the entry's own post-refresh fsync).
        if flags == os.O_RDONLY and Path(path) == store._root:  # type: ignore[arg-type]
            raise OSError(errno.ENOTSUP, "directory open not supported (simulated)")
        return real_open(path, flags, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "open", _unsupported_open)
    ref = store.write_once("tenant-a", "payload")
    assert isinstance(ref, str)
    assert store.read("tenant-a", ref) == "payload"


def test_normalize_tenant_scope_accepts_untenanted_literal_as_valid_tenant() -> None:
    """codex [P2] round 11: `_untenanted` is a config-valid tenant_id —
    `RuntimeConfig.tenant_id`'s own validator reserves only `""`/`"_single"`
    (`types.py::_tenant_id_not_reserved`) — so round 7's blanket rejection of
    this literal was itself the defect: a real deployment configured with
    this tenant_id would pass config load cleanly and then have EVERY
    post-effect result silently degrade to `UnresolvableResultRef` forever.
    The collision round 7 guarded against is now closed at the ENCODING
    layer instead (see `_encode_scope_prefix`), so no literal needs
    reserving.

    Mutation probe: reintroducing the `_UNTENANTED_TAG` rejection in
    `normalize_tenant_scope` makes this call raise instead of returning."""
    assert normalize_tenant_scope("_untenanted") == "_untenanted"


def test_write_once_distinguishes_untenanted_tenant_from_none_scope(tmp_path: Path) -> None:
    """codex [P2] round 11: proves the cross-scope collision the round-7 fix
    guarded against (a real tenant literally named "_untenanted" vs. the
    `None` untenanted scope, which both hex-encoded to the same prefix under
    the old scheme) is now closed by the disjoint `u`/`t`-prefixed encoding
    rather than by reserving the literal — both scopes are live and
    accepted, but a write under one is never readable under the other.

    Mutation probe: reverting `_encode_scope_prefix` to hex-encode a
    reserved sentinel string for the `None` case (the pre-round-11 scheme)
    makes the cross-scope `read()` assertions below succeed instead of
    raising."""
    store = _store(tmp_path)
    tenant_ref = store.write_once("_untenanted", "real tenant's secret")
    none_ref = store.write_once(None, "untenanted scope's secret")
    assert isinstance(tenant_ref, str)
    assert isinstance(none_ref, str)
    assert store.read("_untenanted", tenant_ref) == "real tenant's secret"
    assert store.read(None, none_ref) == "untenanted scope's secret"
    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read(None, tenant_ref)
    with pytest.raises(ProtectedStoreCrossTenantError):
        store.read("_untenanted", none_ref)


def test_write_once_survives_opportunistic_gc_sweep_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """codex [P1] round 7: an exception raised inside the periodic
    opportunistic in-write GC sweep (e.g. a directory-enumeration
    `PermissionError`) must NOT propagate out of `write_once` — that would
    replace the well-typed `UnresolvableResultRef` degradation with an
    unrelated raw exception, risking the raise-site caller (fed by an
    ALREADY-completed paid effect) falling through to generic retry/
    fallback handling instead of the fail-closed carrier path.

    Mutation probe: removing the try/except around `self.gc_sweep(now=now)`
    in `_maybe_opportunistic_gc_sweep` makes this test's `write_once` call
    raise `RuntimeError` instead of returning a `str` ref."""
    store = _store(tmp_path)
    store._last_gc_at = 0.0  # force the opportunistic-interval branch true

    def _boom(*, now: float | None = None) -> list[str]:
        raise RuntimeError("simulated directory-enumeration failure")

    monkeypatch.setattr(store, "gc_sweep", _boom)

    ref = store.write_once(None, {"x": 1})
    assert isinstance(ref, str)
    assert store.read(None, ref) == {"x": 1}
