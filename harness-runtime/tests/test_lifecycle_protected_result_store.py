"""`ProtectedResultStore` unit tests (RATIFIED B-65 Class 2 fork §3b; Runtime
spec v1.103 §14.8.11). All tests exercise a real `cryptography` Fernet — this
module never monkeypatches the codec.
"""

from __future__ import annotations

import errno
import inspect
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import (
    _GC_OBSERVATION_RECORD_TEMP_PREFIX,
    GC_OBSERVATION_RECORD_FILENAME,
    GcObservationRecordState,
    ProtectedResultStore,
    ProtectedStoreCrossTenantError,
    ProtectedStoreEntryNotFoundError,
    ProtectedStoreTamperError,
    UnresolvableResultRef,
    _encode_scope_prefix,
    compose_composite_key,
    normalize_tenant_scope,
    read_protected_result_store_snapshot,
)


def _store(tmp_path: Path, *, ttl_seconds: float = 86400.0) -> ProtectedResultStore:
    return ProtectedResultStore(
        tmp_path / "store", codec=Fernet(Fernet.generate_key()), ttl_seconds=ttl_seconds
    )


def _observation_record_path(store: ProtectedResultStore) -> Path:
    """The durable `B-96` observation record for `store`'s root."""
    return store._root / GC_OBSERVATION_RECORD_FILENAME  # type: ignore[attr-defined]


def _read_observation_record(store: ProtectedResultStore) -> dict[str, float]:
    document = json.loads(_observation_record_path(store).read_text())
    rows: dict[str, float] = document["observations"]
    return rows


def _backdate_observation_record(store: ProtectedResultStore, *, by: float | None = None) -> None:
    """Move every recorded `first_observed_at` BACK by `by` (default: one TTL
    plus a one-second margin), in place, preserving the record's form.

    This is the elapsed-time analogue of the sweep-COUNT era's "just sweep
    twice": it satisfies term 1's SECOND conjunct without moving the sweep's
    own `now`, so a witness's FIRST conjunct — the filesystem-timestamp
    classification it actually exists to discriminate — is evaluated at exactly
    the instant it was before, unchanged. Advancing `now` instead would move
    both conjuncts together and silently re-classify entries the witness
    intends to be fresh.
    """
    path = _observation_record_path(store)
    document = json.loads(path.read_text())
    shift = store._ttl_seconds + 1.0 if by is None else by  # type: ignore[attr-defined]
    rows: dict[str, float] = document["observations"]
    document["observations"] = {name: stamp - shift for name, stamp in rows.items()}
    path.write_text(json.dumps(document))


def _sweep_past_grace(store: ProtectedResultStore, *, now: float | None = None) -> list[str]:
    """Two consecutive sweeps at the SAME `now`, returning the second's report.

    `B-96`'s DURABLE ELAPSED-TIME grace means a sweep never reclaims a
    candidate until a full TTL of wall-clock time has passed since the
    candidate's durably recorded FIRST observation — so every witness about
    what the sweep CLASSIFIES (rather than about the grace itself) needs the
    first sweep to record the observation, that observation aged past the TTL,
    and a second sweep to reach the reclaim.

    Re-grounded from the sweep-COUNT era (`B-77`), where two sweeps at one
    pinned `now` sufficed. The aging is done by BACK-DATING the durable record
    between the two sweeps rather than by advancing `now`, precisely so the
    pinned-`now` property the old helper's callers depend on survives intact:
    both sweeps still evaluate the mtime conjunct at the identical instant, so
    these witnesses discriminate exactly what they discriminated before.

    `observed_at` is pinned to `at` on the FIRST sweep, and that is load-bearing
    rather than tidiness: several callers pass a `now` well AHEAD of the real
    clock (`time.time() + 10.0`, or a `_ScriptedClock` advanced 60s). Left to
    its production default the sample would read the REAL clock, the elapsed
    conjunct would already be satisfied at the first sweep, and the reclaim
    would happen there — leaving the second sweep to return `[]` and every
    `== []` caller passing VACUOUSLY, with the entry gone.
    """
    at = time.time() if now is None else now
    store.gc_sweep(now=at, observed_at=at)
    _backdate_observation_record(store)
    return store.gc_sweep(now=at)


#: How long a "slow" publish step is simulated to take by the witnesses below
#: that pin `_publish_atomic`'s mtime-refresh placement. Advanced on a
#: `_ScriptedClock` rather than slept for real (see `_ScriptedClock`), so the
#: figure is free to be enormous relative to the sub-100ms TTLs those tests
#: configure — the margin no longer competes with CI scheduling latency at
#: all, in either the pass or the mutation-kill direction.
_SIMULATED_SLOW_STEP_SECONDS = 60.0

#: The sub-second phase the coarse-filesystem-granularity witness pins its
#: scripted publish moment to. Any value strictly above that test's 100ms TTL
#: (and strictly below 1.0) exercises the condition; 0.6 sits mid-second, far
#: from both boundaries.
_COARSE_MTIME_PHASE = 0.6


class _ScriptedClock:
    """Deterministic stand-in for the wall clock `_publish_atomic`'s mtime
    refreshes read.

    `gc_sweep`'s age arithmetic has exactly two inputs: the entry file's
    mtime — written ONLY by `os.utime(path, None)`, i.e. the filesystem's
    current wall clock — and the sweep's own already-injectable `now=`.
    Pinning the first to a scripted value (`_pin_mtime_stamps_to_clock`) and
    passing the same value as the second makes every TTL comparison in a
    witness EXACT, instead of a race between a sub-100ms TTL and however
    long the surrounding statements happened to take. `advance()` then
    stands in for a slow publish step without a real `time.sleep` — a
    strictly stronger simulation (it can model an unboundedly slow tail)
    that no CI load can perturb.

    Seeded from the REAL clock deliberately: a mutation that deletes one of
    the two refreshes leaves the file carrying its raw, unstamped write-time
    mtime, and that value must still read as `advance()`-seconds stale for
    the mutation-kill direction to keep its margin. A synthetic epoch (e.g.
    `0.0`) would instead make an unstamped mtime read as far in the FUTURE
    and silently defuse every such probe.
    """

    def __init__(self) -> None:
        self.now = time.time()

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _pin_mtime_stamps_to_clock(monkeypatch: pytest.MonkeyPatch, clock: _ScriptedClock) -> None:
    """Route every `os.utime(path, None)` "refresh to now" through `clock`.

    Only the `times is None` form is redirected — that is precisely
    `_publish_atomic`'s two refresh-to-now stamps. Calls passing explicit
    `times` (a test back-dating a file itself) pass straight through.
    """
    real_utime = os.utime

    def _clocked_utime(path: object, times: object = None, **kwargs: object) -> None:
        if times is None:
            real_utime(path, (clock.now, clock.now), **kwargs)  # type: ignore[arg-type]
            return
        real_utime(path, times, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "utime", _clocked_utime)


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


# A cold child must import cryptography plus every harness dependency before it
# reaches the lock. B-143 measured 5.39s / 33.89s / 7.69s on the same host, so
# the former 10s deadline sat inside the observed distribution. Sixty seconds
# matches the repo's other cold-process witnesses while preserving a bounded
# failure; `_wait_for_child_ready` separately fails immediately on child exit.
_COLD_CHILD_READY_TIMEOUT_SECONDS = 60.0


def _wait_for_child_ready(child: subprocess.Popen[bytes], ready_marker: Path) -> None:
    deadline = time.monotonic() + _COLD_CHILD_READY_TIMEOUT_SECONDS
    while not ready_marker.exists():
        returncode = child.poll()
        assert returncode is None, f"child exited with status {returncode} before lock readiness"
        assert time.monotonic() < deadline, (
            "child never signaled lock readiness within the cold-import budget"
        )
        time.sleep(0.02)


def test_wait_for_child_ready_fails_immediately_when_child_exits(tmp_path: Path) -> None:
    child = subprocess.Popen([sys.executable, "-c", "raise SystemExit(7)"])
    child.wait(timeout=5.0)

    with pytest.raises(AssertionError, match="status 7 before lock readiness"):
        _wait_for_child_ready(child, tmp_path / "never-written")


def test_wait_for_child_ready_bounds_a_live_non_signaling_child(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(globals(), "_COLD_CHILD_READY_TIMEOUT_SECONDS", 0.05)
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    failures: list[BaseException] = []
    completed = threading.Event()

    def wait_for_ready() -> None:
        try:
            _wait_for_child_ready(child, tmp_path / "never-written")
        except BaseException as exc:
            failures.append(exc)
        finally:
            completed.set()

    waiter = threading.Thread(target=wait_for_ready)
    waiter.start()
    try:
        assert completed.wait(timeout=1.0), "readiness helper ignored its cold-import budget"
        assert child.poll() is None
        assert len(failures) == 1
        assert isinstance(failures[0], AssertionError)
        assert "cold-import budget" in str(failures[0])
    finally:
        child.terminate()
        child.wait(timeout=5.0)
        waiter.join(timeout=5.0)


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
    expired = _sweep_past_grace(store, now=time.time() + 10.0)
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

    expired = _sweep_past_grace(store, now=time.time())
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

    expired = _sweep_past_grace(store, now=time.time())
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
    `write_once()` returned. `_publish_atomic` now refreshes the temp
    file's mtime to "now" (B-77: BEFORE the commit, not after) closing
    that remaining gap.

    Mutation probe: removing BOTH of `_publish_atomic`'s refresh-to-now
    stamps reproduces the exact codex-verified failure — the entry keeps
    the temp file's raw write-time mtime, which predates the slowed data
    fsync, and `gc_sweep` collects it. (Removing only ONE of the two does
    NOT fail this witness: the surviving stamp still runs after the slowed
    fsync. Each stamp is pinned individually by
    `test_crash_immediately_after_commit_leaves_an_already_correct_durable_
    mtime` (pre-commit) and `test_slow_post_commit_tail_does_not_falsely_
    expire_a_successful_write` (post-commit); the docstring said "the
    pre-commit refresh" alone until the two-stamp shape landed and is
    corrected here rather than left stale.)

    CI-load hardening: the slow fsync is simulated by ADVANCING a
    `_ScriptedClock` that both the store's mtime stamps and this sweep's
    `now=` read, not by a real `time.sleep` raced against a 20ms TTL — see
    `_ScriptedClock`. The store's TTL and the stamp placement it pins are
    unchanged; only the clock the comparison reads is now exact."""
    store = _store(tmp_path, ttl_seconds=0.02)
    clock = _ScriptedClock()
    _pin_mtime_stamps_to_clock(monkeypatch, clock)
    real_fsync = os.fsync
    seen = {"slowed": False}

    def _slow_first_fsync(fd: int) -> None:
        if not seen["slowed"]:
            seen["slowed"] = True
            clock.advance(_SIMULATED_SLOW_STEP_SECONDS)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _slow_first_fsync)
    ref = store.write_once("tenant-a", "just published")
    assert isinstance(ref, str)

    expired = _sweep_past_grace(store, now=clock.now)
    assert expired == []
    assert store.read("tenant-a", ref) == "just published"


def test_crash_immediately_after_commit_leaves_an_already_correct_durable_mtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-77 (forward-register, out-of-family Codex round 8 on the B-68 arc;
    NARROWED not closed, 2026-07-26 — see the row for the residual).
    Codex caught a wrong dormancy conclusion first (PR #1123 round 1): the
    crash window this finding concerns isn't a fast `os.link`-to-`os.utime`
    gap, it's the WHOLE write+fsync duration — unbounded under I/O
    pressure/a large payload/a slow filesystem, not a fixed small window.
    `_publish_atomic` now refreshes + fsyncs the temp file's mtime BEFORE
    `os.link`, removing THAT (dominant, payload-scaling) duration from the
    window — it does NOT eliminate the window entirely (a narrower residual
    remains; see
    `test_slow_post_commit_tail_does_not_falsely_expire_a_successful_write`
    for Codex round 9's separate, normal-path regression this test does
    NOT cover — this one targets only the DATA-fsync term the fix does
    close). This test: simulate a slowed initial data fsync
    (so the temp file's write-time mtime would badly under-report "now" if
    it were ever used) PLUS a "crash" immediately after the commit (the
    directory fsync — the very next step — raises), and confirm the
    surviving entry already carries a fresh, correct mtime a fresh
    process's immediate bootstrap sweep must not reclaim.

    Mutation probe: reverting to the pre-fix post-commit `os.utime`
    ordering (i.e. deleting the PRE-commit stamp) makes the crash-recovered
    entry inherit the temp file's stale, pre-slow-fsync mtime, and the
    sweep below reclaims it.

    CI-load hardening: the slow fsync is simulated by ADVANCING a
    `_ScriptedClock` that both the store's mtime stamps and this sweep's
    `now=` read, not by a real `time.sleep` raced against a 50ms TTL — see
    `_ScriptedClock`."""
    store = _store(tmp_path, ttl_seconds=0.05)
    clock = _ScriptedClock()
    _pin_mtime_stamps_to_clock(monkeypatch, clock)
    real_fsync = os.fsync
    seen = {"slowed": False}

    def _slow_first_fsync(fd: int) -> None:
        if not seen["slowed"]:
            seen["slowed"] = True
            clock.advance(_SIMULATED_SLOW_STEP_SECONDS)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _slow_first_fsync)

    def _crash_after_commit(root: Path) -> None:
        raise OSError("simulated crash immediately after the commit")

    monkeypatch.setattr(store, "_fsync_dir", _crash_after_commit)

    ref = store.write_once("tenant-a", "crashes right after commit")
    assert isinstance(ref, UnresolvableResultRef)

    entry_path = next((tmp_path / "store").glob("*.entry"))
    assert entry_path.exists()  # the commit itself survived the "crash"

    # A separate, fresh instance sharing the same root stands in for the
    # NEXT process's bootstrap sweep — unaffected by the THREE patches above
    # (the scripted-clock `os.utime` redirect, the slowed global `os.fsync`,
    # and the `store`-bound `_fsync_dir` crash: the first two are global but
    # `seen["slowed"]` is already consumed by the time this runs, and the third
    # is bound to `store`, not to `store2`). Corrected from "the patches" /
    # "both" — an undercount since PR #1226 added the third (scripted-clock)
    # patch, flagged by that arc's merge-gate lens 2.
    store2 = ProtectedResultStore(
        tmp_path / "store",
        codec=store._codec,  # type: ignore[attr-defined]
        ttl_seconds=0.05,
    )
    # Swept PAST the B-77 grace (out-of-family Codex round 3 [P2] on the
    # B-77 arc): a single sweep can no longer reclaim a newly-observed
    # entry whatever its mtime, so a one-sweep assertion here would pass
    # even if the PRE-commit stamp regressed to the raw write-time value —
    # exactly the freshness this witness exists to pin.
    expired = _sweep_past_grace(store2, now=clock.now)
    assert expired == []
    assert entry_path.exists()


