"""Drain worker retry budget.

The retry budget is read from the environment so an operator can widen it during
an incident without a redeploy.
"""

from __future__ import annotations

import os
import time


def _budget() -> int:
    return int(os.environ.get("DRAIN_RETRY_BUDGET", "3"))


def drain_with_retries(step, rows: list[str]) -> list[str]:
    """Drain each row through `step`, returning the rows that were drained.

    A row that times out is retried after a 0.5 s sleep, up to `DRAIN_RETRY_BUDGET`
    attempts; a row that exhausts its attempts is left out of the returned list.
    """
    done: list[str] = []
    for row in rows:
        for _attempt in range(_budget()):
            try:
                step(row)
            except TimeoutError:
                time.sleep(0.5)
                continue
            done.append(row)
            break
    return done
