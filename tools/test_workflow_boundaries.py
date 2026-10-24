"""WO-U05 / WP-04 — distinct boundary admission and completion decisions (spec WS-06,
WS-18; verification WT-10, WT-16 boundary portion).

The four boundaries report readiness apart from observed completion: publish/integrate
need an explicit point and prepare/develop reject one; a `before` admission can never
satisfy an `after` obligation; the `workflow check` CLI emits the exact WS-06 JSON fields
and exits 0/2/3/4/5 for passing, invalid, held, failed and infrastructure-uncertain
outcomes, with a receipt only on a pass; `workflow status` only reads; and the existing
guard modes keep their contract.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType

import pytest

# The guard imports its sibling `codex_loop` the way it does when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as cg

from tools import workflow_boundaries as wb
from tools.workflow_boundaries import (
    BoundaryError,
    BoundaryFacts,
    Reference,
    Shortfall,
    Subject,
    Verified,
    evaluate_boundary,
    parse_request,
    requirements,
)
from tools.workflow_evidence import Checker, InputManifest, check_receipt
from tools.workflow_policy import ActivationAbsent, ProfileSelection, WorkflowPolicy, load_policy

UNIT = "arhugula-harness-trial-193.7x7.fra"
REPO = "thestoryportal/arhugula-harness"
HEAD = "a" * 40
BASE = "b" * 40
TRIAL = ProfileSelection("trial", (), ())
WIRE_FIELDS = [
    "schema_version",
    "policy_id",
    "policy_version",
    "unit_id",
    "boundary",
    "point",
    "result",
    "reason_codes",
    "receipt",
    "next_action",
]
REF = Reference("/evidence/record.json", "c" * 64, 10)
SUBJECT = Subject(REPO, HEAD, BASE)
VALID_PAIRS = [
    ("prepare", None),
    ("develop", None),
    ("publish", "before"),
    ("publish", "after"),
    ("integrate", "before"),
    ("integrate", "after"),
]
INVALID_PAIRS = [
    ("prepare", "before"),
    ("prepare", "after"),
    ("develop", "before"),
    ("develop", "after"),
    ("publish", None),
    ("integrate", None),
    ("publish", "during"),
    ("integrate", "now"),
    ("merge", None),
    ("merge", "after"),
]
# Illustrative producer contracts a test policy registers; the tracked policy has none.
CONTRACTS = {
    "staged_scope": {
        "checker": "staged-diff",
        "argv": ["git", "diff", "--cached"],
        "scope": "index",
    },
    "lint_format": {"checker": "ruff", "argv": ["ruff", "check"], "scope": "index"},
    "behavior_proof": {"checker": "pytest", "argv": ["pytest", "-q"], "scope": "index"},
    "unrelated_work": {"checker": "preserved", "argv": ["git", "status"], "scope": "working_tree"},
    "revision": {"checker": "frozen-head", "argv": ["git", "rev-parse"], "scope": "git_tree"},
    "local_only": {"checker": "local-gaps", "argv": ["just", "local"], "scope": "git_tree"},
}


def policy_bytes(boundary_rules: dict) -> bytes:
    doc = json.loads(wb.POLICY_PATH.read_bytes())
    doc["boundary_rules"] = boundary_rules
    return json.dumps(doc).encode()


def policy_digest(raw: bytes) -> str:
    policy = load_policy(raw)
    assert isinstance(policy, WorkflowPolicy), policy
    return policy.digest


TEST_POLICY = policy_bytes({"checks": CONTRACTS})
TEST_DIGEST = policy_digest(TEST_POLICY)


def facts(request, selection=TRIAL, **overrides) -> BoundaryFacts:
    """Every requirement of `request` verified, then `overrides` by requirement name."""
    observed = {req.name: Verified(REF) for req in requirements(request.step)}
    observed.update(overrides)
    return BoundaryFacts(selection, SUBJECT, MappingProxyType(observed))


# --- requests and the point rules -------------------------------------------------------


@pytest.mark.parametrize(("boundary", "point"), VALID_PAIRS)
def test_every_valid_pair_round_trips(boundary, point):
    request = parse_request(UNIT, boundary, point)
    assert (request.unit, request.boundary, request.point) == (UNIT, boundary, point)


@pytest.mark.parametrize(("boundary", "point"), INVALID_PAIRS)
def test_every_invalid_point_boundary_combination_rejects(boundary, point):
    with pytest.raises(BoundaryError) as raised:
        parse_request(UNIT, boundary, point)
    assert raised.value.field == ("boundary" if boundary == "merge" else "point")


@pytest.mark.parametrize("unit", ["", "Has Space", "unit\n"])
def test_malformed_unit_rejects(unit):
    with pytest.raises(BoundaryError) as raised:
        parse_request(unit, "develop", None)
    assert raised.value.field == "unit"


# --- the pure evaluator -----------------------------------------------------------------


@pytest.mark.parametrize("boundary", ["publish", "integrate"])
def test_before_receipt_cannot_complete_publication_or_merge(boundary):
    before = parse_request(UNIT, boundary, "before")
    after = parse_request(UNIT, boundary, "after")
    admitted = facts(before)

    admission = evaluate_boundary(before, admitted)
    assert (admission.result, admission.record_type) == ("passed", "boundary_admission")

    # Everything the admission saw is still verified, but no action readback exists.
    completion = evaluate_boundary(after, admitted)
    assert completion.result == "held"
    assert completion.record_type is None
    assert completion.reasons == ("check_pending",)

    finished = evaluate_boundary(after, facts(after))
    assert (finished.result, finished.record_type) == ("passed", "boundary_completion")


def test_completion_needs_the_remote_and_own_main_observations_admission_lacks():
    names = {
        (boundary, point): {
            req.name for req in requirements(parse_request(UNIT, boundary, point).step)
        }
        for boundary, point in VALID_PAIRS
    }
    assert names[("publish", "after")] - names[("publish", "before")] == {
        "remote_head",
        "pull_request",
    }
    assert names[("integrate", "after")] - names[("integrate", "before")] == {
        "landing",
        "own_main",
    }
    assert names[("publish", "before")] <= names[("publish", "after")]
    assert names[("integrate", "before")] <= names[("integrate", "after")]


@pytest.mark.parametrize(("boundary", "point"), [("prepare", None), ("develop", None)])
def test_readiness_admits_and_never_completes(boundary, point):
    request = parse_request(UNIT, boundary, point)
    decision = evaluate_boundary(request, facts(request))
    assert (decision.result, decision.record_type) == ("passed", "boundary_admission")


@pytest.mark.parametrize(("boundary", "point"), VALID_PAIRS)
def test_every_missing_requirement_holds_without_a_record(boundary, point):
    request = parse_request(UNIT, boundary, point)
    for req in requirements(request.step):
        observed = {r.name: Verified(REF) for r in requirements(request.step) if r != req}
        decision = evaluate_boundary(request, BoundaryFacts(TRIAL, SUBJECT, observed))
        assert (decision.result, decision.record_type) == ("held", None), req.name
        assert decision.reasons, req.name


def test_held_reasons_name_the_missing_producer():
    request = parse_request(UNIT, "integrate", "before")
    observed = {"authority": Verified(REF), "head_base": Verified(REF), "pr_checks": Verified(REF)}
    decision = evaluate_boundary(request, BoundaryFacts(TRIAL, SUBJECT, observed))
    assert decision.reasons == ("review_blocked", "ownership_conflict")


def test_severity_error_over_failed_over_held_with_every_reason_kept():
    request = parse_request(UNIT, "develop", None)
    held = Shortfall("held", "check_pending")
    failed = Shortfall("failed", "check_failed")
    error = Shortfall("error", "artifact_unavailable")

    assert evaluate_boundary(request, facts(request, staged_scope=held)).result == "held"
    both = evaluate_boundary(request, facts(request, staged_scope=held, lint_format=failed))
    assert (both.result, both.reasons) == ("failed", ("check_pending", "check_failed"))
    worst = evaluate_boundary(
        request, facts(request, staged_scope=held, lint_format=failed, behavior_proof=error)
    )
    assert worst.result == "error"
    assert worst.reasons == ("check_pending", "check_failed", "artifact_unavailable")
    assert worst.record_type is None


@pytest.mark.parametrize(
    ("selection", "reasons"),
    [
        (ProfileSelection("legacy", (), ()), ("policy_mismatch",)),
        (
            ProfileSelection("held", ("authority_unavailable",), ("admission",)),
            ("authority_unavailable",),
        ),
    ],
)
def test_only_the_trial_profile_can_pass_a_boundary(selection, reasons):
    request = parse_request(UNIT, "develop", None)
    decision = evaluate_boundary(request, facts(request, selection=selection))
    assert (decision.result, decision.reasons, decision.record_type) == ("held", reasons, None)


# --- CLI fixtures -----------------------------------------------------------------------


@pytest.fixture
def store(tmp_path, monkeypatch):
    root = tmp_path / "receipts"
    monkeypatch.setattr(wb, "RECEIPT_ROOT", root)
    return root


def use_policy(monkeypatch, tmp_path: Path, raw: bytes) -> None:
    path = tmp_path / "workflow-policy.json"
    path.write_bytes(raw)
    monkeypatch.setattr(wb, "POLICY_PATH", path)


@pytest.fixture
def trial(tmp_path, monkeypatch):
    # The LIT/native selection adapters do not exist yet; only that seam is replaced. The
    # producer contracts come from a real policy file through the real parser.
    monkeypatch.setattr(wb, "observe_selection", lambda *_: TRIAL)
    use_policy(monkeypatch, tmp_path, TEST_POLICY)


def write_check(
    tmp_path: Path,
    name: str,
    result: str = "passed",
    head: str = HEAD,
    *,
    producer: str | None = None,
    digest: str = TEST_DIGEST,
) -> dict:
    """A WS-08 check receipt from the checker contracted for `producer` (default `name`)."""
    contract = CONTRACTS.get(producer or name, CONTRACTS["behavior_proof"])
    manifest = InputManifest(
        unit=UNIT,
        repository=REPO,
        scope=contract["scope"],
        head=head,
        material_base=None,
        checker=Checker(contract["checker"], "1", tuple(contract["argv"])),
        policy_id="arhugula-trial-v1",
        policy_version=1,
        policy_digest=digest,
        domains=("tools",),
        explicit=(),
        environment={},
        files=(),
        refusals=(),
    )
    record = check_receipt(
        manifest,
        record_id=f"check-{name}",
        producer={"tool": contract["checker"]},
        created_at="2026-10-24T00:00:00Z",
        result=result,
        artifacts=[],
    )
    raw = json.dumps(record).encode()
    path = tmp_path / f"{name}.json"
    path.write_bytes(raw)
    return {"uri": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def write_manifest(tmp_path: Path, boundary: str, point: str | None, observations: dict) -> Path:
    path = tmp_path / f"manifest-{boundary}-{point}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "unit_id": UNIT,
                "boundary": boundary,
                "point": point,
                "subject": {"repository": REPO, "head": HEAD, "base": BASE},
                "observations": observations,
            }
        )
    )
    return path


def develop_manifest(tmp_path: Path, **results: str) -> Path:
    names = ("staged_scope", "lint_format", "behavior_proof", "unrelated_work")
    return write_manifest(
        tmp_path,
        "develop",
        None,
        {
            name: {
                "source": "check",
                "record": write_check(tmp_path, name, results.get(name, "passed")),
            }
            for name in names
        },
    )


def run(capsys, *argv: str) -> tuple[int, dict]:
    code = cg.main(["workflow", *argv])
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert len(lines) == 1, out
    return code, json.loads(lines[0])


def check(capsys, manifest: Path, boundary: str, point: str | None = None) -> tuple[int, dict]:
    argv = ["check", "--unit", UNIT, "--boundary", boundary, "--manifest", str(manifest)]
    return run(capsys, *argv, *([] if point is None else ["--point", point]))


# --- CLI: wire contract and exits -------------------------------------------------------


def test_passing_check_emits_exact_wire_fields_and_a_verified_receipt(
    tmp_path, capsys, store, trial
):
    code, out = check(capsys, develop_manifest(tmp_path), "develop")

    assert code == 0
    assert list(out) == WIRE_FIELDS
    assert out["result"] == "passed" and out["reason_codes"] == []
    assert (out["unit_id"], out["boundary"], out["point"]) == (UNIT, "develop", None)
    assert (out["schema_version"], out["policy_id"], out["policy_version"]) == (
        1,
        "arhugula-trial-v1",
        1,
    )
    assert out["next_action"].strip()
    assert set(out["receipt"]) == {"uri", "sha256"}
    raw = Path(out["receipt"]["uri"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == out["receipt"]["sha256"]
    record = json.loads(raw)
    assert record["record_type"] == "boundary_admission"
    assert record["inputs"]["boundary"] == "develop" and record["inputs"]["point"] is None
    assert record["subject"] == {"repository": REPO, "head": HEAD, "base": BASE}
    assert set(record["inputs"]["observations"]) == {
        "staged_scope",
        "lint_format",
        "behavior_proof",
        "unrelated_work",
    }


def test_publish_before_names_its_point_and_holds_on_unadapted_review(
    tmp_path, capsys, store, trial
):
    record = write_check(tmp_path, "revision")
    request = write_check(tmp_path, "request-original")
    manifest = write_manifest(
        tmp_path,
        "publish",
        "before",
        {
            "revision": {"source": "check", "record": record},
            "local_only": {"source": "check", "record": write_check(tmp_path, "local_only")},
            "review_inputs": {"source": "review", "record": request},
            "review_request": {"source": "review", "record": request},
        },
    )
    code, out = check(capsys, manifest, "publish", "before")
    assert (code, out["point"], out["result"]) == (3, "before", "held")
    assert out["reason_codes"] == ["review_blocked"]
    assert out["receipt"] is None and not store.exists()


@pytest.mark.parametrize(("boundary", "point"), INVALID_PAIRS)
def test_cli_rejects_every_invalid_combination_with_exit_2(
    tmp_path, capsys, store, trial, boundary, point
):
    manifest = write_manifest(tmp_path, "develop", None, {})
    code, out = check(capsys, manifest, boundary, point)
    assert code == 2
    assert list(out) == WIRE_FIELDS
    assert (out["result"], out["reason_codes"], out["receipt"]) == (
        "error",
        ["invalid_input"],
        None,
    )
    assert (out["boundary"], out["point"]) == (None, None)
    assert not store.exists()


@pytest.mark.parametrize(
    "argv",
    [
        ["check", "--unit", UNIT, "--boundary", "develop"],
        ["check", "--boundary", "develop", "--manifest", "/nonexistent"],
        ["status"],
        ["promote", "--unit", UNIT],
        [],
    ],
)
def test_malformed_invocation_is_exit_2_json(capsys, store, argv):
    code, out = run(capsys, *argv)
    assert (code, out["result"], out["reason_codes"]) == (2, "error", ["invalid_input"])


@pytest.mark.parametrize(
    ("mutate", "field"),
    [
        (lambda doc: doc.update(point="before"), "point"),
        (lambda doc: doc.update(unit_id="arhugula-other.unit"), "unit"),
        (lambda doc: doc.update(schema_version=2), "schema"),
        (lambda doc: doc.update(extra=True), "extra key"),
        (
            lambda doc: doc["observations"].update(remote_head=doc["observations"]["lint_format"]),
            "requirement",
        ),
        (lambda doc: doc["observations"]["lint_format"].update(source="review"), "source"),
        (
            lambda doc: doc["observations"]["lint_format"]["record"].update(uri="relative.json"),
            "uri",
        ),
        (lambda doc: doc["subject"].update(head="abc"), "head"),
    ],
)
def test_manifest_that_does_not_describe_this_check_rejects(
    tmp_path, capsys, store, trial, mutate, field
):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    mutate(doc)
    path.write_text(json.dumps(doc))
    code, out = check(capsys, path, "develop")
    assert (code, out["reason_codes"], out["receipt"]) == (2, ["invalid_input"], None), field
    assert not store.exists()


def test_held_check_receipt_is_exit_3(tmp_path, capsys, store, trial):
    code, out = check(capsys, develop_manifest(tmp_path, lint_format="held"), "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        3,
        "held",
        ["check_pending"],
        None,
    )


def test_missing_observation_is_exit_3(tmp_path, capsys, store, trial):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    del doc["observations"]["behavior_proof"]
    path.write_text(json.dumps(doc))
    code, out = check(capsys, path, "develop")
    assert (code, out["result"], out["reason_codes"]) == (3, "held", ["check_pending"])
    assert not store.exists()


def test_check_receipt_for_another_head_is_stale(tmp_path, capsys, store, trial):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    doc["observations"]["staged_scope"]["record"] = write_check(
        tmp_path, "old", head="e" * 40, producer="staged_scope"
    )
    path.write_text(json.dumps(doc))
    code, out = check(capsys, path, "develop")
    assert (code, out["result"], out["reason_codes"]) == (3, "held", ["binding_stale"])


def test_failed_check_receipt_is_exit_4(tmp_path, capsys, store, trial):
    code, out = check(capsys, develop_manifest(tmp_path, behavior_proof="failed"), "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        4,
        "failed",
        ["check_failed"],
        None,
    )
    assert not store.exists()


def test_record_that_no_longer_matches_its_hash_is_exit_5(tmp_path, capsys, store, trial):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    Path(doc["observations"]["lint_format"]["record"]["uri"]).write_bytes(b"{}")
    code, out = check(capsys, path, "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        5,
        "error",
        ["artifact_unavailable"],
        None,
    )


def test_unreadable_record_is_exit_5(tmp_path, capsys, store, trial):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    Path(doc["observations"]["lint_format"]["record"]["uri"]).unlink()
    code, out = check(capsys, path, "develop")
    assert (code, out["reason_codes"]) == (5, ["artifact_unavailable"])


def test_receipt_publication_failure_is_exit_5_without_a_receipt(
    tmp_path, capsys, monkeypatch, trial
):
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("")
    monkeypatch.setattr(wb, "RECEIPT_ROOT", blocker / "receipts")
    code, out = check(capsys, develop_manifest(tmp_path), "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        5,
        "error",
        ["publication_uncertain"],
        None,
    )


@pytest.mark.parametrize("boundary", ["publish", "integrate"])
def test_cli_admission_receipt_offered_as_completion_evidence_rejects(
    tmp_path, capsys, store, trial, boundary
):
    # A real passing admission receipt, then that receipt offered for the action readback.
    develop_code, develop = check(capsys, develop_manifest(tmp_path), "develop")
    assert develop_code == 0
    raw = Path(develop["receipt"]["uri"]).read_bytes()
    admission = {
        "uri": develop["receipt"]["uri"],
        "sha256": develop["receipt"]["sha256"],
        "bytes": len(raw),
    }
    readback = "remote_head" if boundary == "publish" else "landing"

    as_admission = write_manifest(
        tmp_path,
        boundary,
        "after",
        {readback: {"source": "boundary_admission", "record": admission}},
    )
    code, out = check(capsys, as_admission, boundary, "after")
    assert (code, out["reason_codes"], out["receipt"]) == (2, ["invalid_input"], None)

    as_remote = write_manifest(
        tmp_path, boundary, "after", {readback: {"source": "remote", "record": admission}}
    )
    code, out = check(capsys, as_remote, boundary, "after")
    assert (code, out["result"], out["receipt"]) == (3, "held", None)
    assert [p.name for p in store.iterdir()] == [Path(develop["receipt"]["uri"]).name]


def test_inactive_policy_keeps_every_unit_out_of_the_trial_lifecycle(
    tmp_path, capsys, store, monkeypatch
):
    monkeypatch.setattr(wb, "read_activation", ActivationAbsent)
    code, out = check(capsys, develop_manifest(tmp_path), "develop")
    # The tracked policy also registers no check producer, so those requirements hold too.
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        3,
        "held",
        ["policy_mismatch", "check_pending"],
        None,
    )
    assert not store.exists()


# --- CLI: producer contracts for check requirements -------------------------------------


def test_tracked_policy_contracts_no_check_producer_so_every_check_requirement_holds(
    tmp_path, capsys, store, monkeypatch
):
    monkeypatch.setattr(wb, "observe_selection", lambda *_: TRIAL)
    code, out = check(capsys, develop_manifest(tmp_path), "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        3,
        "held",
        ["check_pending"],
        None,
    )
    assert not store.exists()


def test_one_generic_passing_receipt_cannot_prove_every_develop_requirement(
    tmp_path, capsys, store, trial
):
    generic = write_check(tmp_path, "generic", producer="behavior_proof")
    names = ("staged_scope", "lint_format", "behavior_proof", "unrelated_work")
    manifest = write_manifest(
        tmp_path, "develop", None, {n: {"source": "check", "record": generic} for n in names}
    )
    code, out = check(capsys, manifest, "develop")
    assert (code, out["result"], out["reason_codes"], out["receipt"]) == (
        3,
        "held",
        ["identity_mismatch"],
        None,
    )
    assert not store.exists()


@pytest.mark.parametrize(
    "change",
    [
        {"checker": "other-linter"},
        {"argv": ["ruff", "check", "--exit-zero"]},
        {"scope": "working_tree"},
    ],
)
def test_receipt_from_another_checker_invocation_or_scope_holds(
    tmp_path, capsys, store, monkeypatch, trial, change
):
    # The policy now contracts a different lint_format invocation than the receipt records.
    raw = policy_bytes(
        {"checks": {**CONTRACTS, "lint_format": {**CONTRACTS["lint_format"], **change}}}
    )
    use_policy(monkeypatch, tmp_path, raw)
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    for name, observation in doc["observations"].items():
        observation["record"] = write_check(
            tmp_path, f"{name}-current", producer=name, digest=policy_digest(raw)
        )
    path.write_text(json.dumps(doc))
    code, out = check(capsys, path, "develop")
    assert (code, out["result"], out["reason_codes"]) == (3, "held", ["identity_mismatch"])
    assert not store.exists()


def test_receipt_produced_under_another_policy_holds(tmp_path, capsys, store, trial):
    path = develop_manifest(tmp_path)
    doc = json.loads(path.read_text())
    doc["observations"]["lint_format"]["record"] = write_check(
        tmp_path, "old-policy", producer="lint_format", digest="d" * 64
    )
    path.write_text(json.dumps(doc))
    code, out = check(capsys, path, "develop")
    assert (code, out["result"], out["reason_codes"]) == (3, "held", ["policy_mismatch"])
    assert not store.exists()


@pytest.mark.parametrize(
    "rules",
    [
        {
            "checks": {
                **CONTRACTS,
                "staged_scope": {**CONTRACTS["staged_scope"], "scope": "git_tree"},
            }
        },
        {"checks": {"review_request": CONTRACTS["revision"]}},
        {"checks": {"not_a_requirement": CONTRACTS["revision"]}},
        {"checks": {"lint_format": {**CONTRACTS["lint_format"], "extra": True}}},
        {"checks": {"lint_format": {**CONTRACTS["lint_format"], "argv": []}}},
        {"checks": {"lint_format": {**CONTRACTS["lint_format"], "scope": "disk"}}},
        {"other": {}},
    ],
)
def test_malformed_check_contract_in_policy_rejects(
    tmp_path, capsys, store, monkeypatch, trial, rules
):
    use_policy(monkeypatch, tmp_path, policy_bytes(rules))
    code, out = check(capsys, develop_manifest(tmp_path), "develop")
    assert (code, out["reason_codes"], out["receipt"]) == (2, ["invalid_input"], None)
    assert not store.exists()


# --- CLI: status ------------------------------------------------------------------------


def test_status_reads_without_side_effects(capsys, store):
    code, out = run(capsys, "status", "--unit", UNIT)
    assert code == 0
    assert list(out) == [*WIRE_FIELDS, "observed_state"]
    assert (out["boundary"], out["point"], out["receipt"]) == (None, None, None)
    assert out["observed_state"] == {
        b: "unknown" for b in ("prepare", "develop", "publish", "integrate")
    }
    assert not store.exists()


def test_status_reports_the_last_verified_receipt_per_boundary(tmp_path, capsys, store, trial):
    _, develop = check(capsys, develop_manifest(tmp_path), "develop")
    before = sorted(store.iterdir())

    code, out = run(capsys, "status", "--unit", UNIT)
    assert code == 0
    assert out["observed_state"]["develop"] == {
        "record_type": "boundary_admission",
        "point": None,
        "receipt": develop["receipt"],
    }
    assert out["observed_state"]["publish"] == "unknown"
    assert sorted(store.iterdir()) == before

    other_code, other = run(capsys, "status", "--unit", "arhugula-harness-trial-193.7x7.nff")
    assert other_code == 0 and other["observed_state"]["develop"] == "unknown"


def test_status_with_a_corrupt_receipt_is_exit_5(capsys, store):
    store.mkdir()
    (store / "broken.json").write_text("{")
    code, out = run(capsys, "status", "--unit", UNIT)
    assert (code, out["result"], out["reason_codes"]) == (5, "error", ["artifact_unavailable"])


def assert_status_refuses(capsys) -> None:
    code, out = run(capsys, "status", "--unit", UNIT)
    assert (code, out["result"], out["reason_codes"]) == (5, "error", ["artifact_unavailable"])
    assert "observed_state" not in out


def test_status_refuses_a_forged_minimal_receipt(capsys, store):
    store.mkdir()
    (store / "forged.json").write_text(
        json.dumps(
            {
                "unit_id": UNIT,
                "record_type": "boundary_completion",
                "result": "passed",
                "created_at": "2026-10-24T00:00:00.000000Z",
                "inputs": {"boundary": "publish", "point": "after"},
            }
        )
    )
    assert_status_refuses(capsys)


def published(tmp_path, capsys) -> tuple[Path, dict]:
    code, out = check(capsys, develop_manifest(tmp_path), "develop")
    assert code == 0
    path = Path(out["receipt"]["uri"])
    return path, json.loads(path.read_bytes())


def republish(store: Path, doc: dict, name: str | None = None) -> None:
    raw = json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()
    (store / f"{name or doc['record_id']}.json").write_bytes(raw)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda doc: doc["subject"].update(head="e" * 40),
        lambda doc: doc.update(policy_version=2),
        lambda doc: doc.update(schema_version=2),
        lambda doc: doc.update(producer={"tool": "someone else"}),
        lambda doc: doc.update(limits=[]),
        lambda doc: doc.pop("supersedes"),
        lambda doc: doc["inputs"]["observations"].pop("lint_format"),
    ],
)
def test_status_refuses_a_receipt_whose_body_disagrees_with_its_record_id(
    tmp_path, capsys, store, trial, mutate
):
    path, doc = published(tmp_path, capsys)
    path.unlink()
    mutate(doc)
    republish(store, doc)
    assert_status_refuses(capsys)


def test_status_refuses_a_digest_consistent_receipt_missing_an_observation(
    tmp_path, capsys, store, trial
):
    path, doc = published(tmp_path, capsys)
    path.unlink()
    body = {k: v for k, v in doc.items() if k != "record_id"}
    del body["inputs"]["observations"]["behavior_proof"]
    record_id = f"{UNIT}.develop.{wb.canonical_digest(body)[:16]}"
    republish(store, {"record_id": record_id, **body})
    assert_status_refuses(capsys)


def test_status_refuses_a_receipt_stored_under_another_name(tmp_path, capsys, store, trial):
    path, _ = published(tmp_path, capsys)
    path.rename(store / "renamed.json")
    assert_status_refuses(capsys)


def test_status_refuses_a_receipt_whose_bytes_are_not_canonical(tmp_path, capsys, store, trial):
    path, doc = published(tmp_path, capsys)
    path.write_text(json.dumps(doc, indent=2))
    assert_status_refuses(capsys)


def status(capsys) -> tuple[int, dict, str]:
    code = cg.main(["workflow", "status", "--unit", UNIT])
    captured = capsys.readouterr()
    return code, json.loads(captured.out), captured.err


def test_status_never_reports_a_completion_whose_producer_records_are_absent(capsys, store, trial):
    request = parse_request(UNIT, "integrate", "after")
    absent = Reference("/nonexistent/producer.json", "0" * 64, 17)
    record = wb.boundary_record(
        request,
        SUBJECT,
        {req.name: absent for req in requirements(request.step)},
        created_at="2026-10-24T00:00:00.000000Z",
    )
    wb.publish(record)  # canonical bytes under the canonical name

    code, out, err = status(capsys)
    assert (code, out["result"]) == (0, "passed")
    assert out["observed_state"]["integrate"] == "unknown"
    assert str(record["record_id"]) in err


def test_status_forgets_a_passing_check_whose_producer_was_deleted(tmp_path, capsys, store, trial):
    path, doc = published(tmp_path, capsys)
    Path(doc["inputs"]["observations"]["lint_format"]["uri"]).unlink()

    code, out, err = status(capsys)
    assert code == 0
    assert out["observed_state"]["develop"] == "unknown"
    assert path.name in err


def test_status_reports_the_last_receipt_whose_producers_still_verify(
    tmp_path, capsys, store, trial
):
    first, _ = published(tmp_path, capsys)
    later = tmp_path / "later"
    later.mkdir()
    second, doc = published(later, capsys)
    Path(doc["inputs"]["observations"]["behavior_proof"]["uri"]).write_bytes(b"changed")

    code, out, err = status(capsys)
    assert code == 0
    assert out["observed_state"]["develop"]["receipt"]["uri"] == str(first)
    assert second.name in err and first.name not in err


# --- existing guard contract ------------------------------------------------------------


def test_existing_modes_keep_their_parser_and_exit():
    with pytest.raises(SystemExit) as raised:
        cg.main(["not-a-mode"])
    assert raised.value.code == 2


def test_script_entry_dispatches_workflow_before_the_mode_parser(tmp_path):
    guard = Path(cg.__file__).resolve()
    proc = subprocess.run(
        [
            sys.executable,
            str(guard),
            "workflow",
            "check",
            "--unit",
            UNIT,
            "--boundary",
            "prepare",
            "--point",
            "before",
            "--manifest",
            str(tmp_path / "absent.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )
    assert proc.returncode == 2, proc.stderr
    assert json.loads(proc.stdout)["reason_codes"] == ["invalid_input"]


def test_a_published_receipt_is_never_overwritten(store):
    wb.publish({"record_id": "fixed", "result": "passed"})
    with pytest.raises(FileExistsError):
        wb.publish({"record_id": "fixed", "result": "failed"})
    assert json.loads((store / "fixed.json").read_text())["result"] == "passed"
