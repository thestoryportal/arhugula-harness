#!/usr/bin/env python3
"""C-HE-22 reviewer-concurrency probe (U-HE-35, plan S6).

Live probe: >= 5 samples at each of N in {1, 2, 4} concurrent `codex-review` /
`gemini-review` invocations against ONE fixed committed diff. GREEN iff the median
per-call wall-clock at every N is <= 2x the N=1 median AND zero validity failures
(C-HE-15: a validity failure is any call that ends without a schema-parsed verdict);
either violation => RED, throttling assumed present, pilots do not start (C-HE-13 §2
order: probe -> coalescing -> pilots). Every sample lands as a C-HE-24 row
(`producer=reviewer_concurrency_probe`, `finding_type=probe-sample`).

The probe measures the reviewer channel, not the review loop: its child invocations
run under an env stripped of the arc/lane ids (see `probe_env`), so the B-215
admission gate reads them as unreserved (Inactive — its sanctioned path) and no
reserved arc's round budget is spent on measurements. The one-fixed-diff premise is
structural, not checked: children run inside a detached worktree pinned at the
captured head with a frozen base sha (see `_pinned_worktree`), so the reviewed bytes
cannot change while the probe runs.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import signal
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import finding_record as fr
import review_wrapper_common as rw

REPO = Path(__file__).resolve().parent.parent
PRODUCER = "reviewer_concurrency_probe"
#: Per channel, the SAME wrapper invocation the loop's review recipes make
#: ([LAW:one-source-of-truth] the probe measures the real instrument, never a stand-in).
CMD = {
    "codex": ["uv", "run", "python", "tools/codex_review.py", "--base"],
    "gemini": ["uv", "run", "python", "tools/agy_review.py", "--base"],
}
#: Per-call ceiling: the wrapper's own shared deadline plus scheduling slack. A call that
#: outlives it is a validity-failure SAMPLE, never a probe crash (`_one`).
CALL_TIMEOUT_S = rw.TOTAL_BUDGET_S + 60

#: codex_review's documented completion signal: the stderr line `codex-review: <TERMINAL>`.
#: Only a schema-parsed verdict prints a bare APPROVE/BLOCK (REVIEWER_UNAVAILABLE and
#: GATE_REFUSED carry a parenthesized tail; an uncaught crash prints no such line), so this
#: match — never the exit code, which an uncaught exception can also produce as 1 — is the
#: C-HE-15 validity fact (codex r1 P1).
_CODEX_TERMINAL_RE = re.compile(r"^codex-review: (?:APPROVE|BLOCK)(?: \[source: [^]]+\])?$", re.M)

#: A sample is (wall_s, valid): valid == the call ended with a schema-parsed verdict.
Sample = tuple[float, bool]


class _LiveGroups:
    """The single owner of the live reviewer process-group ids AND of the terminating
    flag ([LAW:no-shared-mutable-globals] worker threads register/deregister, the run
    edge and its signal handlers terminate — nothing else touches either). Exists so a
    SIGTERM/SIGINT cannot orphan paid reviewer trees, and so killing them unblocks any
    worker still parked in communicate() instead of waiting out the per-call timeout
    (codex r5 P2). Termination and registration share ONE lock (codex r6 P2): a worker
    between Popen and `add` observes the flag inside `add` and owns the kill of its own
    just-spawned group, so no group can slip past `begin_termination`'s snapshot."""

    def __init__(self) -> None:
        # RLock, not Lock (codex r10 P2): the signal handler runs ON the main thread and
        # may interrupt it INSIDE a locked section (kill_all/reset/add) — a non-reentrant
        # lock would self-deadlock before SystemExit and defeat the cleanup guarantee.
        # Same-thread reentrancy is exactly the signal-interrupts-critical-section case.
        self._lock = threading.RLock()
        self._pgids: set[int] = set()
        self._terminating = False

    @property
    def terminating(self) -> bool:
        with self._lock:
            return self._terminating

    def add(self, pgid: int) -> bool:
        """Register a live group. False once termination began — the refused caller
        must kill the group it just spawned (the handler's snapshot cannot see it)."""
        with self._lock:
            if self._terminating:
                return False
            self._pgids.add(pgid)
            return True

    def discard(self, pgid: int) -> None:
        with self._lock:
            self._pgids.discard(pgid)

    def begin_termination(self) -> None:
        """Refuse all future registrations, then kill everything registered so far."""
        with self._lock:
            self._terminating = True
        self.kill_all()

    def reset(self) -> None:
        """Re-arm for the next run (the flag must not poison a later run in-process)."""
        with self._lock:
            self._terminating = False

    def kill_all(self) -> None:
        """TERM every live group (cooperative — each wrapper tears down its own nested
        vendor group), then SIGKILL whatever outlives the grace."""
        with self._lock:
            pgids, self._pgids = tuple(self._pgids), set()
        for pgid in pgids:
            _signal_group(pgid, signal.SIGTERM)
        deadline = time.monotonic() + TERM_GRACE_S
        live = set(pgids)
        while live and time.monotonic() < deadline:
            live = {p for p in live if _group_alive(p)}
            if live:
                time.sleep(0.05)
        for pgid in live:
            _signal_group(pgid, signal.SIGKILL)


