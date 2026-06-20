"""B-ENGINE-OUTPUT-REPLAY — durable per-run output store unit tests.

Verifies the crash-survivable journal mechanics (round-trip across a fresh store
instance = a process restart; per-step keying; last-wins; torn-append skip + the
self-healing leading newline) in isolation — the substrate the producer +
resume-rehydration compose with. Mirrors `test_r_cc_1_api_resume.py`'s durable-
store unit tests.
"""

from __future__ import annotations

from pathlib import Path

from harness_runtime.lifecycle.engine_output_store import (
    EngineOutputStore,
    engine_output_dir_for,
)

_RUN_KEY = "run-idem-key-abc"


def test_record_then_read_round_trip(tmp_path: Path) -> None:
    """record() persists per-step outputs; a FRESH store over the same dir (a
    process restart) reads them back keyed by step_index."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record(_RUN_KEY, 0, "step-0", {"role": "gen", "v": 1})
    store.record(_RUN_KEY, 1, "step-1", {"role": "eval", "v": 2})

    fresh = EngineOutputStore(journal_dir=tmp_path / "eo")  # restart
    outputs = fresh.read_outputs(_RUN_KEY)
    assert outputs == {
        0: ("step-0", {"role": "gen", "v": 1}),
        1: ("step-1", {"role": "eval", "v": 2}),
    }


def test_missing_run_returns_empty(tmp_path: Path) -> None:
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.read_outputs("never-recorded") == {}


def test_last_record_per_step_index_wins(tmp_path: Path) -> None:
    """An idempotent re-record of the same step_index (e.g. a resume re-write)
    yields the latest output (last-wins)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record(_RUN_KEY, 0, "step-0", {"v": "first"})
    store.record(_RUN_KEY, 0, "step-0", {"v": "second"})
    assert store.read_outputs(_RUN_KEY) == {0: ("step-0", {"v": "second"})}


def test_per_run_isolation(tmp_path: Path) -> None:
    """Each run_key has a dedicated file; a read for one run never returns another's."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    store.record("run-a", 0, "s0", {"r": "a"})
    store.record("run-b", 0, "s0", {"r": "b"})
    assert store.read_outputs("run-a") == {0: ("s0", {"r": "a"})}
    assert store.read_outputs("run-b") == {0: ("s0", {"r": "b"})}


def test_torn_trailing_line_is_skipped_not_corrupting(tmp_path: Path) -> None:
    """A crash mid-append leaves a partial trailing line with no newline; the next
    record's leading-newline self-heal makes the fragment its own (skipped) line,
    so the prior committed records + the new clean record are all readable."""
    journal_dir = tmp_path / "eo"
    store = EngineOutputStore(journal_dir=journal_dir)
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    # Simulate a crash mid-append: a partial record with NO trailing newline.
    import hashlib

    digest = hashlib.sha256(_RUN_KEY.encode("utf-8")).hexdigest()
    journal_file = journal_dir / f"{digest}.jsonl"
    with journal_file.open("a", encoding="utf-8") as handle:
        handle.write('{"step_index": 1, "step_id": "TORN-NO-NEWLINE')
    # A clean record after the torn append must be readable + not corrupt step-0.
    store.record(_RUN_KEY, 1, "step-1", {"v": 1})
    outputs = store.read_outputs(_RUN_KEY)
    assert outputs[0] == ("step-0", {"v": 0})
    assert outputs[1] == ("step-1", {"v": 1})


def test_corrupt_line_skipped_committed_records_survive(tmp_path: Path) -> None:
    """A garbage middle line is skipped; the surrounding committed records survive
    (per-line fail-soft; the resume-site prefix-completeness check is the
    fail-closed gate for a MISSING committed step)."""
    journal_dir = tmp_path / "eo"
    store = EngineOutputStore(journal_dir=journal_dir)
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    import hashlib

    digest = hashlib.sha256(_RUN_KEY.encode("utf-8")).hexdigest()
    journal_file = journal_dir / f"{digest}.jsonl"
    with journal_file.open("a", encoding="utf-8") as handle:
        handle.write("{not json at all}\n")
    store.record(_RUN_KEY, 2, "step-2", {"v": 2})
    outputs = store.read_outputs(_RUN_KEY)
    assert outputs == {0: ("step-0", {"v": 0}), 2: ("step-2", {"v": 2})}
    # The gap at index 1 is the corruption the rehydrate site fails closed on.
    assert 1 not in outputs


def test_journal_exists_discriminates_absent_from_recorded(tmp_path: Path) -> None:
    """`journal_exists` is the rehydrate discriminator: False before any record (a
    config flip → degrade), True after (a recorded run; if read then yields nothing
    → unreadable → fail-closed)."""
    store = EngineOutputStore(journal_dir=tmp_path / "eo")
    assert store.journal_exists(_RUN_KEY) is False
    store.record(_RUN_KEY, 0, "step-0", {"v": 0})
    assert store.journal_exists(_RUN_KEY) is True
    # A FRESH store over the same dir (a restart) also sees the existing journal.
    assert EngineOutputStore(journal_dir=tmp_path / "eo").journal_exists(_RUN_KEY) is True


def test_engine_output_dir_for_co_locates_under_state_ledger(tmp_path: Path) -> None:
    assert engine_output_dir_for(tmp_path) == tmp_path / "engine-output"
