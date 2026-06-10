#!/usr/bin/env python3
"""Tests for the spec/CXA/substitution semantic overlay (R-IF-112).

Mirrors `test_substitution_ledger.py`: a pure `derive()` + a `validate()` gate, exercised
against the real repo at HEAD (no fixtures — the repo IS the source of truth).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import overlay


@pytest.fixture(scope="module")
def graph() -> dict:
    return overlay.derive()


# --------------------------------------------------------------------------- #
# cite extraction
# --------------------------------------------------------------------------- #


def test_extract_cites_pulls_each_class() -> None:
    text = (
        '"""Path-class registry — U-IS-01.\n'
        "Implements C-IS-01 §1 per ADR-F2 v1.2; retires H_T-IS-1.\n"
        '"""'
    )
    c = overlay.extract_cites(text)
    assert c["spec_contracts"] == ["C-IS-01"]
    assert c["unit_ids"] == ["U-IS-01"]
    assert c["adrs"] == ["ADR-F2"]
    assert c["substitutions"] == ["H_T-IS-1"]
    assert "§1" in c["section_cites"]


def test_extract_cites_dedupes_and_sorts() -> None:
    c = overlay.extract_cites("U-RT-05 U-RT-112 U-RT-05 C-CP-16 C-CP-16")
    assert c["unit_ids"] == ["U-RT-05", "U-RT-112"]
    assert c["spec_contracts"] == ["C-CP-16"]


def test_has_any_cite_ignores_sections() -> None:
    assert overlay._has_any_cite(overlay.extract_cites("just §5.2 here")) is False
    assert overlay._has_any_cite(overlay.extract_cites("C-IS-08")) is True


# --------------------------------------------------------------------------- #
# CXA seams (code-resident PATTERN_P1_SEAMS, not the delta-only markdown)
# --------------------------------------------------------------------------- #


def test_cxa_seams_load_31() -> None:
    seams = overlay.load_cxa_seams()
    assert len(seams) == 31
    s0 = seams[0]
    assert set(s0) == {"edge_label", "consumer_module", "producer_module", "symbol"}
    # every module name is dotted harness_*
    for s in seams:
        assert s["producer_module"].startswith("harness_")
        assert s["consumer_module"].startswith("harness_")


def test_all_cxa_seams_resolve_to_files(graph: dict) -> None:
    # the HARD-gate invariant: no genuine seam may dangle.
    assert graph["orphans"]["cxa_seam_missing_endpoint"] == []
    assert graph["stats"]["cxa_seams_wired"] == graph["stats"]["cxa_seams_total"] == 31


def test_seams_are_navigable_endpoint_resolved(graph: dict) -> None:
    # the layer code↔code graphs are blind to (stage-01 finding #3): each resolved seam
    # carries both endpoints as files + axes, not just a label.
    assert len(graph["seams"]) == 31
    rec = graph["indices"]["seam_by_label"]["U-CP-30→U-IS-12"]
    assert rec["consumer_axis"] == "CP" and rec["producer_axis"] == "IS"
    assert rec["consumer_file"].endswith("handoff_context.py")
    assert rec["producer_file"].endswith("state_ledger_entry_schema.py")
    assert rec["symbol"] == "Identifier"


def test_node_carries_resolved_seam_endpoints(graph: dict) -> None:
    by_id = {n["id"]: n for n in graph["nodes"]}
    consumer = by_id["file:harness-cp/src/harness_cp/handoff_context.py"]
    out = consumer["cxa_seams"]["outbound"]
    assert any(
        s["edge_label"] == "U-CP-30→U-IS-12" and "state_ledger_entry_schema" in s["producer_file"]
        for s in out
    )


# --------------------------------------------------------------------------- #
# substitutions
# --------------------------------------------------------------------------- #


def test_substitutions_load_55(graph: dict) -> None:
    assert graph["stats"]["substitutions_total"] == 55
    # the join is honestly thin — assert it is non-empty but a minority
    n = graph["stats"]["substitutions_with_carrier"]
    assert 1 <= n < 55


# --------------------------------------------------------------------------- #
# overlay graph shape
# --------------------------------------------------------------------------- #


def test_graph_is_ua_compatible(graph: dict) -> None:
    assert {"version", "nodes", "edges", "indices", "orphans", "stats"} <= set(graph)
    n = graph["nodes"][0]
    # UA node shape + overlay attrs
    assert {"id", "type", "name", "filePath", "ua_id"} <= set(n)
    assert {"spec_contracts", "unit_ids", "adrs", "substitutions", "cxa_role", "axis"} <= set(n)
    assert n["id"].startswith("file:")
    assert n["ua_id"].startswith("file:src/")


def test_indices_round_trip_to_nodes(graph: dict) -> None:
    # a contract in the index must point at nodes that actually carry it
    contract, files = next(iter(graph["indices"]["contract_to_files"].items()))
    by_id = {n["id"]: n for n in graph["nodes"]}
    for nid in files:
        assert contract in by_id[nid]["spec_contracts"]


def test_most_files_carry_a_cite(graph: dict) -> None:
    s = graph["stats"]
    assert s["files_with_cite"] / s["source_files"] > 0.95


def test_contract_without_code_orphans_are_derived_from_spec_keyspace(graph: dict) -> None:
    orphans = graph["orphans"]["contract_without_code"]
    cited_contracts = set(graph["indices"]["contract_to_files"])

    assert graph["stats"]["spec_contracts_total"] >= graph["stats"]["distinct_contracts"]
    for orphan in orphans:
        assert set(orphan) == {"id", "spec_files"}
        assert orphan["id"] not in cited_contracts
        assert orphan["spec_files"]


def test_edges_have_known_types(graph: dict) -> None:
    types = {e["type"] for e in graph["edges"]}
    assert types <= {"cxa_seam", "substitution_carrier"}


# --------------------------------------------------------------------------- #
# validation gate
# --------------------------------------------------------------------------- #


def test_validate_clean_on_head(graph: dict) -> None:
    # at HEAD, the only HARD class is dangling seams — which must be empty.
    seam_violations = [v for v in overlay.validate(graph) if "PATTERN_P1_SEAMS drift" in v]
    assert seam_violations == []


def test_validate_flags_a_dangling_seam(graph: dict) -> None:
    poisoned = dict(graph)
    poisoned["orphans"] = dict(graph["orphans"])
    poisoned["orphans"]["cxa_seam_missing_endpoint"] = [
        {
            "edge_label": "U-XX-99→U-YY-88",
            "symbol": "Ghost",
            "missing_producer": "harness_xx.ghost",
            "missing_consumer": None,
        }
    ]
    violations = overlay.validate(poisoned)
    assert any("PATTERN_P1_SEAMS drift" in v for v in violations)