LIVE_GROUPS = _LiveGroups()


def decide(
    samples: dict[int, list[Sample]], *, min_reps: int = 5, required: tuple[int, ...] = (1, 2, 4)
) -> tuple[bool, str]:
    """The C-HE-22 pass rule, pure ([LAW:effects-at-boundaries] the verdict is computed
    from samples alone; measuring and recording live in `run`). RED wins on any of:
    a missing required series (the contract names {1,2,4} — five N=1 samples alone
    certify nothing, codex r4 P3), a short series, any invalid call, a median blowup."""
    for n in required:
        if n not in samples:
            return False, f"insufficient: no N={n} series (contract requires N in {required})"
    for n in sorted(samples):
        if len(samples[n]) < min_reps:
            return False, f"insufficient reps at N={n} ({len(samples[n])} < {min_reps})"
    if any(not ok for series in samples.values() for _, ok in series):
        return False, "validity failure observed (REVIEWER_UNAVAILABLE / unparsed verdict)"
    base = statistics.median(w for w, _ in samples[1])
    for n in sorted(samples):
        med = statistics.median(w for w, _ in samples[n])
        if med > 2 * base:
            return False, f"wall-clock: median at N={n} is {med:.0f}s > 2x N=1 median {base:.0f}s"
    return True, f"no throttling signal at N<={max(samples)}"


def probe_env() -> dict[str, str]:
    """The child-reviewer environment: the session env MINUS the arc/lane ids.

    [LAW:single-enforcer] the probe's gate posture is set here and nowhere else: without
    HARNESS_ARC_ID the child wrapper falls back to an unreserved `branch-*` id, so the
    B-215 admission gate reads Inactive (its sanctioned unreserved path). Probe calls are
    measurements, not review-loop rounds — inheriting the session's reserved arc id would
    spend that arc's round budget and land every measurement on its reservation."""
    return {k: v for k, v in os.environ.items() if k not in ("HARNESS_ARC_ID", "HARNESS_LANE_ID")}


def _codex_valid(stderr: str) -> bool:
    """codex has no envelope sink; its machine seam is the stderr completion line."""
    return _CODEX_TERMINAL_RE.search(stderr) is not None


def _gemini_valid(sink: Path) -> bool:
    """gemini's machine seam is its `--outcome-json` terminal envelope (the same file the
    D-C failover consumes): valid iff it parses and names a verdict terminal. A missing or
    unparseable envelope — the wrapper crashed, or refused the sink — is invalid."""
    try:
        return json.loads(sink.read_text())["terminal"] in ("APPROVE", "BLOCK")
    except (OSError, ValueError, KeyError, TypeError):
        # TypeError: a syntactically valid but wrong-shaped body (`null`, `[]`) has no
        # ["terminal"] to subscript — the same invalid-envelope fact (codex r7 P3)
        return False


#: Cooperative-stop grace: how long a TERMed wrapper gets to tear down its NESTED vendor
#: group (run_bounded spawns the vendor CLI in its own session, so only the wrapper can
#: kill it — codex r8 P2) before the probe SIGKILLs the wrapper group anyway.
TERM_GRACE_S = 10.0


