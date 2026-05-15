"""Tests for U-IS-02 — path-resolver primitive (C-IS-01 §1).

Test set per the U-IS-02 `Tests:` field. Acceptance-criterion coverage:
  #1 stable within run        -> test_resolve_path_stability_within_run
  #2 workflow-canonical       -> test_resolve_path_workflow_canonical_across_runs
  #3 workflow-class variance  -> test_resolve_path_workflow_class_variance_permitted
  #4 no hard-coded paths      -> test_resolve_path_no_hardcoded_paths
  #5 substrate-residence      -> by construction (see path_resolver module docstring)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from harness_is.path_binding import (
    DeploymentSurface,
    WorkflowClass,
    load_path_binding,
)
from harness_is.path_class_registry import PathClass
from harness_is.path_resolver import PathBindingMissingError, PathResolver

# Representative path-binding config — two workflow classes, one surface.
_RAW_CONFIG: list[dict[str, str]] = [
    {
        "path_class": "SKILLS",
        "workflow_class": "wf-alpha",
        "deployment_surface": "local",
        "path": ".harness/alpha/skills",
    },
    {
        "path_class": "SKILLS",
        "workflow_class": "wf-beta",
        "deployment_surface": "local",
        "path": ".harness/beta/skills",
    },
]


def test_resolve_path_stability_within_run() -> None:
    """Acceptance #1 — repeated calls on one triple return an equal Path."""
    resolver = PathResolver(load_path_binding(_RAW_CONFIG))
    first = resolver.resolve_path(
        PathClass.SKILLS, WorkflowClass("wf-alpha"), DeploymentSurface("local")
    )
    second = resolver.resolve_path(
        PathClass.SKILLS, WorkflowClass("wf-alpha"), DeploymentSurface("local")
    )
    assert first == second == Path(".harness/alpha/skills")


def test_resolve_path_workflow_canonical_across_runs() -> None:
    """Acceptance #2 — a resolver rebuilt from the same config is stable."""
    triple = (PathClass.SKILLS, WorkflowClass("wf-alpha"), DeploymentSurface("local"))
    run_one = PathResolver(load_path_binding(_RAW_CONFIG)).resolve_path(*triple)
    run_two = PathResolver(load_path_binding(_RAW_CONFIG)).resolve_path(*triple)
    assert run_one == run_two


def test_resolve_path_workflow_class_variance_permitted() -> None:
    """Acceptance #3 — differing workflow_class MAY differ, with no error."""
    resolver = PathResolver(load_path_binding(_RAW_CONFIG))
    alpha = resolver.resolve_path(
        PathClass.SKILLS, WorkflowClass("wf-alpha"), DeploymentSurface("local")
    )
    beta = resolver.resolve_path(
        PathClass.SKILLS, WorkflowClass("wf-beta"), DeploymentSurface("local")
    )
    assert alpha != beta


def test_resolve_path_no_hardcoded_paths() -> None:
    """Acceptance #4 — empty config yields a missing-binding error, not a default."""
    resolver = PathResolver(load_path_binding([]))
    with pytest.raises(PathBindingMissingError):
        resolver.resolve_path(
            PathClass.SKILLS, WorkflowClass("wf-alpha"), DeploymentSurface("local")
        )
