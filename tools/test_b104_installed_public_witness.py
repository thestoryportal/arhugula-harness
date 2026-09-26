"""Pure checks of the B-104 installed witness fixture: its gates, config and verdict.

Nothing here bootstraps a harness, resumes a workflow or touches an installed venv. The
scenario itself is only ever exercised by the separately approved installed `run`.
"""

from __future__ import annotations

import copy
import json
import os
import signal
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import b104_installed_public_witness as w

REF = {
    "tenant": None,
    "workflow_id": w.WORKFLOW_ID,
    "run_id": "run-1",
    "record_count": 1,
    "latest_digest": "a" * 64,
    "snapshot_hash": "b" * 64,
}
CLAIM = {"phase": "started", "lease": "busy", "claim_sha256": "c" * 64}
REFUSED = {
    "outcome": "refused",
    "error_type": "harness_runtime.lifecycle.root_resume_admission.ResumeClaimRefusedError",
    "reason": "claim-refused",
    "body_marker_present": False,
    "ref": REF,
    "claim": {**CLAIM, "lease": "free"},
}
KILL_DIGEST = "d" * 64
# The digest the PARENT computed from the receipt it verified; every proved record binds it.
RECEIPT = "e" * 64
WRONG_RECEIPT = "1" * 64
A_PID = 4242
EXITED = {"exit": 0, "timeout": False, "output_ok": True, "kill": None}
KILLED = {"signal": "SIGKILL", "returncode": -signal.SIGKILL, "group_gone": True}
# Every phase the parent waits on to exit by itself (A is killed at its barrier).
EXITING_PHASES = [p for p in w.PHASES if p != "resume-a"]
VENV = "/venv"
SITE = f"{VENV}/lib/python3.12/site-packages"
# What the real prover emits: every entry is the shape `installed_origins` returns.
LOADED_BEFORE_BODY = w.MIN_LOADED_HARNESS_MODULES  # `installed_origins` imports every package
LOADED_AFTER_BODY = 12


def real_shape_origins() -> dict[str, dict[str, Any]]:
    """Per-package origin records shaped exactly like `installed_origins`' output."""
    origins: dict[str, dict[str, Any]] = {}
    for package in sorted(w.PACKAGES):
        files = [f"{SITE}/{package}/__init__.py", f"{SITE}/{package}/lifecycle.py"]
        origins[package] = {
            "record_path": f"{SITE}/{package}-0.0.0.dist-info/RECORD",
            "record_sha256": __import__("hashlib").sha256(package.encode()).hexdigest(),
            "python_files_checked": len(files),
            "verified_files": sorted(files),
        }
    return origins


def _provenance(receipt: str = RECEIPT) -> dict[str, Any]:
    """What an installed, isolated child records; `sys.flags` values are the int 1, not True."""
    return {
        "interpreter": {
            "isolated": 1,
            "no_user_site": 1,
            "prefix": VENV,
            "executable": f"{VENV}/bin/python",
        },
        "installation_receipt_sha256": receipt,
        "installed_origins": real_shape_origins(),
    }


def _ok(phase: str, observed: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": phase,
        "ok": True,
        "observed": observed,
        "provenance": _provenance(),
        "loaded_harness_modules": LOADED_AFTER_BODY,
    }


def evaluate(evidence: dict[str, Any], receipt: str = RECEIPT) -> dict[str, Any]:
    return w.evaluate(evidence, expected_receipt_sha256=receipt)  # type: ignore[return-value]


def passing_evidence() -> dict[str, Any]:
    """Evidence shaped like a complete, correct run; every mutation below breaks one fact."""
    audit = {
        "action": "abandon",
        "action_id": "b104w-abandon-1",
        "stopped_services_digest": KILL_DIGEST,
    }
    inventory = {"journal": "f" * 64}
    return {
        "runs": {
            "capture": dict(EXITED),
            "resume-a": {
                "pid": A_PID,
                "pgid": A_PID,
                "exit": None,
                "timeout": False,
                "output_ok": True,
                "barrier_entered": True,
                "kill": dict(KILLED),
                "marker": {"pid": A_PID, "pgid": A_PID, "step_id": "step-0"},
            },
            "observe-held": dict(EXITED),
            "resume-b": dict(EXITED),
            "recover": dict(EXITED),
            "resume-after-abandon": dict(EXITED),
            "webhooks_after_capture": 1,
        },
        "results": {
            "capture": _ok(
                "capture",
                {
                    "status": "paused",
                    "depth": 0,
                    "ref": REF,
                    "snapshot_hash": REF["snapshot_hash"],
                    "claim": {"phase": "absent"},
                },
            ),
            "resume-a": None,
            "observe-held": _ok("observe-held", {"ref": REF, "claim": CLAIM}),
            "resume-b": _ok("resume-b", copy.deepcopy(REFUSED)),
            "recover": _ok(
                "recover",
                {
                    "ref": REF,
                    "claim_frame_names_record": True,
                    "kill_record_sha256": KILL_DIGEST,
                    "release": {
                        "outcome": "held",
                        "reason": "release-forbidden: execution may have begun",
                    },
                    "abandon": {"outcome": "abandoned", "reason": "claim_tombstone"},
                    "inventory_before": inventory,
                    "inventory_after_release": dict(inventory),
                    "tombstones": ["x.resume-tombstone-1"],
                    "audits": [{**audit, "phase": "intent"}, {**audit, "phase": "complete"}],
                    "claim_after": CLAIM,
                },
            ),
            "resume-after-abandon": _ok("resume-after-abandon", copy.deepcopy(REFUSED)),
        },
        # A never returns a result; this pre-body record is its only installed-child proof.
        "held_provenance": {
            "phase": "resume-a",
            "stage": "pre-body",
            "pid": A_PID,
            "pgid": A_PID,
            "provenance": _provenance(),
            "loaded_harness_modules": LOADED_BEFORE_BODY,
        },
        "webhook_requests": [{"path": "/hook"}],
        "webhook_errors": [],
        "tool_calls": 0,
        "tool_server": {"ready": True, "output_ok": True, "kill": dict(KILLED)},
    }


def _set(path: str, value: object) -> Callable[[dict[str, Any]], None]:
    """A mutation that sets one dotted path in the evidence."""

    def mutate(evidence: dict[str, Any]) -> None:
        *parents, last = path.split(".")
        node = evidence
        for key in parents:
            node = node[key]
        node[last] = value

    return mutate


def _drop(path: str) -> Callable[[dict[str, Any]], None]:
    """A mutation that removes one dotted path from the evidence."""

    def mutate(evidence: dict[str, Any]) -> None:
        *parents, last = path.split(".")
        node = evidence
        for key in parents:
            node = node[key]
        del node[last]

    return mutate


def test_a_complete_correct_run_passes() -> None:
    verdict = evaluate(passing_evidence())

    assert verdict["status"] == "PASS", verdict["failure_reasons"]
    assert verdict["failed_checks"] == [] and verdict["unjudged_checks"] == []
    assert verdict["grammar_failures"] == [] and verdict["global_failures"] == []
    assert {v["state"] for v in verdict["phase_states"].values()} == {"completed"}


def test_the_expected_receipt_must_be_a_lowercase_sha256() -> None:
    for bad in ("", "E" * 64, "e" * 63, "g" * 64):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            w.evaluate(passing_evidence(), expected_receipt_sha256=bad)


