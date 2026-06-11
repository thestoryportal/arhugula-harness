"""Tests for the prompts-management carrier — `PromptManifest` + `PromptVersion`.

Implements IS spec v1.5 §C-IS-05 §5.2 (third procedural-tier hash-component
carrier; post-MVP closure R-CL-P4). Mirrors the `RoutingManifest` shape
(frozen + `extra="forbid"`); empty-defaultable at the runtime carrier.

R-PM-1 cascade PR #1 (IS spec v1.6 §C-IS-05 §5.2 provenance-tightening) adds
the inline `content` carrier + the `version_sha == prompt_version_sha(content)`
derive-invariant (detect-then-refuse).
"""

from __future__ import annotations

import hashlib

import pytest
from harness_is.prompt_manifest import (
    PromptManifest,
    PromptVersion,
    prompt_version_sha,
)
from pydantic import ValidationError


def test_prompt_version_construct_and_frozen() -> None:
    """`PromptVersion` carries a content-derived `version_sha` and is frozen +
    extra-forbid."""
    pv = PromptVersion.from_content("hello prompt")
    assert pv.content == "hello prompt"
    assert pv.version_sha == prompt_version_sha("hello prompt")
    with pytest.raises(ValidationError):
        pv.version_sha = "mutated"  # type: ignore[misc]  # frozen
    with pytest.raises(ValidationError):
        PromptVersion(version_sha="", unexpected="y")  # type: ignore[call-arg]  # extra-forbid


def test_prompt_version_sha_helper_empty_is_sentinel() -> None:
    """`prompt_version_sha("")` is the empty-carrier sentinel; non-empty is a
    hex SHA-256 digest of the content."""
    assert prompt_version_sha("") == ""
    expected = hashlib.sha256(b"some content").hexdigest()
    assert prompt_version_sha("some content") == expected


def test_prompt_version_derive_invariant_rejects_mismatched_sha() -> None:
    """The `version_sha == digest(content)` invariant is enforced at
    construction (detect-then-refuse) — a non-empty content with a wrong sha
    raises, and a non-empty sha with no content raises (the #496 identity-only
    pattern is superseded)."""
    with pytest.raises(ValidationError):
        PromptVersion(version_sha="not-the-digest", content="real content")
    with pytest.raises(ValidationError):
        PromptVersion(version_sha="orphan-sha", content="")


def test_prompt_version_empty_carrier_sentinel() -> None:
    """The empty-carrier shape (`version_sha=""`, `content=""`) is the
    no-active-prompt default and satisfies the invariant."""
    pv = PromptVersion(version_sha="")
    assert pv.version_sha == ""
    assert pv.content == ""
    assert PromptVersion.from_content("") == pv


def test_prompt_manifest_construct_and_frozen() -> None:
    """`PromptManifest` mirrors `RoutingManifest` (frozen + extra-forbid)."""
    pm = PromptManifest(
        manifest_version=1,
        active_prompt_version=PromptVersion.from_content("v-content"),
    )
    assert pm.manifest_version == 1
    assert pm.active_prompt_version.content == "v-content"
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
    a = PromptManifest(manifest_version=1, active_prompt_version=PromptVersion.from_content("s"))
    b = PromptManifest(manifest_version=1, active_prompt_version=PromptVersion.from_content("s"))
    assert a == b
