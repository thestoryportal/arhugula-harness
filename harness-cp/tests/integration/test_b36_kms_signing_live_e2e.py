"""B-36 / ADR-D8 — live AWS KMS `SigningBackend` end-to-end proof.

Intentionally marked ``e2e`` and skip-gated on operator-provisioned AWS KMS
configuration (mirrors the R-830 live S3 e2e skip-gating convention). Exercises
a real `AwsKmsSigningBackend` against the real KMS key provisioned for B-36:
sign, verify, tamper-rejection, and (read-only) confirmation that the backend's
IAM identity is scoped to KMS on that one key only.

Required environment (see ``.env`` / ``just b36-kms-signing-live-e2e``):

- ``B36_KMS_KEY_ARN``: the provisioned KMS key ARN.
- ``B36_KMS_REGION``: AWS region the key lives in.
- ``B36_KMS_SIGNING_AWS_ACCESS`` / ``B36_KMS_SIGNING_AWS_SECRET``: the
  least-privilege IAM user's credentials (Sign/Verify/GetPublicKey/DescribeKey
  on this one key ARN only).
"""

from __future__ import annotations

import importlib.util
import os

import pytest


def _require_live_kms_params() -> dict[str, str]:
    if importlib.util.find_spec("boto3") is None:
        pytest.skip("B-36 live KMS e2e requires boto3; use `just b36-kms-signing-live-e2e`")

    key_arn = os.environ.get("B36_KMS_KEY_ARN", "").strip()
    if not key_arn:
        pytest.skip("B-36 live KMS e2e requires B36_KMS_KEY_ARN")

    params = {"key_arn": key_arn}
    for env_name, param_name in (
        ("B36_KMS_REGION", "region_name"),
        ("B36_KMS_SIGNING_AWS_ACCESS", "aws_access_key_id"),
        ("B36_KMS_SIGNING_AWS_SECRET", "aws_secret_access_key"),
    ):
        value = os.environ.get(env_name, "").strip()
        if not value:
            pytest.skip(f"B-36 live KMS e2e requires {env_name}")
        params[param_name] = value
    return params


@pytest.mark.e2e
def test_aws_kms_signing_backend_live_sign_verify_e2e() -> None:
    import boto3
    from harness_cp.aws_kms_signing_backend import AwsKmsSigningBackend, UnknownSigningKeyIdError

    params = _require_live_kms_params()
    key_id = "tenant_bound:b36-live-e2e"

    session = boto3.Session(
        aws_access_key_id=params["aws_access_key_id"],
        aws_secret_access_key=params["aws_secret_access_key"],
        region_name=params["region_name"],
    )
    kms_client = session.client("kms")
    backend = AwsKmsSigningBackend(key_arns={key_id: params["key_arn"]}, kms_client=kms_client)

    assert backend.algorithm == "ed25519"

    message = b"B-36 live e2e: real AwsKmsSigningBackend sign/verify round-trip"
    signature = backend.sign(message=message, key_id=key_id, key_period=1)
    assert len(signature) == 64, "Ed25519 raw signatures are always 64 bytes"

    assert backend.verify(message=message, signature=signature, key_id=key_id, key_period=1) is True

    tampered = bytes([signature[0] ^ 0xFF]) + signature[1:]
    assert backend.verify(message=message, signature=tampered, key_id=key_id, key_period=1) is False

    assert (
        backend.verify(
            message=b"different message", signature=signature, key_id=key_id, key_period=1
        )
        is False
    )

    with pytest.raises(UnknownSigningKeyIdError):
        backend.sign(message=message, key_id="workflow_bound:unmapped", key_period=1)


@pytest.mark.e2e
def test_aws_kms_signing_backend_live_identity_is_least_privilege() -> None:
    """Confirms the provisioned IAM identity cannot reach S3 or create IAM users —
    the ADR-D8 least-privilege scoping this backend's real credentials rely on."""
    import boto3
    from botocore.exceptions import ClientError

    params = _require_live_kms_params()
    session = boto3.Session(
        aws_access_key_id=params["aws_access_key_id"],
        aws_secret_access_key=params["aws_secret_access_key"],
        region_name=params["region_name"],
    )

    with pytest.raises(ClientError, match="AccessDenied"):
        session.client("s3").list_buckets()

    with pytest.raises(ClientError, match="AccessDenied"):
        session.client("iam").create_user(UserName="should-not-be-creatable-b36-e2e")
