"""WO-U23 — WT-27 refused partial activation and WT-28 preservation-safe rollback (WS-17)."""

from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import workflow_adoption as wa

POLICY = wa.wp.parse_policy(
    json.dumps(
        {
            "schema_version": 1,
            "policy_id": "arhugula-trial-v1",
            "policy_version": 1,
            "lit_project": "arhugula",
            "trial_root": "arhugula-harness-trial-193",
            "eligible_units": [],
            "boundary_rules": {},
            "check_inputs": {},
            "artifact_roots": {},
            "review_rules": {},
            "compatibility": {"phase_record_versions": [1]},
        }
    ).encode()
)
INVENTORY = wa.Inventory("c" * 64, frozenset({"merge_door", "post-merge-refresh.sh"}))


def _consumer(name: str, *, accepts: str | None = POLICY.digest, inventory: str = "c" * 64):
    return wa.Consumer(name, accepts, inventory, retired_rule_present=False)


COHERENT = wa.AdoptionFacts(
    policy=POLICY,
    inventory=INVENTORY,
    consumers=(_consumer("merge_door"), _consumer("post-merge-refresh.sh")),
    active_writers=(),
    independent_review="confirmed",
    required_checks="confirmed",
    own_main="confirmed",
    activation_release="confirmed",
)


def test_only_a_released_reviewed_fully_checked_coherent_set_is_admissible():
    assert wa.evaluate_adoption(COHERENT) == wa.AdoptionDecision("validated", (), ())


@pytest.mark.parametrize(
    ("change", "state", "hold", "detail"),
    [
        # a stale refresh fixture still enforcing the retired rule
        (
            {
                "consumers": (
                    _consumer("merge_door"),
                    dataclasses.replace(
                        _consumer("post-merge-refresh.sh"), retired_rule_present=True
                    ),
                )
            },
            "inactive",
            "check_failed",
            "retired rule still enforced: post-merge-refresh.sh",
        ),
        # an omitted required carrier: observing fewer consumers cannot narrow the set
        (
            {"consumers": (_consumer("merge_door"),)},
            "inactive",
            "policy_mismatch",
            "required consumer missing: post-merge-refresh.sh",
        ),
        # one unrelated consumer, on the right digests, in place of the inventory's set
        (
            {"consumers": (_consumer("unrelated-only"),)},
            "inactive",
            "policy_mismatch",
            "consumer not in the inventory: unrelated-only",
        ),
        ({"consumers": ()}, "inactive", "policy_mismatch", "required consumer missing: merge_door"),
        (
            {"inventory": wa.Inventory("c" * 64, frozenset()), "consumers": ()},
            "inactive",
            "policy_mismatch",
            "no consumers inventoried",
        ),
        # absent or unparseable policy identity (no empty digest can stand in for one)
        (
            {"policy": wa.wp.PolicyDefect("policy: missing")},
            "inactive",
            "policy_mismatch",
            "policy unusable: policy: missing",
        ),
        (
            {
                "consumers": (
                    _consumer("merge_door", accepts=None),
                    _consumer("post-merge-refresh.sh"),
                )
            },
            "inactive",
            "policy_mismatch",
            "consumer not on the policy: merge_door",
        ),
        (
            {
                "consumers": (
                    _consumer("merge_door", accepts="b" * 64),
                    _consumer("post-merge-refresh.sh"),
                )
            },
            "inactive",
            "policy_mismatch",
            "consumer not on the policy: merge_door",
        ),
        # a consumer verified against another inventory version
        (
            {
                "consumers": (
                    _consumer("merge_door", inventory="d" * 64),
                    _consumer("post-merge-refresh.sh"),
                )
            },
            "inactive",
            "policy_mismatch",
            "consumer verified against another inventory: merge_door",
        ),
        ({"independent_review": "unknown"}, "prepared", "review_blocked", None),
        ({"required_checks": "unknown"}, "prepared", "check_pending", None),
        ({"required_checks": "contradicted"}, "prepared", "check_failed", None),
        ({"own_main": "unknown"}, "prepared", "check_pending", None),
        (
            {"active_writers": ("claude-coder:wo-u24",)},
            "validated",
            "ownership_conflict",
            "active writer: claude-coder:wo-u24",
        ),
        ({"activation_release": "unknown"}, "validated", "authority_unavailable", None),
    ],
)
def test_partial_adoption_is_held_and_never_reaches_active(change, state, hold, detail):
    decision = wa.evaluate_adoption(dataclasses.replace(COHERENT, **change))
    assert (decision.state, hold in decision.holds) == (state, True)
    assert detail is None or detail in decision.detail


def test_every_missing_gate_is_reported_at_once():
    decision = wa.evaluate_adoption(
        dataclasses.replace(
            COHERENT, consumers=(), independent_review="unknown", active_writers=("w",)
        )
    )
    assert decision.holds == ("policy_mismatch", "review_blocked", "ownership_conflict")


LEDGER = wa.Ledger(
    records=frozenset({"cmt-new-comment", "report-pass4", "closure-u23", "denial-push"}),
    counters={"source09.passes": 3, "u23.passes": 2, "lifetime.tokens": 912_000},
    current_authority="c12/cmt-ff89c11f",
)
PRIOR = (
    wa.CarrierVersion("merge_door", "cfe756e94831"),
    wa.CarrierVersion("CLAUDE.md", "42cd1892"),
)
RESTORED = {"merge_door": "cfe756e94831", "CLAUDE.md": "42cd1892"}
PRIOR_POLICY = wa.PolicyBinding("arhugula-legacy-v0", "no-receipt")


def _plan(intents=(), holds=(), ledger=LEDGER):
    return wa.plan_rollback(PRIOR_POLICY, PRIOR, holds, ledger, intents)


