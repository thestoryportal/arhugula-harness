"""trial-193 ci-venue-v2: the A5 kernel venue gate fails closed.

Three lenses. The binding lens keeps the reviewed expectations true to the tree: the exact
guarded IDs are what the launcher-gated markers actually select, the bound blobs are the
current files, and the venues are the ci.yml matrix legs. The preflight lens drives the
pure host judgement with each allocation a runner could produce. The outcome lens runs
real pytest to produce real JUnit, then drives every failure path the gate exists for:
missing, duplicate, skipped (including the device-node prerequisite), xfailed, held for
the wrong reason, stale, malformed and cross-run evidence, and a preflight record that is
incomplete, stale against the reviewed expectations or not this leg's."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path, PurePosixPath
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a5_kernel_ci_gate as gate
from a5_kernel_ci_gate import (
    EXPECTATIONS,
    ROOT,
    Expectations,
    ExpectationsError,
    HostReport,
    JUnitError,
    Leg,
    NodeId,
    Outcome,
    PreflightError,
    Refused,
    Status,
    Supported,
    git_blob,
    judge_outcomes,
    judge_preflight,
    kernel_config_problems,
    main,
    parse_expectations,
    parse_inputs,
    parse_junit,
    parse_preflight,
    preflight,
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
    assert (len(marks["supported"]), len(marks["unsupported"])) == (37, 2)


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
    for actual in ({"a.py": "2" * 40}, {"a.py": None}, {}, _BLOBS | {"b.py": "3" * 40}):
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


def test_the_real_preflight_record_parses_back() -> None:
    record = json.loads(json.dumps(preflight("supported", _EXPECTED, "e" * 64)))
    prior = parse_preflight(record)
    assert (prior.venue, prior.expectations_sha256) == ("supported", "e" * 64)
    assert prior.blobs == _EXPECTED.bound_blobs
    assert set(prior.binding) == set(_ENV)
    # What check re-measures on the same runner is exactly what preflight recorded.
    assert prior.leg == gate._measure_leg()


# The runner and checkout `check` measures in the CLI fixture.
_LEG = Leg(
    HostReport("x86_64", 9, None),
    "6.17.0-1004-azure",
    "Ubuntu 26.04 LTS",
    _ENV["CI_TESTED"],
    ("p" * 40, "q" * 40),
)


def _record(expectations_sha256: str) -> dict[str, Any]:
    """A complete, passing preflight record for the CLI fixture's supported venue `x`."""
    return {
        "venue": "x",
        "started_at": (datetime.now(UTC) - timedelta(minutes=5)).isoformat(),
        "host": {"machine": _LEG.host.machine, "landlock_abi": _LEG.host.abi,
                 "launcher": "accepted", "refusal": None, "kernel": _LEG.kernel,
                 "os": _LEG.os_release},
        "binding": dict(_ENV),
        "checked_out": _LEG.checked_out,
        "parents": list(_LEG.parents),
        "blobs": dict(_BLOBS),
        "expectations_sha256": expectations_sha256,
        "problems": [],
    }  # fmt: skip


def _write_leg(
    tmp_path: Path, junit: str, mutate: Callable[[dict[str, Any]], object] = lambda r: None
) -> list[str]:
    raw = json.dumps({
        "inputs": _RAW["inputs"],
        "bound_blobs": _BLOBS,
        "venues": {"x": {"kind": "supported", "image_os": _ENV["ImageOS"]}},
        "supported_host_ids": [str(_id("test_passes"))],
        "unsupported_host_ids": [],
    })  # fmt: skip
    (tmp_path / "expectations.json").write_text(raw)
    record = _record(hashlib.sha256(raw.encode()).hexdigest())
    mutate(record)
    (tmp_path / "preflight.json").write_text(json.dumps(record))
    (tmp_path / "junit.xml").write_text(junit)
    return [
        "check", "--venue", "x", "--expectations", str(tmp_path / "expectations.json"),
        "--preflight", str(tmp_path / "preflight.json"), "--junit", str(tmp_path / "junit.xml"),
        "--out", str(tmp_path / "out" / "outcomes.json"),
    ]  # fmt: skip


def _run(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> tuple[int, dict[str, Any]]:
    for name, value in _ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(gate, "_measure_leg", lambda: _LEG)
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


_REFUSED_HOST = {"landlock_abi": 8, "launcher": "refused", "refusal": _REFUSAL}


@pytest.mark.parametrize(
    ("junit", "mutate", "needle"),
    [
        (_JUNIT, lambda r: r.update(problems=["launcher refused"]), "preflight: launcher refused"),
        (_JUNIT, lambda r: r.update(venue="y"), "venue"),
        (_JUNIT, lambda r: r["binding"].update(GITHUB_RUN_ID="40"), "GITHUB_RUN_ID"),
        (_JUNIT, lambda r: r["binding"].update(GITHUB_RUN_ATTEMPT="2"), "GITHUB_RUN_ATTEMPT"),
        (_JUNIT, lambda r: r["binding"].update(CI_HEAD="0" * 40), "CI_HEAD"),
        (_JUNIT, lambda r: r["binding"].update(RUNNER_NAME="GitHub Actions 9"), "RUNNER_NAME"),
        (_JUNIT, lambda r: r["binding"].update(ImageVersion="20260101.1"), "ImageVersion"),
        (_JUNIT, lambda r: r["binding"].pop("ImageOS"), "incomplete"),
        (_JUNIT, lambda r: r.update(expectations_sha256="wrong"), "bound expectations"),
        (_JUNIT, lambda r: r.pop("expectations_sha256"), "incomplete"),
        (_JUNIT, lambda r: r.update(blobs={}), "stale"),
        (_JUNIT, lambda r: r.update(blobs={"a.py": "2" * 40}), "stale"),
        (_JUNIT, lambda r: r["blobs"].update({"b.py": "3" * 40}), "stale"),
        (_JUNIT, lambda r: r.update(blobs={"a.py": 1}), "neither a git blob"),
        (_JUNIT, lambda r: r.pop("blobs"), "incomplete"),
        (_JUNIT, lambda r: r.update(host={}), "incomplete"),
        (_JUNIT, lambda r: r["host"].update(_REFUSED_HOST), "refused the supported venue"),
        (_JUNIT, lambda r: r["host"].update(launcher="refused"), "contradicts"),
        (_JUNIT, lambda r: r["host"].update(landlock_abi="9"), "not int"),
        (_JUNIT, lambda r: r["host"].pop("kernel"), "incomplete"),
        (_JUNIT, lambda r: r["host"].update(machine="", landlock_abi=0, kernel="", os=""),
         "this leg measures"),
        (_JUNIT, lambda r: r["host"].update(landlock_abi=8), "this leg measures"),
        (_JUNIT, lambda r: r["host"].update(machine="riscv64"), "this leg measures"),
        (_JUNIT, lambda r: r["host"].update(kernel="6.8.0-1017-azure"), "this leg measures"),
        (_JUNIT, lambda r: r.update(parents=[]), "this leg measures"),
        (_JUNIT, lambda r: r.update(parents=["0" * 40]), "this leg measures"),
        (_JUNIT, lambda r: r.update(checked_out="c" * 40), "checked-out"),
        (_JUNIT, lambda r: r.pop("parents"), "incomplete"),
        (_JUNIT, lambda r: r.update(started_at="2026-11-04T00:00:00"), "no timezone"),
        (_JUNIT, lambda r: r.pop("problems"), "incomplete"),
        (_JUNIT, lambda r: r.update(problems=[None]), "not a list of strings"),
        (_JUNIT, lambda r: r.update(parents=[1]), "not a list of strings"),
        (_JUNIT, lambda r: r.update(expectations_sha256="wrong", blobs={}, host={}), "incomplete"),
        (_JUNIT.replace("test_passes", "test_other"), lambda r: None, "exactly one"),
        ("<testsuites>", lambda r: None, "JUnit not usable"),
    ],
    ids=["preflight-failed", "other-venue", "other-run", "other-attempt", "other-head",
         "other-runner", "other-image-version", "binding-incomplete", "stale-expectations",
         "no-expectations-digest", "no-blobs", "stale-blob", "unreviewed-blob", "blob-not-sha",
         "blob-map-absent", "host-absent", "host-refused", "launcher-contradicts-refusal",
         "abi-not-int", "kernel-absent", "accepted-impossible-host", "accepted-abi8-host",
         "other-arch", "other-kernel", "no-parents", "unrelated-parents", "other-checkout",
         "parents-absent", "naive-start",
         "problems-absent", "problem-not-str", "parent-not-str", "review-probe", "missing-id",
         "malformed-junit"],
)  # fmt: skip
def test_check_fails_and_still_records(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    junit: str,
    mutate: Callable[[dict[str, Any]], object],
    needle: str,
) -> None:
    code, record = _run(monkeypatch, _write_leg(tmp_path, junit, mutate))
    assert (code, record["verdict"]) == (1, "fail")
    assert any(needle in p for p in record["problems"]), record["problems"]


def test_a_non_object_preflight_record_is_refused() -> None:
    for raw in ([], None, "x"):
        with pytest.raises(PreflightError):
            parse_preflight(raw)


def test_check_without_a_preflight_record_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    argv = _write_leg(tmp_path, _JUNIT)
    (tmp_path / "preflight.json").unlink()
    code, record = _run(monkeypatch, argv)
    assert code == 1 and "preflight record unusable" in record["problems"][0]


def test_unusable_expectations_exit_2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    argv = _write_leg(tmp_path, _JUNIT)
    (tmp_path / "expectations.json").write_text('{"venues": {}}')
    assert main(argv) == 2
    assert main([*argv[:2], "nowhere", *argv[3:]]) == 2  # unknown venue


# --- Q0 inputs ----------------------------------------------------------------------


def _leaf_paths(node: Any, path: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    if isinstance(node, dict):
        return [p for key, value in node.items() for p in _leaf_paths(value, (*path, key))]
    return [path]


_INPUT_LEAVES = _leaf_paths(_RAW["inputs"])


def _put_input(raw: dict[str, Any], path: tuple[str, ...], value: object) -> None:
    for key in path[:-1]:
        raw = raw[key]
    raw[path[-1]] = value


def _drop_input(raw: dict[str, Any], path: tuple[str, ...]) -> None:
    for key in path[:-1]:
        raw = raw[key]
    del raw[path[-1]]


def _input_value(path: tuple[str, ...]) -> Any:
    node: Any = _RAW["inputs"]
    for key in path:
        node = node[key]
    return node


def test_committed_inputs_pin_the_committed_kernel_fragment() -> None:
    inputs = parse_inputs(_RAW["inputs"])
    fragment = (ROOT / "tools" / "a5_guest_kernel.config").read_bytes()
    assert inputs.kernel.config_sha256 == hashlib.sha256(fragment).hexdigest()
    assert inputs.guest_packages == ("git",)
    assert inputs.virtme_ng_version == "1.40-2"
    assert "expectations" not in _RAW  # Q1 freezes it; Q0 runs without it


def test_inputs_sha256_is_canonical_and_byte_sensitive() -> None:
    reordered = json.loads(json.dumps(_RAW["inputs"], sort_keys=True))
    assert list(reordered) != list(_RAW["inputs"])
    assert parse_inputs(reordered).sha256 == parse_inputs(_RAW["inputs"]).sha256
    changed = json.loads(json.dumps(_RAW["inputs"]))
    changed["archive"]["snapshot_id"] = "20261101T000001Z"
    assert parse_inputs(changed).sha256 != parse_inputs(_RAW["inputs"]).sha256


@pytest.mark.parametrize("path", _INPUT_LEAVES, ids=["/".join(p) for p in _INPUT_LEAVES])
@pytest.mark.parametrize("change", ["empty", "absent"])
def test_every_inputs_field_is_required_and_non_empty(path: tuple[str, ...], change: str) -> None:
    raw = json.loads(json.dumps(_RAW["inputs"]))
    if change == "absent":
        _drop_input(raw, path)
    else:
        _put_input(raw, path, [] if isinstance(_input_value(path), list) else "")
    with pytest.raises(ExpectationsError):
        parse_inputs(raw)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("guest_packages",), ["git", "curl"]),
        (("launcher", "virtme_ng"), "1.42-1"),
        (("launcher", "packages"), ["virtme-ng", "qemu-system-x86"]),
        (("archive", "components"), ["main", "main"]),
        (("archive", "snapshot_id"), "latest"),
        (("archive", "signing_key"), "f6ecb3762474eda9d21b7022871920d1991bc93c"),
        (("base", "tarball"), "ubuntu-base-26.04-base-arm64.tar.gz"),
        (("base", "release_dir"), "http://cdimage.ubuntu.com/ubuntu-base/releases/26.04/release/"),
        (("kernel", "tarball_sha256"), "fa595aad"),
        (("interpreter", "cpython"), "3.13.1"),
        (("interpreter", "uv"), 13),
        (("extra",), "x"),
    ],
    ids=lambda v: "/".join(v) if isinstance(v, tuple) else None,
)
def test_inputs_refuse_substitutions(path: tuple[str, ...], value: object) -> None:
    raw = json.loads(json.dumps(_RAW["inputs"]))
    _put_input(raw, path, value)
    with pytest.raises(ExpectationsError):
        parse_inputs(raw)


@pytest.mark.parametrize("command", ["preflight", "check"])
@pytest.mark.parametrize("change", ["absent", "empty-field"])
def test_every_subcommand_refuses_incomplete_inputs(
    tmp_path: Path, command: str, change: str
) -> None:
    argv = _write_leg(tmp_path, _JUNIT)
    path = tmp_path / "expectations.json"
    raw = json.loads(path.read_text())
    if change == "absent":
        del raw["inputs"]
    else:
        raw["inputs"]["interpreter"]["cpython"] = ""
    path.write_text(json.dumps(raw))
    assert main([command, *argv[1:]]) == 2
    assert not (tmp_path / "out").exists()


def test_guest_kernel_config_must_leave_modules_unset() -> None:
    fragment = (ROOT / "tools" / "a5_guest_kernel.config").read_text()
    assert kernel_config_problems(fragment) == []
    assert kernel_config_problems(
        fragment.replace("# CONFIG_MODULES is not set", "CONFIG_MODULES=y")
    )
    assert kernel_config_problems("CONFIG_SECURITY=y\n")


# --- Q0 observation (host side) -----------------------------------------------------

_IDENTITY = {
    "CI_TESTED": "c" * 40,
    "GITHUB_RUN_ID": "4242",
    "GITHUB_RUN_ATTEMPT": "2",
    "INPUTS_SHA256": "1" * 64,
}
# The tested commit's tree and bound blobs, and a guest that booted and ran exactly them.
_TESTED = gate.TestedTree("e" * 40, {path: "f" * 40 for path in gate.BOUND_PRODUCT})
_GUEST_IDENTITY = gate.GuestIdentity(
    gate.GUEST_RELEASE, ("lockdown", "capability", "landlock"), _TESTED.tree, dict(_TESTED.blobs)
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_FULL_CAPS = (1 << 41) - 1
_FORBIDDEN = sum(1 << bit for _, bit in gate.FORBIDDEN_CAPS)
_CLEAN = {name: _FULL_CAPS & ~_FORBIDDEN for name in gate.CAP_SETS}
_DEBS = (gate.Deb("git_1_amd64.deb", 10, "d" * 64), gate.Deb("perl_2_amd64.deb", 20, "e" * 64))
_PROBE_DEB = gate.Deb("a5-netprobe_1_all.deb", 5, "f" * 64)


def _hexes(masks: dict[str, int]) -> dict[str, str]:
    return {name: f"{mask:016x}" for name, mask in masks.items()}


def _install_run_record(debs: tuple[gate.Deb, ...]) -> dict[str, Any]:
    namespace = {
        "host_netns": "net:[4026531840]",
        "netns": "net:[4026532999]",
        "interfaces": ["lo"],
        "environment": dict(gate.INSTALL_ENV),
        "capabilities": _hexes(_CLEAN),
        "debs": [{"file": d.file, "size": d.size, "sha256": d.sha256} for d in debs],
        "dpkg_exit": 0,
    }
    return {"wrapper_exit": 0, "namespace": namespace}


def _probe_text(net: str, sentinel: str, masks: dict[str, int]) -> str:
    caps = "".join(f"{name}={mask:016x}\n" for name, mask in masks.items())
    return f"net={net}\nsentinel={sentinel}\n{caps}"


def _install_ns_doc() -> dict[str, Any]:
    control = _probe_text("connected", "s3nt", dict.fromkeys(gate.CAP_SETS, _FULL_CAPS))
    return {
        "install": _install_run_record(_DEBS),
        "self_test": {
            "sentinel": "s3nt",
            "control": control,
            "inside": _probe_text("failed", "unset", _CLEAN),
            "accepted": 1,
            "deb": {"file": _PROBE_DEB.file, "size": _PROBE_DEB.size, "sha256": _PROBE_DEB.sha256},
            "run": _install_run_record((_PROBE_DEB,)),
        },
    }


def _binding_values() -> dict[str, str]:
    """Run facts for every binding.env key the host writer does not derive itself."""
    return {
        key: ("9" * 64 if key.endswith("_SHA256") else f"v-{key}")
        for key in gate.BINDING_ENV_KEYS
        if key not in gate.DERIVED_BINDINGS
    } | _IDENTITY


def _records(**overrides: Any) -> gate.HostRecords[bytes]:
    doc = _install_ns_doc()
    args: dict[str, Any] = {
        "values": _binding_values(),
        "host": {"gcc": "gcc 15", "preflight": {"verdict": "fail"}},
        "install": doc["install"],
        "self_test": doc["self_test"],
        "sentinel_sha256": {"home": "5" * 64},
    }
    return gate.host_records(**(args | overrides))


class Q0(dict[str, Path]):
    """One consistent Q0 fixture: retained host records, a pre-launch marker, a fresh /out."""

    def observation(self, **fields: Any) -> None:
        env = gate.parse_binding_env(self["binding_env"].read_bytes())
        raw = {
            **_IDENTITY,
            "binding_env_sha256": _sha(self["binding_env"].read_bytes()),
            "INSTALL_NS_SHA256": env["INSTALL_NS_SHA256"],
            "guest_identity": asdict(_GUEST_IDENTITY),
            **fields,
        }
        self["out"].joinpath("observation.json").write_text(
            json.dumps({k: v for k, v in raw.items() if v is not None})
        )

    def binding_env(self, install_ns_sha256: str, **fields: str) -> bytes:
        values = _binding_values() | {
            "HOST_JSON_SHA256": "9" * 64,
            "INSTALL_NS_SHA256": install_ns_sha256,
        }
        return "".join(f"{k}={v}\n" for k, v in (values | fields).items()).encode()

    def observe(self) -> dict[str, Any]:
        return gate.q0_observe(
            self["out"],
            self["launched"],
            _IDENTITY,
            self["evidence"],
            self["binding_env"],
            self["host_stage"],
            self["install_ns"],
            _DEBS,
            _TESTED,
        )


@pytest.fixture
def q0(tmp_path: Path) -> Q0:
    paths = Q0({name: tmp_path / name for name in ("host", "out", "evidence")})
    for directory in paths.values():
        directory.mkdir()
    paths |= {
        "install_ns": paths["host"] / "install-ns.json",
        "host_json": paths["host"] / "host.json",
        "binding_env": paths["host"] / "binding.env",
        "host_stage": paths["host"] / "host-stage.json",
        "launched": paths["host"] / "launched",
    }
    # The real host writer produces the records every Q0 test starts from.
    gate.write_host_records(
        _records(),
        gate.HostRecords(
            paths["install_ns"], paths["host_json"], paths["binding_env"], paths["host_stage"]
        ),
    )
    paths["launched"].touch()
    paths.observation()
    return paths


def _completed_nothing(record: dict[str, Any]) -> None:
    assert record["completed_observation"] is False and record["problems"]


# Group 1: the passing control.
def test_q0_fresh_bound_observation_completes(q0: Q0) -> None:
    record = q0.observe()
    assert record == {
        "observation_sha256": _sha((q0["out"] / "observation.json").read_bytes()),
        "completed_observation": True,
        "problems": [],
    }
    verify = json.loads((q0["evidence"] / "binding-verify.json").read_text())
    assert verify["verdict"] == "pass"
    assert set(verify["binding_env_sha256"].values()) == {_sha(q0["binding_env"].read_bytes())}
    assert verify["host_stage_sha256"] == _sha(q0["host_stage"].read_bytes())
    assert verify["guest_record_sha256"] == record["observation_sha256"]
    install = json.loads((q0["evidence"] / "install-binding.json").read_text())
    assert install["verdict"] == "pass"
    identity = json.loads((q0["evidence"] / "guest-identity.json").read_text())
    assert identity["verdict"] == "pass" and identity["tested"] == asdict(_TESTED)
    assert (q0["evidence"] / "observation.json").read_bytes() == (
        q0["out"] / "observation.json"
    ).read_bytes()
    assert not {"verdict", "outcomes", "preflight"} & record.keys()


def _replace(path: Path, make: Callable[[Path], None]) -> None:
    path.unlink()
    make(path)


# Group 2: the collector refuses what is not one regular, complete record.
@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda p: p.unlink(), id="missing"),
        pytest.param(lambda p: _replace(p, Path.mkdir), id="directory"),
        pytest.param(lambda p: _replace(p, os.mkfifo), id="fifo"),
        pytest.param(lambda p: p.write_text(""), id="empty"),
        pytest.param(lambda p: p.write_text("{"), id="malformed"),
        pytest.param(lambda p: p.write_text("[]"), id="not-an-object"),
        *[
            pytest.param(
                lambda p, key=key: p.write_text(
                    json.dumps({k: v for k, v in json.loads(p.read_text()).items() if k != key})
                ),
                id=f"no-{key}",
            )
            for key in (*_IDENTITY, "binding_env_sha256", "INSTALL_NS_SHA256")
        ],
    ],
)
def test_q0_collector_refuses_an_unusable_observation(q0: Q0, mutate: Any) -> None:
    mutate(q0["out"] / "observation.json")
    record = q0.observe()
    _completed_nothing(record)
    assert record["problems"][0].startswith("collect:")
    assert list(q0["evidence"].iterdir()) == []


