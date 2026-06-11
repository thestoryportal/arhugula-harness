"""Unit tests for the runtime prompt-selection consumer (R-PM-1 cascade PR #3).

`reconcile_active_prompt_via_selection` composes the CP selection resolver
(`(role, workload) → version_sha`) with the IS `PromptManifest.versions` store
(`version_sha → member`) and reconciles `active_prompt_version` onto the selected
member — so BOTH the runtime injection reader (`.content`) and the C-IS-05 §5.2
procedural-tier hash reader (`.version_sha`) read the SAME selected version
(coherent by construction). The bootstrap-level e2e proof lives in
`test_bootstrap.py`; these isolate the reconciliation logic + the fail-loud
cross-axis membership check.
"""

from __future__ import annotations

import pytest
from harness_core import WorkloadClass
from harness_cp.cp_shared_types import AgentRole
from harness_cp.prompt_selection_manifest import PromptBinding, PromptSelectionManifest
from harness_is.prompt_manifest import PromptManifest, prompt_version_sha
from harness_runtime.lifecycle.prompt_selection import (
    InvalidPromptSelectionManifestError,
    PromptSelectionUnauthoredError,
    reconcile_active_prompt_via_selection,
)

_SE = WorkloadClass.SOFTWARE_ENGINEERING
_RESEARCH = WorkloadClass.RESEARCH


def _store_manifest() -> PromptManifest:
    """A two-version authored store with 'B body' as the standing inline active."""
    return PromptManifest.from_contents(
        manifest_version=1,
        contents=["A body", "B body"],
        active="B body",
    )


def test_reconcile_none_selection_manifest_unchanged() -> None:
    """No selection configured (`None`) → the manifest is returned unchanged (the
    #496/PR-#1 standing inline active prompt; zero behavior change)."""
    pm = _store_manifest()
    result = reconcile_active_prompt_via_selection(pm, None, workload_class=_SE)
    assert result is pm


def test_reconcile_no_match_unchanged() -> None:
    """A selection manifest that binds neither the role nor the workload → unchanged."""
    pm = _store_manifest()
    selection = PromptSelectionManifest(
        manifest_version=1,
        per_workload_overrides={_RESEARCH: PromptBinding(version_sha=prompt_version_sha("A body"))},
    )
    # The run workload is _SE, but the override is for _RESEARCH → no match.
    result = reconcile_active_prompt_via_selection(pm, selection, workload_class=_SE)
    assert result.active_prompt_version.content == "B body"


def test_reconcile_workload_selection_drives_active_and_is_coherent() -> None:
    """A workload override selects an authored member; BOTH the content reader and
    the version_sha (hash) reader move to the selected version — coherent."""
    pm = _store_manifest()  # active = "B body"
    selection = PromptSelectionManifest(
        manifest_version=1,
        per_workload_overrides={_SE: PromptBinding(version_sha=prompt_version_sha("A body"))},
    )
    result = reconcile_active_prompt_via_selection(pm, selection, workload_class=_SE)
    # Injection reader (content) AND §5.2 hash reader (version_sha) BOTH = selected.
    assert result.active_prompt_version.content == "A body"
    assert result.active_prompt_version.version_sha == prompt_version_sha("A body")
    # The store is preserved intact (only the active selection changed).
    assert {v.version_sha for v in result.versions} == {
        prompt_version_sha("A body"),
        prompt_version_sha("B body"),
    }


def test_reconcile_per_role_binding_against_mvp_default_role() -> None:
    """Per-role selection resolves against the MVP-default role (the runtime has no
    per-step role at MVP; faithful to the routing precedent)."""
    pm = _store_manifest()
    selection = PromptSelectionManifest(
        manifest_version=1,
        per_role_bindings={
            AgentRole("default"): PromptBinding(version_sha=prompt_version_sha("A body"))
        },
    )
    # No workload override → falls to the role binding, keyed on the default role.
    result = reconcile_active_prompt_via_selection(pm, selection, workload_class=_SE)
    assert result.active_prompt_version.content == "A body"


def test_reconcile_unauthored_sha_fails_loud() -> None:
    """A binding to a sha that is not an authored store member is fail-loud
    (cross-axis membership check, detect-then-refuse)."""
    pm = _store_manifest()
    selection = PromptSelectionManifest(
        manifest_version=1,
        per_workload_overrides={_SE: PromptBinding(version_sha="deadbeef" * 8)},
    )
    with pytest.raises(PromptSelectionUnauthoredError, match="RT-FAIL-PROMPT-SELECTION-UNAUTHORED"):
        reconcile_active_prompt_via_selection(pm, selection, workload_class=_SE)


def test_reconcile_invalid_manifest_fails_loud() -> None:
    """An operator-supplied manifest that fails the structural validator
    (`manifest_version < 1`) is fail-loud at the consumer site — parity with
    `build_routing_manifest`'s bootstrap validation (the validator is not left
    unwired)."""
    pm = _store_manifest()
    invalid = PromptSelectionManifest(
        manifest_version=0,
        per_workload_overrides={_SE: PromptBinding(version_sha=prompt_version_sha("A body"))},
    )
    with pytest.raises(InvalidPromptSelectionManifestError, match="manifest_version"):
        reconcile_active_prompt_via_selection(pm, invalid, workload_class=_SE)


def test_reconcile_empty_store_with_selection_fails_loud() -> None:
    """Selecting any version against an empty store is fail-loud (you cannot select
    an unauthored version)."""
    pm = PromptManifest.from_contents(manifest_version=1, contents=[], active=None)
    assert pm.versions == ()
    selection = PromptSelectionManifest(
        manifest_version=1,
        per_workload_overrides={_SE: PromptBinding(version_sha=prompt_version_sha("anything"))},
    )
    with pytest.raises(PromptSelectionUnauthoredError):
        reconcile_active_prompt_via_selection(pm, selection, workload_class=_SE)
