"""WO-U03 / WP-02 — trial profile selection (spec WS-01, WS-18; verification WT-01).

Only a unit enrolled in the accepted, activated `arhugula-trial-v1` policy with every
live authority confirmed selects the trial; unrelated work keeps legacy; an enrolled
unit whose policy/activation/authority state is missing, malformed or mismatched holds.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from tools import ci_bookkeeping_diff
from tools.workflow_policy import (
    ACTIVATION_PATH,
    REPOSITORY,
    Activation,
    ActivationAbsent,
    ActivationDefect,
    PolicyDefect,
    PolicyError,
    SelectionFacts,
    load_policy,
    parse_activation,
    parse_policy,
    read_activation,
    refresh_rule,
    select_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACKED_POLICY = REPO_ROOT / ".harness" / "workflow-policy.json"
UNIT = "arhugula-harness-trial-193.7x7.gdh"
ARC = "wo-u03-workflow-policy"


def _policy_doc(**overrides: object) -> dict:
    doc = {
        "schema_version": 1,
        "policy_id": "arhugula-trial-v1",
        "policy_version": 1,
        "lit_project": "arhugula",
        "trial_root": "arhugula-harness-trial-193",
        "eligible_units": [{"unit": UNIT, "arc": ARC}],
        "boundary_rules": {},
        "check_inputs": {},
        "artifact_roots": {},
        "review_rules": {},
        "compatibility": {"phase_record_versions": [1]},
    }
    doc.update(overrides)
    return doc


def _raw(doc: dict) -> bytes:
    return json.dumps(doc).encode()


POLICY = parse_policy(_raw(_policy_doc()))


def _activation(**overrides: object) -> dict:
    doc = {
        "policy_id": "arhugula-trial-v1",
        "policy_version": 1,
        "policy_digest": POLICY.digest,
        "root_revision": "a" * 40,
        "product_revision": "b" * 40,
        "carrier_inventory_digest": "c" * 64,
        "adoption_evidence": "lit:arhugula-harness-trial-193.99c.1zo",
        "prior_policy": "legacy",
    }
    doc.update(overrides)
    return doc


ACTIVE = parse_activation(_raw(_activation()))
ELIGIBLE = SelectionFacts(
    repository=REPOSITORY,
    unit=UNIT,
    arc=ARC,
    trial_relation="confirmed",
    admission="confirmed",
    activation=ACTIVE,
)


# --- WT-01 selection table ------------------------------------------------------------


def test_trial_selection_requires_all_authorities() -> None:
    selection = select_profile(POLICY, ELIGIBLE)
    assert (selection.kind, selection.reasons, selection.unknown) == ("trial", (), ())


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ({"repository": "someone/fork"}, "identity_mismatch"),
        ({"arc": "another-arc"}, "identity_mismatch"),
        ({"trial_relation": "contradicted"}, "authority_changed"),
        ({"trial_relation": "unknown"}, "authority_unavailable"),
        ({"admission": "unknown"}, "authority_unavailable"),
        # The ticket may claim admission; a failed technical receipt still wins.
        ({"admission": "contradicted"}, "authority_changed"),
        ({"activation": ActivationDefect("policy_digest: missing")}, "policy_mismatch"),
        ({"activation": parse_activation(_raw(_activation(policy_version=2)))}, "policy_mismatch"),
        (
            {"activation": parse_activation(_raw(_activation(policy_digest="d" * 64)))},
            "policy_mismatch",
        ),
    ],
)
def test_enrolled_mismatch_holds_instead_of_falling_back_to_legacy(
    change: dict, reason: str
) -> None:
    selection = select_profile(POLICY, replace(ELIGIBLE, **change))
    assert selection.kind == "held"
    assert reason in selection.reasons


def test_unknown_live_facts_stay_visible_on_the_hold() -> None:
    facts = replace(ELIGIBLE, arc=None, trial_relation="unknown", admission="unknown")
    selection = select_profile(POLICY, facts)
    assert selection.kind == "held"
    assert selection.unknown == ("arc", "trial_relation", "admission")


def test_unrelated_task_keeps_legacy() -> None:
    facts = replace(ELIGIBLE, unit="arhugula-cli-usage-pq2", trial_relation="contradicted")
    assert select_profile(POLICY, facts).kind == "legacy"


def test_trial_related_unit_missing_from_the_allowlist_holds() -> None:
    # Every live authority confirmed, but the accepted policy does not enroll the unit.
    facts = replace(ELIGIBLE, unit="arhugula-harness-trial-193.7x7.9tj")
    selection = select_profile(POLICY, facts)
    assert (selection.kind, selection.reasons) == ("held", ("policy_mismatch",))


def test_unverified_relation_of_an_unenrolled_unit_holds_and_stays_visible() -> None:
    facts = replace(ELIGIBLE, unit="arhugula-cli-usage-pq2", trial_relation="unknown")
    selection = select_profile(POLICY, facts)
    assert selection.kind == "held"
    assert "authority_unavailable" in selection.reasons
    assert selection.unknown == ("trial_relation",)


def test_inactive_policy_leaves_enrolled_units_on_legacy() -> None:
    # Before the coherent rollout publishes an activation receipt the old workflow governs.
    assert select_profile(POLICY, replace(ELIGIBLE, activation=ActivationAbsent())).kind == "legacy"


@pytest.mark.parametrize("raw", [None, b"", b"{not json", _raw(_policy_doc(policy_version=2))])
def test_missing_or_malformed_policy_holds_a_trial_related_unit(raw: bytes | None) -> None:
    policy = load_policy(raw)
    assert isinstance(policy, PolicyDefect)
    assert select_profile(policy, ELIGIBLE).kind == "held"
    assert select_profile(policy, replace(ELIGIBLE, trial_relation="unknown")).kind == "held"
    assert select_profile(policy, replace(ELIGIBLE, trial_relation="contradicted")).kind == "legacy"


def test_uncommitted_policy_edit_cannot_self_authorize() -> None:
    # A local edit enrolling a new unit changes the digest the activation does not name.
    edited = parse_policy(
        _raw(
            _policy_doc(
                eligible_units=[
                    {"unit": UNIT, "arc": ARC},
                    {"unit": UNIT + "x", "arc": "self-granted"},
                ]
            )
        )
    )
    facts = replace(ELIGIBLE, unit=UNIT + "x", arc="self-granted")
    selection = select_profile(edited, facts)
    assert selection.kind == "held"
    assert "policy_mismatch" in selection.reasons


def test_branch_env_and_flag_spoofing_cannot_select_trial(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for name in ("ARHUGULA_WORKFLOW_PROFILE", "WORKFLOW_PROFILE", "TRIAL", "GIT_BRANCH"):
        monkeypatch.setenv(name, "arhugula-trial-v1")
    facts = replace(ELIGIBLE, unit="arhugula-harness-trial-193.trial-v1", arc=ARC)
    assert select_profile(POLICY, facts).kind == "held"
    # A caller-supplied root carrying its own receipt is never consulted.
    forged = tmp_path / ".local" / "buford-loop" / "workflow-activation.json"
    forged.parent.mkdir(parents=True)
    forged.write_bytes(_raw(_activation()))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    canonical = ACTIVATION_PATH.read_bytes() if ACTIVATION_PATH.is_file() else None
    assert read_activation() == parse_activation(canonical)
    assert forged != ACTIVATION_PATH


# --- strict parsing (WS-18 invalid input: the diagnostic names the field) --------------


@pytest.mark.parametrize(
    ("doc", "field"),
    [
        (_policy_doc(policy_id="arhugula-trial-v2"), "policy_id"),
        (_policy_doc(policy_version=2), "policy_version"),
        (_policy_doc(trial_root="arhugula-harness-trial-194"), "trial_root"),
        (_policy_doc(lit_project="other"), "lit_project"),
        (_policy_doc(schema_version=2), "schema_version"),
        (_policy_doc(extra=True), "extra"),
        ({k: v for k, v in _policy_doc().items() if k != "review_rules"}, "review_rules"),
        (
            _policy_doc(eligible_units=[{"unit": "arhugula-other-1.x", "arc": ARC}]),
            "eligible_units[0].unit",
        ),
        (_policy_doc(eligible_units=[{"unit": UNIT, "arc": "TBD"}]), "eligible_units[0].arc"),
        (_policy_doc(eligible_units=[{"unit": UNIT, "arc": "<arc>"}]), "eligible_units[0].arc"),
        (_policy_doc(eligible_units=[{"unit": UNIT, "arc": ARC}] * 2), "eligible_units[1].unit"),
        (_policy_doc(boundary_rules=[]), "boundary_rules"),
        (
            _policy_doc(compatibility={"phase_record_versions": [2]}),
            "compatibility.phase_record_versions",
        ),
        (_policy_doc(policy_version=True), "policy_version"),
    ],
)
def test_parse_policy_rejects_invalid_state_naming_the_field(doc: dict, field: str) -> None:
    with pytest.raises(PolicyError) as raised:
        parse_policy(_raw(doc))
    assert raised.value.field == field


def test_digest_covers_normalized_rule_content_not_byte_layout() -> None:
    pretty = json.dumps(_policy_doc(), indent=4, sort_keys=False).encode()
    assert parse_policy(pretty).digest == POLICY.digest
    changed = parse_policy(_raw(_policy_doc(review_rules={"max_passes": 5})))
    assert changed.digest != POLICY.digest


@pytest.mark.parametrize(
    "raw",
    [
        b"[]",
        _raw({k: v for k, v in _activation().items() if k != "prior_policy"}),
        _raw(_activation(policy_digest="short")),
    ],
)
def test_malformed_activation_is_a_typed_defect(raw: bytes) -> None:
    assert isinstance(parse_activation(raw), ActivationDefect)


def test_absent_activation_is_distinct_from_a_defect() -> None:
    assert parse_activation(None) == ActivationAbsent()
    assert isinstance(ACTIVE, Activation)


# --- the tracked policy and its CI treatment -------------------------------------------


def test_tracked_policy_is_the_exact_inactive_trial_profile() -> None:
    policy = parse_policy(TRACKED_POLICY.read_bytes())
    assert (policy.policy_id, policy.policy_version) == ("arhugula-trial-v1", 1)
    for unit in policy.eligible_units:
        facts = replace(ELIGIBLE, unit=unit.unit, arc=unit.arc, activation=ActivationAbsent())
        assert select_profile(policy, facts).kind == "legacy"


def test_a_policy_edit_never_takes_the_bookkeeping_fast_path() -> None:
    assert ci_bookkeeping_diff.classify([".harness/workflow-policy.json"]) is False


@pytest.mark.parametrize(
    ("policy", "activation", "rule"),
    [
        # WO-U23: only a receipt that activates this exact policy hands the refresh to the
        # door's per-landing selection; everything else keeps every enforcer on legacy
        (POLICY, ACTIVE, "trial"),
        (POLICY, ActivationAbsent(), "legacy"),
        (POLICY, ActivationDefect("activation: not JSON"), "legacy"),
        (POLICY, parse_activation(_raw(_activation(policy_digest="d" * 64))), "legacy"),
        (POLICY, parse_activation(_raw(_activation(policy_version=2))), "legacy"),
        (PolicyDefect("policy: missing"), ACTIVE, "legacy"),
    ],
)
def test_refresh_rule_is_trial_only_under_an_activation_of_this_policy(
    policy, activation, rule
) -> None:
    assert refresh_rule(policy, activation) == rule
