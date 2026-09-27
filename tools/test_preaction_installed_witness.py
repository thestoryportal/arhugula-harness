"""Pure checks of the nested PRE_ACTION witness: its verdict, its gates and its shared-owner wiring.

Nothing here bootstraps a harness, resumes a workflow or touches an installed venv. The G1 source
rehearsal (every scenario through the public API, one process per phase) is opt-in through
`PREACTION_G1_*` variables and is never installed acceptance; the installed `run` needs its own
approval.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import installed_witness_provenance as prover
import preaction_installed_witness as pw
from test_installed_witness_provenance import Fixture

TOOLS = Path(__file__).resolve().parent
RECEIPT = "e" * 64
VENV = "/venv"
SITE = f"{VENV}/lib/python3.12/site-packages"
EXITED = {
    "exit": 0,
    "timeout": False,
    "output_ok": True,
    "kill": None,
    "group_survivors": False,
}
KEYS = [pw.KEY_A, pw.KEY_C]
CHAIN = [
    {"workflow_id": pw.ROOT_ID, "run_id": "r" * 32},
    {"workflow_id": pw.MID_ID, "run_id": "m" * 64},
    {"workflow_id": pw.LEAF_ID, "run_id": "l" * 64},
]
REF = {"record_count": 1, "latest_digest": "a" * 64}
REF2 = {"record_count": 2, "latest_digest": "b" * 64}
GONE = {"pgid": 1, "signal": "SIGKILL", "returncode": -signal.SIGKILL, "group_gone": True}


def origins() -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for package in sorted(prover.PACKAGES):
        files = [f"{SITE}/{package}/__init__.py", f"{SITE}/{package}/core.py"]
        result[package] = {
            "record_path": f"{SITE}/{package}-0.0.0.dist-info/RECORD",
            "record_sha256": hashlib.sha256(package.encode()).hexdigest(),
            "python_files_checked": 2,
            "verified_files": sorted(files),
        }
    return result


def provenance() -> dict[str, Any]:
    return {
        "interpreter": {"isolated": 1, "no_user_site": 1, "prefix": VENV},
        "installation_receipt_sha256": RECEIPT,
        "installed_origins": origins(),
    }


def audits(keys: list[str], *, od: list[str] | None = None) -> dict[str, Any]:
    return {
        "entry_count": 40,
        "entries": [{"key": k, "action_id": k} for k in keys],
        "od_entries": [
            {"key": k, "gate_level": "ask", "response": "approve"}
            for k in (keys if od is None else od)
        ],
    }


def run_observed() -> dict[str, Any]:
    return {"status": "paused", "depth": 0, "chain": copy.deepcopy(CHAIN), "audits": audits([])}


def resume_observed(status: str, keys: list[str], ref: dict[str, Any]) -> dict[str, Any]:
    return {
        "outcome": "returned",
        "status": status,
        "addressed_run_id": CHAIN[-1]["run_id"],
        "before_ref": REF,
        "ref": ref,
        "before_claim": {"phase": "started"},
        "chain": copy.deepcopy(CHAIN),
        "audits": audits(keys),
    }


CLAIM_REFUSED = "harness_runtime.lifecycle.root_resume_admission.ResumeClaimRefusedError"
DECLARED = {
    pw.ROOT_ID: [],
    pw.MID_ID: [["witness.a"], ["witness.c"]],
    pw.LEAF_ID: [["witness.z"]],
}


def levels() -> list[dict[str, Any]]:
    return [
        {"workflow_id": pw.ROOT_ID, "pause_reason": "hitl_pending", "branches": []},
        {"workflow_id": pw.MID_ID, "pause_reason": "hitl_pending", "branches": []},
        {"workflow_id": pw.LEAF_ID, "pause_reason": "hitl_pending", "branches": []},
    ]


def lowered_refusal() -> dict[str, Any]:
    """The required shape: a terminal FAILED carrying the child's refusal, no new root record."""
    return {
        **resume_observed("failed", [], REF),
        "failure_cause": {
            "runtime_fail_class": "RT-FAIL-WORKFLOW",
            "detail": "workflow execution returned status='failed' with the CP fail class",
            "validator_fail_class": f"{pw.ROOT_FAMILY}-child-resume-refused ({pw.REFUSAL_REASON})",
        },
        "has_pause_snapshot": False,
        "levels": levels(),
        "declared_placements": copy.deepcopy(DECLARED),
    }


def claim_refused_again() -> dict[str, Any]:
    return {
        "outcome": "raised",
        "error_type": CLAIM_REFUSED,
        "reason": "claim-refused",
        "addressed_run_id": CHAIN[-1]["run_id"],
        "before_ref": REF,
        "ref": REF,
        "before_claim": {"phase": "started"},
        "chain": copy.deepcopy(CHAIN),
        "audits": audits([]),
        "levels": levels(),
        "declared_placements": copy.deepcopy(DECLARED),
    }


def current_bad_paused_shape() -> dict[str, Any]:
    """What b4b14049 does: the refusal is lost, a NEW root record is captured, root pauses."""
    bad = {**resume_observed("paused", [], REF2), "chain": CHAIN[:2]}
    return {
        **bad,
        "failure_cause": None,
        "has_pause_snapshot": True,
        "levels": levels()[:2],
        "declared_placements": copy.deepcopy(DECLARED),
    }


def _ok(phase: str, observed: dict[str, Any]) -> dict[str, Any]:
    record = {"phase": phase, "ok": True, "observed": observed, "provenance": provenance()}
    return {**record, "loaded_harness_modules": 12}


def svc(webhooks: list[str], **tools: int) -> dict[str, Any]:
    return {"webhook_keys": list(webhooks), "tool_counts": dict(tools)}


def scenario(name: str) -> dict[str, Any]:
    if name == "p":
        results = {
            "run": run_observed(),
            "resume-1": resume_observed("paused", [pw.KEY_A], REF2),
            "resume-2": resume_observed("completed", KEYS, REF2),
        }
        services = {
            "run": svc([pw.KEY_A], **{"witness.b": 3}),
            "resume-1": svc(KEYS, **{"witness.a": 1, "witness.b": 3}),
            "resume-2": svc(
                KEYS, **{"witness.a": 1, "witness.b": 3, "witness.c": 1, "witness.d": 1}
            ),
        }
    elif name == "n1":
        results = {
            "run": run_observed(),
            "resume-lowered": lowered_refusal(),
            "resume-lowered-again": claim_refused_again(),
        }
        services = {
            "run": svc([pw.KEY_A], **{"witness.b": 3}),
            "resume-lowered": svc([pw.KEY_A], **{"witness.b": 3}),
            "resume-lowered-again": svc([pw.KEY_A], **{"witness.b": 3}),
        }
    else:
        direct = {
            "outcome": "raised",
            "error_type": "harness_runtime.api.ResumeDirectChildHandleError",
            "leaf_depth": 2,
            "leaf_claim": {"phase": "absent"},
            "root_before_ref": REF,
            "root_ref": REF,
            "root_before_claim": {"phase": "absent", "claim_sha256": None},
            "root_claim": {"phase": "absent", "claim_sha256": None},
            "audits": audits([]),
        }
        results = {"run": run_observed(), "resume-child-handle": direct}
        services = {
            "run": svc([pw.KEY_A], **{"witness.b": 3}),
            "resume-child-handle": svc([pw.KEY_A], **{"witness.b": 3}),
        }
    return {
        "runs": {phase: {**EXITED, "pid": 5, "pgid": 5} for phase in results},
        "results": {phase: _ok(phase, observed) for phase, observed in results.items()},
        "services": services,
        "tool_server": {"kill": dict(GONE), "ready": True},
        "webhook_errors": [],
    }


