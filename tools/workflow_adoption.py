#!/usr/bin/env python3
"""WO-U23 / WP-17 — the coherent adoption and rollback decisions of spec WS-17.

`evaluate_adoption` judges how far a carrier set has progressed through the WS-17 §19.2
states and every reason activation is held. It never activates: publishing the private
receipt (`workflow_policy.ACTIVATION_PATH`) stays a separate, last, authorized act, and
this module only says whether that act would be admissible.

`plan_rollback` (§19.3) restores the prior coherent policy binding while carrying the
adopted version's history forward unchanged. Its inputs have no field for prior counters
or a replay list, so a plan cannot reset a budget, delete a record or re-send an uncertain
merge or prompt; uncertain intents are returned for reconciliation instead. Holds the
current user authority superseded are not restored.

Both functions are pure; adapters observe the facts. Reasons are WS-18 codes.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

AdoptionState = Literal[
    "inactive", "prepared", "validated", "active", "rollback_required", "rolled_back"
]
Observation = Literal["confirmed", "contradicted", "unknown"]
IntentOutcome = Literal["confirmed", "failed", "uncertain"]


@dataclass(frozen=True)
class Consumer:
    """One carrier/enforcer row; `accepts` is the policy digest it consumes, None if unmigrated."""

    name: str
    accepts: str | None
    retired_rule_present: bool  # e.g. a fixture or instruction still requiring a refresh PR


@dataclass(frozen=True)
class AdoptionFacts:
    policy_digest: str
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


def evaluate_adoption(facts: AdoptionFacts) -> AdoptionDecision:
    # [LAW:dataflow-not-control-flow] every gate is evaluated every time; the facts decide
    unmigrated = tuple(c.name for c in facts.consumers if c.accepts != facts.policy_digest)
    stale = tuple(c.name for c in facts.consumers if c.retired_rule_present)
    prepared_holds = ("policy_mismatch",) * bool(unmigrated or not facts.consumers) + (
        "check_failed",
    ) * bool(stale)
    validated_holds = (
        _REVIEW[facts.independent_review] + _CHECKS[facts.required_checks] + _CHECKS[facts.own_main]
    )
    activation_holds = ("ownership_conflict",) * bool(facts.active_writers) + _RELEASE[
        facts.activation_release
    ]
    state: AdoptionState = (
        "inactive" if prepared_holds else "prepared" if validated_holds else "validated"
    )
    detail = (
        tuple(f"consumer not on {facts.policy_digest[:12]}: {name}" for name in unmigrated)
        + tuple(f"retired rule still enforced: {name}" for name in stale)
        + tuple(f"active writer: {writer}" for writer in facts.active_writers)
        + ("no consumers inventoried",) * (not facts.consumers)
    )
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
class RollbackPlan:
    state: AdoptionState  # `rollback_required` until every uncertain intent is reconciled
    restore_policy: str
    restore_holds: tuple[str, ...]
    retained: Ledger
    reconcile: tuple[str, ...]  # observe actual outcome first; never replayed


def plan_rollback(
    prior_policy: str, prior_holds: tuple[Hold, ...], ledger: Ledger, intents: tuple[Intent, ...]
) -> RollbackPlan:
    reconcile = tuple(i.intent_id for i in intents if i.outcome == "uncertain")
    return RollbackPlan(
        state="rollback_required" if reconcile else "rolled_back",
        restore_policy=prior_policy,
        # [LAW:one-source-of-truth] current user authority governs; a lifted hold stays lifted
        restore_holds=tuple(h.hold_id for h in prior_holds if h.superseded_by is None),
        retained=ledger,
        reconcile=reconcile,
    )
