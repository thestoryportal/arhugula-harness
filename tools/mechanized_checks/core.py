"""C-HE-31 framework: the finding, the gathered subject, C-HE-24 emission, and the
promotion/demotion machine over `.harness/mechanized-checks-state.json`.

Sited ONLY at a stable boundary (`just mech-check`: pre-commit / pre-review / pre-PR), never as a
blocking PostToolUse on every intermediate edit (§3). The live mode/window state is runtime
state, plan-owned, stored outside the spec (§4(d)): no runtime path here writes the spec.
No mechanized check is ever cited as grounds for a round cap (C-HE-31 Invariants).
"""

from __future__ import annotations

import json
import os
from collections import Counter
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal, Protocol

import finding_record as fr
import reservations as rs

REPO = Path(__file__).resolve().parents[2]
STATE_PATH = REPO / ".harness" / "mechanized-checks-state.json"
#: §4: the promotion replay and every rolling demotion window span 20 merged arcs; promotion
#: admits zero `rejected`; demotion needs >= 2 `rejected` in EACH of two consecutive windows.
WINDOW = 20
PROMOTE_MAX_REJECTED = 0
DEMOTE_STRIKES = 2
#: Provider credentials a subject-executing check never hands to subject code, plus a keyring it
#: never reaches: the scrub `tools/codex-parity-check.sh` applies before running the suites
#: (`test_subject_env_matches_the_parity_scrub` pins this tuple to that script's `unset` lines).
SUBJECT_ENV_DROP = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "E2B_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "HARNESS_CODEX_REVIEW_ISOLATED",
)
#: The rows that record a check RAN on an arc: its findings and its clean marker.
OBSERVATION_KINDS = ("finding", "no_finding")

Kind = Literal["deterministic", "hybrid"]
Severity = Literal["hard", "warn", "info"]


class StateError(ValueError):
    """The state file does not parse into one state per check. Never swallowed."""


@dataclass(frozen=True)
class MechFinding:
    location: str
    evidence: str
    expected: str
    severity: Severity = "warn"


@dataclass(frozen=True)
class Subject:
    """Everything a check reads, gathered once at the edge (`runner`). Checks never shell out,
    so one check runs unchanged against the working tree and against a replayed arc's extract."""

    repo: Path
    changed: tuple[str, ...]  # repo-relative paths the change touches
    universe: tuple[str, ...]  # repo-relative files of the tree (tracked + untracked, unignored)
    diff: str  # the change as a `--unified=0` diff
    claims_text: str  # the change's commit message(s)
    pr_body: str | None  # None: gh could not produce the body -- never conflated with ""

    def read(self, rel: str) -> str | None:
        path = self.repo / rel
        return path.read_text(errors="replace") if path.is_file() else None

    def changed_texts(self, *suffixes: str) -> list[tuple[str, str]]:
        """`(path, text)` per changed file with one of `suffixes`. A changed path absent from
        the tree is a deletion, and a deletion carries no text to check."""
        return [
            (rel, text)
            for rel in self.changed
            if rel.endswith(suffixes)
            for text in [self.read(rel)]
            if text is not None
        ]


class Check(Protocol):
    check_id: str
    kind: Kind
    replayable: bool  # False: it executes subject code, so it never runs on a historical tree

    def run(self, subject: Subject) -> list[MechFinding]: ...


def subject_env() -> dict[str, str]:
    """The environment for a subprocess that runs subject code or reads the subject tree."""
    kept = {k: v for k, v in os.environ.items() if k not in SUBJECT_ENV_DROP}
    return {**kept, "PYTHON_KEYRING_BACKEND": "keyring.backends.null.Keyring"}


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# --- emission (§1, §5) -------------------------------------------------------------------


def emit(
    check_id: str,
    kind: Kind,
    findings: Sequence[MechFinding],
    *,
    arc_id: str,
    lane_id: str,
    head_sha: str | None,
    lineage: Literal["fresh", "replay"],
) -> list[dict]:
    """C-HE-24 rows with `producer=<check_id>`. A clean run writes one `no_finding` marker, so
    "ran and found nothing" stays distinguishable from "never ran" -- §5 measures a class by
    exactly these rows. Ids are minted under the log lock (`append_observations`), so a rerun at
    the same head is a new observation, never a collision with the last one."""
    ts = fr.now_iso()

    def observation(record_kind: str, f: MechFinding) -> tuple[dict, fr.Envelope]:
        core = {
            "location": f.location,
            "observed_evidence": f.evidence,
            "expected_contract": f.expected,
            "severity": f.severity,
            "finding_type": f"mechanized-{kind}",
            "lineage_claim": lineage,
            "producer": check_id,
        }
        return core, fr.Envelope(record_kind, ts, arc_id, lane_id, head_sha, None, None, None)

    observed = [observation("finding", f) for f in findings]
    clean = [observation("no_finding", MechFinding(check_id, "", "", "info"))]
    return fr.append_observations(lambda _rows: observed or clean)