def _signal_group(pgid: int, sig: int) -> None:
    """Idempotent group signal: the group already being gone is the goal state."""
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        pass


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def _stop_tree(proc: subprocess.Popen[str]) -> None:
    """Cooperative-then-forced stop of a wrapper tree (codex r8 P2): SIGTERM first, so
    the wrapper's own TerminationRequested path (both wrappers install it) unwinds
    through run_bounded and terminates the nested vendor group only IT can see; SIGKILL
    after the grace covers a wrapper too hung to clean up (and only then can the vendor
    be orphaned — a corner no outside kill can close, since the vendor's group id lives
    solely in the hung wrapper)."""
    _signal_group(proc.pid, signal.SIGTERM)
    try:
        proc.communicate(timeout=TERM_GRACE_S)
    except subprocess.TimeoutExpired:
        _signal_group(proc.pid, signal.SIGKILL)
        proc.communicate()  # reap; the group is dead, this cannot block


class PinError(RuntimeError):
    """The pinned worktree could not be created — the probe cannot measure anything.
    `run` converts this into a durable RED probe-result row (a crash with no record
    would leave `pilot-gate-check` reading absent-or-stale — merge-gate concurrency P2)."""


@contextlib.contextmanager
def _pinned_worktree(head_sha: str):
    """A detached worktree at the probed commit — the one-fixed-diff premise made
    STRUCTURAL ([LAW:types-are-the-program] at process level, codex r7 P2): children
    review a checkout whose HEAD cannot move, so no ref-snapshot arithmetic exists to
    race (the r2/r3/r5/r7 escalation on drift windows ends by subtraction, per the
    defect-class-preflight arms-race rule — every window came from checking a mutable
    ref this pin makes immutable). The venv is pre-warmed OUTSIDE any measured call so
    the first sample does not pay the sync ([[ephemeral-worktree-for-git-automation]]:
    detached ephemeral worktrees are the sanctioned automation shape)."""
    with tempfile.TemporaryDirectory(prefix="reviewer-concurrency-probe-") as td:
        # the basename rides the tempdir's OWN unique suffix (merge-gate concurrency
        # P2): git derives the shared `.git/worktrees/<id>/` admin dir from the
        # basename, and a fixed literal ("pinned") lets two CONCURRENT probe runs race
        # git's sequential collision-avoidance — one loses fatally and leaves partial
        # admin state in the shared repo
        workdir = Path(td) / f"pin-{Path(td).name.removeprefix('reviewer-concurrency-probe-')}"
        try:
            subprocess.run(
                ["git", "-C", str(REPO), "worktree", "add", "--detach", str(workdir), head_sha],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            # best-effort prune of any partial admin state the failed add left behind,
            # then surface typed — run() records the durable RED result row
            subprocess.run(["git", "-C", str(REPO), "worktree", "prune"], capture_output=True)
            raise PinError(f"git worktree add failed: {exc.stderr.strip()}") from exc
        try:
            # the pre-warm joins the SAME typed conversion as the add (merge-gate
            # concurrency r2 P2): its CalledProcessError would otherwise escape run()'s
            # `except PinError` and crash recordless — the exact failure PinError closes.
            # Scoped to the pre-warm alone, so a with-body exception is never mislabeled.
            try:
                subprocess.run(
                    ["uv", "run", "python", "-c", ""],
                    cwd=workdir,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as exc:
                raise PinError(f"worktree venv pre-warm failed: {exc.stderr.strip()}") from exc
            yield workdir
        finally:
            rm = subprocess.run(
                ["git", "-C", str(REPO), "worktree", "remove", "--force", str(workdir)],
                capture_output=True,
                text=True,
            )
            if rm.returncode != 0:
                # loud, never silent: the tempdir still deletes the files, but git keeps
                # a stale registration until pruned
                print(
                    f"warning: pinned worktree not removed ({rm.stderr.strip()}); "
                    "run `git worktree prune`",
                    file=sys.stderr,
                )


def _one(channel: str, base: str, env: dict[str, str], scratch: Path, workdir: Path) -> Sample:
    """One reviewer call, run inside the pinned worktree (`workdir`) against the frozen
    `base` sha. Validity is read from the channel's own machine seam (never the exit
    code, which an uncaught wrapper exception can alias to a BLOCK — codex r1 P1):
    codex's stderr completion line, gemini's outcome envelope. A timeout, crash, spawn
    failure, REVIEWER_UNAVAILABLE, or GATE_REFUSED all read invalid.
    [LAW:no-silent-failure] the failure IS the datum: it is recorded as an invalid
    sample (=> RED via `decide`), never raised, so one bad call cannot discard the
    run's other live samples."""
    with tempfile.NamedTemporaryFile(dir=scratch, suffix=".json", delete=True) as tf:
        sink = Path(tf.name)  # a fresh non-existent path: agy's O_EXCL sink refuses reuse
    argv = [*CMD[channel], base]
    if channel == "gemini":
        argv += ["--outcome-json", str(sink)]
    if LIVE_GROUPS.terminating:
        return 0.0, False  # termination began before this worker spawned: no new spend
    t0 = time.monotonic()
    try:
        # its own session => the pid IS the process-group id, so any escape path can
        # kill the WHOLE reviewer tree (uv -> python -> vendor CLI descendants), not
        # just the immediate launcher (codex r4 P2).
        proc = subprocess.Popen(
            argv,
            cwd=workdir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
    except OSError:
        # the SPAWN failed (fork/exec resource exhaustion under the very concurrency
        # being probed) — exactly a validity failure, not a probe crash (codex r3 P2):
        # letting it escape the executor would abort the run with no RED and no record.
        return time.monotonic() - t0, False
    valid = False
    try:
        # registration refused = termination began between Popen and add: this group is
        # OURS to kill (the handler's snapshot cannot see it, codex r6 P2) — handled by
        # the finally below, the ONE place a live child can never escape (codex r7 P2:
        # a communicate()/killpg failure must not discard a still-running group).
        if LIVE_GROUPS.add(proc.pid):
            try:
                _out, err = proc.communicate(timeout=CALL_TIMEOUT_S)
                valid = _codex_valid(err) if channel == "codex" else _gemini_valid(sink)
            except subprocess.TimeoutExpired:
                pass  # the finally kills the tree; the sample stays invalid
    finally:
        if proc.poll() is None:  # ANY escape path with the child alive: no orphan
            _stop_tree(proc)
        LIVE_GROUPS.discard(proc.pid)
    return time.monotonic() - t0, valid


def run(
    base: str,
    *,
    channel: str = "codex",
    reps: int = 5,
    ns: tuple[int, ...] = (1, 2, 4),
    one: Callable[[str, str, dict[str, str], Path, Path], Sample] = _one,
) -> int:
    """Collect reps x N samples per concurrency level (reps >= 1; the CLI boundary refuses
    less), record each as a C-HE-24 row, print the per-N table + verdict. Exit 0 GREEN /
    1 RED (the CLI contract; the durable record is the rows + the §8.1 evidence-log
    paste)."""
    arc_id, lane_id = rw.env_arc_and_lane()
    binding = rw.code_binding(REPO, base)  # the ONE fixed-diff identity every row carries
    env = probe_env()
    samples: dict[int, list[Sample]] = {n: [] for n in ns}

    # a SIGTERM/SIGINT mid-run must not orphan paid reviewer trees (codex r5 P2): the
    # handler kills every live group FIRST — which also unblocks any worker parked in
    # communicate() so executor shutdown does not wait out the per-call timeout — then
    # terminates; the finally covers the non-signal exits.
    def _terminate(signum: int, frame: object) -> None:
        LIVE_GROUPS.begin_termination()  # refuse new registrations, then kill the live
        raise SystemExit(128 + signum)

    previous = {s: signal.signal(s, _terminate) for s in (signal.SIGTERM, signal.SIGINT)}
    pin_failure: PinError | None = None
    try:
        with _pinned_worktree(binding["head_sha"]) as workdir:
            # sinks live beside (not inside) the pinned worktree: agy refuses an
            # --outcome-json path inside its own repo
            scratch = workdir.parent
            for n in ns:
                for rep in range(reps):
                    # each completed call is recorded AS IT FINISHES (codex r9 P2): a
                    # worker that raises, or a signal landing mid-batch, must not
                    # discard the paid samples that already completed — as_completed
                    # narrows the loss window to results not yet iterated. A worker
                    # exception is collected and re-raised AFTER the batch's completed
                    # samples are durable ([LAW:no-silent-failure] the bug still
                    # surfaces; the terminal result row is then absent = not-run).
                    errors: list[BaseException] = []
                    with ThreadPoolExecutor(max_workers=n) as ex:
                        futures = [
                            ex.submit(one, channel, binding["base_sha"], env, scratch, workdir)
                            for _ in range(n)
                        ]
                        for fut in as_completed(futures):
                            try:
                                wall, valid = fut.result()
                            except Exception as exc:
                                errors.append(exc)
                                continue
                            samples[n].append((wall, valid))
                            fr.append_observation(
                                {
                                    "location": f"{channel}@N={n}",
                                    "observed_evidence": json.dumps(
                                        {
                                            "wall_s": round(wall, 1),
                                            "valid": valid,
                                            "n": n,
                                            "rep": rep,
                                        }
                                    ),
                                    "expected_contract": "C-HE-22",
                                    "severity": "info",
                                    "finding_type": "probe-sample",
                                    "lineage_claim": "measured",
                                    "producer": PRODUCER,
                                },
                                fr.Envelope(
                                    record_kind="finding",
                                    ts=fr.now_iso(),
                                    arc_id=arc_id,
                                    lane_id=lane_id,
                                    head_sha=binding["head_sha"],
                                    base_sha=binding["base_sha"],
                                    diff_digest=binding["diff_digest"],
                                    round_n=rep,
                                ),
                            )
                    if errors:
                        raise errors[0]
    except PinError as exc:
        # no worktree, no measurement — but a crash with NO durable record would leave
        # pilot-gate-check reading absent-or-stale (merge-gate concurrency P2): fall
        # through to the terminal result row with a RED verdict instead
        pin_failure = exc
    finally:
        # non-signal exits (normal completion, an exception): reap anything still
        # registered, re-arm the flag for a later run in this process, then restore
        # the inherited handlers
        LIVE_GROUPS.kill_all()
        LIVE_GROUPS.reset()
        for s, h in previous.items():
            signal.signal(s, h)
    medians = {n: statistics.median(w for w, _ in samples[n]) for n in ns if samples[n]}
    for n, med in medians.items():
        all_valid = all(ok for _, ok in samples[n])
        print(f"N={n}: median {med:.0f}s over {len(samples[n])} calls, valid={all_valid}")
    if pin_failure is not None:
        ok, why = False, f"pinned worktree unavailable ({pin_failure}); no calls were made"
    else:
        ok, why = decide(samples)
    # the durable TERMINAL record (codex r4 P2): §8.1's "result row required before
    # pilots" needs a row that exists only when a run actually completed — undelimited
    # probe-sample rows cannot carry that fact, and a process killed mid-sampling
    # leaves no result row (absence = not-run). Location differs from the per-sample
    # `<channel>@N=<n>` locations, so its finding_id lineage is its own.
    fr.append_observation(
        {
            "location": channel,
            "observed_evidence": json.dumps(
                {
                    "verdict": "GREEN" if ok else "RED",
                    "why": why,
                    "medians_s": {str(n): round(m, 1) for n, m in medians.items()},
                    "counts": {str(n): len(samples[n]) for n in ns},
                }
            ),
            "expected_contract": "C-HE-22",
            "severity": "info",
            "finding_type": "probe-result",
            "lineage_claim": "measured",
            "producer": PRODUCER,
        },
        fr.Envelope(
            record_kind="finding",
            ts=fr.now_iso(),
            arc_id=arc_id,
            lane_id=lane_id,
            head_sha=binding["head_sha"],
            base_sha=binding["base_sha"],
            diff_digest=binding["diff_digest"],
            round_n=None,
        ),
    )
    print(f"{'GREEN' if ok else 'RED'}: {why}")
    return 0 if ok else 1


def _at_least_one(text: str) -> int:
    """CLI checkpoint for --reps ([LAW:parse-dont-validate]): a zero/negative count would
    leave every series empty and crash the median print before decide could report RED."""
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError(f"--reps must be >= 1, got {value}")
    return value


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="main")
    p.add_argument("--channel", choices=tuple(CMD), default="codex")
    p.add_argument("--reps", type=_at_least_one, default=5)
    a = p.parse_args(argv)
    return run(a.base, channel=a.channel, reps=a.reps)


if __name__ == "__main__":
    sys.exit(main())
