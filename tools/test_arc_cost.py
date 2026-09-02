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
    report = ac.cost_report([_write(tmp_path / "t.jsonl", DUPED)], cuts=[])
    m = report["main"]
    assert m["calls"] == 2  # not 4
    assert (m["input"], m["cache_write"], m["cache_read"], m["output"]) == (4, 200, 2000, 30)
    # the naive (non-deduplicated) sum is exactly the duplication factor bigger
    naive_output = sum(
        r["message"]["usage"]["output_tokens"] for r in DUPED if r.get("type") == "assistant"
    )
    assert naive_output == 2 * m["output"]


# mutation-probe(tools/arc_cost.py): keep first-copy usage instead of the per-field max
def test_divergent_copies_merge_by_per_field_max_not_arrival_order(tmp_path: Path) -> None:
    """codex u-he-48 r1: a streaming producer could stamp a partial (even all-zero)
    copy before the final one; the merge must not depend on which copy lands first."""
    partial_first = [
        _rec("req_1", "2026-08-26T04:00:00.000Z", out=0, inp=0, cw=0, cr=0),
        _rec("req_1", "2026-08-26T04:00:01.000Z", out=50),
    ]
    report = ac.cost_report([_write(tmp_path / "a.jsonl", partial_first)], cuts=[])
    assert report["main"]["calls"] == 1
    assert report["main"]["output"] == 50  # the real usage, not the zero copy
    # order-independent: reversed arrival yields the identical totals
    reversed_report = ac.cost_report([_write(tmp_path / "b.jsonl", partial_first[::-1])], cuts=[])
    assert reversed_report["main"] == report["main"]


# mutation-probe(tools/arc_cost.py): dedupe per transcript instead of across the pool
def test_multi_transcript_pool_dedupes_globally(tmp_path: Path) -> None:
    """codex u-he-48 r4: a resumed arc spans sessions, and a resumed session can
    copy prior records into its own transcript -- the pool dedupes by requestId
    across ALL transcripts, so the copied call is priced once."""
    t1 = _write(tmp_path / "s1.jsonl", DUPED)
    # the second session re-embeds req_2 (a copy) and adds its own new call
    t2 = _write(
        tmp_path / "s2.jsonl",
        [
            _rec("req_2", "2026-08-26T05:00:00.000Z", out=20),
            _rec("req_3", "2026-08-26T06:00:00.000Z", out=9),
        ],
    )
    report = ac.cost_report([t1, t2], cuts=[])
    assert report["main"]["calls"] == 3  # req_1, req_2 (once), req_3
    assert report["main"]["output"] == 10 + 20 + 9
    assert report["transcripts"] == [str(t1), str(t2)]


def test_malformed_records_refused_not_traceback(tmp_path: Path) -> None:
    """codex u-he-48 r4 P3: JSON-valid but malformed records must land on the
    exit-2 CostError contract, never an uncaught TypeError/AttributeError."""
    bad_ts = _rec("r1", "2026-08-26T04:00:00.000Z")
    bad_ts["timestamp"] = 12345
    with pytest.raises(ac.CostError, match="no string timestamp"):
        ac.cost_report([_write(tmp_path / "a.jsonl", [bad_ts])], cuts=[])
    bad_tok = _rec("r1", "2026-08-26T04:00:00.000Z")
    bad_tok["message"]["usage"]["output_tokens"] = None
    with pytest.raises(ac.CostError, match="non-negative int"):
        ac.cost_report([_write(tmp_path / "b.jsonl", [bad_tok])], cuts=[])
    neg = _rec("r1", "2026-08-26T04:00:00.000Z")
    neg["message"]["usage"]["input_tokens"] = -1
    with pytest.raises(ac.CostError, match="non-negative int"):
        ac.cost_report([_write(tmp_path / "c.jsonl", [neg])], cuts=[])
    # r7 P3: absent fields are malformed (0 of 20,414 measured blocks omit any),
    # and defaulting to zero would silently undercount
    absent = _rec("r1", "2026-08-26T04:00:00.000Z")
    del absent["message"]["usage"]["output_tokens"]
    with pytest.raises(ac.CostError, match="output_tokens is absent"):
        ac.cost_report([_write(tmp_path / "d.jsonl", [absent])], cuts=[])


