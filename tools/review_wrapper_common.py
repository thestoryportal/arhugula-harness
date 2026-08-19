#!/usr/bin/env python3
"""Fail-closed core shared by every reviewer channel wrapper (C-HE-15/16/17).

A verdict COUNTS only when the channel's output parses to its declared JSON
schema AND every one of the six binding fields byte-equals the value this
module computed for the invocation. Exit codes are never a completion signal.
Terminal states are exactly APPROVE / BLOCK / REVIEWER_UNAVAILABLE.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import finding_record as fr
import jsonschema
from agy_review import TOTAL_REVIEW_TIMEOUT_SECONDS

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "tools" / "review_schemas"

TERMINAL_STATES = ("APPROVE", "BLOCK", "REVIEWER_UNAVAILABLE")
BINDING_FIELDS = (
    "head_sha",
    "base_sha",
    "diff_digest",
    "reviewer_identity",
    "prompt_version",
    "config_hash",
)

#: C-HE-16 §3 retry parameters. The total budget reuses agy_review's shared deadline.
PER_ATTEMPT_TIMEOUT_S = 550.0
MAX_ATTEMPTS = 2
TOTAL_BUDGET_S = TOTAL_REVIEW_TIMEOUT_SECONDS  # 1260.0
SECOND_ATTEMPT_MARGIN_S = 30.0

#: C-HE-16 §4 -- per-CLI classifier, ONE ROW PER (channel, regex, class). First match wins.
#: Unknown text -> transient (fail-safe toward retry-then-block, never toward APPROVE).
#: This table WILL drift with vendor error text; every row is unit-tested in
#: tools/test_review_wrapper.py::test_classifier_table.
CLASSIFIER: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("codex", re.compile(r"requires a newer version of Codex"), "permanent"),
    ("codex", re.compile(r"not logged in|login|unauthorized|401|403", re.I), "permanent"),
    ("codex", re.compile(r"command not found"), "permanent"),
    ("codex", re.compile(r"rate limit|429|timed out|ETIMEDOUT|ECONNRESET", re.I), "transient"),
    (
        "gemini",
        re.compile(
            r"antigravity .* not (installed|logged in)|unauthorized|not found on PATH", re.I
        ),
        "permanent",
    ),
    ("gemini", re.compile(r"RESOURCE_EXHAUSTED|429|deadline", re.I), "transient"),
)

_FENCE_RE = re.compile(r"```json\s*\n(.*?)\n\s*```", re.S)


@dataclass
class Attempt:
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool


@dataclass
class ReviewOutcome:
    terminal: str  # APPROVE | BLOCK | REVIEWER_UNAVAILABLE
    channel: str
    failure_class: str | None  # permanent | transient | None
    reason: str
    findings: list[dict] = field(default_factory=list)
    binding: dict[str, str] | None = None
    source: str | None = None  # stdout | session-artifact | None


def classify(channel: str, text: str) -> str:
    for ch, rx, cls in CLASSIFIER:
        if ch == channel and rx.search(text):
            return cls
    return "transient"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def compute_binding(
    repo: Path, base: str, *, channel: str, prompt_version: str, config_hash: str
) -> dict[str, str]:
    """The wrapper's OWN values for the six binding fields (C-HE-15 §4). Never read from the
    channel. `diff_digest` covers the committed diff merge-base(base, HEAD)..HEAD -- the state
    the review is bound to (the loop commits before it reviews)."""
    head_sha = _git(repo, "rev-parse", "HEAD")
    base_sha = _git(repo, "merge-base", base, "HEAD")
    diff = subprocess.run(
        ["git", "-C", str(repo), "diff", base_sha, "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return {
        "head_sha": head_sha,
        "base_sha": base_sha,
        "diff_digest": hashlib.sha256(diff.encode()).hexdigest(),
        "reviewer_identity": channel if channel.endswith("-review") else f"{channel}-review",
        "prompt_version": prompt_version,
        "config_hash": config_hash,
    }


def load_schema(channel: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{channel}.schema.json").read_text())


def extract_fenced_json(text: str) -> str | None:
    blocks = _FENCE_RE.findall(text)
    return blocks[-1] if blocks else None


def parse_verdict(
    channel: str, text: str, expected: dict[str, str], *, source: str = "stdout"
) -> ReviewOutcome:
    """Positive parse or REVIEWER_UNAVAILABLE. Nothing in here maps absence to APPROVE."""

    def unavailable(reason: str) -> ReviewOutcome:
        return ReviewOutcome("REVIEWER_UNAVAILABLE", channel, None, reason, [], None, source)

    if not text or not text.strip():
        return unavailable("empty output")
    raw = extract_fenced_json(text)
    if raw is None:
        return unavailable("no fenced json block")
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        return unavailable(f"malformed json: {exc.msg}")
    try:
        jsonschema.validate(body, load_schema(channel))
    except jsonschema.ValidationError as exc:
        return unavailable(f"schema: {exc.message}")
    for key in BINDING_FIELDS:
        if body[key] != expected[key]:
            return unavailable(
                f"binding mismatch on {key}: got {body[key]!r} expected {expected[key]!r}"
            )
    return ReviewOutcome(
        body["verdict"], channel, None, "", list(body["findings"]), dict(expected), source
    )


def run_with_retry(
    invoke: Callable[[float], Attempt],
    *,
    channel: str,
    expected: dict[str, str],
    deadline: float,
    clock: Callable[[], float] = time.monotonic,
) -> ReviewOutcome:
    """C-HE-16 §3: 550 s x 2 under a 1260 s shared deadline; permanent skips retry.

    ``deadline`` is an absolute value on ``clock``'s axis. Attempt 1's timeout is
    min(550, remaining); attempt 2's is min(550, remaining - 30) computed at attempt time.
    Exhaustion of the budget is HITL-recoverable (a wedged reviewer login is human-fixable),
    not permanent.
    """
    last_reason = "no attempt made"
    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        remaining = deadline - clock()
        margin = 0.0 if attempt_n == 1 else SECOND_ATTEMPT_MARGIN_S
        timeout = min(PER_ATTEMPT_TIMEOUT_S, remaining - margin)
        if timeout <= 0:
            return ReviewOutcome(
                "REVIEWER_UNAVAILABLE",
                channel,
                "transient",
                f"HITL-recoverable: review budget exhausted before attempt {attempt_n} "
                f"({last_reason})",
            )
        att = invoke(timeout)
        combined = (att.stdout or "") + "\n" + (att.stderr or "")
        if att.timed_out:
            last_reason = f"attempt {attempt_n} timed out after {timeout:.0f}s"
            continue  # transient by definition
        outcome = parse_verdict(channel, att.stdout, expected)
        if outcome.terminal != "REVIEWER_UNAVAILABLE":
            return outcome
        cls = classify(channel, combined)
        last_reason = f"attempt {attempt_n}: {outcome.reason}"
        if cls == "permanent":
            return ReviewOutcome("REVIEWER_UNAVAILABLE", channel, "permanent", last_reason)
        # transient (incl. empty first attempt) -> one bounded re-invocation, no backoff
    if clock() >= deadline:
        return ReviewOutcome(
            "REVIEWER_UNAVAILABLE", channel, "transient", f"HITL-recoverable: {last_reason}"
        )
    return ReviewOutcome("REVIEWER_UNAVAILABLE", channel, "transient", last_reason)


def run_with_failover(
    primary: Callable[[], ReviewOutcome],
    failover: Callable[[], ReviewOutcome],
) -> tuple[ReviewOutcome, ReviewOutcome | None]:
    """C-HE-17: on primary REVIEWER_UNAVAILABLE invoke the failover ONCE under the identical
    bar. The failover's terminal is the gate when it runs."""
    p = primary()
    if p.terminal != "REVIEWER_UNAVAILABLE":
        return p, None
    return p, failover()


