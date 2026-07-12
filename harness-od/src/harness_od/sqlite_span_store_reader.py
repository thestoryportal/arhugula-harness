"""C-OD-27 typed read interface for the sqlite span store.

U-OD-45 — closes the `4-OD-B SqliteWritePath` cluster's read-path surface per
OD spec v1.8 §C-OD-27.3 ("Reads via existing `read_state_ledger` shape: typed
query interface, no ad-hoc SQL exposed to runtime"). Parameterized SQL only;
the helper signatures enforce the type-narrow contract so consumers (TUI per
§19.3, audit trace reconciliation per IS-OD compositions) cannot drift to
string concatenation.

Read access is non-blocking from the writer's perspective via WAL mode per
§27.4 invariant 2; this module assumes the connection it receives was opened
through `initialize_span_store` (or otherwise has WAL active).
"""

from __future__ import annotations

import sqlite3

from harness_od.sqlite_span_store import SpanInsertRow

__all__ = [
    "read_all_spans",
    "read_span_by_id",
    "read_spans_by_name",
    "read_spans_by_trace",
    "read_spans_by_workflow",
]


_SELECT_COLUMNS = (
    "span_id, trace_id, parent_span_id, name, kind, "
    "start_time_ns, end_time_ns, status_code, status_message, "
    "attributes_json, events_json, "
    "workflow_id, workflow_run_id, workflow_idempotency_key"
)


def _row_to_span(row: tuple[object, ...]) -> SpanInsertRow:
    return SpanInsertRow(
        span_id=row[0],  # type: ignore[arg-type]
        trace_id=row[1],  # type: ignore[arg-type]
        parent_span_id=row[2],  # type: ignore[arg-type]
        name=row[3],  # type: ignore[arg-type]
        kind=row[4],  # type: ignore[arg-type]
        start_time_ns=row[5],  # type: ignore[arg-type]
        end_time_ns=row[6],  # type: ignore[arg-type]
        status_code=row[7],  # type: ignore[arg-type]
        status_message=row[8],  # type: ignore[arg-type]
        attributes_json=row[9],  # type: ignore[arg-type]
        events_json=row[10],  # type: ignore[arg-type]
        workflow_id=row[11],  # type: ignore[arg-type]
        workflow_run_id=row[12],  # type: ignore[arg-type]
        workflow_idempotency_key=row[13],  # type: ignore[arg-type]
    )


def read_spans_by_workflow(
    conn: sqlite3.Connection, workflow_id: str, workflow_run_id: str
) -> list[SpanInsertRow]:
    """Return all spans for a workflow run, ordered by `start_time_ns` ascending.

    Uses the `idx_workflow` composite index per spec §C-OD-27.1. Strict
    equality on both keys is the canonical workflow-scope query shape.
    """
    rows = conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM spans "
        "WHERE workflow_id = ? AND workflow_run_id = ? "
        "ORDER BY start_time_ns ASC",
        (workflow_id, workflow_run_id),
    ).fetchall()
    return [_row_to_span(r) for r in rows]


def read_spans_by_trace(conn: sqlite3.Connection, trace_id: str) -> list[SpanInsertRow]:
    """Return all spans for a trace, ordered by `start_time_ns` ascending.

    Uses the `idx_trace` index per spec §C-OD-27.1.
    """
    rows = conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM spans WHERE trace_id = ? ORDER BY start_time_ns ASC",
        (trace_id,),
    ).fetchall()
    return [_row_to_span(r) for r in rows]


def read_all_spans(conn: sqlite3.Connection) -> list[SpanInsertRow]:
    """Return every span in the store, ordered by `start_time_ns` ascending.

    Scoped-query surface for TUI views (§19.3) whose primitive is carried as
    an *attribute* on spans of varying names (e.g. the cache-hit-rate
    primitive's `anthropic.cache_*` token attributes live on LLM-inference
    spans named `"chat <model>"`, not on a span named after the primitive
    itself) — those views scan the full table and filter on attribute
    presence rather than on `name`. No index is needed; ring-buffer scale
    (bounded by the §19.2 rotation policy) makes a full scan acceptable.
    """
    rows = conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM spans ORDER BY start_time_ns ASC"
    ).fetchall()
    return [_row_to_span(r) for r in rows]


def read_spans_by_name(conn: sqlite3.Connection, name: str) -> list[SpanInsertRow]:
    """Return all spans with the given `name`, ordered by `start_time_ns` ascending.

    Scoped-query surface for the C-OD-19 §19.3 TUI trace browser's
    operator-burden eval primitive views (per-primitive `source_span_class`
    lookup, e.g. `"hitl.invocation.responded"` / `"sandbox.violation"`).
    No dedicated index exists on `name` — the ring-buffer scale (bounded by
    the §19.2 rotation policy) makes a full scan acceptable for this
    low-frequency operator-facing query.
    """
    rows = conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM spans WHERE name = ? ORDER BY start_time_ns ASC",
        (name,),
    ).fetchall()
    return [_row_to_span(r) for r in rows]


def read_span_by_id(conn: sqlite3.Connection, span_id: str) -> SpanInsertRow | None:
    """Return the span with the given `span_id`, or `None` if not present.

    Uses the primary-key lookup on `spans.span_id`.
    """
    row = conn.execute(
        f"SELECT {_SELECT_COLUMNS} FROM spans WHERE span_id = ?",
        (span_id,),
    ).fetchone()
    return _row_to_span(row) if row is not None else None