def test_zero_yield_subagent_file_refused(tmp_path: Path) -> None:
    """codex u-he-48 r9: an empty or zero-only agent file is a truncated store
    -- pooled silently it would persist files=N with understated cost."""
    t = _write(tmp_path / "sess.jsonl", DUPED)
    subdir = tmp_path / "sess" / "subagents"
    subdir.mkdir(parents=True)
    (subdir / "agent-a.jsonl").write_text("")  # empty sidecar
    with pytest.raises(ac.CostError, match="yields no non-zero calls"):
        ac.cost_report([t], cuts=[])
    zero = _rec("req_s0", "2026-08-26T04:10:00.000Z", out=0, inp=0, cw=0, cr=0)
    _write(subdir / "agent-a.jsonl", [zero])  # zero-only sidecar
    with pytest.raises(ac.CostError, match="yields no non-zero calls"):
        ac.cost_report([t], cuts=[])


def test_present_but_empty_subagents_dir_refused(tmp_path: Path) -> None:
    """codex u-he-48 r7: an existing subagents/ with no agent files never occurs
    naturally (0 of 67 measured) -- it is a GC'd/partial store, and a zero
    there would be a false measurement; an ABSENT dir stays a genuine zero."""
    t = _write(tmp_path / "sess.jsonl", DUPED)
    (tmp_path / "sess" / "subagents").mkdir(parents=True)
    with pytest.raises(ac.CostError, match="exists but holds no agent files"):
        ac.cost_report([t], cuts=[])


def test_iet_formula() -> None:
    t = ac.Totals(calls=1, input=100, cache_write=100, cache_read=100, output=100)
    assert t.iet == 100 + 1.25 * 100 + 0.1 * 100 + 5 * 100


def test_subagent_transcripts_included_and_counted_separately(tmp_path: Path) -> None:
    # the sidechain copy of the subagent call, inlined in the MAIN transcript,
    # must not be double-counted (codex u-he-48 r2; context_budget.py precedent) —
    # subagent-file records carry isSidechain themselves, so the exclusion is
    # main-only, never applied to the subagents/ files
    inlined = _rec("req_s1", "2026-08-26T04:10:00.000Z", out=7)
    inlined["isSidechain"] = True
    t = _write(tmp_path / "sess.jsonl", [*DUPED, inlined])
    subdir = tmp_path / "sess" / "subagents"
    subdir.mkdir(parents=True)
    sub_rec = _rec("req_s1", "2026-08-26T04:10:00.000Z", out=7)
    sub_rec["isSidechain"] = True
    _write(subdir / "agent-a.jsonl", [sub_rec])
    report = ac.cost_report([t], cuts=[])
    assert report["subagents"]["files"] == 1
    assert report["subagents"]["calls"] == 1
    assert report["subagents"]["output"] == 7
    assert report["main"]["calls"] == 2  # the inlined sidechain record stays out of main
    assert report["total_iet"] == report["main"]["iet"] + report["subagents"]["iet"]


