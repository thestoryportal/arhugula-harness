#!/usr/bin/env python3
"""WO-U23 / WP-17 — the coherent adoption and rollback decisions of spec WS-17.

`evaluate_adoption` judges how far a carrier set has progressed through the WS-17 §19.2
states and every reason activation is held. It never activates: publishing the private
receipt (`workflow_policy.ACTIVATION_PATH`) stays a separate, last, authorized act, and
this module only says whether that act would be admissible. The set it judges is the
inventory's required consumers, bound to the inventory digest and the parsed policy: a
caller cannot narrow it by observing fewer consumers.

`plan_rollback` (§19.3) only plans: it binds the prior coherent carrier versions to
restore and a by-value snapshot of the adopted version's history, and stays
`rollback_required`. `verify_rollback` alone can return `rolled_back`, and only when the
restored carriers are observed at those versions, every uncertain intent has been
reconciled and the history after the transition still holds everything the snapshot did.
Neither input has a field for prior counters or a replay list, so rollback cannot reset a
budget, delete a record or re-send an uncertain merge or prompt. Holds the current user
authority superseded are not restored.

All functions are pure; adapters observe the facts. Reasons are WS-18 codes.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal

import workflow_policy as wp

AdoptionState = Literal[
    "inactive", "prepared", "validated", "active", "rollback_required", "rolled_back"
]
Observation = Literal["confirmed", "contradicted", "unknown"]
IntentOutcome = Literal["confirmed", "failed", "uncertain"]


@dataclass(frozen=True)
class Inventory:
    """The adoption inventory (WS-17 §19.1): its digest and the consumers it requires."""

    digest: str
    required: frozenset[str]


@dataclass(frozen=True)
class Consumer:
    """One observed carrier/enforcer: the policy digest it accepts (None if unmigrated) and
    the inventory digest it was verified against."""

    name: str
    accepts: str | None
    inventory: str
    retired_rule_present: bool  # e.g. a fixture or instruction still requiring a refresh PR


@dataclass(frozen=True)
class AdoptionFacts:
    policy: wp.WorkflowPolicy | wp.PolicyDefect
    inventory: Inventory
    consumers: tuple[Consumer, ...]
    active_writers: tuple[str, ...]
    independent_review: Observation
    required_checks: Observation
    own_main: Observation
    activation_release: Observation  # current user authority to activate this version


@dataclass(frozen=True)
class AdoptionDecision:
    state: AdoptionState  # the highest WS-17 state the facts prove; never `active`
    holds: tuple[str, ...]  # empty only when publishing the receipt would be admissible
    detail: tuple[str, ...]


# [LAW:one-source-of-truth] each observed fact maps to its WS-18 code in one table
_REVIEW = {"confirmed": (), "contradicted": ("review_blocked",), "unknown": ("review_blocked",)}
_CHECKS = {"confirmed": (), "contradicted": ("check_failed",), "unknown": ("check_pending",)}
_RELEASE = {
    "confirmed": (),
    "contradicted": ("authority_changed",),
    "unknown": ("authority_unavailable",),
}


def _consumer_detail(facts: AdoptionFacts) -> tuple[str, ...]:
    """Every way the observed consumers fail to be the inventory's set on this policy."""
    policy = facts.policy
    # [LAW:parse-dont-validate] only a parsed policy has a digest; a defect has a reason
    digest, unusable = (
        (None, (f"policy unusable: {policy.reason}",))
        if isinstance(policy, wp.PolicyDefect)
        else (policy.digest, ())
    )
    observed = {c.name for c in facts.consumers}
    required = facts.inventory.required
    return (
        unusable
        + ("no consumers inventoried",) * (not required)
        + tuple(f"required consumer missing: {name}" for name in sorted(required - observed))
        + tuple(f"consumer not in the inventory: {name}" for name in sorted(observed - required))
        + tuple(
            f"consumer verified against another inventory: {c.name}"
            for c in facts.consumers
            if c.inventory != facts.inventory.digest
        )
        + tuple(
            f"consumer not on the policy: {c.name}"
            for c in facts.consumers
            if digest is None or c.accepts != digest
        )
    )


