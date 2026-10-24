#!/usr/bin/env python3
"""WO-U05 / WP-04 — the four lifecycle boundaries and their versioned guard CLI (spec
WS-06, WS-18).

`parse_request` turns a boundary/point pair into a `BoundaryRequest` whose step makes the
WS-06 point rules unrepresentable: `prepare` and `develop` are readiness checks with no
point; `publish` and `integrate` are either a pre-action admission (`before`) or a
post-action completion (`after`). `evaluate_boundary` is a pure decision over
`BoundaryFacts` — the WP-02 profile selection plus one observation per requirement, each
derived by an adapter from an actual producer record. A completion requires every
admission observation plus the remote, landing and own-main observations no admission
carries, and only a passing completion yields a `boundary_completion` record, so a
pre-action success can never stand in for an action that has not happened.

`main` serves `workflow status|check` for `codex_context_guard.py`: it reads the boundary
manifest, verifies each referenced producer record by size and SHA-256, and publishes an
immutable receipt only for a passing check. Only WS-08 check receipts have an adapter
here; requirements sourced from LIT, review, CI, remote readback or the merge door hold
until their producers' adapters exist. Until the coherent activation (WP-17) every unit
selects `legacy`, so the interface is inactive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Literal, NoReturn, cast

from tools.workflow_evidence import ReceiptDefect, load_receipt
from tools.workflow_policy import (
    CANONICAL_ROOT,
    POLICY_VERSION,
    PROFILE_ID,
    ProfileSelection,
    SelectionFacts,
    canonical_digest,
    load_policy,
    read_activation,
    select_profile,
)

SCHEMA_VERSION = 1
POLICY_PATH = Path(__file__).resolve().parent.parent / ".harness" / "workflow-policy.json"
RECEIPT_ROOT = CANONICAL_ROOT / ".local" / "buford-loop" / "workflow-receipts"

Boundary = Literal["prepare", "develop", "publish", "integrate"]
Point = Literal["before", "after"]
Result = Literal["passed", "held", "failed", "error"]
RecordType = Literal["boundary_admission", "boundary_completion"]
Source = Literal["check", "lit", "review", "ci", "remote", "door"]
ReasonCode = Literal[
    "invalid_input",
    "policy_mismatch",
    "authority_changed",
    "authority_unavailable",
    "ownership_conflict",
    "identity_mismatch",
    "headroom_unknown",
    "refresh_required",
    "review_blocked",
    "review_budget_exhausted",
    "check_failed",
    "check_pending",
    "binding_stale",
    "capability_denied",
    "artifact_unavailable",
    "publication_uncertain",
]

BOUNDARIES: tuple[Boundary, ...] = ("prepare", "develop", "publish", "integrate")
_UNIT = re.compile(r"[a-z0-9][a-z0-9._-]*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_GIT_OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")


class BoundaryError(ValueError):
    """Invalid invocation, manifest or producer record; `field` names it (WS-18)."""

    def __init__(self, field: str, problem: str) -> None:
        super().__init__(f"{field}: {problem}")
        self.field = field


# --- requests ----------------------------------------------------------------------------


@dataclass(frozen=True)
class Readiness:
    boundary: Literal["prepare", "develop"]


@dataclass(frozen=True)
class Admission:
    boundary: Literal["publish", "integrate"]


@dataclass(frozen=True)
class Completion:
    boundary: Literal["publish", "integrate"]


Step = Readiness | Admission | Completion

# [LAW:types-are-the-program] the only legal boundary/point pairs; every other pair rejects.
_STEPS: Mapping[tuple[str, str | None], Step] = MappingProxyType(
    {
        ("prepare", None): Readiness("prepare"),
        ("develop", None): Readiness("develop"),
        ("publish", "before"): Admission("publish"),
        ("publish", "after"): Completion("publish"),
        ("integrate", "before"): Admission("integrate"),
        ("integrate", "after"): Completion("integrate"),
    }
)
_POINT: Mapping[type, Point | None] = MappingProxyType(
    {Readiness: None, Admission: "before", Completion: "after"}
)
_RECORD_TYPE: Mapping[type, RecordType] = MappingProxyType(
    {
        Readiness: "boundary_admission",
        Admission: "boundary_admission",
        Completion: "boundary_completion",
    }
)


@dataclass(frozen=True)
class BoundaryRequest:
    unit: str
    step: Step

    @property
    def boundary(self) -> Boundary:
        return self.step.boundary

    @property
    def point(self) -> Point | None:
        return _POINT[type(self.step)]


def parse_request(unit: str, boundary: str, point: str | None) -> BoundaryRequest:
    """The single checkpoint for the WS-06 point rules; raises `BoundaryError`."""
    if not _UNIT.fullmatch(unit):
        raise BoundaryError("unit", "must be a LIT unit id")
    if boundary not in BOUNDARIES:
        raise BoundaryError("boundary", f"must be one of {', '.join(BOUNDARIES)}")
    step = _STEPS.get((boundary, point))
    if step is None:
        rule = "omits --point" if boundary in ("prepare", "develop") else "requires before|after"
        raise BoundaryError("point", f"{boundary} {rule}")
    return BoundaryRequest(unit, step)


# --- requirements ------------------------------------------------------------------------


@dataclass(frozen=True)
class Requirement:
    name: str
    source: Source


def _required(*pairs: tuple[str, Source]) -> tuple[Requirement, ...]:
    return tuple(Requirement(name, source) for name, source in pairs)


_PUBLISH_BEFORE = _required(
    ("revision", "check"),
    ("local_only", "check"),
    ("review_inputs", "review"),
    ("review_request", "review"),
)
_INTEGRATE_BEFORE = _required(
    ("authority", "lit"),
    ("review_verdict", "review"),
    ("head_base", "remote"),
    ("pr_checks", "ci"),
    ("merge_door", "door"),
)
# WS-06 required observations. A completion carries every admission observation plus the
# actual action readback, so the record a `before` check emits can satisfy none of them.
_REQUIREMENTS: Mapping[Step, tuple[Requirement, ...]] = MappingProxyType(
    {
        Readiness("prepare"): _required(
            ("authority", "lit"),
            ("worktree", "lit"),
            ("baseline", "lit"),
            ("guidance", "lit"),
            ("verification_plan", "lit"),
        ),
        Readiness("develop"): _required(
            ("staged_scope", "check"),
            ("lint_format", "check"),
            ("behavior_proof", "check"),
            ("unrelated_work", "check"),
        ),
        Admission("publish"): _PUBLISH_BEFORE,
        Completion("publish"): _PUBLISH_BEFORE
        + _required(("remote_head", "remote"), ("pull_request", "remote")),
        Admission("integrate"): _INTEGRATE_BEFORE,
        Completion("integrate"): _INTEGRATE_BEFORE
        + _required(("landing", "remote"), ("own_main", "ci")),
    }
)
# What an absent or not-yet-adaptable observation from each producer holds on.
_HELD_REASON: Mapping[Source, ReasonCode] = MappingProxyType(
    {
        "check": "check_pending",
        "lit": "authority_unavailable",
        "review": "review_blocked",
        "ci": "check_pending",
        "remote": "check_pending",
        "door": "ownership_conflict",
    }
)


def requirements(step: Step) -> tuple[Requirement, ...]:
    return _REQUIREMENTS[step]


# --- facts and decisions -----------------------------------------------------------------


@dataclass(frozen=True)
class Reference:
    """An immutable WS-08 reference to the producer record behind an observation."""

    uri: str
    sha256: str
    bytes: int

    def to_json(self) -> dict[str, object]:
        return {"uri": self.uri, "sha256": self.sha256, "bytes": self.bytes}


@dataclass(frozen=True)
class Verified:
    record: Reference


@dataclass(frozen=True)
class Shortfall:
    result: Literal["held", "failed", "error"]
    reason: ReasonCode


Observed = Verified | Shortfall


@dataclass(frozen=True)
class Subject:
    repository: str
    head: str
    base: str | None


@dataclass(frozen=True)
class BoundaryFacts:
    """Observations by requirement name; a requirement with no entry is unmet."""

    selection: ProfileSelection
    subject: Subject
    observations: Mapping[str, Observed]


@dataclass(frozen=True)
class BoundaryDecision:
    """`record_type` is set only for `passed`: it names the one record this check may emit."""

    result: Result
    reasons: tuple[ReasonCode, ...]
    record_type: RecordType | None


def _selection_shortfall(selection: ProfileSelection) -> tuple[Shortfall, ...]:
    """Only the trial profile is governed by these boundaries; legacy work keeps its own."""
    reasons = cast(
        tuple[ReasonCode, ...],
        {"trial": (), "legacy": ("policy_mismatch",), "held": selection.reasons}[selection.kind],
    )
    return tuple(Shortfall("held", reason) for reason in reasons)


_SEVERITY: tuple[Result, ...] = ("error", "failed", "held", "passed")


def evaluate_boundary(request: BoundaryRequest, facts: BoundaryFacts) -> BoundaryDecision:
    """Pure: the boundary's result from its observations; requesting an action proves nothing."""
    # [LAW:dataflow-not-control-flow] every requirement is resolved the same way; an absent
    # observation is the producer's held reason, not a skipped check.
    shortfalls = _selection_shortfall(facts.selection) + tuple(
        observed
        for observed in (
            facts.observations.get(req.name, Shortfall("held", _HELD_REASON[req.source]))
            for req in requirements(request.step)
        )
        if isinstance(observed, Shortfall)
    )
    levels: set[Result] = {"passed", *(s.result for s in shortfalls)}
    result: Result = next(level for level in _SEVERITY if level in levels)
    return BoundaryDecision(
        result,
        tuple(dict.fromkeys(s.reason for s in shortfalls)),
        _RECORD_TYPE[type(request.step)] if result == "passed" else None,
    )


