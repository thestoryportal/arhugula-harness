"""The §30 staleness token — a PROPERTY, and the one composition that satisfies it.

`B-69` impl leg. Runtime spec v1.107 §30 term 1 states the token as a **property**,
never a composition:

    *The accessor-minted staleness token MUST differ between any two durably-journaled
    pause records of the same workflow that a caller could successively observe.*

HOW it is composed is implementation discretion, verified by execution. The spec
explicitly does NOT name ``snapshot_hash`` (demonstrably fail-open for the
non-fan-out case — two successive LINEAR pauses at the same ``step_index`` hash
IDENTICALLY under the MVP placeholder ``pause_context_reader``) and does NOT name
``(snapshot_hash, created_at)`` (a luck argument about clock granularity and
monotonicity, which the "by construction, not by luck" standard forbids as its own
carrier).

**The composition chosen, and why it satisfies the property BY CONSTRUCTION.** The
token folds the journal's **record count** together with a digest of its **latest
raw record line**. §14.14.8's append-only / never-truncated substrate invariant is
what makes this sound: no path in the store rewrites, truncates, compacts, rotates,
prunes or removes a previously-appended record, so the record count is monotonically
non-decreasing and increments on every ``capture()``. Two records a caller could
successively observe are therefore separated by at least one append, so their counts
differ — *regardless* of whether the two snapshots happen to hash identically. The
latest-line digest is folded in as well so that a same-count observation of a
different record (not reachable through the shipped store, but cheap to fence) also
differs.

This composition adds NO new persistence and needs NO capture-side carrier change:
``_append`` already writes the full ``model_dump(mode="json")`` per record, and the
count is a property of the file the read already opens.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness_runtime.lifecycle.journal_workflow_pause_store import (
        PauseJournalReadResult,
    )

__all__ = ["mint_staleness_token"]


def mint_staleness_token(read: PauseJournalReadResult) -> str | None:
    """The token for a durable read, or ``None`` when one cannot be minted.

    ``None`` is returned only when the read produced no record to mint from. Callers
    MUST treat that as fail-closed — §14.14.9.4 rules **no-token-returned MUST mean
    no-projection-returned**; never a projection carrying an absent token that a
    subsequent ``resume()`` would read as *"no claim"*.
    """
    if read.latest_record_digest is None or read.record_count <= 0:
        return None
    return hashlib.sha256(
        f"pause-state-staleness:v1:{read.record_count}:{read.latest_record_digest}".encode()
    ).hexdigest()
