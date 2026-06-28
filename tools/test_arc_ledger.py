"""Tests for the arc ledger (roadmap-dashboard overhaul).

Mirrors `tools/test_substitution_ledger.py`: the live ledger must pass validation,
the derived counts must match the snapshot pin (NO inline magic numbers — when a
transit happens the snapshot bump + this test move together), and a battery of
NEGATIVE tests proves each gate failure-class is actually caught.
"""

from __future__ import annotations

import copy

import arc_ledger


def _data() -> dict:
    return arc_ledger.load()


def test_live_ledger_passes_validation() -> None:
    assert arc_ledger.validate(_data()) == []


def test_derived_counts_match_snapshot_pin() -> None:
    """Counts are DERIVED, asserted against the file's own snapshot — not magic numbers."""
    data = _data()
    d = arc_ledger.derive(data)
    snap = data["snapshot"]
    for key in (
        "frozen_total",
        "frozen_done",
        "standalone_closed",
        "standalone_gated",
        "standalone_resolved",
        "standalone_registered",
    ):
        assert d[key] == snap[key], f"{key}: derived {d[key]} != snapshot {snap[key]}"


def test_contract_frozen_arcs_sorted_with_units() -> None:
    d = arc_ledger.derive(_data())
    positions = [a["position"] for a in d["frozen"]]
    assert positions == sorted(positions), "frozen arcs must be position-sorted"
    assert all(a.get("units") for a in d["frozen"]), "every frozen arc carries as-built units"


def test_contract_closed_standalone_carry_a_deliverable() -> None:
    d = arc_ledger.derive(_data())
    for a in d["standalone"]:
        if a["status"] == "closed":
            assert a.get("pr") or a.get("units") or a.get("spec_delta"), (
                f"{a['id']}: closed arc must cite a deliverable"
            )


def test_contract_registered_arcs_have_parent_and_no_units() -> None:
    d = arc_ledger.derive(_data())
    ids = {a["id"] for a in d["frozen"] + d["standalone"]}
    registered = [a for a in d["standalone"] if a["status"] == "registered"]
    if not registered:
        assert d["rfs1_status"] in arc_ledger.RFS1_ZERO_OPEN_ALLOWED
        return
    for a in registered:
        assert a.get("decompose_at_open") is True
        assert a.get("parent_arc") in ids
        assert not [u for u in (a.get("units") or []) if u.get("id")], (
            f"{a['id']}: registered arc must not fabricate U-* units"
        )


# --- negative tests: each gate failure-class is caught ----------------------


def _violates(mutate) -> bool:
    data = copy.deepcopy(_data())
    mutate(data)
    return arc_ledger.validate(data) != []


def _first_registered(data: dict) -> dict:
    for a in data["arcs"]:
        if a.get("status") == "registered":
            return a

    a = _first_closed_standalone(data)
    a["status"] = "registered"
    a["decompose_at_open"] = True
    a["parent_arc"] = data["arcs"][0]["id"]
    a["anticipated_scope"] = "synthetic registered scope for negative validation tests"
    a.pop("pr", None)
    a.pop("spec_delta", None)
    a["units"] = []
    data["snapshot"]["standalone_closed"] -= 1
    data["snapshot"]["standalone_registered"] += 1
    data["snapshot"]["rfs1_status"] = "active"
    return a


def _first_closed_standalone(data: dict) -> dict:
    return next(
        a for a in data["arcs"] if a.get("kind") == "standalone" and a.get("status") == "closed"
    )


def test_negative_registered_with_unit_id_fails() -> None:
    def m(data):
        _first_registered(data)["units"] = [{"id": "U-RT-999", "what": "fabricated"}]

    assert _violates(m)


def test_negative_registered_missing_decompose_marker_fails() -> None:
    def m(data):
        _first_registered(data)["decompose_at_open"] = False

    assert _violates(m)


def test_negative_registered_unknown_parent_fails() -> None:
    def m(data):
        _first_registered(data)["parent_arc"] = "B-DOES-NOT-EXIST"

    assert _violates(m)


def test_negative_closed_without_deliverable_fails() -> None:
    def m(data):
        a = _first_closed_standalone(data)
        a.pop("pr", None)
        a.pop("units", None)
        a.pop("spec_delta", None)

    assert _violates(m)


def test_negative_duplicate_id_fails() -> None:
    def m(data):
        data["arcs"].append(copy.deepcopy(data["arcs"][0]))

    assert _violates(m)


def test_negative_status_flip_without_snapshot_bump_fails() -> None:
    """A registered arc silently flipped to closed (no snapshot bump) must fail."""

    def m(data):
        a = _first_registered(data)
        a["status"] = "closed"
        a["pr"] = "#999"
        # snapshot NOT bumped → counts drift → caught

    assert _violates(m)


def test_negative_drift_empty_forward_register_fails() -> None:
    """All open arcs removed while R-FS-1 is ACTIVE = drift (the FATAL twin)."""

    def m(data):
        data["arcs"] = [
            a for a in data["arcs"] if a.get("status") not in arc_ledger.OPEN_STANDALONE
        ]
        # bump snapshot to zero so ONLY the drift guard fires (isolate the failure class)
        data["snapshot"]["standalone_gated"] = 0
        data["snapshot"]["standalone_registered"] = 0
        data["snapshot"]["rfs1_status"] = "active"

    assert _violates(m)


def test_empty_forward_register_allowed_when_tier1_manual_pending() -> None:
    """The build register may be empty while manual Tier-1 closure gates remain pending."""

    data = arc_ledger.load()
    data["arcs"] = [
        {**a, "status": "closed", "pr": a.get("pr") or "#999"}
        if a.get("status") in arc_ledger.OPEN_STANDALONE
        else a
        for a in data["arcs"]
    ]
    d = arc_ledger.derive(data)
    data["snapshot"]["standalone_closed"] = d["standalone_closed"]
    data["snapshot"]["standalone_gated"] = d["standalone_gated"]
    data["snapshot"]["standalone_registered"] = d["standalone_registered"]
    data["snapshot"]["rfs1_status"] = "tier1_manual_pending"

    assert arc_ledger.validate(data) == []


def test_empty_forward_register_allowed_when_rfs1_resolved() -> None:
    """The terminal state is valid with an explicit R-FS-1 resolved snapshot pin."""

    data = arc_ledger.load()
    data["arcs"] = [
        {**a, "status": "closed", "pr": a.get("pr") or "#999"}
        if a.get("status") in arc_ledger.OPEN_STANDALONE
        else a
        for a in data["arcs"]
    ]
    d = arc_ledger.derive(data)
    data["snapshot"]["standalone_closed"] = d["standalone_closed"]
    data["snapshot"]["standalone_gated"] = d["standalone_gated"]
    data["snapshot"]["standalone_registered"] = d["standalone_registered"]
    data["snapshot"]["rfs1_status"] = "resolved"

    assert arc_ledger.validate(data) == []


def test_negative_unknown_rfs1_status_fails() -> None:
    def m(data):
        data["snapshot"]["rfs1_status"] = "done-ish"

    assert _violates(m)


def test_negative_frozen_bad_position_fails() -> None:
    def m(data):
        next(a for a in data["arcs"] if a.get("kind") == "frozen")["position"] = 99

    assert _violates(m)
