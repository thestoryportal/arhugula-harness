"""Hermetic tests for tools/merge_gate_log.py (U-HE-13, C-HE-23 §2). Every write goes to
tmp_path (an autouse fixture redirects `HARNESS_GATE_LOG` and the module's md path), no
subprocess reaches a real reviewer, and the only git calls are read-only `rev-parse` /
`merge-base` / `diff` against THIS checkout for the binding test."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import merge_gate_log as mgl
import review_wrapper_common as rw

H, B, D = "a" * 40, "b" * 40, "c" * 64
LENS = "merge-gate-concurrency"


@pytest.fixture(autouse=True)
def _isolated(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HARNESS_GATE_LOG", str(tmp_path / "unused-gate-log.jsonl"))
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "unused-gate-log.jsonl")
    monkeypatch.setattr(mgl, "GATE_LOG_MD", tmp_path / "unused-log.md")
    monkeypatch.delenv("HARNESS_ROUND_N", raising=False)
    monkeypatch.delenv("HARNESS_ARC_ID", raising=False)  # adjudicate's arc-binding input
    monkeypatch.setattr(mgl, "config_hash", lambda: "cfg")  # no CLI override exists (R5 P2)
    monkeypatch.setattr(mgl, "LENS_SCRATCH", tmp_path)  # `emit` reads verdict files only here


def _binding(lens: str = LENS, head: str = H) -> dict[str, str]:
    return {
        "head_sha": head,
        "base_sha": B,
        "diff_digest": D,
        "reviewer_identity": lens,
        "prompt_version": mgl.PROMPT_VERSION,
        "config_hash": "cfg",
    }


def _outcome(verdict: str, findings: list[dict] | None = None, lens: str = LENS, head: str = H):
    return rw.ReviewOutcome(verdict, mgl.CHANNEL, None, "", findings or [], _binding(lens, head))


def _emit(
    tmp_path: Path,
    pr: int = 1,
    verdict: str = "APPROVE",
    findings=None,
    lens=LENS,
    head=H,
    md=None,
    jl=None,
    **kw,
):
    return mgl.emit_gate_row(
        pr=pr,
        lens=lens,
        outcome=_outcome(verdict, findings, lens, head),
        lane_id="h-w-1",
        md_path=md or tmp_path / "log.md",
        jsonl_path=jl or tmp_path / "log.jsonl",
        **kw,
    )


# ---- write order + failure semantics -----------------------------------------------------


def test_approve_writes_a_no_finding_row_then_a_structured_md_line(tmp_path: Path):
    rows = _emit(tmp_path)
    assert [r["record_kind"] for r in rows] == ["no_finding"]
    assert rows[0]["producer"] == LENS and rows[0]["arc_id"] == "pr-1" and rows[0]["round_n"] == 1
    assert rows[0]["head_sha"] == H and rows[0]["base_sha"] == B and rows[0]["diff_digest"] == D
    md = (tmp_path / "log.md").read_text()
    assert md == f"| {rows[0]['ts']} | #1 | {H[:12]} | {LENS} | APPROVE | 0 finding(s) | r1 |\n"
    assert mgl.read_md_rows(tmp_path / "log.md") == [
        {
            "ts": rows[0]["ts"],
            "pr": 1,
            "head_sha": H[:12],
            "lens": LENS,
            "verdict": "APPROVE",
            "n_findings": 0,
            "round_n": 1,
        }
    ]


def test_block_writes_one_finding_row_per_finding_and_ids_are_minted_under_the_lock(tmp_path):
    fs = [
        {"severity": "P1", "location": "x.py:1", "message": "m1"},
        {"severity": "P2", "location": "x.py:1", "message": "m2"},
    ]
    rows = _emit(tmp_path, pr=2, verdict="BLOCK", findings=fs)
    assert [r["finding_type"] for r in rows] == ["terminal-block", "terminal-block"]
    assert len({r["finding_id"] for r in rows}) == 2  # same location twice -> distinct ids
    # a re-run at the same head mints NEW ids (never a per-invocation ordinal -> no core clash)
    again = _emit(tmp_path, pr=2, verdict="BLOCK", findings=fs)
    assert {r["finding_id"] for r in again}.isdisjoint({r["finding_id"] for r in rows})
    assert again[0]["round_n"] == 2


# mutation-probe: drop the `fr.append_observation(...)` warn-row call in the md OSError handler
def test_md_failure_leaves_the_jsonl_row_and_records_a_warn_finding(tmp_path: Path, capsys):
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)
    try:
        rows = _emit(tmp_path, md=ro / "sub" / "log.md")
    finally:
        ro.chmod(0o700)
    log = fr.read_rows(tmp_path / "log.jsonl")
    assert log[0]["finding_id"] == rows[0]["finding_id"]
    warn = [r for r in log if r.get("cause_attribution") == "markdown_write_failed"]
    assert len(warn) == 1 and warn[0]["severity"] == "warn"
    assert warn[0]["producer"] == LENS and warn[0]["lineage_claim"] == "wrapper"
    assert warn[0]["cause_attribution"] == "markdown_write_failed"
    assert "markdown" in warn[0]["observed_evidence"] and warn[0]["head_sha"] == H
    assert "JSONL row stands" in capsys.readouterr().err
    # and the reducer does NOT class the row as an orphan: the failure is on record
    rep = mgl.consistency_report(ro / "sub" / "log.md", tmp_path / "log.jsonl")
    assert rep == {"missing_jsonl": [], "orphan_jsonl": []}


def test_jsonl_failure_fails_the_gate_step_and_writes_no_markdown(tmp_path: Path):
    """Write-order witness: with the two writes swapped (markdown first) the md file would exist
    here. Hand-mutation witness recorded in the PR body (a swap is not deletion-expressible for
    `just mutation-probe`)."""
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)
    try:
        with pytest.raises(mgl.GateLogError, match="could not be recorded"):
            _emit(tmp_path, md=tmp_path / "log.md", jl=ro / "log.jsonl")
    finally:
        ro.chmod(0o700)
    assert not (tmp_path / "log.md").exists()


def test_unrecordable_row_is_a_gate_log_error_not_a_record_error(tmp_path: Path):
    """A RecordError from the emitter (here: a `:` in the lane id) surfaces as GateLogError."""
    with pytest.raises(mgl.GateLogError):
        mgl.emit_gate_row(
            pr=1,
            lens=LENS,
            outcome=_outcome("APPROVE"),
            lane_id="a:b",
            md_path=tmp_path / "log.md",
            jsonl_path=tmp_path / "log.jsonl",
        )
    assert not (tmp_path / "log.md").exists()


def test_lens_id_must_match_the_schema_pattern(tmp_path: Path):
    with pytest.raises(mgl.GateLogError, match="merge-gate-"):
        _emit(tmp_path, lens="codex-review")
    with pytest.raises(mgl.GateLogError):
        mgl.lens_binding(mgl.REPO, "main", "merge_gate_x")


# ---- consistency reducer -----------------------------------------------------------------


def test_consistency_orphan_class_and_reconcile(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(
        tmp_path,
        pr=2,
        verdict="BLOCK",
        findings=[{"severity": "P1", "location": "x", "message": "m"}],
        lens="merge-gate-spec",
    )
    md.write_text("")  # simulate a crash between the two writes
    rep = mgl.consistency_report(md, jl)
    assert len(rep["orphan_jsonl"]) == 1 and not rep["missing_jsonl"]
    assert mgl.reconcile_orphans(md, jl) == 1
    assert mgl.read_md_rows(md)[0] == {
        "ts": rep["orphan_jsonl"][0]["ts"],
        "pr": 2,
        "head_sha": H[:12],
        "lens": "merge-gate-spec",
        "verdict": "BLOCK",
        "n_findings": 1,
        "round_n": 1,
    }
    assert "1 finding(s)" in md.read_text()
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    assert mgl.reconcile_orphans(md, jl) == 0


def test_missing_jsonl_is_the_red_class(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    rows = _emit(tmp_path, pr=3)  # establishes the comparison window
    md.write_text(md.read_text() + mgl._md_line(rows[0]["ts"], 4, "d" * 40, LENS, "APPROVE", 0, 1))
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(4, "d" * 12, LENS, "APPROVE", rows[0]["ts"], 0, 1)]
    assert not rep["orphan_jsonl"]


def test_a_deleted_machine_log_reds_every_structured_md_row(tmp_path: Path):
    """codex R3 P1: no time window -- with zero surviving emissions every structured md row is
    MISSING its sibling, so a wiped `.jsonl` can never pass `check`."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=3, md=md, jl=jl)
    _emit(tmp_path, pr=4, md=md, jl=jl, lens="merge-gate-b")
    jl.unlink()
    rep = mgl.consistency_report(md, jl)
    # ordering follows the (head, lens, verdict) join key since U-HE-47 r5; the contract
    # is that BOTH rows red, not their order
    assert sorted(k[0] for k in rep["missing_jsonl"]) == [3, 4] and not rep["orphan_jsonl"]


