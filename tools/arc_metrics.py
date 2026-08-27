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
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

#: Per-process overrides (C-HE-05). Mirrors ARC_METRICS_QUEUE_DIR / ARC_METRICS_MERGED_REF so
#: two subprocess lanes can hold DIFFERENT worktree ledgers over ONE shared queue. Defaults
#: are the checkout root and its tracked ledger -- production behaviour is unchanged when unset.
REPO = Path(os.environ.get("ARC_METRICS_REPO", Path(__file__).resolve().parent.parent))
LEDGER = Path(os.environ.get("ARC_METRICS_LEDGER", REPO / ".harness" / "arc-metrics.jsonl"))
#: N6's numerator source (C-HE-27 §4): finding/adjudication rows. Same override
#: pattern as LEDGER so a test or a second lane can point at its own log.
GATE_LOG = Path(os.environ.get("ARC_METRICS_GATE_LOG", REPO / ".harness" / "merge-gate-log.jsonl"))

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


#: The backfill reservation's pseudo-branch discriminator (codex U-HE-19 r12 P2):
#: ":" is ILLEGAL in a git ref name, so no real arc's reservation can ever carry
#: this value -- cmd_extract's resume path cannot be spoofed by a branch named
#: like it.
BACKFILL_BRANCH = "backfill:cmd-extract"


def _fallback_lane_id(host: str, repo: Path) -> str:
    """STABLE per-(host, worktree) lane id -- never the pid (codex U-HE-19 r1 P2: a
    pid-bearing fallback makes every retrying CLI invocation look like another lane,
    wedging held entries and orphaning valid local rows; processes sharing one worktree
    share its ledger and ARE one lane, C-HE-03 §3). The path digest is the
    distinguishing component, so the ≤64 budget trims the NAME and the HOST, never the
    digest (codex r2/r4 P2: truncating after concatenation let two long-named worktrees
    -- or any two worktrees on a 63-char host label -- collide). Never ':'-bearing or
    empty (reservations._check_id refuses both)."""
    short_host = host.split(".")[0][:22]
    digest = hashlib.sha256(str(repo.resolve()).encode()).hexdigest()[:8]
    name_budget = max(1, 64 - len(short_host) - len(digest) - 2)
    return f"{short_host}-{repo.name[:name_budget]}-{digest}".replace(":", "-")


#: This process's lane identity (C-HE-03 §3). Lane-init (U-HE-31) exports HARNESS_LANE_ID;
#: the fallback derives a stable per-(host, worktree) id.
LANE_ID = os.environ.get("HARNESS_LANE_ID") or _fallback_lane_id(socket.gethostname(), REPO)


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
    round_completeness: str = "complete"  # complete | partial-suffix | unknown
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
    # -- C-HE-25 v1.6 X6e cost fields (additive; historical rows read as null) --
    # requestId-deduplicated IET from the arc's session transcript (arc_cost.py)
    cost_main_calls: int | None = None
    cost_main_iet: float | None = None
    cost_subagent_calls: int | None = None
    cost_subagent_iet: float | None = None
    cost_source: str | None = None  # the transcript the figures were derived from


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


# The wrapper's terminal line ends every published round log. Exactly three
# producer shapes exist, and each label is restricted to the terminals its
# producer actually emits (codex_review._report emits the full enum under
# `codex-review:` and `gemini-review (failover):`; agy_review's own gate emits
# ONLY `gemini-review: GATE_REFUSED (<code>)`; agy's standalone `VERDICT:`
# dialect is NOT a round-log producer and aborts below as terminal-less,
# deliberately). The LAST such line is the transcript's verdict: a failover
# transcript carries the primary's REVIEWER_UNAVAILABLE before the failover
# verdict that stands, and publish-failure noise can FOLLOW it, so neither
# "first" nor "only" is the right read. Residual (named, not handled here):
# reviewer-controlled finding text is printed verbatim into the transcript, so
# a forged line remains representable until the wrapper owns an unforgeable
# terminal sentinel -- that emission contract is wrapper-internal work
# (B-218/U-HE-50 territory); the AUTHORITATIVE per-round terminal already
# lives on the reservation's round_outcomes and the C-HE-24 rows, both written
# from the schema-parsed verdict, never from this transcript read.
ROUND_TERMINAL_RE = re.compile(
    r"^(?:(?:codex-review|gemini-review \(failover\)): "
    r"(APPROVE|BLOCK|REVIEWER_UNAVAILABLE|GATE_REFUSED)"
    r"|gemini-review: (GATE_REFUSED))\b",
    re.MULTILINE,
)
# Round identity lives in the log NAME the publisher wrote (`r9-verdict.log` is
# round 9's verdict; U-HE-49's per-attempt names keep this prefix), never in the
# file's position within a listing.
ROUND_ID_RE = re.compile(r"^r(?:ound-?)?(\d+)(?=$|\D)")