def boundary_record(
    request: BoundaryRequest,
    facts: BoundaryFacts,
    record_type: RecordType,
    *,
    created_at: str,
) -> dict[str, object]:
    """Pure: the WS-08 record a passing check publishes; its record type tells admission
    from completion, and its inputs bind every producer record it consumed."""
    body: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": record_type,
        "policy_id": PROFILE_ID,
        "policy_version": POLICY_VERSION,
        "unit_id": request.unit,
        "producer": {"tool": "codex_context_guard workflow", "version": str(SCHEMA_VERSION)},
        "created_at": created_at,
        "subject": {
            "repository": facts.subject.repository,
            "head": facts.subject.head,
            "base": facts.subject.base,
        },
        "inputs": {
            "boundary": request.boundary,
            "point": request.point,
            "observations": {
                name: observed.record.to_json()
                for name, observed in sorted(facts.observations.items())
                if isinstance(observed, Verified)
            },
        },
        "result": "passed",
        "artifacts": [],
        "supersedes": [],
        "limits": ["Inactive until WP-17 activation; admission is never completion"],
    }
    record_id = f"{request.unit}.{request.boundary}.{canonical_digest(body)[:16]}"
    return {"record_id": record_id, **body}


# --- adapters (effects) ------------------------------------------------------------------


