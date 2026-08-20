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

#: C-HE-16 §3 retry parameters (spec v1.2 X2). This module is the single home of the two
#: budget constants for BOTH channels -- agy_review re-exports them (a back-import from
#: agy_review made `import agy_review` fail on the partially-initialised module; codex round
#: 3). The per-attempt figure is a CAP: every attempt runs min(cap, remaining - margin) on the
#: shared 1260 s deadline, so a second attempt exists only after a FAST transient failure
#: (empty output, rate-limit, auth flake). 1200 s is the bound the gemini channel applied per
#: invocation before S1; the v1/v1.1 figure of 550 s (budget arithmetic) killed real codex
#: reviews mid-flight.
PER_ATTEMPT_TIMEOUT_S = 1200.0
MAX_ATTEMPTS = 2
TOTAL_BUDGET_S = 1260.0
SECOND_ATTEMPT_MARGIN_S = 30.0
#: A stream longer than this is a transcript (the vendor CLIs echo the diff + prompt), not a
#: CLI error: only its tail can carry the fatal line, and diff/prompt text must never feed the
#: classifier (codex round 3 read "not logged in" out of THIS diff and said permanent).
CLASSIFIER_STREAM_LIMIT = 4096
CLASSIFIER_TAIL = 512
#: Environment a nested reviewer process may see: `just`'s dotenv-load injects the harness
#: runtime's provider credentials, and a diff-induced shell command inside the reviewer could
#: surface them into the transcript/model; the sandbox hides files, not the environment (codex
#: rounds 6-7). ALLOWLIST, not denylist (a `DATABASE_URL` / `SENTRY_DSN` carries a secret
#: without a secret-shaped name): exact names the CLIs need to run + vendor/harness prefixes,
#: and a secret-name filter on top of the prefixes.
_ENV_ALLOW_EXACT = frozenset(
    {
        "PATH",
        "HOME",
        "USER",
        "LOGNAME",
        "SHELL",
        "TERM",
        "LANG",
        "LANGUAGE",
        "TMPDIR",
        "TZ",
        "PWD",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "no_proxy",
    }
)
_ENV_ALLOW_PREFIXES = ("LC_", "XDG_", "HARNESS_", "CODEX_", "AGY_", "ANTIGRAVITY_")
_SECRET_NAME_RE = re.compile(r"(KEY|TOKEN|SECRET|CREDENTIAL|PASSWORD|PASSWD|AUTH)", re.I)


def reviewer_env(base: dict[str, str] | None = None) -> dict[str, str]:
    """The environment for a nested reviewer CLI: only allowlisted names / prefixes (never a
    secret-shaped name even under an allowed prefix), plus HARNESS_CODEX_REVIEW_ISOLATED=1 so
    the repo's own hooks (SessionStart / Stop / checkpoint / loop-ledger writers) stay inert
    inside the reviewer (codex round 6)."""
    src = os.environ if base is None else base
    env = {
        k: v
        for k, v in src.items()
        if (k in _ENV_ALLOW_EXACT or k.startswith(_ENV_ALLOW_PREFIXES))
        and not _SECRET_NAME_RE.search(k)
    }
    env["HARNESS_CODEX_REVIEW_ISOLATED"] = "1"
    return env


