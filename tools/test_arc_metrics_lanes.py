"""U-HE-20: AC#2 (a)/(b) — real subprocess lanes over one shared QUEUE_DIR.

NOT threads (module globals cannot diverge per thread -- a false-GREEN certificate, C8),
NOT multiprocessing fork (fork after a held threading.Lock deadlocks the child). Every
case asserts over the UNION of the lane ledgers: exactly one row per arc_id, and the
C-HE-04 two-state invariant (entry still queued while the row is uncommitted).

Deviations from the plan's inline sketch, each grounded at HEAD (see PR body):
- lane worktrees are FRESH repos with no origin/main (the spec's prescribed shape --
  ``committed_arc_ids()`` returns ``set()`` through the real unreadable-``MERGED_REF``
  path); (vi) ALONE publishes a one-baseline-row committed ledger at origin/main via
  ``_publish_baseline``, because its final legs judge local rows against committed
  content and the tri-state reconciliation refuses to judge unreadable committed
  history (codex U-HE-19 r21 P2);
- the fake ``gh`` returns a 40-char ``mergeCommit.oid`` (``ci_metrics`` refuses short
  SHAs) and a full ``round_snapshot`` (extract reads ``round_log_source`` /
  ``first_round_at`` / ``last_round_at`` unconditionally);
- (ii)'s dead ``.taken`` claim carries ``lane_id`` -- an unstamped claim proves nothing
  and the holder transfer is (correctly) refused;
- (iv)/(v)/(b) assert the drain-side classification MESSAGE as well as the row set:
  ``append()``'s ``_require_reservation_holder`` is a second serial guard, so a
  commented drain-side elif alone still yields zero rows -- the message is what makes
  those mutations killable.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent
BARRIER_TIMEOUT_S = 30.0
LANE_MAIN = "import sys, argparse, arc_metrics as am\nsys.exit(am.drain(argparse.Namespace()))\n"
#: 40-char fake merge SHA: ci_metrics refuses anything shorter (silent-zero guard).
MERGE_SHA = "de" * 20
#: Sibling arc committed at each worktree's origin/main baseline (see _git_init).
BASELINE_ARC = "pr-0"
BASELINE_ROW = json.dumps({"arc_id": BASELINE_ARC, "record_kind": "arc"}, sort_keys=True) + "\n"

FAKE_GH = """#!/usr/bin/env bash
case "$*" in
  *'pr view'*)
    echo '{"additions":1,"deletions":1,"changedFiles":1,"commits":[{"oid":"x"}],\
"createdAt":"2026-08-18T00:00:00Z","mergedAt":"2026-08-18T00:10:00Z",\
"mergeCommit":{"oid":"MERGESHA"},"title":"t"}' ;;
  *'run list'*) echo '[]' ;;
  *) echo '{}' ;;
esac
""".replace("MERGESHA", MERGE_SHA)


def _git_init(wt: Path) -> None:
    """A FRESH git worktree with NO origin/main -- the spec's prescribed shape for
    AC#2 (C-HE-03 Verification: ``committed_arc_ids()`` returns ``set()`` through the
    real unreadable-``MERGED_REF`` path, so nothing releases the entry and a lane that
    crashed on that path would surface through ``_finish``'s termination check)."""
    wt.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(wt)], check=True)
    (wt / ".harness").mkdir()


def _publish_baseline(wt: Path) -> None:
    """(vi) only: give the worktree KNOWN committed history at origin/main -- one
    BASELINE row for a sibling arc. The final (vi) legs judge local rows against
    committed content, and the tri-state reconciliation refuses to judge when
    committed history is unreadable. The baseline cannot be an empty file: ``run()``
    validates non-empty output, so ``git show`` of an empty committed ledger reads
    as unreadable and reconciliation (correctly, fail-safe) holds."""
    (wt / ".harness" / "arc-metrics.jsonl").write_text(BASELINE_ROW)
    subprocess.run(["git", "-C", str(wt), "add", ".harness"], check=True)
    subprocess.run(
        ["git", "-C", str(wt), "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "i"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(wt), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True
    )


def _lane_env(wt: Path, q: Path, lane_id: str, **extra: object) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("ARC_METRICS_")}
    env.update(
        {
            "ARC_METRICS_REPO": str(wt),
            "ARC_METRICS_LEDGER": str(wt / ".harness" / "arc-metrics.jsonl"),
            "ARC_METRICS_QUEUE_DIR": str(q),
            "ARC_METRICS_MERGED_REF": "origin/main",
            "HARNESS_LANE_ID": lane_id,
            "PYTHONPATH": str(TOOLS),
        }
    )
    env.update({k: str(v) for k, v in extra.items()})
    return env


