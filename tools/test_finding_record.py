"""C-HE-24 finding record: schema, write-time checks, reducer, projection."""

from __future__ import annotations

import fcntl
import json
import os
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
            ts="2026-08-18T00:00:01Z",  # later ts: the self-disposition ban is the ONLY rejector
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
                    ts="2026-08-18T00:00:01Z",  # later ts: the core check is the ONLY rejector
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
                    ts="2026-08-18T00:00:01Z",
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="merge-gate",
                ),
            ),
            p,
        )
    with pytest.raises(
        fr.RecordError, match="core field 'lane_id'"
    ):  # envelope fields are immutable too (round-3 P2)
        fr.append_row(
            fr.make_row(
                _core(finding_id=fid),
                _env(
                    ts="2026-08-18T00:00:01Z",
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
                    ts="2026-08-18T00:00:01Z",
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
                ts="2026-08-18T00:00:01Z",
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
        p,
    )


# mutation-probe: drop the `datetime.strptime(...)` ts check in validate()
def test_ts_must_be_a_real_utc_timestamp():
    """A shape-matching but impossible ts would out-rank every real adjudication ts under the
    strictly-later rule (Codex round-8 P2)."""
    with pytest.raises(fr.RecordError, match="not a real UTC timestamp"):
        fr.validate(fr.make_row(_core(), _env(ts="9999-99-99T99:99:99Z")))
    with pytest.raises(fr.RecordError, match="not a real UTC timestamp"):
        fr.validate(fr.make_row(_core(), _env(ts="2026-02-30T00:00:00Z")))
    fr.validate(fr.make_row(_core(), _env(ts=fr.now_iso())))  # the emitter's own clock is legal


# mutation-probe: drop the non-empty grounding-fields loop in validate()
@pytest.mark.parametrize("field", ["location", "observed_evidence", "expected_contract"])
def test_finding_rows_require_grounding_fields(field):
    """K5 / C-HE-24 §1: a `finding` with an empty location / evidence / expected contract is
    unactionable and must not persist; marker kinds may carry blanks (Codex round-8 P2)."""
    with pytest.raises(fr.RecordError, match=f"non-empty {field!r}"):
        fr.validate(fr.make_row(_core(**{field: "  "}), _env()))
    fr.validate(fr.make_row(_core(**{field: ""}), _env(record_kind="no_finding")))  # marker: legal


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


# mutation-probe: drop the already-adjudicated guard in _check_against_prior_rows()
def test_retry_after_adjudication_is_rejected(tmp_path: Path):
    """A same-core `finding` retry appended AFTER an adjudication would be the reducer's last row
    with a null disposition -- the decision would silently vanish (Codex round-4 P2)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env()), p)
    fr.append_row(
        fr.make_row(
            _core(),
            _env(
                ts="2026-08-18T00:00:01Z",
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
        p,
    )
    with pytest.raises(fr.RecordError, match="already adjudicated"):
        fr.append_row(fr.make_row(_core(), _env(ts="2026-08-18T00:00:09Z")), p)
    fr.append_row(
        fr.make_row(
            _core(),
            _env(
                ts="2026-08-18T00:00:02Z",
                record_kind="finding_adjudication",
                disposition="rejected",
                disposition_actor="operator",
            ),
        ),
        p,
    )  # further adjudication: legal
    last = fr.reduce_last_by_finding_id(fr.read_rows(p))
    assert last[FID]["disposition"] == "rejected" and len(fr.read_rows(p)) == 3


def test_reducer_uses_file_order_not_ts():
    """The append-only log is the ordering authority: a later physical row with an EARLIER ts
    (a back-filled / imported log the write-time ts guard never saw) still wins (Codex round-1
    P2). Rows are built directly -- append_row itself now rejects a non-later adjudication ts."""
    rows = [
        fr.make_row(_core(), _env(ts="2026-08-18T00:00:05Z")),
        fr.make_row(
            _core(),
            _env(
                ts="2026-08-18T00:00:01Z",  # earlier than the row before it
                record_kind="finding_adjudication",
                disposition="accepted",
                disposition_actor="operator",
            ),
        ),
    ]
    assert fr.reduce_last_by_finding_id(rows)[FID]["disposition"] == "accepted"


def test_next_finding_id_allocates_per_observation():
    """A finding_id names ONE observation (C-HE-24 §4 + Invariants, spec-literal): the allocator
    yields the next free `n` for a (producer, head, location) prefix; other prefixes start at 1."""
    rows = [
        fr.make_row(_core(finding_id=fr.make_finding_id("merge-gate", HEAD, LOC, 1)), _env()),
        fr.make_row(_core(finding_id=fr.make_finding_id("merge-gate", HEAD, LOC, 2)), _env()),
    ]
    assert fr.next_finding_id("merge-gate", HEAD, LOC, rows) == fr.make_finding_id(
        "merge-gate", HEAD, LOC, 3
    )
    assert fr.next_finding_id("merge-gate", HEAD, "tools/y.py:1", rows).endswith(":1")
    assert fr.next_finding_id("codex", HEAD, LOC, rows).endswith(":1")
    assert fr.next_finding_id("merge-gate", "nohead", LOC, []).startswith("merge-gate:nohead:")


def test_append_observation_mints_fresh_ids_across_rounds(tmp_path: Path):
    """A rerun on the same head that re-reports a location -- same or changed evidence -- is a NEW
    observation with a fresh id; `round_n` stays immutable per id (Codex rounds 9-10)."""
    p = tmp_path / "g.jsonl"
    fields = dict(
        location=LOC,
        observed_evidence="lease acquired without pr",
        expected_contract="C-HE-06 §3",
        severity="P1",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    r1 = fr.append_observation(fields, _env(round_n=1), p)
    r2 = fr.append_observation(fields, _env(round_n=2, ts="2026-08-18T00:00:01Z"), p)
    r3 = fr.append_observation(
        {**fields, "observed_evidence": "reworded"}, _env(round_n=2, ts="2026-08-18T00:00:02Z"), p
    )
    assert [r["finding_id"].rsplit(":", 1)[1] for r in (r1, r2, r3)] == ["1", "2", "3"]
    assert len(fr.read_rows(p)) == 3
    with pytest.raises(fr.RecordError, match="core field 'round_n'"):  # the id still binds round_n
        fr.append_row(
            fr.make_row(
                _core(finding_id=r1["finding_id"]), _env(round_n=2, ts="2026-08-18T00:00:03Z")
            ),
            p,
        )
    # a null-head row mints under the `nohead` token and passes the component check
    r4 = fr.append_observation(
        {**fields, "location": "codex"},
        _env(head_sha=None, record_kind="reviewer_unavailable", ts="2026-08-18T00:00:04Z"),
        p,
    )
    assert r4["finding_id"].startswith("merge-gate:nohead:")


# mutation-probe: drop the `_lock_exclusive(fd, path)` line in _under_log_lock()
def test_append_observation_allocates_and_appends_in_one_critical_section(
    tmp_path: Path, monkeypatch
):
    """Two concurrent emitters minting for the same (producer, head, location) get DISTINCT ids
    (`:1`, `:2`) -- never the same id twice. If allocation ran outside the lock (or the lock were
    gone) both would read an empty log, both would mint `:1`, and -- being identical same-kind
    rows -- both would land: two rows, one id. The barrier inside the patched _read_rows_fd
    only rendezvous when both callers are inside the section at once (merge-gate L3
    finding; re-pointed from read_rows when the locked body switched to fd reads --
    the merge-gate r2 witness lens caught the old monkeypatch as dead code)."""
    p = tmp_path / "g.jsonl"
    gate = threading.Barrier(2, timeout=1.0)
    real_read_fd = fr._read_rows_fd

    def read_then_rendezvous(fd, path):
        rows = real_read_fd(fd, path)
        try:
            gate.wait()
        except threading.BrokenBarrierError:
            pass
        return rows

    monkeypatch.setattr(fr, "_read_rows_fd", read_then_rendezvous)
    fields = dict(
        location=LOC,
        observed_evidence="lease acquired without pr",
        expected_contract="C-HE-06 §3",
        severity="P1",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    minted: list[str] = []
    errors: list[BaseException] = []

    def writer() -> None:
        try:
            minted.append(fr.append_observation(fields, _env(), p)["finding_id"])
        except fr.RecordError as exc:  # pragma: no cover - a rejection here is itself a failure
            errors.append(exc)

    threads = [threading.Thread(target=writer) for _ in range(2)]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=30)
    rows = fr.read_rows(p)
    assert errors == [] and len(rows) == 2, (errors, rows)
    assert sorted(r["finding_id"].rsplit(":", 1)[1] for r in rows) == ["1", "2"]
    assert len(set(minted)) == 2


def test_next_finding_id_rejects_a_non_integer_tail_loudly():
    """A legacy/externally-appended row that never passed validate() surfaces as a RecordError,
    not a bare ValueError (merge-gate L3 advisory)."""
    bad = fr.make_row(_core(finding_id=f"merge-gate:{HEAD}:{fr.location_hash(LOC)}:x"), _env())
    with pytest.raises(fr.RecordError, match="non-integer <n>"):
        fr.next_finding_id("merge-gate", HEAD, LOC, [bad])


def test_cli_validate_exit_codes(tmp_path: Path, capsys):
    """`finding_record.py validate <jsonl>`: 0 on an absent/empty/valid file, 1 when any row
    fails validate() (named on stderr), 2 on usage (merge-gate L3 advisory)."""
    p = tmp_path / "g.jsonl"
    assert fr.main(["validate", str(p)]) == 0  # absent
    fr.append_row(fr.make_row(_core(), _env()), p)
    assert fr.main(["validate", str(p)]) == 0  # valid
    bad = fr.make_row(
        _core(), _env(record_kind="finding", disposition="accepted")
    )  # would fail validate()
    with p.open("a") as fh:
        fh.write(json.dumps(bad, sort_keys=True) + "\n")  # bypass the API, as a hand-edit would
    assert fr.main(["validate", str(p)]) == 1
    assert "row 2:" in capsys.readouterr().err
    assert fr.main(["nope"]) == 2


# mutation-probe: drop the `orig["record_kind"] != "finding"` adjudicable-kind guard
def test_only_finding_rows_may_be_adjudicated(tmp_path: Path):
    """An accepted marker would be reduced by N6 as a prevented problem (Codex round-10 P2)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(observed_evidence=""), _env(record_kind="no_finding")), p)
    with pytest.raises(fr.RecordError, match="only finding rows may be adjudicated"):
        fr.append_row(
            fr.make_row(
                _core(observed_evidence=""),
                _env(
                    ts="2026-08-18T00:00:01Z",
                    record_kind="finding_adjudication",
                    disposition="accepted",
                    disposition_actor="operator",
                ),
            ),
            p,
        )


