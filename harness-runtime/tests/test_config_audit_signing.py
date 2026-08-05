"""B-47 PR B — `AuditSigningConfig` + `make_audit_signing_backend` tests.

The composition-root factory (OD spec v1.33 §21.2.1's expected owner of
backend selection/construction). Hermetic: the boto3 client is injected via
the `kms_client` seam (the R-421 `gcp_secret_accessor` precedent); no AWS
credential or network is touched.
"""

from __future__ import annotations

import pytest
from harness_cp.aws_kms_signing_backend import (
    AwsKmsSigningBackend,
    MutableKeyAliasRejectedError,
)
from harness_runtime.config import audit_signing as audit_signing_module
from harness_runtime.config.audit_signing import (
    BreakerGuardedSigningBackend,
    SigningBackendSdkUnavailableError,
    make_audit_signing_backend,
)
from harness_runtime.types import AuditSigningBackendKind, AuditSigningConfig
from pydantic import ValidationError

_ARN = "arn:aws:kms:us-east-1:111122223333:key/deadbeef-dead-beef-dead-beefdeadbeef"


class _FakeKmsClient:
    """Minimal stand-in satisfying `AwsKmsSigningBackend`'s constructor."""


def test_default_config_is_none_backend_and_factory_returns_none() -> None:
    """The default (`backend = "none"`) constructs nothing — every signing
    surface keeps the placeholder path byte-for-byte."""
    config = AuditSigningConfig()
    assert config.backend is AuditSigningBackendKind.NONE
    assert make_audit_signing_backend(config) is None


def test_aws_kms_requires_non_empty_key_arns() -> None:
    """ADR-D8 §Decision item 2 — no default key is ever assumed."""
    with pytest.raises(ValidationError, match="key_arns must be non-empty"):
        AuditSigningConfig(backend=AuditSigningBackendKind.AWS_KMS)


def test_factory_constructs_kms_backend_with_injected_client() -> None:
    """The `kms_client` injection seam (R-421 precedent) yields a real
    `AwsKmsSigningBackend` over the configured mapping — no boto3 import."""
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    backend = make_audit_signing_backend(config, kms_client=_FakeKmsClient())
    # B-47 PR B2a — the factory wraps the concrete backend in the C9
    # breaker at the single construction point; the Protocol surface
    # (algorithm + sign/verify) is preserved by the wrapper.
    assert isinstance(backend, BreakerGuardedSigningBackend)
    assert isinstance(backend._inner, AwsKmsSigningBackend)
    assert backend.algorithm == "ed25519"


def test_factory_rejects_alias_arns_loud() -> None:
    """ADR-D8 §Decision item 2 — a mutable KMS alias must never become a
    signing key's stable identity; the backend's own construction-time
    rejection propagates through the factory unswallowed."""
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"k": "alias/mutable-alias"},
    )
    with pytest.raises(MutableKeyAliasRejectedError):
        make_audit_signing_backend(config, kms_client=_FakeKmsClient())


def test_missing_boto3_fails_loud_not_silent(monkeypatch: pytest.MonkeyPatch) -> None:
    """A deployment that configured real signing must never silently degrade
    to placeholder signatures — an absent boto3 raises the typed error."""

    def _no_boto3(name: str) -> object:
        raise ModuleNotFoundError(f"No module named {name!r}")

    monkeypatch.setattr(audit_signing_module, "import_module", _no_boto3)
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"k": _ARN},
    )
    with pytest.raises(SigningBackendSdkUnavailableError, match="boto3"):
        make_audit_signing_backend(config)


def test_blank_key_arn_values_rejected_at_config() -> None:
    """Codex round-6 (PR B1) — a mapping whose value is blank passed the
    non-empty-dict check and the coverage check, then failed inside boto3 on
    the first signing call; rejected at config validation instead."""
    with pytest.raises(ValidationError, match="is blank"):
        AuditSigningConfig(
            backend=AuditSigningBackendKind.AWS_KMS,
            key_arns={"harness-runtime-redaction-token": "   "},
        )
    with pytest.raises(ValidationError, match="blank logical key_id"):
        AuditSigningConfig(
            backend=AuditSigningBackendKind.AWS_KMS,
            key_arns={" ": _ARN},
        )


def test_key_arns_whitespace_normalized_and_duplicates_rejected() -> None:
    """Codex round-8 (PR B1) — surrounding whitespace must not survive to the
    first KMS Sign call as an invalid KeyId: the stored mapping is
    normalized, and two keys colliding after normalization fail loud."""
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={" harness-runtime-redaction-token ": f"  {_ARN}  "},
    )
    assert config.key_arns == {"harness-runtime-redaction-token": _ARN}

    with pytest.raises(ValidationError, match="duplicate logical key_id"):
        AuditSigningConfig(
            backend=AuditSigningBackendKind.AWS_KMS,
            key_arns={"k": _ARN, " k": _ARN},
        )


