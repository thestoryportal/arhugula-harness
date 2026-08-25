#!/usr/bin/env python3
"""B-215 admission gate for the review loop: attestations in, one decision out.

Every `just review-with-failover` invocation passes through `admit()` before any
reviewer subprocess starts ([LAW:single-enforcer] — codex_review.main() is the one
seam both channels share). The gate converts the review loop's authoring-time
disciplines from instruction-following into refusals:

- CURRENCY: every admission requires the current bytes (head + diff digest via
  `rw.code_binding`, the same formula the reviewer binding uses,
  [LAW:one-source-of-truth]) to carry a sweep-run attestation — a preflight or a
  sweep bound to exactly this diff. A REVIEWER_UNAVAILABLE round reviewed nothing
  and never satisfies it (codex r2 P1).
- OBLIGATIONS: every finding_id ever recorded for the arc (both loop producers —
  round numbers are per-producer scales, so round arithmetic is incoherent across
  them, codex r2 P1) must be answered by some sweep attestation before the next
  round is admitted; refusals enumerate the unanswered ids.
- TERMINATION: review invocations spent — distinct (producer, round) pairs —
  beyond the budget (default 10, the merge-gate cap precedent) refuse with the
  register-and-hold recipe. Extensions are auditable records, not env flags
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
concurrent writers of the state file; appends are read-rewrite, not CAS. The same
discipline flow-excludes the admit-to-emission window (two concurrent wrapper
invocations for one arc): round minting itself (`round_n_for`) carries the identical
documented residual, registered to U-HE-19/21 — the gate adds no new window and
holds no lock.

Trust boundary (the u-he-33 `_record_detection` precedent, reaffirmed here): the
gate enforces DISCIPLINE against drift, not security against an agent with local
write access to this checkout — such an agent could edit this module, the gate log,
or the guard itself; fabricating attestation state is out of scope beyond the loud
containment refusals above. The `review-attest-budget` verb stays ask-gated so the
sanctioned path to more rounds is operator-visible; the filesystem is not a
sanctioned path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat as stat_module
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
    head_sha: str
    diff_digest: str  # full code binding, not head alone: a different --base is a different diff
    finding_ids: tuple[str, ...]  # the obligations this sweep answered (any producer, any round)
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
    code: str  # PREFLIGHT_MISSING | PREFLIGHT_STALE | SWEEP_MISSING
    #           | BUDGET_EXHAUSTED | ARC_UNRESERVED | STATE_UNREADABLE
    detail: str
    recipe: str


Decision = Allowed | Inactive | Refused


def state_path(root: Path) -> Path:
    return root / STATE_REL


def _read_state_bytes(path: Path) -> bytes | None:
    """Containment read (the finding_record/merge_door idiom, codex r1 P1 on this arc):
    O_NOFOLLOW + post-open fstat S_ISREG so a pre-planted symlink or special file at the
    state path is a loud refusal, never a follow. None = no file (empty state)."""
    try:
        fd = os.open(str(path), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise GateError(f"{path} refused (containment): {exc}") from exc
    try:
        if not stat_module.S_ISREG(os.fstat(fd).st_mode):
            raise GateError(f"{path} is not a regular file -- refused (containment)")
        chunks = []
        while chunk := os.read(fd, 65536):
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def load_state(root: Path) -> GateState:
    """Parse the state file to typed attestations; raise GateError on any malformed
    content — the caller decides direction (admit refuses; attest verbs re-init a
    CORRUPT file, but never a containment refusal)."""
    path = state_path(root)
    data = _read_state_bytes(path)
    if data is None:
        return GateState()
    try:
        raw = json.loads(data)
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
    licensed by the tightening-direction invariant (module docstring). A containment
    refusal (symlink/special file) is NOT corruption: it propagates as GateError, and
    the publish goes through a same-directory temp + os.replace (replacing a symlink
    path swaps the link itself, never writing through it)."""
    path = state_path(root)
    data = _read_state_bytes(path)  # GateError on symlink/special -- never re-init those
    try:
        existing = json.loads(data)["records"] if data is not None else []
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
    tmp = path.with_name(path.name + ".tmp")
    # exclusive-create the temp (codex r2 P1: write_text on a fixed .tmp name follows a
    # pre-planted symlink) — unlink removes a stale tmp or a planted link ITSELF, never
    # its target; O_EXCL|O_NOFOLLOW then cannot land on any pre-existing entry
    try:
        os.unlink(tmp)
    except FileNotFoundError:
        pass
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    try:
        os.write(fd, (json.dumps({"records": existing}, indent=1) + "\n").encode())
    finally:
        os.close(fd)
    os.replace(tmp, path)


