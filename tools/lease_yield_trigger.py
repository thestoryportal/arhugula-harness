#!/usr/bin/env python3
"""B-232 trigger evaluator — the session-start carrier of the lease-scope decision.

Usage:
    python3 tools/lease_yield_trigger.py <loop_status.md>

Prints ONE line to stdout and exits 0:
    [b-232] lease_held_yields_30d_max=<n>/<threshold>
with ` TRIGGER FIRED — open the B-232 spec leg (Class 2)` appended when <n> exceeds the
threshold. `<n>` is the most `merge-door-lease-acquire:lease_held_yield` NOTIFY rows in any
half-open 30-day window of the shared loop ledger (loop_cost_baseline.rolling_window_max —
the one definition; this script owns no arithmetic of its own, [LAW:one-source-of-truth]).

A missing or unreadable ledger, or a row whose `ts` cannot be parsed, exits 2 with the
reason on stderr — never a printed zero ([LAW:no-silent-failure]): a zero here would read
to the operator as "no contention", and the banner that runs this script prints its
failure line instead.

stdlib-only on purpose: `tools/roadmap-audit/session-start.sh` invokes it with the plain
`python3` on PATH from its own directory, so it runs in the hook's test harness (a temp
project dir without `tools/`) and in every session, at ≈0.2 s (measured 2026-09-04).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from loop_cost_baseline import (
    TRIGGER_THRESHOLD,
    TRIGGER_WINDOW,
    rolling_window_max,
    yield_stamps,
)

TRIGGER_TEXT = "TRIGGER FIRED — open the B-232 spec leg (Class 2)"


def evaluate(lines: list[str]) -> int:
    """The rolling 30-day maximum over the ledger's yield rows (pure)."""
    return rolling_window_max(yield_stamps(lines), TRIGGER_WINDOW)


def render(n: int) -> str:
    """The banner segment. `fired` is a value the line carries, not a branch on whether
    the line exists ([LAW:dataflow-not-control-flow])."""
    fired = (" " + TRIGGER_TEXT) if n > TRIGGER_THRESHOLD else ""
    return f"[b-232] lease_held_yields_30d_max={n}/{TRIGGER_THRESHOLD}{fired}"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: lease_yield_trigger.py <loop_status.md>", file=sys.stderr)
        return 2
    try:
        lines = Path(args[0]).read_text().splitlines()
        n = evaluate(lines)
    except (OSError, ValueError, IndexError) as exc:
        print(f"lease_yield_trigger: cannot evaluate {args[0]}: {exc}", file=sys.stderr)
        return 2
    print(render(n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
