"""File-backed Ed25519 audit signer for a single host-held key per logical ID.

The loaded private keys stay in process memory. This does not provide rotation
by key period or protect signatures against compromise of the harness OS user.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from harness_core import SigningBackendUnavailableError


class LocalSigningKeyConfigError(ValueError):
    """A configured local private key cannot be safely loaded."""


class UnknownLocalSigningKeyIdError(SigningBackendUnavailableError, KeyError):
    """No private key was configured for this logical ID."""


class LocalEd25519SigningBackend:
    """Sign and verify with the private keys loaded at construction.

    Each logical ID maps to one fixed key. ``key_period`` is accepted for the
    protocol but does not select a rotated key; period-aware signing is a later
    slice. Public-only verification construction is also a later slice.
    """

    algorithm: str = "ed25519"

    def __init__(self, key_paths: Mapping[str, str]) -> None:
        if not key_paths:
            raise LocalSigningKeyConfigError("local_key_paths must be non-empty")
        self._keys = {key_id: _load_private_key(key_id, path) for key_id, path in key_paths.items()}

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

    def _key(self, key_id: str) -> Ed25519PrivateKey:
        try:
            return self._keys[key_id]
        except KeyError as exc:
            raise UnknownLocalSigningKeyIdError(
                f"local Ed25519 signing key_id {key_id!r} is not configured"
            ) from exc


def _load_private_key(key_id: str, path: str) -> Ed25519PrivateKey:
    # [LAW:effects-at-boundaries] Open each component without following links; inspect the fd read.
    if not Path(path).is_absolute():
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} needs an absolute private key path")
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
                raise LocalSigningKeyConfigError(f"key_id {key_id!r} private key has wrong owner")
            if not mode & stat.S_IRUSR or mode & 0o077:
                raise LocalSigningKeyConfigError(
                    f"key_id {key_id!r} private key permissions must allow owner read only"
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
            f"key_id {key_id!r} private key path cannot be opened safely: {exc.strerror}"
        ) from exc
    finally:
        if directory_fd is not None:
            os.close(directory_fd)
    if len(pem) > 65536 or not pem.startswith(b"-----BEGIN PRIVATE KEY-----"):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} must contain an Ed25519 PKCS#8 PEM")
    try:
        key = serialization.load_pem_private_key(pem, password=None)
    except (TypeError, ValueError) as exc:
        raise LocalSigningKeyConfigError(
            f"key_id {key_id!r} must contain an Ed25519 PKCS#8 PEM"
        ) from exc
    if not isinstance(key, Ed25519PrivateKey):
        raise LocalSigningKeyConfigError(f"key_id {key_id!r} is not an Ed25519 private key")
    return key
