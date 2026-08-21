"""Hermetic tests for tools/lanes_verify.py (U-HE-05, spec §8.1 / §0.3). Zero subprocesses
reach a real test: `run_row` takes an injected runner, and coverage reads a tmp log."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lanes_verify as lv


def _row(tag="phase0", art="pytest:tools/test_x.py::t", mp=False, skips=()):
    return lv.Row("C-HE-99", art, tag, "local + CI", mp, tuple(skips))


class _P:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


def test_manifest_rows_well_formed():
    assert lv.MANIFEST, "manifest is empty"
    for r in lv.MANIFEST:
        assert r.tag in lv.TAGS, r
        assert r.artifact.split(":", 1)[0] in lv.KINDS, r
        assert set(r.skip_reasons) <= set(lv.ALLOWED_SKIP_REASONS), r
    assert len({r.artifact for r in lv.MANIFEST}) == len(lv.MANIFEST), "duplicate artifact"


def test_manifest_artifacts_exist_at_head():
    """A pytest/shell row names a file that exists; a `just:` row names a real recipe."""
    justfile = (lv.REPO / "justfile").read_text()
    for r in lv.MANIFEST:
        kind, _, target = r.artifact.partition(":")
        if kind in ("pytest", "shell"):
            assert (lv.REPO / target.split("::")[0].split()[0]).exists(), r.artifact
        elif kind == "just":
            assert f"\n{target.split()[0]}:" in justfile, r.artifact


def test_phase0_skip_counts_as_fail():
    def fake_run(cmd, **kw):
        return _P(0, "1 skipped\nSKIPPED [1] x.py:1: docker-daemon-absent\n")

    res = lv.run_row(_row(tag="env", skips=("docker-daemon-absent",)), runner=fake_run)
    assert res.status == "skip" and res.reason == "docker-daemon-absent"
    assert lv.phase0_verdict([lv.Result(_row(tag="phase0"), "skip", "docker-daemon-absent")]) == 1
    assert lv.phase0_verdict([lv.Result(_row(tag="phase0"), "pass")]) == 0
    assert lv.phase0_verdict([lv.Result(_row(tag="phase0"), "live")]) == 1


def test_unknown_skip_reason_is_fail():
    def fake_run(cmd, **kw):
        return _P(0, "SKIPPED [1] x.py:1: slow\n")

    assert (
        lv.run_row(_row(tag="env", skips=("docker-daemon-absent",)), runner=fake_run).status
        == "fail"
    )


def test_nonzero_exit_is_fail_even_with_a_legal_skip():
    def fake_run(cmd, **kw):
        return _P(1, "SKIPPED [1] x.py:1: docker-daemon-absent\n1 failed\n")

    assert (
        lv.run_row(_row(tag="env", skips=("docker-daemon-absent",)), runner=fake_run).status
        == "fail"
    )


def test_run_row_passes_the_expected_command_from_repo_root():
    seen: list = []

    def fake_run(cmd, **kw):
        seen.append((cmd, kw.get("cwd")))
        return _P(0, "1 passed\n")

    assert lv.run_row(_row(art="pytest:tools/test_x.py::t"), runner=fake_run).status == "pass"
    assert seen == [(["uv", "run", "pytest", "-q", "-rs", "tools/test_x.py::t"], lv.REPO)]


def test_just_args_tokenized_and_placeholder_is_live():
    assert lv._command(_row(tag="phase1", art="just:main-protection-verify")) == [
        "just",
        "main-protection-verify",
    ]
    assert lv._command(_row(tag="phase1", art="just:lanes-pilot-report <run-id>")) is None
    assert lv._command(_row(tag="phase0", art="shell:tools/hooks/test_x.sh")) == [
        "bash",
        "tools/hooks/test_x.sh",
    ]
    assert lv._command(_row(tag="operator-gated", art="live:operator answers")) is None
    live = lv.run_row(_row(tag="operator-gated", art="live:operator answers"))
    assert live.status == "live"


def _sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


@pytest.fixture
def repo(tmp_path: Path, monkeypatch) -> Path:
    """A throwaway REPO: source modules, annotated test files (each probing its sibling
    `x.py` by default), a shell suite and its sibling script."""
    monkeypatch.setattr(lv, "REPO", tmp_path)
    (tmp_path / "tools" / "hooks").mkdir(parents=True)
    for mod in ("x", "y", "z", "a", "b", "src"):
        (tmp_path / "tools" / f"{mod}.py").write_text("def f():\n    return 1\n")
    (tmp_path / "tools" / "test_x.py").write_text("# mutation-probe: a\ndef t(): pass\n")
    (tmp_path / "tools" / "hooks" / "c.sh").write_text("x=1\n")
    (tmp_path / "tools" / "hooks" / "test_c.sh").write_text("true\n")
    return tmp_path


# mutation-probe: drop the shell-annotation scan (explicit-target branch) in required_probes()
def test_shell_row_explicit_annotation_names_hyphenated_probe_target(repo: Path):
    """A shell suite whose sibling default is underivable (hyphenated source name, U-HE-26)
    names its probed file with a file-level red-first-form annotation; an unannotated suite
    keeps the sibling default."""
    (repo / "tools" / "hooks" / "permission-guard.sh").write_text("x=1\n")
    (repo / "tools" / "hooks" / "test_permission_guard.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# mutation-probe: tools/hooks/permission-guard.sh:410-412 deny predicate\n"
        "true\n"
    )
    row = _row(art="shell:tools/hooks/test_permission_guard.sh", mp=True)
    assert lv.required_probes(row) == [
        ("tools/hooks/test_permission_guard.sh", "tools/hooks/permission-guard.sh")
    ]
    unannot = _row(art="shell:tools/hooks/test_c.sh", mp=True)
    assert lv.required_probes(unannot) == [("tools/hooks/test_c.sh", "tools/hooks/c.sh")]
    # codex r8 P3: EVERY annotation is required, not just the first -- a suite probing two
    # source files owes two pins.
    (repo / "tools" / "hooks" / "other-module.sh").write_text("y=1\n")
    (repo / "tools" / "hooks" / "test_permission_guard.sh").write_text(
        "#!/usr/bin/env bash\n"
        "# mutation-probe: tools/hooks/permission-guard.sh:410-412 deny predicate\n"
        "# mutation-probe: tools/hooks/other-module.sh:1 second annotated target\n"
        "true\n"
    )
    assert lv.required_probes(row) == [
        ("tools/hooks/test_permission_guard.sh", "tools/hooks/permission-guard.sh"),
        ("tools/hooks/test_permission_guard.sh", "tools/hooks/other-module.sh"),
    ]


def _nodes(gaps) -> list[str]:
    return [n.split(" [probe of ")[0] for _, n in gaps]


def _entry(repo: Path, test: str, file: str | None = None, rc: int = 0, **over) -> str:
    """A probe-log line as `mutation_probe.log_result` writes it, digests from the repo. The
    probed `file` defaults to the test's sibling module (the annotation's default target)."""
    tf = test.split()
    tf = tf[tf.index("pytest") + 1 :] if "pytest" in tf else tf[1:]
    tfile = next(x for x in tf if not x.startswith("-") and (".py" in x or x.endswith(".sh")))
    tfile = tfile.split("::")[0]
    file = file or lv.default_probe_target(lv._relative(tfile))
    e = {
        "ts": "2026-08-19T00:00:00Z",
        "file": file,
        "lines": "1",
        "test": test,
        "rc": rc,
        "head": "h" * 40,
        "target_sha": over.get("target_sha") or _sha16(repo / file),
        "test_sha": _sha16(repo / lv._relative(tfile)),
    }
    e.update(over)
    return json.dumps(e) + "\n"


# mutation-probe: drop the `if e.get("rc") != 0: continue` guard in _pinned_nodeids()
def test_coverage_gap_when_probe_never_pinned(repo: Path, monkeypatch):
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::t")])
    gaps = lv.coverage_gaps(log)
    assert _nodes(gaps) == ["tools/test_x.py::t"]
    # a PROBE FAILED verdict (rc 1) is not a pin
    log.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::t", rc=1))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]
    log.write_text(log.read_text() + _entry(repo, "uv run pytest -q tools/test_x.py::t"))
    assert lv.coverage_gaps(log) == []


# mutation-probe: drop the `if not _pin_is_live(e, target): continue` guard in _pinned_nodeids()
def test_pin_is_stale_once_the_source_or_the_test_changes(repo: Path, monkeypatch):
    """codex R2 P2: a PINNED verdict is evidence for the bytes it measured. Revert the guarded
    line (source changes) or weaken the witness (test changes) and the pin no longer counts;
    an entry without digests (pre-digest format) never counts."""
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::t")])
    log.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::t"))
    assert lv.coverage_gaps(log) == []
    (repo / "tools" / "x.py").write_text("def f():\n    return 2\n")  # the source moved
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]
    (repo / "tools" / "x.py").write_text("def f():\n    return 1\n")
    assert lv.coverage_gaps(log) == []
    (repo / "tools" / "test_x.py").write_text("# mutation-probe: a\ndef t(): assert 1\n")
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]  # the test moved
    (repo / "tools" / "test_x.py").write_text("# mutation-probe: a\ndef t(): pass\n")
    log.write_text(json.dumps({"test": "uv run pytest -q tools/test_x.py::t", "rc": 0}) + "\n")
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]  # no digests
    log.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::t", target_sha="0" * 16))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]


def test_pinned_nodeid_parser_skips_flags_and_normalizes_absolute_paths(repo: Path):
    log = repo / "mp.jsonl"
    (repo / "tools" / "test_a.py").write_text("def t_a(): pass\n")
    (repo / "tools" / "test_b.py").write_text("def t_b(): pass\n")
    log.write_text(
        _entry(repo, "uv run pytest -q -p no:cacheprovider tools/test_a.py::t_a -x")
        + _entry(repo, f"python -m pytest {repo}/tools/test_b.py::t_b")
        + _entry(repo, "bash tools/hooks/test_c.sh", file="tools/hooks/c.sh")
        + _entry(repo, "bash tools/hooks/test_c.sh", file="tools/hooks/c.sh", rc=2)
    )
    assert lv._pinned_nodeids(log) == {
        ("tools/test_a.py::t_a", "tools/a.py"),
        ("tools/test_b.py::t_b", "tools/b.py"),
        ("tools/hooks/test_c.sh", "tools/hooks/c.sh"),
    }


def test_file_level_row_requires_every_annotation_exactly(repo: Path, monkeypatch):
    """One pinned test in a file must NOT count as coverage for the file's other probes."""
    (repo / "tools" / "test_y.py").write_text(
        "# mutation-probe: a\ndef test_a(): pass\n\n"
        "# mutation-probe: b\n@pytest.mark.x\ndef test_b(): pass\n\n"
        "def test_unannotated(): pass\n"
    )
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_y.py")])
    log = repo / "mp.jsonl"
    log.write_text(_entry(repo, "uv run pytest tools/test_y.py::test_a -q"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_y.py::test_b"]
    log.write_text(log.read_text() + _entry(repo, "uv run pytest tools/test_y.py::test_b -q"))
    assert lv.coverage_gaps(log) == []
    # a whole-file run is NOT per-probe evidence
    log.write_text(_entry(repo, "uv run pytest tools/test_y.py -q"))
    assert len(lv.coverage_gaps(log)) == 2


def test_file_level_row_with_no_annotations_is_a_gap_not_a_vacuous_pass(repo: Path, monkeypatch):
    """codex R3 P2: delete every `# mutation-probe:` comment and the gate must NOT go green."""
    (repo / "tools" / "test_z.py").write_text("def test_a(): pass\n")
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_z.py")])
    assert _nodes(lv.coverage_gaps(repo / "mp.jsonl")) == [
        "tools/test_z.py::<no mutation-probe annotations>"
    ]
    # the production manifest: every file-level probe row has at least one annotation
    monkeypatch.undo()
    for r in lv.MANIFEST:
        if r.mutation_probe and r.artifact.startswith("pytest:") and "::" not in r.artifact:
            nodes = [n for n, _ in lv.required_probes(r)]
            assert "<no mutation-probe annotations>" not in "".join(nodes), r


def test_a_probe_of_the_test_file_itself_or_a_missing_source_is_not_a_pin(repo: Path, monkeypatch):
    """codex R3 P2: the probed `file` must be an existing source file, never the witness."""
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::t")])
    log.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::t", file="tools/test_x.py"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]
    log.write_text(
        _entry(
            repo, "uv run pytest -q tools/test_x.py::t", file="tools/gone.py", target_sha="x" * 16
        )
    )
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::t"]


def test_file_level_row_for_a_not_yet_landed_file_is_a_gap(repo: Path, monkeypatch):
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_future.py")])
    assert _nodes(lv.coverage_gaps(repo / "mp.jsonl")) == ["tools/test_future.py"]


def test_shell_probe_rows_can_be_covered(repo: Path, monkeypatch):
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="shell:tools/hooks/test_c.sh")])
    log = repo / "mp.jsonl"
    assert _nodes(lv.coverage_gaps(log)) == ["tools/hooks/test_c.sh"]
    log.write_text(_entry(repo, "bash tools/hooks/test_c.sh", file="tools/hooks/c.sh"))
    assert lv.coverage_gaps(log) == []


