"""`merge_gate_log.py emit-all` — the three lens verdicts recorded in one call (B-230 Task 5).

Contract under test: every lens is ALWAYS emitted, in the fixed order concurrency →
spec-conformance → witness-adequacy, and the exit is the worst outcome across the three
(2 not recorded > 1 recorded BLOCK > 0 approve). There is no resumption: a re-run re-emits
all three (design (b) of the plan's Task 5 — the JSONL is the only record, so no resume
file can drift from it); a single failed lens is repaired with the per-lens `emit`.

Hermetic: the mocked tests replace the single-emit function and only inspect the call
list; the real-path test writes to tmp_path through the same isolation the sibling
`test_merge_gate_log.py` uses, and its only git calls are read-only against THIS checkout.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
import merge_gate_log as mgl

ROOT = Path(__file__).resolve().parent.parent
LENSES = (
    "merge-gate-concurrency",
    "merge-gate-spec-conformance",
    "merge-gate-witness-adequacy",
)
FILES = {
    "merge-gate-concurrency": "c.txt",
    "merge-gate-spec-conformance": "s.txt",
    "merge-gate-witness-adequacy": "w.txt",
}
BASE_ARGS = [
    "emit-all",
    "--pr",
    "7",
    "--arc-id",
    "b-230-task-5",
    "--concurrency-json",
    "c.txt",
    "--spec-json",
    "s.txt",
    "--witness-json",
    "w.txt",
]


@pytest.fixture(autouse=True)
def _isolated(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HARNESS_GATE_LOG", str(tmp_path / "unused-gate-log.jsonl"))
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", tmp_path / "unused-gate-log.jsonl")
    monkeypatch.setattr(mgl, "GATE_LOG_MD", tmp_path / "unused-log.md")
    monkeypatch.delenv("HARNESS_ROUND_N", raising=False)
    monkeypatch.delenv("HARNESS_ARC_ID", raising=False)
    monkeypatch.setattr(mgl, "config_hash", lambda: "cfg")
    monkeypatch.setattr(mgl, "LENS_SCRATCH", tmp_path)
    monkeypatch.setattr(mgl, "SCRATCH_ANCHOR", tmp_path.parent)


def _run(monkeypatch, codes: dict[str, int], extra: list[str] | None = None):
    """Replace the single-emit function with a recorder that returns `codes[lens]`."""
    calls: list[dict] = []

    def fake(pr, lens, verdict_json, *, base, arc_id, lane_id, round_n, prompt_version):
        calls.append(
            dict(
                pr=pr,
                lens=lens,
                verdict_json=verdict_json,
                base=base,
                arc_id=arc_id,
                lane_id=lane_id,
                round_n=round_n,
                prompt_version=prompt_version,
            )
        )
        return codes[lens]

    monkeypatch.setattr(mgl, "emit_verdict_file", fake)
    rc = mgl.main([*BASE_ARGS, *(extra or [])])
    return rc, calls


def test_a_recorded_block_does_not_abort_the_later_lenses(monkeypatch):
    # (a) concurrency returns 1, the others 0 → all three emitted, in order, exit 1
    rc, calls = _run(monkeypatch, {LENSES[0]: 1, LENSES[1]: 0, LENSES[2]: 0})
    assert rc == 1
    assert [c["lens"] for c in calls] == list(LENSES)
    assert [c["verdict_json"] for c in calls] == [FILES[lens] for lens in LENSES]
    assert {c["pr"] for c in calls} == {7} and {c["arc_id"] for c in calls} == {"b-230-task-5"}


def test_a_not_recorded_middle_lens_still_emits_the_third_and_exits_2(monkeypatch):
    # (b) the middle lens returns 2 → the third is still emitted, exit 2
    rc, calls = _run(monkeypatch, {LENSES[0]: 0, LENSES[1]: 2, LENSES[2]: 0})
    assert rc == 2 and [c["lens"] for c in calls] == list(LENSES)


@pytest.mark.parametrize(
    "codes, expected",
    [
        ((0, 0, 0), 0),
        ((0, 1, 2), 2),  # not-recorded outranks a recorded BLOCK
        ((2, 1, 0), 2),
        ((0, 0, 1), 1),  # a late BLOCK is never masked by earlier approvals
    ],
)
def test_exit_is_the_worst_outcome_across_the_three(monkeypatch, codes, expected):
    rc, calls = _run(monkeypatch, dict(zip(LENSES, codes, strict=True)))
    assert rc == expected and len(calls) == 3


def test_emit_flags_are_forwarded_unchanged_to_every_lens(monkeypatch):
    rc, calls = _run(
        monkeypatch,
        dict.fromkeys(LENSES, 0),
        ["--base", "HEAD", "--lane-id", "h", "--round-n", "4", "--prompt-version", "pv"],
    )
    assert rc == 0
    for c in calls:
        assert (c["base"], c["lane_id"], c["round_n"], c["prompt_version"]) == (
            "HEAD",
            "h",
            4,
            "pv",
        )


def test_emit_flag_defaults_match_the_single_emit_defaults(monkeypatch):
    _, calls = _run(monkeypatch, dict.fromkeys(LENSES, 0))
    for c in calls:
        assert (c["base"], c["lane_id"], c["round_n"], c["prompt_version"]) == (
            "main",
            None,
            None,
            mgl.PROMPT_VERSION,
        )


def _lens_output(binding: dict, verdict: str) -> str:
    # the schema requires a BLOCK to name at least one finding
    findings = [] if verdict == "APPROVE" else [{"severity": "P1", "location": "x", "message": "m"}]
    body = {"verdict": verdict, "findings": findings, **binding}
    tail = "VERDICT: APPROVE" if verdict == "APPROVE" else "VERDICT: BLOCK: the lens reason"
    return "prose\n```json\n" + json.dumps(body) + "\n```\n" + tail + "\n"


def test_real_path_records_three_rows_per_run_and_never_skips(tmp_path, monkeypatch):
    """No resumption: the second run re-emits all three (six rows), each lens's rows
    carrying its own identity; a real BLOCK on one lens is the exit even when the two
    lenses after it approve."""
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    paths = {}
    for lens in LENSES:
        b = mgl.lens_binding(mgl.REPO, "HEAD", lens, cfg_hash="cfg")
        f = tmp_path / f"{lens}.txt"
        f.write_text(_lens_output(b, "BLOCK" if lens == LENSES[0] else "APPROVE"))
        paths[lens] = str(f)
    argv = [
        "emit-all",
        "--pr",
        "9",
        "--arc-id",
        "b-230-task-5",
        "--concurrency-json",
        paths[LENSES[0]],
        "--spec-json",
        paths[LENSES[1]],
        "--witness-json",
        paths[LENSES[2]],
        "--base",
        "HEAD",
        "--lane-id",
        "h",
    ]
    assert mgl.main(argv) == 1
    rows = fr.read_rows(jl)
    assert [r["producer"] for r in rows] == list(LENSES)
    assert rows[0]["record_kind"] == "finding" and rows[0]["finding_type"] == "terminal-block"
    assert [r["record_kind"] for r in rows[1:]] == ["no_finding", "no_finding"]
    assert md.read_text().count("\n") == 3
    assert mgl.main(argv) == 1
    assert [r["producer"] for r in fr.read_rows(jl)] == list(LENSES) * 2


def test_a_missing_verdict_file_is_not_recorded_but_the_rest_still_are(tmp_path, monkeypatch):
    md, jl = tmp_path / "log.md", tmp_path / "log.jsonl"
    monkeypatch.setattr(mgl, "GATE_LOG_MD", md)
    monkeypatch.setattr(fr, "GATE_LOG_JSONL", jl)
    paths = {}
    for lens in LENSES:
        b = mgl.lens_binding(mgl.REPO, "HEAD", lens, cfg_hash="cfg")
        f = tmp_path / f"{lens}.txt"
        f.write_text(_lens_output(b, "APPROVE"))
        paths[lens] = str(f)
    rc = mgl.main(
        [
            "emit-all",
            "--pr",
            "9",
            "--arc-id",
            "b-230-task-5",
            "--concurrency-json",
            paths[LENSES[0]],
            "--spec-json",
            str(tmp_path / "absent.txt"),
            "--witness-json",
            paths[LENSES[2]],
            "--base",
            "HEAD",
            "--lane-id",
            "h",
        ]
    )
    assert rc == 2
    # the two readable lenses ARE recorded; the absent one left no row of its own
    assert [r["producer"] for r in fr.read_rows(jl)] == [LENSES[0], LENSES[2]]


def test_the_single_emit_subcommand_still_routes_through_the_shared_function(monkeypatch):
    seen = []
    monkeypatch.setattr(mgl, "emit_verdict_file", lambda *a, **k: seen.append((a, k)) or 1)
    rc = mgl.main(["emit", "--pr", "3", "--lens", LENSES[1], "--verdict-json", "x.txt"])
    assert rc == 1 and seen[0][0] == (3, LENSES[1], "x.txt")


def test_just_recipe_names_the_subcommand():
    # (e) `just --show merge-gate-emit-all` names the subcommand and forwards every arg
    real = shutil.which("just")
    assert real is not None, "just must be installed: the recipe test reads it"
    out = subprocess.run(
        [real, "--show", "merge-gate-emit-all"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        env={**os.environ},
        check=True,
    ).stdout
    assert "merge_gate_log.py emit-all" in out and '"$@"' in out