def test_finding_count_is_part_of_the_sibling_match(tmp_path: Path):
    """codex R3 P2: a BLOCK emission that lost a finding row (or an md line whose count no
    longer matches any emission) is red -- multiset match on the finding count per key."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    fs = [
        {"severity": "P1", "location": "x", "message": "m1"},
        {"severity": "P2", "location": "y", "message": "m2"},
    ]
    rows = _emit(tmp_path, pr=7, verdict="BLOCK", findings=fs, md=md, jl=jl)
    ts = rows[0]["ts"]
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    lines = jl.read_text().splitlines(keepends=True)
    jl.write_text(lines[0])  # one finding row lost from the machine log
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(7, H[:12], LENS, "BLOCK", ts, 2, 1)]
    assert [r["round_n"] for r in rep["orphan_jsonl"]] == [1]  # the 1-finding emission: no line
    # one emission cannot vouch for two md lines at its key
    jl.write_text("".join(lines))
    md.write_text(md.read_text() * 2)
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(7, H[:12], LENS, "BLOCK", ts, 2, 1)]
    assert not rep["orphan_jsonl"]


def test_one_lens_md_failure_warn_does_not_suppress_another_lens_orphan(tmp_path: Path):
    """gemini R1 P2: the warn is keyed (head_sha, lens), not head_sha alone."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)
    try:
        _emit(tmp_path, pr=5, lens="merge-gate-a", md=ro / "x" / "log.md", jl=jl)  # a: md failed
    finally:
        ro.chmod(0o700)
    _emit(tmp_path, pr=5, lens="merge-gate-b", md=md, jl=jl)
    md.write_text("")  # b: crashed between the writes
    rep = mgl.consistency_report(md, jl)
    assert [r["producer"] for r in rep["orphan_jsonl"]] == ["merge-gate-b"]
    assert mgl.reconcile_orphans(md, jl) == 1
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_headless_gate_rows_are_outside_the_comparison_and_never_re_emitted(tmp_path: Path):
    """gemini R1 P2: a `nohead` md line could never be re-parsed, so reconcile would loop."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    out = rw.ReviewOutcome("APPROVE", mgl.CHANNEL, None, "", [], None)  # unbound outcome
    mgl.emit_gate_row(pr=6, lens=LENS, outcome=out, lane_id="h", md_path=md, jsonl_path=jl)
    assert "nohead" in md.read_text()
    md.write_text("")
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    assert mgl.reconcile_orphans(md, jl) == 0 and "nohead" not in md.read_text()


def test_md_failure_warn_vouches_for_its_own_round_only(tmp_path: Path):
    """codex R2 P2: a round-1 md failure must not hide a round-2 crash between the writes."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)
    try:
        _emit(tmp_path, pr=5, md=ro / "x" / "log.md", jl=jl, round_n=1)  # round 1: md failed
    finally:
        ro.chmod(0o700)
    _emit(tmp_path, pr=5, md=md, jl=jl, round_n=2)
    md.write_text("")  # round 2: crashed between the writes
    rep = mgl.consistency_report(md, jl)
    assert [r["round_n"] for r in rep["orphan_jsonl"]] == [2]


def test_two_emissions_at_one_key_need_two_md_lines(tmp_path: Path):
    """A re-run at the same head with the same verdict is its own emission: one md line does
    not vouch for both (codex R2 P2 -- first-row-per-key dedupe lost the second round)."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=1)
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=2)
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    lines = md.read_text().splitlines(keepends=True)
    md.write_text(lines[0])  # the round-2 line is lost
    rep = mgl.consistency_report(md, jl)
    assert [r["round_n"] for r in rep["orphan_jsonl"]] == [2]
    assert mgl.reconcile_orphans(md, jl) == 1
    assert len(mgl.read_md_rows(md)) == 2
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_md_failure_warn_vouches_for_its_own_pr_only(tmp_path: Path):
    """codex R4 P2: two PRs at one head+lens both have a round 1; PR A's warn must not hide
    PR B's crash between the writes."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    ro = tmp_path / "ro"
    ro.mkdir()
    ro.chmod(0o500)
    try:
        _emit(tmp_path, pr=11, md=ro / "x" / "log.md", jl=jl, round_n=1)  # PR 11: md failed
    finally:
        ro.chmod(0o700)
    _emit(tmp_path, pr=12, md=md, jl=jl, round_n=1)
    md.write_text("")  # PR 12: crashed between the writes
    rep = mgl.consistency_report(md, jl)
    assert [r["arc_id"] for r in rep["orphan_jsonl"]] == ["pr-12"]


