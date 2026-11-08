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

import hashlib
import json
import os
import subprocess
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
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
    main,
    parse_expectations,
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


# --- Q0 observation (host side) -----------------------------------------------------

_IDENTITY = {
    "CI_TESTED": "c" * 40,
    "GITHUB_RUN_ID": "4242",
    "GITHUB_RUN_ATTEMPT": "2",
    "INPUTS_SHA256": "1" * 64,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Q0(dict[str, Path]):
    """One consistent Q0 fixture: retained host records, a pre-launch marker, a fresh /out."""

    def observation(self, **fields: Any) -> None:
        env = gate.parse_binding_env(self["binding_env"].read_bytes())
        raw = {
            **_IDENTITY,
            "binding_env_sha256": _sha(self["binding_env"].read_bytes()),
            "INSTALL_NS_SHA256": env["INSTALL_NS_SHA256"],
            **fields,
        }
        self["out"].joinpath("observation.json").write_text(
            json.dumps({k: v for k, v in raw.items() if v is not None})
        )

    def binding_env(self, install_ns_sha256: str, **fields: str) -> bytes:
        values = (
            {
                key: ("9" * 64 if key.endswith("_SHA256") else f"v-{key}")
                for key in gate.BINDING_ENV_KEYS
            }
            | {k: v for k, v in _IDENTITY.items()}
            | {"INSTALL_NS_SHA256": install_ns_sha256}
        )
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
        )


@pytest.fixture
def q0(tmp_path: Path) -> Q0:
    paths = Q0({name: tmp_path / name for name in ("host", "out", "evidence")})
    for directory in paths.values():
        directory.mkdir()
    paths |= {
        "install_ns": paths["host"] / "install-ns.json",
        "binding_env": paths["host"] / "binding.env",
        "host_stage": paths["host"] / "host-stage.json",
        "launched": paths["host"] / "launched",
    }
    paths["install_ns"].write_text('{"dpkg_exit": 0}\n')
    env = paths.binding_env(_sha(paths["install_ns"].read_bytes()))
    paths["binding_env"].write_bytes(env)
    paths["host_stage"].write_text(json.dumps({"binding_env_sha256": _sha(env)}))
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
    assert gate.binding_verify(q0["binding_env"], q0["host_stage"], guest)["problems"] == []
    mutate(guest)
    # An environment-supplied hash is never a substitute for the recorded one.
    monkeypatch.setenv("binding_env_sha256", _sha(q0["binding_env"].read_bytes()))
    assert gate.binding_verify(q0["binding_env"], q0["host_stage"], guest)["problems"]
    _completed_nothing(q0.observe())


# Group 6: install-binding ties install-ns.json, binding.env and the guest's value.
_INSTALL_MUTATIONS = {
    "absent": lambda q: q["install_ns"].unlink(),
    "malformed": lambda q: q["install_ns"].write_text("{"),
    "changed-after-binding": lambda q: q["install_ns"].write_text('{"dpkg_exit": 1}\n'),
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
