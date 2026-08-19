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

import hashlib
import json
import sys
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


def make_finding_id(producer: str, head_sha: str, location: str, n: int) -> str:
    """``<producer>:<head_sha>:<location-hash>:<n>`` (C-HE-24 §4). Not stable across head_sha."""
    loc = hashlib.sha1(location.encode()).hexdigest()[:12]
    return f"{producer}:{head_sha}:{loc}:{n}"


def make_row(core: FindingCore, env: Envelope) -> dict:
    return {**asdict(core), **asdict(env)}


def validate(row: dict) -> None:
    try:
        jsonschema.validate(row, SCHEMA)
    except jsonschema.ValidationError as exc:
        raise RecordError(f"finding record schema: {exc.message}") from exc
    # `:`-free identifiers (producer / lane_id / disposition_actor, C-HE-24 §2) are enforced by
    # the schema's `pattern` alone -- one enforcement point, no duplicate charset loop here.
    if row["record_kind"] == "finding_adjudication":
        if row["disposition"] is None or row["disposition_actor"] is None:
            raise RecordError("finding_adjudication rows require disposition and disposition_actor")
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


def _check_adjudication_against_original(row: dict, path: Path) -> None:
    """C-HE-24 §5 invariant at WRITE time: two rows with one finding_id differ only by
    ts / record_kind / disposition / disposition_actor / unique_catch. Because `producer` is
    core-immutable, an adjudication cannot smuggle a new producer in to evade the
    self-disposition ban (Codex round-1 P2): the swap is rejected here as a core-field change,
    and the ban itself has exactly one write-time enforcement point -- ``validate()``."""
    if row["record_kind"] != "finding_adjudication":
        return
    prior = [r for r in read_rows(path) if r["finding_id"] == row["finding_id"]]
    if not prior:
        raise RecordError(f"adjudication for unknown finding_id {row['finding_id']!r}")
    orig = prior[0]
    for k in _CORE_IMMUTABLE:
        if row[k] != orig[k]:
            raise RecordError(
                f"adjudication may not change core field {k!r} ({orig[k]!r} -> {row[k]!r})"
            )


def append_row(row: dict, path: Path | None = None) -> None:
    """Validate (incl. the same-core invariant for adjudications), then append one line with a
    single write. `path` defaults to GATE_LOG_JSONL resolved AT CALL TIME (not bound at def
    time) so tests may monkeypatch it and production writes never leak into a test's tree
    (Codex round-5 P1)."""
    path = path or GATE_LOG_JSONL
    validate(row)
    _check_adjudication_against_original(row, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, sort_keys=True) + "\n"
    with path.open("a") as fh:
        fh.write(line)


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
    """Last row per finding_id by (ts, file order). Append-only makes this monotonic."""
    out: dict[str, dict] = {}
    for row in sorted(rows, key=lambda r: r["ts"]):  # stable sort keeps file order on ties
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