def exit_code(outcome: ReviewOutcome) -> int:
    return {"APPROVE": 0, "BLOCK": 1, "REVIEWER_UNAVAILABLE": 2}[outcome.terminal]


def env_arc_and_lane() -> tuple[str, str]:
    """arc_id/lane_id for wrapper rows. Lane-init (U-HE-31) exports HARNESS_LANE_ID; before it,
    a host-cwd fallback keeps the row valid (never empty, never ':')."""
    arc_id = os.environ.get("HARNESS_ARC_ID") or (
        f"branch-{_git(Path.cwd(), 'rev-parse', '--abbrev-ref', 'HEAD')}"
    )
    lane_id = os.environ.get("HARNESS_LANE_ID") or (
        f"{socket.gethostname().split('.')[0]}-{Path.cwd().name}-nolane"
    )
    return arc_id.replace(":", "_"), lane_id.replace(":", "_")


def record_round_outcome_if_reserved(
    arc_id: str, round_n: int, *, channel: str, terminal: str, finding_count: int
) -> None:
    """C-HE-25: persist the per-round terminal outcome on the arc's reservation (folded into
    the arc row at drain, U-HE-19; consumed by N6's REVIEWER_UNAVAILABLE exclusion, U-HE-34).
    No reservation substrate yet (pre-S4b: `tools/reservations.py` absent) or no reservation
    for this arc (backfill) -> no-op. Any other failure is reported, never swallowed: the
    review outcome itself is already on the gate log, so this must not mask it."""
    try:
        import reservations as rs  # U-HE-17
    except ImportError:
        return
    try:
        if rs.current(arc_id) is not None:
            rs.record_round_outcome(
                arc_id, round_n, channel=channel, terminal=terminal, finding_count=finding_count
            )
    except Exception as exc:
        print(f"review wrapper: round outcome not persisted ({exc})", file=sys.stderr)