def test_key_arns_mapping_is_immutable_after_validation() -> None:
    """Codex round-9 (PR B1) — frozen=True prevents rebinding the field but
    not mutating the dict; a post-validation mutation to a blank value would
    defeat everything the validator just rejected. The stored mapping is an
    immutable view."""
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    with pytest.raises(TypeError):
        config.key_arns["harness-runtime-redaction-token"] = ""  # type: ignore[index]


def test_config_deepcopy_and_model_copy_survive_immutability() -> None:
    """Codex round-34 (PR B1) — MappingProxyType broke copy.deepcopy and
    model_copy(deep=True) of every RuntimeConfig carrying the default
    sub-config. The immutable carrier must pickle: copies succeed AND stay
    immutable."""
    import copy

    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    duplicate = copy.deepcopy(config)
    assert duplicate.key_arns == config.key_arns

    shallow_deep = config.model_copy(deep=True)
    assert shallow_deep.key_arns == config.key_arns

    with pytest.raises(TypeError):
        duplicate.key_arns["harness-runtime-redaction-token"] = ""  # type: ignore[index]


def test_ior_operator_cannot_mutate_key_arns() -> None:
    """Codex round-35 (PR B1) — `cfg.key_arns |= {...}` mutated the mapping
    in place BEFORE the frozen-field re-assignment raised; a caught error
    left the 'immutable' mapping changed with an unvalidated value."""
    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    with pytest.raises((TypeError, ValidationError)):
        config.key_arns |= {"evil": ""}  # type: ignore[operator, misc]
    assert dict(config.key_arns) == {"harness-runtime-redaction-token": _ARN}


def test_default_key_arns_is_immutable_too() -> None:
    """Codex round-20 (PR B1) — pydantic skips field validators on defaults
    unless validate_default is set, so the DEFAULT config's key_arns stayed a
    mutable dict that bypassed every blank/normalization check. The default
    is now validated (and therefore proxied) like any supplied value."""
    config = AuditSigningConfig()
    with pytest.raises(TypeError):
        config.key_arns["x"] = "y"  # type: ignore[index]


# ---------------------------------------------------------------------------
# `B-109` — the sealed `_ImmutableKeyArns` carrier.
#
# The disabled item/update methods above left the INHERITED `dict.__init__`
# open, and `dict.__init__` on a live instance UPDATES it in place (it does not
# clear first), so `cfg.key_arns.__init__({...})` re-populated a validated,
# frozen config's signing map post-validation. Witness shapes mirror the
# sibling PD-8 probes (b)/(c) at
# `harness-cp/tests/test_workflow_driver_effect_fence_empty_key_b107.py`.
# ---------------------------------------------------------------------------


def test_b109_reinitializing_the_stored_key_arns_mapping_is_refused() -> None:
    """`B-109` — `obj.__init__({...})` on an already-constructed carrier is
    refused, and the mapping is byte-unchanged afterwards.

    Witnessed on BOTH the raw carrier and through a validated config's field:
    unlike `dict.__setitem__(obj, k, v)`, `obj.__init__(...)` names no base
    class — it resolves through the type's own MRO — so it is a route the type
    EXPOSES, not an explicit base-class escape."""
    from harness_runtime.types import _ImmutableKeyArns

    raw = _ImmutableKeyArns({"harness-runtime-redaction-token": _ARN})
    with pytest.raises(TypeError, match="immutable after validation"):
        raw.__init__({"injected": "arn:EVIL"})  # type: ignore[misc]
    assert dict(raw) == {"harness-runtime-redaction-token": _ARN}

    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    with pytest.raises(TypeError, match="immutable after validation"):
        config.key_arns.__init__({"harness-runtime-redaction-token": "arn:EVIL"})  # type: ignore[misc]
    assert dict(config.key_arns) == {"harness-runtime-redaction-token": _ARN}