def test_q0_collector_refuses_a_symlink_to_a_fresh_record(q0: Q0) -> None:
    real = q0["host"] / "elsewhere.json"
    (q0["out"] / "observation.json").rename(real)
    (q0["out"] / "observation.json").symlink_to(real)
    _completed_nothing(q0.observe())


# Group 3: freshness against the pre-launch marker, and why a timestamp is not enough.
def test_q0_collector_refuses_a_record_predating_the_launch(q0: Q0) -> None:
    launched = q0["launched"].stat().st_mtime_ns
    os.utime(q0["out"] / "observation.json", ns=(launched - 10**9, launched - 10**9))
    record = q0.observe()
    _completed_nothing(record)
    assert "predates the guest launch" in record["problems"][0]


def test_q0_collector_refuses_a_prior_attempt_copied_after_a_new_launch(q0: Q0) -> None:
    prior = {**_IDENTITY, "GITHUB_RUN_ATTEMPT": "1"}
    q0.observation(GITHUB_RUN_ATTEMPT=prior["GITHUB_RUN_ATTEMPT"])
    data = (q0["out"] / "observation.json").read_bytes()
    q0["launched"].touch()
    (q0["out"] / "observation.json").write_bytes(data)
    record = q0.observe()
    _completed_nothing(record)
    assert "GITHUB_RUN_ATTEMPT" in record["problems"][0]


# Group 4: each identity mismatch refuses before binding-verify, with no fallback.
@pytest.mark.parametrize("key", _IDENTITY)
def test_q0_collector_refuses_another_runs_identity(q0: Q0, key: str) -> None:
    q0.observation(**{key: "2" * 64 if key == "INPUTS_SHA256" else "other"})
    (q0["host"] / "host.json").write_text(json.dumps(_IDENTITY))
    record = q0.observe()
    _completed_nothing(record)
    assert key in record["problems"][0] and len(record["problems"]) == 1
    assert list(q0["evidence"].iterdir()) == []


# Group 5: binding-verify needs three equal, lowercase-hex hashes of the retained bytes.
def _drop(path: Path, key: str) -> None:
    raw = json.loads(path.read_text())
    del raw[key]
    path.write_text(json.dumps(raw))


def _set(path: Path, key: str, value: str) -> None:
    path.write_text(json.dumps(json.loads(path.read_text()) | {key: value}))


_HOST_BINDING_MUTATIONS = {
    "binding-env-missing": lambda q: q["binding_env"].unlink(),
    "binding-env-malformed": lambda q: q["binding_env"].write_text("not a binding\n"),
    "binding-env-extra-key": lambda q: q["binding_env"].write_bytes(
        q["binding_env"].read_bytes() + b"EXTRA=1\n"
    ),
    "binding-env-one-byte": lambda q: q["binding_env"].write_bytes(
        q["binding_env"].read_bytes().replace(b"v-CI_HEAD", b"v-CI_HEAE")
    ),
    "host-stage-missing": lambda q: q["host_stage"].unlink(),
    "host-stage-malformed": lambda q: q["host_stage"].write_text("{"),
    "host-stage-no-hash": lambda q: _drop(q["host_stage"], "binding_env_sha256"),
}


@pytest.mark.parametrize("mutate", _HOST_BINDING_MUTATIONS.values(), ids=_HOST_BINDING_MUTATIONS)
def test_q0_binding_verify_failure_keeps_raw_evidence_but_withholds_completion(
    q0: Q0, mutate: Callable[[Q0], None]
) -> None:
    mutate(q0)
    record = q0.observe()
    _completed_nothing(record)
    assert any(p.startswith("binding-verify:") for p in record["problems"])
    assert (q0["evidence"] / "observation.json").is_file()
    verify = json.loads((q0["evidence"] / "binding-verify.json").read_text())
    assert verify["verdict"] == "fail"


_GUEST_BINDING_MUTATIONS = {
    "absent": lambda p: p.unlink(),
    "malformed": lambda p: p.write_text("{"),
    "no-hash": lambda p: _drop(p, "binding_env_sha256"),
    "uppercase": lambda p: _set(p, "binding_env_sha256", "A" * 64),
    "short": lambda p: _set(p, "binding_env_sha256", "a" * 63),
    "differs": lambda p: _set(p, "binding_env_sha256", "a" * 64),
}


@pytest.mark.parametrize("mutate", _GUEST_BINDING_MUTATIONS.values(), ids=_GUEST_BINDING_MUTATIONS)
def test_q0_binding_verify_refuses_an_unbound_guest_record(
    q0: Q0, mutate: Callable[[Path], None], monkeypatch: pytest.MonkeyPatch
) -> None:
    guest = q0["out"] / "observation.json"
    assert (
        gate.binding_verify(q0["binding_env"], q0["host_stage"], guest, _IDENTITY)["problems"] == []
    )
    mutate(guest)
    # An environment-supplied hash is never a substitute for the recorded one.
    monkeypatch.setenv("binding_env_sha256", _sha(q0["binding_env"].read_bytes()))
    assert gate.binding_verify(q0["binding_env"], q0["host_stage"], guest, _IDENTITY)["problems"]
    _completed_nothing(q0.observe())


def test_guest_release_is_the_pinned_source_built_with_the_gate_localversion() -> None:
    assert gate.GUEST_RELEASE == "7.3.1-a5guest"


def test_the_guest_rereads_exactly_the_blobs_the_expectations_bind() -> None:
    assert set(gate.BOUND_PRODUCT) == set(_EXPECTED.bound_blobs)


_FIRST, *_ = gate.BOUND_PRODUCT
_GUEST_IDENTITY_MUTATIONS: dict[str, Any] = {
    "release-unsuffixed": asdict(replace(_GUEST_IDENTITY, release="7.3.1")),
    "release-host-kernel": asdict(replace(_GUEST_IDENTITY, release="6.17.0-1-azure")),
    "no-landlock": asdict(replace(_GUEST_IDENTITY, lsm=("lockdown", "capability"))),
    "landlock-substring": asdict(replace(_GUEST_IDENTITY, lsm=("nolandlock",))),
    "other-tree": asdict(replace(_GUEST_IDENTITY, tree="d" * 40)),
    **{
        f"blob-{path.rsplit('/', 1)[1]}": asdict(
            replace(_GUEST_IDENTITY, blobs=dict(_TESTED.blobs) | {path: "0" * 40})
        )
        for path in gate.BOUND_PRODUCT
    },
    "blob-missing-file": asdict(
        replace(_GUEST_IDENTITY, blobs=dict(_TESTED.blobs) | {_FIRST: None})
    ),
    "blob-unmeasured": asdict(
        replace(_GUEST_IDENTITY, blobs={p: b for p, b in _TESTED.blobs.items() if p != _FIRST})
    ),
}
# Records the host check cannot parse: refused before any value is compared.
_UNPARSABLE_GUEST_IDENTITY: dict[str, Any] = {
    "absent": None,
    "not-an-object": [],
    "lsm-as-text": asdict(_GUEST_IDENTITY) | {"lsm": "landlock"},
    "no-tree": {k: v for k, v in asdict(_GUEST_IDENTITY).items() if k != "tree"},
    "blob-not-text": asdict(_GUEST_IDENTITY) | {"blobs": {_FIRST: 7}},
}


@pytest.mark.parametrize(
    "guest_identity", _GUEST_IDENTITY_MUTATIONS.values(), ids=_GUEST_IDENTITY_MUTATIONS
)
def test_q0_guest_identity_refuses_a_wrong_kernel_or_checkout(q0: Q0, guest_identity: Any) -> None:
    q0.observation(guest_identity=guest_identity)
    record = q0.observe()
    _completed_nothing(record)
    assert all(p.startswith("guest-identity: ") for p in record["problems"]), record["problems"]
    assert json.loads((q0["evidence"] / "guest-identity.json").read_text())["verdict"] == "fail"
    assert json.loads((q0["evidence"] / "binding-verify.json").read_text())["verdict"] == "pass"


@pytest.mark.parametrize(
    "guest_identity", _UNPARSABLE_GUEST_IDENTITY.values(), ids=_UNPARSABLE_GUEST_IDENTITY
)
def test_q0_guest_identity_refuses_an_unparsable_record(q0: Q0, guest_identity: Any) -> None:
    q0.observation(guest_identity=guest_identity)
    _completed_nothing(q0.observe())
    kept = json.loads((q0["evidence"] / "guest-identity.json").read_text())
    assert kept["verdict"] == "fail" and "guest" not in kept
    [problem] = kept["problems"]
    assert problem.startswith("observation.json guest_identity ")


# Group 6: install-binding ties install-ns.json, binding.env and the guest's value.
_INSTALL_MUTATIONS = {
    "absent": lambda q: q["install_ns"].unlink(),
    "malformed": lambda q: q["install_ns"].write_text("{"),
    "changed-after-binding": lambda q: q["install_ns"].write_bytes(
        q["install_ns"].read_bytes() + b"\n"
    ),
}


@pytest.mark.parametrize("mutate", _INSTALL_MUTATIONS.values(), ids=_INSTALL_MUTATIONS)
def test_q0_install_binding_failure_withholds_completion(
    q0: Q0, mutate: Callable[[Q0], None]
) -> None:
    mutate(q0)
    record = q0.observe()
    _completed_nothing(record)
    assert all(p.startswith("install-binding:") for p in record["problems"])
    assert json.loads((q0["evidence"] / "binding-verify.json").read_text())["verdict"] == "pass"


def test_q0_install_binding_refuses_a_guest_value_that_differs(q0: Q0) -> None:
    q0.observation(INSTALL_NS_SHA256="a" * 64)
    record = q0.observe()
    _completed_nothing(record)
    assert record["problems"] == [
        p for p in record["problems"] if p.startswith("install-binding: INSTALL_NS_SHA256")
    ]


def test_q0_install_binding_refuses_a_binding_env_value_that_differs(q0: Q0) -> None:
    env = q0.binding_env("b" * 64)
    q0["binding_env"].write_bytes(env)
    q0["host_stage"].write_text(json.dumps({"binding_env_sha256": _sha(env)}))
    q0.observation(INSTALL_NS_SHA256=_sha(q0["install_ns"].read_bytes()))
    record = q0.observe()
    _completed_nothing(record)
    assert all(p.startswith("install-binding:") for p in record["problems"])


# Group 7: Q0 and Q2 records are not interchangeable.
def test_q2_check_refuses_a_q0_observation(q0: Q0) -> None:
    leg = Leg(HostReport("x86_64", 9, None), "k", "os", "c" * 40, ())
    venue = next(iter(_EXPECTED.venues))
    record = gate.check(
        venue,
        _EXPECTED,
        "e" * 64,
        _IDENTITY,
        leg,
        q0["out"] / "observation.json",
        q0["out"] / "junit.xml",
    )
    assert record["problems"] and "preflight record unusable" in record["problems"][0]


def test_q0_collector_refuses_a_q2_preflight_record(q0: Q0) -> None:
    (q0["out"] / "observation.json").write_text(json.dumps(_record("e" * 64)))
    _completed_nothing(q0.observe())


# FQ0a-1: every hash agrees, but the retained binding.env names another run.
@pytest.mark.parametrize("key", _IDENTITY)
def test_q0_binding_verify_refuses_a_binding_env_of_another_run(q0: Q0, key: str) -> None:
    other = "2" * 64 if key == "INPUTS_SHA256" else "other"
    env = q0.binding_env(_sha(q0["install_ns"].read_bytes()), **{key: other})
    q0["binding_env"].write_bytes(env)
    q0["host_stage"].write_text(json.dumps({"binding_env_sha256": _sha(env)}))
    q0.observation()
    record = q0.observe()
    _completed_nothing(record)
    assert record["problems"] == [
        f"binding-verify: binding.env {key}={other!r} is not this run's {_IDENTITY[key]!r}"
    ]


# FQ0a-2: agreeing hashes over an install the evaluator refuses claim no completion.
def test_q0_bindings_over_a_failed_install_claim_no_completed_observation(q0: Q0) -> None:
    doc = _install_ns_doc()
    doc["install"]["namespace"]["dpkg_exit"] = 1
    q0["install_ns"].write_text(json.dumps(doc))
    env = q0.binding_env(_sha(q0["install_ns"].read_bytes()))
    q0["binding_env"].write_bytes(env)
    q0["host_stage"].write_text(json.dumps({"binding_env_sha256": _sha(env)}))
    q0.observation()
    record = q0.observe()
    _completed_nothing(record)
    assert record["problems"] == ["install-binding: install: dpkg exit 1 is not 0"]


# --- Host records (bindings_crossing_guest; reviewer F7, discriminating test 42) -------


def test_host_records_round_trip_every_binding_key() -> None:
    records = _records()
    env = gate.parse_binding_env(records.binding_env)
    assert list(env) == list(gate.BINDING_ENV_KEYS)
    assert env == _binding_values() | {
        "HOST_JSON_SHA256": _sha(records.host_json),
        "INSTALL_NS_SHA256": _sha(records.install_ns),
    }
    host = json.loads(records.host_json)
    assert host["INSTALL_NS_SHA256"] == env["INSTALL_NS_SHA256"]
    assert "binding_env_sha256" not in host
    assert json.loads(records.install_ns) == _install_ns_doc()
    assert gate.evaluate_install_ns(records.install_ns, _DEBS) == []
    assert json.loads(records.host_stage) == {
        "binding_env_sha256": _sha(records.binding_env),
        "sentinel_sha256": {"home": "5" * 64},
    }


def _without(key: str) -> dict[str, str]:
    return {k: v for k, v in _binding_values().items() if k != key}


@pytest.mark.parametrize(
    "values",
    [
        pytest.param(_without("CI_REF"), id="missing"),
        pytest.param(_binding_values() | {"EXTRA": "1"}, id="extra"),
        pytest.param(_binding_values() | {"INSTALL_NS_SHA256": "a" * 64}, id="derived-supplied"),
        pytest.param(_binding_values() | {"HOST_ENV_SHA256": "A" * 64}, id="uppercase-hash"),
        pytest.param(_binding_values() | {"CI_REF": ""}, id="empty"),
        pytest.param(_binding_values() | {"CI_REF": "a\nCI_HEAD=b"}, id="multi-line"),
    ],
)
def test_host_records_refuse_values_outside_the_schema(values: dict[str, str]) -> None:
    with pytest.raises(gate.Q0Error):
        _records(values=values)


def test_host_records_refuse_a_supplied_host_json_install_hash() -> None:
    with pytest.raises(gate.Q0Error, match="derived"):
        _records(host={"INSTALL_NS_SHA256": "a" * 64})


def _install_line(data: bytes) -> bytes:
    return next(line for line in data.splitlines(True) if line.startswith(b"INSTALL_NS_SHA256="))


@pytest.mark.parametrize(
    "mutate",
    [
        pytest.param(lambda d: d.replace(_install_line(d), b""), id="no-INSTALL_NS_SHA256"),
        pytest.param(lambda d: d + b"EXTRA=1\n", id="extra-key"),
        pytest.param(lambda d: d.replace(_install_line(d), _install_line(d).upper()), id="upper"),
        pytest.param(lambda d: d.replace(_install_line(d), b"INSTALL_NS_SHA256=abc\n"), id="short"),
    ],
)
def test_parse_binding_env_refuses_writer_output_altered(mutate: Callable[[bytes], bytes]) -> None:
    with pytest.raises(gate.Q0Error):
        gate.parse_binding_env(mutate(_records().binding_env))