def outcome_rows(
    outcome: ReviewOutcome, *, producer: str, arc_id: str, lane_id: str, round_n: int
) -> list[dict]:
    """The C-HE-24 observations one outcome yields: one `finding` observation per finding, or
    one `reviewer_unavailable` observation. Each dict is the row MINUS `finding_id`, which is
    minted at append time by `emit_outcome` -> `finding_record.append_observation` under the
    log lock (U-HE-01 interface note: never a per-invocation ordinal)."""
    b = outcome.binding or {}
    env_common = dict(
        ts=fr.now_iso(),
        arc_id=arc_id,
        lane_id=lane_id,
        head_sha=b.get("head_sha"),
        base_sha=b.get("base_sha"),
        diff_digest=b.get("diff_digest"),
        round_n=round_n,
    )
    if outcome.terminal == "REVIEWER_UNAVAILABLE":
        ft = "permanent-fail-exit" if outcome.failure_class == "permanent" else "transient-retry"
        return [
            dict(
                location=outcome.channel,
                observed_evidence=outcome.reason,
                expected_contract="C-HE-15 §1 positive schema parse",
                severity="hard" if ft.startswith("permanent") else "warn",
                finding_type=ft,
                lineage_claim="wrapper",
                producer=producer,
                record_kind="reviewer_unavailable",
                cause_attribution=f"reviewer_unavailable_{outcome.failure_class}",
                **env_common,
            )
        ]
    rows = []
    for f in outcome.findings:
        rows.append(
            dict(
                location=f["location"],
                observed_evidence=f["message"],
                expected_contract="reviewer finding",
                severity=f["severity"],
                finding_type=f"terminal-{outcome.terminal.lower()}",
                lineage_claim="fresh",
                producer=producer,
                record_kind="finding",
                cause_attribution=None,
                **env_common,
            )
        )
    return rows


_ENV_KEYS = (
    "record_kind",
    "ts",
    "arc_id",
    "lane_id",
    "head_sha",
    "base_sha",
    "diff_digest",
    "round_n",
    "cause_attribution",
)


def emit_outcome(
    outcome: ReviewOutcome,
    *,
    producer: str,
    arc_id: str,
    lane_id: str,
    round_n: int,
    path: Path | None = None,
) -> list[dict]:
    """Append every observation of `outcome` to the gate log, minting each `finding_id` under
    the log lock. Returns the rows as written. A `RecordError` propagates: the record is part
    of the contract (C-HE-18 §3), so a failed write must not be silent."""
    written = []
    for obs in outcome_rows(
        outcome, producer=producer, arc_id=arc_id, lane_id=lane_id, round_n=round_n
    ):
        env = fr.Envelope(**{k: obs[k] for k in _ENV_KEYS})
        core = {k: v for k, v in obs.items() if k not in _ENV_KEYS}
        written.append(fr.append_observation(core, env, path))
    return written
