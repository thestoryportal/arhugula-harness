"""Reservation-store reader (the producer detector_suite.py consumes)."""

import json
from datetime import UTC, datetime
from pathlib import Path

STORE = Path.home() / ".detector" / "heads.json"


def heads() -> list[dict]:
    rows = json.loads(STORE.read_text())
    cutoff = datetime.now(UTC).isoformat()
    return [r for r in rows if r.get("reserved_at", "") <= cutoff]
