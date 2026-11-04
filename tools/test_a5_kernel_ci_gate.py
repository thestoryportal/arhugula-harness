"""trial-193 ci-venue-v2: the A5 kernel venue gate fails closed.

Three lenses. The binding lens keeps the reviewed expectations true to the tree: the exact
guarded IDs are what the launcher-gated markers actually select, the bound blobs are the
current files, and the venues are the ci.yml matrix legs. The preflight lens drives the
pure host judgement with each allocation a runner could produce. The outcome lens runs
real pytest to produce real JUnit, then drives every failure path the gate exists for:
missing, duplicate, skipped (including the device-node prerequisite), xfailed, held for
the wrong reason, stale, malformed and cross-run evidence."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a5_kernel_ci_gate import (
    EXPECTATIONS,
    ROOT,
    Expectations,
    ExpectationsError,
    HostReport,
    JUnitError,
    NodeId,
    Outcome,
    Refused,
    Status,
    Supported,
    git_blob,
    judge_outcomes,
    judge_preflight,
    main,
    parse_expectations,
    parse_junit,
    required_outcomes,
)

_RAW = json.loads(EXPECTATIONS.read_text())
_EXPECTED = parse_expectations(_RAW)
_REFUSAL = "Landlock ABI 8 < required 9"


# --- binding lens -------------------------------------------------------------------

_MARKS_PLUGIN = """
import json, os
def pytest_collection_finish(session):
    out = {"supported": [], "unsupported": []}
    for item in session.items:
        for mark in item.iter_markers("skipif"):
            reason = mark.kwargs.get("reason", "")
            if reason.startswith("HELD (unproved here)"):
                out["supported"].append(item.nodeid)
            elif reason.startswith("this host is supported"):
                out["unsupported"].append(item.nodeid)
    with open(os.environ["A5_MARKS_OUT"], "w") as f:
        json.dump(out, f)
