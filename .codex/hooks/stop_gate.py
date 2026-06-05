#!/usr/bin/env python3
"""Stop-time posture reminder for Codex."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(args: list[str]) -> str:
    try:
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive hook path
        return f"<unavailable: {exc}>"


def context_guard() -> str:
    try:
        checkpoint = subprocess.run(
            [
                "/usr/bin/python3",
                "tools/codex_context_guard.py",
                "checkpoint",
                "--label",
                "hook-stop",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=75,
        )
        if checkpoint.returncode != 0:
            output = checkpoint.stdout.strip() or checkpoint.stderr.strip()
            print(output or "<codex checkpoint failed>")
            sys.exit(checkpoint.returncode)
        proc = subprocess.run(
            [
                "/usr/bin/python3",
                "tools/codex_context_guard.py",
                "closeout",
                "--require-fresh-checkpoint",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=75,
        )
    except Exception as exc:  # pragma: no cover - defensive hook path
        raise SystemExit(f"<codex context guard unavailable: {exc}>") from exc
    output = (
        proc.stdout.strip() or proc.stderr.strip() or "<codex context guard produced no output>"
    )
    if proc.returncode != 0:
        print(output)
        sys.exit(proc.returncode)
    return output


status = run(["git", "status", "--short", "--branch"])
print("Codex stop posture:")
print(status or "<git status unavailable>")
print("- Before claiming completion, report exact verification commands and results.")
print("- For PR-ready work, ensure a branch, commit, PR, and CI status are explicit.")
print(context_guard())