@pytest.mark.parametrize(
    ("mutation", "failed"),
    [
        # An unexpected second admission: B's body ran or B was not refused.
        (_set("results.resume-b.observed.body_marker_present", True), "resume-b-refused.no_body"),
        (
            _set("results.resume-b.observed", {"outcome": "returned", "status": "completed"}),
            "resume-b-refused.typed_refusal",
        ),
        (_set("results.resume-b.observed.reason", "claim-busy"), "resume-b-refused.typed_refusal"),
        (
            _set("results.resume-after-abandon.observed.body_marker_present", True),
            "resume-after-abandon-refused.no_body",
        ),
        # A missing or wrong record.
        (_set("results.capture.observed.depth", None), "capture.root_record"),
        (_set("results.capture.observed.status", "completed"), "capture.paused"),
        (
            _set("results.observe-held.observed.ref", {**REF, "record_count": 2}),
            "resume-a-started.same_record",
        ),
        # `started` must be durable, and the lease held, before the kill.
        (
            _set("results.observe-held.observed.claim", {**CLAIM, "phase": "claimed"}),
            "resume-a-started.started_before_kill",
        ),
        (
            _set("results.observe-held.observed.claim", {**CLAIM, "lease": "free"}),
            "resume-a-started.lease_held_by_a",
        ),
        # Manual disposition: never release a started claim; abandon must be audited.
        (
            _set(
                "results.recover.observed.release",
                {"outcome": "released", "reason": "claim_archive"},
            ),
            "release-held.held",
        ),
        (
            _set("results.recover.observed.inventory_after_release", {"journal": "0" * 64}),
            "release-held.no_mutation",
        ),
        (_set("results.recover.observed.audits", []), "abandon-audited.intent_and_complete"),
        (
            _set("results.recover.observed.kill_record_sha256", "0" * 64),
            "abandon-audited.attested_by_kill_record",
        ),
        (_set("results.recover.observed.tombstones", []), "abandon-audited.tombstoned"),
        # No replay of the gate: PASS needs exactly one webhook in total.
        (
            _set("webhook_requests", [{"path": "/hook"}, {"path": "/hook"}]),
            "no-replay.webhooks_total",
        ),
        (_set("webhook_requests", []), "no-replay.webhooks_total"),
        (_set("runs.webhooks_after_capture", 2), "capture.one_webhook"),
        (_set("runs.webhooks_after_capture", True), "capture.one_webhook"),  # bool impostor
    ],
)
def test_each_broken_behaviour_fails_its_named_check(
    mutation: Callable[[dict[str, Any]], None], failed: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert failed in verdict["failed_checks"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        # Named proof failures of a COMPLETED phase (each is `Broken`, never a failed check).
        (_set("runs.resume-a.kill.group_gone", False), "resume-a:group-not-gone"),
        (_set("runs.resume-a.kill.returncode", 0), "resume-a:not-killed-by-sigkill"),
        (_set("runs.resume-a.kill.signal", "SIGTERM"), "resume-a:not-killed-by-sigkill"),
        (_set("runs.resume-a.barrier_entered", False), "resume-a:exited-before-barrier"),
        (_set("results.resume-a", {"ok": True}), "resume-a:a-left-result"),
        (
            _set("results.recover.provenance.installation_receipt_sha256", WRONG_RECEIPT),
            "recover:receipt-mismatch",
        ),
        (
            _set("results.recover.provenance.installation_receipt_sha256", "not-hex"),
            "recover:receipt-malformed",
        ),
        (
            _set("results.resume-b.provenance.interpreter", {"isolated": 0, "no_user_site": 1}),
            "resume-b:not-isolated",
        ),
        (_set("results.recover", None), "recover:result-missing"),
        (_set("results.capture.ok", False), "capture:result-not-ok"),
        (_set("results.capture.phase", "recover"), "capture:result-phase-mismatch"),
        (_drop("results.capture.observed"), "capture:observed-missing"),
        (_drop("results.capture.provenance"), "capture:provenance-missing"),
        (_drop("results.capture.provenance.installed_origins"), "capture:origins-incomplete"),
        (_drop("results.capture.loaded_harness_modules"), "capture:loaded-modules-invalid"),
        (_set("results.capture.loaded_harness_modules", 0), "capture:loaded-modules-invalid"),
    ],
)
def test_each_broken_proof_fails_with_a_named_reason(
    mutation: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert reason in verdict["failure_reasons"]


# --- both Codex counterexamples, and the receipt as a bound proof ------------------------


def test_a_missing_receipt_in_every_child_record_is_a_fail_not_a_pass() -> None:
    """Codex counterexample 1: with no digest anywhere, `{None}` used to look consistent."""
    evidence = passing_evidence()
    for phase in EXITING_PHASES:
        del evidence["results"][phase]["provenance"]["installation_receipt_sha256"]
    del evidence["held_provenance"]["provenance"]["installation_receipt_sha256"]

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    for phase in EXITING_PHASES:
        assert f"{phase}:receipt-missing" in verdict["failure_reasons"]
    assert "resume-a:held-receipt-missing" in verdict["failure_reasons"]


def test_one_consistent_but_wrong_receipt_everywhere_is_a_fail() -> None:
    """Consistency is not proof: every record must carry the digest the PARENT verified."""
    evidence = passing_evidence()
    for phase in EXITING_PHASES:
        evidence["results"][phase]["provenance"]["installation_receipt_sha256"] = WRONG_RECEIPT
    evidence["held_provenance"]["provenance"]["installation_receipt_sha256"] = WRONG_RECEIPT

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    for phase in EXITING_PHASES:
        assert f"{phase}:receipt-mismatch" in verdict["failure_reasons"]
    assert "resume-a:held-receipt-mismatch" in verdict["failure_reasons"]


def test_the_same_run_passes_only_against_its_own_receipt() -> None:
    assert evaluate(passing_evidence(), RECEIPT)["status"] == "PASS"
    assert evaluate(passing_evidence(), WRONG_RECEIPT)["status"] == "FAIL"


def test_a_missing_earlier_provenance_is_not_excused_by_a_later_timeout() -> None:
    """Codex counterexample 2: resume-b times out cleanly, capture's provenance is gone."""
    evidence = stopped_at("resume-b")
    del evidence["results"]["capture"]["provenance"]

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "capture:provenance-missing" in verdict["failure_reasons"]
    assert verdict["phase_states"]["resume-b"]["state"] == "timed-out"


@pytest.mark.parametrize("phase", ["capture", "resume-a", "observe-held"])
def test_a_broken_earlier_proof_stays_a_failure_under_any_later_timeout(phase: str) -> None:
    evidence = stopped_at("resume-b")
    if phase == "resume-a":
        evidence["runs"][phase]["kill"]["group_gone"] = False
    else:
        evidence["results"][phase]["provenance"]["interpreter"] = {"isolated": 0}

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert any(r.startswith(f"{phase}:") for r in verdict["failure_reasons"])


# --- exact types: a bool is not a number -----------------------------------------------


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (_set("results.capture.provenance.interpreter.isolated", True), "capture:not-isolated"),
        (
            _set("results.capture.provenance.interpreter.no_user_site", True),
            "capture:not-no-user-site",
        ),
        (_set("results.capture.provenance.interpreter.isolated", 1.0), "capture:not-isolated"),
        (_set("results.capture.loaded_harness_modules", True), "capture:loaded-modules-invalid"),
        (_set("runs.capture.exit", False), "capture:exit-nonzero"),  # False == 0
        (_set("runs.resume-a.pid", True), "resume-a:held-pid-mismatch"),
        (_set("held_provenance.loaded_harness_modules", True), "resume-a:held-modules-invalid"),
        (_set("held_provenance.loaded_harness_modules", -1), "resume-a:held-modules-invalid"),
        (
            _set("held_provenance.provenance.interpreter.isolated", True),
            "resume-a:held-not-isolated",
        ),
        (_set("tool_calls", False), "tool-called"),  # False == 0
        (_set("tool_calls", 0.0), "tool-called"),
    ],
)
def test_a_bool_or_float_impostor_never_satisfies_a_numeric_proof(
    mutation: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert reason in verdict["failure_reasons"]


# --- the held resume-a: never provenance-exempt ------------------------------------------


def test_the_held_a_needs_its_pre_body_provenance_record() -> None:
    evidence = passing_evidence()
    evidence["held_provenance"] = None

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-a:held-provenance-missing" in verdict["failure_reasons"]


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (_set("held_provenance", "garbage"), "resume-a:held-provenance-missing"),
        (_set("held_provenance", {"unreadable": True}), "resume-a:held-provenance-missing"),
        (_drop("held_provenance.provenance"), "resume-a:held-provenance-missing"),
        (_set("held_provenance.stage", "post-body"), "resume-a:held-record-misplaced"),
        (_set("held_provenance.phase", "recover"), "resume-a:held-record-misplaced"),
        (_set("held_provenance.pid", A_PID + 1), "resume-a:held-pid-mismatch"),
        (_set("held_provenance.pgid", A_PID + 1), "resume-a:held-pgid-mismatch"),
        (_drop("held_provenance.pid"), "resume-a:held-pid-mismatch"),
        (
            _set("held_provenance.provenance.installation_receipt_sha256", WRONG_RECEIPT),
            "resume-a:held-receipt-mismatch",
        ),
        (
            _drop("held_provenance.provenance.installed_origins"),
            "resume-a:held-origins-incomplete",
        ),
        (_drop("held_provenance.loaded_harness_modules"), "resume-a:held-modules-invalid"),
    ],
)
def test_a_missing_or_malformed_held_proof_fails(
    mutation: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert reason in verdict["failure_reasons"]


@pytest.mark.parametrize("count", [0, 1, w.MIN_LOADED_HARNESS_MODULES - 1])
def test_a_held_record_below_the_prover_floor_fails(count: int) -> None:
    """`installed_origins` imports every package before the pre-body record, so a real held
    record reports at least one module per package; zero contradicts the installed path."""
    evidence = passing_evidence()
    evidence["held_provenance"]["loaded_harness_modules"] = count

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-a:held-modules-invalid" in verdict["failure_reasons"]


@pytest.mark.parametrize("count", [w.MIN_LOADED_HARNESS_MODULES, LOADED_AFTER_BODY, 400])
def test_a_held_record_at_or_above_the_prover_floor_passes(count: int) -> None:
    evidence = passing_evidence()
    evidence["held_provenance"]["loaded_harness_modules"] = count

    assert evaluate(evidence)["status"] == "PASS"


def test_the_floor_is_grounded_in_the_installed_prover() -> None:
    """The number of packages `installed_origins` imports is the number the floor rests on."""
    assert w.MIN_LOADED_HARNESS_MODULES == len(w.PACKAGES) == 7
    # The prover now lives in the shared owner module, not in this witness.
    source = w.SHARED_PROVER_PATH.read_text()
    assert "imported = importlib.import_module(package)" in source  # per wheel, all seven
    assert source.index("origins = installed_origins(") < source.index(
        '"installed_origins": origins'
    )


def test_a_present_zero_or_malformed_held_record_fails_even_under_a_valid_later_timeout() -> None:
    for record_mutation in (
        _set("held_provenance.loaded_harness_modules", 0),
        _set("held_provenance.provenance.installed_origins", {p: None for p in w.PACKAGES}),
    ):
        evidence = stopped_at("resume-b")
        record_mutation(evidence)

        verdict = evaluate(evidence)

        assert verdict["status"] == "FAIL"
        assert any(r.startswith("resume-a:held-") for r in verdict["failure_reasons"])


def test_a_genuine_before_proof_timeout_may_lack_the_held_record() -> None:
    evidence = stopped_at("resume-a")
    evidence["held_provenance"] = None

    verdict = evaluate(evidence)

    assert verdict["status"] == "INCONCLUSIVE" and verdict["failure_reasons"] == []


@pytest.mark.parametrize(
    "record", [{"unreadable": True}, {"phase": "resume-a", "stage": "pre-body"}]
)
def test_a_timed_out_a_with_a_present_but_malformed_proof_fails(record: dict[str, Any]) -> None:
    evidence = stopped_at("resume-a")
    evidence["held_provenance"] = record

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert any(r.startswith("resume-a:held-") for r in verdict["failure_reasons"])


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (_set("runs.resume-a.marker.pid", A_PID + 1), "resume-a:marker-pid-mismatch"),
        (_set("runs.resume-a.marker.pgid", A_PID + 1), "resume-a:marker-pgid-mismatch"),
        (_set("runs.resume-a.marker", {"unreadable": True}), "resume-a:marker-pid-mismatch"),
        (_set("runs.resume-a.marker", None), "resume-a:marker-missing"),
        (_set("runs.resume-a.marker", "garbage"), "resume-a:marker-malformed"),
        (_drop("runs.resume-a.marker"), "resume-a:marker-missing"),
    ],
)
def test_the_marker_is_bound_to_the_launched_a(
    mutation: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert reason in verdict["failure_reasons"]


@pytest.mark.parametrize("how", ["absent", "none"])
def test_a_completed_a_without_its_marker_never_completes(how: str) -> None:
    """The real scenario always supplies the marker of an entered A; absence is missing proof."""
    evidence = passing_evidence()
    if how == "absent":
        del evidence["runs"]["resume-a"]["marker"]
    else:
        evidence["runs"]["resume-a"]["marker"] = None

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-a:marker-missing" in verdict["failure_reasons"]
    assert verdict["phase_states"]["resume-a"]["state"] == "broken"


@pytest.mark.parametrize("later", ["observe-held", "resume-b", "recover", "resume-after-abandon"])
def test_a_missing_marker_is_not_excused_by_a_valid_later_timeout(later: str) -> None:
    evidence = stopped_at(later)
    del evidence["runs"]["resume-a"]["marker"]

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-a:marker-missing" in verdict["failure_reasons"]


def test_a_no_barrier_timeout_of_a_may_lack_a_marker() -> None:
    evidence = stopped_at("resume-a")
    evidence["runs"]["resume-a"].pop("marker")

    assert evaluate(evidence)["status"] == "INCONCLUSIVE"


def test_a_deliberately_killed_a_still_needs_a_sigkill_return_code() -> None:
    evidence = passing_evidence()
    evidence["runs"]["resume-a"]["kill"] = {**KILLED, "returncode": -signal.SIGTERM}

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-a:not-killed-by-sigkill" in verdict["failure_reasons"]


def test_a_waited_phase_cap_race_needs_only_the_group_gone_proof() -> None:
    """A phase exiting at the cap may report any return code; its group must still be gone."""
    evidence = stopped_at("resume-b")
    evidence["runs"]["resume-b"]["kill"] = {**KILLED, "returncode": 0}

    assert evaluate(evidence)["status"] == "INCONCLUSIVE"
    evidence["runs"]["resume-b"]["kill"]["group_gone"] = False
    verdict = evaluate(evidence)
    assert verdict["status"] == "FAIL" and "resume-b:group-not-gone" in verdict["failure_reasons"]


# --- timeouts: INCONCLUSIVE only for a clean prefix, cleanup and nothing later ------------


def stopped_at(phase: str) -> dict[str, Any]:
    """What the scenario records when `phase` times out: its group killed and reaped, no
    result from it, and no later phase launched (the scenario stops at its first timeout)."""
    evidence = passing_evidence()
    later = w.PHASES[w.PHASES.index(phase) + 1 :]
    run = evidence["runs"][phase]
    if phase == "resume-a":
        run.update(timeout=True, barrier_entered=False, marker=None)
    else:
        run.update(exit=-signal.SIGKILL, timeout=True, kill=dict(KILLED))
        evidence["results"][phase] = None
    for gone in later:
        evidence["runs"].pop(gone)
        evidence["results"].pop(gone)
    if phase == "capture":
        evidence["runs"].pop("webhooks_after_capture")
        evidence["webhook_requests"] = []
        evidence["held_provenance"] = None
    return evidence


@pytest.mark.parametrize("phase", w.PHASES)
def test_a_clean_prefix_and_proven_cleanup_make_one_timeout_inconclusive(phase: str) -> None:
    verdict = evaluate(stopped_at(phase))

    assert verdict["failure_reasons"] == []
    assert verdict["status"] == "INCONCLUSIVE"
    assert verdict["timed_out_phases"] == [phase]
    assert verdict["unjudged_checks"]  # what could not be judged is named, not dropped
    later = w.PHASES[w.PHASES.index(phase) + 1 :]
    assert all(verdict["phase_states"][p]["state"] == "unstarted" for p in later)


def test_the_unjudged_checks_are_exactly_those_reading_the_stopped_phases() -> None:
    verdict = evaluate(stopped_at("resume-b"))

    unjudged = set(verdict["unjudged_checks"])
    assert "resume-b-refused.typed_refusal" in unjudged
    assert "abandon-audited.abandoned" in unjudged
    assert "resume-after-abandon-refused.no_body" in unjudged
    assert not any(name.startswith(("capture.", "resume-a-started.")) for name in unjudged)
    assert all(
        v is None or isinstance(v, bool)
        for case in verdict["cases"].values()
        for v in case.values()
    )


@pytest.mark.parametrize("phase", EXITING_PHASES)
def test_a_timeout_without_a_kill_record_fails(phase: str) -> None:
    evidence = stopped_at(phase)
    evidence["runs"][phase].pop("kill")

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:kill-missing" in verdict["failure_reasons"]


@pytest.mark.parametrize("phase", w.PHASES)
@pytest.mark.parametrize("gone", [False, None, "yes"])
def test_a_timeout_whose_kill_does_not_prove_the_group_gone_fails(phase: str, gone: object) -> None:
    evidence = stopped_at(phase)
    evidence["runs"][phase]["kill"] = {**KILLED, "group_gone": gone}

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:group-not-gone" in verdict["failure_reasons"]


@pytest.mark.parametrize("phase", EXITING_PHASES)
@pytest.mark.parametrize("left", [{"ok": True}, {"ok": False, "error": "x"}], ids=["ok", "crashed"])
def test_a_timed_out_phase_that_left_any_result_fails(phase: str, left: dict[str, Any]) -> None:
    """Even a finished-then-hung phase (ok true) or a crash is a failure, never INCONCLUSIVE."""
    evidence = stopped_at(phase)
    evidence["results"][phase] = {"phase": phase, **left}

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:timed-out-left-result" in verdict["failure_reasons"]


@pytest.mark.parametrize("later", ["recover", "resume-after-abandon"])
def test_a_phase_that_ran_after_the_stop_is_forbidden(later: str) -> None:
    evidence = stopped_at("resume-b")
    evidence["runs"][later] = dict(EXITED)
    evidence["results"][later] = _ok(later, {})

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{later}:completed-after-stop" in verdict["grammar_failures"]


def test_a_phase_that_left_only_a_result_after_the_stop_is_forbidden() -> None:
    evidence = stopped_at("resume-b")
    evidence["results"]["recover"] = _ok("recover", {})

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "recover:run-missing" in verdict["failure_reasons"]


def test_two_timeouts_are_not_a_run_the_scenario_can_produce() -> None:
    evidence = stopped_at("resume-b")
    evidence["runs"]["observe-held"].update(exit=-signal.SIGKILL, timeout=True, kill=dict(KILLED))
    evidence["results"]["observe-held"] = None

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "resume-b:second-timeout" in verdict["grammar_failures"]


@pytest.mark.parametrize("phase", EXITING_PHASES[1:])
def test_unstarted_phases_without_any_timeout_fail(phase: str) -> None:
    evidence = passing_evidence()
    evidence["runs"].pop(phase)
    evidence["results"].pop(phase)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:unstarted-without-timeout" in verdict["grammar_failures"]


def test_a_stopped_scenario_with_no_later_phases_fails_closed() -> None:
    evidence = passing_evidence()
    for phase in ("resume-b", "recover", "resume-after-abandon"):
        evidence["runs"].pop(phase)
        evidence["results"].pop(phase)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert {
        "resume-b:unstarted-without-timeout",
        "recover:unstarted-without-timeout",
        "resume-after-abandon:unstarted-without-timeout",
    } <= set(verdict["grammar_failures"])


def test_an_unstarted_scenario_with_no_timeout_is_a_fail_not_inconclusive() -> None:
    verdict = evaluate({"runs": {}, "results": {}, "tool_server": {"ready": False}})

    assert verdict["status"] == "FAIL"
    assert "tool-server:not-ready" in verdict["global_failures"]


# --- zero or one webhook ------------------------------------------------------------------


@pytest.mark.parametrize("hooks", [0, 1])
def test_a_capture_timeout_may_have_delivered_zero_or_one_webhook(hooks: int) -> None:
    evidence = stopped_at("capture")
    evidence["webhook_requests"] = [{"path": "/hook"}] * hooks

    assert evaluate(evidence)["status"] == "INCONCLUSIVE"


def test_two_webhooks_are_a_replay_even_when_a_phase_timed_out() -> None:
    evidence = stopped_at("capture")
    evidence["webhook_requests"] = [{"path": "/hook"}] * 2

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL" and "webhook-replay" in verdict["global_failures"]


@pytest.mark.parametrize("bad", [None, "one", {"n": 1}])
def test_malformed_webhook_evidence_fails(bad: object) -> None:
    evidence = passing_evidence()
    evidence["webhook_requests"] = bad

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL" and "webhooks-malformed" in verdict["global_failures"]


# --- owned process groups and bounded phase records (Codex HOLD on 7619e06) --------------


@pytest.mark.parametrize("owner", ["tool_server", "resume-a"])
def test_a_surviving_owned_group_fails_even_when_every_other_fact_passes(owner: str) -> None:
    evidence = passing_evidence()
    record = evidence["tool_server"] if owner == "tool_server" else evidence["runs"][owner]
    record["kill"] = {**KILLED, "group_gone": False}

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert any("group-not-gone" in r for r in verdict["failure_reasons"])
    assert any(r.startswith(owner.replace("_", "-") + ":") for r in verdict["failure_reasons"])


@pytest.mark.parametrize("phase", EXITING_PHASES)
@pytest.mark.parametrize("exit_code", [1, -signal.SIGKILL, None, False, "0"])
def test_a_phase_that_did_not_exit_zero_fails(phase: str, exit_code: object) -> None:
    evidence = passing_evidence()
    evidence["runs"][phase]["exit"] = exit_code

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:exit-nonzero" in verdict["failure_reasons"]


@pytest.mark.parametrize("phase", [*w.PHASES, "tool-server"])
def test_a_phase_whose_output_hit_the_cap_fails(phase: str) -> None:
    evidence = passing_evidence()
    record = evidence["tool_server"] if phase == "tool-server" else evidence["runs"][phase]
    record["output_ok"] = False

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert f"{phase}:output-capped" in verdict["failure_reasons"]


@pytest.mark.parametrize(
    ("capped", "reason"),
    [
        ("resume-b", "resume-b:output-capped"),  # the timed-out phase itself
        ("capture", "capture:output-capped"),  # an earlier phase
        ("tool-server", "tool-server:output-capped"),
    ],
)
def test_capped_output_stays_a_failure_when_a_phase_timed_out(capped: str, reason: str) -> None:
    evidence = stopped_at("resume-b")
    record = evidence["tool_server"] if capped == "tool-server" else evidence["runs"][capped]
    record["output_ok"] = False

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert reason in verdict["failure_reasons"]


@pytest.mark.parametrize(
    "final",
    [
        pytest.param(None, id="final-phase-never-completed"),
        pytest.param({**EXITED, "exit": 1}, id="final-phase-exited-nonzero"),
        pytest.param({**EXITED, "timeout": None}, id="final-phase-timeout-unrecorded"),
    ],
)
def test_the_final_phase_must_itself_complete(final: dict[str, object] | None) -> None:
    evidence = passing_evidence()
    if final is None:
        evidence["runs"].pop("resume-after-abandon")
    else:
        evidence["runs"]["resume-after-abandon"] = final

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert any(r.startswith("resume-after-abandon:") for r in verdict["failure_reasons"])


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param(lambda e: e.clear(), id="empty-evidence"),
        pytest.param(lambda e: e.pop("runs"), id="runs-missing"),
        pytest.param(lambda e: e.pop("tool_server"), id="tool-server-missing"),
        pytest.param(lambda e: e["runs"].__setitem__("capture", "garbage"), id="run-not-a-mapping"),
        pytest.param(
            lambda e: e["tool_server"].__setitem__("kill", "garbage"), id="kill-malformed"
        ),
        pytest.param(
            lambda e: e["results"]["recover"]["observed"].__setitem__("audits", "garbage"),
            id="audits-malformed",
        ),
        pytest.param(
            lambda e: e["results"]["recover"]["observed"].__setitem__("audits", ["garbage"]),
            id="audit-entry-malformed",
        ),
        pytest.param(
            lambda e: e["results"].__setitem__("capture", {"ok": "yes"}), id="ok-not-bool"
        ),
        pytest.param(lambda e: e.__setitem__("webhook_requests", None), id="webhooks-missing"),
        pytest.param(lambda e: e["runs"]["observe-held"].pop("timeout"), id="timeout-unrecorded"),
        pytest.param(
            lambda e: e["results"].__setitem__("observe-held", "garbage"), id="result-str"
        ),
    ],
)
def test_a_missing_or_malformed_record_fails_instead_of_passing_or_crashing(
    mutation: Callable[[dict[str, Any]], object],
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert verdict["failure_reasons"]


# --- the scenario root ------------------------------------------------------------------


def _mountinfo(mount: Path, fs: str) -> str:
    return (
        "22 1 254:0 / / rw,relatime shared:1 - ext4 /dev/vda rw\n"
        f"35 22 0:31 / {mount} rw,nosuid shared:9 - {fs} {fs} rw\n"
    )


@pytest.fixture
def outside_checkout() -> Iterator[Path]:
    """A scratch directory with no `.git` at or above it (the placement rule's own test)."""
    for parent in (Path(tempfile.gettempdir()), Path("/dev/shm")):
        if parent.is_dir() and not any(
            os.path.lexists(p / ".git") for p in (parent, *parent.parents)
        ):
            scratch = Path(tempfile.mkdtemp(prefix="b104w-test-", dir=parent)).resolve()
            try:
                yield scratch
            finally:
                subprocess.run(["rm", "-rf", str(scratch)], check=True)
            return
    pytest.skip("no scratch directory free of a .git ancestor")


def test_a_new_root_on_a_durable_owned_parent_is_accepted(outside_checkout: Path) -> None:
    root = outside_checkout / "scenario"

    placed = w.checked_scenario_root(root, _mountinfo(outside_checkout, "ext4"))

    assert placed == {"root": str(root), "parent": str(outside_checkout), "filesystem_type": "ext4"}


@pytest.mark.parametrize("fs", sorted(w.NON_DURABLE_FILESYSTEMS))
def test_a_non_durable_filesystem_is_refused(outside_checkout: Path, fs: str) -> None:
    with pytest.raises(ValueError, match="not durable"):
        w.checked_scenario_root(outside_checkout / "scenario", _mountinfo(outside_checkout, fs))


def test_a_root_under_any_git_marker_is_refused(outside_checkout: Path) -> None:
    (outside_checkout / ".git").mkdir()  # an empty `.git` directory counts, as for placement

    with pytest.raises(ValueError, match="Git checkout"):
        w.checked_scenario_root(outside_checkout / "scenario", _mountinfo(outside_checkout, "ext4"))


@pytest.mark.parametrize("make", ["existing", "relative", "symlinked-parent"])
def test_an_existing_relative_or_symlinked_root_is_refused(
    outside_checkout: Path, make: str
) -> None:
    root = outside_checkout / "scenario"
    if make == "existing":
        root.mkdir()
    elif make == "relative":
        root = Path("scenario")
    else:
        (outside_checkout / "real").mkdir()
        (outside_checkout / "link").symlink_to(outside_checkout / "real")
        root = outside_checkout / "link" / "scenario"

    with pytest.raises(ValueError):
        w.checked_scenario_root(root, _mountinfo(outside_checkout, "ext4"))


def test_the_longest_covering_mount_decides_the_filesystem() -> None:
    mountinfo = _mountinfo(Path("/dev/shm"), "tmpfs") + "40 22 0:40 / /home\\040x rw - xfs d rw\n"

    assert w.filesystem_type(mountinfo, Path("/dev/shm/a/b")) == "tmpfs"
    assert w.filesystem_type(mountinfo, Path("/home x/y")) == "xfs"
    assert w.filesystem_type(mountinfo, Path("/home/robbo")) == "ext4"


# --- the operator config the children load ----------------------------------------------


def test_the_config_places_durable_state_and_binds_only_loopback_services() -> None:
    layout = w.Layout(Path("/scenario"))

    config = tomllib.loads(w.config_text(layout, 4101, 4102))["runtime"]

    assert config["state_placement"] == {"state_root": "/scenario/state", "forbidden_roots": []}
    assert config["pause_resume_protocol_config"] == {"durable": True}
    assert config["repository_root"] == "/scenario/repo"
    assert config["drain_timeout_seconds"] > w.CHILD_CAP_SECONDS
    assert (
        config["webhook_delivery_composer_config"]["endpoint_url"] == "http://127.0.0.1:4101/hook"
    )
    (client,) = config["mcp_clients"]
    assert client == {
        "client_name": "b104-witness",
        "transport": "streamable_http_l3",
        "trust_level": "L3_ALLOW_WITH_AUDIT",
        "blast_radius": "READ_ONLY",
        "connection_url": "http://127.0.0.1:4102/mcp",
    }
    cells = {e["path_class"]: Path(e["path"]) for e in config["path_bindings"]["raw_entries"]}
    assert set(cells) == set(w.PATH_CLASSES)
    assert cells["STATE_LEDGER"] == layout.ledger_dir
    assert all(p.is_relative_to(layout.repo) for c, p in cells.items() if c != "STATE_LEDGER")


def test_the_path_classes_are_exactly_the_registry_classes() -> None:
    from harness_is.path_class_registry import PathClass

    assert set(w.PATH_CLASSES) == {pc.value for pc in PathClass}


# --- the child command and the interpreter proof ----------------------------------------


def test_each_child_runs_the_installed_python_isolated_with_a_minimal_env() -> None:
    layout = w.Layout(Path("/scenario"))

    argv = w.child_argv(
        Path("/venv/bin/python"), Path("/helper.py"), "resume-b", ["--scenario", "/s"]
    )
    env = w.child_env(layout)

    assert argv == [
        "/venv/bin/python",
        "-I",
        "/helper.py",
        "_child",
        "resume-b",
        "--scenario",
        "/s",
    ]
    assert "PYTHONPATH" not in env and env["PYTHONNOUSERSITE"] == "1"
    assert env["HOME"] == "/scenario/home" and env["TMPDIR"] == "/scenario/tmp"


def test_a_non_isolated_interpreter_is_not_accepted_as_installed(tmp_path: Path) -> None:
    # pytest itself is neither `-I` nor the selected venv: the proof must refuse it.
    with pytest.raises(ValueError, match="not an isolated installed interpreter"):
        w.interpreter_evidence(Path(sys.prefix), tmp_path)


def test_a_loaded_module_outside_the_verified_files_is_refused() -> None:
    with pytest.raises(ValueError, match="not from a verified installed file"):
        w.loaded_harness_origins({"/nowhere/else.py"})


@pytest.mark.parametrize("field", ["candidate", "candidate_head", "venv", "schema"])
def test_a_receipt_for_another_candidate_head_or_venv_is_refused(
    tmp_path: Path, field: str
) -> None:
    receipt = {"schema": 2, "candidate": "/c", "candidate_head": "0" * 40, "venv": "/v"}
    receipt[field] = {"schema": 1}.get(field, "/other")
    path = tmp_path / "receipt.json"
    path.write_text(json.dumps(receipt))

    with pytest.raises(ValueError, match="does not match"):
        w.checked_provenance(path, Path("/c"), Path("/v"), "0" * 40)


# --- process ownership and write-once records --------------------------------------------


def test_kill_group_kills_only_its_own_group_and_proves_it_gone(tmp_path: Path) -> None:
    child = w.spawn(["sleep", "30"], {"PATH": "/usr/bin:/bin"}, tmp_path, tmp_path, "sleeper")
    assert os.getpgid(child.proc.pid) == child.proc.pid != os.getpgid(0)

    record = w.kill_group(child)

    assert record == {
        "pgid": child.proc.pid,
        "signal": "SIGKILL",
        "returncode": -signal.SIGKILL,
        "group_gone": True,
    }


def test_records_are_written_once(tmp_path: Path) -> None:
    w.write_json_new(tmp_path / "r.json", {"a": 1})

    with pytest.raises(FileExistsError):
        w.write_json_new(tmp_path / "r.json", {"a": 2})


# --- origin proof: each emitted package origin is a proving value, not a name ------------


def _origin(evidence: dict[str, Any], target: str) -> dict[str, Any]:
    """The `installed_origins` mapping of a completed result or of the held record."""
    if target == "held":
        return evidence["held_provenance"]["provenance"]["installed_origins"]
    return evidence["results"][target]["provenance"]["installed_origins"]


ORIGIN_TARGETS = ["capture", "resume-b", "recover", "held"]
PKG = "harness_runtime"


def _bad_origins() -> list[tuple[str, Callable[[dict[str, Any]], None], str]]:
    def entry(mutate: Callable[[dict[str, Any]], None]) -> Callable[[dict[str, Any]], None]:
        def apply(origins: dict[str, Any]) -> None:
            mutate(origins[PKG])

        return apply

    def replace(value: object) -> Callable[[dict[str, Any]], None]:
        def apply(origins: dict[str, Any]) -> None:
            origins[PKG] = value

        return apply

    return [
        ("entry-none", replace(None), "origin-malformed"),
        ("entry-empty-dict", replace({}), "origin-record-path-invalid"),
        ("entry-list", replace([]), "origin-malformed"),
        ("empty-inventory", entry(lambda o: o.update(verified_files=[])), "origin-files-invalid"),
        ("inventory-none", entry(lambda o: o.update(verified_files=None)), "origin-files-invalid"),
        ("count-zero", entry(lambda o: o.update(python_files_checked=0)), "origin-count-invalid"),
        ("count-missing", entry(lambda o: o.pop("python_files_checked")), "origin-count-invalid"),
        (
            "count-bool",
            entry(lambda o: o.update(python_files_checked=True)),
            "origin-count-invalid",
        ),
        (
            "count-disagrees",
            entry(lambda o: o.update(python_files_checked=5)),
            "origin-count-invalid",
        ),
        (
            "count-float",
            entry(lambda o: o.update(python_files_checked=2.0)),
            "origin-count-invalid",
        ),
        ("digest-missing", entry(lambda o: o.pop("record_sha256")), "origin-record-digest-invalid"),
        (
            "digest-short",
            entry(lambda o: o.update(record_sha256="ab")),
            "origin-record-digest-invalid",
        ),
        (
            "digest-upper",
            entry(lambda o: o.update(record_sha256="A" * 64)),
            "origin-record-digest-invalid",
        ),
        (
            "record-path-missing",
            entry(lambda o: o.pop("record_path")),
            "origin-record-path-invalid",
        ),
        (
            "record-path-relative",
            entry(lambda o: o.update(record_path="RECORD")),
            "origin-record-path-invalid",
        ),
        (
            "record-path-not-a-record",
            entry(lambda o: o.update(record_path=f"{SITE}/{PKG}-0.0.0.dist-info/METADATA")),
            "origin-record-path-invalid",
        ),
        (
            "record-path-outside-site-packages",
            entry(lambda o: o.update(record_path=f"/elsewhere/{PKG}-0.0.0.dist-info/RECORD")),
            "origin-record-path-invalid",
        ),
        (
            "record-path-outside-the-interpreter-prefix",
            entry(
                lambda o: o.update(record_path=f"/other/site-packages/{PKG}-0.0.0.dist-info/RECORD")
            ),
            "origin-record-path-invalid",
        ),
        (
            "file-outside-site-packages",
            entry(
                lambda o: o.update(
                    verified_files=["/candidate/harness-runtime/src/x.py"], python_files_checked=1
                )
            ),
            "origin-files-invalid",
        ),
        (
            "file-under-the-prefix-but-not-in-site-packages",
            entry(
                lambda o: o.update(
                    verified_files=[f"{VENV}/checkout/{PKG}/x.py"], python_files_checked=1
                )
            ),
            "origin-files-invalid",
        ),
        (
            "file-not-python",
            entry(
                lambda o: o.update(
                    verified_files=[f"{SITE}/{PKG}/data.json"], python_files_checked=1
                )
            ),
            "origin-files-invalid",
        ),
        (
            "file-of-another-package",
            entry(
                lambda o: o.update(
                    verified_files=[f"{SITE}/harness_core/x.py"], python_files_checked=1
                )
            ),
            "origin-files-invalid",
        ),
        (
            "file-duplicated",
            entry(
                lambda o: o.update(
                    verified_files=[f"{SITE}/{PKG}/a.py"] * 2, python_files_checked=2
                )
            ),
            "origin-files-invalid",
        ),
        (
            "files-unsorted",
            entry(lambda o: o.update(verified_files=[f"{SITE}/{PKG}/b.py", f"{SITE}/{PKG}/a.py"])),
            "origin-files-invalid",
        ),
        (
            "files-not-strings",
            entry(lambda o: o.update(verified_files=[1, 2])),
            "origin-files-invalid",
        ),
    ]


@pytest.mark.parametrize("target", ORIGIN_TARGETS)
@pytest.mark.parametrize(
    ("name", "mutate", "reason"), _bad_origins(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_a_bad_origin_entry_fails_an_otherwise_passing_run(
    target: str, name: str, mutate: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = passing_evidence()
    mutate(_origin(evidence, target))

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL", name
    prefix = "resume-a:held-" if target == "held" else f"{target}:"
    assert prefix + reason in verdict["failure_reasons"], name


@pytest.mark.parametrize("target", ["capture", "observe-held", "held"])
@pytest.mark.parametrize(
    ("name", "mutate", "reason"), _bad_origins(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_a_bad_origin_entry_is_not_excused_by_a_valid_later_timeout(
    target: str, name: str, mutate: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = stopped_at("resume-b")
    mutate(_origin(evidence, target))

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL", name
    assert verdict["phase_states"]["resume-b"]["state"] == "timed-out"


def test_the_bad_example_names_alone_are_not_origin_proof() -> None:
    """{package: None} and verified_files=[] with a correct digest and flags must not PASS."""
    none_entries = passing_evidence()
    none_entries["results"]["capture"]["provenance"]["installed_origins"] = {
        p: None for p in w.PACKAGES
    }
    empty_inventory = passing_evidence()
    for package in w.PACKAGES:
        _origin(empty_inventory, "capture")[package]["verified_files"] = []

    assert evaluate(none_entries)["status"] == "FAIL"
    assert evaluate(empty_inventory)["status"] == "FAIL"


def test_the_real_shape_origin_fixture_passes() -> None:
    assert evaluate(passing_evidence())["status"] == "PASS"
    assert set(real_shape_origins()["harness_core"]) == {
        "record_path",
        "record_sha256",
        "python_files_checked",
        "verified_files",
    }


def test_origins_and_prefix_must_agree_across_all_proved_records() -> None:
    other = passing_evidence()
    _origin(other, "recover")[PKG]["record_sha256"] = "9" * 64
    prefix = passing_evidence()
    prefix["results"]["recover"]["provenance"]["interpreter"]["prefix"] = "/venv2"
    for pkg in w.PACKAGES:  # keep its paths consistent with its own (wrong) prefix
        entry = _origin(prefix, "recover")[pkg]
        entry["record_path"] = entry["record_path"].replace("/venv/", "/venv2/")
        entry["verified_files"] = [f.replace("/venv/", "/venv2/") for f in entry["verified_files"]]

    assert "origins-inconsistent" in evaluate(other)["global_failures"]
    assert evaluate(other)["status"] == "FAIL"
    assert "interpreter-inconsistent" in evaluate(prefix)["global_failures"]
    assert evaluate(prefix)["status"] == "FAIL"


def test_a_missing_interpreter_prefix_is_not_proof() -> None:
    evidence = passing_evidence()
    del evidence["results"]["capture"]["provenance"]["interpreter"]["prefix"]

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "capture:interpreter-prefix-invalid" in verdict["failure_reasons"]


@pytest.mark.parametrize("count", [0, 1, w.MIN_LOADED_HARNESS_MODULES - 1])
def test_a_completed_result_below_the_prover_floor_fails(count: int) -> None:
    evidence = passing_evidence()
    evidence["results"]["recover"]["loaded_harness_modules"] = count

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert "recover:loaded-modules-invalid" in verdict["failure_reasons"]


# --- origin path containment and package layout (one parser, canonical paths) -------------

SHAPES = {
    "all-completed": passing_evidence,
    "proved-prefix-then-valid-timeout": lambda: stopped_at("resume-b"),
}
PACKAGE_LIST = sorted(w.PACKAGES)


def _provenances(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    """Every proved record's provenance: completed results and the held A record."""
    records = [r["provenance"] for r in evidence["results"].values() if isinstance(r, dict)]
    held = evidence.get("held_provenance")
    return [*records, held["provenance"]] if isinstance(held, dict) else records


def _mutate_everywhere(
    evidence: dict[str, Any], mutate: Callable[[str, dict[str, Any]], None]
) -> None:
    """Apply one origin mutation to EVERY package of EVERY proved record, consistently, so that
    cross-record disagreement cannot be what rejects it."""
    for provenance in _provenances(evidence):
        for package, entry in provenance["installed_origins"].items():
            mutate(package, entry)


def _relocate(evidence: dict[str, Any], venv: str) -> None:
    """Move the whole synthetic venv (prefix and every origin path) to a real temp location."""
    for provenance in _provenances(evidence):
        text = (
            json.dumps(provenance).replace('"/venv/', f'"{venv}/').replace('"/venv"', f'"{venv}"')
        )
        provenance.clear()
        provenance.update(json.loads(text))


def _files(package: str, *names: str) -> dict[str, Any]:
    return {"verified_files": sorted(names), "python_files_checked": len(names)}


LAYOUT_MUTATIONS: dict[str, Callable[[str, dict[str, Any]], None]] = {
    "traversal-out-of-the-prefix": lambda pkg, e: e.update(
        _files(pkg, f"{SITE}/{pkg}/../../../../../outside.py")
    ),
    "traversal-inside-the-prefix-to-another-package": lambda pkg, e: e.update(
        _files(pkg, f"{SITE}/{pkg}/../harness_core/__init__.py")
    ),
    "traversal-in-the-record-path": lambda pkg, e: e.update(
        record_path=f"{SITE}/../site-packages/{pkg}-0.0.0.dist-info/RECORD"
    ),
    "dot-segment": lambda pkg, e: e.update(_files(pkg, f"{SITE}/{pkg}/./__init__.py")),
    "repeated-separator": lambda pkg, e: e.update(_files(pkg, f"{SITE}//{pkg}/__init__.py")),
    "wrong-package-record": lambda pkg, e: e.update(
        record_path=(
            f"{SITE}/{PACKAGE_LIST[(PACKAGE_LIST.index(pkg) + 1) % 7]}-0.0.0.dist-info/RECORD"
        )
    ),
    "wrong-version-record": lambda pkg, e: e.update(
        record_path=f"{SITE}/{pkg}-9.9.9.dist-info/RECORD"
    ),
    "hyphenated-distribution-name": lambda pkg, e: e.update(
        record_path=f"{SITE}/{pkg.replace('_', '-')}-0.0.0.dist-info/RECORD"
    ),
    "record-not-in-a-dist-info-directory": lambda pkg, e: e.update(
        record_path=f"{SITE}/{pkg}-0.0.0/RECORD"
    ),
    "package-name-in-the-wrong-ancestor": lambda pkg, e: e.update(
        _files(pkg, f"{VENV}/{pkg}/site-packages/other/__init__.py")
    ),
    "package-directory-not-immediately-under-site-packages": lambda pkg, e: e.update(
        _files(pkg, f"{SITE}/other/{pkg}/__init__.py")
    ),
    "file-of-another-package": lambda pkg, e: e.update(
        _files(pkg, f"{SITE}/{PACKAGE_LIST[(PACKAGE_LIST.index(pkg) + 1) % 7]}/__init__.py")
    ),
    "package-prefix-lookalike-directory": lambda pkg, e: e.update(
        _files(pkg, f"{SITE}/{pkg}_evil/__init__.py")
    ),
    "consistent-tree-under-a-differently-named-site-directory": lambda pkg, e: e.update(
        record_path=f"{VENV}/lib/python3.12/dist-packages/{pkg}-0.0.0.dist-info/RECORD",
        **_files(pkg, f"{VENV}/lib/python3.12/dist-packages/{pkg}/__init__.py"),
    ),
    "site-packages-only-as-a-lookalike": lambda pkg, e: e.update(
        record_path=f"{VENV}/lib/python3.12/site-packages-evil/{pkg}-0.0.0.dist-info/RECORD"
    ),
    "site-root-differs-per-package": lambda pkg, e: e.update(
        record_path=f"{VENV}/{pkg}/site-packages/{pkg}-0.0.0.dist-info/RECORD",
        **_files(pkg, f"{VENV}/{pkg}/site-packages/{pkg}/__init__.py"),
    ),
}


@pytest.mark.parametrize("shape", sorted(SHAPES))
@pytest.mark.parametrize("name", sorted(LAYOUT_MUTATIONS))
def test_a_counterfeit_path_layout_fails_the_first_proved_phase(shape: str, name: str) -> None:
    """Applied to every proved record, so agreement across records cannot be what rejects it;
    the FIRST phase's own parse must fail, on all-completed evidence and before a valid timeout."""
    evidence = SHAPES[shape]()
    _mutate_everywhere(evidence, LAYOUT_MUTATIONS[name])

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL", name
    assert any(r.startswith("capture:origin-") for r in verdict["failure_reasons"]), name
    assert any(r.startswith("resume-a:held-origin-") for r in verdict["failure_reasons"]), name


def test_a_consistent_counterfeit_is_not_saved_by_cross_record_agreement() -> None:
    evidence = passing_evidence()
    _mutate_everywhere(evidence, LAYOUT_MUTATIONS["traversal-out-of-the-prefix"])

    verdict = evaluate(evidence)

    assert verdict["global_failures"] == []  # every record agrees with every other one
    assert verdict["status"] == "FAIL"


def test_the_evaluator_reads_no_installed_bytes() -> None:
    """The child prover is the byte authority; evaluate only parses recorded paths, so an
    evaluation over paths that do not exist on this host still passes."""
    evidence = passing_evidence()
    assert not os.path.lexists(SITE)

    assert evaluate(evidence)["status"] == "PASS"


# --- real filesystem cases: symlinks and prefix aliases (disposable temp trees only) -----


def _layout(root: Path) -> Path:
    """A disposable venv-shaped tree; returns its site-packages directory."""
    site = root / "venv" / "lib" / "python3.12" / "site-packages"
    for package in w.PACKAGES:
        (site / package).mkdir(parents=True)
        (site / f"{package}-0.0.0.dist-info").mkdir()
    return site


def _canonical_evidence(shape: str, venv: Path, prefix: str | None = None) -> dict[str, Any]:
    evidence = SHAPES[shape]()
    _relocate(evidence, str(venv))
    if prefix is not None:
        for provenance in _provenances(evidence):
            provenance["interpreter"]["prefix"] = prefix
    return evidence


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_real_canonical_tree_passes(tmp_path: Path, shape: str) -> None:
    root = tmp_path.resolve()
    _layout(root)

    assert evaluate(_canonical_evidence(shape, root / "venv"))["status"] in {"PASS", "INCONCLUSIVE"}
    assert evaluate(_canonical_evidence(shape, root / "venv"))["failure_reasons"] == []


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_symlinked_prefix_alias_is_valid_when_every_path_is_canonical(
    tmp_path: Path, shape: str
) -> None:
    """Both sides are resolved: the recorded prefix may be an alias of the real venv."""
    root = tmp_path.resolve()
    _layout(root)
    (root / "alias").symlink_to(root / "venv")

    evidence = _canonical_evidence(shape, root / "venv", prefix=str(root / "alias"))

    assert evaluate(evidence)["failure_reasons"] == []


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_paths_spelled_through_the_alias_are_not_canonical_and_fail(
    tmp_path: Path, shape: str
) -> None:
    root = tmp_path.resolve()
    _layout(root)
    (root / "alias").symlink_to(root / "venv")

    evidence = _canonical_evidence(shape, root / "alias")

    verdict = evaluate(evidence)
    assert verdict["status"] == "FAIL"
    assert any(r.startswith("capture:origin-") for r in verdict["failure_reasons"])


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_prefix_alias_of_a_different_venv_does_not_contain_the_paths(
    tmp_path: Path, shape: str
) -> None:
    root = tmp_path.resolve()
    _layout(root)
    (root / "other").mkdir()
    (root / "alias").symlink_to(root / "other")

    evidence = _canonical_evidence(shape, root / "venv", prefix=str(root / "alias"))

    verdict = evaluate(evidence)
    assert verdict["status"] == "FAIL"
    assert any(r.startswith("capture:origin-") for r in verdict["failure_reasons"])


SYMLINKS = [
    "file-symlink-out-of-the-prefix",
    "package-directory-symlink",
    "record-directory-symlink",
]


@pytest.mark.parametrize("shape", sorted(SHAPES))
@pytest.mark.parametrize("kind", SYMLINKS)
def test_a_symlink_that_leaves_the_prefix_fails_the_first_proved_phase(
    tmp_path: Path, shape: str, kind: str
) -> None:
    root = tmp_path.resolve()
    site = _layout(root)
    outside = root / "outside"
    outside.mkdir()
    for package in w.PACKAGES:
        if kind == "file-symlink-out-of-the-prefix":
            (outside / "x.py").write_text("")
            (site / package / "escape.py").symlink_to(outside / "x.py")
        elif kind == "package-directory-symlink":
            (outside / package).mkdir()
            (site / package).rmdir()
            (site / package).symlink_to(outside / package)
        else:
            (outside / f"{package}-0.0.0.dist-info").mkdir()
            (site / f"{package}-0.0.0.dist-info").rmdir()
            (site / f"{package}-0.0.0.dist-info").symlink_to(outside / f"{package}-0.0.0.dist-info")
    evidence = _canonical_evidence(shape, root / "venv")

    def spell(package: str, entry: dict[str, Any]) -> None:
        if kind == "file-symlink-out-of-the-prefix":
            entry.update(_files(package, f"{site}/{package}/escape.py"))

    _mutate_everywhere(evidence, spell)

    verdict = evaluate(evidence)

    assert verdict["status"] == "FAIL", kind
    assert any(r.startswith("capture:origin-") for r in verdict["failure_reasons"]), kind


# --- the layout rule is grounded in the workspace, not invented ---------------------------


def test_the_expected_distribution_version_is_the_workspace_version() -> None:
    """One source of truth: every workspace project's own version is the pinned constant, and
    its normalised project name is the package `installed_origins` reports."""
    root = Path(__file__).resolve().parent.parent
    projects = {}
    for path in sorted(root.glob("harness-*/pyproject.toml")):
        project = tomllib.loads(path.read_text())["project"]
        projects[project["name"].replace("-", "_")] = project["version"]

    assert set(projects) == w.PACKAGES
    assert set(projects.values()) == {w.WORKSPACE_DIST_VERSION}


# --- the recording seam: A's provenance exists before its held body ----------------------


def test_run_phase_writes_the_provenance_record_before_the_body_and_the_result_after(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    layout = w.Layout(tmp_path)
    layout.results.mkdir()
    seen: dict[str, Any] = {}

    def body(_layout: w.Layout) -> dict[str, object]:
        # The parent kills the held A here, so nothing after this line is guaranteed to run.
        seen["record_existed"] = layout.provenance_record("resume-a").exists()
        seen["result_existed"] = layout.result("resume-a").exists()
        return {"body": "ran"}

    monkeypatch.setitem(w.PHASE_BODIES, "resume-a", body)

    code = w.run_phase(layout, "resume-a", lambda: {"installed_origins": {}, "marker": "p"})

    assert code == 0
    assert seen == {"record_existed": True, "result_existed": False}
    record = json.loads(layout.provenance_record("resume-a").read_text())
    assert record["phase"] == "resume-a" and record["stage"] == "pre-body"
    assert (record["pid"], record["pgid"]) == (os.getpid(), os.getpgid(0))
    assert type(record["loaded_harness_modules"]) is int
    assert record["provenance"] == {"installed_origins": {}, "marker": "p"}
    result = json.loads(layout.result("resume-a").read_text())
    assert result["ok"] is True and result["observed"] == {"body": "ran"}


def test_a_killed_held_a_leaves_its_provenance_record_and_no_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    layout = w.Layout(tmp_path)
    layout.results.mkdir()

    class Killed(BaseException):
        """Stands in for SIGKILL: nothing after the body's start is recorded."""

    def body(_layout: w.Layout) -> dict[str, object]:
        raise Killed

    monkeypatch.setitem(w.PHASE_BODIES, "resume-a", body)

    with pytest.raises(Killed):
        w.run_phase(layout, "resume-a", lambda: {"installed_origins": {}})

    assert layout.provenance_record("resume-a").exists()
    crashed = json.loads(layout.result("resume-a").read_text())
    assert crashed["ok"] is False  # a crash is recorded evidence, never a pass


def test_a_child_that_cannot_prove_itself_leaves_no_provenance_record(
    tmp_path: Path,
) -> None:
    layout = w.Layout(tmp_path)
    layout.results.mkdir()

    def prove() -> dict[str, object]:
        raise ValueError("not an isolated installed interpreter")

    with pytest.raises(ValueError):
        w.run_phase(layout, "resume-a", prove)

    assert not layout.provenance_record("resume-a").exists()


def test_read_record_marks_unreadable_records_instead_of_treating_them_as_absent(
    tmp_path: Path,
) -> None:
    assert w.read_record(tmp_path / "absent.json") is None
    (tmp_path / "garbage.json").write_text("{not json")
    (tmp_path / "list.json").write_text("[1]")
    (tmp_path / "ok.json").write_text('{"pid": 1}')

    assert w.read_record(tmp_path / "garbage.json") == {"unreadable": True}
    assert w.read_record(tmp_path / "list.json") == {"unreadable": True}
    assert w.read_record(tmp_path / "ok.json") == {"pid": 1}