def _spawn(
    wt: Path, q: Path, lane_id: str, barrier: Path | None = None, **extra: object
) -> subprocess.Popen:
    pre = ""
    if barrier is not None:
        pre = (
            "import os, time\n"
            f"_d = time.monotonic() + {BARRIER_TIMEOUT_S}\n"
            f"while not os.path.exists({str(barrier)!r}):\n"
            "    time.sleep(0.01)\n"
            "    assert time.monotonic() < _d, "
            "'rendezvous timeout -- peer leg did not reach the barrier'\n"
        )
    return subprocess.Popen(
        [sys.executable, "-c", pre + LANE_MAIN],
        env=_lane_env(wt, q, lane_id, **extra),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _finish(p: subprocess.Popen, expect_rc: tuple[int, ...] = (0, 1)) -> tuple[str, str]:
    """Reap a lane and VALIDATE its termination: a losing racer must exit through the
    documented outcome classes (0 = drained clean, 1 = kept/outstanding), never a
    traceback (C-HE-04 §1: the losing racer logs and yields; no FileNotFoundError
    escapes drain()). The kill leg passes expect_rc=(137,)."""
    out, err = p.communicate(timeout=60)
    assert p.returncode in expect_rc, f"lane exited {p.returncode}, wanted {expect_rc}: {err}"
    assert "Traceback" not in err, f"a lane propagated instead of yielding: {err}"
    return out, err


def _entry(q: Path, arc: str = "pr-1") -> None:
    (q / f"{arc}.json").write_text(
        json.dumps(
            {
                "pr": 1,
                "arc_id": arc,
                "arc_type": "inventing",
                "decisions": 1,
                "round_snapshot": {
                    "review_rounds": 1,
                    "round_wall_s": [1.0],
                    "p1_rounds": [0],
                    "round_log_source": "test",
                    "first_round_at": "2026-08-18T00:05:00+00:00",
                    "last_round_at": "2026-08-18T00:06:00+00:00",
                },
            }
        )
    )


def _rows(wt: Path) -> list[dict]:
    """The lane's ledger rows, minus the committed baseline row every worktree carries."""
    p = wt / ".harness" / "arc-metrics.jsonl"
    if not p.exists():
        return []
    rows = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]
    return [r for r in rows if r.get("arc_id") != BASELINE_ARC]


def _wait_for(path: Path, timeout: float = BARRIER_TIMEOUT_S) -> None:
    d = time.monotonic() + timeout
    while not path.exists():
        assert time.monotonic() < d, f"timeout waiting for {path.name}"
        time.sleep(0.01)


def _res_cli(q: Path, *args: str) -> str:
    env = {**os.environ, "ARC_METRICS_QUEUE_DIR": str(q), "PYTHONPATH": str(TOOLS)}
    r = subprocess.run(
        [sys.executable, "-m", "reservations", *args],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return r.stdout.strip()


def _reserve(q: Path, arc: str = "pr-1", lane: str = "seed", state: str = "pending") -> None:
    _res_cli(
        q, "reserve", "--arc-id", arc, "--lane-id", lane, "--branch", "b", "--arc-type", "inventing"
    )
    if state == "open":
        _res_cli(q, "transition", "--arc-id", arc, "--to", "open", "--lane-id", lane)


def _show(q: Path, arc: str = "pr-1") -> dict:
    return json.loads(_res_cli(q, "show", "--arc-id", arc))


def _union_ok(a: Path, b: Path, q: Path, arc: str = "pr-1", expect_rows: int = 1) -> dict:
    """expect_rows=2 is (vi)'s transient keep-loudly state ONLY: both copies name the
    same arc_id and the entry is still held -- never two DIFFERENT arcs."""
    rows = _rows(a) + _rows(b)
    assert [r["arc_id"] for r in rows] == [arc] * expect_rows, (
        f"union must hold exactly {expect_rows} row(s): {rows}"
    )
    # C-HE-04 two-state invariant: the row is uncommitted (nothing merged this ledger
    # into origin/main here), so the queue entry MUST still exist -- (a) of the pair.
    assert (q / f"{arc}.json").exists() or (q / f"{arc}.taken").exists()
    return rows[0]


@pytest.fixture
def lanes(tmp_path, monkeypatch):
    q = tmp_path / "queue"
    q.mkdir()
    a, b = tmp_path / "wt-a", tmp_path / "wt-b"
    _git_init(a)
    _git_init(b)
    # extract() shells to gh; stub it via a fake on PATH answering the two drain queries
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "gh").write_text(FAKE_GH)
    (fake / "gh").chmod(0o755)
    monkeypatch.setenv("PATH", f"{fake}:{os.environ['PATH']}")
    return q, a, b, tmp_path


