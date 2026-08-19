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
import math
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

import review_wrapper_common as rw
from agy_review import GEMINI_PROMPT_VERSION, gemini_config_hash, run_bounded

SESSIONS_DIR = Path.home() / ".codex" / "sessions"
ARTIFACT_LAG_S = 130.0  # measured PR #1386 lag (C-HE-18 §2)
ARTIFACT_POLL_S = 2.0
PROMPT_VERSION = "codex-review-v2-exec"
CHANNEL = "codex"
PRODUCER = "codex_review_wrapper"
MAX_FINDINGS = 8
#: run_bounded's own timeout exit status (agy_review.run_bounded appends the detail to stderr).
_RUN_BOUNDED_TIMEOUT_RC = 124


def review_instructions(binding: dict[str, str]) -> str:
    """The review brief + output contract, run through `codex exec` (interface probes re-run at
    execution: `codex review --base` rejects a PROMPT; `codex review "<prompt>"` treats it as a
    review target and, on a real PR-sized diff, answers in its own native findings JSON and
    ignores the output contract -- round 3 on the S1 branch. `codex exec` follows the brief and
    hands the final message back through `-o`)."""
    return (
        "You are an out-of-family code reviewer for an agent-harness monorepo. Review EXACTLY "
        f"the committed diff `git diff --binary {binding['base_sha']} {binding['head_sha']}` "
        "(run that command read-only; you may open the files it touches at that HEAD for "
        "context) for real defects: correctness, hook and permission semantics, contract "
        "drift, unsafe state handling, concurrency, and tests that would stay green if the "
        f"change were reverted. Report at most {MAX_FINDINGS} findings, each with an exact "
        "file:line location and a concrete message; no style nits; only findings proven by the "
        "diff. Do not edit files. When done, print ONE fenced ```json block, and nothing after "
        "it, with exactly these keys: verdict (APPROVE|BLOCK), findings (array of "
        "{severity: P1|P2|P3, location, message}; BLOCK requires at least one finding, APPROVE "
        "requires none), and copy these six values VERBATIM: "
        + ", ".join(f"{k}={binding[k]}" for k in rw.BINDING_FIELDS)
        + ". No other keys. A missing or altered value invalidates the review."
    )


