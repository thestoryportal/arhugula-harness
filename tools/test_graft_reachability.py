#!/usr/bin/env python3
"""Tests for `tools/graft_reachability.py`.

Both directions for every rule, per this repo's gate discipline: the detector fires on the
shape it exists to catch, AND stays silent on the look-alike that is not that shape. A
detector that fires on everything gets muted within two rounds.

These build a synthetic wiring graph rather than reading the real one. `graft/.graph/
wiring.json` is a gitignored, per-checkout build artifact that does not exist in CI, so a
test against the live graph would either be unrunnable there or would silently pass on an
empty graph — the exact `[[gate-cannot-tell-empty-from-unlooked]]` failure this module is
written to avoid. The one thing that MUST be tested against reality is the missing-graph
path, and that is asserted directly.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import graft_reachability as gr

SRC = "harness-cp/src/harness_cp/thing.py"
TEST = "harness-cp/tests/test_thing.py"


def _node(path: str, name: str, *, kind: str = "function", exported: bool = False) -> dict:
    return {
        "id": f"{path}#{name}",
        "name": name,
        "kind": kind,
        "path": path,
        "span": "L1-L9",
        "exported": exported,
    }


def _graph(nodes: list[dict], calls: list[tuple[str, str]]) -> dict:
    return {
        "nodes": nodes,
        "edges": [
            {"source": s, "target": t, "relation": "calls", "confidence": "extracted"}
            for s, t in calls
        ],
    }


# --- the detector fires -------------------------------------------------------


def test_fires_on_a_src_symbol_called_only_by_tests() -> None:
    graph = _graph(
        [_node(SRC, "_helper"), _node(TEST, "test_helper")],
        [(f"{TEST}#test_helper", f"{SRC}#_helper")],
    )
    findings = gr.derive(graph)
    assert [f.name for f in findings] == ["_helper"]
    assert findings[0].test_callers == 1
    assert findings[0].exported is False


def test_counts_every_test_caller() -> None:
    graph = _graph(
        [_node(SRC, "_helper"), _node(TEST, "t1"), _node(TEST, "t2")],
        [(f"{TEST}#t1", f"{SRC}#_helper"), (f"{TEST}#t2", f"{SRC}#_helper")],
    )
    assert gr.derive(graph)[0].test_callers == 2


def test_conftest_counts_as_a_test_caller() -> None:
    conf = "harness-cp/conftest.py"
    graph = _graph(
        [_node(SRC, "_helper"), _node(conf, "fixture")],
        [(f"{conf}#fixture", f"{SRC}#_helper")],
    )
    assert [f.name for f in gr.derive(graph)] == ["_helper"]


# --- the detector stays silent ------------------------------------------------


def test_silent_when_a_production_caller_exists() -> None:
    """One production caller is enough — the mechanism's other half exists."""
    other = "harness-cp/src/harness_cp/api.py"
    graph = _graph(
        [_node(SRC, "_helper"), _node(TEST, "t1"), _node(other, "run")],
        [(f"{TEST}#t1", f"{SRC}#_helper"), (f"{other}#run", f"{SRC}#_helper")],
    )
    assert gr.derive(graph) == []


def test_silent_on_zero_inbound_edges() -> None:
    """Entry points and public API have no callers by design; that set is not the signal."""
    graph = _graph([_node(SRC, "main")], [])
    assert gr.derive(graph) == []


