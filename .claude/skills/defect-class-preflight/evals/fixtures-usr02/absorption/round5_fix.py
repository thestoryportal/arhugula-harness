"""Round-5 absorption of the reviewer's round-4 finding.

Round-4 finding: `drain_once()` handed the same group to two workers when both
observed the queue between the claim read and the append, so one group's rows
were appended twice.

Fixed here by tracking which groups are already in flight so a second worker
skips a group the first has taken.
"""

from __future__ import annotations

import threading
from collections.abc import Iterable


class _LiveGroups:
    """Registry of groups currently being drained by some worker."""

    def __init__(self) -> None:
        self._live: dict[str, int] = {}

    def claim(self, name: str, worker_id: int) -> bool:
        """Take `name` for `worker_id`. False if another worker already holds it."""
        if name in self._live:
            return False
        self._live[name] = worker_id
        return True

    def release(self, name: str) -> None:
        self._live.pop(name, None)


_LIVE = _LiveGroups()


def drain_once(groups: Iterable[str], worker_id: int, sink: list[str]) -> int:
    drained = 0
    for name in groups:
        if not _LIVE.claim(name, worker_id):
            continue
        try:
            sink.append(name)
            drained += 1
        finally:
            _LIVE.release(name)
    return drained


def drain_all(groups: list[str], workers: int, sink: list[str]) -> None:
    threads = [threading.Thread(target=drain_once, args=(groups, i, sink)) for i in range(workers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
