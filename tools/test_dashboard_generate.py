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


def test_resolved_actions_are_omitted_from_remaining_order(monkeypatch):
    generate = _load_generate_module()
    monkeypatch.setattr(generate, "_SUB_DERIVATION", None)

    closure = generate.compute_closure(
        [
            {
                "id": "R-300-multi-llm-second-provider",
                "surface": "IV",
                "status": "RESOLVED",
            },
        ],
        {"retirement": {}},
    )

    remaining_ids = {item["id"] for item in closure["remaining"]}
    assert "R-300-multi-llm-second-provider" not in remaining_ids


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

    assert closure["activation"]["open"] == 3
    assert closure["activation"]["total"] == 21


def test_closed_xi_items_do_not_appear_in_remaining_cards():
    generate = _load_generate_module()
    roadmap = (Path(__file__).parents[1] / "Project_Roadmap_v1.md").read_text(encoding="utf-8")
    actions = generate.parse_roadmap_actions(roadmap)

    closure = generate.compute_closure(actions, {"retirement": {}})

    remaining_text = "\n".join(
        f"{item['id']} {item['label']} {item['gate']}" for item in closure["remaining"]
    )
    assert "R-XI-02" not in remaining_text
    assert "R-XI-03" not in remaining_text
    assert "R-901" in remaining_text


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
