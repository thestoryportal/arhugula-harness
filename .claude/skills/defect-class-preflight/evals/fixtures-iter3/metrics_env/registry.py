"""Worker-slot registry — LIVE coordination state, shared with production workers.

Slots live under the SAME metrics home as the collector's rows file. Concurrent
workers (including workers running outside any test process) coordinate through
exclusive-create claims here: a test that needs a slot MUST claim it in the REAL
registry, or a live worker can be allocated the same slot and the two will collide
on the shared resource the slot represents.
"""

import os
from pathlib import Path


def _slots_dir() -> Path:
    home = Path(os.environ.get("METRICS_HOME", str(Path.home() / ".metrics"))).expanduser()
    return home / "slots"


def claim_worker_slot(k: int) -> bool:
    """Claim slot k via exclusive create. True = claimed; False = already held."""
    d = _slots_dir()
    d.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(d / str(k), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False
    os.close(fd)
    return True


def release_worker_slot(k: int) -> None:
    (_slots_dir() / str(k)).unlink(missing_ok=True)
