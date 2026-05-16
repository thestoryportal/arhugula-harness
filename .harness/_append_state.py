"""Append one hash-chained landing entry to .harness/state.jsonl."""

from __future__ import annotations

import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(__file__).parent / "state.jsonl"


def main(unit_id: str) -> None:
    lines = [ln for ln in STATE.read_text().splitlines() if ln.strip()]
    prior = json.loads(lines[-1])["response_hash"]
    entry = {
        "action_id": str(uuid.uuid4()),
        "actor": "phase-7-implementation",
        "idempotency_key": hashlib.md5(
            f"land:{unit_id}".encode()
        ).hexdigest(),
        "prior_event_hash": prior,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    entry["response_hash"] = hashlib.sha256(
        json.dumps(entry, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with STATE.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(f"{unit_id} -> {entry['response_hash']}")


if __name__ == "__main__":
    main(sys.argv[1])
