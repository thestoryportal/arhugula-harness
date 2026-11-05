"""U-RT-160b: the one Runtime pause-journal root resolver (Runtime spec v1.137 Rules B3/B7).

Every arm is driven through `resolve_pause_journal_root`, the function all four journal sites
call: the installation state supplies the declaration, the filesystem the observation, and the
config only its bound directories.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from harness_core.deployment_surface import DeploymentSurface
from harness_is.path_class_registry import PathClass
from harness_is.pause_journal_root import UnresolvedCause
from harness_runtime.lifecycle.pause_journal_root_resolver import (
    INSTALLATION_STATE,
    STORAGE_UNSELECTED,
    InstallationState,
    PauseJournalRootUnresolvedError,
    resolve_pause_journal_root,
)
from harness_runtime.types import PathBindingConfig, WorkloadClass

from .pause_journal_roots import declare_pause_journal_root


def _bound_at(*paths: Path) -> Any:
    """A config whose only contribution is its bound path-binding directories."""
    return SimpleNamespace(
        path_bindings=PathBindingConfig(
            raw_entries=tuple(
                {
                    "path_class": path_class,
                    "workflow_class": WorkloadClass.SOFTWARE_ENGINEERING,
                    "deployment_surface": DeploymentSurface.LOCAL_DEVELOPMENT,
                    "path": str(path),
                }
                for path_class, path in zip(PathClass, paths, strict=False)
            )
        )
    )


_UNBOUND = _bound_at()


def _cause(config: Any) -> UnresolvedCause:
    with pytest.raises(PauseJournalRootUnresolvedError) as excinfo:
        resolve_pause_journal_root(config)
    return excinfo.value.cause


def test_a_declared_existing_root_resolves_to_the_declaration(tmp_path: Path) -> None:
    root = tmp_path / "pause-journal"
    root.mkdir()
    declare_pause_journal_root(root)

    assert resolve_pause_journal_root(_bound_at(tmp_path / "ledger")) == root


def test_the_production_state_declares_nothing_so_the_root_is_unbound() -> None:
    INSTALLATION_STATE.set(STORAGE_UNSELECTED)

    assert _cause(_UNBOUND) is UnresolvedCause.UNBOUND


@pytest.mark.parametrize(
    "declarations",
    [
        ({"installation_root": "relative/pause-journal"},),
        ({"installation_root": "/srv/pj/"},),
        ({"installation_root": "/srv/pj", "extra": 1},),
        ({},),
    ],
    ids=["relative", "unnormalized", "extra-key", "no-root"],
)
def test_a_malformed_declaration_is_refused(declarations: tuple[dict[str, object], ...]) -> None:
    INSTALLATION_STATE.set(InstallationState(pause_journal_root_declarations=declarations))

    assert _cause(_UNBOUND) is UnresolvedCause.MALFORMED


def test_two_declarations_conflict_even_when_equal(tmp_path: Path) -> None:
    root = tmp_path / "pause-journal"
    root.mkdir()
    one = {"installation_root": str(root)}
    INSTALLATION_STATE.set(InstallationState(pause_journal_root_declarations=(one, dict(one))))

    assert _cause(_UNBOUND) is UnresolvedCause.CONFLICTING


@pytest.mark.parametrize("shape", ["absent", "file", "dangling-symlink"])
def test_a_declared_root_that_is_not_a_directory_is_missing(tmp_path: Path, shape: str) -> None:
    root = tmp_path / "pause-journal"
    match shape:
        case "file":
            root.write_text("")
        case "dangling-symlink":
            root.symlink_to(tmp_path / "gone")
        case _:
            pass
    declare_pause_journal_root(root)

    assert _cause(_UNBOUND) is UnresolvedCause.MISSING


@pytest.mark.parametrize("relation", ["equal", "ancestor", "descendant"])
def test_a_root_nested_with_a_bound_directory_overlaps(tmp_path: Path, relation: str) -> None:
    root = tmp_path / "state" / "pause-journal"
    root.mkdir(parents=True)
    declare_pause_journal_root(root)
    bound = {"equal": root, "ancestor": root.parent, "descendant": root / "ledger"}[relation]

    assert _cause(_bound_at(tmp_path / "unrelated", bound)) is UnresolvedCause.OVERLAPPING


def test_overlap_is_judged_on_real_paths_through_a_symlinked_root(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger"
    (ledger / "journal").mkdir(parents=True)
    root = tmp_path / "pause-journal"
    root.symlink_to(ledger / "journal")
    declare_pause_journal_root(root)

    assert _cause(_bound_at(ledger)) is UnresolvedCause.OVERLAPPING


def test_a_symlinked_root_outside_every_binding_resolves_to_the_declared_path(
    tmp_path: Path,
) -> None:
    target = tmp_path / "volume" / "journal"
    target.mkdir(parents=True)
    root = tmp_path / "pause-journal"
    root.symlink_to(target)
    declare_pause_journal_root(root)

    assert resolve_pause_journal_root(_bound_at(tmp_path / "ledger")) == root


def test_the_refusal_names_its_cause_and_never_the_path(tmp_path: Path) -> None:
    root = tmp_path / "pause-journal"
    declare_pause_journal_root(root)

    with pytest.raises(PauseJournalRootUnresolvedError) as excinfo:
        resolve_pause_journal_root(_UNBOUND)

    assert "missing" in str(excinfo.value)
    assert str(tmp_path) not in str(excinfo.value)