def round_metrics(globs: list[str]) -> tuple[list[Path], list[float], list[int], list[int]]:
    """Derive per-round records from round-log CONTENT, never file position.

    C-HE-25 (v1.6 X6c): a round is a log whose wrapper terminal line is a review
    verdict; a `GATE_REFUSED` transcript is a refused LAUNCH -- the review never
    began -- and recording it as a round both inflates the count and shifts every
    later P1 index ([B] F15: the u-he-35 dir read as 12 rounds with P1s at 1 and
    11; the true content is 10 rounds with P1s at r1 and r10). Rounds key by the
    round id parsed from the log name, so `p1_rounds` carries ROUND IDS, and a
    refused attempt plus its retry under a fresh name collapse to one round.

    Returns ``(logs, gaps, p1_rounds, round_ids)``. The sorted id list is the
    log set's own testimony about its coverage; the completeness LABEL is a
    claim above that testimony and has exactly one classifier,
    `_completeness_for`, which grounds "complete" in the reservation authority
    -- this function never labels.
    """
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
    if not seen:
        raise AbortError(
            f"round logs: zero files matched {globs} -- refusing to record "
            "'0 rounds' for what may be an unlooked path"
        )

    # [LAW:parse-dont-validate] every matched file is parsed into (round id,
    # terminal) or refused loudly -- an unclassifiable log silently counted (or
    # silently dropped) is exactly the position-derived corruption X6c removes.
    rounds: dict[int, tuple[Path, str]] = {}
    for f in seen:
        try:
            text = f.read_text(errors="replace")
        except OSError as exc:
            raise AbortError(f"round logs: cannot read {f}: {exc}") from exc
        m = ROUND_ID_RE.match(f.stem)
        if not m:
            raise AbortError(
                f"round logs: cannot parse a round id from {f.name!r} -- round "
                "identity comes from the log name (r<N>...), never file position"
            )
        rid = int(m.group(1))
        terminals = [t.group(1) or t.group(2) for t in ROUND_TERMINAL_RE.finditer(text)]
        if not terminals:
            raise AbortError(
                f"round logs: {f.name!r} carries no wrapper terminal line -- a "
                "partial or foreign transcript cannot be classified as a round"
            )
        if terminals[-1] == "GATE_REFUSED":
            continue  # a refused launch, not a round (C-HE-25 X6c)
        if rid in rounds:
            raise AbortError(
                f"round logs: two review transcripts claim round {rid} "
                f"({rounds[rid][0].name!r} and {f.name!r}) -- write-once round "
                "evidence is ambiguous; fix the log set"
            )
        rounds[rid] = (f, text)
    if not rounds:
        raise AbortError(
            f"round logs: every file matching {globs} is a refused launch "
            "(GATE_REFUSED) -- no review round ever ran; fix the glob rather "
            "than record an empty arc"
        )

    # Rounds mint sequentially per arc, and every round's log is write-once
    # (retries publish under fresh per-attempt names), so a hole inside the
    # observed id range means a deleted or never-published log -- counting
    # around it would silently undercount the arc and span the missing round's
    # wall clock across one innocent-looking gap. (A set STARTING above 1 is
    # the distinct, declared `round_completeness=partial-suffix` case.)
    # Gaps derive from ADJACENT sorted ids -- filename ids are caller-controlled
    # input, and materializing min..max (a r100000000.log) is an OOM, not a
    # refusal.
    ids = sorted(rounds)
    gap_spans = [(a + 1, b - 1) for a, b in itertools.pairwise(ids) if b - a > 1]
    if gap_spans:
        shown = ", ".join(str(lo) if lo == hi else f"{lo}-{hi}" for lo, hi in gap_spans)
        raise AbortError(
            f"round logs: round id(s) {shown} are missing inside the observed "
            f"range {ids[0]}..{ids[-1]} -- a deleted or never-published "
            "log breaks the evidence set; fix the log set rather than record an "
            "undercounted arc"
        )

    logs = [rounds[rid][0] for rid in sorted(rounds)]
    mtimes = [f.stat().st_mtime for f in logs]
    # Rounds are published sequentially, so round-id order IS time order; an
    # mtime regression means a copied or re-touched log, and a negative gap
    # would enter cohort medians as a measurement. Refuse rather than record.
    for a, b in itertools.pairwise(zip(logs, mtimes, strict=True)):
        if b[1] < a[1]:
            raise AbortError(
                f"round logs: {b[0].name!r} predates {a[0].name!r} on disk but "
                "follows it by round id -- a copied or re-touched log is in the "
                "set; fix the logs rather than record a negative round gap"
            )
    gaps = [round(b - a, 1) for a, b in itertools.pairwise(mtimes)]

    p1_rounds = [rid for rid in sorted(rounds) if count_p1(rounds[rid][1]) >= 1]
    return logs, gaps, p1_rounds, ids


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
    (Both dialects are shapes WITHIN a transcript's text -- the bare dialect
    rides inside round logs that quote absorption commits, never as a
    standalone terminal-less file; round classification itself stays with the
    wrapper terminal line in round_metrics.)
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
            # Absent on snapshots queued before the X6c rev. Those were
            # computed by the positional algorithm over arbitrary surviving
            # subsets -- refused attempts counted, retries duplicated -- so
            # nothing about them is re-derivable from the snapshot (not even a
            # suffix bound: the stored counts and gaps themselves may be
            # corrupt). Every unlabeled legacy snapshot is `unknown`, which
            # consumers exclude from ALL round-derived aggregates.
            row.round_completeness = snapshot.get("round_completeness") or "unknown"
            first = parse_iso(snapshot["first_round_at"])
            row.first_round_at = snapshot["first_round_at"]
            row.last_round_at = snapshot["last_round_at"]
        else:
            logs, gaps, p1, round_ids = round_metrics(args.round_logs)
            row.review_rounds = len(logs)
            row.round_wall_s = gaps
            row.p1_rounds = p1
            row.round_completeness = _completeness_for(row.arc_id, round_ids)
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

    # Cost fields (C-HE-25 X6e): a closure-time snapshot wins over a live
    # transcript read, for the same reason the round snapshot wins -- the
    # transcript may have grown or been GC'd since the arc closed.
    cost = getattr(args, "cost_snapshot", None)
    if cost is None and getattr(args, "transcript", None):
        cost = _cost_snapshot(args.transcript, row.arc_id)
    if cost:
        row.cost_main_calls = cost["main_calls"]
        row.cost_main_iet = cost["main_iet"]
        row.cost_subagent_calls = cost["subagent_calls"]
        row.cost_subagent_iet = cost["subagent_iet"]
        row.cost_source = cost["source"]
        prov["cost_fields"] = "derived"
    else:
        prov["cost_fields"] = "unmapped:no-transcript-supplied"

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


def _require_reservation_holder(row: ArcRow) -> None:
    """C-HE-04 §2(ii): only the lane holding the OPEN reservation may append -- a lane
    killed after append cannot be silently superseded by a second appender. One
    extension, codex U-HE-19 r3 P1 (registered contradiction, plan rev item vii): the
    lane recorded on a MERGED head may make the arc's FIRST append -- open->merged
    flips before the closure capture drains (the merge door post-U-HE-22, and this
    module's own serialized fold+terminalization at drain), and C-HE-03 §6 forbids
    *re*-appending a merged arc_id, not the merged holder's own capture. Unconditional
    at every production append (codex r8 P2: no caller-optional bypass exists; tests
    stub THIS seam). `reservations` imports this module at load; import it inside the
    functions that need it (plan U-HE-19)."""
    import reservations as rs

    cur = rs.current(row.arc_id)
    state = cur[1].get("state") if cur else None
    owner = cur[1].get("lane_id") if cur else None
    if not (owner == LANE_ID and state in ("open", "merged")):
        raise AbortError(
            f"{row.arc_id}: this lane ({LANE_ID}) is not the reservation holder "
            f"(state={state!r}, lane={owner!r}) -- append refused (C-HE-04 §2)"
        )
    if state == "merged":
        # The merged-holder admission covers exactly the not-yet-committed first
        # capture. Once a row for this arc is in COMMITTED history, a same-lane
        # append from another/reset worktree ledger would be the C-HE-03 §6
        # re-append the per-worktree duplicate guard cannot see (codex r6 P1).
        # TRI-STATE read (codex r7 P1): UNREADABLE merged history must HOLD, never
        # fail open -- committed_arc_ids()'s empty set cannot tell "no row" from
        # "git show failed", so the admission keys on _committed_ledger_lines(),
        # whose None means unknown.
        lines = _committed_ledger_lines()
        if lines is None:
            raise AbortError(
                f"{row.arc_id}: merged reservation but committed history is "
                "unreadable -- holding the append (fail closed, C-HE-03 §6)"
            )
        for line in lines:
            try:
                if json.loads(line).get("arc_id") == row.arc_id:
                    raise AbortError(
                        f"{row.arc_id}: reservation is merged and a row is already "
                        "in committed history -- re-append refused (C-HE-03 §6)"
                    )
            except json.JSONDecodeError as exc:
                # An unparseable committed line could BE this arc's row: corruption
                # reads as UNREADABLE, never as absence (codex r10 P2) -- hold.
                raise AbortError(
                    f"{row.arc_id}: committed ledger history contains an unparseable "
                    "line -- holding the merged-path append (fail closed)"
                ) from exc


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
    _require_reservation_holder(row)
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


def _reservation_recorded_rounds(arc_id: str) -> set[int]:
    """Round ids the C-HE-25 recorder accreted on this arc's reservation.

    Empty when no head or no outcomes exist. ONE-DIRECTIONAL authority: the
    outcomes can legitimately UNDERCOUNT the logs (a round run without the
    HARNESS_ARC_ID prefix records on a fallback arc id), so only a recorded
    round MISSING from the observed set is ever a claim -- observed rounds
    absent from the outcomes are not. (`reservations` imports this module at
    load; import it inside the function, as _require_reservation_holder
    does.)"""
    import reservations as rs

    cur = rs.current(arc_id)
    outcomes = (cur[1].get("round_outcomes") or {}) if cur else {}
    # Keys are "<round>/<channel>" (record_round_outcome_if_reserved; verified
    # live: {"1/codex": ...}). int() raising on a foreign key is the loud path:
    # an unparseable authority must never be silently skipped into "no claim".
    return {int(k.split("/", 1)[0]) for k in outcomes}


# Round numbers are scoped to (arc_id, producer): the merge-gate lenses and
# the reviewer-concurrency probe number their OWN row spaces, which overlap the
# review wrappers' round ids. Only the two wrappers produce review rounds --
# the thing a round LOG evidences -- so only their rows are round authority.
REVIEW_ROUND_PRODUCERS = frozenset({"codex_review_wrapper", "gemini_review_wrapper"})