def honest() -> dict[str, Any]:
    return {name: scenario(name) for name in pw.SCENARIOS}


def verdict(evidence: dict[str, Any], receipt: str | None = RECEIPT) -> dict[str, Any]:
    return pw.evaluate(evidence, expected_receipt_sha256=receipt)


def test_honest_installed_evidence_passes() -> None:
    result = verdict(honest())

    assert result["status"] == "PASS" and result["failure_reasons"] == []
    assert result["phase_states"]["p"] == ["Completed"] * 3


def test_rehearsal_evidence_without_provenance_is_labelled_and_never_an_installed_pass() -> None:
    evidence = honest()
    for ev in evidence.values():
        for record in ev["results"].values():
            del record["provenance"], record["loaded_harness_modules"]

    assert verdict(evidence, receipt=None)["status"] == "REHEARSAL-PASS"
    installed = verdict(evidence)  # the same records judged as installed evidence
    assert installed["status"] == "FAIL"
    assert any("provenance-missing" in r for r in installed["failure_reasons"])


def _at(evidence: dict[str, Any], path: str) -> tuple[Any, str]:
    node: Any = evidence
    *parents, last = path.split("/")
    for part in parents:
        node = node[part]
    return node, last


def set_(path: str, value: Any) -> Callable[[dict[str, Any]], None]:
    def mutate(evidence: dict[str, Any]) -> None:
        node, last = _at(evidence, path)
        node[last] = value

    return mutate


def drop(path: str) -> Callable[[dict[str, Any]], None]:
    def mutate(evidence: dict[str, Any]) -> None:
        node, last = _at(evidence, path)
        del node[last]

    return mutate


