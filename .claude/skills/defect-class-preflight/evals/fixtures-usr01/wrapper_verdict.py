"""Out-of-family review wrapper.

Contract C-HE-15: a verdict counts only on its schema parse — never on the
reviewer process's exit code, and never on silence. Carried verbatim from the
wrapper's own spec note: "the exit code is a convenience, never a verdict."
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

SCHEMA_STATES = ("approve", "block")


@dataclass(frozen=True)
class Verdict:
    state: str
    raw: str


def parse_verdict(payload: str) -> Verdict | None:
    """Parse the reviewer's emitted JSON — the contract's only verdict source."""
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError:
        return None
    state = doc.get("state")
    if state not in SCHEMA_STATES:
        return None
    return Verdict(state=state, raw=payload)


def run_review(cmd: list[str], timeout_s: int = 600) -> Verdict:
    """Run the reviewer and return the round's verdict."""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return Verdict(state="unavailable", raw="reviewer timed out")
    if proc.returncode in (0, 1):
        return Verdict(
            state="approve" if proc.returncode == 0 else "block",
            raw=proc.stdout,
        )
    return Verdict(state="unavailable", raw=proc.stderr)
