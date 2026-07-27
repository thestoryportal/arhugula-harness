"""B-65-A protected result store — stage-4 OD composition-root factory (U-RT-145).

Implements `Spec_Harness_Runtime_v1.md` v1.103 §14.8.11 construction (RATIFIED
B-65 Class 2 fork §3b). Plan home is `Implementation_Plan_Harness_Runtime_v2_51.
md` §1.1 U-RT-145, whose coverage row maps "§14.8.11 protected post-effect result
store (surface A)" to U-RT-145 and whose files-affected list names "the
composition-root factories that build those dispatchers (the store dependency +
owning tenant scope are INJECTED there)" — this module is that injection site.
Mirrors `memory_tool_registry_factory.
_create_fernet_from_key`'s lazy-`cryptography`-import idiom rather than
introducing a second Fernet-construction pattern — `cryptography` stays an
optional dependency behind an RT-FAIL, never imported eagerly.

The store's required-ness is coupled to the RESOLVED `audit_signing_
fail_closed` policy (advisor-resolved fork, 2026-07-22): `validate_mtc_audit_
signing_config` (stage 4, runs BEFORE this factory) already fails loud when
the flag resolves ON and the key env var is unset, so by the time this
factory runs, a resolved-ON bootstrap is GUARANTEED to have a valid key. This
factory itself stays permissive (returns `None` on an unset/malformed key)
because it doesn't know the resolved flag — that's the validation site's job,
not this construction site's.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from harness_runtime.lifecycle.protected_result_store import ProtectedResultStore
from harness_runtime.types import RuntimeConfig

if TYPE_CHECKING:
    from harness_runtime.lifecycle.memory_tool_encrypted import FernetLike

__all__ = ["materialize_protected_result_store_stage"]

_PROTECTED_RESULT_STORE_ROOT_SUBPATH = Path(".harness") / "protected-results"


def _create_fernet_from_key(key: bytes) -> FernetLike | None:
    """Lazily construct a `cryptography` Fernet from the resolved key.

    Mirrors `memory_tool_registry_factory._create_fernet_from_key` exactly
    (same optional-dependency-behind-RT-FAIL shape); kept as a separate
    function (not imported cross-factory) so each factory's failure message
    names its own config surface.
    """
    try:
        fernet_module = importlib.import_module("cryptography.fernet")
    except ImportError:
        return cast(Any, None)
    fernet_cls = cast(Any, fernet_module).Fernet
    try:
        return cast("FernetLike", fernet_cls(key))
    except (ValueError, TypeError):
        return cast(Any, None)


def materialize_protected_result_store_stage(config: RuntimeConfig) -> ProtectedResultStore | None:
    """Construct the stage-4 `ProtectedResultStore` instance, or `None` when
    the configured key env var is unset/malformed.

    `None` is a normal, ergonomically-valid outcome here — the raise-site
    helper `resolve_result_ref` degrades to an `UnresolvableResultRef`
    naming the missing store. Whether `None` is ACCEPTABLE for this
    bootstrap (i.e., whether `audit_signing_fail_closed` resolves ON) is
    `validate_mtc_audit_signing_config`'s job, enforced BEFORE this factory
    runs at stage 4 — this factory does not re-check the flag.
    """
    key_material = os.environ.get(config.protected_result_store_key_env_var)
    if not key_material:
        return None
    codec = _create_fernet_from_key(key_material.encode("utf-8"))
    if codec is None:
        return None
    return ProtectedResultStore(
        root=config.repository_root / _PROTECTED_RESULT_STORE_ROOT_SUBPATH,
        codec=codec,
        ttl_seconds=config.protected_result_store_ttl_seconds,
    )
