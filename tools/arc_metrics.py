#!/usr/bin/env python3
"""Arc-metrics ledger (B-170) -- per-arc wall-clock capture for efficacy tracking.

One row per arc, appended at merge time. The load-bearing field is
``levers_active``: each arc records which wall-clock levers were live when it
ran, so efficacy becomes a cohort comparison rather than an assertion.

Provenance discipline
---------------------
Fields fall into three classes, and the class is recorded per row so a
consumer can never mistake one for another:

``derived``    computed from git / gh / round-log mtimes at run time
``declared``   supplied by the operator (arc type, decision count, levers) --
               these are judgements, not measurements, and are never guessed
``unmapped``   the input for this field does not exist (e.g. no round logs
               survive for that PR). Recorded as null with a reason, never
               imputed and never silently zeroed.

Fail-closed
-----------
Any external call that exits non-zero, returns empty, or parses to an
unexpected shape aborts with a named cause. A row is never emitted with
silently-zeroed fields -- an absent measurement must be distinguishable from
a measured zero.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import itertools
import json
import os
import re
import shutil
import socket
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

#: Per-process overrides (C-HE-05). Mirrors ARC_METRICS_QUEUE_DIR / ARC_METRICS_MERGED_REF so
#: two subprocess lanes can hold DIFFERENT worktree ledgers over ONE shared queue. Defaults
#: are the checkout root and its tracked ledger -- production behaviour is unchanged when unset.
REPO = Path(os.environ.get("ARC_METRICS_REPO", Path(__file__).resolve().parent.parent))
LEDGER = Path(os.environ.get("ARC_METRICS_LEDGER", REPO / ".harness" / "arc-metrics.jsonl"))

#: Pending captures, deliberately OUTSIDE the repo. A topic worktree is
#: disposed at loop completion, so anything queued inside one is lost with it --
#: and a dirty tracked file there blocks that disposal outright. See
#: ``queue_capture``.
#:
#: A DIRECTORY of one file per arc, not a shared append-log. Parallel arcs are
#: supported, and every concurrency hazard a shared log has here is structural
#: rather than incidental: two writers share an inode, a drain that rewrites the
#: file from a stale snapshot erases whatever landed mid-drain, and a crash
#: between "delete the claim" and "write the remainder" loses the retry. With
#: one file per arc no writer touches another's file, drain never rewrites
#: anything, and a file is unlinked only after its row is safely in the ledger.
QUEUE_DIR = Path(
    os.environ.get(
        "ARC_METRICS_QUEUE_DIR",
        Path.home() / ".gstack" / "projects" / "arhugula-v2" / "arc-metrics-queue",
    )
)

# The codex CLI prints every finding TWICE -- once inline in its narrative
# turn, once in the structured block below this marker. Verified byte-for-byte
# on a real transcript during the 2026-08-14 audit. Findings are counted as
# DISTINCT line-anchored matches rather than halved: a halving constant is
# wrong the moment a transcript carries an odd number of contextual mentions,
# and it cannot tell a quoted past finding from a live one.
FINAL_REVIEW_MARKER = "Full review comments:"

#: `gh run list --commit` matches on the full object name only.
FULL_SHA_LEN = 40

#: Where a row counts as durable. Deliberately the merged remote branch and not
#: `HEAD`: a topic-branch commit can still be reset or abandoned.
MERGED_REF = os.environ.get("ARC_METRICS_MERGED_REF", "origin/main")

#: C-HE-19: CI outcomes are exactly these; CANCELLED is INCOMPLETE, never green.
CI_TERMINAL = ("SUCCESS", "FAILURE", "CANCELLED")
CI_GREEN = frozenset({"SUCCESS"})


def ci_is_green(conclusion: str | None) -> bool:
    """Only an exact `success` counts. CANCELLED is named explicitly (C-HE-19 §2: not by
    whitelist omission -- the branch survives a future edit that broadens `CI_GREEN`); empty
    / pending / None -> False. Consumers: the green-timing exclusion below, ship-pr's
    post-merge acceptance, the merge door (U-HE-23)."""
    if not conclusion:
        return False
    c = conclusion.upper()
    if c == "CANCELLED":
        return False
    return c in CI_GREEN


class AbortError(RuntimeError):
    """A named, fail-closed abort. Never swallowed, never defaulted."""


@dataclass
class ArcRow:
    arc_id: str
    pr: int | None = None
    # -- derived from gh --
    additions: int | None = None
    deletions: int | None = None
    files: int | None = None
    commits: int | None = None
    created_at: str | None = None
    merged_at: str | None = None
    total_arc_wall_s: float | None = None
    merge_sha: str | None = None
    # -- derived from round logs --
    review_rounds: int | None = None
    # None, not []. An empty list is a perfectly good MEASUREMENT -- a one-round
    # arc has no gaps, a clean arc has no P1 rounds -- so defaulting to [] would
    # make "no logs were supplied" indistinguishable from "looked, found none",
    # which is the one distinction this ledger exists to keep.
    round_wall_s: list[float] | None = None
    p1_rounds: list[int] | None = None
    round_log_source: str | None = None
    # Absolute round bounds. Without these the ledger cannot reconstruct the
    # real arc window (first review activity -> merge): gap durations alone
    # cannot say WHERE the loop sat relative to the PR, and this workspace has
    # run both review-then-open and open-then-review workflows.
    first_round_at: str | None = None
    last_round_at: str | None = None
    arc_span_s: float | None = None
    # Whether the surviving logs are the WHOLE arc. When only a suffix of an
    # arc's rounds was archived, `review_rounds` and `arc_span_s` are lower
    # bounds, not measurements -- pr-1060 kept round 10 alone out of >=10, and
    # a note saying so is not enough: `summary` reads fields, not prose, and
    # would average a 1-round 44-minute fragment in as if it were the arc.
    round_completeness: str = "complete"  # complete | partial-suffix
    # -- derived from gh run --
    ci_runs: int | None = None
    ci_wall_s: list[float] = field(default_factory=list)
    # -- declared by operator (judgements, never inferred) --
    arc_type: str | None = None
    decision_count: int | None = None
    levers_active: list[str] = field(default_factory=list)
    # -- bookkeeping --
    provenance: dict[str, str] = field(default_factory=dict)
    captured_at: str = ""
    notes: str = ""
    # -- C-HE-25 extension (all additive; historical rows read as null) --
    record_kind: str = "arc"
    reviewer_identity: str | None = None
    prompt_version: str | None = None
    config_hash: str | None = None
    arc_type_open: str | None = None
    arc_type_close: str | None = None
    arc_type_declared_at: str | None = None  # open | close
    # {round_n: {channel, terminal, finding_count}} -- per-round terminal outcome
    round_outcomes: dict[str, dict] = field(default_factory=dict)
    head_sha: str | None = None
    base_sha: str | None = None
    lane_id: str | None = None
    # derived sensor (C-HE-03 §7); the cohort key (C-HE-28 §1)
    concurrent_lanes_at_open: int | None = None
    concurrent_lanes_min: int | None = None
    concurrent_lanes_max: int | None = None
    phases: dict[str, dict] = field(default_factory=dict)  # {phase: {start, end}} (C-HE-27)


def run(cmd: list[str], *, what: str) -> str:
    """Run a command, validating exit status and non-empty output."""
    if shutil.which(cmd[0]) is None:
        raise AbortError(f"{what}: '{cmd[0]}' not on PATH")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    if proc.returncode != 0:
        raise AbortError(
            f"{what}: exit {proc.returncode} from {' '.join(cmd[:4])}...\n"
            f"  stderr: {proc.stderr.strip()[:300]}"
        )
    if not proc.stdout.strip():
        raise AbortError(f"{what}: empty output from {' '.join(cmd[:4])}...")
    return proc.stdout


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def gh_pr(pr: int) -> dict:
    fields = "additions,deletions,changedFiles,commits,createdAt,mergedAt,mergeCommit,title"
    raw = run(["gh", "pr", "view", str(pr), "--json", fields], what=f"gh pr view #{pr}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AbortError(f"gh pr view #{pr}: output is not JSON: {exc}") from exc
    for key in ("additions", "changedFiles", "createdAt"):
        if data.get(key) is None:
            raise AbortError(f"gh pr view #{pr}: missing expected field '{key}'")
    return data


def round_metrics(globs: list[str]) -> tuple[list[Path], list[float], list[int]]:
    """Derive per-round wall clock from log mtimes, and P1 arrival by round."""
    # Resolve before de-duplicating: two overlapping globs matching one file
    # would otherwise count it twice, inventing an extra round, a spurious
    # zero-second gap, and an off-by-one in every later P1 round index.
    seen: dict[Path, None] = {}
    for g in globs:
        p = Path(g).expanduser()
        matched = sorted(p.parent.glob(p.name)) if p.name else []
        for m in matched:
            if m.is_file():
                seen[m.resolve()] = None
    logs: list[Path] = list(seen)
    if not logs:
        raise AbortError(
            f"round logs: zero files matched {globs} -- refusing to record "
            "'0 rounds' for what may be an unlooked path"
        )

    logs.sort(key=lambda f: f.stat().st_mtime)
    mtimes = [f.stat().st_mtime for f in logs]
    gaps = [round(b - a, 1) for a, b in itertools.pairwise(mtimes)]

    p1_rounds: list[int] = []
    for idx, f in enumerate(logs, start=1):
        try:
            text = f.read_text(errors="replace")
        except OSError as exc:
            raise AbortError(f"round logs: cannot read {f}: {exc}") from exc
        if count_p1(text) >= 1:
            p1_rounds.append(idx)
    return logs, gaps, p1_rounds


def count_p1(text: str) -> int:
    """True P1 count, across BOTH round-log dialects.

    Counts only findings, never prose that happens to mention a severity tag.
    A whole-transcript ``text.count("[P1]")`` is wrong twice over: the reviewed
    diff can quote a PAST review ("R1 -- two real [P1]s advisor missed") and a
    skill doc can carry a literal format example, both of which then classify a
    clean round as carrying a P1. Measured on the B-40 round-1 log, where both
    bracketed hits were exactly that.

    So: findings are anchored to line start (``- [P1] ...``, codex's own
    emission shape) and counted as DISTINCT lines. Distinctness -- not a
    halving constant -- is what absorbs codex printing every finding twice
    (once inline, once in the structured block): two identical emissions of one
    finding collapse, while two genuinely different findings do not. When the
    structured block is present, only the LAST one is read, so an earlier
    round quoted inside the transcript cannot leak in.

    Absorption commit messages write a bare ``P1 <CLAIM>`` at line start and are
    NOT duplicated. Counting only one dialect silently reports zero for the
    other, which is the 'empty vs unlooked' failure this ledger exists to avoid.
    """
    payload = text
    if FINAL_REVIEW_MARKER in text:
        payload = text.rsplit(FINAL_REVIEW_MARKER, 1)[1]
    bracketed = {
        line.strip() for line in re.findall(r"^\s*-?\s*\[P1\].*$", payload, flags=re.MULTILINE)
    }
    bare = {line.strip() for line in re.findall(r"^P1\s+\S.*$", payload, flags=re.MULTILINE)}
    return len(bracketed) + len(bare)


def ci_metrics(sha: str) -> tuple[int, list[float]]:
    """CI runs for THIS commit, asked for by commit.

    Scanning the latest N runs and filtering client-side cannot distinguish
    "this commit had no runs" from "this commit is older than the window", and
    the second one silently becomes a measured zero -- the exact absent-vs-zero
    violation this ledger exists to prevent. Measured: 12 of the 16 backfilled
    baseline rows recorded `derived` CI fields with zero runs under the old
    windowed query. ``--commit`` makes an empty result mean what it says -- but
    ONLY for a full 40-char SHA. Measured 2026-08-14: ``gh run list --commit
    <abbrev>`` returns ``[]`` for a commit whose runs plainly exist, so an
    abbreviated SHA would reintroduce the silent zero through the very query
    meant to remove it.
    """
    if len(sha) != FULL_SHA_LEN:
        raise AbortError(
            f"ci runs: need a full {FULL_SHA_LEN}-char SHA, got {len(sha)} chars "
            f"({sha!r}) -- gh returns an empty set for an abbreviated commit, "
            "which would be recorded as a measured zero"
        )
    raw = run(
        [
            "gh",
            "run",
            "list",
            "--commit",
            sha,
            "--limit",
            "100",
            "--json",
            "headSha,createdAt,updatedAt,conclusion,event",
        ],
        what=f"gh run list --commit {sha[:8]}",
    )
    runs = json.loads(raw)
    hit = [r for r in runs if str(r.get("headSha", "")).startswith(sha[:12])]
    durations = []
    for r in hit:
        # A cancelled run is NOT a fast green -- exclude it from timing, or the
        # ~65s cancellation signature poisons the baseline (2026-08-14). One predicate
        # (C-HE-19): only an exact `success` is green.
        if not ci_is_green(r.get("conclusion")):
            continue
        durations.append(
            round((parse_iso(r["updatedAt"]) - parse_iso(r["createdAt"])).total_seconds(), 1)
        )
    return len(hit), durations


def extract(args: argparse.Namespace) -> ArcRow:
    prov: dict[str, str] = {}
    row = ArcRow(arc_id=args.arc_id or f"pr-{args.pr}", pr=args.pr)

    data = gh_pr(args.pr)
    row.additions = data["additions"]
    row.deletions = data.get("deletions")
    row.files = data["changedFiles"]
    row.commits = len(data.get("commits") or [])
    row.created_at = data["createdAt"]
    row.merged_at = data.get("mergedAt")
    row.merge_sha = (data.get("mergeCommit") or {}).get("oid")
    if row.merged_at:
        row.total_arc_wall_s = round(
            (parse_iso(row.merged_at) - parse_iso(row.created_at)).total_seconds(), 1
        )
        prov["total_arc_wall_s"] = "derived"
    else:
        prov["total_arc_wall_s"] = "unmapped:not-merged"
    prov["gh_fields"] = "derived"

    # A snapshot taken by `queue` at closure wins over any live glob: the logs
    # it measured are the arc's own, and re-deriving now would read whatever
    # those files have since become.
    snapshot = getattr(args, "round_snapshot", None)
    if snapshot or args.round_logs:
        if snapshot:
            row.review_rounds = snapshot["review_rounds"]
            row.round_wall_s = snapshot["round_wall_s"]
            row.p1_rounds = snapshot["p1_rounds"]
            row.round_log_source = snapshot["round_log_source"]
            first = parse_iso(snapshot["first_round_at"])
            row.first_round_at = snapshot["first_round_at"]
            row.last_round_at = snapshot["last_round_at"]
        else:
            logs, gaps, p1 = round_metrics(args.round_logs)
            row.review_rounds = len(logs)
            row.round_wall_s = gaps
            row.p1_rounds = p1
            row.round_log_source = str(Path(args.round_logs[0]).parent)
            first = datetime.fromtimestamp(logs[0].stat().st_mtime, tz=UTC)
            last = datetime.fromtimestamp(logs[-1].stat().st_mtime, tz=UTC)
            row.first_round_at = first.isoformat()
            row.last_round_at = last.isoformat()
        if row.merged_at:
            # The real arc window: first review activity through merge. This is
            # the metric the ~5h/arc claim should be measured against -- NOT
            # createdAt->mergedAt, which misses every round run before the PR
            # opened (measured at up to 56x the PR window).
            span = round((parse_iso(row.merged_at) - first).total_seconds(), 1)
            # Both ends, not just the first. A guard on the start alone still
            # accepts a set whose LAST log postdates the merge -- a parallel
            # lane's file caught by the glob, or a re-touched one -- which
            # inflates review_rounds and folds post-merge gaps into the arc
            # while keeping the span positive and innocent-looking.
            # Ordered START-then-END on purpose. Logs are mtime-sorted, so
            # `last >= first`: checking the end first would make this branch
            # unreachable on every input derivable from real logs, leaving a
            # guard that looks load-bearing and never fires.
            if span < 0:
                # A copied or re-touched log can carry an mtime after the merge.
                # A negative span is not a short arc, it is a broken input -- and
                # since negatives are truthy they would sail into cohort medians
                # and drag them down. Refuse rather than record.
                raise AbortError(
                    f"{row.arc_id}: first round log ({row.first_round_at}) postdates "
                    f"the merge ({row.merged_at}) -- a copied or re-touched log is in "
                    "the set; fix the glob rather than record a negative arc span"
                )
            if row.last_round_at and parse_iso(row.last_round_at) > parse_iso(row.merged_at):
                raise AbortError(
                    f"{row.arc_id}: last round log ({row.last_round_at}) postdates the "
                    f"merge ({row.merged_at}) -- the log set reaches past this arc; "
                    "narrow the glob rather than record post-merge rounds"
                )
            row.arc_span_s = span
            # A round log's mtime is when that round's output FINISHED, not when
            # its review began, so the span starts at the END of round 1 and the
            # whole first round is missing from it. On a one-round arc that
            # leaves only the tail: pr-1023 reads 73.5s against an 817s PR
            # window. The number is therefore a LOWER BOUND and is labelled as
            # one -- B-171's round-timing instrumentation is what supplies a
            # real start timestamp; until then, no consumer should read this as
            # the whole arc.
            prov["arc_span_s"] = "derived:lower-bound-excludes-first-round-duration"
        prov["round_fields"] = "derived"
    else:
        prov["round_fields"] = "unmapped:no-round-logs-supplied"

    if row.merge_sha:
        # Deliberately NOT wrapped in a try/except. A transient gh failure
        # (auth, network, outage) is not an absent input: swallowing it into
        # `unmapped` would persist a permanently CI-less row, and both the
        # duplicate guard and the queue drain then refuse the retry that would
        # have fixed it. Let it propagate -- drain() keeps the entry queued.
        # `unmapped` stays reserved for inputs that genuinely do not exist.
        n, durs = ci_metrics(row.merge_sha)
        row.ci_runs, row.ci_wall_s = n, durs
        prov["ci_fields"] = "derived"
    else:
        prov["ci_fields"] = "unmapped:no-merge-sha"

    row.arc_type = args.arc_type
    # C-HE-26: which side of the arc the label was declared on. `open` = the
    # C-HE-03 reservation captured it (U-HE-17/21 carry that capture point);
    # `close` = today's closure-time queue step. Both labels stay visible on the
    # ONE arc row; a close-time change goes through `relabel_arc_type_close`.
    declared_at = getattr(args, "arc_type_declared_at", None) or "close"
    row.arc_type_declared_at = declared_at if args.arc_type else None
    row.arc_type_open = args.arc_type if declared_at == "open" else None
    row.arc_type_close = args.arc_type if declared_at == "close" else None
    row.decision_count = args.decisions
    row.levers_active = args.levers or []
    prov["arc_type"] = "declared" if args.arc_type else "unmapped:unclassified"
    prov["decision_count"] = "declared" if args.decisions is not None else "unmapped:unclassified"
    prov["levers_active"] = "declared"

    row.provenance = prov
    row.captured_at = datetime.now(tz=UTC).isoformat()
    row.notes = args.notes or ""
    return row


def _ledger_claim_path(ledger: Path) -> Path:
    """The ledger's writer claim lives QUEUE_DIR-adjacent, NEVER under REPO (C-HE-02 §2 +
    Invariant: every coordination path derives from QUEUE_DIR -- a per-worktree placement
    re-creates the X3 split-brain; merge-gate L2 on #1399). Keyed by the ledger's resolved
    path so lanes holding DIFFERENT ledgers (ARC_METRICS_REPO) claim different files over
    the ONE shared queue directory."""
    key = hashlib.sha1(str(ledger.resolve()).encode()).hexdigest()[:16]
    return QUEUE_DIR / f".ledger-claim-{key}"


def claim_ledger(ledger: Path) -> None:
    """Take exclusive ownership of the ledger for one write, by CAS on a claim file.

    C-HE-02 §1 bans kernel file locks in this module, so the mutual exclusion
    between the ledger's two writers -- `append` (drain) and
    `relabel_arc_type_close` (whole-file rewrite) -- is the same primitive the
    queue uses: `publish_exclusive` (atomic `os.link`, fails when taken) with a
    pid@host owner stamp, and `_claim_owner_is_dead` to reclaim a claim left by
    a crashed owner on this host. A live or foreign owner means "retry": the
    caller aborts loudly rather than racing (codex R3 P2 -- without this, an
    append landing between the relabel's compare and its replace was lost).
    Pair with `release_ledger` in a `finally`; release is a no-op when nothing
    was claimed, so the claim call is a single deletable statement (probeable).
    """
    claim = _ledger_claim_path(ledger)
    claim.parent.mkdir(parents=True, exist_ok=True)
    stamp = json.dumps({"_claim": {"pid": os.getpid(), "host": socket.gethostname()}})
    for attempt in (1, 2):
        try:
            publish_exclusive(claim, stamp)
            return
        except FileExistsError:
            if attempt == 1 and _reclaim_dead_claim(claim):
                continue  # the dead claim is gone; publish once more
            raise AbortError(
                f"ledger {claim.name} is claimed by another writer -- retry "
                "(a live peer holds it, or the owner cannot be verified)"
            ) from None


def _reclaim_dead_claim(claim: Path) -> bool:
    """Remove a claim whose recorded owner is provably dead -- and ONLY that claim.

    Judge, then move the judged file aside by atomic rename and re-read it: if the
    bytes moved are not the bytes judged, a peer reclaimed first and published its
    own LIVE claim in between (codex R8 P2 -- an unconditional unlink here would
    have stolen it); put it straight back and report "not reclaimed". True iff the
    dead claim was removed by THIS writer.
    """
    try:
        judged = claim.read_bytes()
    except OSError:
        return False
    if not _claim_owner_is_dead(claim):
        return False
    aside = claim.with_name(f"{claim.name}.dead.{os.getpid()}")
    try:
        os.rename(claim, aside)
    except FileNotFoundError:
        return True  # a peer removed it first; the publish retry decides who owns it
    try:
        moved = aside.read_bytes()
    except OSError:
        moved = b""
    if moved != judged:
        os.rename(aside, claim)  # not the claim we judged: a live peer's -- restore it
        return False
    aside.unlink(missing_ok=True)
    return True


def release_ledger(ledger: Path) -> None:
    _ledger_claim_path(ledger).unlink(missing_ok=True)


def append(row: ArcRow) -> None:
    # An arc is not an arc until it merged. Appending a pre-merge row would
    # persist null merge fields AND burn the arc_id, so the duplicate guard
    # below would then reject the correct post-merge capture -- turning a
    # mistyped PR number into manual ledger surgery. Refuse instead; --dry-run
    # stays available for inspecting a row before merge.
    if not row.merged_at or not row.merge_sha:
        raise AbortError(
            f"{row.arc_id}: refusing to append an unmerged arc "
            f"(merged_at={row.merged_at!r}, merge_sha={row.merge_sha!r}) -- "
            "capture after merge, or use --dry-run to inspect"
        )
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    claim_ledger(LEDGER)
    try:
        existing = read_ledger()
        if any(r.get("arc_id") == row.arc_id for r in existing):
            raise AbortError(
                f"arc_id '{row.arc_id}' already in ledger -- refusing to append a "
                "duplicate (use a distinct --arc-id or remove the prior row)"
            )
        with LEDGER.open("a") as fh:
            fh.write(json.dumps(asdict(row), sort_keys=True) + "\n")
    finally:
        release_ledger(LEDGER)


ARC_TYPES = ("inventing", "applying")


def relabel_arc_type_close(arc_id: str, arc_type_close: str) -> None:
    """C-HE-26 §2: a close-time relabel updates the SINGLE arc row in place. Never a
    second row (that would trip SPLIT_BRAIN_LEDGER). The rewrite is whole-file atomic
    (temp + os.replace) and touches only this arc's row.

    Mutual exclusion with `append` is the `claim_ledger` CAS claim (C-HE-02 §1 bans
    kernel file locks here). Inside the claim a byte-compare of the ledger against the
    snapshot the rewrite was derived from still guards against a writer that does not
    take the claim (an older tool, a hand edit): the relabel then aborts (retry) rather
    than silently discarding that write under the whole-file rewrite (codex R2/R3 P2)."""
    if arc_type_close not in ARC_TYPES:
        raise AbortError(f"arc_type_close must be inventing|applying, got {arc_type_close!r}")
    claim_ledger(LEDGER)
    try:
        snapshot = LEDGER.read_bytes() if LEDGER.exists() else b""
        rows = read_ledger()
        hits = [r for r in rows if r.get("arc_id") == arc_id]
        if len(hits) != 1:
            raise AbortError(f"{arc_id}: expected exactly one arc row, found {len(hits)}")
        hits[0]["arc_type_close"] = arc_type_close
        tmp = LEDGER.with_name(f".{LEDGER.name}.{os.getpid()}.tmp")
        tmp.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
        current = LEDGER.read_bytes() if LEDGER.exists() else b""
        if current != snapshot:
            tmp.unlink(missing_ok=True)
            raise AbortError(
                f"{arc_id}: ledger changed while the relabel was prepared -- nothing written, retry"
            )
        os.replace(tmp, LEDGER)
    finally:
        release_ledger(LEDGER)


def cmd_relabel(args: argparse.Namespace) -> int:
    relabel_arc_type_close(args.arc_id, args.arc_type_close)
    print(f"relabelled {args.arc_id}: arc_type_close={args.arc_type_close} -> {LEDGER}")
    return 0


def queue_capture(args: argparse.Namespace) -> int:
    """Record an arc's capture inputs OUTSIDE the repo, for a later drain.

    Capture runs at arc closure, when the merge SHA finally exists -- but that
    is the worst moment to write into the tracked ledger. In an autonomous arc
    the closure step runs inside the topic worktree, and a dirty tracked file
    there both strands the row when the worktree is disposed and blocks the
    disposal itself (worktree GC skips a merged worktree carrying local state,
    while loop completion requires that worktree to be unregistered).

    Committing straight to `main` is no better: before the terminating refresh
    the drift guard hard-fails the push, and after it the next local preflight
    hard-fails instead, demanding yet another refresh.

    So closure writes nothing to the repo. It queues the arc's inputs -- above
    all the DECLARED judgements (arc type, decision count, active levers) that
    only the session which ran the arc can supply -- to a durable path outside
    any worktree. The next arc drains the queue and commits the rows inside its
    own PR, which is an ordinary content commit with none of the above problems.
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    arc_id = args.arc_id or f"pr-{args.pr}"
    # The arc_id becomes a filename. An absolute or `..`-bearing id would land
    # OUTSIDE QUEUE_DIR, where read_queue never looks -- and `queue` would still
    # report success, so the capture is silently never drained. Require a single
    # safe path component rather than trusting the caller.
    if arc_id != Path(arc_id).name or arc_id in {"", ".", ".."} or arc_id.startswith("."):
        raise AbortError(
            f"unsafe --arc-id {arc_id!r}: must be a single filename component "
            "(no '/', no '..', no leading '.') or the queued file lands where "
            "no drain will find it"
        )
    # `.taken` (and everything built on it: `.taken.recover.<host>.<pid>`) is the
    # claim/recovery namespace next to the entry -- an arc_id carrying it would
    # collide with or misparse those coordination names (codex r6/r7 P3).
    if ".taken" in arc_id:
        raise AbortError(f"--arc-id {arc_id!r} contains '.taken', a reserved coordination suffix")
    # Recovery appends `.taken.recover.<hostname>.<pid>` to this name; an arc_id
    # accepted here must keep the WORST-CASE recovery filename under NAME_MAX in
    # BYTES (multi-byte UTF-8 counts) or the dead-claim recovery path fails
    # ENAMETOOLONG and strands the capture (codex r6 P2, r7 P2).
    worst = f"{arc_id}.taken.recover.{socket.gethostname()}.{os.getpid()}".encode()
    if len(worst) > 240:
        raise AbortError(
            f"--arc-id too long ({len(worst)} bytes with the recovery suffix, max 240): "
            "recovery filenames must stay under the filesystem NAME_MAX"
        )

    # Resolve the globs HERE, at closure, and store concrete paths. A pattern
    # stored live would be re-expanded by the next arc's drain, so any file
    # created or touched in between that also matches -- a parallel lane's
    # `round-*.log`, a re-run -- would be silently attributed to this arc, and a
    # match postdating the merge can even yield a negative arc_span_s. The glob
    # must mean what it matched at closure, so it is snapshotted, not deferred.
    # Snapshot the DERIVED METRICS, not just the matched paths. Paths alone
    # still point at mutable files: a log touched, rewritten, or deleted between
    # closure and the next arc's drain would silently change round_wall_s,
    # p1_rounds and arc_span_s -- or make the arc undrainable. Deriving here,
    # while the logs are still exactly what the arc produced, means drain does
    # no recomputation at all and cannot be affected by later edits.
    snapshot: dict | None = None
    if args.round_logs:
        logs, gaps, p1 = round_metrics(args.round_logs)
        first = datetime.fromtimestamp(logs[0].stat().st_mtime, tz=UTC)
        last = datetime.fromtimestamp(logs[-1].stat().st_mtime, tz=UTC)
        snapshot = {
            "review_rounds": len(logs),
            "round_wall_s": gaps,
            "p1_rounds": p1,
            "first_round_at": first.isoformat(),
            "last_round_at": last.isoformat(),
            "round_log_source": str(logs[0].parent),
            "matched": [str(p) for p in logs],
        }

    entry = {
        "pr": args.pr,
        "arc_id": args.arc_id,
        "arc_type": args.arc_type,
        "arc_type_declared_at": getattr(args, "arc_type_declared_at", None) or "close",
        "decisions": args.decisions,
        "round_snapshot": snapshot,
        "round_logs_globs": args.round_logs or [],
        "levers": args.levers or [],
        "notes": args.notes or "",
        "queued_at": datetime.now(tz=UTC).isoformat(),
    }
    path = QUEUE_DIR / f"{arc_id}.json"
    try:
        # Exclusive AND atomic: a second queue for the same arc is a mistake
        # worth surfacing, not an overwrite of the first session's judgements --
        # and a half-written entry would wedge the queue for every later drain.
        publish_exclusive(path, json.dumps(entry, sort_keys=True, indent=2))
    except FileExistsError as exc:
        raise AbortError(
            f"{arc_id} is already queued at {path} -- remove it first if the "
            "queued declarations are wrong"
        ) from exc
    print(f"queued arc capture for #{args.pr} -> {path}")
    return 0


def read_queue(invalid: list[Path] | None = None) -> list[tuple[Path, dict]]:
    """Pending queue entries. An unreadable or malformed FILE is a per-arc content
    fault (C-HE-04 SS3): it is reported, collected into ``invalid`` when given, and
    skipped -- one truncated entry must not abandon every other pending arc. drain()
    counts collected files as kept, so the run still exits nonzero for attention."""
    if not QUEUE_DIR.is_dir():
        return []
    out = []
    for path in sorted(QUEUE_DIR.glob("*.json")):
        try:
            entry = json.loads(path.read_text())
        except FileNotFoundError:
            # A peer claimed or released this entry between the glob and the
            # read -- it is no longer pending. Skip, never propagate (C-HE-04
            # Invariants: no FileNotFoundError escapes drain()).
            continue
        except OSError as exc:
            if _is_systemic(exc) and not os.access(QUEUE_DIR, os.R_OK | os.X_OK):
                raise  # the DIRECTORY is unreadable: queue-wide, abort once
            # EISDIR, ENAMETOOLONG, a mode-000 FILE, ... -- a per-path content
            # fault (the glob itself succeeded, so the directory reads): report
            # + keep, drain the rest (codex r7 P2, r9 P2).
            msg = f"  {path.name}: unreadable ({exc}) -- kept, needs human repair"
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            msg = f"  {path.name}: not valid JSON ({exc}) -- kept, needs human repair"
        else:
            if isinstance(entry, dict):
                out.append((path, entry))
                continue
            msg = f"  {path.name}: queued value is not an object -- kept, needs human repair"
        print(msg, file=sys.stderr)
        if invalid is not None:
            invalid.append(path)
    return out


def publish_exclusive(path: Path, payload: str) -> None:
    """Create ``path`` holding ``payload`` -- atomically AND exclusively.

    ``open("x")`` then ``write`` is neither. The name becomes VISIBLE the moment
    it is created and only gains its content afterwards, so an interrupted
    write leaves a truncated file behind. That is not a lost write, it is a
    deadlock: a truncated queue entry makes every later ``read_queue`` abort,
    while re-queueing the same arc is refused because the name already exists,
    and a truncated claim reads as unverifiable ownership, which
    ``_claim_owner_is_dead`` conservatively treats as still held -- so that arc
    is never retried again without a human deleting the file.

    Writing a temp file first and hard-linking it into place fixes both halves:
    the destination name never exists in a partial state, and ``os.link`` still
    fails when the name is taken, so the exclusivity both call sites depend on
    is preserved.
    """
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        tmp.write_text(payload)
        os.link(tmp, path)  # atomic publish; raises FileExistsError if taken
    finally:
        tmp.unlink(missing_ok=True)


def _process_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True  # exists, owned by someone else
    return True


def committed_arc_ids() -> set[str]:
    """arc_ids present in the ledger on MERGED history, not the topic branch.

    A local append is not durability, and neither is a local commit. The row
    lives on a topic branch until its PR merges, and that branch can still be
    reset, abandoned, or have its worktree disposed -- taking the
    operator-declared fields with it, since only the queued capture ever held
    them. Reading `HEAD` would see the arc the moment it was committed on the
    topic branch and release the capture right there, which is precisely the
    loss this queue exists to prevent, one step later.

    So the release point is the merged default branch. If it cannot be read,
    nothing is released -- holding a capture costs a queue file, dropping one
    costs the declarations permanently.
    """
    try:
        rel = LEDGER.relative_to(REPO)
    except ValueError:
        return set()  # a ledger outside the repo has no committed history
    try:
        raw = run(["git", "show", f"{MERGED_REF}:{rel}"], what="git show merged ledger")
    except AbortError:
        return set()  # unreadable or not yet in merged history -- hold everything
    ids = set()
    for line in raw.splitlines():
        if line.strip():
            try:
                ids.add(json.loads(line).get("arc_id"))
            except json.JSONDecodeError:
                continue
    return ids


def _claim_owner_is_dead(claim: Path) -> bool:
    """True only when the recorded owner is provably gone.

    Unknown ownership is never treated as dead: an unreadable stamp or a claim
    from another host means "cannot tell", and guessing wrong hands a live
    peer's arc to a second drain.
    """
    try:
        held = json.loads(claim.read_text()).get("_claim", {})
    except (json.JSONDecodeError, OSError):
        return False
    pid, host = held.get("pid"), held.get("host")
    if not isinstance(pid, int) or host != socket.gethostname():
        return False
    return not _process_is_alive(pid)


def _claim_arc(path: Path, entry: dict) -> Path | None:
    """Take ownership of a queued arc, stamped in ONE atomic step.

    The claim and its ownership stamp have to be the same operation. A
    rename-then-write leaves a window in which the claim file exists with NO
    stamp, and a peer scanning exactly then reads "no owner" as "dead owner",
    restores the arc, and captures it alongside its still-live owner -- both
    drains reach the ledger and can emit duplicate rows. An O_EXCL create of
    the already-stamped file closes that window: the claim never exists
    unstamped, and only one drain can create it.
    """
    taken = path.with_suffix(".taken")
    payload = json.dumps(
        {**entry, "_claim": {"pid": os.getpid(), "host": socket.gethostname()}},
        sort_keys=True,
    )
    for _attempt in (1, 2):
        try:
            # Atomic publish, not create-then-write: a claim interrupted
            # mid-write is unverifiable ownership, which _claim_owner_is_dead
            # conservatively reads as STILL HELD -- stalling that arc forever.
            publish_exclusive(taken, payload)
        except FileExistsError:
            if _attempt == 1 and _claim_owner_is_dead(taken):
                # Take over by ATOMIC RENAME, never unlink-then-publish: two
                # contenders can both judge the same dead owner, and with a
                # bare unlink the slower one deletes the faster one's freshly
                # published LIVE claim (codex r8 P1). Exactly one rename wins;
                # the loser's rename raises FNF and its retry-publish then sees
                # the winner's live claim.
                aside = taken.with_name(_aside_suffix(taken.name))
                try:
                    os.rename(taken, aside)
                except FileNotFoundError:
                    continue  # a contender took over first; the retry sees its claim
                if not _claim_owner_is_dead(aside):
                    # Our judgment was STALE -- the aside holds a live claim
                    # restamped meanwhile. Return it (exclusively) and yield.
                    try:
                        os.link(aside, taken)
                    except FileExistsError:
                        pass
                    aside.unlink(missing_ok=True)
                    return None
                aside.unlink(missing_ok=True)
                continue  # the owner is provably gone; retry once against the freed name
            return None
        except OSError as exc:
            # A read-only queue, a permission problem, an I/O error -- none of
            # these are a lost race, and reporting them as one would let an
            # incomplete drain exit 0. A SYSTEMIC fault (C-HE-04 SS3) must keep
            # its OSError identity so drain() can abort the whole loop once
            # rather than re-logging the identical failure per entry -- the
            # classification has to happen before the AbortError conversion.
            if _is_systemic(exc):
                raise
            raise AbortError(f"cannot claim {path.name}: {exc}") from exc
        # Verify the entry on disk is still the bytes this drain LISTED before
        # consuming it: a producer can have published corrected declarations
        # (remove + re-queue) after our read_queue() -- unlinking blindly would
        # discard the correction and capture the stale payload (codex r10 P1).
        try:
            current = json.loads(path.read_text())
        except FileNotFoundError:
            # The .json vanished between listing and claiming. The classic
            # cause is a live peer that finished the arc -- but it can also be
            # a dead claimer whose entry only WE now hold (codex r10 P1), so
            # never delete the only copy: re-publish the capture durably
            # (exclusive; a peer's restore wins harmlessly) and yield.
            _restore_or_republish(taken, path, entry)
            return None
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            current = None  # unreadable now = not verifiably ours to consume
        if current != entry:
            # Corrected (or unverifiable) declarations: leave them; drop our
            # stale claim and let a fresh drain list the new bytes.
            taken.unlink(missing_ok=True)
            return None
        try:
            path.unlink()
        except FileNotFoundError:
            _restore_or_republish(taken, path, entry)
            return None
        return taken
    return None


def _kill_after(step: str) -> None:
    """Test seam (C-HE-04 verification (vi)): ARC_METRICS_TEST_KILL_AFTER=<step> exits 137
    right after the named step -- a real process death, not an exception a ``finally``
    could tidy. Steps: claim, extract, append, restore, restore-abort (used by U-HE-20)."""
    if os.environ.get("ARC_METRICS_TEST_KILL_AFTER") == step:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(137)


def _is_systemic(exc: OSError) -> bool:
    """A queue-dir permission / I/O / disk fault -- not a per-arc content fault, not a
    lost race (C-HE-04 SS3). One such fault dooms every remaining entry identically, so
    drain() aborts once instead of re-logging the same failure per arc."""
    return isinstance(exc, PermissionError) or exc.errno in {
        errno.EACCES,
        errno.EROFS,
        errno.EIO,
        errno.ENOSPC,
    }


def _restore_or_republish(taken: Path, path: Path, entry: dict) -> None:
    """Put the queue entry back DURABLY (C-HE-04 SS4/SS7, E9/E21).

    The held ``.taken`` can vanish under us (a peer judged us dead and took over,
    ``_claim_arc``'s dead-owner retry); a bare rename then raises and the
    appended-but-uncommitted row's declarations exist nowhere else. Re-publish from the
    in-memory capture instead. Every path here is EXCLUSIVE (``os.link`` /
    ``publish_exclusive``): while an arc is claimed its ``.json`` name is free, so a
    concurrent ``queue`` can legitimately publish UPDATED declarations there -- a
    clobbering ``os.replace`` would silently revert them to the stale claimed payload.
    ``FileExistsError`` therefore means the queue name is already durably held (a newer
    capture, or a peer's restore) and this stale copy is simply dropped."""
    try:
        os.link(taken, path)
    except FileNotFoundError:
        payload = json.dumps({k: v for k, v in entry.items() if k != "_claim"}, sort_keys=True)
        try:
            publish_exclusive(path, payload)
        except FileExistsError:
            pass
        return
    except FileExistsError:
        pass
    taken.unlink(missing_ok=True)


def _aside_suffix(name: str) -> str:
    """A recovery-aside name that can NEVER collide with an existing aside:
    `os.rename` overwrites its destination, so a deterministic host+pid name
    could destroy a crashed recoverer's orphaned capture once the pid is
    reused (codex r9 P2). The random token keeps the parse shape
    `<base>.recover.<host>.<pid>[-token]` -- liveness reads the pid half."""
    return f"{name}.recover.{socket.gethostname()}.{os.getpid()}-{os.urandom(4).hex()}"


def _recover_dead_claims() -> None:
    """Return claims held by a DEAD drain, and only those.

    A claim marks an arc as being captured right now. A crashed drain leaves
    one behind, and without recovery that arc is stranded where ``read_queue``
    never looks. But "orphaned by a crash" and "held by a live peer" look
    identical on disk, so recovering blindly would hand a live peer's arc to a
    second drain and reproduce the duplicate row the claim exists to prevent.

    Liveness is therefore checked EXACTLY, by pid, rather than through an
    age window -- a window is a guess, and a slow-but-healthy capture that
    outlives it silently becomes a duplicate. A claim from another host cannot
    be judged from here, so it is reported and left alone.
    """
    if not QUEUE_DIR.is_dir():
        return
    # Sweep asides orphaned by a recoverer that died between its rename and its
    # restore: the pid suffix names the recoverer, so deadness is exact. A live
    # recoverer's aside is in flight -- leave it.
    for orphan in sorted(QUEUE_DIR.glob("*.taken.recover.*")):
        # rpartition parses from the RIGHT so an arc_id that itself contains
        # ".taken.recover." cannot shift the host/pid fields (codex r5 P3).
        base, _, rest = orphan.name.rpartition(".recover.")
        if not base.endswith(".taken"):
            continue  # a queue entry that merely matches the glob, not an aside
        host, _, pid_field = rest.rpartition(".")
        pid_s = pid_field.split("-", 1)[0]  # `<pid>-<token>`; legacy bare pid also parses
        if host != socket.gethostname() or not pid_s.isdigit():
            # A foreign-host (or unparseable) recoverer cannot be judged from
            # here: unknown owner is LIVE, never dead (C-HE-02 SS6).
            print(f"  {orphan.name}: recoverer not judgeable from this host; leaving it")
            continue
        if _process_is_alive(int(pid_s)):
            continue
        # The recoverer is dead, but the aside may hold a LIVE re-claim it had
        # moved just before dying (codex r5 P2): re-judge the EMBEDDED owner and
        # route accordingly -- live back to its .taken name, dead to .json. Both
        # routes are exclusive links so a name published meanwhile is never
        # clobbered; the aside copy is then superseded either way.
        if _claim_owner_is_dead(orphan):
            target = orphan.with_name(base[: -len(".taken")] + ".json")
            what = "restored orphaned recovery file"
        else:
            target = orphan.with_name(base)
            what = "returned live claim from a dead recoverer"
        try:
            os.link(orphan, target)
            print(f"  {what} -> {target.name}")
        except FileExistsError:
            pass  # the name is already durably held; the aside is redundant
        except FileNotFoundError:
            continue
        orphan.unlink(missing_ok=True)
    for claim in sorted(QUEUE_DIR.glob("*.taken")):
        restored = claim.with_suffix(".json")
        if restored.exists():
            # The entry is already durably back. A DEAD owner's leftover claim
            # (e.g. the exclusive-restore link crashed before its unlink) would
            # otherwise count as outstanding forever; sweep it through the same
            # move-aside re-judge so a live claim is never touched.
            if _claim_owner_is_dead(claim):
                gone = claim.with_name(_aside_suffix(claim.name))
                try:
                    os.rename(claim, gone)
                except FileNotFoundError:
                    continue
                if _claim_owner_is_dead(gone):
                    gone.unlink(missing_ok=True)
                    print(f"  {claim.name}: dead leftover claim swept (entry already back)")
                else:
                    try:
                        os.link(gone, claim)  # exclusive: never overwrite a newer claim
                    except FileExistsError:
                        pass
                    gone.unlink(missing_ok=True)
            continue
        if not _claim_owner_is_dead(claim):
            print(f"  {claim.name} is held by a live or unverifiable owner; leaving it")
            continue
        # Move the file ASIDE, then RE-JUDGE the moved bytes (the
        # _reclaim_dead_claim idiom, adapted): between the first liveness check
        # and the restore a peer can restore the entry AND a live drain can
        # re-claim it under the same .taken name -- a pathname-keyed replace
        # would then yank the LIVE owner's claim back to .json. Once moved to
        # a pid-suffixed aside name no peer can restamp it, so judging the
        # aside bytes is race-free; a live verdict puts the claim straight back.
        aside = claim.with_name(_aside_suffix(claim.name))
        try:
            os.rename(claim, aside)
        except FileNotFoundError:
            # C-HE-04 SS1: a peer restored it between our scan and this rename.
            # The losing racer logs and yields; it must not propagate.
            print(f"  {claim.name}: a peer recovered it first; leaving it")
            continue
        if not _claim_owner_is_dead(aside):
            # A live drain re-claimed under this name meanwhile -- not ours.
            # Exclusive return: a NEWER claim can have been created from a
            # republished entry while the aside was out; never overwrite it
            # (the displaced owner's restore republishes from memory, E9).
            try:
                os.link(aside, claim)
            except FileExistsError:
                pass
            aside.unlink(missing_ok=True)
            print(f"  {claim.name}: re-claimed by a live owner meanwhile; leaving it")
            continue
        # Exclusive restore: a concurrent queue_capture can have published an
        # UPDATED .json after the exists() check above -- a clobbering replace
        # would silently revert it to the stale dead-claim payload (codex r5
        # P1). FileExistsError therefore means the queue name is durably held
        # and this stale copy is dropped.
        try:
            os.link(aside, restored)
            print(f"  recovered claim from a dead owner -> {restored.name}")
        except FileExistsError:
            print(f"  {claim.name}: a newer capture holds the queue name; dropping the stale copy")
        aside.unlink(missing_ok=True)


def _drain_one(path: Path, entry: dict, arc_id: str, committed: set[str], local: set[str]) -> str:
    """Process ONE queued arc; return its outcome (released|held|outstanding|added).

    Extracted from drain()'s loop body so a fault in one entry -- including inside
    _claim_arc -- surfaces as an exception drain() can isolate per arc (C-HE-04 SS3)
    instead of abandoning every remaining pending entry.
    """
    if arc_id in committed:
        print(f"  {arc_id}: in committed ledger, releasing queue entry")
        path.unlink(missing_ok=True)
        return "released"
    if arc_id in local:
        # Appended, but only into the working tree. Hold the capture until
        # the row actually reaches history -- this arc can still be reset or
        # its worktree disposed, and nothing else holds the declarations.
        print(f"  {arc_id}: row appended locally, awaiting commit -- entry held")
        return "held"

    # CLAIM this arc by renaming its queued file before capturing it. Two
    # parallel next-arc sessions can otherwise both pass the ledger's
    # read-then-check duplicate guard and append the same arc twice, which
    # breaks one-row-per-arc and biases every cohort. Exactly one drain wins
    # the claim, the other sees it vanish and moves on. Same structural fix as
    # the queue itself -- no lock required.
    taken = _claim_arc(path, entry)
    _kill_after("claim")
    if taken is None:
        print(f"  {arc_id}: claimed by a concurrent drain, still outstanding")
        return "outstanding"

    try:
        # Namespace construction reads entry fields, so a malformed entry can
        # raise HERE, after the claim -- it must restore before propagating or
        # the claim wedges under a live pid (codex r4 P2).
        args = argparse.Namespace(
            pr=entry["pr"],
            arc_id=entry.get("arc_id"),
            arc_type=entry.get("arc_type"),
            arc_type_declared_at=entry.get("arc_type_declared_at"),
            decisions=entry.get("decisions"),
            # The metrics were derived at closure; drain never re-reads the logs.
            round_snapshot=entry.get("round_snapshot"),
            round_logs=None,
            levers=entry.get("levers"),
            notes=entry.get("notes", ""),
        )
        row = extract(args)
        _kill_after("extract")
        append(row)
        _kill_after("append")
    except (AbortError, KeyError, TypeError, ValueError, OSError):
        # Durable restore BEFORE the caller reports KEPT QUEUED (C-HE-04 SS7) --
        # OSError included (EMFILE from append, ...): drain() re-classifies it
        # after the entry is durably back (codex r5 P2). If the fault is
        # systemic the restore may itself raise; that escapes to the same
        # systemic abort.
        _restore_or_republish(taken, path, entry)
        _kill_after("restore-abort")
        raise
    # Restore the capture to the queue rather than deleting it: the row is
    # only in the working tree so far, and the declarations it carries exist
    # nowhere else. It is released on a later drain, once the row is in
    # committed history.
    _restore_or_republish(taken, path, entry)
    _kill_after("restore")
    print(f"  {arc_id}: appended (entry held until the row is committed)")
    return "added"


def _report_kept(path: Path, arc_id: str, entry: dict, exc: BaseException) -> bool:
    """`KEPT QUEUED` only when the entry is verifiably back on disk (C-HE-04 SS7).

    A restore can itself fail (the .taken vanished AND the exclusive re-publish
    hit EMFILE / ENAMETOOLONG): claiming "kept" then would be false. When neither
    name exists, say so LOUDLY and print the in-memory payload -- stderr is the
    last carrier of the operator's declarations at that point."""
    if path.exists() or path.with_suffix(".taken").exists():
        print(f"  {arc_id}: KEPT QUEUED -- {exc!r}", file=sys.stderr)
        return True
    payload = json.dumps({k: v for k, v in entry.items() if k != "_claim"}, sort_keys=True)
    print(
        f"  {arc_id}: CAPTURE AT RISK -- entry could not be restored ({exc!r}); "
        f"re-queue it by hand from this payload: {payload}",
        file=sys.stderr,
    )
    return False


def drain(_args: argparse.Namespace) -> int:
    """Fold every queued arc into the tracked ledger.

    Each queued arc is its own file, so this never rewrites shared state: an
    entry is unlinked only once its row is safely in the ledger, and one whose
    capture fails is simply left where it is. A concurrent ``queue`` writes a
    different file and is picked up by this drain or the next one -- there is no
    window in which it can be erased, and no lock is needed to say so.
    """
    try:
        _recover_dead_claims()

        invalid: list[Path] = []
        pending = read_queue(invalid)

        # Claims left behind by a live or unverifiable owner are outstanding
        # work. Reporting "nothing to drain" while they sit there would let
        # automation move on before a peer has finished, and would strand a
        # foreign-host claim silently forever. Globbed AFTER read_queue: a peer
        # that claimed an entry between the two scans (its .json vanished from
        # pending) is then visible as a .taken here, so drain cannot exit 0
        # while that fresh claim exists (codex r6 P1).
        outstanding = (
            sorted(QUEUE_DIR.glob("*.taken")) + sorted(QUEUE_DIR.glob("*.taken.recover.*"))
            if QUEUE_DIR.is_dir()
            else []
        )
    except OSError as exc:
        if _is_systemic(exc):
            # Same single-message abort as an in-loop systemic fault (C-HE-04
            # SS3) -- a read-only queue dir during recovery or the queue read
            # must not surface as a raw traceback.
            print(f"ABORT: systemic queue fault on {QUEUE_DIR}: {exc}", file=sys.stderr)
            return 2
        raise
    if not pending:
        if outstanding:
            names = ", ".join(p.name for p in outstanding)
            print(f"nothing drainable; {len(outstanding)} claim(s) still held: {names}")
            return 1
        if invalid:
            return 1  # unreadable entries were reported by read_queue -- attention owed
        print("arc-metrics queue is empty -- nothing to drain")
        return 0

    committed = committed_arc_ids()
    local = {r.get("arc_id") for r in read_ledger()}
    kept = len(outstanding) + len(invalid)
    added = 0
    lost = 0
    for i, (path, entry) in enumerate(pending):
        arc_id = path.stem  # safe fallback name; refined inside the try
        try:
            # arc_id derivation reads entry fields, so it is a per-arc content
            # fault when the entry is malformed -- it must not abort the loop.
            arc_id = entry.get("arc_id") or f"pr-{entry['pr']}"
            outcome = _drain_one(path, entry, arc_id, committed, local)
        except (AbortError, KeyError, TypeError, ValueError) as exc:
            # Per-arc fault -- AbortError from capture, or a malformed entry
            # (missing/mistyped fields) raising in the arc_id expression or
            # extract(). This entry stays queued (already durably restored by
            # _drain_one where a claim was held); the rest still drain
            # (C-HE-04 SS3).
            if _report_kept(path, arc_id, entry, exc):
                kept += 1
            else:
                lost += 1
            continue
        except OSError as exc:
            if _is_systemic(exc):
                # One systemic queue-dir fault dooms every remaining entry the
                # same way: abort once with one message (C-HE-04 SS3) -- but
                # report THIS entry's disposition first: a systemic fault after
                # its .taken vanished would otherwise discard the only
                # in-memory payload silently (codex r9 P1).
                _report_kept(path, arc_id, entry, exc)
                remaining = len(pending) - i
                print(
                    f"ABORT: systemic queue fault on {QUEUE_DIR}: {exc}; "
                    f"{remaining} entr(y/ies) not processed",
                    file=sys.stderr,
                )
                return 2
            if _report_kept(path, arc_id, entry, exc):
                kept += 1
            else:
                lost += 1
            continue
        if outcome == "added":
            added += 1
            kept += 1
        elif outcome in ("held", "outstanding"):
            # Outstanding, not done: a peer holds it and this drain has no idea
            # whether that peer will succeed. Without counting it here the run
            # could exit 0 with a live claim on disk -- contradicting the
            # documented contract that exit 0 means nothing is left to fold.
            kept += 1

    if lost:
        print(
            f"drained {added} arc(s); {kept} entr(y/ies) still queued; "
            f"{lost} CAPTURE(S) AT RISK (payload printed above)",
            file=sys.stderr,
        )
        return 2
    print(f"drained {added} arc(s); {kept} entr(y/ies) still queued")
    # Non-zero on a retained entry, so automation cannot read a pending retry
    # as a completed fold.
    return 1 if kept else 0


def read_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    rows = []
    for n, line in enumerate(LEDGER.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AbortError(f"ledger line {n} is not valid JSON: {exc}") from exc
    return rows


def fmt_span(vals: list[float], unit: float = 60.0, suffix: str = "m") -> str:
    """Median with range -- never a bare mean. Measured round variance is ~5x."""
    if not vals:
        return "--"
    v = sorted(x / unit for x in vals)
    med = statistics.median(v)
    return f"{med:.1f}{suffix} (n={len(v)}, {v[0]:.1f}-{v[-1]:.1f})"


def arc_duration(row: dict) -> float | None:
    """The arc: first review activity -> merge, falling back to the PR window.

    NOT ``createdAt -> mergedAt``. The review loop largely runs on the branch
    BEFORE the PR opens, so the PR window can understate an arc by 44x (#1337:
    6.1m open vs 269.2m real) or 58x (#1115: 2.8m vs 161.4m). It also runs the
    other way when a merged PR simply sat open (#1060: 548.2m open vs 44.4m of
    actual arc). Reporting the PR window as "arc wall clock" would have made
    the baseline cohort -- the whole point of this ledger -- meaningless.

    ``arc_span_s`` needs round data. Where none survives, the PR window stands
    in and ``summary`` prints how many rows are on that weaker footing.
    """
    span = row.get("arc_span_s")
    # `or` would treat a measured 0.0 as absent and silently fall through to the
    # PR window, which is a different quantity entirely.
    return span if span is not None else row.get("total_arc_wall_s")


def summary(_args: argparse.Namespace) -> int:
    rows = read_ledger()
    if not rows:
        raise AbortError(f"ledger is empty or absent: {LEDGER}")

    baseline = [r for r in rows if not r.get("levers_active")]

    # Group treated rows by their EXACT lever set. Collapsing every non-empty
    # levers_active into one TREATED cohort would average B-171 against B-173
    # and report the blend as if it were an effect, which is precisely the
    # per-lever decision this ledger is supposed to support.
    by_levers: dict[str, list[dict]] = {}
    for r in rows:
        levers = r.get("levers_active")
        if levers:
            by_levers.setdefault(" + ".join(sorted(levers)), []).append(r)

    print(f"arc-metrics ledger: {len(rows)} rows  ({LEDGER})")
    treated_n = sum(len(c) for c in by_levers.values())
    print(f"  baseline (no levers): {len(baseline)}   treated: {treated_n}")
    if by_levers:
        print(f"  lever cohorts: {len(by_levers)} ({', '.join(sorted(by_levers))})")
    print()

    cohorts = [("BASELINE", baseline)]
    cohorts += [(f"TREATED [{name}]", c) for name, c in sorted(by_levers.items())]

    for label, cohort in cohorts:
        if not cohort:
            continue
        print(f"-- {label} (n={len(cohort)}) " + "-" * max(3, 46 - len(label)))
        # A partial row's round count and span are LOWER BOUNDS, so they are
        # excluded from the exact aggregates and surfaced on their own line.
        # Averaging a surviving fragment in as if it were a whole arc is how a
        # baseline quietly understates itself.
        exact = [r for r in cohort if r.get("round_completeness", "complete") == "complete"]
        partial = [r for r in cohort if r.get("round_completeness", "complete") != "complete"]
        # TWO different quantities, reported separately and never pooled. An
        # arc span (first review activity -> merge) and a PR-open window measure
        # different things -- #1337 is 269.2m against 6.1m, #1060 44.4m against
        # 548.2m -- so a median over the mixture is a number about nothing. A
        # footnote was not enough: a reader takes the headline figure.
        # `is not None`, never truthiness. A measured 0.0 is a measurement, and
        # dropping it -- or worse, reclassifying a zero span as a PR window --
        # is the same absent-versus-measured-zero violation this ledger exists
        # to prevent, just pointing the other way.
        arcs = [r["arc_span_s"] for r in exact if r.get("arc_span_s") is not None]
        windows = [
            r["total_arc_wall_s"]
            for r in exact
            if r.get("arc_span_s") is None and r.get("total_arc_wall_s") is not None
        ]
        rounds = [r["review_rounds"] for r in exact if r.get("review_rounds") is not None]
        allgaps = [g for r in cohort for g in (r.get("round_wall_s") or [])]
        adds = [r["additions"] for r in cohort if r.get("additions") is not None]
        print(f"  arc span         {fmt_span(arcs)}          [stochastic, LOWER BOUND]")
        print(
            "     ^ first review activity -> merge. Round-log mtimes mark round COMPLETION, "
            "so each\n       span starts at the END of round 1 and that round's own duration "
            "is missing\n       (B-171 supplies the start timestamps)"
        )
        print(f"  PR-open window   {fmt_span(windows)}          [NOT an arc duration]")
        print(
            "     ^ createdAt -> mergedAt for rows with no round data. Kept separate on "
            "purpose:\n       it misses every round run before the PR opened, and includes "
            "idle time after\n       review ended. Never pool it with the spans above."
        )
        print(f"  round wall clock {fmt_span(allgaps)}          [stochastic]")
        print(
            # :g keeps a genuine .5 median visible -- an even cohort's median can
            # land between two integers, and :.0f would round 4.5 away to 4.
            f"  review rounds    "
            f"{statistics.median(rounds):g} (n={len(rounds)}, "
            f"{min(rounds)}-{max(rounds)})"
            if rounds
            else "  review rounds    --"
        )
        if partial:
            bound = ", ".join(
                f"{r['arc_id']}>={r['review_rounds']}" for r in partial if r.get("review_rounds")
            )
            print(
                f"  {len(partial)} row(s) EXCLUDED from the two exact lines above -- only a "
                f"suffix of their logs survives, so their counts are lower bounds ({bound})"
            )
        print(f"  additions        {fmt_span(adds, 1.0, '')}")
        unmapped = sum(
            1
            for r in cohort
            if str(r.get("provenance", {}).get("round_fields", "")).startswith("unmapped")
        )
        if unmapped:
            print(f"  {unmapped}/{len(cohort)} rows have NO round data (unmapped, not zero)")
        print()

    # C-HE-28 §1: lane-count as a lever is judged BY COHORT on the integer
    # `concurrent_lanes_at_open`. Historical rows carry no such field and group
    # under `null` -- a key, not an error (C-HE-25: additive-safe reads). The
    # label renders via json.dumps so None is the literal `null`, never "None".
    by_lanes: dict[str, list[dict]] = {}
    for r in rows:
        key = f"concurrent_lanes_at_open={json.dumps(r.get('concurrent_lanes_at_open'))}"
        by_lanes.setdefault(key, []).append(r)
    for label in sorted(by_lanes):
        cohort = by_lanes[label]
        rounds = [r["review_rounds"] for r in cohort if r.get("review_rounds") is not None]
        print(f"-- LANES [{label}] (n={len(cohort)}) " + "-" * 20)
        print(
            f"  review rounds    {statistics.median(rounds):g} (n={len(rounds)}, "
            f"{min(rounds)}-{max(rounds)})"
            if rounds
            else "  review rounds    --"
        )
        print()

    allgaps = [g for r in rows for g in (r.get("round_wall_s") or [])]
    if allgaps:
        lo, hi = min(allgaps) / 60, max(allgaps) / 60
        spread = f"{lo:.1f}-{hi:.1f} min/round, {hi / max(lo, 0.1):.0f}x"
    else:
        spread = "not yet measurable"
    print(
        f"NOTE  Metrics marked [stochastic] carry wide measured variance "
        f"({spread}).\n      A ~2% effect is NOT detectable at this sample size. "
        "Deterministic metrics\n      (CI job seconds, arc count, rounds consumed "
        "by mechanised classes) are\n      countable and need no statistics -- "
        "prefer those for efficacy claims."
    )
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    row = extract(args)
    if args.dry_run:
        print(json.dumps(asdict(row), indent=2, sort_keys=True))
        return 0
    append(row)
    print(f"appended {row.arc_id} -> {LEDGER}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="arc_metrics", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extract", help="capture one arc row")
    ex.add_argument("--pr", type=int, required=True)
    ex.add_argument("--arc-id")
    ex.add_argument("--arc-type", choices=list(ARC_TYPES))
    ex.add_argument("--arc-type-declared-at", choices=["open", "close"], default="close")
    ex.add_argument("--decisions", type=int, help="independent decision count")
    ex.add_argument("--round-logs", nargs="+", help="glob(s) for this arc's round logs")
    ex.add_argument("--levers", nargs="*", help="levers live during this arc")
    ex.add_argument("--notes", default="")
    ex.add_argument("--dry-run", action="store_true")
    ex.set_defaults(func=cmd_extract)

    q = sub.add_parser("queue", help="record capture inputs out-of-repo (arc closure)")
    q.add_argument("--pr", type=int, required=True)
    q.add_argument("--arc-id")
    # Required HERE but optional on `extract`: only the closing session knows
    # these, and once a row is drained the duplicate guard blocks a corrected
    # capture. `extract` stays permissive for historical backfills, where the
    # judgement genuinely is unavailable and is recorded as unmapped.
    q.add_argument("--arc-type", choices=list(ARC_TYPES), required=True)
    q.add_argument("--arc-type-declared-at", choices=["open", "close"], default="close")
    q.add_argument("--decisions", type=int, required=True, help="independent decision count")
    q.add_argument("--round-logs", nargs="+", help="glob(s) for this arc's round logs")
    q.add_argument("--levers", nargs="*", help="levers live during this arc")
    q.add_argument("--notes", default="")
    q.set_defaults(func=queue_capture)

    dr = sub.add_parser("drain", help="fold queued arcs into the ledger (next arc's PR)")
    dr.set_defaults(func=drain)

    sm = sub.add_parser("summary", help="per-cohort medians with range")
    sm.set_defaults(func=summary)

    rl = sub.add_parser("relabel", help="close-time arc_type relabel on the single arc row")
    rl.add_argument("--arc-id", required=True)
    rl.add_argument("--arc-type-close", choices=list(ARC_TYPES), required=True)
    rl.set_defaults(func=cmd_relabel)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except AbortError as exc:
        print(f"ABORT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