"""


def test_guarded_ids_are_exactly_what_the_launcher_gated_markers_select(tmp_path: Path) -> None:
    (tmp_path / "a5_marks.py").write_text(_MARKS_PLUGIN)
    out = tmp_path / "marks.json"
    env = {**os.environ, "PYTHONPATH": str(tmp_path), "A5_MARKS_OUT": str(out)}
    test_files = [p for p in _EXPECTED.bound_blobs if "/tests/" in p]
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "a5_marks",
         "-p", "no:cacheprovider", *test_files],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )  # fmt: skip
    assert p.returncode == 0, p.stdout + p.stderr
    marks = json.loads(out.read_text())
    assert marks["supported"] == [str(i) for i in _EXPECTED.supported_host_ids]
    assert marks["unsupported"] == [str(i) for i in _EXPECTED.unsupported_host_ids]
    assert (len(marks["supported"]), len(marks["unsupported"])) == (36, 2)


def test_bound_blobs_are_the_current_files() -> None:
    for path, blob in _EXPECTED.bound_blobs.items():
        assert git_blob((ROOT / path).read_bytes()) == blob, f"{path}: re-review expectations"


def test_git_blob_matches_git() -> None:
    path = next(iter(_EXPECTED.bound_blobs))
    p = subprocess.run(["git", "hash-object", path], cwd=ROOT, capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout.strip() == git_blob((ROOT / path).read_bytes())


def test_venues_are_the_ci_matrix_legs() -> None:
    jobs = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text())["jobs"]
    legs = {m["venue"] for m in jobs["package-tests"]["strategy"]["matrix"]["include"]}
    assert legs == set(_EXPECTED.venues)
    assert _EXPECTED.venues["supported"] == Supported("ubuntu26")
    assert _EXPECTED.venues["unsupported-abi8"] == Refused("ubuntu24", 8, _REFUSAL)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda raw: raw["venues"]["supported"].update(kind="maybe"),
        lambda raw: raw["supported_host_ids"].append(raw["unsupported_host_ids"][0]),
        lambda raw: raw["supported_host_ids"].append("tests/test_x.py::TestA::test_b"),
        lambda raw: raw.pop("bound_blobs"),
    ],
    ids=["unknown-kind", "listed-twice", "class-node-id", "no-bindings"],
)
def test_malformed_expectations_are_refused(mutate: Any) -> None:
    raw = json.loads(json.dumps(_RAW))
    mutate(raw)
    with pytest.raises(ExpectationsError):
        parse_expectations(raw)


def test_test_id_round_trips_to_its_junit_key() -> None:
    test_id = NodeId.parse("harness-runtime/tests/test_a.py::test_b[x/y]")
    assert test_id.junit_key == ("harness-runtime.tests.test_a", "test_b[x/y]")
    assert str(test_id) == "harness-runtime/tests/test_a.py::test_b[x/y]"


# --- preflight lens -----------------------------------------------------------------

_ENV = {
    "CI_HEAD": "h" * 40,
    "CI_BASE": "b" * 40,
    "CI_TESTED": "t" * 40,
    "GITHUB_WORKFLOW": "CI",
    "GITHUB_RUN_ID": "41",
    "GITHUB_RUN_ATTEMPT": "1",
    "ImageOS": "ubuntu24",
    "ImageVersion": "20261028.624",
    "RUNNER_NAME": "GitHub Actions 1",
    "RUNNER_ENVIRONMENT": "github-hosted",
}
_BLOBS = {"a.py": "1" * 40}


def _judge(venue: Any, host: HostReport, **env: str) -> list[str]:
    return judge_preflight(venue, host, _ENV | env, _BLOBS, _BLOBS, _ENV["CI_TESTED"])


def test_the_selected_allocations_pass_preflight() -> None:
    assert _judge(Supported("ubuntu26"), HostReport("x86_64", 9, None), ImageOS="ubuntu26") == []
    assert _judge(Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 8, _REFUSAL)) == []


@pytest.mark.parametrize(
    ("venue", "host", "env", "needle"),
    [
        (Supported("ubuntu26"), HostReport("x86_64", 8, _REFUSAL), {"ImageOS": "ubuntu26"},
         "refused the supported venue"),
        (Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 10, None), {}, "exactly 8"),
        (Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 7, "Landlock ABI 7 < required 9"),
         {}, "exactly 8"),
        (Refused("ubuntu24", 8, _REFUSAL),
         HostReport("riscv64", 8, "Landlock syscalls unverified on architecture 'riscv64'"),
         {}, "venue requires"),
        (Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 8, _REFUSAL),
         {"ImageOS": "ubuntu26"}, "ImageOS"),
        (Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 8, _REFUSAL),
         {"ImageVersion": ""}, "ImageVersion is unset"),
        (Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 8, _REFUSAL),
         {"CI_TESTED": "c" * 40}, "checked-out"),
    ],
    ids=["supported-refused", "abi8-venue-got-10", "abi8-venue-got-7", "wrong-arch",
         "wrong-image", "unknown-image-version", "wrong-checkout"],
)  # fmt: skip
def test_a_wrong_allocation_fails_preflight(
    venue: Any, host: HostReport, env: dict[str, str], needle: str
) -> None:
    problems = _judge(venue, host, **env)
    assert any(needle in p for p in problems), problems


def test_a_stale_binding_fails_preflight() -> None:
    venue, host = Refused("ubuntu24", 8, _REFUSAL), HostReport("x86_64", 8, _REFUSAL)
    for actual in ({"a.py": "2" * 40}, {"a.py": None}):
        problems = judge_preflight(venue, host, _ENV, actual, _BLOBS, _ENV["CI_TESTED"])
        assert any("stale" in p for p in problems), problems


# --- outcome lens -------------------------------------------------------------------

_MODULE = """
import pytest

def test_passes():
    pass

@pytest.mark.skipif(True, reason="HELD: launcher refuses this host: Landlock ABI 8 < required 9")
def test_held():
    pass

def test_skipped_for_a_prerequisite():
    pytest.skip("HELD: a sandbox refuses mknod before Landlock (EPERM)")

@pytest.mark.xfail(reason="expected")
def test_xfails():
    assert False

def test_fails():
    assert False