def test_guest_env_names_are_exactly_the_schema_plus_the_fixed_variables() -> None:
    names = [*gate.BINDING_ENV_KEYS, *gate.FIXED_GUEST_ENV]
    assert gate.guest_env_problems(names) == []
    assert gate.guest_env_problems([n for n in names if n != "INSTALL_NS_SHA256"]) == [
        "guest environment lacks INSTALL_NS_SHA256"
    ]
    assert gate.guest_env_problems([*names, "GITHUB_TOKEN"]) == [
        "guest environment has GITHUB_TOKEN outside the allowlist"
    ]


def test_written_host_records_are_the_composed_bytes(tmp_path: Path) -> None:
    records = _records()
    names = ("install-ns.json", "host.json", "binding.env", "host-stage.json")
    paths = gate.HostRecords(*(tmp_path / name for name in names))
    gate.write_host_records(records, paths)
    assert [(tmp_path / name).read_bytes() for name in names] == [
        records.install_ns,
        records.host_json,
        records.binding_env,
        records.host_stage,
    ]


# --- Install boundary (guest_package_closure step 3) ----------------------------------


def _install_problems(doc: dict[str, Any]) -> list[str]:
    try:
        return gate.evaluate_install_ns(json.dumps(doc).encode(), _DEBS)
    except gate.Q0Error as exc:
        return [str(exc)]


def _ns(doc: dict[str, Any]) -> dict[str, Any]:
    return doc["install"]["namespace"]


def test_the_exact_expected_install_ns_passes() -> None:
    assert _install_problems(_install_ns_doc()) == []


# Discriminating test 37: every deviation from the step-3c boundary fails.
_BOUNDARY_MUTATIONS: dict[str, Callable[[dict[str, Any]], object]] = {
    "netns-of-host": lambda d: _ns(d).update(netns=_ns(d)["host_netns"]),
    "second-interface": lambda d: _ns(d).update(interfaces=["lo", "eth0"]),
    "fourth-env-name": lambda d: _ns(d)["environment"].update(HOME="/root"),
    "changed-env-value": lambda d: _ns(d)["environment"].update(LC_ALL="C.UTF-8"),
    "sentinel-in-env": lambda d: _ns(d)["environment"].update(A5_SENTINEL_ENV="s3nt"),
    "cap-line-missing": lambda d: _ns(d)["capabilities"].pop("CapAmb"),
    "cap-not-hex": lambda d: _ns(d)["capabilities"].update(CapEff="not-a-mask"),
    "wrapper-exit": lambda d: d["install"].update(wrapper_exit=1),
    "dpkg-exit": lambda d: _ns(d).update(dpkg_exit=2),
    "dpkg-never-ran": lambda d: _ns(d).update(dpkg_exit=None),
    "no-namespace-record": lambda d: d["install"].update(namespace=None),
    "deb-sha256-differs": lambda d: _ns(d)["debs"][1].update(sha256="0" * 64),
    "deb-order-differs": lambda d: _ns(d)["debs"].reverse(),
    "deb-missing": lambda d: _ns(d)["debs"].pop(),
    "self-test-absent": lambda d: d.pop("self_test"),
    "self-test-install-failed": lambda d: d["self_test"]["run"].update(wrapper_exit=1),
}


@pytest.mark.parametrize("mutate", _BOUNDARY_MUTATIONS.values(), ids=_BOUNDARY_MUTATIONS)
def test_install_boundary_evaluator_refuses(mutate: Callable[[dict[str, Any]], object]) -> None:
    doc = _install_ns_doc()
    mutate(doc)
    assert _install_problems(doc)


# Discriminating test 40: one tuple derives the setpriv argument and every mask judgement.
_LINUX_CAP_BITS = {
    "net_admin": 12,
    "sys_module": 16,
    "sys_rawio": 17,
    "sys_ptrace": 19,
    "sys_admin": 21,
    "bpf": 39,
}


def test_forbidden_caps_are_the_six_kernel_capabilities() -> None:
    assert dict(gate.FORBIDDEN_CAPS) == _LINUX_CAP_BITS


@pytest.mark.parametrize("cap_set", gate.CAP_SETS)
@pytest.mark.parametrize("cap", [name for name, _ in gate.FORBIDDEN_CAPS])
def test_each_forbidden_bit_in_each_set_is_refused(cap: str, cap_set: str) -> None:
    doc = _install_ns_doc()
    _ns(doc)["capabilities"] = _hexes(
        _CLEAN | {cap_set: _CLEAN[cap_set] | 1 << _LINUX_CAP_BITS[cap]}
    )
    assert _install_problems(doc) == [f"install: {cap_set} holds forbidden {[cap]}"]


def test_entry_argv_is_the_one_bounded_command(tmp_path: Path) -> None:
    argv = gate.install_argv(
        tmp_path / "gate.py", Path("/a5-guest/root"), "net:[1]", tmp_path / "ns.json", _DEBS
    )
    assert argv[: argv.index("/usr/bin/python3")] == [
        "sudo", "-n", "--", "/usr/bin/env", "-i",
        "PATH=/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL=C", "DEBIAN_FRONTEND=noninteractive",
        "/usr/bin/unshare", "--net", "--pid", "--kill-child", "--",
        "/usr/bin/setpriv", "--no-new-privs", "--inh-caps", "-all", "--ambient-caps", "-all",
        "--bounding-set", "-sys_admin,-net_admin,-sys_ptrace,-sys_module,-bpf,-sys_rawio", "--",
    ]  # fmt: skip
    assert argv[-2:] == [deb.file for deb in _DEBS]


# Discriminating test 38: the self-test must discriminate before the real install.
def _test(doc: dict[str, Any]) -> dict[str, Any]:
    return doc["self_test"]


_ALL = dict.fromkeys(gate.CAP_SETS, _FULL_CAPS)
_NETPROBE_MUTATIONS: dict[str, Callable[[dict[str, Any]], object]] = {
    "inside-connected": lambda d: _test(d).update(inside=_probe_text("connected", "unset", _CLEAN)),
    "inside-sentinel": lambda d: _test(d).update(inside=_probe_text("failed", "s3nt", _CLEAN)),
    **{
        f"inside-{cap_set}-forbidden": (
            lambda d, s=cap_set: _test(d).update(
                inside=_probe_text("failed", "unset", _CLEAN | {s: _FULL_CAPS})
            )
        )
        for cap_set in gate.CAP_SETS
    },
    "inside-absent": lambda d: _test(d).pop("inside"),
    "second-connection": lambda d: _test(d).update(accepted=2),
    "control-cannot-connect": lambda d: _test(d).update(
        control=_probe_text("failed", "s3nt", _ALL)
    ),
    "control-no-sentinel": lambda d: _test(d).update(
        control=_probe_text("connected", "unset", _ALL)
    ),
    "control-capbnd-clean": lambda d: _test(d).update(
        control=_probe_text("connected", "s3nt", _ALL | {"CapBnd": _CLEAN["CapBnd"]})
    ),
}


@pytest.mark.parametrize("mutate", _NETPROBE_MUTATIONS.values(), ids=_NETPROBE_MUTATIONS)
def test_netprobe_self_test_refuses(mutate: Callable[[dict[str, Any]], object]) -> None:
    doc = _install_ns_doc()
    mutate(doc)
    assert any(p.startswith("self-test") for p in _install_problems(doc))


def test_netprobe_postinst_is_the_control_probe_writing_into_the_root() -> None:
    package = gate.netprobe_package("192.0.2.7", 4711)
    probe = gate.netprobe_script("192.0.2.7", 4711)
    assert "/dev/tcp/192.0.2.7/4711" in probe and "${A5_SENTINEL_ENV-unset}" in probe
    assert package["DEBIAN/postinst"] == probe.replace(
        "#!/bin/bash\n", f"#!/bin/bash\nexec > /{gate.NETPROBE_OUT} 2>&1\n"
    )
    assert "Package: a5-netprobe\n" in package["DEBIAN/control"]


def test_netprobe_script_reports_its_own_boundary(tmp_path: Path) -> None:
    script = tmp_path / "probe"
    script.write_text(gate.netprobe_script("127.0.0.1", 9))  # discard port: nothing listens
    env = {"PATH": os.environ["PATH"], "A5_SENTINEL_ENV": "s3nt"}
    out = subprocess.run(["bash", str(script)], env=env, capture_output=True, text=True).stdout
    net, sentinel, masks = gate._probe(out, "control")  # pyright: ignore[reportPrivateUsage]
    assert (net, sentinel, sorted(masks)) == ("failed", "s3nt", sorted(gate.CAP_SETS))


# Discriminating test 39: no un-namespaced install path exists.
def test_failed_wrapper_never_reaches_dpkg(tmp_path: Path) -> None:
    record = tmp_path / "ns.json"
    argv = gate.install_argv(tmp_path / "gate.py", tmp_path / "root", "net:[1]", record, _DEBS)
    rejects = [sys.executable, "-c", "raise SystemExit(1)", *argv]  # setpriv rejecting an option
    run = gate.install_run(rejects, record, os.environ)
    assert run == {"wrapper_exit": 1, "namespace": None} and not record.exists()
    assert gate.run_problems(run, _DEBS)


def test_install_run_refuses_a_namespace_record_from_before_the_run(tmp_path: Path) -> None:
    record = tmp_path / "ns.json"
    record.write_text(json.dumps(_install_run_record(_DEBS)["namespace"]))
    with pytest.raises(gate.Q0Error, match="not fresh"):
        gate.install_run([sys.executable, "-c", "pass"], record, os.environ)


def _root(tmp_path: Path) -> Path:
    cache = tmp_path / "root" / gate.DEB_CACHE
    cache.mkdir(parents=True)
    for deb in _DEBS:
        (cache / deb.file).write_bytes(deb.file.encode())
    return tmp_path / "root"


def test_ns_install_outside_the_boundary_never_spawns_dpkg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_dpkg(*args: object, **kwargs: object) -> None:
        raise AssertionError("dpkg spawned outside the boundary")

    monkeypatch.setattr(gate.subprocess, "run", no_dpkg)
    evidence = tmp_path / "ns.json"
    files = [deb.file for deb in _DEBS]
    assert gate.ns_install(_root(tmp_path), "net:[1]", evidence, files) == 1
    assert json.loads(evidence.read_text())["dpkg_exit"] is None


