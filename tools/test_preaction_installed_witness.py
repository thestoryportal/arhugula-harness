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
    result = {}
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
            "validator_fail_class": "linear-resume-hitl-gate-config-changed at step 1",
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
    return pw.evaluate(evidence, expected_receipt_sha256=receipt)  # type: ignore[return-value]


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
        "n1-refusal-reason-unrelated",
        set_(f"{LOW}/failure_cause/validator_fail_class", "some other failure"),
        "n1:resume-lowered:child-refusal-reason-missing",
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
        "n1:resume-lowered:child-refusal-reason-missing",
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


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(candidate_head="4" * 40),
        lambda r: r.update(venv="/other/venv"),
        lambda r: r["startup_hooks"]["files"].__setitem__("_virtualenv.py", "5" * 64),
        lambda r: r["wheels"][0].update(sha256="6" * 64),
        lambda r: r["installed_record_sha256"].pop("harness_cp"),
    ],
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


def test_settle_group_kills_only_a_surviving_own_group(tmp_path: Path) -> None:
    child = subprocess.Popen(
        ["sleep", "30"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert pw.settle_group(child.pid) is True  # alive: reported and killed
        child.wait(timeout=5)
        assert pw.settle_group(child.pid) is False  # gone: nothing left to report
    finally:
        if child.poll() is None:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=5)


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
