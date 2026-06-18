"""Tests for the roadmap dashboard generator."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


def _load_generate_module():
    path = Path(__file__).parent / "dashboard" / "generate.py"
    spec = importlib.util.spec_from_file_location("dashboard_generate", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retired_trend_endpoint_uses_substitution_snapshot_without_yaml(tmp_path, monkeypatch):
    generate = _load_generate_module()
    monkeypatch.setattr(generate, "_SUB_DERIVATION", None)

    harness = tmp_path / ".harness"
    harness.mkdir()
    (harness / "substitutions.yaml").write_text(
        """
snapshot:
  retired: 46
  pipeline_advanced: 49
  total_canonical: 54
substitutions: []
""".lstrip(),
        encoding="utf-8",
    )
    (harness / "phase-7d-retirement-events-batch-51.md").write_text(
        "# batch 51\n\n48/54 RETIRED\n",
        encoding="utf-8",
    )

    trend = generate.parse_retired_trend(tmp_path)

    assert trend[-1]["retired"] == 46


def _real_arc_map_md() -> str:
    # The arc-and-unit map is the single arc→unit source (replaces the parseable
    # "## Remaining forward work" section, now a pointer).
    return (Path(__file__).parents[1] / ".harness" / "r-fs-1-arc-and-unit-map.md").read_text(
        encoding="utf-8"
    )


def test_arc_unit_map_parses_all_11_arcs_in_build_order():
    # The single arc→unit source must yield all 11 arcs in the frozen build order,
    # with the 6 done arcs first and the 5 remaining following.
    generate = _load_generate_module()
    am = generate.parse_arc_unit_map(_real_arc_map_md())
    tags = [a["tag"] for a in am["arcs"]]
    assert tags == ["B1", "B3", "E", "B2", "R", "B4", "CA", "B5", "B6", "B7", "M"]
    assert [a["position"] for a in am["arcs"]] == list(range(1, 12))
    # FROZEN order COMPLETE — all 11 child arcs ✅ done (#637 closed B6, the last).
    assert [a["status"] for a in am["arcs"]] == ["done"] * 11
    by_tag = {a["tag"]: a for a in am["arcs"]}
    # cluster classification: independent vs serial vs maybe-serial.
    assert by_tag["CA"]["cluster"] == "independent"
    assert by_tag["B4"]["cluster"] == "serial"
    # M's card was finalized to "independent (parallel-safe)" when it landed (#635).
    assert by_tag["M"]["cluster"] == "independent"


def test_done_arcs_carry_real_units_remaining_arcs_anticipated():
    generate = _load_generate_module()
    am = generate.parse_arc_unit_map(_real_arc_map_md())
    by_tag = {a["tag"]: a for a in am["arcs"]}
    # done arcs carry as-built units with real U-* ids
    assert by_tag["B1"]["units_status"] == "as-built"
    assert by_tag["B1"]["units"], "B1 must list as-built units"
    assert any("U-CP-86" in u["unit"] for u in by_tag["B1"]["units"])  # PARALLELIZATION
    assert all(u["what"] for u in by_tag["B1"]["units"])  # every unit has a plain-language line
    # B4 is now done — as-built (its 4 slices extended existing contracts → 0 new U-* ids)
    assert by_tag["B4"]["units_status"] == "as-built"
    assert by_tag["B4"]["units"], "B4 must list as-built slices"
    # CA's card carries anticipated units (its card was not back-filled with as-built U-* ids
    # when it landed — pre-existing arc-map card drift; the arc *status* is done, see the
    # parse-order test). Asserting the actual parsed shape.
    assert by_tag["CA"]["units_status"] == "anticipated"
    assert by_tag["CA"]["units"], "CA must list units"
    # dependency text is carried per arc
    assert by_tag["CA"]["depends"] and by_tag["CA"]["parallel"]


def test_remaining_forward_derives_frozen_child_arcs_in_order():
    # parse_remaining_forward now DERIVES the remaining-work view from the arc map
    # (the single source), preserving the {child_arcs, standalone, done} shape that
    # compute_closure + the arc strip consume.
    generate = _load_generate_module()
    rf = generate.parse_remaining_forward(_real_arc_map_md())

    # FROZEN order COMPLETE — no remaining frozen child arcs; all 11 done in build order.
    # (R-FS-1 stays ACTIVE via the standalone B-* arcs; see test below.)
    assert [arc["id"] for arc in rf["child_arcs"]] == []
    assert rf["done"] == ["B1", "B3", "E", "B2", "R", "B4", "CA", "B5", "B6", "B7", "M"]


def test_remaining_forward_derives_standalone_arcs():
    generate = _load_generate_module()
    rf = generate.parse_remaining_forward(_real_arc_map_md())

    sa = rf["standalone"]
    by_id = {arc["id"]: arc for arc in sa}
    # §5 is the COMPLETE standalone enumeration (both families) with 4-way status.
    assert len(sa) == 16
    # design-fork-first "remaining" arcs surfaced during impl (R-FS-1's continuing work)
    family1 = {"B-FANOUT-PAUSE", "B-L2-EMBEDDING-ACTIVATION", "B-TOOL-GATE", "B-EFFECT-FENCE"}
    assert family1 <= set(by_id)
    assert by_id["B-FANOUT-PAUSE"]["status"] == "remaining"
    # closed standalone arcs (built + merged, each its own PR) carry status="closed" + the PR #.
    for cid in (
        "B-MCP-HOST-REMOTE-TRANSPORT",
        "B-MEMORY-SURFACE-BACKEND-IMPLS",
        "B-COST-DISCRIMINATOR-TAXONOMY",
        "B-NONLINEAR-OVERRIDE-PROVENANCE",
        "B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION",
        "B-INTERSTEP",
    ):
        assert by_id[cid]["status"] == "closed", cid
    assert "#640" in by_id["B-MCP-HOST-REMOTE-TRANSPORT"]["status_detail"]
    # B-TAIL is build-authorized but GATED on the R-420/R-421 collector arc.
    assert by_id["B-TAIL-CONDITIONAL-SAMPLING"]["status"] == "gated"
    # Both `resolved` arcs were settled INSIDE the frozen order -> NOT separate post-frozen
    # standalones (excluded from the closed/remaining tallies, never double-counted): B-PER-TOOL
    # built as B6 Slice 2 (#637); B-PER-DISPATCH-DRIVER-PRECISION foreclosed N/A by B6 Option A.
    assert by_id["B-PER-TOOL-SANDBOX-TIER"]["status"] == "resolved"
    assert by_id["B-PER-DISPATCH-DRIVER-PRECISION"]["status"] == "resolved"
    # 4-way bucket counts: 6 closed / 7 remaining / 1 gated / 2 resolved.
    statuses = [arc["status"] for arc in sa]
    assert statuses.count("closed") == 6
    assert statuses.count("remaining") == 7
    assert statuses.count("gated") == 1
    assert statuses.count("resolved") == 2


def test_compute_closure_counts_standalone_by_status():
    # The rfs1 headline carries the standalone status breakdown the masthead renders:
    # closed/remaining/gated/resolved, with `standalone_buildable` = closed + remaining
    # (excludes gated + frozen-resolved so the frozen B6 Slice 2 isn't double-counted).
    generate = _load_generate_module()
    dashboard = {
        "retirement": {},
        "remaining_forward": {
            "child_arcs": [],
            "standalone": [
                {"id": "B-A", "status": "closed"},
                {"id": "B-B", "status": "closed"},
                {"id": "B-C", "status": "remaining"},
                {"id": "B-D", "status": "gated"},
                {"id": "B-E", "status": "resolved"},
            ],
        },
    }
    rfs1 = generate.compute_closure([], dashboard)["rfs1"]
    assert rfs1["standalone_closed"] == 2
    assert rfs1["standalone_remaining"] == 1
    assert rfs1["standalone_gated"] == 1
    assert rfs1["standalone_resolved"] == 1
    assert rfs1["standalone_buildable"] == 3


def test_remaining_excludes_closed_and_done_arcs():
    # Closed/done items must never resurface in the curated remaining list.
    generate = _load_generate_module()
    rf = generate.parse_remaining_forward(_real_arc_map_md())

    blob = " ".join(arc["id"] + arc["label"] for arc in rf["child_arcs"])
    for closed in ("R-411", "R-412", "R-901", "R-CXA-1", "R-300"):
        assert closed not in blob
    # done child arcs (B1/E/B2) are not in the remaining itemization
    ids = {arc["id"] for arc in rf["child_arcs"]}
    assert "R-FS-1·B1" not in ids
    assert "R-FS-1·E" not in ids


def test_assert_remaining_nonempty_raises_on_silent_empty():
    # The fail-loud guard: R-FS-1 ACTIVE + zero parsed child arcs (a drifted source)
    # must raise, not silently render an empty panel.
    generate = _load_generate_module()
    actions = [{"id": "R-FS-1", "status": "ACTIVE"}]

    import pytest

    with pytest.raises(RuntimeError, match="remaining-work source has drifted"):
        generate.assert_remaining_nonempty(actions, {"remaining_forward": {"child_arcs": []}})

    # standalone arcs that are all closed/resolved are NOT remaining work -> still raises
    # (guarding on a merely non-empty list would mask drift once everything is built).
    with pytest.raises(RuntimeError, match="remaining-work source has drifted"):
        generate.assert_remaining_nonempty(
            actions,
            {
                "remaining_forward": {
                    "child_arcs": [],
                    "standalone": [
                        {"id": "B-X", "status": "closed"},
                        {"id": "B-Y", "status": "resolved"},
                    ],
                }
            },
        )

    # an OPEN (remaining/gated) standalone arc keeps the panel non-empty -> no raise
    generate.assert_remaining_nonempty(
        actions,
        {"remaining_forward": {"child_arcs": [], "standalone": [{"id": "B-Z", "status": "gated"}]}},
    )

    # populated child arcs -> no raise
    generate.assert_remaining_nonempty(
        actions, {"remaining_forward": {"child_arcs": [{"id": "R-FS-1·B4"}]}}
    )


def test_compute_closure_sources_remaining_from_dashboard():
    generate = _load_generate_module()
    dashboard = {
        "retirement": {},
        "remaining_forward": {
            "child_arcs": [
                {"n": 1, "id": "R-FS-1·B4", "label": "x", "layer": "build", "gate": "g"}
            ],
            "standalone": [{"id": "B-INTERSTEP", "axis": "runtime", "shape": "s"}],
        },
    }
    closure = generate.compute_closure([], dashboard)

    assert [r["id"] for r in closure["remaining"]] == ["R-FS-1·B4"]
    assert [s["id"] for s in closure["standalone"]] == ["B-INTERSTEP"]


def test_dashboard_status_filters_default_closed_off():
    generate = _load_generate_module()

    html = generate.render_html(
        {
            "live_head": "abc123",
            "dashboard": {},
            "actions": [],
            "open_prs": [],
            "cadence": [],
            "pr_cadence": [],
            "retired_trend": [],
            "depgraph": {},
            "axis_retirement": [],
            "operator_gates": [],
            "post_phase_8": {},
            "closure": {},
        }
    )

    assert 'id="status-board-filters"' in html
    assert 'id="pp8-board-filters"' in html
    assert 'label !== "closed"' in html


def test_activation_open_count_matches_current_forward_catalog():
    generate = _load_generate_module()
    roadmap = (Path(__file__).parents[1] / "Project_Roadmap_v1.md").read_text(encoding="utf-8")
    actions = generate.parse_roadmap_actions(roadmap)

    closure = generate.compute_closure(actions, {"retirement": {}})

    # Point-in-time forward-catalog check (update when the catalog changes): the
    # activation axis = open forward-surface + R-CXA items. 2 open / 25 total at HEAD
    # (R-CL-P1/P2 reconciled DEFERRED→RESOLVED — superseded by R-FS-1 arc R/E).
    assert closure["activation"]["open"] == 2
    assert closure["activation"]["total"] == 25


def test_closed_xi_and_r901_items_do_not_appear_in_remaining_cards():
    generate = _load_generate_module()
    roadmap = (Path(__file__).parents[1] / "Project_Roadmap_v1.md").read_text(encoding="utf-8")
    actions = generate.parse_roadmap_actions(roadmap)

    closure = generate.compute_closure(actions, {"retirement": {}})

    remaining_text = "\n".join(
        f"{item['id']} {item['label']} {item['gate']}" for item in closure["remaining"]
    )
    assert "R-XI-02" not in remaining_text
    assert "R-XI-03" not in remaining_text
    assert "R-901" not in remaining_text


def test_resolved_r411_r412_do_not_appear_in_remaining_cards():
    generate = _load_generate_module()
    roadmap = (Path(__file__).parents[1] / "Project_Roadmap_v1.md").read_text(encoding="utf-8")
    actions = generate.parse_roadmap_actions(roadmap)

    closure = generate.compute_closure(actions, {"retirement": {}})

    remaining_text = "\n".join(
        f"{item['id']} {item['label']} {item['gate']}" for item in closure["remaining"]
    )
    assert "R-411" not in remaining_text
    assert "R-412" not in remaining_text


def test_live_anchor_derives_masthead_values_from_git_and_filesystem(tmp_path):
    generate = _load_generate_module()

    harness = tmp_path / ".harness"
    harness.mkdir()
    (harness / "class_1_fork_example.md").write_text("status\n", encoding="utf-8")
    (harness / "class_3_fork_example.md").write_text("status\n", encoding="utf-8")
    (harness / "phase-7d-retirement-events-batch-53.md").write_text("old\n", encoding="utf-8")
    latest = harness / "phase-7d-retirement-events-batch-54.md"
    latest.write_text("new\n", encoding="utf-8")

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "tracked.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "ops: roadmap status refresh post-test (#399)"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    anchor = generate.build_live_anchor(
        tmp_path,
        [{"number": 7, "branch": "codex/example"}],
    )

    assert anchor["git_head"]
    assert anchor["fork_count"] == "2"
    assert anchor["latest_retirement_batch"] == ".harness/phase-7d-retirement-events-batch-54.md"
    assert anchor["recent_prs"][0]["pr"].startswith("PR #399")
    assert anchor["hash"] == generate.compute_workspace_state_hash(
        git_head=anchor["git_head"],
        open_prs=[{"number": 7, "branch": "codex/example"}],
        open_fork_doc_count=2,
        latest_retirement_batch_path=".harness/phase-7d-retirement-events-batch-54.md",
    )


def test_dashboard_template_has_no_literal_currentness_counts():
    generate = _load_generate_module()

    assert "8 rows below" not in generate.HTML_TEMPLATE
    assert "6 of 20" not in generate.HTML_TEMPLATE
    assert "const live = DATA.live_anchor" in generate.HTML_TEMPLATE
    assert "live.fork_count || d.fork_count" in generate.HTML_TEMPLATE