def _no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    doc = dict(pairs)
    if len(doc) != len(pairs):
        raise BoundaryError("manifest", "duplicate key")
    return doc


def _reject_float(text: str) -> NoReturn:
    raise BoundaryError("manifest", f"float {text} is not allowed")


def _object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise BoundaryError(field, "must be an object")
    return cast(dict[str, object], value)


def _exact_keys(doc: dict[str, object], expected: tuple[str, ...], field: str) -> None:
    if set(doc) != set(expected):
        raise BoundaryError(field, f"must have exactly {', '.join(expected)}")


def _matching(value: object, pattern: re.Pattern[str], field: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise BoundaryError(field, f"must match {pattern.pattern}")
    return value


def _reference(value: object, field: str) -> Reference:
    doc = _object(value, field)
    _exact_keys(doc, ("uri", "sha256", "bytes"), field)
    uri, size = doc["uri"], doc["bytes"]
    if not isinstance(uri, str) or not Path(uri).is_absolute():
        raise BoundaryError(field + ".uri", "must be an absolute path")
    if type(size) is not int or size < 0:
        raise BoundaryError(field + ".bytes", "must be a nonnegative integer")
    return Reference(uri, _matching(doc["sha256"], _SHA256, field + ".sha256"), size)


@dataclass(frozen=True)
class Claim:
    """One manifest observation: the producer it names and the record it points at."""

    requirement: Requirement
    record: Reference


@dataclass(frozen=True)
class BoundaryManifest:
    subject: Subject
    claims: tuple[Claim, ...]


def parse_manifest(raw: bytes, request: BoundaryRequest) -> BoundaryManifest:
    """The single checkpoint for a boundary manifest; it must describe exactly `request`."""
    try:
        doc = _object(
            json.loads(raw, object_pairs_hook=_no_duplicates, parse_float=_reject_float),
            "manifest",
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BoundaryError("manifest", f"not UTF-8 JSON: {exc}") from exc
    _exact_keys(
        doc,
        ("schema_version", "unit_id", "boundary", "point", "subject", "observations"),
        "manifest",
    )
    if type(doc["schema_version"]) is not int or doc["schema_version"] != SCHEMA_VERSION:
        raise BoundaryError("manifest.schema_version", f"unsupported; expected {SCHEMA_VERSION}")
    for name, expected in (
        ("unit_id", request.unit),
        ("boundary", request.boundary),
        ("point", request.point),
    ):
        if doc[name] != expected:
            raise BoundaryError(f"manifest.{name}", f"must be {expected!r} for this check")
    subject = _object(doc["subject"], "manifest.subject")
    _exact_keys(subject, ("repository", "head", "base"), "manifest.subject")
    repository, base = subject["repository"], subject["base"]
    if not isinstance(repository, str) or not repository:
        raise BoundaryError("manifest.subject.repository", "must be a nonempty string")
    by_name = {req.name: req for req in requirements(request.step)}
    claims: list[Claim] = []
    for name, value in _object(doc["observations"], "manifest.observations").items():
        field = f"manifest.observations.{name}"
        requirement = by_name.get(name)
        if requirement is None:
            raise BoundaryError(field, f"is not a {request.boundary} requirement")
        claim = _object(value, field)
        _exact_keys(claim, ("source", "record"), field)
        # [LAW:single-enforcer] the producer kind is fixed by the requirement, so a record
        # from another producer (an admission receipt offered as a remote readback) rejects.
        if claim["source"] != requirement.source:
            raise BoundaryError(field + ".source", f"must be {requirement.source}")
        claims.append(Claim(requirement, _reference(claim["record"], field + ".record")))
    return BoundaryManifest(
        Subject(
            repository,
            _matching(subject["head"], _GIT_OID, "manifest.subject.head"),
            None if base is None else _matching(base, _GIT_OID, "manifest.subject.base"),
        ),
        tuple(claims),
    )


_CHECK_RESULT: Mapping[str, Shortfall] = MappingProxyType(
    {
        "failed": Shortfall("failed", "check_failed"),
        "held": Shortfall("held", "check_pending"),
        "error": Shortfall("error", "artifact_unavailable"),
    }
)


def observe(claim: Claim, request: BoundaryRequest, subject: Subject) -> Observed:
    """[LAW:effects-at-boundaries] read and verify the one producer record a claim names."""
    record = claim.record
    try:
        raw = Path(record.uri).read_bytes()
    except OSError:
        return Shortfall("error", "artifact_unavailable")
    if len(raw) != record.bytes or hashlib.sha256(raw).hexdigest() != record.sha256:
        return Shortfall("error", "artifact_unavailable")
    if claim.requirement.source != "check":
        # No adapter yet validates this producer's native record, so it cannot verify.
        return Shortfall("held", _HELD_REASON[claim.requirement.source])
    receipt = load_receipt(raw)
    if isinstance(receipt, ReceiptDefect):
        raise BoundaryError(f"observations.{claim.requirement.name}.record", str(receipt))
    manifest = receipt.manifest
    if (manifest.unit, manifest.repository, manifest.head) != (
        request.unit,
        subject.repository,
        subject.head,
    ) or manifest.material_base not in (None, subject.base):
        return Shortfall("held", "binding_stale")
    return _CHECK_RESULT.get(receipt.result, Verified(record))


def observe_selection(unit: str, repository: str) -> ProfileSelection:
    """[LAW:effects-at-boundaries] the WP-02 selection from the tracked policy and canonical
    activation. LIT trial relation and native admission have no adapter yet, so they stay
    unknown and enrolled work holds rather than passing on an unread authority."""
    try:
        raw: bytes | None = POLICY_PATH.read_bytes()
    except FileNotFoundError:
        raw = None
    facts = SelectionFacts(
        repository=repository,
        unit=unit,
        arc=None,
        trial_relation="unknown",
        admission="unknown",
        activation=read_activation(),
    )
    return select_profile(load_policy(raw), facts)


def publish(record: dict[str, object]) -> dict[str, str]:
    """[LAW:effects-at-boundaries] write one immutable receipt; never overwrite another."""
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    path = RECEIPT_ROOT / f"{record['record_id']}.json"
    RECEIPT_ROOT.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(raw)
    return {"uri": str(path), "sha256": hashlib.sha256(raw).hexdigest()}


@dataclass(frozen=True)
class Observation:
    """One boundary's last verified receipt in the store."""

    boundary: Boundary
    created_at: str
    state: dict[str, object]


def _stored(path: Path, unit: str) -> Observation | None:
    """A stored receipt for `unit`, None for another unit's; a corrupt one raises."""
    raw = path.read_bytes()
    try:
        doc = _object(json.loads(raw, object_pairs_hook=_no_duplicates), str(path))
        inputs = _object(doc["inputs"], f"{path}.inputs")
        step = _STEPS[(cast(str, inputs["boundary"]), cast("str | None", inputs["point"]))]
        if doc["record_type"] != _RECORD_TYPE[type(step)] or doc["result"] != "passed":
            raise BoundaryError(str(path), "record type or result disagrees with its step")
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BoundaryError(str(path), f"not a boundary receipt: {exc}") from exc
    if doc.get("unit_id") != unit:
        return None
    return Observation(
        step.boundary,
        str(doc["created_at"]),
        {
            "record_type": doc["record_type"],
            "point": inputs["point"],
            "receipt": {"uri": str(path), "sha256": hashlib.sha256(raw).hexdigest()},
        },
    )


def observed_state(unit: str) -> dict[str, object]:
    """Each boundary's last verified receipt for `unit`, or `unknown`; reads only."""
    paths = sorted(RECEIPT_ROOT.glob("*.json"))  # an absent store globs to no receipts
    found = [obs for obs in (_stored(path, unit) for path in paths) if obs is not None]
    latest: dict[str, object] = {boundary: "unknown" for boundary in BOUNDARIES}
    for obs in sorted(found, key=lambda o: o.created_at):
        latest[obs.boundary] = obs.state
    return latest


# --- CLI ---------------------------------------------------------------------------------

_EXIT: Mapping[Result, int] = MappingProxyType({"passed": 0, "held": 3, "failed": 4, "error": 5})
_NEXT_ACTION: Mapping[Result, str] = MappingProxyType(
    {
        "passed": "Proceed with the action this receipt names; an admission is not completion.",
        "held": "Resolve the prerequisites named in reason_codes, then check again.",
        "failed": "Correct the failed verification and rerun it before checking again.",
        "error": "Restore the unavailable record or receipt store and reconcile before retrying.",
    }
)


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise BoundaryError("invocation", message)


def _cli() -> argparse.ArgumentParser:
    parser = _Parser(prog="codex_context_guard.py workflow", add_help=False)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    status = commands.add_parser("status", add_help=False)
    status.add_argument("--unit", required=True)
    check = commands.add_parser("check", add_help=False)
    check.add_argument("--unit", required=True)
    check.add_argument("--boundary", required=True)
    check.add_argument("--manifest", required=True, type=Path)
    check.add_argument("--point")
    return parser


def _wire(
    unit: str | None,
    request: BoundaryRequest | None,
    result: Result,
    reasons: tuple[ReasonCode, ...],
    receipt: dict[str, str] | None,
    next_action: str,
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "policy_id": PROFILE_ID,
        "policy_version": POLICY_VERSION,
        "unit_id": unit,
        "boundary": None if request is None else request.boundary,
        "point": None if request is None else request.point,
        "result": result,
        "reason_codes": list(reasons),
        "receipt": receipt,
        "next_action": next_action,
    }


def _check(
    unit: str, boundary: str, point: str | None, manifest_path: Path
) -> tuple[dict[str, object], int]:
    request = parse_request(unit, boundary, point)
    manifest = parse_manifest(manifest_path.read_bytes(), request)
    facts = BoundaryFacts(
        selection=observe_selection(request.unit, manifest.subject.repository),
        subject=manifest.subject,
        observations={
            claim.requirement.name: observe(claim, request, manifest.subject)
            for claim in manifest.claims
        },
    )
    decision = evaluate_boundary(request, facts)
    if decision.record_type is None:
        return _wire(
            unit, request, decision.result, decision.reasons, None, _NEXT_ACTION[decision.result]
        ), _EXIT[decision.result]
    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    record = boundary_record(request, facts, decision.record_type, created_at=created_at)
    try:
        receipt = publish(record)
    except OSError as exc:
        print(f"workflow check: receipt not published: {exc}", file=sys.stderr)
        return _wire(
            unit, request, "error", ("publication_uncertain",), None, _NEXT_ACTION["error"]
        ), _EXIT["error"]
    return _wire(unit, request, "passed", (), receipt, _NEXT_ACTION["passed"]), _EXIT["passed"]


def _status(unit: str) -> tuple[dict[str, object], int]:
    if not _UNIT.fullmatch(unit):
        raise BoundaryError("unit", "must be a LIT unit id")
    try:
        state = observed_state(unit)
    except (OSError, BoundaryError) as exc:
        print(f"workflow status: receipt store unreadable: {exc}", file=sys.stderr)
        return _wire(
            unit, None, "error", ("artifact_unavailable",), None, _NEXT_ACTION["error"]
        ), _EXIT["error"]
    output = _wire(
        unit, None, "passed", (), None, "Read-only status; run workflow check at a boundary."
    )
    return {**output, "observed_state": state}, 0


def main(argv: list[str]) -> int:
    """`workflow status|check`: one JSON object on stdout; exits 0/2/3/4/5 (WS-06)."""
    unit: str | None = None
    try:
        args = _cli().parse_args(argv)
        unit = args.unit
        output, code = (
            _status(args.unit)
            if args.command == "status"
            else _check(args.unit, args.boundary, args.point, args.manifest)
        )
    except (BoundaryError, OSError) as exc:
        print(f"workflow: invalid input: {exc}", file=sys.stderr)
        output, code = (
            _wire(
                unit,
                None,
                "error",
                ("invalid_input",),
                None,
                "Correct the invocation or manifest field named on stderr.",
            ),
            2,
        )
    print(json.dumps(output, sort_keys=False))
    return code
