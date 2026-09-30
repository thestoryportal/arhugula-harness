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


def _write_public(path: Path, private_path: Path) -> Path:
    key = serialization.load_pem_private_key(private_path.read_bytes(), password=None)
    assert isinstance(key, ed25519.Ed25519PrivateKey)
    path.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    path.chmod(0o644)
    return path


def test_historical_public_identity_is_resolvable_but_cannot_sign(tmp_path: Path) -> None:
    active = _write_key(tmp_path / "active.pem")
    retired = _write_key(tmp_path / "retired.pem")
    public = _write_public(tmp_path / "retired.pub", retired)
    backend = LocalEd25519SigningBackend({"active": str(active)}, {"retired": str(public)})
    assert backend.row_key_identity("active") == backend.key_identity("active")
    assert backend.row_key_identity("retired") is not None
    assert backend.row_key_identity("missing") is None
    with pytest.raises(UnknownLocalSigningKeyIdError):
        backend.sign(message=b"row", key_id="retired", key_period=0)
    with pytest.raises(UnknownLocalSigningKeyIdError):
        backend.verify(message=b"row", signature=b"x" * 64, key_id="retired", key_period=0)


def test_public_loader_rejects_unsafe_paths_and_mismatched_active_id(tmp_path: Path) -> None:
    active = _write_key(tmp_path / "active.pem")
    other = _write_key(tmp_path / "other.pem")
    public = _write_public(tmp_path / "public.pem", other)
    with pytest.raises(LocalSigningKeyConfigError, match="match"):
        LocalEd25519SigningBackend({"active": str(active)}, {"active": str(public)})
    for mode in (0o622, 0o666, 0o000):
        public.chmod(mode)
        with pytest.raises(LocalSigningKeyConfigError):
            LocalEd25519SigningBackend({"active": str(active)}, {"retired": str(public)})
    public.chmod(0o644)
    link = tmp_path / "link.pub"
    link.symlink_to(public)
    with pytest.raises(LocalSigningKeyConfigError):
        LocalEd25519SigningBackend({"active": str(active)}, {"retired": str(link)})
    public.write_bytes(b"x" * 65537)
    with pytest.raises(LocalSigningKeyConfigError):
        LocalEd25519SigningBackend({"active": str(active)}, {"retired": str(public)})


def test_public_loader_rejects_special_files_owners_and_algorithms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from cryptography.exceptions import UnsupportedAlgorithm

    private = _write_key(tmp_path / "private.pem")
    public = _write_public(tmp_path / "public.pem", private)
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(tmp_path, target_is_directory=True)
    fifo = tmp_path / "fifo.pub"
    os.mkfifo(fifo)
    for bad in (linked_parent / "public.pem", fifo, private):
        with pytest.raises(LocalSigningKeyConfigError):
            local_module.load_ed25519_public_key("retired", str(bad))
    monkeypatch.setattr(local_module.os, "geteuid", lambda: os.stat(public).st_uid + 1)
    with pytest.raises(LocalSigningKeyConfigError, match="owner"):
        local_module.load_ed25519_public_key("retired", str(public))
    monkeypatch.undo()

    rsa_public = rsa.generate_private_key(public_exponent=65537, key_size=2048).public_key()
    public.write_bytes(
        rsa_public.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    with pytest.raises(LocalSigningKeyConfigError, match="Ed25519"):
        local_module.load_ed25519_public_key("retired", str(public))
    _write_public(public, private)

    def unsupported(_pem: bytes) -> object:
        raise UnsupportedAlgorithm("unsupported")

    monkeypatch.setattr(local_module.serialization, "load_pem_public_key", unsupported)
    with pytest.raises(LocalSigningKeyConfigError, match="Ed25519"):
        local_module.load_ed25519_public_key("retired", str(public))


def test_public_verifier_is_verify_only_and_bound_to_one_id(tmp_path: Path) -> None:
    from harness_runtime.config.local_ed25519_signing_backend import (
        LocalEd25519PublicVerifier,
        load_ed25519_public_key,
        spki_identity,
    )

    private = ed25519.Ed25519PrivateKey.generate()
    public_path = tmp_path / "row.pub.pem"
    public_path.write_bytes(
        private.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    public_path.chmod(0o644)
    public = load_ed25519_public_key("row", str(public_path))
    verifier = LocalEd25519PublicVerifier("row", public)
    signature = private.sign(b"row")
    assert verifier.algorithm == "ed25519"
    assert verifier.key_identity() == spki_identity(public)
    assert verifier.verify(message=b"row", signature=signature, key_id="row", key_period=0)
    assert not verifier.verify(message=b"wrong", signature=signature, key_id="row", key_period=0)
    assert not verifier.verify(message=b"row", signature=b"short", key_id="row", key_period=0)
    with pytest.raises(SigningBackendUnavailableError):
        verifier.verify(message=b"row", signature=signature, key_id="other", key_period=0)
    with pytest.raises(SigningBackendUnavailableError):
        verifier.sign(message=b"row", key_id="row", key_period=0)