def _gate_log_recorded_rounds(arc_id: str) -> set[int]:
    """The fail-closed half of the round authority.

    The reservation recorder is deliberately best-effort (its writer catches
    every exception and continues), but the C-HE-24 rows are write-first --
    every review terminal yields at least one row under the log lock -- so a
    round whose reservation persistence failed still appears here. Scoped to
    the review-wrapper producers: an unrelated merge-gate lens r1 must neither
    certify a codex log set nor abort it."""
    if not GATE_LOG.exists():
        return set()
    rounds: set[int] = set()
    for line in GATE_LOG.read_text().splitlines():
        row = json.loads(line)  # an unparseable authority is loud, never skipped
        if (
            row.get("arc_id") == arc_id
            and row.get("producer") in REVIEW_ROUND_PRODUCERS
            and row.get("round_n") is not None
        ):
            rounds.add(int(row["round_n"]))
    return rounds


def _recorded_rounds(arc_id: str) -> set[int]:
    """Union of the two round authorities: the best-effort reservation
    accretion and the fail-closed gate log. Either alone can under-record
    (a swallowed reservation write; a pre-C-HE-24 round); together they are
    the strongest recorded evidence available without a paid re-run."""
    return _reservation_recorded_rounds(arc_id) | _gate_log_recorded_rounds(arc_id)


def _completeness_for(arc_id: str, observed_ids: list[int]) -> str:
    """The ONE classifier of a live log set's `round_completeness` label.

    The set's own testimony covers only its start: an observed min above 1
    proves a missing prefix (`partial-suffix`). "complete" is a CLAIM about the
    tail, and only the recorded authority (reservation accretion UNION the
    fail-closed C-HE-24 gate log) can back it -- the recorded set's
    maximum equal to the observed maximum. Any RECORDED round at or after the
    observed start with no surviving classified log is a broken evidence set
    (refuse) -- this covers both a deleted tail AND a real round whose
    transcript reads refused (a refused launch never yields an outcome, so a
    recorded round that parses GATE_REFUSED means a forged or mangled
    transcript); recorded rounds missing BEFORE the start are the ordinary
    partial-suffix archive. No authority, or an
    under-recording one (unprefixed rounds land on fallback arc ids), leaves
    `unknown` -- a label every consumer treats as a lower bound excluded from
    exact aggregates, never a guess of wholeness."""
    recorded = _recorded_rounds(arc_id)
    observed = set(observed_ids)
    start = min(observed)
    # Recorded rounds missing BEFORE the observed start are the ordinary
    # partial-suffix archive (early logs lost); recorded rounds missing AT or
    # AFTER it mean a deleted tail or a real round whose transcript reads
    # refused (a refused launch never yields an outcome, so that is a forged
    # or mangled transcript) -- refuse those.
    missing = sorted(r for r in recorded if r >= start and r not in observed)
    if missing:
        raise AbortError(
            f"round logs: the reservation records round(s) {missing} but no "
            "surviving log classifies as those rounds -- a deleted, forged, or "
            "mangled transcript is in the evidence set; fix the log set rather "
            "than record it as the whole arc"
        )
    if start > 1:
        return "partial-suffix"
    return "complete" if recorded and max(recorded) == max(observed) else "unknown"


