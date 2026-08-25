"""Planted-defect fixture (u-he-33 repair loop): a detection suite consumer.

Planted: (1) venue-blind producer import — `store_reader` needs Python 3.12+
(`datetime.UTC`) but this module is documented to run under /usr/bin/python3 3.9,
and the ImportError arm returns [] so every check silently no-ops there;
(2) success-shaped empty on exception — a corrupt store reads as "nothing to
detect"; (3) an unguarded suppression input — `muted_ids()` trusts a JSON file
that can be a planted symlink or forged entry, and its contents mute hard
detections.
"""

import json
from pathlib import Path

MUTE_FILE = Path.home() / ".detector" / "muted.json"


def open_heads() -> list[dict]:
    try:
        import store_reader  # requires datetime.UTC (3.11+); documented venue is 3.9

        return store_reader.heads()
    except Exception:
        return []  # planted: "couldn't look" reads as empty


def muted_ids() -> set[str]:
    if MUTE_FILE.exists():
        return set(json.loads(MUTE_FILE.read_text()))  # planted: unguarded suppressor
    return set()


def detect_orphans() -> list[str]:
    muted = muted_ids()
    return [h["id"] for h in open_heads() if h.get("orphaned") and h["id"] not in muted]
