#!/usr/bin/env python3
"""C-HE-13 §1-§3 — the mechanical pilot gate and the pilot report.

`gate()` refuses to start a pilot until every §8.1 manifest row tagged `phase0` PASSES at
the current HEAD; a skip-marked row counts as NOT passed (C-HE-13 §1). A pilot run against
unfixed state produces contaminated friction signal, which is why this is a gate rather
than prose ordering.

`report(run_id)` computes the §3 success iff-clause across the three stores. A pilot run
counts as successful iff:

  (a) every lane's arc landed through the merge door — reservation `merged`, and no
      `BASE_TOCTOU` first-parent detection names it;
  (b) the union ledger satisfies the C-HE-03/04 invariants;
  (c) no outstanding HITL escalation carries a `cause_signature` prefixed `merge-door-`
      or `reservation-` (coordination-caused).

**What clause (b) evaluates, and what it does not.** Read-only over the stores, this
module checks the two C-HE-03/04 invariants that are observable after the fact: at most
one union-ledger row per pilot `arc_id` (C-HE-03 "at most one row for that `arc_id` ever
reaches merged history"), and the C-HE-04 post-drain exclusive-or — for each arc, either
its queue entry is still present and its row is not yet in committed history, or the row
is committed and the entry released, never both and never neither. The remaining
invariants of those contracts are properties of the WRITE paths ("no mutation by rename or
replace", "no TTL reclaim", "no `FileNotFoundError` escapes `drain()`"), which no
post-hoc read of the stores can witness; they are covered by the phase0 manifest rows that
`gate()` requires green before a pilot may start, and this report does not restate them.

A held drain is NOT a violation: an arc whose entry is still queued and whose row is not
yet committed is the invariant's own first branch. `report()` distinguishes that from a
real breach so an operator can tell "not folded yet" from "both states at once".
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lanes_verify as lv
from loop_cost_baseline import parse_loop_row

REPO = Path(__file__).resolve().parent.parent

#: C-HE-13 §3: an outstanding HITL escalation under one of these cause prefixes is
#: coordination-caused and fails the pilot. The spec's reference-machine clause requires an
#: ENVIRONMENTAL failure never to be recorded under them, so the prefix is the discriminator.
COORDINATION_CAUSES = ("merge-door-", "reservation-")

#: Both raise sites write this producer, with DIFFERENT arc ids — see `toctou_keys`.
TOCTOU_PRODUCER = "BASE_TOCTOU"

#: C-HE-13 §3 defines a pilot as a run "at 3–4 lanes". A one- or two-lane run is not a
#: pilot at all, so it cannot count toward the ≥ 3 pilots that gate follow-on orchestration.
PILOT_LANES = range(3, 5)


class PilotError(RuntimeError):
    """A pilot question that could not be answered. Never a FAIL verdict: FAIL is a
    measured outcome, and reporting one for a store this tool could not read would be an
    answer-shaped void ([LAW:no-silent-failure])."""


# ── C-HE-13 §1: the gate ──────────────────────────────────────────────────────


def phase0_results() -> list[lv.Result]:
    """Run every phase0 manifest row at the current HEAD (effect; edge of the module)."""
    return [lv.run_row(r) for r in lv.phase0_rows()]


def gate(results: list[lv.Result]) -> tuple[int, str]:
    """C-HE-13 §1 as `(exit code, message)`, pure over the results.

    The VERDICT is `lanes_verify.phase0_verdict` — the same reduction `just
    lanes-phase0-check` exits on, so the runner and the recipe can never disagree about
    what "phase0 green" means ([LAW:single-enforcer]). This function only NAMES the first
    row that is not a pass; it owns no pass/fail rule of its own, which is why a `skip`
    counts as RED here without this file restating that rule.
    """
    rc = lv.phase0_verdict(results)
    if rc == 0:
        return 0, f"phase0 GREEN ({len(results)} rows)"
    bad = next(r for r in results if r.status != "pass")
    return rc, f"phase0 RED: {bad.row.contract} {bad.row.artifact} — {bad.status}: {bad.reason}"


# ── C-HE-13 §3: the report ────────────────────────────────────────────────────


@dataclass(frozen=True)
class Stores:
    """The three stores' contents as plain data, so `evaluate` is pure over them and the
    §3 iff-clause is witnessed without mocking a filesystem ([LAW:effects-at-boundaries]).

    """

    arcs: list[dict]
    gate_rows: list[dict]
    loop_rows: list[dict]
    #: arc_ids of every row on MERGED history — a LIST, because the C-HE-03 invariant is
    #: "at most one row for that arc_id ever reaches merged history" and a set cannot
    #: express the duplicate it forbids. The worktree ledger is NOT this: a topic-branch
    #: row is not merged history (codex r1 P2).
    merged_ledger_arc_ids: list[str]
    queued_arc_ids: set[str]


def door_landing_violations(arcs: list[dict]) -> list[str]:
    """Clause (a) in full: `merged` AND landed THROUGH THE MERGE DOOR.

    Reservation state alone is not that proof. `reservations.reconcile()` flips an
    externally-merged PR to `merged` from `gh` ground truth without ever setting
    `merge_sha` (C-HE-03 §5), so a lane that bypassed the door — a hand `gh pr merge`,
    say — would otherwise satisfy the clause the door exists to enforce. The door records
    `merge_sha` on its own landing path, so its presence is the discriminator; its absence
    also strips `toctou_keys` of the `merge-<sha12>` key, which is the second reason a
    door-less landing must not read as clean (codex r1 P2 on this arc).
    """
    out = []
    for a in arcs:
        if a["state"] != "merged":
            out.append(f"{a['arc_id']} is {a['state']}, not merged")
        elif not a.get("merge_sha"):
            out.append(
                f"{a['arc_id']} is merged with no door-recorded merge_sha — not proof of "
                "a merge-door landing (reconcile() flips on gh ground truth alone)"
            )
    return out


def toctou_keys(arcs: list[dict]) -> set[str]:
    """Every arc id under which a `BASE_TOCTOU` row for these arcs can appear.

    Two raise sites, two shapes, and reading only one makes the check vacuous for the
    other's detections: the merge door emits the arc's OWN id
    (`merge_door._emit_gate(gate="BASE_TOCTOU", arc_id=arc_id)`), while the CI re-check
    emits `merge-<sha12>` (`codex_context_guard.check_base_toctou`). The door's is the
    immediate in-flight detection, so dropping it would be the more costly miss.
    """
    keys = {a["arc_id"] for a in arcs}
    keys |= {f"merge-{a['merge_sha'][:12]}" for a in arcs if a.get("merge_sha")}
    return keys


def coordination_hil(loop_rows: list[dict], arc_ids: set[str]) -> tuple[list[dict], list[dict]]:
    """Clause (c) as `(every occurrence, the subset still outstanding)`.

    C-HE-13 §3 is written as "no HITL escalation carries a `cause_signature` prefixed
    `merge-door-` or `reservation-`" — it is about whether one OCCURRED, not about whether
    one remains open. A pilot that needed operator recovery to clear a coordination
    escalation still hit coordination pain, which is the whole signal §3 collects, so the
    verdict keys on the first element; the second is reported detail (codex r1 P2).

    Attribution is by ARC ID, taken from the detail's leading token — every merge-door
    escalation and every `defer.sh` row writes `<arc-id> — …`. A timestamp window would
    miss precisely the escalations that fire AFTER the `merged` flip stamps
    `transitioned_at`: the door holds its lease past that point, and its post-merge CI and
    BASE_TOCTOU rows land inside the hold.

    Rows reduce last-write-wins per item, keyed on that arc-id token — the identity
    `branch_hygiene_batch.Deferral.item_id` already uses, so a RESOLVED-HIL clears what
    the operator's resolve flow clears. Narrowing named: two concurrently outstanding
    escalations for ONE arc reduce to the later, which is the existing reducer's
    semantics rather than a new rule this module invents.
    """
    occurred: list[dict] = []
    pending: dict[str, dict] = {}
    for row in loop_rows:
        token = (row["detail"].split() or [""])[0]
        if token not in arc_ids:
            continue
        if row["kind"] == "DEFERRED-HIL":
            pending[token] = row
            if row["cause"].startswith(COORDINATION_CAUSES):
                occurred.append(row)
        elif row["kind"] == "RESOLVED-HIL":
            pending.pop(token, None)
    still_open = [r for r in pending.values() if r["cause"].startswith(COORDINATION_CAUSES)]
    return occurred, still_open


def lane_violations(arcs: list[dict]) -> list[str]:
    """C-HE-13 §3 defines a pilot as a run at 3–4 lanes; a run outside that is not a pilot
    and must not count toward the ≥ 3 that gate follow-on orchestration (codex r1 P2)."""
    lanes = {a["lane_id"] for a in arcs}
    if len(lanes) in PILOT_LANES:
        return []
    return [
        f"{len(lanes)} distinct lane(s) ({', '.join(sorted(lanes))}) — C-HE-13 §3 pilots "
        f"run at {PILOT_LANES.start}-{PILOT_LANES.stop - 1} lanes"
    ]


def ledger_invariants(stores: Stores) -> list[str]:
    """Clause (b): the C-HE-03/04 invariants observable read-only, as violation strings.

    An empty list is the clause satisfied. Each violation names the arc and the shape, so
    the operator never has to re-derive which invariant broke.
    """
    violations: list[str] = []
    for arc in stores.arcs:
        arc_id = arc["arc_id"]
        rows = stores.merged_ledger_arc_ids.count(arc_id)
        if rows > 1:
            violations.append(
                f"C-HE-03: {arc_id} has {rows} union-ledger rows; at most one may reach "
                "merged history"
            )
        queued = arc_id in stores.queued_arc_ids
        committed = arc_id in stores.merged_ledger_arc_ids
        if queued and committed:
            violations.append(
                f"C-HE-04: {arc_id} is BOTH queued and in committed history; the "
                "post-drain invariant admits exactly one"
            )
        elif not queued and not committed:
            violations.append(
                f"C-HE-04: {arc_id} has neither a queue entry nor a committed row; its "
                "capture is unaccounted for"
            )
    return violations


def friction(loop_rows: list[dict], arcs: list[dict]) -> list[str]:
    """The §3 organic-pain input: every cause_signature this pilot's lanes emitted.

    A REPORTING field only — `pass` is computed from arc-attributed evidence alone, so
    nothing here can flip a verdict. Deliberately wider than the pass/fail set: rows like
    the merge door's lease-yield NOTIFY carry no arc id in their detail, so arc attribution
    alone would silently drop real friction.

    The lane half is bounded BELOW (the earliest `reserved_at`) and deliberately not
    above. An upper bound at the latest `transitioned_at` is stamped at the merged flip,
    while the door then holds its lease through post-merge CI and the terminating refresh
    — so exactly the arcless post-merge NOTIFY rows would be dropped, undercounting the
    recurring pain that gates follow-on orchestration (codex r1 P2). The residual is the
    opposite error: a later arc on the same lane can contribute a cause. Over-counting a
    REPORTING field is recoverable by reading it; under-counting the organic-pain bar is
    not.
    """
    arc_ids = {a["arc_id"] for a in arcs}
    lanes = {a["lane_id"] for a in arcs}
    t0 = min((a["reserved_at"] for a in arcs), default="")
    causes: set[str] = set()
    for row in loop_rows:
        token = (row["detail"].split() or [""])[0]
        windowed = row["lane"] in lanes and row["ts"] >= t0
        if (token in arc_ids or windowed) and row["cause"] not in ("", "-"):
            causes.add(row["cause"])
    return sorted(causes)


def evaluate(run_id: str, stores: Stores) -> dict:
    """The §3 iff-clause, pure over `stores`.

    Every clause is computed unconditionally and reported as a value, so a reader can see
    WHICH clause failed rather than one collapsed boolean ([LAW:dataflow-not-control-flow]).
    """
    arcs = stores.arcs
    keys = toctou_keys(arcs)
    toctou = [
        r
        for r in stores.gate_rows
        if r.get("producer") == TOCTOU_PRODUCER and r.get("arc_id") in keys
    ]
    hil, still_open = coordination_hil(stores.loop_rows, {a["arc_id"] for a in arcs})
    landing = door_landing_violations(arcs)
    lanes = lane_violations(arcs)
    violations = ledger_invariants(stores)
    unfolded = sorted(
        a["arc_id"]
        for a in arcs
        if a["arc_id"] in stores.queued_arc_ids and a["arc_id"] not in stores.merged_ledger_arc_ids
    )
    return {
        "run_id": run_id,
        "arcs": sorted(a["arc_id"] for a in arcs),
        "lanes": sorted({a["lane_id"] for a in arcs}),
        "door_landing_violations": landing,
        "lane_violations": lanes,
        "base_toctou": len(toctou),
        "ledger_invariant_violations": violations,
        "coordination_hil": [f"{r['cause']}: {r['detail'][:80]}" for r in hil],
        "coordination_hil_still_outstanding": len(still_open),
        "rows_not_yet_folded": unfolded,
        "friction": friction(stores.loop_rows, arcs),
        "pass": not (landing or lanes or toctou or violations or hil),
    }


def recurring(per_pilot: dict[str, set[str]], *, severe: set[str]) -> set[str]:
    """C-HE-13 §3: a `cause_signature` in >= 2 of the >= 3 pilots, OR one the operator
    rates independently severe. The single-severe clause is load-bearing — at n=3 a
    40%-incidence source registers twice with P ~ 0.35."""
    counts: dict[str, int] = {}
    for sigs in per_pilot.values():
        for s in sigs:
            counts[s] = counts.get(s, 0) + 1
    return {s for s, n in counts.items() if n >= 2} | set(severe)


# ── store gathering (the edges) ───────────────────────────────────────────────


def _pilot_arcs(run_id: str) -> list[dict]:
    """Reservation heads carrying this `pilot_run_id`.

    Refusal semantics mirror `codex_context_guard._reservation_heads`, the store's other
    full scan: a genuinely absent store means "no reservations yet", but a store path that
    is not a directory is a containment breach and refuses rather than reading as empty.
    Not imported from there: that helper is private to the CI guard's dispatch layer, and
    binding a read-only report to it would couple this tool to that layer's finding model.
    """
    import reservations as rs

    root = rs.reservations_root()
    if not root.exists():
        return []
    if not root.is_dir():
        raise PilotError(f"reservations root {root} is not a directory — refused")
    arcs = []
    for entry in sorted(root.iterdir()):
        if entry.name.startswith(".") or not entry.is_dir():
            continue
        cur = rs.current(entry.name)
        if cur and cur[1].get("pilot_run_id") == run_id:
            arcs.append(cur[1])
    return arcs


def _loop_rows() -> list[dict]:
    """Every parsed row of the shared ledger. An unreadable or absent ledger RAISES: a
    pilot whose escalations cannot be read has an unanswerable clause (c), and an empty
    list would render that as "no escalations" ([LAW:no-silent-failure])."""
    import subprocess

    proc = subprocess.run(
        [
            "bash",
            "-c",
            "source tools/hooks/lib.sh; source tools/hooks/loop_lib.sh; loop_status_path",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    path = proc.stdout.strip()
    if proc.returncode != 0 or not path:
        raise PilotError(f"could not resolve the shared loop ledger: {proc.stderr.strip()}")
    if not Path(path).exists():
        raise PilotError(f"shared loop ledger {path} does not exist")
    rows = [parse_loop_row(line) for line in Path(path).read_text().splitlines()]
    return [r for r in rows if r is not None]


def report(run_id: str) -> dict:
    """Gather the three stores and evaluate the §3 iff-clause."""
    import arc_metrics as am
    import finding_record as fr

    arcs = _pilot_arcs(run_id)
    if not arcs:
        raise PilotError(
            f"no reservation carries pilot_run_id={run_id!r} — nothing to report. "
            "Each lane records it after arc open (see `lanes-pilot` step 1)."
        )
    queue_dir = am.QUEUE_DIR
    queued = {p.stem for p in queue_dir.glob("*.json")} if queue_dir.is_dir() else set()
    # TRI-STATE, deliberately not `am.committed_arc_ids()`: that helper collapses "merged
    # history is unreadable" into an empty set because holding a capture is the safe
    # default for the DRAIN. For this report the same empty set would make every arc look
    # like the legal queued-and-not-yet-folded branch and print PASS, so the unreadable
    # case must refuse instead (codex r1 P2). `_committed_ledger_lines()` is the
    # workspace's own discriminated reader — None means unreadable — and reusing it keeps
    # one authority on where merged history lives.
    # Class-sibling of the tri-state read below (defect-class-preflight, class 3):
    # `fr.read_rows()` returns [] for an ABSENT gate log, which would make the BASE_TOCTOU
    # half of clause (a) read clean when the detections simply could not be looked at.
    if not fr.GATE_LOG_JSONL.exists():
        raise PilotError(
            f"the gate log ({fr.GATE_LOG_JSONL}) does not exist — the BASE_TOCTOU "
            "first-parent clause cannot be evaluated"
        )
    lines = am._committed_ledger_lines()
    if lines is None:
        raise PilotError(
            f"merged history ({am.MERGED_REF}:{am.LEDGER.name}) is unreadable — the "
            "C-HE-03/04 union-ledger clause cannot be evaluated"
        )
    merged_ids = []
    for line in lines:
        try:
            merged_ids.append(json.loads(line).get("arc_id", ""))
        except json.JSONDecodeError:
            raise PilotError(f"merged ledger carries an unparseable row: {line[:80]}") from None
    return evaluate(
        run_id,
        Stores(
            arcs=arcs,
            gate_rows=fr.read_rows(),
            loop_rows=_loop_rows(),
            merged_ledger_arc_ids=merged_ids,
            queued_arc_ids=queued,
        ),
    )


def start(run_id: str) -> int:
    """Print the manual N-lane pilot recipe (C-HE-13 §3: 3–4 lanes, no Phase-2 machinery)."""
    print(f"pilot {run_id}: Phase 0 GREEN. Manual N-lane pilot recipe (3-4 lanes):")
    print("  1. per lane: `git worktree add ../lane-<k> -b <arc-branch>`;")
    print("     `source tools/hooks/lane-init.sh`; open the arc, then record the run id:")
    print(
        f"     `uv run python tools/reservations.py update --arc-id <arc-id> "
        f"--set pilot_run_id={run_id}`"
    )
    print("  2. run /roadmap-continue then /ship-pr in each lane to landing.")
    print(
        "  3. O1 (after the C-HE-09 X6 fix): in 4 worktrees run `bash -c 'source "
        "tools/hooks/lib.sh; source tools/hooks/loop_lib.sh; loop_status_path'` — one path."
    )
    print("  4. O3: `uv run python tools/arc_disjoint_check.py historical`.")
    print(f"  5. `just lanes-pilot-report {run_id}` once every lane has landed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="C-HE-13 pilot gate and report")
    p.add_argument("cmd", choices=("gate", "start", "report"))
    p.add_argument("run_id", nargs="?")
    a = p.parse_args(argv)
    if a.cmd == "gate":
        rc, msg = gate(phase0_results())
        print(msg)
        return rc
    if not a.run_id:
        print(f"lanes_pilot: {a.cmd} needs a run id", file=sys.stderr)
        return 2
    if a.cmd == "start":
        return start(a.run_id)
    try:
        rep = report(a.run_id)
    except PilotError as exc:
        print(f"lanes_pilot: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        # Exit 1 is the DOCUMENTED measured-FAIL code, so evidence this tool could not
        # read must never arrive as one. The store layers raise their own types
        # (finding_record / arc_metrics / reservations errors, JSON and OS errors), and a
        # traceback would exit 1 and read as a failed pilot (codex r1 P3). Loud and
        # typed-as-unanswerable, never swallowed.
        print(
            f"lanes_pilot: unreadable pilot evidence: {type(exc).__name__}: {exc}", file=sys.stderr
        )
        return 2
    print(json.dumps(rep, indent=2))
    print("PILOT", "PASS" if rep["pass"] else "FAIL")
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
