"""C-HE-03 reservation record: generation CAS, transitions, chain, seq, gc."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import reservations as rs


@pytest.fixture
def qdir(tmp_path, monkeypatch):
    q = tmp_path / "queue"
    q.mkdir()
    monkeypatch.setattr(rs, "QUEUE_DIR", q)
    return q


def test_reserve_creates_gen1_pending_full_snapshot(qdir):
    p = rs.reserve("pr-1", lane_id="h-wt-1", branch="b1", arc_type="inventing")
    assert p["state"] == "pending" and p["generation"] == 1
    assert p["arc_type"] == "inventing" and p["arc_type_declared_at"] == "open"
    assert set(p) >= {
        "arc_id",
        "generation",
        "prev_generation",
        "state",
        "lane_id",
        "branch",
        "pr",
        "head_sha",
        "base_sha",
        "attested_merge_tree",
        "arc_type",
        "arc_type_declared_at",
        "reserved_at",
        "transitioned_at",
        "seq",
        "superseded_by",
        "concurrent_lanes_at_open",
        "phases",
        "_provenance",
    }
    assert (qdir / "reservations" / "pr-1" / "1.json").exists()
    assert p["_provenance"]["reachable_from_state_machine"] is False


def test_reserve_requires_arc_type(qdir):
    with pytest.raises(rs.ReservationError, match="arc_type"):
        rs.reserve("pr-2", lane_id="h", branch="b", arc_type=None)  # type: ignore[arg-type]


# mutation-probe: drop the pending/open refusal in reserve()
def test_second_lane_selection_refused_while_pending_or_open(qdir):
    rs.reserve("pr-3", lane_id="A", branch="b", arc_type="applying")
    with pytest.raises(rs.ReservationHeld):
        rs.reserve("pr-3", lane_id="B", branch="b2", arc_type="applying")
    rs.transition("pr-3", "open", lane_id="A")
    with pytest.raises(rs.ReservationHeld):
        rs.reserve("pr-3", lane_id="B", branch="b2", arc_type="applying")
    assert rs.selectable("pr-3") is False and rs.selectable("pr-new") is True


def test_transition_is_new_gen_never_rename(qdir):
    rs.reserve("pr-4", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-4", "open", lane_id="A")
    d = qdir / "reservations" / "pr-4"
    assert sorted(p.name for p in d.glob("*.json")) == ["1.json", "2.json"]
    g1 = json.loads((d / "1.json").read_text())
    g2 = json.loads((d / "2.json").read_text())
    assert g1["state"] == "pending" and g2["state"] == "open"
    assert g2["prev_generation"] == 1 and g2["seq"] > g1["seq"]


# mutation-probe: drop the re-validation in _cas_next's retry (re-apply the stale payload)
def test_cas_loser_revalidates_and_raises(qdir, monkeypatch):
    """Two writers read gen n (open) with different intents; loser re-validates and RAISES;
    head stays merged."""
    rs.reserve("pr-5", lane_id="A", branch="b", arc_type="inventing")
    rs.reserve("pr-6", lane_id="A", branch="b", arc_type="inventing")  # the superseder must exist
    rs.transition("pr-5", "open", lane_id="A")
    real_write = rs._write_gen
    fired = {"done": False}

    def racing_write(arc_id, gen, payload):
        if not fired["done"] and payload["state"] == "abandoned":
            fired["done"] = True
            # the other writer wins first
            real_write(arc_id, gen, {**payload, "state": "merged", "superseded_by": None})
        return real_write(arc_id, gen, payload)

    monkeypatch.setattr(rs, "_write_gen", racing_write)
    with pytest.raises(rs.IllegalTransition):
        rs.transition("pr-5", "abandoned", lane_id="A", superseded_by="pr-6")
    assert rs.current("pr-5")[1]["state"] == "merged"


# mutation-probe: drop the holder check in transition.build for open->terminal
def test_only_holder_terminalizes_open_reservation(qdir):
    rs.reserve("pr-7b", lane_id="A", branch="b", arc_type="inventing")
    rs.reserve("pr-8", lane_id="A", branch="b", arc_type="inventing")
    rs.reserve("pr-9x", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-7b", "open", lane_id="A")
    with pytest.raises(rs.IllegalTransition, match="requires the holder"):
        rs.transition("pr-7b", "merged", lane_id="B")
    with pytest.raises(rs.IllegalTransition, match="requires the holder"):
        rs.transition("pr-7b", "abandoned", lane_id="B", superseded_by="pr-8")
    assert rs.transition("pr-7b", "merged", lane_id="A")["state"] == "merged"
    rs.reserve("pr-7c", lane_id="A", branch="b", arc_type="inventing")
    # pending->abandoned: legal for a lane that HOLDS the superseding reservation
    # (C-HE-03 §5; codex round-8 P1) -- OTHER owns pr-9y, so OTHER may abandon pr-7c to it
    rs.reserve("pr-9y", lane_id="OTHER", branch="b", arc_type="inventing")
    assert (
        rs.transition("pr-7c", "abandoned", lane_id="OTHER", superseded_by="pr-9y")["state"]
        == "abandoned"
    )


# mutation-probe: drop the missing-superseder existence check in transition.build
def test_abandoned_requires_existing_superseder(qdir):
    """codex round-6 P2: a pointer at a missing reservation committed into an immutable
    terminal head would make walk_terminal raise forever with no repair path."""
    rs.reserve("pr-21", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-21", "open", lane_id="A")
    with pytest.raises(rs.ReservationError, match="missing reservation"):
        rs.transition("pr-21", "abandoned", lane_id="A", superseded_by="pr-ghost")
    with pytest.raises(rs.ReservationError, match="bad arc_id"):
        rs.transition("pr-21", "abandoned", lane_id="A", superseded_by="../evil")
    rs.reserve("pr-22", lane_id="A", branch="b", arc_type="inventing")
    assert (
        rs.transition("pr-21", "abandoned", lane_id="A", superseded_by="pr-22")["state"]
        == "abandoned"
    )


# mutation-probe: drop the superseder-holder check for pending->abandoned in transition.build
def test_pending_abandonment_requires_holding_the_superseder(qdir):
    """codex round-8 P1: a competing lane must not terminalize another lane's selected unit
    by naming a superseder it does not own (C-HE-03 §5)."""
    rs.reserve("pr-24", lane_id="A", branch="b", arc_type="inventing")
    rs.reserve("pr-25", lane_id="A", branch="b", arc_type="inventing")  # A's superseder
    with pytest.raises(rs.IllegalTransition, match="hold the superseding"):
        rs.transition("pr-24", "abandoned", lane_id="HIJACKER", superseded_by="pr-25")
    assert rs.current("pr-24")[1]["state"] == "pending"
    assert (
        rs.transition("pr-24", "abandoned", lane_id="A", superseded_by="pr-25")["state"]
        == "abandoned"
    )
    # OPEN holder may abandon toward a superseder ANOTHER lane owns (codex round-9 P2):
    # the §6 open-holder rule is the gate there, not superseder ownership
    rs.reserve("pr-28", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-28", "open", lane_id="A")
    rs.reserve("pr-29", lane_id="B", branch="b", arc_type="inventing")
    assert (
        rs.transition("pr-28", "abandoned", lane_id="A", superseded_by="pr-29")["state"]
        == "abandoned"
    )


# mutation-probe: drop the symlink refusal in _dir
def test_symlinked_reservation_path_refused_at_read_and_write(qdir, tmp_path):
    """codex round-8 P2: a pre-planted symlink at reservations/<arc_id> must not let reads
    follow forged state or writes escape QUEUE_DIR."""
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    root = qdir / "reservations"
    root.mkdir(parents=True)
    (root / "pr-sym").symlink_to(outside)
    with pytest.raises(rs.ReservationError, match="symlink"):
        rs.reserve("pr-sym", lane_id="A", branch="b", arc_type="inventing")
    with pytest.raises(rs.ReservationError, match="symlink"):
        rs.current("pr-sym")
    assert not list(outside.iterdir())  # nothing was written through the link
    # per-FILE symlink: a planted 999.json link must fail loudly, never inject a forged
    # head or be silently skipped (codex round-10 P2)
    rs.reserve("pr-real", lane_id="A", branch="b", arc_type="inventing")
    forged = tmp_path / "forged.json"
    forged.write_text(json.dumps({"state": "merged"}))
    (root / "pr-real" / "999.json").symlink_to(forged)
    with pytest.raises(rs.ReservationError, match=r"999\.json is a symlink"):
        rs.current("pr-real")
    # root symlink: the whole store relocated is refused at the single source
    # (codex round-11 P2)
    import shutil as _sh

    real_root_backup = tmp_path / "root-backup"
    _sh.move(str(root), str(real_root_backup))
    (qdir / "reservations").symlink_to(real_root_backup)
    with pytest.raises(rs.ReservationError, match="reservations is a symlink"):
        rs.current("pr-real")
    (qdir / "reservations").unlink()
    _sh.move(str(real_root_backup), str(root))
    # .seq allocator containment (codex round-10 P2)
    import shutil

    seq = root / ".seq"
    if seq.exists():
        shutil.rmtree(seq)
    elsewhere = tmp_path / "seq-elsewhere"
    elsewhere.mkdir()
    seq.symlink_to(elsewhere)
    with pytest.raises(rs.ReservationError, match=r"\.seq allocator"):
        rs.alloc_seq()


def test_finding_count_domain_enforced(qdir):
    """codex round-8 P3: nonnegative int, bool excluded."""
    rs.reserve("pr-27", lane_id="A", branch="b", arc_type="inventing")
    for bad in (-1, True, "2"):
        with pytest.raises(rs.ReservationError, match="finding_count"):
            rs.record_round_outcome(
                "pr-27", 1, channel="codex", terminal="BLOCK", finding_count=bad
            )


def test_reserve_declared_at_domain(qdir):
    """codex round-6 P3 + round-13 P2: arbitrary labels refused; 'close' is legal only as
    the documented legacy-queue bootstrap value (plan §6 item 3 / U-HE-19 / U-HE-44)."""
    with pytest.raises(rs.ReservationError, match="arc_type_declared_at"):
        rs.reserve(
            "pr-23", lane_id="A", branch="b", arc_type="inventing", arc_type_declared_at="maybe"
        )
    p = rs.reserve(
        "pr-23b", lane_id="A", branch="b", arc_type="inventing", arc_type_declared_at="close"
    )
    assert p["arc_type_declared_at"] == "close"  # legacy bootstrap path stays drainable


# mutation-probe: drop the REVIEWER_UNAVAILABLE-superseded branch in fold_round_outcomes
def test_fold_round_outcomes_projects_to_c_he_25_shape(qdir):
    """codex round-10/13 P2: the committed projection for the U-HE-19 fold — numeric keys,
    deciding leg wins a failover round, two decided legs fail loudly."""
    single = {"1/codex": {"channel": "codex", "terminal": "APPROVE", "finding_count": 0}}
    assert rs.fold_round_outcomes(single) == {
        "1": {"channel": "codex", "terminal": "APPROVE", "finding_count": 0}
    }
    failover = {
        "1/codex": {"channel": "codex", "terminal": "REVIEWER_UNAVAILABLE", "finding_count": 0},
        "1/gemini": {"channel": "gemini", "terminal": "BLOCK", "finding_count": 2},
        "2/gemini": {"channel": "gemini", "terminal": "APPROVE", "finding_count": 0},
    }
    folded = rs.fold_round_outcomes(failover)
    assert folded == {
        "1": {"channel": "gemini", "terminal": "BLOCK", "finding_count": 2},
        "2": {"channel": "gemini", "terminal": "APPROVE", "finding_count": 0},
    }
    # deciding leg first, unavailable leg second: same result (order-independent)
    reordered = {k: failover[k] for k in ("1/gemini", "1/codex", "2/gemini")}
    assert rs.fold_round_outcomes(reordered) == folded
    with pytest.raises(rs.ReservationError, match="two decided legs"):
        rs.fold_round_outcomes(
            {
                "1/codex": {"channel": "codex", "terminal": "APPROVE", "finding_count": 0},
                "1/gemini": {"channel": "gemini", "terminal": "BLOCK", "finding_count": 1},
            }
        )


def test_abandoned_requires_superseded_by(qdir):
    rs.reserve("pr-7", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-7", "open", lane_id="A")
    with pytest.raises(rs.ReservationError, match="superseded_by"):
        rs.transition("pr-7", "abandoned", lane_id="A")


def test_chain_walk_cap_and_cycle(qdir):
    for i in range(1, 8):
        rs.reserve(f"c-{i}", lane_id="A", branch="b", arc_type="inventing")
    for i in range(1, 6):  # c-1..c-5 abandoned -> c-(i+1); c-6 pending (5-hop resolves)
        rs.transition(f"c-{i}", "abandoned", lane_id="A", superseded_by=f"c-{i + 1}")
    assert rs.walk_terminal("c-1")["arc_id"] == "c-6"
    rs.transition("c-6", "abandoned", lane_id="A", superseded_by="c-7")  # 6 hops -> raises
    with pytest.raises(rs.ChainError, match="depth"):
        rs.walk_terminal("c-1")
    rs.reserve("x", lane_id="A", branch="b", arc_type="inventing")
    rs.reserve("y", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("x", "abandoned", lane_id="A", superseded_by="y")
    rs.transition("y", "abandoned", lane_id="A", superseded_by="x")
    with pytest.raises(rs.ChainError, match="cycle"):
        rs.walk_terminal("x")


def test_seq_is_filesystem_derived_and_monotonic(qdir):
    a, b, c = rs.alloc_seq(), rs.alloc_seq(), rs.alloc_seq()
    assert a < b < c and (qdir / "reservations" / ".seq" / str(c)).exists()


def test_identifiers_reject_colon_and_empty(qdir):
    with pytest.raises(rs.ReservationError, match=":"):
        rs.reserve("pr-8", lane_id="bad:lane", branch="b", arc_type="inventing")
    with pytest.raises(rs.ReservationError, match="nonempty"):
        rs.reserve("pr-8", lane_id="", branch="b", arc_type="inventing")  # codex round-9 P3
    with pytest.raises(rs.ReservationError, match="nonempty"):
        # codex round-11 P2: a None holder would defeat the holder fence
        rs.reserve("pr-8", lane_id=None, branch="b", arc_type="inventing")  # type: ignore[arg-type]
    assert ":" not in rs.mint_lane_id(Path("/tmp/wt-x"))


# mutation-probe: replace the PAYLOAD_MUTABLE allowlist check with the old
# `_STATE_KEYS or lane_id` blocklist
def test_update_and_transition_allowlists(qdir):
    rs.reserve("pr-8b", lane_id="A", branch="b", arc_type="inventing")
    for bad in (
        {"lane_id": "B"},
        {"arc_type": "applying"},
        {"arc_type_declared_at": "close"},
        {"reserved_at": "x"},
        {"superseded_by": "pr-9"},
        {"phases": {}},
    ):
        with pytest.raises(rs.ReservationError, match="may not set"):
            rs.update_payload("pr-8b", bad)
    rs.update_payload("pr-8b", {"pr": 8, "head_sha": "a" * 40, "pilot_run_id": "p1"})  # allowed
    with pytest.raises(rs.ReservationError, match="may not set"):
        rs.transition("pr-8b", "open", lane_id="A", updates={"lane_id": "EVIL"})
    assert (
        rs.transition("pr-8b", "open", lane_id="A", updates={"concurrent_lanes_at_open": 0})[
            "lane_id"
        ]
        == "A"
    )


# mutation-probe: drop the value-domain loop in _check_updates (types no longer enforced)
def test_payload_value_domains_enforced(qdir):
    """codex round-2 P2: C-HE-03 §3 value domains at the write funnel — int|null, str|null,
    nonnegative lane counts; bool is not an int here."""
    rs.reserve("pr-14", lane_id="A", branch="b", arc_type="inventing")
    for bad in (
        {"pr": {}},
        {"pr": True},
        {"head_sha": []},
        {"attested_merge_tree": 7},
        {"concurrent_lanes_min": -1},
        {"concurrent_lanes_max": "3"},
        {"head_sha": ""},  # codex round-11 P3: sha/oid fields are nonempty hex tokens
        {"base_sha": "not-hex!"},
        {"merge_sha": "ABC123"},  # uppercase is not the git object-name form
        {"attested_merge_tree": "abc"},  # < 7 chars
    ):
        with pytest.raises(rs.ReservationError, match="must be"):
            rs.update_payload("pr-14", bad)
    with pytest.raises(rs.ReservationError, match="must be"):
        rs.transition("pr-14", "open", lane_id="A", updates={"concurrent_lanes_at_open": -2})
    rs.update_payload("pr-14", {"pr": None, "head_sha": None})  # null is always legal
    p = rs.transition("pr-14", "open", lane_id="A", updates={"concurrent_lanes_at_open": 0})
    assert p["concurrent_lanes_at_open"] == 0


def test_dot_prefixed_arc_id_refused(qdir):
    """codex round-2 P3 + round-12 P3: dot-prefixed ids collide with `.seq`; the queue's
    `.taken` and recovery-budget rules apply at reserve time too, so an id that reserves
    can always drain."""
    for bad in (".seq", ".hidden", ".", "x.taken", "y.taken.recover.h.1", "z" * 240):
        with pytest.raises(rs.ReservationError, match="bad arc_id"):
            rs.reserve(bad, lane_id="A", branch="b", arc_type="inventing")


def test_round_n_and_ts_domains(qdir):
    """codex round-12 P3: round_n is a nonnegative int (no bools/floats/negatives); phase
    ts is ISO-8601 UTC."""
    rs.reserve("pr-30", lane_id="A", branch="b", arc_type="inventing")
    for bad_round in (-1, True, 1.9):
        with pytest.raises(rs.ReservationError, match="round_n"):
            rs.record_round_outcome(
                "pr-30", bad_round, channel="codex", terminal="APPROVE", finding_count=0
            )
    with pytest.raises(rs.ReservationError, match="ISO-8601"):
        rs.record_phase("pr-30", "execute", "start", ts="t0")
    with pytest.raises(rs.ReservationError, match="ISO-8601"):
        rs.record_phase("pr-30", "execute", "start", ts="2026-08-19 00:00:00")


def test_transfer_holder_only_from_named_lane(qdir):
    rs.reserve("pr-9", lane_id="DEAD", branch="b", arc_type="inventing")
    rs.transition("pr-9", "open", lane_id="DEAD")
    rs.transfer_holder("pr-9", from_lane_id="DEAD", to_lane_id="B")
    assert rs.holder("pr-9") == "B"
    with pytest.raises(rs.IllegalTransition):
        rs.transfer_holder("pr-9", from_lane_id="DEAD", to_lane_id="C")  # stale precondition


def test_record_round_outcome_accretes(qdir):
    rs.reserve("pr-10b", lane_id="A", branch="b", arc_type="inventing")
    rs.record_round_outcome(
        "pr-10b", 1, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    p = rs.record_round_outcome("pr-10b", 2, channel="gemini", terminal="BLOCK", finding_count=3)
    assert p["round_outcomes"] == {
        "1/codex": {"channel": "codex", "terminal": "REVIEWER_UNAVAILABLE", "finding_count": 0},
        "2/gemini": {"channel": "gemini", "terminal": "BLOCK", "finding_count": 3},
    }
    with pytest.raises(rs.ReservationError):
        rs.record_round_outcome("pr-10b", 3, channel="codex", terminal="MAYBE", finding_count=0)


# mutation-probe: drop the append-only conflict check in record_round_outcome.build
def test_round_outcome_map_is_append_only_and_composite_keyed(qdir):
    """codex rounds 3-9 P2: the (round, channel) composite key gives failover legs sharing
    a round NUMBER distinct keys; a SAME-key re-record with different content raises —
    never a silent overwrite; identical re-record is idempotent (CAS-retry safe)."""
    rs.reserve("pr-15", lane_id="A", branch="b", arc_type="inventing")
    rs.record_round_outcome(
        "pr-15", 1, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    # cross-channel same round NUMBER: distinct keys, both persist
    rs.record_round_outcome("pr-15", 1, channel="gemini", terminal="BLOCK", finding_count=2)
    # same-channel next producer round: its own key, no collision (codex round-9 P2)
    rs.record_round_outcome("pr-15", 2, channel="gemini", terminal="APPROVE", finding_count=0)
    # identical re-record is idempotent
    p = rs.record_round_outcome(
        "pr-15", 1, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    assert set(p["round_outcomes"]) == {"1/codex", "1/gemini", "2/gemini"}
    assert p["round_outcomes"]["1/codex"]["terminal"] == "REVIEWER_UNAVAILABLE"
    # same-key different content: append-only conflict
    with pytest.raises(rs.RoundOutcomeConflict, match="append-only"):
        rs.record_round_outcome("pr-15", 1, channel="codex", terminal="APPROVE", finding_count=0)
    with pytest.raises(rs.ReservationError, match="channel"):
        rs.record_round_outcome("pr-15", 3, channel="a/b", terminal="APPROVE", finding_count=0)


def test_gc_sweeps_tmp_in_headless_dir(qdir, monkeypatch):
    """codex round-3 P3: a crash during gen-1 publication leaves a dir with ONLY a tmp
    stager and no head — the sweep must still remove it."""
    d = qdir / "reservations" / "pr-crashed"
    d.mkdir(parents=True)
    tmp = d / ".1.json.88888.tmp"
    tmp.write_text("{}")
    old = datetime.now(UTC) - timedelta(hours=2)
    os.utime(tmp, (old.timestamp(), old.timestamp()))
    monkeypatch.setattr(rs, "_process_is_alive", lambda pid: False)
    removed = rs.gc()
    assert tmp in removed and not tmp.exists()


def test_record_phase_accretes(qdir):
    rs.reserve("pr-10", lane_id="A", branch="b", arc_type="inventing")
    rs.record_phase("pr-10", "execute", "start", ts="2026-08-18T00:00:00Z")
    p = rs.record_phase("pr-10", "execute", "end", ts="2026-08-18T00:10:00Z")
    assert p["phases"]["execute"] == {
        "start": "2026-08-18T00:00:00Z",
        "end": "2026-08-18T00:10:00Z",
    }
    # append-only edges (codex round-14 P2): identical re-record is idempotent, a rewrite
    # of a durable measurement raises
    rs.record_phase("pr-10", "execute", "end", ts="2026-08-18T00:10:00Z")
    with pytest.raises(rs.ReservationError, match="already recorded"):
        rs.record_phase("pr-10", "execute", "end", ts="2026-08-18T00:20:00Z")
    assert rs.current("pr-10")[1]["phases"]["execute"]["end"] == "2026-08-18T00:10:00Z"


def test_cli_update_accepts_digit_leading_sha_and_parses_ints(qdir, capsys):
    """codex round-1 P1: a raw hex SHA beginning with a digit is a STRING, not JSON."""
    rs.reserve("pr-12", lane_id="A", branch="b", arc_type="inventing")
    assert rs.main(["update", "--arc-id", "pr-12", "--set", "head_sha=4be86eec1abc", "pr=8"]) == 0
    head = rs.current("pr-12")[1]
    assert head["head_sha"] == "4be86eec1abc" and head["pr"] == 8


# mutation-probe: drop the symlink/resolved-root refusal in gc()
def test_gc_never_traverses_symlinked_reservation_dir(qdir, tmp_path, monkeypatch):
    """codex round-7 P2: a symlink planted under the shared writable reservations root must
    never let GC read a forged terminal head and unlink files OUTSIDE QUEUE_DIR."""
    outside = tmp_path / "outside"
    outside.mkdir()
    old_ts = "2020-01-01T00:00:00Z"
    (outside / "1.json").write_text(json.dumps({"state": "merged", "transitioned_at": old_ts}))
    (outside / "2.json").write_text(json.dumps({"state": "merged", "transitioned_at": old_ts}))
    root = qdir / "reservations"
    root.mkdir(parents=True)
    (root / "pr-link").symlink_to(outside)
    monkeypatch.setattr(rs, "_process_is_alive", lambda pid: False)
    rs.gc()
    assert (outside / "1.json").exists() and (outside / "2.json").exists()


# hand-witness (probe not deletion-expressible: commenting a bare try/except breaks syntax):
# swap the tmp-sweep `except FileNotFoundError` to another type and this test reds.
def test_gc_survives_tmp_vanishing_mid_sweep(qdir, monkeypatch):
    """codex round-1 P2: a tmp entry unlinked between glob and stat/unlink is benign — the
    sweep continues instead of aborting on FileNotFoundError."""
    rs.reserve("pr-13", lane_id="A", branch="b", arc_type="inventing")
    d = qdir / "reservations" / "pr-13"
    tmp = d / ".1.99999.tmp"
    tmp.write_text("{}")
    old = datetime.now(UTC) - timedelta(hours=2)
    os.utime(tmp, (old.timestamp(), old.timestamp()))

    def vanish_then_dead(pid):
        tmp.unlink()  # a concurrent sweeper wins the unlink race
        return False

    monkeypatch.setattr(rs, "_process_is_alive", vanish_then_dead)
    removed = rs.gc()  # must not raise
    assert not tmp.exists() and tmp not in removed


# mutation-probe: drop the to_state!=abandoned superseded_by refusal in transition()
def test_superseded_by_only_on_abandoned(qdir):
    """codex round-4 P2: a merged record must never carry a supersession pointer
    (C-HE-03 §2)."""
    rs.reserve("pr-16", lane_id="A", branch="b", arc_type="inventing")
    with pytest.raises(rs.ReservationError, match="only legal on abandoned"):
        rs.transition("pr-16", "open", lane_id="A", superseded_by="pr-17")
    rs.transition("pr-16", "open", lane_id="A")
    with pytest.raises(rs.ReservationError, match="only legal on abandoned"):
        rs.transition("pr-16", "merged", lane_id="A", superseded_by="pr-17")
    p = rs.transition("pr-16", "merged", lane_id="A")
    assert p["superseded_by"] is None


# mutation-probe: drop the concurrent_lanes_at_open pending->open-only refusal in transition()
def test_lanes_at_open_sensor_writable_only_at_open_flip(qdir):
    """codex round-4 P2: the cohort sensor is captured at the pending->open flip and never
    rewritten by a later transition (C-HE-03 §7)."""
    rs.reserve("pr-18", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-18", "open", lane_id="A", updates={"concurrent_lanes_at_open": 2})
    with pytest.raises(rs.ReservationError, match="pending->open flip"):
        rs.transition("pr-18", "merged", lane_id="A", updates={"concurrent_lanes_at_open": 9})
    assert rs.current("pr-18")[1]["concurrent_lanes_at_open"] == 2


# mutation-probe: drop the _refuse_terminal_accretion state check
def test_accretion_refused_on_terminal_reservation(qdir):
    """codex round-4 P2: phases / round outcomes accrete only during the open window
    (C-HE-03 §3, C-HE-27 §3) — never onto a merged/abandoned record."""
    rs.reserve("pr-19", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-19", "open", lane_id="A")
    rs.record_phase("pr-19", "execute", "start")
    rs.transition("pr-19", "merged", lane_id="A")
    with pytest.raises(rs.IllegalTransition, match="open window"):
        rs.record_phase("pr-19", "execute", "end")
    with pytest.raises(rs.IllegalTransition, match="open window"):
        rs.record_round_outcome("pr-19", 1, channel="codex", terminal="APPROVE", finding_count=0)
    # codex round-5 P2: payload backfills are open-window too — a CAS replay onto a terminal
    # head must never stamp stale SHAs over the terminal audit.
    with pytest.raises(rs.IllegalTransition, match="open window"):
        rs.update_payload("pr-19", {"head_sha": "stale" + "0" * 35})


# mutation-probe: cut off by each file's mtime instead of the terminal head's transitioned_at
def test_gc_prunes_below_head_only_after_terminal_plus_30d_and_sweeps_tmp(qdir, monkeypatch):
    rs.reserve("pr-11", lane_id="A", branch="b", arc_type="inventing")
    rs.transition("pr-11", "open", lane_id="A")
    d = qdir / "reservations" / "pr-11"
    old = datetime.now(UTC) - timedelta(days=40)
    for p in d.glob("*.json"):  # gens 1-2 are 40 days old...
        os.utime(p, (old.timestamp(), old.timestamp()))
    rs.transition("pr-11", "merged", lane_id="A")  # ...but terminalization is NOW
    (d / ".2.12345.tmp").write_text("{}")
    os.utime(d / ".2.12345.tmp", (old.timestamp(), old.timestamp()))
    monkeypatch.setattr(rs, "_process_is_alive", lambda pid: False)
    rs.gc()
    assert (d / "1.json").exists() and (d / "2.json").exists(), (
        "retention runs from terminalization, not file age"
    )
    assert not (d / ".2.12345.tmp").exists()
    removed_later = rs.gc(now=datetime.now(UTC) + timedelta(days=31))
    assert removed_later and not (d / "1.json").exists() and (d / "3.json").exists()
    assert rs.current("pr-11")[1]["state"] == "merged"
