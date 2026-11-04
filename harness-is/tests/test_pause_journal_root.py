"""Tests for U-IS-21 — installation pause-journal root (C-IS-01 §1.1, IS spec v1.17).

Test set per the U-IS-21 `Tests:` field (IS plan v2.11 §1). Acceptance-criterion coverage:
  #1 cardinality + shape causes      -> test_declaration_cardinality_and_shape_causes
  #2 NotADirectory -> MISSING         -> test_declaration_cardinality_and_shape_causes
  #3 real-path overlap                -> test_overlap_compares_real_paths
  #4 cross-binding identity           -> test_root_independent_of_bound_paths
  #5 closed result, no selector input -> test_no_default_root
  #6 PathClass registry unchanged     -> test_path_class_registry_unchanged

Spec witnesses 2, 4 and 5 and the exit-6 refusal need real Runtime processes; they
run at Runtime plan v2.68 U-RT-160 criteria 15 and 17, not here.
"""

from __future__ import annotations

import inspect
import os
import random
from pathlib import Path
from typing import get_args

import pytest
from harness_is.path_class_registry import PATH_CLASS_REGISTRY, PathClass
from harness_is.pause_journal_root import (
    ExistingDirectory,
    NotADirectory,
    PauseJournalRootDeclaration,
    PauseJournalRootResolution,
    Resolved,
    Unresolved,
    UnresolvedCause,
    parse_declarations,
    resolve_root,
)

_ROOT = Path("/srv/pause-journal")
_DECLARATION = PauseJournalRootDeclaration(installation_root=_ROOT)


def test_declaration_cardinality_and_shape_causes() -> None:
    """Criteria 1-2: count first, then shape, then the observed directory."""
    assert parse_declarations([]) == Unresolved(UnresolvedCause.UNBOUND)
    one = {"installation_root": str(_ROOT)}
    assert parse_declarations([one]) == _DECLARATION
    # Two equal declarations still conflict; they are not collapsed into one.
    assert parse_declarations([one, dict(one)]) == Unresolved(UnresolvedCause.CONFLICTING)
    other = {"installation_root": "/srv/other"}
    assert parse_declarations([one, other]) == Unresolved(UnresolvedCause.CONFLICTING)

    for raw_root in (
        "srv/pause-journal",
        "./pause-journal",
        "",
        "/srv/pause-journal/",
        "/srv//pause-journal",
        "/srv/./pause-journal",
        "/srv/x/../pause-journal",
        "/srv/pause\x00journal",
        7,
        None,
    ):
        assert parse_declarations([{"installation_root": raw_root}]) == Unresolved(
            UnresolvedCause.MALFORMED
        ), raw_root
    assert parse_declarations([{}]) == Unresolved(UnresolvedCause.MALFORMED)
    assert parse_declarations([{**one, "tenant": "acme"}]) == Unresolved(UnresolvedCause.MALFORMED)

    assert resolve_root(_DECLARATION, NotADirectory(), []) == Unresolved(UnresolvedCause.MISSING)


@pytest.mark.parametrize(
    ("root_real_path", "bound"),
    [
        pytest.param("/data/ledger", ["/data/ledger"], id="equal"),
        pytest.param("/data/ledger/pause-journal", ["/data/ledger"], id="inside-bound"),
        pytest.param("/data", ["/data/ledger"], id="contains-bound"),
        pytest.param(
            "/data/prompts/pj", ["/data/skills", "/data/routing", "/data/prompts"], id="last-bound"
        ),
    ],
)
def test_overlap_compares_real_paths(root_real_path: str, bound: list[str]) -> None:
    """Criterion 3: equal, ancestor and descendant real paths, against any bound path."""
    observed = ExistingDirectory(real_path=Path(root_real_path))
    result = resolve_root(_DECLARATION, observed, (Path(p) for p in bound))
    assert result == Unresolved(UnresolvedCause.OVERLAPPING)


def test_overlap_follows_symlink_aliases(tmp_path: Path) -> None:
    """Criterion 3: a declared alias of, or into, a bound directory overlaps."""
    ledger = tmp_path / "data" / "ledger"
    (ledger / "pause-journal").mkdir(parents=True)
    alias_of = tmp_path / "alias-of-ledger"
    alias_of.symlink_to(ledger, target_is_directory=True)
    alias_into = tmp_path / "alias-into-ledger"
    alias_into.symlink_to(ledger / "pause-journal", target_is_directory=True)
    bound = [Path(os.path.realpath(ledger))]

    for alias in (alias_of, alias_into):
        declaration = PauseJournalRootDeclaration(installation_root=alias)
        observed = ExistingDirectory(real_path=Path(os.path.realpath(alias)))
        assert resolve_root(declaration, observed, bound) == Unresolved(UnresolvedCause.OVERLAPPING)

    # A sibling whose name merely extends a bound name does not overlap.
    sibling = tmp_path / "data" / "ledger-pause-journal"
    sibling.mkdir()
    declaration = PauseJournalRootDeclaration(installation_root=sibling)
    observed = ExistingDirectory(real_path=Path(os.path.realpath(sibling)))
    assert resolve_root(declaration, observed, bound) == Resolved(sibling)


def _non_overlapping_bound_sets(count: int) -> list[list[Path]]:
    rng = random.Random(21)
    names = ["skills", "prompts", "routing", "ledger", "ws-a", "ws-b", "état", "pause-journal"]
    return [
        [Path("/data", *rng.sample(names, rng.randint(1, 3))) for _ in range(rng.randint(0, 6))]
        for _ in range(count)
    ]


def test_root_independent_of_bound_paths() -> None:
    """Criterion 4 / spec witness 1: bound paths never change the resolved root."""
    # The declared root is an alias; the result is the declared value, not the real path.
    declaration = PauseJournalRootDeclaration(installation_root=Path("/install/pause-journal"))
    observed = ExistingDirectory(real_path=_ROOT)
    expected = Resolved(Path("/install/pause-journal"))
    results = {
        resolve_root(declaration, observed, bound) for bound in _non_overlapping_bound_sets(200)
    }
    assert results == {expected}


def test_no_default_root() -> None:
    """Criterion 5 / spec witnesses 3-4: closed result, no default, no selector input."""
    assert get_args(PauseJournalRootResolution) == (Resolved, Unresolved)
    unbound = parse_declarations([])
    assert not isinstance(unbound, PauseJournalRootDeclaration | Resolved)
    assert unbound == Unresolved(UnresolvedCause.UNBOUND)

    assert list(inspect.signature(parse_declarations).parameters) == ["raw"]
    assert list(inspect.signature(resolve_root).parameters) == [
        "declaration",
        "observed",
        "bound_real_paths",
    ]
    assert list(PauseJournalRootDeclaration.model_fields) == ["installation_root"]

    # A STATE_LEDGER directory among the bound paths never becomes the root.
    ledger = Path("/data/state-ledger")
    resolved = resolve_root(
        _DECLARATION, ExistingDirectory(real_path=_ROOT), [ledger, ledger / "pause-journal"]
    )
    assert resolved == Resolved(_ROOT)


def test_path_class_registry_unchanged() -> None:
    """Criterion 6: the root is not a path class; the registry stays at four."""
    assert {pc.value for pc in PathClass} == {
        "SKILLS",
        "PROMPTS",
        "ROUTING_MANIFEST",
        "STATE_LEDGER",
    }
    assert set(PATH_CLASS_REGISTRY) == set(PathClass)