def test_a_rollback_plan_never_attests_completion():
    plan = _plan(intents=(wa.Intent("p", "failed"),))
    assert plan.state == "rollback_required"
    assert (plan.restore_policy, plan.restore_carriers) == (PRIOR_POLICY, PRIOR)


def test_rollback_reconciles_uncertain_intents_and_never_replays_them():
    plan = _plan(
        intents=(wa.Intent("merge-pr-1700", "uncertain"), wa.Intent("prompt-54", "confirmed"))
    )
    assert plan.reconcile == ("merge-pr-1700",)
    assert not hasattr(plan, "replay")
    unreconciled = wa.verify_rollback(plan, PRIOR_POLICY, RESTORED, {}, LEDGER)
    assert unreconciled == wa.RollbackVerification(
        "rollback_required", ("intent not reconciled: merge-pr-1700",)
    )
    assert wa.verify_rollback(
        plan, PRIOR_POLICY, RESTORED, {"merge-pr-1700": "confirmed"}, LEDGER
    ).state == ("rolled_back")


def test_only_a_verified_restoration_of_the_prior_set_is_rolled_back():
    plan = _plan()
    assert wa.verify_rollback(plan, PRIOR_POLICY, RESTORED, {}, LEDGER) == wa.RollbackVerification(
        "rolled_back", ()
    )
    half = wa.verify_rollback(plan, PRIOR_POLICY, {"merge_door": "cfe756e94831"}, {}, LEDGER)
    assert half.detail == ("carrier not restored: CLAUDE.md (want 42cd1892, observed nothing)",)
    wrong = wa.verify_rollback(plan, PRIOR_POLICY, {**RESTORED, "merge_door": "a1b2c3"}, {}, LEDGER)
    assert wrong.state == "rollback_required"
    unbound = wa.plan_rollback(PRIOR_POLICY, (), (), LEDGER, ())
    assert wa.verify_rollback(unbound, PRIOR_POLICY, {}, {}, LEDGER).detail == (
        "no prior carrier set bound",
    )


def test_rollback_retains_history_counters_and_authority_by_value():
    counters = dict(LEDGER.counters)
    adopted = dataclasses.replace(LEDGER, counters=counters)
    plan = _plan(ledger=adopted)
    counters["u23.passes"] = 0  # a later edit to the adopted ledger cannot reach the snapshot
    assert dict(plan.retained.counters) == dict(LEDGER.counters)
    assert plan.retained.records == LEDGER.records
    assert plan.retained.current_authority == LEDGER.current_authority

    grown = wa.Ledger(
        LEDGER.records | {"cmt-during-rollback"},
        {**LEDGER.counters, "u23.passes": 3},
        LEDGER.current_authority,
    )
    assert wa.verify_rollback(plan, PRIOR_POLICY, RESTORED, {}, grown).state == "rolled_back"


@pytest.mark.parametrize(
    ("after", "detail"),
    [
        (
            wa.Ledger(LEDGER.records - {"denial-push"}, LEDGER.counters, LEDGER.current_authority),
            "record lost: denial-push",
        ),
        (
            wa.Ledger(
                LEDGER.records, {**LEDGER.counters, "source09.passes": 0}, LEDGER.current_authority
            ),
            "counter reset: source09.passes",
        ),
        (
            wa.Ledger(
                LEDGER.records,
                {k: v for k, v in LEDGER.counters.items() if k != "lifetime.tokens"},
                LEDGER.current_authority,
            ),
            "counter reset: lifetime.tokens",
        ),
        (
            wa.Ledger(LEDGER.records, LEDGER.counters, "legacy-hil-hold"),
            "current authority not retained",
        ),
    ],
)
def test_a_rollback_that_loses_history_or_authority_is_not_rolled_back(after, detail):
    verification = wa.verify_rollback(_plan(), PRIOR_POLICY, RESTORED, {}, after)
    assert (verification.state, verification.detail) == ("rollback_required", (detail,))


def test_rollback_does_not_revive_a_hold_the_user_superseded():
    holds = (wa.Hold("hil-publication", "c12/cmt-0c59889e"), wa.Hold("u14-acceptance", None))
    assert _plan(holds=holds).restore_holds == ("u14-acceptance",)


@pytest.mark.parametrize(
    "observed",
    [None, wa.PolicyBinding("arhugula-legacy-v0", "receipt:" + "d" * 64)],
    ids=["unobserved", "trial-activation-still-bound"],
)
def test_rollback_needs_the_prior_policy_and_activation_binding_observed(observed):
    # WO-U23 F3: restored carriers and a retained ledger are not enough; WS-17 §19.3 restores
    # the prior controls and their versioned activation binding before `rolled_back`
    verification = wa.verify_rollback(_plan(), observed, RESTORED, {}, LEDGER)
    assert verification == wa.RollbackVerification(
        "rollback_required",
        (f"controls not restored: want {PRIOR_POLICY}, observed {observed}",),
    )


@pytest.mark.parametrize(("policy", "activation"), [("", "no-receipt"), ("legacy", " ")])
def test_a_rollback_cannot_bind_blank_controls(policy, activation):
    with pytest.raises(wa.wp.PolicyError):
        wa.PolicyBinding(policy, activation)


@pytest.mark.parametrize("digest", ["", "c" * 63, "C" * 64, "placeholder"])
def test_an_inventory_needs_a_sha256_identity(digest):
    # WO-U23 F2: a blank digest matched consumers carrying the same blank value and validated
    with pytest.raises(wa.wp.PolicyError, match=r"inventory\.digest"):
        wa.Inventory(digest, frozenset({"only"}))
