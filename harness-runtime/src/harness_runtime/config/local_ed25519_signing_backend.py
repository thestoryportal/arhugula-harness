"""File-backed Ed25519 audit signer with public historical row identities.

Private keys stay in process memory. Public-only keys resolve old row identities;
they cannot sign or verify through this active backend. This does not provide
rotation by key period or protect against compromise of the harness OS user.
"""

from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Mapping
from pathlib import Path

from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from harness_core import SigningBackendUnavailableError


class LocalSigningKeyConfigError(ValueError):
    """A configured local key cannot be safely loaded."""


class UnknownLocalSigningKeyIdError(SigningBackendUnavailableError, KeyError):
    """No active private key was configured for this logical ID."""


class LocalEd25519SigningBackend:
    """Sign with active keys and resolve active or historical row identities."""

    algorithm: str = "ed25519"

    def __init__(
        self, key_paths: Mapping[str, str], public_key_paths: Mapping[str, str] | None = None
    ) -> None:
        if not key_paths:
            raise LocalSigningKeyConfigError("local_key_paths must be non-empty")
        self._keys = {key_id: _load_private_key(key_id, path) for key_id, path in key_paths.items()}
        self._historical = {
            key_id: _load_public_key(key_id, path)
            for key_id, path in (public_key_paths or {}).items()
        }
        # [LAW:one-source-of-truth] A configured active ID has one physical identity.
        for key_id, public_key in self._historical.items():
            if key_id in self._keys and _spki_identity(public_key) != self.key_identity(key_id):
                raise LocalSigningKeyConfigError(
                    f"key_id {key_id!r} public and private key identities must match"
                )

    def sign(self, *, message: bytes, key_id: str, key_period: int) -> bytes:
        del key_period
        return self._key(key_id).sign(message)

    def verify(self, *, message: bytes, signature: bytes, key_id: str, key_period: int) -> bool:
        del key_period
        public_key = self._key(key_id).public_key()
        if len(signature) != 64:
            return False
        try:
            public_key.verify(signature, message)
        except InvalidSignature:
            return False
        return True

    def key_identity(self, key_id: str) -> str:
        # [LAW:one-source-of-truth] Derive identity from the key already loaded for signing.
        return _spki_identity(self._key(key_id).public_key())

    def row_key_identity(self, key_id: str) -> str | None:
        # [LAW:types-are-the-program] Public-only IDs resolve rows, never active signing.
        if key_id in self._keys:
            return self.key_identity(key_id)
        public_key = self._historical.get(key_id)
        return _spki_identity(public_key) if public_key is not None else None

    def _key(self, key_id: str) -> Ed25519PrivateKey:
        try:
            return self._keys[key_id]
        except KeyError as exc:
            raise UnknownLocalSigningKeyIdError(
                f"local Ed25519 signing key_id {key_id!r} is not configured"
            ) from exc


def _spki_identity(public_key: Ed25519PublicKey) -> str:
    spki = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return f"ed25519-spki-sha256:{hashlib.sha256(spki).hexdigest()}"


def _read_key_file(key_id: str, path: str, *, public: bool) -> bytes:
    # [LAW:effects-at-boundaries] One fd walk enforces the file policy for both key forms.
    kind = "public" if public else "private"
    if not Path(path).is_absolute():
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} needs an absolute {kind} key path")
    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    directory_flags = flags | os.O_DIRECTORY
    directory_fd = None
    try:
        directory_fd = os.open("/", directory_flags)
        parts = Path(path).parts[1:]
        if not parts:
            raise LocalSigningKeyConfigError(f"key_id {key_id!r} path is not a regular file")
        for component in parts[:-1]:
            next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        fd = os.open(parts[-1], flags | os.O_NONBLOCK, dir_fd=directory_fd)
        try:
            metadata = os.fstat(fd)
            mode = stat.S_IMODE(metadata.st_mode)
            if not stat.S_ISREG(metadata.st_mode):
                raise LocalSigningKeyConfigError(f"key_id {key_id!r} path is not a regular file")
            if metadata.st_uid != os.geteuid():
                raise LocalSigningKeyConfigError(f"key_id {key_id!r} {kind} key has wrong owner")
            if not mode & stat.S_IRUSR or mode & (0o022 if public else 0o077):
                policy = "no group/other write" if public else "owner read only"
                raise LocalSigningKeyConfigError(
                    f"key_id {key_id!r} {kind} key permissions must allow {policy}"
                )
            chunks: list[bytes] = []
            remaining = 65537
            while remaining:
                chunk = os.read(fd, remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            pem = b"".join(chunks)
        finally:
            os.close(fd)
    except OSError as exc:
        raise LocalSigningKeyConfigError(
            f"key_id {key_id!r} {kind} key path cannot be opened safely: {exc.strerror}"
        ) from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    if len(pem) > 65536:
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} {kind} key exceeds 64 KiB")
    return pem


def _load_private_key(key_id: str, path: str) -> Ed25519PrivateKey:
    pem = _read_key_file(key_id, path, public=False)
    if not pem.startswith(b"-----BEGIN PRIVATE KEY-----"):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} must contain an Ed25519 PKCS#8 PEM")
    try:
        key = serialization.load_pem_private_key(pem, password=None)
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise LocalSigningKeyConfigError(
            f"key_id {key_id!r} must contain an Ed25519 PKCS#8 PEM"
        ) from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} is not an Ed25519 private key")
    return key


def _load_public_key(key_id: str, path: str) -> Ed25519PublicKey:
    pem = _read_key_file(key_id, path, public=True)
    if not pem.startswith(b"-----BEGIN PUBLIC KEY-----"):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} must contain an Ed25519 public PEM")
    try:
        key = serialization.load_pem_public_key(pem)
    except (TypeError, ValueError, UnsupportedAlgorithm) as exc:
        raise LocalSigningKeyConfigError(
            f"key_id {key_id!r} must contain an Ed25519 public PEM"
        ) from exc
    if not isinstance(key, Ed25519PublicKey):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} is not an Ed25519 public key")
    return key