def test_ns_install_inside_the_boundary_runs_dpkg_once_in_list_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def dpkg(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(argv, 0)

    for name in list(os.environ):
        monkeypatch.delenv(name)
    for name, value in gate.INSTALL_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.setattr(gate.os, "readlink", lambda path: "net:[2]")
    monkeypatch.setattr(gate.socket, "if_nameindex", lambda: [(1, "lo")])
    monkeypatch.setattr(gate, "_proc_caps", lambda: _hexes(_CLEAN))
    monkeypatch.setattr(gate.subprocess, "run", dpkg)
    root, evidence = _root(tmp_path), tmp_path / "ns.json"
    assert gate.ns_install(root, "net:[1]", evidence, [deb.file for deb in _DEBS]) == 0
    assert calls == [
        (
            ["chroot", str(root), "/usr/bin/dpkg", "-i"]
            + [f"/{gate.DEB_CACHE}/{deb.file}" for deb in _DEBS],
            {"env": gate.INSTALL_ENV, "close_fds": True, "check": False},
        )
    ]
    actual = [gate.Deb(d.file, len(d.file), _sha(d.file.encode())) for d in _DEBS]
    run = {"wrapper_exit": 0, "namespace": json.loads(evidence.read_text())}
    assert gate.run_problems(run, actual) == []


def test_ns_install_exposes_no_option_that_skips_the_boundary(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit):
        main(["guest-stage", "ns-install", "--help"])
    options = {word for word in capsys.readouterr().out.split() if word.startswith("-")}
    assert options == {"-h,", "--help", "--expectations", "--root", "--host-netns", "--evidence"}


# --- Stage manifest and pool delivery: discriminating tests 10, 27, 32 and the 38 stage item


def _stage(tmp_path: Path) -> tuple[Path, Path]:
    """A clean staged root and /a5 tree, with mountpoints the walk must not enter."""
    root, a5 = tmp_path / "root", tmp_path / "a5"
    for d in (root / "etc", root / "proc" / "1", a5 / "src" / "pkg", a5 / "venv" / "lib"):
        d.mkdir(parents=True)
    (root / "etc" / "passwd").write_text("root:x:0:0\n")
    (root / "proc" / "1" / "status").write_text("mounted, never staged\n")
    (root / "bin").symlink_to("usr/bin")
    (a5 / "src" / "pkg" / "__init__.py").write_text("")
    (a5 / "venv" / "lib" / "a5.pth").write_text("# comment\n../../src\n")
    (a5 / "venv" / "python").symlink_to("/a5/src/pkg")
    (a5 / "meta").mkdir()
    for name in ("binding.env", "host.json", "host-env-origin.json", *gate.GUEST_SCRIPTS):
        (a5 / "meta" / name).write_text(name)
    return root, a5


_MOUNTS = ("/proc",)


def _stage_scan(tmp_path: Path) -> gate.Stage:
    return gate.scan_stage(tmp_path / "root", tmp_path / "a5", _MOUNTS)


def test_stage_manifest_records_the_stage_by_guest_path_and_judges_it_clean(
    tmp_path: Path,
) -> None:
    root, a5 = _stage(tmp_path)
    assert gate.guest_stage_verify(root, a5, _MOUNTS) == []
    written = json.loads((a5 / "meta" / "stage-manifest.json").read_bytes())
    assert sorted(written) == [
        "/",
        "/a5",
        "/a5/src",
        "/a5/src/pkg",
        "/a5/src/pkg/__init__.py",
        "/a5/venv",
        "/a5/venv/lib",
        "/a5/venv/lib/a5.pth",
        "/a5/venv/python",
        "/bin",
        "/etc",
        "/etc/passwd",
    ]
    status = (root / "etc" / "passwd").stat()
    assert written["/etc/passwd"] == {
        "type": "file",
        "mode": status.st_mode & 0o7777,
        "uid": status.st_uid,
        "gid": status.st_gid,
        "size": 11,
        "sha256": _sha(b"root:x:0:0\n"),
    }
    assert written["/bin"]["target"] == "usr/bin"
    # The guest's walk of the same tree gives the same bytes: equality needs no mapping.
    assert gate.manifest_diff(_stage_scan(tmp_path).manifest, written) == []


@pytest.mark.parametrize(
    ("change", "path"),
    [
        (lambda r, a: (r / "etc" / "passwd").write_text("root:x:0:1\n"), "/etc/passwd"),
        (lambda r, a: (r / "etc" / "passwd").chmod(0o600), "/etc/passwd"),
        (lambda r, a: ((r / "bin").unlink(), (r / "bin").symlink_to("usr/sbin")), "/bin"),
        (lambda r, a: (a / "src" / "extra.py").write_text(""), "/a5/src/extra.py"),
        (lambda r, a: (a / "src" / "pkg" / "__init__.py").unlink(), "/a5/src/pkg/__init__.py"),
    ],
)
def test_manifest_diff_names_one_changed_file_mode_or_symlink_target(
    tmp_path: Path, change: Callable[[Path, Path], object], path: str
) -> None:
    root, a5 = _stage(tmp_path)
    before = _stage_scan(tmp_path).manifest
    change(root, a5)
    assert gate.manifest_diff(before, _stage_scan(tmp_path).manifest) == [path]


def test_stage_refuses_a_fifo_or_socket(tmp_path: Path) -> None:
    root, a5 = _stage(tmp_path)
    os.mkfifo(root / "etc" / "pipe")
    with socket.socket(socket.AF_UNIX) as server:
        server.bind(str(a5 / "src" / "sock"))
        problems = gate.stage_problems(_stage_scan(tmp_path))
    assert [p.split(" is ")[0] for p in problems] == ["/etc/pipe", "/a5/src/sock"]


@pytest.mark.parametrize(
    "target", ["/etc/passwd", "../../etc", "../venv/../..", "/a5/escape", "loop"]
)
def test_stage_refuses_a_symlink_under_a5_that_leaves_a5(tmp_path: Path, target: str) -> None:
    _, a5 = _stage(tmp_path)
    (a5 / "escape").symlink_to("/etc")  # judged on its own as well
    (a5 / "src" / "link").symlink_to(target)
    (a5 / "src" / "loop").symlink_to("loop")
    problems = gate.stage_problems(_stage_scan(tmp_path))
    assert any(p.startswith("symlink /a5/src/link ") for p in problems), problems
    assert any(p.startswith("symlink /a5/escape ") for p in problems)


def test_stage_accepts_symlinks_that_stay_in_a5_and_root_links_anywhere(tmp_path: Path) -> None:
    root, a5 = _stage(tmp_path)
    (a5 / "src" / "inside").symlink_to("../venv/python/__init__.py")
    (root / "etc" / "abs").symlink_to("/usr/lib/os-release")
    assert gate.stage_problems(_stage_scan(tmp_path)) == []


@pytest.mark.parametrize("line", ["/usr/lib/python3/dist-packages", "../..", "import os"])
def test_stage_refuses_a_pth_line_outside_a5_src(tmp_path: Path, line: str) -> None:
    _, a5 = _stage(tmp_path)
    (a5 / "venv" / "lib" / "a5.pth").write_text(f"../../src\n{line}\n")
    problems = gate.stage_problems(_stage_scan(tmp_path))
    assert problems == [
        f"/a5/venv/lib/a5.pth line {line!r} resolves to "
        f"{gate.resolve(str(PurePosixPath('/a5/venv/lib') / line), {})}, outside /a5/src"
    ]


def test_stage_refuses_an_a5_meta_entry_beyond_the_four(tmp_path: Path) -> None:
    root, a5 = _stage(tmp_path)
    (a5 / "meta" / "outcomes.json").write_text("{}")
    assert gate.guest_stage_verify(root, a5, _MOUNTS) == [
        f"/a5/meta/outcomes.json is not one of {list(gate.STAGE_META)}"
    ]


def test_stage_refuses_a_deb_cache_path_left_in_the_stage(tmp_path: Path) -> None:
    root, _ = _stage(tmp_path)
    (root / gate.DEB_CACHE).mkdir(parents=True)
    assert gate.stage_problems(_stage_scan(tmp_path)) == [
        "/var/cache/a5-debs is left in the stage (step 3e)"
    ]


def _pool(tmp_path: Path) -> tuple[Path, list[gate.Deb]]:
    pool = tmp_path / "pool"
    pool.mkdir()
    for deb in _DEBS:
        (pool / deb.file).write_bytes(deb.file.encode())
    return pool, [gate.Deb(d.file, len(d.file), _sha(d.file.encode())) for d in _DEBS]


def test_deliver_debs_copies_an_exactly_verified_pool_into_the_root(tmp_path: Path) -> None:
    pool, debs = _pool(tmp_path)
    gate.deliver_debs(pool, tmp_path / "root", debs)
    cache = tmp_path / "root" / gate.DEB_CACHE
    assert sorted(p.name for p in cache.iterdir()) == [d.file for d in debs]
    assert all((cache / d.file).read_bytes() == d.file.encode() for d in debs)


@pytest.mark.parametrize(
    ("change", "name"),
    [
        (lambda pool: (pool / _DEBS[0].file).write_bytes(b"git_1_amd64.deX"), _DEBS[0].file),
        (lambda pool: (pool / _DEBS[1].file).write_bytes(b"short"), _DEBS[1].file),
        (lambda pool: (pool / "extra_1_all.deb").write_bytes(b"x"), "extra_1_all.deb"),
        (lambda pool: (pool / _DEBS[0].file).unlink(), _DEBS[0].file),
    ],
)
def test_deliver_debs_refuses_a_mismatched_extra_or_missing_file(
    tmp_path: Path, change: Callable[[Path], object], name: str
) -> None:
    pool, debs = _pool(tmp_path)
    change(pool)
    with pytest.raises(gate.Q0Error, match=f"pool {name}:"):
        gate.deliver_debs(pool, tmp_path / "root", debs)
    assert not (tmp_path / "root").exists()


# --- Bootstrap, closure and kernel: discriminating tests 16, 32 (closure items) and 35 -----


def _gpg(home: Path, *args: str) -> str:
    return subprocess.run(
        ["gpg", "--batch", "--homedir", str(home), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _signer(tmp_path: Path, name: str) -> tuple[Path, str, Path]:
    """A throwaway key: its homedir, primary fingerprint and a keyring holding only it."""
    home = tmp_path / name
    home.mkdir(mode=0o700)
    _gpg(home, "--passphrase", "", "--quick-gen-key", f"{name} <{name}@invalid>", "ed25519")
    fpr = next(
        line.split(":")[9]
        for line in _gpg(home, "--with-colons", "-K").splitlines()
        if line.startswith("fpr:")
    )
    keyring = tmp_path / f"{name}.gpg"
    keyring.write_bytes(
        subprocess.run(
            ["gpg", "--batch", "--homedir", str(home), "--export", fpr],
            check=True,
            capture_output=True,
        ).stdout
    )
    return home, fpr, keyring


def _gpgv(argv: list[str]) -> tuple[str, int]:
    run = subprocess.run(argv, capture_output=True, text=True, check=False)
    return run.stdout, run.returncode


def test_gpgv_judgement_requires_the_pinned_signer_over_unaltered_bytes(tmp_path: Path) -> None:
    home, fpr, keyring = _signer(tmp_path, "pinned")
    _, other, _ = _signer(tmp_path, "other")
    data = tmp_path / "SHA256SUMS"
    data.write_text(f"{'a' * 64} *ubuntu-base-26.04-base-amd64.tar.gz\n")
    _gpg(home, "--detach-sign", "-o", str(tmp_path / "SHA256SUMS.gpg"), str(data))
    status, code = _gpgv(gate.gpgv_argv(keyring, tmp_path / "SHA256SUMS.gpg", data))
    assert gate.signature_problems(status, code, fpr) == []
    assert gate.signature_problems(status, code, other) == [
        f"no valid signature by pinned {other} (signers {[fpr]})"
    ]
    data.write_text(f"{'b' * 64} *ubuntu-base-26.04-base-amd64.tar.gz\n")
    status, code = _gpgv(gate.gpgv_argv(keyring, tmp_path / "SHA256SUMS.gpg", data))
    assert code != 0
    assert gate.signature_problems(status, code, fpr) == [
        f"gpgv exited {code}",
        f"no valid signature by pinned {fpr} (signers [])",
    ]


def test_clearsigned_list_yields_only_its_signed_entries(tmp_path: Path) -> None:
    home, fpr, keyring = _signer(tmp_path, "autosigner")
    body = tmp_path / "sums"
    body.write_text(f"{'c' * 64}  {gate.KERNEL_TARBALL}\n")
    _gpg(home, "--clearsign", "-o", str(tmp_path / "sha256sums.asc"), str(body))
    signed = tmp_path / "sha256sums.asc"
    # Text prepended outside the signature is not signed content and never read.
    signed.write_text(f"{'d' * 64}  {gate.KERNEL_TARBALL}\n" + signed.read_text())
    status, code = _gpgv(gate.gpgv_argv(keyring, "--output", tmp_path / "out", signed))
    assert gate.signature_problems(status, code, fpr) == []
    assert gate.sums_entry((tmp_path / "out").read_text(), gate.KERNEL_TARBALL) == "c" * 64


_TARBALL = "ubuntu-base-26.04-base-amd64.tar.gz"
_SUMS = f"{'1' * 64} *{_TARBALL}\n{'2' * 64} *ubuntu-base-26.04-base-arm64.tar.gz\n".encode()


def _base(**change: str) -> gate.BaseInput:
    pins = {"tarball_sha256": "1" * 64, "sha256sums_sha256": _sha(_SUMS)} | change
    return gate.BaseInput("https://x/", _TARBALL, signing_key="A" * 40, **pins)


def test_base_tarball_is_its_signed_entry_and_the_pin() -> None:
    assert gate.base_problems(_SUMS, "1" * 64, _base()) == []


@pytest.mark.parametrize(
    ("tarball", "base", "problem"),
    [
        ("3" * 64, _base(), f"{_TARBALL} values differ"),
        ("1" * 64, _base(tarball_sha256="3" * 64), f"{_TARBALL} values differ"),
        ("1" * 64, _base(sha256sums_sha256="4" * 64), "SHA256SUMS sha256"),
    ],
)
def test_base_refuses_a_tarball_or_list_off_the_pin(
    tarball: str, base: gate.BaseInput, problem: str
) -> None:
    assert [p for p in gate.base_problems(_SUMS, tarball, base) if p.startswith(problem)]


def test_base_refuses_a_list_without_exactly_one_tarball_entry() -> None:
    with pytest.raises(gate.Q0Error, match="2 times, not once"):
        gate.base_problems(_SUMS + f"{'1' * 64} *{_TARBALL}\n".encode(), "1" * 64, _base())


def test_base_packages_are_every_installed_status_entry() -> None:
    listing = "base-files 14 amd64 ii \nlibc6 2.42-1 amd64 ii \n"
    assert gate.base_packages(listing) == (
        gate.Package("base-files", "14", "amd64"),
        gate.Package("libc6", "2.42-1", "amd64"),
    )
    assert gate.dpkg_query_argv(Path("/r"))[:2] == ["dpkg-query", "--admindir=/r/var/lib/dpkg"]


@pytest.mark.parametrize("listing", ["base-files 14 amd64 ii \nold 1 amd64 rc \n", "", "x 1 ii \n"])
def test_base_packages_refuse_an_entry_not_installed(listing: str) -> None:
    with pytest.raises(gate.Q0Error, match="not 'ii'"):
        gate.base_packages(listing)


def test_apt_private_reads_only_the_pinned_snapshot_and_base_status(tmp_path: Path) -> None:
    archive = gate.ArchiveInput("20261101T000000Z", "resolute", ("main", "universe"), "F" * 40)
    files = gate.apt_private(tmp_path / "apt", tmp_path / "root", tmp_path / "k.gpg", archive)
    assert files["sources.list"] == (
        f"deb [arch=amd64 signed-by={tmp_path}/k.gpg] "
        "https://snapshot.ubuntu.com/ubuntu/20261101T000000Z resolute main universe\n"
    )
    conf = files["apt.conf"]
    assert f'Dir::State::status "{tmp_path}/root/var/lib/dpkg/status";' in conf
    assert f'Dir::State::lists "{tmp_path}/apt/lists";' in conf
    assert 'APT::Architecture "amd64";' in conf
    assert 'Acquire::ForceHash "SHA256";' in conf
    host = {'Dir::Etc::parts "/dev/null";', 'Dir::Etc::main "/dev/null";'}
    assert host <= set(conf.splitlines())
    assert all(
        f'"{tmp_path}/apt/' in line
        for line in conf.splitlines()
        if "::Etc::" in line and line not in host
    )
    argv = gate.apt_argv(tmp_path, *gate.CLOSURE_COMMAND)
    assert argv[:3] == ["env", f"APT_CONFIG={tmp_path}/apt.conf", "apt-get"]
    assert "-c" not in argv
    assert argv[-4:] == [
        "--download-only",
        "--print-uris",
        "install",
        "git",
    ]


_SNAP = "https://snapshot.ubuntu.com/ubuntu/20261101T000000Z/"
_INDEX = """Package: git
Version: 1:2.51.0-1
Architecture: amd64
Description: fast scm
 continuation: line
Filename: pool/main/g/git/git_2.51.0-1_amd64.deb
Size: 10
SHA256: {git}

Package: liberror-perl
Version: 0.17-1
Architecture: all
Filename: pool/main/libe/liberror-perl/liberror-perl_0.17-1_all.deb
Size: 20
SHA256: {perl}
""".format(git="d" * 64, perl="e" * 64)
_URIS = (
    "Reading package lists...\nThe following NEW packages will be installed:\n  git\n"
    f"'{_SNAP}pool/main/libe/liberror-perl/liberror-perl_0.17-1_all.deb' "
    f"liberror-perl_0.17-1_all.deb 20 SHA256:{'e' * 64}\n"
    f"'{_SNAP}pool/main/g/git/git_2.51.0-1_amd64.deb' git_1%3a2.51.0-1_amd64.deb 10 "
    f"SHA256:{'d' * 64}\n"
)
_BASE_SET = (gate.Package("libc6", "2.42-1", "amd64"),)


def test_closure_is_each_added_package_as_the_verified_index_records_it() -> None:
    added = gate.closure(_URIS, gate.packages_index(_INDEX), "20261101T000000Z", _BASE_SET)
    assert [(p.package.name, p.package.version, p.filename) for p in added] == [
        ("liberror-perl", "0.17-1", "pool/main/libe/liberror-perl/liberror-perl_0.17-1_all.deb"),
        ("git", "1:2.51.0-1", "pool/main/g/git/git_2.51.0-1_amd64.deb"),
    ]
    assert added[1].deb == gate.Deb("git_2.51.0-1_amd64.deb", 10, "d" * 64)


@pytest.mark.parametrize(
    ("uris", "base", "match"),
    [
        (_URIS.replace(_SNAP, "https://archive.ubuntu.com/ubuntu/"), _BASE_SET, "pinned snapshot"),
        (_URIS.replace(" 20 SHA256", " 21 SHA256"), _BASE_SET, "disagrees with the verified"),
        (_URIS.replace("libe/liberror-perl/", "libe/x/"), _BASE_SET, "disagrees with the verified"),
        (_URIS.split("'")[0], _BASE_SET, "must add"),
        (_URIS, (gate.Package("liberror-perl", "0.16", "all"),), "no base"),
    ],
)
def test_closure_refuses_an_unpinned_unverified_or_base_overlapping_list(
    uris: str, base: tuple[gate.Package, ...], match: str
) -> None:
    with pytest.raises(gate.Q0Error, match=match):
        gate.closure(uris, gate.packages_index(_INDEX), "20261101T000000Z", base)


def test_packages_index_refuses_a_stanza_without_its_hash() -> None:
    with pytest.raises(gate.Q0Error, match=r"'git' lacks \['SHA256'\]"):
        gate.packages_index(_INDEX.replace(f"SHA256: {'d' * 64}\n", ""))


def test_kernel_tarball_must_equal_its_autosigned_entry_and_the_pin() -> None:
    sums = f"{'5' * 64}  {gate.KERNEL_TARBALL}\n"
    assert gate.tarball_problems(sums, gate.KERNEL_TARBALL, "5" * 64, "5" * 64) == []
    for pin, tarball in (("6" * 64, "5" * 64), ("5" * 64, "6" * 64)):
        assert gate.tarball_problems(sums, gate.KERNEL_TARBALL, pin, tarball) == [
            f"{gate.KERNEL_TARBALL} values differ: "
            f"{ {'pin': pin, 'sums': '5' * 64, 'tarball': tarball} }"
        ]


def test_kernel_steps_fetch_over_https_and_build_the_pinned_configuration(tmp_path: Path) -> None:
    fetch = gate.kernel_fetch(tmp_path)
    assert [argv[-1] for argv in fetch] == [
        f"{gate.KERNEL_URL}linux-7.3.1.tar.xz",
        f"{gate.KERNEL_URL}linux-7.3.1.tar.sign",
        f"{gate.KERNEL_URL}sha256sums.asc",
    ]
    assert all(argv[:5] == ["curl", "-fsSL", "--proto", "=https", "-o"] for argv in fetch)
    build = gate.kernel_build(tmp_path / "linux", gate.GUEST_KERNEL_CONFIG, 4)
    assert [argv[-1] for argv in build] == [
        "defconfig",
        "--kconfig",
        str(gate.GUEST_KERNEL_CONFIG),
        "olddefconfig",
        "bzImage",
    ]
    assert all("LOCALVERSION=-a5guest" in argv for argv in build if argv[0] == "make")


def test_run_steps_stops_at_the_first_failure(tmp_path: Path) -> None:
    steps = [["true"], ["false"], ["touch", "after"]]
    with pytest.raises(gate.Q0Error, match=r"\['false'\] failed"):
        gate.run_steps(steps, tmp_path, 30)
    assert not (tmp_path / "after").exists()


def test_run_steps_fails_at_the_deadline_with_no_later_step(tmp_path: Path) -> None:
    with pytest.raises(gate.Q0Error, match="timed out"):
        gate.run_steps([["sleep", "5"], ["touch", "after"]], tmp_path, 0.5)
    assert not (tmp_path / "after").exists()


# Stage 5 part 2b(i): the Q0 guest observation (discriminating tests 31, 36, 44).
_MOUNTINFO = (
    "22 1 0:20 / / rw,relatime - ext4 /dev/vda rw\n"
    "30 22 0:31 / /a5 ro,relatime - virtiofs a5 ro\n"
    "31 22 0:32 / /out\\040dir rw shared:1 - 9p out rw,trans=virtio\n"
)
_GIT = gate.Package("git", "1:2.51", "amd64")
_FACTS = gate.HostFacts(
    base_packages=(gate.Package("bash", "5.2", "amd64"),),
    closure=(gate.PoolPackage(_GIT, "pool/main/g/git/git_2.51_amd64.deb", 10, "a" * 64),),
    host_packages={"virtme-ng": "1.40-2"},
    root_manifests=({"/x": {"type": "dir"}}, {"/x": {"type": "file"}}),
    vng_help="usage: vng",
    gcc_version="gcc (Ubuntu 15.2.0-1) 15.2.0",
    guest_scripts={gate.GUEST_RUN: "b" * 64, gate.Q0_PROBE: "c" * 64},
)
_HOST_FACTS: dict[str, Any] = asdict(_FACTS)
_GUEST = gate.GuestFacts(("a5", "bin", "out"), _MOUNTINFO, (), (_GIT,), _GUEST_IDENTITY)


def _guest_inputs(**host: Any) -> tuple[bytes, bytes, dict[str, str]]:
    records = _records(host={**_HOST_FACTS, **host})
    env = dict(gate.parse_binding_env(records.binding_env)) | gate.FIXED_GUEST_ENV
    return records.binding_env, records.host_json, env


def _observation(**environ: str) -> bytes:
    binding_env, host_json, env = _guest_inputs()
    return gate.observation(
        parse_inputs(_RAW["inputs"]), binding_env, host_json, env | environ, _GUEST
    )


def test_q0_shares_are_the_host_backed_mounts() -> None:
    assert gate.shares(_MOUNTINFO) == [
        {"mountpoint": "/a5", "fstype": "virtiofs", "source": "a5", "options": "ro,relatime ro"},
        {
            "mountpoint": "/out dir",
            "fstype": "9p",
            "source": "out",
            "options": "rw rw,trans=virtio",
        },
    ]


def test_q0_observation_records_bindings_facts_and_no_verdict() -> None:
    binding_env, _, env = _guest_inputs()
    data = _observation()
    record = json.loads(data)
    assert "verdict" not in record and "outcomes" not in record
    assert record["INPUTS_SHA256"] == parse_inputs(_RAW["inputs"]).sha256
    assert record["binding_env_sha256"] == _sha(binding_env)
    assert record["INSTALL_NS_SHA256"] == env["INSTALL_NS_SHA256"]
    assert record["root_manifest_diff"] == ["/x"]
    assert record["packages"] == [{"name": "git", "version": "1:2.51", "architecture": "amd64"}]
    assert record["guest_identity"] == json.loads(json.dumps(asdict(_GUEST_IDENTITY)))
    assert gate.parse_guest_identity(record["guest_identity"]) == _GUEST_IDENTITY
    # The host collector accepts what the guest writes, bound to the same run.
    parsed = gate.parse_observation(data)
    assert parsed.identity == {key: record[key] for key in gate.Q0_IDENTITY}
    assert {key: env[key] for key in gate.GUEST_BOUND} == {k: record[k] for k in gate.GUEST_BOUND}


def test_q0_host_facts_reach_the_observation_as_the_host_measured_them() -> None:
    record = json.loads(_observation())
    assert record["base_packages"] == [{"name": "bash", "version": "5.2", "architecture": "amd64"}]
    assert record["closure"] == [
        {
            "package": {"name": "git", "version": "1:2.51", "architecture": "amd64"},
            "filename": "pool/main/g/git/git_2.51_amd64.deb",
            "size": 10,
            "sha256": "a" * 64,
        }
    ]
    assert record["host_packages"] == {"virtme-ng": "1.40-2"}
    assert record["root_manifests"] == [{"/x": {"type": "dir"}}, {"/x": {"type": "file"}}]
    assert record["vng_help"] == "usage: vng"


# Test 44: the record is of the parsed bytes; no variable and no host field names it.
def test_q0_binding_env_record_ignores_an_environment_claim() -> None:
    assert _observation(binding_env_sha256="0" * 64) == _observation()
    assert "binding_env_sha256" not in gate.BINDING_ENV_KEYS
    host = json.loads(_guest_inputs()[1])
    assert not [key for key in host if "binding" in key.lower()]


@pytest.mark.parametrize(
    ("host", "environ"),
    [
        *(({fact: None}, {}) for fact in gate.HOST_FACTS),
        ({"root_manifests": [{}]}, {}),
        ({}, {"INSTALL_NS_SHA256": ""}),
        ({}, {"GITHUB_RUN_ID": ""}),
    ],
)
def test_q0_observation_refuses_missing_facts(
    host: dict[str, Any], environ: dict[str, str]
) -> None:
    binding_env, host_json, env = _guest_inputs()
    raw = {**_HOST_FACTS, **host}
    host_json = json.dumps({k: v for k, v in raw.items() if v is not None}).encode()
    with pytest.raises(gate.Q0Error):
        gate.observation(
            parse_inputs(_RAW["inputs"]), binding_env, host_json, env | environ, _GUEST
        )


def _observe_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, document: Any, name: str) -> int:
    binding_env, host_json, env = _guest_inputs()
    meta = tmp_path / "meta"
    meta.mkdir(exist_ok=True)
    (meta / "binding.env").write_bytes(binding_env)
    (meta / "host.json").write_bytes(host_json)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(gate, "guest_facts", lambda: _GUEST)
    doc = tmp_path / f"{name}.json"
    doc.write_text(json.dumps(document))
    return gate.main(
        ["observe", "--expectations", str(doc), "--meta", str(meta), "--out", str(tmp_path / name)]
    )


# Tests 31 and 36: observe parses only `inputs`, writes only observation.json.
def test_q0_observe_never_reads_expectations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    conflicting = {**_RAW, "venues": {"conflict": True}, "expectations": {"bogus": [1]}}
    assert _observe_cli(tmp_path, monkeypatch, _RAW, "a") == 0
    assert _observe_cli(tmp_path, monkeypatch, conflicting, "b") == 0
    assert os.listdir(tmp_path / "a") == ["observation.json"]
    assert (tmp_path / "a" / "observation.json").read_bytes() == (
        tmp_path / "b" / "observation.json"
    ).read_bytes()
    without_inputs = {key: value for key, value in _RAW.items() if key != "inputs"}
    assert _observe_cli(tmp_path, monkeypatch, without_inputs, "c") == 2
    assert not (tmp_path / "c").exists()


# Test 31: an observation.json is refused where check expects JUnit outcomes.
def test_q2_check_refuses_an_observation_as_outcomes(tmp_path: Path) -> None:
    observation = tmp_path / "observation.json"
    observation.write_bytes(_observation())
    leg = Leg(HostReport("x86_64", 9, None), "k", "os", "c" * 40, ())
    venue = next(iter(_EXPECTED.venues))
    preflight_record = tmp_path / "preflight.json"
    preflight_record.write_text(json.dumps(_record("e" * 64)))
    record = gate.check(venue, _EXPECTED, "e" * 64, _IDENTITY, leg, preflight_record, observation)
    assert any("junit" in problem.lower() for problem in record["problems"]), record["problems"]


def test_route_source_is_the_hosts_non_loopback_address() -> None:
    route = "192.0.2.1 via 10.0.2.2 dev enp0s1 src 10.0.2.15 uid 1000 \n    cache \n"
    assert gate.route_source(route) == "10.0.2.15"
    for refused in ("192.0.2.1 dev lo src 127.0.0.1 uid 1000", "unreachable 192.0.2.1"):
        with pytest.raises(gate.Q0Error, match="non-loopback"):
            gate.route_source(refused)


def _self_test_without_namespace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Step 3g run for real except dpkg-deb (absent here) and the sudo namespace entry.

    The stand-in entry runs the postinst with no namespace at all, so a correct
    self-test must report the boundary as crossed.
    """
    root = tmp_path / "fresh-root"
    root.mkdir()

    def build(steps: list[list[str]], cwd: Path, timeout: float) -> None:
        Path(steps[0][-1]).write_bytes(Path(steps[0][-2], "DEBIAN", "postinst").read_bytes())

    def entry(gate_path: Path, at: Path, netns: str, record: Path, debs: Any) -> list[str]:
        deb = at / gate.DEB_CACHE / debs[0].file
        ns = _install_run_record(tuple(debs))["namespace"]
        write = f"import json,sys; open(sys.argv[1],'w').write(json.dumps({ns!r}))"
        # The postinst body minus its absolute redirect, its output landing in the root.
        run = f'tail -n +3 "$1" | bash > "$5/{gate.NETPROBE_OUT}" && "$2" -c "$3" "$4"'
        return ["sh", "-c", run, "-", str(deb), sys.executable, write, str(record), str(at)]

    monkeypatch.setattr(gate, "run_steps", build)
    monkeypatch.setattr(gate, "install_argv", entry)
    return gate.self_test(tmp_path / "gate.py", root, "net:[1]", tmp_path, "s3nt")


def test_self_test_without_a_namespace_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    test = _self_test_without_namespace(tmp_path, monkeypatch)
    problems = gate.netprobe_problems(test)
    assert "inside net=connected" in problems and "inside sentinel='s3nt'" in problems
    assert "listener accepted 2 connections, not 1" in problems
    assert not any(p.startswith("non-discriminating control") for p in problems)
    assert test["deb"]["file"] == "a5-netprobe_1_all.deb"


def test_guest_install_removes_the_delivered_pool_even_after_a_failed_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pool, root = tmp_path / "pool", tmp_path / "root"
    pool.mkdir()
    (pool / "git.deb").write_bytes(b"deb")
    debs = [gate.Deb("git.deb", 3, hashlib.sha256(b"deb").hexdigest())]

    def reject(*_: object) -> list[str]:
        return [sys.executable, "-c", "raise SystemExit(1)"]

    monkeypatch.setattr(gate, "install_argv", reject)
    record = tmp_path / "ns.json"
    run = gate.guest_install(tmp_path / "gate.py", root, "net:[1]", pool, debs, record)
    assert run == {"wrapper_exit": 1, "namespace": None}
    assert root.is_dir() and not (root / gate.DEB_CACHE).exists()


# --- Q0 bootstrap orchestration: steps 1, 2 and the 3g extraction lifecycle ----------


def test_fresh_base_is_discarded_by_root_even_when_its_user_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ran: list[list[str]] = []
    monkeypatch.setattr(gate, "run_steps", lambda steps, *_: ran.extend(map(list, steps)))
    tarball, root = tmp_path / "base.tar.gz", tmp_path / "base"
    with pytest.raises(RuntimeError, match="self-test"), gate.fresh_base(tarball, root) as fresh:
        assert fresh == root and root.is_dir()
        raise RuntimeError("self-test")
    assert ran == [gate.extract_argv(tarball, root), gate.discard_argv(root)]
    assert ran[1][:5] == ["sudo", "-n", "--", "rm", "-rf"] and ran[1][-1] == str(root)


def _signed_base(tmp_path: Path, tarball: bytes) -> tuple[Path, gate.BaseInput]:
    home, fpr, keyring = _signer(tmp_path, "cdimage")
    name = "ubuntu-base-26.04-base-amd64.tar.gz"
    pin = hashlib.sha256(b"base").hexdigest()
    sums = tmp_path / "SHA256SUMS"
    sums.write_text(f"{pin} *{name}\n")
    _gpg(home, "--detach-sign", "-o", str(tmp_path / "SHA256SUMS.gpg"), str(sums))
    (tmp_path / name).write_bytes(tarball)
    sums_sha256 = hashlib.sha256(sums.read_bytes()).hexdigest()
    return keyring, gate.BaseInput("https://cdimage.invalid/", name, pin, sums_sha256, fpr)


def test_verified_base_requires_the_pinned_signer_and_the_pinned_tarball(tmp_path: Path) -> None:
    keyring, base = _signed_base(tmp_path, b"base")
    assert gate.verified_base(tmp_path, keyring, base) == tmp_path / base.tarball
    with pytest.raises(gate.Q0Error, match="no valid signature by pinned"):
        gate.verified_base(tmp_path, keyring, replace(base, signing_key="F" * 40))
    (tmp_path / base.tarball).write_bytes(b"other")
    with pytest.raises(gate.Q0Error, match=base.tarball):
        gate.verified_base(tmp_path, keyring, base)


def _kernel_tarball(tmp_path: Path, content: str) -> Path:
    """An xz'd source tree named like the pinned tarball, from an uncompressed `.tar`."""
    tree = tmp_path / "tree" / content
    (tree / gate.KERNEL_SOURCE).mkdir(parents=True)
    (tree / gate.KERNEL_SOURCE / "Makefile").write_text(content)
    tar = tree / "linux.tar"
    subprocess.run(["tar", "-cf", str(tar), "-C", str(tree), gate.KERNEL_SOURCE], check=True)
    return tar


def _signed_kernel(tmp_path: Path) -> tuple[Path, Path, Path, gate.KernelInput]:
    """The fetched kernel files in `tmp_path/work`, signed by two throwaway pinned keys."""
    auto_home, auto_fpr, autosigner = _signer(tmp_path, "autosigner")
    dev_home, dev_fpr, developer = _signer(tmp_path, "developer")
    work = tmp_path / "work"
    work.mkdir()
    tar = _kernel_tarball(tmp_path, "kernel")
    _gpg(dev_home, "--detach-sign", "-o", str(work / "linux-7.3.1.tar.sign"), str(tar))
    xz = subprocess.run(["xz", "-c", str(tar)], check=True, capture_output=True).stdout
    (work / gate.KERNEL_TARBALL).write_bytes(xz)
    sums = tmp_path / "sums"
    sums.write_text(f"{_sha(xz)}  {gate.KERNEL_TARBALL}\n")
    _gpg(auto_home, "--clearsign", "-o", str(work / "sha256sums.asc"), str(sums))
    pins = gate.KernelInput(
        _sha(xz), auto_fpr, dev_fpr, _sha(gate.GUEST_KERNEL_CONFIG.read_bytes())
    )
    return work, autosigner, developer, pins


def test_verified_kernel_requires_both_pinned_signers_and_both_pins(tmp_path: Path) -> None:
    work, autosigner, developer, pins = _signed_kernel(tmp_path)

    def verify(kernel: gate.KernelInput) -> Path:
        (work / "sha256sums").unlink(missing_ok=True)
        return gate.verified_kernel(work, autosigner, developer, kernel, gate.GUEST_KERNEL_CONFIG)

    assert verify(pins) == work / gate.KERNEL_TARBALL
    for change in ({"autosigner_key": "F" * 40}, {"developer_key": "F" * 40}):
        with pytest.raises(gate.Q0Error, match=f"no valid signature by pinned {'F' * 40}"):
            verify(replace(pins, **change))
    with pytest.raises(gate.Q0Error, match=f"{gate.KERNEL_TARBALL} values differ"):
        verify(replace(pins, tarball_sha256="7" * 64))
    with pytest.raises(gate.Q0Error, match=r"kernel fragment sha256 \w+ is not the pinned"):
        verify(replace(pins, config_sha256="7" * 64))
    # Another tree under the same name: the developer signature over the stream fails too.
    other = _kernel_tarball(tmp_path, "other")
    xz = subprocess.run(["xz", "-c", str(other)], check=True, capture_output=True).stdout
    (work / gate.KERNEL_TARBALL).write_bytes(xz)
    with pytest.raises(gate.Q0Error, match=f"no valid signature by pinned {pins.developer_key}"):
        verify(pins)


def test_kernel_record_binds_the_build_hashes_and_refuses_a_modular_config(
    tmp_path: Path,
) -> None:
    config = b"CONFIG_SECURITY=y\n# CONFIG_MODULES is not set\n"
    record = gate.kernel_record(tmp_path, "5" * 64, config, b"image", "gcc (GCC) 15.2.0\nCopyright")
    assert record == gate.GuestKernel(
        tmp_path, "5" * 64, _sha(config), _sha(b"image"), "gcc (GCC) 15.2.0"
    )
    assert set(record.bindings()) == {
        "GUEST_SOURCE_SHA256",
        "GUEST_CONFIG_SHA256",
        "GUEST_BZIMAGE_SHA256",
    }
    assert set(record.bindings()) < set(gate.BINDING_ENV_KEYS)
    with pytest.raises(gate.Q0Error, match=re.escape("guest .config sets 'CONFIG_MODULES=y'")):
        gate.kernel_record(tmp_path, "5" * 64, b"CONFIG_MODULES=y\n", b"image", "gcc")


def test_guest_kernel_builds_only_the_verified_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fetched, autosigner, developer, pins = _signed_kernel(tmp_path)
    home = gate.imported_keys(tmp_path / "home", (autosigner, developer))
    work = tmp_path / "build"
    work.mkdir()
    config = "# CONFIG_MODULES is not set\n"
    monkeypatch.setattr(
        gate,
        "kernel_fetch",
        lambda target: [["cp", str(path), str(target)] for path in sorted(fetched.iterdir())],
    )
    built: list[Path] = []

    def build(source: Path, fragment: Path, jobs: int) -> list[list[str]]:
        built.append(source)
        assert (source / "Makefile").read_text() == "kernel" and jobs == 3
        script = f"mkdir -p arch/x86/boot && printf image > {gate.BZIMAGE}"
        script += f" && printf '{config}' > .config"
        return [["sh", "-c", script]]

    monkeypatch.setattr(gate, "kernel_build", build)
    record = gate.guest_kernel(work, home, pins, 3)
    source = work / gate.KERNEL_SOURCE
    assert built == [source]
    assert record.bzimage == source / gate.BZIMAGE
    assert (record.source_sha256, record.config_sha256, record.bzimage_sha256) == (
        pins.tarball_sha256,
        _sha(config.encode()),
        _sha(b"image"),
    )
    assert record.gcc_version.startswith("gcc")
    other = tmp_path / "rebuild"
    other.mkdir()
    with pytest.raises(gate.Q0Error, match="no valid signature by pinned"):
        gate.guest_kernel(other, home, replace(pins, developer_key=pins.autosigner_key), 3)
    assert built == [source]


def _recorder(path: Path, log: Path, step: str | None) -> None:
    """An executable that records its cwd, argv and environment, then exits as told."""
    name = repr(step) if step else "sys.argv[2]"
    path.write_text(
        f"#!{sys.executable}\nimport json, os, pathlib, sys\n"
        f"step, log = {name}, pathlib.Path({str(log)!r})\n"
        "seen = [os.getcwd(), sys.argv[1:], dict(os.environ)]\n"
        "(log / f'{step}.seen').write_text(json.dumps(seen))\n"
        "sys.exit(int((log / f'{step}.exit').read_text()))\n"
    )
    path.chmod(0o755)


class _GuestScript:
    """One generated guest script, run as the guest would against recording executables."""

    def __init__(self, tmp_path: Path, name: str) -> None:
        self.a5, self.out, self.log = tmp_path / "a5", tmp_path / "out", tmp_path / "log"
        for path in (self.a5 / "meta", self.a5 / "src", self.a5 / "venv" / "bin", self.log):
            path.mkdir(parents=True)
        self.script = self.a5 / "meta" / name
        self.script.write_text(self.relocate(gate.GUEST_SCRIPTS[name]))
        self.values = {key: "7" * 64 for key in gate.BINDING_ENV_KEYS} | {"CI_PARENTS": "p1 p2"}
        # No newline after the last line: it is still read.
        (self.a5 / "meta" / "binding.env").write_text(
            "\n".join(f"{k}={v}" for k, v in self.values.items())
        )
        _recorder(self.a5 / "venv" / "bin" / "python", self.log, None)
        _recorder(self.a5 / "venv" / "bin" / "pytest", self.log, "pytest")

    def relocate(self, text: str) -> str:
        return text.replace("/a5/", f"{self.a5}/").replace("/out", str(self.out))

    def run(self, steps: Sequence[str], exits: dict[str, int]) -> int:
        shutil.rmtree(self.out, ignore_errors=True)
        for step in steps:
            (self.log / f"{step}.exit").write_text(str(exits.get(step, 0)))
        host = {"PATH": os.environ["PATH"], "GITHUB_TOKEN": "host-only"}
        return subprocess.run(["/bin/sh", str(self.script)], env=host, check=False).returncode

    def bound_argv(self, step: str) -> list[str]:
        """The step's argv, once its cwd and exact environment are the bound ones."""
        cwd, argv, env = json.loads((self.log / f"{step}.seen").read_text())
        assert cwd == str(self.a5 / "src") and gate.guest_env_problems(env) == []
        fixed = {key: self.relocate(value) for key, value in gate.FIXED_GUEST_ENV.items()}
        assert env == self.values | fixed
        return argv


def test_guest_run_gives_each_step_exactly_the_bound_environment(tmp_path: Path) -> None:
    guest = _GuestScript(tmp_path, gate.GUEST_RUN)
    out = guest.out
    steps = [name for name, _, _ in gate.GUEST_STEPS]

    def run(exits: dict[str, int]) -> int:
        return guest.run(steps, exits)

    # A failed suite is recorded and does not stop the outcome check after it.
    assert run({"pytest": 1}) == 0
    assert {step: (out / f"{step}.rc").read_text() for step in steps} == {
        "isolation": "0\n",
        "env-origin": "0\n",
        "preflight": "0\n",
        "pytest": "1\n",
        "check": "0\n",
    }
    assert (out / "pytest.log").is_file() and (out / "home").is_dir() and (out / "tmp").is_dir()
    argvs = [guest.bound_argv(step) for step in steps]
    assert argvs[-1][:2] == ["tools/a5_kernel_ci_gate.py", "check"]
    # A failed isolation or env-origin check stops the run before anything measured runs.
    for gating in ("isolation", "env-origin"):
        assert run({gating: 3}) == 1
        assert (out / f"{gating}.rc").read_text() == "3\n"
        assert not (out / "preflight.rc").exists()


def test_q0_probe_runs_only_observe_and_only_behind_the_isolation_check(
    tmp_path: Path,
) -> None:
    guest = _GuestScript(tmp_path, gate.Q0_PROBE)
    steps = [name for name, _, _ in gate.Q0_STEPS]
    assert guest.run(steps, {}) == 0
    assert {step: (guest.out / f"{step}.rc").read_text() for step in steps} == {
        "isolation": "0\n",
        "observe": "0\n",
    }
    assert [guest.bound_argv(step)[:2] for step in steps] == [
        ["tools/a5_kernel_ci_gate.py", "isolation"],
        ["tools/a5_kernel_ci_gate.py", "observe"],
    ]
    assert guest.bound_argv("observe")[2:] == [
        "--meta",
        f"{guest.a5}/meta",
        "--out",
        str(guest.out),
    ]
    # Q0 measures no suite.
    assert not (guest.log / "pytest.seen").exists()
    assert guest.run(steps, {"isolation": 3}) == 1
    assert (guest.out / "isolation.rc").read_text() == "3\n"
    assert not (guest.out / "observe.rc").exists()
    assert guest.run(steps, {"observe": 2}) == 1


def test_src_config_holds_only_core_and_branch_settings_and_the_file_origin() -> None:
    workspace = Path("/w")
    clean = (
        "core.bare=false\nbranch.main.remote=origin\nremote.origin.url=file:///w\n"
        "remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*\n"
    )
    assert gate.src_config_problems(clean, workspace) == []
    leaked = clean + "http.https://github.com/.extraheader=AUTHORIZATION: basic x\n"
    assert gate.src_config_problems(leaked, workspace) == [
        "/a5/src/.git/config holds http.https://github.com/.extraheader"
    ]
    assert gate.src_config_problems(clean.replace("file:///w", "https://x/r"), workspace) == [
        "/a5/src/.git/config lacks remote.origin.url=file:///w",
        "/a5/src/.git/config holds remote.origin.url",
    ]


def test_stage_a5_detaches_the_tested_commit_and_builds_from_the_pins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace, bin_dir, log = tmp_path / "ws", tmp_path / "bin", tmp_path / "uv.log"
    bin_dir.mkdir()
    git = ["git", "-C", str(workspace), "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q", str(workspace)], check=True)
    (workspace / "f").write_text("tested")
    subprocess.run([*git, "add", "f"], check=True)
    subprocess.run([*git, "commit", "-qm", "tested"], check=True)
    tested = subprocess.run(
        [*git, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    (workspace / "f").write_text("later")
    subprocess.run([*git, "commit", "-qam", "later"], check=True)
    inputs = parse_inputs(_RAW["inputs"])
    (bin_dir / "uv").write_text(
        f"#!{sys.executable}\nimport json, os, sys\n"
        f"if sys.argv[1:] == ['--version']:\n    sys.exit(print('uv {inputs.uv_version} (x)'))\n"
        # Python's own PEP 538 locale coercion sets LC_CTYPE; the real uv is not Python.
        "env = {k: v for k, v in os.environ.items() if k != 'LC_CTYPE'}\n"
        f"open({str(log)!r}, 'a').write(json.dumps([sys.argv[1:], env]) + '\\n')\n"
    )
    (bin_dir / "uv").chmod(0o755)
    monkeypatch.setenv("PATH", f"{bin_dir}:{os.environ['PATH']}")
    a5, cache = tmp_path / "a5", tmp_path / "cache"
    a5.mkdir()
    gate.stage_a5(a5, workspace, tested, cache, inputs)
    head = ["git", "-C", str(a5 / "src"), "rev-parse", "HEAD"]
    assert subprocess.run(head, check=True, capture_output=True, text=True).stdout.strip() == tested
    assert (a5 / "src" / "f").read_text() == "tested"
    for name, text in gate.GUEST_SCRIPTS.items():
        assert (a5 / "meta" / name).read_text() == text
    install = {
        "PATH": "/usr/bin:/bin",
        "UV_PYTHON_INSTALL_DIR": str(a5 / "python"),
        "UV_CACHE_DIR": str(cache),
    }
    assert [json.loads(line) for line in log.read_text().splitlines()] == [
        [["python", "install", inputs.cpython], install],
        [
            ["sync", "--locked", "--all-packages", "--directory", str(a5 / "src")],
            install
            | {
                "UV_PROJECT_ENVIRONMENT": str(a5 / "venv"),
                "UV_PYTHON_PREFERENCE": "only-managed",
                "UV_PYTHON_DOWNLOADS": "never",
                "UV_LINK_MODE": "copy",
            },
        ],
    ]
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(gate.Q0Error, match=r"uv \['.+'\] is not the pinned 0\.0\.1"):
        gate.stage_a5(other, workspace, tested, cache, replace(inputs, uv_version="0.0.1"))
    assert list(other.iterdir()) == []


_CPYTHON = parse_inputs(_RAW["inputs"]).cpython
_SITE = str(gate.site_packages(gate.A5, _CPYTHON))
_ORIGIN = gate.EnvOrigin(
    executable="/a5/venv/bin/python",
    prefix="/a5/venv",
    executable_realpath=f"/a5/python/cpython-{_CPYTHON}/bin/python3",
    base_prefix_realpath=f"/a5/python/cpython-{_CPYTHON}",
    version=_CPYTHON,
    sys_path=("/a5/src/tools", f"/a5/python/cpython-{_CPYTHON}/lib", _SITE, "/a5/src/core/src"),
    user_site=False,
    pyvenv_home=f"/a5/python/cpython-{_CPYTHON}/bin",
    pth=(
        gate.Pth(f"{_SITE}/_editable_impl_core.pth", "core", ("/a5/src/core/src",)),
        gate.Pth(f"{_SITE}/a1_coverage.pth", "coverage", ()),
    ),
    links=(("/a5/venv/bin/python", f"/a5/python/cpython-{_CPYTHON}/bin/python3"),),
    distributions=(gate.Distribution("core", "0.0.0", _SITE, "1" * 64),),
    sources=(("core", "/a5/src/core/src/core/__init__.py"),),
    test_tools=(("pytest", f"{_SITE}/pytest/__init__.py"),),
    pytest_shebang="#!/a5/venv/bin/python",
    git="/usr/bin/git",
)
_ELSEWHERE = "/home/runner/.venv"


def test_env_origin_admits_only_the_staged_tree_at_the_pinned_cpython() -> None:
    assert gate.env_origin_problems(_ORIGIN, gate.A5, _CPYTHON) == []
    stray = gate.Pth(f"{_SITE}/stray.pth", None, ())
    escapes = {
        "executable": f"{_ELSEWHERE}/bin/python",
        "prefix": _ELSEWHERE,
        "executable_realpath": "/usr/bin/python3",
        "base_prefix_realpath": "/usr",
        "version": "3.12.0",
        "sys_path": (*_ORIGIN.sys_path, "/usr/lib/python3/dist-packages"),
        "user_site": True,
        "pyvenv_home": "/usr/bin",
        "pth": (*_ORIGIN.pth, stray),
        "links": (*_ORIGIN.links, ("/a5/python/lib/libssl.so", "/usr/lib/libssl.so")),
        "distributions": (
            *_ORIGIN.distributions,
            gate.Distribution("evil", "1", "/usr/lib/python3/dist-packages", "2" * 64),
        ),
        "sources": (("core", "/a5/src/tools/core.py"),),
        "test_tools": (("pytest", "/usr/lib/python3/dist-packages/pytest/__init__.py"),),
        "pytest_shebang": "#!/usr/bin/python3",
        "git": "/usr/local/bin/git",
    }
    for field, value in escapes.items():
        assert (
            len(gate.env_origin_problems(replace(_ORIGIN, **{field: value}), gate.A5, _CPYTHON))
            == 1
        ), field
    for field, value in {
        "user_site": None,
        "pth": (gate.Pth(f"{_SITE}/_editable_impl_core.pth", "core", ("/etc",)),),
        "distributions": (gate.Distribution("core", "0.0.0", _SITE, None),),
        "sources": (),
        "git": None,
    }.items():
        assert (
            len(gate.env_origin_problems(replace(_ORIGIN, **{field: value}), gate.A5, _CPYTHON))
            == 1
        ), field


def test_env_origin_measures_imports_pth_owners_and_tools_from_the_running_venv(
    tmp_path: Path,
) -> None:
    a5 = tmp_path / "a5"
    (a5 / "src").mkdir(parents=True)
    (a5 / "python").mkdir()
    (a5 / "venv").symlink_to(sys.prefix)
    (a5 / "src" / "pyproject.toml").write_text(
        '[tool.coverage.run]\nsource = ["a5_kernel_ci_gate"]\n'
    )
    origin = gate.measure_env_origin(a5)
    site_dir = os.path.realpath(next(Path(sys.prefix, "lib").glob("*/site-packages")))
    assert origin.executable == sys.executable and origin.version == sys.version.split()[0]
    # Every .pth of the locked venv is bytes some installed distribution's RECORD lists.
    assert origin.pth and all(pth.owner for pth in origin.pth)
    assert {pth.owner for pth in origin.pth if pth.path.endswith("a1_coverage.pth")} == {"coverage"}
    assert {dist.location for dist in origin.distributions} == {site_dir}
    assert all(dist.record_sha256 for dist in origin.distributions)
    assert origin.sources == (("a5_kernel_ci_gate", os.path.realpath(gate.__file__)),)
    assert dict(origin.test_tools)["pytest"] == os.path.realpath(pytest.__file__)
    assert origin.pytest_shebang == f"#!{sys.prefix}/bin/python"
    assert (str(a5 / "venv" / "bin" / "python"), os.path.realpath(sys.executable)) in origin.links
    problems = gate.env_origin_problems(origin, a5, _CPYTHON)
    assert f"coverage source a5_kernel_ci_gate imports from {origin.sources[0][1]}" in "\n".join(
        problems
    )
    (a5 / "python").rmdir()
    with pytest.raises(FileNotFoundError):
        gate.measure_env_origin(a5)


def test_env_origin_guest_record_must_equal_the_host_record_field_for_field(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gate, "measure_env_origin", lambda a5: _ORIGIN)
    without_expectations = {"inputs": _RAW["inputs"]}
    (doc := tmp_path / "inputs.json").write_text(json.dumps(without_expectations))
    host = tmp_path / "meta" / "host-env-origin.json"
    assert main(["env-origin", "--expectations", str(doc), "--out", str(host)]) == 0
    recorded = json.loads(host.read_text())
    assert recorded["verdict"] == "pass" and recorded["git"] == "/usr/bin/git"
    guest = tmp_path / "out" / "env-origin.json"
    argv = ["env-origin", "--expectations", str(doc), "--compare", str(host), "--out", str(guest)]
    assert main(argv) == 0
    host.write_text(json.dumps(recorded | {"git": "/usr/local/bin/git"}))
    assert main(argv) == 1
    assert json.loads(guest.read_text())["problems"] == [f"git differs from {host}"]
    host.unlink()
    assert main(argv) == 1


def test_pinned_keyring_holds_only_the_pinned_key_and_refuses_an_absent_one(
    tmp_path: Path,
) -> None:
    home, fpr, pinned_source = _signer(tmp_path, "pinned")
    other_home, other, other_source = _signer(tmp_path, "other")
    _gpg(home, "--passphrase", "", "--quick-add-key", fpr, "cv25519", "encr")
    subkey = [
        line.split(":")[9]
        for line in _gpg(home, "--with-colons", "-k").splitlines()
        if line.startswith("fpr:")
    ][1]
    pinned_source.write_bytes(
        subprocess.run(
            ["gpg", "--batch", "--homedir", str(home), "--export", fpr],
            check=True,
            capture_output=True,
        ).stdout
    )
    keys = gate.imported_keys(tmp_path / "keys", (pinned_source, other_source))
    keyring = gate.pinned_keyring(keys, fpr, tmp_path / "pinned-keyring.gpg")
    data = tmp_path / "data"
    data.write_text("signed\n")
    for name, signer_home in (("pinned.sig", home), ("other.sig", other_home)):
        _gpg(signer_home, "--detach-sign", "-o", str(tmp_path / name), str(data))
    status, code = _gpgv(gate.gpgv_argv(keyring, tmp_path / "pinned.sig", data))
    assert gate.signature_problems(status, code, fpr) == []
    status, code = _gpgv(gate.gpgv_argv(keyring, tmp_path / "other.sig", data))
    assert code != 0 and gate.signature_problems(status, code, other) != []
    # gpg exports the whole primary key for a subkey fingerprint, exit 0.
    with pytest.raises(gate.Q0Error, match=f"not only pinned {subkey}"):
        gate.pinned_keyring(keys, subkey, tmp_path / "subkey-keyring.gpg")
    with pytest.raises(gate.Q0Error, match="--show-keys"):
        gate.pinned_keyring(keys, "F" * 40, tmp_path / "absent-keyring.gpg")


def test_keyring_listing_must_name_only_the_pinned_primary_key() -> None:
    primary, subkey, extra = "A" * 40, "B" * 40, "C" * 40
    listing = f"pub:-:255:22:{primary[-16:]}:1::::::scSC:\nfpr:::::::::{primary}:\n"
    with_subkey = listing + f"sub:-:255:18:{subkey[-16:]}:1::::::e:\nfpr:::::::::{subkey}:\n"
    assert gate.keyring_problems(with_subkey, primary) == []
    assert gate.keyring_problems(with_subkey, subkey) == [
        f"keyring holds primary keys {[primary]}, not only pinned {subkey}"
    ]
    two = listing + f"pub:-:255:22:{extra[-16:]}:1::::::scSC:\nfpr:::::::::{extra}:\n"
    assert gate.keyring_problems(two, primary) != []
    assert gate.keyring_problems("", primary) != []


def test_resolve_closure_reads_every_verified_component_index_after_update(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    git, perl = _INDEX.split("\n\n")

    def apt(argv: list[str], cwd: Path) -> str:
        calls.append(argv[-1])
        if argv[-1] == "update":
            lists = cwd / "lists"
            (lists / "snap_dists_resolute_main_binary-amd64_Packages").write_text(git)
            (lists / "snap_dists_resolute_universe_binary-amd64_Packages").write_text(perl)
        return _URIS

    monkeypatch.setattr(gate, "_stdout", apt)
    archive = gate.ArchiveInput("20261101T000000Z", "resolute", ("main", "universe"), "A" * 40)
    added = gate.resolve_closure(
        tmp_path, tmp_path / "base", tmp_path / "k.gpg", archive, _BASE_SET
    )
    assert calls == ["update", "git"]
    assert added == gate.closure(_URIS, gate.packages_index(_INDEX), archive.snapshot_id, _BASE_SET)
    assert "Dir::State::status" in (tmp_path / "apt" / "apt.conf").read_text()


def _staging(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dpkg_exits: tuple[int, int] = (0, 0)
) -> tuple[gate.Bootstrap, list[str]]:
    """Extraction writes one base file; the fake entry writes its record and a dpkg log
    naming its own root, so the two stagings differ in exactly that path."""
    ran: list[str] = []

    def steps(argv: Sequence[Sequence[str]], *_: object) -> None:
        for step in map(list, argv):
            ran.append(step[0] if step[0] == "tar" else step[3])
            root = Path(step[-1])
            if step[0] == "tar":
                (root / "etc").mkdir()
                (root / "etc" / "os-release").write_text("ubuntu\n")
            else:
                shutil.rmtree(root)

    def entry(_: Path, root: Path, __: str, record: Path, debs: Sequence[gate.Deb]) -> list[str]:
        ns = _install_run_record(tuple(debs))["namespace"]
        exit_code = dpkg_exits[len([r for r in ran if r == "tar"]) - 1]
        write = (
            "import json,pathlib,sys; pathlib.Path(sys.argv[1]).write_text(sys.argv[3]);"
            "log=pathlib.Path(sys.argv[2],'var','log'); log.mkdir(parents=True);"
            "(log/'dpkg.log').write_text(sys.argv[2])"
        )
        doc = json.dumps(ns | {"dpkg_exit": exit_code})
        return [sys.executable, "-c", write, str(record), str(root), doc]

    monkeypatch.setattr(gate, "run_steps", steps)
    monkeypatch.setattr(gate, "install_argv", entry)
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "git_1_amd64.deb").write_bytes(b"git")
    git = gate.PoolPackage(
        gate.Package("git", "1", "amd64"), "pool/main/g/git/git_1_amd64.deb", 3, _sha(b"git")
    )
    boot = gate.Bootstrap(tmp_path / "base.tar.gz", _BASE_SET, (git,), pool, {}, tmp_path)
    (tmp_path / "work").mkdir()
    return boot, ran


def test_stage_twice_keeps_the_root_and_exposes_the_path_two_builds_disagree_on(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    boot, ran = _staging(tmp_path, monkeypatch)
    root, work = tmp_path / "root", tmp_path / "work"
    staged = gate.stage_twice(tmp_path / "gate.py", boot, root, work, "net:[1]")
    first, second = staged.manifests
    assert ran == ["tar", "tar", "rm"]
    assert gate.manifest_diff(first, second) == ["/var/log/dpkg.log"]
    assert first == gate.root_manifest(root) and "/etc/os-release" in first
    assert not any(path.startswith(f"/{gate.DEB_CACHE}") for path in first | second)
    assert not (work / "root-repeat").exists()
    assert staged.install["wrapper_exit"] == 0
    assert staged.install["namespace"] == json.loads((work / "install-ns-root.json").read_text())
    assert (work / "install-ns-repeat.json").is_file()


@pytest.mark.parametrize(("exits", "steps"), [((1, 0), ["tar"]), ((0, 1), ["tar", "tar", "rm"])])
def test_stage_twice_fails_closed_on_either_install_and_still_discards_the_repeat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exits: tuple[int, int], steps: list[str]
) -> None:
    boot, ran = _staging(tmp_path, monkeypatch, exits)
    with pytest.raises(gate.Q0Error, match="dpkg exit 1 is not 0"):
        gate.stage_twice(
            tmp_path / "gate.py",
            boot,
            tmp_path / "root",
            tmp_path / "work",
            "net:[1]",
        )
    assert ran == steps and not (tmp_path / "work" / "root-repeat").exists()


_JOB = {key: f"job-{key}" for key in gate.JOB_BINDINGS}
_VNG_HELP = "usage: vng [--run RUN] [--root ROOT] [--rodir RODIR] [--rwdir RWDIR]\n" + (
    "  [--cpus CPUS] [--memory MEMORY] [--exec EXEC] [--net NET]\n"
)


class _Host:
    """q0_host with every fetch, build and staging edge replaced by a recording fake."""

    def __init__(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, problems: Sequence[str] = ()
    ) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.inputs = parse_inputs(_RAW["inputs"])
        self.bases = {"HOME": str(tmp_path / "home"), "RUNNER_TEMP": str(tmp_path / "temp")}
        self.at = gate.HostLayout(
            tmp_path / "work",
            tmp_path / "root",
            tmp_path / "a5",
            tmp_path / "evidence",
            tmp_path / "workspace",
            tmp_path / "uv-cache",
        )
        for path in (self.at.work, self.at.a5, self.at.evidence):
            path.mkdir()
        doc = _install_ns_doc()
        manifests = ({"/x": {"type": "dir"}}, {"/x": {"type": "file"}})
        boot = gate.Bootstrap(
            tmp_path / "base.tar.gz", _BASE_SET, (), tmp_path / "pool", doc["self_test"], tmp_path
        )
        kernel = gate.GuestKernel(tmp_path / "bzImage", "1" * 64, "2" * 64, "3" * 64, "gcc 15")
        meta = self.at.a5 / "meta"

        def record(name: str, value: Any, result: Any = None) -> Any:
            self.calls.append((name, value))
            return result

        def stage_a5(a5: Path, workspace: Path, tested: str, cache: Path, inputs: Any) -> None:
            record("stage_a5", (a5, workspace, tested, cache))
            meta.mkdir()
            for name, text in gate.GUEST_SCRIPTS.items():
                (meta / name).write_text(text)

        def steps(argv: Any, cwd: Path, timeout: float) -> None:
            record("run_steps", (argv, cwd))
            # The sentinel steps run before stage_a5 makes meta; only env-origin writes there.
            if argv == [gate.host_env_origin_argv(self.at.a5)]:
                (meta / "host-env-origin.json").write_text('{"verdict": "pass"}')

        def verify(root: Path, a5: Path, mounts: Any) -> list[str]:
            (meta / "stage-manifest.json").write_text('{"/a5/src": {}}')
            return record("verify", (root, a5, tuple(mounts)), list(problems))

        stdout = {"dpkg-query": "virtme-ng 1.40-2 amd64 ii\n", "vng": _VNG_HELP}
        staged = gate.Staged(doc["install"], manifests)
        monkeypatch.setattr(gate, "bootstrap", lambda *a: record("bootstrap", a, boot))
        monkeypatch.setattr(gate, "stage_twice", lambda *a: record("stage_twice", a, staged))
        monkeypatch.setattr(gate, "guest_kernel", lambda *a: record("guest_kernel", a, kernel))
        monkeypatch.setattr(gate, "stage_a5", stage_a5)
        monkeypatch.setattr(gate, "run_steps", steps)
        monkeypatch.setattr(gate, "guest_stage_verify", verify)
        monkeypatch.setattr(
            gate, "_stdout", lambda argv, cwd: record("stdout", argv, stdout[argv[0]])
        )

    def run(self, environ: Mapping[str, str]) -> None:
        environ = self.bases | environ
        gate.q0_host(Path("gate.py"), self.inputs, environ, (Path("keys.asc"),), self.at)


def test_q0_host_writes_records_binding_the_stage_it_built(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _Host(tmp_path, monkeypatch)
    host.run(_JOB | {"UNRELATED": "x"})
    meta, evidence, at = host.at.a5 / "meta", host.at.evidence, host.at
    assert [name for name, _ in host.calls][:9] == [
        "stdout",
        "stdout",
        "run_steps",
        "bootstrap",
        "stage_twice",
        "guest_kernel",
        "stage_a5",
        "run_steps",
        "verify",
    ]
    calls = dict(host.calls)
    assert calls["guest_kernel"][:2] == (at.work / "kernel", tmp_path)
    assert calls["stage_a5"][2] == "job-CI_TESTED"
    assert calls["run_steps"] == ([gate.host_env_origin_argv(at.a5)], at.a5 / "src")
    assert calls["verify"] == (at.root, at.a5, ())
    env = gate.parse_binding_env((meta / "binding.env").read_bytes())
    assert {key: env[key] for key in gate.JOB_BINDINGS} == _JOB
    assert env["STAGE_MANIFEST_SHA256"] == _sha((meta / "stage-manifest.json").read_bytes())
    assert env["HOST_ENV_SHA256"] == _sha((meta / "host-env-origin.json").read_bytes())
    assert env["INSTALL_NS_SHA256"] == _sha((evidence / "install-ns.json").read_bytes())
    assert env["HOST_JSON_SHA256"] == _sha((meta / "host.json").read_bytes())
    assert env["GUEST_BZIMAGE_SHA256"] == "3" * 64
    assert env["BASE_ROOTFS_SHA256"] == host.inputs.base.tarball_sha256
    assert env["INPUTS_SHA256"] == host.inputs.sha256
    facts = json.loads((meta / "host.json").read_bytes())
    assert facts["host_packages"] == {"virtme-ng": "1.40-2"}
    assert facts["gcc_version"] == "gcc 15" and facts["vng_help"] == _VNG_HELP
    assert facts["guest_scripts"] == {
        gate.GUEST_RUN: _sha(gate.GUEST_RUN_SH.encode()),
        gate.Q0_PROBE: _sha(gate.Q0_PROBE_SH.encode()),
    }
    assert gate.evaluate_install_ns((evidence / "install-ns.json").read_bytes(), _DEBS) == []
    stage = json.loads((evidence / "host-stage.json").read_bytes())
    assert stage["binding_env_sha256"] == _sha((meta / "binding.env").read_bytes())
    # Every sentinel is planted before bootstrap, and only its digest is recorded, host side.
    (*writes, git), cwd = host.calls[2][1]
    sites = {
        "$HOME/.a5-sentinel": tmp_path / "home" / ".a5-sentinel",
        "$RUNNER_TEMP/a5-sentinel": tmp_path / "temp" / "a5-sentinel",
        "$GITHUB_WORKSPACE/a5-sentinel": at.workspace / "a5-sentinel",
        "$GITHUB_WORKSPACE/.git/a5-sentinel": at.workspace / ".git" / "a5-sentinel",
        **{site: Path(site) for site in gate.ROOT_SENTINELS},
    }
    planted = {argv[-1]: argv[-2] for argv in writes}
    assert cwd == at.work and sorted(planted) == sorted(str(path) for path in sites.values())
    assert git[:-1] == ["git", "-C", str(at.workspace), "config", "--local", "a5.sentinel"]
    values = {site: planted[str(path)] for site, path in sites.items()} | {
        gate.SENTINEL_GIT: git[-1],
        gate.SENTINEL_ENV: calls["bootstrap"][5],
    }
    assert len(set(values.values())) == len(gate.SENTINEL_SITES) == 9
    assert all(v.startswith(gate.SENTINEL_MARKER) and len(v) == 14 + 64 for v in values.values())
    assert stage["sentinel_sha256"] == {site: _sha(v.encode()) for site, v in values.items()}
    crossing = (meta / "binding.env").read_text() + (meta / "host.json").read_text()
    assert not [value for value in values.values() if value in crossing]
    # The root writer itself, run without sudo, writes exactly the value it is handed.
    at.workspace.mkdir()
    (workspace_write,) = [
        argv for argv in writes if argv[-1] == str(sites["$GITHUB_WORKSPACE/a5-sentinel"])
    ]
    assert workspace_write[:3] == ["sudo", "-n", "--"]
    subprocess.run(workspace_write[3:], check=True)
    assert (at.workspace / "a5-sentinel").read_text() == workspace_write[-2]


def test_the_tested_tree_never_holds_the_sentinel_marker_the_guest_scans_for() -> None:
    found = subprocess.run(
        ["git", "grep", "-lF", gate.SENTINEL_MARKER],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
    )
    assert (found.returncode, found.stdout) == (1, ""), found.stderr
    assert gate.SENTINEL_MARKER == "A5ISO" + "SENTINEL1"


_MARKED = gate.SENTINEL_MARKER + "f" * 64


_DIR = {"type": "dir", "mode": 0o755, "uid": 0, "gid": 0}
_FILE = {"type": "file", "mode": 0o644, "uid": 0, "gid": 0, "size": 1, "sha256": "1" * 64}
# The host manifest as q0_host writes it: /proc and /out are empty mountpoint dirs there.
_HOST_STAGE = {"/": _DIR, "/etc/x": _FILE, "/proc": _DIR, "/out": _DIR, "/a5": _DIR, "/a5/y": _FILE}
_GUEST_MOUNTINFO = (
    "22 1 0:20 / / ro,relatime - virtiofs ROOTFS ro\n"
    "23 22 0:21 / /proc rw - proc proc rw\n"
    "24 22 0:22 / /out rw - virtiofs out rw\n"
    "25 22 0:23 / /a5 ro - virtiofs a5 ro\n"
)
_GUEST_SEEN = {p: n for p, n in _HOST_STAGE.items() if p not in ("/proc", "/out")}


def _clean_facts() -> gate.IsolationFacts:
    names = [*gate.BINDING_ENV_KEYS, *gate.FIXED_GUEST_ENV]
    meta = json.dumps(_HOST_STAGE).encode()
    return gate.IsolationFacts(
        mountinfo=_GUEST_MOUNTINFO,
        environ={name: f"value-of-{name}" for name in names}
        | {"STAGE_MANIFEST_SHA256": _sha(meta)},
        interfaces=("lo",),
        present=(),
        write_errno={"/": errno.EROFS, "/a5": errno.EROFS},
        marker_hits={},
        unreadable={},
        stage_meta=meta,
        stage_seen=_GUEST_SEEN,
    )


def test_stage_mounts_stop_at_every_guest_mount_but_the_walk_tops() -> None:
    nested = _GUEST_MOUNTINFO + "26 25 0:24 / /a5/src ro - tmpfs t ro\n"
    assert gate.stage_mounts(nested) == ("/out", "/proc")


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        pytest.param(
            lambda f: replace(f, stage_seen={**f.stage_seen, "/etc/x": _FILE | {"size": 2}}),
            "guest stage differs from the host manifest at /etc/x",
            id="mutated-file",
        ),
        pytest.param(
            lambda f: replace(f, stage_seen={**f.stage_seen, "/a5/z": _FILE}),
            "guest stage differs from the host manifest at /a5/z",
            id="added-path",
        ),
        pytest.param(
            lambda f: replace(
                f, stage_seen={k: v for k, v in f.stage_seen.items() if k != "/a5/y"}
            ),
            "guest stage differs from the host manifest at /a5/y",
            id="missing-path",
        ),
        pytest.param(
            lambda f: replace(
                f,
                mountinfo=f.mountinfo + "26 25 0:24 / /a5/y ro - 9p y ro\n",
                stage_seen={**f.stage_seen, "/a5/y": _DIR},
            ),
            "guest stage differs from the host manifest at /a5/y",
            id="mount-inside-a5-is-not-projected-away",
        ),
        pytest.param(
            lambda f: replace(f, stage_meta=f.stage_meta + b" "),
            "/a5/meta/stage-manifest.json sha256 {} is not STAGE_MANIFEST_SHA256 {!r}",
            id="meta-not-the-named-manifest",
        ),
    ],
)
def test_isolation_problems_refuse_a_guest_stage_other_than_the_named_manifest(
    change: Callable[[gate.IsolationFacts], gate.IsolationFacts], problem: str
) -> None:
    clean = _clean_facts()
    facts = change(clean)
    expected = problem.format(_sha(facts.stage_meta), clean.environ["STAGE_MANIFEST_SHA256"])
    assert gate.isolation_problems(facts) == [expected]


def test_isolation_problems_pass_a_guest_that_reaches_nothing() -> None:
    assert gate.isolation_problems(_clean_facts()) == []


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        pytest.param(
            lambda f: replace(f, environ={**f.environ, "GITHUB_TOKEN": "t"}),
            "guest environment has GITHUB_TOKEN outside the allowlist",
            id="env-name",
        ),
        pytest.param(
            lambda f: replace(f, environ={**f.environ, "CI_REF": "x" + _MARKED}),
            "guest environment CI_REF holds the sentinel marker",
            id="env-value",
        ),
        pytest.param(
            lambda f: replace(f, interfaces=("eth0", "lo")),
            "guest has network interface eth0",
            id="interface",
        ),
        pytest.param(
            lambda f: replace(f, present=("/etc/a5-sentinel",)),
            "guest sees host path /etc/a5-sentinel",
            id="host-path",
        ),
        pytest.param(
            lambda f: replace(f, write_errno={**f.write_errno, "/a5": 0}),
            "/a5 write probe errno 0 is not EROFS",
            id="writable",
        ),
        pytest.param(
            lambda f: replace(f, write_errno={**f.write_errno, "/": errno.EACCES}),
            "/ write probe errno EACCES is not EROFS",
            id="refused-not-read-only",
        ),
        pytest.param(
            lambda f: replace(f, marker_hits={"/a5/src/x": "a" * 64}),
            f"/a5/src/x holds the sentinel marker (sha256 {'a' * 64})",
            id="marker-hit",
        ),
        pytest.param(
            lambda f: replace(f, unreadable={"/x": "Permission denied"}),
            "/x unreadable: Permission denied",
            id="unreadable",
        ),
    ],
)
def test_isolation_problems_fail_closed_on_each_reach(
    change: Callable[[gate.IsolationFacts], gate.IsolationFacts], problem: str
) -> None:
    assert gate.isolation_problems(change(_clean_facts())) == [problem]