def test_slow_post_commit_tail_does_not_falsely_expire_a_successful_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-77 (forward-register, out-of-family Codex round 9 [P1] on the
    B-68 arc). The round-1 reorder fix (mtime stamped on the temp file
    BEFORE `os.link`) closed the crash-recovery gap but opened a
    DIFFERENT, normal-path regression against `main`: on `main`, the
    (single) mtime stamp runs AFTER the full commit tail (metadata fsync
    + `os.link` + directory fsync), so a successful `write_once()` always
    returns a genuinely-fresh entry. With the stamp moved to run BEFORE
    that tail instead, a slow tail (a large payload, I/O pressure, or —
    as here — an injected delay) could make an IMMEDIATE `gc_sweep()`
    right after a successful, uninterrupted `write_once()` reclaim the
    entry it just returned a reference for — no crash involved. Codex
    reproduced this with a 20ms TTL and a 100ms-delayed directory fsync.
    `_publish_atomic` now refreshes the mtime a SECOND time, on the
    entry, AFTER the full commit tail — restoring `main`'s original
    normal-path guarantee — in ADDITION to (not instead of) the
    pre-commit stamp `test_crash_immediately_after_commit_leaves_an_
    already_correct_durable_mtime` covers.

    Mutation probe: removing the post-commit `os.utime`+fsync block
    (reverting to the round-1-only, pre-commit-stamp-alone shape) makes
    this test fail — the immediate sweep below reclaims the entry.

    A NUANCE in the other direction, recorded so the PD-8 matrix is not
    misread (PR #1226's merge-gate lens 3): the drop-PRE-commit-stamp mutation
    ALSO fails this test, but that kill is an ORDERING ARTIFACT rather than a
    semantic one — removing the pre-commit stamp removes its own `fsync`, so
    the `calls["n"] == 3` counter below lands on a DIFFERENT `fsync` and the
    clock advance moves. It is not evidence that this witness pins the
    pre-commit stamp; `test_crash_immediately_after_commit_leaves_an_already_
    correct_durable_mtime` is what pins that. No coverage gap either way — each
    stamp has its own dedicated witness.

    CI-load hardening: the slow directory fsync is simulated by ADVANCING a
    `_ScriptedClock` that both the store's mtime stamps and this sweep's
    `now=` read, not by a real `time.sleep` raced against a 20ms TTL. The
    original 100ms-vs-20ms margin was the flake: under CI load the wall
    time between the post-commit stamp and the sweep's own `time.time()`
    could itself exceed 20ms, expiring a correctly-stamped entry (recorded
    instances: PRs #1103, #1130, #1213, #1223). The reproduction's shape
    (which fsync is slowed, which stamp must run below it) is unchanged."""
    store = _store(tmp_path, ttl_seconds=0.02)
    clock = _ScriptedClock()
    _pin_mtime_stamps_to_clock(monkeypatch, clock)
    real_fsync = os.fsync
    calls = {"n": 0}

    def _slow_third_fsync(fd: int) -> None:
        calls["n"] += 1
        # Third fsync call is the DESTINATION-directory fsync
        # (`_fsync_dir`, inside `_publish_atomic`, after `os.link`) — see
        # the discrimination note on `test_directory_fsync_durability_
        # failure_degrades_to_unresolvable` above for the full call
        # ordering.
        if calls["n"] == 3:
            clock.advance(_SIMULATED_SLOW_STEP_SECONDS)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _slow_third_fsync)

    ref = store.write_once("tenant-a", "slow tail, no crash")
    assert isinstance(ref, str)

    expired = _sweep_past_grace(store, now=clock.now)
    assert expired == []
    assert store.read("tenant-a", ref) == "slow tail, no crash"


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


def test_transient_stat_failure_at_lock_key_resolution_propagates_not_falls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-76 (codex round 8 on the B-68 arc): `_lock_for_root` no longer
    catches `OSError` from `resolved.stat()` and silently falls back to a
    resolved-path-STRING key. The unconditional `mkdir` immediately above
    that call already makes the not-yet-created-directory case
    unreachable, so the only failure the old fallback still caught was a
    genuinely TRANSIENT I/O error — and silently switching key namespaces
    there would let two near-simultaneous callers key DIFFERENT locks
    (one string-keyed, one inode-keyed) for the SAME logical root,
    reopening the exact aliasing race this identity-based key exists to
    close.

    Mutation probe: restoring the `except OSError: key = str(resolved)`
    fallback makes the first access below return a (wrongly divergent)
    lock instead of raising, and this test's `pytest.raises` fails."""
    store_a = _store(tmp_path)
    lock_a = store_a._publish_lock  # type: ignore[attr-defined]  # establishes the real, inode-keyed lock

    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,  # type: ignore[attr-defined]
        ttl_seconds=1.0,
    )
    real_stat = Path.stat
    resolved_root = (tmp_path / "store").resolve()
    calls = {"n": 0}

    def _flaky_stat(self: Path, *args: object, **kwargs: object) -> os.stat_result:
        # Only intercepts `_root_identity_key`'s OWN direct `resolved.stat()`
        # call (checked by immediate-caller frame) — `Path.resolve()` and
        # `Path.mkdir()`'s `exist_ok` branch both call `.stat()`
        # internally too (pathlib-version-dependent, and each already
        # swallows its own `OSError`), so a blind global intercept would
        # get absorbed there instead of ever reaching the line under test.
        frame = inspect.currentframe()
        caller = frame.f_back if frame is not None else None
        if (
            self == resolved_root
            and caller is not None
            and caller.f_code.co_name == "_root_identity_key"
        ):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError(errno.EIO, "simulated transient I/O failure")
        return real_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", _flaky_stat)

    with pytest.raises(OSError):
        _ = store_b._publish_lock  # type: ignore[attr-defined]  # transient failure propagates, no fallback lock

    # Retry after the transient failure clears: must resolve to the SAME
    # lock object already registered for this root's true identity —
    # never a second, divergently-keyed one.
    assert store_b._publish_lock is lock_a  # type: ignore[attr-defined]


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
    # `B-96` durable elapsed-time grace: the stalled sweep below must actually
    # REACH its decrypt phase, which only happens for an entry whose recorded
    # first observation is already a full TTL old. This priming sweep (run
    # before the stall is installed) records that observation; back-dating the
    # record then ages it past the TTL without touching the sweep's own clock.
    # Re-pinned from the `B-77` sweep-COUNT form, where the priming sweep alone
    # sufficed.
    store_a.gc_sweep()
    _backdate_observation_record(store_a)

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

    # Run the write on its OWN thread and check with a bounded join —
    # calling `write_once()` directly and merely timing how long it takes
    # would not discriminate: under the pre-fix whole-body lock it still
    # eventually completes (once the mock's own 5s wait times out), just
    # slower, so a synchronous call passes either way. A join window well
    # under the mock's 5s stall is what actually distinguishes "blocked on
    # the stalled sweep" from "completed promptly".
    #
    # The window's exact size is INCIDENTAL to that claim — any bound
    # comfortably below the 5s stall discriminates identically, because
    # under the mutation the write cannot return until the stall ends. It
    # is widened from the original 0.3s purely for CI-load headroom (a
    # genuine, unblocked `write_once()` — pickle + Fernet + three fsyncs —
    # can take far longer than 0.3s on a loaded runner without any lock
    # being involved), which costs the mutation-kill direction nothing.
    write_results: list[object] = []

    def _run_write() -> None:
        write_results.append(store_b.write_once("tenant-b", "must not block on the stalled sweep"))

    writer = threading.Thread(target=_run_write)
    writer.start()
    writer.join(timeout=1.5)
    assert not writer.is_alive(), (
        "write_once() was still blocked 1.5s after starting — it waited on "
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
    back to start at `os.link` (the round 2/3 shape) makes the sweeper
    acquire the lock immediately — the writer has not reached it yet — so
    the timing assertion below (`not sweep_done.wait(0.3)`) fails.

    merge-gate round-2 test-witness lens (PR #1163) — what this test
    discriminates CHANGED with B-77's first-observation grace, and the
    docstring is corrected in place rather than left stale: the probe
    outcome above used to be stated as "`write_once()` returns
    `UnresolvableResultRef`" (the sweeper unlinks the in-flight temp file,
    so the subsequent `os.link` raises `FileNotFoundError`). Under the
    grace, the concurrent sweeper can no longer unlink a temp file on the
    sweep that FIRST observes it, so that downstream consequence no longer
    materializes on a single sweep. The load-bearing assertion is now the
    TIMING/lock one below — the sweeper must not COMPLETE while the parked
    writer still holds `self._publish_lock` — which is the property this
    test was always structurally pinning (`[[verification-shape-sharpened-
    grep-vs-e2e]]`: assert lock-identity, not a race outcome). The test
    itself is unchanged and not weakened.

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
            _wait_for_child_ready(child, ready_marker)
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
            _wait_for_child_ready(child, ready_marker)
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


def test_gc_sweep_candidate_enumeration_runs_without_holding_publish_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-75 (codex round 8 on the B-68 arc, closed via advisor()-directed
    snapshot-then-verify at the B-76 arc): candidate ENUMERATION (`glob()`
    over `*.entry`/`.tmp-*`) must run WITHOUT holding `self._publish_lock`.
    Round 7's fix already moved decrypt+unlink off-lock; round 8 found the
    `glob()`/`stat()` SCAN itself was still unbounded while held — a
    pathologically large backlog, or a hanging filesystem mount, could
    stall the scan and block every concurrent write/sweep on this root
    (worse after B-73: across OS PROCESSES too, since the scan also held
    `_cross_process_lock`).

    Structural witness (not wall-clock, per
    `[[verification-shape-sharpened-grep-vs-e2e]]`): records whether
    `store._publish_lock` is held at the moment each `Path.glob()` call is
    made on the store's own directory, and asserts every enumeration call
    observes it UNHELD.

    Mutation probe: wrapping the enumeration loops back inside the
    `with self._publish_lock, self._cross_process_lock():` block (the
    pre-fix shape) makes every recorded `glob()` call see the lock HELD."""
    store = _store(tmp_path, ttl_seconds=0.01)
    ref = store.write_once("tenant-a", "will be swept")
    assert isinstance(ref, str)
    time.sleep(0.05)  # comfortably past the 0.01s TTL

    lock_held_at_glob: list[bool] = []
    real_glob = Path.glob

    def _recording_glob(self: Path, pattern: str) -> object:
        if self == store._root:  # type: ignore[attr-defined]
            lock_held_at_glob.append(store._publish_lock.locked())  # type: ignore[attr-defined]
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", _recording_glob)

    expired = _sweep_past_grace(store, now=time.time())

    assert lock_held_at_glob, "no glob() call was observed on the store root"
    assert not any(lock_held_at_glob), (
        f"candidate enumeration ran with `_publish_lock` HELD at least once: {lock_held_at_glob}"
    )
    assert expired == [store._entry_path(ref).stem]  # type: ignore[attr-defined,arg-type]


def test_write_once_does_not_block_on_a_stalled_gc_sweep_enumeration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-75 companion: with candidate enumeration off-lock, a `write_once()`
    on a SEPARATE instance must not block on a concurrent `gc_sweep()`
    stalled inside its (now unlocked) `glob()` scan — mirrors
    `test_write_once_does_not_block_on_a_sweep_stalled_in_its_decrypt_phase`'s
    structure for the newly-unlocked enumeration phase instead of decrypt.

    Mutation probe: re-wrapping the enumeration loops back under
    `self._publish_lock` makes the write block for the stall duration
    instead of completing promptly."""
    store_a = _store(tmp_path, ttl_seconds=86400.0)
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,  # type: ignore[attr-defined]
        ttl_seconds=86400.0,
    )
    (tmp_path / "store").mkdir(parents=True, exist_ok=True)
    # A fresh instance's `_last_gc_at` starts at 0.0 — suppress store_b's
    # OWN opportunistic sweep so the property under test (a write not
    # blocking on ANOTHER thread's stalled sweep) isn't confounded by its
    # own nested `gc_sweep()` call hitting the same stalled mock.
    store_b._last_gc_at = time.time()  # type: ignore[attr-defined]

    enumeration_entered = threading.Event()
    enumeration_may_proceed = threading.Event()
    real_glob = Path.glob
    calls = {"n": 0}

    def _stalled_glob(self: Path, pattern: str) -> object:
        if self == store_a._root:  # type: ignore[attr-defined]
            calls["n"] += 1
            if calls["n"] == 1:
                enumeration_entered.set()
                enumeration_may_proceed.wait(timeout=5.0)
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", _stalled_glob)

    sweep_results: list[list[str]] = []

    def _run_sweep() -> None:
        sweep_results.append(store_a.gc_sweep(now=time.time()))

    sweeper = threading.Thread(target=_run_sweep)
    sweeper.start()
    assert enumeration_entered.wait(timeout=5.0), "sweep never reached its enumeration phase"

    write_results: list[object] = []

    def _run_write() -> None:
        write_results.append(store_b.write_once("tenant-b", "must not block on the stalled scan"))

    # The join window's exact size is INCIDENTAL to the claim — any bound
    # comfortably below the mock's 5s stall discriminates identically, because
    # under the mutation the write cannot return until the stall ends. Widened
    # from 0.3s purely for CI-load headroom (a genuine, unblocked
    # `write_once()` — pickle + Fernet + three fsyncs — can take far longer
    # than 0.3s on a loaded runner without any lock being involved), which
    # costs the mutation-kill direction nothing. Mirrors the same widening
    # applied to the sibling
    # `test_write_once_does_not_block_on_a_sweep_stalled_in_its_decrypt_phase`
    # at PR #1226; that arc's merge-gate lens 1 flagged this same-shape join as
    # the one left un-widened, and this is that follow-up.
    writer = threading.Thread(target=_run_write)
    writer.start()
    writer.join(timeout=1.5)
    assert not writer.is_alive(), (
        "write_once() was still blocked 1.5s after starting — it waited on "
        "the stalled enumeration's lock instead of completing promptly"
    )
    assert len(write_results) == 1

    enumeration_may_proceed.set()
    sweeper.join(timeout=5.0)
    assert not sweeper.is_alive()

    write_result = write_results[0]
    assert isinstance(write_result, str)
    assert store_b.read("tenant-b", write_result) == "must not block on the stalled scan"
    assert sweep_results == [[]]


def test_gc_sweep_does_not_collect_unexpired_entries(tmp_path: Path) -> None:
    store = _store(tmp_path, ttl_seconds=86400.0)
    store.write_once("tenant-a", "fresh entry")
    expired = _sweep_past_grace(store, now=time.time())
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
    # Two writes, not one: the `B-96` durable grace means the sweep this write
    # triggers only RECORDS `entry_a`'s first observation; reclaim additionally
    # needs a TTL of elapsed time since that record, which the back-dating
    # supplies without disturbing `entry_a`'s own mtime classification.
    # Re-grounded from the `B-77` sweep-COUNT form (U-RT-150 AC #13), where the
    # second write's sweep alone sufficed.
    store.write_once("tenant-a", "records the expired entry")
    assert entry_a.exists()
    _backdate_observation_record(store)
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
    # `B-96` durable grace: the rigged unlink below is only reached for an
    # entry whose recorded first observation is already a TTL old — this
    # priming sweep records it, and the back-dating ages it (U-RT-150 AC #13,
    # re-grounded from the `B-77` sweep-COUNT form).
    store.gc_sweep()
    _backdate_observation_record(store)

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
        # First call is the temp-file's own DATA fsync; second is the
        # temp-file's own pre-commit METADATA (mtime) fsync (B-77); third
        # is the DESTINATION-directory fsync (`_fsync_dir`, after the
        # commit) — the one this fix targets. A fourth call (the entry's
        # own post-commit metadata fsync, B-77) follows but is unreached
        # once this one raises.
        if calls["n"] == 3:
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
        # See the discrimination note in the test above — the directory
        # fsync is the THIRD call (B-77 inserted a temp-file metadata
        # fsync as the second, pre-commit, and an entry metadata fsync as
        # a fourth, post-commit).
        if calls["n"] == 3:
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

    _sweep_past_grace(store, now=time.time())
    assert not orphan.exists()


def test_gc_sweep_does_not_reclaim_fresh_temp_files(tmp_path: Path) -> None:
    """A temp file mid-write (well within the TTL) must NOT be reclaimed —
    only a genuinely stale (crash-orphaned) one."""
    store = _store(tmp_path, ttl_seconds=86400.0)
    store_root = tmp_path / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    fresh = store_root / ".tmp-in-progress-write"
    fresh.write_bytes(b"a write still in flight")

    _sweep_past_grace(store, now=time.time())
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
        # `_fsync_dir` opens `store._root` with exactly `os.O_RDONLY`; the
        # temp file's own pre-commit metadata fsync AND the entry's own
        # post-commit metadata fsync (both B-77) ALSO do a bare
        # `os.O_RDONLY` open — flags alone no longer discriminate any of
        # these, so key on the PATH (the directory vs. the temp/entry
        # file) instead. `tempfile.mkstemp` (the SAME write's temp-file
        # creation, earlier in the call chain) uses neither this path nor
        # these flags.
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
        # directory PATH, not flags alone (the temp/entry files' own
        # pre-/post-commit metadata fsyncs, both B-77, ALSO do a bare
        # `os.O_RDONLY` open).
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


def test_crash_between_link_and_post_commit_refresh_survives_a_fresh_bootstrap_sweep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-77 (out-of-family Codex round 8 on the B-68 arc; NARROWED at PR
    #1123, CLOSED here). `_publish_atomic` stamps the mtime TWICE — once on
    the temp file before `os.link` (crash recovery) and once on the entry
    after (normal-path freshness). A process KILLED strictly BETWEEN those
    two leaves a COMPLETE, durably-linked, genuinely-live entry carrying
    only the PRE-commit stamp, which under a short deployment
    `ttl_seconds` looks already expired. The next process's bootstrap sweep
    (`bootstrap/stage_4_od.py`, on a FRESH `ProtectedResultStore` built by
    `protected_result_store_factory`) would then reclaim the only
    recoverable copy of an already-completed paid effect on sight.

    `gc_sweep`'s durable elapsed-time grace closes that: reclaim additionally
    requires a full TTL of elapsed time since the candidate's recorded FIRST
    observation, and a sweep cannot record an observation before the candidate
    exists. The crash is simulated exactly at the registered window — the
    post-commit `os.utime` raises once, and the pre-commit one lands an mtime
    old enough that the surviving entry reads as expired.

    RE-GROUNDED at `B-96` / U-RT-150 AC #13 (see the inline note at the second
    sweep): the closing assertions moved from "reclaimed by the NEXT sweep" to
    "NOT reclaimed by an immediately-following sweep; reclaimed once a TTL of
    elapsed time has passed".

    Mutation probe: removing the elapsed-time conjunct from `gc_sweep`'s
    eligibility predicate (reclaiming every verified candidate outright) makes
    the fresh instance's FIRST sweep collect the entry, and the
    `entry_path.exists()` assertion below fails."""
    store = _store(tmp_path, ttl_seconds=0.05)
    real_utime = os.utime
    calls = {"n": 0}

    def _crashing_utime(path: object, times: object = None, **kwargs: object) -> None:
        calls["n"] += 1
        if calls["n"] == 1:
            # The PRE-commit stamp on the temp file: land it well past the
            # TTL, standing in for a crash window longer than `ttl_seconds`.
            stale = time.time() - 10.0
            real_utime(path, (stale, stale))  # type: ignore[arg-type]
            return
        # The POST-commit stamp on the committed entry: the process dies
        # here, so this refresh never happens.
        raise OSError(errno.EIO, "simulated crash between os.link and the mtime refresh")

    monkeypatch.setattr(os, "utime", _crashing_utime)
    ref = store.write_once("tenant-a", "an already-completed paid effect")
    monkeypatch.undo()

    # The crash left the entry durably committed (that is the whole point —
    # `os.link` already ran), even though the write reported unresolvable.
    assert isinstance(ref, UnresolvableResultRef)
    entry_path = next((tmp_path / "store").glob("*.entry"))

    # A FRESH instance, exactly as the next bootstrap builds one.
    recovered = ProtectedResultStore(
        tmp_path / "store",
        codec=store._codec,  # type: ignore[attr-defined]
        ttl_seconds=0.05,
    )
    first_sweep_at = time.time()
    assert recovered.gc_sweep(now=first_sweep_at, observed_at=first_sweep_at) == []
    assert entry_path.exists(), (
        "the crash-recovered entry was reclaimed by the first bootstrap sweep "
        "that ever saw it — the durable first-observation grace did not hold"
    )

    # RE-PINNED at `B-96` / U-RT-150 AC #13. Under the retired sweep-COUNT
    # grace this was "still expired at the NEXT sweep", and an immediately
    # following sweep collected it — the very residue `B-96` names, since a
    # short run's own shutdown sweep fires milliseconds later. Under the
    # elapsed-time rule an immediately-following sweep must NOT reclaim, and
    # reclaim arrives only once a full TTL has elapsed since the recorded first
    # observation. Both halves are asserted, so the witness still proves
    # bounded retention rather than immunity.
    assert recovered.gc_sweep(now=first_sweep_at + 0.01) == [], (
        "an immediately-following sweep reclaimed the entry — the grace is "
        "still bounded by sweep COUNT rather than by elapsed time"
    )
    assert entry_path.exists()
    assert recovered.gc_sweep(now=first_sweep_at + 0.06) == [entry_path.stem]
    assert not entry_path.exists()


def test_uninterrupted_write_survives_an_immediate_sweep_past_the_grace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-77 normal-path regression guard (the PR #1123 round-2 defect class,
    reproduced by out-of-family Codex round 9 [P1]): a SUCCESSFUL,
    uninterrupted `write_once()` must never return a reference an immediate
    sweep reclaims. The first-observation grace must not be what carries
    that property — the post-commit mtime stamp still must — so this
    witness sweeps TWICE at the same instant, past the grace, and still
    expects the entry live.

    Same shape as the round-9 reproduction: a 20ms TTL with the
    DESTINATION-directory fsync (the third `fsync` call, below the
    pre-commit stamp) slowed.

    Mutation probe: removing `_publish_atomic`'s POST-commit
    `os.utime(entry_path, None)` refresh leaves the entry carrying the
    pre-commit stamp, a full slow-tail duration stale on return — the
    second sweep then reclaims it and this test fails.

    A NUANCE in the other direction, recorded so the PD-8 matrix is not
    misread (PR #1226's merge-gate lens 3): the drop-PRE-commit-stamp mutation
    ALSO fails this test, but that kill is an ORDERING ARTIFACT rather than a
    semantic one — removing the pre-commit stamp removes its own `fsync`, so
    the `calls["n"] == 3` counter below lands on a DIFFERENT `fsync` and the
    clock advance moves. This witness pins the POST-commit stamp; the
    pre-commit one has its own dedicated witness, so there is no coverage gap.

    CI-load hardening: that slow tail is simulated by ADVANCING a
    `_ScriptedClock` both the store's mtime stamps and this sweep's `now=`
    read, not by a real `time.sleep` raced against the 20ms TTL — see
    `_ScriptedClock`. This test is one of the recorded CI flakes (PRs
    #1103/#1130/#1213/#1223: the wall time between the post-commit stamp
    and the sweep's own `time.time()` exceeded the TTL under load, so a
    correctly-stamped entry read as expired)."""
    store = _store(tmp_path, ttl_seconds=0.02)
    clock = _ScriptedClock()
    _pin_mtime_stamps_to_clock(monkeypatch, clock)
    real_fsync = os.fsync
    calls = {"n": 0}

    def _slow_third_fsync(fd: int) -> None:
        calls["n"] += 1
        if calls["n"] == 3:
            clock.advance(_SIMULATED_SLOW_STEP_SECONDS)
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", _slow_third_fsync)
    ref = store.write_once("tenant-a", "uninterrupted, must stay live")
    assert isinstance(ref, str)

    assert _sweep_past_grace(store, now=clock.now) == []
    assert store.read("tenant-a", ref) == "uninterrupted, must stay live"


def test_genuinely_expired_entry_is_reclaimed_once_the_grace_elapses(
    tmp_path: Path,
) -> None:
    """Liveness bound (U-RT-150 AC #14(ii)), RE-GROUNDED at AC #13 from the
    retired `B-77` sweep-COUNT form: the grace must DELAY reclaim, never grant
    immunity — the spec v1.103 §14.8.11 bounded-retention term still holds (a
    signing outage must not grow an unbounded store of sensitive payloads).

    Renamed because the property it pins changed: reclaim is no longer keyed on
    the SECOND SWEEP but on a TTL of ELAPSED TIME since the recorded first
    observation. The middle assertion is the discriminator `B-96` exists for —
    a second sweep firing immediately after the first (the short-run shutdown
    sweep) must NOT reclaim.

    Mutation probes (three directions): dropping the elapsed-time conjunct
    makes the FIRST sweep reclaim and its `[] ==` assertion fails; making the
    elapsed conjunct unsatisfiable (never recording an observation) makes the
    LAST sweep return `[]`; keying the grace on sweep COUNT again makes the
    immediately-following middle sweep reclaim."""
    store = _store(tmp_path, ttl_seconds=1.0)
    ref = store.write_once("tenant-a", "genuinely expires")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    sweep_at = time.time() + 10.0

    assert store.gc_sweep(now=sweep_at, observed_at=sweep_at) == []
    assert entry_path.exists()

    # A second sweep milliseconds later — the short-or-failing-run shape.
    assert store.gc_sweep(now=sweep_at + 0.001) == []
    assert entry_path.exists()

    assert store.gc_sweep(now=sweep_at + 1.5) == [entry_path.stem]
    assert not entry_path.exists()


def test_coarse_filesystem_mtime_granularity_does_not_lose_a_live_entry_on_sight(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """B-74 re-assessment against the landed B-77 grace. On a
    coarse-granularity filesystem the STORED mtime rounds DOWN by up to the
    filesystem's own resolution (up to ~1s at 1-second resolution), so a
    `ttl_seconds` shorter than that rounding error makes a just-published,
    genuinely-live entry read as already expired — the store's own refresh
    working exactly as designed, the filesystem simply unable to represent
    the precision it relies on.

    Simulated by flooring every `os.utime(path, None)` refresh to whole
    seconds (the store's OWN stamp lands coarse, as it would on such a
    volume) with a 100ms TTL.

    `B-74` CLOSES HERE, and this witness is RE-PINNED AS A POSITIVE ONE
    (U-RT-150 AC #13 + the `B-96` ratification record §8). Under the retired
    sweep-COUNT grace the error was absorbed only for the sweep that FIRST
    observed the entry, and a granularity error larger than the gap between two
    sweeps still lost the live entry — the REGISTERED RESIDUAL the closing
    assertion used to pin, in the shape *"the live entry is reclaimed"*. Under
    the ratified elapsed-time rule that residue is DISSOLVED rather than
    narrowed: the inter-sweep gap ceases to be a term in the reclaim decision
    at all, so the closing assertion now witnesses that the LIVE ENTRY SURVIVES
    BOTH SWEEPS — exactly as the row's own close_out instructs — and is kept
    rather than deleted.

    Mutation probes (both directions): removing the elapsed-time conjunct from
    `gc_sweep`'s eligibility predicate makes the first sweep reclaim the live
    entry and the `read()` below raises `ProtectedStoreEntryNotFoundError`;
    re-keying the grace on sweep COUNT makes the second sweep reclaim it and
    the re-pinned `== []` assertion fails.

    CI-load hardening: the publish moment is a `_ScriptedClock` pinned to a
    fixed mid-second PHASE, so the rounding error this witness needs is
    exactly `_COARSE_MTIME_PHASE` on every run. Out-of-family Codex round 1
    [P1] had already identified the phase dependence and answered it with a
    busy-wait for a favourable phase BEFORE the write — but that only fixed
    the phase at the START of `write_once()`, and a write slow enough under
    CI load to cross the next second boundary re-floored the stamp to that
    NEW second, collapsing the error to ~0 and failing the `> 0.1`
    assertion below (a recorded flake: PR #1223,
    `assert (1785922920.0142367 - 1785922920.0) > 0.1`). Pinning the clock
    removes the dependence entirely rather than betting on the write being
    fast — the busy-wait it replaces is deleted."""
    clock = _ScriptedClock()
    # A fixed mid-second phase: the store's own stamp lands on the second
    # boundary below, so the granularity error is exactly this figure —
    # comfortably outside the 100ms TTL, on every run, whatever the load.
    clock.now = float(int(clock.now)) + _COARSE_MTIME_PHASE
    real_utime = os.utime

    def _coarse_utime(path: object, times: object = None, **kwargs: object) -> None:
        if times is None:
            floored = float(int(clock.now))
            real_utime(path, (floored, floored))  # type: ignore[arg-type]
            return
        real_utime(path, times, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "utime", _coarse_utime)
    store = _store(tmp_path, ttl_seconds=0.1)
    ref = store.write_once("tenant-a", "live despite a coarse mtime")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    # The stored mtime is now a full `_COARSE_MTIME_PHASE` behind the true
    # publish moment — far outside the 100ms TTL, so the entry reads as
    # expired.
    assert clock.now - entry_path.stat().st_mtime > 0.1

    assert store.gc_sweep(now=clock.now, observed_at=clock.now) == []
    assert store.read("tenant-a", ref) == "live despite a coarse mtime"

    # `B-74` CLOSED — re-pinned POSITIVE. The second sweep fires immediately
    # after the first (the gap that used to lose the entry), and the live entry
    # SURVIVES: the elapsed-time conjunct is not yet satisfied, and no
    # filesystem granularity error can satisfy it, because the recorded first
    # observation is this store's own wall-clock reading rather than a value
    # the volume rounded.
    assert store.gc_sweep(now=clock.now) == [], (
        "the coarse-mtime live entry was reclaimed by an immediately-following "
        "sweep — the B-74 residue is not dissolved"
    )
    assert entry_path.exists()
    assert store.read("tenant-a", ref) == "live despite a coarse mtime"


def test_observation_record_is_shared_across_instances_of_one_root(tmp_path: Path) -> None:
    """merge-gate round-2 test-witness lens (PR #1163), BLOCKING finding,
    RE-GROUNDED at U-RT-150 AC #13. The observation record must be shared by
    every `ProtectedResultStore` on one root, because the composition root
    builds a FRESH instance per `run()`/`resume()` bootstrap
    (`bootstrap/factories/protected_result_store_factory.py` ->
    `bootstrap/stage_4_od.py`, which sweeps immediately). A per-instance record
    would hand EVERY bootstrap sweep a fresh grace and defer reclaim
    indefinitely, weakening the spec's bounded-retention term.

    Nothing else in this module discriminates that: the crash-recovery
    witness's fresh instance is NOT load-bearing there, because `write_once`
    runs `_maybe_opportunistic_gc_sweep()` before publishing and a fresh
    instance's `_last_gc_at = 0.0` makes that pre-publish sweep always fire.
    This test pins the property directly: instance A observes the expired
    entry, then a SECOND instance on the SAME root reclaims it on ITS OWN FIRST
    sweep once the grace has elapsed, inheriting A's observation.

    What changed at `B-96`: the sharing carrier is no longer the module-level
    `_root_observed_expired` registry keyed by filesystem identity but the
    DURABLE record in the root itself — which is strictly stronger, since it
    survives process exit as well as instance churn (that half is witnessed
    across real processes by `test_one_shot_process_invocations_...`).

    Mutation probe: making the record an instance attribute (e.g. an
    in-memory `self._observed` dict initialized in `__init__` instead of the
    durable file) makes instance B's sweep return `[]` and this test fails."""
    store_a = _store(tmp_path, ttl_seconds=1.0)
    ref = store_a.write_once("tenant-a", "observed by A, reclaimed by B")
    assert isinstance(ref, str)
    entry_path = store_a._entry_path(ref)  # type: ignore[attr-defined]
    sweep_at = time.time() + 10.0

    # A observes it past TTL (grace: no reclaim).
    assert store_a.gc_sweep(now=sweep_at, observed_at=sweep_at) == []
    assert entry_path.exists()

    # A genuinely fresh instance on the SAME root — exactly what the next
    # bootstrap constructs.
    store_b = ProtectedResultStore(
        tmp_path / "store",
        codec=store_a._codec,  # type: ignore[attr-defined]
        ttl_seconds=1.0,
    )
    assert store_b.gc_sweep(now=sweep_at + 1.5) == [entry_path.stem], (
        "a second instance's sweep did not inherit the first instance's "
        "observation — the record is per-instance, not per-root"
    )
    assert not entry_path.exists()


def test_observation_records_are_keyed_per_root_not_one_global_set(tmp_path: Path) -> None:
    """merge-gate round-2 test-witness lens (PR #1163), rider 1, RE-GROUNDED at
    U-RT-150 AC #13. The record is per-ROOT and REPLACED wholesale on each
    sweep (that replacement is what keeps it bounded). Those two facts only
    compose safely because the record is per-root: one shared, un-keyed record
    replaced each sweep would let alternating sweeps of two distinct roots wipe
    each other's observations and starve reclaim indefinitely.

    Under `B-96` the per-root property is carried by the record's RESIDENCE —
    it lives in the store root it indexes — rather than by a filesystem-identity
    key into a module-wide dict. Both roots' records are asserted to hold only
    their own root's names, which is the property directly.

    Mutation probe: pointing `_observation_record_path` at a single shared
    location (e.g. a fixed path outside the root) makes each root's later sweep
    return `[]` — the other root's sweep having replaced the shared record —
    and this test fails."""
    store_1 = _store(tmp_path / "one", ttl_seconds=1.0)
    store_2 = ProtectedResultStore(
        tmp_path / "two" / "store",
        codec=store_1._codec,  # type: ignore[attr-defined]
        ttl_seconds=1.0,
    )
    ref_1 = store_1.write_once("tenant-a", "root one")
    ref_2 = store_2.write_once("tenant-a", "root two")
    assert isinstance(ref_1, str) and isinstance(ref_2, str)
    entry_1 = store_1._entry_path(ref_1)  # type: ignore[attr-defined]
    entry_2 = store_2._entry_path(ref_2)  # type: ignore[attr-defined]
    sweep_at = time.time() + 10.0

    # Interleaved first observations — neither may disturb the other's.
    assert store_1.gc_sweep(now=sweep_at, observed_at=sweep_at) == []
    assert store_2.gc_sweep(now=sweep_at, observed_at=sweep_at) == []

    # Each root's record holds ONLY that root's own candidate name.
    assert set(_read_observation_record(store_1)) == {entry_1.name}
    assert set(_read_observation_record(store_2)) == {entry_2.name}

    assert store_1.gc_sweep(now=sweep_at + 1.5) == [entry_1.stem]
    assert store_2.gc_sweep(now=sweep_at + 1.5) == [entry_2.stem]
    assert not entry_1.exists()
    assert not entry_2.exists()


def test_crash_orphaned_temp_file_survives_its_first_observed_sweep(tmp_path: Path) -> None:
    """merge-gate round-2 test-witness lens (PR #1163), rider 2. The grace
    covers `.tmp-*` crash orphans uniformly with `*.entry` — one rule, no
    branch — and `test_gc_sweep_reclaims_crash_orphaned_temp_files` only
    asserts EVENTUAL reclaim (it sweeps past the grace), so nothing pinned
    the tmp half of the gate.

    RE-GROUNDED at U-RT-150 AC #13 + AC #5: the second half now waits for the
    ELAPSED grace rather than for a second sweep, and an intervening
    immediately-following sweep is asserted NOT to reclaim.

    Mutation probes (both directions): dropping the elapsed-time conjunct from
    the tmp path alone (`tmp_candidates = verified_tmp`) makes the first sweep
    reclaim the orphan; restricting the record's key to the published-entry
    class leaves the orphan's conjunct (b) permanently unsatisfiable and the
    final reclaim assertion fails."""
    store = _store(tmp_path, ttl_seconds=1.0)
    store_root = tmp_path / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    orphan = store_root / ".tmp-crash-orphan-first-observation"
    orphan.write_bytes(b"partial ciphertext from a killed write")
    old_time = time.time() - 10.0
    os.utime(orphan, (old_time, old_time))
    sweep_at = time.time()

    store.gc_sweep(now=sweep_at, observed_at=sweep_at)
    assert orphan.exists(), (
        "a crash-orphaned temp file was reclaimed by the sweep that FIRST "
        "observed it — the grace does not cover the .tmp-* path"
    )
    assert set(_read_observation_record(store)) == {orphan.name}

    store.gc_sweep(now=sweep_at + 0.001)
    assert orphan.exists(), "the orphan was reclaimed by an immediately-following sweep"

    store.gc_sweep(now=sweep_at + 1.5)
    assert not orphan.exists()


def test_observe_candidates_runs_while_the_publish_lock_is_held(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """merge-gate round-2 test-witness lens (PR #1163), rider 4, RE-GROUNDED at
    U-RT-150 AC #13 onto the renamed `_observe_candidates`.
    `_observe_candidates`'s docstring claims it is called with
    `self._publish_lock` held — that is what stops two concurrent sweeps of one
    root from interleaving a read with the other's replace (a lost observation,
    hence a premature reclaim). Under `B-96` the same lock ALSO makes the
    wall-clock sample the term-3 LOCKED, POST-RE-VERIFICATION point, so this
    structural pin now carries two properties rather than one.

    Same shape as `test_gc_sweep_candidate_enumeration_runs_without_holding_
    publish_lock` (`[[verification-shape-sharpened-grep-vs-e2e]]`: assert
    lock-identity, not a race outcome): record whether the lock is held at the
    moment the call is made.

    Mutation probe: hoisting the `self._observe_candidates(...)` call out of
    `gc_sweep`'s `with self._publish_lock, self._cross_process_lock():` block
    records `False` and this test fails."""
    store = _store(tmp_path, ttl_seconds=0.01)
    ref = store.write_once("tenant-a", "will be swept")
    assert isinstance(ref, str)
    time.sleep(0.05)  # comfortably past the 0.01s TTL

    lock_held_at_call: list[bool] = []
    real_observe = store._observe_candidates  # type: ignore[attr-defined]

    def _recording_observe(names: list[str], **kwargs: object) -> object:
        lock_held_at_call.append(store._publish_lock.locked())  # type: ignore[attr-defined]
        return real_observe(names, **kwargs)

    monkeypatch.setattr(store, "_observe_candidates", _recording_observe)

    store.gc_sweep(now=time.time())

    assert lock_held_at_call == [True], (
        f"_observe_candidates was called with `_publish_lock` UNHELD: {lock_held_at_call}"
    )


# ---------------------------------------------------------------------------
# `B-96` / U-RT-150 — durable, publication-bounded, elapsed-time GC reclaim
# grace (Runtime spec v1.111 §14.8.11.1, terms 1-12 + the record's carrier).
# ---------------------------------------------------------------------------


def _stale_entry(
    tmp_path: Path, *, ttl_seconds: float, age_seconds: float
) -> tuple[ProtectedResultStore, Path]:
    """A store holding ONE published entry whose filesystem timestamp already
    reads `age_seconds` old — the shape every conjunct-(a)-satisfied witness
    below needs, without waiting for real time to pass."""
    store = _store(tmp_path, ttl_seconds=ttl_seconds)
    ref = store.write_once("tenant-a", "an already-completed paid effect")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    stale = time.time() - age_seconds
    os.utime(entry_path, (stale, stale))
    return store, entry_path


def test_reclaim_requires_both_conjuncts_and_admits_no_third_path(tmp_path: Path) -> None:
    """AC #1 — reclaim is ELIGIBLE iff BOTH the filesystem-timestamp age AND
    the elapsed time since the durably recorded first observation are past the
    TTL. The four-cell matrix is asserted, not just the positive diagonal, so
    the witness pins a CONJUNCTION rather than either half.

    Eligibility is the contract; COLLECTION is best-effort and deliberately
    allowed to fail (a removal `OSError` is caught, logged and skipped — see
    `test_gc_unlink_failure_does_not_propagate_or_replace_the_carrier`), so
    this witness asserts the eligibility decision, never that every eligible
    entry is always collected.

    Mutation probes (both directions): relaxing the predicate to conjunct (a)
    alone reclaims in the fresh-observation cell; relaxing it to conjunct (b)
    alone reclaims in the young-file cell."""
    ttl = 1.0

    # Cell 1 — timestamp past TTL, observation FRESH: NOT eligible.
    store, entry_path = _stale_entry(tmp_path / "a", ttl_seconds=ttl, age_seconds=10.0)
    at = time.time()
    assert store.gc_sweep(now=at, observed_at=at) == []
    assert entry_path.exists()

    # Cell 2 — timestamp past TTL, observation ALSO past TTL: eligible.
    assert store.gc_sweep(now=at + 1.5) == [entry_path.stem]
    assert not entry_path.exists()

    # Cell 3 — observation past TTL, timestamp YOUNG: NOT eligible. The entry
    # is observed while stale, then its timestamp is refreshed before the
    # second sweep, so only conjunct (b) holds.
    store_2, entry_2 = _stale_entry(tmp_path / "b", ttl_seconds=ttl, age_seconds=10.0)
    at_2 = time.time()
    assert store_2.gc_sweep(now=at_2, observed_at=at_2) == []
    fresh = at_2 + 1.4
    os.utime(entry_2, (fresh, fresh))
    assert store_2.gc_sweep(now=at_2 + 1.5) == [], (
        "an entry whose filesystem timestamp is YOUNG was reclaimed on the "
        "strength of its observation alone — conjunct (a) is not gating"
    )
    assert entry_2.exists()

    # Cell 4 — neither conjunct: NOT eligible (the ordinary fresh-store case).
    store_3 = _store(tmp_path / "c", ttl_seconds=ttl)
    ref_3 = store_3.write_once("tenant-a", "fresh")
    assert isinstance(ref_3, str)
    now_3 = time.time()
    assert store_3.gc_sweep(now=now_3, observed_at=now_3) == []
    assert store_3.gc_sweep(now=now_3 + 0.1) == []


def test_no_absolute_ceiling_reclaims_an_ancient_entry_inside_its_grace(
    tmp_path: Path,
) -> None:
    """AC #1's *no third path* half, in the direction a `k × ttl_seconds`
    ceiling would break (ratified form C-2: NO absolute reclaim ceiling of any
    kind). An entry whose filesystem timestamp reads ONE HUNDRED TTLs old, but
    whose first observation is fresh, must survive every sweep inside its
    grace — under any ceiling term it would be reclaimed at once.

    Mutation probe: adding `or age > k * self._ttl_seconds` to the eligibility
    predicate for any finite `k` reclaims the entry at the first sweep."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=100.0 * ttl)
    at = time.time()
    assert store.gc_sweep(now=at, observed_at=at) == []
    for offset in (0.1, 0.3, 0.6, 0.9):
        assert store.gc_sweep(now=at + offset) == [], (
            f"a 100×TTL-old entry was reclaimed {offset}s into its grace — an "
            f"absolute age ceiling is gating reclaim"
        )
        assert entry_path.exists()
    # And it IS reclaimed once the grace itself elapses — the ceiling's absence
    # does not become immortality.
    assert store.gc_sweep(now=at + 1.5) == [entry_path.stem]


def test_reclaim_never_precedes_publication_plus_ttl_under_an_under_reporting_mtime(
    tmp_path: Path,
) -> None:
    """AC #2 — the PUBLICATION BOUND. For an entry published at `t_pub`, no
    reclaim occurs before `t_pub + TTL`, across an arbitrary number of sweeps
    and INDEPENDENT of the recorded filesystem timestamp — including the
    crash-window shape `B-77` / `B-74` name, where that timestamp UNDER-REPORTS
    publication by an unbounded amount (simulated here as ten seconds against a
    one-second TTL).

    SCOPE, stated so this is not read as proving more than it does: the bound
    holds under spec term 2's stated assumption — a wall clock FREE OF STEP
    DISCONTINUITIES IN EITHER DIRECTION between publication and reclaim. A
    backward step before the first observation, or a forward step larger than
    the TTL at any point before reclaim, each break it; closing that residual is
    NOT owed by this unit (it is a property of the store's wall-clock age
    authority as a whole, and the pre-existing timestamp comparison carries it
    identically), and substituting a monotonic clock is FORBIDDEN because the
    observation state is durable across process exit. The sweep instants below
    are therefore asserted to be MONOTONICALLY NON-DECREASING, so a
    backward-stepping clock can never pass this witness as evidence of the
    unconditional bound.

    Mutation probes: sampling the first observation before the existence
    re-verification, or reintroducing a mtime-only reclaim path, reclaims at the
    very first sweep (the timestamp already reads 10× the TTL)."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    t_pub = time.time()

    sweep_instants = [t_pub + offset for offset in (0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99)]
    assert sweep_instants == sorted(sweep_instants), (
        "the sweep instants are not monotonically non-decreasing — a "
        "backward-stepping clock would make this witness vacuous"
    )
    for index, instant in enumerate(sweep_instants):
        observed_at = instant if index == 0 else None
        assert store.gc_sweep(now=instant, observed_at=observed_at) == [], (
            f"reclaim occurred {instant - t_pub:.2f}s after publication, before "
            f"publication + TTL ({ttl}s)"
        )
        assert entry_path.exists()

    assert store.gc_sweep(now=t_pub + ttl + 0.01) == [entry_path.stem]


def test_first_observed_at_is_sampled_under_the_lock_after_re_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #3 — `first_observed_at` is a WALL-CLOCK value sampled at the LOCKED,
    POST-RE-VERIFICATION observation point, NEVER at the sweep's pre-enumeration
    clock read. Asserted BY CONSTRUCTION on two independent axes:

    (i) the two clock seams are DISTINCT — driven to different values, the
        recorded stamp is the observation-point one, and the pre-enumeration
        `now` is not obtainable from the record; and
    (ii) with both seams left to their production default, the candidate's
        existence has ALREADY been re-verified under the lock by the time the
        sample is taken — the entry has been `stat`-ed at least twice (the
        unlocked provisional pass and the locked re-verify pass).

    The lock-HELD half is pinned separately by
    `test_observe_candidates_runs_while_the_publish_lock_is_held`.

    Mutation probe: moving the sample to the pre-enumeration `now` read makes
    (i) record the pre-enumeration value; moving the `_observe_candidates` call
    above the locked re-verify loop makes (ii) see one `stat` instead of two —
    the same relocation AC #2's witness independently kills."""
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)

    # (i) two independently drivable seams.
    pre_enumeration = time.time()
    observation_point = pre_enumeration + 4321.0
    store.gc_sweep(now=pre_enumeration, observed_at=observation_point)
    recorded = _read_observation_record(store)
    assert recorded == {entry_path.name: observation_point}
    assert recorded[entry_path.name] != pre_enumeration

    # (i-bis) and with the observation seam left to its PRODUCTION default, the
    # recorded stamp is STILL not obtainable from the pre-enumeration read —
    # the half that discriminates a default-path implementation quietly reusing
    # `now` when no `observed_at` is supplied. `now` is driven far from the real
    # clock so the two are unmistakably distinguishable. Its OWN store, because
    # a `now` that far ahead legitimately reclaims on the spot.
    other, other_entry = _stale_entry(tmp_path / "default-seam", ttl_seconds=1.0, age_seconds=10.0)
    far_future = pre_enumeration + 100_000.0
    other.gc_sweep(now=far_future)
    defaulted = _read_observation_record(other)[other_entry.name]
    assert defaulted != far_future, (
        "with no `observed_at` supplied the sweep recorded its own "
        "pre-enumeration `now` — the sample is not taken at the observation point"
    )
    assert abs(defaulted - time.time()) < 60.0, (
        f"the default sample is not a wall-clock reading taken during the sweep: {defaulted}"
    )

    # (ii) re-verification precedes the sample.
    _observation_record_path(store).unlink()
    stat_calls = {"n": 0}
    real_stat = Path.stat

    def _counting_stat(self: Path, **kwargs: object) -> object:
        if self == entry_path:
            stat_calls["n"] += 1
        return real_stat(self, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "stat", _counting_stat)
    stats_at_sample: list[int] = []
    real_observe = store._observe_candidates  # type: ignore[attr-defined]

    def _recording_observe(names: list[str], **kwargs: object) -> object:
        stats_at_sample.append(stat_calls["n"])
        return real_observe(names, **kwargs)

    monkeypatch.setattr(store, "_observe_candidates", _recording_observe)
    store.gc_sweep()
    assert stats_at_sample and stats_at_sample[0] >= 2, (
        f"the observation was sampled after only {stats_at_sample} stat call(s) "
        f"on the candidate — the locked re-verification had not run yet"
    )


def test_a_deleted_record_begins_a_fresh_grace_and_can_only_lengthen_retention(
    tmp_path: Path,
) -> None:
    """AC #4 — the record is a DERIVED INDEX, never an authority. With the
    record DELETED between two sweeps, a past-TTL entry is NOT reclaimed at the
    next sweep: a fresh grace begins.

    SCOPE, exactly as spec term 4 scopes it — to record LOSS. An ABSENT record
    (and, per AC #11, an UNREADABLE one) can only LENGTHEN retention and MUST
    NOT be able to shorten it. This is NOT a universal over every record state:
    a STALE BUT READABLE row surviving a removed-then-reused temporary name is a
    distinct case AC #5 explicitly permits and registered row `B-110` tracks,
    and asserting this property universally would make the two ACs mutually
    unsatisfiable.

    Mutation probe: treating an absent record as *observed long ago* (e.g.
    defaulting a missing `first_observed_at` to `0.0` instead of the sample
    time) reclaims at the sweep after the deletion."""
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    at = time.time()
    assert store.gc_sweep(now=at, observed_at=at) == []
    assert _observation_record_path(store).exists()

    _observation_record_path(store).unlink()

    # Well past the grace the FIRST observation would have granted — and still
    # not reclaimed, because that observation no longer exists.
    assert store.gc_sweep(now=at + 5.0, observed_at=at + 5.0) == [], (
        "a past-TTL entry was reclaimed at the sweep following record deletion "
        "— record loss SHORTENED retention"
    )
    assert entry_path.exists()
    # The fresh grace is a grace, not immunity.
    assert store.gc_sweep(now=at + 6.5) == [entry_path.stem]


def test_record_content_set_is_closed_at_two_members_and_discloses_nothing(
    tmp_path: Path,
) -> None:
    """AC #5 — the record's content is EXACTLY `{candidate filename,
    first_observed_at}` per name, CLOSED at two members, over BOTH sweep
    classes. The REFUSALS are asserted, not merely the presence: the persisted
    bytes carry no composite key in whole or in part, no tenant tag, no
    plaintext and no ciphertext — a known sentinel written through the store is
    absent from the raw bytes AND from their base64 and utf-8 decodings.

    Mutation probe: adding any third member (a tenant tag, the composite key, a
    ciphertext digest) to the published payload fails the closed-set assertion;
    keying on the composite key rather than the candidate filename fails the
    key-shape and no-composite-key assertions together."""
    import base64

    sentinel = "SENTINEL-PAYLOAD-b96-must-never-reach-the-record"
    store = _store(tmp_path, ttl_seconds=1.0)
    ref = store.write_once("tenant-a", sentinel)
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    stale = time.time() - 10.0
    os.utime(entry_path, (stale, stale))
    orphan = (tmp_path / "store") / ".tmp-b96-closed-set-orphan"
    orphan.write_bytes(b"partial ciphertext from a killed write")
    os.utime(orphan, (stale, stale))

    at = time.time()
    store.gc_sweep(now=at, observed_at=at)

    raw = _observation_record_path(store).read_bytes()
    document = json.loads(raw.decode("utf-8"))
    # CLOSED at two members: the document's own keys are form metadata plus the
    # observations map, and each ROW is exactly `name -> first_observed_at`.
    assert set(document) == {"version", "observations"}
    assert document["observations"] == {entry_path.name: at, orphan.name: at}

    # The refusals — over the raw bytes and both decodings a reader might apply.
    decodings = [raw, raw.decode("utf-8").encode("utf-8"), base64.b64encode(raw)]
    forbidden = [
        sentinel.encode("utf-8"),
        ref.encode("utf-8"),
        ref.split(":", 1)[1].encode("utf-8"),  # the uuid4 half of the composite key
        b"tenant-a",
        entry_path.read_bytes()[:32],  # a ciphertext prefix
    ]
    for blob in decodings:
        for secret in forbidden:
            assert secret not in blob, f"{secret!r} leaked into the observation record"


def test_reused_temporary_name_stays_bounded_by_its_own_filesystem_timestamp(
    tmp_path: Path,
) -> None:
    """AC #5's NAME-REUSE BOUND — the registered residual `B-110`, witnessed at
    exactly the strength the ratified carrier can deliver and no further.

    A temporary name is drawn by a mechanism that avoids only names CURRENTLY
    PRESENT, so once an orphan is removed its name is redrawable and a surviving
    record row can match a DIFFERENT later file. This witnesses the bound that
    SURVIVES that: conjunct (a) is keyed on the NEW file's own filesystem
    timestamp, so the recreated file is NOT reclaimed before `new_mtime + TTL`.

    WHAT THIS DOES **NOT** WITNESS, stated so the assertion is never read as
    more: it does NOT witness spec TERM 2. Term 2 bounds reclaim by
    PUBLICATION; a temporary orphan is not a published entry, and on a volume
    whose timestamps under-report creation `new_mtime + TTL` can elapse before
    the new file's own creation + TTL. That overstatement is exactly what
    `B-110` records as lost, and closing it is NOT owed by this unit. Nor does
    this assert that the new file receives a FRESH `first_observed_at` — the
    record's ratified content set is closed at two members and carries no
    generation identity, so such an assertion would be unsatisfiable and an
    implementation contorted to pass it would be widening a ratified closed set.

    Mutation probe: dropping conjunct (a) so a stale record row alone can
    reclaim makes the recreated file disappear at the first post-recreation
    sweep."""
    ttl = 1.0
    store = _store(tmp_path, ttl_seconds=ttl)
    store_root = tmp_path / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    orphan = store_root / ".tmp-b110-reused-name"
    orphan.write_bytes(b"generation one")
    stale = time.time() - 10.0
    os.utime(orphan, (stale, stale))

    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    assert set(_read_observation_record(store)) == {orphan.name}

    # The surviving row is aged well past its own grace, so conjunct (b) is
    # satisfied for the reused name — the degraded state `B-110` names.
    _backdate_observation_record(store, by=10.0)

    # Generation one is removed; a DIFFERENT file takes the same name, and its
    # own timestamp is fresh.
    orphan.unlink()
    orphan.write_bytes(b"generation two - a different file, the same name")
    recreated_at = at + 0.05
    os.utime(orphan, (recreated_at, recreated_at))

    # BEFORE the new file's own timestamp + TTL: conjunct (a) still gates it,
    # even though the stale row has already satisfied conjunct (b).
    assert store.gc_sweep(now=recreated_at + ttl - 0.1) == []
    assert orphan.exists(), (
        "a recreated file bearing a reused temporary name was reclaimed before "
        "its OWN filesystem timestamp plus the TTL — conjunct (a) is not gating"
    )
    assert orphan.read_bytes() == b"generation two - a different file, the same name"

    # AFTER it, the timestamp-derived bound is met and the file is reclaimed —
    # which is precisely the degradation `B-110` records: for this ONE candidate
    # the reclaim bound falls back to the pre-existing timestamp-derived one,
    # rather than gaining the additional grace a fresh observation would give.
    assert store.gc_sweep(now=recreated_at + ttl + 0.1) == []
    assert not orphan.exists()


def test_absent_record_emits_the_reset_as_an_observed_fact_never_a_diagnosis(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #6 — when a sweep finds one or more past-TTL candidates AND reads no
    observation record, it emits a typed report-log line carrying the observed
    state and NOTHING BEYOND IT: that no record was read, the COUNT of past-TTL
    candidates OVER BOTH CLASSES, the oldest resident candidate's age from the
    same timestamp pass, and that a fresh grace begins.

    The MUST-NOTs are asserted: the line does not assert, name or classify the
    record as LOST, and emits no verdict. Emission is UNCONDITIONAL and
    PER-OCCURRENCE — it fires on the FIRST occurrence, with no in-process
    suppression and no waiting for a second.

    Mutation probe: adding a *record lost* classification (or any verdict word)
    fails the MUST-NOT assertions; suppressing the first occurrence, or gating
    on a second, fails the first-occurrence assertion."""
    import logging

    store, _entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    orphan = (tmp_path / "store") / ".tmp-b96-reset-line-orphan"
    orphan.write_bytes(b"partial ciphertext")
    stale = time.time() - 20.0
    os.utime(orphan, (stale, stale))

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)

    reset_lines = [r for r in caplog.records if "no GC observation record was read" in r.message]
    assert len(reset_lines) == 1, (
        "the reset line did not fire on the FIRST occurrence, or fired more "
        f"than once for one sweep: {[r.message for r in caplog.records]}"
    )
    message = reset_lines[0].message
    assert "past_ttl_entries=1" in message
    assert "past_ttl_orphans=1" in message  # BOTH classes are counted
    assert "oldest_entry_age_s=" in message and "oldest_orphan_age_s=" in message
    assert "fresh grace begins" in message
    lowered = message.lower()
    for forbidden in ("lost", "loss", "corrupt", "verdict", "fail", "error", "invalid"):
        assert forbidden not in lowered, (
            f"the reset line classifies the record ({forbidden!r}) — it must "
            f"state the observed state and nothing beyond it"
        )


def test_typical_worst_case_retention_is_two_ttls_from_publication(tmp_path: Path) -> None:
    """AC #7's positive half — the TYPICAL worst case is `2 × TTL` plus up to
    two sweep-trigger intervals: one interval to the first post-TTL observation,
    one more to the post-grace reclaim. Driven on a pinned clock: sweeps at
    `t_pub`, at `t_pub + TTL + ε` (the first post-TTL observation), and at
    `t_pub + 2×TTL + ε` (the reclaim).

    Mutation probe: dropping the elapsed conjunct collapses this to `1 × TTL`
    and the middle assertion fails."""
    ttl = 1.0
    store = _store(tmp_path, ttl_seconds=ttl)
    ref = store.write_once("tenant-a", "retained for two TTLs")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    t_pub = time.time()
    os.utime(entry_path, (t_pub, t_pub))

    # Sweep 1, at publication: not even past the TTL yet.
    assert store.gc_sweep(now=t_pub, observed_at=t_pub) == []
    # Sweep 2, one TTL later: past-TTL and FIRST observed — still not reclaimed.
    at_one_ttl = t_pub + ttl + 0.01
    assert store.gc_sweep(now=at_one_ttl, observed_at=at_one_ttl) == []
    assert entry_path.exists()
    # Sweep 3, two TTLs after publication: the grace has elapsed.
    assert store.gc_sweep(now=t_pub + 2 * ttl + 0.02) == [entry_path.stem]


def test_no_surface_claims_an_unconditional_retention_bound(tmp_path: Path) -> None:
    """AC #7's NEGATIVE half, which is the load-bearing one: an implementation
    that ships a correct reclaim rule and an OVERCLAIMING docstring violates
    spec term 7. Retention under this form is CONDITIONAL — on the observation
    record being present and readable, and on a sweep-trigger interval that is
    unbounded in the one-shot process shape — so no `N × TTL` bound may be
    asserted anywhere on the surface: not in the module, not in an emission,
    not in a docstring, not in the operator-facing CLI row.

    Mutation probe: adding a sentence such as *"retention is bounded by 2 × TTL"*
    to any of the scanned surfaces fires one of the patterns below."""
    import re

    from harness_runtime.admin import inspect as inspect_module
    from harness_runtime.lifecycle import protected_result_store as store_module

    overclaims = [
        re.compile(r"bound(?:ed)?\s+by\s+\d+\s*[×x*]\s*(?:ttl|TTL)", re.IGNORECASE),
        re.compile(r"(?:unconditional|guaranteed|hard)\s+(?:retention\s+)?bound", re.IGNORECASE),
        re.compile(r"never\s+retained\s+(?:for\s+)?(?:more|longer)\s+than", re.IGNORECASE),
        re.compile(r"retention\s+is\s+bounded\s+by", re.IGNORECASE),
    ]
    scanned: list[tuple[str, str]] = []
    for module in (store_module, inspect_module):
        source_path = Path(str(module.__file__))
        scanned.append((source_path.name, source_path.read_text(encoding="utf-8")))

    # Plus the operator-facing rendering itself, over a live store.
    store, _entry = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    snapshot = read_protected_result_store_snapshot(tmp_path / "store")
    assert snapshot is not None
    from harness_runtime.admin.inspect import _format_protected_result_store_human

    scanned.append(("harness-inspect output", _format_protected_result_store_human(snapshot)))

    for label, text in scanned:
        for pattern in overclaims:
            match = pattern.search(text)
            assert match is None, (
                f"{label} asserts an unconditional retention bound: {match.group(0)!r}"
            )


def test_oldest_candidate_age_is_a_field_of_every_sweep_emission_never_cached(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #8(a) — the oldest resident candidate's age is a FIELD OF every
    sweep's report-log emission (the reclaim line and the AC #6 / AC #11
    lines), NEVER a separate line, and computed AT READ TIME from the timestamp
    pass the sweep already performs rather than cached between sweeps.

    The not-cached half is witnessed by VALUE: two sweeps a known interval
    apart must report ages that differ by that interval, which a cached value
    cannot do.

    Mutation probe: caching the gauge on the instance (computing it once and
    reusing it) makes the second sweep report the first sweep's age and the
    delta assertion fails; moving the age onto its own log line leaves the
    reclaim line without the field and the membership assertion fails."""
    import logging

    ttl = 10.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=20.0)
    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    # Derived from the recorded mtime rather than the wall clock, so the
    # reported ages below are EXACT on every run whatever the load.
    mtime = entry_path.stat().st_mtime
    at = mtime + 20.0

    store.gc_sweep(now=at, observed_at=at)
    reset_line = next(r for r in caplog.records if "no GC observation record" in r.message)
    assert "oldest_entry_age_s=20.0" in reset_line.message

    caplog.clear()
    # A sweep five seconds later, with the record removed so the same emission
    # fires again: the SAME entry, a five-second-older reported age.
    _observation_record_path(store).unlink()
    store.gc_sweep(now=at + 5.0, observed_at=at + 5.0)
    later_line = next(r for r in caplog.records if "no GC observation record" in r.message)
    assert "oldest_entry_age_s=25.0" in later_line.message, (
        f"the oldest-candidate age did not advance with the sweep clock — it is "
        f"cached rather than computed at read time: {later_line.message}"
    )

    caplog.clear()
    _backdate_observation_record(store)
    reclaimed = store.gc_sweep(now=at + 6.0)
    assert reclaimed == [entry_path.stem]
    reclaim_line = next(r for r in caplog.records if "TTL-expired entry GC'd" in r.message)
    assert "oldest_entry_age_s=26.0" in reclaim_line.message, (
        "the reclaim emission does not carry the oldest-candidate age as a FIELD"
    )


def test_reclaim_emission_carries_the_which_term_fired_last_discriminator(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #8's WHICH-RECLAIM-TERM-FIRED-LAST discriminator — the later of the
    two conjunct deadlines, DERIVED AT THE RECLAIM SITE and never stored, as an
    ATTRIBUTE of the reclaim emission rather than a line of its own. Both
    values of the discriminator are exercised.

    Mutation probe: storing the discriminator in the observation record (a third
    member) breaks AC #5's closed-set witness; hard-coding one value fails
    whichever half it does not produce."""
    import logging

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")

    # (a) The FIRST-OBSERVATION deadline is the later one: the timestamp is
    # ancient, so the observation is what gates.
    store, entry = _stale_entry(tmp_path / "obs", ttl_seconds=1.0, age_seconds=100.0)
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    caplog.clear()
    assert store.gc_sweep(now=at + 1.5) == [entry.stem]
    line = next(r for r in caplog.records if "TTL-expired entry GC'd" in r.message)
    assert "reclaim_term=first-observation" in line.message

    # (b) The FILESYSTEM-AGE deadline is the later one: the entry is observed
    # long before its own timestamp (the reused-name shape), so the timestamp
    # is what gates.
    store_2 = _store(tmp_path / "fs", ttl_seconds=1.0)
    store_root = tmp_path / "fs" / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    orphan = store_root / ".tmp-which-term-fs-age"
    orphan.write_bytes(b"partial ciphertext")
    stale = time.time() - 10.0
    os.utime(orphan, (stale, stale))
    at_2 = time.time()
    store_2.gc_sweep(now=at_2, observed_at=at_2)
    _backdate_observation_record(store_2, by=100.0)
    later = at_2 + 1.0
    os.utime(orphan, (later, later))
    caplog.clear()
    store_2.gc_sweep(now=later + 1.5)
    line_2 = next(r for r in caplog.records if "crash-orphaned temp-file GC'd" in r.message)
    assert "reclaim_term=filesystem-age" in line_2.message


def test_snapshot_surface_is_read_only_sweep_free_and_reports_the_record_three_ways(
    tmp_path: Path,
) -> None:
    """AC #8(b) — the read-only, sweep-free store read. It engages only when
    the root exists, computes the same timestamp-derived oldest-candidate age at
    read time, reports the observation record's own state THREE-WAY, adds ZERO
    persistence, and WRITES NOTHING / CREATES NOTHING.

    Mutation probes: making the surface create the store root fails the
    read-only invariant assertion (the directory listing would change and the
    absent-root case would stop returning `None`); collapsing the three-way
    record state to present/absent fails the unreadable branch."""
    root = tmp_path / "store"

    # Absent root: no engagement, and nothing is created.
    assert read_protected_result_store_snapshot(root) is None
    assert not root.exists(), "the read-only surface CREATED the store root"

    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    orphan = root / ".tmp-snapshot-orphan"
    orphan.write_bytes(b"partial ciphertext")
    orphan_stale = time.time() - 30.0
    os.utime(orphan, (orphan_stale, orphan_stale))

    # (1) record ABSENT.
    before = sorted(p.name for p in root.iterdir())
    snapshot = read_protected_result_store_snapshot(root, now=time.time())
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.ABSENT
    assert snapshot.entry_count == 1 and snapshot.orphan_count == 1
    assert snapshot.gauge.oldest_entry_age_seconds is not None
    assert 9.0 < snapshot.gauge.oldest_entry_age_seconds < 12.0
    assert snapshot.gauge.oldest_orphan_age_seconds is not None
    assert 29.0 < snapshot.gauge.oldest_orphan_age_seconds < 32.0
    # Sweep-free and read-only: the directory is byte-for-byte the same set,
    # and no record was published.
    assert sorted(p.name for p in root.iterdir()) == before
    assert entry_path.exists() and orphan.exists()

    # (2) record PRESENT AND READABLE, after a real sweep publishes one.
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_READABLE

    # (3) record PRESENT BUT UNREADABLE.
    _observation_record_path(store).write_text('{"version": 1, "observations": {"a": 1.0')
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_UNREADABLE


def test_the_gauge_covers_an_orphan_only_store_with_no_observation_record(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #8's GAUGE TOTALITY, asserted rather than assumed. With a store
    holding ONLY past-TTL temporary-file crash orphans and no observation
    record — a state AC #6 makes reachable and requires an emission for — BOTH
    the sweep emission (a) and the read-only surface (b) must still report a
    conforming oldest-candidate age. A gauge permitted to exclude the orphan
    class would leave that case with no conforming value at all.

    Mutation probe: excluding the crash-orphan class from either gauge leaves
    both reported ages `none-resident` here and this test fails."""
    import logging

    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    orphan = root / ".tmp-orphan-only-store"
    orphan.write_bytes(b"partial ciphertext")
    stale = time.time() - 42.0
    os.utime(orphan, (stale, stale))

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    line = next(r for r in caplog.records if "no GC observation record" in r.message)
    assert "past_ttl_orphans=1" in line.message
    assert "oldest_orphan_age_s=42.0" in line.message

    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.orphan_count == 1
    assert snapshot.gauge.oldest_orphan_age_seconds is not None
    assert snapshot.gauge.oldest_orphan_age_seconds > 41.0


def test_record_is_replaced_not_accumulated_over_the_union_of_both_classes(
    tmp_path: Path,
) -> None:
    """AC #9's first half — the record is REPLACED WHOLESALE at each sweep over
    the union of both candidate classes; names no longer resident are DROPPED,
    so a long-lived store's record does not grow without bound as entries come
    and go. Includes the completed-publication case: a temporary name drops out
    of the union exactly as a reclaimed entry's name does.

    Mutation probe: accumulating (merging the new observations into the old map
    rather than replacing it) leaves the removed names in the record and the
    final size assertion fails."""
    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    stale = time.time() - 10.0

    names_seen: set[str] = set()
    at = time.time()
    for generation in range(4):
        orphan = root / f".tmp-generation-{generation}"
        orphan.write_bytes(b"partial ciphertext")
        os.utime(orphan, (stale, stale))
        names_seen.add(orphan.name)
        store.gc_sweep(now=at, observed_at=at)
        assert set(_read_observation_record(store)) == {orphan.name}, (
            "the record accumulated names from earlier sweeps instead of being replaced wholesale"
        )
        orphan.unlink()

    assert len(names_seen) == 4
    store.gc_sweep(now=at)
    assert _read_observation_record(store) == {}


def test_a_retained_candidate_keeps_its_original_first_observed_at(tmp_path: Path) -> None:
    """AC #9's SECOND half — the one a literal reading of *replace wholesale*
    would break. A candidate that SURVIVES a sweep retains its ORIGINAL
    `first_observed_at`: the replacement rewrites the RECORD, never the
    timestamps of names already in it.

    Driven across FOUR sweeps at intervals SHORTER than the TTL, then asserted
    reclaimed on schedule from its FIRST observation.

    Mutation probe: re-sampling `first_observed_at` for a retained name slides
    each deadline forward by the inter-sweep interval, so under this sub-TTL
    cadence the entry is NEVER reclaimed at all — precisely the unbounded
    retention this unit exists to prevent — and the final assertion fails."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    at = time.time()

    store.gc_sweep(now=at, observed_at=at)
    original = _read_observation_record(store)[entry_path.name]
    assert original == at

    for offset in (0.2, 0.4, 0.6, 0.8):
        assert store.gc_sweep(now=at + offset, observed_at=at + offset) == []
        assert _read_observation_record(store)[entry_path.name] == original, (
            "a retained candidate's first_observed_at was re-sampled — under a "
            "sub-TTL sweep cadence nothing would ever become reclaimable"
        )

    # On schedule from the FIRST observation, not from the latest sweep.
    assert store.gc_sweep(now=at + ttl + 0.05, observed_at=at + ttl + 0.05) == [entry_path.stem]


def test_unreadable_record_reads_as_no_observation_for_every_name(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #11 — a record that EXISTS but is truncated, corrupted or written in
    an incompatible form reads as NO OBSERVATION FOR EVERY NAME, never partial
    trust of the rows that happen to parse. The record written below has rows
    that are individually well-formed (`"<name>": <float>` pairs a permissive
    reader would happily take) while the WHOLE is invalid, and NO name is
    treated as observed.

    The emission is asserted and so is its DISCRIMINATION as *record present but
    unreadable*, both of which are MANDATORY. The additional FAULT
    CLASSIFICATION is PERMITTED rather than required by spec term 11, so it is
    deliberately NOT asserted here.

    Mutation probe: trusting the parseable subset lets a row carrying an
    earlier-than-truth `first_observed_at` shorten retention — the direction
    AC #4 forbids — and the entry is reclaimed at the sweep below."""
    import logging

    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)

    # Individually well-formed rows; the document as a whole is truncated.
    long_ago = at - 1_000_000.0
    _observation_record_path(store).write_text(
        f'{{"version": 1, "observations": {{"{entry_path.name}": {long_ago}, "other.entry": 1.0'
    )

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    assert store.gc_sweep(now=at + 5.0, observed_at=at + 5.0) == [], (
        "a name from an INVALID record was treated as observed — the parseable "
        "subset was trusted, and a row older than the truth shortened retention"
    )
    assert entry_path.exists()

    lines = [r for r in caplog.records if "PRESENT BUT UNREADABLE" in r.message]
    assert len(lines) == 1, "the unreadable-record emission is missing or duplicated"
    assert "past_ttl_entries=1" in lines[0].message
    assert "oldest_entry_age_s=" in lines[0].message

    # Totality is fail-SAFE, not fail-open: a fresh grace runs and then reclaim
    # proceeds normally.
    assert store.gc_sweep(now=at + 6.5) == [entry_path.stem]


def test_one_malformed_row_invalidates_the_whole_record_not_just_that_row(
    tmp_path: Path,
) -> None:
    """AC #11's TOTALITY at ROW granularity — the case a document-level parse
    failure alone cannot reach. The record below is VALID JSON with a valid
    envelope; only ONE of its two rows carries a non-numeric
    `first_observed_at`. The OTHER row is perfectly well-formed and names a
    genuinely resident candidate, so an implementation that skipped the bad row
    and trusted the good one would treat that name as observed.

    Fail-safe is a TOTALITY: NO name is observed, because a corrupted row that
    happens to parse can carry a `first_observed_at` EARLIER than the truth and
    thereby SHORTEN retention — the one direction AC #4 forbids.

    Mutation probe: skipping the malformed row (`continue`) instead of
    invalidating the whole record makes the good row's back-dated stamp
    reachable and the entry is reclaimed at the sweep below."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    at = time.time()

    # The good row is back-dated far enough that trusting it WOULD reclaim.
    _observation_record_path(store).write_text(
        json.dumps(
            {
                "version": 1,
                "observations": {
                    entry_path.name: at - 1_000_000.0,
                    "sibling.entry": "not-a-number",
                },
            }
        )
    )

    assert store.gc_sweep(now=at, observed_at=at) == [], (
        "a well-formed row from a record with ONE malformed row was trusted — "
        "partial trust shortened retention"
    )
    assert entry_path.exists()
    # And the fresh grace it granted is a real one.
    assert store.gc_sweep(now=at + ttl + 0.1) == [entry_path.stem]


def test_an_out_of_domain_first_observed_at_invalidates_the_record(tmp_path: Path) -> None:
    """AC #11's totality against the NUMERIC-BUT-UNUSABLE stamp, which a type
    check alone admits. Four shapes, all reachable from a restored, hand-edited
    or foreign-build record:

    - `-Infinity` — Python's `json` accepts the non-standard literal; it is
      numeric, so it parses, and `current_time - (-inf)` is `+inf`, which passes
      the elapsed conjunct INSTANTLY and DELETES a protected result rather than
      granting it a fresh grace: the earlier-than-truth, retention-SHORTENING
      direction AC #4 forbids.
    - `Infinity` — the same literal family, in the lengthening direction.
    - `NaN` — fails the elapsed comparison in the SAFE direction on its own, but
      is rejected too, because the fail-safe is a TOTALITY over anything that is
      not *read, parsed whole, entries usable*, not a set of individually
      patched hazards.
    - a finite NEGATIVE stamp — the quiet one. `first_observed_at` is a
      wall-clock reading taken AFTER the candidate was observed to exist (AC
      #3), so a pre-epoch value cannot be one; treating it as an ancient
      observation reclaims on the first sweep.
    - a JSON integer too large for a float — `math.isfinite` RAISES on it rather
      than answering, so an unguarded domain test lets an unreadable record
      escape the totality as an uncaught `OverflowError` out of `gc_sweep`.

    This is a DOMAIN check and the witness claims no more: it pins that values
    which cannot be a wall-clock observation at all are refused. It asserts
    nothing about detecting an arbitrarily corrupted but IN-domain stamp, which
    the ratified two-member content set carries no way to detect.

    *(Out-of-family review rounds 1 [P1] and 2 [P1].)*

    Mutation probes: dropping the `math.isfinite`/`value < 0.0` guard makes the
    `-Infinity` and negative cases reclaim the live entry on the FIRST sweep;
    dropping the `OverflowError` guard turns the huge-integer case into an
    uncaught exception rather than a refusal."""
    ttl = 1.0
    huge_integer = "1" + "0" * 400
    for index, literal in enumerate(("-Infinity", "Infinity", "NaN", "-1", huge_integer)):
        store, entry_path = _stale_entry(
            tmp_path / f"case-{index}", ttl_seconds=ttl, age_seconds=10.0
        )
        _observation_record_path(store).write_text(
            f'{{"version": 1, "observations": {{"{entry_path.name}": {literal}}}}}'
        )
        at = time.time()
        assert store.gc_sweep(now=at, observed_at=at) == [], (
            f"a record carrying {literal[:24]} as a first_observed_at was "
            f"trusted — a numeric-but-unusable stamp reached the reclaim decision"
        )
        assert entry_path.exists()
        # Fail-SAFE, not fail-open: the fresh grace it granted is a real one.
        assert store.gc_sweep(now=at + ttl + 0.1) == [entry_path.stem]


def test_a_bool_version_field_invalidates_the_record(tmp_path: Path) -> None:
    """AC #11's totality against the `bool`-is-`int` trap at the ENVELOPE, which
    the row loop already guards one level down. `True == 1` in Python, so a
    record carrying `"version": true` — reachable from a foreign build or a
    hand-edit — passed a bare `!= _GC_OBSERVATION_RECORD_VERSION` and read as
    PRESENT_READABLE, admitting its rows. A `0.0` stamp among them is finite and
    non-negative, so the domain check trusts it, and `current_time - 0.0` clears
    the elapsed conjunct instantly: the invalid record RECLAIMS on the FIRST
    sweep — the retention-SHORTENING direction AC #4 forbids.

    *(Out-of-family review round 4 [P1], reproduced independently before the
    fix.)*

    Mutation probe: dropping the `isinstance(version, bool)` guard makes the
    record read PRESENT_READABLE and the live entry is reclaimed on the first
    sweep, failing both assertions below."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    _observation_record_path(store).write_text(
        json.dumps({"version": True, "observations": {entry_path.name: 0.0}})
    )

    # The READ-ONLY surface first — a sweep republishes the record, so checking
    # it afterwards would read the sweep's own valid replacement.
    snapshot = read_protected_result_store_snapshot(tmp_path / "store")
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_UNREADABLE

    at = time.time()
    assert store.gc_sweep(now=at, observed_at=at) == [], (
        "a record whose `version` was the bool `true` was trusted — `True == 1` "
        "let an invalid envelope admit its rows and reclaim on sight"
    )
    assert entry_path.exists()


def test_the_snapshot_gauge_mirrors_the_sweep_globs_including_dot_leading_names(
    tmp_path: Path,
) -> None:
    """AC #8(b)'s gauge must never UNDER-REPORT relative to what the SWEEP
    enumerates. `pathlib`'s `glob` does NOT hide dotfiles the way shell globbing
    does — `*.entry` matches `.hidden.entry` — so a membership test that
    excluded dot-leading names from the entry class counted FEWER candidates
    than the sweep sees, on the one surface whose purpose is to make the
    retention level falsifiable.

    Membership is also NOT exclusive: `.tmp-x.entry` is matched by BOTH globs
    and enumerated in both classes by the sweep, so the gauge counts it in both.

    Both properties are asserted against the sweep's OWN globs rather than
    against a restated expectation, so the two can never silently diverge again.

    *(Out-of-family review round 4 [P2], reproduced independently before the
    fix.)*

    Mutation probe: restoring the `not name.startswith(".")` condition drops
    the dot-leading entry and the count-parity assertion fails; making the
    membership exclusive drops the dual-match name from one class."""
    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    stale = time.time() - 100.0
    for name in ("plain.entry", ".hidden.entry", ".tmp-orphan", ".tmp-dual.entry"):
        (root / name).write_bytes(b"x")
        os.utime(root / name, (stale, stale))

    # The sweep's own globs are the reference — not a restated expectation.
    swept_entries = {p.name for p in root.glob("*.entry")}
    swept_orphans = {p.name for p in root.glob(".tmp-*")}
    assert ".hidden.entry" in swept_entries, "premise changed: pathlib glob now hides dotfiles"
    assert ".tmp-dual.entry" in swept_entries and ".tmp-dual.entry" in swept_orphans

    snapshot = read_protected_result_store_snapshot(root, now=time.time())
    assert snapshot is not None
    assert snapshot.entry_count == len(swept_entries), (
        f"the gauge counted {snapshot.entry_count} entries where the sweep "
        f"enumerates {len(swept_entries)} ({sorted(swept_entries)}) — it UNDER-REPORTS"
    )
    assert snapshot.orphan_count == len(swept_orphans), (
        f"the gauge counted {snapshot.orphan_count} orphans where the sweep "
        f"enumerates {len(swept_orphans)} ({sorted(swept_orphans)})"
    )
    assert store._ttl_seconds == 1.0  # type: ignore[attr-defined]


def test_an_unusable_store_root_is_a_path_error_not_an_absent_store(tmp_path: Path) -> None:
    """AC #8(b)'s engagement predicate discriminates ABSENT from UNUSABLE. A
    configured root that EXISTS but is a regular file, or whose contents cannot
    be read, is NOT the *no store here* case: collapsing the two would report
    nothing at all, successfully, for a store the operator cannot inspect — on
    the one surface whose purpose is to make the retention level falsifiable.

    *(Out-of-family review round 1 [P2].)*

    Mutation probe: reverting the predicate to a bare `root.is_dir()` returns
    `None` for the regular-file case (silently suppressing the row) and lets the
    unreadable-directory case raise an UNCAUGHT `PermissionError` out of the
    read instead of a typed path error — both assertions below fail."""
    # Genuinely absent → None, and nothing is created.
    absent = tmp_path / "never-existed"
    assert read_protected_result_store_snapshot(absent) is None
    assert not absent.exists()

    # Exists but is a regular file → a path error, not `None`.
    not_a_dir = tmp_path / "a-file-not-a-store"
    not_a_dir.write_text("this is not a store root")
    with pytest.raises(NotADirectoryError):
        read_protected_result_store_snapshot(not_a_dir)

    # Exists, is a directory, but is unreadable → a path error, not `None`.
    unreadable = tmp_path / "unreadable-store"
    unreadable.mkdir()
    (unreadable / GC_OBSERVATION_RECORD_FILENAME).write_text('{"version": 1, "observations": {}}')
    unreadable.chmod(0o000)
    try:
        if os.access(unreadable, os.R_OK):  # pragma: no cover — root/CI-as-root
            pytest.skip("running as a user that bypasses directory permissions")
        with pytest.raises(OSError):
            read_protected_result_store_snapshot(unreadable)
    finally:
        unreadable.chmod(0o700)


def test_deeply_nested_json_reads_as_unreadable_rather_than_raising(tmp_path: Path) -> None:
    """AC #11's totality against an exception ESCAPING it. `json.loads` raises
    `RecursionError` — not a `ValueError` — on sufficiently deeply nested input,
    and left uncaught it aborts `gc_sweep` and crashes the inspection surface
    instead of reporting *present but unreadable*. Every invalid record must
    READ as no observation; none may raise.

    *(Out-of-family review round 3 [P2]; the same species as round 2's
    `OverflowError` half.)*

    Mutation probe: dropping `RecursionError` from the parse guard turns both
    calls below into an uncaught exception rather than a refusal."""
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    depth = sys.getrecursionlimit() * 20
    corrupt = "[" * depth + "]" * depth
    # Verified in-test rather than assumed: this input really does raise
    # `RecursionError` from the parser, so the witness is not vacuous.
    with pytest.raises(RecursionError):
        json.loads(corrupt)

    # The READ-ONLY surface first — a sweep republishes the record, so checking
    # it afterwards would read the sweep's own valid replacement.
    _observation_record_path(store).write_text(corrupt)
    snapshot = read_protected_result_store_snapshot(tmp_path / "store")
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_UNREADABLE

    at = time.time()
    assert store.gc_sweep(now=at, observed_at=at) == []
    assert entry_path.exists()


def test_an_unreadable_store_directory_scan_is_never_a_zero_reading(tmp_path: Path) -> None:
    """AC #8(b)'s under-report guard, at the ENUMERATION rather than the
    per-candidate stat. On a directory that is SEARCHABLE but not READABLE
    (mode `0100`), `Path.glob` suppresses the `EACCES` and simply yields
    nothing — so both classes would come back EMPTY while the record path still
    resolves, and the surface would report zero counts for a store full of
    resident entries. `os.scandir` raises instead.

    *(Out-of-family review round 3 [P2]; completes round 2's [P2], which
    guarded the root and record stats but not the scan between them.)*

    Mutation probe: reverting the enumeration to `root.glob(...)` makes the
    snapshot return a successful ZERO reading instead of raising."""
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    root = tmp_path / "store"
    assert entry_path.exists()

    root.chmod(0o100)  # --x------ : searchable, NOT readable
    try:
        if os.access(root, os.R_OK):  # pragma: no cover — root/CI-as-root
            pytest.skip("running as a user that bypasses directory permissions")
        with pytest.raises(OSError):
            read_protected_result_store_snapshot(root)
    finally:
        root.chmod(0o700)

    # And the ordinary path still reads the resident entry.
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.entry_count == 1


def test_an_unreadable_candidate_is_never_silently_dropped_from_the_gauge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #8(b)'s gauge must never UNDER-REPORT. If a resident candidate's
    `stat()` fails with a real error (`EIO`, `EACCES`), skipping it drops it
    from BOTH the count and the oldest-age reading and lets the binary exit 0 on
    a falsely LOW value — on the one surface whose whole purpose is to make the
    retention level falsifiable, an under-report is the single worst direction
    to fail in. Only a BENIGN concurrent disappearance is skipped.

    The SWEEP's own skip-and-continue is deliberately untouched and is asserted
    here to still hold: it is shipped behaviour, and a sweep that skips an
    unreadable candidate merely RETAINS it — the safe direction.

    *(Out-of-family review round 2 [P2].)*

    Mutation probe: widening the inspector's guard back to `except OSError`
    makes the snapshot report `entry_count == 0` with a `None` age instead of
    raising, and this test fails."""
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    root = tmp_path / "store"
    real_stat = Path.stat

    def _failing_stat(self: Path, **kwargs: object) -> object:
        if self == entry_path:
            raise PermissionError(errno.EACCES, "simulated unreadable candidate")
        return real_stat(self, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "stat", _failing_stat)
    with pytest.raises(PermissionError):
        read_protected_result_store_snapshot(root)

    # A benign concurrent disappearance IS skipped — that is not an error.
    def _vanished_stat(self: Path, **kwargs: object) -> object:
        if self == entry_path:
            raise FileNotFoundError(errno.ENOENT, "vanished mid-scan")
        return real_stat(self, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "stat", _vanished_stat)
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.entry_count == 0
    assert snapshot.gauge.oldest_entry_age_seconds is None

    # The SWEEP still skips-and-continues, unchanged: it retains the entry.
    monkeypatch.setattr(Path, "stat", _failing_stat)
    assert store.gc_sweep(now=time.time()) == []
    monkeypatch.undo()
    assert entry_path.exists()


def test_emissions_ride_the_report_log_with_no_span_no_metric_no_composite_key(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """AC #12 — the emission surface. Every emission this unit adds rides the
    TYPED REPORT-LOG LINE the store already uses: NO span is emitted, NO metric
    instrument is created, and NO new observability namespace appears. The
    composite key MUST NOT appear in any emission; the AC #6 / AC #11 lines
    decrypt nothing and therefore carry no tenant identity. A candidate filename
    may appear in a BODY but is never a dimension or label of an aggregate
    (logging records carry no label dimension at all). The implementation does
    not rely on the `PersonaTier` span-processor gradient reaching this carrier
    — it does not.

    Mutation probes: emitting the composite key on any of these lines fails the
    content assertions; decrypting an entry to tag the reset line pulls the
    tenant tag in and fails the reset-line assertion; adding a span or a metric
    instrument pulls an `opentelemetry` import into the module and fails the
    carrier assertions."""
    import logging

    from harness_runtime.lifecycle import protected_result_store as store_module

    source = Path(str(store_module.__file__)).read_text(encoding="utf-8")
    for forbidden_token in (
        "opentelemetry",
        "start_as_current_span",
        "get_tracer",
        "get_meter",
        "create_counter",
        "create_histogram",
        "PersonaTier",
    ):
        assert forbidden_token not in source, (
            f"the store module references {forbidden_token!r} — this unit's "
            f"emissions ride the typed report-log line and nothing else"
        )
    assert store_module.logger.name == "harness.runtime.protected_result_store"

    store = _store(tmp_path, ttl_seconds=1.0)
    ref = store.write_once("tenant-a", "a paid effect's payload")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    stale = time.time() - 10.0
    os.utime(entry_path, (stale, stale))

    caplog.set_level(logging.WARNING, logger="harness.runtime.protected_result_store")
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    reset_line = next(r for r in caplog.records if "no GC observation record" in r.message)
    assert "tenant" not in reset_line.message.lower(), (
        "the reset line carries a tenant identity — it must derive from the "
        "timestamp pass and the record read ALONE, decrypting nothing"
    )

    _backdate_observation_record(store)
    caplog.clear()
    assert store.gc_sweep(now=at) == [entry_path.stem]

    for record in caplog.records:
        assert record.name == "harness.runtime.protected_result_store"
        assert ref not in record.message, "the composite key leaked into an emission"
        assert ref.split(":", 1)[1] not in record.message, (
            "part of the composite key leaked into an emission"
        )


_B96_ONE_SHOT_SWEEP_SCRIPT = """
import json
import sys
from pathlib import Path
from cryptography.fernet import Fernet
from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore

store_dir, key, ttl, now, observed_at, result_marker = sys.argv[1:7]
store = ProtectedResultStore(Path(store_dir), codec=Fernet(key.encode()), ttl_seconds=float(ttl))
reclaimed = store.gc_sweep(now=float(now), observed_at=float(observed_at))
Path(result_marker).write_text(json.dumps(reclaimed))
"""


def test_one_shot_process_invocations_accumulate_the_grace_across_process_exit(
    tmp_path: Path,
) -> None:
    """AC #10 + AC #14(i) — the criterion that DISCRIMINATES the ratified form
    from the retired Reading B, and the one an in-process test structurally
    cannot see.

    Across N SUCCESSIVE ONE-SHOT PROCESS INVOCATIONS against the same store
    root — genuine `subprocess` runs, each a fresh interpreter with no shared
    Python state — a genuinely expired entry IS eventually reclaimed, because
    the grace clock ACCUMULATES ACROSS PROCESS EXITS. Per-process elapsed time
    is FORBIDDEN (spec term 10): in this exact shape it never accumulates, so
    the entry would never be reclaimed and retention would be unbounded.

    The durable record's own cross-process survival is asserted DIRECTLY
    between invocations (AC #14(i)), not merely inferred from the outcome.

    Mutation probe: holding the observation state in process-local memory only
    (the retired `_root_observed_expired` module dict) makes invocation 3 record
    a FRESH observation instead of inheriting invocation 1's — the entry is
    never reclaimed and the final assertion fails."""
    ttl = 1.0
    key = Fernet.generate_key()
    store_dir = tmp_path / "store"
    store_dir.mkdir(parents=True)
    store = ProtectedResultStore(store_dir, codec=Fernet(key), ttl_seconds=ttl)
    ref = store.write_once("tenant-a", "survives across process exits")
    assert isinstance(ref, str)
    entry_path = store._entry_path(ref)  # type: ignore[attr-defined]
    stale = time.time() - 10.0
    os.utime(entry_path, (stale, stale))
    record_path = store_dir / GC_OBSERVATION_RECORD_FILENAME
    record_path.unlink(missing_ok=True)  # start from a genuine first cutover

    t0 = time.time()

    def _invoke(now: float, observed_at: float, marker: Path) -> list[str]:
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                _B96_ONE_SHOT_SWEEP_SCRIPT,
                str(store_dir),
                key.decode("ascii"),
                str(ttl),
                str(now),
                str(observed_at),
                str(marker),
            ],
            capture_output=True,
            timeout=120.0,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")
        reclaimed: list[str] = json.loads(marker.read_text())
        return reclaimed

    # Invocation 1 — first observation; nothing reclaimed.
    assert _invoke(t0, t0, tmp_path / "r1") == []
    assert entry_path.exists()
    # AC #14(i): the observation SURVIVED that process's exit.
    assert record_path.exists()
    surviving = json.loads(record_path.read_text())["observations"]
    assert surviving == {entry_path.name: t0}

    # Invocation 2 — a second one-shot run well inside the grace.
    assert _invoke(t0 + 0.2, t0 + 0.2, tmp_path / "r2") == []
    assert entry_path.exists()
    assert json.loads(record_path.read_text())["observations"] == {entry_path.name: t0}, (
        "the second process re-sampled the observation instead of inheriting "
        "the first process's — the grace is not accumulating across exits"
    )

    # Invocation 3 — past the grace: the entry IS reclaimed.
    assert _invoke(t0 + ttl + 0.2, t0 + ttl + 0.2, tmp_path / "r3") == [entry_path.stem]
    assert not entry_path.exists()


def test_record_publication_is_crash_atomic_and_never_no_replace_or_unlink_recreate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #14(iii) — crash-atomicity of the RECORD's own publication.
    Interrupting the record write AFTER the temp write and BEFORE the atomic
    replace leaves the PREVIOUS record intact and readable, never an absent or
    half-written one. And the publication path is temp-write + `fsync` + ATOMIC
    REPLACE + directory `fsync`: NEVER the write-once no-replace primitive
    (`os.link`, which would freeze the record at its first snapshot) and NEVER
    unlink-then-recreate (which opens a window in which the record reads ABSENT
    and every grace restarts).

    Mutation probes: publishing with the no-replace primitive freezes the record
    at its first snapshot, so the second sweep's new name never appears and the
    replaced-content assertion fails; unlink-then-recreate removes the record
    before writing, so the interrupted publication below leaves it ABSENT and
    the previous-record assertion fails."""
    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    stale = time.time() - 10.0
    first = root / ".tmp-crash-atomic-one"
    first.write_bytes(b"partial ciphertext")
    os.utime(first, (stale, stale))

    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    record_path = _observation_record_path(store)
    original_bytes = record_path.read_bytes()
    assert json.loads(original_bytes)["observations"] == {first.name: at}

    # The publication path uses os.replace, and neither os.link nor an unlink
    # of the record itself.
    second = root / ".tmp-crash-atomic-two"
    second.write_bytes(b"partial ciphertext")
    os.utime(second, (stale, stale))
    replaces: list[str] = []
    links: list[str] = []
    unlinks: list[str] = []
    real_replace, real_link, real_unlink = os.replace, os.link, os.unlink

    def _spy_replace(src: object, dst: object, **kwargs: object) -> None:
        replaces.append(str(dst))
        real_replace(src, dst, **kwargs)  # type: ignore[arg-type]

    def _spy_link(src: object, dst: object, **kwargs: object) -> None:
        links.append(str(dst))
        real_link(src, dst, **kwargs)  # type: ignore[arg-type]

    def _spy_unlink(path: object, **kwargs: object) -> None:
        unlinks.append(str(path))
        real_unlink(path, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "replace", _spy_replace)
    monkeypatch.setattr(os, "link", _spy_link)
    monkeypatch.setattr(os, "unlink", _spy_unlink)
    store.gc_sweep(now=at + 0.1, observed_at=at + 0.1)
    monkeypatch.undo()

    assert str(record_path) in replaces, "the record was not published via os.replace"
    assert str(record_path) not in links, (
        "the record was published with the write-once NO-REPLACE primitive — it "
        "would freeze at its first snapshot"
    )
    assert str(record_path) not in unlinks, (
        "the record was unlinked before being recreated — that opens a window "
        "in which it reads ABSENT and every grace restarts"
    )
    # Replacement really happened: the new name is in the record.
    assert set(_read_observation_record(store)) == {first.name, second.name}
    intact_bytes = record_path.read_bytes()

    # Now interrupt a publication between the temp write and the replace.
    def _failing_replace(src: object, dst: object, **kwargs: object) -> None:
        raise OSError(errno.EIO, "simulated crash before the atomic replace")

    monkeypatch.setattr(os, "replace", _failing_replace)
    store.gc_sweep(now=at + 0.2, observed_at=at + 0.2)
    monkeypatch.undo()

    assert record_path.exists(), "an interrupted record publication left NO record"
    assert record_path.read_bytes() == intact_bytes, (
        "an interrupted record publication left a half-written record instead "
        "of the PREVIOUS one intact"
    )
    assert read_protected_result_store_snapshot(root) is not None
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_READABLE


def test_record_carrier_is_glob_disjoint_and_not_dot_leading(tmp_path: Path) -> None:
    """AC #15 — the record is a dedicated file in the store root whose name is
    DISJOINT FROM BOTH SWEEP GLOBS, so the sweep can never enumerate its own
    record as a candidate, AND is NOT DOT-LEADING, which closes the
    dotfile-skipping copy channel that is one of the two ways the record is lost
    while the entries it indexes survive.

    BOTH properties are asserted DIRECTLY AND SEPARATELY: glob-disjointness does
    not imply non-dot-leading (a name such as `.gc-observations` satisfies the
    first and defeats the second), so a single glob probe cannot discharge this
    AC.

    Mutation probes: naming the record so a sweep glob matches it (e.g.
    `gc-observations.entry`) fails the enumeration assertions; naming it with a
    leading dot fails the dot-leading assertion."""
    assert not GC_OBSERVATION_RECORD_FILENAME.startswith("."), (
        f"the observation record name {GC_OBSERVATION_RECORD_FILENAME!r} is "
        f"DOT-LEADING — a dotfile-skipping copy would silently drop it while "
        f"preserving every entry it indexes"
    )

    store, entry_path = _stale_entry(tmp_path, ttl_seconds=1.0, age_seconds=10.0)
    root = tmp_path / "store"
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    record_path = _observation_record_path(store)
    assert record_path.exists()

    enumerated = {p.name for p in root.glob("*.entry")} | {p.name for p in root.glob(".tmp-*")}
    assert GC_OBSERVATION_RECORD_FILENAME not in enumerated, (
        "the record's own name is matched by a sweep glob — the sweep would "
        "enumerate, age, report and unlink its own record"
    )
    assert enumerated == {entry_path.name}

    # And it is never reported or reclaimed as a candidate, however long it sits.
    _backdate_observation_record(store)
    assert store.gc_sweep(now=at + 3600.0) == [entry_path.stem]
    assert record_path.exists(), "the sweep reclaimed its own observation record"


def test_record_publication_temporary_is_never_enumerated_as_a_payload_orphan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC #15's SECOND half — the same disjointness binds EVERY INTERMEDIATE
    FILE the record's own publication creates, not merely the final name. If the
    publication temporary reused the store's `.tmp-` PAYLOAD-temp naming
    convention, a crash after the temp write would leave an artifact the next
    sweep classifies as a crash-orphaned payload — entering count and age
    accounting, being reported as a candidate, and being unlinked as though it
    were ciphertext — all while the FINAL record name still satisfies the
    disjointness check.

    RE-PINNED DELIBERATELY at U-RT-151 (`B-111`), and exactly ONE assertion
    group flips. The witness's old teardown loop (which unlinked each leftover)
    is DROPPED AS REDUNDANT rather than wrapped in a broader `try`: once the
    cleanup ships the leftover is already gone, so that loop would raise
    `FileNotFoundError` and ERROR the test rather than fail it.

    The leftover of the killed publication is no longer permanently
    resident: a LATER, SUCCESSFUL PUBLICATION of the record reclaims it once it
    is past TTL (AC #15's v2.59 qualifier). The flip is a POSITIVE witness that
    ATTRIBUTES the removal to the publication path — the unlink must happen
    INSIDE `_publish_observation_record`, between the record's `os.replace` and
    the method's return — because a witness that merely observed the file's
    absence would equally pass an implementation that widened a SWEEP glob,
    which is the defect AC #15 exists to close. The `.tmp-` prefix-disjointness
    assertion and the not-reported-as-a-candidate log assertion are PRESERVED:
    both are the SWEEP half the qualifier leaves unqualified, and both must
    still hold at every sweep here.

    Mutation probes: naming the publication temporary with the payload-temp
    prefix makes the post-crash sweep enumerate, report and remove it, failing
    the preserved assertions; reverting U-RT-151's cleanup fails the flipped
    assertion; widening `_ORPHAN_GLOB` to match the record's temp prefix fails
    the not-reported assertion AND
    `test_a_failed_publication_leaves_the_leftover_untouched_by_every_sweep`
    (and cannot satisfy the flipped assertion either, since a sweep-glob removal
    happens OUTSIDE the publication window this asserts)."""
    import logging

    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    orphan = root / ".tmp-real-payload-orphan"
    orphan.write_bytes(b"partial ciphertext")
    stale = time.time() - 10.0
    os.utime(orphan, (stale, stale))

    # Simulate a crash mid-publication: the temp is written, the replace never
    # happens, and the leftover temporary is NOT cleaned up.
    def _failing_replace(src: object, dst: object, **kwargs: object) -> None:
        raise OSError(errno.EIO, "simulated crash before the atomic replace")

    def _no_cleanup(path: object, **kwargs: object) -> None:
        return None

    at = time.time()
    monkeypatch.setattr(os, "replace", _failing_replace)
    monkeypatch.setattr(os, "unlink", _no_cleanup)
    store.gc_sweep(now=at, observed_at=at)
    monkeypatch.undo()

    leftovers = [
        p.name
        for p in root.iterdir()
        if p.name != orphan.name and p.name != GC_OBSERVATION_RECORD_FILENAME
    ]
    leftovers = [name for name in leftovers if not name.endswith(".entry")]
    leftovers = [name for name in leftovers if name != ".cross_process.lock"]
    assert leftovers, "the mid-publication crash left no temporary to classify"
    for name in leftovers:
        assert not name.startswith(".tmp-"), (
            f"the record's publication temporary {name!r} carries the PAYLOAD-temp "
            f"prefix — the next sweep would classify it as crash-orphaned ciphertext"
        )

    # The next sweep, well past every TTL, must not enumerate, report or remove it.
    caplog_records: list[logging.LogRecord] = []

    class _Collector(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            caplog_records.append(record)

    handler = _Collector(level=logging.WARNING)
    logger = logging.getLogger("harness.runtime.protected_result_store")
    logger.addHandler(handler)
    # Attribution instrumentation for the flipped assertion: every unlink and
    # the publication's own entry/return are recorded in ONE ordered event log,
    # so "removed by the publication path" is asserted BY POSITION rather than
    # inferred from the file's absence.
    events: list[str] = []
    real_unlink = os.unlink
    real_publish = store._publish_observation_record  # type: ignore[attr-defined]

    def _tracing_unlink(path: object, **kwargs: object) -> None:
        events.append(f"unlink:{os.path.basename(str(path))}")
        real_unlink(path, **kwargs)  # type: ignore[arg-type]

    def _tracing_publish(observations: object, **kwargs: object) -> None:
        events.append("publication:enter")
        try:
            real_publish(observations, **kwargs)
        finally:
            events.append("publication:return")

    try:
        # The crashed publication left no record at all, so a successful sweep
        # first re-records the observation; back-dating then ages it past the
        # grace for the final, reclaim-reaching sweep.
        store.gc_sweep(now=at + 0.01, observed_at=at + 0.01)
        for name in leftovers:
            assert (root / name).exists(), (
                f"the FRESH leftover {name!r} — younger than the TTL at this sweep — was "
                f"removed: the cleanup's past-TTL age gate is missing"
            )
        _backdate_observation_record(store)
        monkeypatch.setattr(os, "unlink", _tracing_unlink)
        monkeypatch.setattr(store, "_publish_observation_record", _tracing_publish)
        store.gc_sweep(now=at + 3600.0)
        monkeypatch.undo()
    finally:
        logger.removeHandler(handler)

    assert events.count("publication:enter") == 1, (
        f"expected exactly one record publication in the final sweep: {events}"
    )
    opened = events.index("publication:enter")
    returned = events.index("publication:return")
    for name in leftovers:
        # FLIPPED (U-RT-151 AC #2): the leftover IS reclaimed — by a LATER
        # PUBLICATION, attributed by position inside the publication window.
        assert not (root / name).exists(), (
            f"the record's own publication temporary {name!r} SURVIVED a later, "
            f"successful publication — U-RT-151's cleanup did not run"
        )
        assert opened < events.index(f"unlink:{name}") < returned, (
            f"the record's own publication temporary {name!r} was removed OUTSIDE the "
            f"publication path (a widened sweep glob would look like this): {events}"
        )
        # PRESERVED: the SWEEP half never reports it as a candidate.
        assert not any(name in record.message for record in caplog_records), (
            f"the sweep REPORTED the record's own publication temporary {name!r} as a candidate"
        )
        # PRESERVED, and asserted at the ENUMERATION surface as well as the
        # reporting one: a widened `_ORPHAN_GLOB` would carry the name into the
        # published observation record even on a sweep whose reclaim the
        # publication's own cleanup pre-empts.
        assert name not in _read_observation_record(store), (
            f"the sweep ENUMERATED the record's own publication temporary {name!r} "
            f"into candidate accounting"
        )


# ---------------------------------------------------------------------------
# `B-111` / U-RT-151 — the record's OWN publication-temp cleanup, permitted by
# U-RT-150 AC #15's v2.59 qualifier (Runtime plan v2.59 §2).
# ---------------------------------------------------------------------------


def _record_publication_leftover(root: Path, suffix: str, *, mtime: float) -> Path:
    """A leftover of a KILLED record publication: a file carrying the record's
    own publication-temp prefix, disjoint from BOTH sweep globs, backdated to
    `mtime`."""
    leftover = root / f"{_GC_OBSERVATION_RECORD_TEMP_PREFIX}{suffix}"
    leftover.write_bytes(b'{"version": 1, "observations": {}}')
    os.utime(leftover, (mtime, mtime))
    return leftover


def test_publication_removes_exactly_its_own_past_ttl_leftovers_and_nothing_else(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """U-RT-151 AC #1 — the cleanup is PREFIX-SCOPED BY CONSTRUCTION, PAST-TTL
    AGE-GATED, and its ENUMERATION RUNS OFF THE LOCK.

    The scope refusals are ASSERTED AS AN EXACT SET rather than as "the leftover
    is gone": the store root additionally holds a real `.tmp-*` payload orphan,
    an `*.entry` member, the record itself, the cross-process lock file, an
    unrelated arbitrarily-named file, and a FRESH own-prefix leftover younger
    than `ttl_seconds`. A publication removes exactly the PAST-TTL own-prefix
    leftovers and nothing else — the fresh one SURVIVES, which is the age-gate
    witness (the deterministic stand-in for the Windows in-flight-temporary race
    a lock-no-op platform cannot witness deterministically).

    The enumeration is asserted OFF-LOCK BY CONSTRUCTION — by the lock's state
    at the moment the prefix-scoped glob runs, not by timing. A root scan under
    the combined lock is O(total files in the root), the cost `B-75` moved off
    it, and would falsify `_publish_observation_record`'s own docstring
    justification for holding the lock across its write.

    Mutation probes: broadening the scope from the prefix constant to the whole
    root fails the exact-set assertion; moving the enumeration inside the lock
    fails the off-lock assertion; removing the age gate fails the
    fresh-leftover-SURVIVES membership of the exact set; unlinking the path's
    OWN in-flight temporary fails the own-temp-survives assertion (and U-RT-150
    AC #14(iii)'s crash-atomicity witness)."""
    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    root = tmp_path / "store"
    stale = time.time() - 10.0

    orphan = root / ".tmp-real-payload-orphan"
    orphan.write_bytes(b"partial ciphertext")
    os.utime(orphan, (stale, stale))
    unrelated = root / "operator-notes.txt"
    unrelated.write_text("neither a candidate nor ours")
    os.utime(unrelated, (stale, stale))
    lock_file = root / ".cross_process.lock"
    lock_file.touch()
    os.utime(lock_file, (stale, stale))
    killed_one = _record_publication_leftover(root, "killed-one", mtime=stale)
    killed_two = _record_publication_leftover(root, "killed-two", mtime=stale)
    # Fresh: written now, so it is younger than the TTL at the sweep below.
    fresh = _record_publication_leftover(root, "live-co-resident", mtime=time.time())

    globs: list[tuple[str, bool]] = []
    real_glob = Path.glob
    real_mkstemp = tempfile.mkstemp
    real_unlink = os.unlink
    in_flight: list[str] = []
    unlinked: list[str] = []

    def _tracing_glob(self: Path, pattern: str, **kwargs: object) -> object:
        # `_publish_lock` is acquired in the SAME `with` statement as the
        # cross-process lock, so its state is a faithful, observable proxy for
        # "the combined lock is held" — and a state check, not a timing one.
        globs.append((pattern, store._publish_lock.locked()))  # type: ignore[attr-defined]
        return real_glob(self, pattern, **kwargs)  # type: ignore[arg-type]

    def _tracing_mkstemp(**kwargs: object) -> tuple[int, str]:
        fd, name = real_mkstemp(**kwargs)  # type: ignore[arg-type]
        in_flight.append(name)
        return fd, name

    def _tracing_unlink(path: object, **kwargs: object) -> None:
        unlinked.append(str(path))
        real_unlink(path, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "glob", _tracing_glob)
    monkeypatch.setattr(tempfile, "mkstemp", _tracing_mkstemp)
    monkeypatch.setattr(os, "unlink", _tracing_unlink)
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    monkeypatch.undo()

    assert sorted(p.name for p in root.iterdir()) == sorted(
        [
            entry_path.name,
            orphan.name,
            unrelated.name,
            lock_file.name,
            GC_OBSERVATION_RECORD_FILENAME,
            fresh.name,
        ]
    ), (
        "the publication's cleanup did not remove EXACTLY the past-TTL own-prefix "
        f"leftovers ({killed_one.name!r}, {killed_two.name!r}) and nothing else"
    )

    own_prefix_globs = [
        held for pattern, held in globs if pattern.startswith(_GC_OBSERVATION_RECORD_TEMP_PREFIX)
    ]
    assert own_prefix_globs, (
        "the cleanup's candidate list was not produced by a prefix-scoped glob of "
        f"the store root: {globs}"
    )
    assert not any(own_prefix_globs), (
        "the cleanup's ENUMERATION ran while the publish lock was held — that is "
        "the O(store size) root scan `B-75` moved OFF the lock"
    )

    assert in_flight, "the publication created no temporary at all"
    for name in in_flight:
        assert name not in unlinked, (
            f"the cleanup unlinked the publication's OWN in-flight temporary {name!r} — "
            f"that reopens the unlink-then-recreate window AC #14(iii) forbids"
        )
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_READABLE


def test_a_failed_publication_leaves_the_leftover_untouched_by_every_sweep(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """U-RT-151 AC #2's ADDED witness, isolating the SWEEP half AC #15's
    qualifier PRESERVES. Once the cleanup ships, every successful publication
    reclaims the leftover before a later sweep can reach it — so without this
    witness nothing would still exercise "a SWEEP must not enumerate, report or
    remove the record's publication temporary", and disposition (a) would
    silently trade a real protection for the fix.

    With the leftover present and the record's publication made to FAIL (so the
    cleanup does not run — it sits strictly after the `os.replace`), a full
    sweep PAST every TTL — one that demonstrably reaches its reclaim path, since
    it removes the real payload orphan — still neither enumerates the leftover
    (it never enters the observation record, and the orphan-class gauge reports
    the PAYLOAD orphan's age although the leftover is far older), reports it,
    nor removes it.

    Mutation probe: widening `_ORPHAN_GLOB` to match the record's temp prefix is
    caught by the ORPHAN-CLASS GAUGE assertion below — it reads the leftover's
    ~5000s in place of the payload orphan's 10s. That single assertion is the
    load-bearing killer, and naming it matters: the surrounding assertions do NOT
    kill under that mutation, because the leftover is planted after the only
    successful sweep and so carries no recorded first observation — it would be
    enumerated but not yet ELIGIBLE, hence still neither reclaimed nor named in
    any line."""
    import logging

    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    orphan = root / ".tmp-real-payload-orphan"
    orphan.write_bytes(b"partial ciphertext")
    orphan_mtime = time.time() - 10.0
    os.utime(orphan, (orphan_mtime, orphan_mtime))
    at = orphan_mtime + 10.0

    caplog.set_level(logging.DEBUG, logger="harness.runtime.protected_result_store")
    # A first, successful sweep records the payload orphan's observation. The
    # leftover is planted AFTER it, so no successful publication ever sees it —
    # the only publication that could have cleaned it up is the FAILING one
    # below, which never reaches its post-`os.replace` cleanup.
    store.gc_sweep(now=at, observed_at=at)
    leftover = _record_publication_leftover(root, "killed", mtime=orphan_mtime - 4990.0)
    _backdate_observation_record(store)
    caplog.clear()

    def _failing_replace(src: object, dst: object, **kwargs: object) -> None:
        raise OSError(errno.EIO, "simulated crash before the atomic replace")

    monkeypatch.setattr(os, "replace", _failing_replace)
    store.gc_sweep(now=at)
    monkeypatch.undo()

    assert not orphan.exists(), (
        "the sweep never reached its reclaim path — the isolation this witness "
        "asserts would be vacuous"
    )
    assert leftover.exists(), (
        "a SWEEP removed the record's own publication temporary — the half AC #15's "
        "qualifier PRESERVES unqualified"
    )
    assert not any(leftover.name in record.message for record in caplog.records), (
        "a SWEEP reported the record's own publication temporary as a candidate"
    )
    # Not ENUMERATED either: the orphan-class gauge on that sweep's own reclaim
    # emission reports the PAYLOAD orphan's 10s, not the leftover's 5000s.
    gc_line = next(r for r in caplog.records if "crash-orphaned temp-file GC'd" in r.message)
    assert "oldest_orphan_age_s=10.0" in gc_line.message, (
        f"the leftover entered the orphan class's age accounting: {gc_line.message}"
    )
    assert leftover.name not in _read_observation_record(store), (
        "the record's publication temporary was ENUMERATED into candidate accounting"
    )


def test_the_payload_orphan_class_is_byte_unchanged_by_the_record_temp_cleanup(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """U-RT-151 AC #3 — in the SAME witness state as AC #1, a real `.tmp-*`
    payload orphan is STILL classified exactly as before: enumerated by the
    sweep, counted, carried by AC #8's oldest-resident-candidate gauge at BOTH
    surfaces, reported as a candidate, reclaimed once BOTH conjuncts elapse —
    and NOT reclaimed on the sweep that first observes it.

    Load-bearing rather than bookkeeping: the cheapest wrong way to close
    `B-111` is to let the record's temporary fall into the payload class, and an
    acceptance surface asserting only "the leftover is gone" would accept it.

    Mutation probe: routing the record's publication temporary through the
    payload-orphan class fails this criterion (the counts and both gauges read
    one too many) together with AC #2's preserved assertions."""
    import logging

    ttl = 1.0
    store, entry_path = _stale_entry(tmp_path, ttl_seconds=ttl, age_seconds=10.0)
    root = tmp_path / "store"
    orphan = root / ".tmp-real-payload-orphan"
    orphan.write_bytes(b"partial ciphertext")
    orphan_mtime = time.time() - 10.0
    os.utime(orphan, (orphan_mtime, orphan_mtime))
    (root / "operator-notes.txt").write_text("neither a candidate nor ours")
    _record_publication_leftover(root, "killed-one", mtime=orphan_mtime - 4990.0)
    _record_publication_leftover(root, "live-co-resident", mtime=time.time())
    at = orphan_mtime + 10.0

    caplog.set_level(logging.DEBUG, logger="harness.runtime.protected_result_store")
    store.gc_sweep(now=at, observed_at=at)

    # Enumerated + counted + gauged + reported, at the sweep emission surface.
    reset_line = next(r for r in caplog.records if "no GC observation record" in r.message)
    assert "past_ttl_orphans=1" in reset_line.message
    assert "oldest_orphan_age_s=10.0" in reset_line.message
    assert orphan.name in _read_observation_record(store)
    # NOT reclaimed on the sweep that first observes it.
    assert orphan.exists(), "the crash orphan was reclaimed on its FIRST observation"

    # The second gauge surface — the read-only, sweep-free snapshot.
    snapshot = read_protected_result_store_snapshot(root, now=at)
    assert snapshot is not None
    assert snapshot.orphan_count == 1, (
        f"the record's publication temporary entered the payload-orphan count: {snapshot}"
    )
    assert snapshot.gauge.oldest_orphan_age_seconds is not None
    assert 9.9 < snapshot.gauge.oldest_orphan_age_seconds < 10.1
    assert snapshot.entry_count == 1

    # Reclaimed once BOTH conjuncts elapse.
    _backdate_observation_record(store)
    caplog.clear()
    assert store.gc_sweep(now=at) == [entry_path.stem]
    assert not orphan.exists()
    gc_line = next(r for r in caplog.records if "crash-orphaned temp-file GC'd" in r.message)
    assert orphan.name in gc_line.message


def test_the_cleanup_is_silent_on_success_and_reports_a_suppressed_unlink_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """U-RT-151 AC #4 — the success path adds NO surface; the failure path adds
    exactly ONE emission, on the sweep's EXISTING report-log carrier.

    On success the cleanup emits no report-log line at any level, no span and no
    metric, mints no namespace, and creates no file or directory (the removals
    are of an artifact that is a candidate of neither class and appears in no
    count, gauge or report). A suppressed removal `OSError` MUST nonetheless be
    REPORTED — a persistently failing cleanup that said nothing would recreate
    exactly the accounting invisibility `B-111` was ratified to close — while
    never failing the publication and never propagating; the directory `fsync`
    still runs. And the suppression MUST NOT extend over the `os.replace`
    itself: a failing replace still emits the publication-failure line.

    A leftover that VANISHED before the removal is a benign concurrent reclaim,
    not a failure, and MUST NOT be reported either — otherwise two sweeps that
    collected the same pre-lock leftover inject a false positive into exactly the
    persistent-failure signal phase 2 exists to keep truthful.

    Mutation probes: emitting anything on the SUCCESS path fails phase 1; moving
    the cleanup loop after the directory `fsync` fails phase 1's ORDER assertion;
    suppressing the failure emission fails phase 2; letting the removal
    `OSError` propagate fails phase 2's no-raise assertion; broadening the
    suppression over the `os.replace` fails phase 3 (and leaks the in-flight
    temporary as a FRESH own-prefix leftover, failing AC #1's exact set);
    reporting the vanished leftover fails phase 4."""
    import logging

    store = _store(tmp_path, ttl_seconds=1.0)
    root = tmp_path / "store"
    root.mkdir(parents=True, exist_ok=True)
    stale = time.time() - 10.0
    leftover = _record_publication_leftover(root, "killed-one", mtime=stale)

    # Phase 1 — SUCCESS is silent, creates nothing, and the removal runs BEFORE
    # the directory `fsync` (the sweep's ONLY `_fsync_dir` call), which is what
    # makes the removal durable under the same barrier as the `os.replace`.
    caplog.set_level(logging.DEBUG, logger="harness.runtime.protected_result_store")
    order: list[str] = []
    ordering_real_unlink = os.unlink
    ordering_real_fsync_dir = store._fsync_dir  # type: ignore[attr-defined]

    def _ordering_unlink(path: object, **kwargs: object) -> None:
        order.append(f"unlink:{os.path.basename(str(path))}")
        ordering_real_unlink(path, **kwargs)  # type: ignore[arg-type]

    def _ordering_fsync_dir(directory: Path) -> None:
        order.append(f"fsync:{Path(directory).name}")
        ordering_real_fsync_dir(directory)

    monkeypatch.setattr(os, "unlink", _ordering_unlink)
    monkeypatch.setattr(store, "_fsync_dir", _ordering_fsync_dir)
    at = time.time()
    store.gc_sweep(now=at, observed_at=at)
    monkeypatch.undo()
    assert not leftover.exists()
    assert order.index(f"unlink:{leftover.name}") < order.index(f"fsync:{root.name}"), (
        "the cleanup loop ran AFTER the directory `fsync` — the removal is then "
        f"outside the barrier that durably records the publication: {order}"
    )
    assert not any(leftover.name in record.message for record in caplog.records), (
        "the cleanup emitted on its SUCCESS path — it removes an artifact that "
        "appears in no count, gauge or report"
    )
    assert sorted(p.name for p in root.iterdir()) == sorted(
        [GC_OBSERVATION_RECORD_FILENAME, ".cross_process.lock"]
    ), "the cleanup created a new file or directory"

    # Phase 2 — a suppressed removal `OSError` IS reported, never fails the
    # publication, never propagates, and the directory `fsync` still runs.
    second = _record_publication_leftover(root, "killed-two", mtime=stale)
    real_unlink = os.unlink

    def _refusing_unlink(path: object, **kwargs: object) -> None:
        if os.path.basename(str(path)).startswith(_GC_OBSERVATION_RECORD_TEMP_PREFIX):
            raise OSError(errno.EACCES, "simulated permission denied")
        real_unlink(path, **kwargs)  # type: ignore[arg-type]

    fsyncs: list[str] = []
    real_fsync_dir = store._fsync_dir  # type: ignore[attr-defined]

    def _tracing_fsync_dir(directory: Path) -> None:
        fsyncs.append(str(directory))
        real_fsync_dir(directory)

    caplog.clear()
    monkeypatch.setattr(os, "unlink", _refusing_unlink)
    monkeypatch.setattr(store, "_fsync_dir", _tracing_fsync_dir)
    _backdate_observation_record(store)
    store.gc_sweep(now=at + 0.1, observed_at=at + 0.1)  # MUST NOT raise
    monkeypatch.undo()

    assert second.exists(), "the refusing unlink did not actually refuse"
    failure_lines = [
        r for r in caplog.records if second.name in r.message and r.levelno >= logging.ERROR
    ]
    assert failure_lines, (
        "a SUPPRESSED removal `OSError` was not reported on the sweep's existing "
        "report-log carrier — a persistently failing cleanup would be invisible"
    )
    assert fsyncs, "the directory fsync did not run after a suppressed removal failure"
    snapshot = read_protected_result_store_snapshot(root)
    assert snapshot is not None
    assert snapshot.record_state is GcObservationRecordState.PRESENT_READABLE, (
        "a suppressed cleanup failure failed the publication"
    )

    # Phase 3 — the suppression never covers the `os.replace`.
    def _failing_replace(src: object, dst: object, **kwargs: object) -> None:
        raise OSError(errno.EIO, "simulated crash before the atomic replace")

    caplog.clear()
    monkeypatch.setattr(os, "replace", _failing_replace)
    store.gc_sweep(now=at + 0.2, observed_at=at + 0.2)
    monkeypatch.undo()

    # (i) A suppression broadened over the `os.replace` SKIPS the
    # `except BaseException` handler, leaking the failed publication's OWN
    # in-flight temporary as a fresh own-prefix leftover.
    leaked = [
        p.name
        for p in root.iterdir()
        if p.name.startswith(_GC_OBSERVATION_RECORD_TEMP_PREFIX) and p.name != second.name
    ]
    assert not leaked, (
        f"the failed publication leaked its own in-flight temporary {leaked} — the "
        f"suppression covered the `os.replace` and skipped the cleanup handler"
    )
    # (ii) ...and the failing replace still reports through `_observe_candidates`.
    assert any("GC observation record publication failed" in r.message for r in caplog.records), (
        "a failing `os.replace` was swallowed — the suppression covers more than the removal"
    )
    assert second.exists(), "the cleanup ran even though the publication FAILED"

    # Phase 4 — a leftover that VANISHED before the removal is NOT a failure.
    # The vanish is REAL, not simulated at the unlink: the file is removed
    # between this sweep's off-lock enumeration and its publication, exactly as
    # a concurrent sweep that collected the same pre-lock leftover would.
    third = _record_publication_leftover(root, "killed-three", mtime=stale)
    real_observe = store._observe_candidates  # type: ignore[attr-defined]

    def _vanishing_observe(names: list[str], **kwargs: object) -> object:
        os.unlink(third)  # the OTHER sweep reclaimed it first
        return real_observe(names, **kwargs)

    caplog.clear()
    monkeypatch.setattr(store, "_observe_candidates", _vanishing_observe)
    store.gc_sweep(now=at + 0.3, observed_at=at + 0.3)  # MUST NOT raise
    monkeypatch.undo()

    assert not third.exists()
    assert not [
        r for r in caplog.records if third.name in r.message and r.levelno >= logging.ERROR
    ], (
        "a benign concurrent reclaim — the leftover vanished before the unlink — was "
        "reported as a cleanup FAILURE, a false positive in the operator's "
        "persistent-failure signal"
    )


def test_a_recycled_temporary_name_is_refused_by_lock_bound_identity_revalidation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """`B-110` mechanism (c), taken as this arc's companion per its standing
    opportunistic trigger (the unit works `gc_sweep`'s phase split).

    Phase 1 — RELOCATION: the `.tmp-*` unlinks run UNDER the lock hold that
    SELECTED them, not off-lock. Off-lock, two concurrent sweeps can both select
    one expired orphan; if the first removes it and a publisher is handed the
    freed name, the second sweep's stale path unlinks that ACTIVE replacement,
    bypassing `_publish_atomic`'s whole-lifetime lock hold and losing a completed
    paid effect's recovery record.

    Phase 2 — REVALIDATION: the identity captured at SELECTION (the
    `(st_dev, st_ino, st_mtime)` triple — a bare re-`stat()` is insufficient,
    since POSIX offers no compare-inode-and-unlink primitive) is re-verified
    under the same lock immediately before the unlink. The collision is injected
    DETERMINISTICALLY rather than raced for: between selection and removal, the
    other sweep's unlink is performed and `tempfile.mkstemp` is monkeypatched to
    hand the publisher exactly the just-freed name.

    Mutation probes: moving the unlink loop back outside the `with` block fails
    phase 1's lock-held assertion; dropping the identity revalidation lets phase
    2 unlink the replacement and fails its survival assertion."""
    import logging

    caplog.set_level(logging.DEBUG, logger="harness.runtime.protected_result_store")

    # Phase 1 — the removal happens under the selecting lock hold.
    store = _store(tmp_path / "relocation", ttl_seconds=1.0)
    root = tmp_path / "relocation" / "store"
    root.mkdir(parents=True, exist_ok=True)
    orphan = root / ".tmp-under-lock-removal"
    orphan.write_bytes(b"partial ciphertext")
    stale = time.time() - 10.0
    os.utime(orphan, (stale, stale))
    at = stale + 10.0
    store.gc_sweep(now=at, observed_at=at)
    _backdate_observation_record(store)

    lock_held: list[bool] = []
    real_path_unlink = Path.unlink

    def _recording_unlink(self: Path, **kwargs: object) -> None:
        if self.name == orphan.name:
            lock_held.append(store._publish_lock.locked())  # type: ignore[attr-defined]
        real_path_unlink(self, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "unlink", _recording_unlink)
    store.gc_sweep(now=at)
    monkeypatch.undo()
    assert not orphan.exists()
    assert lock_held == [True], (
        f"the crash-orphan unlink ran with the selecting lock RELEASED: {lock_held}"
    )

    # Phase 2 — the recycled-name collision is refused.
    store_2 = _store(tmp_path / "revalidation", ttl_seconds=1.0)
    root_2 = tmp_path / "revalidation" / "store"
    root_2.mkdir(parents=True, exist_ok=True)
    recycled = root_2 / ".tmp-recycled-name"
    recycled.write_bytes(b"the EXPIRED crash orphan both sweeps selected")
    os.utime(recycled, (stale, stale))
    store_2.gc_sweep(now=at, observed_at=at)
    _backdate_observation_record(store_2)

    hand_back: list[str] = []
    real_mkstemp = tempfile.mkstemp
    real_observe = store_2._observe_candidates  # type: ignore[attr-defined]
    replacement_payload = b"a NEW in-flight temporary at the just-freed name"

    def _recycling_mkstemp(**kwargs: object) -> tuple[int, str]:
        if hand_back:
            name = hand_back.pop()
            return os.open(name, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600), name
        return real_mkstemp(**kwargs)  # type: ignore[arg-type]

    def _other_sweep_then_publisher(names: list[str], **kwargs: object) -> object:
        # The OTHER sweep removes the orphan both sweeps selected...
        os.unlink(recycled)
        # ...and `tempfile.mkstemp` then hands the publisher the freed name.
        hand_back.append(str(recycled))
        fd, drawn = tempfile.mkstemp(dir=root_2, prefix=".tmp-")
        os.write(fd, replacement_payload)
        os.close(fd)
        assert drawn == str(recycled)
        return real_observe(names, **kwargs)

    monkeypatch.setattr(tempfile, "mkstemp", _recycling_mkstemp)
    monkeypatch.setattr(store_2, "_observe_candidates", _other_sweep_then_publisher)
    caplog.clear()
    store_2.gc_sweep(now=at)
    monkeypatch.undo()

    assert recycled.exists(), (
        "the sweep unlinked an ACTIVE file that had inherited the just-freed name — "
        "the selection-time identity was not revalidated under the lock"
    )
    assert recycled.read_bytes() == replacement_payload
    assert any("refers to a DIFFERENT file" in r.message for r in caplog.records), (
        "the refusal was not reported at all"
    )
