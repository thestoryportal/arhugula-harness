"""Witness for tools/lease_yield_trigger.py — the B-232 trigger's session-start carrier.

The contract: one line, the rolling 30-day maximum over the ledger's yield rows against
the B-232 threshold; `TRIGGER FIRED` only past the threshold; a ledger that cannot be
evaluated is exit 2 with a reason, never a printed zero.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lease_yield_trigger import TRIGGER_TEXT, evaluate, render
from loop_cost_baseline import TRIGGER_THRESHOLD, YIELD_CAUSE

SCRIPT = Path(__file__).resolve().parent / "lease_yield_trigger.py"
HEADER = "| ts | kind | lane;cause | detail |\n|---|---|---|---|\n"


def _yield_row(day: int) -> str:
    return f"| 2020-01-{day:02d}T00:00:00Z | NOTIFY | lane=L;cause={YIELD_CAUSE} | h=x b=0 |\n"


def _run(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, check=False
    )


def test_below_threshold_prints_the_count_without_firing(tmp_path: Path) -> None:
    ledger = tmp_path / "loop_status.md"
    ledger.write_text(
        HEADER
        + "| 2020-01-01T00:00:00Z | NOTIFY | lane=L;cause=- | not a yield |\n"
        + "".join(_yield_row(d) for d in range(1, TRIGGER_THRESHOLD + 1))
    )
    proc = _run(ledger)
    assert proc.returncode == 0, proc.stderr
    n = TRIGGER_THRESHOLD
    assert proc.stdout == f"[b-232] lease_held_yields_30d_max={n}/{n}\n"
    assert TRIGGER_TEXT not in proc.stdout


def test_past_threshold_fires(tmp_path: Path) -> None:
    ledger = tmp_path / "loop_status.md"
    ledger.write_text(HEADER + "".join(_yield_row(d) for d in range(1, TRIGGER_THRESHOLD + 2)))
    proc = _run(ledger)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith(
        f"[b-232] lease_held_yields_30d_max={TRIGGER_THRESHOLD + 1}/{TRIGGER_THRESHOLD} "
    )
    assert proc.stdout.rstrip("\n").endswith(TRIGGER_TEXT)


def test_six_rows_spread_over_years_do_not_fire() -> None:
    lines = [
        f"| 20{20 + i}-01-01T00:00:00Z | NOTIFY | lane=L;cause={YIELD_CAUSE} | h |"
        for i in range(6)
    ]
    assert evaluate(lines) == 1
    assert render(evaluate(lines)) == f"[b-232] lease_held_yields_30d_max=1/{TRIGGER_THRESHOLD}"


def test_missing_ledger_is_exit_2_never_a_zero(tmp_path: Path) -> None:
    proc = _run(tmp_path / "absent.md")
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "cannot evaluate" in proc.stderr


def test_unparseable_ts_is_exit_2(tmp_path: Path) -> None:
    ledger = tmp_path / "loop_status.md"
    ledger.write_text(HEADER + f"| yesterday | NOTIFY | lane=L;cause={YIELD_CAUSE} | h |\n")
    proc = _run(ledger)
    assert proc.returncode == 2 and proc.stdout == ""


def test_usage_error_is_exit_2() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False
    )
    assert proc.returncode == 2 and "usage" in proc.stderr
