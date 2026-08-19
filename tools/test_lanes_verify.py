"""Hermetic tests for tools/lanes_verify.py (U-HE-05, spec §8.1 / §0.3). Zero subprocesses
reach a real test: `run_row` takes an injected runner, and coverage reads a tmp log."""

from __future__ import annotations

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


# mutation-probe: drop the `if e.get("rc") != 0: continue` guard in _pinned_nodeids()
def test_coverage_gap_when_probe_never_pinned(tmp_path: Path, monkeypatch):
    log = tmp_path / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::t")])
    gaps = lv.coverage_gaps(log)
    assert gaps and gaps[0][1] == "tools/test_x.py::t"
    # a PROBE FAILED verdict (rc 1) is not a pin
    log.write_text(json.dumps({"test": "uv run pytest -q tools/test_x.py::t", "rc": 1}) + "\n")
    assert lv.coverage_gaps(log) == [(lv.MANIFEST[0], "tools/test_x.py::t")]
    log.write_text(
        log.read_text()
        + json.dumps({"test": "uv run pytest -q tools/test_x.py::t", "rc": 0})
        + "\n"
    )
    assert lv.coverage_gaps(log) == []


def test_pinned_nodeid_parser_skips_flags_and_normalizes_absolute_paths(tmp_path: Path):
    log = tmp_path / "mp.jsonl"
    entries = [
        {"test": "uv run pytest -q -p no:cacheprovider tools/test_a.py::t_a -x", "rc": 0},
        {"test": f"python -m pytest {lv.REPO}/tools/test_b.py::t_b", "rc": 0},
        {"test": "bash tools/hooks/test_c.sh", "rc": 0},
        {"test": "bash tools/hooks/test_failed.sh", "rc": 2},
    ]
    log.write_text("".join(json.dumps(e) + "\n" for e in entries))
    assert lv._pinned_nodeids(log) == {
        "tools/test_a.py::t_a",
        "tools/test_b.py::t_b",
        "tools/hooks/test_c.sh",
    }


def test_file_level_row_requires_every_annotation_exactly(tmp_path: Path, monkeypatch):
    """One pinned test in a file must NOT count as coverage for the file's other probes."""
    monkeypatch.setattr(lv, "REPO", tmp_path)
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "test_y.py").write_text(
        "# mutation-probe: a\ndef test_a(): pass\n\n"
        "# mutation-probe: b\n@pytest.mark.x\ndef test_b(): pass\n\n"
        "def test_unannotated(): pass\n"
    )
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_y.py")])
    log = tmp_path / "mp.jsonl"
    log.write_text(json.dumps({"test": "uv run pytest tools/test_y.py::test_a -q", "rc": 0}) + "\n")
    assert [n for _, n in lv.coverage_gaps(log)] == ["tools/test_y.py::test_b"]
    log.write_text(
        log.read_text()
        + json.dumps({"test": "uv run pytest tools/test_y.py::test_b -q", "rc": 0})
        + "\n"
    )
    assert lv.coverage_gaps(log) == []
    # a whole-file run is NOT per-probe evidence
    log.write_text(json.dumps({"test": "uv run pytest tools/test_y.py -q", "rc": 0}) + "\n")
    assert len(lv.coverage_gaps(log)) == 2


def test_file_level_row_for_a_not_yet_landed_file_is_a_gap(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(lv, "REPO", tmp_path)
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_future.py")])
    assert [n for _, n in lv.coverage_gaps(tmp_path / "mp.jsonl")] == ["tools/test_future.py"]


def test_shell_probe_rows_can_be_covered(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="shell:tools/hooks/test_loop_lib.sh")])
    log = tmp_path / "mp.jsonl"
    assert [n for _, n in lv.coverage_gaps(log)] == ["tools/hooks/test_loop_lib.sh"]
    log.write_text(json.dumps({"test": "bash tools/hooks/test_loop_lib.sh", "rc": 0}) + "\n")
    assert lv.coverage_gaps(log) == []


def test_rows_not_marked_mutation_probe_require_nothing():
    assert lv.required_probes(_row(mp=False, art="pytest:tools/test_x.py")) == []
    assert lv.required_probes(_row(mp=False, art="shell:tools/hooks/test_x.sh")) == []


def test_main_modes_and_exit_codes(monkeypatch, capsys):
    monkeypatch.setattr(
        lv, "MANIFEST", [_row(tag="phase0", mp=True, art="pytest:tools/test_x.py::t")]
    )
    monkeypatch.setattr(lv, "PROBE_LOG", Path("/nonexistent/mp.jsonl"))
    assert lv.main(["coverage"]) == 1
    assert "UNPROBED C-HE-99 tools/test_x.py::t" in capsys.readouterr().out
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
