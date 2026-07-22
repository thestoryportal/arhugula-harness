"""Tests for `AwsKmsSigningBackend` — B-36 / ADR-D8.

No live AWS calls. `_FakeKmsClient` below is a TEST-ONLY double that performs
real Ed25519 cryptography (via the `cryptography` library, already a root
dev dependency for the `_InMemoryEd25519Backend` test double at
`test_f5_signing_key_resolution.py`) behind the same request/response shape
AWS KMS's `Sign` / `Verify` APIs use — proving the backend's message/response
plumbing is correct, not merely that mocked methods were called.

The real, credential-gated, live-AWS-KMS proof lives at
`harness-cp/tests/integration/test_b36_kms_signing_live_e2e.py`.
"""

from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness_cp.aws_kms_signing_backend import (
    AwsKmsSigningBackend,
    MutableKeyAliasRejectedError,
    UnknownSigningKeyIdError,
)

_KEY_ID = "tenant_bound:acme-corp"
_KEY_ARN = "arn:aws:kms:us-east-1:123456789012:key/test-fixture-key-id"


from botocore.exceptions import ClientError as _BotoClientError


class _KMSInvalidSignatureException(_BotoClientError):
    """Mirrors the botocore-generated exception class at `client.exceptions`.

    Subclasses the REAL `botocore.exceptions.ClientError` — as the generated
    modeled exceptions on a real client do — so the backend's catch ORDER is
    pinned by the unit suite (merge-gate test-witness lens, PR #1073): with a
    plain-`Exception` fake, reordering the `(BotoCoreError, ClientError)`
    availability catch BEFORE the mismatch catch would pass every unit test
    while reclassifying real-client signature mismatches as availability."""

    def __init__(self) -> None:
        super().__init__(
            {"Error": {"Code": "KMSInvalidSignatureException", "Message": "invalid"}},
            "Verify",
        )


class _FakeKmsExceptions:
    KMSInvalidSignatureException = _KMSInvalidSignatureException


class _FakeKmsClient:
    """TEST-ONLY double standing in for a real `boto3.client("kms")`.

    Performs genuine Ed25519 sign/verify so these tests exercise real
    cryptographic round-tripping through `AwsKmsSigningBackend`'s
    request/response plumbing, not just mock call-recording.
    """

    exceptions = _FakeKmsExceptions()

    def __init__(self) -> None:
        self._private_key = Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        self.sign_calls: list[dict[str, object]] = []
        self.verify_calls: list[dict[str, object]] = []

    def sign(self, **kwargs: object) -> dict[str, bytes]:
        self.sign_calls.append(kwargs)
        assert kwargs["KeyId"] == _KEY_ARN
        assert kwargs["MessageType"] == "RAW"
        assert kwargs["SigningAlgorithm"] == "ED25519_SHA_512"
        message = kwargs["Message"]
        assert isinstance(message, bytes)
        return {"Signature": self._private_key.sign(message)}

    def verify(self, **kwargs: object) -> dict[str, bool]:
        self.verify_calls.append(kwargs)
        assert kwargs["KeyId"] == _KEY_ARN
        assert kwargs["MessageType"] == "RAW"
        assert kwargs["SigningAlgorithm"] == "ED25519_SHA_512"
        message = kwargs["Message"]
        signature = kwargs["Signature"]
        assert isinstance(message, bytes)
        assert isinstance(signature, bytes)
        try:
            self._public_key.verify(signature, message)
        except InvalidSignature as exc:
            raise _KMSInvalidSignatureException() from exc
        return {"SignatureValid": True}


def _backend(client: _FakeKmsClient) -> AwsKmsSigningBackend:
    return AwsKmsSigningBackend(key_arns={_KEY_ID: _KEY_ARN}, kms_client=client)


def test_algorithm_is_ed25519() -> None:
    assert AwsKmsSigningBackend(key_arns={}, kms_client=_FakeKmsClient()).algorithm == "ed25519"


def test_sign_then_verify_round_trips() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)
    message = b"a canonical signing message"

    signature = backend.sign(message=message, key_id=_KEY_ID, key_period=1)

    assert backend.verify(message=message, signature=signature, key_id=_KEY_ID, key_period=1)


def test_sign_calls_kms_with_correct_request_shape() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)

    backend.sign(message=b"msg", key_id=_KEY_ID, key_period=7)

    assert len(client.sign_calls) == 1
    assert client.sign_calls[0]["KeyId"] == _KEY_ARN


def test_verify_rejects_tampered_signature() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)
    message = b"a canonical signing message"
    signature = backend.sign(message=message, key_id=_KEY_ID, key_period=1)
    tampered = bytes([signature[0] ^ 0xFF]) + signature[1:]

    assert (
        backend.verify(message=message, signature=tampered, key_id=_KEY_ID, key_period=1) is False
    )


def test_verify_rejects_wrong_message() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)
    signature = backend.sign(message=b"original", key_id=_KEY_ID, key_period=1)

    assert (
        backend.verify(message=b"different", signature=signature, key_id=_KEY_ID, key_period=1)
        is False
    )


def test_sign_unknown_key_id_raises_without_calling_kms() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)

    with pytest.raises(UnknownSigningKeyIdError, match="unmapped-key"):
        backend.sign(message=b"msg", key_id="unmapped-key", key_period=1)

    assert client.sign_calls == []


def test_verify_unknown_key_id_raises_without_calling_kms() -> None:
    client = _FakeKmsClient()
    backend = _backend(client)

    with pytest.raises(UnknownSigningKeyIdError, match="unmapped-key"):
        backend.verify(message=b"msg", signature=b"sig", key_id="unmapped-key", key_period=1)

    assert client.verify_calls == []


