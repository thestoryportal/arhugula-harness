"""Hermetic tests for tools/lanes_verify.py (U-HE-05, spec §8.1 / §0.3). Zero subprocesses
reach a real test: `run_row` takes an injected runner, and coverage reads a tmp log."""

from __future__ import annotations

import hashlib
import json
import re
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
    """A pytest/shell row names a file that exists; a `just:` row names a real recipe.

    A recipe declaration is `name:` OR `name <param…>:` — a substring search for `name:`
    alone reports every PARAMETERIZED recipe as missing (`lanes-pilot-report <run-id>`,
    U-HE-37), which is a false RED on a row whose artifact does exist.
    """
    justfile = (lv.REPO / "justfile").read_text()
    for r in lv.MANIFEST:
        kind, _, target = r.artifact.partition(":")
        if kind in ("pytest", "shell"):
            assert (lv.REPO / target.split("::")[0].split()[0]).exists(), r.artifact
        elif kind == "just":
            name = re.escape(target.split()[0])
            assert re.search(rf"^{name}( +[^:\n]*)?:", justfile, re.M), r.artifact


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
    # the producer's own target grammar (codex u-sr-09 r7): the FIRST collection target's
    # file is the artifact this row digests, never an option's value
    targets = lv.pin_scope.pytest_targets(tf) if "pytest" in tf else tf[1:2]
    tfile = targets[0].split("::")[0]
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


def _block_entry(
    repo: Path, test: str, lines: str, node: str | None, file: str = "tools/x.py", **over
) -> str:
    """A U-SR-09 block-scoped row as `mutation_probe.log_result` writes it: `pin_scope` block,
    `block_sha` over the probed lines of `file`, `test_scope` slice (the test file minus its
    other top-level tests, cut for `node`) or artifact."""
    a, b = lv.pin_scope.parse_line_range(lines)
    tfile = next(t for t in test.split() if ".py" in t or t.endswith(".sh")).split("::")[0]
    body = lv.pin_scope.test_slice_digest((repo / tfile).read_text(), node) if node else None
    fields = {
        "lines": lines,
        "pin_scope": lv.pin_scope.PIN_SCOPE_BLOCK,
        "block_sha": lv.pin_scope.block_digest((repo / file).read_text(), a, b),
        "test_scope": lv.pin_scope.TEST_SCOPE_SLICE if body else lv.pin_scope.TEST_SCOPE_ARTIFACT,
        "test_slice_sha": body,
    }
    fields.update(over)  # a caller's override wins (an unknown scope, a missing digest)
    return _entry(repo, test, file=file, **fields)


