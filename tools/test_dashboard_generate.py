"""Tests for the roadmap dashboard generator."""

from __future__ import annotations

import importlib.util
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
