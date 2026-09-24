"""Provider-free contract tests for the file-backed audit signer."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from harness_core import SigningBackendUnavailableError
from harness_runtime.config import local_ed25519_signing_backend as local_module
from harness_runtime.config.local_ed25519_signing_backend import (
    LocalEd25519SigningBackend,
    LocalSigningKeyConfigError,
    UnknownLocalSigningKeyIdError,
)


def _write_key(path: Path, key: ed25519.Ed25519PrivateKey | None = None) -> Path:
    key = key or ed25519.Ed25519PrivateKey.generate()
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    return path


def test_round_trip_tamper_wrong_key_and_unknown_id(tmp_path: Path) -> None:
    first = _write_key(tmp_path / "first.pem")
    second = _write_key(tmp_path / "second.pem")
    backend = LocalEd25519SigningBackend({"first": str(first), "second": str(second)})
    message = b"audit row"
    signature = backend.sign(message=message, key_id="first", key_period=1)
    assert backend.algorithm == "ed25519"
    assert len(signature) == 64
    assert backend.verify(message=message, signature=signature, key_id="first", key_period=1)
    assert not backend.verify(message=b"altered", signature=signature, key_id="first", key_period=1)
    assert not backend.verify(
        message=message,
        signature=signature[:-1] + bytes([signature[-1] ^ 1]),
        key_id="first",
        key_period=1,
    )
    assert not backend.verify(message=message, signature=signature, key_id="second", key_period=1)
    assert not backend.verify(message=message, signature=b"short", key_id="first", key_period=1)
    with pytest.raises(UnknownLocalSigningKeyIdError) as excinfo:
        backend.sign(message=message, key_id="missing", key_period=1)
    assert isinstance(excinfo.value, SigningBackendUnavailableError)
    with pytest.raises(UnknownLocalSigningKeyIdError):
        backend.verify(message=message, signature=signature, key_id="missing", key_period=1)


def test_reload_from_same_file_verifies_prior_signature(tmp_path: Path) -> None:
    path = _write_key(tmp_path / "key.pem")
    first = LocalEd25519SigningBackend({"k": str(path)})
    signature = first.sign(message=b"before restart", key_id="k", key_period=0)
    del first
    restarted = LocalEd25519SigningBackend({"k": str(path)})
    assert restarted.verify(
        message=b"before restart", signature=signature, key_id="k", key_period=0
    )


@pytest.mark.parametrize("mode", [0o000, 0o400, 0o604, 0o620, 0o640, 0o660, 0o601])
def test_rejects_unreadable_or_shared_permissions(tmp_path: Path, mode: int) -> None:
    path = _write_key(tmp_path / "key.pem")
    path.chmod(mode)
    if mode == 0o400:
        LocalEd25519SigningBackend({"k": str(path)})
    else:
        # Mode 000 is refused by open(2) before the fd permission check runs.
        with pytest.raises(LocalSigningKeyConfigError):
            LocalEd25519SigningBackend({"k": str(path)})


def test_rejects_missing_directory_symlink_and_relative_path(tmp_path: Path) -> None:
    path = _write_key(tmp_path / "key.pem")
    link = tmp_path / "link.pem"
    link.symlink_to(path)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(tmp_path, target_is_directory=True)
    for bad in (
        tmp_path / "missing.pem",
        tmp_path,
        link,
        linked_parent / "key.pem",
        Path("relative.pem"),
        Path("/"),
    ):
        with pytest.raises(LocalSigningKeyConfigError):
            LocalEd25519SigningBackend({"k": str(bad)})


def test_rejects_wrong_owner_without_reading_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _write_key(tmp_path / "key.pem")
    monkeypatch.setattr(local_module.os, "geteuid", lambda: os.stat(path).st_uid + 1)
    with pytest.raises(LocalSigningKeyConfigError, match="owner"):
        LocalEd25519SigningBackend({"k": str(path)})


def test_rejects_non_ed25519_and_malformed_key(tmp_path: Path) -> None:
    rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    path = tmp_path / "rsa.pem"
    path.write_bytes(
        rsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    with pytest.raises(LocalSigningKeyConfigError, match="Ed25519"):
        LocalEd25519SigningBackend({"k": str(path)})
    path.write_bytes(b"not a PEM key")
    with pytest.raises(LocalSigningKeyConfigError, match="PKCS#8"):
        LocalEd25519SigningBackend({"k": str(path)})


def test_key_identity_uses_loaded_public_spki_and_unknown_id(tmp_path: Path) -> None:
    import hashlib

    key = ed25519.Ed25519PrivateKey.generate()
    path = _write_key(tmp_path / "key.pem", key)
    backend = LocalEd25519SigningBackend({"a": str(path)})
    spki = key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    expected = f"ed25519-spki-sha256:{hashlib.sha256(spki).hexdigest()}"
    path.unlink()  # identity must come from the key already loaded, without reopening
    assert backend.key_identity("a") == expected
    with pytest.raises(UnknownLocalSigningKeyIdError):
        backend.key_identity("missing")
