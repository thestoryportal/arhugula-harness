#!/usr/bin/env python3
"""Fail-closed wrapper for the Codex review channel (C-HE-18).

Mirrors tools/agy_review.py's hardening: bounded timeout, exit-code-independent
capture, declared-schema parse, permanent/transient classification, and a
REVIEWER_UNAVAILABLE terminal on ANY parse failure. When stdout is inconclusive
it reads the channel's own session artifact (the PR #1386 mode: log frozen at
313 bytes for 130 s after process exit while the real verdict sat only in
~/.codex/sessions/) -- and still requires a positive schema parse from it.

Exit 0 APPROVE / 1 BLOCK / 2 REVIEWER_UNAVAILABLE. The terminal line on stderr
(`codex-review: <TERMINAL>`) is the completion signal callers read; the exit
code is a convenience, never a verdict (C-HE-15 §1).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

import review_wrapper_common as rw
from agy_review import run_bounded

SESSIONS_DIR = Path.home() / ".codex" / "sessions"
ARTIFACT_LAG_S = 130.0  # measured PR #1386 lag (C-HE-18 §2)
ARTIFACT_POLL_S = 2.0
PROMPT_VERSION = "codex-review-v1"
CHANNEL = "codex"
PRODUCER = "codex_review_wrapper"
#: run_bounded's own timeout exit status (agy_review.run_bounded appends the detail to stderr).
_RUN_BOUNDED_TIMEOUT_RC = 124


def review_instructions(binding: dict[str, str]) -> str:
    return (
        "Review the diff for correctness defects. When done, print ONE fenced ```json block, "
        "and nothing after it, with exactly these keys: verdict (APPROVE|BLOCK), findings "
        "(array of {severity: P1|P2|P3, location, message}), and copy these six values "
        "VERBATIM: " + ", ".join(f"{k}={binding[k]}" for k in rw.BINDING_FIELDS) + ". "
        "No other keys. A missing or altered value invalidates the review."
    )


def build_command(base: str, instructions: str) -> list[str]:
    return [
        "codex",
        "review",
        "-c",
        'preferred_auth_method="chatgpt"',
        "--base",
        base,
        instructions,
    ]


def _config_hash() -> str:
    cfg = Path.home() / ".codex" / "config.toml"
    body = cfg.read_bytes() if cfg.exists() else b""
    return hashlib.sha256(body).hexdigest()[:16]


def _binding(repo: Path, base: str) -> dict[str, str]:
    return rw.compute_binding(
        repo, base, channel=CHANNEL, prompt_version=PROMPT_VERSION, config_hash=_config_hash()
    )


def artifact_text(path: Path) -> str:
    """Session artifacts are JSONL envelopes: the assistant text (with its fenced block) sits
    INSIDE string fields, newline-escaped. Deserialize every line and collect all string values
    so the fenced JSON is visible to the parser (Codex round-2 P1 on the plan: raw `read_text()`
    can never match `_FENCE_RE`)."""
    out: list[str] = []

    def collect(v: object) -> None:
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                collect(x)
        elif isinstance(v, list):
            for x in v:
                collect(x)

    for line in path.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            collect(json.loads(line))
        except json.JSONDecodeError:
            out.append(line)  # a non-JSON line is kept verbatim; the schema parse decides
    return "\n".join(out)


def find_session_artifact(
    head_sha: str, *, started_at: float, now: float, root: Path = SESSIONS_DIR
) -> Path | None:
    """Newest file under root modified after started_at whose content contains head_sha
    (C-HE-18 §2)."""
    if not root.is_dir():
        return None
    candidates: list[tuple[float, Path]] = []
    for p in root.rglob("*.jsonl"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if started_at <= mtime <= now:
            candidates.append((mtime, p))
    for _, p in sorted(candidates, key=lambda t: t[0], reverse=True):
        try:
            if head_sha in p.read_text(errors="replace"):
                return p
        except OSError:
            continue
    return None


def _default_invoke(repo: Path, base: str, instructions: str) -> Callable[[float], rw.Attempt]:
    def invoke(timeout: float) -> rw.Attempt:
        # Subscription auth, never the metered key (justfile `_require-codex-subscription`).
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        proc = run_bounded(build_command(base, instructions), cwd=repo, timeout=timeout, env=env)
        timed_out = proc.returncode == _RUN_BOUNDED_TIMEOUT_RC and "timed out" in (
            proc.stderr or ""
        )
        return rw.Attempt(proc.stdout or "", proc.stderr or "", proc.returncode, timed_out)

    return invoke


def run_codex_review(
    repo: Path,
    base: str,
    *,
    invoke: Callable[[float], rw.Attempt] | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> rw.ReviewOutcome:
    binding = _binding(repo, base)
    instructions = review_instructions(binding)
    invoke = invoke or _default_invoke(repo, base, instructions)
    started_wall = time.time()
    deadline = clock() + rw.TOTAL_BUDGET_S
    wall_deadline = started_wall + rw.TOTAL_BUDGET_S
    used_artifact = False

    def attempt_with_artifact(timeout: float) -> rw.Attempt:
        nonlocal used_artifact
        att = invoke(timeout)
        if att.timed_out:
            return att
        if rw.parse_verdict(CHANNEL, att.stdout, binding).terminal != "REVIEWER_UNAVAILABLE":
            return att
        # stdout inconclusive: wait up to ARTIFACT_LAG_S for the session artifact, never past
        # the shared 1260 s budget (Codex round-1 P2 on the plan).
        end = min(time.time() + ARTIFACT_LAG_S, wall_deadline)
        while True:
            art = find_session_artifact(
                binding["head_sha"], started_at=started_wall, now=time.time(), root=SESSIONS_DIR
            )
            if art is not None:
                text = artifact_text(art)
                if rw.parse_verdict(CHANNEL, text, binding).terminal != "REVIEWER_UNAVAILABLE":
                    used_artifact = True
                    return rw.Attempt(text, att.stderr, att.returncode, False)
            if time.time() >= end:
                break
            time.sleep(min(ARTIFACT_POLL_S, max(0.0, end - time.time())))
        return att

    outcome = rw.run_with_retry(
        attempt_with_artifact, channel=CHANNEL, expected=binding, deadline=deadline, clock=clock
    )
    if used_artifact and outcome.terminal != "REVIEWER_UNAVAILABLE":
        outcome.source = "session-artifact"
    return outcome


def _emit_rows(
    outcome: rw.ReviewOutcome, *, producer: str = PRODUCER, channel: str = CHANNEL
) -> None:
    arc_id, lane_id = rw.env_arc_and_lane()
    round_n = int(os.environ.get("HARNESS_ROUND_N", "0"))
    rw.emit_outcome(outcome, producer=producer, arc_id=arc_id, lane_id=lane_id, round_n=round_n)
    rw.record_round_outcome_if_reserved(
        arc_id,
        round_n,
        channel=channel,
        terminal=outcome.terminal,
        finding_count=len(outcome.findings),
    )


def _report(outcome: rw.ReviewOutcome, *, label: str) -> None:
    for f in outcome.findings:
        print(f"- [{f['severity']}] {f['location']}: {f['message']}")
    tail = f" ({outcome.failure_class}: {outcome.reason})" if outcome.reason else ""
    src = f" [source: {outcome.source}]" if outcome.source == "session-artifact" else ""
    print(f"{label}: {outcome.terminal}{tail}{src}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="main")
    p.add_argument(
        "--invoke-test-empty", action="store_true", help=argparse.SUPPRESS
    )  # test seam: zero-byte channel
    args = p.parse_args(argv)
    invoke = (lambda timeout: rw.Attempt("", "", 0, False)) if args.invoke_test_empty else None
    outcome = run_codex_review(Path.cwd(), args.base, invoke=invoke)
    _emit_rows(outcome)
    _report(outcome, label="codex-review")
    return rw.exit_code(outcome)


if __name__ == "__main__":
    raise SystemExit(main())
