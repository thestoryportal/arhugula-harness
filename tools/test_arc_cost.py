"""Witnesses for the per-arc cost extractor (U-HE-48, C-HE-25 v1.6 X6e).

The load-bearing property is requestId dedupe: a transcript stores one
assistant record per content block, each carrying a COPY of the same usage
block, so a naive sum double-counts (~1.9x on the [B] audit transcript). The
synthetic fixture here asserts that delta directly; the live witness (skipped
when the archived U-HE-35 transcript is absent) reproduces the [B] headline.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import arc_cost as ac
import arc_metrics as am

U_HE_35_TRANSCRIPT = Path(
    "~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/"
    "b6bed0d9-79b6-4d82-8c35-bc94342f1706.jsonl"
).expanduser()


def _rec(rid: str, ts: str, out: int = 10, inp: int = 2, cw: int = 100, cr: int = 1000) -> dict:
    return {
        "type": "assistant",
        "requestId": rid,
        "timestamp": ts,
        "message": {
            "usage": {
                "input_tokens": inp,
                "cache_creation_input_tokens": cw,
                "cache_read_input_tokens": cr,
                "output_tokens": out,
            }
        },
    }


def _write(path: Path, records: list[dict]) -> Path:
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    return path


# Two calls, each stored as two block records with identical usage copies --
# the exact duplication shape the [B] audit measured at 1.9x.
DUPED = [
    _rec("req_1", "2026-08-26T04:00:00.000Z"),
    _rec("req_1", "2026-08-26T04:00:00.000Z"),
    _rec("req_2", "2026-08-26T05:00:00.000Z", out=20),
    _rec("req_2", "2026-08-26T05:00:00.000Z", out=20),
    {"type": "user", "timestamp": "2026-08-26T04:30:00.000Z"},
]


# mutation-probe(tools/arc_cost.py): count every usage record instead of one per requestId
def test_dedupe_collapses_duplicate_request_ids(tmp_path: Path) -> None:
    report = ac.cost_report(_write(tmp_path / "t.jsonl", DUPED), cuts=[])
    m = report["main"]
    assert m["calls"] == 2  # not 4
    assert (m["input"], m["cache_write"], m["cache_read"], m["output"]) == (4, 200, 2000, 30)
    # the naive (non-deduplicated) sum is exactly the duplication factor bigger
    naive_output = sum(
        r["message"]["usage"]["output_tokens"] for r in DUPED if r.get("type") == "assistant"
    )
    assert naive_output == 2 * m["output"]


def test_iet_formula() -> None:
    t = ac.Totals(calls=1, input=100, cache_write=100, cache_read=100, output=100)
    assert t.iet == 100 + 1.25 * 100 + 0.1 * 100 + 5 * 100


def test_subagent_transcripts_included_and_counted_separately(tmp_path: Path) -> None:
    t = _write(tmp_path / "sess.jsonl", DUPED)
    subdir = tmp_path / "sess" / "subagents"
    subdir.mkdir(parents=True)
    _write(subdir / "agent-a.jsonl", [_rec("req_s1", "2026-08-26T04:10:00.000Z", out=7)])
    report = ac.cost_report(t, cuts=[])
    assert report["subagents"]["files"] == 1
    assert report["subagents"]["calls"] == 1
    assert report["subagents"]["output"] == 7
    assert report["main"]["calls"] == 2  # subagent usage never pools into main
    assert report["total_iet"] == report["main"]["iet"] + report["subagents"]["iet"]


def test_windows_partition_at_cut_and_sum_to_whole(tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    report = ac.cost_report(t, cuts=[ac.parse_ts("2026-08-26T04:30:00Z", what="cut")])
    w0, w1 = report["windows"]
    assert (w0["main"]["calls"], w1["main"]["calls"]) == (1, 1)
    assert w0["main"]["output"] + w1["main"]["output"] == report["main"]["output"]


def test_unsorted_cuts_refused(tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    cuts = [ac.parse_ts(s, what="cut") for s in ("2026-08-26T05:00:00Z", "2026-08-26T04:00:00Z")]
    with pytest.raises(ac.CostError, match="ascending"):
        ac.cost_report(t, cuts=cuts)


def test_usage_without_request_id_refused_not_guessed(tmp_path: Path) -> None:
    rec = _rec("x", "2026-08-26T04:00:00.000Z")
    del rec["requestId"]
    with pytest.raises(ac.CostError, match="no requestId"):
        ac.cost_report(_write(tmp_path / "t.jsonl", [rec]), cuts=[])


def test_transcript_with_no_usage_refused_never_a_zero_cost_arc(tmp_path: Path) -> None:
    with pytest.raises(ac.CostError, match="no assistant usage"):
        ac.cost_report(_write(tmp_path / "t.jsonl", [{"type": "user"}]), cuts=[])


def test_missing_transcript_is_exit_2(tmp_path: Path, capsys) -> None:
    assert ac.main([str(tmp_path / "absent.jsonl")]) == 2
    assert "ERROR" in capsys.readouterr().err


# -- the arc-row seam (arc_metrics --transcript -> cost_* fields) -----------


def test_cost_snapshot_shape_matches_the_fold(tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    snap = am._cost_snapshot(str(t))
    assert snap == {
        "main_calls": 2,
        "main_iet": ac.cost_report(t, cuts=[])["main"]["iet"],
        "subagent_calls": 0,
        "subagent_iet": 0.0,
        "source": str(t),
    }


def test_cost_snapshot_failure_aborts_loudly(tmp_path: Path) -> None:
    with pytest.raises(am.AbortError, match="cost extraction failed"):
        am._cost_snapshot(str(tmp_path / "absent.jsonl"))


def _extract_args(**kw) -> argparse.Namespace:
    return argparse.Namespace(
        pr=1,
        arc_id="u-test",
        arc_type="inventing",
        arc_type_declared_at="open",
        decisions=0,
        round_snapshot=None,
        round_logs=None,
        cost_snapshot=kw.get("cost_snapshot"),
        transcript=kw.get("transcript"),
        levers=[],
        notes="",
    )


@pytest.fixture
def _gh_stub(monkeypatch):
    monkeypatch.setattr(
        am,
        "gh_pr",
        lambda pr: {
            "additions": 1,
            "changedFiles": 1,
            "commits": [],
            "createdAt": "2026-08-27T00:00:00Z",
        },
    )


# mutation-probe(tools/arc_metrics.py): drop the cost_snapshot fold in extract()
def test_extract_folds_cost_snapshot_onto_the_row(_gh_stub) -> None:
    snap = {
        "main_calls": 5,
        "main_iet": 1000.5,
        "subagent_calls": 2,
        "subagent_iet": 50.0,
        "source": "/tmp/t.jsonl",
    }
    row = am.extract(_extract_args(cost_snapshot=snap))
    assert (row.cost_main_calls, row.cost_main_iet) == (5, 1000.5)
    assert (row.cost_subagent_calls, row.cost_subagent_iet) == (2, 50.0)
    assert row.cost_source == "/tmp/t.jsonl"
    assert row.provenance["cost_fields"] == "derived"


def test_extract_without_transcript_reads_null_never_zero(_gh_stub) -> None:
    row = am.extract(_extract_args())
    assert row.cost_main_calls is None
    assert row.cost_main_iet is None
    assert row.provenance["cost_fields"] == "unmapped:no-transcript-supplied"


def test_extract_derives_live_when_only_a_transcript_is_given(_gh_stub, tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    row = am.extract(_extract_args(transcript=str(t)))
    assert row.cost_main_calls == 2
    assert row.cost_source == str(t)


# -- live witness: the [B] audit headline ------------------------------------


@pytest.mark.skipif(not U_HE_35_TRANSCRIPT.is_file(), reason="archived U-HE-35 transcript GC'd")
def test_b_audit_headline_reproduced_on_the_archived_transcript() -> None:
    """[B] Evidence and method: 418 main calls / ~20.99M IET main / ~4.52M subagents.

    The transcript outlived the audit (the session continued), so the witness
    bounds at the audit's last-record timestamp via a stage-window cut.
    """
    cut = ac.parse_ts("2026-08-26T21:16:18Z", what="cut")
    report = ac.cost_report(U_HE_35_TRANSCRIPT, cuts=[cut])
    audited = report["windows"][0]
    assert audited["main"]["calls"] == 418
    assert round(audited["main"]["iet"]) == 20_996_434  # 20.99M
    assert audited["subagents"]["calls"] == 286
    assert round(audited["subagents"]["iet"]) == 4_516_426  # 4.52M
