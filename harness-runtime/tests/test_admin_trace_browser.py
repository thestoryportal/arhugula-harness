"""B-OD19-LOCAL-INSPECTION slice (a) — TUI trace browser tests.

Acceptance per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §3:
"browser walks a seeded ring buffer + renders the five primitives (scripted
TUI test or headless render harness)". These tests exercise the pure
`compute_operator_burden_rollups` + `render_operator_burden_screen` functions
directly — no live terminal required — plus `open_readonly_span_store`'s
read-only-invariant + not-found behavior. The curses driver itself
(`run_trace_browser_tui`) is a thin, untestable-without-a-terminal loop over
these pure functions; its wiring is covered by `test_admin_inspect.py`'s
`--browse` CLI tests (monkeypatched `curses.wrapper`).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from harness_od.operator_burden_eval_primitives import (
    EVAL_PRIMITIVE_DECLARATIONS,
    OperatorBurdenEvalPrimitive,
)
from harness_od.sqlite_span_store import SpanInsertRow, initialize_span_store, insert_spans
from harness_runtime.admin.trace_browser import (
    compute_operator_burden_rollups,
    open_readonly_span_store,
    render_operator_burden_screen,
)


def _span(
    span_id: str,
    *,
    name: str,
    attributes_json: str = "{}",
) -> SpanInsertRow:
    return SpanInsertRow(
        span_id=span_id,
        trace_id="t1",
        parent_span_id=None,
        name=name,
        kind=0,
        start_time_ns=0,
        end_time_ns=1,
        status_code=0,
        status_message=None,
        attributes_json=attributes_json,
        events_json="[]",
        workflow_id=None,
        workflow_run_id=None,
        workflow_idempotency_key=None,
    )


@pytest.fixture()
def conn(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    c = initialize_span_store(tmp_path / "spans.db")
    yield c
    c.close()


# ---------------------------------------------------------------------------
# compute_operator_burden_rollups.
# ---------------------------------------------------------------------------


def test_rollups_cover_all_five_primitives_in_canonical_order(
    conn: sqlite3.Connection,
) -> None:
    rollups = compute_operator_burden_rollups(conn)
    assert len(rollups) == 5
    assert [r.declaration.primitive for r in rollups] == [
        d.primitive for d in EVAL_PRIMITIVE_DECLARATIONS
    ]


def test_rollup_counter_primitive_counts_matching_spans(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span("s1", name="hitl.invocation.responded"),
            _span("s2", name="hitl.invocation.responded"),
            _span("s3", name="sandbox.violation"),
        ],
    )
    rollups = compute_operator_burden_rollups(conn)
    by_primitive = {r.declaration.primitive: r for r in rollups}
    assert (
        by_primitive[
            OperatorBurdenEvalPrimitive.EXPECTED_HITL_INVOCATIONS_PER_SESSION
        ].matching_span_count
        == 2
    )
    assert (
        by_primitive[
            OperatorBurdenEvalPrimitive.EXPECTED_SANDBOX_VIOLATIONS_PER_SESSION
        ].matching_span_count
        == 1
    )


def test_rollup_zero_when_no_matching_spans(conn: sqlite3.Connection) -> None:
    rollups = compute_operator_burden_rollups(conn)
    assert all(r.matching_span_count == 0 for r in rollups)
    assert all(r.value is None for r in rollups)


def test_rollup_cache_hit_ratio_computed_from_attributes(conn: sqlite3.Connection) -> None:
    insert_spans(
        conn,
        [
            _span(
                "s1",
                name="anthropic.cache",
                attributes_json=(
                    '{"anthropic.cache_read_input_tokens": 300, '
                    '"anthropic.cache_creation_input_tokens": 100}'
                ),
            ),
        ],
    )
    rollups = compute_operator_burden_rollups(conn)
    by_primitive = {r.declaration.primitive: r for r in rollups}
    cache_rollup = by_primitive[OperatorBurdenEvalPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR]
    assert cache_rollup.value == pytest.approx(0.75)


def test_rollup_ignores_non_object_attributes_json(conn: sqlite3.Connection) -> None:
    """`attributes_json` decoding to a list/scalar (not a dict) must not crash
    the rollup — it contributes zero, same as unparseable JSON."""
    insert_spans(
        conn,
        [
            _span("s1", name="anthropic.cache", attributes_json="[1, 2, 3]"),
            _span("s2", name="anthropic.cache", attributes_json='"just a string"'),
        ],
    )
    rollups = compute_operator_burden_rollups(conn)
    by_primitive = {r.declaration.primitive: r for r in rollups}
    cache_rollup = by_primitive[OperatorBurdenEvalPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR]
    assert cache_rollup.value is None
    assert cache_rollup.matching_span_count == 2


def test_rollup_ignores_non_numeric_cache_token_values(conn: sqlite3.Connection) -> None:
    """A malformed (non-numeric) token attribute value must not raise —
    contributes zero to the ratio rather than crashing the whole rollup."""
    insert_spans(
        conn,
        [
            _span(
                "s1",
                name="anthropic.cache",
                attributes_json='{"anthropic.cache_read_input_tokens": "not-a-number"}',
            ),
            _span(
                "s2",
                name="anthropic.cache",
                attributes_json='{"anthropic.cache_creation_input_tokens": 50}',
            ),
        ],
    )
    rollups = compute_operator_burden_rollups(conn)
    by_primitive = {r.declaration.primitive: r for r in rollups}
    cache_rollup = by_primitive[OperatorBurdenEvalPrimitive.CACHE_HIT_RATE_ALIGNMENT_FLOOR]
    # "not-a-number" contributes 0 to read_total; s2's 50 lands in creation_total.
    assert cache_rollup.value == pytest.approx(0.0)


def test_rollup_holdout_primitives_share_meta_eval_span_class(
    conn: sqlite3.Connection,
) -> None:
    """§17.1 declares `source_span_class="meta-eval"` for both holdout-evaluable
    primitives — spec fidelity means both rollups see the same matching count,
    not an under-differentiated query."""
    insert_spans(conn, [_span("s1", name="meta-eval"), _span("s2", name="meta-eval")])
    rollups = compute_operator_burden_rollups(conn)
    by_primitive = {r.declaration.primitive: r for r in rollups}
    assert (
        by_primitive[OperatorBurdenEvalPrimitive.SANDBOX_TIER_ROUTING_ACCURACY].matching_span_count
        == 2
    )
    assert (
        by_primitive[OperatorBurdenEvalPrimitive.ROUTING_ACCURACY_HOLDOUT].matching_span_count == 2
    )


# ---------------------------------------------------------------------------
# render_operator_burden_screen (pure — headless render harness).
# ---------------------------------------------------------------------------


def test_render_includes_all_primitive_names(conn: sqlite3.Connection) -> None:
    rollups = compute_operator_burden_rollups(conn)
    lines = render_operator_burden_screen(rollups, selected_index=0)
    blob = "\n".join(lines)
    for declaration in EVAL_PRIMITIVE_DECLARATIONS:
        assert declaration.primitive.value in blob


def test_render_marks_selected_row(conn: sqlite3.Connection) -> None:
    rollups = compute_operator_burden_rollups(conn)
    lines = render_operator_burden_screen(rollups, selected_index=2)
    marked = [
        line
        for line in lines
        if line.startswith(">") and rollups[2].declaration.primitive.value in line
    ]
    assert len(marked) == 1


def test_render_shows_holdout_annotation_for_holdout_evaluable_primitive(
    conn: sqlite3.Connection,
) -> None:
    rollups = compute_operator_burden_rollups(conn)
    lines = render_operator_burden_screen(rollups, selected_index=0)
    blob = "\n".join(lines)
    assert "B-OD17" in blob


def test_render_shows_ratio_for_cache_primitive_when_computed(
    conn: sqlite3.Connection,
) -> None:
    insert_spans(
        conn,
        [
            _span(
                "s1",
                name="anthropic.cache",
                attributes_json='{"anthropic.cache_read_input_tokens": 100}',
            ),
        ],
    )
    rollups = compute_operator_burden_rollups(conn)
    lines = render_operator_burden_screen(rollups, selected_index=0)
    blob = "\n".join(lines)
    assert "ratio=1.000" in blob


def test_render_respects_width_bound(conn: sqlite3.Connection) -> None:
    rollups = compute_operator_burden_rollups(conn)
    lines = render_operator_burden_screen(rollups, selected_index=0, width=20)
    assert all(len(line) <= 20 for line in lines)


def test_render_is_pure_deterministic(conn: sqlite3.Connection) -> None:
    rollups = compute_operator_burden_rollups(conn)
    a = render_operator_burden_screen(rollups, selected_index=1)
    b = render_operator_burden_screen(rollups, selected_index=1)
    assert a == b


# ---------------------------------------------------------------------------
# open_readonly_span_store.
# ---------------------------------------------------------------------------


def test_open_readonly_span_store_reads_existing_rows(tmp_path: Path) -> None:
    db_path = tmp_path / "spans.db"
    setup_conn = initialize_span_store(db_path)
    insert_spans(setup_conn, [_span("s1", name="hitl.invocation.responded")])
    setup_conn.close()

    ro_conn = open_readonly_span_store(db_path)
    try:
        rollups = compute_operator_burden_rollups(ro_conn)
    finally:
        ro_conn.close()
    by_primitive = {r.declaration.primitive: r for r in rollups}
    assert (
        by_primitive[
            OperatorBurdenEvalPrimitive.EXPECTED_HITL_INVOCATIONS_PER_SESSION
        ].matching_span_count
        == 1
    )


def test_open_readonly_span_store_rejects_writes(tmp_path: Path) -> None:
    db_path = tmp_path / "spans.db"
    initialize_span_store(db_path).close()

    ro_conn = open_readonly_span_store(db_path)
    try:
        with pytest.raises(sqlite3.OperationalError):
            ro_conn.execute("INSERT INTO spans (span_id) VALUES ('x')")
    finally:
        ro_conn.close()


def test_open_readonly_span_store_missing_file_raises(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.db"
    with pytest.raises(sqlite3.OperationalError):
        open_readonly_span_store(missing)


@pytest.mark.parametrize("name", ["a?b.db", "a#b.db", "a b.db"])
def test_open_readonly_span_store_handles_uri_metacharacters_in_path(
    tmp_path: Path, name: str
) -> None:
    """A `?` or `#` in the path must not be parsed as SQLite URI syntax — the
    path is percent-encoded via `Path.as_uri()` before `?mode=ro` is appended,
    so the connection resolves to (and stays read-only against) the exact
    file requested, not a truncated/different one."""
    db_path = tmp_path / name
    initialize_span_store(db_path).close()

    ro_conn = open_readonly_span_store(db_path)
    try:
        rollups = compute_operator_burden_rollups(ro_conn)
        assert all(r.matching_span_count == 0 for r in rollups)
        with pytest.raises(sqlite3.OperationalError):
            ro_conn.execute("INSERT INTO spans (span_id) VALUES ('x')")
    finally:
        ro_conn.close()
    # No stray *differently-named* db was created (e.g. truncated at the '?'
    # or '#'). WAL mode's own `-wal`/`-shm` sidecars alongside `name` are
    # expected and not the bug being guarded against.
    stray = {p.name for p in tmp_path.iterdir()} - {name, f"{name}-wal", f"{name}-shm"}
    assert stray == set()