def test_reconcile_is_serialized_with_an_in_flight_emission(tmp_path: Path, monkeypatch):
    """codex R4 P2: a concurrent `reconcile` must not see emitter A's JSONL-but-not-yet-md
    state (it would write A's line, A writes it again -> a duplicate with no emission). Both
    take the emission lock: B blocks until A has written its md line, then finds no orphan."""
    import subprocess
    import sys

    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    real = rw.emit_outcome
    b: dict = {}

    def emit_then_let_b_race(*a, **k):
        rows = real(*a, **k)  # A's JSONL rows are on disk; its md line is NOT yet
        code = (
            f"import sys; sys.path.insert(0, {str(Path(mgl.__file__).parent)!r}); "
            "from pathlib import Path; import merge_gate_log as m; "
            f"print('reconciled', m.reconcile_orphans(Path({str(md)!r}), Path({str(jl)!r})))"
        )
        b["proc"] = subprocess.Popen(
            [sys.executable, "-c", code], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        try:
            b["proc"].wait(timeout=3)  # without the lock B finishes here (and writes A's line)
            b["finished_while_a_held_the_lock"] = True
        except subprocess.TimeoutExpired:
            b["finished_while_a_held_the_lock"] = False  # blocked on the lock, as it must be
        return rows

    monkeypatch.setattr(rw, "emit_outcome", emit_then_let_b_race)
    _emit(tmp_path, pr=5, md=md, jl=jl)
    out, err = b["proc"].communicate(timeout=60)
    assert b["finished_while_a_held_the_lock"] is False, (out, err)
    assert "reconciled 0" in out, (out, err)
    assert len(mgl.read_md_rows(md)) == 1
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_a_duplicated_round_1_line_cannot_stand_in_for_a_lost_round_2_line(tmp_path, monkeypatch):
    """codex R8 P2: the md line carries its emission's ts; the match is on (ts, count), so a
    duplicate of round 1's line + a lost round-2 line is one missing + one orphan, not clean."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-19T10:00:00Z")
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=1)
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-19T10:00:07Z")
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=2)
    l1, l2 = md.read_text().splitlines(keepends=True)
    md.write_text(l1 + l1)  # round 1's line twice, round 2's lost
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(4, H[:12], LENS, "APPROVE", "2026-08-19T10:00:00Z", 0, 1)]
    assert [r["round_n"] for r in rep["orphan_jsonl"]] == [2]
    assert mgl.reconcile_orphans(md, jl) == 1
    assert md.read_text().endswith(l2)  # re-emitted with round 2's own ts


def test_same_second_reruns_are_distinct_md_lines(tmp_path, monkeypatch):
    """codex R9 P2: two reruns within one second at one head/lens/verdict/count are told apart
    by the md line's round column; a duplicate of one cannot conceal the loss of the other."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-19T10:00:00Z")
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=1)
    _emit(tmp_path, pr=4, md=md, jl=jl, round_n=2)
    l1, l2 = md.read_text().splitlines(keepends=True)
    assert l1.endswith("| r1 |\n") and l2.endswith("| r2 |\n")
    md.write_text(l1 + l1)
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(4, H[:12], LENS, "APPROVE", "2026-08-19T10:00:00Z", 0, 1)]
    assert [r["round_n"] for r in rep["orphan_jsonl"]] == [2]


def test_landing_delta_transfers_only_over_gate_row_files(tmp_path: Path):
    """codex R8 P1 / U-HE-23 predicate: H1..H2 may touch ONLY the two gate-log files."""
    import subprocess

    repo = tmp_path / "r"
    repo.mkdir()
    g = lambda *a: subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True, check=True)  # noqa: E731
    g("init", "-q")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    (repo / ".harness").mkdir()
    (repo / "code.py").write_text("x = 1\n")
    (repo / ".harness" / "merge-gate-log.jsonl").write_text('{"a": 1}\n')
    (repo / ".harness" / "merge-gate-log.md").write_text("| row |\n")
    g("add", "-A")
    g("commit", "-qm", "h1")
    h1 = g("rev-parse", "HEAD").stdout.strip()
    (repo / ".harness" / "merge-gate-log.jsonl").write_text('{"a": 1}\n{"b": 2}\n')
    (repo / ".harness" / "merge-gate-log.md").write_text("| row |\n| row2 |\n")
    g("add", "-A")
    g("commit", "-qm", "gate rows")
    assert mgl.landing_delta(h1, "HEAD", repo) == []  # approvals transfer
    h2 = g("rev-parse", "HEAD").stdout.strip()
    (repo / "code.py").write_text("x = 2\n")
    g("add", "-A")
    g("commit", "-qm", "sneaky")
    assert mgl.landing_delta(h1, "HEAD", repo) == ["code.py"]  # re-gate
    assert mgl.main(["landing-delta", "--reviewed", "not-a-ref"]) == 2
    # codex R9 P2: a gate-log file counts only as an APPEND -- rewrite / truncate / delete is change
    g("checkout", "-q", h2)
    (repo / ".harness" / "merge-gate-log.jsonl").write_text("")  # truncated
    g("add", "-A")
    g("commit", "-qm", "truncate")
    assert mgl.landing_delta(h1, "HEAD", repo) == [
        ".harness/merge-gate-log.jsonl (not an append: rewritten, truncated or removed)"
    ]
    g("checkout", "-q", h2)
    (repo / ".harness" / "merge-gate-log.md").write_text(
        "| roW |\n| row2 |\n"
    )  # rewritten in place
    g("add", "-A")
    g("commit", "-qm", "rewrite")
    assert mgl.landing_delta(h1, "HEAD", repo) == [
        ".harness/merge-gate-log.md (not an append: rewritten, truncated or removed)"
    ]
    g("checkout", "-q", h2)
    g("rm", "-q", ".harness/merge-gate-log.md")
    g("commit", "-qm", "delete")
    assert mgl.landing_delta(h1, "HEAD", repo) == [
        ".harness/merge-gate-log.md (not an append: rewritten, truncated or removed)"
    ]


def test_one_lens_sibling_never_vouches_for_another_lens(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=5, lens="merge-gate-a")
    _emit(tmp_path, pr=5, lens="merge-gate-b")
    lines = md.read_text().splitlines(keepends=True)
    md.write_text(lines[0])  # lens b's md line lost
    rep = mgl.consistency_report(md, jl)
    assert [r["producer"] for r in rep["orphan_jsonl"]] == ["merge-gate-b"]


