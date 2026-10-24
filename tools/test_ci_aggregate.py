"""WO-U09: the `pytest (all axis packages) — blocking` aggregate and the graph behind it.

Two lenses. The verdict lens checks `tools/ci_aggregate.py` against the WS-10 §12.2 truth
table, restated here independently and enumerated over every input combination, and runs
the aggregate step's own command with the env the workflow wires. The graph lens pins the
ci.yml contract that the verdict depends on: the exact required name, `always()`, both
constituents independent of each other, one coverage-enabled suite execution, and the
unchanged set of required contexts."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_aggregate import Inputs, JobResult, decide, main

_REPO = Path(__file__).resolve().parent.parent
_CI_YML = _REPO / ".github" / "workflows" / "ci.yml"
_REQUIRED_NAME = "pytest (all axis packages) — blocking"
_PRIMARY_PYTEST = (
    'uv run pytest -m "not e2e" --cov --cov-report=term-missing --cov-report=xml --cov-report=json'
)
# The 14 required contexts recorded by the WO-U01 inventory (reviewed 5a53b104).
_REQUIRED_CONTEXTS = frozenset(
    {
        "pytest (all axis packages) — blocking",
        "ruff (lint + format) — blocking",
        "pyright (strict) — blocking",
        "substitution ledger (tally gate) — blocking",
        "CLAUDE.md citations (I-1 resolution gate) — blocking",
        "arc ledger (tally gate) — blocking",
        "semantic overlay (drift gate) — blocking",
        "tools/ test coverage guard + codex-loop tests — blocking",
        "Q1 review gate (structured artifact) — blocking",
        "Q3 evidence + closure gate — blocking",
        "merge-gate log consistency (C-HE-23 §2 reducer) — blocking",
        "Codex context guard (anti-rot gate) — blocking",
        "split-brain ledger backstop — blocking",
        "clearance corpus (frontmatter gate) — blocking",
    }
)

_RESULTS = ("success", "failure", "cancelled", "skipped")
_BOOKKEEPING = ("true", "false", "", "maybe")


def _spec_passes(classifier: str, bookkeeping: str, package: str, parity: str) -> bool:
    # WS-10 §12.2, row by row; every other combination fails.
    if classifier != "success":
        return False
    if bookkeeping == "false":
        return (package, parity) == ("success", "success")
    if bookkeeping == "true":
        return (package, parity) in {("skipped", "skipped"), ("success", "success")}
    return False


def _env(classifier: str, bookkeeping: str, package: str, parity: str) -> dict[str, str]:
    return {
        "CLASSIFIER_RESULT": classifier,
        "BOOKKEEPING": bookkeeping,
        "PACKAGE_RESULT": package,
        "PARITY_RESULT": parity,
    }


def _without(var: str) -> dict[str, str]:
    env = _env("success", "false", "success", "success")
    del env[var]
    return env


# --- verdict lens ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("classifier", "bookkeeping", "package", "parity"),
    list(itertools.product(_RESULTS, _BOOKKEEPING, _RESULTS, _RESULTS)),
)
def test_verdict_matches_the_truth_table(
    classifier: str, bookkeeping: str, package: str, parity: str
) -> None:
    inputs = Inputs(JobResult(classifier), bookkeeping, JobResult(package), JobResult(parity))
    assert decide(inputs).passed is _spec_passes(classifier, bookkeeping, package, parity)


@pytest.mark.parametrize(
    ("case", "env"),
    [
        ("parity missing while package skipped", _env("success", "false", "skipped", "skipped")),
        ("superseded constituent canceled", _env("success", "false", "success", "cancelled")),
        ("bookkeeping with one unexpected skip", _env("success", "true", "skipped", "success")),
        ("bookkeeping with a canceled suite", _env("success", "true", "cancelled", "skipped")),
        ("classifier failed, full suites green", _env("failure", "", "success", "success")),
        ("classifier green, empty output", _env("success", "", "success", "success")),
    ],
)
def test_named_failure_shapes_exit_1(
    case: str, env: dict[str, str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(env) == 1, case
    assert "FAIL: no accepted row" in capsys.readouterr().err


@pytest.mark.parametrize(
    "env",
    [
        _env("success", "false", "success", "neutral"),
        _env("success", "false", "", "success"),
        _without("PARITY_RESULT"),
        _without("BOOKKEEPING"),
    ],
)
def test_malformed_input_exits_2(env: dict[str, str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(env) == 2
    assert "unparseable aggregate input" in capsys.readouterr().err


def test_pass_reports_the_classification_and_both_results(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(_env("success", "true", "skipped", "skipped")) == 0
    out = capsys.readouterr().out
    assert out.startswith("PASS: validated bookkeeping: both suites skipped")
    assert "bookkeeping='true' package=skipped parity=skipped" in out


# --- graph lens -----------------------------------------------------------------------


def _jobs() -> dict[str, dict[str, Any]]:
    return yaml.safe_load(_CI_YML.read_text())["jobs"]


def _aggregate_id(jobs: dict[str, dict[str, Any]]) -> str:
    [job_id] = [k for k, job in jobs.items() if job.get("name") == _REQUIRED_NAME]
    return job_id


def _aggregate_step(job: dict[str, Any]) -> dict[str, Any]:
    [step] = [s for s in job["steps"] if "ci_aggregate.py" in str(s.get("run", ""))]
    return step


def test_aggregate_keeps_the_required_name_and_waits_for_every_input() -> None:
    job = _jobs()[_aggregate_id(_jobs())]
    assert job["if"] == "always()"
    assert sorted(job["needs"]) == ["changes", "package-tests", "parity-tests"]
    assert "continue-on-error" not in job
    assert not _aggregate_step(job).get("continue-on-error", False)


def test_aggregate_env_wires_each_input_to_its_own_job() -> None:
    env = _aggregate_step(_jobs()[_aggregate_id(_jobs())])["env"]
    assert env == {
        "CLASSIFIER_RESULT": "${{ needs.changes.result }}",
        "BOOKKEEPING": "${{ needs.changes.outputs.bookkeeping }}",
        "PACKAGE_RESULT": "${{ needs.package-tests.result }}",
        "PARITY_RESULT": "${{ needs.parity-tests.result }}",
    }


@pytest.mark.parametrize(
    ("values", "expected_exit"),
    [
        (("success", "false", "success", "success"), 0),
        (("success", "false", "failure", "success"), 1),
        (("success", "true", "skipped", "skipped"), 0),
        (("failure", "", "success", "success"), 1),
    ],
)
def test_aggregate_step_command_runs_the_verdict(
    values: tuple[str, str, str, str], expected_exit: int
) -> None:
    # The step's own `run:`, with the runner's /usr/bin/python3 swapped for this
    # interpreter so the witness resolves on any host.
    run = str(_aggregate_step(_jobs()[_aggregate_id(_jobs())])["run"])
    assert "/usr/bin/python3 tools/ci_aggregate.py" in run
    p = subprocess.run(
        ["bash", "-eo", "pipefail", "-c", run.replace("/usr/bin/python3", sys.executable)],
        cwd=_REPO,
        env={**os.environ, **_env(*values)},
        capture_output=True,
        text=True,
    )
    assert p.returncode == expected_exit, p.stdout + p.stderr


def test_constituents_follow_classification_and_not_each_other() -> None:
    jobs = _jobs()
    for job_id in ("package-tests", "parity-tests"):
        assert jobs[job_id]["needs"] == "changes", job_id
        assert not str(jobs[job_id]["name"]).endswith("— blocking"), job_id


def _runs(job: dict[str, Any]) -> list[str]:
    return [str(s["run"]) for s in job["steps"] if "run" in s]


def test_one_provider_free_suite_execution_carries_coverage() -> None:
    jobs = _jobs()
    suite_runs = [
        (job_id, run)
        for job_id, job in jobs.items()
        for run in _runs(job)
        if re.search(r'uv run pytest -m "not e2e"', run)
    ]
    assert suite_runs == [("package-tests", _PRIMARY_PYTEST)]
    pytest_step = next(s for s in jobs["package-tests"]["steps"] if s.get("run") == _PRIMARY_PYTEST)
    assert "continue-on-error" not in pytest_step
    assert "continue-on-error" not in jobs["package-tests"]


def test_coverage_publishing_is_advisory_and_names_its_binding() -> None:
    steps = _jobs()["package-tests"]["steps"]
    after = steps[[s.get("run") for s in steps].index(_PRIMARY_PYTEST) + 1 :]
    assert after, "coverage publishing follows the primary suite"
    for step in after:
        assert str(step.get("if")).startswith("always()"), step.get("name")
        assert step.get("continue-on-error") is True, step.get("name")
    upload = next(s for s in after if "upload-artifact" in str(s.get("uses", "")))
    name = upload["with"]["name"]
    # WS-10 §12.4: a PR's github.sha is the synthetic merge commit, not the reviewed head.
    for part in ("github.event.pull_request.head.sha || github.sha", "run_id", "run_attempt"):
        assert part in name
    assert set(upload["with"]["path"].split()) == {"coverage.xml", "coverage-provenance.json"}
    # [LAW:verifiable-goals] A pathname alone cannot certify a complete manifest.
    assert upload["if"] == "always() && steps.coverage_provenance.outputs.valid == 'true'"
    assert _provenance_step()["id"] == "coverage_provenance"


def _provenance_step() -> dict[str, Any]:
    steps = _jobs()["package-tests"]["steps"]
    [step] = [s for s in steps if "coverage-provenance.json" in str(s.get("run", ""))]
    return step


def test_provenance_env_keeps_head_base_and_tested_commit_distinct() -> None:
    env = _provenance_step()["env"]
    assert env["COVERAGE_HEAD"] == "${{ github.event.pull_request.head.sha || github.sha }}"
    assert (
        env["COVERAGE_BASE"] == "${{ github.event.pull_request.base.sha || github.event.before }}"
    )
    assert env["COVERAGE_TESTED"] == "${{ github.sha }}"
    assert env["COVERAGE_COMMAND"] == _PRIMARY_PYTEST


@pytest.mark.parametrize("xml_state", ["present", "missing"])
@pytest.mark.parametrize("json_state", ["valid", "missing", "malformed"])
def test_provenance_step_writes_the_manifest_it_summarizes(
    tmp_path: Path, xml_state: str, json_state: str
) -> None:
    (tmp_path / "uv.lock").write_text("lock\n")
    totals = {"percent_covered_display": "91", "covered_lines": 91, "num_statements": 100}
    json_body = {"valid": json.dumps({"totals": totals}), "malformed": "{not json"}
    if json_state in json_body:
        (tmp_path / "coverage.json").write_text(json_body[json_state])
    if xml_state == "present":
        (tmp_path / "coverage.xml").write_text("<coverage/>")
    available = (xml_state, json_state) == ("present", "valid")
    p = _run_provenance(tmp_path)
    assert p.returncode == 0, p.stderr
    summary = (tmp_path / "summary").read_text()
    assert p.stdout == ""
    assert (tmp_path / "output").read_text() == "valid=true\n"
    manifest = json.loads((tmp_path / "coverage-provenance.json").read_text())
    assert manifest == {
        "head": "h" * 40,
        "base": "b" * 40,
        "tested_commit": "m" * 40,
        "workflow": "CI",
        "run_id": "7",
        "run_attempt": "2",
        "platform": manifest["platform"],
        "uv_lock_sha256": hashlib.sha256(b"lock\n").hexdigest(),
        "command": _PRIMARY_PYTEST,
        "coverage_xml": xml_state,
        "coverage_json": json_state,
        "coverage_json_error": manifest["coverage_json_error"],
        "coverage_available": available,
    }
    assert manifest["platform"]
    assert (manifest["coverage_json_error"] is None) is (json_state != "malformed")
    assert json.dumps(manifest, indent=2) in summary
    assert ("Total line coverage: 91%" in summary) is available
    assert ("Coverage unavailable" in summary) is not available


def _run_provenance(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    # Execute the complete shell step, including its summary redirection.
    run = str(_provenance_step()["run"]).replace("uv run python", sys.executable)
    env = {
        **os.environ,
        "COVERAGE_HEAD": "h" * 40,
        "COVERAGE_BASE": "b" * 40,
        "COVERAGE_TESTED": "m" * 40,
        "COVERAGE_COMMAND": _PRIMARY_PYTEST,
        "GITHUB_WORKFLOW": "CI",
        "GITHUB_RUN_ID": "7",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "PYTHONPATH": str(tmp_path),
    }
    (tmp_path / "output").touch()
    return subprocess.run(
        ["bash", "-eo", "pipefail", "-c", run],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("failure", ["interrupted", "short-write"])
def test_incomplete_provenance_is_never_published(tmp_path: Path, failure: str) -> None:
    (tmp_path / "uv.lock").write_text("lock\n")
    # Inject the disk failure below the real publication program. A short write
    # returns normally, so successful publication must also validate persisted JSON.
    (tmp_path / "sitecustomize.py").write_text(
        "from pathlib import Path\n"
        "original = Path.write_text\n"
        "def write(self, data, *args, **kwargs):\n"
        "    if 'coverage-provenance' in self.name:\n"
        "        original(self, '{partial', *args, **kwargs)\n"
        + (
            "        raise OSError('interrupted write')\n"
            if failure == "interrupted"
            else "        return 8\n"
        )
        + "    return original(self, data, *args, **kwargs)\n"
        "Path.write_text = write\n"
    )
    p = _run_provenance(tmp_path)
    assert p.returncode != 0, p.stdout + p.stderr
    assert not (tmp_path / "coverage-provenance.json").exists()
    assert (tmp_path / "output").read_text() == ""


def test_summary_redirection_failure_cannot_authorize_upload(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("lock\n")
    (tmp_path / "summary").mkdir()
    p = _run_provenance(tmp_path)
    assert p.returncode != 0
    assert not (tmp_path / "coverage-provenance.json").exists()
    assert (tmp_path / "output").read_text() == ""


def test_parity_job_provides_just_and_zsh_then_runs_the_parity_script() -> None:
    steps = _jobs()["parity-tests"]["steps"]
    uses = [str(s.get("uses", "")) for s in steps]
    runs = _runs(_jobs()["parity-tests"])
    assert any(u.startswith("extractions/setup-just@") for u in uses)
    assert any("apt-get install -y zsh" in r for r in runs)
    assert runs[-1] == "bash tools/codex-parity-check.sh"
    job = _jobs()["parity-tests"]
    assert not job.get("continue-on-error", False)
    assert not steps[-1].get("continue-on-error", False)


def test_reducer_regressions_have_an_independently_required_blocking_job() -> None:
    job = _jobs()["tools-test-coverage-and-codex-loop"]
    assert job["name"] in _REQUIRED_CONTEXTS
    assert job["needs"] == "changes"
    assert not job.get("continue-on-error", False)
    [step] = [s for s in job["steps"] if "test_ci_aggregate.py" in str(s.get("run", ""))]
    assert step["run"] == "uv run python -m pytest tools/test_ci_aggregate.py -q"
    assert not step.get("continue-on-error", False)


def test_required_context_names_are_unchanged() -> None:
    names = (str(job.get("name", "")) for job in _jobs().values())
    blocking = {name for name in names if name.endswith("— blocking")}
    assert blocking == _REQUIRED_CONTEXTS
