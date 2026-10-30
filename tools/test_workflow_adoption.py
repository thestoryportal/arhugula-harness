"""WO-U23 — WT-27 refused partial activation and WT-28 preservation-safe rollback (WS-17)."""

from __future__ import annotations

import dataclasses

import pytest
import workflow_adoption as wa

DIGEST = "a" * 64
COHERENT = wa.AdoptionFacts(
    policy_digest=DIGEST,
    consumers=(
        wa.Consumer("merge_door", DIGEST, retired_rule_present=False),
        wa.Consumer("post-merge-refresh.sh", DIGEST, retired_rule_present=False),
    ),
    active_writers=(),
    independent_review="confirmed",
    required_checks="confirmed",
    own_main="confirmed",
    activation_release="confirmed",
)


def test_only_a_released_reviewed_fully_checked_coherent_set_is_admissible():
    assert wa.evaluate_adoption(COHERENT) == wa.AdoptionDecision("validated", (), ())


@pytest.mark.parametrize(
    ("change", "state", "hold"),
    [
        # a stale refresh fixture still enforcing the retired rule
        (
            {"consumers": (wa.Consumer("test_merge_door", DIGEST, True),)},
            "inactive",
            "check_failed",
        ),
        # a missing consumer, and one still on the prior policy version
        ({"consumers": ()}, "inactive", "policy_mismatch"),
        ({"consumers": (wa.Consumer("merge_door", None, False),)}, "inactive", "policy_mismatch"),
        (
            {"consumers": (wa.Consumer("merge_door", "b" * 64, False),)},
            "inactive",
            "policy_mismatch",
        ),
        ({"independent_review": "unknown"}, "prepared", "review_blocked"),
        ({"required_checks": "unknown"}, "prepared", "check_pending"),
        ({"required_checks": "contradicted"}, "prepared", "check_failed"),
        ({"own_main": "unknown"}, "prepared", "check_pending"),
        ({"active_writers": ("claude-coder:wo-u24",)}, "validated", "ownership_conflict"),
        ({"activation_release": "unknown"}, "validated", "authority_unavailable"),
    ],
)
def test_partial_adoption_is_held_and_never_reaches_active(change, state, hold):
    decision = wa.evaluate_adoption(dataclasses.replace(COHERENT, **change))
    assert (decision.state, hold in decision.holds) == (state, True)


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


def test_rollback_reconciles_uncertain_intents_and_never_replays_them():
    plan = wa.plan_rollback(
        "arhugula-legacy-v0",
        (),
        LEDGER,
        (wa.Intent("merge-pr-1700", "uncertain"), wa.Intent("prompt-54", "confirmed")),
    )
    assert (plan.state, plan.reconcile) == ("rollback_required", ("merge-pr-1700",))
    assert not hasattr(plan, "replay")


def test_rollback_retains_history_counters_and_current_authority():
    plan = wa.plan_rollback("arhugula-legacy-v0", (), LEDGER, (wa.Intent("p", "failed"),))
    assert plan.state == "rolled_back"
    assert plan.restore_policy == "arhugula-legacy-v0"
    assert plan.retained == LEDGER  # no record dropped, no counter decremented or reset


def test_rollback_does_not_revive_a_hold_the_user_superseded():
    holds = (wa.Hold("hil-publication", "c12/cmt-0c59889e"), wa.Hold("u14-acceptance", None))
    plan = wa.plan_rollback("arhugula-legacy-v0", holds, LEDGER, ())
    assert plan.restore_holds == ("u14-acceptance",)