def test_legacy_markdown_rows_and_wrapper_rows_are_outside_the_comparison(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    md.write_text(
        "# merge-gate audit log\n\n| #1397 | 2026-08-19 | he-lanes-s1 | L1: **APPROVE** | notes |\n"
    )
    # a codex wrapper row on the same log is not a gate verdict
    rw.emit_outcome(
        rw.ReviewOutcome("APPROVE", "codex", None, "", [], _binding("codex-review")),
        producer="codex_review_wrapper",
        arc_id="pr-1397",
        lane_id="h",
        round_n=1,
        path=jl,
    )
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    # a STRUCTURED md row is always compared, whatever its date (no window, codex R3 P1)
    md.write_text(
        md.read_text() + mgl._md_line("2000-01-01T00:00:00Z", 1, H, LENS, "APPROVE", 0, 1)
    )
    assert mgl.consistency_report(md, jl)["missing_jsonl"] == [
        (1, H[:12], LENS, "APPROVE", "2000-01-01T00:00:00Z", 0, 1)
    ]


def test_reviewer_unavailable_is_recorded_but_is_not_a_gate_verdict(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    out = rw.ReviewOutcome(
        "REVIEWER_UNAVAILABLE", mgl.CHANNEL, "transient", "no fenced json block", [], _binding()
    )
    rows = mgl.emit_gate_row(pr=7, lens=LENS, outcome=out, lane_id="h", md_path=md, jsonl_path=jl)
    assert rows[0]["record_kind"] == "reviewer_unavailable"
    assert "REVIEWER_UNAVAILABLE" in md.read_text()
    assert mgl.read_md_rows(md) == []  # the reducer reads APPROVE|BLOCK lines only
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


# ---- binding + CLI -----------------------------------------------------------------------


def test_lens_binding_uses_the_orchestrators_values_and_the_lens_identity():
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=mgl.REPO, capture_output=True, text=True, check=True
    ).stdout.strip()
    assert b["head_sha"] == head and b["base_sha"] == head
    assert b["reviewer_identity"] == LENS and b["prompt_version"] == mgl.PROMPT_VERSION
    assert b["config_hash"] == "cfg" and len(b["diff_digest"]) == 64
    assert set(b) == set(rw.BINDING_FIELDS)


def test_config_hash_covers_every_carrier_on_both_runners(tmp_path: Path, monkeypatch):
    """gemini R1 P2: the Claude skill alone is not the configuration -- the Codex projection and
    the Codex lens prompts are carriers too; a change to ANY of them changes the hash."""
    monkeypatch.undo()  # this test exercises the REAL config_hash (the autouse pin is lifted)
    monkeypatch.setattr(mgl, "REPO", tmp_path)
    claude, codex = tmp_path / "c" / "SKILL.md", tmp_path / "a" / "SKILL.md"
    lenses = tmp_path / "lenses"
    monkeypatch.setattr(mgl, "CONFIG_CARRIERS", (claude, codex))
    monkeypatch.setattr(mgl, "CONFIG_CARRIER_GLOB", (lenses, "*.md"))
    assert mgl.config_hash() == "noskill"
    claude.parent.mkdir()
    claude.write_text("claude rules v1")
    h1 = mgl.config_hash()
    assert len(h1) == 16
    codex.parent.mkdir()
    codex.write_text("codex rules v1")
    h2 = mgl.config_hash()
    assert h2 != h1  # the Codex projection is part of the configuration
    lenses.mkdir()
    (lenses / "lens1.md").write_text("lens prompt v1")
    h3 = mgl.config_hash()
    assert h3 != h2  # and so is each Codex lens prompt
    (lenses / "lens1.md").write_text("lens prompt v2")
    assert mgl.config_hash() != h3
    assert [p.name for p in mgl.config_carriers()] == ["SKILL.md", "SKILL.md", "lens1.md"]
    # the real carriers exist at HEAD: the production hash is never the sentinel
    monkeypatch.undo()
    assert mgl.config_hash() != "noskill" and len(mgl.config_carriers()) >= 5


def _lens_output(binding: dict, verdict: str, findings: list | None = None, line=None) -> str:
    body = {"verdict": verdict, "findings": findings or [], **binding}
    default = "VERDICT: APPROVE" if verdict == "APPROVE" else "VERDICT: BLOCK: the lens reason"
    tail = default if line is None else line
    return "prose before\n```json\n" + json.dumps(body) + "\n```\nprose after\n" + tail + "\n"


def test_cli_emit_parses_the_schema_block_and_holds_it_to_the_binding(
    tmp_path, monkeypatch, capsys
):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE"))
    rc = mgl.main(
        [
            "emit",
            "--pr",
            "9",
            "--lens",
            LENS,
            "--verdict-json",
            str(f),
            "--base",
            "HEAD",
            "--lane-id",
            "h",
        ]
    )
    assert rc == 0 and "APPROVE recorded" in capsys.readouterr().out
    assert fr.read_rows(jl)[0]["record_kind"] == "no_finding" and md.exists()
    # BLOCK with one finding -> exit 1 (recorded), one finding row
    f.write_text(_lens_output(b, "BLOCK", [{"severity": "P1", "location": "x", "message": "m"}]))
    rc = mgl.main(
        [
            "emit",
            "--pr",
            "9",
            "--lens",
            LENS,
            "--verdict-json",
            str(f),
            "--base",
            "HEAD",
            "--lane-id",
            "h",
        ]
    )
    assert rc == 1 and fr.read_rows(jl)[-1]["finding_type"] == "terminal-block"
    # binding mismatch (another lens's identity / a moved head) -> not a verdict: exit 2,
    # a bound reviewer_unavailable marker is recorded
    f.write_text(_lens_output({**b, "reviewer_identity": "merge-gate-spec"}, "APPROVE"))
    rc = mgl.main(
        [
            "emit",
            "--pr",
            "9",
            "--lens",
            LENS,
            "--verdict-json",
            str(f),
            "--base",
            "HEAD",
            "--lane-id",
            "h",
        ]
    )
    assert rc == 2
    last = fr.read_rows(jl)[-1]
    assert last["record_kind"] == "reviewer_unavailable" and last["head_sha"] == b["head_sha"]
    assert "binding mismatch" in last["observed_evidence"]
    # no fenced block at all -> exit 2 as well (never APPROVE by absence)
    f.write_text("APPROVE\n")
    assert (
        mgl.main(
            [
                "emit",
                "--pr",
                "9",
                "--lens",
                LENS,
                "--verdict-json",
                str(f),
                "--base",
                "HEAD",
                "--lane-id",
                "h",
            ]
        )
        == 2
    )
    assert mgl.main(["check"]) == 0


def _cli(f, *extra):
    return ["emit", "--pr", "9", "--lens", LENS, "--verdict-json", str(f), "--base", "HEAD",
            "--lane-id", "h", *extra]  # fmt: skip


def test_cli_emit_exit_2_on_any_non_recording_failure_never_1(tmp_path, monkeypatch, capsys):
    """codex R2 P2: a missing verdict file / failed git call must be exit 2 (NOT recorded), never
    the uncaught exit 1 the skills read as 'BLOCK recorded'."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    rc = mgl.main(_cli(tmp_path / "nope"))
    assert rc == 2 and "NOT RECORDED" in capsys.readouterr().err
    assert not jl.exists() and not md.exists()

    def git_down(*a, **k):
        raise RuntimeError("git down")

    monkeypatch.setattr(mgl, "lens_binding", git_down)
    f = tmp_path / "v.txt"
    f.write_text("x")
    rc = mgl.main(_cli(f))
    assert rc == 2 and "git down" in capsys.readouterr().err


def test_cli_emit_head_moved_during_emit_is_not_a_verdict_for_the_checkout(
    tmp_path, monkeypatch, capsys
):
    """codex R2 P1: the rows are a true record of the head the binding named, but if HEAD moved
    while recording, exit 2 -- the skill must not read it as a verdict for the current tree."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE"))
    real_git = rw._git
    moved = {"n": 0}

    def git_with_a_moved_head(repo, *args):
        if args == ("rev-parse", "HEAD") and jl.exists():  # after the rows were written
            moved["n"] += 1
            return "f" * 40
        return real_git(repo, *args)

    monkeypatch.setattr(rw, "_git", git_with_a_moved_head)
    rc = mgl.main(_cli(f))
    err = capsys.readouterr().err
    assert rc == 2 and "HEAD moved during emit" in err and moved["n"] == 1
    assert fr.read_rows(jl)[0]["head_sha"] == b["head_sha"]  # the record stands, bound to H1