def evaluate_adoption(facts: AdoptionFacts) -> AdoptionDecision:
    # [LAW:dataflow-not-control-flow] every gate is evaluated every time; the facts decide
    mismatch = _consumer_detail(facts)
    stale = tuple(
        f"retired rule still enforced: {c.name}" for c in facts.consumers if c.retired_rule_present
    )
    prepared_holds = ("policy_mismatch",) * bool(mismatch) + ("check_failed",) * bool(stale)
    validated_holds = (
        _REVIEW[facts.independent_review] + _CHECKS[facts.required_checks] + _CHECKS[facts.own_main]
    )
    activation_holds = ("ownership_conflict",) * bool(facts.active_writers) + _RELEASE[
        facts.activation_release
    ]
    state: AdoptionState = (
        "inactive" if prepared_holds else "prepared" if validated_holds else "validated"
    )
    detail = mismatch + stale + tuple(f"active writer: {writer}" for writer in facts.active_writers)
    holds = tuple(dict.fromkeys(prepared_holds + validated_holds + activation_holds))
    return AdoptionDecision(state, holds, detail)


@dataclass(frozen=True)
class Intent:
    """A remote or native action started under the adopted version (merge, prompt, push)."""

    intent_id: str
    outcome: IntentOutcome


@dataclass(frozen=True)
class Hold:
    hold_id: str
    superseded_by: str | None  # the current user authority that lifted it, if any


@dataclass(frozen=True)
class Ledger:
    """Durable history produced while adopted: comments, reports, passes, closures, denials,
    goal-lineage receipts and lifetime totals. Rollback carries it forward as-is."""

    records: frozenset[str]
    counters: Mapping[str, int]
    current_authority: str


@dataclass(frozen=True)
class CarrierVersion:
    """One carrier/enforcer of the prior coherent set, at the version rollback restores."""

    name: str
    version: str


@dataclass(frozen=True)
class RollbackPlan:
    state: AdoptionState  # always `rollback_required`: a plan restores nothing by itself
    restore_policy: str
    restore_carriers: tuple[CarrierVersion, ...]
    restore_holds: tuple[str, ...]
    retained: Ledger  # a by-value snapshot; later edits to the adopted ledger do not reach it
    reconcile: tuple[str, ...]  # observe actual outcome first; never replayed


@dataclass(frozen=True)
class RollbackVerification:
    state: AdoptionState  # `rolled_back` only when `detail` is empty
    detail: tuple[str, ...]


def _snapshot(ledger: Ledger) -> Ledger:
    return Ledger(
        records=ledger.records,
        counters=MappingProxyType(dict(ledger.counters)),
        current_authority=ledger.current_authority,
    )


def plan_rollback(
    prior_policy: str,
    prior_carriers: tuple[CarrierVersion, ...],
    prior_holds: tuple[Hold, ...],
    ledger: Ledger,
    intents: tuple[Intent, ...],
) -> RollbackPlan:
    return RollbackPlan(
        state="rollback_required",
        restore_policy=prior_policy,
        restore_carriers=prior_carriers,
        # [LAW:one-source-of-truth] current user authority governs; a lifted hold stays lifted
        restore_holds=tuple(h.hold_id for h in prior_holds if h.superseded_by is None),
        retained=_snapshot(ledger),
        reconcile=tuple(i.intent_id for i in intents if i.outcome == "uncertain"),
    )


def verify_rollback(
    plan: RollbackPlan,
    observed_carriers: Mapping[str, str],
    reconciled: Mapping[str, IntentOutcome],
    ledger_after: Ledger,
) -> RollbackVerification:
    """[LAW:single-enforcer] the one place a rollback can be attested complete."""
    kept = plan.retained
    detail = (
        tuple(
            f"carrier not restored: {c.name} (want {c.version}, "
            f"observed {observed_carriers.get(c.name, 'nothing')})"
            for c in plan.restore_carriers
            if observed_carriers.get(c.name) != c.version
        )
        + ("no prior carrier set bound",) * (not plan.restore_carriers)
        + tuple(
            f"intent not reconciled: {intent}"
            for intent in plan.reconcile
            if reconciled.get(intent, "uncertain") == "uncertain"
        )
        + tuple(f"record lost: {r}" for r in sorted(kept.records - ledger_after.records))
        + tuple(
            f"counter reset: {name}"
            for name, value in sorted(kept.counters.items())
            if name not in ledger_after.counters or ledger_after.counters[name] < value
        )
        + ("current authority not retained",)
        * (ledger_after.current_authority != kept.current_authority)
    )
    return RollbackVerification("rollback_required" if detail else "rolled_back", detail)