def test_write_targets_always_hold_a5_and_never_out() -> None:
    lines = [
        "22 1 0:20 / / ro,relatime - virtiofs ROOTFS ro",
        "23 22 0:21 / /out rw,relatime - virtiofs out rw",
        "24 22 0:22 / /proc rw - proc proc rw",
    ]
    assert gate.write_targets("\n".join(lines)) == ["/", "/a5"]
    lines.append("25 22 0:23 / /a5 ro - 9p a5 ro")
    assert gate.write_targets("\n".join(lines)) == ["/", "/a5"]


def test_write_probe_reports_a_created_file_and_leaves_nothing(tmp_path: Path) -> None:
    assert gate._write_errno(str(tmp_path)) == 0  # pyright: ignore[reportPrivateUsage]
    assert list(tmp_path.iterdir()) == []
    assert gate._write_errno(str(tmp_path / "absent")) == errno.ENOENT  # pyright: ignore[reportPrivateUsage]


def test_marker_scan_finds_a_split_marker_and_follows_no_link(tmp_path: Path) -> None:
    marker = gate.SENTINEL_MARKER.encode()
    share, outside = tmp_path / "share", tmp_path / "outside"
    (share / "sub").mkdir(parents=True)
    outside.mkdir()
    split = b"x" * (gate._SCAN_CHUNK - 5) + marker + b"tail"  # pyright: ignore[reportPrivateUsage]
    (share / "split").write_bytes(split)
    (share / "clean").write_bytes(b"x" * 10)
    (share / "sub" / "deep").write_bytes(marker)
    (outside / "leak").write_bytes(marker)
    (share / "file-link").symlink_to(outside / "leak")
    (share / "dir-link").symlink_to(outside)
    hits, unreadable = gate._marker_scan([str(share)], marker)  # pyright: ignore[reportPrivateUsage]
    assert hits == {str(share / "split"): _sha(split), str(share / "sub" / "deep"): _sha(marker)}
    assert unreadable == {}


