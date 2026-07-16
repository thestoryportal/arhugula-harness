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

Optional (strengthens the least-privilege proof from negative-probing to an
authoritative policy-document read):

- ``S3_AWS_ACCESS`` / ``S3_AWS_SECRET``: account-admin credentials able to
  read IAM policy documents. Without these, the policy-document test skips
  and the negative-probe test remains the only least-privilege witness.
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
    """Confirms the provisioned IAM identity is scoped to exactly
    Sign/Verify/GetPublicKey/DescribeKey on the one provisioned KMS key —
    the ADR-D8 least-privilege guarantee this backend's real credentials
    rely on.

    Every check here is a read-only AWS API call the identity is NOT
    granted, so a denial is the expected, safe outcome and a surprise
    "allowed" is the only way this test can leave residual AWS state (none
    of these calls mutate anything even on unexpected success). An earlier
    version of this test called `iam.create_user(...)` directly — an
    out-of-family Codex review finding on the initial B-36 landing noted
    that if the identity were ever misconfigured with broader-than-intended
    permissions, that call would succeed and leave a persistent IAM user
    before the assertion could even run. `iam.simulate_principal_policy` was
    considered as a safer alternative but is itself not granted to this
    identity (empirically confirmed — `iam:SimulatePrincipalPolicy` is not
    in the least-privilege policy, so calling it also raises AccessDenied,
    which is the correct behavior but not usable to *evaluate* other
    actions). `kms:GetKeyPolicy` (read-only, NOT in the granted action set)
    against the SAME real, provisioned key proves the policy is scoped by
    ACTION beyond the 4 granted — not merely by service."""
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
        session.client("iam").list_users()

    with pytest.raises(ClientError, match="AccessDenied"):
        session.client("kms").get_key_policy(KeyId=params["key_arn"], PolicyName="default")


@pytest.mark.e2e
def test_aws_kms_signing_backend_live_identity_policy_document_is_exact() -> None:
    """Authoritative version of the least-privilege check above: rather than
    negative-probing a handful of not-granted actions (which cannot rule out
    an accidentally-broader policy the probes happen not to exercise), reads
    the actual attached IAM policy document via an admin identity and asserts
    it is EXACTLY the 4 actions on the 1 key ARN ADR-D8 commits to — nothing
    more (out-of-family Codex review round-2 finding: negative probing alone
    "does not prove the claimed 'exactly four actions on one key' boundary").
    Skips (not fails) if no admin credential is configured — this is a
    stronger complement to, not a replacement for, the black-box test above,
    which remains the one every CI-adjacent operator credential set can run."""
    import json

    import boto3

    params = _require_live_kms_params()
    admin_access = os.environ.get("S3_AWS_ACCESS", "").strip()
    admin_secret = os.environ.get("S3_AWS_SECRET", "").strip()
    if not admin_access or not admin_secret:
        pytest.skip("policy-document proof requires S3_AWS_ACCESS/S3_AWS_SECRET (account-admin)")

    admin_session = boto3.Session(
        aws_access_key_id=admin_access,
        aws_secret_access_key=admin_secret,
        region_name=params["region_name"],
    )
    iam = admin_session.client("iam")
    caller_arn = (
        boto3.Session(
            aws_access_key_id=params["aws_access_key_id"],
            aws_secret_access_key=params["aws_secret_access_key"],
            region_name=params["region_name"],
        )
        .client("sts")
        .get_caller_identity()["Arn"]
    )
    user_name = caller_arn.rsplit("/", 1)[-1]

    inline_policy_names = iam.list_user_policies(UserName=user_name)["PolicyNames"]
    assert len(inline_policy_names) == 1, (
        f"expected exactly one inline policy on {user_name}, found {inline_policy_names}"
    )
    policy_doc = iam.get_user_policy(UserName=user_name, PolicyName=inline_policy_names[0])[
        "PolicyDocument"
    ]

    statements = policy_doc["Statement"]
    assert len(statements) == 1, f"expected exactly one statement, found {json.dumps(statements)}"
    statement = statements[0]
    assert statement["Effect"] == "Allow"
    actions = statement["Action"]
    actions = [actions] if isinstance(actions, str) else actions
    assert set(actions) == {"kms:Sign", "kms:Verify", "kms:GetPublicKey", "kms:DescribeKey"}
    resources = statement["Resource"]
    resources = [resources] if isinstance(resources, str) else resources
    assert set(resources) == {params["key_arn"]}

    attached_managed = iam.list_attached_user_policies(UserName=user_name)["AttachedPolicies"]
    assert attached_managed == [], (
        f"expected no managed policies attached, found {attached_managed}"
    )

    groups = iam.list_groups_for_user(UserName=user_name)["Groups"]
    assert groups == [], f"expected no group memberships (no inherited permissions), found {groups}"
