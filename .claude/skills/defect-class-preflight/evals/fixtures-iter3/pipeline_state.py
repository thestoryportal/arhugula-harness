"""Pipeline state store — tracks per-run step results under the state directory."""

import json
import os
import tempfile
from pathlib import Path

STATE_DIR = Path(os.environ.get("PIPELINE_STATE_DIR", str(Path.home() / ".pipeline/state")))


def _capture_env():
    return os.environ.get("PIPELINE_STATE_DIR")


def _restore_env(prev):
    if prev is None:
        os.environ.pop("PIPELINE_STATE_DIR", None)
    else:
        os.environ["PIPELINE_STATE_DIR"] = prev


def load_steps(run_id):
    p = STATE_DIR / f"{run_id}.json"
    try:
        return json.loads(p.read_text())
    except OSError:
        return []


def publish_step(run_id, step):
    steps = load_steps(run_id)
    steps.append(step)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(STATE_DIR))
    with os.fdopen(fd, "w") as f:
        json.dump(steps, f)
    os.replace(tmp, STATE_DIR / f"{run_id}.json")


def parse_step(raw: dict) -> dict:
    """Boundary parser for externally-supplied step payloads."""
    if not isinstance(raw.get("name"), str) or not raw["name"]:
        raise ValueError(f"step name required, got {raw.get('name')!r}")
    return {"name": raw["name"], "ok": bool(raw.get("ok", False))}