def _cost_snapshot(transcripts: list[str], arc_id: str) -> dict | None:
    """C-HE-25 X6e: requestId-deduplicated transcript cost (arc_cost.py owns the math).

    Bounded to THIS arc's window (codex u-he-48 r3): one session ships
    consecutive arcs, so whole-session totals would fold every earlier arc's
    usage into the later row. The arc-start authority is the reservation's
    ``reserved_at``; without a head there is no truthful boundary, so the cost
    is skipped loudly (null fields read as could-not-look, C-HE-25) rather
    than recorded cumulatively. A resumed/handed-off arc spans sessions (r4):
    every transcript that ran the arc is passed and pooled with global
    requestId dedupe inside arc_cost.
    """
    # lazy imports, same as elsewhere: keep module load free of tool coupling
    import arc_cost
    import reservations as rs

    cur = rs.current(arc_id)
    if cur is None:
        print(f"  {arc_id}: cost skipped — no reservation head to bound the arc window")
        return None
    since = arc_cost.parse_ts(cur[1]["reserved_at"], what=f"{arc_id} reserved_at")
    try:
        report = arc_cost.cost_report([Path(t) for t in transcripts], cuts=[since])
    except arc_cost.CostError as exc:
        raise AbortError(f"cost extraction failed: {exc}") from exc
    window = report["windows"][1]  # [reserved_at, end)
    if window["main"]["calls"] == 0:
        # transcripts with no usage inside this arc's window are some OTHER
        # session's — a false measured-zero must not enter the ledger
        raise AbortError(
            f"cost extraction refused: {';'.join(transcripts)} has no main-session usage "
            f"after {arc_id}'s reserved_at ({cur[1]['reserved_at']}) — wrong transcript(s)?"
        )
    return {
        "main_calls": window["main"]["calls"],
        "main_iet": window["main"]["iet"],
        "subagent_calls": window["subagents"]["calls"],
        "subagent_iet": window["subagents"]["iet"],
        "source": ";".join(report["transcripts"]),
    }


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
        logs, gaps, p1, round_ids = round_metrics(args.round_logs)
        completeness = _completeness_for(arc_id, round_ids)
        first = datetime.fromtimestamp(logs[0].stat().st_mtime, tz=UTC)
        last = datetime.fromtimestamp(logs[-1].stat().st_mtime, tz=UTC)
        snapshot = {
            "review_rounds": len(logs),
            "round_wall_s": gaps,
            "p1_rounds": p1,
            "round_completeness": completeness,
            "first_round_at": first.isoformat(),
            "last_round_at": last.isoformat(),
            "round_log_source": str(logs[0].parent),
            "matched": [str(p) for p in logs],
        }

    # Same snapshot rationale as the round logs: the transcript is the arc's own
    # NOW, and it can grow (the session continues past closure) or be GC'd before
    # the next arc's drain runs. Derive at closure; drain folds the numbers.
    cost_snapshot = (
        _cost_snapshot(args.transcript, arc_id) if getattr(args, "transcript", None) else None
    )

    entry = {
        "pr": args.pr,
        "arc_id": args.arc_id,
        "arc_type": args.arc_type,
        "arc_type_declared_at": getattr(args, "arc_type_declared_at", None) or "close",
        "decisions": args.decisions,
        "cost_snapshot": cost_snapshot,
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


def _committed_ledger_lines() -> set[str] | None:
    """The merged default branch's ledger, as normalized raw lines. TRI-STATE (codex r7
    P1): a set (possibly empty) is KNOWN content; None means merged history exists but
    is UNREADABLE (hold / fail closed). A ledger outside the repo has no committed
    history at all -- that is a KNOWN-empty set, not an unknown."""
    try:
        rel = LEDGER.relative_to(REPO)
    except ValueError:
        return set()
    try:
        raw = run(["git", "show", f"{MERGED_REF}:{rel}"], what="git show merged ledger")
    except AbortError:
        return None
    return {line.strip() for line in raw.splitlines() if line.strip()}


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
    # lane_id in the stamp is the D2-transfer witness (codex U-HE-19 r1 P1): recovery may
    # move a reservation's holder only when the DEAD claimant provably was that holder --
    # pid/host alone cannot say which lane the claimant belonged to.
    payload = json.dumps(
        {**entry, "_claim": {"pid": os.getpid(), "host": socket.gethostname(), "lane_id": LANE_ID}},
        sort_keys=True,
    )
    dead_claim_entry: dict | None = None
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
                # The dead claimant may have been the reservation holder (it claimed,
                # flipped open, and died mid-drain after the startup recovery sweep):
                # STASH the aside bytes -- the LAST lane-stamped evidence -- before
                # they vanish (codex U-HE-19 r12 P2); the transfer itself waits until
                # the replacement claim is atomically WON (codex r15 P2: transferring
                # first and then losing the retry would re-home the reservation under
                # a lane with no claim).
                try:
                    dead_claim_entry = json.loads(aside.read_text())
                except (OSError, ValueError):
                    dead_claim_entry = None
                if dead_claim_entry is not None:
                    # Adjudicated r15 vs merge-gate/codex r20 tension: transfer NOW,
                    # from the stashed bytes, BEFORE the evidence is destroyed. If we
                    # then lose the retry-publish to a concurrent claimant, the
                    # reservation is held by THIS (live) lane and we drain the entry on
                    # our own next pass -- not a wedge; if we die first it degrades to
                    # the registered stuck-open §5 HITL posture. The alternative
                    # (transfer only after winning) let a lost retry destroy the only
                    # dead-holder evidence and strand the arc under a DEAD lane.
                    _transfer_from_dead_claim(dead_claim_entry)
                    dead_claim_entry = None
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


def _hold_after(step: str) -> None:
    """Test seam (U-HE-20, sibling of ``_kill_after``): ``ARC_METRICS_TEST_HOLD_AFTER=<step>``
    -> touch ``<ARC_METRICS_TEST_HOLD_DIR>/<step>.reached`` and wait (<= 30 s) for
    ``<step>.go``. Lets a test interleave a peer action at an exact point
    (C-HE-04 verification (iii)/(iv)/(v)). Steps: the ``_kill_after`` names plus
    ``restore-link`` (mid-restore, between the exclusive re-link and the claim unlink)."""
    if os.environ.get("ARC_METRICS_TEST_HOLD_AFTER") != step:
        return
    hold = Path(os.environ["ARC_METRICS_TEST_HOLD_DIR"])
    (hold / f"{step}.reached").touch()
    deadline = time.monotonic() + 30
    while not (hold / f"{step}.go").exists():
        if time.monotonic() > deadline:
            raise AbortError(f"hold seam timeout at {step}")
        time.sleep(0.02)


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
        # U-HE-20 (iv) mid-restore hold: BOTH names exist here; a peer's takeover is
        # refused by this drain's live claim (exclusive create), never by timing.
        _hold_after("restore-link")
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


def _transfer_reservation_to_recoverer(restored: Path) -> None:
    """C-HE-04 §4 second half: restoring a DEAD owner's entry transfers its `open`
    reservation to THIS lane in the same recovery step (C-HE-03 §6 -- the named D2
    exception), so the recovering lane's holder-gated append() is authorized. The
    deadness adjudication lives at the call site (the pid+host liveness check on the
    claim bytes); this helper only records the already-adjudicated transfer.

    Accepted residual (codex U-HE-19 r3 P1, D8 fail-toward-stall): if the RECOVERER
    dies after this transfer and before draining the restored entry, no claim carries
    the new holder's lane, so a later recovery pass cannot re-adjudicate -- the arc
    stalls as a stuck-open reservation until C-HE-03 §5's ground-truth pass escalates
    it (NOTIFY + DEFERRED-HIL via reconcile_all at session start; HITL, never TTL).
    Stall-not-duplicate is the same posture C-HE-02 §6 accepts for pid reuse."""
    try:
        entry = json.loads(restored.read_text())
    except (OSError, ValueError):
        return  # consumed or unreadable meanwhile -- the drain loop re-judges it
    _transfer_from_dead_claim(entry)


def _transfer_from_dead_claim(entry: dict) -> None:
    """The parsed-bytes half of `_transfer_reservation_to_recoverer` -- for callers
    that must stash the dead claim's evidence and transfer only after a later atomic
    step succeeds (codex r15 P2: _claim_arc's takeover transfers only once it has WON
    the replacement claim)."""
    import reservations as rs

    arc_id = entry.get("arc_id") or (f"pr-{entry['pr']}" if "pr" in entry else None)
    if not arc_id:
        return
    # The dead CLAIMANT's lane, from the claim stamp the restore preserved. Transfer only
    # when that lane IS the reservation holder (codex U-HE-19 r1 P1): a non-holder can
    # claim a held entry and die -- moving the LIVE holder's reservation to the recoverer
    # would authorize a second append. An unstamped (legacy/foreign) claim proves nothing.
    claim_lane = (entry.get("_claim") or {}).get("lane_id")
    if not claim_lane:
        print(f"  {arc_id}: dead claim carries no lane identity; holder transfer skipped")
        return
    try:
        cur = rs.current(arc_id)
        dead_lane = cur[1].get("lane_id") if cur else None
        if (
            dead_lane
            and claim_lane == dead_lane
            and rs.holder(arc_id) == dead_lane
            and dead_lane != LANE_ID
        ):
            rs.transfer_holder(arc_id, from_lane_id=dead_lane, to_lane_id=LANE_ID)
            print(f"  {arc_id}: reservation holder transferred {dead_lane} -> {LANE_ID}")
        elif dead_lane and claim_lane != dead_lane:
            print(
                f"  {arc_id}: dead claim belonged to {claim_lane!r}, not the holder "
                f"({dead_lane!r}); holder transfer refused"
            )
    except OSError as exc:
        if _is_systemic(exc):
            raise  # queue-dir permission / I/O faults keep their whole-drain abort semantics
        # a directory-shaped or unreadable generation (IsADirectoryError -- codex r17
        # P2) is a per-arc condition, same disposition as a malformed head
        print(
            f"  {arc_id}: holder transfer skipped ({exc}); "
            "stuck-open heads escalate via the C-HE-03 §5 reconcile pass"
        )
    except (KeyError, TypeError, ValueError, AttributeError, rs.ReservationError) as exc:
        # A stale precondition (a peer transferred first, the state moved on) OR an
        # unreadable/malformed reservation head (JSONDecodeError is a ValueError; a
        # non-object head raises AttributeError -- codex r6 P2) is a per-arc condition:
        # the entry is safely back; the holder gate at append keeps this lane honest
        # either way. Loud, never silent, never a whole-drain abort. An ATTEMPTED
        # transfer that failed (CAS exhaustion / malformed head -- codex r16 P2)
        # degrades to the registered stall posture: the reservation stays stuck-open
        # and C-HE-03 §5's ground-truth pass escalates it (DEFERRED-HIL), while a
        # stale-precondition loss means another lane already resolved it.
        print(
            f"  {arc_id}: holder transfer skipped ({exc}); "
            "stuck-open heads escalate via the C-HE-03 §5 reconcile pass"
        )


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
            # Dead-owner route only: same-step holder transfer (C-HE-04 §4), read from the
            # aside bytes BEFORE the queue name is public (codex U-HE-19 r2 P2: once the
            # .json exists a peer can claim + consume it and the stamped dead-holder
            # evidence vanishes with the aside).
            _transfer_reservation_to_recoverer(orphan)
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
                    # The re-judged aside is the LAST dead-holder evidence for this
                    # arc (codex r7 P2: a drain that died after the restore link but
                    # before this unlink left its reservation open-held) -- run the
                    # C-HE-04 §4 transfer from those bytes before they vanish.
                    _transfer_reservation_to_recoverer(gone)
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
        # Transfer the holder from the ASIDE bytes, BEFORE the queue name is public
        # (codex U-HE-19 r2 P2): once the .json exists a peer can claim + consume it and
        # the dead-holder evidence (the stamped claim) is gone with the aside.
        _transfer_reservation_to_recoverer(aside)
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
        # If OUR open reservation survived an interrupted post-append
        # terminalization, finish it here (codex r6 P2: without this retry the
        # early return keeps the head open forever while the row sits local).
        import reservations as rs

        try:
            cur = rs.current(arc_id)
            if cur and cur[1]["state"] == "open" and cur[1]["lane_id"] == LANE_ID:
                updates = (
                    {"pr": entry["pr"]} if cur[1].get("pr") is None and "pr" in entry else None
                )
                rs.transition(arc_id, "merged", lane_id=LANE_ID, updates=updates)
                head = rs.current(arc_id)
                if head:
                    # the crashed drain's fold may predate accretions; re-fold the
                    # still-uncommitted row from the now-terminal head (codex r9)
                    _refold_local_row(arc_id, head[1])
                print(f"  {arc_id}: completed deferred reservation terminalization")
            elif cur and cur[1]["state"] == "merged" and cur[1]["lane_id"] == LANE_ID:
                # A refold that failed after the terminal flip (ledger claimed, I/O --
                # codex r10 P2) heals here: idempotent re-projection from the terminal
                # head on every held pass while the row is uncommitted.
                _refold_local_row(arc_id, cur[1])
        except (KeyError, TypeError, AttributeError, ValueError, rs.ReservationError) as exc:
            print(f"  {arc_id}: deferred terminalization not completed ({exc})")
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
    _hold_after("claim")
    if taken is None:
        print(f"  {arc_id}: claimed by a concurrent drain, still outstanding")
        return "outstanding"

    # `reservations` imports this module at load; import it inside the functions that
    # need it (plan U-HE-19) so the cycle never forms at import time. The U-HE-16
    # module-set grep witness is unaffected.
    import reservations as rs

    try:
        # C-HE-04 §2 order: (i) flip pending->open with holder = this lane, (ii) append
        # (holder-gated), (iii) restore/hold. The flip happens BEFORE append so a lane
        # killed after append leaves an `open` reservation a peer can only take over
        # through §4's adjudicated holder transfer -- never by silently re-appending.
        cur = rs.current(arc_id)
        if cur is None:
            # Transitional bootstrap for entries queued before reservations existed
            # (migration, plan §6 open item 3): reserve with the truthful close-time
            # label. The reservation is created BEFORE the fail-closed NOTIFY
            # (loop_log_structured lands at U-HE-29), so a raised emit costs one loud
            # KEPT-QUEUED cycle, never the capture: the next drain finds the pending
            # reservation and proceeds without re-emitting.
            rs.reserve(
                arc_id,
                lane_id=LANE_ID,
                branch=entry.get("branch", "unknown"),
                arc_type=entry["arc_type"],
                # honor the entry's own declaration (codex r13 P2: hard-coding "close"
                # here while extract() preserves the queue's "open" value would stamp
                # a row whose provenance disagrees with its authoritative reservation)
                arc_type_declared_at=entry.get("arc_type_declared_at") or "close",
            )
            rs.emit_loop_row(
                "NOTIFY",
                LANE_ID,
                "reservation-bootstrap:transient-retry:legacy_queue_entry",
                f"{arc_id} reservation created at drain (legacy entry)",
            )
            cur = rs.current(arc_id)
        state = cur[1]["state"]
        if cur[1].get("branch") == BACKFILL_BRANCH:
            # merge-gate r1/r2 concurrency P2: a head minted by cmd_extract's backfill
            # belongs to THAT invocation in EVERY state -- pending, open, or merged
            # (same-worktree lane_id matches, so the state elifs below cannot
            # distinguish ownership). Consuming it here would fold the backfill's
            # placeholder head over the drain's row AND discard the backfill's own
            # capture at its transition/append. Hold the entry; the backfill completes
            # (or its aged head escalates via C-HE-03 §5).
            _restore_or_republish(taken, path, entry)
            print(
                f"  {arc_id}: reservation belongs to a cmd_extract backfill "
                f"(state={state!r}); entry held for that flow"
            )
            return "held"
        if state == "pending":
            cur = (cur[0], rs.open_with_sensor(arc_id, LANE_ID))
        elif state == "open" and cur[1]["lane_id"] != LANE_ID:
            _restore_or_republish(taken, path, entry)
            print(
                f"  {arc_id}: open reservation held by {cur[1]['lane_id']}; "
                "not appendable by this lane -- entry held"
            )
            return "held"
        elif state == "merged" and cur[1]["lane_id"] != LANE_ID:
            # NEVER release here (codex U-HE-19 r2 P1): the C-HE-04 invariant releases an
            # entry only once its row is in COMMITTED history (the `arc_id in committed`
            # branch above). A merged reservation proves the PR merged -- not that any
            # lane's row exists (the holder can die between the merged flip and append;
            # reconcile() terminalizes from GitHub state alone). Another lane's merged
            # arc is not ours to append: hold the sole capture for that lane / HITL.
            _restore_or_republish(taken, path, entry)
            print(
                f"  {arc_id}: reservation merged by {cur[1]['lane_id']} and the row is "
                "not in committed history; entry held (HITL if it persists)"
            )
            return "held"
        # `merged` held by THIS lane falls through (codex U-HE-19 r3 P1): the
        # post-U-HE-22 normal flow flips open->merged at the merge door BEFORE the
        # closure capture drains, so the merged holder's own first append IS the
        # ordinary capture path -- append()'s gate admits exactly this shape.
        res = cur[1]
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
            cost_snapshot=entry.get("cost_snapshot"),
            transcript=None,
            levers=entry.get("levers"),
            notes=entry.get("notes", ""),
        )
        if os.environ.get("ARC_METRICS_TEST_ABORT_EXTRACT"):
            raise AbortError("test: extract abort (U-HE-20 (v))")
        row = extract(args)

        # C-HE-27 §3 fold at drain, after the flip: the reservation's accreted facts land
        # on the ONE arc row. `fold_round_outcomes` is the committed projection of the
        # composite "<round>/<channel>" carrier into the C-HE-25 numeric arc-row shape
        # (plan rev 2026-08-20, clearance marker
        # implementation-plan-he-loop-lanes-v1-s4b-u-he-19-fold-rev-cleared-2026-08-20).
        # Fold from a fresh head, append, THEN terminalize -- generation-bound (codex
        # r4/r7/r8/r9 lineage). Append-first keeps every recovery path alive: a lane
        # dying between append and the flip leaves an OPEN head whose dead claim §4
        # can transfer, and the local-hold branch completes the terminalization on
        # retry -- terminalize-first left a merged headless capture NO lane could ever
        # drain (codex r9 P1). Accretion-completeness is preserved the other way
        # round: the flip is generation-bound to the folded head, and a lost race
        # RE-FOLDS the still-uncommitted local row from the terminal head
        # (_refold_local_row) instead of silently omitting the late CAS.
        if res.get("state") == "open":
            fresh = rs.current(arc_id)
            if not fresh or fresh[1].get("state") != "open" or fresh[1].get("lane_id") != LANE_ID:
                raise AbortError(f"{arc_id}: reservation moved during the drain fold -- entry kept")
            res = fresh[1]
        _fold_head_onto(row, res)
        _kill_after("extract")
        _hold_after("extract")
        append(row)
        _kill_after("append")
        _hold_after("append")
        if res.get("state") == "open":
            updates = {"pr": entry["pr"]} if res.get("pr") is None and "pr" in entry else None
            try:
                rs.transition(
                    arc_id,
                    "merged",
                    lane_id=LANE_ID,
                    updates=updates,
                    expect={"generation": res.get("generation")},
                )
            except rs.IllegalTransition:
                head = rs.current(arc_id)
                if head and head[1].get("state") == "open" and head[1].get("lane_id") == LANE_ID:
                    # an accretion CAS won the generation: close the head, then re-fold
                    rs.transition(arc_id, "merged", lane_id=LANE_ID, updates=updates)
                    head = rs.current(arc_id)
                if head and head[1].get("state") == "merged":
                    _refold_local_row(arc_id, head[1])
                    print(f"  {arc_id}: late accretion re-folded into the local row")
                else:
                    raise  # the head moved to a shape we do not own -- per-arc kept, loud
    except (
        AbortError,
        KeyError,
        TypeError,
        AttributeError,
        ValueError,
        OSError,
        rs.ReservationError,
    ):
        # Durable restore BEFORE the caller reports KEPT QUEUED (C-HE-04 SS7) --
        # OSError included (EMFILE from append, ...): drain() re-classifies it
        # after the entry is durably back (codex r5 P2). If the fault is
        # systemic the restore may itself raise; that escapes to the same
        # systemic abort.
        _restore_or_republish(taken, path, entry)
        _kill_after("restore-abort")
        _hold_after("restore-abort")
        raise
    # Restore the capture to the queue rather than deleting it: the row is
    # only in the working tree so far, and the declarations it carries exist
    # nowhere else. It is released on a later drain, once the row is in
    # committed history.
    _restore_or_republish(taken, path, entry)
    _kill_after("restore")
    _hold_after("restore")
    print(f"  {arc_id}: appended (entry held until the row is committed)")
    return "added"