def test_b109_the_seal_itself_cannot_be_reopened_by_attribute_assignment() -> None:
    """`B-109` — a naive `_sealed` flag would be reopenable via
    `obj._sealed = False`, walking straight back into the hole the seal closes
    (the sibling's round-3 lesson, carried rather than re-learned). `__slots__`
    plus a refusing `__setattr__`/`__delattr__` closes it: there is no instance
    `__dict__` to write into and no ordinary assignment that reaches the slot.

    The residual `object.__setattr__(obj, "_sealed", False)` route explicitly
    NAMES A BASE CLASS and is deliberately out of scope — Python cannot seal
    against that."""
    from harness_runtime.types import _ImmutableKeyArns

    stored = _ImmutableKeyArns({"harness-runtime-redaction-token": _ARN})
    with pytest.raises(TypeError):
        stored._sealed = False  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        del stored._sealed  # type: ignore[attr-defined]
    assert not hasattr(stored, "__dict__"), "a `__dict__` would reintroduce the writable seal"
    with pytest.raises(TypeError, match="immutable after validation"):
        stored.__init__({"injected": "arn:EVIL"})  # type: ignore[misc]
    assert dict(stored) == {"harness-runtime-redaction-token": _ARN}


def test_b109_copies_of_a_populated_config_succeed_and_are_themselves_sealed() -> None:
    """`B-109` — the seal must not cost the compatibility the dict-subclass
    choice exists to buy (round 34). `__reduce__` rebuilds a FRESH object whose
    slot is unset, so `copy.deepcopy` / `pickle` / `model_copy(deep=True)` all
    still succeed — and each copy ends up sealed in its own right."""
    import copy
    import pickle

    config = AuditSigningConfig(
        backend=AuditSigningBackendKind.AWS_KMS,
        key_arns={"harness-runtime-redaction-token": _ARN},
    )
    for copied in (
        copy.deepcopy(config),
        pickle.loads(pickle.dumps(config)),
        config.model_copy(deep=True),
    ):
        assert dict(copied.key_arns) == {"harness-runtime-redaction-token": _ARN}
        with pytest.raises(TypeError, match="immutable after validation"):
            copied.key_arns.__init__({"injected": "arn:EVIL"})  # type: ignore[misc]
        assert dict(copied.key_arns) == {"harness-runtime-redaction-token": _ARN}


def test_b109_no_arg_construction_still_works_and_is_sealed() -> None:
    """`B-109` — the sealed `__init__`'s single positional-only parameter
    defaults to a read-only empty mapping (a shared mutable `{}` default would
    be a live class-level container), so `cls()` stays valid — the shape
    `__reduce__` and the default-config path both depend on."""
    from harness_runtime.types import _ImmutableKeyArns

    empty = _ImmutableKeyArns()
    assert dict(empty) == {}
    with pytest.raises(TypeError, match="immutable after validation"):
        empty.__init__({"injected": "arn:EVIL"})  # type: ignore[misc]
    assert dict(empty) == {}


class _FlakyBackend:
    """Scripted inner backend: raises while `failing` is True."""

    algorithm = "ed25519"

    def __init__(self) -> None:
        self.failing = True
        self.sign_calls = 0
        self.verify_calls = 0

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        self.sign_calls += 1
        if self.failing:
            raise RuntimeError("kms down")
        return b"s" * 64  # genuine ed25519 width — the wrapper validates length

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        self.verify_calls += 1
        return True


def _guarded(inner: _FlakyBackend, clock: dict[str, float]) -> BreakerGuardedSigningBackend:
    return BreakerGuardedSigningBackend(
        inner,
        fail_threshold=3,
        cooldown_seconds=30.0,
        monotonic=lambda: clock["now"],
    )


def test_breaker_opens_after_consecutive_failures_and_fails_fast() -> None:
    """B-47 item (d), ADR-D8 §Decision item 5 — threshold consecutive sign
    failures open the breaker; while open, sign raises WITHOUT touching the
    backend (fail-loud-fast: no placeholder degradation, no hot-path stall)."""
    from harness_runtime.config.audit_signing import AuditSigningBreakerOpenError

    inner = _FlakyBackend()
    clock = {"now": 0.0}
    guarded = _guarded(inner, clock)

    for _ in range(3):
        with pytest.raises(RuntimeError, match="kms down"):
            guarded.sign(message=b"m", key_id="k", key_period=0)
    assert inner.sign_calls == 3

    with pytest.raises(AuditSigningBreakerOpenError, match="breaker OPEN"):
        guarded.sign(message=b"m", key_id="k", key_period=0)
    assert inner.sign_calls == 3  # backend NOT touched while open

    # verify passes through unguarded even while open (ADR-D8 scopes the
    # breaker to the signing call).
    assert guarded.verify(message=b"m", signature=b"s", key_id="k", key_period=0)
    assert inner.verify_calls == 1


