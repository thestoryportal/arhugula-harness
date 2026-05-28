"""C-OD-27 sqlite span-store schema + WAL-mode initialization.

U-OD-42 — `4-OD-B SqliteWritePath` cluster L0 anchor. Lands the canonical
14-column `spans` table per OD spec v1.8 §C-OD-27.1, 4 indexes
(`idx_workflow` composite / `idx_idempotency` / `idx_trace` /
`idx_time_range` composite), and WAL-mode + foreign-keys-off pragmas per
§27.2 row 2. Idempotent re-initialization via `CREATE TABLE IF NOT EXISTS`
+ `CREATE INDEX IF NOT EXISTS` (§27.4 invariant via declarative DDL).

Subsequent units in the cluster (U-OD-43 batched flush, U-OD-44 lazy-on-write
retention, U-OD-45 typed read interface) extend this module without altering
the schema.

Closes `H_T-OD-6 PARTIAL` sqlite-write-path gap per workspace CLAUDE.md §4.1
OD substitution row. Plan AC #1 cites "12 columns" — implementation follows
OD spec v1.8 §C-OD-27.1 (14 columns) per checkpoint-ratified spec-canonical
discipline; plan canonical-reading amendment owed at OD plan v2.24.

Parent-directory creation at `db_path.parent` is implementer-discretion per
§27.5 silence; default is `mkdir(parents=True, exist_ok=True)` for true
idempotent init.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

__all__ = [
    "SPANS_DDL",
    "INDEX_DDL",
    "initialize_span_store",
]


SPANS_DDL = """\
CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    parent_span_id TEXT NULL,
    name TEXT NOT NULL,
    kind INTEGER NOT NULL,
    start_time_ns INTEGER NOT NULL,
    end_time_ns INTEGER NOT NULL,
    status_code INTEGER NOT NULL,
    status_message TEXT NULL,
    attributes_json TEXT NOT NULL,
    events_json TEXT NOT NULL,
    workflow_id TEXT NULL,
    workflow_run_id TEXT NULL,
    workflow_idempotency_key TEXT NULL
)
"""

INDEX_DDL: tuple[str, ...] = (
    "CREATE INDEX IF NOT EXISTS idx_workflow ON spans(workflow_id, workflow_run_id)",
    "CREATE INDEX IF NOT EXISTS idx_idempotency ON spans(workflow_idempotency_key)",
    "CREATE INDEX IF NOT EXISTS idx_trace ON spans(trace_id)",
    "CREATE INDEX IF NOT EXISTS idx_time_range ON spans(start_time_ns, end_time_ns)",
)


def initialize_span_store(db_path: Path) -> sqlite3.Connection:
    """Open the span-store sqlite db, apply pragmas, and ensure schema.

    Caller owns the returned connection and is responsible for `close()`.
    Re-invocation against an existing db is a no-op (schema + indexes use
    `IF NOT EXISTS`; pragmas are idempotent).
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute(SPANS_DDL)
    for stmt in INDEX_DDL:
        conn.execute(stmt)
    conn.commit()
    return conn
