#!/usr/bin/env python3
"""C-HE-24 common finding record and its `Finding` projection.

Every finding-class row (reviewer verdicts, deterministic checks, adjudications,
shadow-trial markers, equivalence proofs, gate demotions) carries the ratified
8-field core plus the row envelope and is appended to
``.harness/merge-gate-log.jsonl`` (C-HE-23 §2). ``.harness/arc-metrics.jsonl``
carries only ``record_kind=arc`` rows and never uses this module's emitter.

Adjudication is append-only (C-HE-24 §5): a later disposition is a new
``finding_adjudication`` row with the same ``finding_id``; readers reduce to
the last row. The write-time checks below are the enforcement of the "reviewer
is never authoritative for disposition" rule -- not prose.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema
from codex_context_guard import Finding

REPO = Path(__file__).resolve().parent.parent
GATE_LOG_JSONL = REPO / ".harness" / "merge-gate-log.jsonl"
SCHEMA_PATH = REPO / "tools" / "review_schemas" / "finding_record.schema.json"
SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text())

RECORD_KINDS = tuple(SCHEMA["properties"]["record_kind"]["enum"])
DISPOSITIONS = tuple(SCHEMA["properties"]["disposition"]["enum"])
SEVERITIES = tuple(SCHEMA["properties"]["severity"]["enum"])

#: C-HE-24 §4 ``finding_id`` shape: ``<producer>:<head_sha>:<location-hash>:<n>``.
_FINDING_ID_RE = re.compile(
    r"^(?P<producer>[^:]+):(?P<head>[^:]+):(?P<loc>[0-9a-f]{12}):(?P<n>[0-9]+)$"
)
#: Bounded wait for the log's exclusive lock (local read + one write; never a network call).
LOCK_TIMEOUT_S = 30.0

#: C-HE-24 §3 projection: fail-class (carried in ``finding_type``) -> guard severity.
_HARD_PREFIXES = ("terminal-", "permanent-fail-exit")
_WARN_PREFIXES = ("transient-retry", "Reflexion-", "HITL-recoverable")


class RecordError(ValueError):
    """A row that must not be written. Never swallowed."""


@dataclass(frozen=True)
class FindingCore:
    finding_id: str
    location: str
    observed_evidence: str
    expected_contract: str
    severity: str
    finding_type: str
    lineage_claim: str
    producer: str


@dataclass(frozen=True)
class Envelope:
    record_kind: str
    ts: str
    arc_id: str
    lane_id: str
    head_sha: str | None
    base_sha: str | None
    diff_digest: str | None
    round_n: int | None
    cause_attribution: str | None = None
    disposition: str | None = None
    disposition_actor: str | None = None
    unique_catch: bool | None = None


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def location_hash(location: str) -> str:
    return hashlib.sha1(location.encode()).hexdigest()[:12]


def make_finding_id(producer: str, head_sha: str, location: str, n: int) -> str:
    """``<producer>:<head_sha>:<location-hash>:<n>`` (C-HE-24 §4). Not stable across head_sha."""
    return f"{producer}:{head_sha}:{location_hash(location)}:{n}"


def _check_finding_id_components(row: dict) -> None:
    """The id is the ONLY join key reducers and adjudications use, so its components must agree
    with the row they key (Codex round-2 P2): shape per C-HE-24 §4, `producer` component ==
    row producer, location-hash component == sha1(location)[:12], head component == row
    head_sha when the row carries one (a null head_sha row is not held to that component)."""
    m = _FINDING_ID_RE.match(row["finding_id"])
    if m is None:
        raise RecordError(
            f"finding_id {row['finding_id']!r} is not <producer>:<head_sha>:<12-hex>:<n> "
            "(C-HE-24 §4)"
        )
    if m["producer"] != row["producer"]:
        raise RecordError(
            f"finding_id producer component {m['producer']!r} != row producer {row['producer']!r}"
        )
    if m["loc"] != location_hash(row["location"]):
        raise RecordError(
            f"finding_id location-hash {m['loc']!r} != sha1({row['location']!r})[:12]"
        )
    if row["head_sha"] is not None and m["head"] != row["head_sha"]:
        raise RecordError(
            f"finding_id head component {m['head']!r} != row head_sha {row['head_sha']!r}"
        )


def make_row(core: FindingCore, env: Envelope) -> dict:
    return {**asdict(core), **asdict(env)}


def validate(row: dict) -> None:
    try:
        jsonschema.validate(row, SCHEMA)
    except jsonschema.ValidationError as exc:
        raise RecordError(f"finding record schema: {exc.message}") from exc
    _check_finding_id_components(row)
    # `:`-free identifiers (producer / lane_id / disposition_actor, C-HE-24 §2) are enforced by
    # the schema's `pattern` alone -- one enforcement point, no duplicate charset loop here.
    if row["record_kind"] == "finding_adjudication":
        if row["disposition"] is None or row["disposition_actor"] is None:
            raise RecordError("finding_adjudication rows require disposition and disposition_actor")
    elif row["disposition"] is not None or row["disposition_actor"] is not None:
        # C-HE-24 §2/§5: disposition is set ONLY by an append-only adjudication row. A `finding`
        # row that arrives pre-disposed would let the reviewer dispose its own finding without
        # any adjudication event (Codex round-1 P1).
        raise RecordError(
            f"{row['record_kind']!r} rows must carry null disposition/disposition_actor "
            "(only finding_adjudication rows dispose, C-HE-24 §5)"
        )
    if row["disposition_actor"] is not None and row["disposition_actor"] == row["producer"]:
        raise RecordError(
            f"disposition_actor {row['disposition_actor']!r} equals producer -- "
            "a reviewer never disposes its own finding (C-HE-24 §5)"
        )


# Everything but ts / record_kind / disposition / disposition_actor / unique_catch.
_CORE_IMMUTABLE = (
    "location",
    "observed_evidence",
    "expected_contract",
    "severity",
    "finding_type",
    "lineage_claim",
    "producer",
    "arc_id",
    "lane_id",
    "head_sha",
    "base_sha",
    "diff_digest",
    "round_n",
    "cause_attribution",
)


def _check_against_prior_rows(row: dict, path: Path) -> None:
    """C-HE-24 §5 invariants at WRITE time, for EVERY row kind: two rows with one finding_id
    differ only by ts / record_kind / disposition / disposition_actor / unique_catch; the only
    kind transition is <original kind> -> finding_adjudication; an adjudication's ts is strictly
    later; nothing but further adjudications follows an adjudication. A repeated
    `finding` row (an emitter retry minting the same id) is held to the same core as the first
    row, not only adjudications (Codex round-1 P1). Because `producer` is core-immutable, an
    adjudication cannot smuggle a new producer in to evade the self-disposition ban: the swap
    is rejected here as a core-field change, and the ban itself has exactly one write-time
    enforcement point -- ``validate()``."""
    prior = [r for r in read_rows(path) if r["finding_id"] == row["finding_id"]]
    if not prior:
        if row["record_kind"] == "finding_adjudication":
            raise RecordError(f"adjudication for unknown finding_id {row['finding_id']!r}")
        return
    if row["record_kind"] != "finding_adjudication" and any(
        r["record_kind"] == "finding_adjudication" for r in prior
    ):
        # Once adjudicated, only further adjudications may follow: a same-core retry appended
        # after the decision would become the reducer's last row with a null disposition and
        # silently erase it (Codex round-4 P2; C-HE-24 §5, C-HE-29 "last disposition").
        raise RecordError(
            f"finding_id {row['finding_id']!r} is already adjudicated; a {row['record_kind']!r} "
            "row may not follow a finding_adjudication row"
        )
    orig = prior[0]
    if row["record_kind"] not in ("finding_adjudication", orig["record_kind"]):
        # A retry may repeat the ORIGINAL kind; the only other kind allowed on an existing id is
        # an adjudication. `finding` -> `no_finding` on one id would let the producer erase its
        # own finding through the reducer with no disposition_actor (Codex round-5 P1).
        raise RecordError(
            f"finding_id {row['finding_id']!r} was recorded as {orig['record_kind']!r}; a "
            f"{row['record_kind']!r} row may not follow it (only a same-kind retry or a "
            "finding_adjudication may)"
        )
    for k in _CORE_IMMUTABLE:
        if row[k] != orig[k]:
            raise RecordError(
                f"adjudication may not change core field {k!r} ({orig[k]!r} -> {row[k]!r})"
            )
    if row["record_kind"] == "finding_adjudication":
        latest_ts = max(r["ts"] for r in prior)
        if row["ts"] <= latest_ts:
            # C-HE-24 §5: an adjudication carries "a later ts". `now_iso()` is second-granular,
            # so a same-second adjudication is reachable and is rejected here rather than
            # recorded as a non-monotonic lineage (Codex round-5 P2). Reduction stays file-order.
            raise RecordError(
                f"adjudication ts {row['ts']!r} must be later than the finding's latest row ts "
                f"{latest_ts!r} (C-HE-24 §5)"
            )


def _lock_exclusive(fh, path: Path, timeout_s: float = LOCK_TIMEOUT_S) -> None:
    """Bounded `flock(LOCK_EX)` on the log's own fd -- the house pattern (`mutation_probe.py`,
    `tools/hooks/lib.sh`). Admissible here because the log is a REPO-resident record, not
    QUEUE_DIR coordination state: C-HE-02 §1's CAS-only rule and its `flock|fcntl` invariant are
    scoped to `arc_metrics.py` / `merge_door.py` / `reservations.py`. Kernel-released on process
    death, so there is no stale-lock reclaim path; the critical section is a local read + one
    write (C-HE-02 §3 satisfied). Times out loudly rather than waiting forever."""
    deadline = time.monotonic() + timeout_s
    delay = 0.005
    while True:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            if time.monotonic() >= deadline:
                raise RecordError(f"could not lock {path} within {timeout_s}s") from None
            time.sleep(delay)
            delay = min(delay * 2, 0.1)


def append_row(row: dict, path: Path | None = None) -> None:
    """Validate, then -- under the log's exclusive lock -- run the same-core invariant for
    repeated finding_ids and append one line with a single write. The check and the append are
    ONE critical section: two writers minting the same finding_id (C-HE-22's concurrent reviewer
    invocations) must not both pass the check and then both append conflicting cores (Codex
    round-2 P1). `path` defaults to GATE_LOG_JSONL resolved AT CALL TIME (not bound at def time)
    so tests may monkeypatch it and production writes never leak into a test's tree (Codex
    round-5 P1)."""
    path = path or GATE_LOG_JSONL
    validate(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, sort_keys=True) + "\n"
    with path.open("a") as fh:
        _lock_exclusive(fh, path)
        try:
            _check_against_prior_rows(row, path)
            fh.write(line)
            fh.flush()
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def read_rows(path: Path | None = None) -> list[dict]:
    path = path or GATE_LOG_JSONL  # call-time resolution (see append_row)
    if not path.exists():
        return []
    rows: list[dict] = []
    for n, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise RecordError(f"{path}:{n} is not valid JSON: {exc}") from exc
    return rows


def reduce_last_by_finding_id(rows: list[dict]) -> dict[str, dict]:
    """Last row per finding_id in FILE (append) order -- the append-only log is the ordering
    authority. `ts` is emitter-supplied and is never used to reorder: a clock regression or a
    back-filled row must not let an earlier physical row outrank the latest appended
    adjudication (Codex round-1 P2; C-HE-24 §5 "readers reduce by finding_id -> last row")."""
    out: dict[str, dict] = {}
    for row in rows:
        out[row["finding_id"]] = row
    return out


def to_guard_finding(row: dict) -> Finding:
    """C-HE-24 §3 projection for the CI surface. Existing guard codes are untouched."""
    ft = row["finding_type"]
    if ft.startswith(_HARD_PREFIXES):
        severity = "hard"
    elif ft.startswith(_WARN_PREFIXES):
        severity = "warn"
    else:
        severity = "info"
    code = f"{row['producer']}:{ft}:{row['cause_attribution'] or '-'}"
    return Finding(severity, code, row["observed_evidence"])


def main(argv: list[str] | None = None) -> int:
    """`python tools/finding_record.py validate <jsonl>` -- schema-check every row."""
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 2 or args[0] != "validate":
        print("usage: finding_record.py validate <path.jsonl>", file=sys.stderr)
        return 2
    bad = 0
    for n, row in enumerate(read_rows(Path(args[1])), start=1):
        try:
            validate(row)
        except RecordError as exc:
            bad += 1
            print(f"row {n}: {exc}", file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
