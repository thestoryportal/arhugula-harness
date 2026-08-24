"""Metrics collector — appends measurement rows to the metrics home."""

import json
import os
import time
from pathlib import Path


def metrics_home() -> Path:
    return Path(os.environ.get("METRICS_HOME", str(Path.home() / ".metrics"))).expanduser()


def append_row(kind: str, value: float) -> None:
    home = metrics_home()
    home.mkdir(parents=True, exist_ok=True)
    with open(home / "rows.jsonl", "a") as f:
        f.write(json.dumps({"ts": time.time(), "kind": kind, "value": value}) + "\n")
