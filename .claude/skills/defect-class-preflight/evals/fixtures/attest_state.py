"""Attestation state carrier for a review gate.

The attest verbs that write this file are guard-auto-allowed in autonomous loop
mode; the gate's admit() reads it to decide whether a review round may launch.
Single lane per arc (serial writer).
"""

import json
from pathlib import Path

STATE = Path(".harness/attest_state.json")


def load() -> list[dict]:
    if not STATE.exists():
        return []
    return json.loads(STATE.read_text())["records"]


def append(record: dict) -> None:
    records = load()
    records.append(record)
    STATE.write_text(json.dumps({"records": records}))
