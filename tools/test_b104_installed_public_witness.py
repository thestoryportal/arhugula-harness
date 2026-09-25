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


def _ok(phase: str, observed: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": phase,
        "ok": True,
        "observed": observed,
        "provenance": {"installation_receipt_sha256": "e" * 64, "interpreter": {"isolated": 1}},
    }


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
            "capture": {"exit": 0, "timeout": False},
            "resume-a": {
                "exit": None,
                "timeout": False,
                "barrier_entered": True,
                "kill": {"signal": "SIGKILL", "returncode": -signal.SIGKILL, "group_gone": True},
            },
            "observe-held": {"exit": 0, "timeout": False},
            "resume-b": {"exit": 0, "timeout": False},
            "recover": {"exit": 0, "timeout": False},
            "resume-after-abandon": {"exit": 0, "timeout": False},
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
        "webhook_requests": [{"path": "/hook"}],
        "webhook_errors": [],
        "tool_calls": 0,
        "tool_server": {"ready": True},
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


def test_a_complete_correct_run_passes() -> None:
    verdict = w.evaluate(passing_evidence())

    assert verdict["status"] == "PASS", verdict["failed_checks"]
    assert verdict["failed_checks"] == []


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
        (_set("runs.resume-a.kill.group_gone", False), "resume-a-started.killed_by_parent"),
        (_set("results.resume-a", {"ok": True}), "resume-a-started.no_result_from_a"),
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
        # No replay of the gate or the tool.
        (
            _set("webhook_requests", [{"path": "/hook"}, {"path": "/hook"}]),
            "no-replay.webhooks_total",
        ),
        (_set("tool_calls", 1), "no-replay.tool_never_called"),
        (_set("tool_server", {"ready": False}), "no-replay.tool_server_ready"),
        # Provenance: every child installed, one receipt.
        (
            _set("results.recover.provenance.installation_receipt_sha256", "1" * 64),
            "provenance.one_receipt",
        ),
        (
            _set("results.resume-b.provenance.interpreter", {"isolated": 0}),
            "provenance.every_child_installed",
        ),
        (_set("results.recover", None), "provenance.every_phase_recorded"),
    ],
)
def test_each_broken_fact_fails_its_named_check(
    mutation: Callable[[dict[str, Any]], None], failed: str
) -> None:
    evidence = passing_evidence()
    mutation(evidence)

    verdict = w.evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert failed in verdict["failed_checks"]


def test_a_timed_out_phase_is_inconclusive_not_pass_or_fail() -> None:
    evidence = passing_evidence()
    evidence["runs"]["resume-b"]["timeout"] = True

    verdict = w.evaluate(evidence)

    assert verdict["status"] == "INCONCLUSIVE"
    assert verdict["timed_out_phases"] == ["resume-b"]


def test_a_stopped_scenario_with_no_later_phases_fails_closed() -> None:
    evidence = passing_evidence()
    for phase in ("resume-b", "recover", "resume-after-abandon"):
        evidence["runs"].pop(phase)
        evidence["results"].pop(phase)

    verdict = w.evaluate(evidence)

    assert verdict["status"] == "FAIL"
    assert {"provenance.every_phase_recorded", "resume-b-refused.typed_refusal"} <= set(
        verdict["failed_checks"]
    )


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
