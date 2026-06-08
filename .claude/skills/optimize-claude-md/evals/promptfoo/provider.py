#!/usr/bin/env python3
"""File-reader promptfoo provider for the optimize-claude-md eval loop (NO API, no model call).

The self-improvement loop runs IN-SESSION (skill-creator + the agent), not via a model API.
Each iteration the agent runs optimize-claude-md on a fixture and writes the result to
outputs/<case>.json (the contract documented in assertions.py). This provider returns that
pre-produced output so promptfoo can run the deterministic assertions on it. It NEVER calls a
model — keeping the loop zero-cost and in-environment per the operator's directive.
"""

from __future__ import annotations

from pathlib import Path

_OUT_DIR = Path(__file__).resolve().parent / "outputs"


def call_api(prompt, options, context):
    vars_ = (context or {}).get("vars", {}) or {}
    case = vars_.get("case")
    if not case:
        return {"error": "test var 'case' is required (names outputs/<case>.json)"}
    out = _OUT_DIR / f"{case}.json"
    if not out.exists():
        return {
            "error": (
                f"no agent output at {out}; the loop must run optimize-claude-md on the "
                f"fixture and write outputs/{case}.json before 'promptfoo eval'"
            )
        }
    return {"output": out.read_text(encoding="utf-8")}
