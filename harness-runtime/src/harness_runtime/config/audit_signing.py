"""Audit-signing backend composition-root factory — `B-47` PR B (ADR-D8).

Constructs the concrete `SigningBackend` a deployment selected via
`RuntimeConfig.audit_signing` (OD spec v1.33 §21.2.1's injection seam expects
the composition root — this module — to own backend selection, client
construction, and credential sourcing; the seam itself never reads config).

Mirrors the R-421 `make_provider_secret_resolver` shape at
`config/provider_secrets.py`: a config-`backend`-dispatch factory with an
injectable client seam for hermetic tests, and an import-guarded vendor SDK
(`boto3` here, `google.cloud.secretmanager` there) that fails loud with a
typed error when the selected backend's SDK is absent — never a silent
fallback to the placeholder signing path (workspace `CLAUDE.md` §6
no-silent-failure).

Credential posture per ADR-D8 §Consequences: the boto3 KMS client uses
boto3's OWN credential-resolution chain (env / shared config / instance
role) — this factory never reads, relocates, or embeds credentials, and the
least-privilege IAM identity provisioned at B-36
(`arhugula-harness-cp-signing`, scoped to one key ARN) is the pattern a
deployment should extend.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from importlib import import_module
from typing import TYPE_CHECKING, Any, Final

from harness_as.secret_fail_class import SecretBackendBreakerKey, construct_breaker_key
from harness_as.secret_fetch import SecretScope
from harness_cp.aws_kms_signing_backend import AwsKmsSigningBackend

from harness_runtime.types import AuditSigningBackendKind, AuditSigningConfig

if TYPE_CHECKING:
    from harness_cp.f5_signing_key_resolution import SigningBackend

__all__ = [
    "AuditSigningBreakerOpenError",
    "BreakerGuardedSigningBackend",
    "SigningBackendUnavailableError",
    "make_audit_signing_backend",
]

#: Breaker trip threshold / cooldown — mirror the runtime reliability
#: breaker's bootstrap defaults (`retry_breaker.DEFAULT_FAIL_THRESHOLD` /
#: `DEFAULT_COOLDOWN_SECONDS`) so signing availability degrades on the same
#: operator-familiar policy curve as provider dispatch.
SIGNING_BREAKER_FAIL_THRESHOLD: Final[int] = 5
SIGNING_BREAKER_COOLDOWN_SECONDS: Final[float] = 30.0

#: C9 per-{secret_backend, scope} breaker key (C-AS-07 §7.1/§7.3 — the
#: previously key-type-only scaffolding at `harness_as.secret_fail_class`,
#: wired here per ADR-D8 §Decision item 5: "The signing call — not merely
#: `resolve_signing_key`'s key-resolution step — should be wired through the
#: existing per-`{secret_backend, scope}` C9 breaker discipline ... at the
#: deployment-time composition-root arc").
AWS_KMS_SIGNING_BREAKER_KEY: Final[SecretBackendBreakerKey] = construct_breaker_key(
    "aws-kms", SecretScope(name="audit-signing")
)


class AuditSigningBreakerOpenError(RuntimeError):
    """The audit-signing breaker is OPEN — signing fails fast, never silently.

    Raised INSTEAD of invoking the wrapped backend while the breaker is open
    (or while another thread's half-open probe is in flight). Audit signing
    is a compliance guarantee, so an unavailable KMS must fail the audit
    write loudly and quickly — degrading to placeholder signatures is
    forbidden (ADR-D8 / OD spec v1.33 §21.2.1 never-silently-degrade), and
    hammering a down KMS from every span-end thread would stall the entire
    hot path on network timeouts.
    """


class BreakerGuardedSigningBackend:
    """C9 per-{secret_backend, scope} breaker on the signing call itself.

    ADR-D8 §Decision item 5 assigns THIS composition root the wiring: "AWS
    KMS availability now sits on the audit-write hot path." Hand-rolled per
    the `Plan_Executability_Audit_v1.md` framework-pull discipline, mirroring
    `retry_breaker.BreakerStateMachine`'s closed → open → half-open shape
    (that machine is keyed on the OD `BreakerScope` PER_MODEL/PER_PROVIDER
    enum and consulted-not-raising — the wrong carrier for a secret-backend
    scope, so this wrapper keys on the C-AS-07 §7.1 `SecretBackendBreakerKey`
    and raises, which the signing call sites' fail-loud posture requires).

    Semantics: `fail_threshold` CONSECUTIVE `sign` failures open the breaker;
    while open, `sign` raises `AuditSigningBreakerOpenError` without touching
    the backend; after `cooldown_seconds` ONE probe call is admitted
    (half-open) — success closes, failure re-opens the cooldown window.
    `verify` passes through unguarded: ADR-D8 scopes the breaker to "the
    signing call" (the write-time hot path); verifiers want the real error.

    Thread-safe (span-end worker threads + dispatch paths sign concurrently):
    state transitions under a lock, the backend call itself outside it.
    """

    def __init__(
        self,
        inner: SigningBackend,
        *,
        breaker_key: SecretBackendBreakerKey = AWS_KMS_SIGNING_BREAKER_KEY,
        fail_threshold: int = SIGNING_BREAKER_FAIL_THRESHOLD,
        cooldown_seconds: float = SIGNING_BREAKER_COOLDOWN_SECONDS,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._inner = inner
        # Plain attribute (not a property): the §20.2.1 Protocol declares
        # `algorithm: str` as a mutable attribute, which a read-only property
        # does not structurally satisfy under pyright strict.
        self.algorithm = inner.algorithm
        self.breaker_key = breaker_key
        self._fail_threshold = fail_threshold
        self._cooldown_seconds = cooldown_seconds
        self._monotonic = monotonic
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._half_open_probe_inflight = False
        # Epoch guard (codex round-1 P1 on PR B2a): bumped on every OPEN /
        # CLOSE transition. A slow call admitted while CLOSED can finish
        # AFTER other calls opened the breaker — its stale outcome must not
        # mutate the newer state (an unconditional _record_success would
        # instantly close a just-opened breaker; a stale failure would
        # double-count into the new window).
        self._epoch = 0

    def _admit_or_raise(self) -> tuple[bool, int]:
        """Under the lock: admit this call and return
        `(is_half_open_probe, admission_epoch)`; raise when the breaker
        refuses admission."""
        with self._lock:
            if self._opened_at is None:
                return False, self._epoch
            elapsed = self._monotonic() - self._opened_at
            if elapsed < self._cooldown_seconds or self._half_open_probe_inflight:
                raise AuditSigningBreakerOpenError(
                    f"audit-signing breaker OPEN for "
                    f"{self.breaker_key.secret_backend}/"
                    f"{self.breaker_key.scope.name} after "
                    f"{self._consecutive_failures} consecutive signing "
                    f"failures — failing fast for "
                    f"{max(0.0, self._cooldown_seconds - elapsed):.1f}s more "
                    f"rather than degrading to placeholder signatures or "
                    f"stalling the audit hot path on a down KMS"
                )
            self._half_open_probe_inflight = True
            return True, self._epoch

    def _record_success(self, *, admission_epoch: int) -> None:
        with self._lock:
            if admission_epoch != self._epoch:
                # Stale outcome from before the last state transition —
                # a pre-open success must not close an OPEN breaker.
                return
            transitioning = self._opened_at is not None
            self._consecutive_failures = 0
            self._opened_at = None
            self._half_open_probe_inflight = False
            if transitioning:
                self._epoch += 1

    def _record_failure(self, *, was_probe: bool, admission_epoch: int) -> None:
        with self._lock:
            if admission_epoch != self._epoch:
                return
            self._consecutive_failures += 1
            if was_probe or self._consecutive_failures >= self._fail_threshold:
                transitioning = self._opened_at is None or was_probe
                self._opened_at = self._monotonic()
                if transitioning:
                    self._epoch += 1
            self._half_open_probe_inflight = False

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        was_probe, admission_epoch = self._admit_or_raise()
        try:
            signature = self._inner.sign(message=message, key_id=key_id, key_period=key_period)
        except Exception:
            self._record_failure(was_probe=was_probe, admission_epoch=admission_epoch)
            raise
        self._record_success(admission_epoch=admission_epoch)
        return signature

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        return self._inner.verify(
            message=message, signature=signature, key_id=key_id, key_period=key_period
        )


class SigningBackendUnavailableError(RuntimeError):
    """The selected audit-signing backend cannot be constructed.

    Raised when the configured backend's vendor SDK is not importable
    (e.g. `boto3` absent for `aws-kms`). Fails loud at bootstrap rather than
    letting a deployment that explicitly configured real signing silently
    degrade to placeholder signatures.
    """


def _default_kms_client(region: str | None) -> Any:
    """Construct a boto3 KMS client — import-guarded (mirrors R-421's
    `_default_gcp_secret_accessor`)."""
    try:
        boto3 = import_module("boto3")
    except ModuleNotFoundError as exc:
        raise SigningBackendUnavailableError(
            "audit_signing.backend is 'aws-kms' but boto3 is not installed — "
            "install the aws extra or set audit_signing.backend to 'none' "
            "(placeholder signing); real signing is never silently skipped"
        ) from exc
    if region is not None:
        return boto3.client("kms", region_name=region)
    return boto3.client("kms")


def make_audit_signing_backend(
    config: AuditSigningConfig,
    *,
    kms_client: Any | None = None,
) -> SigningBackend | None:
    """Construct the deployment-selected `SigningBackend`, or `None`.

    `None` (for `backend = "none"`, the default) means every downstream
    signing surface keeps the placeholder path byte-for-byte — the OD spec
    v1.33 §21.2.1 absent-backend contract. For `aws-kms`, constructs ADR-D8's
    `AwsKmsSigningBackend` over the config's `key_id → KMS key ARN` mapping;
    a KMS *alias* in the mapping fails loud at construction
    (`MutableKeyAliasRejectedError`), and a missing `boto3` fails loud
    (`SigningBackendUnavailableError`) — a deployment that asked for real
    signing never silently degrades.

    `kms_client` is the hermetic-test injection seam (mirrors R-421's
    `gcp_secret_accessor` parameter); production callers omit it and get the
    import-guarded boto3 client with boto3's own credential chain.
    """
    if config.backend is AuditSigningBackendKind.NONE:
        return None
    client = kms_client if kms_client is not None else _default_kms_client(config.aws_region)
    # B-47 PR B2a — item (d): every consumer that receives this backend
    # (span-processor token map, HITL/sub-agent composers, cost builders)
    # gets the C9 breaker transparently by wrapping HERE, at the single
    # construction point, per ADR-D8 §Decision item 5.
    return BreakerGuardedSigningBackend(
        AwsKmsSigningBackend(key_arns=config.key_arns, kms_client=client)
    )
