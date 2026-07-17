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

from importlib import import_module
from typing import TYPE_CHECKING, Any

from harness_cp.aws_kms_signing_backend import AwsKmsSigningBackend

from harness_runtime.types import AuditSigningBackendKind, AuditSigningConfig

if TYPE_CHECKING:
    from harness_cp.f5_signing_key_resolution import SigningBackend

__all__ = [
    "SigningBackendUnavailableError",
    "make_audit_signing_backend",
]


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
    return AwsKmsSigningBackend(key_arns=config.key_arns, kms_client=client)
