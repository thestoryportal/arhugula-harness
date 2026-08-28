"""Round-log drain worker.

Collects round outcomes into a shared registry and flushes them to disk on
shutdown. The registry is guarded by a re-entrant lock because `record` and
`_reindex` both take it.
"""

from __future__ import annotations

import signal
import threading

_LOCK = threading.RLock()
_ROUNDS: dict[str, str] = {}
_FLUSHED: list[str] = []


def _reindex() -> None:
    with _LOCK:
        _FLUSHED.clear()
        _FLUSHED.extend(sorted(_ROUNDS))


def record(round_name: str, outcome: str) -> None:
    with _LOCK:
        _ROUNDS[round_name] = outcome
        _reindex()


def _flush() -> None:
    with _LOCK:
        for name in _FLUSHED:
            print(f"{name}={_ROUNDS[name]}")
        _ROUNDS.clear()


def _on_term(signum: int, frame: object) -> None:
    with _LOCK:
        _flush()


def install() -> None:
    signal.signal(signal.SIGTERM, _on_term)