def test_cli_emit_reconciles_earlier_orphans_first(tmp_path, monkeypatch, capsys):
    """codex R2 P3: 'the next gate run' re-emits orphan md rows -- emit is that run."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    _emit(tmp_path, pr=3, md=md, jl=jl)
    md.write_text("")  # an earlier crash between the writes
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE"))
    rc = mgl.main(_cli(f))
    assert rc == 0 and "reconciled 1 orphan" in capsys.readouterr().out
    assert [r["pr"] for r in mgl.read_md_rows(md)] == [3, 9]
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_cli_emit_requires_the_verdict_line_to_agree_with_the_block(tmp_path, monkeypatch, capsys):
    """codex R3 P2: JSON APPROVE + `VERDICT: BLOCK`, or no VERDICT line, is not a verdict."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE", line="VERDICT: BLOCK: contradicts the block"))
    assert mgl.main(_cli(f)) == 2
    assert fr.read_rows(jl)[-1]["record_kind"] == "reviewer_unavailable"
    assert "disagrees" in fr.read_rows(jl)[-1]["observed_evidence"]
    f.write_text(_lens_output(b, "APPROVE", line="no verdict line here"))
    assert mgl.main(_cli(f)) == 2
    # codex R6 P1: the line is a FULL-line match -- ambiguous / decorated forms never approve
    for bad in (
        "VERDICT: APPROVE or BLOCK",
        "VERDICT: APPROVE (tentative)",
        "VERDICT:APPROVE",
        "VERDICT: APPROVE: with a reason",
    ):  # all disagree with the APPROVE block
        f.write_text(_lens_output(b, "APPROVE", line=bad))
        assert mgl.main(_cli(f)) == 2, bad
    f.write_text(
        _lens_output(
            b,
            "BLOCK",
            [{"severity": "P1", "location": "x", "message": "m"}],
            line="VERDICT: BLOCK: one concrete reason",
        )
    )
    assert mgl.main(_cli(f)) == 1
    # merge-gate L3 on #1399: a BLOCK-schema verdict with a BARE `VERDICT: BLOCK` line (no
    # reason) is NOT a verdict -- the contract's reason suffix is required, not decorative
    f.write_text(
        _lens_output(
            b, "BLOCK", [{"severity": "P1", "location": "x", "message": "m"}], line="VERDICT: BLOCK"
        )
    )
    assert mgl.main(_cli(f)) == 2
    assert fr.read_rows(jl)[-1]["record_kind"] == "reviewer_unavailable"
    f.write_text(_lens_output(b, "APPROVE", line="VERDICT: APPROVE"))
    assert mgl.main(_cli(f)) == 0
    assert fr.read_rows(jl)[-1]["record_kind"] == "no_finding"
    assert len(mgl.read_md_rows(md)) == 2  # only the agreeing runs produced structured lines
    assert md.read_text().count("REVIEWER_UNAVAILABLE") == 7


def test_no_cli_override_of_the_config_hash(tmp_path: Path):
    """codex R5 P2: `config_hash` is always the independent digest of the current carriers --
    neither command accepts a caller-supplied value that both could share."""
    for argv in (
        ["binding", "--lens", LENS, "--config-hash", "x"],
        ["emit", "--pr", "1", "--lens", LENS, "--verdict-json", "f", "--config-hash", "x"],
    ):
        with pytest.raises(SystemExit) as exc:
            mgl.main(argv)
        assert exc.value.code == 2


def test_cli_emit_head_reread_failure_after_recording_is_exit_2(tmp_path, monkeypatch, capsys):
    """codex R5 P2: a failing post-record `rev-parse` must be exit 2 (recorded, but not known
    to be for this checkout), never the uncaught exit 1 the skills read as BLOCK."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS)
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE"))
    real_git = rw._git

    def git_dies_after_recording(repo, *args):
        if args == ("rev-parse", "HEAD") and jl.exists():
            raise RuntimeError("git gone")
        return real_git(repo, *args)

    monkeypatch.setattr(rw, "_git", git_dies_after_recording)
    assert mgl.main(_cli(f)) == 2
    assert "HEAD could not be re-read" in capsys.readouterr().err
    assert fr.read_rows(jl)[0]["record_kind"] == "no_finding"  # the record stands


def test_cli_emit_reads_only_regular_files_under_the_lens_scratch_dir(
    tmp_path, monkeypatch, capsys
):
    """codex R7 P2: the guard auto-allows a RELATIVE `--verdict-json`; a relative symlink could
    point anywhere. `emit` resolves the path and refuses anything that is a symlink or lands
    outside `.harness/tmp/` -- exit 2, nothing recorded, content never echoed."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(mgl, "LENS_SCRATCH", scratch)
    outside = tmp_path / "secret.txt"
    outside.write_text("VERDICT: APPROVE\nTOKEN=hunter2\n")
    link = scratch / "lens.txt"
    link.symlink_to(outside)
    assert mgl.main(_cli(link)) == 2
    err = capsys.readouterr().err
    assert "must be '-' or a regular file directly under" in err and "hunter2" not in err
    assert mgl.main(_cli(outside)) == 2  # a real file outside the scratch dir
    assert not jl.exists()
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS)
    good = scratch / "ok.txt"
    good.write_text(_lens_output(b, "APPROVE"))
    assert mgl.main(_cli(good)) == 0


