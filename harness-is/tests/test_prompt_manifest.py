"""Tests for the prompts-management carrier — `PromptManifest` + `PromptVersion`.

Implements IS spec v1.5 §C-IS-05 §5.2 (third procedural-tier hash-component
carrier; post-MVP closure R-CL-P4). Mirrors the `RoutingManifest` shape
(frozen + `extra="forbid"`); empty-defaultable at the runtime carrier.
"""

from __future__ import annotations

import pytest
from harness_is.prompt_manifest import PromptManifest, PromptVersion
from pydantic import ValidationError


def test_prompt_version_construct_and_frozen() -> None:
    """`PromptVersion` carries a `version_sha` and is frozen + extra-forbid."""
    pv = PromptVersion(version_sha="abc123")
    assert pv.version_sha == "abc123"
    with pytest.raises(ValidationError):
        pv.version_sha = "mutated"  # type: ignore[misc]  # frozen
    with pytest.raises(ValidationError):
        PromptVersion(version_sha="x", unexpected="y")  # type: ignore[call-arg]  # extra-forbid


def test_prompt_manifest_construct_and_frozen() -> None:
    """`PromptManifest` mirrors `RoutingManifest` (frozen + extra-forbid)."""
    pm = PromptManifest(
        manifest_version=1,
        active_prompt_version=PromptVersion(version_sha="v-sha"),
    )
    assert pm.manifest_version == 1
    assert pm.active_prompt_version.version_sha == "v-sha"
    with pytest.raises(ValidationError):
        pm.manifest_version = 2  # type: ignore[misc]  # frozen
    with pytest.raises(ValidationError):
        PromptManifest(  # type: ignore[call-arg]  # extra-forbid
            manifest_version=1,
            active_prompt_version=PromptVersion(version_sha=""),
            extra="nope",
        )


def test_prompt_manifest_empty_carrier_sentinel() -> None:
    """The empty-carrier shape (`version_sha=""`) is the no-active-prompt default."""
    empty = PromptManifest(
        manifest_version=1,
        active_prompt_version=PromptVersion(version_sha=""),
    )
    assert empty.active_prompt_version.version_sha == ""


def test_prompt_manifest_equality_by_value() -> None:
    """Two logically-identical manifests compare equal (value semantics for the
    resolver's cross-instance determinism)."""
    a = PromptManifest(manifest_version=1, active_prompt_version=PromptVersion(version_sha="s"))
    b = PromptManifest(manifest_version=1, active_prompt_version=PromptVersion(version_sha="s"))
    assert a == b