def test_key_period_is_accepted_but_does_not_affect_key_selection() -> None:
    """Single-physical-key-per-key_id scope (ADR-D8 §Decision item 2, B-33 residual)."""
    client = _FakeKmsClient()
    backend = _backend(client)
    message = b"msg"
    signature = backend.sign(message=message, key_id=_KEY_ID, key_period=1)

    assert backend.verify(message=message, signature=signature, key_id=_KEY_ID, key_period=999)


@pytest.mark.parametrize(
    "alias_value",
    [
        "alias/audit-signing",
        "arn:aws:kms:us-east-1:123456789012:alias/audit-signing",
    ],
)
def test_construction_rejects_kms_alias(alias_value: str) -> None:
    """Out-of-family Codex finding: aliases are mutable and would let a
    repointed alias silently swap key material under an already-used
    logical `key_id` — rejected at construction, not merely documented."""
    with pytest.raises(MutableKeyAliasRejectedError, match=_KEY_ID):
        AwsKmsSigningBackend(key_arns={_KEY_ID: alias_value}, kms_client=_FakeKmsClient())


# ---------------------------------------------------------------------------
# B-63 — verify() infra failures are typed availability, defects unwrapped.
# ---------------------------------------------------------------------------


def _availability_raising_client(exc: BaseException) -> _FakeKmsClient:
    client = _FakeKmsClient()

    def _raising_verify(**_kwargs: object) -> dict[str, bool]:
        raise exc

    client.verify = _raising_verify  # type: ignore[method-assign]
    return client


def test_b63_verify_boto_client_error_raises_typed_availability() -> None:
    """A boto `ClientError` from the Verify call (throttling / missing IAM
    Verify permission / service 5xx) is INFRASTRUCTURE — typed as the shared
    `SigningBackendUnavailableError` with the vendor exception chained,
    never a `False` verdict and never a raw vendor leak (OD v1.34 §21.2.2
    row 7(b); B-63)."""
    from botocore.exceptions import ClientError
    from harness_core import SigningBackendUnavailableError

    vendor_exc = ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "rate exceeded"}}, "Verify"
    )
    backend = AwsKmsSigningBackend({_KEY_ID: _KEY_ARN}, _availability_raising_client(vendor_exc))
    with pytest.raises(SigningBackendUnavailableError) as excinfo:
        backend.verify(message=b"m", signature=b"s" * 64, key_id=_KEY_ID, key_period=1)
    assert excinfo.value.__cause__ is vendor_exc


def test_b63_verify_botocore_error_raises_typed_availability() -> None:
    """A `BotoCoreError` (network/endpoint/credential resolution) is equally
    availability-classed."""
    from botocore.exceptions import EndpointConnectionError
    from harness_core import SigningBackendUnavailableError

    vendor_exc = EndpointConnectionError(endpoint_url="https://kms.test")
    backend = AwsKmsSigningBackend({_KEY_ID: _KEY_ARN}, _availability_raising_client(vendor_exc))
    with pytest.raises(SigningBackendUnavailableError):
        backend.verify(message=b"m", signature=b"s" * 64, key_id=_KEY_ID, key_period=1)


def test_b63_verify_non_boto_raise_propagates_unwrapped_as_defect() -> None:
    """A non-boto raise (a programming defect, e.g. `TypeError`) is NOT
    availability — it propagates unwrapped per the same spec row ("raises
    that are NOT the typed availability error ... are DEFECTS")."""
    from harness_core import SigningBackendUnavailableError

    backend = AwsKmsSigningBackend(
        {_KEY_ID: _KEY_ARN}, _availability_raising_client(TypeError("defect"))
    )
    with pytest.raises(TypeError):
        backend.verify(message=b"m", signature=b"s" * 64, key_id=_KEY_ID, key_period=1)
    # And the defect is NOT catchable as availability (taxonomy separation).
    try:
        backend.verify(message=b"m", signature=b"s" * 64, key_id=_KEY_ID, key_period=1)
    except SigningBackendUnavailableError:  # pragma: no cover - failure branch
        pytest.fail("a programming defect was misclassified as availability")
    except TypeError:
        pass


def test_b63_invalid_signature_exception_still_means_false_not_availability() -> None:
    """The modeled mismatch exception keeps meaning `False` — the
    availability catch must not swallow it (it is caught FIRST)."""
    backend = AwsKmsSigningBackend({_KEY_ID: _KEY_ARN}, _FakeKmsClient())
    signature = backend.sign(message=b"message", key_id=_KEY_ID, key_period=1)
    assert (
        backend.verify(message=b"TAMPERED", signature=signature, key_id=_KEY_ID, key_period=1)
        is False
    )


def test_b63_unknown_key_id_is_catchable_as_shared_availability_type() -> None:
    """The register row's concrete instance: an unmapped `key_id` is
    availability by spec text — `UnknownSigningKeyIdError` is catchable as
    BOTH the shared `SigningBackendUnavailableError` AND the pre-B-63
    `KeyError` base (existing callers keep working)."""
    from harness_core import SigningBackendUnavailableError

    backend = AwsKmsSigningBackend({_KEY_ID: _KEY_ARN}, _FakeKmsClient())
    with pytest.raises(SigningBackendUnavailableError):
        backend.verify(message=b"m", signature=b"s" * 64, key_id="unmapped", key_period=1)
    with pytest.raises(KeyError):
        backend.sign(message=b"m", key_id="unmapped", key_period=1)