def test_annotation_binds_the_pin_to_the_annotated_file(repo: Path, monkeypatch):
    """codex R3/R4 P2: a pin is credited to (test node, probed file). The default target is the
    test's sibling module; `# mutation-probe(<path>):` names another. A pin of an unrelated
    file under the same test node is NOT coverage."""
    (repo / "tools" / "test_w.py").write_text(
        "# mutation-probe: default target\ndef test_d(): pass\n\n"
        "# mutation-probe(tools/src.py): explicit target\ndef test_e(): pass\n\n"
        "# mutation-probe: tools/src.py:12-14 the red-first form names the target too\n"
        "def test_f(): pass\n"
    )
    (repo / "tools" / "w.py").write_text("def f():\n    return 1\n")
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_w.py")])
    assert lv.required_probes(lv.MANIFEST[0]) == [
        ("tools/test_w.py::test_d", "tools/w.py"),
        ("tools/test_w.py::test_e", "tools/src.py"),
        ("tools/test_w.py::test_f", "tools/src.py"),
    ]
    log = repo / "mp.jsonl"
    # pins of the WRONG file do not count, even under the right test node
    log.write_text(
        _entry(repo, "uv run pytest tools/test_w.py::test_d -q", file="tools/src.py")
        + _entry(repo, "uv run pytest tools/test_w.py::test_e -q", file="tools/w.py")
    )
    assert _nodes(lv.coverage_gaps(log)) == [
        "tools/test_w.py::test_d",
        "tools/test_w.py::test_e",
        "tools/test_w.py::test_f",
    ]
    assert all("[probe of tools/" in n for _, n in lv.coverage_gaps(log))
    log.write_text(
        _entry(repo, "uv run pytest tools/test_w.py::test_d -q", file="tools/w.py")
        + _entry(repo, "uv run pytest tools/test_w.py::test_e -q", file="tools/src.py")
        + _entry(repo, "uv run pytest tools/test_w.py::test_f -q", file="tools/src.py")
    )
    assert lv.coverage_gaps(log) == []
    # a node-level row honours the node's own explicit target
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_w.py::test_e")])
    assert lv.required_probes(lv.MANIFEST[0]) == [("tools/test_w.py::test_e", "tools/src.py")]
    assert lv.coverage_gaps(log) == []
    assert lv.default_probe_target("tools/hooks/test_loop_lib.sh") == "tools/hooks/loop_lib.sh"