def test_breaker_half_open_probe_closes_on_success() -> None:
    from harness_runtime.config.audit_signing import AuditSigningBreakerOpenError

    inner = _FlakyBackend()
    clock = {"now": 0.0}
    guarded = _guarded(inner, clock)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            guarded.sign(message=b"m", key_id="k", key_period=0)

    # Cooldown not yet elapsed → still failing fast.
    clock["now"] = 29.0
    with pytest.raises(AuditSigningBreakerOpenError):
        guarded.sign(message=b"m", key_id="k", key_period=0)

    # Cooldown elapsed; the probe is admitted and succeeds → breaker closes.
    clock["now"] = 31.0
    inner.failing = False
    assert guarded.sign(message=b"m", key_id="k", key_period=0) == b"s" * 64
    assert guarded.sign(message=b"m", key_id="k", key_period=0) == b"s" * 64
    assert inner.sign_calls == 5


def test_breaker_half_open_probe_failure_reopens_cooldown() -> None:
    from harness_runtime.config.audit_signing import AuditSigningBreakerOpenError

    inner = _FlakyBackend()
    clock = {"now": 0.0}
    guarded = _guarded(inner, clock)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            guarded.sign(message=b"m", key_id="k", key_period=0)

    clock["now"] = 31.0
    with pytest.raises(RuntimeError, match="kms down"):  # probe admitted, fails
        guarded.sign(message=b"m", key_id="k", key_period=0)
    assert inner.sign_calls == 4

    # Re-opened: a fresh cooldown window from the probe failure.
    clock["now"] = 60.0
    with pytest.raises(AuditSigningBreakerOpenError):
        guarded.sign(message=b"m", key_id="k", key_period=0)
    assert inner.sign_calls == 4


def test_stale_pre_open_success_does_not_close_open_breaker() -> None:
    """Codex round-1 P1 (PR B2a) — a slow call admitted while CLOSED can
    succeed AFTER concurrent failures opened the breaker; that stale success
    must not instantly close the newly-opened breaker (epoch guard)."""
    import threading as threading_module

    from harness_runtime.config.audit_signing import AuditSigningBreakerOpenError

    entered = threading_module.Event()
    release = threading_module.Event()

    class _SlowFirstBackend:
        algorithm = "ed25519"

        def __init__(self) -> None:
            self.calls = 0
            self._lock = threading_module.Lock()

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            with self._lock:
                self.calls += 1
                mine = self.calls
            if mine == 1:
                entered.set()
                assert release.wait(timeout=10.0)
                return b"w" * 64
            raise RuntimeError("kms down")

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            return True

    inner = _SlowFirstBackend()
    clock = {"now": 0.0}
    guarded = _guarded(inner, clock)

    slow_result: list[bytes] = []
    slow = threading_module.Thread(
        target=lambda: slow_result.append(guarded.sign(message=b"m", key_id="k", key_period=0)),
        daemon=True,
    )
    slow.start()
    assert entered.wait(timeout=10.0)

    # While the slow (closed-epoch) call is in flight, three failures open
    # the breaker.
    for _ in range(3):
        with pytest.raises(RuntimeError, match="kms down"):
            guarded.sign(message=b"m", key_id="k", key_period=0)

    release.set()
    slow.join(timeout=10.0)
    assert slow_result == [b"w" * 64]

    # The stale success must NOT have closed the breaker.
    with pytest.raises(AuditSigningBreakerOpenError):
        guarded.sign(message=b"m", key_id="k", key_period=0)


def test_malformed_signature_is_typed_failure_and_counts_toward_breaker() -> None:
    """Codex round-9 P2 — a 'successful' KMS response carrying a malformed
    signature recorded breaker SUCCESS and failed downstream as an untyped
    ValueError (silently swallowed by the best-effort paths; repeated
    malformed responses never opened the breaker). Result validation now
    lives inside the typed boundary."""
    from harness_runtime.config.audit_signing import (
        AuditSigningBreakerOpenError,
        AuditSigningFailedError,
    )

    class _MalformedKms:
        algorithm = "ed25519"

        def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
            return b"short"  # 5 bytes, not the ed25519 64

        def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
            return True

    inner = _MalformedKms()
    clock = {"now": 0.0}
    guarded = BreakerGuardedSigningBackend(
        inner, fail_threshold=3, cooldown_seconds=30.0, monotonic=lambda: clock["now"]
    )

    for _ in range(3):
        with pytest.raises(AuditSigningFailedError, match="malformed"):
            guarded.sign(message=b"m", key_id="k", key_period=0)

    # Malformed responses COUNT toward the breaker: it is open now.
    with pytest.raises(AuditSigningBreakerOpenError):
        guarded.sign(message=b"m", key_id="k", key_period=0)