def test_windows_partition_at_cut_and_sum_to_whole(tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    report = ac.cost_report([t], cuts=[ac.parse_ts("2026-08-26T04:30:00Z", what="cut")])
    w0, w1 = report["windows"]
    assert (w0["main"]["calls"], w1["main"]["calls"]) == (1, 1)
    assert w0["main"]["output"] + w1["main"]["output"] == report["main"]["output"]


def test_unsorted_cuts_refused(tmp_path: Path) -> None:
    t = _write(tmp_path / "t.jsonl", DUPED)
    cuts = [ac.parse_ts(s, what="cut") for s in ("2026-08-26T05:00:00Z", "2026-08-26T04:00:00Z")]
    with pytest.raises(ac.CostError, match="ascending"):
        ac.cost_report([t], cuts=cuts)


def test_usage_without_request_id_refused_not_guessed(tmp_path: Path) -> None:
    rec = _rec("x", "2026-08-26T04:00:00.000Z")
    del rec["requestId"]
    with pytest.raises(ac.CostError, match="no requestId"):
        ac.cost_report([_write(tmp_path / "t.jsonl", [rec])], cuts=[])


def _synthetic_error(ts: str, **tokens: int) -> dict:
    """The transport's own error row: `isApiErrorMessage`, model "<synthetic>",
    a usage block, no requestId (the 2026-09-02 WAN-outage shape)."""
    rec = _rec("unused", ts, **({"out": 0, "inp": 0, "cw": 0, "cr": 0} | tokens))
    del rec["requestId"]
    rec["isApiErrorMessage"] = True
    rec["message"]["model"] = "<synthetic>"
    return rec


# mutation-probe(tools/arc_cost.py): drop the zero-usage `isApiErrorMessage` skip
def test_synthetic_api_error_row_without_request_id_is_skipped(tmp_path: Path) -> None:
    """u-sr-09 close (2026-09-02): the queue step aborted on one such row --
    it is not a call, and skipping its zero usage changes no total."""
    err = _synthetic_error("2026-09-02T11:36:42.188Z")
    report = ac.cost_report([_write(tmp_path / "t.jsonl", [*DUPED, err])], cuts=[])
    assert report["main"]["calls"] == 2


def test_synthetic_api_error_row_with_tokens_still_refused(tmp_path: Path) -> None:
    """The carve-out is the all-zero shape only: a synthetic row that claims
    tokens is a producer contradiction and keeps the no-requestId refusal
    (0 of 54 synthetic rows across 1,012 transcripts carried tokens at
    2026-09-02, so this pins a shape not yet observed)."""
    err = _synthetic_error("2026-09-02T11:36:42.188Z", out=3)
    with pytest.raises(ac.CostError, match="no requestId"):
        ac.cost_report([_write(tmp_path / "t.jsonl", [*DUPED, err])], cuts=[])


@pytest.mark.parametrize(
    "widen",
    [
        pytest.param({"requestId": ""}, id="present-empty-requestId"),
        pytest.param({"requestId": 0}, id="present-zero-requestId"),
        pytest.param({"model": "claude-opus-5"}, id="non-synthetic-model"),
        pytest.param({"flag": False}, id="flag-false"),
    ],
)
def test_carve_out_is_the_observed_shape_and_nothing_wider(tmp_path: Path, widen: dict) -> None:
    """codex r1: `not rid` would also have swallowed a PRESENT malformed
    requestId, and the model was never checked. Each widening of the observed
    shape keeps the fail-closed refusal."""
    err = _synthetic_error("2026-09-02T11:36:42.188Z")
    if "requestId" in widen:
        err["requestId"] = widen["requestId"]
    if "model" in widen:
        err["message"]["model"] = widen["model"]
    if "flag" in widen:
        err["isApiErrorMessage"] = widen["flag"]
    with pytest.raises(ac.CostError, match="no requestId"):
        ac.cost_report([_write(tmp_path / "t.jsonl", [*DUPED, err])], cuts=[])


def test_transcript_with_no_usage_refused_never_a_zero_cost_arc(tmp_path: Path) -> None:
    with pytest.raises(ac.CostError, match="no assistant usage with non-zero"):
        ac.cost_report([_write(tmp_path / "t.jsonl", [{"type": "user"}])], cuts=[])


# mutation-probe(tools/arc_cost.py): keep all-zero merged calls in the return
def test_all_zero_calls_dropped_and_zero_only_transcript_refused(tmp_path: Path) -> None:
    """codex u-he-48 r6: an all-zero merged call is an aborted request, not work
    -- kept, a truncated transcript would persist as a measured 0-IET arc."""
    zero = _rec("req_z", "2026-08-26T04:20:00.000Z", out=0, inp=0, cw=0, cr=0)
    report = ac.cost_report([_write(tmp_path / "a.jsonl", [*DUPED, zero])], cuts=[])
    assert report["main"]["calls"] == 2  # req_z dropped
    with pytest.raises(ac.CostError, match="no assistant usage with non-zero"):
        ac.cost_report([_write(tmp_path / "b.jsonl", [zero])], cuts=[])


def test_sidechain_work_with_missing_subagent_files_refused(tmp_path: Path) -> None:
    """codex u-he-48 r5: visible sidechain records with NO subagents/ files is a
    GC'd store, not a measured zero -- a zero would read as an artificially
    cheap arc in every cost median."""
    inlined = _rec("req_s1", "2026-08-26T04:10:00.000Z", out=7)
    inlined["isSidechain"] = True
    t = _write(tmp_path / "sess.jsonl", [*DUPED, inlined])  # no subagents/ dir
    with pytest.raises(ac.CostError, match="subagent transcripts are missing"):
        ac.cost_report([t], cuts=[])


def test_non_object_record_message_and_usage_refused(tmp_path: Path) -> None:
    """codex u-he-48 r5 P3: JSON-valid non-object shapes land on the exit-2
    CostError contract, never an AttributeError."""
    t = tmp_path / "a.jsonl"
    t.write_text('"just a string"\n')
    with pytest.raises(ac.CostError, match="not a transcript record object"):
        ac.cost_report([t], cuts=[])
    bad_msg = {"type": "assistant", "requestId": "r1", "message": "nope"}
    with pytest.raises(ac.CostError, match="message is not an object"):
        ac.cost_report([_write(tmp_path / "b.jsonl", [bad_msg])], cuts=[])
    bad_usage = {"type": "assistant", "requestId": "r1", "message": {"usage": [1]}}
    with pytest.raises(ac.CostError, match="usage is not a non-empty object"):
        ac.cost_report([_write(tmp_path / "c.jsonl", [bad_usage])], cuts=[])
    # r8 P3: a PRESENT empty usage is malformed (0 of 30,595 measured records)
    # -- silently skipping it would understate the arc; absent usage still skips
    empty_usage = {"type": "assistant", "requestId": "r1", "message": {"usage": {}}}
    with pytest.raises(ac.CostError, match="usage is not a non-empty object"):
        ac.cost_report([_write(tmp_path / "d2.jsonl", [*DUPED, empty_usage])], cuts=[])


# mutation-probe(justfile): delete the arc-cost recipe
def test_justfile_carries_the_arc_cost_recipe() -> None:
    """codex u-he-48 r5 P3: the spec's public command is `just arc-cost` -- the
    module tests stay green if the recipe is deleted, so pin it statically."""
    justfile = (Path(__file__).resolve().parents[1] / "justfile").read_text()
    recipe = justfile[justfile.index("arc-cost *ARGS:") :].split("\n\n")[0]
    assert "tools/arc_cost.py" in recipe


def test_missing_transcript_is_exit_2(tmp_path: Path, capsys) -> None:
    assert ac.main([str(tmp_path / "absent.jsonl")]) == 2
    assert "ERROR" in capsys.readouterr().err


# -- the arc-row seam (arc_metrics --transcript -> cost_* fields) -----------


def _stub_reservation(monkeypatch, reserved_at: str = "2026-08-26T00:00:00.000Z") -> None:
    import reservations as rs

    monkeypatch.setattr(rs, "current", lambda arc_id: ("head", {"reserved_at": reserved_at}))


def test_cost_snapshot_shape_matches_the_fold(monkeypatch, tmp_path: Path) -> None:
    _stub_reservation(monkeypatch)
    t = _write(tmp_path / "t.jsonl", DUPED)
    snap = am._cost_snapshot([str(t)], "u-x")
    assert snap == {
        "main_calls": 2,
        "main_iet": ac.cost_report([t], cuts=[])["main"]["iet"],
        "subagent_calls": 0,
        "subagent_iet": 0.0,
        "source": str(t),
    }


# mutation-probe(tools/arc_metrics.py): pass cuts=[] instead of the reserved_at cut
def test_cost_snapshot_is_bounded_to_the_arc_window(monkeypatch, tmp_path: Path) -> None:
    """codex u-he-48 r3: one session ships consecutive arcs — usage before this
    arc's reserved_at belongs to earlier arcs and must stay out of its row."""
    _stub_reservation(monkeypatch, reserved_at="2026-08-26T04:30:00.000Z")
    t = _write(tmp_path / "t.jsonl", DUPED)  # req_1 at 04:00 (before), req_2 at 05:00
    snap = am._cost_snapshot([str(t)], "u-x")
    assert snap is not None and snap["main_calls"] == 1
    assert snap["main_iet"] == 2 + 1.25 * 100 + 0.1 * 1000 + 5 * 20  # req_2 only


def test_cost_snapshot_without_reservation_skips_never_totals_the_session(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    import reservations as rs

    monkeypatch.setattr(rs, "current", lambda arc_id: None)
    t = _write(tmp_path / "t.jsonl", DUPED)
    assert am._cost_snapshot([str(t)], "u-x") is None
    assert "cost skipped" in capsys.readouterr().out


def test_cost_snapshot_refuses_a_transcript_with_no_usage_in_the_window(
    monkeypatch, tmp_path: Path
) -> None:
    """A wrong (older) transcript has no calls after reserved_at — a false
    measured-zero must not enter the ledger."""
    _stub_reservation(monkeypatch, reserved_at="2026-08-27T00:00:00.000Z")
    t = _write(tmp_path / "t.jsonl", DUPED)  # all records predate the boundary
    with pytest.raises(am.AbortError, match="wrong transcript"):
        am._cost_snapshot([str(t)], "u-x")


def test_cost_snapshot_failure_aborts_loudly(monkeypatch, tmp_path: Path) -> None:
    _stub_reservation(monkeypatch)
    with pytest.raises(am.AbortError, match="cost extraction failed"):
        am._cost_snapshot([str(tmp_path / "absent.jsonl")], "u-x")


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
        cost_skip_reason=kw.get("cost_skip_reason"),
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


def test_unbounded_transcript_records_no_arc_boundary_provenance(
    _gh_stub, monkeypatch, tmp_path: Path
) -> None:
    """codex u-he-48 r6 P3: a supplied-but-unboundable transcript is not
    "no transcript supplied" -- the ledger provenance carries the real reason."""
    import reservations as rs

    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    monkeypatch.setattr(rs, "current", lambda arc_id: None)
    t = _write(tmp_path / "t.jsonl", DUPED)
    assert (
        am.main(
            [
                "queue",
                "--pr",
                "1",
                "--arc-id",
                "u-nb",
                "--arc-type",
                "inventing",
                "--decisions",
                "0",
                "--transcript",
                str(t),
            ]
        )
        == 0
    )
    entry = am.read_queue()[0][1]
    assert entry["cost_snapshot"] is None
    assert entry["cost_skip_reason"] == "no-arc-boundary"
    row = am.extract(_extract_args(cost_skip_reason="no-arc-boundary"))
    assert row.provenance["cost_fields"] == "unmapped:no-arc-boundary"


# mutation-probe(tools/arc_metrics.py): drop the queue-time _cost_snapshot call, or
# drop cost_snapshot from _drain_one's Namespace — either leaves this red
def test_production_queue_to_drain_path_carries_the_cost_snapshot(
    monkeypatch, tmp_path: Path
) -> None:
    """codex u-he-48 r2: the extract-level tests stay green with the closure-time
    snapshot or its drain forwarding deleted; this witness walks the real path —
    queue_capture writes the snapshot, drain's Namespace forwards it."""
    import reservations as rs

    qdir = tmp_path / "queue"
    monkeypatch.setattr(am, "QUEUE_DIR", qdir)
    # isolate the reservations store the drain's bootstrap reserve writes into
    monkeypatch.setattr(rs, "QUEUE_DIR", qdir)
    monkeypatch.setattr(rs, "emit_loop_row", lambda *a, **k: None)
    t = _write(tmp_path / "t.jsonl", DUPED)
    # Independent patch for the QUEUE phase only: the window boundary must stub
    # a head whose reserved_at admits the fixture records, but the DRAIN phase
    # below needs the real (isolated) reservation flow, so undo before drain.
    qp = pytest.MonkeyPatch()
    qp.setattr(rs, "current", lambda arc_id: ("head", {"reserved_at": "2026-08-26T00:00:00Z"}))
    try:
        # through the REAL parser (codex u-he-48 r5): reverting the queue
        # subcommand's --transcript option must red this, not only a Namespace
        assert (
            am.main(
                [
                    "queue",
                    "--pr",
                    "1",
                    "--arc-id",
                    "u-qc",
                    "--arc-type",
                    "inventing",
                    "--decisions",
                    "0",
                    "--transcript",
                    str(t),
                ]
            )
            == 0
        )
    finally:
        qp.undo()
    entries = am.read_queue()
    assert len(entries) == 1
    snap = entries[0][1]["cost_snapshot"]
    assert snap["main_calls"] == 2 and snap["source"] == str(t)

    captured: dict = {}

    def capture(args: argparse.Namespace):
        captured["cost_snapshot"] = args.cost_snapshot
        raise am.AbortError("stop after capture")  # keep the entry queued, skip append

    monkeypatch.setattr(am, "extract", capture)
    monkeypatch.setattr(am, "committed_arc_ids", set)
    am.drain(argparse.Namespace())
    assert captured["cost_snapshot"] == snap


# -- live witness: the [B] audit headline ------------------------------------


@pytest.mark.skipif(not U_HE_35_TRANSCRIPT.is_file(), reason="archived U-HE-35 transcript GC'd")
def test_b_audit_headline_reproduced_on_the_archived_transcript() -> None:
    """[B] Evidence and method: 418 main calls / ~20.99M IET main / ~4.52M subagents.

    The transcript outlived the audit (the session continued), so the witness
    bounds at the audit's last-record timestamp via a stage-window cut. Main
    reproduces [B] exactly (its usage copies are identical: 0 divergent of 428
    requestIds). Subagents reproduce the call count exactly but the IET lands
    0.12M ABOVE [B]'s 4.52M: the subagent files stamp an early partial
    output_tokens copy before the final one (measured: 42 of 291 requestIds),
    [B]'s first-copy read undercounted those calls, and the per-field-max merge
    (codex u-he-48 r1) prices the final copy instead.
    """
    cut = ac.parse_ts("2026-08-26T21:16:18Z", what="cut")
    report = ac.cost_report([U_HE_35_TRANSCRIPT], cuts=[cut])
    audited = report["windows"][0]
    assert audited["main"]["calls"] == 418
    assert round(audited["main"]["iet"]) == 20_996_434  # 20.99M, == [B]
    assert audited["subagents"]["calls"] == 286
    assert round(audited["subagents"]["iet"]) == 4_636_541  # [B]'s 4.52M + corrected output
