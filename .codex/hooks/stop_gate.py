#!/usr/bin/env python3
"""Stop-time posture reminder for Codex."""

from __future__ import annotations

import subprocess


def run(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False).stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive hook path
        return f"<unavailable: {exc}>"


status = run(["git", "status", "--short", "--branch"])
print("Codex stop posture:")
print(status or "<git status unavailable>")
print("- Before claiming completion, report exact verification commands and results.")
print("- For PR-ready work, ensure a branch, commit, PR, and CI status are explicit.")
