"""AWS KMS `SigningBackend` — B-36 / ADR-D8.

Implements the C-CP-20 §20.2.1 `SigningBackend` Protocol via AWS KMS
delegated signing (key spec `ECC_NIST_EDWARDS25519`, signing algorithm
`ED25519_SHA_512`) — see `design-substrate/ADR-D8_audit_signing_backend.md`
for the concrete-backend-selection rationale (council-grounded: the private
key never leaves the AWS KMS HSM boundary; `sign()` / `verify()` are network
calls against KMS's `Sign` / `Verify` APIs, not local cryptographic
operations against locally-resolved key material).

Scoped to a single-physical-key-per-logical-`key_id` mapping supplied at
construction by the deployment-time composition root (ADR-D8 §Decision item
2) — multi-key fleet routing across distinct `WORKFLOW_BOUND` /
`TENANT_BOUND` / `FLEET_BOUND` scopes and rotation-boundary key-period
selection (`B-33`) are out of scope here; an unmapped `key_id` fails loud
rather than silently falling back to a default key.

This module carries the workspace's only `boto3` dependency in `harness-cp`
(CLAUDE.md §3.2 framework-pull discipline — this is a per-provider official
SDK for a concrete backend selection, not a banned orchestration framework).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


class UnknownSigningKeyIdError(KeyError):
    """`key_id` has no entry in this backend's `key_id -> KMS key ARN` mapping.

    Fails loud rather than silently signing under a default/wrong key
    (ADR-D8 §Decision item 2).
    """


class MutableKeyAliasRejectedError(ValueError):
    """A `key_arns` value names a KMS *alias* rather than a physical key ARN/ID.

    Aliases are mutable — repointing one to a different physical key would
    make this backend silently sign/verify under different key material for
    the *same* logical `key_id`, and (since `key_period` is not yet used for
    key selection, see module docstring) undetectably invalidate the
    identity guarantee the signing key exists to provide. Rejected at
    construction (out-of-family Codex review finding on the initial B-36
    landing) rather than left as a latent correctness hazard."""


def _is_kms_alias(value: str) -> bool:
    """True if `value` is a KMS alias name/ARN rather than a key ARN/ID.

    KMS key ARNs/IDs never contain the literal `alias/` segment; alias ARNs
    are shaped `arn:...:alias/<name>` and bare alias names are `alias/<name>`.
    """
    return value.startswith("alias/") or ":alias/" in value


class AwsKmsSigningBackend:
    """A `C-CP-20 §20.2.1` `SigningBackend` backed by AWS KMS delegated signing.

    `algorithm` is fixed at `"ed25519"` — this backend only supports
    `ECC_NIST_EDWARDS25519` KMS keys. Both `sign()` and `verify()` call the
    KMS API directly rather than caching/verifying against a locally-fetched
    public key, keeping every cryptographic operation behind the KMS
    boundary on a single, auditable code path.

    `key_period` is accepted (per the Protocol shape — a rotation-aware
    backend needs it) but not yet used for key selection; this backend
    manages exactly the keys named in its `key_arns` mapping, one physical
    KMS key per logical `key_id`. Rotation-boundary-aware key-period
    selection is `B-33`'s scope.
    """

    algorithm: str = "ed25519"

    def __init__(self, key_arns: Mapping[str, str], kms_client: Any) -> None:
        """`key_arns` maps a CP-axis logical `key_id` (e.g. `"tenant_bound:acme-corp"`,
        the shape `resolve_signing_key` produces) to the physical AWS KMS key
        ARN or key ID the deployment-time composition root provisioned for it
        — a KMS *alias* is rejected (`MutableKeyAliasRejectedError`), since
        aliases are mutable and would silently repoint an already-used
        logical `key_id` to different key material. `kms_client` is a
        `boto3` KMS client (e.g. `boto3.client("kms")`) — accepted as a
        constructor parameter rather than constructed internally so the
        composition root owns session/credential/region configuration.
        """
        for key_id, value in key_arns.items():
            if _is_kms_alias(value):
                raise MutableKeyAliasRejectedError(
                    f"key_arns[{key_id!r}]={value!r} is a KMS alias, not a physical "
                    f"key ARN/ID — aliases are mutable and must not be used as a "
                    f"signing key's stable identity (see MutableKeyAliasRejectedError)"
                )
        self._key_arns = dict(key_arns)
        self._kms = kms_client

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_period  # single-physical-key-per-key_id scope; see module docstring
        key_arn = self._resolve_key_arn(key_id)
        response = self._kms.sign(
            KeyId=key_arn,
            Message=message,
            MessageType="RAW",
            SigningAlgorithm="ED25519_SHA_512",
        )
        return response["Signature"]

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_period
        key_arn = self._resolve_key_arn(key_id)
        # AWS KMS's own service-model documentation for the `Verify` operation's
        # `SignatureValid` output member: "If the signature is not verified, the
        # `Verify` operation fails with a `KMSInvalidSignatureException` exception."
        # (botocore kms service model, confirmed via `get_service_model("kms")
        # .operation_model("Verify").output_shape.members["SignatureValid"]
        # .documentation` — not merely an empirical single observation) — a
        # successful response's `SignatureValid` is therefore always `True`.
        try:
            response = self._kms.verify(
                KeyId=key_arn,
                Message=message,
                Signature=signature,
                MessageType="RAW",
                SigningAlgorithm="ED25519_SHA_512",
            )
        except self._kms.exceptions.KMSInvalidSignatureException:
            return False
        return response["SignatureValid"]

    def _resolve_key_arn(self, key_id: str) -> str:
        try:
            return self._key_arns[key_id]
        except KeyError as exc:
            raise UnknownSigningKeyIdError(
                f"no KMS key ARN mapped for key_id={key_id!r}; the deployment-time "
                f"composition root must supply an explicit key_id -> KMS key ARN "
                f"mapping (ADR-D8 §Decision item 2) — no default key is assumed"
            ) from exc