def build_command(repo: Path, instructions: str, *, output_file: Path) -> list[str]:
    """`codex exec` in a read-only sandbox; the final assistant message is ALSO written to
    `output_file` (`-o`), the channel's most reliable output surface (probed 2026-08-19)."""
    return [
        "codex",
        "exec",
        "--sandbox",
        "read-only",
        "-c",
        'preferred_auth_method="chatgpt"',
        "-C",
        str(repo),
        "-o",
        str(output_file),
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
    # Whole-second floor: a filesystem may truncate mtime granularity, so an artifact written
    # right after a fractional `started_at` must not fall below it (gemini round 3). No upper
    # bound: the head_sha content check is the binding, and `now` only names the scan time.
    del now
    floor = math.floor(started_at)
    candidates: list[tuple[float, Path]] = []
    for p in root.rglob("*.jsonl"):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime >= floor:
            candidates.append((mtime, p))
    for _, p in sorted(candidates, key=lambda t: t[0], reverse=True):
        try:
            if head_sha in p.read_text(errors="replace"):
                return p
        except OSError:
            continue
    return None


def _default_invoke(repo: Path, instructions: str) -> Callable[[float], rw.Attempt]:
    def invoke(timeout: float) -> rw.Attempt:
        # Subscription auth, never the metered key (justfile `_require-codex-subscription`).
        env = {k: v for k, v in os.environ.items() if k != "OPENAI_API_KEY"}
        with tempfile.TemporaryDirectory(prefix="arhugula-codex-review-") as scratch:
            out_file = Path(scratch) / "last-message.md"
            proc = run_bounded(
                build_command(repo, instructions, output_file=out_file),
                cwd=repo,
                timeout=timeout,
                env=env,
            )
            # The `-o` file is the channel's own final-message surface: read it as stdout when
            # it exists (stdout may be truncated/frozen -- the PR #1386 mode; stderr carries the
            # transcript). The same positive parse applies to whichever surface is used.
            stdout = proc.stdout or ""
            if out_file.exists():
                last = out_file.read_text(errors="replace")
                if last.strip():
                    stdout = last
        timed_out = proc.returncode == _RUN_BOUNDED_TIMEOUT_RC and "timed out" in (
            proc.stderr or ""
        )
        return rw.Attempt(stdout, proc.stderr or "", proc.returncode, timed_out)

    return invoke


def run_codex_review(
    repo: Path,
    base: str,
    *,
    invoke: Callable[[float], rw.Attempt] | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> rw.ReviewOutcome:
    try:
        binding = _binding(repo, base)
    except subprocess.CalledProcessError as exc:
        # An unresolvable base / detached state is a caller-side, human-fixable condition:
        # REVIEWER_UNAVAILABLE(permanent) with the git error as evidence, never a traceback
        # (gemini failover round 2 on the S1 branch: "an invalid base reference ... will
        # crash the process entirely during the binding phase").
        return rw.ReviewOutcome(
            "REVIEWER_UNAVAILABLE",
            CHANNEL,
            "permanent",
            f"binding: {' '.join(exc.cmd[:4])} failed: {(exc.stderr or '').strip()[:300]}",
        )
    instructions = review_instructions(binding)
    invoke = invoke or _default_invoke(repo, instructions)
    started_wall = time.time()
    deadline = clock() + rw.TOTAL_BUDGET_S
    wall_deadline = started_wall + rw.TOTAL_BUDGET_S
    source = "stdout"

    def conclusive(text: str) -> bool:
        return rw.parse_verdict(CHANNEL, text, binding).terminal != "REVIEWER_UNAVAILABLE"

    def attempt_with_artifact(timeout: float) -> rw.Attempt:
        nonlocal source
        att = invoke(timeout)
        if conclusive(att.stdout):
            return att
        if att.timed_out:
            # Killed at the cap: the verdict may already sit in the session artifact (the CLI
            # persists the final message before it finishes streaming). One look, no wait --
            # the same positive parse + byte-compare applies; otherwise the timeout stands.
            art = find_session_artifact(
                binding["head_sha"], started_at=started_wall, now=time.time(), root=SESSIONS_DIR
            )
            if art is not None:
                text = artifact_text(art)
                if conclusive(text):
                    source = "session-artifact"
                    return rw.Attempt(text, att.stderr, att.returncode, False)
            return att
        # `codex review` echoes its transcript (final message included) on stderr: the same
        # positive parse + byte-compare applies there before the session artifact is consulted.
        if conclusive(att.stderr):
            source = "stderr"
            return rw.Attempt(att.stderr, att.stderr, att.returncode, False)
        # stdout inconclusive: wait up to ARTIFACT_LAG_S for the session artifact, never past
        # the shared 1260 s budget (Codex round-1 P2 on the plan).
        end = min(time.time() + ARTIFACT_LAG_S, wall_deadline)
        while True:
            art = find_session_artifact(
                binding["head_sha"], started_at=started_wall, now=time.time(), root=SESSIONS_DIR
            )
            if art is not None:
                text = artifact_text(art)
                if conclusive(text):
                    source = "session-artifact"
                    return rw.Attempt(text, att.stderr, att.returncode, False)
            if time.time() >= end:
                break
            time.sleep(min(ARTIFACT_POLL_S, max(0.0, end - time.time())))
        return att

    outcome = rw.run_with_retry(
        attempt_with_artifact, channel=CHANNEL, expected=binding, deadline=deadline, clock=clock
    )
    if outcome.terminal != "REVIEWER_UNAVAILABLE":
        outcome.source = source
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


def _gemini_config_hash() -> str:
    """The gemini channel's own config-hash rule (agy_review.gemini_config_hash), so the failover
    computes the identical expected binding the wrapper prompts for."""
    return gemini_config_hash()


#: `just gemini-review` carries its own C-HE-16 §3 budget; this outer cap only fences a wedged
#: `just`/preflight, never the review itself.
FAILOVER_SUBPROCESS_CAP_S = rw.TOTAL_BUDGET_S + 60.0
GEMINI_PRODUCER = "gemini_review_wrapper"


def _read_envelope(path: Path, expected: dict[str, str]) -> rw.ReviewOutcome | None:
    """The gemini wrapper's OWN terminal envelope (`agy_review --outcome-json`): terminal in the
    C-HE-16 §3 triple, findings a list, and -- identical bar -- a terminal verdict's binding
    byte-equal to THIS invocation's expected six values. Anything else -> None (not an
    envelope we can trust)."""
    if not path.exists():
        return None
    try:
        env = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(env, dict) or env.get("terminal") not in rw.TERMINAL_STATES:
        return None
    findings = env.get("findings")
    if not isinstance(findings, list):
        return None
    if env["terminal"] != "REVIEWER_UNAVAILABLE" and env.get("binding") != expected:
        return rw.ReviewOutcome(
            "REVIEWER_UNAVAILABLE",
            "gemini",
            "transient",
            f"failover envelope bound to a different invocation: {env.get('binding')!r}",
            [],
            dict(expected),
        )
    return rw.ReviewOutcome(
        env["terminal"],
        "gemini",
        env.get("failure_class"),
        str(env.get("reason") or ""),
        findings,
        dict(expected),
        env.get("source"),
    )


def _run_gemini_failover(repo: Path, base: str) -> rw.ReviewOutcome:
    """C-HE-17 §1: on primary REVIEWER_UNAVAILABLE run `just gemini-review` ONCE under the
    IDENTICAL bar. The gemini wrapper (U-HE-06) does its own schema parse and records its own
    rows; this reads back its terminal ENVELOPE (`--outcome-json`), never the raw vendor stdout
    (codex round 3: a vendor exit-2 path may still print a schema-valid APPROVE block) and never
    the exit code. Envelope absent = the wrapper never reached a terminal (recipe preflight
    death, missing `just`, cap): classified from stderr and recorded HERE, the one emitter for
    that case (no global row counting -- gemini round 3 / codex round 3)."""
    try:
        binding = rw.compute_binding(
            repo,
            base,
            channel="gemini",
            prompt_version=GEMINI_PROMPT_VERSION,
            config_hash=_gemini_config_hash(),
        )
    except subprocess.CalledProcessError as exc:
        err = (
            exc.stderr
            if isinstance(exc.stderr, str)
            else (exc.stderr or b"").decode(errors="replace")
        )
        outcome = rw.ReviewOutcome(
            "REVIEWER_UNAVAILABLE",
            "gemini",
            "permanent",
            f"binding: {' '.join(exc.cmd[:4])} failed: {err.strip()[:300]}",
        )
        _emit_rows(outcome, producer=GEMINI_PRODUCER, channel="gemini")
        return outcome
    with tempfile.TemporaryDirectory(prefix="arhugula-gemini-failover-") as scratch:
        envelope = Path(scratch) / "outcome.json"
        # run_bounded (agy_review): bounded wait + process-GROUP cleanup on timeout, so a
        # timed-out `just` cannot leave the wrapper / agy descendants alive to append gate
        # state after this process recorded the failover unavailable (codex round 4). A missing
        # `just` surfaces as its rc-127 CompletedProcess (gemini round 3), never an exception.
        proc = run_bounded(
            ["just", "gemini-review", base, str(envelope)],
            cwd=repo,
            timeout=FAILOVER_SUBPROCESS_CAP_S,
            env=dict(os.environ),
        )
        stdout, stderr = proc.stdout or "", proc.stderr or ""
        outcome = _read_envelope(envelope, binding)
    if outcome is not None:
        return outcome  # the wrapper reached a terminal and recorded its own rows
    outcome = rw.ReviewOutcome(
        "REVIEWER_UNAVAILABLE",
        "gemini",
        rw.classify("gemini", rw.classifier_text(stdout, stderr)),
        "no outcome envelope from the gemini wrapper"
        + (f"; {stderr.strip()[-400:]}" if stderr.strip() else ""),
        [],
        binding,
    )
    _emit_rows(outcome, producer=GEMINI_PRODUCER, channel="gemini")
    return outcome


def _route_to_hitl(arc_id: str, reason: str) -> None:
    """C-HE-20 §1: a REVIEWER_UNAVAILABLE that blocks the arc routes to the EXISTING durable
    HITL queue -- a `DEFERRED-HIL` row via `loop_defer` (loop_lib.sh, the C-HE-09 venue); no new
    escalation store (codex round 4). A failed write is reported loudly; the exit code already
    blocks."""
    lib = rw.REPO / "tools" / "hooks"
    script = (
        f'. "{lib / "lib.sh"}" && . "{lib / "loop_lib.sh"}" && '
        'loop_defer "$1" "review-with-failover: REVIEWER_UNAVAILABLE on both channels — $2"'
    )
    proc = subprocess.run(
        ["bash", "-c", script, "loop_defer", arc_id, reason],
        cwd=rw.REPO,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(
            f"review-with-failover: HITL row NOT written (rc {proc.returncode}): "
            f"{(proc.stderr or '').strip()[-300:]}",
            file=sys.stderr,
        )


def _report(outcome: rw.ReviewOutcome, *, label: str) -> None:
    for f in outcome.findings:
        print(f"- [{f['severity']}] {f['location']}: {f['message']}")
    tail = f" ({outcome.failure_class}: {outcome.reason})" if outcome.reason else ""
    src = f" [source: {outcome.source}]" if outcome.source not in (None, "stdout") else ""
    print(f"{label}: {outcome.terminal}{tail}{src}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="main")
    p.add_argument(
        "--failover",
        action="store_true",
        help="D-C failover (C-HE-17): on REVIEWER_UNAVAILABLE run `just gemini-review` once "
        "under the identical bar; its verdict blocks",
    )
    p.add_argument(
        "--invoke-test-empty", action="store_true", help=argparse.SUPPRESS
    )  # test seam: zero-byte channel
    args = p.parse_args(argv)
    invoke = (lambda timeout: rw.Attempt("", "", 0, False)) if args.invoke_test_empty else None

    def primary() -> rw.ReviewOutcome:
        outcome = run_codex_review(Path.cwd(), args.base, invoke=invoke)
        _emit_rows(outcome)  # the primary's row lands before the failover runs
        _report(outcome, label="codex-review")
        return outcome

    if not args.failover:
        return rw.exit_code(primary())
    first, fo = rw.run_with_failover(primary, lambda: _run_gemini_failover(Path.cwd(), args.base))
    if fo is None:
        return rw.exit_code(first)
    # NO second emission for the failover: `just gemini-review` (agy_review, U-HE-06) already
    # wrote its rows and round outcome, or `_run_gemini_failover` did when the recipe never ran.
    _report(fo, label="gemini-review (failover)")
    if fo.terminal == "REVIEWER_UNAVAILABLE":
        both = f"codex: {first.reason}; gemini: {fo.reason}"
        print(f"review-with-failover: BOTH channels unavailable -- {both}", file=sys.stderr)
        _route_to_hitl(rw.env_arc_and_lane()[0], both)
    return rw.exit_code(fo)


if __name__ == "__main__":
    raise SystemExit(main())