# mutation-probe: drop the `elif row["record_kind"] == "equivalence_proof":` branch in validate()
def test_equivalence_proof_rows_carry_the_prover_inline():
    """C-HE-32 §1: the proof row IS the disposition, by a decorrelated party (U-HE-41's helper);
    a proof without a prover, or by the beneficiary itself, is refused (Codex round-10 P2)."""
    proof = dict(record_kind="equivalence_proof", disposition="accepted", disposition_actor="codex")
    fr.validate(
        fr.make_row(_core(finding_type="equivalence_proof", producer="ship-pr"), _env(**proof))
    )
    with pytest.raises(fr.RecordError, match="decorrelated prover"):
        fr.validate(
            fr.make_row(
                _core(finding_type="equivalence_proof", producer="ship-pr"),
                _env(record_kind="equivalence_proof"),
            )
        )
    with pytest.raises(fr.RecordError, match="equals producer"):
        fr.validate(
            fr.make_row(
                _core(finding_type="equivalence_proof", producer="ship-pr"),
                _env(**{**proof, "disposition_actor": "ship-pr"}),
            )
        )


# mutation-probe: drop the record_kind-transition guard in _check_against_prior_rows()
def test_only_same_kind_retry_or_adjudication_may_follow_an_existing_id(tmp_path: Path):
    """`finding` -> `no_finding` on one id would let the producer erase its own finding through
    the reducer with no disposition_actor (Codex round-5 P1)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env()), p)
    with pytest.raises(fr.RecordError, match="may not follow it"):
        fr.append_row(
            fr.make_row(_core(), _env(record_kind="no_finding", ts="2026-08-18T00:00:01Z")), p
        )
    fr.append_row(
        fr.make_row(_core(), _env(ts="2026-08-18T00:00:01Z")), p
    )  # same-kind retry: legal
    assert len(fr.read_rows(p)) == 2


# mutation-probe: drop the adjudication-ts guard in _check_against_prior_rows()
def test_adjudication_ts_must_be_strictly_later(tmp_path: Path):
    """C-HE-24 §5: an adjudication carries "a later ts" -- same-second (now_iso() is
    second-granular) and earlier are both rejected at write (Codex round-5 P2)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env(ts="2026-08-18T00:00:05Z")), p)
    adj = dict(
        record_kind="finding_adjudication", disposition="accepted", disposition_actor="operator"
    )
    for ts in ("2026-08-18T00:00:05Z", "2026-08-18T00:00:01Z"):
        with pytest.raises(fr.RecordError, match="must be later"):
            fr.append_row(fr.make_row(_core(), _env(ts=ts, **adj)), p)
    fr.append_row(fr.make_row(_core(), _env(ts="2026-08-18T00:00:06Z", **adj)), p)
    assert len(fr.read_rows(p)) == 2


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
    with p.open("a") as holder, p.open("a") as waiter:
        fr._lock_exclusive(holder.fileno(), p)
        try:
            with pytest.raises(fr.RecordError, match="could not lock"):
                fr._lock_exclusive(waiter.fileno(), p, timeout_s=0.2)
        finally:
            fcntl.flock(holder.fileno(), fcntl.LOCK_UN)


