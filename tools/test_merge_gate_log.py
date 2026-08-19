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
    assert md == f"| {rows[0]['ts']} | #1 | {H[:12]} | {LENS} | APPROVE | 0 finding(s) |\n"
    assert mgl.read_md_rows(tmp_path / "log.md") == [
        {"ts": rows[0]["ts"], "pr": 1, "head_sha": H[:12], "lens": LENS, "verdict": "APPROVE"}
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
    }
    assert "1 finding(s)" in md.read_text()
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}
    assert mgl.reconcile_orphans(md, jl) == 0


def test_missing_jsonl_is_the_red_class(tmp_path: Path):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    rows = _emit(tmp_path, pr=3)  # establishes the comparison window
    md.write_text(md.read_text() + mgl._md_line(rows[0]["ts"], 4, "d" * 40, LENS, "APPROVE", 0))
    rep = mgl.consistency_report(md, jl)
    assert rep["missing_jsonl"] == [(4, "d" * 12, LENS, "APPROVE")] and not rep["orphan_jsonl"]


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
    # an md structured row dated BEFORE the first gate verdict is outside the window
    md.write_text(md.read_text() + mgl._md_line("2000-01-01T00:00:00Z", 1, H, LENS, "APPROVE", 0))
    _emit(tmp_path, pr=6)
    assert mgl.consistency_report(md, jl) == {"missing_jsonl": [], "orphan_jsonl": []}


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


def _lens_output(binding: dict, verdict: str, findings: list | None = None) -> str:
    body = {"verdict": verdict, "findings": findings or [], **binding}
    return "prose before\n```json\n" + json.dumps(body) + "\n```\nprose after\n"


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
            "--config-hash",
            "cfg",
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
            "--config-hash",
            "cfg",
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
            "--config-hash",
            "cfg",
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
                "--config-hash",
                "cfg",
                "--lane-id",
                "h",
            ]
        )
        == 2
    )
    assert mgl.main(["check"]) == 0


def _cli(f, *extra):
    return ["emit", "--pr", "9", "--lens", LENS, "--verdict-json", str(f), "--base", "HEAD",
            "--config-hash", "cfg", "--lane-id", "h", *extra]  # fmt: skip


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


def test_cli_binding_prints_the_six_fields(capsys):
    assert mgl.main(["binding", "--lens", LENS, "--base", "HEAD", "--config-hash", "cfg"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert set(out) == set(rw.BINDING_FIELDS) and out["reviewer_identity"] == LENS
    assert mgl.main(["binding", "--lens", "nope", "--base", "HEAD"]) == 2


def test_cli_check_is_red_only_on_missing_jsonl(tmp_path: Path, monkeypatch, capsys):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    rows = _emit(tmp_path, pr=3, md=md, jl=jl)
    md.write_text("")
    assert mgl.main(["check"]) == 0  # orphan: listed, reconciled next run, not red
    assert "ORPHAN-JSONL" in capsys.readouterr().out
    assert mgl.main(["reconcile"]) == 0 and mgl.read_md_rows(md)
    md.write_text(md.read_text() + mgl._md_line(rows[0]["ts"], 8, "e" * 40, LENS, "BLOCK", 1))
    assert mgl.main(["check"]) == 1
    assert "MISSING-JSONL pr=8" in capsys.readouterr().out