P_RUN = "p/results/run/observed"
P_R1 = "p/results/resume-1/observed"
P_R2 = "p/results/resume-2/observed"
S = "p/services"
LOW = "n1/results/resume-lowered/observed"
AGAIN = "n1/results/resume-lowered-again/observed"
DIRECT = "n2/results/resume-child-handle/observed"
GATE_A = "witness.a"
BEHAVIOUR: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
    # inheritance missing: the leaf's gated tool ran before any approval, or never paused
    (
        "a-ran-before-approval",
        set_(f"{S}/run/tool_counts/{GATE_A}", 1),
        "p:run:inheritance-missing",
    ),
    ("no-pause-webhook", set_(f"{S}/run/webhook_keys", []), "p:run:webhook:missing"),
    ("run-completed", set_(f"{P_RUN}/status", "completed"), "p:run:not-paused"),
    ("carrier-missing-leaf", set_(f"{P_RUN}/chain", CHAIN[:2]), "p:run:nested-carrier-missing"),
    ("root-depth", set_(f"{P_RUN}/depth", 1), "p:run:root-depth-not-zero"),
    # filter leakage: an ungated tool produced a prompt or an audit
    (
        "webhook-for-b",
        set_(f"{S}/resume-2/webhook_keys", [*KEYS, "hitl:workflow:x:step:0:pre-action"]),
        "filter-leakage",
    ),
    (
        "f2-for-d",
        set_(f"{P_R2}/audits", audits([*KEYS, "hitl:workflow:x:step:3:pre-action"])),
        "p:resume-2:f2:filter-leakage",
    ),
    # duplicates: one prompt, one audit, one dispatch per gated action
    (
        "webhook-twice",
        set_(f"{S}/resume-1/webhook_keys", [pw.KEY_A, pw.KEY_A, pw.KEY_C]),
        "webhook:duplicate",
    ),
    ("f2-twice", set_(f"{P_R1}/audits", audits([pw.KEY_A, pw.KEY_A])), "f2:duplicate"),
    ("od-without-f2", set_(f"{P_R1}/audits", audits([pw.KEY_A], od=[])), "od:missing"),
    ("a-twice", set_(f"{S}/resume-1/tool_counts/{GATE_A}", 2), "p:resume-1:duplicate:witness.a"),
    # placement lost across resume: c ran without a second pause
    ("c-without-second-pause", set_(f"{P_R1}/status", "completed"), "placement-lost-across-resume"),
    (
        "c-ran-early",
        set_(f"{S}/resume-1/tool_counts/witness.c", 1),
        "p:resume-1:inheritance-missing:witness.c",
    ),
    # replay of completed orchestrator effects
    ("b-replayed", set_(f"{S}/resume-1/tool_counts/witness.b", 4), "p:resume-1:replay:witness.b"),
    ("d-twice", set_(f"{S}/resume-2/tool_counts/witness.d", 2), "p:resume-2:duplicate:witness.d"),
    ("d-missing", drop(f"{S}/resume-2/tool_counts/witness.d"), "effect-missing:witness.d"),
    # addressing, approval and claim facts
    (
        "wrong-leaf-run-id",
        set_(f"{P_R1}/addressed_run_id", "x" * 64),
        "response-not-addressed-to-leaf",
    ),
    (
        "not-approved",
        set_(
            f"{P_R1}/audits",
            {
                **audits([pw.KEY_A]),
                "od_entries": [{"key": pw.KEY_A, "gate_level": "ask", "response": "reject"}],
            },
        ),
        "od-not-approved-at-ask",
    ),
    (
        "gate-auto",
        set_(
            f"{P_R1}/audits",
            {
                **audits([pw.KEY_A]),
                "od_entries": [{"key": pw.KEY_A, "gate_level": "auto", "response": "approve"}],
            },
        ),
        "od-not-approved-at-ask",
    ),
    (
        "prior-claim-not-started",
        set_(f"{P_R1}/before_claim/phase", "claimed"),
        "prior-claim-not-started",
    ),
    ("record-not-advanced", set_(f"{P_R1}/ref", REF), "record-not-advanced"),
    ("resume-2-not-completed", set_(f"{P_R2}/status", "paused"), "p:resume-2:not-completed"),
    ("resume-raised", set_(f"{P_R1}/outcome", "raised"), "p:resume-1:not-returned"),
    # N1: the parent's placement was lowered; the first resume must end as a terminal refusal
    (
        "n1-completed-without-child",
        set_(f"{LOW}/status", "completed"),
        "n1:resume-lowered:completed-without-the-child",
    ),
    (
        "n1-paused-instead-of-refused",
        set_(f"{LOW}/status", "paused"),
        "n1:resume-lowered:paused-instead-of-refused",
    ),
    (
        "n1-new-pause-snapshot",
        set_(f"{LOW}/has_pause_snapshot", True),
        "n1:resume-lowered:new-pause-snapshot",
    ),
    (
        "n1-root-record-advanced",
        set_(f"{LOW}/ref", REF2),
        "n1:resume-lowered:root-record-advanced",
    ),
    (
        "n1-refusal-reason-missing",
        set_(f"{LOW}/failure_cause", None),
        "n1:resume-lowered:child-refusal-reason-missing",
    ),
    (
        "n1-raw-leaf-class-at-the-root",
        set_(
            f"{LOW}/failure_cause/validator_fail_class",
            "linear-resume-hitl-gate-config-changed at step 1",
        ),
        "n1:resume-lowered:terminal-refusal-grammar",
    ),
    (
        "n1-wrong-family",
        set_(
            f"{LOW}/failure_cause/validator_fail_class",
            "parallelization-child-resume-refused (hitl-gate-config-changed)",
        ),
        "n1:resume-lowered:terminal-refusal-wrong-family",
    ),
    (
        "n1-reason-embedded-in-another-token",
        set_(
            f"{LOW}/failure_cause/validator_fail_class",
            "orchestrator-workers-child-resume-refused (xhitl-gate-config-changed-extra)",
        ),
        "n1:resume-lowered:child-refusal-reason-missing",
    ),
    (
        "n1-grammar-quoted-inside-other-text",
        set_(
            f"{LOW}/failure_cause/validator_fail_class",
            "note orchestrator-workers-child-resume-refused (hitl-gate-config-changed)",
        ),
        "n1:resume-lowered:terminal-refusal-grammar",
    ),
    (
        "n1-text-after-the-terminal-grammar",
        set_(
            f"{LOW}/failure_cause/validator_fail_class",
            "orchestrator-workers-child-resume-refused (hitl-gate-config-changed) at step 1",
        ),
        "n1:resume-lowered:terminal-refusal-grammar",
    ),
    (
        "n1-refusal-reason-unrelated",
        set_(f"{LOW}/failure_cause/validator_fail_class", "some other failure"),
        "n1:resume-lowered:terminal-refusal-grammar",
    ),
    (
        "n1-reason-only-in-human-detail",
        set_(
            f"{LOW}/failure_cause",
            {
                "runtime_fail_class": "RT-FAIL-WORKFLOW",
                "detail": "fail_class='linear-resume-hitl-gate-config-changed at step 1'",
                "validator_fail_class": None,
            },
        ),
        "n1:resume-lowered:child-refusal-reason-missing",
    ),
    (
        "n1-arbitrary-failed-is-not-a-refusal",
        set_(f"{LOW}/failure_cause/validator_fail_class", "step-body-raised"),
        "n1:resume-lowered:terminal-refusal-grammar",
    ),
    (
        "n1-failure-is-not-a-workflow-failure",
        set_(f"{LOW}/failure_cause/runtime_fail_class", "RT-FAIL-DRAIN-TIMEOUT"),
        "n1:resume-lowered:failure-not-a-workflow-failure",
    ),
    (
        "n1-a-ran",
        set_("n1/services/resume-lowered/tool_counts/witness.a", 1),
        "n1:resume-lowered:inheritance-missing:witness.a",
    ),
    (
        "n1-audit-written",
        set_(f"{LOW}/audits", audits([pw.KEY_A])),
        "n1:resume-lowered:f2:unexpected",
    ),
    (
        "n1-new-webhook",
        set_("n1/services/resume-lowered/webhook_keys", [pw.KEY_A, pw.KEY_C]),
        "n1:resume-lowered:webhook:unexpected",
    ),
    (
        "n1-claim-not-admitted",
        set_(f"{LOW}/before_claim/phase", "absent"),
        "root-claim-not-admitted",
    ),
    (
        "n1-second-resume-not-refused",
        set_(f"{AGAIN}/outcome", "returned"),
        "n1:resume-lowered-again:not-claim-refused",
    ),
    (
        "n1-second-resume-wrong-refusal",
        set_(f"{AGAIN}/reason", "placement"),
        "n1:resume-lowered-again:not-claim-refused",
    ),
    (
        "n1-second-resume-other-record",
        set_(f"{AGAIN}/before_ref", REF2),
        "n1:resume-lowered-again:different-record",
    ),
    (
        "n1-second-resume-effect",
        set_("n1/services/resume-lowered-again/tool_counts/witness.d", 1),
        "n1:resume-lowered-again:inheritance-missing:witness.d",
    ),
    (
        "n1-mid-lost-its-own-a-placement",
        set_(f"{LOW}/declared_placements/{pw.MID_ID}", [["witness.c"]]),
        "n1:fixture:mid-lost-own-a-placement",
    ),
    # N2: a direct child handle
    ("n2-not-refused", set_(f"{DIRECT}/outcome", "returned"), "n2:direct-child-handle-not-refused"),
    (
        "n2-wrong-error",
        set_(f"{DIRECT}/error_type", "builtins.ValueError"),
        "n2:direct-child-handle-not-refused",
    ),
    ("n2-root-depth", set_(f"{DIRECT}/leaf_depth", 0), "n2:leaf-record-not-below-root"),
    ("n2-root-record-changed", set_(f"{DIRECT}/root_ref", REF2), "n2:root-record-changed"),
    (
        "n2-root-claim-created",
        set_(f"{DIRECT}/root_claim", {"phase": "started", "claim_sha256": "c" * 64}),
        "n2:root-claim-changed",
    ),
    ("n2-root-record-unobserved", drop(f"{DIRECT}/root_ref"), "n2:root-record-unobserved"),
    ("n2-root-claim-unobserved", drop(f"{DIRECT}/root_before_claim"), "n2:root-claim-unobserved"),
    (
        "n1-root-record-unobserved",
        drop(f"{LOW}/ref"),
        "n1:resume-lowered:root-record-unobserved",
    ),
    (
        "n1-second-resume-record-unobserved",
        drop(f"{AGAIN}/before_ref"),
        "n1:resume-lowered-again:different-record|n1:resume-lowered-again:record-unobserved",
    ),
    (
        "n2-claim-created",
        set_(f"{DIRECT}/leaf_claim/phase", "claimed"),
        "n2:claim-created-for-refused-handle",
    ),
    (
        "n2-effect",
        set_("n2/services/resume-child-handle/tool_counts/witness.c", 1),
        "n2:resume:inheritance-missing:witness.c",
    ),
    # owned services
    ("webhook-errors", set_("p/webhook_errors", ["bad request"]), "p:webhook-listener-errors"),
    (
        "tool-server-not-killed",
        set_("p/tool_server/kill", {**GONE, "group_gone": False}),
        "p:tool-server:group-not-gone",
    ),
    ("tool-server-kill-missing", set_("p/tool_server/kill", None), "p:tool-server:kill-missing"),
    (
        "child-group-survived",
        set_("p/runs/run/group_survivors", True),
        "p:run:surviving-process-group",
    ),
    ("survivor-unproven", drop("n2/runs/run/group_survivors"), "n2:run:surviving-process-group"),
]


