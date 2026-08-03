#!/usr/bin/env python3
"""Stop-time posture reminder for Codex."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import cast

ROOT = Path(__file__).resolve().parents[2]

if os.environ.get("HARNESS_CODEX_REVIEW_ISOLATED") == "1":
    raise SystemExit(0)


def run(args: list[str]) -> str:
    try:
        return subprocess.run(
            args, cwd=ROOT, capture_output=True, text=True, check=False
        ).stdout.strip()
    except Exception as exc:  # pragma: no cover - defensive hook path
        return f"<unavailable: {exc}>"


def render_guard(payload: object) -> tuple[str, set[str]]:
    if not isinstance(payload, dict):
        raise ValueError("invalid context guard JSON")
    guard = cast(dict[str, object], payload)
    raw_findings = guard.get("findings")
    if not isinstance(raw_findings, list):
        raise ValueError("invalid context guard findings")
    root = guard.get("root")
    branch = guard.get("branch")
    lines = [
        "Codex context guard",
        f"root: {root if isinstance(root, str) else '<unknown>'}",
        f"branch: {branch if isinstance(branch, str) else '<unknown>'}",
    ]
    hard_codes: set[str] = set()
    if not raw_findings:
        lines.append("Findings: none")
    else:
        lines.append("Findings:")
        for raw_finding in cast(list[object], raw_findings):
            if not isinstance(raw_finding, dict):
                raise ValueError("invalid context guard finding")
            finding = cast(dict[str, object], raw_finding)
            severity = finding.get("severity")
            code = finding.get("code")
            message = finding.get("message")
            if (
                not isinstance(severity, str)
                or severity not in {"hard", "warn", "info"}
                or not isinstance(code, str)
                or not code
                or not isinstance(message, str)
                or not message
            ):
                raise ValueError("invalid context guard finding fields")
            lines.append(f"- {severity.upper()} {code}: {message}")
            if severity == "hard":
                hard_codes.add(code)
    return "\n".join(lines), hard_codes


def context_guard() -> str:
    allow_roadmap_drift = (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("GITHUB_EVENT_NAME") == "push"
        and os.environ.get("GITHUB_REF") == "refs/heads/main"
    )
    roadmap_drift_args = ["--allow-roadmap-drift"] if allow_roadmap_drift else []
    try:
        checkpoint = subprocess.run(
            [
                "/usr/bin/python3",
                "tools/codex_context_guard.py",
                "checkpoint",
                "--label",
                "hook-stop",
                "--include-branch-diff",
                *roadmap_drift_args,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=75,
        )
        if checkpoint.returncode != 0:
            output = checkpoint.stdout.strip() or checkpoint.stderr.strip()
            print(output or "<codex checkpoint failed>", file=sys.stderr)
            sys.exit(checkpoint.returncode)
        proc = subprocess.run(
            [
                "/usr/bin/python3",
                "tools/codex_context_guard.py",
                "closeout",
                "--require-fresh-checkpoint",
                "--include-branch-diff",
                "--json",
                *roadmap_drift_args,
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
    try:
        rendered, hard_codes = render_guard(json.loads(output))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"{output}\n<invalid context guard output: {exc}>", file=sys.stderr)
        sys.exit(proc.returncode or 1)
    if proc.returncode != 0:
        if not hard_codes or hard_codes - {"CODEX_LOOP_INCOMPLETE"}:
            print(rendered, file=sys.stderr)
            sys.exit(proc.returncode or 1)
        return "\n".join(
            [
                rendered,
                "- Stop is advisory only for an incomplete in-progress autonomous loop; "
                "`just codex-closeout` remains the hard completion/commit/PR gate.",
            ]
        )
    if hard_codes:
        print(rendered, file=sys.stderr)
        sys.exit(1)
    return rendered


status = run(["git", "status", "--short", "--branch"])
message = "\n".join(
    [
        "Codex stop posture:",
        status or "<git status unavailable>",
        "- Before claiming completion, report exact verification commands and results.",
        "- For PR-ready work, ensure a branch, commit, PR, and CI status are explicit.",
        context_guard(),
    ]
)
print(json.dumps({"continue": True, "systemMessage": message}, separators=(",", ":")))
