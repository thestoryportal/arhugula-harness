"""B-208 — the shared loop ledger must be unreachable from a test process.

`loop_status_path()` (tools/hooks/loop_lib.sh) resolves the venue from the ambient
environment, falling back to the operator's real ledger when `HARNESS_LOOP_STATUS_PATH`
is unset. Every pytest process starts with it unset, so any test reaching a real emit
path appended real `DEFERRED-HIL` rows to the venue the SessionStart hook reads.
`tools/conftest.py` now redirects it once per `tools/` session -- at the joint where
every loop-row producer lives, rather than at the root, where the redirect would also
leak a `HARNESS_*` name into axis suites that assert none is set. These witness that.

Case 2 is the load-bearing one and is deliberately hermetic: it moves the COMPUTED
FALLBACK to a temp dir, so removing the conftest redirect sends the write into a file
this test owns rather than into the operator's ledger. A mutation probe of the fix must
not reproduce the very damage the fix prevents.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reservations as rs


def test_session_venue_is_redirected_away_from_the_default():
    """(1) The redirect happened at all, and named a real absolute path."""
    venue = os.environ.get("HARNESS_LOOP_STATUS_PATH")
    assert venue, "tools/conftest.py must redirect HARNESS_LOOP_STATUS_PATH"
    assert venue.startswith("/"), f"loop_status_path rejects a relative venue, got {venue!r}"
    assert "harness-loop-status-" in venue, f"not the session's throwaway venue: {venue!r}"
    assert ".gstack" not in venue, f"venue still resolves inside the operator's store: {venue!r}"


def test_a_real_emit_lands_in_the_redirect_and_not_in_the_computed_fallback(monkeypatch, tmp_path):
    """(2) The redirect governs the ACTUAL writer, not just the variable.

    `emit_loop_row` shells out to `loop_log_structured`, which is also the path the
    door's subprocess-driven tests take — monkeypatching the Python seam cannot reach
    those, so the environment is the only lever and this asserts on it end to end.
    """
    # Relocate the fallback the shell would compute if the redirect were gone. With the
    # redirect in place HARNESS_LOOP_STATUS_PATH wins and this file must never appear;
    # revert the conftest and the emit lands here instead — discriminating, and harmless.
    queue = tmp_path / "arc-metrics-queue"
    queue.mkdir()
    monkeypatch.setenv("ARC_METRICS_QUEUE_DIR", str(queue))
    fallback = tmp_path / "loop_status.md"

    # Read the venue WITHOUT subscripting: with the redirect reverted the variable is
    # absent, and dying here would leave the assertion below — the one that actually
    # observes the pollution — unexercised, so the probe would prove only that the test
    # reads an env var. The emit must run either way for the witness to see the mechanism.
    redirect = os.environ.get("HARNESS_LOOP_STATUS_PATH")
    venue = Path(redirect) if redirect else None
    before = venue.read_text() if venue and venue.exists() else ""

    rs.emit_loop_row(
        "NOTIFY", "b-208-witness", "b-208:isolation:probe", "row from the B-208 witness"
    )

    assert not fallback.exists(), (
        "a real emit reached the COMPUTED fallback venue — under a production environment "
        f"that path is the operator's shared append-only ledger ({fallback})"
    )
    assert venue is not None, "tools/conftest.py must redirect HARNESS_LOOP_STATUS_PATH"
    assert venue.exists(), "the emit did not reach the redirected venue"
    appended = venue.read_text()[len(before) :]
    assert "b-208:isolation:probe" in appended, f"row missing from the redirect: {appended!r}"