def test_silent_on_a_production_reference_rather_than_a_call() -> None:
    """The `_on_drain_signal` false positive: registered as a callback, never called.

    `loop.add_signal_handler(sig, _on_drain_signal, ctx)` produces no `calls` edge, so the
    call-edge pass alone reports it. The AST reference set is what rescues it.
    """
    graph = _graph(
        [_node(SRC, "_on_drain_signal"), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{SRC}#_on_drain_signal")],
    )
    assert [f.name for f in gr.derive(graph, set())] == ["_on_drain_signal"]
    assert gr.derive(graph, {"_on_drain_signal"}) == []


def test_silent_on_symbols_outside_harness_src() -> None:
    """`tools/` and test-defined helpers are not the subject; only shipped source is."""
    tool = "tools/some_script.py"
    graph = _graph(
        [_node(tool, "_helper"), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{tool}#_helper")],
    )
    assert gr.derive(graph) == []


def test_silent_on_non_callable_kinds() -> None:
    """A class is reached by construction; `calls` edges model that differently."""
    graph = _graph(
        [_node(SRC, "Thing", kind="class"), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{SRC}#Thing")],
    )
    assert gr.derive(graph) == []


def test_non_call_relations_are_ignored() -> None:
    """An `imports` edge from production is not evidence the symbol is invoked."""
    other = "harness-cp/src/harness_cp/api.py"
    graph = _graph(
        [_node(SRC, "_helper"), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{SRC}#_helper")],
    )
    graph["edges"].append(
        {"source": f"{other}#run", "target": f"{SRC}#_helper", "relation": "imports"}
    )
    assert [f.name for f in gr.derive(graph)] == ["_helper"]


# --- classification + ordering ------------------------------------------------


def test_exported_symbols_are_flagged_not_dropped() -> None:
    graph = _graph(
        [_node(SRC, "public_fn", exported=True), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{SRC}#public_fn")],
    )
    findings = gr.derive(graph)
    assert len(findings) == 1 and findings[0].exported is True


def test_findings_sort_by_descending_test_caller_count() -> None:
    graph = _graph(
        [_node(SRC, "few"), _node(SRC, "many"), _node(TEST, "t1"), _node(TEST, "t2")],
        [
            (f"{TEST}#t1", f"{SRC}#few"),
            (f"{TEST}#t1", f"{SRC}#many"),
            (f"{TEST}#t2", f"{SRC}#many"),
        ],
    )
    assert [f.name for f in gr.derive(graph)] == ["many", "few"]


def test_dunder_all_membership_promotes_an_underscore_name_to_exported() -> None:
    """A `_name` deliberately published via `__all__` is a design choice, not an oversight.

    `harness-od/src/harness_od/pause_resume_namespace.py` really does this. Reporting such
    a symbol as "private, actionable" manufactures urgency for intentional API surface.
    """
    graph = _graph(
        [_node(SRC, "_published"), _node(TEST, "t1")],
        [(f"{TEST}#t1", f"{SRC}#_published")],
    )
    assert gr.derive(graph, set(), set())[0].exported is False
    assert gr.derive(graph, set(), {"_published"})[0].exported is True


def test_dunder_all_extraction_reads_list_and_tuple_forms(tmp_path: Path) -> None:
    lst = tmp_path / "a.py"
    lst.write_text('__all__ = ["_a", "_b"]\n')
    tup = tmp_path / "b.py"
    tup.write_text('__all__ = ("_c",)\n')
    assert gr.dunder_all_names([lst, tup]) == {"_a", "_b", "_c"}


def test_dunder_all_extraction_ignores_other_assignments(tmp_path: Path) -> None:
    """Only `__all__` publishes; an unrelated list of strings must not promote anything."""
    f = tmp_path / "m.py"
    f.write_text('_REGISTRY = ["_a"]\n')
    assert gr.dunder_all_names([f]) == set()


# --- the AST reference pass ---------------------------------------------------


def test_ast_pass_finds_a_callback_argument(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_text("def register(loop):\n    loop.add_signal_handler(1, _on_drain, None)\n")
    assert "_on_drain" in gr.production_references([f])


def test_ast_pass_finds_an_attribute_reference(tmp_path: Path) -> None:
    f = tmp_path / "m.py"
    f.write_text("def go(obj):\n    return obj._helper\n")
    assert "_helper" in gr.production_references([f])


def test_a_definition_is_not_a_reference_to_itself(tmp_path: Path) -> None:
    """Otherwise every symbol would self-rescue and the detector would never fire."""
    f = tmp_path / "m.py"
    f.write_text("def _helper():\n    return 1\n")
    assert "_helper" not in gr.production_references([f])


def test_unparseable_file_is_skipped_without_emptying_the_set(tmp_path: Path) -> None:
    good = tmp_path / "good.py"
    good.write_text("x = _wanted\n")
    bad = tmp_path / "bad.py"
    bad.write_text("def (((\n")
    assert "_wanted" in gr.production_references([bad, good])


# --- fail-loud posture --------------------------------------------------------


def test_missing_graph_raises_rather_than_returning_empty(tmp_path: Path) -> None:
    """ "Could not look" must never be indistinguishable from "looked, found nothing"."""
    with pytest.raises(gr.GraphUnavailableError) as exc:
        gr.load_graph(tmp_path)
    assert "graft build" in str(exc.value)


def test_unparseable_graph_raises(tmp_path: Path) -> None:
    target = tmp_path / gr.WIRING
    target.parent.mkdir(parents=True)
    target.write_text("{not json")
    with pytest.raises(gr.GraphUnavailableError):
        gr.load_graph(tmp_path)


def test_wrong_shape_graph_raises(tmp_path: Path) -> None:
    target = tmp_path / gr.WIRING
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"something": "else"}))
    with pytest.raises(gr.GraphUnavailableError):
        gr.load_graph(tmp_path)


def _checkout(tmp_path: Path, *, graph_first: bool) -> Path:
    """A miniature checkout with a wiring graph and one indexed source file.

    `os.utime` sets both mtimes explicitly rather than relying on write order — a
    near-boundary fixture age is a sawtooth by clock phase, per
    `[[touch-t-truncation-eats-boundary-headroom]]`, and an ordering assertion that
    depends on how fast the test machine writes two files is not an assertion.
    """
    graph = tmp_path / gr.WIRING
    graph.parent.mkdir(parents=True)
    graph.write_text(json.dumps({"nodes": [], "edges": []}))
    src = tmp_path / "harness-cp" / "src" / "harness_cp" / "m.py"
    src.parent.mkdir(parents=True)
    src.write_text("x = 1\n")
    graph_t, src_t = (100.0, 50.0) if graph_first else (50.0, 100.0)
    os.utime(graph, (graph_t, graph_t))
    os.utime(src, (src_t, src_t))
    return tmp_path


def test_a_graph_older_than_an_indexed_source_is_refused(tmp_path: Path) -> None:
    """Codex P2: an existing-but-stale graph yields confidently wrong edges at exit 0."""
    root = _checkout(tmp_path, graph_first=False)
    assert gr.stale_sources(root)
    with pytest.raises(gr.GraphUnavailableError) as exc:
        gr.collect(root)
    assert "graft build" in str(exc.value)


def test_a_graph_newer_than_every_indexed_source_is_accepted(tmp_path: Path) -> None:
    """The other direction — a fresh graph must not be refused, or the tool is unusable."""
    root = _checkout(tmp_path, graph_first=True)
    assert gr.stale_sources(root) == []
    assert gr.collect(root) == []


def test_staleness_check_is_inert_when_there_is_no_graph(tmp_path: Path) -> None:
    """Absence is `load_graph`'s error to raise; the staleness probe must not preempt it."""
    assert gr.stale_sources(tmp_path) == []


def test_cli_exits_2_and_reports_nothing_when_the_graph_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.chdir(tmp_path)
    assert gr.main([]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "CANNOT LOOK" in captured.err


# --- rendering ----------------------------------------------------------------


def test_render_carries_the_triage_caveat() -> None:
    """The caveat is load-bearing: this output is a triage list, not a defect list."""
    out = gr.render([], show_all=False)
    assert "TRIAGE LIST, NOT A DEFECT LIST" in out


def test_render_hides_exported_rows_unless_asked() -> None:
    findings = [
        gr.Finding("pub", SRC, "L1-L9", 1, True),
        gr.Finding("_priv", SRC, "L1-L9", 1, False),
    ]
    assert "pub" not in gr.render(findings, show_all=False)
    assert "pub" in gr.render(findings, show_all=True)