def test_rows_not_marked_mutation_probe_require_nothing():
    assert lv.required_probes(_row(mp=False, art="pytest:tools/test_x.py")) == []
    assert lv.required_probes(_row(mp=False, art="shell:tools/hooks/test_x.sh")) == []


def test_main_modes_and_exit_codes(repo: Path, monkeypatch, capsys):
    monkeypatch.setattr(
        lv, "MANIFEST", [_row(tag="phase0", mp=True, art="pytest:tools/test_x.py::t")]
    )
    monkeypatch.setattr(lv, "PROBE_LOG", Path("/nonexistent/mp.jsonl"))
    assert lv.main(["coverage"]) == 1
    assert "UNPROBED C-HE-99 tools/test_x.py::t" in capsys.readouterr().out
    # the log path is resolved at CALL time: a pinned row in the (patched) log turns it green
    pinned = repo / "mp.jsonl"
    pinned.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::t"))
    monkeypatch.setattr(lv, "PROBE_LOG", pinned)
    assert lv.main(["coverage"]) == 0
    monkeypatch.setattr(lv, "run_row", lambda r, **k: lv.Result(r, "skip", "gh-auth-absent"))
    assert lv.main(["phase0"]) == 1  # a phase0 skip is NOT a pass
    assert lv.main(["verify"]) == 0  # verify reds only on fail
    assert lv.main(["bogus"]) == 2


@pytest.mark.parametrize("mode", ["verify", "phase0"])
def test_live_rows_are_reported_never_counted_as_pass(mode, monkeypatch, capsys):
    monkeypatch.setattr(
        lv, "MANIFEST", [_row(tag="phase0", art="live:operator-gated step"), _row(tag="phase0")]
    )
    monkeypatch.setattr(
        lv,
        "run_row",
        lambda r, **k: (
            lv.Result(r, "pass") if r.artifact.startswith("pytest") else lv.Result(r, "live", "x")
        ),
    )
    rc = lv.main([mode])
    out = capsys.readouterr().out
    assert "LIVE " in out and "PASS " in out
    assert rc == (1 if mode == "phase0" else 0)