# --- runtime state (§4(d)) ---------------------------------------------------------------


@dataclass(frozen=True)
class Advisory:
    windows: tuple[int, ...] = ()


@dataclass(frozen=True)
class Blocking:
    promoted_at: str  # the start of the demotion windows (§4(b) counts arcs from promotion on)
    windows: tuple[int, ...] = ()


CheckState = Advisory | Blocking


def _parse_entry(check_id: str, raw: object) -> CheckState:
    if not isinstance(raw, dict):
        raise StateError(f"{check_id}: state entry is not an object")
    windows = raw.get("windows")
    if not isinstance(windows, list) or not all(isinstance(w, int) for w in windows):
        raise StateError(f"{check_id}: windows must be a list of rejected counts")
    match raw.get("mode"):
        case "advisory":
            return Advisory(tuple(windows))
        case "blocking" if isinstance(raw.get("promoted_at"), str):
            return Blocking(raw["promoted_at"], tuple(windows))
        case "blocking":
            raise StateError(f"{check_id}: a blocking check needs promoted_at (its window start)")
        case mode:
            raise StateError(f"{check_id}: mode {mode!r} is neither advisory nor blocking")


def load_state() -> dict[str, CheckState]:
    raw = json.loads(STATE_PATH.read_text())
    if not isinstance(raw, dict):
        raise StateError(f"{STATE_PATH} is not an object keyed by check_id")
    return {check_id: _parse_entry(check_id, entry) for check_id, entry in raw.items()}


def _encode(state: CheckState) -> dict:
    match state:
        case Advisory(windows):
            return {"mode": "advisory", "windows": list(windows)}
        case Blocking(promoted_at, windows):
            return {"mode": "blocking", "promoted_at": promoted_at, "windows": list(windows)}


def save_state(state: dict[str, CheckState]) -> None:
    body = json.dumps({k: _encode(v) for k, v in state.items()}, indent=2, sort_keys=True)
    tmp = STATE_PATH.with_name(STATE_PATH.name + ".tmp")
    tmp.write_text(body + "\n")
    tmp.replace(STATE_PATH)


@contextmanager
def state_lock() -> Iterator[None]:
    """Serialize every read-modify-write of the state file, so two lanes' `just lanes-verify`
    cannot interleave load and save and silently undo a demotion. The house bounded flock
    (`finding_record._lock_exclusive`, loud on timeout) on a gitignored sidecar: `save_state`
    replaces the state file, so a lock on its inode would not serialize the next opener."""
    lock = STATE_PATH.with_name(STATE_PATH.name + ".lock")
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o644)
    try:
        fr._lock_exclusive(fd, lock)
        yield
    finally:
        os.close(fd)


# --- promotion (§4(a)) -------------------------------------------------------------------


@dataclass(frozen=True)
class Unmeasured:
    arcs: tuple[str, ...]


@dataclass(frozen=True)
class Pending:
    findings: int


@dataclass(frozen=True)
class Measured:
    rejected: tuple[bool, ...]  # per replayed arc: does it carry a finding adjudicated rejected


ReplayVerdict = Unmeasured | Pending | Measured


def _mine(rows: Sequence[dict], check_id: str) -> list[dict]:
    """The latest row of each of this check's observations (C-HE-24 §5: readers reduce by
    finding_id to the last appended row). A row without a producer is nobody's observation."""
    last = fr.reduce_last_by_finding_id(list(rows)).values()
    return [r for r in last if r.get("producer") == check_id]


def replay_verdict(rows: Sequence[dict], check_id: str, arc_ids: Sequence[str]) -> ReplayVerdict:
    """§4(a) over the replay's rows. An arc the check never ran on is unmeasured, and a finding
    nobody has adjudicated is pending: neither is ever read as zero `rejected`."""
    mine = [r for r in _mine(rows, check_id) if r["arc_id"] in arc_ids]
    observed = {r["arc_id"] for r in mine}
    unmeasured = tuple(a for a in arc_ids if a not in observed)
    pending = sum(r["record_kind"] == "finding" for r in mine)
    rejected = {r["arc_id"] for r in mine if r["disposition"] == "rejected"}
    measured = Measured(tuple(a in rejected for a in arc_ids))
    return Unmeasured(unmeasured) if unmeasured else Pending(pending) if pending else measured