def _reconcile_local_rows() -> None:
    """C-HE-04 §5: drop this worktree's uncommitted rows whose reservation is held or
    merged by ANOTHER lane (we died after append; a peer superseded us via §4). Atomic
    whole-file rewrite; committed rows untouched. Closes the "orphaned local row rides
    along in the next PR" path (ADV-F6) before SPLIT_BRAIN_LEDGER would catch it at CI."""
    import reservations as rs

    if not LEDGER.exists():
        return
    # Under the ledger claim (codex U-HE-19 r1 P2): an append/relabel landing between an
    # unclaimed read and the whole-file replace would be silently discarded. A live peer
    # holding the claim means yield loudly -- reconciliation re-runs at every drain start.
    try:
        claim_ledger(LEDGER)
    except AbortError as exc:
        print(f"  local-row reconciliation skipped: {exc}")
        return
    try:
        rows = read_ledger()
        if not rows:
            return
        committed_lines = _committed_ledger_lines()
        if committed_lines is None:
            # Tri-state stop (codex r21 P2): committed_arc_ids()'s empty set cannot
            # tell "no committed rows" from "git show failed", and an unreadable
            # MERGED_REF would misclassify committed baseline rows as uncommitted --
            # droppable. When committed history is UNKNOWN, reconcile NOTHING.
            print("  local-row reconciliation skipped: committed history unreadable")
            return
        committed = set()
        for cl in committed_lines:
            try:
                committed.add(json.loads(cl).get("arc_id"))
            except json.JSONDecodeError:
                # A malformed committed line could BE any arc's row: corruption reads
                # as UNREADABLE, never as absence (codex r22 P2, same posture as the
                # merged-append fence) -- no destructive judgment on a corrupt ledger.
                print(
                    "  local-row reconciliation skipped: committed history contains "
                    "an unparseable line"
                )
                return
        keep, dropped = [], []
        replaced: set[str] = set()
        for r in rows:
            aid = r.get("arc_id")
            try:
                # The WHOLE per-row judgment is guarded (codex U-HE-19 r2/r3 P2): a
                # corrupt reservation head raising anywhere here -- read, shape access,
                # missing keys -- must not abort the drain. Fail SAFE: keep the row.
                if aid and aid in committed:
                    if aid in replaced:
                        # every LATER occurrence of a committed aid is a duplicate,
                        # whatever its bytes (codex r10 P2: a canonical first line must
                        # not let a divergent second one mint another canonical copy)
                        dropped.append(f"{aid} (duplicate of a committed arc)")
                        continue
                    replaced.add(aid)
                    line = json.dumps(r, sort_keys=True)
                    if committed_lines is not None and line not in committed_lines:
                        # The arc IS in committed history but THIS row is not that
                        # content. Discriminate by the reservation (codex r9/r10 P2):
                        # superseded-by-a-peer (open/merged held by another lane) means
                        # ours is the stale bytes -- converge to the committed
                        # canonical line, never a bare deletion. NO such reservation
                        # means the divergence is a legitimate local update to a
                        # committed row (a pending relabel) or pre-rebase baseline
                        # content -- ours to keep untouched.
                        cur = rs.current(aid)
                        if (
                            cur
                            and cur[1].get("lane_id") != LANE_ID
                            and cur[1].get("state") in ("open", "merged")
                        ):
                            canonical = next(
                                (
                                    cl
                                    for cl in committed_lines
                                    if json.loads(cl).get("arc_id") == aid
                                ),
                                None,
                            )
                            if canonical is None:
                                dropped.append(aid)
                                continue
                            keep.append(json.loads(canonical))
                            dropped.append(f"{aid} (replaced with committed content)")
                            continue
                    keep.append(r)
                    continue
                cur = rs.current(aid) if aid else None
                if cur and cur[1]["state"] == "open" and cur[1]["lane_id"] != LANE_ID:
                    # Superseded via §4 while this lane was dead: the peer HOLDS the
                    # open reservation and owns the append; the queue entry (held under
                    # the C-HE-04 invariant) still carries the declarations.
                    dropped.append(aid)
                    continue
                if cur and cur[1]["state"] == "merged" and cur[1]["lane_id"] != LANE_ID:
                    # C-HE-04 §5 names "merged by another lane's ROW" -- merged state
                    # alone does not prove that row exists (codex U-HE-19 r2 P1: the
                    # holder can die between the merged flip and append). Until the
                    # replacement row reaches committed history, this row may be the
                    # only capture: keep it, loudly.
                    print(
                        f"  {aid}: reservation merged by {cur[1]['lane_id']} but no "
                        "committed row yet; local row kept pending reconciliation"
                    )
            except OSError as exc:
                if _is_systemic(exc):
                    raise
                # per-row (codex r17 P2): a directory-shaped generation raises
                # IsADirectoryError from rs.current -- keep the row, keep draining
                print(f"  {aid}: reservation unreadable during reconciliation ({exc}); row kept")
            except (KeyError, TypeError, AttributeError, ValueError, rs.ReservationError) as exc:
                # AttributeError included: a syntactically valid NON-OBJECT head makes
                # cur[1].get raise it (codex r13 P2) -- per-row, never a drain abort
                print(f"  {aid}: reservation unreadable during reconciliation ({exc}); row kept")
            keep.append(r)
        if dropped:
            tmp = LEDGER.with_name(f".{LEDGER.name}.{os.getpid()}.tmp")
            tmp.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in keep))
            os.replace(tmp, LEDGER)
            print(
                f"  dropped {len(dropped)} orphaned local row(s) superseded by another lane: "
                f"{', '.join(dropped)}"
            )
    finally:
        release_ledger(LEDGER)