# ── pure core ([LAW:effects-at-boundaries]: no IO below this line) ───────────


def _loop_rounds(rows: list[dict], arc_id: str) -> list[dict]:
    return [
        r
        for r in rows
        if r.get("arc_id") == arc_id
        and r.get("producer") in LOOP_PRODUCERS
        and r.get("round_n") is not None
    ]


def unanswered_findings(state: GateState, rows: list[dict], arc_id: str) -> list[str]:
    """Findings are OBLIGATIONS, not round rows (codex r2 P1): round numbers are
    per-producer scales, so a standalone gemini finding minted at its own round 1
    while codex sits at round 5 must still block admission. The unit is the
    finding_id; coverage is a set difference against every sweep ever attested."""
    all_ids = {
        r["finding_id"]
        for r in _loop_rounds(rows, arc_id)
        if r.get("record_kind") == "finding" and r.get("finding_id")
    }
    answered: set[str] = set()
    for s in state.sweeps:
        if s.arc_id == arc_id:
            answered.update(s.finding_ids)
    return sorted(all_ids - answered)


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
    # budget counts review invocations SPENT — distinct (producer, round) pairs, since
    # round numbers are per-producer scales and a max() across them undercounts
    # (codex r2 P1: codex round 5 + three standalone gemini rounds = 8 spent, not 5)
    rounds_spent = len({(r["producer"], r["round_n"]) for r in scoped})
    allowed_total = budget + sum(e.extra_rounds for e in state.extensions if e.arc_id == arc_id)
    if rounds_spent >= allowed_total:
        return Refused(
            code="BUDGET_EXHAUSTED",
            detail=f"{rounds_spent} review rounds spent for {arc_id}; budget {allowed_total}",
            recipe=(
                "round budget spent — this is the register-and-hold point, not a bug to "
                "keep iterating: register the residual findings as a forward item and "
                "defer (`bash tools/04-loop/defer.sh <arc> '<reason>'`); an operator may "
                "instead extend deliberately via `just review-attest-budget` (ask-gated)."
            ),
        )
    unanswered = unanswered_findings(state, rows, arc_id)
    if unanswered:
        return Refused(
            code="SWEEP_MISSING",
            detail="findings without a class-sibling sweep answer: " + ", ".join(unanswered),
            recipe=(
                "answer each finding_id in a sweep answers file (classify the miss, grep "
                "the diff for class siblings), commit the absorption, then "
                "`just review-attest-sweep <answers-file>`"
            ),
        )
    # currency invariant (codex r2 P1, subsuming the earlier post-APPROVE residual):
    # the CURRENT bytes must carry a sweep-run attestation — a preflight or a sweep
    # bound to exactly this (head, digest). A REVIEWER_UNAVAILABLE round minted no
    # findings and reviewed nothing, so it never satisfies this by itself.
    arc_attestations = [a for a in (*state.preflights, *state.sweeps) if a.arc_id == arc_id]
    if not any(a.head_sha == head_sha and a.diff_digest == diff_digest for a in arc_attestations):
        if not arc_attestations:
            return Refused(
                code="PREFLIGHT_MISSING",
                detail=f"no preflight attestation for {arc_id}",
                recipe=(
                    "run the defect-class-preflight sweep, write the named answers, COMMIT "
                    "the work, then attest AFTER the final commit: "
                    "`just review-attest-preflight <answers-file>`"
                ),
            )
        return Refused(
            code="PREFLIGHT_STALE",
            detail=(
                f"no attestation covers the reviewable diff "
                f"{head_sha[:12]}/{diff_digest[:12]} — the tree moved since the last "
                "preflight or sweep"
            ),
            recipe=(
                "re-run `just review-attest-preflight <answers-file>` after the last "
                "commit (every reviewed byte is attested-swept, always)"
            ),
        )
    return Allowed(round_n=max((r["round_n"] for r in scoped), default=0) + 1)


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
    # Reservation scope FIRST: Inactive means the gate is not in force for this arc,
    # so an unreadable state file must not refuse an out-of-scope invocation (it broke
    # the whole wrapper battery on a live schema migration before this ordering).
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
        binding = rw.code_binding(repo, base)
    except subprocess.CalledProcessError as exc:
        # An unresolvable base / broken git is a WRAPPER-infrastructure failure, not an
        # admission fact: defer to run_codex_review's own binding path, which classifies
        # it REVIEWER_UNAVAILABLE under the existing terminal contract (codex r1 P2).
        return Inactive(
            reason=f"code binding unavailable ({exc}) — the wrapper's binding path classifies"
        )
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


