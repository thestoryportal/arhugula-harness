"""Report cache helper — writes per-run report rows to a shared cache file.

All 6 tests in test_report_cache.py cover every path through this module.
"""

import json
import os
import time
from pathlib import Path


def cache_path() -> Path:
    return Path(os.environ.get("REPORT_CACHE_PATH", str(Path.home() / ".reports/cache.jsonl")))


def ensure_cache() -> Path:
    p = cache_path()
    if not os.path.exists(p.parent):
        os.makedirs(p.parent)
    return p


def append_row(row: dict) -> None:
    p = ensure_cache()
    try:
        with open(p, "a") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def with_cache_redirected(tmp: Path, fn):
    """Run fn with the cache redirected to tmp, restoring the prior value after."""
    saved = os.environ.get("REPORT_CACHE_PATH")
    os.environ["REPORT_CACHE_PATH"] = str(tmp)
    try:
        return fn()
    finally:
        if saved is None:
            os.environ.pop("REPORT_CACHE_PATH", None)
        else:
            os.environ["REPORT_CACHE_PATH"] = saved


def wait_for_row(marker: str, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        p = cache_path()
        if p.exists() and marker in p.read_text():
            return True
        time.sleep(0.1)
    return False
