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
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import mechanized_checks as mc
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
) -> dict:
    location = f"doc.md:{arc}"
    core_ = fr.FindingCore(
        fr.make_finding_id(producer, HEAD, location, n),
        location,
        "e",
        "x",
        "warn",
        "mechanized-deterministic",
        "fresh",
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


# mutation-probe: tools/mechanized_checks/stale_carry.py:51 drop the count-vs-table mismatch filter
def test_stale_carry_clean(tmp_path):
    (tmp_path / "ok.md").write_text(
        "Two contracts:\n| id | name |\n|---|---|\n| a | x |\n| b | y |\n\n"
        "Two rows:\n| a |\n| b |\n\nSee r<N>.log and TBDX.\n"
    )
    assert stale_carry.Check().run(_subject(tmp_path, changed=["ok.md"])) == []


# mutation-probe: tools/mechanized_checks/cited_symbol_exists.py:40 drop the cited-line-count filter
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


# mutation-probe: tools/mechanized_checks/unswept_consumers.py:46 drop the still-defined filter
def test_unswept_consumers_ignores_edited_and_moved_definitions(tmp_path):
    (tmp_path / "a.py").write_text("def kept(x, y):\n    pass\n")
    (tmp_path / "c.py").write_text("def moved():\n    pass\n")
    (tmp_path / "b.py").write_text("kept(1, 2)\nmoved()\n")
    diff = "-def kept(x):\n+def kept(x, y):\n-def moved():\n"
    assert unswept_consumers.Check().run(_subject(tmp_path, diff=diff)) == []


def test_unrun_cli_reruns_read_only_claims_and_flags_failures(tmp_path):
    calls: list[list[str]] = []

    def execute(argv: list[str], cwd: Path) -> tuple[int, str]:
        calls.append(argv)
        return (1, "") if argv[1] == "broken-check" else (0, "ok")

    subject = _subject(
        tmp_path,
        claims_text="feat: x\n\nVerified: `just broken-check` and `just codex-check`\n",
        pr_body="Ran: `uv run pytest tools/test_x.py -q`\n",
    )
    found = unrun_cli.Check(execute=execute).run(subject)
    assert [(f.severity, f.location) for f in found] == [("warn", "just broken-check")]
    assert calls == [
        ["just", "broken-check"],
        ["just", "codex-check"],
        ["uv", "run", "pytest", "tools/test_x.py", "-q"],
    ]


# mutation-probe: tools/mechanized_checks/unrun_cli.py:87-95 drop the read-only grammar gate
def test_unrun_cli_never_executes_outside_the_read_only_grammar(tmp_path):
    refused = [
        "just main-protection-apply",
        "just check; rm -rf /",
        "just fmt-check fmt",  # `just` runs extra tokens as further recipes
        "just fmt-check main-protection-rollback",
        "just mech-check",  # recipes that run this runner would recurse
        "just lanes-verify",
        "uv run python tools/mechanized_checks/runner.py check",
        "uv run python tools/../escape.py check",
        "uv run pytest --basetemp=/tmp/wiped",  # pytest deletes its basetemp
        "uv run pytest ../elsewhere/test_x.py",
    ]
    subject = _subject(tmp_path, claims_text="".join(f"Ran: `{c}`\n" for c in refused))
    found = unrun_cli.Check(execute=lambda argv, cwd: pytest.fail(f"executed {argv}")).run(subject)
    assert [(f.severity, f.location) for f in found] == [("info", c) for c in refused]


def test_runner_recipes_match_the_justfile():
    recipe, invoking = None, set()
    for line in (core.REPO / "justfile").read_text().splitlines():
        header = re.match(r"^([A-Za-z][\w-]*)(?:\s[^:]*)?:(?!=)", line)
        recipe = header.group(1) if header else recipe
        if "mechanized_checks/runner.py" in line:
            invoking.add(recipe)
    assert invoking == unrun_cli.RUNNER_RECIPES


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
    assert unrun_cli.execute_argv(["just", "check"], tmp_path) == (0, "outerr")
    assert seen["argv"] == ["just", "check"] and not seen.get("shell") and seen["cwd"] == tmp_path


def _probe_fixture(tmp_path: Path, *, logged: bool) -> core.Subject:
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "x.py").write_text("A = 1\nB = 2\n")
    (tmp_path / "tools" / "test_x.py").write_text(
        "# mutation-probe: drop B\ndef test_t():\n    assert True\n"
    )
    (tmp_path / ".harness").mkdir()
    rows = [
        {
            "test": "uv run pytest tools/test_x.py::test_t -q",
            "file": "tools/x.py",
            "lines": "2-2",
            "rc": 0,
        }
    ]
    (tmp_path / ".harness" / "mutation-probe-log.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows[: int(logged)])
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


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:94-98 drop the restore abort
def test_mutation_probe_restore_failure_stops_the_run_whatever_the_mode(tmp_path, monkeypatch):
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    restore_failed = mpr.Check(probe=lambda repo, file, lines, node: (3, "RESTORE FAILED: x.py"))
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


# mutation-probe: tools/mechanized_checks/mutation_probe_reverify.py:85-92 drop the unprobed arm
def test_mutation_probe_reverify_never_reads_an_unprobed_annotation_as_verified(tmp_path):
    found = mpr.Check(probe=lambda *a: pytest.fail("probed without a logged range")).run(
        _probe_fixture(tmp_path, logged=False)
    )
    assert [(f.severity, f.location) for f in found] == [("warn", "tools/test_x.py::test_t")]
    assert "never probed" in found[0].evidence


# mutation-probe: tools/mechanized_checks/double_fidelity.py:20-23 drop the issubclass raise
def test_assert_fake_is_subclass_detects_a_false_fidelity_claim():
    class Real: ...

    class Good(Real): ...

    class Fake: ...

    tdf.assert_fake_is_subclass(Good, Real)
    with pytest.raises(AssertionError, match="wrong-fidelity"):
        tdf.assert_fake_is_subclass(Fake, Real)


# mutation-probe: tools/mechanized_checks/double_fidelity.py:41 drop the assertion exemption
def test_double_fidelity_flags_a_bare_double_without_an_assertion(tmp_path):
    (tmp_path / "test_a.py").write_text(
        "class FakeClock:\n    pass\n\ndef test_a():\n    use(FakeClock())\n"
    )
    (tmp_path / "test_b.py").write_text(
        "class FakeClock:\n    pass\n\nassert_fake_is_subclass(FakeClock, Clock)\n\n"
        "def test_b():\n    use(FakeClock())\n"
    )
    (tmp_path / "test_c.py").write_text(
        "class FakeClock(Clock):\n    pass\n\ndef test_c():\n    use(FakeClock())\n"
    )
    found = tdf.Check().run(_subject(tmp_path, changed=["test_a.py", "test_b.py", "test_c.py"]))
    assert [f.location for f in found] == ["test_a.py:1"]


# --- emission, run verdict, replay ------------------------------------------------------


def test_emit_writes_findings_and_a_clean_marker_and_reruns_never_collide(tmp_path, monkeypatch):
    log = tmp_path / "gate.jsonl"
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", log)
    finding = [core.MechFinding("doc.md:1", "e", "x")]
    ids = {"arc_id": "u-he-40", "lane_id": "lane-a", "head_sha": HEAD}
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


# mutation-probe: tools/mechanized_checks/core.py:290-292 drop the gate_demotion row + NOTIFY
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

    assert core.evaluate_demotion("stale_carry", [3]) is False  # one window: no demotion
    assert core.evaluate_demotion("stale_carry", [3, 1]) is False  # second window < 2
    assert not log.exists()
    assert core.evaluate_demotion("stale_carry", [3, 2]) is True  # two consecutive windows >= 2
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
        core.evaluate_demotion("stale_carry", [3, 2]) is False
    )  # an advisory check is never re-demoted
    assert len(fr.read_rows(log)) == 1