def _unanswered_labels(labels: tuple[str, ...], answers: str) -> list[str]:
    # hit labels are fixed multi-word strings from the sweep script — substring is exact
    return [n for n in labels if n not in answers]


def _unanswered_ids(ids: tuple[str, ...], answers: str) -> list[str]:
    # token-exact, not substring (codex r2 P2: an answer naming ...:10 must not
    # satisfy the sibling ...:1) — ids are whitespace/punctuation-delimited tokens
    tokens = set(re.split(r"[\s,;()\[\]{}'\"`]+", answers))
    return [n for n in ids if n not in tokens]


def _attest_preflight(repo: Path, base: str, answers_path: Path, arc_id: str) -> int:
    b = rw.code_binding(repo, base)
    labels = _run_sweep_script(repo, f"{b['base_sha']}..{b['head_sha']}")
    answers = _read_answers(answers_path)
    missing = _unanswered_labels(labels, answers)
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


def _attest_sweep(repo: Path, base: str, answers_path: Path, arc_id: str) -> int:
    """Attest the OUTSTANDING obligations — every unanswered finding_id for the arc,
    any producer, any round (the finding-as-obligation model, codex r2 P1) — plus the
    class-sibling textual floor over the attested bytes."""
    state = load_state(repo)  # GateError (containment/corrupt) propagates loud to main
    ids = unanswered_findings(state, fr.read_rows(), arc_id)
    if not ids:
        print(
            f"review-gate: no unanswered findings for {arc_id} — nothing to sweep "
            "(a moved tree re-attests via review-attest-preflight)",
            file=sys.stderr,
        )
        return 1
    b = rw.code_binding(repo, base)  # ONE binding per attest: sweep range and record agree
    # class-sibling textual floor over the attested bytes, same enforcer as preflight
    labels = _run_sweep_script(repo, f"{b['base_sha']}..{b['head_sha']}")
    answers = _read_answers(answers_path)
    missing = _unanswered_ids(tuple(ids), answers) + _unanswered_labels(labels, answers)
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
            head_sha=b["head_sha"],
            diff_digest=b["diff_digest"],
            finding_ids=tuple(ids),
            answers_digest=hashlib.sha256(answers.encode()).hexdigest(),
            ts=_now_iso(),
        ),
    )
    print(f"review-gate: sweep attested at {b['head_sha'][:12]} ({len(ids)} findings answered)")
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
            return _attest_sweep(repo, args.base, Path(args.answers), arc_id)
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