def test_append_is_one_write_syscall_and_a_short_write_rolls_back(tmp_path: Path, monkeypatch):
    """The line goes down in ONE os.write; a short write (disk full) is truncated back to the
    pre-write offset before raising, so a torn tail never poisons the log (Codex round-6 P2)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env()), p)
    before = p.read_bytes()
    calls: list[int] = []
    real_write = os.write

    def half_write(fd: int, data: bytes) -> int:
        calls.append(len(data))
        return real_write(fd, data[: len(data) // 2])  # simulate ENOSPC mid-line

    monkeypatch.setattr(os, "write", half_write)
    with pytest.raises(fr.RecordError, match="short write"):
        fr.append_row(
            fr.make_row(_core(finding_id=fr.make_finding_id("merge-gate", HEAD, LOC, 2)), _env()), p
        )
    monkeypatch.undo()
    assert len(calls) == 1  # one syscall carried the whole encoded line
    assert p.read_bytes() == before  # rolled back byte-exact
    assert len(fr.read_rows(p)) == 1  # still parseable
    fr.append_row(
        fr.make_row(_core(finding_id=fr.make_finding_id("merge-gate", HEAD, LOC, 2)), _env()), p
    )
    assert len(fr.read_rows(p)) == 2


def test_torn_tail_line_fails_loudly_with_its_line_number(tmp_path: Path):
    """A torn last line is a hard, named RecordError -- never silently skipped (a legacy or
    externally-damaged log must surface, not lose rows)."""
    p = tmp_path / "g.jsonl"
    fr.append_row(fr.make_row(_core(), _env()), p)
    with p.open("a") as fh:
        fh.write('{"finding_id": "torn')  # no newline, not JSON
    with pytest.raises(fr.RecordError, match=r"g\.jsonl:2 is not valid JSON"):
        fr.read_rows(p)


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
    other = fr.to_guard_finding(fr.make_row(_core(finding_type="equivalence_proof"), _env()))
    assert other.severity == "info"  # anything outside the hard/warn prefix families


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


def test_locked_body_reads_through_the_fd_not_the_pathname(tmp_path: Path, monkeypatch):
    """merge-gate r2 witness lens: the positive witness that critical-section reads come
    from the LOCKED fd (codex r15 P1 -- an in-boundary guarantee). Poison the pathname
    reader: if any locked body still called read_rows(path), the append would blow up."""
    p = tmp_path / "g.jsonl"

    def poisoned(path=None):
        raise AssertionError("locked body read via the pathname, not the fd")

    monkeypatch.setattr(fr, "read_rows", poisoned)
    fields = dict(
        location=LOC,
        observed_evidence="fd-read witness",
        expected_contract="C-HE-24 §4",
        severity="P2",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    row = fr.append_observation(fields, _env(), p)
    assert row["finding_id"].endswith(":1")
    monkeypatch.undo()
    assert len(fr.read_rows(p)) == 1


def test_append_observations_reads_through_the_fd_not_the_pathname(tmp_path: Path, monkeypatch):
    """merge-gate r3 witness: the fd-read guarantee at append_observations -- the call
    site the C-HE-12 detection dispatch actually uses (the r2 witness covered only
    append_observation; the lens mutation-verified this site's regression path was
    undetectable). Poisoned pathname reader: a revert to read_rows(path) blows up."""
    p = tmp_path / "g.jsonl"

    def poisoned(path=None):
        raise AssertionError("locked body read via the pathname, not the fd")

    monkeypatch.setattr(fr, "read_rows", poisoned)
    fields = dict(
        location=LOC,
        observed_evidence="fd-read witness (observations)",
        expected_contract="C-HE-24 §4",
        severity="P2",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    written = fr.append_observations(lambda rows: [(dict(fields), _env())], p)
    assert len(written) == 1 and written[0]["finding_id"].endswith(":1")
    monkeypatch.undo()
    assert len(fr.read_rows(p)) == 1


def test_append_row_reads_through_the_fd_not_the_pathname(tmp_path: Path, monkeypatch):
    """merge-gate r3 witness (P3 sibling): append_row's critical-section prior-rows
    check also reads via the locked fd."""
    p = tmp_path / "g.jsonl"
    env = _env()
    head = env.head_sha if env.head_sha is not None else "nohead"
    core = fr.FindingCore(
        finding_id=fr.make_finding_id("merge-gate", head, LOC, 1),
        location=LOC,
        observed_evidence="fd-read witness (row)",
        expected_contract="C-HE-24 §4",
        severity="P2",
        finding_type="terminal-block",
        lineage_claim="fresh",
        producer="merge-gate",
    )
    row = fr.make_row(core, env)

    def poisoned(path=None):
        raise AssertionError("locked body read via the pathname, not the fd")

    monkeypatch.setattr(fr, "read_rows", poisoned)
    fr.append_row(row, p)
    monkeypatch.undo()
    assert len(fr.read_rows(p)) == 1
