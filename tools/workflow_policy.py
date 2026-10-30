#!/usr/bin/env python3
"""WO-U03 / WP-02 — strict selection of the accepted trial workflow profile (spec WS-01).

`parse_policy` turns the tracked `.harness/workflow-policy.json` bytes into a
`WorkflowPolicy`; `parse_activation` does the same for the private activation receipt
that only the canonical orchestration root may publish (WS-01 §3.1, WP-17).
`select_profile` is a pure decision over that policy and `SelectionFacts` observed by
the caller's adapters from live LIT, native admission and Git:

- before an activation receipt exists every unit keeps `legacy` — the old workflow
  governs until the coherent rollout publishes one;
- a unit absent from `eligible_units` (or any unit when the policy is unreadable)
  keeps the unchanged `legacy` workflow only when LIT verifies it is unrelated to the
  trial root; trial-related or unverified work holds rather than silently leaving;
- an enrolled unit selects `trial` only when every authority is confirmed and the
  activation names exactly this policy's digest/version; anything missing, malformed,
  contradicted or mismatched is `held` with WS-18 reason codes, never a silent
  downgrade into another lifecycle.

`SelectionFacts` has no branch, label, environment or flag field, so none of those can
select the profile, and the activation is read from one fixed canonical path rather
than a caller-supplied root. Nothing here writes, activates or consults live services.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, cast

PROFILE_ID = "arhugula-trial-v1"
POLICY_VERSION = 1
SCHEMA_VERSION = 1
TRIAL_ROOT = "arhugula-harness-trial-193"
LIT_PROJECT = "arhugula"
REPOSITORY = "thestoryportal/arhugula-harness"
# The only root whose receipt can activate the profile (WS-01 §3.1): a known path, not
# a parameter, so no caller can point selection at a receipt it wrote itself.
CANONICAL_ROOT = Path("/home/robbo/Work/arhugula-omarchy")
ACTIVATION_PATH = CANONICAL_ROOT / ".local" / "buford-loop" / "workflow-activation.json"

_POLICY_FIELDS = (
    "schema_version",
    "policy_id",
    "policy_version",
    "lit_project",
    "trial_root",
    "eligible_units",
    "boundary_rules",
    "check_inputs",
    "artifact_roots",
    "review_rules",
    "compatibility",
)
# Owned by later packages (WP-03/04/09/13); this parser fixes only that each is an object.
_RULE_FIELDS = ("boundary_rules", "check_inputs", "artifact_roots", "review_rules")
_ACTIVATION_FIELDS = (
    "policy_id",
    "policy_version",
    "policy_digest",
    "root_revision",
    "product_revision",
    "carrier_inventory_digest",
    "adoption_evidence",
    "prior_policy",
)
_UNIT_ID = re.compile(re.escape(TRIAL_ROOT) + r"(\.[a-z0-9]+)+")
_ARC_ID = re.compile(r"[a-z0-9][a-z0-9._-]*")
_PLACEHOLDER = re.compile(r"(^|[._-])(tbd|todo|placeholder|example|xxx+)($|[._-])")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_GIT_SHA = re.compile(r"[0-9a-f]{40}")
_TEXT = re.compile(r"\S+")
_ACTIVATION_PROFILE = re.compile(re.escape(PROFILE_ID))

Observation = Literal["confirmed", "contradicted", "unknown"]
SelectionKind = Literal["trial", "legacy", "held"]
RefreshRule = Literal["legacy", "trial"]


class PolicyError(ValueError):
    """Invalid policy or activation input; `field` names the offending field (WS-18)."""

    def __init__(self, field: str, problem: str) -> None:
        super().__init__(f"{field}: {problem}")
        self.field = field


@dataclass(frozen=True)
class EligibleUnit:
    unit: str
    arc: str


@dataclass(frozen=True)
class WorkflowPolicy:
    policy_id: str
    policy_version: int
    eligible_units: tuple[EligibleUnit, ...]
    rules: Mapping[str, Mapping[str, object]]
    phase_record_versions: tuple[int, ...]
    digest: str

    def member(self, unit: str) -> EligibleUnit | None:
        return next((entry for entry in self.eligible_units if entry.unit == unit), None)


@dataclass(frozen=True)
class PolicyDefect:
    """The policy could not be read or parsed; enrolled work holds on it."""

    reason: str


@dataclass(frozen=True)
class Activation:
    policy_id: str
    policy_version: int
    policy_digest: str
    root_revision: str
    product_revision: str
    carrier_inventory_digest: str
    adoption_evidence: str
    prior_policy: str


@dataclass(frozen=True)
class ActivationAbsent:
    """No receipt has been published: the old workflow governs."""


@dataclass(frozen=True)
class ActivationDefect:
    reason: str


ActivationState = Activation | ActivationAbsent | ActivationDefect


@dataclass(frozen=True)
class SelectionFacts:
    """Live facts observed by adapters; `arc=None` means the unit's arc is unknown."""

    repository: str
    unit: str
    arc: str | None
    trial_relation: Observation
    admission: Observation
    activation: ActivationState