@pytest.mark.parametrize(
    "interleaving",
    [
        "i-both-claim",
        "ii-both-recover",
        "iii-peer-removes-taken",
        "iv-restore-vs-claim",
        "v-abort-vs-claim",
        "vi-killed-after-append",
    ],
)
# mutation-probe(tools/arc_metrics.py): republish/transfer/open-held-elif pins at (iii)/(ii)/(v)
def test_ac2_a_same_instant(lanes, interleaving):
    q, a, b, root = lanes
    hold = root / "hold"
    hold.mkdir()
    barrier = root / ".go"
    _entry(q)

    if interleaving == "i-both-claim":
        _reserve(q)
        pa, pb = _spawn(a, q, "lane-a", barrier), _spawn(b, q, "lane-b", barrier)
        barrier.touch()
        _finish(pa), _finish(pb)
        _union_ok(a, b, q)

    elif interleaving == "ii-both-recover":
        _reserve(q, lane="dead-lane", state="open")
        (q / "pr-1.json").rename(q / "pr-1.taken")
        d = json.loads((q / "pr-1.taken").read_text())
        # a dead claim is transferable only when it PROVABLY belonged to the holder:
        # pid+host say dead, lane_id says which lane (codex U-HE-19 r1 P1). The pid is
        # a REAPED child's -- provably dead on every platform (codex U-HE-20 r2 P3;
        # a fixed sentinel like 999999 can be a live pid where pid_max exceeds it).
        reaped = subprocess.Popen([sys.executable, "-c", "pass"])
        reaped.wait(timeout=30)
        d["_claim"] = {"pid": reaped.pid, "host": socket.gethostname(), "lane_id": "dead-lane"}
        (q / "pr-1.taken").write_text(json.dumps(d))
        # same-instant leg: both lanes judge the same dead .taken recoverable
        pa, pb = _spawn(a, q, "lane-a", barrier), _spawn(b, q, "lane-b", barrier)
        barrier.touch()
        _finish(pa), _finish(pb)
        res = _show(q)
        winner = res["lane_id"]
        assert winner in ("lane-a", "lane-b"), f"holder must transfer off dead-lane: {res}"
        # deterministic completion leg: the claim race may have gone to the non-holder
        # once -- the transferred holder drains again and MUST be the one that appends
        pw = _spawn(a if winner == "lane-a" else b, q, winner)
        _finish(pw)
        row = _union_ok(a, b, q)
        assert row["lane_id"] == winner
        assert _show(q)["lane_id"] == winner

    elif interleaving == "iii-peer-removes-taken":
        _reserve(q)
        pa = _spawn(
            a, q, "lane-a", ARC_METRICS_TEST_HOLD_AFTER="append", ARC_METRICS_TEST_HOLD_DIR=hold
        )
        _wait_for(hold / "append.reached")
        (q / "pr-1.taken").unlink()  # B removes A's .taken under it (E9)
        (hold / "append.go").touch()
        _finish(pa)
        assert (q / "pr-1.json").exists(), "A must re-publish the entry from its in-memory capture"
        _union_ok(a, b, q)

    elif interleaving == "iv-restore-vs-claim":
        _reserve(q)
        pa = _spawn(
            a, q, "lane-a", ARC_METRICS_TEST_HOLD_AFTER="restore", ARC_METRICS_TEST_HOLD_DIR=hold
        )
        _wait_for(hold / "restore.reached")  # A appended + restored; entry is back
        pb = _spawn(b, q, "lane-b")
        out_b, _ = _finish(pb)
        # by the restore hold-point A has already terminalized open->merged, so B's
        # guard is the merged-held-by-other elif; the message witnesses THAT guard
        # (append()'s holder gate is a second serial guard that would mask its removal)
        assert "reservation merged by lane-a" in out_b, out_b
        (hold / "restore.go").touch()
        _finish(pa)
        _union_ok(a, b, q)

    elif interleaving == "v-abort-vs-claim":
        _reserve(q)
        pa = _spawn(
            a,
            q,
            "lane-a",
            ARC_METRICS_TEST_HOLD_AFTER="restore-abort",
            ARC_METRICS_TEST_HOLD_DIR=hold,
            ARC_METRICS_TEST_ABORT_EXTRACT="1",
        )
        _wait_for(hold / "restore-abort.reached")  # A flipped open, aborted, restored
        pb = _spawn(b, q, "lane-b")
        out_b, _ = _finish(pb)
        assert "open reservation held by lane-a" in out_b, out_b
        (hold / "restore-abort.go").touch()
        _finish(pa)
        assert _rows(a) + _rows(b) == [], "nothing may append across the abort"
        assert (q / "pr-1.json").exists(), "the entry stays durable"
        pa2 = _spawn(a, q, "lane-a")  # A (holder) re-drains and appends
        _finish(pa2)
        _union_ok(a, b, q)

    else:  # vi-killed-after-append
        _publish_baseline(a)
        _publish_baseline(b)
        _reserve(q)
        pa = _spawn(a, q, "lane-a", ARC_METRICS_TEST_KILL_AFTER="append")
        _finish(pa, expect_rc=(137,))  # a real death, not an exception
        assert (q / "pr-1.taken").exists(), "the dead lane's claim survives"
        assert [r["arc_id"] for r in _rows(a)] == ["pr-1"], "A appended before dying"
        pb = _spawn(b, q, "lane-b")  # recovers the dead claim, takes the holder, appends
        _finish(pb)
        assert [r["arc_id"] for r in _rows(b)] == ["pr-1"]
        # A resumes while B's row is still uncommitted: the AS-LANDED C-HE-04 SS5
        # (U-HE-19 rev item (vi)/(ix), codex r2 P1) KEEPS the merged-by-other row
        # LOUDLY -- merged state alone does not prove the replacement row exists, and
        # dropping here could discard the only capture. The drop the spec's (vi)
        # sentence names happens at the committed point below (residual routed to
        # U-HE-22 alongside the merged-gate contradiction).
        pa2 = _spawn(a, q, "lane-a")
        out_a2, _ = _finish(pa2)
        assert "local row kept pending reconciliation" in out_a2, out_a2
        assert [r["arc_id"] for r in _rows(a)] == ["pr-1"], "no silent drop, no double-append"
        _union_ok(a, b, q, expect_rows=2)  # transient two-copy state, entry still held
        # Emulate B's PR merging: B's canonical row reaches A's committed history
        # while A's working ledger still carries its stale superseded copy.
        canonical = next(
            ln
            for ln in (b / ".harness" / "arc-metrics.jsonl").read_text().splitlines()
            if json.loads(ln).get("arc_id") == "pr-1"
        )
        led = a / ".harness" / "arc-metrics.jsonl"
        stale = led.read_text()
        led.write_text(BASELINE_ROW + canonical + "\n")
        subprocess.run(["git", "-C", str(a), "add", ".harness"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                str(a),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                "commit",
                "-qm",
                "m",
            ],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(a), "update-ref", "refs/remotes/origin/main", "HEAD"], check=True
        )
        led.write_text(stale)  # working tree back to the stale pre-merge state
        pa3 = _spawn(a, q, "lane-a")  # now the SS5 drop/convergence fires
        _finish(pa3)
        rows_a = _rows(a)
        assert [json.dumps(r, sort_keys=True) for r in rows_a] == [canonical], (
            "A's stale superseded copy must converge to the committed canonical row"
        )
        assert not (q / "pr-1.json").exists() and not (q / "pr-1.taken").exists(), (
            "entry released once the row is in committed history (two-state invariant (b))"
        )


# mutation-probe(tools/arc_metrics.py): comment out the merged-held-by-other elif -> red
def test_ac2_b_cross_latency(lanes):
    """A drains and restores pending merge; B drains the same QUEUE_DIR while A's row is
    unmerged: B MUST NOT re-append (C-HE-03 Verification AC#2(b)). RED against unfixed
    HEAD with no fault injection: committed_arc_ids() == set() through the real path."""
    q, a, b, _root = lanes
    _entry(q)
    _reserve(q)
    pa = _spawn(a, q, "lane-a")
    _finish(pa)
    assert [r["arc_id"] for r in _rows(a)] == ["pr-1"]
    pb = _spawn(b, q, "lane-b")
    out_b, _ = _finish(pb)
    assert _rows(b) == [], "B re-appended across PR-merge latency (X4)"
    assert "reservation merged by lane-a" in out_b, out_b
    _union_ok(a, b, q)
