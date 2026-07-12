"""Operator review-loop persistence — B-OD17-EVAL-LOOP-TOOLING.

The "categorize" half of the Husain manual-review -> categorize -> automate
-> align loop (`HusainLoopState.iteration_phase`,
`operator_burden_eval_dashboard_binding.py`): once a `HoldoutSet`
(`holdout_set.py`) names the traces in scope, the operator manually assigns
each one a category (free-text — C-OD-17 §17.3 names no fixed taxonomy) and
this module appends that categorization to a durable, append-only ledger.

Hard boundary (`[[eval-harness-refused-as-governance-gate]]`): a
`ReviewEntry.category` is always operator-authored input; nothing in this
module infers, scores, or judges a category — it only persists what the
operator typed.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from harness_od.observability_matrix import CellID
from harness_od.operator_burden_eval_primitives import OperatorBurdenEvalPrimitive

__all__ = [
    "ReviewEntry",
    "append_review_entry",
    "read_review_ledger",
    "reviewed_trace_ids",
]


class ReviewEntry(BaseModel):
    """One operator-categorized holdout trace (C-OD-17 §17.3 "categorize" phase).

    Frozen -> `Eq`. `loop_phase` is carried verbatim as `"categorize"` — the
    same phase-name vocabulary `HusainLoopState.iteration_phase` uses — so a
    ledger entry is legible against the declared loop shape without inventing
    a parallel vocabulary.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    cell_id: CellID
    primitive: OperatorBurdenEvalPrimitive
    trace_id: str
    #: operator-authored free-text category; no fixed taxonomy per §17.3.
    category: str
    notes: str | None
    reviewed_at: str
    loop_phase: str = "categorize"


def append_review_entry(ledger_path: Path, entry: ReviewEntry) -> None:
    """Append `entry` as one JSON line to `ledger_path`.

    Creates the file (and parent directories) on first write; every
    subsequent call appends — the ledger is append-only, mirroring the
    workspace's own JSONL state-ledger convention (`harness_is` §5).
    """
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(entry.model_dump_json() + "\n")


def read_review_ledger(ledger_path: Path) -> list[ReviewEntry]:
    """Read every entry from `ledger_path`, in append order.

    Returns an empty list if `ledger_path` does not exist yet (an unreviewed
    holdout set has no ledger) rather than raising `FileNotFoundError` — the
    review loop's "already reviewed?" check must work against a fresh cell.
    """
    if not ledger_path.exists():
        return []
    entries: list[ReviewEntry] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        entries.append(ReviewEntry.model_validate(json.loads(stripped)))
    return entries


def reviewed_trace_ids(ledger_path: Path) -> set[str]:
    """The set of `trace_id`s already present in `ledger_path`.

    Convenience for the review loop to skip traces a prior run already
    categorized (a `HoldoutSet` may be reviewed across multiple sessions).
    """
    return {entry.trace_id for entry in read_review_ledger(ledger_path)}