def _fold_head_onto(row: ArcRow, head: dict) -> None:
    """C-HE-27 §3 / C-HE-25 / C-HE-26 §1 fold: project the reservation head's accreted
    facts onto the ONE arc row. `fold_round_outcomes` is the committed projection of
    the composite "<round>/<channel>" carrier (plan rev 2026-08-20, fold-rev marker)."""
    import reservations as rs

    row.phases = head.get("phases", {})
    row.round_outcomes = rs.fold_round_outcomes(head.get("round_outcomes", {}))
    row.concurrent_lanes_at_open = head.get("concurrent_lanes_at_open")
    if head.get("arc_type_declared_at") == "open":
        # C-HE-26 §1: the reservation IS the open-time capture point -- the label joins
        # via arc_id AND the row's provenance says so (codex r4 P2). The canonical
        # label follows the declared-at provenance (codex r6 P2); the close-time queue
        # label stays visible beside it (C-HE-26 §2).
        row.arc_type_open = head.get("arc_type")
        row.arc_type_declared_at = "open"
        row.arc_type = head.get("arc_type")
    row.lane_id = LANE_ID
    row.head_sha = head.get("head_sha")
    row.base_sha = head.get("base_sha")


def _refold_local_row(arc_id: str, head: dict) -> None:
    """Re-project the head's accreted facts onto the already-appended LOCAL row --
    only ever called while the row is uncommitted, under the ledger claim. This is how
    a late accretion CAS (landing between the fold read and the generation-bound
    terminalization) reaches the one arc row instead of vanishing (codex r8/r9)."""
    import reservations as rs

    claim_ledger(LEDGER)
    try:
        rows = read_ledger()
        hit = False
        for r in rows:
            if r.get("arc_id") != arc_id:
                continue
            hit = True
            r["phases"] = head.get("phases", {})
            r["round_outcomes"] = rs.fold_round_outcomes(head.get("round_outcomes", {}))
            r["concurrent_lanes_at_open"] = head.get("concurrent_lanes_at_open")
            if head.get("arc_type_declared_at") == "open":
                r["arc_type_open"] = head.get("arc_type")
                r["arc_type_declared_at"] = "open"
                r["arc_type"] = head.get("arc_type")
            r["head_sha"] = head.get("head_sha")
            r["base_sha"] = head.get("base_sha")
        if hit:
            tmp = LEDGER.with_name(f".{LEDGER.name}.{os.getpid()}.tmp")
            tmp.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
            os.replace(tmp, LEDGER)
    finally:
        release_ledger(LEDGER)


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
    import reservations as rs

    try:
        _recover_dead_claims()
        _reconcile_local_rows()

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
        except (
            AbortError,
            KeyError,
            TypeError,
            AttributeError,
            ValueError,
            rs.ReservationError,
        ) as exc:
            # Per-arc fault -- AbortError from capture, a malformed entry
            # (missing/mistyped fields) raising in the arc_id expression or
            # extract(), a reservation-layer refusal (a lost reserve race, the
            # fail-closed loop emitter before U-HE-29, a holder mismatch), or a
            # malformed head shape (a null accretion map raises AttributeError in
            # the fold -- codex r7 P2). This entry stays queued (already durably
            # restored by _drain_one where a claim was held); the rest still
            # drain (C-HE-04 SS3).
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