# mutation-probe: tools/mechanized_checks/core.py:267 drop the since-promotion window filter
def test_rejected_windows_count_arcs_observed_since_promotion():
    early = "2026-09-01T00:00:00Z"  # before promotion: its arc belongs to no window
    rows = [
        _row(99, "no_finding", ts=early),
        _row(99, "finding", n=2, ts=early),
        _row(99, "finding_adjudication", n=2, ts=early, disposition="rejected"),
    ]
    rows += [_row(a, "no_finding") for a in range(45)]
    rows += [_row(a, "finding", n=2) for a in (3, 5, 25, 30, 41)]
    rows += [_row(a, "finding_adjudication", n=2, disposition="rejected") for a in (3, 5, 25, 30)]
    rows += [
        _row(7, "finding", n=2, producer="cited_symbol_exists"),
        _row(
            7, "finding_adjudication", n=2, disposition="rejected", producer="cited_symbol_exists"
        ),
    ]
    # 45 arcs -> two complete 20-arc windows; arc 41's finding sits in the incomplete third
    assert core.rejected_windows(rows, "stale_carry", since=PROMOTED) == [2, 2]


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

    with runner.commit_subject(repo, head, pr_body=lambda repo, ref: "body") as replayed:
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


def test_replay_measures_each_arc_once(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for n in range(3):
        (repo / "a.md").write_text(f"{n}\n")
        _git(repo, "add", "a.md")
        _git(repo, "commit", "-qm", f"feat: step {n} (#{n + 1})")
    monkeypatch.setattr(core, "WINDOW", 2)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "gate.jsonl")
    check = Counting("stale_carry")

    def run() -> core.ReplayVerdict:
        return runner.replay(repo, check, lane_id="lane-a", ref="HEAD", pr_body=lambda r, ref: None)

    assert run() == run() == core.Measured((False, False))
    assert check.seen == [("a.md",), ("a.md",)]  # two arcs, each measured by the first replay only


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
