"""WO-U24 — the canonical LIT trial-relation fact behind `SelectionFacts.trial_relation`."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from tools import workflow_facts as wf

ROOT = "arhugula-harness-trial-193"
EPIC = f"{ROOT}.99c"
UNIT = f"{EPIC}.1zo"
OTHER = "arhugula-storage-recovery-ugz"


def _export(*edges: tuple[str, str], issues: tuple[str, ...] = (ROOT, EPIC, UNIT, OTHER)) -> dict:
    return {
        "version": 2,
        "issues": [{"id": issue, "status": "open"} for issue in issues],
        "comments": [],
        "relations": [
            {"src_id": child, "dst_id": parent, "type": "parent-child"} for child, parent in edges
        ]
        + [{"src_id": OTHER, "dst_id": UNIT, "type": "blocks"}],
    }


_TREE = ((UNIT, EPIC), (EPIC, ROOT))


def _relation(export: dict, unit: str) -> str:
    return wf.trial_relation(wf.parse_tree(json.dumps(export).encode()), unit, ROOT)


@pytest.mark.parametrize(
    ("unit", "expected"),
    [(UNIT, "confirmed"), (EPIC, "confirmed"), (ROOT, "confirmed"), (OTHER, "contradicted")],
)
def test_parent_chain_decides_the_relation(unit: str, expected: str) -> None:
    # a `blocks` edge from an unrelated issue is not membership
    assert _relation(_export(*_TREE), unit) == expected


def test_a_chain_ending_at_another_root_is_contradicted() -> None:
    assert _relation(_export((UNIT, OTHER)), UNIT) == "contradicted"


@pytest.mark.parametrize(
    "export",
    [
        _export((EPIC, ROOT), issues=(ROOT, EPIC, OTHER)),  # the unit is absent
        _export((UNIT, EPIC), (EPIC, UNIT)),  # a cycle never reaches a root
    ],
    ids=["absent-unit", "cycle"],
)
def test_unprovable_relations_are_unknown(export: dict) -> None:
    assert _relation(export, UNIT) == "unknown"


@pytest.mark.parametrize(
    "raw",
    [
        b"not json",
        b"[]",
        json.dumps({**_export(*_TREE), "version": 1}).encode(),
        json.dumps({k: v for k, v in _export(*_TREE).items() if k != "relations"}).encode(),
        json.dumps(_export((UNIT, EPIC), (UNIT, OTHER))).encode(),
        json.dumps(_export((UNIT, "arhugula-missing"))).encode(),
        json.dumps({**_export(*_TREE), "issues": [{"id": UNIT}, {"id": UNIT}]}).encode(),
        json.dumps({**_export(*_TREE), "issues": [{"id": ""}]}).encode(),
    ],
    ids=[
        "garbage",
        "array",
        "other-version",
        "partial",
        "two-parents",
        "dangling",
        "duplicate-id",
        "empty-id",
    ],
)
def test_malformed_exports_are_refused(raw: bytes) -> None:
    with pytest.raises(ValueError):
        wf.parse_tree(raw)


def _fake_lit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str) -> Path:
    """A `lit` first on PATH whose `export` runs `body`; returns the directory it ran in."""
    bin_dir, store = tmp_path / "bin", tmp_path / "store"
    bin_dir.mkdir()
    store.mkdir()
    lit = bin_dir / "lit"
    lit.write_text(f'#!/bin/sh\n[ "$1" = export ] || exit 9\npwd > "{tmp_path}/cwd"\n{body}\n')
    lit.chmod(lit.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return store


def test_observation_reads_the_named_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    export = tmp_path / "export.json"
    export.write_text(json.dumps(_export(*_TREE)))
    store = _fake_lit(tmp_path, monkeypatch, f'cat "{export}"')

    assert wf.observe_trial_relation(store, UNIT, ROOT) == "confirmed"
    assert wf.observe_trial_relation(store, OTHER, ROOT) == "contradicted"
    assert (tmp_path / "cwd").read_text().strip() == str(store)


@pytest.mark.parametrize(
    "body", ["exit 3", "echo '{\"version\": 2}'", "printf ''"], ids=["fails", "partial", "empty"]
)
def test_a_failed_read_is_unknown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str
) -> None:
    store = _fake_lit(tmp_path, monkeypatch, body)

    assert wf.observe_trial_relation(store, UNIT, ROOT) == "unknown"


def test_a_missing_store_or_lit_is_unknown(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert wf.observe_trial_relation(tmp_path / "absent", UNIT, ROOT) == "unknown"
    monkeypatch.setenv("PATH", str(tmp_path))  # no lit at all
    assert wf.observe_trial_relation(tmp_path, UNIT, ROOT) == "unknown"


def test_admission_values_are_the_policy_observations() -> None:
    from typing import get_args

    from tools import workflow_policy as wp

    assert set(get_args(wp.Observation)) == wf.OBSERVATIONS


def _fake_orchestration(tmp_path: Path, body: str) -> Path:
    """A checkout whose admission script records its argv/cwd/isolation, then runs `body`."""
    root = tmp_path / "orchestration"
    script = root / wf.ADMISSION_SCRIPT
    script.parent.mkdir(parents=True)
    script.write_text(
        "import json, os, sys\n"
        f"open({str(tmp_path / 'call')!r}, 'w').write(json.dumps("
        "[sys.argv[1:], os.getcwd(), sys.flags.isolated]))\n" + body + "\n"
    )
    return root


@pytest.mark.parametrize("observed", ["confirmed", "contradicted", "unknown"])
@pytest.mark.parametrize("operation", ["implementation", "integration"])
def test_admission_is_the_orchestration_scripts_observation(
    tmp_path: Path, observed: str, operation: wf.Operation
) -> None:
    line = json.dumps({"admission": observed, "reasons": [], "session_id": "s"})
    root = _fake_orchestration(tmp_path, f"print({line!r})")

    assert wf.observe_admission(root, UNIT, operation) == observed
    argv, cwd, isolated = json.loads((tmp_path / "call").read_text())
    assert (argv, cwd, isolated) == (["admission", UNIT, operation], str(root), 1)


@pytest.mark.parametrize(
    "body",
    [
        "sys.exit(2)",
        "print(json.dumps({'admission': 'confirmed'})); sys.exit(1)",
        "pass",
        "print('not json')",
        "print(json.dumps(['confirmed']))",
        "print(json.dumps({'admission': 'allow'}))",
        "print(json.dumps({'reasons': []}))",
        "line = json.dumps({'admission': 'confirmed'}); print(line); print(line)",
    ],
    ids=["usage", "failed", "silent", "not-json", "not-object", "foreign", "absent", "two-lines"],
)
def test_an_unparseable_admission_is_unknown(tmp_path: Path, body: str) -> None:
    root = _fake_orchestration(tmp_path, body)

    assert wf.observe_admission(root, UNIT, "implementation") == "unknown"


def test_a_missing_or_slow_orchestration_checkout_is_unknown(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert wf.observe_admission(tmp_path / "absent", UNIT, "integration") == "unknown"
    monkeypatch.setattr(wf, "ADMISSION_TIMEOUT_SECONDS", 0.5)
    root = _fake_orchestration(tmp_path, "import time; time.sleep(5)")
    assert wf.observe_admission(root, UNIT, "integration") == "unknown"
