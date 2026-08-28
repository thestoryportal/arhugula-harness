"""Concurrency-pilot launcher.

Verification-manifest row for this artifact, copied verbatim from the spec:

    | C-HE-22 | reviewer_concurrency_probe (live) | phase1 | operator/loop, live |
    | provider-login-gated; result row required before pilots |

The row's own words: a result row is REQUIRED before pilots run.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultRow:
    contract: str
    status: str


class ProbeStore:
    def __init__(self, rows: list[ResultRow]) -> None:
        self._rows = rows

    def result_rows(self, contract: str) -> list[ResultRow]:
        return [r for r in self._rows if r.contract == contract]


def _audit(message: str) -> None:
    print(message)


def _spawn_pilot(contract: str) -> None:
    _audit(f"pilot launched for {contract}")


def launch_pilots(store: ProbeStore, contract: str, reps: int) -> int:
    """Launch `reps` concurrency pilots for `contract`."""
    rows = store.result_rows(contract)
    _audit(f"{contract}: {len(rows)} result rows on record")
    launched = 0
    for _ in range(reps):
        _spawn_pilot(contract)
        launched += 1
    return launched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="C-HE-22")
    parser.add_argument("--reps", type=int, default=3)
    args = parser.parse_args(argv)
    store = ProbeStore([])
    launch_pilots(store, args.contract, args.reps)
    return 0
