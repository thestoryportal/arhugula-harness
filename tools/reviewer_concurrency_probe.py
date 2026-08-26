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
reserved arc's round budget is spent on measurements.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
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

#: A sample is (wall_s, valid): valid == the call ended with a schema-parsed verdict.
Sample = tuple[float, bool]


def decide(samples: dict[int, list[Sample]], *, min_reps: int = 5) -> tuple[bool, str]:
    """The C-HE-22 pass rule, pure ([LAW:effects-at-boundaries] the verdict is computed
    from samples alone; measuring and recording live in `run`). RED wins on any of:
    missing N=1 baseline, a short series, any invalid call, a median blowup."""
    if 1 not in samples:
        return False, "insufficient: no N=1 baseline series"
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


def _one(channel: str, base: str, env: dict[str, str]) -> Sample:
    """One reviewer call: wall-clock + verdict validity. Exit 0/1 is a schema-parsed
    verdict (C-HE-15); anything else — 2 REVIEWER_UNAVAILABLE, 3 GATE_REFUSED, a timeout —
    is a validity failure. [LAW:no-silent-failure] the failure IS the datum: it is
    recorded as an invalid sample (=> RED via `decide`), never raised, so one bad call
    cannot discard the run's other live samples."""
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            [*CMD[channel], base],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            timeout=CALL_TIMEOUT_S,
        )
        valid = proc.returncode in (0, 1)
    except subprocess.TimeoutExpired:
        valid = False
    return time.monotonic() - t0, valid


def run(
    base: str,
    *,
    channel: str = "codex",
    reps: int = 5,
    ns: tuple[int, ...] = (1, 2, 4),
    one: Callable[[str, str, dict[str, str]], Sample] = _one,
) -> int:
    """Collect reps x N samples per concurrency level, record each as a C-HE-24 row, print
    the per-N table + verdict. Exit 0 GREEN / 1 RED (the CLI contract; the durable record
    is the rows + the §8.1 evidence-log paste)."""
    arc_id, lane_id = rw.env_arc_and_lane()
    binding = rw.code_binding(REPO, base)  # the ONE fixed-diff identity every row carries
    env = probe_env()
    samples: dict[int, list[Sample]] = {n: [] for n in ns}
    for n in ns:
        for rep in range(reps):
            with ThreadPoolExecutor(max_workers=n) as ex:
                results = list(ex.map(lambda _: one(channel, base, env), range(n)))
            for wall, valid in results:
                samples[n].append((wall, valid))
                fr.append_observation(
                    {
                        "location": f"{channel}@N={n}",
                        "observed_evidence": json.dumps(
                            {"wall_s": round(wall, 1), "valid": valid, "n": n, "rep": rep}
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
    for n in ns:
        med = statistics.median(w for w, _ in samples[n])
        all_valid = all(ok for _, ok in samples[n])
        print(f"N={n}: median {med:.0f}s over {len(samples[n])} calls, valid={all_valid}")
    ok, why = decide(samples)
    print(f"{'GREEN' if ok else 'RED'}: {why}")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="main")
    p.add_argument("--channel", choices=tuple(CMD), default="codex")
    p.add_argument("--reps", type=int, default=5)
    a = p.parse_args(argv)
    return run(a.base, channel=a.channel, reps=a.reps)


if __name__ == "__main__":
    sys.exit(main())