@pytest.mark.parametrize(("name", "mutate", "reason"), BEHAVIOUR, ids=[b[0] for b in BEHAVIOUR])
def test_each_broken_property_fails_the_verdict_with_its_named_reason(
    name: str, mutate: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = honest()
    mutate(evidence)

    result = verdict(evidence)

    assert result["status"] == "FAIL", name
    assert any(any(part in r for part in reason.split("|")) for r in result["failure_reasons"]), (
        name,
        result["failure_reasons"],
    )


def prov(path: str) -> str:
    return f"p/results/run/provenance/{path}"


PROVENANCE: list[tuple[str, Callable[[dict[str, Any]], None], str]] = [
    ("receipt-mismatch", set_(prov("installation_receipt_sha256"), "1" * 64), "receipt-mismatch"),
    ("receipt-missing", drop(prov("installation_receipt_sha256")), "receipt-missing"),
    ("origins-empty", set_(prov("installed_origins"), {}), "origins-incomplete"),
    ("origin-none", set_(prov("installed_origins/harness_cp"), None), "origin-malformed"),
    (
        "origin-files-empty",
        set_(prov("installed_origins/harness_cp/verified_files"), []),
        "origin-files-invalid",
    ),
    (
        "origin-outside-prefix",
        set_(prov("interpreter/prefix"), "/elsewhere"),
        "origin-record-path-invalid",
    ),
    ("not-isolated", set_(prov("interpreter/isolated"), 0), "not-isolated"),
    ("zero-modules", set_("p/results/run/loaded_harness_modules", 0), "loaded-modules-invalid"),
    ("bool-modules", set_("p/results/run/loaded_harness_modules", True), "loaded-modules-invalid"),
    ("provenance-missing", drop("p/results/run/provenance"), "provenance-missing"),
]


@pytest.mark.parametrize(("name", "mutate", "reason"), PROVENANCE, ids=[b[0] for b in PROVENANCE])
def test_a_phase_without_proved_installed_provenance_is_broken(
    name: str, mutate: Callable[[dict[str, Any]], None], reason: str
) -> None:
    evidence = honest()
    mutate(evidence)

    result = verdict(evidence)

    assert result["status"] == "FAIL", name
    assert any(reason in r for r in result["failure_reasons"]), (name, result["failure_reasons"])
    assert result["phase_states"]["p"][0] == "Broken"


def test_a_phase_that_fails_or_times_out_uses_the_reviewed_grammar() -> None:
    timed_out = honest()
    timed_out["p"]["runs"]["resume-2"] = {
        **EXITED,
        "exit": None,
        "timeout": True,
        "kill": dict(GONE),
        "pid": 5,
        "pgid": 5,
    }
    del timed_out["p"]["results"]["resume-2"]
    assert verdict(timed_out)["status"] == "INCONCLUSIVE"

    later = copy.deepcopy(timed_out)  # a completed phase after the timeout breaks the grammar
    later["p"]["results"]["resume-2"] = _ok("resume-2", resume_observed("completed", KEYS, REF2))
    later["p"]["runs"]["resume-2"] = {**EXITED, "pid": 5, "pgid": 5}
    later["p"]["runs"]["resume-1"] = {**timed_out["p"]["runs"]["resume-2"]}
    del later["p"]["results"]["resume-1"]
    assert verdict(later)["status"] == "FAIL"

    two = copy.deepcopy(timed_out)
    two["n2"]["runs"]["resume-child-handle"] = dict(timed_out["p"]["runs"]["resume-2"])
    del two["n2"]["results"]["resume-child-handle"]
    assert verdict(two)["status"] == "FAIL"

    nonzero = honest()
    nonzero["n1"]["runs"]["resume-lowered"]["exit"] = 1
    assert verdict(nonzero)["status"] == "FAIL"


def test_the_verdict_never_rests_on_exit_zero_alone() -> None:
    evidence = honest()
    for ev in evidence.values():
        ev["results"] = {}

    assert verdict(evidence)["status"] == "FAIL"


# --- N3: the shared prover refuses before any service or child ------------------------------------


@pytest.fixture
def fx(tmp_path: Path) -> Fixture:
    return Fixture(tmp_path)


@pytest.fixture
def nothing_may_start(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    started: list[str] = []

    def boom(*_args: object, **_kwargs: object) -> object:
        started.append("started")
        raise AssertionError("a service or child started before provenance was proved")

    monkeypatch.setattr(pw, "with_services", boom)
    monkeypatch.setattr(pw.HELPERS, "spawn", boom)
    return started


def _run(fx: Fixture, tmp_path: Path, *, head: str | None = None) -> None:
    pw.run(
        fx.candidate,
        fx.venv,
        head or fx.head,
        fx.receipt_path,
        tmp_path / "scenarios",
        tmp_path / "out" / "report.json",
    )


def test_a_wrong_pin_is_refused_before_anything_starts(
    fx: Fixture, tmp_path: Path, nothing_may_start: list[str]
) -> None:
    with pytest.raises(ValueError, match="differs from pin or tree is not clean"):
        _run(fx, tmp_path, head="3" * 40)

    assert nothing_may_start == [] and not (tmp_path / "scenarios").exists()


def _receipt_head(receipt: dict[str, Any]) -> None:
    receipt.update(candidate_head="4" * 40)


def _receipt_venv(receipt: dict[str, Any]) -> None:
    receipt.update(venv="/other/venv")


def _receipt_startup(receipt: dict[str, Any]) -> None:
    receipt["startup_hooks"]["files"]["_virtualenv.py"] = "5" * 64


def _receipt_wheel(receipt: dict[str, Any]) -> None:
    receipt["wheels"][0]["sha256"] = "6" * 64


def _receipt_records(receipt: dict[str, Any]) -> None:
    receipt["installed_record_sha256"].pop("harness_cp")


@pytest.mark.parametrize(
    "mutate",
    [_receipt_head, _receipt_venv, _receipt_startup, _receipt_wheel, _receipt_records],
    ids=["receipt-head", "receipt-venv", "startup-pin", "wheel-pin", "record-hashes"],
)
def test_a_mismatched_receipt_is_refused_before_anything_starts(
    fx: Fixture,
    tmp_path: Path,
    nothing_may_start: list[str],
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    mutate(fx.receipt)
    fx.write_receipt()

    with pytest.raises(ValueError):
        _run(fx, tmp_path)

    assert nothing_may_start == []
    assert not (tmp_path / "scenarios").exists() and not (tmp_path / "out").exists()


def test_a_changed_startup_hook_is_refused_before_anything_starts(
    fx: Fixture, tmp_path: Path, nothing_may_start: list[str]
) -> None:
    (fx.site / "_virtualenv.py").write_bytes(b"# tampered\n")

    with pytest.raises(ValueError, match="startup hook differs"):
        _run(fx, tmp_path)

    assert nothing_may_start == []


# --- one owner and a stable public surface --------------------------------------------------------


def test_the_witness_reuses_the_shared_prover_and_the_b104_process_helpers() -> None:
    import ast

    assert pw.PROVER is prover
    assert pw.SHARED_PROVER_PATH == TOOLS / "installed_witness_provenance.py"
    tree = ast.parse((TOOLS / "preaction_installed_witness.py").read_text())
    defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    duplicated = {
        "provenance_reasons",
        "origin_reasons",
        "checked_provenance",
        "checked_candidate",
        "installed_origins",
        "spawn",
        "kill_group",
        "finish",
        "parse_waited_phase",
        "sequence_failures",
    }
    assert defined.isdisjoint(duplicated)


def test_the_public_plan_command_runs_under_isolated_mode_and_matches_the_plan() -> None:
    """The installed child is `python -I <helper>`: it must load its siblings unaided."""
    result = subprocess.run(
        [sys.executable, "-I", str(TOOLS / "preaction_installed_witness.py"), "plan"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == pw.PLAN


def test_the_installed_child_command_line_keeps_isolation() -> None:
    argv = pw.child_argv_installed(Path("/venv/bin/python"), Path("/h.py"), "p", "run", ["--x"])

    assert argv[:3] == ["/venv/bin/python", "-I", "/h.py"] and "--source-rehearsal" not in argv
    source = pw.child_argv_source(Path("/py"), Path("/h.py"), "p", "run", [])
    assert "-I" not in source and "--source-rehearsal" in source


def test_the_scenario_plan_matches_the_reviewed_design() -> None:
    assert pw.PHASES_P == ("run", "resume-1", "resume-2")
    assert set(pw.SCENARIOS) == {"p", "n1", "n2"}
    assert (pw.CHILD_CAP_SECONDS, pw.OVERALL_CAP_SECONDS) == (60, 600)
    assert pw.KEY_A.endswith(":step:1:pre-action") and pw.KEY_C.endswith(":step:2:pre-action")


def _starter(tmp_path: Path, argv: list[str]) -> Callable[[str], Any]:
    return lambda phase: pw.HELPERS.spawn(
        argv, {"PATH": "/usr/bin:/bin"}, tmp_path, tmp_path, phase
    )


def test_settle_kills_only_an_owned_unsettled_group_then_never_signals_it_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fleet = pw.Fleet()
    running = fleet.launch(_starter(tmp_path, ["sleep", "30"]), "running")
    exited = fleet.launch(_starter(tmp_path, ["true"]), "exited")
    bystander = subprocess.Popen(["sleep", "30"], start_new_session=True)
    try:
        exited.proc.wait(timeout=5)
        assert fleet.settle(exited.proc.pid) is False  # nothing outlived it
        assert fleet.settle(running.proc.pid) is True  # a live member: reported and killed
        assert not _alive(running.proc.pid)

        signalled: list[int] = []
        real_killpg = os.killpg

        def record(pgid: int, sig: int) -> None:
            signalled.append(pgid)
            real_killpg(pgid, sig)

        monkeypatch.setattr(os, "killpg", record)
        for pgid in (running.proc.pid, exited.proc.pid, bystander.pid):
            with pytest.raises(ValueError, match="not an owned unsettled group"):
                fleet.settle(pgid)
        assert fleet.settle_all() == []
        assert signalled == [], "a settled or unrelated group was signalled"
        assert bystander.poll() is None
    finally:
        monkeypatch.undo()
        for child in (running.proc, bystander):
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)


def _term_blocked(native_id: int) -> bool:
    status = Path(f"/proc/self/task/{native_id}/status").read_text()
    [mask] = [line.split()[1] for line in status.splitlines() if line.startswith("SigBlk:")]
    return bool(int(mask, 16) >> (signal.SIGTERM - 1) & 1)


def test_the_webhook_thread_blocks_term_even_when_started_by_an_unmasked_caller() -> None:
    """Started from an unmasked caller, the listener still blocks TERM for its whole life."""
    assert signal.SIGTERM not in signal.pthread_sigmask(signal.SIG_BLOCK, [])
    capture = pw.WebhookCapture()
    capture.start()
    try:
        native_id = capture.thread.native_id
        assert native_id is not None
        assert _term_blocked(native_id)
    finally:  # the server's own API, so a broken capture can never leave its thread running
        capture.server.shutdown()
        capture.server.server_close()


def test_a_failed_group_kill_stays_owned_and_never_strands_the_other_groups(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fleet = pw.Fleet()
    children = [fleet.launch(_starter(tmp_path, ["sleep", "30"]), f"c{i}") for i in range(2)]
    real_killpg = os.killpg
    refused: list[int] = []

    def refuse_the_first_kill(pgid: int, sig: int) -> None:
        if sig and not refused:
            refused.append(pgid)
            raise PermissionError("injected kill failure")
        real_killpg(pgid, sig)

    try:
        monkeypatch.setattr(os, "killpg", refuse_the_first_kill)
        with pytest.raises(PermissionError):
            fleet.settle_all()
        [other] = [c.proc.pid for c in children if c.proc.pid not in refused]
        assert not _alive(other), "a later group was stranded by an earlier failure"
        assert _alive(refused[0])
        assert [kill["pgid"] for kill in fleet.settle_all()] == refused  # still owned
        assert not _alive(refused[0])
    finally:
        monkeypatch.undo()
        for child in children:
            if child.proc.poll() is None:
                os.killpg(child.proc.pid, signal.SIGKILL)
                child.proc.wait(timeout=5)


# --- G1: the source rehearsal (opt-in; never installed acceptance) -------------------------------

G1_PYTHON = os.environ.get("PREACTION_G1_PYTHON")
G1_PRODUCT = os.environ.get("PREACTION_G1_PRODUCT_ROOT")
G1_WORK = os.environ.get("PREACTION_G1_WORKDIR")


@pytest.mark.skipif(
    not (G1_PYTHON and G1_PRODUCT and G1_WORK),
    reason="G1 source rehearsal needs PREACTION_G1_PYTHON, _PRODUCT_ROOT and _WORKDIR",
)
def test_g1_the_public_api_carries_the_nested_pause_and_refusals_through_real_processes() -> None:
    assert G1_PYTHON and G1_PRODUCT and G1_WORK
    work = Path(G1_WORK) / f"g1-{os.getpid()}"
    src = [str(p) for p in sorted(Path(G1_PRODUCT).glob("harness-*/src"))]
    argv = [
        G1_PYTHON,
        str(TOOLS / "preaction_installed_witness.py"),
        "rehearse",
        "--python",
        G1_PYTHON,
    ]
    for path in src:
        argv += ["--product-src", path]
    argv += ["--work", str(work), "--output", str(Path(G1_WORK) / f"g1-{os.getpid()}.json")]

    done = subprocess.run(argv, capture_output=True, text=True, timeout=590, check=False)

    assert done.returncode == 0, (done.stdout, done.stderr)
    assert json.loads(done.stdout)["status"] == "REHEARSAL-PASS"


def test_the_current_lost_refusal_shapes_fail_and_the_terminal_refusal_passes() -> None:
    assert verdict(honest())["status"] == "PASS"

    paused = honest()
    paused["n1"]["results"]["resume-lowered"] = _ok("resume-lowered", current_bad_paused_shape())
    proceeds = {**claim_refused_again(), "outcome": "returned", "status": "completed"}
    proceeds |= {"before_ref": REF2, "ref": REF2, "chain": CHAIN[:2]}
    proceeds.pop("reason")
    proceeds.pop("error_type")
    paused["n1"]["results"]["resume-lowered-again"] = _ok("resume-lowered-again", proceeds)
    result = verdict(paused)

    assert result["status"] == "FAIL"
    for reason in (
        "n1:resume-lowered:paused-instead-of-refused",
        "n1:resume-lowered:new-pause-snapshot",
        "n1:resume-lowered:root-record-advanced",
        "n1:resume-lowered:child-refusal-reason-missing",
        "n1:resume-lowered-again:not-claim-refused",
        "n1:resume-lowered-again:different-record",
    ):
        assert reason in result["failure_reasons"], reason

    silent = honest()
    silent["n1"]["results"]["resume-lowered"] = _ok(
        "resume-lowered", {**current_bad_paused_shape(), "status": "completed"}
    )
    assert "n1:resume-lowered:completed-without-the-child" in verdict(silent)["failure_reasons"]


def test_absence_of_effects_alone_is_never_a_pass_for_n1() -> None:
    """No a/c/d effect, no audit and no new webhook are necessary, not sufficient."""
    evidence = honest()
    evidence["n1"]["results"]["resume-lowered"] = _ok("resume-lowered", current_bad_paused_shape())

    result = verdict(evidence)

    assert result["status"] == "FAIL"
    assert not any("inheritance-missing" in r or "webhook" in r for r in result["failure_reasons"])


REFUSED = f"{pw.ROOT_FAMILY}-child-resume-refused"


@pytest.mark.parametrize(
    ("text", "family", "reasons", "signing"),
    [
        (
            f"{REFUSED} (hitl-gate-config-changed)",
            "orchestrator-workers",
            {"hitl-gate-config-changed"},
            False,
        ),
        (
            f"{REFUSED} (claim-refused; hitl-gate-config-changed)",
            "orchestrator-workers",
            {"claim-refused", "hitl-gate-config-changed"},
            False,
        ),
        (
            f"{REFUSED} (snapshot-mismatch; unreadable-record; audit-signing-failed)",
            "orchestrator-workers",
            {"snapshot-mismatch", "unreadable-record"},
            True,
        ),
        (
            "parallelization-child-resume-refused (claim-busy)",
            "parallelization",
            {"claim-busy"},
            False,
        ),
    ],
)
def test_the_terminal_refusal_grammar_parses_into_typed_parts(
    text: str, family: str, reasons: set[str], signing: bool
) -> None:
    parsed = pw.parse_terminal_refusal(text)

    assert parsed == pw.TerminalRefusal(family, frozenset(reasons), signing)


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        7,
        "linear-resume-hitl-gate-config-changed at step 1",
        f"prefix {REFUSED} (claim-refused)",
        f"{REFUSED} (claim-refused) trailing",
        f"{REFUSED} ()",
        f"{REFUSED} (audit-signing-failed)",
        f"{REFUSED} (hitl-gate-config-changed; claim-refused)",
        f"{REFUSED} (claim-refused; claim-refused)",
        f"{REFUSED} (audit-signing-failed; claim-refused)",
        f"{REFUSED} (claim-refused;hitl-gate-config-changed)",
        f"{REFUSED}  (claim-refused)",
        f"{REFUSED} (Claim-Refused)",
        f"{REFUSED} (claim-refused (nested))",
    ],
)
def test_anything_outside_the_terminal_refusal_grammar_parses_to_nothing(text: object) -> None:
    assert pw.parse_terminal_refusal(text) is None


def test_the_signing_flag_is_retained_not_dropped() -> None:
    parsed = pw.parse_terminal_refusal(
        f"{REFUSED} (hitl-gate-config-changed; audit-signing-failed)"
    )

    assert parsed is not None and parsed.audit_signing_failed is True


# --- an outside SIGTERM must run the helper's own cleanup: services and the in-flight phase ---

_TERM_DRIVER = r"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import preaction_installed_witness as pw

mode, root = sys.argv[2], Path(sys.argv[3])
STUB_SERVER = '''
import os, socket, sys
port = int(sys.argv[2])
listener = socket.socket()
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(("127.0.0.1", port))
listener.listen()
open(sys.argv[1] + ".pgid", "w").write(str(os.getpgid(0)))
while True:
    listener.accept()[0].close()
'''
PHASE_CHILD = '''
import os, sys, time
open(sys.argv[1], "w").write(str(os.getpgid(0)))
time.sleep(600)
'''
pw.MCP_SERVER_SOURCE = STUB_SERVER
marker = root / "phase.pgid"
root.mkdir(parents=True)


def argv(python, helper, name, phase, fixed):
    return [sys.executable, "-c", PHASE_CHILD, str(marker)]


pw.child_argv_source = argv
pw.child_argv_installed = argv
if mode == "rehearse":
    work = root / "work"
    work.mkdir()
    pw.rehearse(Path(sys.executable), [Path("unused")], work / "scenarios", work)
else:
    pw.PROVER.checked_candidate = lambda c, v, h: (root, root, Path(sys.executable))
    pw.PROVER.checked_provenance = lambda r, c, i, h: {"wheels": []}
    pw.HELPERS.checked_scenario_root = lambda r, m: {}
    receipt = root / "receipt.json"
    receipt.write_text("{}")
    pw.run(root, root, "0" * 40, receipt, root / "scenario", root / "report.json")
"""


def _wait_for(path: Path, seconds: float = 20.0) -> int:
    """Wait for a child-written pgid marker: an event the child emits, not a guess at timing."""
    import time

    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if path.exists() and path.read_text().strip():
            return int(path.read_text())
        time.sleep(0.05)
    raise AssertionError(f"{path} never appeared")


def _alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.mark.parametrize("mode", ["rehearse", "run"])
def test_sigterm_mid_scenario_leaves_no_owned_process_group_alive(
    mode: str, tmp_path: Path
) -> None:
    root = tmp_path / "attempt"
    bystander = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(600)"], start_new_session=True
    )
    driver = subprocess.Popen(
        [sys.executable, "-c", _TERM_DRIVER, str(TOOLS), mode, str(root)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    owned: list[int] = []
    try:
        phase_pgid = _wait_for(root / "phase.pgid")
        owned.append(phase_pgid)
        tool_markers = sorted(root.rglob("*.pgid"))
        tool_pgids = [int(m.read_text()) for m in tool_markers if m.name != "phase.pgid"]
        owned += tool_pgids
        assert tool_pgids, "the stub tool server never announced its group"
        assert all(_alive(p) for p in owned)

        driver.send_signal(signal.SIGTERM)
        driver.wait(timeout=30)

        survivors = [p for p in owned if _alive(p)]
        assert survivors == [], f"owned groups outlived the helper: {survivors}"
        assert bystander.poll() is None and _alive(bystander.pid), "an unrelated process was killed"
    finally:
        for pgid in owned:
            if _alive(pgid):
                os.killpg(pgid, signal.SIGKILL)
        if driver.poll() is None:
            driver.kill()
        driver.wait()
        bystander.kill()
        bystander.wait()


# --- lifecycle boundaries: acquisition, registration, settlement and cleanup under TERM/faults ---
#
# Each case runs the real `rehearse` in its own driver process with stub services. The fault or the
# process-directed TERM is injected at an OS-facing seam (`HELPERS.spawn`, `HELPERS.finish`,
# `os.killpg`, a removed log file), fired by the parent's own observable action, never by a sleep.
# The driver records every group the helper started and what it saw at the injection point, then
# exits without waiting for threads, so a leaked listener is reported instead of hanging the test.

_LIFECYCLE_DRIVER = r"""
import json, os, signal, socket, sys, threading, time, traceback
from pathlib import Path

sys.path.insert(0, sys.argv[1])
import preaction_installed_witness as pw

case, root = sys.argv[2], Path(sys.argv[3])
work = root / "work"
work.mkdir(parents=True)
facts = {"owned_pgids": [], "webhook_ports": [], "boundary": {}}
original_handler = signal.getsignal(signal.SIGTERM)

pw.MCP_SERVER_SOURCE = '''
import socket, sys
listener = socket.socket()
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(("127.0.0.1", int(sys.argv[2])))
listener.listen()
while True:
    listener.accept()[0].close()
'''
RUNNING_LEADER = "import time; time.sleep(600)"
EXITING_LEADER = '''
import subprocess, sys
descendant = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
open(sys.argv[1], "w").write(str(descendant.pid))
'''
leader = EXITING_LEADER if case in {
    "term-after-leader-exit",
    "term-during-settle",
    "kill-fails-during-settle",
    "term-at-settle-gone-proof",
} else RUNNING_LEADER
descendant_marker = root / "descendant.pid"
pw.child_argv_source = lambda *_: [sys.executable, "-c", leader, str(descendant_marker)]


def term_blocked_in_every_thread():
    blocked = []
    for status in sorted(Path("/proc/self/task").glob("*/status")):
        line = next(x for x in status.read_text().splitlines() if x.startswith("SigBlk:"))
        blocked.append(bool(int(line.split()[1], 16) >> (signal.SIGTERM - 1) & 1))
    return blocked


def deliver_term():
    # A process-directed TERM, then wait for its observable fate: held pending (every thread blocks
    # it) or handled (the handler raises here). Neither within the bound is itself a failure.
    os.kill(os.getpid(), signal.SIGTERM)
    limit = time.monotonic() + 10
    while signal.SIGTERM not in signal.sigpending():
        if time.monotonic() > limit:
            raise AssertionError("TERM was neither held pending nor handled")
        time.sleep(0.001)


def descendant_alive():
    try:
        os.kill(int(descendant_marker.read_text()), 0)
    except (OSError, ValueError):
        return False
    return True


real_config, real_spawn, real_finish = pw.config_text, pw.HELPERS.spawn, pw.HELPERS.finish
real_killpg = os.killpg
waited = set()


def config_text(layout, webhook_port, mcp_port):
    facts["webhook_ports"].append(webhook_port)
    return real_config(layout, webhook_port, mcp_port)


def spawn(argv, env, cwd, logs, phase):
    child = real_spawn(argv, env, cwd, logs, phase)
    facts["owned_pgids"].append(child.proc.pid)
    wanted = {"term-at-tool-server-spawn": "tool-server", "term-at-phase-spawn": "p-run"}
    if wanted.get(case) == phase:
        facts["boundary"] = {"fired": True, "term_blocked": term_blocked_in_every_thread()}
        deliver_term()
    return child


def finish(child, deadline):
    if case == "term-during-cleanup":
        facts["boundary"] = {"leader_running": child.proc.poll() is None}
        raise RuntimeError("injected body failure")
    if case == "cleanup-stream-fails":
        (work / "p" / "tool-server.stdout").unlink()
        facts["boundary"] = {"fired": True, "leader_running": child.proc.poll() is None}
        deliver_term()
    record = real_finish(child, deadline)
    waited.add(child.proc.pid)
    if case == "term-after-leader-exit":
        facts["boundary"] = {
            "fired": True,
            "leader_exited": child.proc.poll() is not None,
            "descendant_alive": descendant_alive(),
        }
        deliver_term()
    return record


def killpg(pgid, sig):
    if case == "term-at-settle-gone-proof" and pgid in waited:
        if facts["boundary"]:
            facts["boundary"]["signals_after_gone"].append(sig)
            return real_killpg(pgid, sig)
        try:
            return real_killpg(pgid, sig)
        except ProcessLookupError:
            if sig == 0:  # the settle has just proved the group gone
                facts["boundary"] = {"fired": True, "signals_after_gone": []}
                deliver_term()
            raise
    if case == "term-during-cleanup" and sig and "fired" not in facts["boundary"]:
        facts["boundary"].update(fired=True, signal=sig)
        deliver_term()
    first = pgid in waited and not facts["boundary"]
    if first and (case == "term-during-settle" or (case == "kill-fails-during-settle" and sig)):
        facts["boundary"] = {"fired": True, "signal": sig, "descendant_alive": descendant_alive()}
        if case == "kill-fails-during-settle":
            raise PermissionError("injected kill failure during settle")
        deliver_term()
    return real_killpg(pgid, sig)


pw.config_text, pw.HELPERS.spawn, pw.HELPERS.finish, os.killpg = config_text, spawn, finish, killpg
python = root / "no-such-python" if case == "tool-server-spawn-fails" else Path(sys.executable)
chain = []
try:
    pw.rehearse(python, [Path("unused")], work / "scenarios", work)
except BaseException as exc:
    traceback.print_exc()
    while exc is not None:
        chain.append(type(exc).__name__)
        exc = exc.__context__


def accepting(port):
    try:
        socket.create_connection(("127.0.0.1", port), timeout=1).close()
    except OSError:
        return False
    return True


facts.update(
    chain=chain,
    open_webhook_ports=[p for p in facts["webhook_ports"] if accepting(p)],
    other_threads=[t.name for t in threading.enumerate() if t is not threading.main_thread()],
    handler_restored=signal.getsignal(signal.SIGTERM) == original_handler,
    term_still_blocked=signal.SIGTERM in signal.pthread_sigmask(signal.SIG_BLOCK, []),
)
(root / "facts.json").write_text(json.dumps(facts))
os._exit(0)
"""

# case -> (exception chain the attempt must end with, boundary facts that prove it was reached)
LIFECYCLE_CASES: dict[str, tuple[list[str], dict[str, object]]] = {
    "term-at-tool-server-spawn": (["InterruptedError"], {"fired": True}),
    "term-at-phase-spawn": (["InterruptedError"], {"fired": True}),
    "tool-server-spawn-fails": (["FileNotFoundError"], {}),
    "term-after-leader-exit": (
        ["InterruptedError"],
        {"fired": True, "leader_exited": True, "descendant_alive": True},
    ),
    "term-during-settle": (["InterruptedError"], {"fired": True, "descendant_alive": True}),
    "kill-fails-during-settle": (
        ["PermissionError"],
        {"fired": True, "signal": signal.SIGKILL, "descendant_alive": True},
    ),
    "cleanup-stream-fails": (
        ["FileNotFoundError", "InterruptedError"],
        {"fired": True, "leader_running": True},
    ),
    "term-during-cleanup": (
        ["InterruptedError", "RuntimeError"],
        {"fired": True, "signal": signal.SIGKILL, "leader_running": True},
    ),
    "term-at-settle-gone-proof": (["InterruptedError"], {"fired": True, "signals_after_gone": []}),
}


@pytest.mark.parametrize("case", list(LIFECYCLE_CASES))
def test_every_owned_resource_is_released_whatever_interrupts_its_lifecycle(
    case: str, tmp_path: Path
) -> None:
    chain, boundary = LIFECYCLE_CASES[case]
    root = tmp_path / "attempt"
    bystander = subprocess.Popen(["sleep", "600"], start_new_session=True)
    driver = subprocess.Popen(
        [sys.executable, "-c", _LIFECYCLE_DRIVER, str(TOOLS), case, str(root)],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    facts: dict[str, Any] = {}
    try:
        _, stderr = driver.communicate(timeout=90)
        facts = json.loads((root / "facts.json").read_text())
        assert facts["chain"] == chain, stderr.decode()
        assert {k: facts["boundary"].get(k) for k in boundary} == boundary, facts["boundary"]
        assert all(facts["boundary"].get("term_blocked", [True])), "a thread could take the TERM"
        assert facts["webhook_ports"], "the webhook was never acquired"
        survivors = [p for p in facts["owned_pgids"] if _alive(p)]
        assert survivors == [], f"owned groups outlived the helper: {survivors}"
        assert facts["open_webhook_ports"] == [], "the owned webhook listener still accepts"
        assert facts["other_threads"] == [], (
            f"threads outlived the helper: {facts['other_threads']}"
        )
        assert facts["handler_restored"] and not facts["term_still_blocked"]
        assert bystander.poll() is None and _alive(bystander.pid), "an unrelated process was killed"
    finally:
        for pgid in facts.get("owned_pgids", []):
            if _alive(pgid):
                os.killpg(pgid, signal.SIGKILL)
        if driver.poll() is None:
            os.killpg(driver.pid, signal.SIGKILL)
        driver.wait()
        bystander.kill()
        bystander.wait()


STUB_TOOL_SERVER = """
import socket, sys
listener = socket.socket()
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(("127.0.0.1", int(sys.argv[2])))
listener.listen()
while True:
    listener.accept()[0].close()
"""


def test_the_installed_report_pins_every_owner_the_verdict_relies_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The verdict grammar, ownership and config come from the B-104 helper: its hash is pinned."""
    monkeypatch.setattr(pw, "MCP_SERVER_SOURCE", STUB_TOOL_SERVER)

    def exits_at_once(*_args: object) -> list[str]:
        return [sys.executable, "-c", "raise SystemExit(0)"]

    def candidate(*_args: object) -> tuple[Path, Path, Path]:
        return tmp_path, tmp_path, Path(sys.executable)

    def no_wheels(*_args: object) -> dict[str, list[str]]:
        return {"wheels": []}

    def no_placement(*_args: object) -> dict[str, str]:
        return {}

    monkeypatch.setattr(pw, "child_argv_installed", exits_at_once)
    monkeypatch.setattr(pw.PROVER, "checked_candidate", candidate)
    monkeypatch.setattr(pw.PROVER, "checked_provenance", no_wheels)
    monkeypatch.setattr(pw.HELPERS, "checked_scenario_root", no_placement)
    receipt = tmp_path / "receipt.json"
    receipt.write_text("{}")

    report = pw.run(
        tmp_path, tmp_path, "0" * 40, receipt, tmp_path / "scenario", tmp_path / "report.json"
    )

    def digest(name: str) -> str:
        return hashlib.sha256((TOOLS / name).read_bytes()).hexdigest()

    assert report["helper_sha256"] == digest("preaction_installed_witness.py")
    assert report["shared_prover_sha256"] == digest("installed_witness_provenance.py")
    assert report["b104_helpers_sha256"] == digest("b104_installed_public_witness.py")
    assert json.loads((tmp_path / "report.json").read_text())["b104_helpers_sha256"] == digest(
        "b104_installed_public_witness.py"
    )


def test_a_phase_run_record_is_parsed_into_typed_facts_or_refused() -> None:
    good: dict[str, object] = {"pgid": 4242, "timeout": False, "exit": 0}

    assert pw.parse_phase_run(good) == pw.PhaseRun(pgid=4242, timed_out=False, exit_code=0)
    bad_records: list[dict[str, object]] = [
        {**good, "pgid": True},
        {**good, "pgid": "4242"},
        {**good, "pgid": None},
        {**good, "timeout": 0},
        {**good, "timeout": None},
        {**good, "exit": None},
        {**good, "exit": False},
        {"timeout": False, "exit": 0},
    ]
    for bad in bad_records:
        with pytest.raises(ValueError, match="malformed phase run record"):
            pw.parse_phase_run(bad)


def test_a_malformed_child_record_stops_the_loop_before_any_group_is_signalled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Settling signals a process group; a bool or string id must never reach `killpg`."""
    signalled: list[int] = []

    def record_signal(pgid: int, _sig: int) -> None:
        signalled.append(pgid)

    def finished_with_a_bool_group(*_args: object) -> dict[str, object]:
        return {"pgid": True, "timeout": False, "exit": 0}

    def launch_nothing(_phase: str) -> SimpleNamespace:
        """A started phase process that has already exited."""
        return SimpleNamespace(proc=SimpleNamespace(poll=lambda: 0, pid=4242))

    monkeypatch.setattr(os, "killpg", record_signal)
    monkeypatch.setattr(pw.HELPERS, "finish", finished_with_a_bool_group)
    capture = pw.WebhookCapture()

    try:
        with pytest.raises(ValueError, match="malformed phase run record"):
            pw.run_scenario("p", pw.Layout(tmp_path), launch_nothing, pw.Fleet(), capture, 0.0)
    finally:
        capture.server.server_close()

    assert signalled == []


def test_verified_paths_come_only_from_a_record_the_prover_parses() -> None:
    paths = pw.verified_paths(provenance())

    assert paths == {f for entry in origins().values() for f in entry["verified_files"]}
    files_not_a_list = provenance()
    files_not_a_list["installed_origins"]["harness_cp"]["verified_files"] = "x.py"
    no_interpreter = provenance()
    del no_interpreter["interpreter"]
    no_receipt = provenance()
    del no_receipt["installation_receipt_sha256"]
    broken_records: list[dict[str, Any]] = [
        {},
        {**provenance(), "installed_origins": {}},
        {**provenance(), "installed_origins": "not-a-mapping"},
        {**provenance(), "installed_origins": {**origins(), "harness_cp": 7}},
        files_not_a_list,
        no_interpreter,
        no_receipt,
    ]
    for broken in broken_records:
        with pytest.raises(ValueError, match="not parseable provenance"):
            pw.verified_paths(broken)