def test_cli_binding_publishes_the_six_fields_to_a_file_and_prints_only_its_path(
    tmp_path, monkeypatch, capsys
):
    """U-SR-03 (charter WR-09): the values land in a file; stdout carries the path alone.

    The contract this pins is the ABSENCE of the values from stdout, not merely their
    presence in the file. Printing both would leave the hand-copy path -- the source of both
    round-3 lens corruptions -- just as available as before, and a test that only checked the
    file would stay green through exactly that regression.
    """
    scratch = tmp_path / "scratch"
    monkeypatch.setattr(mgl, "LENS_SCRATCH", scratch)
    expected = mgl.lens_binding(mgl.REPO, "HEAD", LENS)  # the binding the CLI resolves
    assert mgl.main(["binding", "--lens", LENS, "--base", "HEAD"]) == 0
    printed = capsys.readouterr().out.strip()
    assert printed == str(mgl.binding_path(LENS, expected))
    written = json.loads(mgl.binding_path(LENS, expected).read_text())
    assert written == expected and set(written) == set(rw.BINDING_FIELDS)

    # The name is CONTENT-ADDRESSED, so identical name implies identical contents: changing
    # ANY field -- not just the head -- moves the file, and an in-flight lens's named path
    # can never be repointed under it (codex r1 P1 on the lens-only key, r2 P1 on lens+head).
    for field in rw.BINDING_FIELDS:
        altered = {**expected, field: "different"}
        assert mgl.binding_path(LENS, altered) != mgl.binding_path(LENS, expected), (
            f"{field} does not participate in the published name"
        )

    # No value is copyable off stdout. `reviewer_identity` is the sole exemption because it
    # IS the `--lens` argument the caller passed -- a value you supplied is not one you can
    # mistranscribe. Every other value is absent outright, which is what a revert to printing
    # the JSON would violate.
    for field, value in written.items():
        if field == "reviewer_identity":
            continue
        assert value not in printed, f"{field} is transcribable off stdout"

    assert mgl.main(["binding", "--lens", "nope", "--base", "HEAD"]) == 2
    assert list(scratch.iterdir()) == [mgl.binding_path(LENS, expected)], (
        "a refused id published something"
    )


def test_cli_binding_refuses_a_symlinked_scratch_directory(tmp_path, monkeypatch, capsys):
    """codex r1 P2: `O_NOFOLLOW` guards the final component only.

    With `.harness/tmp` itself pre-planted as a symlink, `mkdir(exist_ok=True)` succeeds and
    the temp open, the write, and the `os.replace` all land in the external target -- the
    auto-allowed recipe would publish somewhere it never promised to write. Refuse loudly
    (exit 2, nothing written) rather than silently relocate the publication.
    """
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    scratch = tmp_path / "scratch"
    scratch.symlink_to(elsewhere, target_is_directory=True)
    monkeypatch.setattr(mgl, "LENS_SCRATCH", scratch)

    assert mgl.main(["binding", "--lens", LENS, "--base", "HEAD"]) == 2
    assert "not a usable scratch directory" in capsys.readouterr().err
    assert list(elsewhere.iterdir()) == [], "published into the symlink target anyway"

    # Same enforcer, other caller: `emit`'s reader resolved through this directory too, so a
    # symlinked scratch dir would have let a lens file from outside the worktree in. The
    # sibling is closed by construction rather than by a second, drift-prone check.
    planted = elsewhere / "lens.txt"
    planted.write_text("VERDICT: APPROVE\n")
    with pytest.raises(mgl.GateLogError, match="not a usable scratch directory"):
        mgl._read_text(str(scratch / "lens.txt"))


def test_cli_binding_replaces_a_pre_planted_destination_instead_of_following_it(
    tmp_path, monkeypatch, capsys
):
    """The recipe that writes this file is auto-allowed by the permission guard, and it
    writes into a gitignored directory any other actor in the worktree can reach first.
    `os.replace` overwrites the NAME, so a symlink planted at the destination is dropped
    rather than used to clobber whatever it aimed at -- the containment `emit` already
    applies to its `--verdict-json` sibling in the same directory."""
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setattr(mgl, "LENS_SCRATCH", scratch)
    expected = mgl.lens_binding(mgl.REPO, "HEAD", LENS)
    victim = tmp_path / "tracked-file-someone-cares-about.md"
    victim.write_text("original content\n")
    mgl.binding_path(LENS, expected).symlink_to(victim)

    assert mgl.main(["binding", "--lens", LENS, "--base", "HEAD"]) == 0
    capsys.readouterr()
    assert victim.read_text() == "original content\n", "the symlink target was clobbered"
    assert not mgl.binding_path(LENS, expected).is_symlink()
    assert set(json.loads(mgl.binding_path(LENS, expected).read_text())) == set(rw.BINDING_FIELDS)
    assert [p.name for p in scratch.iterdir()] == [mgl.binding_path(LENS, expected).name], (
        "a temp file was left behind"
    )


def test_cli_check_is_red_only_on_missing_jsonl(tmp_path: Path, monkeypatch, capsys):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    rows = _emit(tmp_path, pr=3, md=md, jl=jl)
    md.write_text("")
    assert mgl.main(["check"]) == 0  # orphan: listed, reconciled next run, not red
    assert "ORPHAN-JSONL" in capsys.readouterr().out
    assert mgl.main(["reconcile"]) == 0 and mgl.read_md_rows(md)
    md.write_text(md.read_text() + mgl._md_line(rows[0]["ts"], 8, "e" * 40, LENS, "BLOCK", 1, 1))
    assert mgl.main(["check"]) == 1
    assert "MISSING-JSONL pr=8" in capsys.readouterr().out


# ---- U-HE-47: emit-time attribution (C-HE-24 §2 X6d) + absorption adjudication (§5) ------


def _codex_round(tmp_path: Path, arc_id: str, findings: list[dict], round_n: int) -> list[dict]:
    """One preceding codex review round on the fixture arc (producer=codex_review_wrapper)."""
    out = rw.ReviewOutcome("BLOCK", "codex", None, "", findings, _binding())
    return rw.emit_outcome(
        out,
        producer="codex_review_wrapper",
        arc_id=arc_id,
        lane_id="h-w-1",
        round_n=round_n,
        path=tmp_path / "log.jsonl",
    )


# mutation-probe(tools/merge_gate_log.py): drop the attributor wiring -> F16 nulls -> red
def test_gate_rows_after_two_codex_rounds_carry_non_null_attribution_on_every_row(tmp_path):
    _codex_round(tmp_path, "u-t-1", [{"severity": "P1", "location": "a.py:10", "message": "m"}], 1)
    _codex_round(tmp_path, "u-t-1", [{"severity": "P2", "location": "b.py:20", "message": "m"}], 2)
    fs = [
        {"severity": "P1", "location": "a.py:10", "message": "same place, same type"},
        {"severity": "P2", "location": "c.py:30", "message": "gate-only catch"},
    ]
    rows = _emit(tmp_path, pr=9, verdict="BLOCK", findings=fs, arc_id="u-t-1")
    assert all(r["cause_attribution"] is not None for r in rows)  # F16 unrepresentable
    assert all(r["unique_catch"] is not None for r in rows)
    by_loc = {r["location"]: r for r in rows}
    assert by_loc["a.py:10"]["unique_catch"] is False
    assert by_loc["a.py:10"]["cause_attribution"] == "codex_round_overlap"
    assert by_loc["c.py:30"]["unique_catch"] is True
    assert by_loc["c.py:30"]["cause_attribution"] == "gate_unique_catch"