@dataclass(frozen=True)
class ProfileSelection:
    kind: SelectionKind
    reasons: tuple[str, ...]
    unknown: tuple[str, ...]


def _object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise PolicyError(field, "must be a JSON object")
    # Decoded JSON object keys are always strings.
    return cast(dict[str, object], value)


def _array(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise PolicyError(field, "must be a JSON array")
    return cast(list[object], value)


def _exact_keys(doc: dict[str, object], expected: tuple[str, ...], prefix: str = "") -> None:
    for key in sorted(set(doc) - set(expected)):
        raise PolicyError(prefix + key, "unknown field")
    for key in expected:
        if key not in doc:
            raise PolicyError(prefix + key, "missing")


def _int(value: object, field: str) -> int:
    # bool is an int subclass; `true` is not a version.
    if type(value) is not int:
        raise PolicyError(field, "must be an integer")
    return value


def _equal(value: object, expected: object, field: str) -> None:
    if value != expected or type(value) is not type(expected):
        raise PolicyError(field, f"must be {expected!r}")


def _matching(value: object, pattern: re.Pattern[str], field: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value) or _PLACEHOLDER.search(value):
        raise PolicyError(field, "malformed or placeholder identifier")
    return value


def _decode(raw: bytes, field: str) -> object:
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PolicyError(field, f"not JSON: {exc}") from exc


def canonical_digest(doc: dict[str, object]) -> str:
    # WS-08 serialization: UTF-8 JSON, sorted keys, no insignificant whitespace.
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


def _eligible(value: object) -> tuple[EligibleUnit, ...]:
    units: list[EligibleUnit] = []
    for index, item in enumerate(_array(value, "eligible_units")):
        prefix = f"eligible_units[{index}]."
        entry = _object(item, prefix.rstrip("."))
        _exact_keys(entry, ("unit", "arc"), prefix)
        unit = _matching(entry["unit"], _UNIT_ID, prefix + "unit")
        if any(existing.unit == unit for existing in units):
            raise PolicyError(prefix + "unit", "duplicate enrollment")
        units.append(EligibleUnit(unit, _matching(entry["arc"], _ARC_ID, prefix + "arc")))
    return tuple(units)


def _phase_record_versions(value: object) -> tuple[int, ...]:
    field = "compatibility.phase_record_versions"
    compatibility = _object(value, "compatibility")
    _exact_keys(compatibility, ("phase_record_versions",), "compatibility.")
    parsed = tuple(
        _int(version, field) for version in _array(compatibility["phase_record_versions"], field)
    )
    if POLICY_VERSION not in parsed:
        raise PolicyError(field, f"must accept policy_version {POLICY_VERSION}")
    return parsed


def parse_policy(raw: bytes) -> WorkflowPolicy:
    """The single checkpoint for policy bytes; raises `PolicyError` naming the field."""
    doc = _object(_decode(raw, "policy"), "policy")
    _exact_keys(doc, _POLICY_FIELDS)
    _equal(doc["schema_version"], SCHEMA_VERSION, "schema_version")
    _equal(doc["policy_id"], PROFILE_ID, "policy_id")
    _equal(doc["policy_version"], POLICY_VERSION, "policy_version")
    _equal(doc["lit_project"], LIT_PROJECT, "lit_project")
    _equal(doc["trial_root"], TRIAL_ROOT, "trial_root")
    rules = {field: MappingProxyType(_object(doc[field], field)) for field in _RULE_FIELDS}
    return WorkflowPolicy(
        policy_id=PROFILE_ID,
        policy_version=POLICY_VERSION,
        eligible_units=_eligible(doc["eligible_units"]),
        rules=MappingProxyType(rules),
        phase_record_versions=_phase_record_versions(doc["compatibility"]),
        digest=canonical_digest(doc),
    )


def load_policy(raw: bytes | None) -> WorkflowPolicy | PolicyDefect:
    """Policy bytes as read (None when the file is absent) to a policy or typed defect."""
    if raw is None:
        return PolicyDefect("policy: missing")
    try:
        return parse_policy(raw)
    except PolicyError as exc:
        return PolicyDefect(str(exc))


def parse_activation(raw: bytes | None) -> ActivationState:
    if raw is None:
        return ActivationAbsent()
    try:
        doc = _object(_decode(raw, "activation"), "activation")
        _exact_keys(doc, _ACTIVATION_FIELDS)
        return Activation(
            policy_id=_matching(doc["policy_id"], _ACTIVATION_PROFILE, "policy_id"),
            policy_version=_int(doc["policy_version"], "policy_version"),
            policy_digest=_matching(doc["policy_digest"], _SHA256, "policy_digest"),
            root_revision=_matching(doc["root_revision"], _GIT_SHA, "root_revision"),
            product_revision=_matching(doc["product_revision"], _GIT_SHA, "product_revision"),
            carrier_inventory_digest=_matching(
                doc["carrier_inventory_digest"], _SHA256, "carrier_inventory_digest"
            ),
            adoption_evidence=_matching(doc["adoption_evidence"], _TEXT, "adoption_evidence"),
            prior_policy=_matching(doc["prior_policy"], _TEXT, "prior_policy"),
        )
    except PolicyError as exc:
        return ActivationDefect(str(exc))


def read_activation() -> ActivationState:
    """[LAW:effects-at-boundaries] the one read of the canonical receipt."""
    # A symlink could redirect the canonical path to a receipt written elsewhere.
    if ACTIVATION_PATH.is_symlink():
        return ActivationDefect(f"{ACTIVATION_PATH}: symlink is not the canonical receipt")
    try:
        raw = ACTIVATION_PATH.read_bytes()
    except FileNotFoundError:
        return ActivationAbsent()
    except OSError as exc:
        return ActivationDefect(f"{ACTIVATION_PATH}: {exc}")
    return parse_activation(raw)


_OBSERVATION_REASON: Mapping[Observation, tuple[str, ...]] = MappingProxyType(
    {"confirmed": (), "contradicted": ("authority_changed",), "unknown": ("authority_unavailable",)}
)


def activation_binds(policy: WorkflowPolicy, activation: ActivationState) -> bool:
    """[LAW:single-enforcer] the one test that a published receipt activates this policy."""
    return isinstance(activation, Activation) and (
        activation.policy_id,
        activation.policy_version,
        activation.policy_digest,
    ) == (policy.policy_id, policy.policy_version, policy.digest)


def refresh_rule(policy: WorkflowPolicy | PolicyDefect, activation: ActivationState) -> RefreshRule:
    """Which rule governs the post-merge terminating refresh (WS-11, WS-17 §19.1).

    `legacy` until a receipt activates the tracked policy: every substantive merge owes a
    terminating refresh and the roadmap-status enforcers keep requiring it. `trial` once
    one does: the merge door applies `select_profile` to each landing, driving a legacy
    landing's refresh PR before it releases and giving a trial landing none, so the
    status enforcers stop demanding a refresh the door has already ruled on."""
    bound = isinstance(policy, WorkflowPolicy) and activation_binds(policy, activation)
    return "trial" if bound else "legacy"


def _enrolled_selection(
    policy: WorkflowPolicy, entry: EligibleUnit, facts: SelectionFacts
) -> ProfileSelection:
    reasons: list[str] = []
    if not activation_binds(policy, facts.activation):
        reasons.append("policy_mismatch")
    if facts.repository != REPOSITORY or (facts.arc is not None and facts.arc != entry.arc):
        reasons.append("identity_mismatch")
    reasons += _OBSERVATION_REASON[facts.trial_relation] + _OBSERVATION_REASON[facts.admission]
    unknown = tuple(
        name
        for name, is_unknown in (
            ("arc", facts.arc is None),
            ("trial_relation", facts.trial_relation == "unknown"),
            ("admission", facts.admission == "unknown"),
        )
        if is_unknown
    )
    if unknown and "authority_unavailable" not in reasons:
        reasons.append("authority_unavailable")
    return ProfileSelection("held" if reasons else "trial", tuple(dict.fromkeys(reasons)), unknown)


def _outside_policy(facts: SelectionFacts) -> ProfileSelection:
    """No usable enrollment: legacy only for work LIT verifies is unrelated to the trial."""
    if facts.trial_relation == "contradicted":
        return ProfileSelection("legacy", (), ())
    unknown = ("trial_relation",) if facts.trial_relation == "unknown" else ()
    return ProfileSelection(
        "held", ("policy_mismatch",) + _OBSERVATION_REASON[facts.trial_relation], unknown
    )


def select_profile(
    policy: WorkflowPolicy | PolicyDefect, facts: SelectionFacts
) -> ProfileSelection:
    """`trial`, `legacy` or `held` for one unit; pure, with no authority of its own."""
    if isinstance(policy, PolicyDefect):
        return _outside_policy(facts)
    if isinstance(facts.activation, ActivationAbsent):
        return ProfileSelection("legacy", (), ())
    entry = policy.member(facts.unit)
    if entry is None:
        return _outside_policy(facts)
    return _enrolled_selection(policy, entry, facts)