@pytest.mark.skipif(os.geteuid() == 0, reason="root reads a mode-000 file")
def test_marker_scan_records_what_it_cannot_read(tmp_path: Path) -> None:
    (secret := tmp_path / "secret").write_bytes(b"x")
    secret.chmod(0)
    (closed := tmp_path / "closed").mkdir()
    closed.chmod(0)
    try:
        hits, unreadable = gate._marker_scan([str(tmp_path)], b"marker")  # pyright: ignore[reportPrivateUsage]
    finally:
        closed.chmod(0o700)
    assert hits == {}
    assert unreadable == {str(closed): "Permission denied", str(secret): "Permission denied"}


@pytest.mark.parametrize(
    ("extra", "code", "problems"),
    [
        pytest.param({}, 0, [], id="isolated"),
        pytest.param(
            {"GITHUB_TOKEN": _MARKED},
            1,
            [
                "guest environment has GITHUB_TOKEN outside the allowlist",
                "guest environment GITHUB_TOKEN holds the sentinel marker",
            ],
            id="leaked",
        ),
    ],
)
def test_isolation_command_records_env_names_only_before_its_verdict_exits(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    extra: dict[str, str],
    code: int,
    problems: list[str],
) -> None:
    facts = _clean_facts()
    facts = replace(facts, environ={**facts.environ, **extra})
    monkeypatch.setattr(gate, "isolation_facts", lambda: facts)
    # An inputs-only file: isolation runs before any Q1 section is parsed.
    (doc := tmp_path / "inputs.json").write_text(json.dumps({"inputs": _RAW["inputs"]}))
    out = tmp_path / "out" / "isolation.json"
    assert main(["isolation", "--expectations", str(doc), "--out", str(out)]) == code
    record = json.loads(out.read_bytes())
    assert record["problems"] == problems
    assert record["verdict"] == ("fail" if problems else "pass")
    assert record["environ"] == sorted(facts.environ)
    assert record["shares"] == gate.shares(facts.mountinfo)
    assert record["stage_meta_sha256"] == _sha(facts.stage_meta)
    assert "stage_seen" not in record and "/etc/x" not in out.read_text()
    assert "value-of-" not in out.read_text() and gate.SENTINEL_MARKER not in out.read_text()