def test_clean_approve_lens_row_is_attributed_non_null(tmp_path: Path):
    rows = _emit(tmp_path, pr=9, verdict="APPROVE", arc_id="u-t-1")
    assert rows[0]["record_kind"] == "no_finding"
    assert rows[0]["cause_attribution"] == "clean_approve"
    assert rows[0]["unique_catch"] is False


def test_unique_catch_join_is_intra_arc_never_cross_arc(tmp_path: Path):
    f = {"severity": "P1", "location": "a.py:10", "message": "m"}
    _codex_round(tmp_path, "u-other", [f], 1)
    rows = _emit(
        tmp_path,
        pr=9,
        verdict="BLOCK",
        findings=[{"severity": "P1", "location": "a.py:10", "message": "m"}],
        arc_id="u-t-1",
    )
    assert rows[0]["unique_catch"] is True  # the match lives on another arc: out of scope


def test_codex_wrapper_rows_stay_unattributed(tmp_path: Path):
    rows = _codex_round(
        tmp_path, "u-t-1", [{"severity": "P1", "location": "a.py:10", "message": "m"}], 1
    )
    assert rows[0]["cause_attribution"] is None and rows[0]["unique_catch"] is None


def test_adjudicate_appends_the_disposition_row_and_the_reducer_returns_it(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:00Z")
    rows = _emit(
        tmp_path,
        pr=9,
        verdict="BLOCK",
        findings=[{"severity": "P1", "location": "c.py:30", "message": "m"}],
        arc_id="u-t-1",
    )
    fid = rows[0]["finding_id"]
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:07Z")
    adj = mgl.adjudicate(fid, "accepted", "claude_absorber", tmp_path / "log.jsonl")
    assert adj["record_kind"] == "finding_adjudication" and adj["disposition"] == "accepted"
    assert adj["disposition_actor"] == "claude_absorber"
    assert adj["unique_catch"] is rows[0]["unique_catch"]  # emit-time attribution carried
    reduced = fr.reduce_last_by_finding_id(fr.read_rows(tmp_path / "log.jsonl"))
    assert reduced[fid]["disposition"] == "accepted"


def test_adjudicate_rejects_actor_equal_to_producer(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:00Z")
    rows = _emit(
        tmp_path,
        pr=9,
        verdict="BLOCK",
        findings=[{"severity": "P1", "location": "c.py:30", "message": "m"}],
        arc_id="u-t-1",
    )
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:07Z")
    with pytest.raises(fr.RecordError, match="never disposes its own finding"):
        mgl.adjudicate(rows[0]["finding_id"], "accepted", LENS, tmp_path / "log.jsonl")


def test_adjudicate_unknown_finding_id_is_a_gate_log_error(tmp_path: Path):
    (tmp_path / "log.jsonl").write_text("")
    with pytest.raises(mgl.GateLogError, match="no row with finding_id"):
        mgl.adjudicate("x:y:000000000000:1", "accepted", "claude_absorber", tmp_path / "log.jsonl")


def test_cli_adjudicate_exit_0_recorded_2_not_recorded(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mgl, "GATE_LOG_MD", tmp_path / "log.md")
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "log.jsonl")
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:00Z")
    rows = mgl.emit_gate_row(
        pr=9,
        lens=LENS,
        outcome=_outcome("BLOCK", [{"severity": "P1", "location": "c.py:30", "message": "m"}]),
        lane_id="h-w-1",
    )
    fid = rows[0]["finding_id"]
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:07Z")
    args = ["adjudicate", "--finding-id", fid, "--disposition", "rejected", "--actor", "op"]
    assert mgl.main(args) == 0
    assert f"{fid} disposed rejected by op" in capsys.readouterr().out
    # a second disposition write on the adjudicated lineage needs a later ts; same-second -> 2
    assert mgl.main(args) == 2
    assert "NOT ADJUDICATED" in capsys.readouterr().err


def test_reviewer_unavailable_lens_row_is_attributed_non_null(tmp_path: Path):
    out = rw.ReviewOutcome(
        "REVIEWER_UNAVAILABLE", mgl.CHANNEL, "transient", "lens died", [], _binding()
    )
    rows = mgl.emit_gate_row(
        pr=9,
        lens=LENS,
        outcome=out,
        lane_id="h-w-1",
        md_path=tmp_path / "log.md",
        jsonl_path=tmp_path / "log.jsonl",
    )
    assert rows[0]["record_kind"] == "reviewer_unavailable"
    assert rows[0]["cause_attribution"] == "reviewer_unavailable_transient"
    assert rows[0]["unique_catch"] is False


def test_cli_adjudicate_oserror_is_exit_2_not_1(tmp_path, monkeypatch, capsys):
    # r1 P3: an unreadable log (here: the path is a directory) is "not recorded" -> exit 2,
    # never the uncaught-exception exit 1 the skill would misread as a recorded failure
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path)
    args = ["adjudicate", "--finding-id", "x:y:000000000000:1", "--disposition", "accepted"]
    assert mgl.main([*args, "--actor", "op"]) == 2
    assert "NOT ADJUDICATED" in capsys.readouterr().err


def test_cli_adjudicate_refuses_a_cross_arc_target_when_arc_bound(tmp_path, monkeypatch, capsys):
    # r4 P1: with HARNESS_ARC_ID set (the guard-required headless form), only the current
    # arc's own findings are disposable; a historical finding from another arc is refused.
    monkeypatch.setattr(mgl, "GATE_LOG_MD", tmp_path / "log.md")
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "log.jsonl")
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:00Z")
    rows = mgl.emit_gate_row(
        pr=9,
        lens=LENS,
        outcome=_outcome("BLOCK", [{"severity": "P1", "location": "c.py:30", "message": "m"}]),
        arc_id="u-t-1",
        lane_id="h-w-1",
    )
    fid = rows[0]["finding_id"]
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:07Z")
    monkeypatch.setattr(mgl, "arc_not_held_reason", lambda a: None)  # holder half tested below
    args = ["adjudicate", "--finding-id", fid, "--disposition", "accepted", "--actor", "op"]
    monkeypatch.setenv("HARNESS_ARC_ID", "u-other")
    assert mgl.main(args) == 2
    assert "cross-arc adjudication" in capsys.readouterr().err
    monkeypatch.setenv("HARNESS_ARC_ID", "u-t-1")
    assert mgl.main(args) == 0


