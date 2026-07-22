"""`ProtectedResultStore` unit tests (RATIFIED B-65 Class 2 fork §3b; Runtime
spec v1.103 §14.8.11). All tests exercise a real `cryptography` Fernet — this
module never monkeypatches the codec.
"""

from __future__ import annotations

import errno
import os
import time
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import (
    ProtectedResultStore,
    ProtectedStoreCrossTenantError,
    ProtectedStoreTamperError,
    UnresolvableResultRef,
    _encode_tenant_tag,
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
    forged_ref = _encode_tenant_tag("tenant-b") + ":" + "f" * 32
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
    fixed_key = _encode_tenant_tag("tenant-a") + ":" + "0" * 32
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
    fixed_key = _encode_tenant_tag("tenant-a") + ":" + "1" * 32
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
