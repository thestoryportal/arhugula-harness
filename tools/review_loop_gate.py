#!/usr/bin/env python3
"""B-215 admission gate for the review loop: attestations in, one decision out.

Every `just review-with-failover` invocation passes through `admit()` before any
reviewer subprocess starts ([LAW:single-enforcer] — codex_review.main() is the one
seam both channels share). The gate converts the review loop's authoring-time
disciplines from instruction-following into refusals:

- round 1 requires a PREFLIGHT attestation bound to the exact reviewed bytes
  (`rw.code_binding` — the same digest formula the reviewer binding uses,
  [LAW:one-source-of-truth]);
- after a BLOCK round, the next round requires a SWEEP attestation covering every
  finding_id that round recorded (both loop producers — a failover round's
  findings land under the gemini producer at the forced shared round number);
- rounds beyond the budget (default 10, the merge-gate cap precedent) refuse with
  the register-and-hold recipe. Extensions are auditable records, not env flags
  ([LAW:no-mode-explosion]).

A refusal is NOT a review terminal: C-HE-16 §3 closes that enum at
{APPROVE, BLOCK, REVIEWER_UNAVAILABLE}, and a refused invocation never begins —
no C-HE-24 row is written, no round outcome is recorded, the wrapper exits 3
behind its own distinct stderr line (`codex-review: GATE_REFUSED (<code>)`).

State lives at `.harness/review_loop_gate_state.json` — local and gitignored,
same class as codex_loop's state: transient loop progress, never a tracked
artifact. Round history is deliberately NOT stored here: it derives from the
C-HE-24 gate log, the same source `round_n_for` mints from. The invariant that
follows ([LAW:one-source-of-truth], tested): losing or corrupting the state file
only TIGHTENS the gate (attestations vanish, rounds do not), so attest verbs may
loudly re-initialize a corrupt file — the safe direction — while `admit()` on a
corrupt file refuses (an unreadable state must never read as clean,
[LAW:no-silent-failure]).

Single-writer: the arc-serial holder discipline (one lane per arc) excludes
concurrent writers of the state file; appends are read-rewrite, not CAS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import review_wrapper_common as rw

STATE_REL = Path(".harness/review_loop_gate_state.json")
PREFLIGHT_SCRIPT_REL = Path(".claude/skills/defect-class-preflight/scripts/preflight-grep.sh")
#: Producers whose rows are review-LOOP rounds. Merge-gate lenses and detection
#: producers are excluded: lens rounds are per-producer and their numbers collide
#: with loop rounds; detection rows carry round_n=None (same filter round_n_for uses).
LOOP_PRODUCERS = ("codex_review_wrapper", "gemini_review_wrapper")
DEFAULT_ROUND_BUDGET = 10  # merge-gate fix-and-re-gate cap precedent (2026-08-01)

_HIT_LABEL = re.compile(r"^\[(.+)\]$", re.MULTILINE)


class GateError(Exception):
    """Loud gate failure (unreadable state, unrunnable sweep script)."""


# ── typed state ([LAW:parse-dont-validate]: JSON crosses once, here) ─────────


@dataclass(frozen=True)
class PreflightAttestation:
    arc_id: str
    head_sha: str
    diff_digest: str
    hit_labels: tuple[str, ...]
    answers_digest: str
    ts: str


@dataclass(frozen=True)
class SweepAttestation:
    arc_id: str
    round_n: int
    head_sha: str
    finding_ids: tuple[str, ...]
    answers_digest: str
    ts: str


@dataclass(frozen=True)
class BudgetExtension:
    arc_id: str
    extra_rounds: int
    reason: str
    ts: str


@dataclass(frozen=True)
class GateState:
    preflights: tuple[PreflightAttestation, ...] = ()
    sweeps: tuple[SweepAttestation, ...] = ()
    extensions: tuple[BudgetExtension, ...] = ()


_KINDS = {
    "preflight": (PreflightAttestation, "preflights"),
    "sweep": (SweepAttestation, "sweeps"),
    "budget_extension": (BudgetExtension, "extensions"),
}
_TUPLE_FIELDS = ("hit_labels", "finding_ids")


# ── decisions ([LAW:types-are-the-program]: three arms, no boolean folklore) ─


@dataclass(frozen=True)
class Allowed:
    round_n: int


@dataclass(frozen=True)
class Inactive:
    """Gate not in force (unreserved arc outside loop mode) — allow, loudly."""

    reason: str


@dataclass(frozen=True)
class Refused:
    code: str  # PREFLIGHT_MISSING | PREFLIGHT_STALE | SWEEP_MISSING | SWEEP_STALE
    #           | BUDGET_EXHAUSTED | ARC_UNRESERVED | STATE_UNREADABLE
    detail: str
    recipe: str


Decision = Allowed | Inactive | Refused


def state_path(root: Path) -> Path:
    return root / STATE_REL


def load_state(root: Path) -> GateState:
    """Parse the state file to typed attestations; raise GateError on any malformed
    content — the caller decides direction (admit refuses; attest verbs re-init)."""
    path = state_path(root)
    if not path.exists():
        return GateState()
    try:
        raw = json.loads(path.read_text())
        buckets: dict[str, list] = {attr: [] for _, attr in _KINDS.values()}
        for rec in raw["records"]:
            cls, attr = _KINDS[rec["kind"]]
            fields = {k: v for k, v in rec.items() if k != "kind"}
            for tf in _TUPLE_FIELDS:
                if tf in fields:
                    fields[tf] = tuple(fields[tf])
            buckets[attr].append(cls(**fields))
        return GateState(**{attr: tuple(v) for attr, v in buckets.items()})
    except (KeyError, TypeError, ValueError) as exc:
        raise GateError(f"{path} is unreadable as gate state: {exc}") from exc


def _append_record(root: Path, kind: str, record: object) -> None:
    """Read-rewrite append. A corrupt existing file is re-initialized LOUDLY —
    licensed by the tightening-direction invariant (module docstring)."""
    path = state_path(root)
    try:
        existing = json.loads(path.read_text())["records"] if path.exists() else []
        if not isinstance(existing, list):
            raise ValueError("records is not a list")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        print(
            f"review-gate: corrupt {path} — re-init (attestations lost, gate tightens only)",
            file=sys.stderr,
        )
        existing = []
    existing.append({"kind": kind, **asdict(record)})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"records": existing}, indent=1) + "\n")


# ── pure core ([LAW:effects-at-boundaries]: no IO below this line) ───────────


def _loop_rounds(rows: list[dict], arc_id: str) -> list[dict]:
    return [
        r
        for r in rows
        if r.get("arc_id") == arc_id
        and r.get("producer") in LOOP_PRODUCERS
        and r.get("round_n") is not None
    ]


def decide(
    state: GateState,
    rows: list[dict],
    *,
    arc_id: str,
    head_sha: str,
    diff_digest: str,
    budget: int = DEFAULT_ROUND_BUDGET,
) -> Allowed | Refused:
    scoped = _loop_rounds(rows, arc_id)
    last = max((r["round_n"] for r in scoped), default=0)
    allowed_total = budget + sum(e.extra_rounds for e in state.extensions if e.arc_id == arc_id)
    if last >= allowed_total:
        return Refused(
            code="BUDGET_EXHAUSTED",
            detail=f"{last} review rounds recorded for {arc_id}; budget {allowed_total}",
            recipe=(
                "round budget spent — this is the register-and-hold point, not a bug to "
                "keep iterating: register the residual findings as a forward item and "
                "defer (`bash tools/04-loop/defer.sh <arc> '<reason>'`); an operator may "
                "instead extend deliberately via `just review-attest-budget` (ask-gated)."
            ),
        )
    if last == 0:
        pf = next((p for p in reversed(state.preflights) if p.arc_id == arc_id), None)
        if pf is None:
            return Refused(
                code="PREFLIGHT_MISSING",
                detail=f"no preflight attestation for {arc_id}",
                recipe=(
                    "run the defect-class-preflight sweep, write the named answers, COMMIT "
                    "the work, then attest AFTER the final commit: "
                    "`just review-attest-preflight <answers-file>`"
                ),
            )
        if pf.head_sha != head_sha or pf.diff_digest != diff_digest:
            return Refused(
                code="PREFLIGHT_STALE",
                detail=(
                    f"preflight attested {pf.head_sha[:12]}/{pf.diff_digest[:12]} but the "
                    f"reviewable diff is {head_sha[:12]}/{diff_digest[:12]}"
                ),
                recipe=(
                    "the tree moved since attesting — re-run "
                    "`just review-attest-preflight` after the last commit"
                ),
            )
        return Allowed(round_n=1)
    unanswered_ids = sorted(
        r["finding_id"]
        for r in scoped
        if r["round_n"] == last and r.get("record_kind") == "finding" and r.get("finding_id")
    )
    if unanswered_ids:
        sweep = next(
            (s for s in reversed(state.sweeps) if s.arc_id == arc_id and s.round_n == last), None
        )
        if sweep is not None:
            if sweep.head_sha != head_sha:
                return Refused(
                    code="SWEEP_STALE",
                    detail=(
                        f"sweep for round {last} attested at {sweep.head_sha[:12]} but HEAD "
                        f"is {head_sha[:12]} — the sweep must cover the fix's final form"
                    ),
                    recipe="re-run `just review-attest-sweep <answers-file>` after the last commit",
                )
            unanswered_ids = [i for i in unanswered_ids if i not in sweep.finding_ids]
        if unanswered_ids:
            return Refused(
                code="SWEEP_MISSING",
                detail=(
                    f"round {last} findings without a class-sibling sweep answer: "
                    + ", ".join(unanswered_ids)
                ),
                recipe=(
                    "answer each finding_id in a sweep answers file (classify the miss, grep "
                    "the diff for class siblings), commit the absorption, then "
                    "`just review-attest-sweep <answers-file>`"
                ),
            )
    return Allowed(round_n=last + 1)


# ── edge: admit ──────────────────────────────────────────────────────────────


def _loop_mode(root: Path) -> bool:
    # mirror of tools/hooks/lib.sh loop_mode_active(): env OR workspace marker
    return os.environ.get("HARNESS_LOOP") == "1" or (root / ".harness" / ".loop-active").exists()


def _reservation_exists(arc_id: str) -> bool:
    try:
        import reservations as rs
    except ImportError:
        return False
    return rs.current(arc_id) is not None


def admit(repo: Path, base: str, arc_id: str) -> Decision:
    try:
        state = load_state(repo)
    except GateError as exc:
        return Refused(
            code="STATE_UNREADABLE",
            detail=str(exc),
            recipe=(
                "inspect the file; any attest verb re-initializes it loudly (state loss "
                "only tightens the gate — round counts live in the gate log)"
            ),
        )
    try:
        reserved = _reservation_exists(arc_id)
    except Exception as exc:  # unreadable store: cannot tell -> never read as reserved
        reserved = False
        print(f"review-gate: reservation store unreadable ({exc})", file=sys.stderr)
    if not reserved:
        if _loop_mode(repo):
            return Refused(
                code="ARC_UNRESERVED",
                detail=f"arc {arc_id} has no reservation and loop mode is active",
                recipe=(
                    "loop arcs are reserved at selection — open via roadmap-continue, or "
                    "export the reserved arc's HARNESS_ARC_ID before invoking the wrapper"
                ),
            )
        return Inactive(reason=f"arc {arc_id} unreserved — attestation gate not in force")
    binding = rw.code_binding(repo, base)
    return decide(
        state,
        fr.read_rows(),
        arc_id=arc_id,
        head_sha=binding["head_sha"],
        diff_digest=binding["diff_digest"],
    )


# ── edge: attest verbs ───────────────────────────────────────────────────────


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_sweep_script(repo: Path, diff_range: str) -> tuple[str, ...]:
    """Run the textual defect-class sweep over EXACTLY the attested bytes — the
    committed `<base>..<head>` range the binding digest covers, never the working
    tree (empty right after the commit the attestation requires). Return hit
    labels. GateError when the sweep could not run — 'couldn't look' must never
    attest as looked-and-clean."""
    script = repo / PREFLIGHT_SCRIPT_REL
    proc = subprocess.run(
        ["bash", str(script), diff_range], cwd=repo, capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise GateError(
            f"preflight sweep did not run (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return tuple(_HIT_LABEL.findall(proc.stdout))


def _read_answers(path: Path) -> str:
    if not path.is_file():
        raise GateError(f"answers file {path} does not exist")
    text = path.read_text()
    if not text.strip():
        raise GateError(f"answers file {path} is empty")
    return text


def _unanswered(needles: tuple[str, ...], answers: str) -> list[str]:
    return [n for n in needles if n not in answers]


def _attest_preflight(repo: Path, base: str, answers_path: Path, arc_id: str) -> int:
    b = rw.code_binding(repo, base)
    labels = _run_sweep_script(repo, f"{b['base_sha']}..{b['head_sha']}")
    answers = _read_answers(answers_path)
    missing = _unanswered(labels, answers)
    if missing:
        print(
            "review-gate: preflight NOT attested — hits without a named answer: "
            + "; ".join(missing),
            file=sys.stderr,
        )
        return 1
    _append_record(
        repo,
        "preflight",
        PreflightAttestation(
            arc_id=arc_id,
            head_sha=b["head_sha"],
            diff_digest=b["diff_digest"],
            hit_labels=labels,
            answers_digest=hashlib.sha256(answers.encode()).hexdigest(),
            ts=_now_iso(),
        ),
    )
    print(
        f"review-gate: preflight attested at {b['head_sha'][:12]} "
        f"({len(labels)} hit labels answered)"
    )
    return 0


def _attest_sweep(
    repo: Path, base: str, answers_path: Path, arc_id: str, round_arg: int | None
) -> int:
    scoped = _loop_rounds(fr.read_rows(), arc_id)
    last = max((r["round_n"] for r in scoped), default=0)
    target = round_arg if round_arg is not None else last
    if target == 0:
        print(
            f"review-gate: no recorded review rounds for {arc_id} — nothing to sweep",
            file=sys.stderr,
        )
        return 1
    ids = sorted(
        r["finding_id"]
        for r in scoped
        if r["round_n"] == target and r.get("record_kind") == "finding" and r.get("finding_id")
    )
    if not ids:
        print(
            f"review-gate: round {target} of {arc_id} has no findings — nothing to sweep",
            file=sys.stderr,
        )
        return 1
    b = rw.code_binding(repo, base)  # ONE binding per attest: sweep range and record agree
    # class-sibling textual floor over the attested bytes, same enforcer as preflight
    labels = _run_sweep_script(repo, f"{b['base_sha']}..{b['head_sha']}")
    answers = _read_answers(answers_path)
    missing = _unanswered(tuple(ids), answers) + _unanswered(labels, answers)
    if missing:
        print(
            "review-gate: sweep NOT attested — unanswered: " + "; ".join(missing),
            file=sys.stderr,
        )
        return 1
    _append_record(
        repo,
        "sweep",
        SweepAttestation(
            arc_id=arc_id,
            round_n=target,
            head_sha=b["head_sha"],
            finding_ids=tuple(ids),
            answers_digest=hashlib.sha256(answers.encode()).hexdigest(),
            ts=_now_iso(),
        ),
    )
    print(
        f"review-gate: round {target} sweep attested at {b['head_sha'][:12]} "
        f"({len(ids)} findings answered)"
    )
    return 0


def _attest_budget(repo: Path, extra: int, reason: str, arc_id: str) -> int:
    if not reason.strip():
        print("review-gate: budget extension requires a non-empty --reason", file=sys.stderr)
        return 1
    _append_record(
        repo,
        "budget_extension",
        BudgetExtension(arc_id=arc_id, extra_rounds=extra, reason=reason, ts=_now_iso()),
    )
    print(f"review-gate: budget extended by {extra} rounds for {arc_id}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("attest-preflight", "attest-sweep"):
        sp = sub.add_parser(name)
        sp.add_argument("--answers", required=True, help="in-worktree relative path")
        sp.add_argument("--base", default="main")
        sp.add_argument("--repo", default=".")
        if name == "attest-sweep":
            sp.add_argument("--round", type=int, default=None)
    sp = sub.add_parser("attest-budget")
    sp.add_argument("--extra", type=int, required=True)
    sp.add_argument("--reason", required=True)
    sp.add_argument("--repo", default=".")
    sp = sub.add_parser("check")
    sp.add_argument("--base", default="main")
    sp.add_argument("--repo", default=".")
    args = p.parse_args(argv)
    repo = Path(args.repo).resolve()
    arc_id, _ = rw.env_arc_and_lane()
    try:
        if args.cmd == "attest-preflight":
            return _attest_preflight(repo, args.base, Path(args.answers), arc_id)
        if args.cmd == "attest-sweep":
            return _attest_sweep(repo, args.base, Path(args.answers), arc_id, args.round)
        if args.cmd == "attest-budget":
            return _attest_budget(repo, args.extra, args.reason, arc_id)
    except GateError as exc:
        print(f"review-gate: {exc}", file=sys.stderr)
        return 1
    decision = admit(repo, args.base, arc_id)
    if isinstance(decision, Refused):
        print(f"review-gate: {decision.detail}\n  recipe: {decision.recipe}", file=sys.stderr)
        print(f"review-gate-check: REFUSED ({decision.code})", file=sys.stderr)
        return 3
    if isinstance(decision, Inactive):
        print(f"review-gate-check: INACTIVE — {decision.reason}")
        return 0
    print(f"review-gate-check: ALLOWED (next round {decision.round_n})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
