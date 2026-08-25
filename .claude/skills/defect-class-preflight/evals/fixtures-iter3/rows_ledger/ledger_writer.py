"""rows_ledger — a small append-only JSONL ledger and its own reader.

Fixture data surface for the new-consumer inventory pause eval. Schema
history: v1 rows carried {"ts", "arc_id", "generation"}; v2 added
"verdict". Real ledgers hold a mix of both shapes.
"""

from __future__ import annotations

import json
import os
from typing import Any

LEDGER_PATH = os.path.expanduser("~/.rows-ledger/rows.jsonl")


def append_row(ts: str, arc_id: str | None, generation: int, verdict: str | None = None) -> None:
    """Append one row.

    arc_id is None when no reservation context exists (headless runs).
    verdict is omitted from the row (not written as null) for pre-v2
    callers. The append is a plain buffered write — a crash mid-write can
    leave a truncated trailing line on disk.
    """
    row: dict[str, Any] = {"ts": ts, "arc_id": arc_id, "generation": generation}
    if verdict is not None:
        row["verdict"] = verdict
    with open(LEDGER_PATH, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def iter_rows(path: str = LEDGER_PATH) -> list[dict[str, Any]]:
    """The surface's own reader — the precedent a new consumer matches or
    names why it diverges.

    - A malformed line (e.g. truncated by a mid-write crash) is skipped,
      never raised.
    - Rows missing "verdict" are v1 rows: verdict is filled with the
      sentinel "pre-v2", never treated as an error.
    - Within one arc_id, a higher generation supersedes lower ones; only
      the highest-generation row per arc survives. Rows whose arc_id is
      None are never deduplicated — each stands alone.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except FileNotFoundError:
        return []
    best: dict[str, dict[str, Any]] = {}
    standalone: list[dict[str, Any]] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # truncated trailing line from a mid-write crash
        row.setdefault("verdict", "pre-v2")
        arc = row["arc_id"]
        if arc is None:
            standalone.append(row)
        elif arc not in best or row["generation"] > best[arc]["generation"]:
            best[arc] = row
    return standalone + list(best.values())
