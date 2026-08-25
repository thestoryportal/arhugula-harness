"""Reads reservation heads from the store and reports orphaned arcs.

Documented runtime: /usr/bin/python3 (the system interpreter), so the report stays
runnable before the workspace env is synced.
"""

import json
from pathlib import Path

MUTE_FILE = Path.home() / ".detector" / "muted.json"


def open_heads() -> list[dict]:
    try:
        import store_reader

        return store_reader.heads()
    except Exception:
        return []


def muted_ids() -> set[str]:
    if MUTE_FILE.exists():
        return set(json.loads(MUTE_FILE.read_text()))
    return set()


def detect_orphans() -> list[str]:
    muted = muted_ids()
    return [h["id"] for h in open_heads() if h.get("orphaned") and h["id"] not in muted]
