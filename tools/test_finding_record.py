"""C-HE-24 finding record: schema, write-time checks, reducer, projection."""

from __future__ import annotations

import fcntl
import json
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import codex_context_guard as cg
import finding_record as fr
from codex_context_guard import Finding

HEAD = "a" * 40
LOC = "tools/x.py:12"
FID = fr.make_finding_id("merge-gate", HEAD, LOC, 1)  # consistent with the _core/_env defaults


def _core(**over):
    base = dict(
        location=LOC,
        observed_evidence="lease acquired without pr",
        expected_contract="C-HE-06 §3",
        severity="P1",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    base.update(over)
    # The id binds producer + head + location (C-HE-24 §4); derive it from the (possibly
    # overridden) fields unless a test pins one explicitly.
    base.setdefault("finding_id", fr.make_finding_id(base["producer"], HEAD, base["location"], 1))
    return fr.FindingCore(**base)


def _env(**over):
    base = dict(
        record_kind="finding",
        ts="2026-08-18T00:00:00Z",
        arc_id="pr-1",
        lane_id="host-wt-abcdef01",
        head_sha=HEAD,
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
    fid = FID
    fr.append_row(fr.make_row(_core(finding_id=fid), _env()), p)
    with pytest.raises(fr.RecordError, match="core field 'severity'"):
        fr.append_row(
            fr.make_row(
                _core(finding_id=fid, severity="P3"),
                _env(
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="operator",
                ),
            ),
            p,
        )
    with pytest.raises(
        fr.RecordError, match="finding_id producer component"
    ):  # producer swapped to evade the self-disposition ban -> the id no longer names the row
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
                _core(finding_id=fr.make_finding_id("merge-gate", HEAD, LOC, 99)),
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
    fid = FID
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
    fid = FID
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
    fid = FID
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


# mutation-probe: drop the `_check_finding_id_components(row)` call in validate()
def test_finding_id_components_must_agree_with_the_row():
    """The id is the only join key, so a row whose id names another producer / head / location
    would collapse unrelated findings or mis-attach a disposition (Codex round-2 P2)."""
    with pytest.raises(fr.RecordError, match="not <producer>"):
        fr.validate(fr.make_row(_core(finding_id="merge-gate:abc:loc:1"), _env()))
    with pytest.raises(fr.RecordError, match="producer component"):
        fr.validate(
            fr.make_row(_core(finding_id=fr.make_finding_id("codex", HEAD, LOC, 1)), _env())
        )
    with pytest.raises(fr.RecordError, match="location-hash"):
        fr.validate(
            fr.make_row(
                _core(finding_id=fr.make_finding_id("merge-gate", HEAD, "elsewhere", 1)), _env()
            )
        )
    with pytest.raises(fr.RecordError, match="head component"):
        fr.validate(
            fr.make_row(
                _core(finding_id=fr.make_finding_id("merge-gate", "b" * 40, LOC, 1)), _env()
            )
        )
    # a null head_sha row is not held to the head component (the other three still bind)
    fr.validate(
        fr.make_row(
            _core(finding_id=fr.make_finding_id("merge-gate", "b" * 40, LOC, 1)),
            _env(head_sha=None),
        )
    )


# mutation-probe: drop the `_lock_exclusive(fh, path)` line in append_row()
def test_check_and_append_are_one_critical_section(tmp_path: Path, monkeypatch):
    """Two writers minting the same finding_id with CONFLICTING cores: exactly one row lands and
    the other writer is rejected -- never two conflicting rows (Codex round-2 P1). The barrier
    inside the (patched) prior-rows read only rendezvous when both writers are inside the check
    at once, i.e. only when the check-and-append is NOT serialized."""
    p = tmp_path / "g.jsonl"
    gate = threading.Barrier(2, timeout=1.0)
    real_read = fr.read_rows

    def read_then_rendezvous(path=None):
        rows = real_read(path)
        try:
            gate.wait()  # unserialized: both arrive -> both saw an empty log -> both append
        except threading.BrokenBarrierError:
            pass  # serialized: the holder times out here, the waiter finds the barrier broken
        return rows

    monkeypatch.setattr(fr, "read_rows", read_then_rendezvous)
    errors: list[BaseException] = []

    def writer(evidence: str) -> None:
        try:
            fr.append_row(fr.make_row(_core(observed_evidence=evidence), _env()), p)
        except fr.RecordError as exc:
            errors.append(exc)

    threads = [threading.Thread(target=writer, args=(e,)) for e in ("first", "second")]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=30)
    rows = real_read(p)
    assert len(rows) == 1, rows
    assert len(errors) == 1 and "core field 'observed_evidence'" in str(errors[0])


def test_lock_wait_is_bounded(tmp_path: Path):
    """A held lock makes append_row fail LOUDLY after the bounded wait, never hang."""
    p = tmp_path / "g.jsonl"
    p.write_text("")
    with p.open("a") as holder:
        fr._lock_exclusive(holder, p)
        try:
            with pytest.raises(fr.RecordError, match="could not lock"):
                fr._lock_exclusive(p.open("a"), p, timeout_s=0.2)
        finally:
            fcntl.flock(holder.fileno(), fcntl.LOCK_UN)


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


def _guard_state() -> cg.GuardState:
    # Mirrors tools/test_codex_context_guard.py::_state -- the report's non-findings fields are
    # incidental here; the assertion is on the `findings` list it renders.
    return cg.GuardState(
        root=Path("/repo"),
        cwd=Path("/repo"),
        branch="feature",
        default_branch="main",
        head8="abc12345",
        git_dir=".git/worktrees/feature",
        is_linked_worktree=True,
        status_entries=[],
        changed_files=[],
        roadmap_status=cg.RoadmapStatusState(
            hash="abc", git_head="abc12345", last_refreshed="2026-06-05T00:00:00-06:00"
        ),
        computed_hash="abc",
        open_prs="",
        open_prs_available=True,
        fork_doc_count=0,
        latest_retirement_batch=".harness/phase-7d-retirement-events-batch-51.md",
        lag_expected=False,
        owed_lag=False,
    )


def test_projection_round_trip_through_json_report_keeps_existing_codes_byte_identical():
    """C-HE-24 §Verification: record -> `Finding` -> `_json_report` unchanged for pre-existing
    codes. The REAL path (Codex round-3 P2): a projected record row and a pre-existing guard
    finding go through `codex_context_guard._json_report` together; the pre-existing code comes
    out byte-identical and the projected one carries the namespaced triple -- neither is
    split, re-shaped, or dropped by the report."""
    pre_existing = Finding("hard", "ROADMAP_STATUS_DRIFT", "x")
    row = fr.make_row(_core(finding_type="terminal-block"), _env(cause_attribution="lease_lost"))
    projected = fr.to_guard_finding(row)
    report = json.loads(cg._json_report(_guard_state(), [pre_existing, projected]))
    assert report["findings"] == [
        {"severity": "hard", "code": "ROADMAP_STATUS_DRIFT", "message": "x"},
        {
            "severity": "hard",
            "code": "merge-gate:terminal-block:lease_lost",
            "message": row["observed_evidence"],
        },
    ]
    assert json.dumps(report["findings"][0]) == json.dumps(pre_existing.__dict__)