def test_arc_not_held_reason_binds_to_reservation_holder_state(tmp_path, monkeypatch):
    # r5 P1: the HARNESS_ARC_ID prefix is caller-chosen text; authority comes from the
    # reservation store (live head, held by THIS lane's persisted id) — the record_phase
    # pattern. Terminal (historical) arcs and other lanes' holds refuse.
    import reservations as rs

    monkeypatch.setattr(mgl, "LANE_ID_FILE", tmp_path / "lane-id")
    (tmp_path / "lane-id").write_text("lane-A\n")
    heads = {
        "u-held": {"state": "open", "lane_id": "lane-A"},
        "u-pending": {"state": "pending", "lane_id": "lane-A"},
        "u-merged": {"state": "merged", "lane_id": "lane-A"},
        "u-theirs": {"state": "open", "lane_id": "lane-B"},
    }
    monkeypatch.setattr(rs, "current", lambda a: (1, heads[a]) if a in heads else None)
    assert mgl.arc_not_held_reason("u-held") is None
    assert mgl.arc_not_held_reason("u-pending") is None
    assert "terminal" in (mgl.arc_not_held_reason("u-merged") or "")
    assert "not this lane" in (mgl.arc_not_held_reason("u-theirs") or "")
    assert "no reservation" in (mgl.arc_not_held_reason("u-absent") or "")
    (tmp_path / "lane-id").unlink()
    assert "lane identity unreadable" in (mgl.arc_not_held_reason("u-held") or "")


def test_cli_adjudicate_refuses_an_arc_this_lane_does_not_hold(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(mgl, "GATE_LOG_MD", tmp_path / "log.md")
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "log.jsonl")
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:00Z")
    rows = mgl.emit_gate_row(
        pr=9,
        lens=LENS,
        outcome=_outcome("BLOCK", [{"severity": "P1", "location": "c.py:30", "message": "m"}]),
        arc_id="u-hist",
        lane_id="h-w-1",
    )
    monkeypatch.setattr(fr, "now_iso", lambda: "2026-08-27T10:00:07Z")
    monkeypatch.setattr(mgl, "arc_not_held_reason", lambda a: f"arc {a!r} has no reservation")
    monkeypatch.setenv("HARNESS_ARC_ID", "u-hist")
    args = ["adjudicate", "--finding-id", rows[0]["finding_id"], "--disposition", "accepted"]
    assert mgl.main([*args, "--actor", "op"]) == 2
    assert "no reservation" in capsys.readouterr().err


def test_reservation_arc_lens_rows_join_their_md_lines(tmp_path):
    # r5 P1 (the live 23-missing-siblings defect): a lens row whose arc_id is the
    # reservation id — the U-HE-34 carrier form — must join its md line.
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=42, md=md, jl=jl, arc_id="u-he-99")
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_reservation_arc_orphan_is_left_standing_and_the_store_is_never_consulted(
    tmp_path, monkeypatch, capsys
):
    # r6 P2 -> r7 P1, settled by DELETION: the reservation's `pr` is mutable, so orphan
    # PR recovery from it can relabel an old verdict. The md line is the only pr
    # authority — a reservation-arc orphan is reported loudly and left standing, and
    # the store is not even read (witness: a consulting call would raise).
    import reservations as rs

    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=42, md=md, jl=jl, arc_id="u-he-99")
    md.write_text("")  # crash between the writes

    def _boom(_a):
        raise AssertionError("reconcile must not consult the reservation store")

    monkeypatch.setattr(rs, "current", _boom)
    assert mgl.reconcile_orphans(md, jl) == 0
    assert "no recoverable PR" in capsys.readouterr().err
    assert len(mgl.consistency_report(md, jl)["orphan_jsonl"]) == 1  # still visible, never lost
    # r8 P2 + r9 P2: the SAME arc's gate rerun AT THE SAME REVIEWED HEAD carries the
    # recovery authority — its own (arc, pr, head) triple; a different arc, a different
    # head, or a missing head must not renumber it.
    assert mgl.reconcile_orphans(md, jl, arc_id="u-other", pr=99, head_sha=H) == 0
    assert mgl.reconcile_orphans(md, jl, arc_id="u-he-99", pr=99, head_sha="f" * 40) == 0
    assert mgl.reconcile_orphans(md, jl, arc_id="u-he-99", pr=42) == 0  # no head: no recovery
    assert mgl.reconcile_orphans(md, jl, arc_id="u-he-99", pr=42, head_sha=H) == 1
    assert mgl.read_md_rows(md)[0]["pr"] == 42
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    # a pr-N-arc orphan alongside it still reconciles from its own arc id
    _emit(tmp_path, pr=7, md=md, jl=jl)
    md_lines = md.read_text()
    md.write_text("\n".join(ln for ln in md_lines.splitlines() if "#7" not in ln) + "\n")
    assert mgl.reconcile_orphans(md, jl) == 1
    assert any(r["pr"] == 7 for r in mgl.read_md_rows(md))


def test_orphan_pr_recovery_is_bound_to_the_emissions_own_head(tmp_path, monkeypatch, capsys):
    # r6 P2: the reservation's `pr` is mutable — a payload rebound to a NEW head must not
    # relabel an old orphan verdict; recovery requires the reservation head == row head.
    import reservations as rs

    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    _emit(tmp_path, pr=42, md=md, jl=jl, arc_id="u-he-99")
    md.write_text("")
    monkeypatch.setattr(
        rs,
        "current",
        lambda a: (2, {"pr": 77, "head_sha": "f" * 40}),  # rebound payload
    )
    assert mgl.reconcile_orphans(md, jl) == 0
    assert "no recoverable PR" in capsys.readouterr().err
    assert len(mgl.consistency_report(md, jl)["orphan_jsonl"]) == 1


def test_cli_emit_recovers_a_reservation_arc_orphan_via_the_real_entry_point(
    tmp_path, monkeypatch, capsys
):
    # merge-gate witness lens on PR #1467: the arc/pr/head recovery triple is wired in
    # main()'s emit branch — this drives it through mgl.main, so reverting the call site
    # to a bare reconcile_orphans() reds here (every other recovery test calls the
    # function directly and cannot see the wiring).
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    b = mgl.lens_binding(mgl.REPO, "HEAD", LENS, cfg_hash="cfg")
    _emit(tmp_path, pr=42, head=b["head_sha"], md=md, jl=jl, arc_id="u-he-99")
    md.write_text("")  # crash between the writes: a reservation-arc orphan at this head
    f = tmp_path / "lens.txt"
    f.write_text(_lens_output(b, "APPROVE"))
    rc = mgl.main(
        [
            "emit",
            "--pr",
            "42",
            "--arc-id",
            "u-he-99",
            "--lens",
            LENS,
            "--verdict-json",
            str(f),
            "--base",
            "HEAD",
            "--lane-id",
            "h",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0 and "reconciled 1 orphan md row(s)" in out
    assert [r["pr"] for r in mgl.read_md_rows(md)].count(42) == 2  # recovered + new emission
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


def test_arc_not_held_reason_without_reservations_substrate_refuses(monkeypatch):
    monkeypatch.setitem(sys.modules, "reservations", None)  # import raises ImportError
    assert "no reservations substrate" in (mgl.arc_not_held_reason("u-x") or "")