#: C-HE-16 §4 -- per-CLI classifier, ONE ROW PER (channel, regex, class). First match wins.
#: Unknown text -> transient (fail-safe toward retry-then-block, never toward APPROVE).
#: This table WILL drift with vendor error text; every row is unit-tested in
#: tools/test_review_wrapper.py::test_classifier_table.
CLASSIFIER: tuple[tuple[str, re.Pattern[str], str], ...] = (
    ("codex", re.compile(r"requires a newer version of Codex"), "permanent"),
    ("codex", re.compile(r"not logged in|login|unauthorized|401|403", re.I), "permanent"),
    # a missing binary: the shell's wording AND run_bounded's Popen OSError wording (codex round 5)
    ("codex", re.compile(r"command not found|No such file or directory: '?codex'?"), "permanent"),
    ("codex", re.compile(r"rate limit|429|timed out|ETIMEDOUT|ECONNRESET", re.I), "transient"),
    (
        "gemini",
        re.compile(
            r"antigravity .* not (installed|logged in)|unauthorized|not found on PATH"
            r"|No such file or directory: '?agy'?|command not found",
            re.I,
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
    #: the six binding values the invocation was held to (byte-equal to the channel's on
    #: APPROVE/BLOCK; the wrapper's expected values on a retry-loop REVIEWER_UNAVAILABLE so the
    #: silent-death row is still bound to its head; None only for a bare parse failure)
    binding: dict[str, str] | None = None
    source: str | None = None  # stdout | session-artifact | None


def classify(channel: str, text: str) -> str:
    for ch, rx, cls in CLASSIFIER:
        if ch == channel and rx.search(text):
            return cls
    return "transient"


#: Only ERROR-SHAPED lines reach the C-HE-16 §4 table: a line with an error prefix (`Error:`,
#: `fatal:`, `[Errno`, `HTTP 401`, `bash: x:` ...) or one carrying an unambiguous failure phrase.
#: Reviewer prose / echoed diff text that merely DISCUSSES logins or 401s is never classified
#: (codex rounds 3/8/9).
_ERROR_LINE_RE = re.compile(
    r"^\s*(?:[\w./ -]+:\s*)?(?:error|fatal|panic|warning|\[errno|http/?\s?\d{3}\b|\d{3} "
    r"(?:unauthorized|forbidden|too many))"
    r"|command not found|no such file or directory|etimedout|econnreset|resource_exhausted"
    r"|rate limit|timed out|requires a newer version|not logged in|not installed|not found on path"
    r"|deadline exceeded",
    re.I,
)


def classifier_text(stdout: str, stderr: str) -> str:
    """The part of a channel's output the C-HE-16 §4 table may read: the error-shaped lines of
    stderr -- where both CLIs report usage / auth / binary errors -- or of stdout when stderr is
    silent; a long stream contributes only its tail (a transcript echoes the reviewed diff)."""

    def part(s: str) -> str:
        s = s or ""
        s = s if len(s) <= CLASSIFIER_STREAM_LIMIT else s[-CLASSIFIER_TAIL:]
        return "\n".join(ln for ln in s.splitlines() if _ERROR_LINE_RE.search(ln))

    if (stderr or "").strip():
        return part(stderr)
    return part(stdout)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def bound_diff(repo: Path, base_sha: str, head_sha: str) -> bytes:
    """THE reviewed bytes: `git diff --binary <base_sha> <head_sha>` as raw bytes (a diff may
    carry non-UTF-8 hunks; gemini round 3). Both the digest and the reviewer's payload come
    from this one function so the digest describes exactly what was reviewed (codex round 3)."""
    return subprocess.run(
        ["git", "-C", str(repo), "diff", "--binary", base_sha, head_sha],
        check=True,
        capture_output=True,
    ).stdout


def compute_binding(
    repo: Path, base: str, *, channel: str, prompt_version: str, config_hash: str
) -> dict[str, str]:
    """The wrapper's OWN values for the six binding fields (C-HE-15 §4). Never read from the
    channel. `diff_digest` covers the committed diff merge-base(base, HEAD)..HEAD -- the state
    the review is bound to (the loop commits before it reviews)."""
    head_sha = _git(repo, "rev-parse", "HEAD")
    # merge-base against the CAPTURED head, not "HEAD" again: a commit landing between the two
    # git calls must not bind a base computed for a head other than head_sha (merge-gate L1)
    base_sha = _git(repo, "merge-base", base, head_sha)
    return {
        "head_sha": head_sha,
        "base_sha": base_sha,
        "diff_digest": hashlib.sha256(bound_diff(repo, base_sha, head_sha)).hexdigest(),
        "reviewer_identity": channel if channel.endswith("-review") else f"{channel}-review",
        "prompt_version": prompt_version,
        "config_hash": config_hash,
    }


def load_schema(channel: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{channel}.schema.json").read_text())


def extract_fenced_json(text: str) -> str | None:
    """Exactly ONE distinct fenced block, or None. Two different blocks are AMBIGUOUS output
    (C-HE-15 §2 -> REVIEWER_UNAVAILABLE; a later APPROVE must never override an earlier BLOCK
    -- codex round 4). Byte-identical repeats collapse to one: the session artifact carries the
    final message in several envelopes."""
    blocks = {b.strip() for b in _FENCE_RE.findall(text)}
    if len(blocks) != 1:
        return None
    return next(iter(blocks))


def parse_verdict(
    channel: str, text: str, expected: dict[str, str], *, source: str = "stdout"
) -> ReviewOutcome:
    """Positive parse or REVIEWER_UNAVAILABLE. Nothing in here maps absence to APPROVE."""

    def unavailable(reason: str) -> ReviewOutcome:
        return ReviewOutcome("REVIEWER_UNAVAILABLE", channel, None, reason, [], None, source)

    # ONE enforcement point for "nothing to parse": empty/whitespace output has no fenced
    # block, so the fence check is the single guard (a separate empty guard was an
    # equivalent mutant under probe); the reason still names which shape arrived.
    raw = extract_fenced_json(text or "")
    if raw is None:
        n = len({b.strip() for b in _FENCE_RE.findall(text or "")})
        if n > 1:
            return unavailable(f"ambiguous output: {n} distinct fenced json blocks")
        return unavailable("empty output" if not (text or "").strip() else "no fenced json block")
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
    """C-HE-16 §3 (v1.2 X2): up to 2 attempts under a 1260 s shared deadline, each capped at
    PER_ATTEMPT_TIMEOUT_S; permanent skips retry.

    ``deadline`` is an absolute value on ``clock``'s axis. Attempt 1's timeout is
    min(cap, remaining); attempt 2's is min(cap, remaining - 30) computed at attempt time.
    Exhaustion of the budget is HITL-recoverable (a wedged reviewer login is human-fixable),
    not permanent.
    """
    last_reason = "no attempt made"

    def unavailable(cls: str, reason: str) -> ReviewOutcome:
        return ReviewOutcome("REVIEWER_UNAVAILABLE", channel, cls, reason, [], dict(expected))

    for attempt_n in range(1, MAX_ATTEMPTS + 1):
        remaining = deadline - clock()
        margin = 0.0 if attempt_n == 1 else SECOND_ATTEMPT_MARGIN_S
        timeout = min(PER_ATTEMPT_TIMEOUT_S, remaining - margin)
        if timeout <= 0:
            return unavailable(
                "transient",
                f"HITL-recoverable: review budget exhausted before attempt {attempt_n} "
                f"({last_reason})",
            )
        att = invoke(timeout)
        combined = classifier_text(att.stdout, att.stderr)
        if att.timed_out:
            # A timed-out attempt is transient but NOT re-invoked: the retry exists for FAST
            # failures (spec v1.2 X2); after a cap-length attempt only a ~30 s stub of budget
            # remains and a second full review cannot fit (codex round 4).
            return unavailable(
                "transient",
                f"HITL-recoverable: attempt {attempt_n} timed out after {timeout:.0f}s "
                "(a timed-out attempt is not re-invoked)",
            )
        outcome = parse_verdict(channel, att.stdout, expected)
        if outcome.terminal == "BLOCK":
            return outcome  # a crash after a parsed BLOCK still blocks: findings are preserved
        if outcome.terminal == "APPROVE":
            if att.returncode in (0, None):
                return outcome
            # A reviewer that exited non-zero does not get to approve (gemini round 3: exit
            # code is never a COMPLETION signal, but a failed process's approval is not a
            # verdict either); classified like any other failure and retried if transient.
            outcome = ReviewOutcome(
                "REVIEWER_UNAVAILABLE",
                channel,
                None,
                f"exit {att.returncode} with a parsed APPROVE (fail-closed: not counted)",
            )
        cls = classify(channel, combined)
        last_reason = f"attempt {attempt_n}: {outcome.reason}"
        if cls == "permanent":
            return unavailable("permanent", last_reason)
        # transient (incl. empty first attempt) -> one bounded re-invocation, no backoff
    if clock() >= deadline:
        return unavailable("transient", f"HITL-recoverable: {last_reason}")
    return unavailable("transient", last_reason)


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


def round_n_for(arc_id: str, producer: str, rows: list[dict] | None = None) -> int:
    """`HARNESS_ROUND_N` when the loop sets it; otherwise the next round for this (arc, producer)
    derived from the gate log (codex round 6: without this every invocation was round 0 and
    distinct review heads collapsed into one round)."""
    env = os.environ.get("HARNESS_ROUND_N")
    if env is not None:
        return int(env)
    prior = [
        r["round_n"]
        for r in (rows if rows is not None else fr.read_rows())
        if r.get("arc_id") == arc_id
        and r.get("producer") == producer
        and r.get("round_n") is not None
    ]
    return max(prior, default=0) + 1


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
            try:
                rs.record_round_outcome(
                    arc_id,
                    round_n,
                    channel=channel,
                    terminal=terminal,
                    finding_count=finding_count,
                )
            except rs.RoundOutcomeConflict:
                # Gate-log rounds are per (arc, producer) (`round_n_for`), so a D-C
                # failover's two legs can both carry the same number arc-level; the
                # reservation map is append-only (C-HE-25), so land this leg at the next
                # free arc-level round instead of erasing or dropping it (codex round-5 P2).
                rs.record_round_outcome_next(
                    arc_id, channel=channel, terminal=terminal, finding_count=finding_count
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
    if outcome.terminal == "APPROVE":
        # A clean review is durable evidence too (C-HE-17 §5 "both rows in the record"): one
        # bound `no_finding` marker per approving invocation (codex round 3), never a `finding`.
        return [
            dict(
                location=outcome.channel,
                observed_evidence=f"APPROVE from {outcome.source or 'stdout'}: 0 findings",
                expected_contract="C-HE-15 §1 positive schema parse",
                severity="info",
                finding_type="clean-approve",
                lineage_claim="wrapper",
                producer=producer,
                record_kind="no_finding",
                cause_attribution=None,
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
    round_n: int | None,
    path: Path | None = None,
) -> list[dict]:
    """Append every observation of `outcome` to the gate log in ONE critical section: when
    `round_n` is None the round is minted there (`round_n_for` against the log as it stands
    under the lock -- two concurrent wrappers on one arc cannot both take the same round; codex
    round 7), and each `finding_id` is minted against the same snapshot. Returns the rows as
    written (their `round_n` is the allocated one). A `RecordError` propagates: the record is
    part of the contract (C-HE-18 §3), so a failed write must not be silent."""

    def build(rows: list[dict]) -> list[tuple[dict, fr.Envelope]]:
        n = round_n if round_n is not None else round_n_for(arc_id, producer, rows)
        pairs = []
        for obs in outcome_rows(
            outcome, producer=producer, arc_id=arc_id, lane_id=lane_id, round_n=n
        ):
            env = fr.Envelope(**{k: obs[k] for k in _ENV_KEYS})
            core = {k: v for k, v in obs.items() if k not in _ENV_KEYS}
            pairs.append((core, env))
        return pairs

    return fr.append_observations(build, path)