@pytest.mark.parametrize("base", ["HOME", "RUNNER_TEMP"])
def test_q0_host_refuses_an_unset_sentinel_base_before_planting_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, base: str
) -> None:
    host = _Host(tmp_path, monkeypatch)
    with pytest.raises(gate.Q0Error, match=rf"lacks \['{base}'\]"):
        host.run(_JOB | {base: ""})
    assert host.calls == []


def test_launcher_problems_pass_the_pinned_vng_with_every_launch_option() -> None:
    assert gate.launcher_problems({"virtme-ng": "1.40-2"}, _VNG_HELP, "1.40-2") == []
    assert gate.launcher_problems({"virtme-ng": "1.42-1"}, _VNG_HELP, "1.40-2") == [
        "host virtme-ng '1.42-1' is not 1.40-2"
    ]
    assert gate.launcher_problems({}, _VNG_HELP, "1.40-2") == ["host virtme-ng None is not 1.40-2"]
    # An option is present only as itself, never as the prefix of a longer one.
    shadowed = _VNG_HELP.replace("--root ROOT", "--rootfs ROOT").replace("--run RUN", "--run-x X")
    assert gate.launcher_problems({"virtme-ng": "1.40-2"}, shadowed, "1.40-2") == [
        "vng --help lacks --run",
        "vng --help lacks --root",
    ]


def test_q0_host_refuses_a_launcher_mismatch_before_planting_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _Host(tmp_path, monkeypatch)
    stdout = {"dpkg-query": "virtme-ng 1.42-1 amd64 ii\n", "vng": "usage: vng [--run RUN]"}
    monkeypatch.setattr(gate, "_stdout", lambda argv, cwd: stdout[argv[0]])
    with pytest.raises(
        gate.Q0Error,
        match=r"launcher: host virtme-ng '1\.42-1' is not 1\.40-2; vng --help lacks --root;",
    ):
        host.run(_JOB)
    assert host.calls == []


def test_vng_argv_launches_the_built_kernel_with_exactly_the_checked_options(
    tmp_path: Path,
) -> None:
    argv = gate.vng_argv(tmp_path / "work", Path("/a5-guest/root"), tmp_path / "out", gate.Q0_EXEC)
    assert argv[:4] == ["timeout", "--kill-after=30s", "2700", "vng"]
    options = dict(zip(argv[4::2], argv[5::2], strict=True))
    assert tuple(options) == gate.VNG_OPTIONS
    assert options == {
        "--run": str(tmp_path / "work" / "kernel" / gate.KERNEL_SOURCE / gate.BZIMAGE),
        "--root": "/a5-guest/root",
        "--rodir": "/a5=/a5",
        "--rwdir": f"/out={tmp_path / 'out'}",
        "--cpus": "4",
        "--memory": "12G",
        "--exec": "/bin/sh /a5/meta/q0-probe.sh",
    }