# mutation-probe: drop the `if scope == pin_scope.PIN_SCOPE_FILE:` legacy arm in _pin_is_live()
def test_block_scoped_pin_survives_unrelated_edits_and_stales_on_the_block_or_body(
    repo: Path, monkeypatch
):
    """U-SR-09 b1 ([B] F7/c1): the pin binds the probed BLOCK and the judging test's SLICE (the
    file minus its other top-level tests), so an edit elsewhere in the source or in a sibling
    test keeps it live; the block, the test body, or the test's imports moving stales it; a
    legacy (scope-less) row keeps the whole-file rule."""
    src, tst = repo / "tools" / "x.py", repo / "tools" / "test_x.py"
    src.write_text("import os\n\n\ndef f():\n    return 1\n\n\ndef g():\n    return 2\n")
    tst.write_text(
        "# mutation-probe: a\ndef test_f():\n    assert f() == 1\n\n\n"
        "def test_g():\n    assert g() == 2\n"
    )
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::test_f")])
    log.write_text(_block_entry(repo, "uv run pytest -q tools/test_x.py::test_f", "5", "test_f"))
    assert lv.coverage_gaps(log) == []
    # an unrelated edit ABOVE the block shifts its line but not its bytes: still live
    src.write_text(
        "import os\nimport sys\n\n\ndef f():\n    return 1\n\n\ndef g():\n    return 2\n"
    )
    assert lv.coverage_gaps(log) == []
    # an unrelated edit BELOW the block: still live
    src.write_text(src.read_text().replace("return 2", "return 3"))
    assert lv.coverage_gaps(log) == []
    # a SIBLING test edited: still live (slice scope)
    tst.write_text(tst.read_text().replace("assert g() == 2", "assert g() == 3"))
    assert lv.coverage_gaps(log) == []
    # the block itself edited: stale
    src.write_text(src.read_text().replace("return 1", "return 0"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    src.write_text(src.read_text().replace("return 0", "return 1"))
    assert lv.coverage_gaps(log) == []
    # the judging test's body edited: stale
    tst.write_text(tst.read_text().replace("assert f() == 1", "assert f() == 1  # weaker?"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    tst.write_text(tst.read_text().replace("  # weaker?", ""))
    assert lv.coverage_gaps(log) == []
    # the test's IMPORTS edited (codex u-sr-09 r1: a swapped import hollows the test): stale
    tst.write_text("import os\n" + tst.read_text())
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    tst.write_text(tst.read_text().removeprefix("import os\n"))
    assert lv.coverage_gaps(log) == []
    # the probed block DUPLICATED elsewhere in the source: stale (no copy may vouch)
    src.write_text(src.read_text() + "\n\ndef h():\n    return 1\n")
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    src.write_text(src.read_text().removesuffix("\n\ndef h():\n    return 1\n"))
    assert lv.coverage_gaps(log) == []
    # a legacy row (no pin_scope) still lives by the whole-file rule -- the 1,300-row log
    # written before U-SR-09 is not mass-staled by the landing
    log.write_text(_entry(repo, "uv run pytest -q tools/test_x.py::test_f"))
    assert lv.coverage_gaps(log) == []
    src.write_text(src.read_text().replace("return 3", "return 2"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    # an unknown scope, or a block row missing its digest, never counts
    cmd = "uv run pytest -q tools/test_x.py::test_f"
    log.write_text(_block_entry(repo, cmd, "5", "test_f", pin_scope="quantum"))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]
    log.write_text(_block_entry(repo, cmd, "5", "test_f", block_sha=None))
    assert _nodes(lv.coverage_gaps(log)) == ["tools/test_x.py::test_f"]


def test_annotation_binds_across_a_multiline_decorator(repo: Path):
    """codex u-sr-09 r5: an annotation above `@pytest.mark.parametrize(` spanning several
    lines names that test; one above a non-test `def` binds nothing."""
    (repo / "tools" / "test_x.py").write_text(
        "import pytest\n\n\n"
        "# mutation-probe: drop the glob arm\n"
        "@pytest.mark.parametrize(\n"
        '    ("a", "b"),\n'
        "    [(1, 2)],\n"
        ")\n"
        "def test_p(a, b):\n    assert a < b\n\n\n"
        "# mutation-probe: bound to nothing\n"
        "def helper():\n    pass\n\n\n"
        "def test_q():\n    assert True\n"
    )
    assert lv._annotations(repo / "tools" / "test_x.py") == [("test_p", None)]
    # codex u-sr-09 r7: an `async def test_*` binds its own annotation; the bridge never
    # walks through it to the next test
    (repo / "tools" / "test_y.py").write_text(
        "# mutation-probe: a\nasync def test_a():\n    pass\n\n\n"
        "# mutation-probe: b\ndef test_b():\n    pass\n"
    )
    assert lv._annotations(repo / "tools" / "test_y.py") == [("test_a", None), ("test_b", None)]
    # codex u-sr-09 r8: a statement between the annotation and the next test ends the
    # bridge -- the annotation binds nothing rather than the later test
    (repo / "tools" / "test_z.py").write_text(
        "# mutation-probe: orphaned\nX = 1\n\n\ndef test_later():\n    pass\n\n\n"
        "# mutation-probe: orphaned too\nclass K:\n    pass\n\n\ndef test_last():\n    pass\n"
    )
    assert lv._annotations(repo / "tools" / "test_z.py") == []
    # codex u-sr-09 r9: two STACKED annotations above one test each bind it (two targets)
    (repo / "tools" / "test_w.py").write_text(
        "# mutation-probe(tools/a.py): first\n# mutation-probe(tools/b.py): second\n"
        "def test_two():\n    pass\n"
    )
    assert lv._annotations(repo / "tools" / "test_w.py") == [
        ("test_two", "tools/a.py"),
        ("test_two", "tools/b.py"),
    ]
    row = _row(mp=True, art="pytest:tools/test_w.py")
    assert lv.required_probes(row) == [
        ("tools/test_w.py::test_two", "tools/a.py"),
        ("tools/test_w.py::test_two", "tools/b.py"),
    ]
    row = _row(mp=True, art="pytest:tools/test_x.py")
    assert lv.required_probes(row) == [("tools/test_x.py::test_p", "tools/x.py")]


def test_block_scoped_pin_on_a_crlf_source_is_live(repo: Path, monkeypatch):
    """codex u-sr-09 r4: the producer digests the block from bytes (CRLF kept); the consumer
    must decode bytes too -- `read_text()`'s universal newlines would never match."""
    src = repo / "tools" / "x.py"
    src.write_bytes(b"def f():\r\n    return 1\r\n")
    (repo / "tools" / "test_x.py").write_text(
        "# mutation-probe: a\ndef test_f():\n    assert f() == 1\n"
    )
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="pytest:tools/test_x.py::test_f")])
    a, b = 2, 2
    row = _entry(
        repo,
        "uv run pytest -q tools/test_x.py::test_f",
        lines="2",
        pin_scope=lv.pin_scope.PIN_SCOPE_BLOCK,
        block_sha=lv.pin_scope.block_digest(src.read_bytes().decode("utf-8"), a, b),
        test_scope=lv.pin_scope.TEST_SCOPE_ARTIFACT,
        test_slice_sha=None,
    )
    log.write_text(row)
    assert lv.coverage_gaps(log) == []


def test_block_scoped_pin_with_artifact_scope_binds_the_whole_shell_suite(repo: Path, monkeypatch):
    """A shell suite has no `def` to bind, so its block pin carries `test_scope` artifact: the
    probed block is content-anchored as before, but ANY edit to the script stales the pin."""
    hk = repo / "tools" / "hooks"
    hk.mkdir(parents=True, exist_ok=True)
    (hk / "y.sh").write_text("#!/usr/bin/env bash\necho 1\necho 2\n")
    (hk / "test_y.sh").write_text("#!/usr/bin/env bash\nbash tools/hooks/y.sh | grep -q 2\n")
    log = repo / "mp.jsonl"
    monkeypatch.setattr(lv, "MANIFEST", [_row(mp=True, art="shell:tools/hooks/test_y.sh")])
    log.write_text(
        _block_entry(repo, "bash tools/hooks/test_y.sh", "3", None, file="tools/hooks/y.sh")
    )
    assert lv.coverage_gaps(log) == []
    (hk / "y.sh").write_text("#!/usr/bin/env bash\n# a comment above the block\necho 1\necho 2\n")
    assert lv.coverage_gaps(log) == []  # the block moved down: still present verbatim
    (hk / "test_y.sh").write_text("#!/usr/bin/env bash\nbash tools/hooks/y.sh | grep -q 2  # x\n")
    assert _nodes(lv.coverage_gaps(log)) == ["tools/hooks/test_y.sh"]  # the script changed


def test_pinned_nodeid_parser_uses_the_producers_target_grammar(repo: Path):
    """codex u-sr-09 r7: `--ignore tools/helper.py a.py::t` names a.py, not helper.py; two
    targets name nothing (the producer bound nothing either)."""
    log = repo / "mp.jsonl"
    log.write_text(
        _entry(repo, "uv run pytest -q --ignore tools/helper.py tools/test_x.py::t")
        + _entry(repo, "uv run pytest -q tools/test_x.py::t tools/test_y.py")
    )
    assert lv._pinned_nodeids(log) == {("tools/test_x.py::t", "tools/x.py")}


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


def test_probe_result_verdict_fail_closed(tmp_path):
    """C-HE-22 pilot gate (U-HE-35 codex r10 P1): absent and RED refuse; only the LATEST
    probe-result row's GREEN admits (an old GREEN superseded by a RED must not)."""
    import json as _json

    log = tmp_path / "gate-log.jsonl"
    # absent: the probe never completed a run
    verdict, why = lv.probe_result_verdict(log)
    assert verdict == "absent" and "not run" in why

    def row(kind: str, verdict_value: str) -> str:
        return _json.dumps(
            {
                "finding_type": kind,
                "observed_evidence": _json.dumps({"verdict": verdict_value, "why": "w"}),
            }
        )

    # sample rows never satisfy the gate; the latest RESULT row decides
    log.write_text("\n".join([row("probe-sample", "GREEN"), row("probe-result", "GREEN")]) + "\n")
    assert lv.probe_result_verdict(log)[0] == "GREEN"
    with log.open("a") as fh:
        fh.write(row("probe-result", "RED") + "\n")
    assert lv.probe_result_verdict(log)[0] == "RED"  # the newer RED supersedes


def test_pilot_gate_cli_dispatch(monkeypatch):
    """merge-gate witness P2: the REAL consumer path is `just pilot-gate-check` ->
    main(["pilot-gate"]) — exercise the dispatch itself: exit 0 only on GREEN, and the
    branch RETURNS (a dropped return would fall through to the MANIFEST runner, which
    now contains the just:pilot-gate-check row itself — recursion)."""
    ran = []
    monkeypatch.setattr(lv, "run_row", lambda row, **k: ran.append(row) or lv.Result(row, "pass"))
    for verdict, rc in (("GREEN", 0), ("RED", 1), ("absent", 1)):
        monkeypatch.setattr(lv, "probe_result_verdict", lambda log_path=None, v=verdict: (v, "w"))
        assert lv.main(["pilot-gate"]) == rc
    assert ran == []  # dispatch returned — never fell through to the manifest runner
