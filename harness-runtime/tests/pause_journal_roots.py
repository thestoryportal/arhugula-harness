"""Declare the installation's pause-journal root for a test (U-RT-160b, Runtime spec v1.137 Rule B3).

Production reads `INSTALLATION_STATE` from the operator's installation-state document, absent
until storage is bound, so every journal site fails closed; a test that exercises a journal site
writes its own document under the test's interpreter prefix. The conftest's autouse
`_storage_unselected` gives every test that empty prefix and restores the binding after it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from harness_runtime.bootstrap import stage_1_is
from harness_runtime.config import state_placement
from harness_runtime.lifecycle.installation_state import (
    installation_state_path,
    read_installation_state,
)
from harness_runtime.lifecycle.pause_journal_root_resolver import INSTALLATION_STATE
from harness_runtime.types import PathBindingConfig, RuntimeConfig, StatePlacementConfig


def write_installation_state(document: str) -> None:
    """Write the operator's document, then bind it for the rest of this test.

    Direct journal-site calls see it through the binding; every public ingress re-reads it.
    """
    path = installation_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")
    INSTALLATION_STATE.set(read_installation_state())


def declare_pause_journal_roots(*roots: object) -> None:
    """Declare each raw `installation_root` value, in order, for the rest of this test."""
    write_installation_state(
        json.dumps({"pause_journal_root_declarations": [{"installation_root": r} for r in roots]})
    )


def declare_pause_journal_root(root: Path) -> Path:
    """Declare `root` for the rest of this test (and the tasks/threads it starts); returns it."""
    declare_pause_journal_roots(str(root))
    return root


@pytest.fixture
def placed_root(world: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A stamped external state root beside a checkout, holding the declared journal root.

    Rule B3 places a fresh run's pause-journal root with the same verification a durable
    claim uses, so a run admits only under a declared `state_placement` (`placed_config`).
    The root is stamped before the journal root is created in it: bootstrap refuses to
    adopt a non-empty unmarked directory.
    """
    # The scratch dir may be tmpfs; the verifier's real resolver is covered in test_state_placement.
    monkeypatch.setattr(stage_1_is, "linux_filesystem_type", lambda _p: "ext4")
    monkeypatch.setattr(state_placement, "linux_filesystem_type", lambda _p: "ext4")
    repo = world / "repo"
    (repo / ".git").mkdir(parents=True)
    root = world / "state"
    state_placement.bootstrap_state_root(
        StatePlacementConfig(state_root=root),
        repository_root=repo,
        worktree_base=state_placement.transient_worktree_base(repo),
        path_bindings=PathBindingConfig(),
        filesystem_type=lambda _p: "ext4",
    )
    declare_pause_journal_root(root / "pause-journal").mkdir()
    return root


def placed_config(config: RuntimeConfig, root: Path) -> RuntimeConfig:
    """`config` placed under the `placed_root` fixture's `root`, its checkout beside it."""
    return config.model_copy(
        update={
            "repository_root": root.parent / "repo",
            "state_placement": StatePlacementConfig(state_root=root),
        }
    )