def test_launch_records_its_scope_before_the_guest_runs_and_returns_the_guest_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    handles, out = tmp_path / "ev" / "handles.json", tmp_path / "out"
    launched: list[Sequence[str]] = []

    def run(argv: Sequence[str], env: Mapping[str, str]) -> int:
        record = json.loads(handles.read_bytes())
        assert record == {
            "scope": "a5-guest-41-2.scope",
            "sentinel_env_sha256": hashlib.sha256(env[gate.SENTINEL_ENV].encode()).hexdigest(),
        }
        launched.append(argv)
        return 7

    monkeypatch.setattr(gate, "_launch_exit", run)
    run_env = {"GITHUB_RUN_ID": "41", "GITHUB_RUN_ATTEMPT": "2"} | LAUNCH_JOB_ENV
    root = Path("/a5-guest/root")
    assert gate.launch(run_env, tmp_path / "work", root, out, handles) == 7
    assert out.is_dir()
    vng = gate.vng_argv(tmp_path / "work", root, out, gate.Q0_EXEC)
    assert launched == [
        ["systemd-run", "--user", "--scope", "--quiet", "--unit=a5-guest-41-2.scope", "--", *vng]
    ]
    assert gate.launch({"GITHUB_RUN_ID": "41"}, tmp_path, root, out, tmp_path / "h.json") == 1
    assert not (tmp_path / "h.json").exists() and len(launched) == 1


LAUNCH_JOB_ENV = {"PATH": "/usr/bin:/bin", "HOME": "/home/runner", "XDG_RUNTIME_DIR": "/run/u"}


def test_launch_starts_systemd_run_under_only_the_launch_env_and_a_fresh_canary(
    tmp_path: Path,
) -> None:
    # The fake records its own exec-time environment block, the env vng would inherit.
    bin_dir, seen, handles = tmp_path / "bin", tmp_path / "seen", tmp_path / "handles.json"
    bin_dir.mkdir()
    (bin_dir / "systemd-run").write_text(f"#!/bin/sh\ncat /proc/$$/environ > {seen}\n")
    (bin_dir / "systemd-run").chmod(0o755)
    job = {"GITHUB_RUN_ID": "41", "GITHUB_RUN_ATTEMPT": "2", "GITHUB_TOKEN": "ghs_ambient"}
    job |= {"ACTIONS_RUNTIME_TOKEN": "ambient", "RUNNER_TEMP": "/tmp/r"}
    job |= LAUNCH_JOB_ENV | {"PATH": f"{bin_dir}:/usr/bin:/bin"}
    root = Path("/a5-guest/root")
    assert gate.launch(job, tmp_path / "work", root, tmp_path / "out", handles) == 0
    received = dict(entry.split("=", 1) for entry in seen.read_text().split("\0") if entry)
    canary = received.pop(gate.SENTINEL_ENV)
    assert canary.startswith(gate.SENTINEL_MARKER) and len(canary) > len(gate.SENTINEL_MARKER)
    assert received == {key: job[key] for key in gate.LAUNCH_ENV}
    record = json.loads(handles.read_bytes())
    assert record["sentinel_env_sha256"] == hashlib.sha256(canary.encode()).hexdigest()


@pytest.mark.parametrize("absent", ["PATH", "HOME", "XDG_RUNTIME_DIR"])
def test_launch_refuses_a_job_lacking_a_launch_variable_before_recording_a_scope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, absent: str
) -> None:
    monkeypatch.setattr(gate, "_launch_exit", lambda argv, env: pytest.fail(f"ran {argv}"))
    job = {"GITHUB_RUN_ID": "41", "GITHUB_RUN_ATTEMPT": "2"} | LAUNCH_JOB_ENV
    del job[absent]
    handles = tmp_path / "handles.json"
    assert gate.launch(job, tmp_path, Path("/r"), tmp_path / "out", handles) == 1
    assert not handles.exists()


@pytest.mark.parametrize(
    ("after_stop", "after_kill", "actions", "code"),
    [
        pytest.param([], [], ["stop"], 0, id="stopped"),
        pytest.param([12], [], ["stop", "kill"], 0, id="killed"),
        pytest.param([12], [12], ["stop", "kill"], 1, id="survivor"),
    ],
)
def test_cleanup_signals_only_the_recorded_scope_and_fails_on_a_survivor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    after_stop: list[int],
    after_kill: list[int],
    actions: list[str],
    code: int,
) -> None:
    (handles := tmp_path / "handles.json").write_text('{"scope": "a5-guest-41-2.scope"}')
    signalled: list[Sequence[str]] = []
    settled = iter([after_stop, after_kill])
    monkeypatch.setattr(gate, "scope_pids", lambda unit: [11, 12])
    monkeypatch.setattr(gate, "_exit_code", lambda argv: signalled.append(argv) or 0)
    monkeypatch.setattr(gate, "_settle", lambda pids, seconds: next(settled))
    out = tmp_path / "ev" / "cleanup.json"
    assert gate.cleanup(handles, out) == code
    assert [argv[2] for argv in signalled] == actions
    assert all(argv[-1] == "a5-guest-41-2.scope" for argv in signalled)
    record = json.loads(out.read_bytes())
    assert record["pids"] == {"11": "gone", "12": "alive" if after_kill else "gone"}
    assert record["verdict"] == ("fail" if code else "pass")


def test_cleanup_with_nothing_in_the_scope_signals_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (handles := tmp_path / "handles.json").write_text('{"scope": "a5-guest-41-2.scope"}')
    monkeypatch.setattr(gate, "scope_pids", lambda unit: [])
    monkeypatch.setattr(gate, "_exit_code", lambda argv: pytest.fail(f"signalled {argv}"))
    assert gate.cleanup(handles, tmp_path / "cleanup.json") == 0
    assert json.loads((tmp_path / "cleanup.json").read_bytes())["signals"] == []
    (handles).write_text('{"scope": "user.slice"}')
    assert gate.cleanup(handles, tmp_path / "refused.json") == 1


def test_settle_returns_only_the_pids_still_running(tmp_path: Path) -> None:
    child = subprocess.Popen(["sleep", "30"])
    try:
        assert gate._settle([child.pid], 0) == [child.pid]  # pyright: ignore[reportPrivateUsage]
    finally:
        child.kill()
        child.wait()
    assert gate._settle([child.pid], 1) == []  # pyright: ignore[reportPrivateUsage]


def test_q0_host_refuses_an_unset_job_binding_before_fetching_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _Host(tmp_path, monkeypatch)
    with pytest.raises(gate.Q0Error, match=r"lacks \['CI_PARENTS'\]"):
        host.run(_JOB | {"CI_PARENTS": ""})
    assert host.calls == []


def test_q0_host_writes_no_binding_for_a_stage_that_may_not_boot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    host = _Host(tmp_path, monkeypatch, problems=["/a5/x: socket"])
    with pytest.raises(gate.Q0Error, match="stage: /a5/x: socket"):
        host.run(_JOB)
    assert not (host.at.a5 / "meta" / "binding.env").exists()
    assert not (host.at.evidence / "host-stage.json").exists()


def test_host_command_stages_at_a5_from_inputs_alone_and_fails_loudly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    seen: list[tuple[Any, ...]] = []

    def q0_host(*args: Any) -> None:
        seen.append(args)
        raise gate.Q0Error("pool git_1: missing")

    monkeypatch.setattr(gate, "q0_host", q0_host)
    (doc := tmp_path / "inputs.json").write_text(json.dumps({"inputs": _RAW["inputs"]}))
    paths = {
        name: tmp_path / name for name in ("work", "root", "evidence", "workspace", "uv-cache")
    }
    argv = ["host", "--expectations", str(doc), "--key", "a.asc", "--key", "b.asc"]
    argv += [f"--{name}={path}" for name, path in paths.items()]
    assert main(argv) == 1
    assert "a5-kernel-ci host: pool git_1: missing" in capsys.readouterr().err
    (_, inputs, _, keys, at) = seen[0]
    assert inputs == parse_inputs(_RAW["inputs"]) and keys == (Path("a.asc"), Path("b.asc"))
    assert at == gate.HostLayout(
        paths["work"],
        paths["root"],
        gate.A5,
        paths["evidence"],
        paths["workspace"],
        paths["uv-cache"],
    )


# --- Q0 post-launch: q0-collect over the records the host writer retained --------------

_CLOSURE = tuple(
    gate.PoolPackage(
        gate.Package(name, version, "amd64"), f"pool/main/{deb.file}", deb.size, deb.sha256
    )
    for (name, version), deb in zip((("git", "1"), ("perl", "2")), _DEBS, strict=True)
)
_RUN_ENV = _JOB | {key: _IDENTITY[key] for key in gate.Q0_IDENTITY if key in _JOB}
_Q0_INPUTS = replace(parse_inputs(_RAW["inputs"]), sha256=_IDENTITY["INPUTS_SHA256"])


def _git_out(src: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(src), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


class PostLaunch(dict[str, Path]):
    """The host's retained records as q0_host lays them out, and one fresh guest /out."""

    tested: str  # the commit the stage clone holds, bound as this run's CI_TESTED

    @property
    def environ(self) -> dict[str, str]:
        return _RUN_ENV | {"CI_TESTED": self.tested}

    def write(self, closure: Any, **guest_identity: Any) -> None:
        manifest = (self["meta"] / "stage-manifest.json").read_bytes()
        src = self["a5"] / "src"
        gate.write_host_records(
            _records(
                values=_binding_values()
                | {"CI_TESTED": self.tested, "STAGE_MANIFEST_SHA256": _sha(manifest)},
                host={"closure": closure},
            ),
            gate.HostRecords(
                self["evidence"] / "install-ns.json",
                self["meta"] / "host.json",
                self["meta"] / "binding.env",
                self["evidence"] / "host-stage.json",
            ),
        )
        binding_env = (self["meta"] / "binding.env").read_bytes()
        identity = {
            "release": gate.GUEST_RELEASE,
            "lsm": ["capability", "landlock"],
            "tree": _git_out(src, "rev-parse", "HEAD^{tree}"),
            "blobs": {p: gate.git_blob((src / p).read_bytes()) for p in gate.BOUND_PRODUCT},
        }
        observation = {
            **_IDENTITY,
            "CI_TESTED": self.tested,
            "binding_env_sha256": _sha(binding_env),
            "INSTALL_NS_SHA256": gate.parse_binding_env(binding_env)["INSTALL_NS_SHA256"],
            "guest_identity": identity | guest_identity,
        }
        (self["out"] / "observation.json").write_text(json.dumps(observation))

    def run(
        self, environ: Mapping[str, str] | None = None, inputs: gate.Inputs = _Q0_INPUTS
    ) -> dict[str, Any]:
        return gate.q0_post_launch(
            inputs,
            self.environ if environ is None else environ,
            self["root"],
            self["a5"],
            self["out"],
            self["launched"],
            self["evidence"],
        )


@pytest.fixture
def post(tmp_path: Path) -> PostLaunch:
    paths = PostLaunch({name: tmp_path / name for name in ("root", "a5", "out", "evidence")})
    paths["meta"] = paths["a5"] / "meta"
    for directory in paths.values():
        directory.mkdir()
    (paths["root"] / "etc").mkdir()
    (paths["root"] / "etc" / "x").write_text("x")
    src = paths["a5"] / "src"
    src.mkdir()
    (src / "y.py").write_text("y")
    for path in gate.BOUND_PRODUCT:
        (src / path).parent.mkdir(parents=True, exist_ok=True)
        (src / path).write_text(f"# {path}\n")
    _git_out(src, "init", "-q")
    _git_out(src, "add", "-A")
    _git_out(src, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "tested")
    paths.tested = _git_out(src, "rev-parse", "HEAD")
    assert gate.guest_stage_verify(paths["root"], paths["a5"], ()) == []
    paths["launched"] = tmp_path / "launched"
    paths["launched"].touch()
    paths.write([asdict(package) for package in _CLOSURE])
    return paths


def test_q0_post_launch_completes_from_the_retained_records_alone(post: PostLaunch) -> None:
    record = post.run()
    assert record["completed_observation"] is True, record["problems"]
    assert record["observation_sha256"] == _sha((post["out"] / "observation.json").read_bytes())
    install = json.loads((post["evidence"] / "install-binding.json").read_text())
    assert install["verdict"] == "pass"
    unchanged = json.loads((post["evidence"] / "stage-unchanged.json").read_text())
    assert unchanged["verdict"] == "pass"


@pytest.mark.parametrize(
    "write",
    [
        pytest.param(lambda post: (post["root"] / "etc" / "x").write_text("z"), id="mutated-file"),
        pytest.param(lambda post: (post["root"] / "etc" / "new").write_text(""), id="added-root"),
        pytest.param(lambda post: (post["a5"] / "src" / "new.py").write_text(""), id="added-a5"),
        pytest.param(lambda post: (post["root"] / "etc" / "x").chmod(0o600), id="mode"),
    ],
)
def test_q0_post_launch_refuses_a_stage_the_guest_run_changed(
    post: PostLaunch, write: Callable[[PostLaunch], object]
) -> None:
    write(post)
    record = post.run()
    assert record["completed_observation"] is False
    [problem] = record["problems"]
    assert problem.startswith("stage-unchanged: post-run stage ")
    unchanged = json.loads((post["evidence"] / "stage-unchanged.json").read_text())
    assert unchanged["verdict"] == "fail"


def test_q0_post_launch_binds_the_guest_to_the_tested_commit_in_the_stage_clone(
    post: PostLaunch,
) -> None:
    assert post.run()["completed_observation"] is True
    src = post["a5"] / "src"
    tested = json.loads((post["evidence"] / "guest-identity.json").read_text())["tested"]
    assert tested == {
        "tree": _git_out(src, "rev-parse", f"{post.tested}^{{tree}}"),
        "blobs": {p: _git_out(src, "rev-parse", f"{post.tested}:{p}") for p in gate.BOUND_PRODUCT},
    }


@pytest.mark.parametrize(
    "guest_identity",
    [
        pytest.param({"release": "7.3.1-generic"}, id="release"),
        pytest.param({"lsm": ["capability"]}, id="no-landlock"),
        pytest.param({"tree": "d" * 40}, id="tree"),
        pytest.param({"blobs": dict.fromkeys(gate.BOUND_PRODUCT, "0" * 40)}, id="blobs"),
    ],
)
def test_q0_post_launch_refuses_a_guest_of_another_kernel_or_checkout(
    post: PostLaunch, guest_identity: dict[str, Any]
) -> None:
    post.write([asdict(package) for package in _CLOSURE], **guest_identity)
    record = post.run()
    _completed_nothing(record)
    assert all(p.startswith("guest-identity: guest ") for p in record["problems"])


def test_q0_post_launch_refuses_a_tested_commit_the_stage_clone_lacks(post: PostLaunch) -> None:
    record = post.run(post.environ | {"CI_TESTED": "c" * 40})
    _completed_nothing(record)
    [problem] = record["problems"]
    assert problem.startswith("host: ['git', '-C', ") and "rev-parse" in problem
    assert list(post["evidence"].glob("observation.json")) == []


def test_closure_debs_are_the_closure_q0_host_installs() -> None:
    records = _records(host={"closure": [asdict(package) for package in _CLOSURE]})
    assert gate.closure_debs(records.host_json, records.binding_env) == _DEBS


_ENTRY = asdict(_CLOSURE[0])


@pytest.mark.parametrize(
    "closure",
    [
        pytest.param([], id="empty"),
        pytest.param({"0": _ENTRY}, id="not-a-list"),
        pytest.param(None, id="absent"),
        pytest.param([_ENTRY | {"size": True}], id="bool-size"),
        pytest.param([_ENTRY | {"size": "10"}], id="text-size"),
        pytest.param([_ENTRY | {"sha256": "D" * 64}], id="upper-hex"),
        pytest.param([{k: v for k, v in _ENTRY.items() if k != "filename"}], id="no-filename"),
        pytest.param([_ENTRY | {"package": {"name": "git"}}], id="partial-package"),
    ],
)
def test_q0_post_launch_refuses_a_malformed_closure_before_collecting(
    post: PostLaunch, closure: Any
) -> None:
    post.write(closure)
    record = post.run()
    _completed_nothing(record)
    assert record["problems"][0].startswith("host: host.json closure")
    assert list(post["evidence"].glob("observation.json")) == []


def test_q0_post_launch_refuses_a_host_json_binding_env_does_not_name(post: PostLaunch) -> None:
    host_json = post["meta"] / "host.json"
    named = _sha(host_json.read_bytes())
    host_json.write_bytes(host_json.read_bytes().replace(b'"perl"', b'"perk"'))
    record = post.run()
    assert record["problems"] == [f"host: host.json is not the record binding.env names ({named})"]
    assert list(post["evidence"].glob("observation.json")) == []


def test_q0_post_launch_judges_a_debs_list_the_install_record_does_not_hold(
    post: PostLaunch,
) -> None:
    post.write([asdict(_CLOSURE[0])])
    record = post.run()
    _completed_nothing(record)
    assert all(problem.startswith("install-binding:") for problem in record["problems"])


@pytest.mark.parametrize("key", ["CI_TESTED", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT"])
def test_q0_post_launch_takes_the_run_identity_from_the_job(post: PostLaunch, key: str) -> None:
    _completed_nothing(post.run(post.environ | {key: "other"}))
    unset = post.run({k: v for k, v in post.environ.items() if k != key})
    assert unset["problems"] == [f"host: job environment lacks {[key]}"]


def test_q0_post_launch_takes_inputs_sha256_from_the_parsed_inputs(post: PostLaunch) -> None:
    record = post.run(inputs=replace(_Q0_INPUTS, sha256="2" * 64))
    _completed_nothing(record)
    assert record["problems"][0].startswith("collect: observation.json INPUTS_SHA256")


def test_q0_collect_command_keeps_its_record_and_exits_on_completion(
    post: PostLaunch, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(gate, "A5", post["a5"])
    for key, value in post.environ.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(gate, "parse_inputs", lambda raw: _Q0_INPUTS)
    (doc := post["a5"].parent / "inputs.json").write_text(json.dumps({"inputs": _RAW["inputs"]}))
    argv = ["q0-collect", "--expectations", str(doc)]
    argv += [f"--{name}={post[name]}" for name in ("root", "out", "launched", "evidence")]
    assert main(argv) == 0
    kept = json.loads((post["evidence"] / "q0-collect.json").read_text())
    assert kept["completed_observation"] is True and "verdict" not in kept
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "3")
    assert main(argv) == 1
    err = capsys.readouterr().err
    assert "a5-kernel-ci q0-collect: collect: observation.json GITHUB_RUN_ATTEMPT" in err
    assert json.loads((post["evidence"] / "q0-collect.json").read_text())["problems"]


def test_ns_install_runs_from_the_q0_inputs_only_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[tuple[Any, ...]] = []
    monkeypatch.setattr(gate, "ns_install", lambda *args: seen.append(args) or 7)
    (doc := tmp_path / "inputs.json").write_text(json.dumps({"inputs": _RAW["inputs"]}))
    argv = ["guest-stage", "ns-install", "--expectations", str(doc), "--root", "/r"]
    assert main([*argv, "--host-netns", "net:[1]", "--evidence", "/e", "a.deb"]) == 7
    assert seen == [(Path("/r"), "net:[1]", Path("/e"), ["a.deb"])]
