"""C-HE-24 finding record: schema, write-time checks, reducer, projection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import finding_record as fr
from codex_context_guard import Finding


def _core(**over):
    base = dict(
        finding_id="merge-gate:abc123:0000deadbeef:1",
        location="tools/x.py:12",
        observed_evidence="lease acquired without pr",
        expected_contract="C-HE-06 §3",
        severity="P1",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    base.update(over)
    return fr.FindingCore(**base)


def _env(**over):
    base = dict(
        record_kind="finding",
        ts="2026-08-18T00:00:00Z",
        arc_id="pr-1",
        lane_id="host-wt-abcdef01",
        head_sha="a" * 40,
        base_sha="b" * 40,
        diff_digest="c" * 64,
        round_n=1,
    )
    base.update(over)
    return fr.Envelope(**base)


def test_row_validates_against_schema():
    row = fr.make_row(_core(), _env())
    fr.validate(row)  # no raise
    assert set(row) == set(fr.SCHEMA["properties"])


def test_schema_is_closed():
    row = fr.make_row(_core(), _env())
    row["extra"] = 1
    with pytest.raises(fr.RecordError):
        fr.validate(row)


def test_record_kind_union_enforced():
    with pytest.raises(fr.RecordError):
        fr.validate(fr.make_row(_core(), _env(record_kind="arc")))


# mutation-probe: drop the `disposition_actor == producer` check in validate()
def test_self_disposition_rejected_at_write(tmp_path: Path):
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env()), p)  # the original finding
    row = fr.make_row(
        _core(),
        _env(
            record_kind="finding_adjudication",
            disposition="accepted",
            disposition_actor="merge-gate",
        ),
    )
    with pytest.raises(fr.RecordError, match="disposition_actor"):
        fr.append_row(row, p)
    assert len(fr.read_rows(p)) == 1


def test_adjudication_requires_actor():
    with pytest.raises(fr.RecordError):
        fr.validate(
            fr.make_row(_core(), _env(record_kind="finding_adjudication", disposition="accepted"))
        )


# The `:` ban has ONE enforcement point -- the schema `pattern` -- so there is no Python guard
# line to mutation-probe; the hand witness (drop the pattern -> this test red) is in the PR body.
@pytest.mark.parametrize("field", ["producer", "lane_id"])
def test_colon_in_identifier_rejected(field):
    kwargs = {field: "bad:id"}
    if field == "producer":
        row = fr.make_row(_core(**kwargs), _env())
    else:
        row = fr.make_row(_core(), _env(**kwargs))
    with pytest.raises(fr.RecordError, match=":"):
        fr.validate(row)


# mutation-probe: drop the _check_against_prior_rows() call from append_row()
def test_adjudication_cannot_change_core_or_evade_self_disposition(tmp_path: Path):
    p = tmp_path / "g.jsonl"
    fid = "merge-gate:abc:loc:1"
    fr.append_row(fr.make_row(_core(finding_id=fid), _env()), p)
    with pytest.raises(fr.RecordError, match="core field"):
        fr.append_row(
            fr.make_row(
                _core(finding_id=fid, location="elsewhere"),
                _env(
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="operator",
                ),
            ),
            p,
        )
    with pytest.raises(
        fr.RecordError, match="core field 'producer'"
    ):  # producer swapped to evade the self-disposition ban -> a core-field change
        fr.append_row(
            fr.make_row(
                _core(finding_id=fid, producer="operator"),
                _env(
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="merge-gate",
                ),
            ),
            p,
        )
    with pytest.raises(
        fr.RecordError, match="core field"
    ):  # envelope fields are immutable too (round-3 P2)
        fr.append_row(
            fr.make_row(
                _core(finding_id=fid),
                _env(
                    lane_id="other-lane",
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="operator",
                ),
            ),
            p,
        )
    with pytest.raises(fr.RecordError, match="unknown finding_id"):
        fr.append_row(
            fr.make_row(
                _core(finding_id="never-seen"),
                _env(
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="operator",
                ),
            ),
            p,
        )
    fr.append_row(  # legal
        fr.make_row(
            _core(finding_id=fid),
            _env(
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
        p,
    )


# mutation-probe: drop the `elif` non-adjudication null-disposition branch in validate()
@pytest.mark.parametrize("kind", ["finding", "no_finding", "gate_demotion"])
def test_only_adjudication_rows_carry_disposition(kind):
    """C-HE-24 §5: a pre-disposed non-adjudication row would let a reviewer dispose its own
    finding without any append-only adjudication event (Codex round-1 P1)."""
    with pytest.raises(fr.RecordError, match="null disposition"):
        fr.validate(fr.make_row(_core(), _env(record_kind=kind, disposition="accepted")))
    with pytest.raises(fr.RecordError, match="null disposition"):
        fr.validate(fr.make_row(_core(), _env(record_kind=kind, disposition_actor="operator")))
    fr.validate(fr.make_row(_core(), _env(record_kind=kind)))  # null both -> legal


def test_repeated_finding_row_must_keep_the_same_core(tmp_path: Path):
    """C-HE-24 invariant: two rows with one finding_id differ only by ts / record_kind /
    disposition / disposition_actor / unique_catch -- for a repeated `finding` row too, not only
    adjudications (Codex round-1 P1)."""
    p = tmp_path / "g.jsonl"
    fid = "merge-gate:abc:loc:1"
    fr.append_row(fr.make_row(_core(finding_id=fid), _env()), p)
    with pytest.raises(fr.RecordError, match="core field 'observed_evidence'"):
        fr.append_row(fr.make_row(_core(finding_id=fid, observed_evidence="rewritten"), _env()), p)
    with pytest.raises(fr.RecordError, match="core field 'severity'"):
        fr.append_row(fr.make_row(_core(finding_id=fid, severity="P3"), _env()), p)
    fr.append_row(
        fr.make_row(_core(finding_id=fid), _env(ts="2026-08-18T00:00:09Z")), p
    )  # same core: legal
    assert len(fr.read_rows(p)) == 2


def test_reducer_uses_file_order_not_ts(tmp_path: Path):
    """The append-only log is the ordering authority: a later physical row with an EARLIER ts
    (clock regression / back-fill) still wins (Codex round-1 P2)."""
    p = tmp_path / "g.jsonl"
    fid = "merge-gate:abc:loc:1"
    fr.append_row(fr.make_row(_core(finding_id=fid), _env(ts="2026-08-18T00:00:05Z")), p)
    fr.append_row(
        fr.make_row(
            _core(finding_id=fid),
            _env(
                ts="2026-08-18T00:00:01Z",  # earlier than the row before it
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
        p,
    )
    last = fr.reduce_last_by_finding_id(fr.read_rows(p))
    assert last[fid]["disposition"] == "accepted"


def test_reducer_last_row_wins(tmp_path: Path):
    p = tmp_path / "g.jsonl"
    fid = "merge-gate:abc:loc:1"
    fr.append_row(fr.make_row(_core(finding_id=fid), _env(ts="2026-08-18T00:00:00Z")), p)
    fr.append_row(
        fr.make_row(
            _core(finding_id=fid),
            _env(
                ts="2026-08-18T00:00:01Z",
                record_kind="finding_adjudication",
                disposition="rejected",
                disposition_actor="operator",
            ),
        ),
        p,
    )
    fr.append_row(
        fr.make_row(
            _core(finding_id=fid),
            _env(
                ts="2026-08-18T00:00:02Z",
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
        p,
    )
    last = fr.reduce_last_by_finding_id(fr.read_rows(p))
    assert last[fid]["disposition"] == "accepted"


def test_finding_id_shape():
    fid = fr.make_finding_id("codex_review_wrapper", "a" * 40, "tools/x.py:1", 3)
    parts = fid.split(":")
    assert parts[0] == "codex_review_wrapper" and parts[1] == "a" * 40 and parts[3] == "3"
    assert len(parts[2]) == 12


# mutation-probe: drop the `code` join line in to_guard_finding()
def test_projection_code_triple_and_severity_map():
    row = fr.make_row(
        _core(producer="merge-door-lease-acquire", finding_type="transient-retry", severity="P3"),
        _env(cause_attribution="lease_contended"),
    )
    f = fr.to_guard_finding(row)
    assert isinstance(f, Finding)
    assert f.code == "merge-door-lease-acquire:transient-retry:lease_contended"
    assert f.severity == "warn"
    assert f.message == row["observed_evidence"]
    hard = fr.to_guard_finding(fr.make_row(_core(finding_type="permanent-fail-exit"), _env()))
    assert hard.severity == "hard"


def test_projection_round_trip_keeps_existing_codes_byte_identical():
    """Pre-existing guard codes are never re-shaped by the projection layer."""
    f = Finding("hard", "ROADMAP_STATUS_DRIFT", "x")
    assert (
        json.dumps(f.__dict__)
        == '{"severity": "hard", "code": "ROADMAP_STATUS_DRIFT", "message": "x"}'
    )
