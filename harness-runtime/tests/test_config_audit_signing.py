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
    SigningBackendUnavailableError,
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
    assert isinstance(backend, AwsKmsSigningBackend)
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
    with pytest.raises(SigningBackendUnavailableError, match="boto3"):
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