@pytest.fixture
def broken():
    raise RuntimeError("setup")

def test_errors(broken):
    pass
"""


@pytest.fixture(scope="module")
def real_junit(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, datetime]:
    root = tmp_path_factory.mktemp("junit")
    (root / "test_sample.py").write_text(_MODULE)
    before = datetime.now(UTC)
    subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", str(root),
         "--junitxml", str(root / "junit.xml"), str(root / "test_sample.py")],
        cwd=root, capture_output=True, text=True,
    )  # fmt: skip
    return (root / "junit.xml").read_text(), before


def _id(name: str) -> NodeId:
    return NodeId("test_sample.py", name)


def test_real_junit_outcomes_are_classified(real_junit: tuple[str, datetime]) -> None:
    text, before = real_junit
    outcomes = parse_junit(text, before)
    got = {name: o[0].status for (_, name), o in outcomes.items()}
    assert got == {
        "test_passes": Status.PASSED,
        "test_held": Status.SKIPPED,
        "test_skipped_for_a_prerequisite": Status.SKIPPED,
        "test_xfails": Status.XFAILED,
        "test_fails": Status.FAILED,
        "test_errors": Status.ERROR,
    }
    assert set(outcomes) == {_id(n).junit_key for n in got}
    [held] = outcomes[_id("test_held").junit_key]
    assert _REFUSAL in held.message


def _expectations(supported: list[str], unsupported: list[str]) -> Expectations:
    return Expectations(
        {}, {}, tuple(_id(n) for n in supported), tuple(_id(n) for n in unsupported)
    )


def test_the_supported_venue_needs_every_positive_to_pass(real_junit: tuple[str, datetime]) -> None:
    outcomes = parse_junit(*real_junit)
    good = _expectations(["test_passes"], ["test_held"])
    assert judge_outcomes(required_outcomes(good, Supported("ubuntu26")), outcomes)[1] == []
    for name in ("test_skipped_for_a_prerequisite", "test_xfails", "test_fails", "test_errors"):
        bad = _expectations(["test_passes", name], ["test_held"])
        observed, problems = judge_outcomes(required_outcomes(bad, Supported("ubuntu26")), outcomes)
        assert problems and str(_id(name)) in problems[0], (name, problems)
        assert observed[str(_id(name))] != "passed"


def test_the_refused_venue_needs_positives_held_for_the_actual_refusal(
    real_junit: tuple[str, datetime],
) -> None:
    outcomes = parse_junit(*real_junit)
    venue = Refused("ubuntu24", 8, _REFUSAL)
    good = _expectations(["test_held"], ["test_passes"])
    assert judge_outcomes(required_outcomes(good, venue), outcomes)[1] == []
    # Skipped, but for a prerequisite rather than the launcher's refusal: not proof.
    wrong_reason = _expectations(["test_skipped_for_a_prerequisite"], ["test_passes"])
    assert judge_outcomes(required_outcomes(wrong_reason, venue), outcomes)[1]
    # A positive that ran on a host the launcher refuses is not the venue either.
    ran = _expectations(["test_passes"], ["test_held"])
    assert len(judge_outcomes(required_outcomes(ran, venue), outcomes)[1]) == 2


def test_missing_and_duplicate_ids_fail() -> None:
    expected = _expectations(["test_a", "test_b"], [])
    passed = Outcome(Status.PASSED, "")
    outcomes = {_id("test_b").junit_key: [passed, passed]}  # test_a deselected/absent
    observed, problems = judge_outcomes(required_outcomes(expected, Supported("u")), outcomes)
    assert observed == {str(_id("test_a")): "missing", str(_id("test_b")): "duplicate"}
    assert len(problems) == 2


def test_malformed_or_stale_junit_is_refused(real_junit: tuple[str, datetime]) -> None:
    text, before = real_junit
    with pytest.raises(JUnitError, match="malformed"):
        parse_junit(text[: len(text) // 2], before)
    with pytest.raises(JUnitError, match="predates"):
        parse_junit(text, before + timedelta(hours=1))
    with pytest.raises(JUnitError, match="no testsuite"):
        parse_junit("<testsuites/>", before)
    naive = '<testsuite timestamp="2026-11-04T00:00:00"><testcase name="b"/></testsuite>'
    with pytest.raises(JUnitError):
        parse_junit(naive, before)


# --- CLI: check binds this leg's evidence --------------------------------------------


def _write_leg(tmp_path: Path, junit: str, **preflight: Any) -> list[str]:
    started = (datetime.now(UTC) - timedelta(minutes=5)).isoformat()
    record = {"venue": "x", "started_at": started, "binding": dict(_ENV), "problems": []}
    (tmp_path / "preflight.json").write_text(json.dumps(record | preflight))
    (tmp_path / "junit.xml").write_text(junit)
    raw = {
        "bound_blobs": {},
        "venues": {"x": {"kind": "supported", "image_os": "ubuntu26"}},
        "supported_host_ids": [str(_id("test_passes"))],
        "unsupported_host_ids": [],
    }
    (tmp_path / "expectations.json").write_text(json.dumps(raw))
    return [
        "check", "--venue", "x", "--expectations", str(tmp_path / "expectations.json"),
        "--preflight", str(tmp_path / "preflight.json"), "--junit", str(tmp_path / "junit.xml"),
        "--out", str(tmp_path / "out" / "outcomes.json"),
    ]  # fmt: skip


def _run(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> tuple[int, dict[str, Any]]:
    for name, value in _ENV.items():
        monkeypatch.setenv(name, value)
    code = main(argv)
    return code, json.loads(Path(argv[-1]).read_text())


_JUNIT = (
    f'<testsuites><testsuite timestamp="{datetime.now(UTC).isoformat()}">'
    '<testcase classname="test_sample" name="test_passes"/></testsuite></testsuites>'
)


def test_check_passes_this_legs_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    code, record = _run(monkeypatch, _write_leg(tmp_path, _JUNIT))
    assert (code, record["verdict"], record["problems"]) == (0, "pass", [])
    assert record["outcomes"] == {str(_id("test_passes")): "passed"}
    assert {"junit_sha256", "preflight_sha256", "expectations_sha256"} <= set(record)


@pytest.mark.parametrize(
    ("junit", "preflight", "needle"),
    [
        (_JUNIT, {"problems": ["launcher refused"]}, "preflight: launcher refused"),
        (_JUNIT, {"venue": "y"}, "venue"),
        (_JUNIT, {"binding": _ENV | {"GITHUB_RUN_ID": "40"}}, "GITHUB_RUN_ID"),
        (_JUNIT, {"binding": _ENV | {"GITHUB_RUN_ATTEMPT": "2"}}, "GITHUB_RUN_ATTEMPT"),
        (_JUNIT, {"binding": _ENV | {"CI_HEAD": "0" * 40}}, "CI_HEAD"),
        (_JUNIT.replace("test_passes", "test_other"), {}, "exactly one"),
        ("<testsuites>", {}, "JUnit not usable"),
    ],
    ids=["preflight-failed", "other-venue", "other-run", "other-attempt", "other-head",
         "missing-id", "malformed-junit"],
)  # fmt: skip
def test_check_fails_and_still_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, junit: str, preflight: Any, needle: str
) -> None:
    code, record = _run(monkeypatch, _write_leg(tmp_path, junit, **preflight))
    assert (code, record["verdict"]) == (1, "fail")
    assert any(needle in p for p in record["problems"]), record["problems"]


def test_check_without_a_preflight_record_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    argv = _write_leg(tmp_path, _JUNIT)
    (tmp_path / "preflight.json").unlink()
    code, record = _run(monkeypatch, argv)
    assert code == 1 and "preflight record unreadable" in record["problems"][0]


def test_unusable_expectations_exit_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    argv = _write_leg(tmp_path, _JUNIT)
    (tmp_path / "expectations.json").write_text('{"venues": {}}')
    assert main(argv) == 2
    assert main([*argv[:2], "nowhere", *argv[3:]]) == 2  # unknown venue
