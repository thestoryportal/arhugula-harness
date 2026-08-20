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
    rs.transition("pr-7b", "open", lane_id="A")
    with pytest.raises(rs.IllegalTransition, match="requires the holder"):
        rs.transition("pr-7b", "merged", lane_id="B")
    with pytest.raises(rs.IllegalTransition, match="requires the holder"):
        rs.transition("pr-7b", "abandoned", lane_id="B", superseded_by="pr-8")
    assert rs.transition("pr-7b", "merged", lane_id="A")["state"] == "merged"
    rs.reserve("pr-7c", lane_id="A", branch="b", arc_type="inventing")
    # pending: any lane
    assert (
        rs.transition("pr-7c", "abandoned", lane_id="OTHER", superseded_by="pr-9")["state"]
        == "abandoned"
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


def test_identifiers_reject_colon(qdir):
    with pytest.raises(rs.ReservationError, match=":"):
        rs.reserve("pr-8", lane_id="bad:lane", branch="b", arc_type="inventing")
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
    rs.update_payload("pr-8b", {"pr": 8, "head_sha": "h" * 40, "pilot_run_id": "p1"})  # allowed
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
    ):
        with pytest.raises(rs.ReservationError, match="must be"):
            rs.update_payload("pr-14", bad)
    with pytest.raises(rs.ReservationError, match="must be"):
        rs.transition("pr-14", "open", lane_id="A", updates={"concurrent_lanes_at_open": -2})
    rs.update_payload("pr-14", {"pr": None, "head_sha": None})  # null is always legal
    p = rs.transition("pr-14", "open", lane_id="A", updates={"concurrent_lanes_at_open": 0})
    assert p["concurrent_lanes_at_open"] == 0


def test_dot_prefixed_arc_id_refused(qdir):
    """codex round-2 P3: a dot-prefixed arc_id would collide with `.seq` and be invisible
    to sibling_open_count/gc."""
    for bad in (".seq", ".hidden", "."):
        with pytest.raises(rs.ReservationError, match="bad arc_id"):
            rs.reserve(bad, lane_id="A", branch="b", arc_type="inventing")


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
        "1": {"channel": "codex", "terminal": "REVIEWER_UNAVAILABLE", "finding_count": 0},
        "2": {"channel": "gemini", "terminal": "BLOCK", "finding_count": 3},
    }
    with pytest.raises(rs.ReservationError):
        rs.record_round_outcome("pr-10b", 3, channel="codex", terminal="MAYBE", finding_count=0)


# mutation-probe: drop the append-only conflict check in record_round_outcome.build
def test_round_outcome_map_is_append_only(qdir):
    """codex round-3 P2: a conflicting re-record of an existing round_n raises — a failover
    leg must never erase the codex REVIEWER_UNAVAILABLE row (C-HE-25; C-HE-27 §4 N6
    exclusion). Identical re-record is idempotent."""
    rs.reserve("pr-15", lane_id="A", branch="b", arc_type="inventing")
    rs.record_round_outcome(
        "pr-15", 1, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    with pytest.raises(rs.ReservationError, match="append-only"):
        rs.record_round_outcome("pr-15", 1, channel="gemini", terminal="BLOCK", finding_count=2)
    # idempotent identical re-record
    rs.record_round_outcome(
        "pr-15", 1, channel="codex", terminal="REVIEWER_UNAVAILABLE", finding_count=0
    )
    p = rs.record_round_outcome("pr-15", 2, channel="gemini", terminal="BLOCK", finding_count=2)
    assert p["round_outcomes"]["1"]["terminal"] == "REVIEWER_UNAVAILABLE"
    assert p["round_outcomes"]["2"]["channel"] == "gemini"


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


def test_cli_update_accepts_digit_leading_sha_and_parses_ints(qdir, capsys):
    """codex round-1 P1: a raw hex SHA beginning with a digit is a STRING, not JSON."""
    rs.reserve("pr-12", lane_id="A", branch="b", arc_type="inventing")
    assert rs.main(["update", "--arc-id", "pr-12", "--set", "head_sha=4be86eec1abc", "pr=8"]) == 0
    head = rs.current("pr-12")[1]
    assert head["head_sha"] == "4be86eec1abc" and head["pr"] == 8


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