def evaluate_promotion(check_id: str, replay_rejected: Sequence[bool]) -> bool:
    """§4(a): one fixed replay of the last WINDOW merged arcs, evaluated once -- zero arcs with a
    `rejected` finding promotes an advisory check to blocking. Operating characteristic, stated
    honestly: P(pass | true per-arc FP rate p=0.05) = 0.95**20 ≈ 0.36, so the bar excludes
    p ≳ 0.15, not less."""
    with state_lock():
        state = load_state()
        promoted = (
            isinstance(state[check_id], Advisory)
            and len(replay_rejected) == WINDOW
            and sum(replay_rejected) <= PROMOTE_MAX_REJECTED
        )
        state[check_id] = Blocking(fr.now_iso()) if promoted else state[check_id]
        save_state(state)
    return promoted


# --- demotion (§4(b), §4(c)) -------------------------------------------------------------


def rejected_windows(rows: Sequence[dict], check_id: str, *, since: str) -> list[int]:
    """§4(b)'s rolling windows: the arcs this check observed LIVE at or after `since` (its
    promotion), in first-observation order, cut into consecutive non-overlapping WINDOW-arc
    windows that END at the latest arc -- the oldest partial window is the one dropped, so the
    last two entries are always the two most recent windows. Replay observations re-measure
    history and never advance a window."""
    observed = [
        r
        for r in rows
        if r.get("producer") == check_id
        and r["record_kind"] in OBSERVATION_KINDS
        and r["lineage_claim"] == "fresh"
        and r["ts"] >= since
    ]
    # a rejection counts only for a finding observed inside that same qualifying set: an arc
    # rechecked after promotion never imports its earlier, pre-promotion rejections
    qualifying = {r["finding_id"] for r in observed if r["record_kind"] == "finding"}
    last = fr.reduce_last_by_finding_id(list(rows))
    rejected = Counter(
        last[f]["arc_id"] for f in qualifying if last[f]["disposition"] == "rejected"
    )
    arcs = list(dict.fromkeys(r["arc_id"] for r in observed))
    recent = arcs[len(arcs) % WINDOW :]
    return [sum(rejected[a] for a in recent[i : i + WINDOW]) for i in range(0, len(recent), WINDOW)]


def demotion_due(state: CheckState, windows: Sequence[int]) -> bool:
    """Two-strikes hysteresis: a single window at p=0.03 flaps with P ≈ 0.12, two consecutive
    windows at >= DEMOTE_STRIKES do not."""
    last_two = windows[-2:]
    return isinstance(state, Blocking) and len(last_two) == 2 and min(last_two) >= DEMOTE_STRIKES


def evaluate_demotion(check_id: str, windows: Sequence[int], *, promoted_at: str) -> bool:
    """Record the check's latest windows; when a demotion is due, write the `gate_demotion` row
    and the NOTIFY FIRST (§4(c): at the moment it fires), then flip the state -- a crash between
    the two leaves a duplicate audit row on retry, never a demotion with no audit row. The windows
    were computed outside the lock for the promotion stamped `promoted_at`; they apply only while
    the check still carries that promotion, so a concurrent demote-and-repromote is never judged
    by the previous promotion's windows."""
    with state_lock():
        state = load_state()
        current = state[check_id]
        last_two = tuple(windows[-2:])
        same_promotion = isinstance(current, Blocking) and current.promoted_at == promoted_at
        demoted = same_promotion and demotion_due(current, last_two)
        if demoted:
            _demotion_row(check_id, last_two)
            _notify(check_id, last_two)
        if same_promotion:
            state[check_id] = Advisory(last_two) if demoted else replace(current, windows=last_two)
            save_state(state)
    return demoted


def _demotion_row(check_id: str, counts: tuple[int, ...]) -> None:
    core = {
        "location": check_id,
        "observed_evidence": f"rejected findings in two consecutive {WINDOW}-arc windows: "
        f"{list(counts)}",
        "expected_contract": "C-HE-31 §4(b): fewer than 2 rejected in one of the last two windows",
        "severity": "warn",
        "finding_type": "gate_demotion",
        "lineage_claim": "policy",
        "producer": "lanes_verify",
    }
    env = fr.Envelope(
        "gate_demotion",
        fr.now_iso(),
        "policy",
        "lanes_verify",
        None,
        None,
        None,
        None,
        cause_attribution=check_id,
    )
    fr.append_observation(core, env)


def _notify(check_id: str, counts: tuple[int, ...]) -> None:
    rs.emit_loop_row(
        "NOTIFY",
        "lanes_verify",
        "mech-check-demoted:HITL-recoverable:two_strikes",
        f"{check_id} demoted blocking->advisory (rejected per window {list(counts)})",
    )