def phase_spans(row: dict) -> dict[str, float]:
    """Per-phase seconds from the row's OWN {start,end} pairs -- never from a
    neighbouring row (C-HE-27 §2: an intervening record can be dropped, reordered,
    or written by another lane, so an inter-record delta silently becomes a
    different quantity). An edge-only phase (e.g. the result_capture pair, which
    records single completion timestamps) is recorded but yields no span. A span
    whose end precedes its start is corrupt phase state and fails LOUD -- the edges
    are recorded independently, so a reversed pair is representable on disk, and a
    negative duration flowing into N6 would publish a negative rate (codex r2)."""
    out = {}
    for name, span in (row.get("phases") or {}).items():
        if span.get("start") and span.get("end"):
            secs = (parse_iso(span["end"]) - parse_iso(span["start"])).total_seconds()
            if secs < 0:
                raise AbortError(
                    f"phase {name!r} on arc {row.get('arc_id')!r}: end precedes start "
                    f"({span['end']} < {span['start']}) -- corrupt phase state"
                )
            out[name] = secs
    return out


def n6(rows: list[dict], gate_rows: list[dict]) -> tuple[float | None, float, float]:
    """C-HE-27 §4: problems prevented per hour = COUNT(DISTINCT finding_id last-disposed
    accepted) / sum(verify + edit) hours, read from the durable phases map.

    The numerator's window is the set of arcs that actually CONTRIBUTE denominator
    hours -- an accepted finding from an arc with no measured verify/edit time would
    divide by hours it never spent and inflate N6 (codex U-HE-34 r1/r2; C-HE-27 §4
    "across the window's arcs"). Two downtime buckets feed the third element and NEVER
    the denominator: the verify span of an arc whose ROUND-1 outcomes all terminated
    REVIEWER_UNAVAILABLE (verify is the round-1 window, so only round 1's terminal can
    invalidate it -- a later round's downtime must not erase valid round-1 review), and
    any explicit `verify_unavailable` span. The downtime span carries its own
    timestamps, so the subtraction is INTERVAL arithmetic, not scalar (codex r5): each
    counted phase loses exactly its measured OVERLAP with the downtime window -- an
    outage overlapping edit is removed from edit, one overlapping neither phase
    removes nothing -- and the excluded bucket is the UNION of the excluded-verify
    window and the downtime window, never their sum (codex r3: summing a nested pair
    overstated downtime). Returns None, not 0, when no hours are measured -- an
    absent denominator is not a measured zero."""
    import finding_record as fr

    def interval(r: dict, name: str) -> tuple[datetime, datetime] | None:
        span = (r.get("phases") or {}).get(name) or {}
        if span.get("start") and span.get("end"):
            return (parse_iso(span["start"]), parse_iso(span["end"]))
        return None

    def overlap_s(
        a: tuple[datetime, datetime] | None, b: tuple[datetime, datetime] | None
    ) -> float:
        if a is None or b is None:
            return 0.0
        return max(0.0, (min(a[1], b[1]) - max(a[0], b[0])).total_seconds())

    denom_s = 0.0
    excluded_s = 0.0
    window_arcs = set()
    for r in rows:
        spans = phase_spans(r)
        r1 = [
            o for key, o in (r.get("round_outcomes") or {}).items() if str(key).split("/")[0] == "1"
        ]
        r1_unavailable = bool(r1) and all(o.get("terminal") == "REVIEWER_UNAVAILABLE" for o in r1)
        vu_iv = interval(r, "verify_unavailable")
        vu = spans.get("verify_unavailable", 0.0)
        verify_iv = interval(r, "verify")
        edit_iv = interval(r, "edit")
        contributed = 0.0
        if r1_unavailable:
            # union, not sum: a downtime window nested in the excluded verify span is
            # already inside it
            excluded_s += spans.get("verify", 0.0) + vu - overlap_s(verify_iv, vu_iv)
        else:
            contributed += spans.get("verify", 0.0) - overlap_s(verify_iv, vu_iv)
            excluded_s += vu
        contributed += spans.get("edit", 0.0) - overlap_s(edit_iv, vu_iv)
        denom_s += contributed
        if contributed > 0:
            window_arcs.add(r.get("arc_id"))
    last = fr.reduce_last_by_finding_id(gate_rows)
    accepted = {
        fid
        for fid, r in last.items()
        if r.get("disposition") == "accepted" and r.get("arc_id") in window_arcs
    }
    hours = denom_s / 3600.0
    return (len(accepted) / hours if hours else None), hours, excluded_s


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
        # Two distinct non-exact classes, rendered apart: a `partial-suffix`
        # row's counts and gaps are TRUE measurements of its surviving suffix
        # (a lower bound); an `unknown` row's round-derived numbers may be
        # position-era corruption (refused logs counted, gaps spanning them),
        # so they enter NO round-derived aggregate at all.
        suffix = [r for r in cohort if r.get("round_completeness", "complete") == "partial-suffix"]
        unknown = [
            r
            for r in cohort
            if r.get("round_completeness", "complete") not in ("complete", "partial-suffix")
        ]
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
        allgaps = [g for r in exact + suffix for g in (r.get("round_wall_s") or [])]
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
        if suffix:
            bound = ", ".join(
                f"{r['arc_id']}>={r['review_rounds']}" for r in suffix if r.get("review_rounds")
            )
            print(
                f"  {len(suffix)} row(s) EXCLUDED from the two exact lines above -- only a "
                f"suffix of their logs survives, so their counts are lower bounds ({bound})"
            )
        if unknown:
            names = ", ".join(sorted(r["arc_id"] for r in unknown))
            print(
                f"  {len(unknown)} row(s) of UNKNOWN completeness excluded from ALL "
                f"round-derived aggregates -- their round metrics may be position-era "
                f"corruption, not lower bounds ({names})"
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
        # Same discipline as the lever cohorts above: a lower-bound row
        # (partial-suffix / unknown) must not enter an exact lane median.
        exact_rows = [r for r in cohort if r.get("round_completeness", "complete") == "complete"]
        rounds = [r["review_rounds"] for r in exact_rows if r.get("review_rounds") is not None]
        bounded = len(cohort) - len(exact_rows)
        print(f"-- LANES [{label}] (n={len(cohort)}) " + "-" * 20)
        print(
            f"  review rounds    {statistics.median(rounds):g} (n={len(rounds)}, "
            f"{min(rounds)}-{max(rounds)})"
            if rounds
            else "  review rounds    --"
        )
        if bounded:
            print(f"  {bounded} lower-bound row(s) excluded from the exact line above")
        print()

    # C-HE-27 §4: N6 from the durable phases map + the gate log's dispositions.
    # An absent gate log or an unmeasured denominator prints as "--", never as a
    # zero -- "could not look" must stay distinguishable from "looked, found none".
    if GATE_LOG.exists():
        import finding_record as fr

        n6_val, n6_hours, n6_excluded_s = n6(rows, fr.read_rows(GATE_LOG))
        n6_txt = "-- (no verify/edit spans measured)" if n6_val is None else f"{n6_val:.2f}"
        print(
            f"N6 problems-prevented/hour  {n6_txt}  "
            f"[{n6_hours:.2f}h verify+edit; {n6_excluded_s:.0f}s verify excluded as "
            "REVIEWER_UNAVAILABLE]"
        )
    else:
        print(f"N6 problems-prevented/hour  -- (gate log absent: {GATE_LOG})")
    print()

    # Same exclusion as every round-derived aggregate above: an `unknown` row's
    # gaps may be position-era corruption, not measurements.
    allgaps = [
        g
        for r in rows
        if r.get("round_completeness", "complete") in ("complete", "partial-suffix")
        for g in (r.get("round_wall_s") or [])
    ]
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
    # Manual/historical backfill: no check-then-act bypass at all (codex U-HE-19
    # r1/r2/r3/r4 P2 -- every recheck variant left a window). The backfill RESERVES the
    # arc first: reserve()'s exclusive-create CAS is the fence, so either this command
    # owns the reservation end-to-end or it loses the race loudly and appends nothing.
    # The reservation is minted with the truthful close-time label and terminalized
    # `merged` (append already proved merged_at/merge_sha), leaving an audit record.
    import reservations as rs

    # BEFORE any reservation mutation (codex r7 P1): a premature backfill of a
    # still-open PR must abort with NOTHING minted -- terminalizing first would leave
    # the authoritative reservation falsely `merged` while append() then refuses the
    # unmerged row. Same predicate append() enforces; hoisted to the earliest stage.
    if not row.merged_at or not row.merge_sha:
        raise AbortError(
            f"{row.arc_id}: refusing to backfill an unmerged arc "
            f"(merged_at={row.merged_at!r}, merge_sha={row.merge_sha!r})"
        )
    if row.arc_type_declared_at == "open":
        # One authoritative provenance (codex r7 P2): the backfill's minted
        # reservation is close-declared by definition; an open-time label can only
        # come from the real reservation flow (U-HE-21).
        raise AbortError(
            f"{row.arc_id}: historical backfill declares at close; "
            "--arc-type-declared-at open belongs to the reservation flow"
        )
    cur = rs.current(row.arc_id)
    if cur is None:
        if not row.arc_type:
            raise AbortError(
                f"{row.arc_id}: historical backfill now mints its reservation and "
                "C-HE-26 §1 requires an arc_type -- pass --arc-type (same rule as queue)"
            )
        try:
            rs.reserve(
                row.arc_id,
                lane_id=LANE_ID,
                branch=BACKFILL_BRANCH,
                arc_type=row.arc_type,
                arc_type_declared_at="close",
            )
        except rs.ReservationError as exc:
            raise AbortError(
                f"{row.arc_id}: lost the backfill reservation race ({exc}); the "
                "reserving lane's drain will capture this arc"
            ) from exc
        if row.pr is not None:
            # stamp the PR at mint time (codex r20 P2): a crash between reserve and
            # this line is the only window in which a retry's resume fence sees
            # pr=null and cannot bind the PR -- keep it near-zero, not open-ended
            rs.update_payload(row.arc_id, {"pr": row.pr})
        cur = rs.current(row.arc_id)
        print("note: historical backfill reserved by this lane")
    state, owner = cur[1]["state"], cur[1]["lane_id"]
    if owner == LANE_ID and cur[1].get("branch") != BACKFILL_BRANCH:
        # A NORMAL same-lane reservation is not this command's to consume (codex r9
        # P2): appending here would skip the drain's reservation fold (phases, round
        # outcomes, open-time label) and then deadlock the queued drain's correct row
        # behind the duplicate guard. The queue+drain path owns reserved arcs.
        raise AbortError(
            f"{row.arc_id}: an active reservation exists for this lane's arc "
            f"(state={state!r}) -- capture it through `queue` + `drain` (the drain "
            "folds the reservation); extract-backfill is for reservation-less history"
        )
    if owner == LANE_ID and cur[1].get("branch") == BACKFILL_BRANCH:
        # A lane+branch match alone does not make it THIS invocation's reservation
        # (codex r11 P2): a concurrent/retried backfill in the same worktree could
        # terminalize one reservation and append the other's payload. The recorded
        # pr/arc_type must agree with what THIS invocation extracted.
        res_pr, res_type = cur[1].get("pr"), cur[1].get("arc_type")
        if (res_pr is not None and row.pr is not None and res_pr != row.pr) or (
            row.arc_type and res_type and res_type != row.arc_type
        ):
            raise AbortError(
                f"{row.arc_id}: the existing backfill reservation records "
                f"pr={res_pr!r}/arc_type={res_type!r} but this invocation extracted "
                f"pr={row.pr!r}/arc_type={row.arc_type!r} -- not this command's "
                "reservation to consume"
            )
    if owner == LANE_ID and state in ("pending", "open"):
        # Terminalize BEFORE append (codex U-HE-19 r5 P2): a crash between the two
        # leaves a merged head whose retry falls straight through to append() below via
        # the merged-holder gate -- self-healing, never an open/pr=null wedge deadlocked
        # behind the duplicate guard. The extract() precondition (merged_at/merge_sha)
        # is the C-HE-03 §4 confirmed-merge witness for this flip.
        try:
            if state == "pending":
                rs.open_with_sensor(row.arc_id, LANE_ID)
            if row.pr is not None and cur[1].get("pr") is None:
                rs.update_payload(row.arc_id, {"pr": row.pr})
            rs.transition(row.arc_id, "merged", lane_id=LANE_ID)
        except rs.ReservationError as exc:
            # A concurrent same-worktree retry won a CAS in this sequence (codex r14
            # P3): an expected cooperative loss surfaces as the CLI's clean AbortError
            # semantics, never a raw traceback. The winner completes the backfill.
            raise AbortError(
                f"{row.arc_id}: lost the backfill resume race ({exc}); the winning "
                "invocation completes this backfill"
            ) from exc
        print("note: backfill reservation terminalized merged; appending the row")
    if owner == LANE_ID:
        # Adjudicated reviewer flip (codex r16 vs r18): the row does NOT fold the
        # synthetic backfill reservation's lane_id / sensor -- those would be false
        # derived data measured long after the historical arc ran; C-HE-25's own model
        # is "all additive; historical rows read as null". Only the operator-declared
        # classification is adopted from the minted reservation.
        head = rs.current(row.arc_id)
        if head:
            if not row.arc_type and head[1].get("arc_type"):
                # A crash-retry without --arc-type still records the reservation's
                # close-declared classification (codex r17 P2): the minted reservation
                # is the authoritative carrier; a null row label would misfile a NEW
                # capture into the historical-null cohorts.
                row.arc_type = head[1]["arc_type"]
                row.arc_type_close = head[1]["arc_type"]
                row.arc_type_declared_at = "close"
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
    ex.add_argument(
        "--transcript",
        nargs="+",
        help="the arc's session transcript(s) .jsonl for cost fields (X6e)",
    )
    ex.add_argument("--levers", nargs="*", help="levers live during this arc")
    ex.add_argument("--notes", default="")
    ex.add_argument("--dry-run", action="store_true")
    ex.set_defaults(func=cmd_extract)

    q = sub.add_parser("queue", help="record capture inputs out-of-repo (arc closure)")
    q.add_argument("--pr", type=int, required=True)
    q.add_argument("--arc-id")
    # Required HERE and (since U-HE-19, codex r4/r6) effectively on `extract` too: the
    # backfill now mints its race-fence reservation, whose C-HE-26 §1 label is
    # mandatory -- cmd_extract refuses an unclassified non-dry-run backfill with an
    # instruction to pass --arc-type. Pre-existing unclassified HISTORICAL rows keep
    # their null arc_type (C-HE-25 additive-null reads); only NEW manual captures must
    # declare, at parity with this queue entrance.
    q.add_argument("--arc-type", choices=list(ARC_TYPES), required=True)
    q.add_argument("--arc-type-declared-at", choices=["open", "close"], default="close")
    q.add_argument("--decisions", type=int, required=True, help="independent decision count")
    q.add_argument("--round-logs", nargs="+", help="glob(s) for this arc's round logs")
    q.add_argument(
        "--transcript",
        nargs="+",
        help="the arc's session transcript(s) .jsonl for cost fields (X6e)",
    )
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
